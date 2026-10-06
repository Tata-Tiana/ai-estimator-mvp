"""Runs every section end to end from one filled review workbook and saves each one's result JSON
into a single results_dir - the missing middle step between core.job_runner.run_section()/
run_floor_slab_pours() (run one section/the floor-slab group) and
export_calculator_results_to_estimate_workbook.py (reads a results_dir, builds the final smeta).

Before this script, no such driver existed anywhere in the pipeline for the other 6 sections -
run_section() has only ever been called interactively/for adapter verification (confirmed by
searching the whole pipeline: FLOOR_SLAB_UNIFICATION_PLAN.md's own P2/P3 research, and several
one-off output/trc_calculator_run_* folders in this directory that show someone did this by hand,
repeatedly, with no script backing it up). This script is that missing piece, for all 8 sections at
once - the 6 SECTION_ORDER sections via run_section(), floor_slab_1/floor_slab_2 via
build_floor_slabs_result() (P2/P3).

Each <section_code>_result.json is saved in the same shape run_section() itself returns
(section_code/workbook_path/normalized_review/calculator_input/result) - matches the shape already
used in every real output/trc_calculator_run_* folder found in this repo, and
export_calculator_results_to_estimate_workbook.py's own _load_lines() already unwraps either that
shape or a bare result dict.

Does NOT stop at the first section's error: a real project setup commonly has more than one
section with a missing/bad field, and fixing them one at a time via repeated single-section runs
is slower than seeing every problem at once. Sections that fail are reported clearly and their
result file is NOT written (never leave a stale/partial file that export_calculator_results_to_
estimate_workbook.py might silently pick up) - the build only succeeds (exit 0) when every section
succeeded.

Usage:
    python3 build_all_section_results.py --workbook <filled review_workbook.xlsx> \
        --results-dir <dir for export_calculator_results_to_estimate_workbook.py --results-dir>
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent / "review_to_calculator"))
from core.job_runner import JobRunnerError, build_floor_slabs_result, run_section  # noqa: E402

from export_calculator_results_to_estimate_workbook import (  # noqa: E402
    FLOOR_SLABS_RESULT_FILENAME,
    SECTION_ORDER,
)


def build_all_section_results(workbook_path: str | Path, results_dir: Path) -> dict[str, Any]:
    results_dir.mkdir(parents=True, exist_ok=True)
    succeeded: list[str] = []
    failed: list[tuple[str, str]] = []

    for section_code, _title in SECTION_ORDER:
        try:
            result = run_section(section_code, workbook_path)
        except (JobRunnerError, ValueError) as exc:
            failed.append((section_code, str(exc)))
            continue
        except Exception as exc:  # noqa: BLE001 - report any failure, don't let one section crash the whole build
            failed.append((section_code, f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"))
            continue
        out_path = results_dir / f"{section_code}_result.json"
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        succeeded.append(section_code)

    try:
        floor_slabs_result = build_floor_slabs_result(workbook_path)
    except (JobRunnerError, ValueError) as exc:
        failed.append(("floor_slabs", str(exc)))
    except Exception as exc:  # noqa: BLE001
        failed.append(("floor_slabs", f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"))
    else:
        out_path = results_dir / FLOOR_SLABS_RESULT_FILENAME
        out_path.write_text(json.dumps(floor_slabs_result, ensure_ascii=False, indent=2), encoding="utf-8")
        succeeded.append(f"floor_slabs ({len(floor_slabs_result['pours'])} pours)")

    return {"succeeded": succeeded, "failed": failed}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", required=True, help="Filled review_workbook.xlsx path.")
    parser.add_argument(
        "--results-dir",
        required=True,
        help="Directory to write every section's <code>_result.json into - pass the same path to "
        "export_calculator_results_to_estimate_workbook.py's --results-dir afterward.",
    )
    args = parser.parse_args()

    outcome = build_all_section_results(args.workbook, Path(args.results_dir))

    print(f"succeeded ({len(outcome['succeeded'])}):")
    for code in outcome["succeeded"]:
        print(f"  - {code}")

    if outcome["failed"]:
        print(f"\nFAILED ({len(outcome['failed'])}):")
        for code, message in outcome["failed"]:
            first_line = message.splitlines()[0] if message else ""
            print(f"  - {code}: {first_line}")
        print(
            "\nNo result file was written for a failed section - fix the underlying issue "
            "(missing/blank field on sheet 01, usually) and re-run this whole script."
        )
        return 1

    print(f"\nAll sections built. Results dir: {Path(args.results_dir).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
