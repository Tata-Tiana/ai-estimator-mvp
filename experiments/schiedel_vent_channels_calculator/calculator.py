from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any


D0 = Decimal("0")
D1 = Decimal("1")


def d(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def round_money_half_up(value: Any) -> int:
    return int(d(value).quantize(D1, rounding=ROUND_HALF_UP))


def decimal_str(value: Any) -> str:
    value_dec = d(value)
    if value_dec == value_dec.to_integral_value():
        return str(value_dec.quantize(D1))
    return format(value_dec.normalize(), "f")


def estimate_line(
    *,
    code: str,
    name: str,
    unit: str,
    line_type: str,
    quantity_raw: Any,
    quantity_display: Any | None = None,
    quantity_source: str,
    price_code: str | None = None,
    material_unit_price: Any = 0,
    material_total_raw: Any = 0,
    work_unit_price: Any = 0,
    work_total_raw: Any = 0,
    formula: dict[str, Any] | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    material_raw = d(material_total_raw)
    work_raw = d(work_total_raw)
    line_raw = material_raw + work_raw
    payload = {
        "code": code,
        "name": name,
        "unit": unit,
        "line_type": line_type,
        "quantity_raw": decimal_str(quantity_raw),
        "quantity_display": decimal_str(quantity_raw if quantity_display is None else quantity_display),
        "quantity_source": quantity_source,
        "internal_cost": {
            "material_unit_price": decimal_str(material_unit_price),
            "material_total_raw": decimal_str(material_raw),
            "material_total": round_money_half_up(material_raw),
            "work_unit_price": decimal_str(work_unit_price),
            "work_total_raw": decimal_str(work_raw),
            "work_total": round_money_half_up(work_raw),
            "line_total_raw": decimal_str(line_raw),
            "line_total": round_money_half_up(line_raw),
        },
        "formula": formula or {},
        "notes": notes or [],
    }
    if price_code:
        payload["price_code"] = price_code
    return payload


def zero_structure_line(code: str, name: str) -> dict[str, Any]:
    return estimate_line(
        code=code,
        name=name,
        unit="-",
        line_type="zero_excel_structure_line",
        quantity_raw=1,
        quantity_source="excel_structure_line",
        notes=[
            "Строка сохранена для структуры Excel.",
            "В текущем scope серая внутренняя себестоимость равна 0.",
        ],
    )


def calculate_schiedel_vent_channels(input_data: dict[str, Any]) -> dict[str, Any]:
    warnings = [
        "Количество материалов Schiedel 24 и 8 требует подтверждения у Елены/по спецификации.",
        "Количество доставки является ручным параметром.",
        "Клиентская часть не считается.",
    ]

    masonry_length = d(input_data["schiedel_masonry_total_length_m"])
    masonry_control_length = (
        d(input_data["vent_channel_1_height_m"])
        + d(input_data["vent_channel_2_height_m"]) * d(input_data["vent_channel_2_count"])
    )
    masonry_work_raw = masonry_length * d(input_data["schiedel_masonry_work_rate_per_m"])

    channel_2x_qty = d(input_data["schiedel_vent_channel_2x_count"])
    channel_2x_total_raw = channel_2x_qty * d(input_data["schiedel_vent_channel_2x_unit_price"])

    channel_3x_qty = d(input_data["schiedel_vent_channel_3x_count"])
    channel_3x_total_raw = channel_3x_qty * d(input_data["schiedel_vent_channel_3x_unit_price"])

    delivery_trips = d(input_data["schiedel_delivery_trips"])
    delivery_material_raw = delivery_trips * d(input_data["schiedel_delivery_truck_price"])
    delivery_work_raw = delivery_trips * d(input_data["schiedel_delivery_work_price"])

    direct_cost_base_before_consumables = (
        masonry_work_raw
        + channel_2x_total_raw
        + channel_3x_total_raw
        + delivery_material_raw
        + delivery_work_raw
    )
    consumables_total_raw = direct_cost_base_before_consumables * d(input_data["consumables_rate"])

    lines = [
        estimate_line(
            code="schiedel_masonry_work",
            name="Кладка вентканалов Schiedel",
            unit="мп",
            line_type="work",
            quantity_raw=masonry_length,
            quantity_source="schiedel_masonry_total_length_m",
            work_unit_price=input_data["schiedel_masonry_work_rate_per_m"],
            work_total_raw=masonry_work_raw,
            formula={
                "control_length_m": decimal_str(masonry_control_length),
                "control_formula": "vent_channel_1_height_m + vent_channel_2_height_m * vent_channel_2_count",
                "work_total": "schiedel_masonry_total_length_m * schiedel_masonry_work_rate_per_m",
            },
            notes=[
                "Серая сумма считается от raw 15.82 мп.",
                "Не считать от старого отображаемого количества 16 мп.",
            ],
        ),
        estimate_line(
            code="schiedel_vent_channel_2x_36_25",
            name="Вентиляционный канал 2х,36/25 см Schiedel",
            unit="шт",
            line_type="materials",
            quantity_raw=channel_2x_qty,
            quantity_source="manual_from_schiedel_specification_or_elena_table",
            price_code="schiedel_vent_channel_2x_36_25_item",
            material_unit_price=input_data["schiedel_vent_channel_2x_unit_price"],
            material_total_raw=channel_2x_total_raw,
            formula={
                "quantity": "manual/specification input",
                "material_total": "schiedel_vent_channel_2x_count * schiedel_vent_channel_2x_unit_price",
                "control_blocks_raw": "65.51515152",
                "secondary_control_value": "28",
            },
            notes=[
                "Количество 24 не выводится автоматически из контрольных правых значений.",
                "Контрольные числа сохранены справочно и не участвуют в quantity.",
            ],
        ),
        estimate_line(
            code="schiedel_vent_channel_3x_52_25",
            name="Вентиляционный канал 3х,52/25 см Schiedel",
            unit="шт",
            line_type="materials",
            quantity_raw=channel_3x_qty,
            quantity_source="manual_from_schiedel_specification_or_elena_table",
            price_code="schiedel_vent_channel_3x_52_25_item",
            material_unit_price=input_data["schiedel_vent_channel_3x_unit_price"],
            material_total_raw=channel_3x_total_raw,
            formula={
                "quantity": "manual/specification input",
                "material_total": "schiedel_vent_channel_3x_count * schiedel_vent_channel_3x_unit_price",
                "control_blocks_raw": "14.57575758",
                "secondary_control_value": "6",
            },
            notes=[
                "Количество 8 не выводится автоматически из контрольных правых значений.",
                "Контрольные числа сохранены справочно и не участвуют в quantity.",
            ],
        ),
        estimate_line(
            code="schiedel_delivery",
            name="Доставка вентканалов",
            unit="маш",
            line_type="material_and_work",
            quantity_raw=delivery_trips,
            quantity_source="manual_input",
            price_code="schiedel_delivery_truck",
            material_unit_price=input_data["schiedel_delivery_truck_price"],
            material_total_raw=delivery_material_raw,
            work_unit_price=input_data["schiedel_delivery_work_price"],
            work_total_raw=delivery_work_raw,
            formula={
                "material_total": "schiedel_delivery_trips * schiedel_delivery_truck_price",
                "work_total": "schiedel_delivery_trips * schiedel_delivery_work_price",
            },
        ),
        estimate_line(
            code="schiedel_consumables_tool_depreciation",
            name="Расходные материалы, амортизация инструмента",
            unit="комплект",
            line_type="percentage_addon",
            quantity_raw=1,
            quantity_source="direct_cost_base_before_consumables * consumables_rate",
            material_total_raw=consumables_total_raw,
            formula={
                "direct_cost_base_before_consumables": decimal_str(direct_cost_base_before_consumables),
                "consumables_rate": decimal_str(input_data["consumables_rate"]),
                "material_total_raw": decimal_str(consumables_total_raw),
            },
            notes=["Расходные материалы считаются как 3% от прямой базы 114456."],
        ),
        zero_structure_line("technical_supervision_zero", "Технический надзор"),
        zero_structure_line("procurement_storage_zero", "Заготовительно-складские расходы"),
        zero_structure_line("overhead_zero", "Накладные и общехозяйственные расходы"),
        zero_structure_line("profit_zero", "Сметная прибыль"),
    ]

    materials_raw = sum((d(line["internal_cost"]["material_total_raw"]) for line in lines), D0)
    works_raw = sum((d(line["internal_cost"]["work_total_raw"]) for line in lines), D0)
    displayed_materials = sum((int(line["internal_cost"]["material_total"]) for line in lines), 0)
    displayed_works = sum((int(line["internal_cost"]["work_total"]) for line in lines), 0)

    return {
        "section_code": "schiedel_vent_channels",
        "section_name": "ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel",
        "project_name": input_data["project_name"],
        "inputs": input_data,
        "calculation_blocks": {
            "masonry": {
                "schiedel_masonry_total_length_m": decimal_str(masonry_length),
                "control_length_m": decimal_str(masonry_control_length),
                "work_rate_per_m": decimal_str(input_data["schiedel_masonry_work_rate_per_m"]),
            },
            "materials": {
                "schiedel_vent_channel_2x_count": decimal_str(channel_2x_qty),
                "schiedel_vent_channel_3x_count": decimal_str(channel_3x_qty),
                "counts_source": "manual/specification input",
            },
            "delivery": {
                "schiedel_delivery_trips": decimal_str(delivery_trips),
            },
            "consumables": {
                "direct_cost_base_before_consumables": decimal_str(direct_cost_base_before_consumables),
                "consumables_rate": decimal_str(input_data["consumables_rate"]),
                "consumables_total_raw": decimal_str(consumables_total_raw),
            },
            "control_metrics": {
                "schiedel_2x_control_blocks_raw": "65.51515152",
                "schiedel_2x_secondary_control_value": "28",
                "schiedel_3x_control_blocks_raw": "14.57575758",
                "schiedel_3x_secondary_control_value": "6",
            },
        },
        "estimate_lines": lines,
        "totals": {
            "internal_materials_total_raw": decimal_str(materials_raw),
            "internal_materials_total": round_money_half_up(materials_raw),
            "internal_works_total_raw": decimal_str(works_raw),
            "internal_works_total": round_money_half_up(works_raw),
            "internal_section_total_raw": decimal_str(materials_raw + works_raw),
            "internal_section_total": round_money_half_up(materials_raw + works_raw),
            "sum_of_displayed_line_material_totals": displayed_materials,
            "sum_of_displayed_line_work_totals": displayed_works,
            "sum_of_displayed_line_totals": displayed_materials + displayed_works,
        },
        "warnings": warnings,
    }
