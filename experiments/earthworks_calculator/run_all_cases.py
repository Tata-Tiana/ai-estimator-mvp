from __future__ import annotations

import json
from pathlib import Path

from run_earthworks_calc import CASES_DIR, OUTPUT_DIR, run


def iter_case_dirs() -> list[Path]:
    return sorted(path for path in CASES_DIR.iterdir() if (path / "input.json").exists())


def load_result(case_name: str) -> dict:
    result_path = OUTPUT_DIR / case_name / "earthworks_result.json"
    with result_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    case_dirs = iter_case_dirs()
    if not case_dirs:
        print("No cases found.")
        return

    failed_cases = []

    for case_dir in case_dirs:
        run(str(case_dir))
        result = load_result(case_dir.name)
        comparison = result.get("comparison", [])
        ok_count = sum(item.get("status") == "ok" for item in comparison)
        mismatch_count = len(comparison) - ok_count
        status = "ok" if mismatch_count == 0 else "mismatch"

        print(f"{case_dir.name} -> {status} ({ok_count}/{len(comparison)})")
        if mismatch_count:
            failed_cases.append(case_dir.name)

    if failed_cases:
        names = ", ".join(failed_cases)
        raise SystemExit(f"Cases with mismatches: {names}")


if __name__ == "__main__":
    main()
