from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from job_locator import resolve_stage1_job_dir

REPO_ROOT = Path(__file__).resolve().parents[2]
BASE_DIR = Path(__file__).resolve().parent
BUILD_FROM_GOOGLE_SHEET = BASE_DIR / "build_from_google_sheet.py"

_DEFAULT_OUT_ROOT = BASE_DIR / "outputs" / "jobs"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build earthworks estimate from Google Sheet by job ID"
    )
    parser.add_argument("--job-id", required=True, help="Job ID (Stage1 folder name)")
    parser.add_argument("--section-number", type=int, default=2)
    parser.add_argument("--estimate-date", default=None, help="DD.MM.YYYY for Excel tab")
    parser.add_argument("--jobs-root", default=None, help="Override default jobs root")
    parser.add_argument("--out-root", default=None, help="Override default outputs root")
    parser.add_argument("--section-row", type=int, default=11)
    parser.add_argument("--data-start-row", type=int, default=12)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    jobs_root = Path(args.jobs_root).resolve() if args.jobs_root else None
    try:
        stage1_job_dir = resolve_stage1_job_dir(args.job_id, jobs_root)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    out_root = Path(args.out_root).resolve() if args.out_root else _DEFAULT_OUT_ROOT
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = out_root / args.job_id / f"build_{timestamp}"

    python = sys.executable
    cmd = [
        python,
        str(BUILD_FROM_GOOGLE_SHEET),
        "--stage1-job-dir", str(stage1_job_dir),
        "--out-dir", str(out_dir),
        "--section-number", str(args.section_number),
        "--section-row", str(args.section_row),
        "--data-start-row", str(args.data_start_row),
    ]
    if args.estimate_date:
        cmd.extend(["--estimate-date", args.estimate_date])

    display = [str(p) for p in cmd]
    display[0] = "python"
    print(f"[build_job] job_id = {args.job_id}")
    print(f"[build_job] out_dir = {out_dir}")
    print(f"$ {shlex.join(display)}")
    print()

    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
