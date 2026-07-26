from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
from typing import Any


D0 = Decimal("0")
D1 = Decimal("1")


def d(value: Any) -> Decimal:
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
) -> dict[str, Any]:
    method = rates.get("formwork_delivery_calc_method", "area_threshold")
    if method not in {"area_threshold", "manual_override"}:
        raise ValueError("rates.formwork_delivery_calc_method must be area_threshold or manual_override")

    if slab_formwork_area < D0:
        raise ValueError("slab_formwork_area_m2 must be >= 0")
    delivery_rate = d(rates["formwork_delivery_rate_per_trip"])
    if delivery_rate < D0:
        raise ValueError("rates.formwork_delivery_rate_per_trip must be >= 0")

    threshold = d(180)
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


def calculate_insulation_context(
    insulation: dict[str, Any],
    beams: dict[str, Any] | None,
    slab_thickness: Decimal,
) -> tuple[dict[str, Any], list[str]]:
    method = insulation.get("insulation_calc_method")
    if method not in {"legacy_fixed_edge_length", "spec_work_quantities"}:
        raise ValueError("insulation.insulation_calc_method must be legacy_fixed_edge_length or spec_work_quantities")

    eps_thickness = d(insulation.get("eps_thickness_m", "0.1"))
    eps_waste_coeff = d(insulation.get("eps_waste_coeff", "1.05"))
    eps_pack_volume = d(insulation["eps_pack_volume_m3"])
    foam_coverage = d(insulation["foam_coverage_m2_per_can"])
    total_eps_volume_from_spec = d(insulation["total_eps_volume_from_spec_m3"])
    if eps_thickness <= D0:
        raise ValueError("insulation.eps_thickness_m must be > 0")
    if eps_waste_coeff < D0:
        raise ValueError("insulation.eps_waste_coeff must be >= 0")
    if eps_pack_volume <= D0:
        raise ValueError("insulation.eps_pack_volume_m3 must be > 0")
    if foam_coverage <= D0:
        raise ValueError("insulation.foam_coverage_m2_per_can must be > 0")
    if total_eps_volume_from_spec < D0:
        raise ValueError("insulation.total_eps_volume_from_spec_m3 must be >= 0")

    beam_items = (beams or {}).get("items") or []
    beams_eps_work_length = D0
    beams_eps_material_area = D0
    for beam in beam_items:
        count = d(beam.get("count", 1))
        length = d(beam["length_m"])
        height = d(beam["height_m"])
        if count < D0 or length < D0 or height < D0:
            raise ValueError("beams.items length_m, height_m and count must be >= 0")
        beams_eps_work_length += length * count
        beams_eps_material_area += length * height * count

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
    else:
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

    edge_beam_eps_work_length = slab_outer_edge_eps_work_length + beams_eps_work_length
    foam_base_area = edge_and_beam_eps_material_area + bottom_slab_eps_work_area
    required_eps_volume = total_eps_volume_from_spec * eps_waste_coeff
    eps_packs_raw = required_eps_volume / eps_pack_volume
    eps_packs_ordered = ceil_decimal(eps_packs_raw)
    order_eps_volume = d(eps_packs_ordered) * eps_pack_volume
    foam_cans_raw = foam_base_area / foam_coverage
    foam_cans_ordered = ceil_decimal(foam_cans_raw)

    context = {
        "insulation_calc_method": method,
        "edge_insulation_height_m": round_decimal(edge_insulation_height),
        "edge_insulation_height_source": edge_insulation_height_source,
        "slab_outer_edge_length_m": round_decimal(slab_outer_edge_eps_work_length),
        "slab_outer_edge_eps_work_length_m": round_decimal(slab_outer_edge_eps_work_length),
        "insulated_beams_total_length_m": round_decimal(beams_eps_work_length),
        "beams_eps_work_length_m": round_decimal(beams_eps_work_length),
        "total_insulation_length_m": round_decimal(edge_beam_eps_work_length),
        "edge_beam_eps_work_length_m": round_decimal(edge_beam_eps_work_length),
        "slab_edge_insulation_area_m2": round_decimal(slab_edge_eps_material_area),
        "slab_edge_eps_material_area_m2": round_decimal(slab_edge_eps_material_area),
        "beams_insulation_area_m2": round_decimal(beams_eps_material_area),
        "beams_eps_material_area_m2": round_decimal(beams_eps_material_area),
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
        source = "legacy_calculated_from_geometry"
    else:
        main_formwork_area = first_optional_decimal(
            (input_data, "main_formwork_area_m2"),
            (geometry_in, "main_formwork_area_m2"),
        )
        # edge_and_beam_formwork_area_combined_m2: additive alternative to edge_formwork_area_m2 +
        # beams_formwork_area_m2 (2026-07-21, UNIVERSALIZATION_PLAN.md P1). Real project case: the PDF
        # prints slab-edge and beam vertical formwork as ONE merged number ("Вертикальные поверхности
        # плиты и ж/б балок") with no way to split it. Every downstream estimate line (installation,
        # plywood sheets, timber volume) already reads only the edge+beams SUM, never the two parts
        # separately for money math — so accepting the merged figure directly is safe. When absent,
        # behavior is byte-for-byte identical to before.
        edge_and_beam_formwork_area_combined = first_optional_decimal(
            (input_data, "edge_and_beam_formwork_area_combined_m2"),
            (geometry_in, "edge_and_beam_formwork_area_combined_m2"),
        )
        edge_formwork_area = first_optional_decimal(
            (input_data, "edge_formwork_area_m2"),
            (geometry_in, "edge_formwork_area_m2"),
        )
        beams_formwork_area = first_optional_decimal(
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
    main_delta = delta(main_formwork_area, calculated_main_formwork_area, "main_formwork_area_m2")
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


def calculate_floor_slab_1(input_data: dict[str, Any]) -> dict[str, Any]:
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
        length = d(item["length_m"])
        width = d(item["width_m"])
        height = d(item["height_m"])
        count = d(item.get("count", 1))
        if count < D0:
            raise ValueError("beams.items[].count must be >= 0")
        concrete_volume = length * width * height * count
        formwork_area = length * (width + d(2) * height) * count
        beam_items.append(
            {
                "code": item["code"],
                "name": item["name"],
                "length_m": round_decimal(length),
                "width_m": round_decimal(width),
                "height_m": round_decimal(height),
                "count": round_decimal(count),
                "concrete_volume_m3": round_decimal(concrete_volume),
                "formwork_area_m2": round_decimal(formwork_area),
            }
        )

    beams_total_length = dec_sum([d(item["length_m"]) * d(item["count"]) for item in beam_items])
    calculated_beams_concrete_volume = dec_sum([item["concrete_volume_m3"] for item in beam_items])
    beams_formwork_area = dec_sum([item["formwork_area_m2"] for item in beam_items])

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
        if d(zone["concrete_volume_m3"]) < D0:
            raise ValueError(f"slab_zones.{zone['context']}.concrete_volume_m3 must be >= 0")
    if slab_zones_in:
        total_concrete_volume = dec_sum([d(zone["concrete_volume_m3"]) for zone in slab_zones_in])
    else:
        total_concrete_volume = d(geometry_in["total_concrete_volume_from_spec_m3"])
    slab_thickness = d(geometry_in["slab_thickness_m"])
    slab_concrete_volume = total_concrete_volume - beams_concrete_volume
    calculated_main_formwork_area = slab_concrete_volume / slab_thickness
    calculated_edge_formwork_area = d(geometry_in["slab_edge_perimeter_m"]) * d(geometry_in["edge_formwork_height_m"])
    calculated_beams_formwork_area = beams_formwork_area
    formwork_area_warnings: list[str] = []
    formwork_areas_context = calculate_formwork_areas_context(
        input_data,
        geometry_in,
        calculated_main_formwork_area,
        calculated_edge_formwork_area,
        calculated_beams_formwork_area,
        formwork_area_warnings,
    )
    slab_formwork_area = d(formwork_areas_context["slab_formwork_area_m2"])
    edge_formwork_area_ctx = formwork_areas_context["edge_formwork_area_m2"]
    edge_formwork_area = None if edge_formwork_area_ctx is None else d(edge_formwork_area_ctx)
    beams_formwork_area_ctx = formwork_areas_context["beams_formwork_area_m2"]
    beams_formwork_area = None if beams_formwork_area_ctx is None else d(beams_formwork_area_ctx)
    edge_and_beam_formwork_area = d(formwork_areas_context["edge_and_beam_formwork_area_m2"])

    formwork_rate_context = calculate_formwork_rate_context(rates, slab_formwork_area)
    formwork_rate = d(formwork_rate_context["formwork_rate_per_m2"])
    formwork_delivery_context = calculate_formwork_delivery_context(rates, manual_lines, slab_formwork_area)
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

    concrete_volume_with_waste = total_concrete_volume * d(rates["concrete_waste_coeff"])
    order_concrete_volume = ceil_decimal(concrete_volume_with_waste)
    concrete_delivery_trips = ceil_decimal(concrete_volume_with_waste / d(rates["mixer_capacity_m3"]))

    insulation_context, insulation_warnings = calculate_insulation_context(insulation_in, beams_in, slab_thickness)
    total_insulation_length = d(insulation_context["edge_beam_eps_work_length_m"])
    bottom_slab_insulation_area = d(insulation_context["bottom_slab_eps_work_area_m2"])
    order_eps_volume = d(insulation_context["order_eps_volume_m3_raw"])
    foam_cans_ordered = d(insulation_context["foam_cans_ordered"])

    if beam_items:
        beam_concreting_work_rate_per_m3 = d(rates["beam_concreting_work_rate_per_m3"])
    else:
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
                "Бетонирование балки бетоном марки В22,5 (М300)",
                "м3",
                "work",
                beams_concrete_volume,
                display_decimal(beams_concrete_volume),
                0,
                beams_concrete_volume * beam_concreting_work_rate_per_m3,
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
                d("207.6"),
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
                d("51.9"),
                0,
                bottom_slab_insulation_area * d(rates["bottom_slab_insulation_work_rate_per_m2"]),
                notes=["Стоимость считается от raw 51.92, не от display 51.9."],
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
            "slab_edge_perimeter_m": geometry_in["slab_edge_perimeter_m"],
            "edge_formwork_height_m": geometry_in["edge_formwork_height_m"],
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
            "order_concrete_volume_m3": order_concrete_volume,
            "mixer_capacity_m3": rates["mixer_capacity_m3"],
            "concrete_delivery_trips": concrete_delivery_trips,
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
            "beam_concreting_control_total_by_length": round_money_half_up(beams_total_length * d(2000)),
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
