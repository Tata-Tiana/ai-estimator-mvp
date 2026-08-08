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
    # See floor_slab_1_calculator.py's identical guard for the full rationale: every
    # legitimate optional-value case here already guards before calling d(), so d(None) was
    # never meant to succeed - it silently became Decimal("None") and crashed with
    # decimal.InvalidOperation, with no indication of which field/row was the problem.
    if value is None:
        raise ValueError("numeric value is required, got None")
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


# Product types confirmed across real projects (2026-07-26): 1x/2x on one project, 3x/4x on another.
# CVENT is a rare distinct Schiedel product line (Elena: "бывает достаточно редко") — kept in the same
# enum so a project that has it doesn't need a schema change. Brand is always Schiedel per Elena's rule
# ("всегда используется Шидель, даже если в проекте не указано название, во всех проектах") — confirmed
# against a real delivered smeta that bills Schiedel-branded blocks even though that project's PDF
# drawings never name the brand explicitly. 2x/3x keep their pre-existing price codes (already real
# entries in the price registry); 1x/4x/cvent are new codes.
CHANNEL_TYPE_SPECS: dict[str, dict[str, str]] = {
    "1x": {
        "name": "Вентиляционный канал 1х Schiedel",
        "price_code": "schiedel_vent_channel_1x_item",
        "price_field": "schiedel_vent_channel_1x_unit_price",
    },
    "2x": {
        "name": "Вентиляционный канал 2х,36/25 см Schiedel",
        "price_code": "schiedel_vent_channel_2x_36_25_item",
        "price_field": "schiedel_vent_channel_2x_unit_price",
    },
    "3x": {
        "name": "Вентиляционный канал 3х,52/25 см Schiedel",
        "price_code": "schiedel_vent_channel_3x_52_25_item",
        "price_field": "schiedel_vent_channel_3x_unit_price",
    },
    "4x": {
        "name": "Вентиляционный канал 4х Schiedel",
        "price_code": "schiedel_vent_channel_4x_item",
        "price_field": "schiedel_vent_channel_4x_unit_price",
    },
    "cvent": {
        "name": "Вентиляционный канал CVENT Schiedel",
        "price_code": "schiedel_vent_channel_cvent_item",
        "price_field": "schiedel_vent_channel_cvent_unit_price",
    },
}

# Gas block used to build the vent-channel shaft itself (masonry between/around the Schiedel
# ceramic modules) — a DIFFERENT block from vent_chimney_cladding's 600x150x250 (that one lives in
# load_bearing_walls_lintels_calculator.py and is hardcoded D500, confirmed against a real smeta).
# This shaft-masonry block's density is NOT assumed by width/heuristic — it's whatever the project's
# own PDF specification states next to the block (found 2026-07-26: one real project labels its
# 150x250x650 shaft block D400 repeatedly, distinct from the wall-block-family D400/D500 rule which
# covers a different block size/purpose entirely). Both densities are supported so the calculator
# never has to guess.
SCHIEDEL_MASONRY_GAS_BLOCK_SPECS: dict[str, dict[str, str]] = {
    "D400": {
        "name": "Газобетонный блок D400 150x250x650 мм для кладки вентканалов",
        "price_code": "schiedel_masonry_gas_block_d400_m3",
        "price_field": "schiedel_masonry_gas_block_d400_unit_price",
    },
    "D500": {
        "name": "Газобетонный блок D500 150x250x650 мм для кладки вентканалов",
        "price_code": "schiedel_masonry_gas_block_d500_m3",
        "price_field": "schiedel_masonry_gas_block_d500_unit_price",
    },
}

PRICE_FIELD_BY_CODE = {
    "schiedel_masonry_work": "schiedel_masonry_work_rate_per_m",
    "schiedel_delivery": "schiedel_delivery_truck_price",
    **{
        f"schiedel_vent_channel_{product_type}": spec["price_field"]
        for product_type, spec in CHANNEL_TYPE_SPECS.items()
    },
    **{
        f"schiedel_masonry_gas_block_{density}": spec["price_field"]
        for density, spec in SCHIEDEL_MASONRY_GAS_BLOCK_SPECS.items()
    },
}

PRICE_CODE_BY_FIELD = {
    "schiedel_masonry_work_rate_per_m": "schiedel_masonry_work_m",
    "schiedel_delivery_truck_price": "schiedel_delivery_truck",
    **{spec["price_field"]: spec["price_code"] for spec in CHANNEL_TYPE_SPECS.values()},
    **{spec["price_field"]: spec["price_code"] for spec in SCHIEDEL_MASONRY_GAS_BLOCK_SPECS.values()},
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
            "unit_price_original": decimal_str(original_price) if original_price is not None else None,
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
        "Количество вентканалов по типам берётся из schiedel_channel_items — из спецификации проекта "
        "или, если PDF не даёт готовое количество в штуках, вручную от сметчицы.",
        "Количество доставки является ручным параметром.",
        "Клиентская часть не считается.",
        *pricing_warnings,
    ]

    # Masonry work is the one payable quantity regardless of channel type/count (Elena,
    # 2026-07-21: "работа у нас одна") — driven solely by the reviewed total length, in
    # running meters. Shaft count/height are NOT tracked here at all (Elena, 2026-07-26:
    # "не надо считать шахты, это не важно") — only module/material count matters.
    masonry_length = d(input_data["schiedel_masonry_total_length_m"])
    masonry_work_raw = masonry_length * d(input_data["schiedel_masonry_work_rate_per_m"])

    # schiedel_channel_items[]: dynamic list of {product_type, quantity_pcs}, replacing the
    # old hardcoded schiedel_vent_channel_2x_count/_3x_count scalar pair (2026-07-26). Rows
    # with the same product_type are summed, same bucketing convention as
    # wall_block_items_totals() elsewhere in this pipeline. Any subset of the five known
    # types can appear; a project with only 1x and 2x or only 3x and 4x (both real project
    # cases) needs no code change either way.
    channel_items_in = input_data.get("schiedel_channel_items") or []
    channel_totals: dict[str, Decimal] = {product_type: D0 for product_type in CHANNEL_TYPE_SPECS}
    for item in channel_items_in:
        product_type = item.get("product_type")
        if product_type not in CHANNEL_TYPE_SPECS:
            raise ValueError(
                f"schiedel_channel_items[].product_type must be one of {sorted(CHANNEL_TYPE_SPECS)}"
            )
        # `.get(key, 0)` alone doesn't help when the key is present with value None (the more
        # common real shape of extraction-derived rows) - `or 0` catches both missing and null.
        quantity_pcs = d(item.get("quantity_pcs") or 0)
        if quantity_pcs < D0:
            raise ValueError("schiedel_channel_items[].quantity_pcs must be >= 0")
        channel_totals[product_type] += quantity_pcs

    channel_lines: list[dict[str, Any]] = []
    channel_material_raw_total = D0
    channel_breakdown: dict[str, str] = {}
    for product_type, spec in CHANNEL_TYPE_SPECS.items():
        quantity_pcs = channel_totals[product_type]
        channel_breakdown[f"schiedel_channel_{product_type}_count"] = decimal_str(quantity_pcs)
        if quantity_pcs <= D0:
            continue
        unit_price = d(input_data[spec["price_field"]])
        total_raw = quantity_pcs * unit_price
        channel_material_raw_total += total_raw
        channel_lines.append(
            estimate_line(
                code=f"schiedel_vent_channel_{product_type}",
                name=spec["name"],
                unit="шт",
                line_type="materials",
                quantity_raw=quantity_pcs,
                quantity_source="sum of schiedel_channel_items rows with this product_type",
                price_code=spec["price_code"],
                material_unit_price=unit_price,
                material_total_raw=total_raw,
            )
        )

    # schiedel_masonry_gas_block_items[]: additive, optional list of {density, volume_m3} for the
    # gas block used to build the vent-channel shaft itself. Absent/empty by default — projects that
    # never had this field keep byte-identical output. Density is taken as-is from the spec (D400 or
    # D500), never defaulted from block width.
    masonry_gas_block_items_in = input_data.get("schiedel_masonry_gas_block_items") or []
    masonry_gas_block_totals: dict[str, Decimal] = {
        density: D0 for density in SCHIEDEL_MASONRY_GAS_BLOCK_SPECS
    }
    for item in masonry_gas_block_items_in:
        density = item.get("density")
        if density not in SCHIEDEL_MASONRY_GAS_BLOCK_SPECS:
            raise ValueError(
                "schiedel_masonry_gas_block_items[].density must be one of "
                f"{sorted(SCHIEDEL_MASONRY_GAS_BLOCK_SPECS)}"
            )
        volume_m3 = d(item.get("volume_m3") or 0)
        if volume_m3 < D0:
            raise ValueError("schiedel_masonry_gas_block_items[].volume_m3 must be >= 0")
        masonry_gas_block_totals[density] += volume_m3

    masonry_gas_block_lines: list[dict[str, Any]] = []
    masonry_gas_block_material_raw_total = D0
    masonry_gas_block_breakdown: dict[str, str] = {}
    for density, spec in SCHIEDEL_MASONRY_GAS_BLOCK_SPECS.items():
        volume_m3 = masonry_gas_block_totals[density]
        masonry_gas_block_breakdown[f"schiedel_masonry_gas_block_{density}_volume_m3"] = decimal_str(
            volume_m3
        )
        if volume_m3 <= D0:
            continue
        unit_price = d(input_data[spec["price_field"]])
        total_raw = volume_m3 * unit_price
        masonry_gas_block_material_raw_total += total_raw
        masonry_gas_block_lines.append(
            estimate_line(
                code=f"schiedel_masonry_gas_block_{density}",
                name=spec["name"],
                unit="м3",
                line_type="materials",
                quantity_raw=volume_m3,
                quantity_source="sum of schiedel_masonry_gas_block_items rows with this density",
                price_code=spec["price_code"],
                material_unit_price=unit_price,
                material_total_raw=total_raw,
            )
        )

    delivery_trips = d(input_data["schiedel_delivery_trips"])
    delivery_material_raw = delivery_trips * d(input_data["schiedel_delivery_truck_price"])
    delivery_work_raw = delivery_trips * d(input_data["schiedel_delivery_work_price"])

    direct_cost_base_before_consumables = (
        masonry_work_raw
        + channel_material_raw_total
        + masonry_gas_block_material_raw_total
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
            formula={"work_total": "schiedel_masonry_total_length_m * schiedel_masonry_work_rate_per_m"},
        ),
        *channel_lines,
        *masonry_gas_block_lines,
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
                "work_rate_per_m": decimal_str(input_data["schiedel_masonry_work_rate_per_m"]),
            },
            "materials": {
                **channel_breakdown,
                "counts_source": "schiedel_channel_items (specification or manual estimator input)",
            },
            "masonry_gas_block": {
                **masonry_gas_block_breakdown,
                "volume_source": (
                    "sum of schiedel_masonry_gas_block_items rows (density trusted as stated in the "
                    "project's own PDF specification, never defaulted from block width)"
                ),
            },
            "delivery": {
                "schiedel_delivery_trips": decimal_str(delivery_trips),
            },
            "consumables": {
                "direct_cost_base_before_consumables": decimal_str(direct_cost_base_before_consumables),
                "consumables_rate": decimal_str(input_data["consumables_rate"]),
                "consumables_total_raw": decimal_str(consumables_total_raw),
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
