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
REPO_ROOT = BASE_DIR.parents[1]
PRICING_DIR = REPO_ROOT / "experiments" / "pricing"
if str(PRICING_DIR) not in sys.path:
    sys.path.insert(0, str(PRICING_DIR))

from live_pricing import apply_live_pricing, price_sources_markdown, pricing_mode  # noqa: E402

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
    raw_data = json.loads(path.read_text(encoding="utf-8"))
    raw_data.pop("pricing", None)
    return LoadBearingWallsLintelsInput.from_dict(raw_data)


def load_raw_input(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def scaffolding_formula_markdown(calculation: dict[str, Any]) -> list[str]:
    scaffolding = calculation["calculation_blocks"].get("scaffolding", {})
    method = scaffolding.get("scaffolding_calc_method")
    lines = ["## Формулы подмостей/лесов", ""]
    if method == "floors_based":
        lines.extend(
            [
                "Production-режим `floors_based`: подмости считаются от количества этажей.",
                "",
                "* `scaffolding_setup_quantity = floors_count * scaffolding_setup_units_per_floor`",
                "* `scaffolding_timber_quantity_m3 = floors_count * scaffolding_timber_m3_per_floor`",
                "",
                *dict_table(
                    {
                        "scaffolding_calc_method": method,
                        "floors_count": scaffolding.get("floors_count"),
                        "setup_units_per_floor": scaffolding.get("setup_units_per_floor"),
                        "timber_m3_per_floor": scaffolding.get("timber_m3_per_floor"),
                        "setup_quantity": scaffolding.get("setup_quantity"),
                        "timber_quantity_m3": scaffolding.get("timber_quantity_m3"),
                    }
                ),
            ]
        )
    else:
        lines.extend(
            [
                "Legacy-режим `legacy_direct_quantity`: используются прямые значения `scaffolding_setup_quantity` и `scaffolding_timber_quantity_m3` из старого input.json.",
                "",
                *dict_table(
                    {
                        "scaffolding_calc_method": method,
                        "setup_quantity": scaffolding.get("setup_quantity"),
                        "timber_quantity_m3": scaffolding.get("timber_quantity_m3"),
                    }
                ),
            ]
        )
    return lines


def cutoff_waterproofing_formula_markdown(calculation: dict[str, Any]) -> list[str]:
    cutoff = calculation["calculation_blocks"].get("cutoff_waterproofing", {})
    method = cutoff.get("cutoff_waterproofing_calc_method")
    lines = ["## Формулы отсечной гидроизоляции", ""]
    if method == "spec_area":
        lines.extend(
            [
                "Production-режим `spec_area`: площадь отсечной гидроизоляции под несущие стены берётся готовым значением из спецификации.",
                "",
                "Площадь перегородок сюда не включается; для перегородок нужен отдельный параметр `cutoff_waterproofing_partitions_area_m2`.",
                "",
                *dict_table(
                    {
                        "cutoff_waterproofing_calc_method": method,
                        "cutoff_waterproofing_source": cutoff.get("cutoff_waterproofing_source"),
                        "cutoff_waterproofing_load_bearing_walls_area_m2": cutoff.get("cutoff_waterproofing_load_bearing_walls_area_m2"),
                        "cutoff_waterproofing_area_m2": cutoff.get("cutoff_waterproofing_area_m2"),
                    }
                ),
            ]
        )
    else:
        lines.extend(
            [
                "Legacy-режим `legacy_lengths_by_wall_thickness`: площадь считается по длинам стен 400/250 мм и толщине стены.",
                "",
                "* `area = sum(lengths_400) * wall_400_thickness_m + sum(lengths_250) * wall_250_thickness_m`",
                "",
                *dict_table(
                    {
                        "cutoff_waterproofing_calc_method": method,
                        "cutoff_waterproofing_source": cutoff.get("cutoff_waterproofing_source"),
                        "wall_400_length_m": cutoff.get("wall_400_length_m"),
                        "wall_250_length_m": cutoff.get("wall_250_length_m"),
                        "cutoff_waterproofing_area_m2": cutoff.get("cutoff_waterproofing_area_m2"),
                    }
                ),
            ]
        )
    return lines


def lintel_formula_markdown(calculation: dict[str, Any]) -> list[str]:
    lintels = calculation["calculation_blocks"].get("lintels", {})
    method = lintels.get("lintel_length_calc_method")
    u_block_line = next((line for line in calculation["estimate_lines"] if line["code"] == "u_block_lintel_cutting"), {})
    lines = ["## Формулы перемычек", ""]
    if method == "spec_total_length":
        lines.extend(
            [
                "Production-режим `spec_total_length`: общая длина перемычек в U-блоке берётся готовым значением из спецификации.",
                "",
                "* `u_block_quantity = lintel_total_length_m / gas_block_length_m`",
                "* строка `u_block_lintel_cutting` остаётся в штуках (`шт`), не в м.п.",
                "",
                *dict_table(
                    {
                        "lintel_length_calc_method": method,
                        "lintel_length_source": lintels.get("lintel_length_source"),
                        "lintel_total_length_m": lintels.get("lintel_total_length_m"),
                        "gas_block_length_m": lintels.get("gas_block_length_m"),
                        "u_block_quantity": lintels.get("u_block_quantity"),
                        "lintel_section_width_m": lintels.get("lintel_section_width_m"),
                        "lintel_section_height_m": lintels.get("lintel_section_height_m"),
                        "u_block_lintel_cutting.unit": u_block_line.get("unit"),
                    }
                ),
            ]
        )
    else:
        lines.extend(
            [
                "Legacy-режим `legacy_length_count_items`: общая длина перемычек считается по списку `length_m * count`.",
                "",
                "* `lintel_total_length_m = sum(length_m * count)`",
                "* `u_block_quantity = lintel_total_length_m / gas_block_length_m`",
                "",
                *dict_table(
                    {
                        "lintel_length_calc_method": method,
                        "lintel_length_source": lintels.get("lintel_length_source"),
                        "lintel_total_length_m": lintels.get("lintel_total_length_m"),
                        "gas_block_length_m": lintels.get("gas_block_length_m"),
                        "u_block_quantity": lintels.get("u_block_quantity"),
                        "lintel_section_width_m": lintels.get("lintel_section_width_m"),
                        "lintel_section_height_m": lintels.get("lintel_section_height_m"),
                        "u_block_lintel_cutting.unit": u_block_line.get("unit"),
                    }
                ),
            ]
        )
    lines.extend(["", ""])
    if lintels.get("lintel_concrete_calc_method") == "spec_volume":
        lines.extend(
            [
                "Бетон перемычек standard: проектный объём берётся из спецификации, без повторного коэффициента запаса.",
                "",
                "* `lintel_required_concrete_volume_m3 = lintel_concrete_spec_volume_m3`",
                "* `lintel_concrete_order_volume_m3 = max(1, ceil(lintel_required_concrete_volume_m3))`",
                "",
                *dict_table(
                    {
                        "lintel_concrete_calc_method": lintels.get("lintel_concrete_calc_method"),
                        "lintel_concrete_source": lintels.get("lintel_concrete_source"),
                        "lintel_concrete_spec_volume_m3": lintels.get("lintel_concrete_spec_volume_m3"),
                        "lintel_required_concrete_volume_m3": lintels.get("lintel_required_concrete_volume_m3"),
                        "lintel_concrete_min_order_volume_m3": lintels.get("lintel_concrete_min_order_volume_m3"),
                        "lintel_concrete_order_volume_m3": lintels.get("lintel_concrete_order_volume_m3"),
                    }
                ),
            ]
        )
    else:
        lines.extend(
            [
                "Бетон перемычек legacy: объём считается по длине перемычек и сечению U-блока.",
                "",
                "* `lintel_raw_concrete_volume_m3 = lintel_total_length_m * lintel_section_width_m * lintel_section_height_m`",
                "* `lintel_required_concrete_volume_m3 = lintel_raw_concrete_volume_m3 * concrete_waste_coeff`",
                "* `lintel_concrete_order_volume_m3 = max(1, ceil(lintel_required_concrete_volume_m3))`",
                "",
                *dict_table(
                    {
                        "lintel_concrete_calc_method": lintels.get("lintel_concrete_calc_method"),
                        "lintel_concrete_source": lintels.get("lintel_concrete_source"),
                        "lintel_section_width_m": lintels.get("lintel_section_width_m"),
                        "lintel_section_height_m": lintels.get("lintel_section_height_m"),
                        "lintel_raw_concrete_volume_m3": lintels.get("lintel_raw_concrete_volume_m3"),
                        "lintel_required_concrete_volume_m3": lintels.get("lintel_required_concrete_volume_m3"),
                        "lintel_concrete_order_volume_m3": lintels.get("lintel_concrete_order_volume_m3"),
                    }
                ),
            ]
        )
    return lines


def rebar_formula_markdown(calculation: dict[str, Any]) -> list[str]:
    main = calculation["calculation_blocks"].get("main_wall_reinforcement", {})
    lintels = calculation["calculation_blocks"].get("lintels", {})
    lines = ["## Формулы арматуры", ""]
    if main.get("main_wall_rebar_calc_method") == "spec_length_items":
        lines.extend(
            [
                "Арматура кладки standard: берётся из спецификации в м.п. по этажам и конструкциям.",
                "",
                "| floor | component | steel_class | diameter_mm | spec_length_m | length_with_waste_m | rods | order_length_m | kg_per_meter | delivery_weight_kg | price_code |",
                "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for item in main.get("items", {}).values():
            lines.append(
                f"| `{item.get('floor')}` | `{item.get('component')}` | `{item.get('steel_class')}` | `{item.get('diameter_mm')}` | "
                f"`{item.get('spec_length_m')}` | `{item.get('length_with_waste_m')}` | `{item.get('rods')}` | `{item.get('order_length_m')}` | "
                f"`{item.get('kg_per_meter')}` | `{item.get('delivery_weight_kg')}` | `{item.get('price_code')}` |"
            )
    else:
        lines.extend(
            [
                "Арматура кладки legacy: считается через длины стен, ряды, нитки и коэффициент нахлёста.",
                "",
                *dict_table(
                    {
                        "main_wall_rebar_calc_method": main.get("main_wall_rebar_calc_method"),
                        "main_wall_rebar_source": main.get("main_wall_rebar_source"),
                        "main_wall_chasing_quantity_m": main.get("main_wall_chasing_quantity_m"),
                    }
                ),
            ]
        )

    lines.extend(["", ""])
    if lintels.get("lintel_rebar_calc_method") == "spec_length_items":
        lines.extend(
            [
                "Арматура перемычек standard: берётся из спецификации в м.п. по этажам.",
                "",
                "| floor | component | steel_class | diameter_mm | spec_length_m | length_with_waste_m | rods | order_length_m | kg_per_meter | delivery_weight_kg | price_code |",
                "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for item in lintels.get("rebar", {}).values():
            lines.append(
                f"| `{item.get('floor')}` | `{item.get('component')}` | `{item.get('steel_class')}` | `{item.get('diameter_mm')}` | "
                f"`{item.get('spec_length_m')}` | `{item.get('length_with_waste_m')}` | `{item.get('rods')}` | `{item.get('order_length_m')}` | "
                f"`{item.get('kg_per_meter')}` | `{item.get('delivery_weight_kg')}` | `{item.get('price_code')}` |"
            )
    else:
        lines.extend(
            [
                "Арматура перемычек legacy: считается через вес `weight_kg` с переводом в м.п.",
                "",
                *dict_table(
                    {
                        "lintel_rebar_calc_method": lintels.get("lintel_rebar_calc_method"),
                        "lintel_rebar_source": lintels.get("lintel_rebar_source"),
                        "lintel_rebar_frame_assembly_quantity_m": lintels.get("lintel_rebar_frame_assembly_quantity_m"),
                    }
                ),
            ]
        )
    return lines


def main_walls_crane_formula_markdown(calculation: dict[str, Any]) -> list[str]:
    delivery = calculation["calculation_blocks"].get("deliveries_and_cranes", {})
    method = delivery.get("main_walls_crane_calc_method")
    lines = ["## Формулы крана несущих стен", ""]
    if method == "delivery_trucks_threshold":
        lines.extend(
            [
                "Production-режим `delivery_trucks_threshold`: количество смен крана считается от количества доставок блоков.",
                "",
                "* если `gas_block_delivery_trucks <= 3`, то `main_walls_crane_shifts = 1`",
                "* если `gas_block_delivery_trucks >= 4`, то `main_walls_crane_shifts = 2`",
                "",
                *dict_table(
                    {
                        "main_walls_crane_calc_method": method,
                        "gas_block_delivery_trucks": delivery.get("gas_block_delivery_trucks"),
                        "main_walls_crane_threshold_trucks": delivery.get("main_walls_crane_threshold_trucks"),
                        "main_walls_crane_shifts": delivery.get("main_walls_crane_shifts"),
                    }
                ),
            ]
        )
    else:
        lines.extend(
            [
                "Legacy-режим `legacy_manual_shifts`: используется прямое значение `main_walls_crane_shifts` из старого input.json.",
                "",
                *dict_table(
                    {
                        "main_walls_crane_calc_method": method,
                        "gas_block_delivery_trucks": delivery.get("gas_block_delivery_trucks"),
                        "main_walls_crane_shifts": delivery.get("main_walls_crane_shifts"),
                    }
                ),
            ]
        )
    return lines


def format_markdown(case_name: str, input_data: LoadBearingWallsLintelsInput, calculation: dict[str, Any], comparison: list[dict[str, Any]]) -> str:
    input_values = input_data.to_dict()
    if input_data.upper_floor_calc_method == "floor_2_spec_volume":
        input_values = {
            key: value
            for key, value in input_values.items()
            if not key.startswith("second_light_") and key not in {"parapet_enabled", "vent_chimney_cladding_enabled"}
        }
    if input_data.vent_chimney_geometry_calc_method == "spec_volume_thickness":
        input_values = {
            key: value
            for key, value in input_values.items()
            if key not in {"vent_chimney_segment_lengths_m", "vent_chimney_rows", "block_height_m"}
        }
    input_lines = [f"- `{key}`: `{value}`" for key, value in input_values.items()]
    block_rows = flatten("", calculation["calculation_blocks"])
    warning_lines = [f"- {warning}" for warning in calculation.get("warnings", [])] or ["Предупреждений нет."]
    pricing_sections = []
    if calculation.get("pricing_summary", {}).get("mode") == "price_registry_with_fallback":
        pricing_sections = [
            "",
            *price_sources_markdown(calculation["estimate_lines"]),
            "",
            "## Pricing summary",
            *dict_table(calculation["pricing_summary"]),
        ]
    return "\n".join(
        [
            f"# Расчёт несущих стен и перемычек: {case_name}",
            "",
            f"Проект: `{input_data.project_name}`",
            "",
            "## Входные параметры",
            *input_lines,
            "",
            *scaffolding_formula_markdown(calculation),
            "",
            *cutoff_waterproofing_formula_markdown(calculation),
            "",
            *lintel_formula_markdown(calculation),
            "",
            *rebar_formula_markdown(calculation),
            "",
            *main_walls_crane_formula_markdown(calculation),
            "",
            "## Расчётные блоки",
            *dict_table(block_rows),
            "",
            "## Строки серой внутренней сметы",
            *lines_table(calculation["estimate_lines"]),
            "",
            "## Итоги raw/rounded",
            *dict_table(calculation["internal_totals"]),
            *pricing_sections,
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
    raw_input = load_raw_input(input_path)
    input_data = LoadBearingWallsLintelsInput.from_dict({k: v for k, v in raw_input.items() if k != "pricing"})
    expected = load_expected(expected_path)
    calculation = calculate_load_bearing_walls_lintels(input_data)
    calculation = apply_live_pricing(calculation, raw_input, REPO_ROOT, totals_key="internal_totals")
    comparison = compare_with_expected(calculation, expected)
    is_live_pricing = pricing_mode(raw_input) == "price_registry_with_fallback"
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
    if is_live_pricing:
        payload["pricing_summary"] = calculation.get("pricing_summary", {})
    save_json(output_dir / "load_bearing_walls_lintels_result.json", payload)
    (output_dir / "load_bearing_walls_lintels_result.md").write_text(
        format_markdown(case_name, input_data, calculation, comparison),
        encoding="utf-8",
    )
    if expected_path is None:
        save_json(input_path.parent / "result.json", payload)
        (input_path.parent / "result.md").write_text(
            format_markdown(case_name, input_data, calculation, comparison),
            encoding="utf-8",
        )
    return calculation


if __name__ == "__main__":
    result = run(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps({"calculation_blocks": result["calculation_blocks"], "internal_totals": result["internal_totals"]}, ensure_ascii=False, indent=2))
