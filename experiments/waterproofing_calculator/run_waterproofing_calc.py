from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from waterproofing_calculator import WaterproofingInput, calculate_waterproofing


BASE_DIR = Path(__file__).resolve().parent
CASES_DIR = BASE_DIR / "cases"
DEFAULT_CASE_DIR = CASES_DIR / "test_waterproofing_foundation_slab"
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


def load_input(path: Path) -> WaterproofingInput:
    with path.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)
    return WaterproofingInput.from_dict(raw_data)


def load_expected(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")


def compare_with_expected(
    calculation: dict[str, Any],
    expected: dict[str, Any],
    tolerance: float = 0.001,
) -> list[dict[str, Any]]:
    comparison = []
    lines_by_code = {line["code"]: line for line in calculation["estimate_lines"]}

    def append_comparison(key: str, expected_value: Any, actual_value: Any) -> None:
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
                actual_block = calculation["calculation_blocks"].get(block_name, {})
                for key, expected_value in block_expected.items():
                    append_comparison(
                        f"calculation_blocks.{block_name}.{key}",
                        expected_value,
                        actual_block.get(key),
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
        elif section == "internal_totals":
            for key, expected_value in expected_values.items():
                append_comparison(
                    f"internal_totals.{key}",
                    expected_value,
                    calculation["internal_totals"].get(key),
                )
        else:
            append_comparison(section, expected_values, calculation.get(section))

    return comparison


def format_dict_table(rows: dict[str, Any]) -> list[str]:
    lines = ["| Показатель | Значение |", "| --- | ---: |"]
    for key, value in rows.items():
        lines.append(f"| `{key}` | `{value}` |")
    return lines


def format_estimate_lines_markdown(lines_data: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| code | name | quantity | display_quantity | unit | material_unit_price | material_total | work_unit_price | work_total | line_total |",
        "| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for line in lines_data:
        display_quantity = line.get("display_quantity", "")
        lines.append(
            "| "
            f"`{line['code']}` | "
            f"{line['name']} | "
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


def format_price_sources_markdown(lines_data: list[dict[str, Any]]) -> list[str]:
    has_live_sources = any("unit_price_source" in line for line in lines_data)
    if not has_live_sources:
        return ["Price source details are only shown for `price_registry_with_fallback` mode."]

    lines = [
        "| Строка сметы | price_code | старая цена | использованная цена | источник | предупреждение |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for line in lines_data:
        lines.append(
            "| "
            f"{line['name']} | "
            f"`{line.get('price_code', '')}` | "
            f"`{line.get('unit_price_original', '')}` | "
            f"`{line.get('unit_price_used', '')}` | "
            f"`{line.get('unit_price_source', '')}` | "
            f"{line.get('price_warning') or ''} |"
        )
    return lines


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


def format_markdown(
    case_name: str,
    input_data: WaterproofingInput,
    calculation: dict[str, Any],
    comparison: list[dict[str, Any]],
) -> str:
    inputs = input_data.to_dict()
    input_lines = [
        f"- `{key}`: `{value}`" for key, value in inputs.items() if value is not None
    ]
    waterproofing_block = calculation["calculation_blocks"]["waterproofing"]
    area_method = waterproofing_block.get("waterproofing_area_calc_method")
    area_source = waterproofing_block.get("waterproofing_area_source")
    if area_method == "spec_area":
        area_formula_lines = [
            "- Площадь гидроизоляции standard: `waterproofing_area_m2` берётся из спецификации проекта как площадь опалубки фундаментной плиты.",
        ]
    else:
        area_formula_lines = [
            "- Площадь гидроизоляции legacy: `waterproofing_area_m2 = slab_formwork_perimeter_m * slab_edge_height_m`.",
        ]
    is_live_pricing = (
        calculation.get("pricing_summary", {}).get("mode")
        == "price_registry_with_fallback"
    )
    pricing_sections = []
    if is_live_pricing:
        pricing_sections = [
            "## Источники цен",
            *format_price_sources_markdown(calculation["estimate_lines"]),
            "",
            "## Pricing summary",
            *format_dict_table(calculation.get("pricing_summary", {})),
            "",
            "## Warnings",
            *(f"- {warning}" for warning in calculation.get("warnings", [])),
            "",
        ]

    return "\n".join(
        [
            f"# Расчёт гидроизоляции фундаментной плиты: {case_name}",
            "",
            f"Проект: `{input_data.project_name}`",
            "",
            "## Входные параметры",
            *input_lines,
            "",
            "## Формулы",
            *area_formula_lines,
            f"- Использованный метод площади: `{area_method}`.",
            f"- Источник площади: `{area_source}`.",
            f"- Площадь, которая ушла в работы, праймер и мастику: `{waterproofing_block.get('waterproofing_area_m2')}` м2.",
            "- Праймер: `primer_required_liters = waterproofing_area_m2 * primer_consumption_l_per_m2`; `primer_units = ceil(primer_required_liters / primer_canister_volume_l)`.",
            "- Мастика: `mastic_required_kg = waterproofing_area_m2 * mastic_consumption_kg_per_m2_per_layer * mastic_layers`; `mastic_units = ceil(mastic_required_kg / mastic_bucket_weight_kg)`.",
            "- Основная площадь работ по ЭППС 100 мм торец/борт плиты: если в проекте есть явная площадь `eps100_wall_insulation_area_m2`, используется она; иначе fallback `eps100_wall_volume_m3 / eps100_wall_thickness_m`.",
            "- Геометрическая проверка по участкам без утепления включается только если заданы `slab_formwork_perimeter_m`, `slab_edge_height_m` и `non_insulated_edge_lengths_m`.",
            "- Если геометрическая проверка выключена, площадь ЭППС берётся из спецификации через `объём / толщину`.",
            f"- Геометрическая проверка включена: `{waterproofing_block.get('eps100_wall_geometry_check_enabled')}`.",
            "",
            "## Расчётные блоки",
            *format_dict_table(waterproofing_block),
            "",
            "## Строки серой внутренней сметы",
            *format_estimate_lines_markdown(calculation["estimate_lines"]),
            "",
            "## Итоги серой внутренней себестоимости",
            *format_dict_table(calculation["internal_totals"]),
            "",
            *pricing_sections,
            "## Comparison",
            *format_comparison_markdown(comparison),
            "",
        ]
    )


def save_markdown(
    path: Path,
    case_name: str,
    input_data: WaterproofingInput,
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
    calculation = calculate_waterproofing(input_data)
    comparison = compare_with_expected(calculation, expected)
    is_live_pricing = (
        calculation.get("pricing_summary", {}).get("mode")
        == "price_registry_with_fallback"
    )

    result_payload = {
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
    if is_live_pricing:
        result_payload["pricing_summary"] = calculation.get("pricing_summary", {})

    save_json(
        case_output_dir / "waterproofing_result.json",
        result_payload,
    )
    save_markdown(
        case_output_dir / "waterproofing_result.md",
        case_name,
        input_data,
        calculation,
        comparison,
    )

    if expected_path is None:
        save_json(
            input_path.parent / "result.json",
            result_payload,
        )
        save_markdown(
            input_path.parent / "result.md",
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
