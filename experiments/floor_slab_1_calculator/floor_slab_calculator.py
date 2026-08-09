from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
from typing import Any


D0 = Decimal("0")
D1 = Decimal("1")


def d(value: Any) -> Decimal:
    # Every legitimate optional-value case in this file already guards before calling d()
    # (e.g. `d(x) if x is not None else None`, `d(row.get(k) or 0)`) - d(None) was never
    # meant to succeed. Without this guard it silently became Decimal(str(None)) ->
    # Decimal("None"), which crashes with decimal.InvalidOperation and no indication of
    # which field or row was the problem. Raising here doesn't fix that on its own (still no
    # field name), but every call site's failure becomes at least a clean, catchable
    # ValueError instead of a cryptic low-level Decimal parsing error.
    if value is None:
        raise ValueError("numeric value is required, got None")
    return value if isinstance(value, Decimal) else Decimal(str(value))


def round_money_half_up(value: Any) -> int:
    return int(d(value).quantize(D1, rounding=ROUND_HALF_UP))


def round_decimal(value: Any, places: str = "0.000001") -> float:
    return float(d(value).quantize(Decimal(places), rounding=ROUND_HALF_UP))


def display_decimal(value: Any, places: str = "0.01") -> float:
    return float(d(value).quantize(Decimal(places), rounding=ROUND_HALF_UP))


def quantized_decimal(value: Any, places: str) -> Decimal:
    return d(value).quantize(Decimal(places), rounding=ROUND_HALF_UP)


def ceil_decimal(value: Any) -> int:
    return int(d(value).to_integral_value(rounding=ROUND_CEILING))


def dec_sum(values: list[Any]) -> Decimal:
    total = D0
    for value in values:
        total += d(value)
    return total


def make_rebar_code(steel_class: str, diameter_mm: int) -> str:
    return f"rebar_{steel_class.lower()}_d{diameter_mm}"


def make_rebar_name(steel_class: str, diameter_mm: int) -> str:
    return f"Арматура класса {steel_class} диаметром {diameter_mm} мм"


def calculate_rebar_item(item: dict[str, Any], rebar_calc_method: str) -> dict[str, Any]:
    if rebar_calc_method not in {"legacy_weight_parts", "spec_length_items"}:
        raise ValueError("rebar_calc_method must be legacy_weight_parts or spec_length_items")

    for required_key in ("steel_class", "diameter_mm", "kg_per_meter", "waste_coeff", "rod_length_m", "unit_price_per_m"):
        if item.get(required_key) is None:
            raise ValueError(
                f"rebar_items[].{required_key} is required (row: {item.get('code') or item.get('name') or item})"
            )
    steel_class = item["steel_class"]
    diameter_mm = int(item["diameter_mm"])
    kg_per_meter = d(item["kg_per_meter"])
    waste_coeff = d(item["waste_coeff"])
    rod_length = d(item["rod_length_m"])
    unit_price = d(item["unit_price_per_m"])

    if kg_per_meter <= D0:
        raise ValueError("rebar_items[].kg_per_meter must be > 0")
    if rod_length <= D0:
        raise ValueError("rebar_items[].rod_length_m must be > 0")
    if unit_price < D0:
        raise ValueError("rebar_items[].unit_price_per_m must be >= 0")
    if waste_coeff < D0:
        raise ValueError("rebar_items[].waste_coeff must be >= 0")

    if rebar_calc_method == "legacy_weight_parts":
        source_weight = d(item.get("source_weight_kg", dec_sum(item.get("source_weight_parts_kg", []))))
        if source_weight < D0:
            raise ValueError("rebar_items[].source_weight_kg must be >= 0")
        base_length = source_weight / kg_per_meter
        source_payload = {"source_weight_kg": round_decimal(source_weight)}
        weight_with_waste = source_weight * waste_coeff
    else:
        if item.get("component") != "floor_slab_1":
            raise ValueError("rebar_items[].component must be floor_slab_1 for floor_slab_1_calculator")
        if int(item.get("floor", 0)) != 1:
            raise ValueError("rebar_items[].floor must be 1 for floor_slab_1_calculator")
        if "spec_length_m" not in item:
            raise ValueError("rebar_items[].spec_length_m is required for spec_length_items")
        base_length = d(item["spec_length_m"])
        if base_length < D0:
            raise ValueError("rebar_items[].spec_length_m must be >= 0")
        source_payload = {
            "floor": 1,
            "component": "floor_slab_1",
            "spec_length_m": round_decimal(base_length),
        }
        weight_with_waste = base_length * waste_coeff * kg_per_meter

    length_with_waste = base_length * waste_coeff
    rods_ordered = ceil_decimal(length_with_waste / rod_length)
    order_length = d(rods_ordered) * rod_length
    delivery_weight = order_length * kg_per_meter
    material_total_raw = order_length * unit_price

    return {
        "code": item.get("code", make_rebar_code(steel_class, diameter_mm)),
        "name": item.get("name", make_rebar_name(steel_class, diameter_mm)),
        "steel_class": steel_class,
        "diameter_mm": diameter_mm,
        **source_payload,
        "kg_per_meter": round_decimal(kg_per_meter),
        "base_length_m": round_decimal(base_length),
        "waste_coeff": round_decimal(waste_coeff),
        "length_with_waste_m": round_decimal(length_with_waste),
        "weight_with_waste_kg_display": display_decimal(weight_with_waste),
        "rod_length_m": round_decimal(rod_length),
        "rods": rods_ordered,
        "rods_ordered": rods_ordered,
        "order_length_m": round_decimal(order_length),
        "delivery_weight_kg": round_decimal(delivery_weight),
        "unit_price_per_m": round_decimal(unit_price),
        "material_total_raw": round_decimal(material_total_raw),
        "material_total": round_money_half_up(material_total_raw),
    }


def calculate_rebar_items_pooled(
    items_in: list[dict[str, Any]],
    valid_zone_contexts: set[str],
) -> list[dict[str, Any]]:
    """spec_length_items only (legacy_weight_parts keeps calculate_rebar_item()'s independent
    per-row rounding unchanged - no real-project evidence covers that path). Pools same (floor,
    component, zone_context, steel_class, diameter_mm) rows into ONE combined rod-purchase
    rounding, instead of rounding each spec row to its own rod-multiple independently. Same bug
    and same fix as load_bearing_walls_lintels_calculator.py's rebar_from_spec_length_items_pooled
    (2026-08-09) - confirmed exact on real TRC: main zone's 12 separately-named Ø10 rows sum to
    4286.375m base length, *1.05=4500.69m, /11.7=384.67->385 rods=4504.5m, matching her real number
    exactly (independent per-row rounding gave 4551.3m instead); kitchen zone's 3 Ø10 rows sum to
    811.15m, *1.05=851.71m, /11.7=72.79->73 rods=854.1m, also exact. zone_context (optional per
    item, matching a slab_zones[].context) keeps the two zones' rebar pooled SEPARATELY - pooling
    main+kitchen together instead gives 458 rods=5359.8m, NOT her real 4504.5+854.1=5358.6m (she
    rounds per zone independently, same "apply per zone, then sum" mechanism already proven on
    formwork-delivery trucks and concrete material/trips). The real TRC extraction does not
    currently populate zone_context on rebar rows (a genuine gap, not wired here) - when absent on
    every item, all same-diameter rows across the whole section pool into one group (graceful
    degradation, not a crash), which is closer to her real number than independent rounding but not
    exact for multi-zone projects until zone_context is added at extraction time. See
    floor_slab_1_comparison_findings_2026-08-09 memory."""
    groups: dict[tuple[int, str, str | None, str, int], list[dict[str, Any]]] = {}
    order: list[tuple[int, str, str | None, str, int]] = []
    for item in items_in:
        for required_key in ("steel_class", "diameter_mm", "kg_per_meter", "waste_coeff", "rod_length_m", "unit_price_per_m"):
            if item.get(required_key) is None:
                raise ValueError(
                    f"rebar_items[].{required_key} is required (row: {item.get('code') or item.get('name') or item})"
                )
        if item.get("component") != "floor_slab_1":
            raise ValueError("rebar_items[].component must be floor_slab_1 for floor_slab_1_calculator")
        if int(item.get("floor", 0)) != 1:
            raise ValueError("rebar_items[].floor must be 1 for floor_slab_1_calculator")
        if "spec_length_m" not in item:
            raise ValueError("rebar_items[].spec_length_m is required for spec_length_items")
        if d(item["spec_length_m"]) < D0:
            raise ValueError("rebar_items[].spec_length_m must be >= 0")
        zone_context = item.get("zone_context")
        if zone_context is not None and zone_context not in valid_zone_contexts:
            raise ValueError(
                f"rebar_items[{item.get('code')!r}].zone_context {zone_context!r} does not match "
                "any slab_zones[].context"
            )
        key = (1, "floor_slab_1", zone_context, item["steel_class"], int(item["diameter_mm"]))
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(item)

    zone_index_by_context = {context: i + 1 for i, context in enumerate(sorted(valid_zone_contexts))}
    results: list[dict[str, Any]] = []
    for key in order:
        group_items = groups[key]
        floor, component, zone_context, steel_class, diameter_mm = key
        kg_per_meter = d(group_items[0]["kg_per_meter"])
        rod_length = d(group_items[0]["rod_length_m"])
        unit_price = d(group_items[0]["unit_price_per_m"])
        waste_coeff = d(group_items[0]["waste_coeff"])
        for other in group_items[1:]:
            if (
                d(other["kg_per_meter"]) != kg_per_meter
                or d(other["rod_length_m"]) != rod_length
                or d(other["unit_price_per_m"]) != unit_price
                or d(other["waste_coeff"]) != waste_coeff
            ):
                raise ValueError(
                    f"rebar pooling: rows sharing floor={floor}, component={component}, "
                    f"zone_context={zone_context!r}, steel_class={steel_class}, "
                    f"diameter_mm={diameter_mm} disagree on kg_per_meter/rod_length_m/"
                    "unit_price_per_m/waste_coeff - can't pool safely."
                )

        base_length = dec_sum([d(item["spec_length_m"]) for item in group_items])
        length_with_waste = base_length * waste_coeff
        rods_ordered = ceil_decimal(length_with_waste / rod_length)
        order_length = d(rods_ordered) * rod_length
        delivery_weight = order_length * kg_per_meter
        material_total_raw = order_length * unit_price
        weight_with_waste = length_with_waste * kg_per_meter

        if len(group_items) == 1 and group_items[0].get("code"):
            code = group_items[0]["code"]
            name = group_items[0].get("name") or make_rebar_name(steel_class, diameter_mm)
        else:
            zone_suffix = f"_z{zone_index_by_context[zone_context]}" if zone_context is not None else ""
            code = f"{make_rebar_code(steel_class, diameter_mm)}{zone_suffix}"
            zone_label = f" ({zone_context})" if zone_context is not None else ""
            name = f"{make_rebar_name(steel_class, diameter_mm)}{zone_label}"

        results.append(
            {
                "code": code,
                "name": name,
                "steel_class": steel_class,
                "diameter_mm": diameter_mm,
                "floor": floor,
                "component": component,
                "zone_context": zone_context,
                "spec_length_m": round_decimal(base_length),
                "kg_per_meter": round_decimal(kg_per_meter),
                "base_length_m": round_decimal(base_length),
                "waste_coeff": round_decimal(waste_coeff),
                "length_with_waste_m": round_decimal(length_with_waste),
                "weight_with_waste_kg_display": display_decimal(weight_with_waste),
                "rod_length_m": round_decimal(rod_length),
                "rods": rods_ordered,
                "rods_ordered": rods_ordered,
                "order_length_m": round_decimal(order_length),
                "delivery_weight_kg": round_decimal(delivery_weight),
                "unit_price_per_m": round_decimal(unit_price),
                "material_total_raw": round_decimal(material_total_raw),
                "material_total": round_money_half_up(material_total_raw),
            }
        )
    return results


def calculate_formwork_rate_context(
    rates: dict[str, Any],
    slab_formwork_area: Decimal,
) -> dict[str, Any]:
    method = rates.get("formwork_rate_calc_method")
    if method not in {"legacy_supplier_quote_context", "direct_section_rate"}:
        raise ValueError("formwork_rate_calc_method must be legacy_supplier_quote_context or direct_section_rate")

    if "formwork_rate_per_m2" not in rates:
        raise ValueError("rates.formwork_rate_per_m2 is required")
    formwork_rate = d(rates["formwork_rate_per_m2"])
    if formwork_rate < D0:
        raise ValueError("rates.formwork_rate_per_m2 must be >= 0")

    if method == "legacy_supplier_quote_context":
        if "formwork_supplier_quote_total" not in rates:
            raise ValueError("rates.formwork_supplier_quote_total is required for legacy_supplier_quote_context")
        if "slab_2_formwork_area_for_rate_context_m2" not in rates:
            raise ValueError("rates.slab_2_formwork_area_for_rate_context_m2 is required for legacy_supplier_quote_context")
        formwork_quote_total = d(rates["formwork_supplier_quote_total"])
        slab_2_area_context = d(rates["slab_2_formwork_area_for_rate_context_m2"])
        if formwork_quote_total < D0:
            raise ValueError("rates.formwork_supplier_quote_total must be >= 0")
        if slab_2_area_context < D0:
            raise ValueError("rates.slab_2_formwork_area_for_rate_context_m2 must be >= 0")
        raw_average_rate = formwork_quote_total / (slab_formwork_area + slab_2_area_context)
        return {
            "formwork_rate_calc_method": method,
            "formwork_supplier_quote_total": round_decimal(formwork_quote_total),
            "slab_2_formwork_area_for_rate_context_m2": round_decimal(slab_2_area_context),
            "raw_average_rate": round_decimal(raw_average_rate, "0.0000001"),
            "formwork_rate_per_m2": round_decimal(formwork_rate),
            "box_level_quote_context_used": True,
        }

    return {
        "formwork_rate_calc_method": method,
        "formwork_rate_per_m2": round_decimal(formwork_rate),
        "box_level_quote_context_used": False,
    }


def calculate_metal_delivery_context(
    rates: dict[str, Any],
    section_rebar_delivery_weight: Decimal,
    legacy_section_delivery_weight: Decimal,
) -> dict[str, Any]:
    method = rates.get("metal_delivery_calc_method", "legacy_slab1_slab2_context")
    if method not in {"legacy_slab1_slab2_context", "section_output_only"}:
        raise ValueError("metal_delivery_calc_method must be legacy_slab1_slab2_context or section_output_only")

    capacity = d(rates.get("max_rebar_delivery_weight_per_truck_kg", 10000))
    if capacity <= D0:
        raise ValueError("rates.max_rebar_delivery_weight_per_truck_kg must be > 0")

    if method == "legacy_slab1_slab2_context":
        if "floor_slab_2_rebar_weight_for_delivery_context_kg" not in rates:
            raise ValueError(
                "rates.floor_slab_2_rebar_weight_for_delivery_context_kg is required "
                "for legacy_slab1_slab2_context"
            )
        slab_2_weight = d(rates["floor_slab_2_rebar_weight_for_delivery_context_kg"])
        if slab_2_weight < D0:
            raise ValueError("rates.floor_slab_2_rebar_weight_for_delivery_context_kg must be >= 0")
        total_context_weight = legacy_section_delivery_weight + slab_2_weight
        trucks_ordered = ceil_decimal(total_context_weight / capacity)
        return {
            "metal_delivery_calc_method": method,
            "section_rebar_delivery_weight_kg": round_decimal(section_rebar_delivery_weight),
            "floor_slab_2_rebar_weight_for_delivery_context_kg": round_decimal(slab_2_weight),
            "total_delivery_weight_kg_raw": round_decimal(total_context_weight),
            "total_delivery_weight_kg_display": ceil_decimal(total_context_weight),
            "max_weight_per_truck_kg": round_decimal(capacity),
            "trucks_ordered": trucks_ordered,
            "legacy_delivery_line_enabled": True,
            "box_level_delivery_required": False,
        }

    return {
        "metal_delivery_calc_method": method,
        "section_rebar_delivery_weight_kg": round_decimal(section_rebar_delivery_weight),
        "max_weight_per_truck_kg": round_decimal(capacity),
        "legacy_delivery_line_enabled": False,
        "box_level_delivery_required": True,
    }


def calculate_formwork_delivery_context(
    rates: dict[str, Any],
    manual_lines: dict[str, Any],
    slab_formwork_area: Decimal,
    zone_under_slab_areas_m2: list[Decimal] | None = None,
) -> dict[str, Any]:
    method = rates.get("formwork_delivery_calc_method", "area_threshold")
    if method not in {"area_threshold", "manual_override"}:
        raise ValueError("rates.formwork_delivery_calc_method must be area_threshold or manual_override")

    if slab_formwork_area < D0:
        raise ValueError("slab_formwork_area_m2 must be >= 0")
    delivery_rate = d(rates["formwork_delivery_rate_per_trip"])
    if delivery_rate < D0:
        raise ValueError("rates.formwork_delivery_rate_per_trip must be >= 0")

    # formwork_delivery_threshold_m2 (rates, optional, default 180) - added 2026-08-09 P1.2 so a
    # wrapper can configure it instead of relying on a hardcoded constant; no existing case overrides
    # it, so this is byte-identical everywhere it's not set.
    threshold = d(rates.get("formwork_delivery_threshold_m2", 180))
    if method == "manual_override":
        if "formwork_delivery_trucks_override" not in manual_lines:
            raise ValueError(
                "manual_lines.formwork_delivery_trucks_override is required for formwork_delivery_calc_method=manual_override"
            )
        trucks = d(manual_lines["formwork_delivery_trucks_override"])
        if trucks < D0:
            raise ValueError("manual_lines.formwork_delivery_trucks_override must be >= 0")
        return {
            "formwork_delivery_calc_method": method,
            "formwork_delivery_area_source_m2": round_decimal(slab_formwork_area),
            "formwork_delivery_threshold_m2": round_decimal(threshold),
            "formwork_delivery_trucks": round_decimal(trucks),
            "formwork_delivery_breakdown": "manual override",
            "formwork_delivery_status": "manual_override",
            "formwork_delivery_note": "Количество машин доставки/вывоза опалубки задано ручным override.",
        }

    # Per-zone threshold (2026-08-09): when slab_zones[] gives real per-zone under-slab areas, the
    # 2-or-4-truck threshold is applied to EACH zone independently and summed, not once to the
    # combined project area. Confirmed on real TRC (both zones <=180m2 -> 2+2=4 trucks, not the 2
    # trucks a combined-area check on 148m2 would give) and ARK (zone1 321m2>180 -> 4, zone2
    # 97m2<=180 -> 2, reported as two separate delivery lines, never summed into one project-wide
    # figure) - see reports/trc_vs_original_comparison/05_floor_slab_1.md. Uses each zone's raw
    # spec under_slab_formwork_area_m2 directly (not the fixed-up combined slab_formwork_area,
    # which can't be split back out per zone since beams.items[] isn't zone-scoped - see that same
    # report's Finding 3) - safe here because the threshold check only needs each zone's own area,
    # not a beam-corrected one. Deliberately NOT validated against ЮСВ (single zone, 207.64m2 ->
    # her real 2 trucks contradicts a flat >180 check) - that project has no zone split at all, so
    # this per-zone path never applies to it; the underlying threshold value may not be universal,
    # only the "apply per zone, then sum" mechanism is confirmed.
    if zone_under_slab_areas_m2:
        zone_trucks = [d(2) if area <= threshold else d(4) for area in zone_under_slab_areas_m2]
        trucks = dec_sum(zone_trucks)
        breakdown = " + ".join(
            f"{'1 привоз + 1 вывоз' if zt == d(2) else '2 привоза + 2 вывоза'} (зона {i + 1}, {round_decimal(area)} м2)"
            for i, (zt, area) in enumerate(zip(zone_trucks, zone_under_slab_areas_m2))
        )
        return {
            "formwork_delivery_calc_method": method,
            "formwork_delivery_area_source_m2": round_decimal(slab_formwork_area),
            "formwork_delivery_threshold_m2": round_decimal(threshold),
            "formwork_delivery_trucks": round_decimal(trucks),
            "formwork_delivery_breakdown": breakdown,
            "formwork_delivery_status": "calculated_per_zone",
            "formwork_delivery_note": (
                "Порог 180 м2 применён к каждой зоне slab_zones[] отдельно и просуммирован "
                "(не к общей площади проекта) - подтверждено на реальных ТРЦ/АРК."
            ),
        }

    trucks = d(2) if slab_formwork_area <= threshold else d(4)
    breakdown = "1 привоз + 1 вывоз" if trucks == d(2) else "2 привоза + 2 вывоза"
    return {
        "formwork_delivery_calc_method": method,
        "formwork_delivery_area_source_m2": round_decimal(slab_formwork_area),
        "formwork_delivery_threshold_m2": round_decimal(threshold),
        "formwork_delivery_trucks": round_decimal(trucks),
        "formwork_delivery_breakdown": breakdown,
        "formwork_delivery_status": "calculated",
        "formwork_delivery_note": (
            "До 180 м2 включительно: 1 привоз + 1 вывоз = 2 машины; "
            "более 180 м2: 2 привоза + 2 вывоза = 4 машины."
        ),
    }


def calculate_concrete_order_context(
    rates: dict[str, Any],
    total_concrete_volume: Decimal,
    slab_zones_in: list[dict[str, Any]],
    additional_concrete_items_in: list[dict[str, Any]],
) -> dict[str, Any]:
    """Combined-total waste+ceil by default (unchanged behavior). Switches to per-zone
    waste+ceil-then-sum (2026-08-09) ONLY when additional_concrete_items[] is non-empty - a
    top-level, optional list (same convention as beam_items, NOT nested inside slab_zones, since
    each group is its own set of review-workbook rows) of extra concrete-volume line items some
    real drawings print separately from a zone's main slab pour (e.g. TRC's "балка/ребро в теле
    плиты перекрытия" rows). Her real smeta counts these toward ordered concrete/delivery trips
    only, not toward slab-only concreting volume or formwork area (both already proven correct
    without this addition) - see floor_slab_1_comparison_findings_2026-08-09 memory. Proven exact
    on TRC: main (25.337+1.091)*1.05=27.749->28 m3/4 trips, kitchen (5.975+0.199)*1.05=6.483->7
    m3/1 trip, matching her real rows digit-for-digit (the combined-total formula gives 33 m3/4
    trips instead). Same "apply per zone, then sum" mechanism already confirmed on
    formwork-delivery trucks (TRC+ARK, calculate_formwork_delivery_context). Not validated on a
    second real project yet (ARK's floor slab has no equivalent line to check against) - only the
    per-zone mechanism itself is multi-project-proven."""
    waste_coeff = d(rates["concrete_waste_coeff"])
    mixer_capacity = d(rates["mixer_capacity_m3"])
    if slab_zones_in and additional_concrete_items_in:
        # validated upstream (in calculate_floor_slab_1): every item's zone_context either matches
        # a real zone, or (single-zone projects only) is None and defaults to that one zone.
        default_zone_context = slab_zones_in[0]["context"] if len(slab_zones_in) == 1 else None
        items_by_zone: dict[str, list[Decimal]] = {zone["context"]: [] for zone in slab_zones_in}
        for item in additional_concrete_items_in:
            zone_context = item.get("zone_context") or default_zone_context
            items_by_zone[zone_context].append(d(item["concrete_volume_m3"]))

        zone_volumes_with_waste = []
        zone_order_volumes = []
        zone_trips = []
        for zone in slab_zones_in:
            zone_additional = dec_sum(items_by_zone[zone["context"]])
            zone_with_waste = (d(zone["concrete_volume_m3"]) + zone_additional) * waste_coeff
            zone_volumes_with_waste.append(zone_with_waste)
            zone_order_volumes.append(ceil_decimal(zone_with_waste))
            zone_trips.append(ceil_decimal(zone_with_waste / mixer_capacity))
        concrete_volume_with_waste = dec_sum(zone_volumes_with_waste)
        order_concrete_volume = dec_sum(zone_order_volumes)
        concrete_delivery_trips = dec_sum(zone_trips)
        source = "per_zone_with_additional_items"
    else:
        concrete_volume_with_waste = total_concrete_volume * waste_coeff
        round_step = rates.get("concrete_round_step_m3")
        # concrete_round_step_m3 (rates, optional) - added 2026-08-09 P1.2 so a wrapper can round
        # the order up to a fixed step (floor_slab_2's historical ceil-to-step behavior) instead of
        # always ceiling to a whole m3. Absent (floor_slab_1's own fixtures) -> unchanged behavior.
        if round_step:
            order_concrete_volume = ceil_decimal(concrete_volume_with_waste / d(round_step)) * d(round_step)
        else:
            order_concrete_volume = ceil_decimal(concrete_volume_with_waste)
        concrete_delivery_trips = ceil_decimal(concrete_volume_with_waste / mixer_capacity)
        source = "combined_total"
    return {
        "concrete_volume_with_waste": round_decimal(concrete_volume_with_waste),
        "order_concrete_volume": round_decimal(order_concrete_volume),
        "concrete_delivery_trips": round_decimal(concrete_delivery_trips),
        "concrete_order_source": source,
    }


def calculate_insulation_context(
    insulation: dict[str, Any],
    beams: dict[str, Any] | None,
    slab_thickness: Decimal,
) -> tuple[dict[str, Any], list[str]]:
    method = insulation.get("insulation_calc_method")
    if method not in {"legacy_fixed_edge_length", "spec_work_quantities", "perimeter_based"}:
        raise ValueError(
            "insulation.insulation_calc_method must be legacy_fixed_edge_length, spec_work_quantities "
            "or perimeter_based"
        )

    eps_thickness = d(insulation.get("eps_thickness_m", "0.1"))
    eps_waste_coeff = d(insulation.get("eps_waste_coeff", "1.05"))
    eps_pack_volume = d(insulation["eps_pack_volume_m3"])
    foam_coverage = d(insulation["foam_coverage_m2_per_can"])
    # perimeter_based (floor_slab_2's historical mode) has no independent spec total to cross-check
    # against - it derives total_eps_volume_from_spec_m3 FROM the perimeter formula itself below,
    # so there's never a delta to compute (matches floor_slab_2's calculator.py exactly, which never
    # reads a separate total field at all in this mode).
    if method == "perimeter_based":
        total_eps_volume_from_spec = None
    else:
        total_eps_volume_from_spec = d(insulation["total_eps_volume_from_spec_m3"])
        if total_eps_volume_from_spec < D0:
            raise ValueError("insulation.total_eps_volume_from_spec_m3 must be >= 0")
    if eps_thickness <= D0:
        raise ValueError("insulation.eps_thickness_m must be > 0")
    if eps_waste_coeff < D0:
        raise ValueError("insulation.eps_waste_coeff must be >= 0")
    if eps_pack_volume <= D0:
        raise ValueError("insulation.eps_pack_volume_m3 must be > 0")
    if foam_coverage <= D0:
        raise ValueError("insulation.foam_coverage_m2_per_can must be > 0")

    beam_items = (beams or {}).get("items") or []
    calculated_beams_eps_work_length = D0
    calculated_beams_eps_material_area = D0
    for beam in beam_items:
        count_raw = beam.get("count", 1)
        count = D1 if count_raw is None else d(count_raw)
        length = d(beam["length_m"])
        height = d(beam["height_m"])
        if count < D0 or length < D0 or height < D0:
            raise ValueError("beams.items length_m, height_m and count must be >= 0")
        calculated_beams_eps_work_length += length * count
        calculated_beams_eps_material_area += length * height * count

    warnings: list[str] = []
    if "edge_insulation_height_m" in insulation:
        edge_insulation_height = d(insulation["edge_insulation_height_m"])
        edge_insulation_height_source = "specification"
    else:
        edge_insulation_height = slab_thickness
        edge_insulation_height_source = "fallback_slab_thickness"
        warnings.append("edge_insulation_height_m is not provided; fallback to slab_thickness_m.")
    if edge_insulation_height <= D0:
        raise ValueError("insulation.edge_insulation_height_m must be > 0")

    beams_eps_work_length_override = insulation.get("beams_eps_work_length_m")
    beams_eps_material_area_override = insulation.get("beams_eps_material_area_m2")
    if beams_eps_work_length_override is not None:
        beams_eps_work_length = d(beams_eps_work_length_override)
        beams_eps_work_length_source = "specification"
    else:
        beams_eps_work_length = D0
        beams_eps_work_length_source = "not_provided"
        if beam_items:
            warnings.append(
                "insulation.beams_eps_work_length_m is not provided; beam EPS work length is treated as 0. "
                "Provide the explicit project value when beams are insulated."
            )
    if beams_eps_material_area_override is not None:
        beams_eps_material_area = d(beams_eps_material_area_override)
        beams_eps_material_area_source = "specification"
    else:
        beams_eps_material_area = D0
        beams_eps_material_area_source = "not_provided"
        if beam_items:
            warnings.append(
                "insulation.beams_eps_material_area_m2 is not provided; beam EPS material area is treated as 0. "
                "Provide the explicit project value when beams are insulated."
            )
    if beams_eps_work_length < D0:
        raise ValueError("insulation.beams_eps_work_length_m must be >= 0")
    if beams_eps_material_area < D0:
        raise ValueError("insulation.beams_eps_material_area_m2 must be >= 0")

    if method == "legacy_fixed_edge_length":
        # Fixed fallback constant, not derived from any project's actual geometry — this legacy
        # mode never reads slab dimensions at all, it always uses the same edge length regardless
        # of which project is run. Kept only for historical regression fixtures predating
        # spec_work_quantities (the production mode, which takes this length directly from the
        # project's own specification instead).
        slab_outer_edge_eps_work_length = d("84.8")
        slab_edge_eps_material_area = slab_outer_edge_eps_work_length * edge_insulation_height
        edge_and_beam_eps_material_area = slab_edge_eps_material_area + beams_eps_material_area
        edge_and_beam_eps_volume = edge_and_beam_eps_material_area * eps_thickness
        bottom_slab_eps_volume = total_eps_volume_from_spec - edge_and_beam_eps_volume
        bottom_slab_eps_work_area = bottom_slab_eps_volume / eps_thickness
        calculated_clean_eps_volume = total_eps_volume_from_spec
        eps_volume_delta = D0
    elif method == "spec_work_quantities":
        required_fields = [
            "slab_outer_edge_eps_work_length_m",
            "slab_edge_eps_material_area_m2",
            "bottom_slab_eps_work_area_m2",
            "total_eps_volume_from_spec_m3",
        ]
        for field_name in required_fields:
            if field_name not in insulation:
                raise ValueError(f"insulation.{field_name} is required for spec_work_quantities")

        slab_outer_edge_eps_work_length = d(insulation["slab_outer_edge_eps_work_length_m"])
        slab_edge_eps_material_area = d(insulation["slab_edge_eps_material_area_m2"])
        bottom_slab_eps_work_area = d(insulation["bottom_slab_eps_work_area_m2"])
        if slab_outer_edge_eps_work_length < D0:
            raise ValueError("insulation.slab_outer_edge_eps_work_length_m must be >= 0")
        if slab_edge_eps_material_area < D0:
            raise ValueError("insulation.slab_edge_eps_material_area_m2 must be >= 0")
        if bottom_slab_eps_work_area < D0:
            raise ValueError("insulation.bottom_slab_eps_work_area_m2 must be >= 0")

        edge_and_beam_eps_material_area = slab_edge_eps_material_area + beams_eps_material_area
        edge_and_beam_eps_volume = edge_and_beam_eps_material_area * eps_thickness
        bottom_slab_eps_volume = bottom_slab_eps_work_area * eps_thickness
        calculated_clean_eps_volume = edge_and_beam_eps_volume + bottom_slab_eps_volume
        eps_volume_delta = calculated_clean_eps_volume - total_eps_volume_from_spec
        if abs(eps_volume_delta) > d("0.01"):
            warnings.append("EPS clean volume from areas differs from total_eps_volume_from_spec_m3")
    else:
        # perimeter_based (floor_slab_2's historical mode, ported 2026-08-09 P1.2): edge length
        # comes straight from the slab's own edge perimeter, not a spec work-quantity row, and
        # there's no independent spec total to cross-check against - the "spec total" IS the
        # calculated volume, so eps_volume_delta is always 0 (matches calculator.py exactly: it
        # never reads a separate total_eps_volume field in this mode either).
        if "slab_edge_perimeter_m" not in insulation:
            raise ValueError("insulation.slab_edge_perimeter_m is required for perimeter_based")
        slab_edge_perimeter = d(insulation["slab_edge_perimeter_m"])
        if slab_edge_perimeter < D0:
            raise ValueError("insulation.slab_edge_perimeter_m must be >= 0")
        bottom_slab_eps_work_area = d(insulation.get("bottom_slab_eps_work_area_m2") or 0)
        if bottom_slab_eps_work_area < D0:
            raise ValueError("insulation.bottom_slab_eps_work_area_m2 must be >= 0")

        slab_outer_edge_eps_work_length = slab_edge_perimeter
        slab_edge_eps_material_area = slab_edge_perimeter * edge_insulation_height
        edge_and_beam_eps_material_area = slab_edge_eps_material_area + beams_eps_material_area
        edge_and_beam_eps_volume = edge_and_beam_eps_material_area * eps_thickness
        bottom_slab_eps_volume = bottom_slab_eps_work_area * eps_thickness
        calculated_clean_eps_volume = edge_and_beam_eps_volume + bottom_slab_eps_volume
        total_eps_volume_from_spec = calculated_clean_eps_volume
        eps_volume_delta = D0

    edge_beam_eps_work_length = slab_outer_edge_eps_work_length + beams_eps_work_length
    foam_base_area = edge_and_beam_eps_material_area + bottom_slab_eps_work_area
    required_eps_volume = total_eps_volume_from_spec * eps_waste_coeff
    eps_packs_raw = required_eps_volume / eps_pack_volume
    eps_packs_ordered = ceil_decimal(eps_packs_raw)
    order_eps_volume = d(eps_packs_ordered) * eps_pack_volume
    foam_cans_raw = foam_base_area / foam_coverage
    foam_min_cans = int(insulation.get("foam_min_cans") or 0)
    foam_cans_ordered = max(foam_min_cans, ceil_decimal(foam_cans_raw))

    context = {
        "insulation_calc_method": method,
        "edge_insulation_height_m": round_decimal(edge_insulation_height),
        "edge_insulation_height_source": edge_insulation_height_source,
        "slab_outer_edge_length_m": round_decimal(slab_outer_edge_eps_work_length),
        "slab_outer_edge_eps_work_length_m": round_decimal(slab_outer_edge_eps_work_length),
        "insulated_beams_total_length_m": round_decimal(beams_eps_work_length),
        "beams_eps_work_length_m": round_decimal(beams_eps_work_length),
        "beams_eps_work_length_source": beams_eps_work_length_source,
        "calculated_all_beams_eps_work_length_m": round_decimal(calculated_beams_eps_work_length),
        "total_insulation_length_m": round_decimal(edge_beam_eps_work_length),
        "edge_beam_eps_work_length_m": round_decimal(edge_beam_eps_work_length),
        "slab_edge_insulation_area_m2": round_decimal(slab_edge_eps_material_area),
        "slab_edge_eps_material_area_m2": round_decimal(slab_edge_eps_material_area),
        "beams_insulation_area_m2": round_decimal(beams_eps_material_area),
        "beams_eps_material_area_m2": round_decimal(beams_eps_material_area),
        "beams_eps_material_area_source": beams_eps_material_area_source,
        "calculated_all_beams_eps_material_area_m2": round_decimal(calculated_beams_eps_material_area),
        "edge_and_beam_insulation_area_m2": round_decimal(edge_and_beam_eps_material_area),
        "edge_and_beam_eps_material_area_m2": round_decimal(edge_and_beam_eps_material_area),
        "edge_and_beam_eps_volume_m3": round_decimal(edge_and_beam_eps_volume),
        "bottom_slab_eps_volume_m3": round_decimal(bottom_slab_eps_volume),
        "bottom_slab_insulation_area_m2_raw": round_decimal(bottom_slab_eps_work_area),
        "bottom_slab_eps_work_area_m2": round_decimal(bottom_slab_eps_work_area),
        "total_insulation_area_m2": round_decimal(foam_base_area),
        "foam_base_area_m2": round_decimal(foam_base_area),
        "total_eps_volume_from_spec_m3": round_decimal(total_eps_volume_from_spec),
        "calculated_clean_eps_volume_m3": round_decimal(calculated_clean_eps_volume),
        "eps_volume_delta_m3": round_decimal(eps_volume_delta),
        "eps_thickness_m": round_decimal(eps_thickness),
        "eps_waste_coeff": round_decimal(eps_waste_coeff),
        "required_eps_volume_m3_raw": round_decimal(required_eps_volume),
        "eps_pack_volume_m3": round_decimal(eps_pack_volume),
        "eps_packs_raw": round_decimal(eps_packs_raw),
        "eps_packs_ordered": eps_packs_ordered,
        "order_eps_volume_m3_raw": round_decimal(order_eps_volume),
        "foam_cans_raw": round_decimal(foam_cans_raw),
        "foam_cans_ordered": foam_cans_ordered,
    }
    return context, warnings


def optional_decimal(source: dict[str, Any], key: str) -> Decimal | None:
    if key not in source or source.get(key) is None:
        return None
    return d(source[key])


def first_optional_decimal(*sources_and_keys: tuple[dict[str, Any], str]) -> Decimal | None:
    for source, key in sources_and_keys:
        value = optional_decimal(source, key)
        if value is not None:
            return value
    return None


def calculate_formwork_areas_context(
    input_data: dict[str, Any],
    geometry_in: dict[str, Any],
    calculated_main_formwork_area: Decimal | None,
    calculated_edge_formwork_area: Decimal | None,
    calculated_beams_formwork_area: Decimal | None,
    warnings: list[str],
    zone_main_formwork_area: Decimal | None = None,
    zone_edge_and_beam_formwork_area: Decimal | None = None,
) -> dict[str, Any]:
    method = input_data.get("formwork_areas_calc_method")
    if method not in {"legacy_calculated_from_geometry", "spec_formwork_areas"}:
        raise ValueError("formwork_areas_calc_method must be legacy_calculated_from_geometry or spec_formwork_areas")

    def delta(spec_value: Decimal | None, calculated_value: Decimal | None, label: str) -> Decimal | None:
        if spec_value is None or calculated_value is None:
            return None
        result = spec_value - calculated_value
        if abs(result) > d("0.01"):
            warnings.append(f"Spec formwork area differs from calculated control area: {label}")
        return result

    edge_and_beam_formwork_area_combined: Decimal | None = None
    spec_main_formwork_area: Decimal | None = None

    if method == "legacy_calculated_from_geometry":
        if calculated_main_formwork_area is None:
            raise ValueError("calculated main formwork area is required for legacy_calculated_from_geometry")
        if calculated_edge_formwork_area is None:
            raise ValueError("calculated edge formwork area is required for legacy_calculated_from_geometry")
        if calculated_beams_formwork_area is None:
            raise ValueError("calculated beams formwork area is required for legacy_calculated_from_geometry")
        main_formwork_area = calculated_main_formwork_area
        edge_formwork_area = calculated_edge_formwork_area
        beams_formwork_area = calculated_beams_formwork_area
        spec_main_formwork_area = calculated_main_formwork_area
        source = "legacy_calculated_from_geometry"
    else:
        # main_formwork_area (площадь опалубки под перекрытие, drives "Монтаж опалубки"/"Комплект
        # опалубки"): calculated_main_formwork_area (slab_concrete_volume / slab_thickness) wins
        # over the PDF-quoted spec area (slab_zones' under_slab_formwork_area_m2 / flat
        # main_formwork_area_m2), reversed 2026-08-09. Real TRC/АРК/ЮСВ data confirms her real
        # "Монтаж опалубки"/"Комплект опалубки" quantity always equals slab-only concreting volume
        # divided by slab thickness EXACTLY (TRC main zone: 23.6436/0.2=118.218, kitchen zone:
        # 5.975/0.2=29.875, both exact to 3 decimals; АРК zone with known 0.18m thickness:
        # 17.514/0.18=97.3, exact) - never the "горизонтальная опалубка" PDF area, which apparently
        # represents a different physical concept and consistently undercounted her real quantity
        # by ~20% (see reports/trc_vs_original_comparison/05_floor_slab_1.md). This is universal,
        # not TRC-specific: total_concrete_volume_from_spec_m3/slab_thickness_m are both required
        # geometry inputs, so calculated_main_formwork_area is always available. The spec-quoted
        # area (when given) is kept only as a cross-check delta warning below, not the source.
        spec_main_formwork_area = zone_main_formwork_area if zone_main_formwork_area is not None else first_optional_decimal(
            (input_data, "main_formwork_area_m2"),
            (geometry_in, "main_formwork_area_m2"),
        )
        # 2026-08-09 update: only override with the calculated value when the spec area came from
        # slab_zones[] specifically - that's the exact path proven against real TRC data (see
        # comment above). The flat main_formwork_area_m2 scalar override (input_data/geometry_in)
        # keeps its original priority - existing regression cases show it can legitimately diverge
        # from the concrete-volume calculation (e.g. when beam volumes are themselves estimated
        # rather than given), and there's no real-project evidence yet that it should be overridden.
        if zone_main_formwork_area is not None and calculated_main_formwork_area is not None:
            main_formwork_area = calculated_main_formwork_area
        else:
            main_formwork_area = spec_main_formwork_area
        # edge_and_beam_formwork_area_combined_m2: additive alternative to edge_formwork_area_m2 +
        # beams_formwork_area_m2 (2026-07-21, UNIVERSALIZATION_PLAN.md P1). Real project case: the PDF
        # prints slab-edge and beam vertical formwork as ONE merged number ("Вертикальные поверхности
        # плиты и ж/б балок") with no way to split it. Every downstream estimate line (installation,
        # plywood sheets, timber volume) already reads only the edge+beams SUM, never the two parts
        # separately for money math — so accepting the merged figure directly is safe. When absent,
        # behavior is byte-for-byte identical to before.
        edge_and_beam_formwork_area_combined = (
            zone_edge_and_beam_formwork_area
            if zone_edge_and_beam_formwork_area is not None
            else first_optional_decimal(
                (input_data, "edge_and_beam_formwork_area_combined_m2"),
                (geometry_in, "edge_and_beam_formwork_area_combined_m2"),
            )
        )
        edge_formwork_area = None if zone_edge_and_beam_formwork_area is not None else first_optional_decimal(
            (input_data, "edge_formwork_area_m2"),
            (geometry_in, "edge_formwork_area_m2"),
        )
        beams_formwork_area = None if zone_edge_and_beam_formwork_area is not None else first_optional_decimal(
            (input_data, "beams_formwork_area_m2"),
            (geometry_in, "beams_formwork_area_m2"),
        )
        if main_formwork_area is None:
            raise ValueError("main_formwork_area_m2 is required for spec_formwork_areas")
        if edge_and_beam_formwork_area_combined is not None:
            if edge_formwork_area is not None or beams_formwork_area is not None:
                raise ValueError(
                    "edge_and_beam_formwork_area_combined_m2 cannot be combined with "
                    "edge_formwork_area_m2/beams_formwork_area_m2 — the source is either split or "
                    "merged, not both at once"
                )
        else:
            if edge_formwork_area is None:
                raise ValueError(
                    "edge_formwork_area_m2 is required for spec_formwork_areas unless "
                    "edge_and_beam_formwork_area_combined_m2 is provided"
                )
            if beams_formwork_area is None:
                beams_formwork_area = (
                    calculated_beams_formwork_area if calculated_beams_formwork_area is not None else D0
                )
                warnings.append(
                    "beams_formwork_area_m2 is not provided; using sum of beams.items formwork_area_m2 "
                    "instead (0 when no beams.items were given)."
                )
        source = "spec_formwork_areas" if edge_and_beam_formwork_area_combined is None else "spec_formwork_areas_combined_edge_and_beam"

    for key, value in {
        "main_formwork_area_m2": main_formwork_area,
        "edge_formwork_area_m2": edge_formwork_area,
        "beams_formwork_area_m2": beams_formwork_area,
        "edge_and_beam_formwork_area_combined_m2": edge_and_beam_formwork_area_combined,
    }.items():
        if value is not None and value < D0:
            raise ValueError(f"{key} must be >= 0")

    if edge_and_beam_formwork_area_combined is not None:
        edge_and_beam_formwork_area = edge_and_beam_formwork_area_combined
    else:
        edge_and_beam_formwork_area = edge_formwork_area + beams_formwork_area
    # Always compares the two alternative sources directly (spec-quoted vs concrete-volume-derived)
    # regardless of which one main_formwork_area actually took - unchanged in spirit from before
    # 2026-08-09, just now meaningful for both the slab_zones path (where calculated wins) and the
    # flat-scalar path (where spec still wins): comparing against main_formwork_area itself would
    # always show a trivial zero delta on whichever path already won.
    main_delta = delta(spec_main_formwork_area, calculated_main_formwork_area, "main_formwork_area_m2")
    edge_delta = delta(edge_formwork_area, calculated_edge_formwork_area, "edge_formwork_area_m2")
    beams_delta = delta(beams_formwork_area, calculated_beams_formwork_area, "beams_formwork_area_m2")

    return {
        "formwork_areas_calc_method": method,
        "formwork_areas_source": source,
        "main_formwork_area_m2": round_decimal(main_formwork_area),
        "slab_formwork_area_m2": round_decimal(main_formwork_area),
        "edge_formwork_area_m2": None if edge_formwork_area is None else round_decimal(edge_formwork_area),
        "beams_formwork_area_m2": None if beams_formwork_area is None else round_decimal(beams_formwork_area),
        "edge_and_beam_formwork_area_combined_m2": None
        if edge_and_beam_formwork_area_combined is None
        else round_decimal(edge_and_beam_formwork_area_combined),
        "edge_and_beam_formwork_area_m2": round_decimal(edge_and_beam_formwork_area),
        "calculated_main_formwork_area_m2": None
        if calculated_main_formwork_area is None
        else round_decimal(calculated_main_formwork_area),
        "calculated_edge_formwork_area_m2": None
        if calculated_edge_formwork_area is None
        else round_decimal(calculated_edge_formwork_area),
        "calculated_beams_formwork_area_m2": None
        if calculated_beams_formwork_area is None
        else round_decimal(calculated_beams_formwork_area),
        "main_formwork_area_delta_m2": None if main_delta is None else round_decimal(main_delta),
        "edge_formwork_area_delta_m2": None if edge_delta is None else round_decimal(edge_delta),
        "beams_formwork_area_delta_m2": None if beams_delta is None else round_decimal(beams_delta),
    }


def estimate_line(
    code: str,
    name: str,
    unit: str,
    line_type: str,
    quantity_raw: Any,
    quantity_display: Any,
    material_total_raw: Any = 0,
    work_total_raw: Any = 0,
    notes: list[str] | None = None,
    price_code: str | None = None,
) -> dict[str, Any]:
    material_raw = d(material_total_raw)
    work_raw = d(work_total_raw)
    line_raw = material_raw + work_raw
    payload = {
        "code": code,
        "name": name,
        "unit": unit,
        "line_type": line_type,
        "quantity_raw": round_decimal(quantity_raw),
        "quantity_display": round_decimal(quantity_display),
        "material_total_raw": round_decimal(material_raw),
        "material_total": round_money_half_up(material_raw),
        "work_total_raw": round_decimal(work_raw),
        "work_total": round_money_half_up(work_raw),
        "line_total_raw": round_decimal(line_raw),
        "line_total": round_money_half_up(line_raw),
        "notes": notes or [],
    }
    if price_code:
        payload["price_code"] = price_code
    return payload


def calculate_floor_slab_pour(input_data: dict[str, Any]) -> dict[str, Any]:
    """Generic "one physical slab pour" calculator - FLOOR_SLAB_UNIFICATION_PLAN.md P1.2/P1.3.
    Lives in its own module (moved out of floor_slab_1_calculator.py in P1.3, 2026-08-09) precisely
    so its name doesn't imply floor_slab_2 depends on floor_slab_1 - both floor_slab_1_calculator.py
    and floor_slab_2_calculator/calculator.py are equally just callers of this engine, neither one
    is "the real one". The function body IS floor_slab_1's own former logic (the more mature of the
    two original calculators, per FLOOR_SLAB_1_VS_2_CALCULATOR_COMPARISON.md P1.1) plus new optional
    calc_method-style knobs that let it also reproduce floor_slab_2's historical behavior when a
    wrapper asks for it: `beam_concreting_calc_method` (rates, default "height_split", alt
    "single_rate" - all beams priced by total length, no height-based volume line),
    `concrete_round_step_m3` (rates, optional - when absent, ceils to a whole m3 exactly as before;
    when set, ceils to that step instead, e.g. 0.5), `formwork_delivery_threshold_m2` (rates,
    optional, default 180), `insulation.insulation_calc_method` gaining a third value
    "perimeter_based" (edge length/area derived from slab_edge_perimeter_m, no independent
    spec-total cross-check - see calculate_insulation_context) and `insulation.foam_min_cans`
    (optional, default 0, applies to all 3 insulation modes). Every new knob defaults to
    floor_slab_1's exact prior behavior - calculate_floor_slab_1() (floor_slab_1_calculator.py)
    calls this with zero overrides, so its 19 regression cases stay byte-identical.
    calculate_floor_slab_2() (floor_slab_2_calculator/calculator.py) is a translation wrapper
    around this same function, not a copy of its logic. `component`/`floor` on rebar_items are
    still hardcoded to "floor_slab_1"/1 inside the rebar validation below - a real leftover from
    when this function was floor_slab_1-only, harmless today (never read beyond the equality check,
    floor_slab_2's wrapper injects the same literal to pass it) but needs generalizing once P2
    makes this a genuinely pour-agnostic N-pour engine.
    NOT added here: formwork_dismantling priced-vs-zero-control - both calculators are zero_control
    today (only ARK/USV's real smetas price it; no fixture exists to validate a "priced" branch
    against), and the two calculators' zero-control lines differ only in code/line_type strings
    (cosmetic), which the floor_slab_2 wrapper's output-shape translation handles directly - see
    FLOOR_SLAB_1_VS_2_CALCULATOR_COMPARISON.md."""
    case_meta = input_data["case_meta"]
    geometry_in = input_data["geometry"]
    beams_in = input_data.get("beams")
    rates = input_data["rates"]
    rebar_items_in = input_data["rebar_items"]
    insulation_in = input_data["insulation"]
    overheads_in = input_data["overheads"]
    manual_lines = input_data["manual_lines"]
    rebar_calc_method = input_data.get("rebar_calc_method")

    beam_items = []
    for item in (beams_in or {}).get("items") or []:
        for required_key in ("length_m", "height_m"):
            if item.get(required_key) is None:
                raise ValueError(f"beams.items[{item.get('code')!r}].{required_key} is required")
        length = d(item["length_m"])
        height = d(item["height_m"])
        width_raw = item.get("width_m")
        width = d(width_raw) if width_raw is not None else None
        count_raw = item.get("count", 1)
        count = D1 if count_raw is None else d(count_raw)
        if count < D0:
            raise ValueError("beams.items[].count must be >= 0")

        # width_m is optional (2026-07-28): real spec tables sometimes combine beams of different
        # cross-sections into one row (e.g. ARK's Б4/Б4-1, 300mm vs 400mm) with no single valid width.
        # concrete_volume_m3/formwork_area_m2 can then be given ready on the row instead of recomputed
        # from length*width*height — also lets clean cases (e.g. USV, which prints ready concrete AND
        # formwork per beam) use the spec's own numbers instead of a recomputation that can drift from
        # rounding. See beam_items_width_optional_ready_value_override memory / plan section 39.
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
            }
        )

    beams_total_length = dec_sum([d(item["length_m"]) * d(item["count"]) for item in beam_items])
    calculated_beams_concrete_volume = dec_sum([item["concrete_volume_m3"] for item in beam_items])
    beams_formwork_area = dec_sum([item["formwork_area_m2"] for item in beam_items])

    # Beam concreting height split (2026-08-09, reinstated - was flattened to one rate 2026-07-28,
    # see beam_concreting_work's contract notes for the real-project evidence that reversed this).
    # Beams <=250mm tall are priced by length (мп), beams >250mm tall are priced by concrete volume
    # (м3) - confirmed on real TRC and АРК smetas, and Elena's own current pricelist has both rates
    # (row 28 "до 250мм" мп + row 29 "более 250мм" м3, the second one just never got wired in).
    #
    # beam_concreting_calc_method (rates, optional, default "height_split") - added 2026-08-09 P1.2.
    # "single_rate" reproduces floor_slab_2's historical behavior (all beams, any height, priced by
    # total length at one rate, no volume-based line) by simply routing every beam's length into the
    # "short" bucket and leaving the "tall" bucket empty - the downstream estimate_line code for both
    # lines is untouched, so the two modes never diverge in how a line is built, only in which beams
    # feed which bucket.
    beam_concreting_calc_method = rates.get("beam_concreting_calc_method", "height_split")
    beam_tall_height_threshold_m = d("0.25")
    if beam_concreting_calc_method == "single_rate":
        beams_short_total_length = beams_total_length
        beams_tall_total_volume = D0
    else:
        beams_short_total_length = dec_sum(
            [d(item["length_m"]) * d(item["count"]) for item in beam_items if d(item["height_m"]) <= beam_tall_height_threshold_m]
        )
        beams_tall_total_volume = dec_sum(
            [item["concrete_volume_m3"] for item in beam_items if d(item["height_m"]) > beam_tall_height_threshold_m]
        )

    beams_concrete_warnings: list[str] = []
    beams_concrete_volume_override = input_data.get("beams_concrete_volume_m3")
    if beams_concrete_volume_override is not None:
        beams_concrete_volume = d(beams_concrete_volume_override)
        if beams_concrete_volume < D0:
            raise ValueError("beams_concrete_volume_m3 must be >= 0")
        beams_concrete_volume_source = "spec_beams_concrete_volume"
        beams_concrete_volume_delta = beams_concrete_volume - calculated_beams_concrete_volume
        if abs(beams_concrete_volume_delta) > d("0.01"):
            beams_concrete_warnings.append(
                "beams_concrete_volume_m3 differs from sum of beams.items concrete_volume_m3 by more than 0.01 m3."
            )
    else:
        beams_concrete_volume = calculated_beams_concrete_volume
        beams_concrete_volume_source = "calculated_from_beam_items"
        beams_concrete_volume_delta = None

    # slab_zones[]: purely additive alternative to the scalar geometry.total_concrete_volume_from_spec_m3
    # (2026-07-20, UNIVERSALIZATION_PLAN.md P1). When present, its sum overrides the scalar below —
    # everything downstream already reads the single `total_concrete_volume` local, so no other change
    # is needed. Fixes the real-project case where the slab's concrete is printed as separate zones
    # (main slab + kitchen/dining slab) with no combined total. See p1_slab_zones_shipped memory.
    slab_zones_in = input_data.get("slab_zones") or []
    for zone in slab_zones_in:
        if not zone.get("context"):
            raise ValueError("slab_zones[].context is required")
        if zone.get("concrete_volume_m3") is None:
            raise ValueError(f"slab_zones.{zone['context']}.concrete_volume_m3 is required")
        if d(zone["concrete_volume_m3"]) < D0:
            raise ValueError(f"slab_zones.{zone['context']}.concrete_volume_m3 must be >= 0")

    # additional_concrete_items[]: optional, purely additive (2026-08-09), top-level group (same
    # convention as beam_items - NOT nested inside slab_zones, since the review workbook represents
    # each group as its own set of rows). Some real drawings print a small extra concrete line
    # separately from a zone's main slab pour (e.g. TRC's "балка/ребро в теле плиты перекрытия"
    # rows) that her real smeta counts toward ordered concrete/delivery trips only, not toward
    # slab-only concreting volume or formwork area (both already proven correct without it). A list
    # (not one pre-summed scalar) so any number of such rows, under any name, are captured without
    # losing pieces - same "don't lose pieces" principle as rebar_items[]/roof_zones[] - see
    # floor_slab_1_comparison_findings_2026-08-09 memory. zone_context (optional, required only
    # when multiple slab_zones exist) attributes each item to a zone the same way rebar_items[]
    # already carries floor/component tags for pooling.
    additional_concrete_items_in = input_data.get("additional_concrete_items") or []
    valid_zone_contexts = {zone["context"] for zone in slab_zones_in}
    for extra_item in additional_concrete_items_in:
        if not extra_item.get("name"):
            raise ValueError("additional_concrete_items[].name is required")
        if extra_item.get("concrete_volume_m3") is None:
            raise ValueError(f"additional_concrete_items[{extra_item.get('name')!r}].concrete_volume_m3 is required")
        if d(extra_item["concrete_volume_m3"]) < D0:
            raise ValueError(f"additional_concrete_items[{extra_item.get('name')!r}].concrete_volume_m3 must be >= 0")
        zone_context = extra_item.get("zone_context")
        if zone_context is not None and zone_context not in valid_zone_contexts:
            raise ValueError(
                f"additional_concrete_items[{extra_item['name']!r}].zone_context {zone_context!r} "
                "does not match any slab_zones[].context"
            )
        if zone_context is None and len(slab_zones_in) > 1:
            raise ValueError(
                f"additional_concrete_items[{extra_item['name']!r}].zone_context is required when "
                "more than one slab_zones[] entry exists (ambiguous which zone it belongs to)"
            )
    if slab_zones_in:
        total_concrete_volume = dec_sum([d(zone["concrete_volume_m3"]) for zone in slab_zones_in])
    else:
        total_concrete_volume = d(geometry_in["total_concrete_volume_from_spec_m3"])
    slab_thickness = d(geometry_in["slab_thickness_m"])
    slab_concrete_volume = total_concrete_volume - beams_concrete_volume
    calculated_main_formwork_area = slab_concrete_volume / slab_thickness

    # slab_zones[]-level formwork (2026-08-05, Elena's idea): purely additive alternative to the
    # flat slab_edge_perimeter_m/main_formwork_area_m2/edge_and_beam_formwork_area_combined_m2
    # scalars below. Optional per zone, but once any zone gives any of the three fields, every zone
    # must give all three (no silently-dropped zone). Real ТРЦ case this fixes: the flat scalars can
    # only represent ONE project-wide situation (either a clean edge/beam split, or one merged
    # edge+beam number) — but this project has BOTH at once across its two zones: the main zone's
    # vertical formwork is one unsplittable merged number (torец плиты + балки), while the second
    # (kitchen/dining) zone gives its own pure edge-only number with no beams at all. Each zone's
    # edge_and_beam_formwork_area_m2 already represents whatever mix applies to THAT zone - summing
    # across zones is safe because calculate_formwork_areas_context only ever needs the final total.
    zone_formwork_fields = ("edge_perimeter_m", "under_slab_formwork_area_m2", "edge_and_beam_formwork_area_m2")
    zones_have_formwork = any(zone.get(f) is not None for zone in slab_zones_in for f in zone_formwork_fields)
    zone_edge_perimeter_m: Decimal | None = None
    zone_main_formwork_area_m2: Decimal | None = None
    zone_edge_and_beam_formwork_area_m2: Decimal | None = None
    zone_under_slab_areas_m2: list[Decimal] | None = None
    if zones_have_formwork:
        for zone in slab_zones_in:
            for field in zone_formwork_fields:
                if zone.get(field) is None:
                    raise ValueError(
                        f"slab_zones.{zone['context']}.{field} is required once any zone provides "
                        "zone-level formwork data (all zones must give all three formwork fields, "
                        "not just some — otherwise a zone's real area would be silently dropped)"
                    )
                if d(zone[field]) < D0:
                    raise ValueError(f"slab_zones.{zone['context']}.{field} must be >= 0")
        zone_edge_perimeter_m = dec_sum([d(zone["edge_perimeter_m"]) for zone in slab_zones_in])
        zone_main_formwork_area_m2 = dec_sum([d(zone["under_slab_formwork_area_m2"]) for zone in slab_zones_in])
        zone_edge_and_beam_formwork_area_m2 = dec_sum(
            [d(zone["edge_and_beam_formwork_area_m2"]) for zone in slab_zones_in]
        )
        # Per-zone delivery-truck threshold (2026-08-09) needs each zone's own area separately,
        # not just the sum - see calculate_formwork_delivery_context()'s docstring comment.
        zone_under_slab_areas_m2 = [d(zone["under_slab_formwork_area_m2"]) for zone in slab_zones_in]

    slab_edge_perimeter_m = zone_edge_perimeter_m if zone_edge_perimeter_m is not None else d(geometry_in["slab_edge_perimeter_m"])
    # edge_formwork_height_m: control-calc-only input (never money-critical, see its two usages
    # below). Added 2026-08-05: falls back to slab_thickness_m when not given a value of its own,
    # matching this field's own documented behavior ("если отдельной строки нет, она принимается
    # равной толщине плиты") - previously this fallback was only described in the contract, never
    # actually implemented, so a real project without this line would hard-crash with a KeyError.
    edge_formwork_height_m = geometry_in.get("edge_formwork_height_m")
    if edge_formwork_height_m is None:
        edge_formwork_height_m = geometry_in["slab_thickness_m"]
    calculated_edge_formwork_area = slab_edge_perimeter_m * d(edge_formwork_height_m)
    calculated_beams_formwork_area = beams_formwork_area
    formwork_area_warnings: list[str] = []
    formwork_areas_context = calculate_formwork_areas_context(
        input_data,
        geometry_in,
        calculated_main_formwork_area,
        calculated_edge_formwork_area,
        calculated_beams_formwork_area,
        formwork_area_warnings,
        zone_main_formwork_area=zone_main_formwork_area_m2,
        zone_edge_and_beam_formwork_area=zone_edge_and_beam_formwork_area_m2,
    )
    slab_formwork_area = d(formwork_areas_context["slab_formwork_area_m2"])
    edge_formwork_area_ctx = formwork_areas_context["edge_formwork_area_m2"]
    edge_formwork_area = None if edge_formwork_area_ctx is None else d(edge_formwork_area_ctx)
    beams_formwork_area_ctx = formwork_areas_context["beams_formwork_area_m2"]
    beams_formwork_area = None if beams_formwork_area_ctx is None else d(beams_formwork_area_ctx)
    edge_and_beam_formwork_area = d(formwork_areas_context["edge_and_beam_formwork_area_m2"])

    formwork_rate_context = calculate_formwork_rate_context(rates, slab_formwork_area)
    formwork_rate = d(formwork_rate_context["formwork_rate_per_m2"])
    formwork_delivery_context = calculate_formwork_delivery_context(
        rates, manual_lines, slab_formwork_area, zone_under_slab_areas_m2=zone_under_slab_areas_m2
    )
    formwork_delivery_trucks = d(formwork_delivery_context["formwork_delivery_trucks"])

    # beams_bottom_formwork_area_m2: additive, real-project case (2026-07-26) — a project can print
    # the beam's HORIZONTAL (bottom) formwork area as its own separate line, distinct from both the
    # slab's horizontal area (main_formwork_area_m2) and the combined slab+beam VERTICAL area
    # (edge_and_beam_formwork_area). Nothing upstream folds this into edge_and_beam_formwork_area
    # today, so without this field the beam bottom area was silently never counted for plywood/timber.
    # When absent, behavior is byte-for-byte identical to before.
    beams_bottom_formwork_area = d(input_data.get("beams_bottom_formwork_area_m2") or 0)
    plywood_working_area = d(rates["plywood_sheet_working_area_m2"])
    non_multiple_coeff = d(rates["non_multiple_places_coeff"])
    reserve_plywood_sheets = d(rates["reserve_plywood_sheets"])
    edge_beam_formwork_area_for_materials = edge_and_beam_formwork_area + beams_bottom_formwork_area
    edge_beam_plywood_raw = edge_beam_formwork_area_for_materials / plywood_working_area
    non_multiple_area = slab_formwork_area * non_multiple_coeff
    non_multiple_plywood_raw = non_multiple_area / plywood_working_area
    base_plywood_raw = edge_beam_plywood_raw + non_multiple_plywood_raw
    order_plywood_raw = base_plywood_raw + reserve_plywood_sheets
    order_plywood_sheets = ceil_decimal(order_plywood_raw)

    overhang_sheet_equivalent = d(rates["overhang_sheet_equivalent"])
    timber_thickness = d(rates["timber_thickness_m"])
    additional_timber_volume = (
        (non_multiple_plywood_raw + overhang_sheet_equivalent)
        * d(rates["additional_timber_coeff"])
        * d(rates["additional_timber_thickness_m"])
    )
    base_timber_volume = edge_beam_formwork_area_for_materials * timber_thickness
    timber_volume = quantized_decimal(base_timber_volume + additional_timber_volume, "0.000000001")

    if rebar_calc_method == "spec_length_items":
        # Pooled rounding (2026-08-09) - see calculate_rebar_items_pooled() docstring. Only
        # spec_length_items has real-project evidence for this; legacy_weight_parts keeps the
        # original independent per-row rounding via calculate_rebar_item() below.
        valid_zone_contexts = {zone["context"] for zone in slab_zones_in}
        rebar_items = calculate_rebar_items_pooled(rebar_items_in, valid_zone_contexts)
    else:
        rebar_items = [calculate_rebar_item(item, rebar_calc_method) for item in rebar_items_in]
    rebar_order_length_total = dec_sum([item["order_length_m"] for item in rebar_items])
    floor_slab_1_rebar_weight_with_waste_raw = dec_sum(
        [d(item["length_with_waste_m"]) * d(item["kg_per_meter"]) for item in rebar_items]
    )
    floor_slab_1_rebar_weight_with_waste = d(display_decimal(floor_slab_1_rebar_weight_with_waste_raw, "0.1"))
    section_rebar_delivery_weight = dec_sum(
        [d(item["order_length_m"]) * d(item["kg_per_meter"]) for item in rebar_items]
    )
    rebar_item_controls_by_code = {
        item["code"]: {
            "code": item["code"],
            "name": item["name"],
            "steel_class": item["steel_class"],
            "diameter_mm": item["diameter_mm"],
            "floor": item.get("floor"),
            "component": item.get("component"),
            "spec_length_m": item.get("spec_length_m"),
            "base_length_m": item["base_length_m"],
            "length_with_waste_m": item["length_with_waste_m"],
            "rods": item["rods"],
            "order_length_m": item["order_length_m"],
            "delivery_weight_kg": item["delivery_weight_kg"],
            "material_total_raw": item["material_total_raw"],
        }
        for item in rebar_items
    }
    metal_delivery_context = calculate_metal_delivery_context(
        rates,
        section_rebar_delivery_weight,
        floor_slab_1_rebar_weight_with_waste,
    )

    concrete_order_context = calculate_concrete_order_context(
        rates, total_concrete_volume, slab_zones_in, additional_concrete_items_in
    )
    concrete_volume_with_waste = d(concrete_order_context["concrete_volume_with_waste"])
    # int() would silently truncate a fractional order volume from concrete_round_step_m3 (e.g.
    # step=0.5 -> 33.5); only fall back to int for the whole-m3 case so the default path (no step
    # set) stays byte-identical to the old int()-cast behavior instead of becoming a float everywhere.
    _raw_order_volume = d(concrete_order_context["order_concrete_volume"])
    order_concrete_volume = (
        int(_raw_order_volume)
        if _raw_order_volume == _raw_order_volume.to_integral_value()
        else _raw_order_volume
    )
    concrete_delivery_trips = int(concrete_order_context["concrete_delivery_trips"])

    insulation_context, insulation_warnings = calculate_insulation_context(insulation_in, beams_in, slab_thickness)
    total_insulation_length = d(insulation_context["edge_beam_eps_work_length_m"])
    bottom_slab_insulation_area = d(insulation_context["bottom_slab_eps_work_area_m2"])
    order_eps_volume = d(insulation_context["order_eps_volume_m3_raw"])
    foam_cans_ordered = d(insulation_context["foam_cans_ordered"])

    if beam_items:
        beam_concreting_work_rate_per_m = d(rates["beam_concreting_work_rate_per_m"])
        beam_concreting_work_rate_per_m3 = d(rates["beam_concreting_work_rate_per_m3"])
    else:
        beam_concreting_work_rate_per_m = D0
        beam_concreting_work_rate_per_m3 = D0

    lines = [
        estimate_line(
            "slab_formwork_installation_control",
            "Монтаж опалубки под монолитное перекрытие 1-го этажа",
            "м2",
            "zero_control_line",
            slab_formwork_area,
            slab_formwork_area,
        ),
        estimate_line(
            "formwork_set_rental_material",
            "Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые)",
            "м2",
            "materials",
            slab_formwork_area,
            slab_formwork_area,
            slab_formwork_area * formwork_rate,
            price_code="formwork_rental_m2",
        ),
        estimate_line(
            "formwork_delivery_return_manipulator",
            "Доставка, вывоз опалубки манипулятором",
            "маш",
            "logistics_machinery",
            formwork_delivery_trucks,
            formwork_delivery_trucks,
            formwork_delivery_trucks * d(rates["formwork_delivery_rate_per_trip"]),
            notes=[formwork_delivery_context["formwork_delivery_note"]],
            price_code="formwork_delivery_truck",
        ),
        estimate_line(
            "formwork_rebar_crane_supply",
            "Подача опалубки, арматуры автокраном",
            "смена",
            "machinery",
            d(manual_lines["formwork_rebar_crane_shifts"]),
            d(manual_lines["formwork_rebar_crane_shifts"]),
            d(manual_lines["formwork_rebar_crane_shifts"]) * d(rates["crane_shift_rate"]),
            notes=["3-я смена пока только manual_review / override."],
            price_code="crane_shift",
        ),
        estimate_line(
            "formwork_consumables",
            "Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки)",
            "-",
            "materials_consumables",
            1,
            1,
            slab_formwork_area * d(rates["formwork_consumables_rate_per_m2"]),
            price_code="formwork_consumables_m2",
        ),
        estimate_line(
            "edge_beam_formwork_installation_control",
            "Монтаж опалубки из доски 50 мм и фанеры для устройства балок, для отбортовки плиты",
            "м2",
            "zero_control_line",
            edge_beam_formwork_area_for_materials,
            display_decimal(edge_beam_formwork_area_for_materials),
        ),
        estimate_line(
            "plywood_fk_18mm_for_edges_and_non_multiple_places",
            "Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов",
            "шт",
            "materials",
            order_plywood_sheets,
            order_plywood_sheets,
            d(order_plywood_sheets) * d(rates["plywood_unit_price"]),
            price_code="plywood_1520x1520_18mm_sheet",
        ),
        estimate_line(
            "formwork_timber_gost",
            "Пиломатериал обрезной для устройства опалубки ГОСТ",
            "м3",
            "materials",
            timber_volume,
            display_decimal(timber_volume),
            timber_volume * d(rates["timber_unit_price"]),
            notes=["Сумма считается от quantity_raw, не от отображаемого количества."],
            price_code="timber_m3",
        ),
        estimate_line(
            "floor_slab_rebar_frame_assembly_control",
            "Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры (в том числе балок)",
            "мп",
            "zero_control_line",
            rebar_order_length_total,
            rebar_order_length_total,
        ),
    ]

    for item in rebar_items:
        lines.append(
            estimate_line(
                item["code"],
                item["name"],
                "мп",
                "materials",
                item["order_length_m"],
                item["order_length_m"],
                item["material_total_raw"],
                price_code=f"rebar_{item['steel_class'].lower()}_d{item['diameter_mm']}_m",
            )
        )

    if metal_delivery_context["legacy_delivery_line_enabled"]:
        rebar_delivery_trucks = d(metal_delivery_context["trucks_ordered"])
        lines.append(
            estimate_line(
                "rebar_metal_delivery",
                "Доставка арматуры, металла",
                "маш",
                "logistics_machinery",
                rebar_delivery_trucks,
                rebar_delivery_trucks,
                rebar_delivery_trucks * d(rates["rebar_delivery_rate_per_truck"]),
                notes=["Legacy: доставка металла считалась с контекстом веса арматуры плиты 2-го этажа."],
                price_code="metal_delivery_truck",
            )
        )
    elif metal_delivery_context["box_level_delivery_required"]:
        # section_output_only (production, 2026-07-30): this section no longer computes its own
        # delivery-truck count from a slab_1+slab_2-only context (see legacy branch above) - the
        # count comes from the box_calculator's 10-tonne threshold allocation across all 4
        # rebar-bearing sections (populate_review_workbook_from_extraction.py), same mechanism as
        # foundation_slab.rebar_metal_delivery_trucks. Naturally 0 for projects where this section's
        # own rebar weight doesn't cross a threshold - same zero-when-absent pattern as
        # beam_concreting_work above.
        rebar_delivery_trucks = d(manual_lines["rebar_metal_delivery_trucks"])
        lines.append(
            estimate_line(
                "rebar_metal_delivery",
                "Доставка арматуры, металла",
                "маш",
                "logistics_machinery",
                rebar_delivery_trucks,
                rebar_delivery_trucks,
                rebar_delivery_trucks * d(rates["rebar_metal_delivery_unit_price"]),
                notes=["Количество машин — с уровня коробки (box-калькулятор, накопление 10 т по всем разделам с арматурой)."],
                price_code="metal_delivery_truck",
            )
        )

    lines.extend(
        [
            estimate_line(
                "floor_slab_concreting_work",
                "Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300)",
                "м3",
                "work",
                slab_concrete_volume,
                display_decimal(slab_concrete_volume),
                0,
                slab_concrete_volume * d(rates["slab_concreting_work_rate_per_m3"]),
                notes=["Стоимость считается от raw 37.3752, не от display 37.38."],
                price_code="concrete_placing_work_m3",
            ),
            estimate_line(
                "beam_concreting_work",
                "Бетонирование балки высотой до 250мм бетоном марки В22,5 (М300)",
                "мп",
                "work",
                beams_short_total_length,
                display_decimal(beams_short_total_length),
                0,
                beams_short_total_length * beam_concreting_work_rate_per_m,
                notes=[
                    "2026-08-09: разделено по высоте балки (было единой ставкой по длине с "
                    "2026-07-28 по всем балкам). Только балки высотой <=250мм."
                ],
                price_code="beam_concrete_placing_work_m",
            ),
            estimate_line(
                "beam_concreting_work_tall",
                "Бетонирование балки высотой более 250мм бетоном марки В22,5 (М300)",
                "м3",
                "work",
                beams_tall_total_volume,
                display_decimal(beams_tall_total_volume),
                0,
                beams_tall_total_volume * beam_concreting_work_rate_per_m3,
                notes=["2026-08-09: только балки высотой >250мм, цена за м3 бетона, а не за метр балки."],
                price_code="beam_concrete_placing_work_m3",
            ),
            estimate_line(
                "concrete_b22_5_m300_material",
                "Бетон марки В22,5 (М300)",
                "м3",
                "materials",
                order_concrete_volume,
                order_concrete_volume,
                d(order_concrete_volume) * d(rates["concrete_unit_price_per_m3"]),
                price_code="concrete_b22_5_m3",
            ),
            estimate_line(
                "concrete_delivery",
                "Доставка бетона до объекта",
                "рейс",
                "logistics_machinery",
                concrete_delivery_trips,
                concrete_delivery_trips,
                d(concrete_delivery_trips) * d(rates["concrete_delivery_rate_per_trip"]),
                price_code="concrete_delivery_trip",
            ),
            estimate_line(
                "concrete_pump_32m",
                "Работа бетононасоса 32м + гаситель",
                "смена",
                "machinery_fixed",
                d(manual_lines["concrete_pump_shifts"]),
                d(manual_lines["concrete_pump_shifts"]),
                d(manual_lines["concrete_pump_shifts"]) * d(rates["concrete_pump_rate"]),
                notes=["Fixed/manual line; не вычислять от объёма бетона."],
                price_code="concrete_pump_32m_shift",
            ),
            estimate_line(
                "formwork_dismantling_zero_internal",
                "Демонтаж опалубки после завершения бетонирования",
                "м2",
                "client_only_zero_internal_line",
                slab_formwork_area,
                display_decimal(slab_formwork_area),
            ),
            estimate_line(
                "edge_beam_insulation_work",
                "Устройство утепления по наружной стороне торцов плиты, балок",
                "мп",
                "work",
                total_insulation_length,
                total_insulation_length,
                0,
                total_insulation_length * d(rates["edge_beam_insulation_work_rate_per_m"]),
                price_code="edge_insulation_work_m",
            ),
            estimate_line(
                "bottom_slab_insulation_work",
                "Устройство утепления низа плиты",
                "м2",
                "work",
                bottom_slab_insulation_area,
                display_decimal(bottom_slab_insulation_area),
                0,
                bottom_slab_insulation_area * d(rates["bottom_slab_insulation_work_rate_per_m2"]),
                price_code="eps_bottom_slab_insulation_work_m2",
            ),
            estimate_line(
                "eps_penoplex_osnova_100mm",
                "Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм",
                "м3",
                "materials",
                order_eps_volume,
                display_decimal(order_eps_volume),
                order_eps_volume * d(insulation_in["eps_unit_price_per_m3"]),
                notes=["Стоимость считается от закупочного raw-объёма 8.319, не от display 8.32."],
                price_code="eps_penoplex_osnova_100_m3",
            ),
            estimate_line(
                "eps_glue_foam",
                "Клей-пена для ЭППС",
                "баллон",
                "materials_consumables",
                foam_cans_ordered,
                foam_cans_ordered,
                d(foam_cans_ordered) * d(insulation_in["foam_unit_price_per_can"]),
                price_code="eps_foam_glue_can",
            ),
        ]
    )

    base_subtotal_raw = dec_sum([line["line_total_raw"] for line in lines])
    logistics_total_raw = base_subtotal_raw * d(overheads_in["logistics_and_supply_percent"])
    consumables_total_raw = base_subtotal_raw * d(overheads_in["consumables_and_tool_percent"])
    lines.extend(
        [
            estimate_line(
                "logistics_and_supply",
                "Логистика, и снабжение",
                "-",
                "materials_overhead_percent",
                1,
                1,
                logistics_total_raw,
            ),
            estimate_line(
                "consumables_tool_depreciation",
                "Расходные материалы, амортизация инструмента",
                "комплект",
                "materials_overhead_percent",
                1,
                1,
                consumables_total_raw,
            ),
            estimate_line(
                "technical_supervision",
                "Технический надзор",
                "-",
                "manual_fixed_work",
                1,
                1,
                0,
                d(manual_lines["technical_supervision_amount"]),
                price_code="technical_supervision_fixed",
            ),
        ]
    )

    materials_total = sum(line["material_total"] for line in lines)
    works_total = sum(line["work_total"] for line in lines)
    section_total = materials_total + works_total

    formwork_block = {
        **formwork_areas_context,
        "excel_rate_per_m2": formwork_rate_context["formwork_rate_per_m2"],
        **formwork_delivery_context,
    }
    if formwork_rate_context["formwork_rate_calc_method"] == "legacy_supplier_quote_context":
        formwork_block.update(
            {
                "supplier_quote_total": formwork_rate_context["formwork_supplier_quote_total"],
                "slab_2_formwork_area_for_rate_context_m2": formwork_rate_context[
                    "slab_2_formwork_area_for_rate_context_m2"
                ],
                "raw_average_rate": formwork_rate_context["raw_average_rate"],
            }
        )

    calculation_blocks = {
        "geometry": {
            "total_concrete_volume_from_spec_m3": round_decimal(total_concrete_volume),
            "slab_thickness_m": round_decimal(slab_thickness),
            "slab_concrete_volume_m3_raw": round_decimal(slab_concrete_volume),
            "slab_concrete_volume_m3_display": display_decimal(slab_concrete_volume),
            "slab_formwork_area_m2": display_decimal(slab_formwork_area),
            "slab_control_geometry_area_m2": geometry_in["slab_control_geometry_area_m2"],
            "slab_edge_perimeter_m": round_decimal(slab_edge_perimeter_m),
            "edge_formwork_height_m": round_decimal(d(edge_formwork_height_m)),
        },
        "beams": {
            "items": beam_items,
            "total_length_m": round_decimal(beams_total_length),
            "total_concrete_volume_m3": round_decimal(beams_concrete_volume),
            "total_formwork_area_m2": None if beams_formwork_area is None else round_decimal(beams_formwork_area),
            "concrete_volume_source": beams_concrete_volume_source,
            "calculated_concrete_volume_m3": round_decimal(calculated_beams_concrete_volume),
            "concrete_volume_delta_m3": None
            if beams_concrete_volume_delta is None
            else round_decimal(beams_concrete_volume_delta),
        },
        "formwork": formwork_block,
        "formwork_rate_context": formwork_rate_context,
        "plywood_and_timber": {
            "beams_bottom_formwork_area_m2": round_decimal(beams_bottom_formwork_area),
            "edge_beam_formwork_area_for_materials_m2": round_decimal(edge_beam_formwork_area_for_materials),
            "edge_and_beam_plywood_sheets_raw": round_decimal(edge_beam_plywood_raw),
            "non_multiple_places_area_m2": round_decimal(non_multiple_area),
            "non_multiple_places_plywood_sheets_raw": round_decimal(non_multiple_plywood_raw),
            "base_plywood_sheets_raw": round_decimal(base_plywood_raw),
            "order_plywood_sheets_raw": round_decimal(order_plywood_raw),
            "order_plywood_sheets": order_plywood_sheets,
            "overhang_sheet_equivalent": round_decimal(overhang_sheet_equivalent),
            "base_timber_volume_m3": round_decimal(base_timber_volume),
            "additional_timber_volume_m3": round_decimal(additional_timber_volume),
            "timber_volume_m3_raw": round_decimal(timber_volume),
        },
        "rebar": {
            "rebar_calc_method": rebar_calc_method,
            "items": rebar_items,
            "item_controls_by_code": rebar_item_controls_by_code,
            "rebar_frame_assembly_quantity_m": round_decimal(rebar_order_length_total),
            "floor_slab_1_rebar_weight_with_waste_kg": display_decimal(floor_slab_1_rebar_weight_with_waste, "0.1"),
            **metal_delivery_context,
        },
        "concrete": {
            "total_project_concrete_volume_m3": round_decimal(total_concrete_volume),
            "concrete_volume_with_waste_m3_raw": round_decimal(concrete_volume_with_waste),
            "concrete_volume_with_waste_m3_display": display_decimal(concrete_volume_with_waste),
            "order_concrete_volume_m3": (
                order_concrete_volume
                if isinstance(order_concrete_volume, int)
                else round_decimal(order_concrete_volume)
            ),
            "mixer_capacity_m3": rates["mixer_capacity_m3"],
            "concrete_delivery_trips": concrete_delivery_trips,
            "concrete_order_source": concrete_order_context["concrete_order_source"],
            "additional_concrete_items": additional_concrete_items_in,
        },
        "slab_zones": {
            "used": bool(slab_zones_in),
            "zone_count": len(slab_zones_in),
        },
        "insulation": insulation_context,
        "overheads": {
            "base_subtotal_raw_before_overheads": round_decimal(base_subtotal_raw),
            "logistics_and_supply_percent": overheads_in["logistics_and_supply_percent"],
            "logistics_and_supply_total_raw": round_decimal(logistics_total_raw),
            "logistics_and_supply_total": round_money_half_up(logistics_total_raw),
            "consumables_and_tool_percent": overheads_in["consumables_and_tool_percent"],
            "consumables_and_tool_depreciation_total_raw": round_decimal(consumables_total_raw),
            "consumables_and_tool_depreciation_total": round_money_half_up(consumables_total_raw),
        },
        "manual_lines": {
            "concrete_pump_shifts": manual_lines["concrete_pump_shifts"],
            "technical_supervision_amount": manual_lines["technical_supervision_amount"],
        },
        "control_metrics": {
            "control_geometry_area_m2": geometry_in["slab_control_geometry_area_m2"],
            "slab_area_used_in_estimate_m2": display_decimal(slab_formwork_area),
            "beam_concreting_control_total_by_length": round_money_half_up(
                beams_total_length * beam_concreting_work_rate_per_m
            ),
            "reinforcement_density_kg_per_m3": display_decimal(
                floor_slab_1_rebar_weight_with_waste
                / d(display_decimal(concrete_volume_with_waste))
            ),
        },
    }

    return {
        "case_meta": case_meta,
        "inputs": input_data,
        "calculation_blocks": calculation_blocks,
        "estimate_lines": lines,
        "totals": {
            "internal_materials_total": materials_total,
            "internal_works_total": works_total,
            "internal_section_total": section_total,
            "base_subtotal_raw_before_overheads": round_decimal(base_subtotal_raw),
            "logistics_and_supply_total": round_money_half_up(logistics_total_raw),
            "consumables_and_tool_depreciation_total": round_money_half_up(consumables_total_raw),
            "technical_supervision_total": round_money_half_up(manual_lines["technical_supervision_amount"]),
        },
        "warnings": formwork_area_warnings + insulation_warnings + beams_concrete_warnings,
    }
