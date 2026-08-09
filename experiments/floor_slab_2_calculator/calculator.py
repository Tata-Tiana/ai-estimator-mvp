from __future__ import annotations

import sys
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP
from pathlib import Path
from typing import Any

# calculate_floor_slab_2() below is a translation wrapper (FLOOR_SLAB_UNIFICATION_PLAN.md P1.2/
# P1.3) around calculate_floor_slab_pour() - the real money math (rebar rounding/pooling,
# insulation, beam concreting, concrete order rounding, formwork rate/delivery/metal-delivery
# modes) lives there now, not duplicated here. The shared engine lives in floor_slab_calculator.py
# (moved out of floor_slab_1_calculator.py in P1.3) precisely so this import doesn't read as
# "floor_slab_2 depends on floor_slab_1" - it depends on the shared engine, same as floor_slab_1
# itself does.
_FLOOR_SLAB_ENGINE_DIR = Path(__file__).resolve().parents[1] / "floor_slab_1_calculator"
if str(_FLOOR_SLAB_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_FLOOR_SLAB_ENGINE_DIR))
from floor_slab_calculator import calculate_floor_slab_pour  # noqa: E402

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


def ceil_decimal(value: Any) -> int:
    return int(d(value).to_integral_value(rounding=ROUND_CEILING))


def round_decimal(value: Any, places: str = "0.000001") -> float:
    return float(d(value).quantize(Decimal(places), rounding=ROUND_HALF_UP))


def display_decimal(value: Any, places: str = "0.01") -> float:
    return float(d(value).quantize(Decimal(places), rounding=ROUND_HALF_UP))


def ceil_to_step(value: Any, step: Any) -> Decimal:
    value_dec = d(value)
    step_dec = d(step)
    return d(ceil_decimal(value_dec / step_dec)) * step_dec


def make_rebar_code(steel_class: str, diameter_mm: int) -> str:
    return f"rebar_{steel_class.lower()}_d{diameter_mm}"


def make_rebar_name(steel_class: str, diameter_mm: int) -> str:
    return f"Арматура класса {steel_class} диаметром {diameter_mm} мм"


def round_optional(value: Any, places: str = "0.000001") -> float | None:
    return None if value is None else round_decimal(value, places)


def calculate_beam_items(
    beams_in: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], Decimal, Decimal, Decimal, Decimal]:
    items_in = (beams_in or {}).get("items") or []
    beam_items: list[dict[str, Any]] = []
    for item in items_in:
        for required_key in ("length_m", "height_m"):
            if item.get(required_key) is None:
                raise ValueError(f"beams.items[{item.get('code')!r}].{required_key} is required")
        length = d(item["length_m"])
        height = d(item["height_m"])
        width_raw = item.get("width_m")
        width = d(width_raw) if width_raw is not None else None
        count_raw = item.get("count", 1)
        count = D1 if count_raw is None else d(count_raw)
        if length < D0 or (width is not None and width < D0) or height < D0 or count < D0:
            raise ValueError("beams.items length_m, width_m, height_m and count must be >= 0")

        # width_m is optional (2026-07-28), ported from floor_slab_1_calculator.py: real spec tables
        # sometimes combine beams of different cross-sections into one row with no single valid width.
        # concrete_volume_m3/formwork_area_m2 can be given ready on the row instead of recomputed.
        concrete_volume_override = item.get("concrete_volume_m3")
        if concrete_volume_override is not None:
            concrete_volume = d(concrete_volume_override)
        elif width is not None:
            concrete_volume = length * width * height * count
        else:
            raise ValueError(
                f"beams.items[{item.get('code')!r}] needs either width_m or concrete_volume_m3 "
                "to determine concrete volume"
            )

        formwork_area_override = item.get("formwork_area_m2")
        if formwork_area_override is not None:
            formwork_area = d(formwork_area_override)
        elif width is not None:
            formwork_area = length * (width + d(2) * height) * count
        else:
            formwork_area = D0

        eps_material_area = length * height * count
        beam_items.append(
            {
                "code": item["code"],
                "name": item["name"],
                "length_m": round_decimal(length),
                "width_m": None if width is None else round_decimal(width),
                "height_m": round_decimal(height),
                "count": round_decimal(count),
                "concrete_volume_m3": round_decimal(concrete_volume),
                "formwork_area_m2": round_decimal(formwork_area),
                "eps_material_area_m2": round_decimal(eps_material_area),
            }
        )
    beams_concrete_volume = sum((d(item["concrete_volume_m3"]) for item in beam_items), D0)
    beams_formwork_area = sum((d(item["formwork_area_m2"]) for item in beam_items), D0)
    beams_eps_material_area = sum((d(item["eps_material_area_m2"]) for item in beam_items), D0)
    beams_eps_work_length = sum(
        (d(item["length_m"]) * d(item["count"]) for item in beam_items), D0
    )
    return (
        beam_items,
        beams_concrete_volume,
        beams_formwork_area,
        beams_eps_material_area,
        beams_eps_work_length,
    )


def calculate_geometry_context(
    input_data: dict[str, Any],
    warnings: list[str],
    beams_items_formwork_area: Decimal | None = None,
) -> dict[str, Any]:
    method = input_data.get("formwork_area_calc_method")
    if method not in {"legacy_dimensions", "spec_formwork_area"}:
        raise ValueError(
            "formwork_area_calc_method must be either legacy_dimensions or spec_formwork_area."
        )

    slab_length = d(input_data["slab_length_m"]) if input_data.get("slab_length_m") is not None else None
    slab_width = d(input_data["slab_width_m"]) if input_data.get("slab_width_m") is not None else None
    input_slab_area = d(input_data["slab_area_m2"]) if input_data.get("slab_area_m2") is not None else None
    input_edge_perimeter = (
        d(input_data["slab_edge_perimeter_m"])
        if input_data.get("slab_edge_perimeter_m") is not None
        else None
    )
    input_edge_formwork_area = (
        d(input_data["edge_formwork_area_m2"])
        if input_data.get("edge_formwork_area_m2") is not None
        else None
    )
    input_beams_formwork_area = (
        d(input_data["beams_formwork_area_m2"])
        if input_data.get("beams_formwork_area_m2") is not None
        else None
    )
    input_edge_and_beam_formwork_area_combined = (
        d(input_data["edge_and_beam_formwork_area_combined_m2"])
        if input_data.get("edge_and_beam_formwork_area_combined_m2") is not None
        else None
    )
    edge_formwork_height = (
        d(input_data["edge_formwork_height_m"])
        if input_data.get("edge_formwork_height_m") is not None
        else None
    )

    calculated_slab_area = None
    calculated_slab_edge_perimeter = None
    if slab_length is not None and slab_width is not None:
        calculated_slab_area = slab_length * slab_width
        calculated_slab_edge_perimeter = slab_length * d(2) + slab_width * d(2)

    area_delta = None
    if calculated_slab_area is not None and input_slab_area is not None:
        area_delta = calculated_slab_area - input_slab_area
        if abs(area_delta) > d("0.01"):
            warnings.append(
                "calculated_slab_area_m2 differs from slab_area_m2 by more than 0.01 m2."
            )

    if method == "legacy_dimensions":
        if slab_length is None or slab_width is None:
            raise ValueError("slab_length_m and slab_width_m are required for legacy_dimensions.")
        slab_area = calculated_slab_area
        slab_edge_perimeter = calculated_slab_edge_perimeter
        main_formwork_area = slab_area
        if edge_formwork_height is None:
            raise ValueError("edge_formwork_height_m is required for legacy_dimensions.")
        edge_formwork_area = slab_edge_perimeter * edge_formwork_height
        beams_formwork_area = D0
        formwork_area_source = "legacy_dimensions"
        edge_formwork_area_source = "legacy_dimensions"
        slab_edge_perimeter_source = "legacy_dimensions"
    else:
        if input_data.get("main_formwork_area_m2") is None:
            raise ValueError("main_formwork_area_m2 is required for spec_formwork_area.")
        main_formwork_area = d(input_data["main_formwork_area_m2"])
        if main_formwork_area < D0:
            raise ValueError("main_formwork_area_m2 must be >= 0.")
        if input_edge_and_beam_formwork_area_combined is not None:
            # edge_and_beam_formwork_area_combined_m2: additive alternative to edge_formwork_area_m2 +
            # beams_formwork_area_m2 (2026-07-26, ported from floor_slab_1 — same real-project pattern:
            # a project can give edge+beam vertical formwork as one merged number with no way to split
            # it). Mutually exclusive with the split fields.
            if input_edge_formwork_area is not None or input_beams_formwork_area is not None:
                raise ValueError(
                    "edge_and_beam_formwork_area_combined_m2 cannot be combined with "
                    "edge_formwork_area_m2/beams_formwork_area_m2 — the source is either split or "
                    "merged, not both."
                )
            edge_formwork_area = None
            beams_formwork_area = None
            edge_formwork_area_source = "spec_formwork_area_combined_edge_and_beam"
        else:
            if input_edge_formwork_area is None:
                raise ValueError(
                    "edge_formwork_area_m2 is required for spec_formwork_area unless "
                    "edge_and_beam_formwork_area_combined_m2 is provided."
                )
            edge_formwork_area = input_edge_formwork_area
            if edge_formwork_area < D0:
                raise ValueError("edge_formwork_area_m2 must be >= 0.")
            if input_beams_formwork_area is None:
                if beams_items_formwork_area is not None:
                    beams_formwork_area = beams_items_formwork_area
                    warnings.append(
                        "beams_formwork_area_m2 is not provided; using sum of beams.items formwork_area_m2 instead."
                    )
                else:
                    beams_formwork_area = D0
                    warnings.append(
                        "beams_formwork_area_m2 is not provided and no beams.items were given; assumed 0 for this run."
                    )
            else:
                beams_formwork_area = input_beams_formwork_area
                if beams_items_formwork_area is not None:
                    beams_formwork_delta = beams_formwork_area - beams_items_formwork_area
                    if abs(beams_formwork_delta) > d("0.01"):
                        warnings.append(
                            "beams_formwork_area_m2 differs from sum of beams.items formwork_area_m2 by more than 0.01 m2."
                        )
            if beams_formwork_area < D0:
                raise ValueError("beams_formwork_area_m2 must be >= 0.")
            edge_formwork_area_source = "spec_formwork_area"

        if input_edge_perimeter is not None:
            slab_edge_perimeter = input_edge_perimeter
            slab_edge_perimeter_source = "spec_edge_perimeter"
        elif calculated_slab_edge_perimeter is not None:
            slab_edge_perimeter = calculated_slab_edge_perimeter
            slab_edge_perimeter_source = "dimensions_fallback"
            warnings.append(
                "slab_edge_perimeter_m was calculated from dimensions as fallback; "
                "production should provide it from specification."
            )
        else:
            raise ValueError(
                "slab_edge_perimeter_m is required for spec_formwork_area because edge insulation uses it."
            )

        if slab_edge_perimeter < D0:
            raise ValueError("slab_edge_perimeter_m must be >= 0.")

        slab_area = input_slab_area if input_slab_area is not None else calculated_slab_area
        formwork_area_source = "spec_formwork_area"

    formwork_area_delta = None
    if input_slab_area is not None:
        formwork_area_delta = main_formwork_area - input_slab_area
        if abs(formwork_area_delta) > d("0.01"):
            warnings.append("main_formwork_area_m2 differs from slab_area_m2 by more than 0.01 m2.")

    edge_and_beam_formwork_area = (
        input_edge_and_beam_formwork_area_combined
        if input_edge_and_beam_formwork_area_combined is not None
        else edge_formwork_area + beams_formwork_area
    )
    calculated_edge_formwork_area = None
    edge_formwork_area_delta = None
    if edge_formwork_area is not None and slab_edge_perimeter is not None and edge_formwork_height is not None:
        calculated_edge_formwork_area = slab_edge_perimeter * edge_formwork_height
        edge_formwork_area_delta = edge_formwork_area - calculated_edge_formwork_area
        if method == "spec_formwork_area" and abs(edge_formwork_area_delta) > d("0.01"):
            warnings.append("Spec edge_formwork_area_m2 differs from calculated control area.")

    return {
        "formwork_area_calc_method": method,
        "formwork_area_source": formwork_area_source,
        "edge_formwork_area_source": edge_formwork_area_source,
        "slab_edge_perimeter_source": slab_edge_perimeter_source,
        "slab_length_m": slab_length,
        "slab_width_m": slab_width,
        "slab_area_m2": slab_area,
        "slab_edge_perimeter_m": slab_edge_perimeter,
        "main_formwork_area_m2": main_formwork_area,
        "edge_formwork_area_m2": edge_formwork_area,
        "beams_formwork_area_m2": beams_formwork_area,
        "edge_and_beam_formwork_area_combined_m2": input_edge_and_beam_formwork_area_combined,
        "edge_and_beam_formwork_area_m2": edge_and_beam_formwork_area,
        "calculated_edge_formwork_area_m2": calculated_edge_formwork_area,
        "edge_formwork_area_delta_m2": edge_formwork_area_delta,
        "calculated_slab_area_m2": calculated_slab_area,
        "calculated_slab_edge_perimeter_m": calculated_slab_edge_perimeter,
        "input_slab_area_m2": input_slab_area,
        "area_delta_m2": area_delta,
        "formwork_area_delta_m2": formwork_area_delta,
    }


def estimate_line(
    code: str,
    name: str,
    unit: str,
    line_type: str,
    quantity_raw: Any,
    quantity_display: Any | None = None,
    material_unit_price: Any = 0,
    work_unit_price: Any = 0,
    material_total_raw: Any = 0,
    work_total_raw: Any = 0,
    notes: list[str] | None = None,
    extra: dict[str, Any] | None = None,
    price_code: str | None = None,
) -> dict[str, Any]:
    material_raw = d(material_total_raw)
    work_raw = d(work_total_raw)
    line_raw = material_raw + work_raw
    display = quantity_raw if quantity_display is None else quantity_display
    payload = {
        "code": code,
        "name": name,
        "unit": unit,
        "line_type": line_type,
        "quantity_raw": round_decimal(quantity_raw),
        "quantity_display": round_decimal(display),
        "material_unit_price": round_decimal(material_unit_price),
        "material_total_raw": round_decimal(material_raw),
        "material_total": round_money_half_up(material_raw),
        "work_unit_price": round_decimal(work_unit_price),
        "work_total_raw": round_decimal(work_raw),
        "work_total": round_money_half_up(work_raw),
        "line_total_raw": round_decimal(line_raw),
        "line_total": round_money_half_up(line_raw),
        "notes": notes or [],
    }
    if extra:
        payload.update(extra)
    if price_code:
        payload["price_code"] = price_code
    return payload


def _translate_pour_rebar_item(pour_item: dict[str, Any]) -> dict[str, Any]:
    """Renames calculate_floor_slab_pour()'s rebar item fields back to floor_slab_2's original
    shape (raw_length_m/order_weight_kg/weight_with_waste_kg instead of base_length_m/
    delivery_weight_kg/weight_with_waste_kg_display; price_code computed since the shared function
    builds it at the estimate_line call site instead of storing it on the item; rods_ordered/floor/
    component/zone_context dropped - never part of floor_slab_2's own item shape)."""
    out = dict(pour_item)
    out["raw_length_m"] = out.pop("base_length_m")
    out["raw_rods"] = round_decimal(d(out["length_with_waste_m"]) / d(out["rod_length_m"]))
    out["order_weight_kg"] = out.pop("delivery_weight_kg")
    if "weight_with_waste_kg_display" in out:
        # Recompute at full precision instead of renaming: weight_with_waste_kg_display is
        # display_decimal-rounded (2dp) in the shared function, but floor_slab_2's own field is
        # round_decimal-rounded (6dp). Prefer source_weight_kg*waste_coeff (floor_slab_2's own
        # legacy_weight_kg formula, avoids a double-rounding step through the already-6dp-rounded
        # length_with_waste_m); pooled spec_length_items items have no source_weight_kg, so fall
        # back to length_with_waste_m*kg_per_meter there (algebraically identical, just one more
        # rounding step removed from the original raw value).
        if "source_weight_kg" in out:
            out["weight_with_waste_kg"] = round_decimal(d(out["source_weight_kg"]) * d(out["waste_coeff"]))
        else:
            out["weight_with_waste_kg"] = round_decimal(d(out["length_with_waste_m"]) * d(out["kg_per_meter"]))
        out.pop("weight_with_waste_kg_display")
    out["price_code"] = f"rebar_{out['steel_class'].lower()}_d{out['diameter_mm']}_m"
    for stale_key in ("rods_ordered", "floor", "component", "zone_context"):
        out.pop(stale_key, None)
    return out


def calculate_floor_slab_2(input_data: dict[str, Any]) -> dict[str, Any]:
    """Translation wrapper (FLOOR_SLAB_UNIFICATION_PLAN.md P1.2) around calculate_floor_slab_pour()
    in floor_slab_1_calculator.py, the shared "one physical slab pour" calculator. The real money
    math (rebar rounding/pooling, insulation, beam concreting split, concrete order step-rounding,
    formwork rate/delivery/metal-delivery modes) all runs through that one function now; this
    wrapper (a) translates floor_slab_2's flat input_data into the shared function's nested schema,
    and (b) translates the result back into floor_slab_2's original calculation_blocks/
    estimate_lines/totals shape, so all 12 of this section's regression fixtures stay byte-
    identical. calculate_geometry_context()/calculate_beam_items() above are KEPT, not superseded -
    they already produce exactly the output shape this section needs, and their own logic was
    never part of what got unified (no real money flows through them beyond feeding already-
    resolved spec areas into the shared function's flat-scalar "spec_formwork_areas" path, which
    always uses a given scalar as-is - see FLOOR_SLAB_1_VS_2_CALCULATOR_COMPARISON.md point 3).
    delivery_trips_raw/concrete_delivery are computed locally, not pulled from the shared function -
    a genuine, newly-found 7th methodological difference: floor_slab_1 ceils delivery trips from
    the pre-step-rounding waste volume, floor_slab_2 ceils from the already step-rounded order
    volume. Both ceil to the same integer trip count in every existing fixture, but the *_raw
    diagnostic value differs, and two fixtures assert it exactly - so this one piece stays local to
    preserve floor_slab_2's own original formula precisely."""
    warnings: list[str] = []

    (
        beam_items,
        calculated_beams_concrete_volume,
        beams_items_formwork_area,
        beams_items_eps_material_area,
        beams_items_eps_work_length,
    ) = calculate_beam_items(input_data.get("beams"))
    beams_items_total_length = beams_items_eps_work_length

    beams_concrete_volume_override = input_data.get("beams_concrete_volume_m3")
    if beams_concrete_volume_override is not None:
        beams_items_concrete_volume = d(beams_concrete_volume_override)
        if beams_items_concrete_volume < D0:
            raise ValueError("beams_concrete_volume_m3 must be >= 0")
        beams_concrete_volume_source = "spec_beams_concrete_volume"
        beams_concrete_volume_delta = beams_items_concrete_volume - calculated_beams_concrete_volume
        if abs(beams_concrete_volume_delta) > d("0.01"):
            warnings.append(
                "beams_concrete_volume_m3 differs from sum of beams.items concrete_volume_m3 by more than 0.01 m3."
            )
    else:
        beams_items_concrete_volume = calculated_beams_concrete_volume
        beams_concrete_volume_source = "calculated_from_beam_items"
        beams_concrete_volume_delta = None

    geometry_context = calculate_geometry_context(
        input_data,
        warnings,
        beams_items_formwork_area=beams_items_formwork_area if beam_items else None,
    )
    slab_area = geometry_context["slab_area_m2"]
    slab_edge_perimeter = geometry_context["slab_edge_perimeter_m"]
    main_formwork_area = geometry_context["main_formwork_area_m2"]
    edge_formwork_area = geometry_context["edge_formwork_area_m2"]
    beams_formwork_area = geometry_context["beams_formwork_area_m2"]
    edge_and_beam_formwork_area = geometry_context["edge_and_beam_formwork_area_m2"]

    supplier_quote = d(input_data["formwork_rental_supplier_quote_total"])
    raw_supplier_rate = supplier_quote / main_formwork_area
    formwork_rate = d(input_data["formwork_rental_used_rate_per_m2"])

    beams_bottom_formwork_area = d(input_data.get("beams_bottom_formwork_area_m2") or 0)
    edge_beam_formwork_area_for_materials = edge_and_beam_formwork_area + beams_bottom_formwork_area

    # --- build calculate_floor_slab_pour()'s input schema ---
    pour_geometry: dict[str, Any] = {
        "total_concrete_volume_from_spec_m3": input_data["concrete_placing_volume_m3"],
        # slab_thickness_m has no floor_slab_2 equivalent - it's only used by the shared function
        # for a diagnostic delta/fallback that this wrapper always bypasses (an explicit
        # edge_formwork_height_m and pre-resolved spec areas are always given below), so any
        # positive placeholder is safe here.
        "slab_thickness_m": d(1),
        "slab_control_geometry_area_m2": round_decimal(main_formwork_area),
        "slab_edge_perimeter_m": slab_edge_perimeter,
        "main_formwork_area_m2": main_formwork_area,
    }
    if geometry_context["edge_and_beam_formwork_area_combined_m2"] is not None:
        pour_geometry["edge_and_beam_formwork_area_combined_m2"] = geometry_context[
            "edge_and_beam_formwork_area_combined_m2"
        ]
    else:
        pour_geometry["edge_formwork_area_m2"] = edge_formwork_area
        pour_geometry["beams_formwork_area_m2"] = beams_formwork_area
    if input_data.get("edge_formwork_height_m") is not None:
        pour_geometry["edge_formwork_height_m"] = input_data["edge_formwork_height_m"]

    pour_rates: dict[str, Any] = {
        "formwork_rate_calc_method": "direct_section_rate",
        "formwork_rate_per_m2": input_data["formwork_rental_used_rate_per_m2"],
        "formwork_delivery_calc_method": input_data.get("formwork_delivery_calc_method", "area_threshold"),
        "formwork_delivery_rate_per_trip": input_data["formwork_delivery_unit_price"],
        "formwork_delivery_threshold_m2": input_data.get("formwork_delivery_threshold_m2", 180),
        "formwork_consumables_rate_per_m2": input_data["formwork_consumables_rate_per_m2"],
        "plywood_sheet_working_area_m2": input_data["plywood_sheet_working_area_m2"],
        "non_multiple_places_coeff": input_data["non_multiple_places_coeff"],
        "reserve_plywood_sheets": input_data["plywood_reserve_sheets"],
        # additional_timber_coeff=0 neutralizes the shared function's "additional timber" term
        # entirely (a component floor_slab_2 has never had) - overhang_sheet_equivalent/
        # additional_timber_thickness_m are required reads but always multiplied by 0 as a result,
        # so any placeholder value is safe.
        "overhang_sheet_equivalent": 0,
        "additional_timber_coeff": 0,
        "additional_timber_thickness_m": 0,
        "timber_thickness_m": input_data["timber_thickness_m"],
        "plywood_unit_price": input_data["plywood_unit_price"],
        "timber_unit_price": input_data["timber_unit_price"],
        "crane_shift_rate": input_data["crane_unit_price"],
        "metal_delivery_calc_method": "section_output_only",
        "rebar_metal_delivery_unit_price": input_data["rebar_metal_delivery_unit_price"],
        "concrete_waste_coeff": input_data["concrete_waste_coeff"],
        "mixer_capacity_m3": input_data["concrete_mixer_volume_m3"],
        "concrete_round_step_m3": input_data["concrete_round_step_m3"],
        "concrete_unit_price_per_m3": input_data["concrete_unit_price"],
        "concrete_delivery_rate_per_trip": input_data["concrete_delivery_unit_price"],
        "slab_concreting_work_rate_per_m3": input_data["concrete_placing_work_unit_price"],
        "concrete_pump_rate": input_data["concrete_pump_unit_price"],
        "beam_concreting_calc_method": "single_rate",
        "beam_concreting_work_rate_per_m": input_data.get("beam_concreting_work_unit_price") or 0,
        "beam_concreting_work_rate_per_m3": input_data.get("beam_concreting_work_unit_price") or 0,
        "edge_beam_insulation_work_rate_per_m": input_data["edge_insulation_work_unit_price_per_m"],
        "bottom_slab_insulation_work_rate_per_m2": input_data.get(
            "bottom_slab_insulation_work_unit_price_per_m2"
        )
        or 0,
    }

    pour_manual_lines: dict[str, Any] = {
        "formwork_rebar_crane_shifts": input_data["crane_shifts"],
        "concrete_pump_shifts": input_data["concrete_pump_shifts"],
        # technical_supervision_amount=0: floor_slab_2's own line is a zero-cost structural
        # placeholder (line_type zero_excel_structure_line), never a real manual charge - the
        # output translation below rebuilds this line in floor_slab_2's own shape regardless of
        # what the shared function does with it.
        "technical_supervision_amount": 0,
        "rebar_metal_delivery_trucks": input_data["rebar_metal_delivery_trucks"],
    }

    pour_insulation: dict[str, Any] = {
        "insulation_calc_method": "perimeter_based",
        "slab_edge_perimeter_m": slab_edge_perimeter,
        "edge_insulation_height_m": input_data["edge_insulation_height_m"],
        "eps_thickness_m": input_data["eps100_thickness_m"],
        "eps_waste_coeff": input_data["eps_waste_coeff"],
        "eps_pack_volume_m3": input_data["eps100_pack_volume_m3"],
        "foam_coverage_m2_per_can": input_data["foam_coverage_area_per_can_m2"],
        "foam_min_cans": input_data["foam_min_cans"],
        "bottom_slab_eps_work_area_m2": input_data.get("bottom_slab_eps_work_area_m2"),
        "beams_eps_work_length_m": input_data.get("beams_eps_work_length_m"),
        "beams_eps_material_area_m2": input_data.get("beams_eps_material_area_m2"),
        "eps_unit_price_per_m3": input_data["eps100_unit_price"],
        "foam_unit_price_per_can": input_data["foam_can_unit_price"],
    }

    rebar_calc_method_map = {"legacy_weight_kg": "legacy_weight_parts", "spec_length_items": "spec_length_items"}
    input_rebar_calc_method = input_data.get("rebar_calc_method")
    if input_rebar_calc_method not in rebar_calc_method_map:
        raise ValueError("rebar_calc_method must be either legacy_weight_kg or spec_length_items.")
    pour_rebar_calc_method = rebar_calc_method_map[input_rebar_calc_method]

    default_waste_coeff = input_data["rebar_waste_coeff"]
    pour_rebar_items = []
    for item in input_data["rebar_items"]:
        translated = dict(item)
        translated.setdefault("waste_coeff", default_waste_coeff)
        # component/floor: calculate_floor_slab_pour()'s rebar validation hardcodes these two
        # literal checks (a leftover from when the function was floor_slab_1-only) - harmless for
        # floor_slab_2 since nothing downstream reads them beyond the equality check itself, and
        # _translate_pour_rebar_item() strips both back out of the output. P2's real N-pour
        # orchestration will need to generalize this; not touched here to avoid any risk to
        # floor_slab_1's own already-verified 19 regression fixtures.
        translated["component"] = "floor_slab_1"
        translated["floor"] = 1
        pour_rebar_items.append(translated)

    pour_input_data: dict[str, Any] = {
        "case_meta": {"section": "floor_slab_2", "case_name": input_data.get("project_name")},
        "formwork_areas_calc_method": "spec_formwork_areas",
        "geometry": pour_geometry,
        "beams": input_data.get("beams"),
        "beams_concrete_volume_m3": input_data.get("beams_concrete_volume_m3"),
        "beams_bottom_formwork_area_m2": input_data.get("beams_bottom_formwork_area_m2"),
        "rates": pour_rates,
        "rebar_items": pour_rebar_items,
        "rebar_calc_method": pour_rebar_calc_method,
        "insulation": pour_insulation,
        "overheads": {"logistics_and_supply_percent": 0, "consumables_and_tool_percent": 0},
        "manual_lines": pour_manual_lines,
    }

    pour_result = calculate_floor_slab_pour(pour_input_data)
    pour_lines = {line["code"]: line for line in pour_result["estimate_lines"]}
    pour_blocks = pour_result["calculation_blocks"]

    formwork_rental_total_raw = d(pour_lines["formwork_set_rental_material"]["material_total_raw"])
    formwork_delivery_trips = d(pour_blocks["formwork"]["formwork_delivery_trucks"])
    formwork_delivery_unit_price = d(input_data["formwork_delivery_unit_price"])
    formwork_delivery_total_raw = formwork_delivery_trips * formwork_delivery_unit_price
    crane_total_raw = d(input_data["crane_shifts"]) * d(input_data["crane_unit_price"])
    rebar_metal_delivery_total_raw = d(input_data["rebar_metal_delivery_trucks"]) * d(
        input_data["rebar_metal_delivery_unit_price"]
    )
    formwork_consumables_total_raw = d(pour_lines["formwork_consumables"]["material_total_raw"])

    pt = pour_blocks["plywood_and_timber"]
    edge_plywood_sheets_raw = d(pt["edge_and_beam_plywood_sheets_raw"])
    non_multiple_places_area = d(pt["non_multiple_places_area_m2"])
    non_multiple_plywood_sheets_raw = d(pt["non_multiple_places_plywood_sheets_raw"])
    base_plywood_sheets_raw = d(pt["base_plywood_sheets_raw"])
    order_plywood_sheets_raw = d(pt["order_plywood_sheets_raw"])
    plywood_sheets = pt["order_plywood_sheets"]
    plywood_total_raw = d(pour_lines["plywood_fk_18mm_for_edges_and_non_multiple_places"]["material_total_raw"])
    timber_volume = d(pt["timber_volume_m3_raw"])
    timber_total_raw = d(pour_lines["formwork_timber_gost"]["material_total_raw"])

    rebar_items = [_translate_pour_rebar_item(item) for item in pour_blocks["rebar"]["items"]]
    total_rebar_order_length = sum((d(item["order_length_m"]) for item in rebar_items), D0)
    total_rebar_order_weight = sum((d(item["order_weight_kg"]) for item in rebar_items), D0)
    total_rebar_weight_with_waste = sum(
        (d(item.get("weight_with_waste_kg", item["order_weight_kg"])) for item in rebar_items),
        D0,
    )
    rebar_estimate_lines = [
        estimate_line(
            item["code"],
            item["name"],
            "мп",
            "materials",
            item["order_length_m"],
            material_unit_price=item["unit_price_per_m"],
            material_total_raw=item["material_total_raw"],
            price_code=item["price_code"],
        )
        for item in rebar_items
    ]

    concrete_placing_volume = d(input_data["concrete_placing_volume_m3"])
    slab_concrete_volume = concrete_placing_volume - beams_items_concrete_volume
    if slab_concrete_volume < D0:
        raise ValueError("beams.items concrete volume exceeds concrete_placing_volume_m3")
    concrete_work_total_raw = d(pour_lines["floor_slab_concreting_work"]["work_total_raw"])
    if beam_items:
        beam_concreting_work_unit_price = d(input_data["beam_concreting_work_unit_price"])
    else:
        beam_concreting_work_unit_price = D0
    beam_concrete_work_total_raw = d(pour_lines["beam_concreting_work"]["work_total_raw"])
    concrete_volume_with_waste = d(pour_blocks["concrete"]["concrete_volume_with_waste_m3_raw"])
    concrete_order_volume = d(pour_blocks["concrete"]["order_concrete_volume_m3"])
    concrete_material_total_raw = d(pour_lines["concrete_b22_5_m300_material"]["material_total_raw"])
    # delivery_trips_raw/concrete_delivery_total_raw: computed locally from concrete_order_volume,
    # not pulled from the shared function - see this function's docstring (7th difference).
    concrete_delivery_trips_raw = concrete_order_volume / d(input_data["concrete_mixer_volume_m3"])
    concrete_delivery_trips = ceil_decimal(concrete_delivery_trips_raw)
    concrete_delivery_total_raw = d(concrete_delivery_trips) * d(input_data["concrete_delivery_unit_price"])
    concrete_pump_total_raw = d(input_data["concrete_pump_shifts"]) * d(input_data["concrete_pump_unit_price"])

    ic = pour_blocks["insulation"]
    edge_insulation_height = d(input_data["edge_insulation_height_m"])
    edge_insulation_height_source = "specification"
    warnings.append(
        "edge_insulation_height_m = 0.18 m is confirmed by specification; "
        "200 mm in the section title is considered a naming error."
    )
    beams_eps_work_length_override = input_data.get("beams_eps_work_length_m")
    beams_items_eps_work_length = (
        d(beams_eps_work_length_override) if beams_eps_work_length_override is not None else D0
    )
    beams_eps_work_length_source = ic["beams_eps_work_length_source"]
    if beams_eps_work_length_source == "not_provided" and beam_items:
        warnings.append(
            "beams_eps_work_length_m is not provided; beam EPS work length is treated as 0. "
            "Provide the explicit project value when beams are insulated."
        )
    beams_eps_material_area_override = input_data.get("beams_eps_material_area_m2")
    beams_items_eps_material_area = (
        d(beams_eps_material_area_override) if beams_eps_material_area_override is not None else D0
    )
    beams_eps_material_area_source = ic["beams_eps_material_area_source"]
    if beams_eps_material_area_source == "not_provided" and beam_items:
        warnings.append(
            "beams_eps_material_area_m2 is not provided; beam EPS material area is treated as 0. "
            "Provide the explicit project value when beams are insulated."
        )
    edge_insulation_area = d(ic["slab_edge_insulation_area_m2"])
    edge_and_beam_insulation_area = d(ic["edge_and_beam_insulation_area_m2"])
    total_insulation_length = d(ic["edge_beam_eps_work_length_m"])
    bottom_slab_eps_work_area = d(ic["bottom_slab_eps_work_area_m2"])
    bottom_slab_eps_volume = d(ic["bottom_slab_eps_volume_m3"])
    eps100_required_without_waste = d(ic["calculated_clean_eps_volume_m3"])
    eps100_required_with_waste = d(ic["required_eps_volume_m3_raw"])
    eps100_packs_raw = d(ic["eps_packs_raw"])
    eps100_packs = ic["eps_packs_ordered"]
    eps100_order_volume = d(ic["order_eps_volume_m3_raw"])
    foam_cans_raw = d(ic["foam_cans_raw"])
    foam_cans_ordered = ic["foam_cans_ordered"]
    eps100_total_raw = d(pour_lines["eps_penoplex_osnova_100mm"]["material_total_raw"])
    edge_insulation_work_total_raw = d(pour_lines["edge_beam_insulation_work"]["work_total_raw"])
    if bottom_slab_eps_work_area > D0 and "bottom_slab_insulation_work_unit_price_per_m2" not in input_data:
        raise ValueError(
            "bottom_slab_insulation_work_unit_price_per_m2 is required when "
            "bottom_slab_eps_work_area_m2 is provided."
        )
    bottom_slab_insulation_work_total_raw = d(pour_lines["bottom_slab_insulation_work"]["work_total_raw"])
    foam_total_raw = d(pour_lines["eps_glue_foam"]["material_total_raw"])

    direct_cost_base_before_addons_raw = (
        formwork_rental_total_raw
        + formwork_delivery_total_raw
        + crane_total_raw
        + formwork_consumables_total_raw
        + plywood_total_raw
        + timber_total_raw
        + sum((d(item["material_total_raw"]) for item in rebar_items), D0)
        + concrete_work_total_raw
        + beam_concrete_work_total_raw
        + concrete_material_total_raw
        + concrete_delivery_total_raw
        + concrete_pump_total_raw
        + edge_insulation_work_total_raw
        + bottom_slab_insulation_work_total_raw
        + eps100_total_raw
        + foam_total_raw
    )
    logistics_total_raw = direct_cost_base_before_addons_raw * d(input_data["logistics_rate"])
    consumables_total_raw = direct_cost_base_before_addons_raw * d(input_data["consumables_rate"])

    lines = [
        estimate_line(
            "floor_slab_2_formwork_installation_control",
            "Монтаж опалубки под монолитное перекрытие 2-го этажа",
            "м2",
            "zero_excel_structure_line",
            main_formwork_area,
        ),
        estimate_line(
            "formwork_rental_set",
            "Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые)",
            "м2",
            "materials",
            main_formwork_area,
            material_unit_price=formwork_rate,
            material_total_raw=formwork_rental_total_raw,
            price_code="formwork_rental_m2",
        ),
        estimate_line(
            "formwork_delivery_manipulator",
            "Доставка, вывоз опалубки манипулятором",
            "маш",
            "logistics_machinery",
            formwork_delivery_trips,
            material_unit_price=formwork_delivery_unit_price,
            material_total_raw=formwork_delivery_total_raw,
            notes=[
                "До 180 м2 включительно: 1 привоз + 1 вывоз = 2 рейса; "
                "более 180 м2: 2 привоза + 2 вывоза = 4 рейса."
            ],
            price_code="formwork_delivery_truck",
        ),
        estimate_line(
            "crane_supply_formwork_rebar",
            "Подача опалубки, арматуры автокраном",
            "смена",
            "machinery",
            input_data["crane_shifts"],
            material_unit_price=input_data["crane_unit_price"],
            material_total_raw=crane_total_raw,
            price_code="crane_shift",
        ),
        estimate_line(
            "rebar_metal_delivery",
            "Доставка арматуры, металла",
            "маш",
            "logistics_machinery",
            input_data["rebar_metal_delivery_trucks"],
            material_unit_price=input_data["rebar_metal_delivery_unit_price"],
            material_total_raw=rebar_metal_delivery_total_raw,
            notes=["Количество машин — с уровня коробки (box-калькулятор, накопление 10 т по всем разделам с арматурой)."],
            price_code="metal_delivery_truck",
        ),
        estimate_line(
            "formwork_consumables",
            "Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки)",
            "-",
            "materials_consumables",
            1,
            material_total_raw=formwork_consumables_total_raw,
            price_code="formwork_consumables_m2",
        ),
        estimate_line(
            "edge_formwork_installation_control",
            "Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты",
            "м2",
            "zero_excel_structure_line",
            edge_beam_formwork_area_for_materials,
            notes=[
                "Production quantity uses edge_formwork_area_m2 + beams_formwork_area_m2 "
                "(or edge_and_beam_formwork_area_combined_m2) + beams_bottom_formwork_area_m2 "
                "from specification — same combined quantity as plywood/timber material."
            ],
        ),
        estimate_line(
            "plywood_for_edges",
            "Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов",
            "шт",
            "materials",
            plywood_sheets,
            material_unit_price=input_data["plywood_unit_price"],
            material_total_raw=plywood_total_raw,
            price_code="plywood_1520x1520_18mm_sheet",
        ),
        estimate_line(
            "timber_for_formwork",
            "Пиломатериал обрезной для устройства опалубки ГОСТ",
            "м3",
            "materials",
            timber_volume,
            quantity_display=display_decimal(timber_volume, "0.01"),
            material_unit_price=input_data["timber_unit_price"],
            material_total_raw=timber_total_raw,
            notes=["Money is calculated from raw quantity 0.362, not displayed quantity 0.36."],
            price_code="timber_m3",
        ),
        estimate_line(
            "rebar_frame_assembly_control",
            "Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры",
            "мп",
            "zero_excel_structure_line",
            total_rebar_order_length,
        ),
        *rebar_estimate_lines,
        estimate_line(
            "concrete_placing_work",
            "Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300)",
            "м3",
            "work",
            slab_concrete_volume,
            work_unit_price=input_data["concrete_placing_work_unit_price"],
            work_total_raw=concrete_work_total_raw,
            price_code="concrete_placing_work_m3",
        ),
        estimate_line(
            "beam_concreting_work",
            "Бетонирование балки бетоном марки В22,5 (М300)",
            "мп",
            "work",
            beams_items_total_length,
            work_unit_price=beam_concreting_work_unit_price,
            work_total_raw=beam_concrete_work_total_raw,
            notes=[
                "С 2026-07-28 работа по бетонированию балок считается по длине балок, а не по объему бетона.",
                "Quantity and total are 0 when no beams.items are given for this floor slab.",
            ],
            price_code="beam_concrete_placing_work_m",
        ),
        estimate_line(
            "concrete_b22_5_m300_material",
            "Бетон марки В22,5 (М300)",
            "м3",
            "materials",
            concrete_order_volume,
            material_unit_price=input_data["concrete_unit_price"],
            material_total_raw=concrete_material_total_raw,
            price_code="concrete_b22_5_m3",
            extra={
                "quantity_raw_before_order_rounding": round_decimal(concrete_volume_with_waste),
                "quantity_display_control": display_decimal(concrete_volume_with_waste),
            },
        ),
        estimate_line(
            "concrete_delivery",
            "Доставка бетона до объекта",
            "рейс",
            "logistics_machinery",
            concrete_delivery_trips,
            material_unit_price=input_data["concrete_delivery_unit_price"],
            material_total_raw=concrete_delivery_total_raw,
            price_code="concrete_delivery_trip",
        ),
        estimate_line(
            "concrete_pump_32m",
            "Работа бетононасоса 32м + гаситель",
            "смена",
            "machinery_fixed",
            input_data["concrete_pump_shifts"],
            material_unit_price=input_data["concrete_pump_unit_price"],
            material_total_raw=concrete_pump_total_raw,
            price_code="concrete_pump_32m_shift",
        ),
        estimate_line(
            "formwork_dismantling_control",
            "Демонтаж опалубки после завершения бетонирования",
            "м2",
            "zero_excel_structure_line",
            main_formwork_area,
        ),
        estimate_line(
            "edge_insulation_work",
            "Устройство утепления по наружной стороне торцов плиты, балок",
            "мп",
            "work",
            total_insulation_length,
            work_unit_price=input_data["edge_insulation_work_unit_price_per_m"],
            work_total_raw=edge_insulation_work_total_raw,
            notes=[
                "Quantity is slab_edge_perimeter_m plus beams_eps_work_length_m when the project "
                "explicitly gives insulated beam length; beam length is not inferred from beam_items."
            ],
            price_code="edge_insulation_work_m",
        ),
        estimate_line(
            "bottom_slab_insulation_work",
            "Устройство утепления низа плиты",
            "м2",
            "work",
            bottom_slab_eps_work_area,
            work_unit_price=d(input_data.get("bottom_slab_insulation_work_unit_price_per_m2") or 0),
            work_total_raw=bottom_slab_insulation_work_total_raw,
            notes=[
                "Optional production quantity from PDF: horizontal/bottom EPS insulation area of the slab itself. "
                "Defaults to 0 when the project has no such separate line."
            ],
            price_code="eps_bottom_slab_insulation_work_m2",
        ),
        estimate_line(
            "eps100_penoplex_material",
            "Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм",
            "м3",
            "materials",
            eps100_order_volume,
            quantity_display=display_decimal(eps100_order_volume, "0.01"),
            material_unit_price=input_data["eps100_unit_price"],
            material_total_raw=eps100_total_raw,
            price_code="eps_penoplex_osnova_100_m3",
        ),
        estimate_line(
            "eps_foam_glue",
            "Клей-пена для ЭППС",
            "баллон",
            "materials_consumables",
            foam_cans_ordered,
            material_unit_price=input_data["foam_can_unit_price"],
            material_total_raw=foam_total_raw,
            price_code="eps_foam_glue_can",
        ),
        estimate_line(
            "logistics_and_supply",
            "Логистика, и снабжение",
            "-",
            "materials_overhead_percent",
            1,
            material_total_raw=logistics_total_raw,
        ),
        estimate_line(
            "consumables_tool_depreciation",
            "Расходные материалы, амортизация инструмента",
            "комплект",
            "materials_overhead_percent",
            1,
            material_total_raw=consumables_total_raw,
        ),
        estimate_line("technical_supervision", "Технический надзор", "-", "zero_excel_structure_line", 1),
        estimate_line(
            "procurement_storage_costs",
            "Заготовительно-складские расходы",
            "-",
            "zero_excel_structure_line",
            1,
        ),
        estimate_line(
            "overhead_general_business_costs",
            "Накладные и общехозяйственные расходы",
            "-",
            "zero_excel_structure_line",
            1,
        ),
        estimate_line("estimated_profit", "Сметная прибыль", "-", "zero_excel_structure_line", 1),
    ]

    internal_materials_total_raw = sum((d(line["material_total_raw"]) for line in lines), D0)
    internal_works_total_raw = sum((d(line["work_total_raw"]) for line in lines), D0)
    internal_section_total_raw = internal_materials_total_raw + internal_works_total_raw

    totals = {
        "internal_materials_total_raw": round_decimal(internal_materials_total_raw),
        "internal_materials_total": round_money_half_up(internal_materials_total_raw),
        "internal_works_total_raw": round_decimal(internal_works_total_raw),
        "internal_works_total": round_money_half_up(internal_works_total_raw),
        "internal_section_total_raw": round_decimal(internal_section_total_raw),
        "internal_section_total": round_money_half_up(internal_section_total_raw),
        "sum_of_displayed_line_material_totals": sum(line["material_total"] for line in lines),
        "sum_of_displayed_line_work_totals": sum(line["work_total"] for line in lines),
        "sum_of_displayed_line_totals": sum(line["line_total"] for line in lines),
    }

    calculation_blocks = {
        "geometry": {
            "formwork_area_calc_method": geometry_context["formwork_area_calc_method"],
            "formwork_area_source": geometry_context["formwork_area_source"],
            "edge_formwork_area_source": geometry_context["edge_formwork_area_source"],
            "slab_edge_perimeter_source": geometry_context["slab_edge_perimeter_source"],
            "slab_length_m": round_optional(geometry_context["slab_length_m"]),
            "slab_width_m": round_optional(geometry_context["slab_width_m"]),
            "slab_area_m2": round_optional(slab_area),
            "slab_edge_perimeter_m": round_decimal(slab_edge_perimeter),
            "main_formwork_area_m2": round_decimal(main_formwork_area),
            "edge_formwork_area_m2": round_optional(edge_formwork_area),
            "beams_formwork_area_m2": round_optional(beams_formwork_area),
            "edge_and_beam_formwork_area_combined_m2": round_optional(
                geometry_context["edge_and_beam_formwork_area_combined_m2"]
            ),
            "edge_and_beam_formwork_area_m2": round_decimal(edge_and_beam_formwork_area),
            "calculated_edge_formwork_area_m2": round_optional(
                geometry_context["calculated_edge_formwork_area_m2"]
            ),
            "edge_formwork_area_delta_m2": round_optional(
                geometry_context["edge_formwork_area_delta_m2"]
            ),
            "calculated_slab_area_m2": round_optional(geometry_context["calculated_slab_area_m2"]),
            "calculated_slab_edge_perimeter_m": round_optional(
                geometry_context["calculated_slab_edge_perimeter_m"]
            ),
            "input_slab_area_m2": round_optional(geometry_context["input_slab_area_m2"]),
            "area_delta_m2": round_optional(geometry_context["area_delta_m2"]),
            "formwork_area_delta_m2": round_optional(geometry_context["formwork_area_delta_m2"]),
        },
        "formwork": {
            "formwork_area_calc_method": geometry_context["formwork_area_calc_method"],
            "main_formwork_area_m2": round_decimal(main_formwork_area),
            "raw_supplier_rate": round_decimal(raw_supplier_rate),
            "used_rate_per_m2": round_decimal(formwork_rate),
            "edge_formwork_area_m2": round_optional(edge_formwork_area),
            "beams_formwork_area_m2": round_optional(beams_formwork_area),
            "edge_and_beam_formwork_area_m2": round_decimal(edge_and_beam_formwork_area),
            "beams_bottom_formwork_area_m2": round_decimal(beams_bottom_formwork_area),
            "edge_beam_formwork_area_for_materials_m2": round_decimal(edge_beam_formwork_area_for_materials),
            "calculated_edge_formwork_area_m2": round_optional(
                geometry_context["calculated_edge_formwork_area_m2"]
            ),
            "edge_formwork_area_delta_m2": round_optional(
                geometry_context["edge_formwork_area_delta_m2"]
            ),
            "edge_formwork_area_source": geometry_context["edge_formwork_area_source"],
            "formwork_delivery_calc_method": pour_blocks["formwork"]["formwork_delivery_calc_method"],
            "formwork_delivery_area_source_m2": pour_blocks["formwork"]["formwork_delivery_area_source_m2"],
            "formwork_delivery_threshold_m2": pour_blocks["formwork"]["formwork_delivery_threshold_m2"],
            "formwork_delivery_trips": round_decimal(formwork_delivery_trips),
            "formwork_delivery_breakdown": pour_blocks["formwork"]["formwork_delivery_breakdown"],
            "formwork_delivery_status": pour_blocks["formwork"]["formwork_delivery_status"],
        },
        "plywood_and_timber": {
            "edge_and_beam_formwork_area_m2": round_decimal(edge_and_beam_formwork_area),
            "beams_bottom_formwork_area_m2": round_decimal(beams_bottom_formwork_area),
            "edge_beam_formwork_area_for_materials_m2": round_decimal(edge_beam_formwork_area_for_materials),
            "edge_plywood_sheets_raw": round_decimal(edge_plywood_sheets_raw),
            "non_multiple_places_area_m2": round_decimal(non_multiple_places_area),
            "non_multiple_places_plywood_sheets_raw": round_decimal(non_multiple_plywood_sheets_raw),
            "base_plywood_sheets_raw": round_decimal(base_plywood_sheets_raw),
            "order_plywood_sheets_raw": round_decimal(order_plywood_sheets_raw),
            "plywood_sheets": plywood_sheets,
            "timber_volume_m3_raw": round_decimal(timber_volume),
            "timber_volume_m3_display": display_decimal(timber_volume, "0.01"),
        },
        "beams": {
            "items": beam_items,
            "items_count": len(beam_items),
            "items_total_length_m": round_decimal(beams_items_total_length),
            "items_total_concrete_volume_m3": round_decimal(beams_items_concrete_volume),
            "items_total_formwork_area_m2": round_decimal(beams_items_formwork_area),
            "items_total_eps_material_area_m2": round_decimal(beams_items_eps_material_area),
            "items_total_eps_work_length_m": round_decimal(beams_items_eps_work_length),
            "eps_work_length_source": beams_eps_work_length_source,
            "eps_material_area_source": beams_eps_material_area_source,
            "concrete_volume_source": beams_concrete_volume_source,
            "calculated_concrete_volume_m3": round_decimal(calculated_beams_concrete_volume),
            "concrete_volume_delta_m3": None
            if beams_concrete_volume_delta is None
            else round_decimal(beams_concrete_volume_delta),
            "notes": [
                "All values are 0 when no beams.items are given. Beam concrete is subtracted from "
                "concrete_placing_volume_m3 for the slab work line and priced separately on the "
                "beam_concreting_work estimate line. beams_formwork_area_m2 and the insulation "
                "length/area both use this data when their own scalar inputs are absent."
            ],
        },
        "rebar": {
            "rebar_calc_method": input_rebar_calc_method,
            "items": rebar_items,
            "total_rebar_order_length_m": round_decimal(total_rebar_order_length),
            "total_rebar_order_weight_kg": round_decimal(total_rebar_order_weight),
            "total_rebar_weight_with_waste_kg": round_decimal(total_rebar_weight_with_waste, "0.01"),
        },
        "concrete": {
            "concrete_placing_volume_m3": round_decimal(concrete_placing_volume),
            "slab_concrete_volume_m3": round_decimal(slab_concrete_volume),
            "beams_concrete_volume_m3": round_decimal(beams_items_concrete_volume),
            "concrete_volume_with_waste_raw_m3": round_decimal(concrete_volume_with_waste),
            "concrete_volume_with_waste_display_m3": display_decimal(concrete_volume_with_waste),
            "concrete_order_volume_m3": round_decimal(concrete_order_volume),
            "delivery_trips_raw": round_decimal(concrete_delivery_trips_raw),
            "delivery_trips": concrete_delivery_trips,
            "reinforcement_density_kg_per_m3": round_decimal(
                total_rebar_weight_with_waste / concrete_volume_with_waste, "0.01"
            ),
        },
        "insulation": {
            "edge_insulation_height_m": round_decimal(edge_insulation_height),
            "edge_insulation_height_source": edge_insulation_height_source,
            "edge_insulation_area_m2": round_decimal(edge_insulation_area),
            "edge_and_beam_insulation_area_m2": round_decimal(edge_and_beam_insulation_area),
            "bottom_slab_eps_work_area_m2": round_decimal(bottom_slab_eps_work_area),
            "bottom_slab_eps_volume_m3": round_decimal(bottom_slab_eps_volume),
            "total_insulation_length_m": round_decimal(total_insulation_length),
            "eps100_required_volume_without_waste_m3": round_decimal(eps100_required_without_waste),
            "eps100_required_volume_with_waste_m3": round_decimal(eps100_required_with_waste),
            "eps100_packs_raw": round_decimal(eps100_packs_raw),
            "eps100_packs_ordered": eps100_packs,
            "eps100_order_volume_m3": round_decimal(eps100_order_volume),
            "foam_cans_raw": round_decimal(foam_cans_raw),
            "foam_cans_display_control": display_decimal(foam_cans_raw),
            "foam_cans_ordered": foam_cans_ordered,
        },
        "addons": {
            "direct_cost_base_before_addons_raw": round_decimal(direct_cost_base_before_addons_raw),
            "logistics_rate": round_decimal(input_data["logistics_rate"]),
            "logistics_total_raw": round_decimal(logistics_total_raw),
            "consumables_rate": round_decimal(input_data["consumables_rate"]),
            "consumables_total_raw": round_decimal(consumables_total_raw),
        },
    }

    # section_title: was hardcoded to one TRC project's own elevation/thickness ("+4.680 (200мм)")
    # regardless of which project actually ran - same bug class as floor_slab_1's earlier literal-
    # 51.9 bug (see FLOOR_SLAB_1_VS_2_CALCULATOR_COMPARISON.md finding 9). Not compared by run_case.py
    # and not read by the real production workbook (export_calculator_results_to_estimate_workbook.py's
    # own SECTION_ORDER has its own generic title) - only used by this file's own diagnostic
    # markdown report - but still a real "test data leaked into general code" bug. Fixed 2026-08-09
    # (P1.3) by accepting an optional project-supplied override with a generic, non-project-specific
    # fallback instead of a fake elevation/thickness.
    section_title = input_data.get(
        "section_title", "Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 2-го этажа"
    )

    return {
        "project_name": input_data["project_name"],
        "section": "floor_slab_2",
        "section_title": section_title,
        "inputs": input_data,
        "calculation_blocks": calculation_blocks,
        "estimate_lines": lines,
        "totals": totals,
        "warnings": warnings,
    }
