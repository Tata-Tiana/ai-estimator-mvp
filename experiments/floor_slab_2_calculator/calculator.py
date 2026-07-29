from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP
from typing import Any


D0 = Decimal("0")
D1 = Decimal("1")

def d(value: Any) -> Decimal:
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


def calculate_rebar_item(
    item: dict[str, Any],
    default_waste_coeff: Any,
    calc_method: str,
) -> dict[str, Any]:
    steel_class = str(item["steel_class"]).upper()
    diameter_mm = int(item["diameter_mm"])
    waste_coeff = d(item.get("waste_coeff", default_waste_coeff))
    unit_price = d(item["unit_price_per_m"])
    kg_per_meter = d(item["kg_per_meter"])
    rod_length = d(item["rod_length_m"])
    code = item.get("code", make_rebar_code(steel_class, diameter_mm))
    name = item.get("name", make_rebar_name(steel_class, diameter_mm))
    price_code = item.get("price_code", f"rebar_{steel_class.lower()}_d{diameter_mm}_m")

    if calc_method == "legacy_weight_kg":
        source_weight = d(item["source_weight_kg"])
        raw_length = source_weight / kg_per_meter
        spec_length = None
        weight_with_waste = source_weight * waste_coeff
    elif calc_method == "spec_length_items":
        if item.get("spec_length_m") is None:
            raise ValueError("rebar_items[*].spec_length_m is required for spec_length_items.")
        spec_length = d(item["spec_length_m"])
        if spec_length < D0:
            raise ValueError("rebar_items[*].spec_length_m must be >= 0.")
        source_weight = None
        raw_length = spec_length
        weight_with_waste = None
    else:
        raise ValueError("rebar_calc_method must be either legacy_weight_kg or spec_length_items.")

    if kg_per_meter <= D0:
        raise ValueError("rebar kg_per_meter must be > 0.")
    if rod_length <= D0:
        raise ValueError("rebar rod_length_m must be > 0.")
    if unit_price < D0:
        raise ValueError("rebar unit_price_per_m must be >= 0.")

    length_with_waste = raw_length * waste_coeff
    raw_rods = length_with_waste / rod_length
    rods = ceil_decimal(raw_rods)
    order_length = d(rods) * rod_length
    order_weight = order_length * kg_per_meter
    material_total_raw = order_length * unit_price

    result = {
        "code": code,
        "name": name,
        "steel_class": steel_class,
        "diameter_mm": diameter_mm,
        "kg_per_meter": round_decimal(kg_per_meter),
        "raw_length_m": round_decimal(raw_length),
        "waste_coeff": round_decimal(waste_coeff),
        "length_with_waste_m": round_decimal(length_with_waste),
        "rod_length_m": round_decimal(rod_length),
        "raw_rods": round_decimal(raw_rods),
        "rods": rods,
        "order_length_m": round_decimal(order_length),
        "order_weight_kg": round_decimal(order_weight),
        "unit_price_per_m": round_decimal(unit_price),
        "price_code": price_code,
        "material_total_raw": round_decimal(material_total_raw),
        "material_total": round_money_half_up(material_total_raw),
    }
    if source_weight is not None:
        result["source_weight_kg"] = round_decimal(source_weight)
    if spec_length is not None:
        result["spec_length_m"] = round_decimal(spec_length)
    if weight_with_waste is not None:
        result["weight_with_waste_kg"] = round_decimal(weight_with_waste)
    return result


def round_optional(value: Any, places: str = "0.000001") -> float | None:
    return None if value is None else round_decimal(value, places)


def calculate_beam_items(
    beams_in: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], Decimal, Decimal, Decimal, Decimal]:
    items_in = (beams_in or {}).get("items") or []
    beam_items: list[dict[str, Any]] = []
    for item in items_in:
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


def calculate_formwork_delivery_context(
    input_data: dict[str, Any],
    main_formwork_area: Decimal,
) -> dict[str, Any]:
    method = input_data.get("formwork_delivery_calc_method", "area_threshold")
    threshold = d(input_data.get("formwork_delivery_threshold_m2", 180))
    manual_lines = input_data.get("manual_lines") or {}

    if method == "area_threshold":
        if main_formwork_area < D0:
            raise ValueError("main_formwork_area_m2 must be >= 0 for area_threshold.")
        if main_formwork_area <= threshold:
            trips = 2
            breakdown = "1 привоз + 1 вывоз"
        else:
            trips = 4
            breakdown = "2 привоза + 2 вывоза"
        status = "calculated"
    elif method == "manual_override":
        override = manual_lines.get("formwork_delivery_trips_override", input_data.get("formwork_delivery_trips"))
        if override is None:
            raise ValueError(
                "manual_lines.formwork_delivery_trips_override is required for manual_override."
            )
        trips_decimal = d(override)
        if trips_decimal < D0:
            raise ValueError("manual_lines.formwork_delivery_trips_override must be >= 0.")
        trips = trips_decimal
        breakdown = "manual override"
        status = "manual_override"
    else:
        raise ValueError(
            "formwork_delivery_calc_method must be either area_threshold or manual_override."
        )

    unit_price = d(input_data["formwork_delivery_unit_price"])
    if unit_price < D0:
        raise ValueError("formwork_delivery_unit_price must be >= 0.")

    return {
        "formwork_delivery_calc_method": method,
        "formwork_delivery_area_source_m2": main_formwork_area,
        "formwork_delivery_threshold_m2": threshold,
        "formwork_delivery_trips": trips,
        "formwork_delivery_breakdown": breakdown,
        "formwork_delivery_status": status,
        "formwork_delivery_unit_price": unit_price,
        "formwork_delivery_total_raw": d(trips) * unit_price,
        "formwork_delivery_note": (
            "До 180 м2 включительно: 1 привоз + 1 вывоз = 2 рейса; "
            "более 180 м2: 2 привоза + 2 вывоза = 4 рейса."
        ),
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


def calculate_floor_slab_2(input_data: dict[str, Any]) -> dict[str, Any]:
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
    formwork_rental_total_raw = main_formwork_area * formwork_rate

    formwork_delivery = calculate_formwork_delivery_context(input_data, main_formwork_area)
    formwork_delivery_total_raw = d(formwork_delivery["formwork_delivery_total_raw"])
    crane_total_raw = d(input_data["crane_shifts"]) * d(input_data["crane_unit_price"])
    formwork_consumables_total_raw = main_formwork_area * d(input_data["formwork_consumables_rate_per_m2"])

    # beams_bottom_formwork_area_m2: additive, real-project case (2026-07-26, ported from floor_slab_1)
    # — a project can print the beam's HORIZONTAL (bottom) formwork area as its own separate line,
    # distinct from both the slab's horizontal area (main_formwork_area_m2) and the combined slab+beam
    # VERTICAL area (edge_and_beam_formwork_area). Feeds both plywood/timber material AND the edge+beam
    # installation work quantity — confirmed against real project smetas that the installation work
    # line's own quantity already includes this area, not just the material. When absent, behavior is
    # byte-for-byte identical to before.
    beams_bottom_formwork_area = d(input_data.get("beams_bottom_formwork_area_m2") or 0)
    edge_beam_formwork_area_for_materials = edge_and_beam_formwork_area + beams_bottom_formwork_area

    plywood_working_area = d(input_data["plywood_sheet_working_area_m2"])
    edge_plywood_sheets_raw = edge_beam_formwork_area_for_materials / plywood_working_area
    non_multiple_places_area = main_formwork_area * d(input_data["non_multiple_places_coeff"])
    non_multiple_plywood_sheets_raw = non_multiple_places_area / plywood_working_area
    base_plywood_sheets_raw = edge_plywood_sheets_raw + non_multiple_plywood_sheets_raw
    order_plywood_sheets_raw = base_plywood_sheets_raw + d(input_data["plywood_reserve_sheets"])
    plywood_sheets = ceil_decimal(order_plywood_sheets_raw)
    plywood_total_raw = d(plywood_sheets) * d(input_data["plywood_unit_price"])

    timber_volume = edge_beam_formwork_area_for_materials * d(input_data["timber_thickness_m"])
    timber_total_raw = timber_volume * d(input_data["timber_unit_price"])

    rebar_calc_method = input_data.get("rebar_calc_method")
    if rebar_calc_method not in {"legacy_weight_kg", "spec_length_items"}:
        raise ValueError("rebar_calc_method must be either legacy_weight_kg or spec_length_items.")
    rebar_items = [
        calculate_rebar_item(item, input_data["rebar_waste_coeff"], rebar_calc_method)
        for item in input_data["rebar_items"]
    ]
    total_rebar_order_length = sum((d(item["order_length_m"]) for item in rebar_items), D0)
    total_rebar_order_weight = sum((d(item["order_weight_kg"]) for item in rebar_items), D0)
    total_rebar_weight_with_waste = sum(
        (d(item.get("weight_with_waste_kg", item["order_weight_kg"])) for item in rebar_items),
        D0,
    )

    concrete_placing_volume = d(input_data["concrete_placing_volume_m3"])
    warnings.append(
        "concrete_placing_volume_m3 is a manual/project quantity for this case; "
        "it is not derived from slab_area_m2 * slab thickness. If beams exist, this total "
        "is expected to already include beam concrete, same as floor_slab_1_calculator."
    )
    slab_concrete_volume = concrete_placing_volume - beams_items_concrete_volume
    if slab_concrete_volume < D0:
        raise ValueError("beams.items concrete volume exceeds concrete_placing_volume_m3")
    concrete_work_total_raw = slab_concrete_volume * d(input_data["concrete_placing_work_unit_price"])
    if beam_items:
        beam_concreting_work_unit_price = d(input_data["beam_concreting_work_unit_price"])
    else:
        beam_concreting_work_unit_price = D0
    beam_concrete_work_total_raw = beams_items_total_length * beam_concreting_work_unit_price
    concrete_volume_with_waste = concrete_placing_volume * d(input_data["concrete_waste_coeff"])
    concrete_order_volume = ceil_to_step(concrete_volume_with_waste, input_data["concrete_round_step_m3"])
    concrete_material_total_raw = concrete_order_volume * d(input_data["concrete_unit_price"])
    concrete_delivery_trips_raw = concrete_order_volume / d(input_data["concrete_mixer_volume_m3"])
    concrete_delivery_trips = ceil_decimal(concrete_delivery_trips_raw)
    concrete_delivery_total_raw = d(concrete_delivery_trips) * d(input_data["concrete_delivery_unit_price"])
    concrete_pump_total_raw = d(input_data["concrete_pump_shifts"]) * d(input_data["concrete_pump_unit_price"])

    edge_insulation_height = d(input_data["edge_insulation_height_m"])
    if edge_insulation_height <= D0:
        raise ValueError("edge_insulation_height_m must be > 0.")
    edge_insulation_height_source = "specification"
    warnings.append(
        "edge_insulation_height_m = 0.18 m is confirmed by specification; "
        "200 mm in the section title is considered a naming error."
    )
    edge_insulation_area = slab_edge_perimeter * edge_insulation_height
    edge_and_beam_insulation_area = edge_insulation_area + beams_items_eps_material_area
    total_insulation_length = slab_edge_perimeter + beams_items_eps_work_length
    eps100_required_without_waste = edge_and_beam_insulation_area * d(input_data["eps100_thickness_m"])
    eps100_required_with_waste = eps100_required_without_waste * d(input_data["eps_waste_coeff"])
    eps100_packs_raw = eps100_required_with_waste / d(input_data["eps100_pack_volume_m3"])
    eps100_packs = ceil_decimal(eps100_packs_raw)
    eps100_order_volume = d(eps100_packs) * d(input_data["eps100_pack_volume_m3"])
    eps100_total_raw = eps100_order_volume * d(input_data["eps100_unit_price"])
    edge_insulation_work_total_raw = total_insulation_length * d(input_data["edge_insulation_work_unit_price_per_m"])

    foam_cans_raw = edge_and_beam_insulation_area / d(input_data["foam_coverage_area_per_can_m2"])
    foam_cans_ordered = max(int(input_data["foam_min_cans"]), ceil_decimal(foam_cans_raw))
    foam_total_raw = d(foam_cans_ordered) * d(input_data["foam_can_unit_price"])

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
        + eps100_total_raw
        + foam_total_raw
    )
    logistics_total_raw = direct_cost_base_before_addons_raw * d(input_data["logistics_rate"])
    consumables_total_raw = direct_cost_base_before_addons_raw * d(input_data["consumables_rate"])

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
            formwork_delivery["formwork_delivery_trips"],
            material_unit_price=formwork_delivery["formwork_delivery_unit_price"],
            material_total_raw=formwork_delivery_total_raw,
            notes=[formwork_delivery["formwork_delivery_note"]],
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
                "Quantity is slab_edge_perimeter_m plus the sum of beams.items length_m * count; "
                "equals slab_edge_perimeter_m alone when no beams.items are given."
            ],
            price_code="edge_insulation_work_m",
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
            "formwork_delivery_calc_method": formwork_delivery["formwork_delivery_calc_method"],
            "formwork_delivery_area_source_m2": round_decimal(
                formwork_delivery["formwork_delivery_area_source_m2"]
            ),
            "formwork_delivery_threshold_m2": round_decimal(
                formwork_delivery["formwork_delivery_threshold_m2"]
            ),
            "formwork_delivery_trips": round_decimal(formwork_delivery["formwork_delivery_trips"]),
            "formwork_delivery_breakdown": formwork_delivery["formwork_delivery_breakdown"],
            "formwork_delivery_status": formwork_delivery["formwork_delivery_status"],
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
            "rebar_calc_method": rebar_calc_method,
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

    return {
        "project_name": input_data["project_name"],
        "section": "floor_slab_2",
        "section_title": "Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 2-го этажа на отм. +4.680 (200мм)",
        "inputs": input_data,
        "calculation_blocks": calculation_blocks,
        "estimate_lines": lines,
        "totals": totals,
        "warnings": warnings,
    }
