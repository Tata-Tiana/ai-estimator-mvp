"""floor_slab_2: normalized_review -> calculate_floor_slab_2() plain-dict input.

Fifth adapter for review_to_calculator (see ../../ADAPTER_BUILD_PLAN.md, Этап 2). Plain-dict
calculator input (no dataclass), same convention as schiedel_vent_channels. Reuses the
template rebar-pricing mechanism added for foundation_slab (core/workbook_reader.py's
template_price_keys()/read_prices(), core/price_resolver.py's resolve_prices()) - this is
the second of the 3 future sections that mechanism was built for (floor_slab_1,
load_bearing_walls_lintels still to come).

Fixed production calc_method defaults (contract `defaults:`, all `allow_override_later:
false`): formwork_area_calc_method=spec_formwork_area, formwork_delivery_calc_method=
area_threshold, rebar_calc_method=spec_length_items. Unlike foundation_slab's
thermal_insert_mode, nothing in this section is dynamically chosen - the contract doesn't
even declare the legacy_dimensions/edge_and_beam_formwork_area_combined_m2/legacy_weight_kg
alternatives as review_parameters at all, so this adapter only ever exercises the single
production path for each calc_method.

Unlike foundation_slab's rebar items, floor_slab_2_rebar_items' `rod_length_m` is a real
per-row PDF/spec column (not a per-item default) - passed straight through from the review
row, only `unit_price_per_m` is adapter-injected (per contract note: "unit_price_per_m and
code are adapter-filled, not extracted from the PDF" - code is left unset entirely, the
calculator derives it from steel_class + diameter_mm when absent).

beam_items -> `beams: {"items": [...]}` (calculator_input_path is "beams.items", not a flat
"beam_items" key - easy to miss since every other repeated_rows group in this pipeline so
far maps 1:1 to its own top-level key).

formwork_rental_supplier_quote_total is a real special case: AUTO_CALCULATED but never
actually populated anywhere in the codebase (show_to_user: false, allow_manual_override:
false - Elena never sees or touches it), yet the calculator requires it unconditionally.
The contract's own notes say why it's safe to synthesize: it only feeds a self-comparison
ratio (raw_supplier_rate = quote / main_formwork_area) shown for cross-check against
formwork_rental_used_rate_per_m2, never an actual estimate line total. This adapter derives
it as main_formwork_area_m2 * formwork_rental_used_rate_per_m2 (ratio exactly 1.0, i.e. "no
anomaly"), exactly as the contract note prescribes - never reads it from scalars.
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
from core.rebar_item_defaults import fill_rebar_catalog_defaults

REQUIRED_SCALARS = (
    "main_formwork_area_m2",
    "edge_formwork_area_m2",
    "slab_edge_perimeter_m",
    "edge_insulation_height_m",
    "concrete_placing_volume_m3",
)
OPTIONAL_SCALARS = (
    "beams_formwork_area_m2",
    "beams_bottom_formwork_area_m2",
    "beams_concrete_volume_m3",
    "beams_eps_work_length_m",
    "beams_eps_material_area_m2",
    "bottom_slab_eps_work_area_m2",
    "slab_area_m2",
)
BEAM_ITEMS_GROUP_KEY = "beam_items"
REBAR_GROUP_KEY = "floor_slab_2_rebar_items"
REBAR_TEMPLATE_PRICE_KEY = "rebar_unit_price_by_item"
FORMWORK_RENTAL_QUOTE_KEY = "formwork_rental_supplier_quote_total"
FORMWORK_RENTAL_RATE_PRICE_KEY = "formwork_rental_used_rate_per_m2"


def _rebar_registry_code(steel_class: Any, diameter_mm: Any) -> str | None:
    """Must match build_review_workbook_from_contracts.py's _rebar_registry_code() exactly -
    same convention already used by sections/foundation_slab/build_input.py."""
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
    contract = load_contract("floor_slab_2")
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
                f"floor_slab_2: required parameter '{key}' is missing/blank on sheet 01 "
                "(check 'Найдено в проекте' / 'Исправить / ввести значение')"
            )
        result[key] = value

    for key in OPTIONAL_SCALARS:
        row = scalars.get(key)
        if row and row["value_number"] is not None:
            result[key] = row["value_number"]

    beam_rows = production_items.get(BEAM_ITEMS_GROUP_KEY)
    if beam_rows:
        result["beams"] = {"items": beam_rows}

    # floor_slab_2_rebar_items -> rebar_items, with per-item unit_price_per_m injected from
    # sheet 02's expanded rebar_<class>_d<diameter>_m template rows. rod_length_m is already
    # a real column on this group (unlike foundation_slab) so it's never touched here.
    rebar_rows = production_items.get(REBAR_GROUP_KEY)
    if not rebar_rows:
        raise ValueError(
            f"floor_slab_2: required repeated-row group '{REBAR_GROUP_KEY}' has no rows on "
            "sheet 01"
        )
    rebar_prices = resolved_prices.get(REBAR_TEMPLATE_PRICE_KEY) or {}
    priced_rebar_items = []
    for item in rebar_rows:
        registry_code = _rebar_registry_code(item.get("steel_class"), item.get("diameter_mm"))
        price = rebar_prices.get(registry_code) if registry_code else None
        if price is None:
            raise ValueError(
                f"floor_slab_2: no resolved price for rebar item "
                f"{item.get('steel_class')}/⌀{item.get('diameter_mm')} "
                f"(expected sheet 02 row with price_registry_code={registry_code!r}, "
                f"calc_price_key={REBAR_TEMPLATE_PRICE_KEY})"
            )
        priced_rebar_items.append(
            fill_rebar_catalog_defaults(
                {**item, "unit_price_per_m": price},
                section="floor_slab_2",
            )
        )
    result["rebar_items"] = priced_rebar_items

    # supplier_inputs: crane_shifts, rebar_metal_delivery_trucks, concrete_pump_shifts read
    # explicitly from scalars (no dataclass defaults to fall back on - this is a plain dict,
    # but the calculator still indexes these directly with input_data[...], so a missing key
    # would KeyError deep inside the calculator with a far less useful message).
    # formwork_rental_supplier_quote_total is handled separately below - see module docstring.
    for entry in all_supplier_inputs(contract):
        key = entry["key"]
        if key == FORMWORK_RENTAL_QUOTE_KEY:
            continue
        row = scalars.get(key)
        value = row["value_number"] if row else None
        if value is None:
            if entry.get("required", True):
                raise ValueError(
                    f"floor_slab_2: required supplier input '{key}' is missing/blank (check "
                    "sheet 01 or 01-1's 'Исправить для этого проекта')"
                )
            value = 0
        result[key] = value

    rental_rate = resolved_prices.get(FORMWORK_RENTAL_RATE_PRICE_KEY)
    if rental_rate is None:
        raise ValueError(
            f"floor_slab_2: no resolved price for '{FORMWORK_RENTAL_RATE_PRICE_KEY}' - needed "
            f"to derive {FORMWORK_RENTAL_QUOTE_KEY} (see module docstring)"
        )
    result[FORMWORK_RENTAL_QUOTE_KEY] = result["main_formwork_area_m2"] * rental_rate

    for key, entry in defaults.items():
        if key in result:
            continue
        # Defensive, mirrors foundation_slab/build_input.py: skip any default whose
        # calculator_input_path targets a per-item field rather than a flat top-level one.
        # No such default currently exists in this contract, but the check costs nothing and
        # avoids repeating foundation_slab's rod_length_m bug if one is ever added here.
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
            raise ValueError(f"floor_slab_2: required price '{key}' has no resolved value")

    return result
