from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from load_bearing_walls_lintels_calculator import (
    LoadBearingWallsLintelsInput,
    calculate_load_bearing_walls_lintels,
)


BASE_DIR = Path(__file__).resolve().parent
CASES_DIR = BASE_DIR / "cases"
DEFAULT_CASE_DIR = CASES_DIR / "test_load_bearing_walls_lintels"
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


def load_input(path: Path) -> LoadBearingWallsLintelsInput:
    return LoadBearingWallsLintelsInput.from_dict(json.loads(path.read_text(encoding="utf-8")))


def load_expected(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


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


def compare_with_expected(calculation: dict[str, Any], expected: dict[str, Any], tolerance: float = 0.001) -> list[dict[str, Any]]:
    comparison: list[dict[str, Any]] = []
    lines_by_code = {line["code"]: line for line in calculation["estimate_lines"]}

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

    for section, values in expected.items():
        if section == "calculation_blocks":
            for block_name, block_expected in values.items():
                actual_block = calculation["calculation_blocks"].get(block_name, {})
                for key, expected_value in block_expected.items():
                    add(f"calculation_blocks.{block_name}.{key}", expected_value, nested(actual_block, key))
        elif section == "estimate_lines":
            for code, line_expected in values.items():
                actual_line = lines_by_code.get(code, {})
                for key, expected_value in line_expected.items():
                    add(f"estimate_lines.{code}.{key}", expected_value, actual_line.get(key))
        elif section == "internal_totals":
            for key, expected_value in values.items():
                add(f"internal_totals.{key}", expected_value, calculation["internal_totals"].get(key))
        else:
            add(section, values, calculation.get(section))
    return comparison


def dict_table(rows: dict[str, Any]) -> list[str]:
    lines = ["| Показатель | Значение |", "| --- | ---: |"]
    for key, value in rows.items():
        lines.append(f"| `{key}` | `{value}` |")
    return lines


def flatten(prefix: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {prefix: value}
    result = {}
    for key, child in value.items():
        child_prefix = f"{prefix}.{key}" if prefix else key
        if isinstance(child, dict):
            result.update(flatten(child_prefix, child))
        else:
            result[child_prefix] = child
    return result


def lines_table(lines_data: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| code | name | quantity | display_quantity | unit | material_unit_price | material_total_raw | material_total | work_unit_price | work_total_raw | work_total | line_total_raw | line_total | case_specific |",
        "| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in lines_data:
        lines.append(
            "| "
            f"`{item['code']}` | {item['name']} | `{item['quantity']}` | `{item.get('display_quantity', '')}` | `{item['unit']}` | "
            f"`{item['material_unit_price']}` | `{item['material_total_raw']}` | `{item['material_total']}` | "
            f"`{item['work_unit_price']}` | `{item['work_total_raw']}` | `{item['work_total']}` | "
            f"`{item['line_total_raw']}` | `{item['line_total']}` | `{item['is_case_specific']}` |"
        )
    return lines


def comparison_table(comparison: list[dict[str, Any]]) -> list[str]:
    if not comparison:
        return ["Expected values are not provided for this case."]
    lines = ["| Показатель | Ожидание | Получено | Разница | Статус |", "| --- | ---: | ---: | ---: | --- |"]
    for item in comparison:
        diff = "" if item["diff"] is None else item["diff"]
        lines.append(f"| `{item['key']}` | `{item['expected']}` | `{item['actual']}` | `{diff}` | `{item['status']}` |")
    return lines


def format_markdown(case_name: str, input_data: LoadBearingWallsLintelsInput, calculation: dict[str, Any], comparison: list[dict[str, Any]]) -> str:
    input_lines = [f"- `{key}`: `{value}`" for key, value in input_data.to_dict().items()]
    block_rows = flatten("", calculation["calculation_blocks"])
    warning_lines = [f"- {warning}" for warning in calculation.get("warnings", [])] or ["Предупреждений нет."]
    return "\n".join(
        [
            f"# Расчёт несущих стен и перемычек: {case_name}",
            "",
            f"Проект: `{input_data.project_name}`",
            "",
            "## Входные параметры",
            *input_lines,
            "",
            "## Расчётные блоки",
            *dict_table(block_rows),
            "",
            "## Строки серой внутренней сметы",
            *lines_table(calculation["estimate_lines"]),
            "",
            "## Итоги raw/rounded",
            *dict_table(calculation["internal_totals"]),
            "",
            "## Warnings",
            *warning_lines,
            "",
            "## Comparison",
            *comparison_table(comparison),
            "",
        ]
    )


def run(raw_case_path: str | None = None) -> dict[str, Any]:
    case_name, input_path, expected_path = resolve_case_path(raw_case_path)
    output_dir = OUTPUT_DIR / case_name
    output_dir.mkdir(parents=True, exist_ok=True)
    input_data = load_input(input_path)
    expected = load_expected(expected_path)
    calculation = calculate_load_bearing_walls_lintels(input_data)
    comparison = compare_with_expected(calculation, expected)
    payload = {
        "case_name": case_name,
        "input_path": str(input_path),
        "expected_path": str(expected_path) if expected_path else None,
        "inputs": calculation["inputs"],
        "calculation_blocks": calculation["calculation_blocks"],
        "estimate_lines": calculation["estimate_lines"],
        "internal_totals": calculation["internal_totals"],
        "expected": expected,
        "comparison": comparison,
        "warnings": calculation["warnings"],
    }
    save_json(output_dir / "load_bearing_walls_lintels_result.json", payload)
    (output_dir / "load_bearing_walls_lintels_result.md").write_text(
        format_markdown(case_name, input_data, calculation, comparison),
        encoding="utf-8",
    )
    return calculation


if __name__ == "__main__":
    result = run(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps({"calculation_blocks": result["calculation_blocks"], "internal_totals": result["internal_totals"]}, ensure_ascii=False, indent=2))
