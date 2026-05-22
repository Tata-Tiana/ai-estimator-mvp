from __future__ import annotations

from pathlib import Path
from typing import Any


ZERO_STRUCTURE_CODES = {
    "procurement_warehouse_costs_excel_structure",
    "overhead_general_business_costs_excel_structure",
    "estimated_profit_excel_structure",
}


def value_text(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(format_number(item) for item in value)
    return format_number(value)


def format_number(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return str(value)
    if numeric.is_integer():
        return f"{int(numeric):,}".replace(",", " ")
    text = f"{numeric:,.4f}".replace(",", " ")
    return text.rstrip("0").rstrip(".")


def money(value: Any) -> str:
    return f"{format_number(value)} руб."


def bullet(label: str, value: Any, unit: str = "") -> str:
    suffix = f" {unit}" if unit else ""
    return f"- {label}: {format_number(value)}{suffix}"


def comparison_counts(result: dict[str, Any]) -> tuple[int, int]:
    comparison = result.get("comparison", [])
    if isinstance(comparison, dict):
        return int(comparison.get("ok_count", 0)), int(comparison.get("mismatch_count", 0))
    ok = sum(1 for item in comparison if item.get("status") == "ok")
    mismatch = sum(1 for item in comparison if item.get("status") != "ok")
    return ok, mismatch


def line_kind(line: dict[str, Any], blocks: dict[str, Any]) -> str:
    code = line.get("code")
    line_type = line.get("line_type")
    manual_lines = blocks.get("manual_lines", {})
    if line_type == "zero_excel_structure_line" or code in ZERO_STRUCTURE_CODES:
        return "zero_excel_structure_line"
    if code in manual_lines:
        return manual_lines[code].get("line_type", "fixed/manual")
    if line.get("line_total") == 0:
        return "control/zero line"
    if line.get("material_total", 0) and not line.get("work_total", 0):
        return "materials"
    if line.get("work_total", 0) and not line.get("material_total", 0):
        return "work"
    return line_type or "mixed"


def formula_for_line(
    line: dict[str, Any],
    inputs: dict[str, Any],
    blocks: dict[str, Any],
) -> tuple[list[str], list[str], list[str], list[str]]:
    code = line.get("code")
    source: list[str] = []
    formula: list[str] = []
    rounding: list[str] = []
    notes: list[str] = []

    membrane = blocks.get("membrane", {})
    formwork = blocks.get("formwork", {})
    eps = blocks.get("eps", {})
    thermal = blocks.get("thermal_insert", {})
    rebar = blocks.get("rebar", {})
    concrete = blocks.get("concrete", {})
    manual = blocks.get("manual_lines", {}).get(code, {})

    if code == "planter_membrane_installation":
        source = [
            bullet("Площадь мембраны", inputs.get("membrane_area_m2"), "м2"),
            bullet("Ставка работы", inputs.get("membrane_installation_work_unit_price"), "руб/м2"),
        ]
        formula = [
            f"{format_number(inputs.get('membrane_area_m2'))} × "
            f"{format_number(inputs.get('membrane_installation_work_unit_price'))} = "
            f"{money(line.get('work_total'))}"
        ]

    elif code == "planter_standard_material":
        source = [
            bullet("Площадь мембраны", inputs.get("membrane_area_m2"), "м2"),
            bullet("Нахлёст", inputs.get("membrane_overlap_coeff")),
            bullet("Площадь рулона", inputs.get("membrane_roll_area_m2"), "м2"),
            bullet("Цена рулона", inputs.get("planter_standard_roll_unit_price"), "руб."),
        ]
        formula = [
            f"{format_number(inputs.get('membrane_area_m2'))} × "
            f"{format_number(inputs.get('membrane_overlap_coeff'))} = "
            f"{format_number(membrane.get('membrane_area_with_overlap_m2'))} м2",
            f"{format_number(membrane.get('membrane_area_with_overlap_m2'))} / "
            f"{format_number(inputs.get('membrane_roll_area_m2'))} = "
            f"{format_number(membrane.get('membrane_raw_rolls'))} рул.",
            f"{format_number(membrane.get('membrane_rolls'))} × "
            f"{format_number(inputs.get('planter_standard_roll_unit_price'))} = "
            f"{money(line.get('material_total'))}",
        ]
        rounding = [f"Округляем вверх: {format_number(membrane.get('membrane_rolls'))} рул."]

    elif code == "planterband_material":
        source = [
            bullet("Количество рулонов мембраны", membrane.get("membrane_rolls"), "рул."),
            bullet("PLANTERBAND на рулон", inputs.get("planterband_per_membrane_roll"), "шт."),
            bullet("Цена PLANTERBAND", inputs.get("planterband_unit_price"), "руб/шт"),
        ]
        formula = [
            f"{format_number(membrane.get('membrane_rolls'))} × "
            f"{format_number(inputs.get('planterband_per_membrane_roll'))} = "
            f"{format_number(membrane.get('planterband_quantity'))} шт.",
            f"{format_number(membrane.get('planterband_quantity'))} × "
            f"{format_number(inputs.get('planterband_unit_price'))} = "
            f"{money(line.get('material_total'))}",
        ]

    elif code == "formwork_installation":
        source = [
            bullet("Периметр бортов", inputs.get("slab_formwork_perimeter_m"), "м"),
            bullet("Высота борта", inputs.get("slab_edge_height_m"), "м"),
        ]
        formula = [
            f"{format_number(inputs.get('slab_formwork_perimeter_m'))} × "
            f"{format_number(inputs.get('slab_edge_height_m'))} = "
            f"{format_number(formwork.get('formwork_area_m2'))} м2"
        ]
        notes = [
            "Строка нужна для структуры Excel и как база для фанеры/пиломатериала.",
            "В серой себестоимости строка нулевая.",
        ]

    elif code == "formwork_plywood":
        source = [
            bullet("Площадь опалубки бортов", formwork.get("formwork_area_m2"), "м2"),
            bullet("Рабочая площадь листа фанеры", inputs.get("plywood_sheet_working_area_m2"), "м2"),
            bullet("Цена листа", inputs.get("plywood_unit_price"), "руб/шт"),
        ]
        formula = [
            f"{format_number(formwork.get('formwork_area_m2'))} / "
            f"{format_number(inputs.get('plywood_sheet_working_area_m2'))} = "
            f"{format_number(formwork.get('plywood_raw_sheets'))} лист.",
            f"{format_number(formwork.get('plywood_sheets'))} × "
            f"{format_number(inputs.get('plywood_unit_price'))} = "
            f"{money(line.get('material_total'))}",
        ]
        rounding = [f"Округляем вверх: {format_number(formwork.get('plywood_sheets'))} лист."]

    elif code == "formwork_timber":
        source = [
            bullet("Площадь опалубки бортов", formwork.get("formwork_area_m2"), "м2"),
            bullet("Толщина пиломатериала", inputs.get("timber_thickness_m"), "м"),
            bullet("Цена пиломатериала", inputs.get("timber_unit_price"), "руб/м3"),
        ]
        formula = [
            f"{format_number(formwork.get('formwork_area_m2'))} × "
            f"{format_number(inputs.get('timber_thickness_m'))} = "
            f"{format_number(formwork.get('timber_raw_volume_m3'))} м3",
            f"{format_number(formwork.get('timber_raw_volume_m3'))} × "
            f"{format_number(inputs.get('timber_unit_price'))} = "
            f"{money(line.get('material_total'))}",
        ]
        rounding = ["Количество в Excel отображается округлённо, сумма считается от raw-объёма."]

    elif code == "eps50_laying_under_slab":
        source = [
            bullet("Объём ЭППС 50 мм под плитой", inputs.get("eps50_under_slab_volume_m3"), "м3"),
            bullet("Толщина ЭППС", inputs.get("eps50_thickness_m"), "м"),
            bullet("Ставка работы", inputs.get("eps50_laying_work_unit_price"), "руб/м2"),
        ]
        formula = [
            f"{format_number(inputs.get('eps50_under_slab_volume_m3'))} / "
            f"{format_number(inputs.get('eps50_thickness_m'))} = "
            f"{format_number(eps.get('eps50_laying_area_m2'))} м2",
            f"{format_number(eps.get('eps50_laying_area_m2'))} × "
            f"{format_number(inputs.get('eps50_laying_work_unit_price'))} = "
            f"{money(line.get('work_total'))}",
        ]

    elif code == "thermal_insert_installation":
        source = [
            bullet("Длина термовкладыша", inputs.get("thermal_insert_length_m"), "м.п."),
            bullet("Ставка монтажа", inputs.get("thermal_insert_installation_work_unit_price"), "руб/м.п."),
        ]
        formula = [
            f"{format_number(inputs.get('thermal_insert_length_m'))} × "
            f"{format_number(inputs.get('thermal_insert_installation_work_unit_price'))} = "
            f"{money(line.get('work_total'))}"
        ]

    elif code == "eps50_penoplex_geo_material":
        source = [
            bullet("ЭППС 50 мм под плитой с запасом", eps.get("eps50_under_slab_required_volume_m3"), "м3"),
            bullet("ЭППС 50 мм для термовкладышей", eps.get("eps50_thermal_insert_volume_m3"), "м3"),
            bullet("Объём пачки", inputs.get("eps50_pack_volume_m3"), "м3"),
            bullet("Цена", inputs.get("eps50_unit_price"), "руб/м3"),
        ]
        formula = [
            f"{format_number(eps.get('eps50_under_slab_required_volume_m3'))} + "
            f"{format_number(eps.get('eps50_thermal_insert_volume_m3'))} = "
            f"{format_number(eps.get('eps50_required_volume_m3'))} м3",
            f"{format_number(eps.get('eps50_required_volume_m3'))} / "
            f"{format_number(inputs.get('eps50_pack_volume_m3'))} = "
            f"{format_number(eps.get('eps50_raw_packs'))} пач.",
            f"{format_number(eps.get('eps50_packs'))} × "
            f"{format_number(inputs.get('eps50_pack_volume_m3'))} = "
            f"{format_number(eps.get('eps50_order_volume_m3'))} м3",
            f"{format_number(eps.get('eps50_order_volume_m3'))} × "
            f"{format_number(inputs.get('eps50_unit_price'))} = "
            f"{money(line.get('material_total'))}",
        ]
        rounding = [f"Округляем вверх до целых пачек: {format_number(eps.get('eps50_packs'))} пач."]

    elif code == "eps100_penoplex_geo_material":
        source = [
            bullet("Объём ЭППС 100 мм для термовкладышей", eps.get("eps100_required_volume_m3"), "м3"),
            bullet("Объём пачки", inputs.get("eps100_pack_volume_m3"), "м3"),
            bullet("Цена", inputs.get("eps100_unit_price"), "руб/м3"),
        ]
        formula = [
            f"{format_number(eps.get('eps100_required_volume_m3'))} / "
            f"{format_number(inputs.get('eps100_pack_volume_m3'))} = "
            f"{format_number(eps.get('eps100_raw_packs'))} пач.",
            f"{format_number(eps.get('eps100_packs'))} × "
            f"{format_number(inputs.get('eps100_pack_volume_m3'))} = "
            f"{format_number(eps.get('eps100_order_volume_m3'))} м3",
            f"{format_number(eps.get('eps100_order_volume_m3'))} × "
            f"{format_number(inputs.get('eps100_unit_price'))} = "
            f"{money(line.get('material_total'))}",
        ]
        rounding = [f"Округляем вверх до целых пачек: {format_number(eps.get('eps100_packs'))} пач."]

    elif code == "rebar_crane_supply":
        source = [
            bullet("Количество смен", inputs.get("rebar_crane_shifts"), "смена"),
            bullet("Ставка", inputs.get("rebar_crane_unit_price"), "руб/смена"),
        ]
        formula = [
            f"{format_number(inputs.get('rebar_crane_shifts'))} × "
            f"{format_number(inputs.get('rebar_crane_unit_price'))} = "
            f"{money(line.get('material_total'))}"
        ]
        notes = ["Ручная/fixed строка механизма для подачи арматуры."]

    elif code == "rebar_frame_assembly":
        items = rebar.get("items", {})
        source = [
            bullet("Ø16", items.get("rebar_a500_d16", {}).get("order_length_m"), "м.п."),
            bullet("Ø12", items.get("rebar_a500_d12", {}).get("order_length_m"), "м.п."),
            bullet("Ø10", items.get("rebar_a500_d10", {}).get("order_length_m"), "м.п."),
            bullet("Ø6", items.get("rebar_a240_d6", {}).get("order_length_m"), "м.п."),
        ]
        formula = [
            f"{format_number(items.get('rebar_a500_d16', {}).get('order_length_m'))} + "
            f"{format_number(items.get('rebar_a500_d12', {}).get('order_length_m'))} + "
            f"{format_number(items.get('rebar_a500_d10', {}).get('order_length_m'))} + "
            f"{format_number(items.get('rebar_a240_d6', {}).get('order_length_m'))} = "
            f"{format_number(rebar.get('rebar_frame_assembly_quantity_m'))} м.п."
        ]
        notes = [
            "Материал арматуры считается отдельными строками по диаметрам.",
            "Эта строка — нулевая строка структуры.",
        ]

    elif code in {"rebar_a500_d16", "rebar_a500_d12", "rebar_a500_d10", "rebar_a240_d6"}:
        item = rebar.get("items", {}).get(code, {})
        input_item = next((part for part in inputs.get("rebar_items", []) if part.get("code") == code), {})
        source = [
            bullet("Вес по спецификации", item.get("total_weight_kg"), "кг"),
            bullet("Кг на метр", input_item.get("kg_per_meter"), "кг/м"),
            bullet("Запас", inputs.get("rebar_waste_coeff")),
            bullet("Длина прутка", input_item.get("rod_length_m"), "м"),
            bullet("Цена за метр", input_item.get("unit_price_per_m"), "руб/м.п."),
        ]
        formula = [
            f"{format_number(item.get('total_weight_kg'))} / "
            f"{format_number(input_item.get('kg_per_meter'))} = "
            f"{format_number(item.get('raw_length_m'))} м.п.",
            f"{format_number(item.get('raw_length_m'))} × "
            f"{format_number(inputs.get('rebar_waste_coeff'))} = "
            f"{format_number(item.get('length_with_waste_m'))} м.п.",
            f"{format_number(item.get('length_with_waste_m'))} / "
            f"{format_number(input_item.get('rod_length_m'))} = "
            f"{format_number(item.get('raw_rods'))} прут.",
            f"{format_number(item.get('rods'))} × "
            f"{format_number(input_item.get('rod_length_m'))} = "
            f"{format_number(item.get('order_length_m'))} м.п.",
            f"{format_number(item.get('order_length_m'))} × "
            f"{format_number(input_item.get('unit_price_per_m'))} = "
            f"{money(line.get('material_total'))}",
        ]
        rounding = [f"Округляем вверх до целых прутков: {format_number(item.get('rods'))} прут."]

    elif code == "rebar_metal_delivery":
        source = [
            bullet("Вес металла коробки для доставки", inputs.get("box_total_metal_weight_kg"), "кг"),
            bullet("Вместимость машины", inputs.get("box_metal_delivery_capacity_kg"), "кг"),
            bullet("Ставка за машину", inputs.get("rebar_metal_delivery_unit_price"), "руб."),
        ]
        formula = [
            f"{format_number(inputs.get('rebar_metal_delivery_trucks'))} × "
            f"{format_number(inputs.get('rebar_metal_delivery_unit_price'))} = "
            f"{money(line.get('material_total'))}"
        ]
        notes = ["В demo используется зафиксированное количество машин из калькулятора."]

    elif code == "foundation_slab_concreting_work":
        source = [
            bullet("Проектный объём бетона", inputs.get("concrete_project_volume_m3"), "м3"),
            bullet("Ставка бетонирования", inputs.get("concreting_work_unit_price"), "руб/м3"),
        ]
        formula = [
            f"{format_number(inputs.get('concrete_project_volume_m3'))} × "
            f"{format_number(inputs.get('concreting_work_unit_price'))} = "
            f"{money(line.get('work_total'))}"
        ]

    elif code == "concrete_b22_5_m300_material":
        source = [
            bullet("Проектный объём бетона", inputs.get("concrete_project_volume_m3"), "м3"),
            bullet("Запас", inputs.get("concrete_waste_coeff")),
            bullet("Шаг заказа", inputs.get("concrete_round_step_m3"), "м3"),
            bullet("Цена бетона", inputs.get("concrete_unit_price"), "руб/м3"),
        ]
        formula = [
            f"{format_number(inputs.get('concrete_project_volume_m3'))} × "
            f"{format_number(inputs.get('concrete_waste_coeff'))} = "
            f"{format_number(concrete.get('concrete_raw_order_volume_m3'))} м3",
            f"{format_number(concrete.get('concrete_order_volume_m3'))} × "
            f"{format_number(inputs.get('concrete_unit_price'))} = "
            f"{money(line.get('material_total'))}",
        ]
        rounding = [
            f"Округляем заказ до шага {format_number(inputs.get('concrete_round_step_m3'))} м3: "
            f"{format_number(concrete.get('concrete_order_volume_m3'))} м3."
        ]

    elif code == "concrete_delivery":
        source = [
            bullet("Заказной объём бетона", concrete.get("concrete_order_volume_m3"), "м3"),
            bullet("Объём миксера", inputs.get("concrete_mixer_volume_m3"), "м3"),
            bullet("Ставка за рейс", inputs.get("concrete_delivery_unit_price"), "руб."),
        ]
        formula = [
            f"{format_number(concrete.get('concrete_order_volume_m3'))} / "
            f"{format_number(inputs.get('concrete_mixer_volume_m3'))} = "
            f"{format_number(concrete.get('concrete_delivery_raw_trips'))} рейс.",
            f"{format_number(concrete.get('concrete_delivery_trips'))} × "
            f"{format_number(inputs.get('concrete_delivery_unit_price'))} = "
            f"{money(line.get('material_total'))}",
        ]
        rounding = [f"Округляем вверх: {format_number(concrete.get('concrete_delivery_trips'))} рейс."]

    elif code == "concrete_pump_32m":
        source = [
            bullet("Количество смен", inputs.get("concrete_pump_shifts"), "смена"),
            bullet("Ставка", inputs.get("concrete_pump_unit_price"), "руб/смена"),
        ]
        formula = [
            f"{format_number(inputs.get('concrete_pump_shifts'))} × "
            f"{format_number(inputs.get('concrete_pump_unit_price'))} = "
            f"{money(line.get('material_total'))}"
        ]
        notes = ["Fixed/manual строка: бетононасос не вычисляется от объёма бетона."]

    elif code == "formwork_dismantling":
        source = [
            bullet("Площадь опалубки", formwork.get("formwork_area_m2"), "м2"),
            bullet("Ставка демонтажа", inputs.get("formwork_dismantling_work_unit_price"), "руб/м2"),
        ]
        formula = [
            f"{format_number(formwork.get('formwork_area_m2'))} × "
            f"{format_number(inputs.get('formwork_dismantling_work_unit_price'))} = "
            f"{money(line.get('work_total'))}"
        ]
        notes = ["В текущей серой себестоимости строка нулевая."]

    elif code in {"logistics_and_supply", "consumables_tool_amortization", "technical_supervision"}:
        amount = manual.get("unit_price", line.get("line_total"))
        source = [
            bullet("Количество", manual.get("quantity", line.get("quantity")), line.get("unit", "")),
            bullet("Зафиксированная сумма", amount, "руб."),
        ]
        formula = [
            f"{format_number(manual.get('quantity', line.get('quantity')))} × "
            f"{format_number(amount)} = {money(line.get('line_total'))}"
        ]
        notes = ["Fixed/manual строка из текущего scope калькулятора."]

    elif code in ZERO_STRUCTURE_CODES:
        source = ["- Количество: 1", "- Ставки материалов и работ: 0"]
        formula = ["Строка добавлена для структуры Excel."]
        notes = [
            "В текущем scope не рассчитывается.",
            "Серая себестоимость = 0.",
            "Клиентская часть = 0.",
            "Не влияет на internal_totals.",
        ]

    else:
        source = [
            bullet("Количество", line.get("quantity"), line.get("unit", "")),
            bullet("Цена материалов", line.get("material_unit_price"), "руб."),
            bullet("Цена работ", line.get("work_unit_price"), "руб."),
        ]
        formula = ["Строка выведена из результата калькулятора без дополнительной расшифровки."]

    return source, formula, rounding, notes


def append_line_calc(
    report_lines: list[str],
    index: int,
    line: dict[str, Any],
    inputs: dict[str, Any],
    blocks: dict[str, Any],
) -> None:
    source, formula, rounding, notes = formula_for_line(line, inputs, blocks)
    quantity_raw = line.get("quantity_raw", line.get("quantity"))
    quantity_display = line.get("display_quantity", line.get("quantity_display"))
    kind = line_kind(line, blocks)

    report_lines.extend(
        [
            f"### {index}. {line.get('name', '')}",
            "",
            bullet("Ед. изм.", line.get("unit")),
            bullet("Количество raw", quantity_raw),
        ]
    )
    if quantity_display is not None:
        report_lines.append(bullet("Количество display", quantity_display))
    report_lines.extend(
        [
            f"- Тип строки: {kind}",
            "",
            "Исходные данные:",
            *source,
            "",
            "Формула:",
            *[f"- {item}" for item in formula],
        ]
    )
    if rounding:
        report_lines.extend(["", "Округление:", *[f"- {item}" for item in rounding]])
    report_lines.extend(
        [
            "",
            "Итог:",
            f"- Материалы: {format_number(line.get('material_total', 0))}",
            f"- Работы: {format_number(line.get('work_total', 0))}",
            f"- Итого: {format_number(line.get('line_total', 0))}",
        ]
    )
    if notes:
        report_lines.extend(["", "Примечание:", *[f"- {item}" for item in notes]])
    report_lines.append("")


def build_markdown_report(
    path_or_card: dict[str, Any],
    result: dict[str, Any],
    section_title: str,
) -> str:
    review_card = path_or_card
    inputs = result.get("inputs", {})
    blocks = result.get("calculation_blocks", {})
    totals = result.get("internal_totals", {})
    ok_count, mismatch_count = comparison_counts(result)

    lines = [
        "# Расчётный отчёт по разделу:",
        section_title,
        "",
        "## Краткое пояснение",
        "",
        "- AI не считает смету.",
        "- Параметры извлечены из PDF и требуют проверки Еленой.",
        "- Расчёт выполнен Python-калькулятором.",
        "- Клиентская часть не считается.",
        "- Белая зона Excel — техническая копия серой зоны.",
        "",
        "## Параметры из PDF",
        "",
        "| Параметр | Значение | Ед. | Источник | Страница | Статус |",
        "| --- | ---: | --- | --- | ---: | --- |",
    ]
    for item in review_card.get("parameters", []):
        lines.append(
            "| "
            f"{item.get('label')} | "
            f"{value_text(item.get('value'))} | "
            f"{item.get('unit')} | "
            f"`{item.get('source_file')}` | "
            f"{item.get('page')} | "
            f"{item.get('review_status')} |"
        )

    lines.extend(["", "## Построчный расчёт сметы", ""])
    for index, estimate_line in enumerate(result.get("estimate_lines", []), start=1):
        append_line_calc(lines, index, estimate_line, inputs, blocks)

    lines.extend(
        [
            "## Итоги раздела",
            "",
            f"- Материалы: {format_number(totals.get('internal_materials_total'))}",
            f"- Работы: {format_number(totals.get('internal_works_total'))}",
            f"- Итого: {format_number(totals.get('internal_section_total'))}",
            "",
            "## Проверка",
            "",
            f"- comparison: {ok_count} ok / {mismatch_count} mismatch",
            "",
            "Warnings:",
        ]
    )
    warnings = result.get("warnings", [])
    lines.extend([f"- {warning}" for warning in warnings] or ["- Нет предупреждений."])
    lines.extend(
        [
            "",
            "Пометка:",
            "- AI не считает смету. Расчёт выполнен Python-калькулятором по зафиксированным формулам.",
            "- Клиентская часть не рассчитывается и клиентские ставки из старой сметы не переносятся.",
        ]
    )
    return "\n".join(lines) + "\n"


def save_markdown_report(
    path: Path,
    review_card: dict[str, Any],
    result: dict[str, Any],
    section_title: str,
) -> str:
    payload = build_markdown_report(review_card, result, section_title)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")
    return payload
