"""load_bearing_walls_lintels: normalized_review -> LoadBearingWallsLintelsInput-shaped dict.

Eighth and final adapter of Этап 2 (see ../../ADAPTER_BUILD_PLAN.md). The most involved
section in the whole pipeline: a typed dataclass (like foundation_slab/waterproofing/
earthworks, not a plain dict) with 12 `*_calc_method` fields (memory says "9" - an
undercount from before this adapter was actually built), all flat top-level (no namespacing
like floor_slab_1, no dotted paths in price_keys either - every price_keys key IS its own
dataclass field name).

Fixed production calc_methods (contract `defaults:`, all `allow_override_later: false`):
scaffolding_calc_method=floors_based, cutoff_waterproofing_calc_method=spec_area,
lintel_length_calc_method=spec_total_length, lintel_concrete_calc_method=spec_volume,
main_wall_rebar_calc_method=spec_length_items, lintel_rebar_calc_method=spec_length_items,
main_walls_crane_calc_method=delivery_trucks_threshold (fully automatic - crane shifts come
from gas block delivery truck count, main_walls_crane_shifts is never read in this mode and
deliberately left unset), upper_floor_calc_method=floor_2_spec_volume,
parapet_calc_method=flat_roof_spec_volume, vent_chimney_cladding_calc_method=
flat_roof_spec_volume, vent_chimney_geometry_calc_method=spec_volume_thickness,
walls_consumables_calc_method=section_total_rate. Nothing dynamically chosen by this adapter -
every mode is a fixed contract default, same as every prior section except foundation_slab's
thermal_insert_mode.

flat_roof_enabled is a real design decision, not obvious from the code: it's AUTO_CALCULATED,
required, but never actually populated anywhere (Elena never sees it - show_to_user: false).
The contract's own note says exactly what to do: "true for flat-roof projects where parapet
or vent/chimney cladding rows are relevant; false otherwise" - so this adapter derives it
directly from whether THIS section's own parapet/vent scalars carry a real value (parapet
fields and vent_chimney_gas_block_spec_volume_m3 only ever get PDF data on a flat-roof
project in the first place, per their own field notes).

Two dead contract entries found while building this adapter, neither requiring a fix - both
already self-documented as legacy leftovers in their own notes:
floor_1/2_lintel_formwork_plywood_qty and floor_1/2_lintel_formwork_timber_volume_m3 have a
real calculator_input_path but point at dataclass fields that were REMOVED from the
calculator 2026-07-25 (formwork material is now derived from area, not a ready qty/volume);
the review_parameters entries were simply never deleted (show_to_user: false already, pending
a separate re-wiring check per their own notes). This adapter never reads them - passing them
would raise TypeError on dataclass construction (unexpected keyword argument).

Rebar items: main_wall_rebar_items/lintel_rebar_items both carry real `floor`/`component`
columns from extraction (unlike foundation_slab's rod_length_m, these vary: a project can
have rebar on floor 1 and/or floor 2). `component` is force-set per group anyway
("load_bearing_walls" / "lintels" respectively) since it's structurally constant within each
group and validate_spec_rebar_item() hard-fails on any mismatch - same defensive reasoning as
floor_slab_1's forced component/floor, just per-group instead of per-section. `floor` is left
as extraction provides it. unit_price_per_m is injected via the same per-item template
mechanism as every other rebar-bearing section (core/workbook_reader.py's
template_price_keys()/resolve_prices()).
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
    "cutoff_waterproofing_load_bearing_walls_area_m2",
    "main_wall_gas_block_400_spec_volume_m3",
    "main_wall_gas_block_250_spec_volume_m3",
)
OPTIONAL_SCALARS = (
    "floors_count",
    "lintel_total_length_m",
    "lintel_concrete_spec_volume_m3",
    "floor_2_lintel_ublock_total_length_m",
    "floor_2_lintel_concrete_spec_volume_m3",
    "floor_2_concrete_delivery_trips",
    "floor_1_lintel_monolithic_concrete_volume_m3",
    "floor_1_lintel_monolithic_total_length_m",
    "floor_1_lintel_monolithic_insulation_length_m",
    "floor_1_lintel_formwork_horizontal_area_m2",
    "floor_1_lintel_formwork_vertical_area_m2",
    "floor_1_lintel_insulation_eps_spec_volume_m3",
    "floor_2_lintel_monolithic_concrete_volume_m3",
    "floor_2_lintel_monolithic_total_length_m",
    "floor_2_lintel_monolithic_insulation_length_m",
    "floor_2_lintel_formwork_horizontal_area_m2",
    "floor_2_lintel_formwork_vertical_area_m2",
    "floor_2_lintel_insulation_eps_spec_volume_m3",
    "floor_2_masonry_volume_m3",
    "parapet_masonry_volume_m3",
    "parapet_gas_block_d500_250_spec_volume_m3",
    "parapet_chasing_base_length_m",
    "parapet_rebar_base_length_m",
    "vent_chimney_gas_block_spec_volume_m3",
)
FLAT_ROOF_SIGNAL_SCALARS = (
    "parapet_masonry_volume_m3",
    "parapet_gas_block_d500_250_spec_volume_m3",
    "vent_chimney_gas_block_spec_volume_m3",
)
WALL_BLOCK_ITEMS_GROUP_KEY = "wall_block_items"
MAIN_WALL_REBAR_GROUP_KEY = "main_wall_rebar_items"
LINTEL_REBAR_GROUP_KEY = "lintel_rebar_items"
REBAR_TEMPLATE_PRICE_KEY = "rebar_unit_price_by_item"


def _rebar_registry_code(steel_class: Any, diameter_mm: Any) -> str | None:
    """Must match build_review_workbook_from_contracts.py's _rebar_registry_code() exactly -
    same convention already used by every other rebar-bearing section's build_input.py."""
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


def _priced_rebar_items(
    rows: list[dict[str, Any]], rebar_prices: dict[str, float], component: str, section: str
) -> list[dict[str, Any]]:
    priced = []
    for item in rows:
        registry_code = _rebar_registry_code(item.get("steel_class"), item.get("diameter_mm"))
        price = rebar_prices.get(registry_code) if registry_code else None
        if price is None:
            raise ValueError(
                f"{section}: no resolved price for rebar item "
                f"{item.get('steel_class')}/⌀{item.get('diameter_mm')} "
                f"(expected sheet 02 row with price_registry_code={registry_code!r}, "
                f"calc_price_key={REBAR_TEMPLATE_PRICE_KEY})"
            )
        priced.append(
            fill_rebar_catalog_defaults(
                {**item, "unit_price_per_m": price, "component": component},
                section=section,
            )
        )
    return priced


def build_calculator_input(normalized_review: dict[str, Any]) -> dict[str, Any]:
    contract = load_contract("load_bearing_walls_lintels")
    defaults = default_by_key(contract)
    scalars = normalized_review["scalar_parameters"]
    production_items = normalized_review["production_items"]
    resolved_prices = normalized_review["resolved_prices"]

    result: dict[str, Any] = {"project_name": normalized_review["project_name"]}

    for key in REQUIRED_SCALARS:
        row = scalars.get(key)
        value = row["value_number"] if row else None
        if value is None:
            raise ValueError(
                f"load_bearing_walls_lintels: required parameter '{key}' is missing/blank on "
                "sheet 01 (check 'Найдено в проекте' / 'Исправить / ввести значение')"
            )
        result[key] = value

    for key in OPTIONAL_SCALARS:
        row = scalars.get(key)
        if row and row["value_number"] is not None:
            result[key] = row["value_number"]

    wall_block_rows = production_items.get(WALL_BLOCK_ITEMS_GROUP_KEY)

    if (
        result.get("floors_count") == 2
        and "floor_2_masonry_volume_m3" not in result
        and not wall_block_rows
    ):
        raise ValueError(
            "load_bearing_walls_lintels: floor_2_masonry_volume_m3 is required when "
            "floors_count is 2 (production upper_floor_calc_method=floor_2_spec_volume)"
        )
    if wall_block_rows and "floor_2_masonry_volume_m3" not in result:
        # Compatibility for the dataclass validator. The calculator itself uses
        # wall_block_items totals when this group is present, so the scalar is ignored.
        result["floor_2_masonry_volume_m3"] = 0

    # flat_roof_enabled: system flag, never filled by Elena - see module docstring.
    result["flat_roof_enabled"] = any(
        scalars.get(key) and scalars[key]["value_number"] not in (None, 0)
        for key in FLAT_ROOF_SIGNAL_SCALARS
    )

    if wall_block_rows:
        result[WALL_BLOCK_ITEMS_GROUP_KEY] = wall_block_rows

    rebar_prices = resolved_prices.get(REBAR_TEMPLATE_PRICE_KEY) or {}

    main_wall_rebar_rows = production_items.get(MAIN_WALL_REBAR_GROUP_KEY)
    if not main_wall_rebar_rows:
        raise ValueError(
            f"load_bearing_walls_lintels: required repeated-row group "
            f"'{MAIN_WALL_REBAR_GROUP_KEY}' has no rows on sheet 01"
        )
    result[MAIN_WALL_REBAR_GROUP_KEY] = _priced_rebar_items(
        main_wall_rebar_rows, rebar_prices, "load_bearing_walls", "load_bearing_walls_lintels"
    )

    lintel_rebar_rows = production_items.get(LINTEL_REBAR_GROUP_KEY)
    if not lintel_rebar_rows:
        raise ValueError(
            f"load_bearing_walls_lintels: required repeated-row group "
            f"'{LINTEL_REBAR_GROUP_KEY}' has no rows on sheet 01"
        )
    result[LINTEL_REBAR_GROUP_KEY] = _priced_rebar_items(
        lintel_rebar_rows, rebar_prices, "lintels", "load_bearing_walls_lintels"
    )

    for entry in all_supplier_inputs(contract):
        key = entry["key"]
        if key == "flat_roof_enabled":
            continue  # handled above, derived
        row = scalars.get(key)
        value = row["value_number"] if row else None
        if value is None:
            if entry.get("required", True):
                raise ValueError(
                    f"load_bearing_walls_lintels: required supplier input '{key}' is "
                    "missing/blank (check sheet 01 or 01-1's 'Исправить для этого проекта')"
                )
            value = 0
        result[key] = value

    # Generic defaults fallback: calculator_input_path is almost always identical to the
    # default's own key, except two documentation-only entries whose path packs 6 (and 2)
    # dead-in-production dataclass fields into one pipe-delimited string
    # (main_wall_legacy_geometry_placeholder_zero, second_light_legacy_base_length_placeholder_zero)
    # - see their own contract notes. Splitting on "|" handles both shapes uniformly.
    for key, entry in defaults.items():
        if key in result:
            continue
        path = entry.get("calculator_input_path") or key
        for target in path.split("|"):
            if target not in result:
                result[target] = entry["value"]

    for price_key in contract_price_keys(contract):
        key = price_key["key"]
        if key == REBAR_TEMPLATE_PRICE_KEY:
            continue  # handled above, per-item, not a flat top-level field
        if key in resolved_prices:
            result[key] = resolved_prices[key]
        elif price_key.get("required", True):
            raise ValueError(
                f"load_bearing_walls_lintels: required price '{key}' has no resolved value"
            )

    return result
