from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from job_locator import resolve_stage1_job_dir
from job_state import load_job_state, update_after_rerun

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_V3 = REPO_ROOT / "experiments" / "usv_strict_pdf_parser_v3" / "run_v3.py"
RUN_STAGE1 = REPO_ROOT / "experiments" / "earthworks_parser_google_stage1" / "run_stage1.py"


def _python() -> str:
    return sys.executable


def _next_run_name(job_dir: Path) -> str:
    runs_dir = job_dir / "parser_runs"
    if not runs_dir.exists():
        return "run_001"
    existing = sorted(
        p.name for p in runs_dir.iterdir()
        if p.is_dir() and re.match(r"^run_\d{3}$", p.name)
    )
    if not existing:
        return "run_001"
    n = int(existing[-1].split("_")[1]) + 1
    return f"run_{n:03d}"


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
        description="Rerun PDF parser on existing job's input PDFs and create a new Google review sheet."
    )
    p.add_argument("--job-id", required=True, help="Stage1 job ID")
    p.add_argument(
        "--sharing",
        default="anyone_writer",
        choices=["owner_only", "anyone_reader", "anyone_writer"],
        help="Google Sheet sharing policy (default: anyone_writer)",
    )
    p.add_argument("--reason", default="", help="Reason for rerun, e.g. parser_improved / bad_extraction")
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

    print(f"rerun_parser: job_dir = {job_dir}", file=log)

    # 2. Read and validate job_state
    state = load_job_state(job_dir)
    source_pdfs = state.get("source", {}).get("input_pdfs", [])
    if not source_pdfs:
        print(
            "ERROR: Cannot rerun parser: no source input PDFs found in job_state.",
            file=sys.stderr,
        )
        return 1

    old_parser_block = state.get("parser") or {}
    old_active_run = old_parser_block.get("active_run", "")
    old_active_artifacts = old_parser_block.get("active_artifacts_dir", "")

    # 3. Verify job/input_pdfs directory
    input_pdfs_dir = job_dir / "input_pdfs"
    if not input_pdfs_dir.exists() or not any(input_pdfs_dir.glob("*.pdf")):
        print(
            f"ERROR: Cannot rerun parser: no PDF files found in {input_pdfs_dir}",
            file=sys.stderr,
        )
        return 1

    pdf_count = len(list(input_pdfs_dir.glob("*.pdf")))
    print(f"  input_pdfs_dir: {input_pdfs_dir} ({pdf_count} PDFs)", file=log)
    print(f"  old_active_run: {old_active_run or '(none)'}", file=log)
    print(f"  global_v3_data_used: false", file=log)
    print(f"  source_input_pdfs_changed: false", file=log)

    # 4. Determine next run name and create dir
    new_run_name = _next_run_name(job_dir)
    new_run_dir = job_dir / "parser_runs" / new_run_name
    new_run_rel = f"parser_runs/{new_run_name}"
    new_run_dir.mkdir(parents=True, exist_ok=True)
    print(f"  new_parser_run: {new_run_name}", file=log)

    # 5. Archive current google files before Stage1 overwrites them
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    iso_ts = now.isoformat(timespec="seconds")
    old_google_sheet = state.get("google_sheet", {})
    old_spreadsheet_id = old_google_sheet.get("spreadsheet_id", "")
    old_spreadsheet_url = old_google_sheet.get("url", "")
    print(f"  archiving current google files → google_history/{timestamp}/", file=log)
    archive_dir = _archive_google_files(job_dir, timestamp, log)
    archive_dir_rel = f"google_history/{timestamp}"

    # 6. Run parser v3 on the same input_pdfs
    v3_cmd = [
        _python(), str(RUN_V3),
        "--input-dir", str(input_pdfs_dir),
        "--out-dir", str(new_run_dir),
        "--json",
    ]
    print(f"$ {shlex.join([str(c) for c in v3_cmd])}", file=log)
    v3_result = subprocess.run(v3_cmd, cwd=str(REPO_ROOT), stdout=sub_stdout)

    if v3_result.returncode != 0:
        # Parser failed — keep old active run intact
        parser_run_json = new_run_dir / "parser_run.json"
        failed_info: dict = {}
        if parser_run_json.exists():
            failed_info = json.loads(parser_run_json.read_text(encoding="utf-8"))

        print(
            f"ERROR: Parser v3 failed (exit code {v3_result.returncode}). "
            f"Old active run '{old_active_run}' unchanged.",
            file=sys.stderr,
        )
        if args.json_output:
            output: dict = {
                "status": "parser_failed",
                "job_id": args.job_id,
                "old_parser_run_kept": old_active_run,
                "new_parser_run_attempted": new_run_name,
                "google_sheet_recreated": False,
                "error": f"run_v3 exit code {v3_result.returncode}",
            }
            if failed_info:
                output["failed_run_info"] = {
                    "pages_count": failed_info.get("pages_count"),
                    "errors": failed_info.get("errors", []),
                }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        return v3_result.returncode

    # 7. Read new parser_run.json
    parser_run_json_path = new_run_dir / "parser_run.json"
    if not parser_run_json_path.exists():
        print(f"ERROR: parser_run.json not found at {parser_run_json_path}", file=sys.stderr)
        return 1
    new_parser_run = json.loads(parser_run_json_path.read_text(encoding="utf-8"))

    print(
        f"  parser completed: pages={new_parser_run.get('pages_count')} "
        f"tables={new_parser_run.get('tables_count')} "
        f"candidates={new_parser_run.get('candidates_count')}",
        file=log,
    )

    # 8. Run Stage1 on the new parser_run
    project_name = state.get("project_name", args.job_id)
    stage1_cmd = [
        _python(), str(RUN_STAGE1), "prepare",
        "--project-name", project_name,
        "--job-id", args.job_id,
        "--artifacts-dir", str(new_run_dir),
        "--sharing", args.sharing,
        "--anti-cheat-mode", "warn",
    ]
    print(f"$ {shlex.join([str(c) for c in stage1_cmd])}", file=log)
    stage1_result = subprocess.run(stage1_cmd, cwd=str(REPO_ROOT), stdout=sub_stdout)
    if stage1_result.returncode != 0:
        print(f"ERROR: Stage1 prepare failed (exit code {stage1_result.returncode})", file=sys.stderr)
        return stage1_result.returncode

    # 9. Read new google_sheet_metadata
    metadata_path = job_dir / "google" / "google_sheet_metadata.json"
    if not metadata_path.exists():
        print("ERROR: google_sheet_metadata.json not created by Stage1.", file=sys.stderr)
        return 1
    new_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    # 10. Update job_state
    final_state = update_after_rerun(
        job_dir,
        old_parser_block,
        new_run_name,
        new_run_rel,
        new_parser_run,
        old_google_sheet,
        new_metadata,
        archive_dir_rel,
        args.reason,
        iso_ts,
    )
    new_google_sheet = final_state.get("google_sheet", {})

    print(f"rerun_parser completed", file=log)
    print(f"  old_parser_run: {old_active_run or '(none)'}", file=log)
    print(f"  new_active_run: {new_run_name}", file=log)
    print(f"  old_spreadsheet_id: {old_spreadsheet_id or '(none)'}", file=log)
    print(f"  new_spreadsheet_id: {new_google_sheet.get('spreadsheet_id')}", file=log)
    print(f"  archive_dir: {archive_dir_rel}", file=log)
    print(f"  parser_history entries: {len(final_state.get('parser_history', []))}", file=log)
    print(f"  google_sheet_history entries: {len(final_state.get('google_sheet_history', []))}", file=log)

    if args.json_output:
        output = {
            "status": "rerun_completed",
            "job_id": args.job_id,
            "job_dir": str(job_dir),
            "source": {
                "input_pdfs_count": len(source_pdfs),
                "input_pdfs_changed": False,
                "global_v3_data_used": False,
            },
            "old_parser_run": {
                "run": old_active_run,
                "artifacts_dir": old_active_artifacts,
                "old_parser_run_preserved": True,
            },
            "new_parser_run": {
                "run": new_run_name,
                "artifacts_dir": new_run_rel,
                "status": new_parser_run.get("status"),
                "pages_count": new_parser_run.get("pages_count"),
                "tables_count": new_parser_run.get("tables_count"),
                "logical_pages_count": new_parser_run.get("logical_pages_count"),
                "candidates_count": new_parser_run.get("candidates_count"),
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
