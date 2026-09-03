"""P5 adapter for floor_slabs: normalized review JSON -> one calculate_floor_slab_pour() input per
physical slab (review_to_calculator/core/job_runner.py fans build_calculator_inputs()'s list out
into one calculator call per pour). Replaces sections/floor_slab_1 and sections/floor_slab_2's own
build_input.py for production use - see P5_SLAB_DATA_CONTRACT.md for the full design and
P5_SLAB_CLEAN_SCHEMA_INVENTORY.md for the migration history.

Deliberately simpler than the old floor_slab_1 adapter: there is no "combined vs split" ambiguity
to gate here, because the review data is already zone-shaped from the start (one floor_slab_zones
row = one physical slab = one calculator call, always - never a whole-section flat scalar to fall
back to). If a repeated-row item can't be attached to a real zone_id, that is a readiness blocker
(a clear ValueError naming the row), not a [combined] fallback - see P5_SLAB_DATA_CONTRACT.md's
Adapter section.

Insulation readiness (Elena + Codex, 2026-08-10, canonical rule in P5_SLAB_DATA_CONTRACT.md's
"Готовность к автоматическому расчёту работ по утеплению" - read that before changing this file):
material (EPS volume to order) and work (the priced мп/м2 lines) are independent per role.
- slab_edge: material ready from area_m2 or volume_m3 (derived via thickness_mm, needs_review);
  work needs an explicit length_m - never derived from area/volume, never a height fallback.
- slab_bottom: one area (area_m2 or volume_m3/thickness) serves both material and work.
- combined_bottom_and_edge: material only (its volume is always safe to fold into
  total_eps_volume_from_spec_m3) - work is NEVER derived from a combined row. If a zone's only EPS
  data is combined-only volume with no separately-split length/area, work must fail loudly here
  (spec_work_quantities would otherwise silently compute 0 work while still ordering full material -
  exactly the silent money-loss shape this pipeline avoids everywhere else).
- No floor_slab_eps_items rows at all for a zone is a normal "not insulated" outcome, not an error.
"""

from __future__ import annotations

import re
from typing import Any

from core.contract_loader import (
    default_by_key,
    load_contract,
    price_keys as contract_price_keys,
    review_parameter_by_key,
)
from core.rebar_item_defaults import fill_rebar_catalog_defaults

ZONES_GROUP_KEY = "floor_slab_zones"
EPS_ITEMS_GROUP_KEY = "floor_slab_eps_items"
BEAM_ITEMS_GROUP_KEY = "floor_slab_beam_items"
REBAR_GROUP_KEY = "floor_slab_rebar_items"
ADDITIONAL_ITEMS_GROUP_KEY = "floor_slab_additional_items"
REBAR_TEMPLATE_PRICE_KEY = "rebar_unit_price_by_item"
# Handled explicitly (per-zone manual_lines), not through the generic price-fill loop at the end -
# same treatment the old floor_slab_1 adapter already gave this exact key, for the same reason
# (calculator reads it from manual_lines, not rates) - see the price_key's own contract note.
TECHNICAL_SUPERVISION_PRICE_KEY = "technical_supervision_amount"
CONCRETE_VOLUME_UNITS = {"м3", "m3", "куб.м"}


def _set_nested(container: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    node = container
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def _rebar_registry_code(steel_class: Any, diameter_mm: Any) -> str | None:
    """Must match build_review_workbook_from_contracts.py's _rebar_registry_code() exactly -
    same convention every other section's rebar pricing already uses."""
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


def _beam_formwork_area_m2(beam: dict[str, Any]) -> float:
    """Mirrors floor_slab_calculator.py's own per-beam formwork formula exactly (formwork_area_m2
    override if given, else length*(width+2*height)*count, else 0 when width is also absent) -
    needed here because passing a zone through slab_zones[] (see build_calculator_inputs()) makes
    the engine drop its own internally-computed beams_formwork_area entirely once
    edge_and_beam_formwork_area_m2 is zone-supplied (calculate_formwork_areas_context: beams_
    formwork_area = None whenever a zone value is present) - so a zone with real beams AND a pure
    (non-combined) edge area must fold its own beams' formwork into edge_and_beam_formwork_area_m2
    itself here, or that beam formwork would silently vanish from the money calculation."""
    override = beam.get("formwork_area_m2")
    if override is not None:
        return float(override)
    width = _num(beam.get("width_m"))
    if width is None:
        return 0.0
    length = _num(beam.get("length_m")) or 0.0
    height = _num(beam.get("height_m")) or 0.0
    count = _num(beam.get("count"))
    count = 1.0 if count is None else count
    return length * (width + 2 * height) * count


def _zone_label(zone: dict[str, Any]) -> str:
    return str(zone.get("display_name") or zone.get("zone_id") or "?")


def _num(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _resolve_insulation(zone: dict[str, Any], eps_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Builds the spec_work_quantities fields for one zone from its own floor_slab_eps_items rows.
    Raises a clear, zone-named error when material exists but work can't be honestly derived -
    see this module's own docstring for the readiness rule this implements."""
    zone_label = _zone_label(zone)
    total_volume = 0.0
    edge_length = 0.0
    edge_length_present = False
    edge_area = 0.0
    edge_area_present = False
    bottom_area = 0.0
    bottom_area_present = False
    combined_volume = 0.0

    for row in eps_rows:
        role = row.get("role")
        thickness_mm = _num(row.get("thickness_mm")) or 100.0
        thickness_m = thickness_mm / 1000.0
        volume = _num(row.get("volume_m3"))
        area = _num(row.get("area_m2"))
        length = _num(row.get("length_m"))
        height = _num(row.get("height_m"))
        if volume is not None:
            total_volume += volume

        if role == "slab_edge":
            if length is not None:
                edge_length += length
                edge_length_present = True
            if area is not None:
                edge_area += area
                edge_area_present = True
            elif volume is not None and thickness_m > 0:
                edge_area += volume / thickness_m
                edge_area_present = True
            elif volume is None and length is not None and height is not None:
                # ARK real case (2026-09-03): unlike ТРЦ/ЮСВ, this project's PDF never gives a
                # ready area_m2/volume_m3 for slab-edge EPS at all - only length_m + height_m
                # ("...под устройство утепления из ЭППС 100мм (н=180мм) - 73,2м.пог"). The work
                # quantity (edge_length) already derives fine from length_m alone, but material
                # area/volume silently stayed 0 with no length*height fallback, even though both
                # numbers are right here in the same row - a real material-cost line (Elena's real
                # smeta: 72 615₽ on this exact project) was computing to 0₽. volume_m3 was never
                # populated for this row, so it never reached total_volume via the branch above
                # either - add the derived volume here too, since total_volume (not the area-based
                # calculated_clean_eps_volume) is what actually drives the ordered pack quantity
                # downstream in floor_slab_calculator.py.
                derived_area = length * height
                edge_area += derived_area
                edge_area_present = True
                total_volume += derived_area * thickness_m
        elif role == "slab_bottom":
            if area is not None:
                bottom_area += area
                bottom_area_present = True
            elif volume is not None and thickness_m > 0:
                bottom_area += volume / thickness_m
                bottom_area_present = True
        elif role == "combined_bottom_and_edge":
            if volume is not None:
                combined_volume += volume
        # role == "unknown"/None: already counted into total_volume above (material-only,
        # same as combined_bottom_and_edge), never contributes to a work quantity.

    if combined_volume > 0 and not (edge_length_present or bottom_area_present):
        raise ValueError(
            f"floor_slabs: zone '{zone_label}' has only a combined torец+низ EPS volume "
            f"({combined_volume:g} м3) with no separately-given edge length or bottom area - "
            "work quantities cannot be honestly split from one combined number. Разнесите объём "
            "по торцу/низу вручную на листе 01 (floor_slab_eps_items) или подтвердите методику, "
            "прежде чем эта плита сможет посчитаться автоматически."
        )
    if edge_area_present and not edge_length_present:
        # Real project cross-check (ТРЦ, 2026-08-16): the zone's own PDF-given
        # slab_edge_perimeter_m (67.2m) matched Elena's real delivered smeta's edge insulation
        # work length (67.0 мп) far better than deriving length from slab_thickness_m (73.9m,
        # ~10% over) - edge insulation physically runs along the slab's own perimeter, so that
        # PDF-given number is the more honest source when no explicit length is given. Tried in
        # order of reliability; each is still a real project number, never invented.
        zone_perimeter = _num(zone.get("slab_edge_perimeter_m"))
        slab_thickness = _num(zone.get("slab_thickness_m"))
        if zone_perimeter is not None and zone_perimeter > 0:
            edge_length = zone_perimeter
            edge_length_present = True
        elif slab_thickness is not None and slab_thickness > 0:
            edge_length = edge_area / slab_thickness
            edge_length_present = True
        else:
            raise ValueError(
                f"floor_slabs: zone '{zone_label}' has slab_edge EPS material (area/volume) but no "
                "edge work length (floor_slab_eps_items[role=slab_edge].length_m), no zone "
                "slab_edge_perimeter_m, and no slab_thickness_m to derive it from - the м.п. work "
                "line can't be derived at all. Заполните length_m вручную или подтвердите, что "
                "работа по торцу этой плиты не нужна."
            )

    return {
        "insulation_calc_method": "spec_work_quantities",
        "slab_outer_edge_eps_work_length_m": round(edge_length, 6),
        "slab_edge_eps_material_area_m2": round(edge_area, 6),
        "bottom_slab_eps_work_area_m2": round(bottom_area, 6),
        "total_eps_volume_from_spec_m3": round(total_volume, 6),
    }


def _resolve_additional_concrete_items(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """floor_slab_additional_items is deliberately more generic than the calculator's own
    additional_concrete_items[] (name/concrete_volume_m3) - see the group's contract notes. Only
    rows whose unit reads as a concrete volume are wired through; everything else is
    diagnostic/captured, not priced, until a real need to price it appears."""
    items = []
    for row in rows:
        unit = str(row.get("unit") or "").strip().lower()
        if unit not in CONCRETE_VOLUME_UNITS:
            continue
        quantity = _num(row.get("quantity"))
        if quantity is None:
            continue
        items.append({"name": row.get("name") or "", "concrete_volume_m3": quantity})
    return items


def build_calculator_inputs(normalized_review: dict[str, Any]) -> list[dict[str, Any]]:
    contract = load_contract("floor_slabs")
    defaults = default_by_key(contract)
    params = review_parameter_by_key(contract)
    production_items = normalized_review["production_items"]
    resolved_prices = normalized_review["resolved_prices"]
    project_name = normalized_review["project_name"]

    zone_rows = production_items.get(ZONES_GROUP_KEY) or []
    if not zone_rows:
        raise ValueError(
            "floor_slabs: no floor_slab_zones rows found on sheet 01 - at least one physical "
            "slab is required"
        )

    eps_rows_all = production_items.get(EPS_ITEMS_GROUP_KEY) or []
    beam_rows_all = production_items.get(BEAM_ITEMS_GROUP_KEY) or []
    rebar_rows_all = production_items.get(REBAR_GROUP_KEY) or []
    additional_rows_all = production_items.get(ADDITIONAL_ITEMS_GROUP_KEY) or []

    valid_zone_ids = {zone.get("zone_id") for zone in zone_rows if zone.get("zone_id")}
    for group_name, rows in (
        (EPS_ITEMS_GROUP_KEY, eps_rows_all),
        (BEAM_ITEMS_GROUP_KEY, beam_rows_all),
        (REBAR_GROUP_KEY, rebar_rows_all),
        (ADDITIONAL_ITEMS_GROUP_KEY, additional_rows_all),
    ):
        for row in rows:
            zone_id = row.get("zone_id")
            if zone_id and zone_id not in valid_zone_ids:
                raise ValueError(
                    f"floor_slabs: {group_name} row {row.get('name') or row.get('code') or row!r} "
                    f"has zone_id {zone_id!r} which matches no floor_slab_zones row - fix the "
                    "zone_id on sheet 01 or add the missing zone."
                )

    rebar_waste_coeff = defaults["rebar_waste_coeff"]["value"]
    rebar_prices = resolved_prices.get(REBAR_TEMPLATE_PRICE_KEY) or {}

    # Shared across every pour - resolved once, not per zone.
    shared_rates: dict[str, Any] = {}
    for key, entry in defaults.items():
        path = entry.get("calculator_input_path") or ""
        if not path or "[" in path:
            continue  # per-item default (rebar_waste_coeff), applied per rebar row instead
        _set_nested(shared_rates, path, entry["value"])
    for price_key in contract_price_keys(contract):
        key = price_key["key"]
        if key in (REBAR_TEMPLATE_PRICE_KEY, TECHNICAL_SUPERVISION_PRICE_KEY):
            continue  # handled per-pour below (rebar is per-item, tech-supervision is per-zone manual)
        if key in resolved_prices:
            path = price_key.get("calculator_input_path") or f"rates.{key}"
            _set_nested(shared_rates, path, resolved_prices[key])
        elif price_key.get("required", True):
            raise ValueError(f"floor_slabs: required price '{key}' has no resolved value")

    pours: list[dict[str, Any]] = []
    for zone in zone_rows:
        if zone.get("include_in_estimate") is False:
            continue
        zone_id = zone.get("zone_id")
        if not zone_id:
            raise ValueError(f"floor_slabs: a floor_slab_zones row is missing zone_id: {zone!r}")
        zone_label = _zone_label(zone)

        concrete_slab_volume = _num(zone.get("concrete_slab_volume_m3"))
        if concrete_slab_volume is None:
            raise ValueError(
                f"floor_slabs: zone '{zone_label}' is missing concrete_slab_volume_m3 on sheet 01"
            )
        under_slab_area = _num(zone.get("formwork_under_slab_area_m2"))
        if under_slab_area is None:
            raise ValueError(
                f"floor_slabs: zone '{zone_label}' is missing formwork_under_slab_area_m2 on sheet 01"
            )
        # slab_thickness_m is genuinely money-critical here, not control-only: passing this zone
        # through slab_zones[] below (required to get the calculator's own real, evidence-checked
        # main_formwork_area = concrete_volume/thickness - see this function's docstring) means
        # thickness directly drives the "Монтаж опалубки"/"Комплект опалубки" quantity. Do not
        # derive it from concrete_volume/under_slab_area - that would just reproduce the raw PDF
        # area this whole mechanism exists to correct.
        slab_thickness = _num(zone.get("slab_thickness_m"))
        if slab_thickness is None:
            raise ValueError(
                f"floor_slabs: zone '{zone_label}' is missing slab_thickness_m on sheet 01"
            )

        edge_area = _num(zone.get("formwork_edge_area_m2"))
        combined_area = _num(zone.get("formwork_edge_and_beam_combined_area_m2"))
        if edge_area is not None and combined_area is not None:
            raise ValueError(
                f"floor_slabs: zone '{zone_label}' has both formwork_edge_area_m2 and "
                "formwork_edge_and_beam_combined_area_m2 filled - the PDF source is either split "
                "or merged, not both."
            )
        if edge_area is None and combined_area is None:
            raise ValueError(
                f"floor_slabs: zone '{zone_label}' is missing formwork_edge_area_m2 (or "
                "formwork_edge_and_beam_combined_area_m2 for the merged-with-beams case)."
            )

        # code/name are required directly by the engine (no fallback) - floor_slab_beam_items
        # identifies a beam by beam_id/mark instead, map them across here.
        beam_rows = []
        beam_only_concrete_items: list[dict[str, Any]] = []
        for row in beam_rows_all:
            if row.get("zone_id") != zone_id:
                continue
            # A beam row with no length_m can't be priced as a beam at all - the engine's own
            # concreting-rate bucketing (short/tall, priced by length vs by volume) is keyed on
            # length_m unconditionally, even when concrete_volume_m3 is given ready. Real project data
            # has this exact shape for small in-slab concrete elements ("ребро 50мм в теле плиты
            # перекрытия" - a stiffening rib: only height_m + a ready concrete_volume_m3, genuinely
            # no length printed anywhere in the PDF). The old floor_slab_1 architecture routed
            # exactly this case through additional_concrete_items (name + concrete_volume_m3 only -
            # material/delivery-trip accounting, no formwork/concreting line), see cases/
            # test_slab_zones_additional_concrete_items/input.json - do the same here instead of
            # crashing or inventing a fake length (2026-08-11, found while verifying the P5 rebuild).
            if row.get("length_m") in (None, "") and _num(row.get("concrete_volume_m3")) is not None:
                beam_only_concrete_items.append(
                    {
                        "name": row.get("name") or row.get("mark") or row.get("beam_id") or "",
                        "concrete_volume_m3": _num(row.get("concrete_volume_m3")),
                    }
                )
                continue
            beam = dict(row)
            beam.setdefault("code", beam.get("beam_id") or beam.get("mark"))
            beam.setdefault("name", beam.get("name") or beam.get("mark") or beam.get("beam_id"))
            beam_rows.append(beam)
        eps_rows = [row for row in eps_rows_all if row.get("zone_id") == zone_id]

        # slab_edge_perimeter_m: control-geometry only (confirmed by reading the engine - it only
        # ever feeds a cross-check warning, never a money line), and not currently an extraction
        # target on floor_slab_zones. Falls back to this zone's own EPS slab-edge work length,
        # which is the same physical perimeter in every real project checked so far - safe
        # specifically because this field never touches money either way.
        slab_edge_perimeter = _num(zone.get("slab_edge_perimeter_m"))
        if slab_edge_perimeter is None:
            eps_edge_length = sum(
                _num(row.get("length_m")) or 0.0 for row in eps_rows if row.get("role") == "slab_edge"
            )
            slab_edge_perimeter = eps_edge_length

        # beams_formwork_sum/beams_bottom_sum: this zone's own beams, using the exact same
        # per-beam formula the engine itself uses (see _beam_formwork_area_m2's docstring for why
        # this can't just be left to the engine once slab_zones[] is in play).
        beams_formwork_sum = sum(_beam_formwork_area_m2(row) for row in beam_rows)
        beams_bottom_sum = sum(_num(row.get("bottom_formwork_area_m2")) or 0.0 for row in beam_rows)

        edge_and_beam_value = combined_area if combined_area is not None else (edge_area or 0.0) + beams_formwork_sum

        # Seed with the shared rates/insulation-defaults/overheads/calc_method dict FIRST - per-zone
        # values below (in particular insulation) must be merged into these, never wholesale
        # overwritten by them (shared_rates itself carries eps_thickness_m/eps_waste_coeff/etc.
        # under "insulation", same nesting level as the per-zone insulation quantities).
        result: dict[str, Any] = {"case_meta": {"project_name": project_name, "pour_context": zone_label}}
        for path, value in shared_rates.items():
            _set_nested(result, path, dict(value) if isinstance(value, dict) else value)

        # geometry.slab_thickness_m is required unconditionally by the engine regardless of
        # slab_zones[]. geometry.total_concrete_volume_from_spec_m3/slab_edge_perimeter_m/
        # main_formwork_area_m2/edge_formwork_area_m2 below are effectively superseded by
        # slab_zones[] once it's non-empty (the engine sums slab_zones instead) but are still set
        # as a harmless, consistent fallback.
        _set_nested(result, "geometry.total_concrete_volume_from_spec_m3", concrete_slab_volume)
        _set_nested(result, "geometry.slab_thickness_m", slab_thickness)
        _set_nested(result, "geometry.slab_edge_perimeter_m", slab_edge_perimeter)
        # edge_formwork_height_m: control-geometry only, never money - falls back to slab
        # thickness, same convention the old floor_slab_1 contract documented (no separate PDF
        # signal exists for this and none is needed).
        _set_nested(result, "geometry.edge_formwork_height_m", slab_thickness)
        _set_nested(result, "geometry.slab_control_geometry_area_m2", under_slab_area)
        _set_nested(result, "main_formwork_area_m2", under_slab_area)
        _set_nested(result, "edge_and_beam_formwork_area_combined_m2", edge_and_beam_value)

        # slab_zones[] (single item) - this is what actually makes main_formwork_area use the
        # evidence-checked concrete_volume/thickness formula instead of the raw (and, per real
        # data from all 3 checked projects, ~20% undercounted) PDF-quoted under_slab_formwork_area_m2. See
        # calculate_formwork_areas_context()'s own "reversed 2026-08-09" comment in
        # floor_slab_calculator.py before changing this.
        result["slab_zones"] = [
            {
                "context": zone_id,
                "concrete_volume_m3": concrete_slab_volume,
                "edge_perimeter_m": slab_edge_perimeter,
                "under_slab_formwork_area_m2": under_slab_area,
                "edge_and_beam_formwork_area_m2": edge_and_beam_value,
            }
        ]

        beams_bottom_override = _num(zone.get("formwork_beams_bottom_area_m2"))
        result["beams_bottom_formwork_area_m2"] = (
            beams_bottom_override if beams_bottom_override is not None else beams_bottom_sum
        )

        # beams_concrete_volume_m3: spec-table override (Prompt rule 25 - spec always wins over
        # summing floor_slab_beam_items' own L*W*H, which real TRC data proved unreliable when a
        # beam's height gets misread off a crowded plan drawing). Only set the key when a real
        # override is given - absent, the engine's own default already falls back to summing
        # beam_items, no fallback needed here.
        beams_concrete_volume_override = _num(zone.get("beams_concrete_volume_m3"))
        if beams_concrete_volume_override is not None:
            result["beams_concrete_volume_m3"] = beams_concrete_volume_override

        # manual_plywood_reserve_sheets: per-pour override of rates.reserve_plywood_sheets (catalog
        # default 0, see defaults_catalog.yaml's 2026-08-22 note - real ТРЦ/АРК/ЮСВ data shows this
        # reserve is a genuine manual per-pour judgment call, not a formula, and varies 0/5/10 with
        # no discoverable pattern). Only overrides the shared_rates value already seeded above when
        # Elena actually fills it in; absent means 0, same convention as crane/pump but WITH a safe
        # default, so this field is never critical/red (see populate_review_workbook_from_extraction.py).
        plywood_reserve_override = _num(zone.get("manual_plywood_reserve_sheets"))
        if plywood_reserve_override is not None:
            _set_nested(result, "rates.reserve_plywood_sheets", plywood_reserve_override)

        if beam_rows:
            result["beams"] = {"items": beam_rows}

        additional_rows = [row for row in additional_rows_all if row.get("zone_id") == zone_id]
        additional_items = _resolve_additional_concrete_items(additional_rows) + beam_only_concrete_items
        if additional_items:
            result["additional_concrete_items"] = additional_items

        result.setdefault("insulation", {}).update(_resolve_insulation(zone, eps_rows))

        rebar_rows = [row for row in rebar_rows_all if row.get("zone_id") == zone_id]
        if not rebar_rows:
            raise ValueError(
                f"floor_slabs: zone '{zone_label}' has no floor_slab_rebar_items rows on sheet 01"
            )
        priced_rebar_items = []
        for item in rebar_rows:
            registry_code = _rebar_registry_code(item.get("steel_class"), item.get("diameter_mm"))
            price = rebar_prices.get(registry_code) if registry_code else None
            if price is None:
                raise ValueError(
                    f"floor_slabs: zone '{zone_label}': no resolved price for rebar item "
                    f"{item.get('steel_class')}/⌀{item.get('diameter_mm')} (expected sheet 02 row "
                    f"with price_registry_code={registry_code!r}, calc_price_key={REBAR_TEMPLATE_PRICE_KEY})"
                )
            priced_item = fill_rebar_catalog_defaults(
                {
                    **item,
                    "unit_price_per_m": price,
                    "waste_coeff": rebar_waste_coeff,
                    "zone_context": zone_id,
                },
                section="floor_slabs",
            )
            priced_rebar_items.append(priced_item)
        result["rebar_items"] = priced_rebar_items

        manual_lines = {
            "formwork_rebar_crane_shifts": _num(zone.get("manual_formwork_rebar_crane_shifts")) or 0,
            "concrete_pump_shifts": _num(zone.get("manual_concrete_pump_shifts")) or 0,
            "rebar_metal_delivery_trucks": _num(zone.get("manual_rebar_metal_delivery_trucks")) or 0,
            # Default 5000 (not 0) - checked 3 real projects' delivered smetas 2026-08-15: every
            # floor-slab zone/pour consistently carries 5000 for technical supervision (4/4
            # instances checked, no exceptions), unlike crane/pump/metal-delivery above which
            # genuinely vary per real project logistics and have no such universal default.
            "technical_supervision_amount": _num(zone.get("manual_technical_supervision_amount")) or 5000,
        }
        _set_nested(result, "manual_lines", manual_lines)

        pours.append(result)

    if not pours:
        raise ValueError(
            "floor_slabs: every floor_slab_zones row has include_in_estimate=false - nothing to "
            "calculate. Confirm at least one real pour should be included."
        )
    return pours
