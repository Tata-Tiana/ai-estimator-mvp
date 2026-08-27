"""flat_roof: normalized_review -> calculate_flat_roof() plain-dict input.

Seventh adapter for review_to_calculator (see ../../ADAPTER_BUILD_PLAN.md, Этап 2). Plain-dict
calculator input (no dataclass, no namespaced sub-dicts either - unlike floor_slab_1, every
field here is genuinely top-level).

Fixed production calc_methods (contract `defaults:`, all `allow_override_later: false`):
roof_geometry_calc_method=roof_zones, roof_consumables_calc_method=section_total_rate,
roof_logistics_and_supply_calc_method=section_total_rate,
technical_supervision_calc_method=section_work_rate,
procurement_storage_calc_method=section_material_rate. Nothing dynamically chosen.

Two real gaps found while building this adapter, not by reading the contract but by actually
running the calculator - both share the same shape as floor_slab_1's
slab_control_geometry_area_m2 gap: fields the contract marks optional/fallback-only that the
calculator reads unconditionally anyway, purely for a diagnostic report block:

1. roof_area_level_1_m2, roof_area_level_2_m2, project_spec_roof_area_m2,
   parapet_length_level_1_m, parapet_length_level_2_m, vent_wall_abutment_level_1_m,
   vent_wall_abutment_level_2_m are all `required: false` in the contract (explicitly
   "fallback only for the legacy detailed_project_geometry mode, leave blank when roof_zones
   is used" - production always uses roof_zones), but calculate_flat_roof()'s result-building
   code (calculation_blocks.geometry) directly indexes all 7 unconditionally with no
   fallback. Confirmed by reading every usage that none of them feed the roof_zones geometry
   path or any money line. Per explicit user decision (2026-08-05), this adapter defaults all
   7 to 0 when absent from scalars rather than requiring Elena fill fields the contract itself
   tells her to skip.
2. slope_plate_unit_price_per_m3 is one reviewed price in the contract but the calculator
   reads 4 separate top-level fields (slope_plate_a/b/j/k_unit_price_per_m3) built via an
   f-string prefix internally - contract's own note confirms this is intentional ("all 4 are
   the same real product/price in every production test case"). This adapter resolves the one
   price and duplicates it into all 4 fields.

pvc_membrane_vgr_unit_price_per_roll_display is only required when at least one roof_zones row
has operability="exploitable" with real area, OR roof_raw_material_spec_rows has a real V-GR
row (see has_spec_vgr_area below) - the calculator only touches vgr_membrane_* fields in that
case (see calculate_flat_roof's `vgr_membrane_required_area > 0` gate). Added 2026-08-06 for
the first real project with an exploitable zone; the contract's own price_key is required:false
for the same reason - most flat_roof projects never need it. pvc_membrane_vgr_roll_width_m /
_roll_length_m are plain contract defaults (2.1x20m, same as V-RP) always present regardless.

roof_raw_material_spec_rows (2026-08-24): was diagnostic-only (calculator_input_path: "") until
a real TRC gap was found - the geometric roof_zones formula overshoots V-GR membrane area badly
for small exploitable zones with a high perimeter-to-area ratio (46.9m2 computed vs 29.9m2 on
the project's own spec table, 1 extra roll). Now passed through to the calculator unconditionally
(empty list when absent, matching every other optional group in this file);
calculate_flat_roof's spec_table_area_m2() uses a matching V-GR row when present, falls back to
the geometric formula otherwise - existing projects/fixtures with no such row are unaffected.
V-RP deliberately does NOT get the same override - checked against real TRC data and the spec
table's own V-RP total (169.48m2, rounds to 5 rolls) UNDER-orders vs Elena's real 6 rolls, which
matches our existing geometric formula exactly. Both spec rows are flagged "Уточнить у монтажной
организации" (confirm with installer) in the source PDF - i.e. neither the spec table nor our
formula is the true final order, they're both approximations of a separate installer quote; V-GR
happens to need the spec approximation, V-RP happens to need the geometric one. See
calculator.py's comment right above the V-RP block for the same note.
"""

from __future__ import annotations

from typing import Any

from core.contract_loader import (
    all_supplier_inputs,
    default_by_key,
    load_contract,
    price_keys as contract_price_keys,
)

REQUIRED_SCALARS = (
    "parapet_roof_drains_count",
    "internal_roof_drains_count",
    "slope_plate_a_supplier_required_volume_m3",
    "slope_plate_b_supplier_required_volume_m3",
    "slope_plate_j_supplier_required_volume_m3",
    "slope_plate_k_supplier_required_volume_m3",
    "eps50_supplier_required_volume_m3",
    "roof_aerators_count",
    "internal_drain_height_per_drain_m",
)
# Contractually optional/fallback-only, but read unconditionally by the calculator for its
# own diagnostic report block - see module docstring point 1.
FALLBACK_SCALARS = (
    "roof_area_level_1_m2",
    "roof_area_level_2_m2",
    "project_spec_roof_area_m2",
    "parapet_length_level_1_m",
    "parapet_length_level_2_m",
    "vent_wall_abutment_level_1_m",
    "vent_wall_abutment_level_2_m",
)
ROOF_ZONES_GROUP_KEY = "roof_zones"
# Optional, unlike ROOF_ZONES_GROUP_KEY - see roof_screed_items[] handling below.
ROOF_SCREED_ITEMS_GROUP_KEY = "roof_screed_items"
SCREED_PRICE_KEYS = (
    "roof_screed_installation_work_rate_per_m2",
    "roof_screed_board_unit_price",
    "roof_fiberglass_mat_unit_price_per_m2",
    # roof_screed_geotextile (the 4th screed line) reuses geotextile_parapet_unit_price_per_m2,
    # which is already required:true unconditionally - no separate check needed for it here.
)
SLOPE_PLATE_TEMPLATE_PRICE_KEY = "slope_plate_unit_price_per_m3"
SLOPE_PLATE_PREFIXES = ("slope_plate_a", "slope_plate_b", "slope_plate_j", "slope_plate_k")
VGR_MEMBRANE_PRICE_KEY = "pvc_membrane_vgr_unit_price_per_roll_display"
# price_key -> (roll_width_key, roll_length_key) - see the price-resolution loop below for why
# these 2 registry prices need multiplying by roll area before use.
MEMBRANE_ROLL_PRICE_KEYS = {
    "pvc_membrane_unit_price_per_roll_display": ("pvc_membrane_roll_width_m", "pvc_membrane_roll_length_m"),
    VGR_MEMBRANE_PRICE_KEY: ("pvc_membrane_vgr_roll_width_m", "pvc_membrane_vgr_roll_length_m"),
}


def build_calculator_input(normalized_review: dict[str, Any]) -> dict[str, Any]:
    contract = load_contract("flat_roof")
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
                f"flat_roof: required parameter '{key}' is missing/blank on sheet 01 "
                "(check 'Найдено в проекте' / 'Исправить / ввести значение')"
            )
        result[key] = value

    for key in FALLBACK_SCALARS:
        row = scalars.get(key)
        result[key] = row["value_number"] if row and row["value_number"] is not None else 0

    zone_rows = production_items.get(ROOF_ZONES_GROUP_KEY)
    if not zone_rows:
        raise ValueError(
            f"flat_roof: required repeated-row group '{ROOF_ZONES_GROUP_KEY}' has no rows on "
            "sheet 01 (production mode roof_geometry_calc_method=roof_zones requires at least "
            "one zone)"
        )
    result[ROOF_ZONES_GROUP_KEY] = zone_rows

    # roof_screed_items[]: optional, real recurring case (not every project - Elena confirmed
    # some projects have a walkable/exploitable roof zone with a ЦСП screed build-up, others
    # don't) - unlike ROOF_ZONES_GROUP_KEY above, absence is normal, not an error. Defaults to an
    # empty list, matching calculate_flat_roof()'s own "0 lines when empty" gate (see its
    # roof_screed_items docstring note, 2026-08-24).
    result[ROOF_SCREED_ITEMS_GROUP_KEY] = production_items.get(ROOF_SCREED_ITEMS_GROUP_KEY) or []

    # roof_raw_material_spec_rows: ready quantities straight off the project's own roof material
    # spec table (production_input: true, captured for every project regardless of section -
    # was diagnostic-only, calculator_input_path: "", until 2026-08-24). calculate_flat_roof()
    # now gives a real V-GR row here priority over its own zone-based estimate (V-RP deliberately
    # excluded - see module docstring) - see calculator.py's spec_table_area_m2() docstring.
    spec_rows = production_items.get("roof_raw_material_spec_rows") or []
    result["roof_raw_material_spec_rows"] = spec_rows
    has_spec_vgr_area = any(
        "V-GR" in str(row.get("name") or "") and (row.get("quantity") or 0) > 0
        for row in spec_rows
    )

    has_exploitable_zone = any(
        zone.get("operability") == "exploitable" and (zone.get("area_m2") or 0) > 0
        for zone in zone_rows
    )
    if (has_exploitable_zone or has_spec_vgr_area) and VGR_MEMBRANE_PRICE_KEY not in resolved_prices:
        raise ValueError(
            f"flat_roof: at least one roof_zones row is exploitable (or a V-GR row exists in "
            f"roof_raw_material_spec_rows), so the calculator needs "
            f"the V-GR membrane price - required price '{VGR_MEMBRANE_PRICE_KEY}' has no "
            "resolved value on sheet 02 (add a row: calc_price_key="
            f"{VGR_MEMBRANE_PRICE_KEY}, price_registry_code="
            "roof_pvc_membrane_logicroof_vgr_1_5mm_gray_roll)"
        )

    # Same "required only when actually used" shape as the V-GR check above: these 3 prices are
    # required:false in the contract (most projects have no screed at all), but once a project
    # DOES have real roof_screed_items[] rows, calculate_flat_roof() reads all 3 unconditionally -
    # a missing price there must fail loudly and specifically, not silently produce a 0-priced
    # line or a generic KeyError with no indication of which field/row was the problem.
    if any((row.get("area_m2") or 0) > 0 for row in result[ROOF_SCREED_ITEMS_GROUP_KEY]):
        for key in SCREED_PRICE_KEYS:
            if key not in resolved_prices:
                raise ValueError(
                    f"flat_roof: roof_screed_items[] has a real area, so the calculator needs "
                    f"'{key}' - no resolved value on sheet 02 (add a row: calc_price_key={key})"
                )

    for entry in all_supplier_inputs(contract):
        key = entry["key"]
        if not entry.get("required", True):
            continue  # legacy/hidden optional fields (vent_shaft_abutment_count,
            # roof_work_coeff, legacy money totals) - calculator reads all of them via
            # .get(..., default) internally, never required.
        row = scalars.get(key)
        value = row["value_number"] if row else None
        if value is None:
            raise ValueError(
                f"flat_roof: required supplier input '{key}' is missing/blank (check sheet 01 "
                "or 01-1's 'Исправить для этого проекта')"
            )
        result[key] = value

    for key, entry in defaults.items():
        if key in result:
            continue
        result[key] = entry["value"]

    for price_key in contract_price_keys(contract):
        key = price_key["key"]
        if key == SLOPE_PLATE_TEMPLATE_PRICE_KEY:
            continue  # handled below, duplicated into 4 fields
        if key in resolved_prices:
            if key in MEMBRANE_ROLL_PRICE_KEYS:
                # roof_pvc_membrane_logicroof_v*_1_5mm_gray_roll price registry rows are
                # unit="м2" (the registry itself flags them "проставлено автоматически по
                # точному совпадению номенклатуры; проверьте цену/единицу" - never verified),
                # but the calculator field is genuinely a per-ROLL price (real project data,
                # 2026-08-23: ТРЦ/АРК/ЮСВ smetas each compute their own membrane roll price as
                # roll_width*roll_length*price_per_m2, ~925-1166 руб/м2 - matches the registry's
                # м2 number almost exactly). Multiply by roll area here, once, at the boundary
                # where the м2 registry price becomes a roll price - the calculator's own
                # fixtures already expect a real per-roll number and must not change.
                width_key, length_key = MEMBRANE_ROLL_PRICE_KEYS[key]
                roll_area = result[width_key] * result[length_key]
                result[key] = resolved_prices[key] * roll_area
            else:
                result[key] = resolved_prices[key]
        elif price_key.get("required", True):
            raise ValueError(f"flat_roof: required price '{key}' has no resolved value")

    slope_plate_price = resolved_prices.get(SLOPE_PLATE_TEMPLATE_PRICE_KEY)
    if slope_plate_price is None:
        raise ValueError(
            f"flat_roof: required price '{SLOPE_PLATE_TEMPLATE_PRICE_KEY}' has no resolved value"
        )
    for prefix in SLOPE_PLATE_PREFIXES:
        result[f"{prefix}_unit_price_per_m3"] = slope_plate_price

    return result
