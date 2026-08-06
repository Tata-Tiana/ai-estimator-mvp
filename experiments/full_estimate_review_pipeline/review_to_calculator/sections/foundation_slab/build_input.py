"""foundation_slab: normalized_review -> FoundationSlabInput-shaped dict.

Fourth adapter for review_to_calculator (see ../../ADAPTER_BUILD_PLAN.md, Этап 2). The
most involved section so far: 6 fixed `*_calc_method` production defaults (formwork,
plywood, rebar, logistics, consumables - all single fixed modes like earthworks/
schiedel), one *dynamically* chosen mode (thermal_insert_mode - see below, unlike every
other calc_method in this whole pipeline so far), and the first use of core/'s new
per-item "template" price mechanism (see core/workbook_reader.py's
template_price_keys()/read_prices(), core/price_resolver.py's resolve_prices() -
added 2026-08-05 specifically to unblock this adapter, needed by every future
rebar-bearing section too: floor_slab_1, floor_slab_2, load_bearing_walls_lintels).

Fixed production calc_method defaults (from the contract's `defaults:`, all
`allow_override_later: false`): formwork_calc_method=spec_area,
plywood_calc_method=actual_area_with_waste, rebar_calc_method=spec_length_m,
logistics_and_supply_calc_method=section_total_rate,
consumables_tool_amortization_calc_method=section_total_rate.

thermal_insert_mode is the one exception in this whole pipeline: it is NOT a single
fixed default here, because the review-workbook layer itself already treats
thermal_insert_items[] and the scalar thermal_insert_50/100_length_m pair as mutually
exclusive alternatives for the same real-world data (see
populate_review_workbook_from_extraction.py's not_required_alt handling and
target_aliases_ru.yaml - a real project gives EITHER a fixed 50mm+100mm pair OR
arbitrary-size items, never both). This adapter picks "items" mode when
thermal_insert_items has real rows on sheet 01, else falls back to the contract's
"standard_50_100" default and reads the scalar fields instead.

Per-item rebar pricing: RebarItemInput requires each row to carry its own
unit_price_per_m directly (same convention as ThermalInsertItem's material_unit_price)
- Elena is never asked to type a price into a rebar row on sheet 01 (correction_columns
for foundation_rebar_items only cover PDF geometry fields), so this adapter must inject
it. Sheet 02 expands the contract's single `rebar_unit_price_by_item` template
price_key into one real row per steel_class/diameter_mm actually in the project
(registry code convention: rebar_a{digits from steel_class}_d{diameter_mm}_m - must
match build_review_workbook_from_contracts.py's _rebar_registry_code() exactly, kept
duplicated here rather than cross-importing from outside review_to_calculator/).
resolve_prices() returns this template as {registry_code: price} instead of a single
float (see core/price_resolver.py) - this adapter looks up each item's own code in
that dict and raises a specific, item-named error if a particular diameter/class has
no matching price, rather than a generic "some rebar price is missing".

foundation_wall_items / column_footing_items are diagnostic-only
(production_input: false, calculator_input_path: "") - never read here, the
calculator has no field for them.

Field sourcing for scalars: membrane_area_m2, slab_side_formwork_area_m2,
eps50_under_slab_volume_m3, concrete_project_volume_m3 (all required - the last one
already reflects any slab_zones autosum the review-workbook layer applied, and the
calculator's own __post_init__ additionally re-derives it from slab_zones when that
group is passed, so both paths agree); supplier_inputs (rebar_crane_shifts,
rebar_metal_delivery_trucks, box_total_metal_weight_kg, concrete_pump_shifts,
logistics_and_supply_amount, consumables_tool_amortization_amount) are read explicitly
by key from `scalars` since FoundationSlabInput has no dataclass default for any of
them; everything else not explicitly listed comes mechanically from contract
defaults/resolved_prices by exact key-name match, same pattern as every prior adapter -
except per-item defaults (calculator_input_path containing "[", currently only
rod_length_m) which the generic fallback loop skips on principle since they belong on
each rebar_items row, not as a flat top-level field.
"""

from __future__ import annotations

import re
from typing import Any

from core.contract_loader import (
    all_supplier_inputs,
    default_by_key,
    load_contract,
    price_keys as contract_price_keys,
)

REQUIRED_SCALARS = (
    "membrane_area_m2",
    "slab_side_formwork_area_m2",
    "eps50_under_slab_volume_m3",
    "concrete_project_volume_m3",
)
OPTIONAL_STANDARD_5010_SCALARS = (
    "thermal_insert_50_length_m",
    "thermal_insert_100_length_m",
    "thermal_insert_combined_length_m",
    "thermal_insert_50_material_spec_qty",
    "thermal_insert_100_material_spec_qty",
)
OPTIONAL_PRODUCTION_ITEM_GROUPS = ("slab_zones",)
REBAR_GROUP_KEY = "foundation_rebar_items"
REBAR_TEMPLATE_PRICE_KEY = "rebar_unit_price_by_item"
THERMAL_INSERT_ITEMS_KEY = "thermal_insert_items"


def _rebar_registry_code(steel_class: Any, diameter_mm: Any) -> str | None:
    """Must match build_review_workbook_from_contracts.py's _rebar_registry_code() exactly -
    steel_class as extracted is Russian text (e.g. "А500С"), the registry code only encodes
    the numeric class, so match on digits rather than transliterating."""
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


def build_calculator_input(normalized_review: dict[str, Any]) -> dict[str, Any]:
    contract = load_contract("foundation_slab")
    defaults = default_by_key(contract)
    scalars = normalized_review["scalar_parameters"]
    production_items = normalized_review["production_items"]
    resolved_prices = normalized_review["resolved_prices"]

    result: dict[str, Any] = {
        "project_name": normalized_review["project_name"],
    }

    for key in REQUIRED_SCALARS:
        row = scalars.get(key)
        value = row["value_number"] if row else None
        if value is None:
            raise ValueError(
                f"foundation_slab: required parameter '{key}' is missing/blank on sheet "
                "01 (check 'Найдено в проекте' / 'Исправить / ввести значение')"
            )
        result[key] = value

    for key in OPTIONAL_PRODUCTION_ITEM_GROUPS:
        items = production_items.get(key)
        if items:
            result[key] = items

    # thermal_insert_mode: the one dynamically-chosen calc_method in this pipeline - see
    # module docstring. Falls back to the contract's fixed default (standard_50_100) when
    # thermal_insert_items has no real rows.
    thermal_items = production_items.get(THERMAL_INSERT_ITEMS_KEY)
    if thermal_items:
        result["thermal_insert_mode"] = "items"
        result["thermal_insert_items"] = thermal_items
    else:
        result["thermal_insert_mode"] = defaults["thermal_insert_mode"]["value"]
        for key in OPTIONAL_STANDARD_5010_SCALARS:
            row = scalars.get(key)
            if row and row["value_number"] is not None:
                result[key] = row["value_number"]

    # foundation_rebar_items -> rebar_items, with per-item unit_price_per_m injected from
    # sheet 02's expanded rebar_<class>_d<diameter>_m template rows (see module docstring).
    rebar_rows = production_items.get(REBAR_GROUP_KEY)
    if not rebar_rows:
        raise ValueError(
            "foundation_slab: required repeated-row group 'foundation_rebar_items' has no "
            "rows on sheet 01"
        )
    rebar_prices = resolved_prices.get(REBAR_TEMPLATE_PRICE_KEY) or {}
    rod_length_default = defaults["rod_length_m"]["value"]
    priced_rebar_items = []
    for item in rebar_rows:
        registry_code = _rebar_registry_code(item.get("steel_class"), item.get("diameter_mm"))
        price = rebar_prices.get(registry_code) if registry_code else None
        if price is None:
            raise ValueError(
                f"foundation_slab: no resolved price for rebar item "
                f"{item.get('steel_class')}/⌀{item.get('diameter_mm')} "
                f"(expected sheet 02 row with price_registry_code={registry_code!r}, "
                "calc_price_key=rebar_unit_price_by_item)"
            )
        priced_item = {**item, "unit_price_per_m": price}
        # rod_length_m is not one of foundation_rebar_items' own columns (PDF specs never
        # give it) - it's a per-item "catalog default unless item overrides" value, so it's
        # injected here rather than pulled from `defaults` as a flat top-level field.
        priced_item.setdefault("rod_length_m", rod_length_default)
        priced_rebar_items.append(priced_item)
    result["rebar_items"] = priced_rebar_items

    # supplier_inputs (crane/pump shifts, delivery trucks, box metal weight, legacy fixed
    # amounts): FoundationSlabInput has no dataclass default for any of these, so every one
    # must be supplied here explicitly - not covered by the `defaults` fallback loop below,
    # which only walks the contract's `defaults:` section. Read via scalars (populated from
    # sheet 01 for AUTO_CALCULATED fields, sheet 01-1 for MANUAL_REVIEW/SUPPLIER_INPUT fields
    # via core/workbook_reader.py's read_manual_values()). required:false entries
    # (logistics_and_supply_amount, consumables_tool_amortization_amount) default to 0 when
    # absent - production always uses the *_rate calc_method instead, these are legacy-only.
    for entry in all_supplier_inputs(contract):
        key = entry["key"]
        row = scalars.get(key)
        value = row["value_number"] if row else None
        if value is None:
            if entry.get("required", True):
                raise ValueError(
                    f"foundation_slab: required supplier input '{key}' is missing/blank "
                    "(check sheet 01 or 01-1's 'Исправить для этого проекта')"
                )
            value = 0
        result[key] = value

    for key, entry in defaults.items():
        if key in result:
            continue
        # Per-item defaults (calculator_input_path targets rebar_items[*].<field>, not a
        # flat top-level FoundationSlabInput field) are injected above, at the item level -
        # skip them here on principle, not just for rod_length_m specifically.
        if "[" in (entry.get("calculator_input_path") or ""):
            continue
        result[key] = entry["value"]

    for price_key in contract_price_keys(contract):
        key = price_key["key"]
        if key == REBAR_TEMPLATE_PRICE_KEY:
            continue  # handled above, per-item, not a flat top-level field
        if key in resolved_prices:
            result[key] = resolved_prices[key]
        elif price_key.get("required", True):
            raise ValueError(f"foundation_slab: required price '{key}' has no resolved value")

    return result
