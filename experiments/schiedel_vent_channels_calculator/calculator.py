from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PRICING_DIR = REPO_ROOT / "experiments" / "pricing"
if str(PRICING_DIR) not in sys.path:
    sys.path.insert(0, str(PRICING_DIR))

from price_reader import (  # noqa: E402
    load_price_registry,
    load_project_price_overrides,
    resolve_price,
)


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


PRICE_FIELD_BY_CODE = {
    "schiedel_masonry_work": "schiedel_masonry_work_rate_per_m",
    "schiedel_vent_channel_2x_36_25": "schiedel_vent_channel_2x_unit_price",
    "schiedel_vent_channel_3x_52_25": "schiedel_vent_channel_3x_unit_price",
    "schiedel_delivery": "schiedel_delivery_truck_price",
}

PRICE_CODE_BY_FIELD = {
    "schiedel_masonry_work_rate_per_m": "schiedel_masonry_work_m",
    "schiedel_vent_channel_2x_unit_price": "schiedel_vent_channel_2x_36_25_item",
    "schiedel_vent_channel_3x_unit_price": "schiedel_vent_channel_3x_52_25_item",
    "schiedel_delivery_truck_price": "schiedel_delivery_truck",
}


def pricing_mode(input_data: dict[str, Any]) -> str:
    return (input_data.get("pricing") or {}).get("mode", "locked_case_prices")


def resolve_registry_path(input_data: dict[str, Any]) -> Path:
    raw_path = (input_data.get("pricing") or {}).get(
        "registry_path",
        "output/price_registry_filled_v3.xlsx",
    )
    path = Path(raw_path)
    return path if path.is_absolute() else REPO_ROOT / path


def build_effective_pricing(
    input_data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    mode = pricing_mode(input_data)
    if mode == "locked_case_prices":
        return dict(input_data), {
            "mode": mode,
            "prices_from_price_registry": 0,
            "prices_from_project_overrides": 0,
            "prices_from_fallback_input": 0,
            "warnings_count": 0,
            "price_resolutions_by_code": {},
        }, []

    if mode != "price_registry_with_fallback":
        raise ValueError(f"Unsupported pricing mode: {mode}")

    registry_path = resolve_registry_path(input_data)
    registry = load_price_registry(registry_path)
    overrides = load_project_price_overrides(registry_path)

    effective_data = dict(input_data)
    resolutions_by_code: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    summary = {
        "mode": mode,
        "registry_path": str(registry_path),
        "prices_from_price_registry": 0,
        "prices_from_project_overrides": 0,
        "prices_from_fallback_input": 0,
        "warnings_count": 0,
        "price_resolutions_by_code": resolutions_by_code,
    }

    for field_name, price_code in PRICE_CODE_BY_FIELD.items():
        original_price = input_data.get(field_name)
        resolved = resolve_price(price_code, original_price, registry, overrides)
        source = resolved["source"]
        if source == "price_registry":
            summary["prices_from_price_registry"] += 1
        elif source == "project_price_overrides":
            summary["prices_from_project_overrides"] += 1
        else:
            summary["prices_from_fallback_input"] += 1

        if resolved["warning"]:
            warnings.append(f"{price_code}: {resolved['warning']}")

        used_price = resolved["price"]
        effective_data[field_name] = float(used_price) if used_price is not None else original_price
        resolutions_by_code[price_code] = {
            "price_code": price_code,
            "unit_price_source": source,
            "unit_price_original": decimal_str(original_price),
            "unit_price_used": decimal_str(used_price) if used_price is not None else None,
            "price_warning": resolved["warning"],
        }

    summary["warnings_count"] = len(warnings)
    return effective_data, summary, warnings


def enrich_lines_with_pricing(
    lines: list[dict[str, Any]],
    pricing_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    if pricing_summary["mode"] == "locked_case_prices":
        return lines

    resolutions = pricing_summary.get("price_resolutions_by_code", {})
    enriched = []
    for line in lines:
        item = dict(line)
        price_code = item.get("price_code")
        if price_code in resolutions:
            item.update(resolutions[price_code])
        else:
            cost = item["internal_cost"]
            original_price = cost.get("material_unit_price") or cost.get("work_unit_price")
            item.setdefault("price_code", price_code)
            item["unit_price_source"] = "locked_case_prices"
            item["unit_price_original"] = str(original_price)
            item["unit_price_used"] = str(original_price)
            item["price_warning"] = None
        enriched.append(item)
    return enriched


def calculate_schiedel_vent_channels(input_data: dict[str, Any]) -> dict[str, Any]:
    original_input_data = dict(input_data)
    input_data, pricing_summary, pricing_warnings = build_effective_pricing(input_data)
    warnings = [
        "Количество материалов Schiedel 24 и 8 требует подтверждения у Елены/по спецификации.",
        "Количество доставки является ручным параметром.",
        "Клиентская часть не считается.",
        *pricing_warnings,
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
            price_code="schiedel_masonry_work_m",
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
    lines = enrich_lines_with_pricing(lines, pricing_summary)

    materials_raw = sum((d(line["internal_cost"]["material_total_raw"]) for line in lines), D0)
    works_raw = sum((d(line["internal_cost"]["work_total_raw"]) for line in lines), D0)
    displayed_materials = sum((int(line["internal_cost"]["material_total"]) for line in lines), 0)
    displayed_works = sum((int(line["internal_cost"]["work_total"]) for line in lines), 0)

    inputs = dict(original_input_data)
    if inputs.get("pricing") is None:
        inputs.pop("pricing", None)

    return {
        "section_code": "schiedel_vent_channels",
        "section_name": "ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel",
        "project_name": input_data["project_name"],
        "inputs": inputs,
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
        "pricing_summary": {
            key: value
            for key, value in pricing_summary.items()
            if key != "price_resolutions_by_code"
        },
        "warnings": warnings,
    }
