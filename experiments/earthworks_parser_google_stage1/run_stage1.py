from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime

from config import DATA_DIR, DEFAULT_PROJECT_NAME, EXPERIMENT_DIR
from google_sheets.google_sheet_publisher import publish_workbook_if_configured
from google_sheets.review_workbook_builder import build_review_workbook
from parser.earthworks_v3_adapter import extract_earthworks_parameters
from pricing.earthworks_price_resolver import resolve_earthworks_prices
from pricing.google_price_registry_reader import load_price_registry_snapshot
from reports.anti_cheat import run_anti_cheat
from reports.report_builder import write_reports
from source_paths import job_dir


HUMAN_REVIEW_VERSION = "earthworks_stage1_human_review_v10"


def make_job_id(project_name: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in project_name).strip("_") or "project"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{slug}_earthworks_stage1_{stamp}"


def cmd_prepare(args: argparse.Namespace) -> int:
    project_name = args.project_name or DEFAULT_PROJECT_NAME
    current_job_dir = job_dir(args.job_id or make_job_id(project_name))
    current_job_dir.mkdir(parents=True, exist_ok=True)

    extracted = extract_earthworks_parameters()
    (current_job_dir / "extracted").mkdir(parents=True, exist_ok=True)
    (current_job_dir / "extracted" / "earthworks_extracted_parameters.json").write_text(
        json.dumps(extracted, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    registry_rows, registry_warnings = load_price_registry_snapshot(current_job_dir)
    resolved = resolve_earthworks_prices(current_job_dir, registry_rows)
    price_resolution = resolved["resolution"]

    workbook_path = build_review_workbook(current_job_dir, extracted, price_resolution, project_name)
    publisher_result = publish_workbook_if_configured(
        workbook_path,
        f"Земляные работы — parser stage1 — {project_name} — {HUMAN_REVIEW_VERSION}",
    )
    (current_job_dir / "google").mkdir(parents=True, exist_ok=True)
    (current_job_dir / "google" / "google_sheet_metadata.json").write_text(
        json.dumps(publisher_result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    write_reports(current_job_dir, extracted, price_resolution, publisher_result, registry_warnings)
    run_anti_cheat(current_job_dir, EXPERIMENT_DIR)

    print("Earthworks stage1 prepare completed")
    print(f"- job: {current_job_dir}")
    print(f"- review_workbook: {workbook_path}")
    print(f"- google_status: {publisher_result.get('status')}")
    if publisher_result.get("url"):
        print(f"- google_sheet: {publisher_result['url']}")
    print(f"- price_resolution: {current_job_dir / 'pricing' / 'earthworks_price_resolution.json'}")
    print(f"- internal_prices: {current_job_dir / 'pricing' / 'earthworks_internal_prices.json'}")
    print(f"- report: {current_job_dir / 'reports' / 'earthworks_price_resolution_report.md'}")
    return 0


def cmd_clean(args: argparse.Namespace) -> int:
    jobs_dir = DATA_DIR / "jobs"
    removed: list[str] = []
    if args.job_id:
        targets = [jobs_dir / args.job_id]
    else:
        targets = [path for path in jobs_dir.iterdir() if path.is_dir()] if jobs_dir.exists() else []

    for target in targets:
        if not target.exists():
            continue
        if target.parent != jobs_dir:
            raise ValueError(f"Refusing to remove path outside jobs dir: {target}")
        shutil.rmtree(target)
        removed.append(str(target))

    jobs_dir.mkdir(parents=True, exist_ok=True)
    print("Earthworks stage1 clean completed")
    if removed:
        print("Removed jobs:")
        for path in removed:
            print(f"- {path}")
    else:
        print("No jobs to remove.")
    print("Preserved:")
    print(f"- input PDFs dir: {DATA_DIR / 'input_pdfs'}")
    print("- OAuth files, .env, source code, v3 parser outputs, and price registry")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Earthworks parser Google stage1")
    subparsers = parser.add_subparsers(dest="command")
    prepare = subparsers.add_parser("prepare", help="Build earthworks review sheet and price resolution")
    prepare.add_argument("--project-name", default=DEFAULT_PROJECT_NAME)
    prepare.add_argument("--job-id", default="")
    clean = subparsers.add_parser("clean", help="Remove generated stage1 job outputs only")
    clean.add_argument("--job-id", default="", help="Remove one job. If omitted, remove all stage1 jobs.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "clean":
        return cmd_clean(args)
    if args.command == "prepare":
        return cmd_prepare(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
