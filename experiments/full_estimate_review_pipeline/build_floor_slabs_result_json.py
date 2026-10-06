"""P3 (FLOOR_SLAB_UNIFICATION_PLAN.md): CLI wrapper around
review_to_calculator.core.job_runner.build_floor_slabs_result() - runs floor_slab_1+floor_slab_2
off a filled review workbook and writes floor_slabs_result.json, the file
export_calculator_results_to_estimate_workbook.py's dynamic floor-slabs block reads.

There's no existing "run every section end to end and save its JSON" driver anywhere in this
pipeline (run_section() itself is only ever called interactively/from adapter-verification code,
per FLOOR_SLAB_UNIFICATION_PLAN.md's own P2/P3 research) - this script is that missing piece for
floor_slab_1/floor_slab_2 specifically, not a general-purpose one for all 8 sections.

Usage:
    python3 build_floor_slabs_result_json.py --workbook <filled review_workbook.xlsx> \
        --results-dir <same dir export_calculator_results_to_estimate_workbook.py will read from>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "review_to_calculator"))
from core.job_runner import build_floor_slabs_result  # noqa: E402

RESULT_FILENAME = "floor_slabs_result.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", required=True, help="Filled review_workbook.xlsx path.")
    parser.add_argument(
        "--results-dir",
        required=True,
        help="Directory to write floor_slabs_result.json into (same one --results-dir points at "
        "for export_calculator_results_to_estimate_workbook.py).",
    )
    args = parser.parse_args()

    result = build_floor_slabs_result(args.workbook)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / RESULT_FILENAME
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{out_path.resolve()} ({len(result['pours'])} pours)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
