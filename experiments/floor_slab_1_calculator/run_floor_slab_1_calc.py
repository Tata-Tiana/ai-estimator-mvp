from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from floor_slab_1_calculator import calculate_floor_slab_1


BASE_DIR = Path(__file__).resolve().parent
CASES_DIR = BASE_DIR / "cases"
DEFAULT_CASE_DIR = CASES_DIR / "test_floor_slab_1"
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


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get_nested(data: Any, dotted_path: str) -> Any:
    current = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def compare_values(expected_value: Any, actual_value: Any, tolerance: float = 0.001) -> tuple[bool, Any]:
    if isinstance(expected_value, int) and isinstance(actual_value, int):
        return expected_value == actual_value, actual_value - expected_value
    if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
        diff = round(actual_value - expected_value, 6)
        return abs(diff) <= tolerance, diff
    return expected_value == actual_value, None


def compare_with_expected(calculation: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    lines_by_code = {line["code"]: line for line in calculation["estimate_lines"]}

    def add(key: str, expected_value: Any, actual_value: Any) -> None:
        ok, diff = compare_values(expected_value, actual_value)
        items.append(
            {
                "key": key,
                "expected": expected_value,
                "actual": actual_value,
                "diff": diff,
                "status": "ok" if ok else "mismatch",
            }
        )

    for key, expected_value in expected.get("totals", {}).items():
        add(f"totals.{key}", expected_value, calculation["totals"].get(key))

    for block_name, block_expected in expected.get("calculation_blocks", {}).items():
        actual_block = calculation["calculation_blocks"].get(block_name, {})
        for key, expected_value in block_expected.items():
            add(f"calculation_blocks.{block_name}.{key}", expected_value, get_nested(actual_block, key))

    for code, line_expected in expected.get("estimate_lines", {}).items():
        actual_line = lines_by_code.get(code)
        if actual_line is None:
            add(f"estimate_lines.{code}", "present", "missing")
            continue
        for key, expected_value in line_expected.items():
            add(f"estimate_lines.{code}.{key}", expected_value, actual_line.get(key))

    ok_count = sum(1 for item in items if item["status"] == "ok")
    mismatch_count = len(items) - ok_count
    return {
        "status": "ok" if mismatch_count == 0 else "mismatch",
        "ok_count": ok_count,
        "mismatch_count": mismatch_count,
        "items": items,
    }


def flatten(prefix: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {prefix: value}
    result = {}
    for key, child in value.items():
        child_prefix = f"{prefix}.{key}" if prefix else key
        if isinstance(child, dict):
            result.update(flatten(child_prefix, child))
        elif isinstance(child, list):
            result[child_prefix] = json.dumps(child, ensure_ascii=False)
        else:
            result[child_prefix] = child
    return result


def dict_table(rows: dict[str, Any]) -> list[str]:
    lines = ["| Показатель | Значение |", "| --- | ---: |"]
    for key, value in rows.items():
        lines.append(f"| `{key}` | `{value}` |")
    return lines


def lines_table(lines_data: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| code | name | quantity_raw | quantity_display | unit | line_type | material_total_raw | material_total | work_total_raw | work_total | line_total_raw | line_total |",
        "| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in lines_data:
        lines.append(
            "| "
            f"`{item['code']}` | {item['name']} | `{item['quantity_raw']}` | `{item['quantity_display']}` | `{item['unit']}` | `{item['line_type']}` | "
            f"`{item['material_total_raw']}` | `{item['material_total']}` | `{item['work_total_raw']}` | `{item['work_total']}` | "
            f"`{item['line_total_raw']}` | `{item['line_total']}` |"
        )
    return lines


def comparison_table(comparison: dict[str, Any]) -> list[str]:
    lines = ["| Показатель | Ожидание | Получено | Разница | Статус |", "| --- | ---: | ---: | ---: | --- |"]
    for item in comparison["items"]:
        diff = "" if item["diff"] is None else item["diff"]
        lines.append(f"| `{item['key']}` | `{item['expected']}` | `{item['actual']}` | `{diff}` | `{item['status']}` |")
    return lines


def collect_notes(calculation: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    for line in calculation["estimate_lines"]:
        for note in line.get("notes", []):
            notes.append(f"`{line['code']}`: {note}")
    return notes


def format_markdown(case_name: str, calculation: dict[str, Any], comparison: dict[str, Any]) -> str:
    notes = collect_notes(calculation)
    warnings = calculation.get("warnings", [])
    return "\n".join(
        [
            f"# Расчёт монолитной плиты перекрытия 1-го этажа: {case_name}",
            "",
            f"Проект: `{calculation['case_meta']['project']}`",
            "",
            "## Итоги",
            *dict_table(calculation["totals"]),
            "",
            "## Comparison Summary",
            f"- status: `{comparison['status']}`",
            f"- ok: `{comparison['ok_count']}`",
            f"- mismatch: `{comparison['mismatch_count']}`",
            "",
            "## Расчётные блоки",
            *dict_table(flatten("", calculation["calculation_blocks"])),
            "",
            "## Строки серой внутренней сметы",
            *lines_table(calculation["estimate_lines"]),
            "",
            "## Warnings / Notes",
            *(f"- {warning}" for warning in warnings),
            *(f"- {note}" for note in notes),
            *([] if warnings or notes else ["Предупреждений и заметок нет."]),
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
    input_data = load_json(input_path)
    expected = load_json(expected_path)
    calculation = calculate_floor_slab_1(input_data)
    comparison = compare_with_expected(calculation, expected)
    payload = {
        **calculation,
        "case_name": case_name,
        "input_path": str(input_path),
        "expected_path": str(expected_path) if expected_path else None,
        "expected": expected,
        "comparison": comparison,
    }
    save_json(output_dir / "floor_slab_1_result.json", payload)
    (output_dir / "floor_slab_1_result.md").write_text(
        format_markdown(case_name, payload, comparison),
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    result = run(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps({"totals": result["totals"], "comparison": result["comparison"]}, ensure_ascii=False, indent=2))
