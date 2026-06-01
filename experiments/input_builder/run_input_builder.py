from __future__ import annotations

import argparse
from pathlib import Path

from input_builder import build_inputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Build calculator inputs from reviewed_parameters.xlsx")
    parser.add_argument("case_dir", help="Path to input_builder case directory")
    parser.add_argument(
        "--mode",
        choices=["strict", "demo_with_template_fallback"],
        default=None,
        help="Optional builder_mode override for smoke/demo checks",
    )
    args = parser.parse_args()

    case_dir = Path(args.case_dir).resolve()
    result = build_inputs(case_dir, mode_override=args.mode)
    print(f"builder_mode: {result['builder_mode']}")
    print(f"sections_enabled: {result['totals']['sections_enabled']}")
    print(f"sections_generated: {result['totals']['sections_generated']}")
    print(f"sections_blocked: {result['totals']['sections_blocked']}")
    print(f"missing_required_total: {result['totals']['missing_required_total']}")
    print(f"manual_required_total: {result['totals']['manual_required_total']}")
    print(f"result_json: {case_dir / 'result.json'}")
    print(f"result_md: {case_dir / 'result.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
