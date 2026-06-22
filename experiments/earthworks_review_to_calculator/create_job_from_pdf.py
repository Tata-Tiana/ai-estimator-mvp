from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from job_state import init_or_update_from_stage1, save_job_state, update_source_and_parser

REPO_ROOT = Path(__file__).resolve().parents[2]
STAGE1_DIR = REPO_ROOT / "experiments" / "earthworks_parser_google_stage1"
V3_DIR = REPO_ROOT / "experiments" / "usv_strict_pdf_parser_v3"
RUN_V3 = V3_DIR / "run_v3.py"
RUN_STAGE1 = STAGE1_DIR / "run_stage1.py"
_DEFAULT_JOBS_ROOT = STAGE1_DIR / "data" / "jobs"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_job_id(project_name: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in project_name).strip("_") or "project"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{slug}_earthworks_stage1_{stamp}"


def _validate_pdfs(pdfs: list[Path]) -> None:
    for pdf in pdfs:
        if not pdf.exists():
            raise FileNotFoundError(f"PDF not found: {pdf}")
        if not pdf.is_file():
            raise ValueError(f"Not a file: {pdf}")
        if pdf.suffix.lower() != ".pdf":
            raise ValueError(f"Not a PDF file: {pdf}")
        if pdf.stat().st_size == 0:
            raise ValueError(f"PDF is empty (0 bytes): {pdf}")


def _python() -> str:
    return sys.executable


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Create earthworks Stage1 job from PDF files")
    p.add_argument("--project-name", required=True, help="Human-readable project name (used for job_id slug)")
    p.add_argument("--pdf", nargs="+", required=True, type=Path, dest="pdfs", help="PDF file(s) to parse")
    p.add_argument(
        "--sharing",
        default="anyone_writer",
        choices=["owner_only", "anyone_reader", "anyone_writer"],
        help="Google Sheet sharing policy (default: anyone_writer)",
    )
    p.add_argument("--jobs-root", type=Path, default=None, help="Override Stage1 jobs root directory")
    p.add_argument("--json", action="store_true", dest="json_output", help="Print result as JSON")
    args = p.parse_args(argv)

    pdfs = [Path(pdf).resolve() for pdf in args.pdfs]
    _validate_pdfs(pdfs)

    jobs_root = Path(args.jobs_root).resolve() if args.jobs_root else _DEFAULT_JOBS_ROOT
    job_id = _make_job_id(args.project_name)
    job_dir = jobs_root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    # Copy PDFs to job_dir/input_pdfs/
    input_pdfs_dir = job_dir / "input_pdfs"
    input_pdfs_dir.mkdir(parents=True, exist_ok=True)
    input_pdf_records = []
    for pdf in pdfs:
        dest = input_pdfs_dir / pdf.name
        shutil.copy2(pdf, dest)
        input_pdf_records.append({
            "name": pdf.name,
            "sha256": _sha256(dest),
            "size_bytes": dest.stat().st_size,
        })

    # Run parser v3
    parser_run_dir = job_dir / "parser_runs" / "run_001"
    parser_run_dir.mkdir(parents=True, exist_ok=True)
    v3_cmd = [
        _python(), str(RUN_V3),
        "--input-dir", str(input_pdfs_dir),
        "--out-dir", str(parser_run_dir),
        "--json",
    ]
    print(f"$ {shlex.join([str(c) for c in v3_cmd])}")
    v3_result = subprocess.run(v3_cmd, cwd=str(REPO_ROOT))
    if v3_result.returncode != 0:
        print(f"ERROR: parser v3 failed with exit code {v3_result.returncode}", file=sys.stderr)
        return v3_result.returncode

    parser_run_json_path = parser_run_dir / "parser_run.json"
    if not parser_run_json_path.exists():
        print(f"ERROR: parser_run.json not found at {parser_run_json_path}", file=sys.stderr)
        return 1
    parser_run_data = json.loads(parser_run_json_path.read_text(encoding="utf-8"))

    # Run Stage1 prepare
    stage1_cmd = [
        _python(), str(RUN_STAGE1), "prepare",
        "--project-name", args.project_name,
        "--job-id", job_id,
        "--artifacts-dir", str(parser_run_dir),
        "--sharing", args.sharing,
    ]
    print(f"$ {shlex.join([str(c) for c in stage1_cmd])}")
    stage1_result = subprocess.run(stage1_cmd, cwd=str(REPO_ROOT))
    if stage1_result.returncode != 0:
        print(f"ERROR: Stage1 prepare failed with exit code {stage1_result.returncode}", file=sys.stderr)
        return stage1_result.returncode

    # Update job_state
    state = init_or_update_from_stage1(job_dir)
    update_source_and_parser(job_dir, input_pdf_records, parser_run_data)

    print(f"create_job_from_pdf completed")
    print(f"- job_id: {job_id}")
    print(f"- job_dir: {job_dir}")
    print(f"- parser_run: {parser_run_json_path}")
    print(f"- input_pdfs: {len(input_pdf_records)}")
    print(f"- candidates: {parser_run_data.get('candidates_count')}")
    print(f"- parser_errors: {parser_run_data.get('errors', [])}")

    if args.json_output:
        output = {
            "job_id": job_id,
            "job_dir": str(job_dir),
            "project_name": args.project_name,
            "sharing": args.sharing,
            "input_pdfs": input_pdf_records,
            "parser_run": {
                "pages_count": parser_run_data.get("pages_count"),
                "tables_count": parser_run_data.get("tables_count"),
                "logical_pages_count": parser_run_data.get("logical_pages_count"),
                "candidates_count": parser_run_data.get("candidates_count"),
                "errors": parser_run_data.get("errors", []),
            },
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
