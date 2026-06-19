from __future__ import annotations

import argparse
import sys
from pathlib import Path

from anti_cheat import run_anti_cheat
from calculator_input_builder import (
    build_calculator_input,
    dump_json,
    load_json,
    render_calculator_input_report,
)
from constants import (
    CALCULATOR_INPUT_FILENAME,
    CALCULATOR_INPUT_REPORT_FILENAME,
    OUTPUT_DIR,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build calculator input from normalized review JSON")
    parser.add_argument(
        "--normalized-json",
        required=True,
        help="Path to review_values_normalized.json",
    )
    parser.add_argument(
        "--out",
        default=str(OUTPUT_DIR / CALCULATOR_INPUT_FILENAME),
        help="Path for earthworks_calculation_input.json",
    )
    parser.add_argument(
        "--report",
        default=str(OUTPUT_DIR / CALCULATOR_INPUT_REPORT_FILENAME),
        help="Path for calculator_input_report.md",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    normalized_path = Path(args.normalized_json)
    out_path = Path(args.out)
    report_path = Path(args.report)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    normalized_data = load_json(normalized_path)
    calculator_input, summary_info = build_calculator_input(normalized_data)

    dump_json(out_path, calculator_input)
    report_path.write_text(
        render_calculator_input_report(normalized_data, calculator_input, summary_info, out_path),
        encoding="utf-8",
    )

    print(f"calculator_input: {out_path}")
    print(f"report: {report_path}")

    anti_cheat_ok = run_anti_cheat(normalized_path, out_path)
    if anti_cheat_ok:
        print("anti_cheat: clean")
        return 0

    print("anti_cheat: dirty")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
