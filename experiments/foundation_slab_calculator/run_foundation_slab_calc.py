from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from foundation_slab_calculator import (
    FoundationSlabInput,
    calculate_foundation_slab,
)


BASE_DIR = Path(__file__).resolve().parent
CASES_DIR = BASE_DIR / "cases"
DEFAULT_CASE_DIR = CASES_DIR / "test_foundation_slab"
OUTPUT_DIR = BASE_DIR / "output"


def resolve_case_path(raw_path: str | None = None) -> tuple[str, Path, Path | None]:
    case_path = Path(raw_path) if raw_path else DEFAULT_CASE_DIR
    if not case_path.is_absolute():
        case_path = Path.cwd() / case_path
    case_path = case_path.resolve()

    if case_path.is_dir():
        case_name = case_path.name
        input_path = case_path / "input.json"
        expected_path = case_path / "expected.json"
        return case_name, input_path, expected_path if expected_path.exists() else None

    if case_path.name != "input.json":
        raise ValueError("Pass a case directory or a path to input.json")

    case_name = case_path.parent.name
    expected_path = case_path.parent / "expected.json"
    return case_name, case_path, expected_path if expected_path.exists() else None


def load_input(path: Path) -> FoundationSlabInput:
    with path.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)
    return FoundationSlabInput.from_dict(raw_data)


def load_expected(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")


def get_nested_value(data: dict[str, Any], dotted_path: str) -> Any:
    current: Any = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def compare_with_expected(
    calculation: dict[str, Any],
    expected: dict[str, Any],
    tolerance: float = 0.001,
) -> list[dict[str, Any]]:
    comparison = []
    lines_by_code = {line["code"]: line for line in calculation["estimate_lines"]}

    def append_comparison(
        key: str,
        expected_value: Any,
        actual_value: Any,
    ) -> None:
        if isinstance(expected_value, int) and isinstance(actual_value, int):
            is_ok = actual_value == expected_value
            diff = actual_value - expected_value
        elif isinstance(expected_value, (int, float)) and isinstance(
            actual_value,
            (int, float),
        ):
            diff = round(actual_value - expected_value, 6)
            is_ok = abs(diff) <= tolerance
        else:
            diff = None
            is_ok = actual_value == expected_value

        comparison.append(
            {
                "key": key,
                "expected": expected_value,
                "actual": actual_value,
                "diff": diff,
                "status": "ok" if is_ok else "mismatch",
            }
        )

    for section, expected_values in expected.items():
        if section == "calculation_blocks":
            for block_name, block_expected in expected_values.items():
                for key, expected_value in block_expected.items():
                    actual_value = get_nested_value(
                        calculation["calculation_blocks"].get(block_name, {}),
                        key,
                    )
                    append_comparison(
                        f"calculation_blocks.{block_name}.{key}",
                        expected_value,
                        actual_value,
                    )
        elif section == "internal_totals":
            for key, expected_value in expected_values.items():
                append_comparison(
                    f"internal_totals.{key}",
                    expected_value,
                    calculation["internal_totals"].get(key),
                )
        elif section == "estimate_lines":
            for line_code, line_expected in expected_values.items():
                actual_line = lines_by_code.get(line_code, {})
                for key, expected_value in line_expected.items():
                    append_comparison(
                        f"estimate_lines.{line_code}.{key}",
                        expected_value,
                        actual_line.get(key),
                    )
        else:
            append_comparison(section, expected_values, calculation.get(section))

    return comparison


def format_comparison_markdown(comparison: list[dict[str, Any]]) -> list[str]:
    if not comparison:
        return ["Expected values are not provided for this case."]

    lines = [
        "| Показатель | Ожидание | Получено | Разница | Статус |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for item in comparison:
        diff = "" if item["diff"] is None else item["diff"]
        lines.append(
            f"| `{item['key']}` | `{item['expected']}` | `{item['actual']}` | `{diff}` | `{item['status']}` |"
        )
    return lines


def format_dict_table(rows: dict[str, Any]) -> list[str]:
    lines = ["| Показатель | Значение |", "| --- | ---: |"]
    for key, value in rows.items():
        lines.append(f"| `{key}` | `{value}` |")
    return lines


def flatten_block(prefix: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {prefix: value}

    rows = {}
    for key, child in value.items():
        child_prefix = f"{prefix}.{key}" if prefix else key
        if isinstance(child, dict):
            rows.update(flatten_block(child_prefix, child))
        else:
            rows[child_prefix] = child
    return rows


def format_estimate_lines_markdown(lines_data: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| code | name | line_type | quantity | display_quantity | unit | material_unit_price | material_total | work_unit_price | work_total | line_total |",
        "| --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for line in lines_data:
        display_quantity = line.get("display_quantity", "")
        line_type = line.get("line_type", "")
        lines.append(
            "| "
            f"`{line['code']}` | "
            f"{line['name']} | "
            f"`{line_type}` | "
            f"`{line['quantity']}` | "
            f"`{display_quantity}` | "
            f"`{line['unit']}` | "
            f"`{line['material_unit_price']}` | "
            f"`{line['material_total']}` | "
            f"`{line['work_unit_price']}` | "
            f"`{line['work_total']}` | "
            f"`{line['line_total']}` |"
        )
    return lines


def format_confirmed_rules_markdown(calculation: dict[str, Any]) -> list[str]:
    rules = calculation["calculation_blocks"].get("confirmed_rules", [])
    return [f"- {rule}" for rule in rules]


def format_warnings_markdown(calculation: dict[str, Any]) -> list[str]:
    warnings = calculation.get("warnings", [])
    if not warnings:
        return ["Предупреждений нет."]
    return [f"- {warning}" for warning in warnings]


def format_markdown(
    case_name: str,
    input_data: FoundationSlabInput,
    calculation: dict[str, Any],
    comparison: list[dict[str, Any]],
) -> str:
    inputs = input_data.to_dict()
    input_lines = [
        f"- `{key}`: `{value}`" for key, value in inputs.items() if value is not None
    ]
    block_rows = flatten_block("", calculation["calculation_blocks"])

    return "\n".join(
        [
            f"# Расчёт фундаментной плиты: {case_name}",
            "",
            f"Проект: `{input_data.project_name}`",
            "",
            "## Входные параметры",
            *input_lines,
            "",
            "## Формулы",
            "- Монтаж мембраны: `quantity = membrane_area_m2`.",
            "- Planter Standard: `rolls = ceil(membrane_area_m2 * overlap / roll_area)`.",
            "- PLANTERBAND: `quantity = membrane_rolls * planterband_per_membrane_roll`.",
            "- Опалубка: `formwork_area = slab_formwork_perimeter_m * slab_edge_height_m`.",
            "- Фанера: `working_area` считает `ceil(formwork_area / plywood_sheet_working_area_m2)`, `actual_area_with_waste` считает через фактическую площадь листа и запас.",
            "- Пиломатериал: `timber_volume = formwork_area * timber_thickness_m`.",
            "- ЭППС 50 под плитой, работа: `area = eps50_under_slab_volume_m3 / eps50_thickness_m`.",
            "- Термовкладыш: `pieces = ceil(thermal_insert_length_m / thermal_insert_piece_length_m)`.",
            "- Арматура: вес -> м.п. -> запас 5% -> прутки -> закупочные м.п. -> стоимость.",
            "- Бетонирование: работа по проектному объёму, материал с запасом и округлением вверх.",
            "- Итог раздела: `internal_section_total = internal_materials_total + internal_works_total`.",
            "",
            "## Подтверждённые правила Елены",
            *format_confirmed_rules_markdown(calculation),
            "",
            "## Промежуточные расчёты",
            *format_dict_table(block_rows),
            "",
            "## Предупреждения",
            *format_warnings_markdown(calculation),
            "",
            "## Строки серой внутренней сметы",
            *format_estimate_lines_markdown(calculation["estimate_lines"]),
            "",
            "## Итоги серой внутренней сметы",
            *format_dict_table(calculation["internal_totals"]),
            "",
            "## Проверка с расчётом Елены",
            *format_comparison_markdown(comparison),
            "",
        ]
    )


def save_markdown(
    path: Path,
    case_name: str,
    input_data: FoundationSlabInput,
    calculation: dict[str, Any],
    comparison: list[dict[str, Any]],
) -> None:
    path.write_text(
        format_markdown(case_name, input_data, calculation, comparison),
        encoding="utf-8",
    )


def run(raw_case_path: str | None = None) -> dict[str, Any]:
    case_name, input_path, expected_path = resolve_case_path(raw_case_path)
    case_output_dir = OUTPUT_DIR / case_name
    case_output_dir.mkdir(parents=True, exist_ok=True)

    input_data = load_input(input_path)
    expected = load_expected(expected_path)
    calculation = calculate_foundation_slab(input_data)
    comparison = compare_with_expected(calculation, expected)

    save_json(
        case_output_dir / "foundation_slab_result.json",
        {
            "case_name": case_name,
            "input_path": str(input_path),
            "expected_path": str(expected_path) if expected_path else None,
            "inputs": calculation["inputs"],
            "calculation_blocks": calculation["calculation_blocks"],
            "warnings": calculation["warnings"],
            "estimate_lines": calculation["estimate_lines"],
            "internal_totals": calculation["internal_totals"],
            "expected": expected,
            "comparison": comparison,
        },
    )
    save_markdown(
        case_output_dir / "foundation_slab_result.md",
        case_name,
        input_data,
        calculation,
        comparison,
    )

    return calculation


if __name__ == "__main__":
    calculation_result = run(sys.argv[1] if len(sys.argv) > 1 else None)
    print(
        json.dumps(
            {
                "calculation_blocks": calculation_result["calculation_blocks"],
                "internal_totals": calculation_result["internal_totals"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
