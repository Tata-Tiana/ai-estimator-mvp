from __future__ import annotations

import argparse
import sys
from pathlib import Path

from job_locator import resolve_stage1_job_dir
from job_state import JOB_STATE_FILENAME, load_job_state


def _fmt(value: object, suffix: str = "") -> str:
    if value is None:
        return "—"
    return f"{value}{suffix}"


def print_status(state: dict) -> None:
    gs = state.get("google_sheet") or {}
    sharing = gs.get("sharing") or {}
    build = state.get("last_build") or {}
    totals = build.get("totals") or {}
    key_values = build.get("key_values") or {}

    print(f"Проект: {_fmt(state.get('project_name'))}")
    print(f"Job ID: {_fmt(state.get('job_id'))}")
    print(f"Раздел: {_fmt(state.get('section_title'))}")
    print()
    print("Google Sheet:")
    print(f"  status:  {_fmt(gs.get('status'))}")
    sharing_line = (
        f"{_fmt(sharing.get('mode'))} / {_fmt(sharing.get('status'))} / role={_fmt(sharing.get('role'))}"
    )
    print(f"  sharing: {sharing_line}")
    print(f"  url:     {_fmt(gs.get('url'))}")
    print()

    build_status = build.get("status", "not_built")
    print("Last build:")
    print(f"  status:           {build_status}")

    if build_status not in ("not_built", "running"):
        print(f"  excel_validation: {_fmt(build.get('excel_validation'))}")
        if totals:
            print(f"  section_total:    {_fmt(totals.get('section_total'))}")
            print(f"  materials:        {_fmt(totals.get('materials'))}")
            print(f"  works:            {_fmt(totals.get('works'))}")
        if key_values:
            print(f"  pit_area_m2:      {_fmt(key_values.get('pit_area_m2'))}")
            print(f"  consumables:      {_fmt(key_values.get('consumables_amount'))}")
            print(f"  excavation_m3:    {_fmt(key_values.get('manual_excavation_total_m3'))}")
            print(f"  excavator_shifts: {_fmt(key_values.get('excavator_shifts'))}")
        out_dir = build.get("out_dir", "")
        final_excel = build.get("final_excel", "")
        if out_dir and final_excel:
            print(f"  final_excel:      {out_dir}/{final_excel}")
        built_at = build.get("built_at") or build.get("failed_at")
        if built_at:
            print(f"  timestamp:        {built_at}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show earthworks job status")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--stage1-job-dir",
        help="Path to Stage1 job directory (contains job_state.json)",
    )
    group.add_argument(
        "--job-id",
        help="Job ID (folder name inside jobs root)",
    )
    parser.add_argument(
        "--jobs-root",
        default=None,
        help="Override default jobs root directory",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.stage1_job_dir:
        stage1_job_dir = Path(args.stage1_job_dir).resolve()
    else:
        jobs_root = Path(args.jobs_root).resolve() if args.jobs_root else None
        try:
            stage1_job_dir = resolve_stage1_job_dir(args.job_id, jobs_root)
        except (FileNotFoundError, NotADirectoryError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    job_state_path = stage1_job_dir / JOB_STATE_FILENAME
    if not job_state_path.exists():
        print(f"job_state.json not found. Run build_from_google_sheet.py first.")
        print(f"Expected: {job_state_path}")
        return 1

    state = load_job_state(stage1_job_dir)
    print_status(state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
