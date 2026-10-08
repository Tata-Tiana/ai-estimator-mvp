from __future__ import annotations

import re
from typing import Any

from core.contract_loader import (
    all_supplier_inputs,
    default_by_key,
    load_contract,
    price_keys as contract_price_keys,
)
from core.rebar_item_defaults import fill_rebar_catalog_defaults


REBAR_TEMPLATE_PRICE_KEY = "rebar_unit_price_by_item"
ELEMENT_FIELDS = {
    "element_id",
    "display_name",
    "element_type",
    "level",
    "width_m",
    "height_m",
    "length_m",
    "count",
    "concrete_grade",
    "concrete_volume_m3",
    "membrane_area_m2",
    "inventory_formwork_area_m2",
    "timber_formwork_area_m2",
    "horizontal_insulation_material",
    "horizontal_insulation_thickness_mm",
    "horizontal_insulation_area_m2",
    "horizontal_insulation_volume_m3",
    "include_in_estimate",
}
REBAR_FIELDS = {
    "element_id",
    "code",
    "name",
    "steel_class",
    "diameter_mm",
    "source_length_m",
    "kg_per_meter",
    "rod_length_m",
}


def _rebar_registry_code(steel_class: Any, diameter_mm: Any) -> str | None:
    if not steel_class or diameter_mm in (None, ""):
        return None
    try:
        diameter = int(float(diameter_mm))
    except (TypeError, ValueError):
        return None
    digits = re.sub(r"\D", "", str(steel_class))
    return f"rebar_a{digits}_d{diameter}_m" if digits else None


def build_calculator_input(normalized_review: dict[str, Any]) -> dict[str, Any]:
    contract = load_contract("grillage")
    defaults = default_by_key(contract)
    scalars = normalized_review["scalar_parameters"]
    production_items = normalized_review["production_items"]
    resolved_prices = normalized_review["resolved_prices"]

    element_rows = production_items.get("grillage_elements") or []
    if not element_rows:
        raise ValueError("grillage: grillage_elements has no rows")
    rebar_rows = production_items.get("grillage_rebar_items") or []
    if not rebar_rows:
        raise ValueError("grillage: grillage_rebar_items has no rows")

    result: dict[str, Any] = {
        "project_name": normalized_review["project_name"],
        "grillage_elements": [
            {key: value for key, value in row.items() if key in ELEMENT_FIELDS}
            for row in element_rows
        ],
    }
    included_inventory_formwork_area = sum(
        float(row.get("inventory_formwork_area_m2") or 0)
        for row in result["grillage_elements"]
        if row.get("include_in_estimate", True)
    )

    rebar_prices = resolved_prices.get(REBAR_TEMPLATE_PRICE_KEY) or {}
    rod_length_default = defaults["rod_length_m"]["value"]
    result["rebar_items"] = []
    for index, row in enumerate(rebar_rows, start=1):
        registry_code = _rebar_registry_code(row.get("steel_class"), row.get("diameter_mm"))
        price = rebar_prices.get(registry_code) if registry_code else None
        if price is None:
            raise ValueError(
                f"grillage: no resolved price for {row.get('steel_class')}/"
                f"D{row.get('diameter_mm')} ({registry_code!r})"
            )
        item = {key: value for key, value in row.items() if key in REBAR_FIELDS}
        item.setdefault("code", f"grillage_rebar_{index}")
        item.setdefault("name", f"Арматура ростверка {row.get('steel_class')} D{row.get('diameter_mm')}")
        item = fill_rebar_catalog_defaults(
            {**item, "unit_price_per_m": price},
            section="grillage",
        )
        item.setdefault("rod_length_m", rod_length_default)
        result["rebar_items"].append(item)

    for entry in all_supplier_inputs(contract):
        key = entry["key"]
        row = scalars.get(key)
        value = row["value_number"] if row else None
        if value is None:
            if key == "inventory_formwork_rental_unit_price" and included_inventory_formwork_area > 0:
                raise ValueError(
                    "grillage: inventory formwork supplier rate is required "
                    "when included elements have inventory formwork area"
                )
            if entry.get("required", True):
                raise ValueError(f"grillage: required manual value '{key}' is blank")
            value = entry.get("default_value", 0)
        result[key] = value

    for key, entry in defaults.items():
        if key in result or "[" in (entry.get("calculator_input_path") or ""):
            continue
        result[key] = entry["value"]

    for entry in contract_price_keys(contract):
        key = entry["key"]
        if key == REBAR_TEMPLATE_PRICE_KEY:
            continue
        if key in resolved_prices:
            result[key] = resolved_prices[key]
        elif entry.get("required", True):
            raise ValueError(f"grillage: required price '{key}' has no resolved value")

    return result
