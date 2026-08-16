"""P6 adapter for load_bearing_walls_lintels_p6.

This is intentionally separate from the old load_bearing_walls_lintels adapter. It consumes the
new clean zone-shaped workbook data and builds the input expected by
load_bearing_walls_lintels_p6_calculator.py:

- wall_zones[] is the only production shape for masonry zones;
- block/rebar/lintel flat workbook groups are nested back under their zone_id;
- lintel_rebar_items are nested under their lintel_id;
- no scalar fallback is accepted.
"""

from __future__ import annotations

import re
from typing import Any

from core.contract_loader import default_by_key, load_contract, price_keys as contract_price_keys
from core.rebar_item_defaults import fill_rebar_catalog_defaults

SECTION_CODE = "load_bearing_walls_lintels_p6"
ZONES_GROUP_KEY = "wall_zones"
BLOCK_ITEMS_GROUP_KEY = "wall_block_items"
WALL_REBAR_GROUP_KEY = "wall_chasing_rebar_items"
LINTEL_ITEMS_GROUP_KEY = "lintel_items"
LINTEL_REBAR_GROUP_KEY = "lintel_rebar_items"
REBAR_TEMPLATE_PRICE_KEY = "rebar_unit_price_by_item"


def _num(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _drop_blank_values(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if value not in (None, "") and not key.startswith("_")}


def _rebar_registry_code(steel_class: Any, diameter_mm: Any) -> str | None:
    if not steel_class or diameter_mm in (None, ""):
        return None
    try:
        diameter = int(float(diameter_mm))
    except (TypeError, ValueError):
        return None
    digits = re.sub(r"\D", "", str(steel_class))
    if not digits:
        return None
    return f"rebar_a{digits}_d{diameter}_m"


def _priced_rebar_item(item: dict[str, Any], rebar_prices: dict[str, float]) -> dict[str, Any]:
    registry_code = _rebar_registry_code(item.get("steel_class"), item.get("diameter_mm"))
    price = rebar_prices.get(registry_code) if registry_code else None
    if price is None:
        raise ValueError(
            f"{SECTION_CODE}: no resolved price for rebar item "
            f"{item.get('steel_class')}/⌀{item.get('diameter_mm')} "
            f"(expected sheet 02 row with price_registry_code={registry_code!r}, "
            f"calc_price_key={REBAR_TEMPLATE_PRICE_KEY})"
        )
    cleaned = _drop_blank_values(item)
    cleaned["unit_price_per_m"] = price
    with_catalog = fill_rebar_catalog_defaults(cleaned, section=SECTION_CODE)
    allowed_fields = {
        "item_id",
        "purpose",
        "steel_class",
        "diameter_mm",
        "spec_length_m",
        "kg_per_meter",
        "rod_length_m",
        "unit_price_per_m",
        "source_label",
    }
    return {key: value for key, value in with_catalog.items() if key in allowed_fields}


def _require_zone_id(row: dict[str, Any], group_name: str, valid_zone_ids: set[str]) -> str:
    zone_id = row.get("zone_id")
    if not zone_id:
        raise ValueError(f"{SECTION_CODE}: {group_name} row has no zone_id: {row!r}")
    if zone_id not in valid_zone_ids:
        raise ValueError(
            f"{SECTION_CODE}: {group_name} row {row.get('item_id') or row.get('lintel_id') or row!r} "
            f"has zone_id {zone_id!r}, but no wall_zones row has this zone_id."
        )
    return str(zone_id)


def _default_purpose_for_wall_rebar(zone_kind: str | None) -> str:
    if zone_kind == "parapet":
        return "parapet_chasing"
    return "masonry_chasing"


def _default_purpose_for_lintel_rebar() -> str:
    return "lintels"


def _zone_kind_from_zone_id(zone_id: str) -> str:
    zone_id_lower = zone_id.lower()
    if "parapet" in zone_id_lower:
        return "parapet"
    if "vent" in zone_id_lower or "chimney" in zone_id_lower:
        return "vent_chimney_cladding"
    if "floor_2" in zone_id_lower:
        return "floor_2"
    if "floor_1" in zone_id_lower:
        return "main_walls"
    return "other"


def _ensure_zones_from_child_rows(zone_rows: list[dict[str, Any]], production_items: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    """Keep reviewed workbooks resilient when a visible zone marker row is hidden/omitted.

    The repeated child rows are the actual production data and carry both zone_id and the
    visible zone label. If a child references a zone whose own wall_zones marker row is absent,
    synthesize the minimal marker instead of silently losing the whole zone.
    """
    seen = {str(row.get("zone_id")) for row in zone_rows if row.get("zone_id")}
    synthesized: list[dict[str, Any]] = []
    for group_key in (BLOCK_ITEMS_GROUP_KEY, WALL_REBAR_GROUP_KEY, LINTEL_ITEMS_GROUP_KEY, LINTEL_REBAR_GROUP_KEY):
        for item in production_items.get(group_key) or []:
            zone_id = item.get("zone_id")
            if not zone_id:
                continue
            zone_id = str(zone_id)
            if zone_id in seen:
                continue
            label = item.get("_zone_label") or zone_id
            synthesized.append(
                {
                    "zone_id": zone_id,
                    "display_name": label,
                    "zone_kind": _zone_kind_from_zone_id(zone_id),
                }
            )
            seen.add(zone_id)
    return zone_rows + synthesized


def build_calculator_input(normalized_review: dict[str, Any]) -> dict[str, Any]:
    contract = load_contract(SECTION_CODE)
    defaults = default_by_key(contract)
    production_items = normalized_review["production_items"]
    resolved_prices = normalized_review["resolved_prices"]

    zone_rows = _ensure_zones_from_child_rows(production_items.get(ZONES_GROUP_KEY) or [], production_items)
    if not zone_rows:
        raise ValueError(f"{SECTION_CODE}: no wall_zones rows found on sheet 01")

    valid_zone_ids = {row.get("zone_id") for row in zone_rows if row.get("zone_id")}
    if len(valid_zone_ids) != len([row for row in zone_rows if row.get("zone_id")]):
        raise ValueError(f"{SECTION_CODE}: wall_zones contains duplicate or blank zone_id values")

    zone_by_id: dict[str, dict[str, Any]] = {}
    for zone in zone_rows:
        zone_id = zone.get("zone_id")
        if not zone_id:
            raise ValueError(f"{SECTION_CODE}: wall_zones row is missing zone_id: {zone!r}")
        cleaned_zone = _drop_blank_values(zone)
        cleaned_zone.setdefault("display_name", zone_id)
        cleaned_zone.setdefault("zone_kind", "other")
        cleaned_zone.setdefault("block_items", [])
        cleaned_zone.setdefault("chasing_rebar_items", [])
        cleaned_zone.setdefault("unassigned_lintel_rebar_items", [])
        cleaned_zone.setdefault("lintel_items", [])
        zone_by_id[str(zone_id)] = cleaned_zone

    for row in production_items.get(BLOCK_ITEMS_GROUP_KEY) or []:
        zone_id = _require_zone_id(row, BLOCK_ITEMS_GROUP_KEY, valid_zone_ids)
        item = _drop_blank_values(row)
        item.pop("zone_id", None)
        if not item.get("item_id"):
            item["item_id"] = f"{item.get('block_density', 'block')}_{len(zone_by_id[zone_id]['block_items']) + 1}"
        for field in ("volume_m3", "material_unit_price", "pallet_volume_m3"):
            if field in item:
                number = _num(item[field])
                item[field] = number if number is not None else item[field]
        zone_by_id[zone_id]["block_items"].append(item)

    rebar_prices = resolved_prices.get(REBAR_TEMPLATE_PRICE_KEY) or {}
    zone_kind_by_id = {zone_id: zone.get("zone_kind") for zone_id, zone in zone_by_id.items()}
    for row in production_items.get(WALL_REBAR_GROUP_KEY) or []:
        zone_id = _require_zone_id(row, WALL_REBAR_GROUP_KEY, valid_zone_ids)
        item = _drop_blank_values(row)
        item.pop("zone_id", None)
        item.setdefault("purpose", _default_purpose_for_wall_rebar(zone_kind_by_id.get(zone_id)))
        if not item.get("item_id"):
            item["item_id"] = f"{zone_id}_{item['purpose']}_{item.get('steel_class')}_d{item.get('diameter_mm')}"
        zone_by_id[zone_id]["chasing_rebar_items"].append(_priced_rebar_item(item, rebar_prices))

    lintel_by_zone_and_id: dict[tuple[str, str], dict[str, Any]] = {}
    for row in production_items.get(LINTEL_ITEMS_GROUP_KEY) or []:
        zone_id = _require_zone_id(row, LINTEL_ITEMS_GROUP_KEY, valid_zone_ids)
        item = _drop_blank_values(row)
        item.pop("zone_id", None)
        lintel_id = item.get("lintel_id")
        if not lintel_id:
            lintel_id = f"{item.get('lintel_kind', 'lintel')}_{len(zone_by_id[zone_id]['lintel_items']) + 1}"
            item["lintel_id"] = lintel_id
        item.setdefault("lintel_kind", "u_block")
        item.setdefault("rebar_items", [])
        for field in (
            "total_length_m",
            "concrete_volume_m3",
            "formwork_horizontal_area_m2",
            "formwork_vertical_area_m2",
            "insulation_length_m",
            "insulation_eps_spec_volume_m3",
        ):
            if field in item:
                number = _num(item[field])
                item[field] = number if number is not None else item[field]
        zone_by_id[zone_id]["lintel_items"].append(item)
        lintel_by_zone_and_id[(zone_id, str(lintel_id))] = item

    for row in production_items.get(LINTEL_REBAR_GROUP_KEY) or []:
        zone_id = _require_zone_id(row, LINTEL_REBAR_GROUP_KEY, valid_zone_ids)
        lintel_id = row.get("lintel_id")
        item = _drop_blank_values(row)
        item.pop("zone_id", None)
        item.pop("lintel_id", None)
        item.setdefault("purpose", _default_purpose_for_lintel_rebar())
        if not item.get("item_id"):
            item["item_id"] = f"{zone_id}_{lintel_id or 'unassigned_lintel'}_{item.get('steel_class')}_d{item.get('diameter_mm')}"
        if not lintel_id:
            zone_by_id[zone_id]["unassigned_lintel_rebar_items"].append(_priced_rebar_item(item, rebar_prices))
            continue
        lintel = lintel_by_zone_and_id.get((zone_id, str(lintel_id)))
        if lintel is None:
            raise ValueError(
                f"{SECTION_CODE}: lintel_rebar_items row references lintel_id={lintel_id!r} "
                f"in zone_id={zone_id!r}, but no lintel_items row has that pair."
            )
        lintel["rebar_items"].append(_priced_rebar_item(item, rebar_prices))

    empty_block_zones = [
        zone.get("display_name") or zone_id
        for zone_id, zone in zone_by_id.items()
        if not zone.get("block_items")
    ]
    if empty_block_zones:
        raise ValueError(
            f"{SECTION_CODE}: every wall_zones row must have at least one wall_block_items row. "
            f"Missing block rows for: {empty_block_zones}"
        )

    rates: dict[str, Any] = {}
    for price_key in contract_price_keys(contract):
        key = price_key["key"]
        if key == REBAR_TEMPLATE_PRICE_KEY:
            continue
        if key in resolved_prices:
            rates[key] = resolved_prices[key]
        elif price_key.get("required", True):
            raise ValueError(f"{SECTION_CODE}: required price '{key}' has no resolved value")

    default_values = {key: entry["value"] for key, entry in defaults.items()}

    # scaffolding_setup_quantity/scaffolding_timber_quantity_m3 moved off the pure-DEFAULT path
    # 2026-08-16 - real smetas disagree per project (ТРЦ 2/2, АРК 1/1.5, ЮСВ 1/1 м3), no formula
    # found, so they no longer live in `defaults(contract)` at all. Read from sheet 01-1 (manual
    # review) instead, falling back to 2/2 only if genuinely still unset - matches the typical
    # value shown to Elena on sheet 01-1, not a silently different number.
    scalar_parameters = normalized_review.get("scalar_parameters") or {}
    for manual_key, fallback in (
        ("scaffolding_setup_quantity", 2),
        ("scaffolding_timber_quantity_m3", 2),
    ):
        manual_value = (scalar_parameters.get(manual_key) or {}).get("value_number")
        default_values[manual_key] = manual_value if manual_value is not None else fallback

    return {
        "project_name": normalized_review["project_name"],
        "wall_zones": list(zone_by_id.values()),
        "rates": rates,
        "defaults": default_values,
        "rebar_metal_delivery_trucks": 0,
    }
