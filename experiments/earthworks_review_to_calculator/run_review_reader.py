from __future__ import annotations

import argparse
import sys
from pathlib import Path

from constants import NORMALIZED_JSON_FILENAME, OUTPUT_DIR, REPORT_MD_FILENAME
from review_workbook_reader import build_review_data, dump_review_json, render_review_report
from anti_cheat import run_anti_cheat


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read earthworks review workbook into normalized JSON")
    parser.add_argument("--workbook", required=True, help="Path to local review_workbook.xlsx")
    parser.add_argument("--out-dir", default=str(OUTPUT_DIR), help="Directory for normalized outputs")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_review_data(args.workbook)
    json_path = out_dir / NORMALIZED_JSON_FILENAME
    report_path = out_dir / REPORT_MD_FILENAME
    dump_review_json(data, json_path)
    report_path.write_text(render_review_report(data), encoding="utf-8")

    print(f"normalized_json: {json_path}")
    print(f"report: {report_path}")

    anti_cheat_result = run_anti_cheat(json_path)
    if anti_cheat_result:
        print("anti_cheat: clean")
        return 0

    print("anti_cheat: dirty")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

