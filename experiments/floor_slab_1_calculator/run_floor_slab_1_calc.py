from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from floor_slab_1_calculator import calculate_floor_slab_1


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
PRICING_DIR = REPO_ROOT / "experiments" / "pricing"
if str(PRICING_DIR) not in sys.path:
    sys.path.insert(0, str(PRICING_DIR))

from live_pricing import apply_live_pricing, price_sources_markdown, pricing_mode  # noqa: E402

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


def formwork_areas_context_markdown(calculation: dict[str, Any]) -> list[str]:
    formwork = calculation["calculation_blocks"].get("formwork", {})
    method = formwork.get("formwork_areas_calc_method")
    lines = ["## Площади опалубки", ""]
    if method == "spec_formwork_areas":
        lines.extend(
            [
                "Production-режим `spec_formwork_areas`: три площади опалубки берутся готовыми значениями из спецификации.",
                "",
                "Старые формулы через бетон, толщину, периметр и `beams.items` выводятся только как контрольные значения.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "Legacy-режим `legacy_calculated_from_geometry`: площади опалубки восстанавливаются из объёма бетона, толщины, периметра и геометрии балок.",
                "",
            ]
        )

    lines.extend(
        dict_table(
            {
                "formwork_areas_calc_method": method,
                "formwork_areas_source": formwork.get("formwork_areas_source"),
                "main_formwork_area_m2": formwork.get("main_formwork_area_m2"),
                "slab_formwork_area_m2": formwork.get("slab_formwork_area_m2"),
                "edge_formwork_area_m2": formwork.get("edge_formwork_area_m2"),
                "beams_formwork_area_m2": formwork.get("beams_formwork_area_m2"),
                "edge_and_beam_formwork_area_m2": formwork.get("edge_and_beam_formwork_area_m2"),
                "calculated_main_formwork_area_m2": formwork.get("calculated_main_formwork_area_m2"),
                "calculated_edge_formwork_area_m2": formwork.get("calculated_edge_formwork_area_m2"),
                "calculated_beams_formwork_area_m2": formwork.get("calculated_beams_formwork_area_m2"),
                "main_formwork_area_delta_m2": formwork.get("main_formwork_area_delta_m2"),
                "edge_formwork_area_delta_m2": formwork.get("edge_formwork_area_delta_m2"),
                "beams_formwork_area_delta_m2": formwork.get("beams_formwork_area_delta_m2"),
            }
        )
    )
    return lines


def formwork_rate_context_markdown(calculation: dict[str, Any]) -> list[str]:
    context = calculation["calculation_blocks"].get("formwork_rate_context", {})
    method = context.get("formwork_rate_calc_method")
    lines = ["## Ставка комплекта опалубки", ""]
    if method == "direct_section_rate":
        lines.extend(
            [
                "Production-режим `direct_section_rate`: ставка опалубки взята напрямую для плиты перекрытия 1-го этажа.",
                "",
                "Общая сумма предложения поставщика и площадь плиты 2-го этажа в этом калькуляторе не используются.",
                "",
                *dict_table(
                    {
                        "formwork_rate_calc_method": method,
                        "formwork_rate_per_m2": context.get("formwork_rate_per_m2"),
                        "box_level_quote_context_used": context.get("box_level_quote_context_used"),
                    }
                ),
            ]
        )
    else:
        lines.extend(
            [
                "Legacy-режим `legacy_supplier_quote_context`: справочная средняя ставка считается из общего предложения поставщика по двум плитам.",
                "",
                *dict_table(
                    {
                        "formwork_rate_calc_method": method,
                        "formwork_supplier_quote_total": context.get("formwork_supplier_quote_total"),
                        "slab_2_formwork_area_for_rate_context_m2": context.get("slab_2_formwork_area_for_rate_context_m2"),
                        "raw_average_rate": context.get("raw_average_rate"),
                        "formwork_rate_per_m2": context.get("formwork_rate_per_m2"),
                    }
                ),
            ]
        )
    return lines


def metal_delivery_context_markdown(calculation: dict[str, Any]) -> list[str]:
    rebar = calculation["calculation_blocks"].get("rebar", {})
    method = rebar.get("metal_delivery_calc_method")
    lines = ["## Доставка арматуры и металла", ""]
    if method == "section_output_only":
        lines.extend(
            [
                "Production-режим `section_output_only`: калькулятор плиты 1-го этажа отдаёт только вес закупочной арматуры текущего раздела.",
                "",
                "Количество машин доставки металла считается выше, на уровне `box_calculator`, по суммарному весу металла коробки.",
                "",
                *dict_table(
                    {
                        "metal_delivery_calc_method": method,
                        "section_rebar_delivery_weight_kg": rebar.get("section_rebar_delivery_weight_kg"),
                        "max_weight_per_truck_kg": rebar.get("max_weight_per_truck_kg"),
                        "legacy_delivery_line_enabled": rebar.get("legacy_delivery_line_enabled"),
                        "box_level_delivery_required": rebar.get("box_level_delivery_required"),
                    }
                ),
            ]
        )
    else:
        lines.extend(
            [
                "Legacy-режим `legacy_slab1_slab2_context`: строка доставки металла использует контекст веса арматуры плит 1-го и 2-го этажа.",
                "",
                *dict_table(
                    {
                        "metal_delivery_calc_method": method,
                        "section_rebar_delivery_weight_kg": rebar.get("section_rebar_delivery_weight_kg"),
                        "floor_slab_2_rebar_weight_for_delivery_context_kg": rebar.get(
                            "floor_slab_2_rebar_weight_for_delivery_context_kg"
                        ),
                        "total_delivery_weight_kg_raw": rebar.get("total_delivery_weight_kg_raw"),
                        "trucks_ordered": rebar.get("trucks_ordered"),
                    }
                ),
            ]
        )
    return lines


def rebar_context_markdown(calculation: dict[str, Any]) -> list[str]:
    rebar = calculation["calculation_blocks"].get("rebar", {})
    method = rebar.get("rebar_calc_method")
    lines = ["## Арматура плиты перекрытия 1-го этажа", ""]
    if method == "spec_length_items":
        lines.extend(
            [
                "Production-режим `spec_length_items`: арматура берётся из спецификации в м.п. по классу стали и диаметру.",
                "",
                "Формула: `length_with_waste_m = spec_length_m * waste_coeff`; `order_length_m = ceil(length_with_waste_m / rod_length_m) * rod_length_m`.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "Legacy-режим `legacy_weight_parts`: арматура берётся весом в кг и переводится в м.п. через `kg_per_meter`.",
                "",
            ]
        )

    rows = []
    for item in rebar.get("items", []):
        rows.append(
            {
                "code": item.get("code"),
                "floor": item.get("floor"),
                "component": item.get("component"),
                "steel_class": item.get("steel_class"),
                "diameter_mm": item.get("diameter_mm"),
                "spec_length_m": item.get("spec_length_m"),
                "base_length_m": item.get("base_length_m"),
                "length_with_waste_m": item.get("length_with_waste_m"),
                "rods": item.get("rods"),
                "order_length_m": item.get("order_length_m"),
                "kg_per_meter": item.get("kg_per_meter"),
                "delivery_weight_kg": item.get("delivery_weight_kg"),
                "price_code": f"rebar_{str(item.get('steel_class', '')).lower()}_d{item.get('diameter_mm')}_m",
            }
        )

    lines.extend(
        [
            *dict_table(
                {
                    "rebar_calc_method": method,
                    "rebar_frame_assembly_quantity_m": rebar.get("rebar_frame_assembly_quantity_m"),
                    "section_rebar_delivery_weight_kg": rebar.get("section_rebar_delivery_weight_kg"),
                }
            ),
            "",
            "| code | floor | component | steel_class | diameter_mm | spec_length_m | base_length_m | length_with_waste_m | rods | order_length_m | kg_per_meter | delivery_weight_kg | price_code |",
            "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                str(row.get(key, ""))
                for key in [
                    "code",
                    "floor",
                    "component",
                    "steel_class",
                    "diameter_mm",
                    "spec_length_m",
                    "base_length_m",
                    "length_with_waste_m",
                    "rods",
                    "order_length_m",
                    "kg_per_meter",
                    "delivery_weight_kg",
                    "price_code",
                ]
            )
            + " |"
        )
    return lines


def insulation_context_markdown(calculation: dict[str, Any]) -> list[str]:
    insulation = calculation["calculation_blocks"].get("insulation", {})
    method = insulation.get("insulation_calc_method")
    lines = ["## Утепление плиты", ""]
    if method == "spec_work_quantities":
        lines.extend(
            [
                "Production-режим `spec_work_quantities`: рабочие количества и чистый объём ЭППС берутся из спецификации.",
                "",
                "Длина утепления балок и площадь утепления балок считаются из `beams.items`; площадь торца плиты не выводится из длины и толщины, а приходит отдельным значением.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "Legacy-режим `legacy_usv_geometry`: утепление рассчитано по старой геометрии ЮСВ для сохранения сверки с исходной сметой.",
                "",
            ]
        )

    lines.extend(
        dict_table(
            {
                "insulation_calc_method": method,
                "slab_outer_edge_eps_work_length_m": insulation.get("slab_outer_edge_eps_work_length_m"),
                "beams_eps_work_length_m": insulation.get("beams_eps_work_length_m"),
                "edge_beam_eps_work_length_m": insulation.get("edge_beam_eps_work_length_m"),
                "slab_edge_eps_material_area_m2": insulation.get("slab_edge_eps_material_area_m2"),
                "beams_eps_material_area_m2": insulation.get("beams_eps_material_area_m2"),
                "edge_and_beam_eps_material_area_m2": insulation.get("edge_and_beam_eps_material_area_m2"),
                "bottom_slab_eps_work_area_m2": insulation.get("bottom_slab_eps_work_area_m2"),
                "total_eps_volume_from_spec_m3": insulation.get("total_eps_volume_from_spec_m3"),
                "calculated_clean_eps_volume_m3": insulation.get("calculated_clean_eps_volume_m3"),
                "eps_volume_delta_m3": insulation.get("eps_volume_delta_m3"),
                "eps_waste_coeff": insulation.get("eps_waste_coeff"),
                "required_eps_volume_m3_raw": insulation.get("required_eps_volume_m3_raw"),
                "eps_pack_volume_m3": insulation.get("eps_pack_volume_m3"),
                "eps_packs_raw": insulation.get("eps_packs_raw"),
                "eps_packs_ordered": insulation.get("eps_packs_ordered"),
                "order_eps_volume_m3_raw": insulation.get("order_eps_volume_m3_raw"),
                "foam_cans_ordered": insulation.get("foam_cans_ordered"),
            }
        )
    )
    return lines


def format_markdown(case_name: str, calculation: dict[str, Any], comparison: dict[str, Any]) -> str:
    notes = collect_notes(calculation)
    warnings = calculation.get("warnings", [])
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
            *formwork_areas_context_markdown(calculation),
            "",
            *formwork_rate_context_markdown(calculation),
            "",
            *rebar_context_markdown(calculation),
            "",
            *metal_delivery_context_markdown(calculation),
            "",
            *insulation_context_markdown(calculation),
            "",
            "## Строки серой внутренней сметы",
            *lines_table(calculation["estimate_lines"]),
            *pricing_sections,
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
    calculation = apply_live_pricing(calculation, input_data, REPO_ROOT, totals_key="totals")
    comparison = compare_with_expected(calculation, expected)
    is_live_pricing = pricing_mode(input_data) == "price_registry_with_fallback"
    payload = {
        **calculation,
        "case_name": case_name,
        "input_path": str(input_path),
        "expected_path": str(expected_path) if expected_path else None,
        "expected": expected,
        "comparison": comparison,
    }
    if not is_live_pricing:
        payload.pop("pricing_summary", None)
    save_json(output_dir / "floor_slab_1_result.json", payload)
    (output_dir / "floor_slab_1_result.md").write_text(
        format_markdown(case_name, payload, comparison),
        encoding="utf-8",
    )
    if expected_path is None:
        save_json(input_path.parent / "result.json", payload)
        (input_path.parent / "result.md").write_text(
            format_markdown(case_name, payload, comparison),
            encoding="utf-8",
        )
    return payload


if __name__ == "__main__":
    result = run(sys.argv[1] if len(sys.argv) > 1 else None)
    print(json.dumps({"totals": result["totals"], "comparison": result["comparison"]}, ensure_ascii=False, indent=2))
