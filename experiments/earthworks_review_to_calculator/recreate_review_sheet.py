from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from job_locator import resolve_stage1_job_dir
from job_state import load_job_state, update_after_recreate

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_STAGE1 = REPO_ROOT / "experiments" / "earthworks_parser_google_stage1" / "run_stage1.py"

REQUIRED_ARTIFACT_FILES = [
    "extracted/earthworks.json",
    "extracted/candidates.json",
    "raw/logical_pages.json",
    "raw/tables.json",
]


def _python() -> str:
    return sys.executable


def _resolve_artifacts_dir(job_dir: Path, parser_block: dict) -> Path:
    raw = parser_block.get("active_artifacts_dir", "")
    if raw:
        p = Path(raw)
        return p if p.is_absolute() else job_dir / p
    # fallback: derive from active_run name
    return job_dir / "parser_runs" / parser_block.get("active_run", "run_001")


def _archive_google_files(job_dir: Path, timestamp: str, log) -> Path:
    archive_dir = job_dir / "google_history" / timestamp
    archive_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("google_sheet_metadata.json", "review_workbook.xlsx"):
        src = job_dir / "google" / filename
        if src.exists():
            shutil.copy2(src, archive_dir / filename)
            print(f"  archived: google/{filename} → google_history/{timestamp}/{filename}", file=log)
    return archive_dir


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Recreate Google review sheet from existing parser artifacts without re-running the PDF parser."
    )
    p.add_argument("--job-id", required=True, help="Stage1 job ID")
    p.add_argument(
        "--sharing",
        default="anyone_writer",
        choices=["owner_only", "anyone_reader", "anyone_writer"],
        help="Google Sheet sharing policy (default: anyone_writer)",
    )
    p.add_argument(
        "--reason",
        default="",
        help="Reason for recreation, e.g. table_broken / template_updated",
    )
    p.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Print result JSON to stdout; all logs go to stderr",
    )
    args = p.parse_args(argv)

    log = sys.stderr if args.json_output else sys.stdout
    sub_stdout = sys.stderr if args.json_output else None

    # 1. Locate job directory
    try:
        job_dir = resolve_stage1_job_dir(args.job_id)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"recreate_review_sheet: job_dir = {job_dir}", file=log)

    # 2. Read and validate job_state
    state = load_job_state(job_dir)
    parser_block = state.get("parser")
    if not parser_block:
        print(
            "ERROR: Cannot recreate review sheet: no active parser run found in job_state.json.",
            file=sys.stderr,
        )
        return 1

    for key in ("active_run", "active_artifacts_dir"):
        if not parser_block.get(key):
            print(
                f"ERROR: Cannot recreate review sheet: parser.{key} is missing or empty.",
                file=sys.stderr,
            )
            return 1

    if not state.get("source", {}).get("input_pdfs"):
        print(
            "ERROR: Cannot recreate review sheet: source.input_pdfs is missing.",
            file=sys.stderr,
        )
        return 1

    # 3. Resolve and validate artifacts_dir
    artifacts_dir = _resolve_artifacts_dir(job_dir, parser_block)
    missing = [f for f in REQUIRED_ARTIFACT_FILES if not (artifacts_dir / f).exists()]
    if missing:
        print("ERROR: Cannot recreate review sheet: parser artifacts are missing:", file=sys.stderr)
        for f in missing:
            print(f"  {artifacts_dir / f}", file=sys.stderr)
        return 1

    print(f"  active_run: {parser_block['active_run']}", file=log)
    print(f"  artifacts_dir: {artifacts_dir}", file=log)
    print(f"  parser_was_rerun: false", file=log)
    print(f"  used_existing_parser_artifacts: true", file=log)

    # 4. Snapshot current google_sheet for archiving and history
    old_google_sheet = state.get("google_sheet", {})
    old_spreadsheet_id = old_google_sheet.get("spreadsheet_id", "")
    old_spreadsheet_url = old_google_sheet.get("url", "")

    # 5. Archive existing google files before Stage1 overwrites them
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    iso_ts = now.isoformat(timespec="seconds")
    print(f"  archiving current google files → google_history/{timestamp}/", file=log)
    archive_dir = _archive_google_files(job_dir, timestamp, log)
    archive_dir_rel = f"google_history/{timestamp}"

    # 6. Run Stage1 prepare with same job_id and existing artifacts
    project_name = state.get("project_name", args.job_id)
    stage1_cmd = [
        _python(), str(RUN_STAGE1), "prepare",
        "--project-name", project_name,
        "--job-id", args.job_id,
        "--artifacts-dir", str(artifacts_dir),
        "--sharing", args.sharing,
        "--anti-cheat-mode", "warn",
    ]
    print(f"$ {shlex.join([str(c) for c in stage1_cmd])}", file=log)
    stage1_result = subprocess.run(stage1_cmd, cwd=str(REPO_ROOT), stdout=sub_stdout)
    if stage1_result.returncode != 0:
        print(f"ERROR: Stage1 prepare failed (exit code {stage1_result.returncode})", file=sys.stderr)
        return stage1_result.returncode

    # 7. Read new google_sheet_metadata written by Stage1
    metadata_path = job_dir / "google" / "google_sheet_metadata.json"
    if not metadata_path.exists():
        print("ERROR: google_sheet_metadata.json not created by Stage1.", file=sys.stderr)
        return 1
    new_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    # 8. Update job_state: archive old sheet, write new sheet, append history
    final_state = update_after_recreate(
        job_dir, old_google_sheet, new_metadata, archive_dir_rel, args.reason, iso_ts
    )
    new_google_sheet = final_state.get("google_sheet", {})

    print(f"recreate_review_sheet completed", file=log)
    print(f"  old_spreadsheet_id: {old_spreadsheet_id or '(none)'}", file=log)
    print(f"  new_spreadsheet_id: {new_google_sheet.get('spreadsheet_id')}", file=log)
    print(f"  new_spreadsheet_url: {new_google_sheet.get('url')}", file=log)
    print(f"  archive_dir: {archive_dir_rel}", file=log)
    print(f"  history_entries: {len(final_state.get('google_sheet_history', []))}", file=log)

    if args.json_output:
        output = {
            "status": "recreated",
            "job_id": args.job_id,
            "job_dir": str(job_dir),
            "parser_run": {
                "active_run": parser_block["active_run"],
                "artifacts_dir": str(artifacts_dir),
                "parser_was_rerun": False,
                "used_existing_parser_artifacts": True,
            },
            "old_google_sheet": {
                "spreadsheet_id": old_spreadsheet_id,
                "spreadsheet_url": old_spreadsheet_url,
            },
            "new_google_sheet": {
                "spreadsheet_id": new_google_sheet.get("spreadsheet_id", ""),
                "spreadsheet_url": new_google_sheet.get("url", ""),
                "status": new_google_sheet.get("status", ""),
                "sharing": new_google_sheet.get("sharing", {}),
            },
            "archive_dir": archive_dir_rel,
            "reason": args.reason,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
