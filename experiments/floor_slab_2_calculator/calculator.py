from __future__ import annotations

from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP
from typing import Any


D0 = Decimal("0")
D1 = Decimal("1")

REBAR_CATALOG: dict[tuple[str, int], dict[str, Any]] = {
    ("A500", 16): {
        "code": "rebar_a500_d16",
        "name": "Арматура класса А500 диаметром 16 мм",
        "kg_per_meter": Decimal("1.58"),
        "rod_length_m": Decimal("11.7"),
        "price_code": "rebar_a500_d16_m",
    },
    ("A500", 12): {
        "code": "rebar_a500_d12",
        "name": "Арматура класса А500 диаметром 12 мм",
        "kg_per_meter": Decimal("0.888"),
        "rod_length_m": Decimal("11.7"),
        "price_code": "rebar_a500_d12_m",
    },
    ("A500", 10): {
        "code": "rebar_a500_d10",
        "name": "Арматура класса А500 диаметром 10 мм",
        "kg_per_meter": Decimal("0.617"),
        "rod_length_m": Decimal("11.7"),
        "price_code": "rebar_a500_d10_m",
    },
}


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


def rebar_catalog_item(steel_class: Any, diameter_mm: Any) -> dict[str, Any]:
    normalized_steel_class = str(steel_class).upper()
    normalized_diameter = int(diameter_mm)
    catalog_item = REBAR_CATALOG.get((normalized_steel_class, normalized_diameter))
    if catalog_item is None:
        raise ValueError(
            "Unsupported rebar catalog item: "
            f"steel_class={steel_class}, diameter_mm={diameter_mm}"
        )
    return catalog_item


def calculate_rebar_item(
    item: dict[str, Any],
    default_waste_coeff: Any,
    calc_method: str,
) -> dict[str, Any]:
    steel_class = str(item["steel_class"]).upper()
    diameter_mm = int(item["diameter_mm"])
    waste_coeff = d(item.get("waste_coeff", default_waste_coeff))
    unit_price = d(item["unit_price_per_m"])

    if calc_method == "legacy_weight_kg":
        source_weight = d(item["source_weight_kg"])
        kg_per_meter = d(item["kg_per_meter"])
        rod_length = d(item["rod_length_m"])
        code = item["code"]
        name = item["name"]
        price_code = item.get("price_code", f"rebar_{steel_class.lower()}_d{diameter_mm}_m")
        raw_length = source_weight / kg_per_meter
        spec_length = None
        weight_with_waste = source_weight * waste_coeff
    elif calc_method == "spec_length_items":
        if item.get("spec_length_m") is None:
            raise ValueError("rebar_items[*].spec_length_m is required for spec_length_items.")
        catalog_item = rebar_catalog_item(steel_class, diameter_mm)
        spec_length = d(item["spec_length_m"])
        if spec_length < D0:
            raise ValueError("rebar_items[*].spec_length_m must be >= 0.")
        kg_per_meter = d(catalog_item["kg_per_meter"])
        rod_length = d(catalog_item["rod_length_m"])
        code = catalog_item["code"]
        name = catalog_item["name"]
        price_code = catalog_item["price_code"]
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


def calculate_geometry_context(input_data: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    method = input_data.get("formwork_area_calc_method", "legacy_dimensions")
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
        if input_edge_formwork_area is None:
            raise ValueError("edge_formwork_area_m2 is required for spec_formwork_area.")
        edge_formwork_area = input_edge_formwork_area
        if edge_formwork_area < D0:
            raise ValueError("edge_formwork_area_m2 must be >= 0.")
        if input_beams_formwork_area is None:
            beams_formwork_area = D0
            warnings.append(
                "beams_formwork_area_m2 is not provided; floor slab 2 has no beams, assumed 0."
            )
        else:
            beams_formwork_area = input_beams_formwork_area
        if beams_formwork_area < D0:
            raise ValueError("beams_formwork_area_m2 must be >= 0.")

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
        edge_formwork_area_source = "spec_formwork_area"

    formwork_area_delta = None
    if input_slab_area is not None:
        formwork_area_delta = main_formwork_area - input_slab_area
        if abs(formwork_area_delta) > d("0.01"):
            warnings.append("main_formwork_area_m2 differs from slab_area_m2 by more than 0.01 m2.")

    edge_and_beam_formwork_area = edge_formwork_area + beams_formwork_area
    calculated_edge_formwork_area = None
    edge_formwork_area_delta = None
    if slab_edge_perimeter is not None and edge_formwork_height is not None:
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

    geometry_context = calculate_geometry_context(input_data, warnings)
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

    plywood_working_area = d(input_data["plywood_sheet_working_area_m2"])
    edge_plywood_sheets_raw = edge_and_beam_formwork_area / plywood_working_area
    non_multiple_places_area = main_formwork_area * d(input_data["non_multiple_places_coeff"])
    non_multiple_plywood_sheets_raw = non_multiple_places_area / plywood_working_area
    base_plywood_sheets_raw = edge_plywood_sheets_raw + non_multiple_plywood_sheets_raw
    order_plywood_sheets_raw = base_plywood_sheets_raw + d(input_data["plywood_reserve_sheets"])
    plywood_sheets = ceil_decimal(order_plywood_sheets_raw)
    plywood_total_raw = d(plywood_sheets) * d(input_data["plywood_unit_price"])

    timber_volume = edge_and_beam_formwork_area * d(input_data["timber_thickness_m"])
    timber_total_raw = timber_volume * d(input_data["timber_unit_price"])

    rebar_calc_method = input_data.get("rebar_calc_method", "legacy_weight_kg")
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
        "it is not derived from slab_area_m2 * slab thickness."
    )
    concrete_work_total_raw = concrete_placing_volume * d(input_data["concrete_placing_work_unit_price"])
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
    eps100_required_without_waste = edge_insulation_area * d(input_data["eps100_thickness_m"])
    eps100_required_with_waste = eps100_required_without_waste * d(input_data["eps_waste_coeff"])
    eps100_packs_raw = eps100_required_with_waste / d(input_data["eps100_pack_volume_m3"])
    eps100_packs = ceil_decimal(eps100_packs_raw)
    eps100_order_volume = d(eps100_packs) * d(input_data["eps100_pack_volume_m3"])
    eps100_total_raw = eps100_order_volume * d(input_data["eps100_unit_price"])
    edge_insulation_work_total_raw = slab_edge_perimeter * d(input_data["edge_insulation_work_unit_price_per_m"])

    foam_cans_raw = edge_insulation_area / d(input_data["foam_coverage_area_per_can_m2"])
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
        + concrete_material_total_raw
        + concrete_delivery_total_raw
        + concrete_pump_total_raw
        + edge_insulation_work_total_raw
        + eps100_total_raw
        + foam_total_raw
    )
    logistics_total_raw = direct_cost_base_before_addons_raw * d(input_data["logistics_rate"])
    consumables_total_raw = direct_cost_base_before_addons_raw * d(input_data["consumables_rate"])

    rebar_by_code = {item["code"]: item for item in rebar_items}

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
            edge_and_beam_formwork_area,
            notes=[
                "Production quantity uses edge_formwork_area_m2 + beams_formwork_area_m2 from specification."
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
        estimate_line(
            "rebar_a500_d16",
            rebar_by_code["rebar_a500_d16"]["name"],
            "мп",
            "materials",
            rebar_by_code["rebar_a500_d16"]["order_length_m"],
            material_unit_price=rebar_by_code["rebar_a500_d16"]["unit_price_per_m"],
            material_total_raw=rebar_by_code["rebar_a500_d16"]["material_total_raw"],
            price_code=rebar_by_code["rebar_a500_d16"]["price_code"],
        ),
        estimate_line(
            "rebar_a500_d12",
            rebar_by_code["rebar_a500_d12"]["name"],
            "мп",
            "materials",
            rebar_by_code["rebar_a500_d12"]["order_length_m"],
            material_unit_price=rebar_by_code["rebar_a500_d12"]["unit_price_per_m"],
            material_total_raw=rebar_by_code["rebar_a500_d12"]["material_total_raw"],
            price_code=rebar_by_code["rebar_a500_d12"]["price_code"],
        ),
        estimate_line(
            "rebar_a500_d10",
            rebar_by_code["rebar_a500_d10"]["name"],
            "мп",
            "materials",
            rebar_by_code["rebar_a500_d10"]["order_length_m"],
            material_unit_price=rebar_by_code["rebar_a500_d10"]["unit_price_per_m"],
            material_total_raw=rebar_by_code["rebar_a500_d10"]["material_total_raw"],
            price_code=rebar_by_code["rebar_a500_d10"]["price_code"],
        ),
        estimate_line(
            "concrete_placing_work",
            "Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300)",
            "м3",
            "work",
            concrete_placing_volume,
            work_unit_price=input_data["concrete_placing_work_unit_price"],
            work_total_raw=concrete_work_total_raw,
            price_code="concrete_placing_work_m3",
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
            slab_edge_perimeter,
            work_unit_price=input_data["edge_insulation_work_unit_price_per_m"],
            work_total_raw=edge_insulation_work_total_raw,
            notes=[
                "Line name keeps the source wording; for floor slab 2 the calculation covers slab edges only, without beams."
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
            "edge_formwork_area_m2": round_decimal(edge_formwork_area),
            "beams_formwork_area_m2": round_decimal(beams_formwork_area),
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
            "edge_formwork_area_m2": round_decimal(edge_formwork_area),
            "beams_formwork_area_m2": round_decimal(beams_formwork_area),
            "edge_and_beam_formwork_area_m2": round_decimal(edge_and_beam_formwork_area),
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
            "edge_plywood_sheets_raw": round_decimal(edge_plywood_sheets_raw),
            "non_multiple_places_area_m2": round_decimal(non_multiple_places_area),
            "non_multiple_places_plywood_sheets_raw": round_decimal(non_multiple_plywood_sheets_raw),
            "base_plywood_sheets_raw": round_decimal(base_plywood_sheets_raw),
            "order_plywood_sheets_raw": round_decimal(order_plywood_sheets_raw),
            "plywood_sheets": plywood_sheets,
            "timber_volume_m3_raw": round_decimal(timber_volume),
            "timber_volume_m3_display": display_decimal(timber_volume, "0.01"),
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
