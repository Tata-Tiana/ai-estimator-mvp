from __future__ import annotations

import argparse
from pathlib import Path

from calculation_runner import run_calculation_runner


def main() -> int:
    parser = argparse.ArgumentParser(description="Run calculators from generated input_builder inputs")
    parser.add_argument("case_dir", help="Path to calculation_runner case directory")
    args = parser.parse_args()

    case_dir = Path(args.case_dir).resolve()
    result = run_calculation_runner(case_dir)
    print(f"mode: {result['mode']}")
    print(f"sections_enabled: {result['totals']['sections_enabled']}")
    print(f"sections_completed: {result['totals']['sections_completed']}")
    print(f"sections_failed: {result['totals']['sections_failed']}")
    print(f"sections_skipped: {result['totals']['sections_skipped']}")
    print(f"grand_total: {result['totals']['grand_total']}")
    print(f"result_json: {case_dir / 'result.json'}")
    print(f"result_md: {case_dir / 'result.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
