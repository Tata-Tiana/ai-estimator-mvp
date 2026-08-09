"""floor_slab_1: normalized_review -> calculate_floor_slab_1() plain-dict input.

Sixth adapter for review_to_calculator (see ../../ADAPTER_BUILD_PLAN.md, Этап 2). Plain-dict
calculator input (no dataclass, like floor_slab_2/schiedel), but unlike every prior adapter
this calculator's input is namespaced into sub-dicts: geometry.*, insulation.*, rates.*,
overheads.*, manual_lines.*, plus a case_meta dict the calculator never reads (just echoes
into its result) and several genuinely top-level fields (main_formwork_area_m2,
edge_formwork_area_m2, beams_*, slab_zones, rebar_items, beams.items,
formwork_areas_calc_method, rebar_calc_method). The contract's own `calculator_input_path`
already encodes this exactly (dotted paths for nested fields), so this adapter reads that
path generically via `_set_nested()` instead of hand-coding which sub-dict each field belongs
to - far less error-prone than repeating the namespace choice for every one of the ~35 fields
this section has.

Fixed production calc_method defaults (contract `defaults:`, all `allow_override_later:
false`): formwork_areas_calc_method=spec_formwork_areas, rebar_calc_method=spec_length_items,
insulation.insulation_calc_method=spec_work_quantities, rates.formwork_rate_calc_method=
direct_section_rate, rates.formwork_delivery_calc_method=area_threshold,
rates.metal_delivery_calc_method=section_output_only. Nothing dynamically chosen.

Price placement: every price_keys entry lands under rates.<key> UNLESS the contract gives it
an explicit calculator_input_path (eps_unit_price_per_m3/foam_unit_price_per_can go under
insulation.*, technical_supervision_amount goes under manual_lines.* - the contract's own
notes explain each exception). rebar_unit_price_by_item is the per-item template key (same
mechanism as foundation_slab/floor_slab_2), resolved per rebar_items row, never a flat field.

Two real gaps found and fixed while building this adapter:

1. The contract had NO `rebar_waste_coeff` default at all (unlike every other rebar-bearing
   section), yet calculate_rebar_item() reads item["waste_coeff"] unconditionally with no
   fallback - a guaranteed crash on any real run. Fixed by adding the missing default
   (1.05, same value as foundation_slab/floor_slab_2) with explicit user authorization; this
   adapter injects it into each rebar_items row, same pattern as foundation_slab's
   rod_length_m.
2. calculate_rebar_item()'s spec_length_items branch also hard-requires
   item["component"] == "floor_slab_1" and int(item["floor"]) == 1 - structural constants for
   this section, not real per-project data (every row in this group is always floor 1,
   component floor_slab_1). Rather than trust extraction to get two constant validation
   fields right on every row, this adapter force-sets them on every rebar_items row,
   overriding whatever extraction produced - same reasoning as forcing rod_length_m in
   foundation_slab.
"""

from __future__ import annotations

import re
from typing import Any

from core.contract_loader import (
    all_supplier_inputs,
    default_by_key,
    load_contract,
    price_keys as contract_price_keys,
    review_parameter_by_key,
)
from core.rebar_item_defaults import fill_rebar_catalog_defaults

REQUIRED_SCALARS = (
    "total_concrete_volume_from_spec_m3",
    "slab_thickness_m",
    "slab_edge_perimeter_m",
    "edge_formwork_height_m",
    "main_formwork_area_m2",
    "slab_outer_edge_eps_work_length_m",
    "edge_insulation_height_m",
    "slab_edge_eps_material_area_m2",
    "bottom_slab_eps_work_area_m2",
    "total_eps_volume_from_spec_m3",
)
OPTIONAL_SCALARS = (
    "beams_formwork_area_m2",
    "beams_bottom_formwork_area_m2",
    "beams_concrete_volume_m3",
    "beams_eps_work_length_m",
    "beams_eps_material_area_m2",
)
EDGE_FORMWORK_AREA_KEY = "edge_formwork_area_m2"
EDGE_AND_BEAM_COMBINED_KEY = "edge_and_beam_formwork_area_combined_m2"
SLAB_ZONES_GROUP_KEY = "slab_zones"
BEAM_ITEMS_GROUP_KEY = "beam_items"
ADDITIONAL_CONCRETE_ITEMS_GROUP_KEY = "additional_concrete_items"
REBAR_GROUP_KEY = "floor_slab_1_rebar_items"
REBAR_TEMPLATE_PRICE_KEY = "rebar_unit_price_by_item"
SLAB_ZONE_FORMWORK_FIELDS = (
    "edge_perimeter_m",
    "under_slab_formwork_area_m2",
    "edge_and_beam_formwork_area_m2",
)


def _set_nested(container: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    node = container
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def _rebar_registry_code(steel_class: Any, diameter_mm: Any) -> str | None:
    """Must match build_review_workbook_from_contracts.py's _rebar_registry_code() exactly -
    same convention already used by foundation_slab/floor_slab_2's build_input.py."""
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
    contract = load_contract("floor_slab_1")
    defaults = default_by_key(contract)
    params = review_parameter_by_key(contract)
    scalars = normalized_review["scalar_parameters"]
    production_items = normalized_review["production_items"]
    resolved_prices = normalized_review["resolved_prices"]
    zone_rows = production_items.get(SLAB_ZONES_GROUP_KEY)
    zones_have_formwork = bool(
        zone_rows
        and any(zone.get(field) is not None for zone in zone_rows for field in SLAB_ZONE_FORMWORK_FIELDS)
    )

    result: dict[str, Any] = {"case_meta": {"project_name": normalized_review["project_name"]}}

    for key in REQUIRED_SCALARS:
        if zones_have_formwork and key in {
            "slab_edge_perimeter_m",
            "main_formwork_area_m2",
        }:
            continue
        row = scalars.get(key)
        value = row["value_number"] if row else None
        if value is None:
            raise ValueError(
                f"floor_slab_1: required parameter '{key}' is missing/blank on sheet 01 "
                "(check 'Найдено в проекте' / 'Исправить / ввести значение')"
            )
        _set_nested(result, params[key]["calculator_input_path"], value)

    # geometry.slab_control_geometry_area_m2: required unconditionally by the calculator
    # (calculate_floor_slab_1() reads geometry_in["slab_control_geometry_area_m2"] directly,
    # no fallback) but not declared anywhere in the contract - a real gap, not an oversight
    # in this adapter. Purely a diagnostic/cross-check echo into calculation_blocks, never
    # touches any money calculation (confirmed by reading every usage in the calculator).
    # No PDF signal exists for a separate control area, so this mirrors main_formwork_area_m2
    # (the production formwork area itself) per explicit user decision, 2026-08-05.
    control_area = result.get("main_formwork_area_m2")
    if control_area is None and zones_have_formwork:
        control_area = sum(
            float(zone.get("under_slab_formwork_area_m2") or 0)
            for zone in zone_rows or []
        )
    _set_nested(result, "geometry.slab_control_geometry_area_m2", control_area)

    for key in OPTIONAL_SCALARS:
        row = scalars.get(key)
        if row and row["value_number"] is not None:
            _set_nested(result, params[key]["calculator_input_path"], row["value_number"])

    # edge_formwork_area_m2 / edge_and_beam_formwork_area_combined_m2 are mutually exclusive
    # (the PDF gives either a clean edge/beam split or one unsplittable merged number, never
    # both) - the calculator itself raises if both are supplied, but a clearer adapter-level
    # message is more useful than a generic error deep inside calculate_formwork_areas_context.
    combined_row = scalars.get(EDGE_AND_BEAM_COMBINED_KEY)
    combined_value = combined_row["value_number"] if combined_row else None
    edge_row = scalars.get(EDGE_FORMWORK_AREA_KEY)
    edge_value = edge_row["value_number"] if edge_row else None
    if zones_have_formwork:
        pass
    elif combined_value is not None:
        if edge_value is not None:
            raise ValueError(
                "floor_slab_1: edge_and_beam_formwork_area_combined_m2 and edge_formwork_area_m2 "
                "cannot both be filled - the PDF source is either split or merged, not both"
            )
        _set_nested(result, params[EDGE_AND_BEAM_COMBINED_KEY]["calculator_input_path"], combined_value)
    else:
        if edge_value is None:
            raise ValueError(
                "floor_slab_1: required parameter 'edge_formwork_area_m2' is missing/blank "
                "(or provide edge_and_beam_formwork_area_combined_m2 instead)"
            )
        _set_nested(result, params[EDGE_FORMWORK_AREA_KEY]["calculator_input_path"], edge_value)

    if zone_rows:
        normalized_zones = []
        for zone in zone_rows:
            normalized_zone = dict(zone)
            if zones_have_formwork:
                for field in SLAB_ZONE_FORMWORK_FIELDS:
                    normalized_zone[field] = normalized_zone.get(field) or 0
            normalized_zones.append(normalized_zone)
        result[SLAB_ZONES_GROUP_KEY] = normalized_zones

    beam_rows = production_items.get(BEAM_ITEMS_GROUP_KEY)
    if beam_rows:
        result["beams"] = {"items": beam_rows}

    additional_concrete_rows = production_items.get(ADDITIONAL_CONCRETE_ITEMS_GROUP_KEY)
    if additional_concrete_rows:
        result[ADDITIONAL_CONCRETE_ITEMS_GROUP_KEY] = additional_concrete_rows

    # technical_supervision_amount: a price-like manual amount that lives in price_keys (not
    # supplier_inputs) but the calculator reads it from manual_lines, not rates - see contract
    # note and module docstring.
    tech_supervision_price = resolved_prices.get("technical_supervision_amount")
    if tech_supervision_price is None:
        raise ValueError(
            "floor_slab_1: required price 'technical_supervision_amount' has no resolved value"
        )
    _set_nested(
        result,
        "manual_lines.technical_supervision_amount",
        tech_supervision_price,
    )

    for entry in all_supplier_inputs(contract):
        key = entry["key"]
        row = scalars.get(key)
        value = row["value_number"] if row else None
        if value is None:
            if entry.get("required", True):
                raise ValueError(
                    f"floor_slab_1: required supplier input '{key}' is missing/blank (check "
                    "sheet 01 or 01-1's 'Исправить для этого проекта')"
                )
            value = 0
        _set_nested(result, entry["calculator_input_path"], value)

    # floor_slab_1_rebar_items -> rebar_items, with per-item unit_price_per_m injected from
    # sheet 02's expanded rebar_<class>_d<diameter>_m template rows, waste_coeff injected from
    # the (newly added) rebar_waste_coeff default, and component/floor force-set to this
    # section's own structural constants - see module docstring point 2.
    rebar_rows = production_items.get(REBAR_GROUP_KEY)
    if not rebar_rows:
        raise ValueError(
            f"floor_slab_1: required repeated-row group '{REBAR_GROUP_KEY}' has no rows on "
            "sheet 01"
        )
    rebar_prices = resolved_prices.get(REBAR_TEMPLATE_PRICE_KEY) or {}
    rebar_waste_coeff = defaults["rebar_waste_coeff"]["value"]
    priced_rebar_items = []
    for item in rebar_rows:
        registry_code = _rebar_registry_code(item.get("steel_class"), item.get("diameter_mm"))
        price = rebar_prices.get(registry_code) if registry_code else None
        if price is None:
            raise ValueError(
                f"floor_slab_1: no resolved price for rebar item "
                f"{item.get('steel_class')}/⌀{item.get('diameter_mm')} "
                f"(expected sheet 02 row with price_registry_code={registry_code!r}, "
                f"calc_price_key={REBAR_TEMPLATE_PRICE_KEY})"
            )
        priced_item = fill_rebar_catalog_defaults(
            {
                **item,
                "unit_price_per_m": price,
                "waste_coeff": rebar_waste_coeff,
                "component": "floor_slab_1",
                "floor": 1,
            },
            section="floor_slab_1",
        )
        priced_rebar_items.append(priced_item)
    result["rebar_items"] = priced_rebar_items

    for key, entry in defaults.items():
        path = entry.get("calculator_input_path") or ""
        if "[" in path:
            continue  # per-item default (rebar_waste_coeff), injected above
        _set_nested(result, path, entry["value"])

    for price_key in contract_price_keys(contract):
        key = price_key["key"]
        if key in (REBAR_TEMPLATE_PRICE_KEY, "technical_supervision_amount"):
            continue  # handled above (per-item / explicit manual_lines placement)
        if key in resolved_prices:
            path = price_key.get("calculator_input_path") or f"rates.{key}"
            _set_nested(result, path, resolved_prices[key])
        elif price_key.get("required", True):
            raise ValueError(f"floor_slab_1: required price '{key}' has no resolved value")

    return result
