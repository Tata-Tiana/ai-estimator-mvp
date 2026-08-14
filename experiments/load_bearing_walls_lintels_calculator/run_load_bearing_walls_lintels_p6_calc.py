from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from load_bearing_walls_lintels_p6_calculator import (
    P6LoadBearingWallsLintelsInput,
    calculate_load_bearing_walls_lintels_p6,
)


BASE_DIR = Path(__file__).resolve().parent
CASES_DIR = BASE_DIR / "cases"
DEFAULT_CASE_DIR = CASES_DIR / "test_p6_zone_model_basic"
OUTPUT_DIR = BASE_DIR / "output"


def resolve_case_path(raw_path: str | None = None) -> tuple[str, Path, Path | None]:
    case_path = Path(raw_path) if raw_path else DEFAULT_CASE_DIR
    if not case_path.is_absolute():
        case_path = Path.cwd() / case_path
    case_path = case_path.resolve()
    if case_path.is_dir():
        expected_path = case_path / "expected.json"
        return case_path.name, case_path / "input.json", expected_path if expected_path.exists() else None
    if case_path.name != "input.json":
        raise ValueError("Pass a case directory or a path to input.json")
    expected_path = case_path.parent / "expected.json"
    return case_path.parent.name, case_path, expected_path if expected_path.exists() else None


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def nested(data: Any, dotted_path: str) -> Any:
    current = data
    for part in dotted_path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def compare_with_expected(calculation: dict[str, Any], expected_path: Path | None, tolerance: float = 0.001) -> list[dict[str, Any]]:
    if expected_path is None:
        return []
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    lines_by_code = {item["code"]: item for item in calculation["estimate_lines"]}
    comparison: list[dict[str, Any]] = []

    def add(key: str, expected_value: Any, actual_value: Any) -> None:
        if isinstance(expected_value, int) and isinstance(actual_value, int):
            diff = actual_value - expected_value
            ok = diff == 0
        elif isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
            diff = round(actual_value - expected_value, 6)
            ok = abs(diff) <= tolerance
        else:
            diff = None
            ok = actual_value == expected_value
        comparison.append(
            {
                "key": key,
                "expected": expected_value,
                "actual": actual_value,
                "diff": diff,
                "status": "ok" if ok else "mismatch",
            }
        )

    for code, fields in expected.get("estimate_lines", {}).items():
        actual_line = lines_by_code.get(code, {})
        for field, expected_value in fields.items():
            add(f"estimate_lines.{code}.{field}", expected_value, actual_line.get(field))
    for path, expected_value in expected.get("calculation_blocks", {}).items():
        add(f"calculation_blocks.{path}", expected_value, nested(calculation["calculation_blocks"], path))
    return comparison


def comparison_table(comparison: list[dict[str, Any]]) -> list[str]:
    if not comparison:
        return ["Expected values are not provided for this case."]
    lines = ["| key | expected | actual | diff | status |", "| --- | ---: | ---: | ---: | --- |"]
    for item in comparison:
        diff = "" if item["diff"] is None else item["diff"]
        lines.append(f"| `{item['key']}` | `{item['expected']}` | `{item['actual']}` | `{diff}` | `{item['status']}` |")
    return lines


def lines_table(lines_data: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| code | name | quantity | unit | material_total | work_total | line_total |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: |",
    ]
    for item in lines_data:
        lines.append(
            "| "
            f"`{item['code']}` | {item['name']} | `{item['quantity']}` | `{item['unit']}` | "
            f"`{item['material_total']}` | `{item['work_total']}` | `{item['line_total']}` |"
        )
    return lines


def render_markdown(case_name: str, calculation: dict[str, Any], comparison: list[dict[str, Any]]) -> str:
    totals = calculation["internal_totals"]
    lines = [
        f"# P6 расчёт несущих стен и перемычек: {case_name}",
        "",
        "## Итоги",
        "",
        f"- Материалы: `{totals['internal_materials_total']}`",
        f"- Работы: `{totals['internal_works_total']}`",
        f"- Итого: `{totals['internal_section_total']}`",
        "",
        "## Проверка expected.json",
        "",
        *comparison_table(comparison),
        "",
        "## Строки сметы",
        "",
        *lines_table(calculation["estimate_lines"]),
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    case_name, input_path, expected_path = resolve_case_path(sys.argv[1] if len(sys.argv) > 1 else None)
    raw_data = json.loads(input_path.read_text(encoding="utf-8"))
    input_data = P6LoadBearingWallsLintelsInput.from_dict(raw_data)
    calculation = calculate_load_bearing_walls_lintels_p6(input_data)
    comparison = compare_with_expected(calculation, expected_path)

    output_dir = OUTPUT_DIR / case_name
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "case_name": case_name,
        "input_path": str(input_path),
        "expected_path": str(expected_path) if expected_path else None,
        "comparison": comparison,
        **calculation,
    }
    save_json(output_dir / "load_bearing_walls_lintels_p6_result.json", payload)
    (output_dir / "load_bearing_walls_lintels_p6_result.md").write_text(
        render_markdown(case_name, calculation, comparison),
        encoding="utf-8",
    )
    mismatches = [item for item in comparison if item["status"] != "ok"]
    print(json.dumps({"case_name": case_name, "output_dir": str(output_dir), "mismatches": len(mismatches)}, ensure_ascii=False))
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
