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


def calculate_rebar_item(item: dict[str, Any]) -> dict[str, Any]:
    source_weight = d(item.get("source_weight_kg", dec_sum(item.get("source_weight_parts_kg", []))))
    kg_per_meter = d(item["kg_per_meter"])
    waste_coeff = d(item["waste_coeff"])
    rod_length = d(item["rod_length_m"])
    unit_price = d(item["unit_price_per_m"])
    base_length = source_weight / kg_per_meter
    length_with_waste = base_length * waste_coeff
    rods_ordered = ceil_decimal(length_with_waste / rod_length)
    order_length = d(rods_ordered) * rod_length
    material_total_raw = order_length * unit_price
    return {
        "code": item["code"],
        "name": item["name"],
        "steel_class": item["steel_class"],
        "diameter_mm": item["diameter_mm"],
        "source_weight_kg": round_decimal(source_weight),
        "kg_per_meter": round_decimal(kg_per_meter),
        "base_length_m": round_decimal(base_length),
        "waste_coeff": round_decimal(waste_coeff),
        "length_with_waste_m": round_decimal(length_with_waste),
        "weight_with_waste_kg_display": display_decimal(source_weight * waste_coeff),
        "rod_length_m": round_decimal(rod_length),
        "rods_ordered": rods_ordered,
        "order_length_m": round_decimal(order_length),
        "unit_price_per_m": round_decimal(unit_price),
        "material_total_raw": round_decimal(material_total_raw),
        "material_total": round_money_half_up(material_total_raw),
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
) -> dict[str, Any]:
    material_raw = d(material_total_raw)
    work_raw = d(work_total_raw)
    line_raw = material_raw + work_raw
    return {
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


def calculate_floor_slab_1(input_data: dict[str, Any]) -> dict[str, Any]:
    case_meta = input_data["case_meta"]
    geometry_in = input_data["geometry"]
    beams_in = input_data["beams"]
    rates = input_data["rates"]
    rebar_items_in = input_data["rebar_items"]
    insulation_in = input_data["insulation"]
    overheads_in = input_data["overheads"]
    manual_lines = input_data["manual_lines"]

    beam_items = []
    for item in beams_in["items"]:
        length = d(item["length_m"])
        width = d(item["width_m"])
        height = d(item["height_m"])
        concrete_volume = length * width * height
        formwork_area = length * (width + d(2) * height)
        beam_items.append(
            {
                "code": item["code"],
                "name": item["name"],
                "length_m": round_decimal(length),
                "width_m": round_decimal(width),
                "height_m": round_decimal(height),
                "concrete_volume_m3": round_decimal(concrete_volume),
                "formwork_area_m2": round_decimal(formwork_area),
            }
        )

    beams_total_length = dec_sum([item["length_m"] for item in beam_items])
    beams_concrete_volume = dec_sum([item["concrete_volume_m3"] for item in beam_items])
    beams_formwork_area = dec_sum([item["formwork_area_m2"] for item in beam_items])

    total_concrete_volume = d(geometry_in["total_concrete_volume_from_spec_m3"])
    slab_thickness = d(geometry_in["slab_thickness_m"])
    slab_concrete_volume = total_concrete_volume - beams_concrete_volume
    slab_formwork_area = slab_concrete_volume / slab_thickness
    edge_formwork_area = d(geometry_in["slab_edge_perimeter_m"]) * d(geometry_in["edge_formwork_height_m"])
    edge_and_beam_formwork_area = edge_formwork_area + beams_formwork_area

    formwork_quote_total = d(rates["formwork_supplier_quote_total"])
    slab_2_area_context = d(rates["slab_2_formwork_area_for_rate_context_m2"])
    raw_average_rate = formwork_quote_total / (slab_formwork_area + slab_2_area_context)
    formwork_delivery_trucks = (
        d(4)
        if slab_formwork_area > d(180)
        else d(2)
        if slab_formwork_area <= d(150)
        else d(manual_lines["formwork_delivery_trucks_override"])
    )
    formwork_delivery_status = "calculated" if slab_formwork_area <= d(150) or slab_formwork_area > d(180) else "manual_review"

    plywood_working_area = d(rates["plywood_sheet_working_area_m2"])
    non_multiple_coeff = d(rates["non_multiple_places_coeff"])
    reserve_plywood_sheets = d(rates["reserve_plywood_sheets"])
    edge_beam_plywood_raw = edge_and_beam_formwork_area / plywood_working_area
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
    base_timber_volume = edge_and_beam_formwork_area * timber_thickness
    timber_volume = quantized_decimal(base_timber_volume + additional_timber_volume, "0.000000001")

    rebar_items = [calculate_rebar_item(item) for item in rebar_items_in]
    rebar_order_length_total = dec_sum([item["order_length_m"] for item in rebar_items])
    floor_slab_1_rebar_weight_with_waste_raw = dec_sum(
        [
            d(item.get("source_weight_kg", dec_sum(item.get("source_weight_parts_kg", []))))
            * d(item["waste_coeff"])
            for item in rebar_items_in
        ]
    )
    floor_slab_1_rebar_weight_with_waste = d(display_decimal(floor_slab_1_rebar_weight_with_waste_raw, "0.1"))
    delivery_weight = floor_slab_1_rebar_weight_with_waste + d(rates["floor_slab_2_rebar_weight_for_delivery_context_kg"])
    rebar_delivery_trucks = ceil_decimal(delivery_weight / d(rates["max_rebar_delivery_weight_per_truck_kg"]))

    concrete_volume_with_waste = total_concrete_volume * d(rates["concrete_waste_coeff"])
    order_concrete_volume = ceil_decimal(concrete_volume_with_waste)
    concrete_delivery_trips = ceil_decimal(concrete_volume_with_waste / d(rates["mixer_capacity_m3"]))

    slab_outer_edge_length = d(19) * d(2) + (d(7) + d("13.2")) * d(2) + d("3.2") * d(2)
    insulated_beams_length = beams_total_length
    total_insulation_length = slab_outer_edge_length + insulated_beams_length
    slab_edge_insulation_area = slab_outer_edge_length * slab_thickness
    beams_insulation_area = (
        d(7) * d("0.25")
        + d("7.2") * d("0.68")
        + d(9) * d("0.43")
    )
    edge_beam_insulation_area = slab_edge_insulation_area + beams_insulation_area
    eps_thickness = d(insulation_in["eps_thickness_m"])
    edge_beam_eps_volume = edge_beam_insulation_area * eps_thickness
    bottom_slab_eps_volume = d(insulation_in["total_eps_volume_from_spec_m3"]) - edge_beam_eps_volume
    bottom_slab_insulation_area = bottom_slab_eps_volume / eps_thickness
    total_eps_insulation_area = edge_beam_insulation_area + bottom_slab_insulation_area
    required_eps_volume = total_eps_insulation_area * eps_thickness * d(insulation_in["eps_waste_coeff"])
    eps_packs_raw = required_eps_volume / d(insulation_in["eps_pack_volume_m3"])
    eps_packs_ordered = ceil_decimal(eps_packs_raw)
    order_eps_volume = d(eps_packs_ordered) * d(insulation_in["eps_pack_volume_m3"])
    foam_cans_raw = total_eps_insulation_area / d(insulation_in["foam_coverage_m2_per_can"])
    foam_cans_ordered = ceil_decimal(foam_cans_raw)

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
            slab_formwork_area * d(rates["formwork_rate_per_m2"]),
        ),
        estimate_line(
            "formwork_delivery_return_manipulator",
            "Доставка, вывоз опалубки манипулятором",
            "маш",
            "logistics_machinery",
            formwork_delivery_trucks,
            formwork_delivery_trucks,
            formwork_delivery_trucks * d(rates["formwork_delivery_rate_per_trip"]),
            notes=["<=150 м2: 1 привоз + 1 вывоз; >180 м2: 2 привоз + 2 вывоз; 150-180 м2: manual_review."],
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
        ),
        estimate_line(
            "formwork_consumables",
            "Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки)",
            "-",
            "materials_consumables",
            1,
            1,
            slab_formwork_area * d(rates["formwork_consumables_rate_per_m2"]),
        ),
        estimate_line(
            "edge_beam_formwork_installation_control",
            "Монтаж опалубки из доски 50 мм и фанеры для устройства балок, для отбортовки плиты",
            "м2",
            "zero_control_line",
            edge_and_beam_formwork_area,
            display_decimal(edge_and_beam_formwork_area),
        ),
        estimate_line(
            "plywood_fk_18mm_for_edges_and_non_multiple_places",
            "Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов",
            "шт",
            "materials",
            order_plywood_sheets,
            order_plywood_sheets,
            d(order_plywood_sheets) * d(rates["plywood_unit_price"]),
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
            )
        )

    lines.extend(
        [
            estimate_line(
                "rebar_metal_delivery",
                "Доставка арматуры, металла",
                "маш",
                "logistics_machinery",
                rebar_delivery_trucks,
                rebar_delivery_trucks,
                d(rebar_delivery_trucks) * d(rates["rebar_delivery_rate_per_truck"]),
                notes=["В будущем box_calculator доставка металла должна считаться один раз по общему весу металла коробки."],
            ),
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
            ),
            estimate_line(
                "beam_concreting_work",
                "Бетонирование балки бетоном марки В22,5 (М300)",
                "м3",
                "work",
                beams_concrete_volume,
                display_decimal(beams_concrete_volume),
                0,
                beams_concrete_volume * d(rates["beam_concreting_work_rate_per_m3"]),
            ),
            estimate_line(
                "concrete_b22_5_m300_material",
                "Бетон марки В22,5 (М300)",
                "м3",
                "materials",
                order_concrete_volume,
                order_concrete_volume,
                d(order_concrete_volume) * d(rates["concrete_unit_price_per_m3"]),
            ),
            estimate_line(
                "concrete_delivery",
                "Доставка бетона до объекта",
                "рейс",
                "logistics_machinery",
                concrete_delivery_trips,
                concrete_delivery_trips,
                d(concrete_delivery_trips) * d(rates["concrete_delivery_rate_per_trip"]),
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
            ),
            estimate_line(
                "eps_glue_foam",
                "Клей-пена для ЭППС",
                "баллон",
                "materials_consumables",
                foam_cans_ordered,
                foam_cans_ordered,
                d(foam_cans_ordered) * d(insulation_in["foam_unit_price_per_can"]),
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
            ),
        ]
    )

    materials_total = sum(line["material_total"] for line in lines)
    works_total = sum(line["work_total"] for line in lines)
    section_total = materials_total + works_total

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
            "total_formwork_area_m2": round_decimal(beams_formwork_area),
        },
        "formwork": {
            "edge_formwork_area_m2": round_decimal(edge_formwork_area),
            "edge_and_beam_formwork_area_m2": round_decimal(edge_and_beam_formwork_area),
            "supplier_quote_total": round_decimal(formwork_quote_total),
            "slab_2_formwork_area_for_rate_context_m2": round_decimal(slab_2_area_context),
            "raw_average_rate": round_decimal(raw_average_rate, "0.0000001"),
            "excel_rate_per_m2": rates["formwork_rate_per_m2"],
            "formwork_delivery_trucks": round_decimal(formwork_delivery_trucks),
            "formwork_delivery_status": formwork_delivery_status,
        },
        "plywood_and_timber": {
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
            "items": rebar_items,
            "rebar_frame_assembly_quantity_m": round_decimal(rebar_order_length_total),
            "floor_slab_1_rebar_weight_with_waste_kg": display_decimal(floor_slab_1_rebar_weight_with_waste, "0.1"),
            "floor_slab_2_rebar_weight_for_delivery_context_kg": rates["floor_slab_2_rebar_weight_for_delivery_context_kg"],
            "total_delivery_weight_kg_raw": round_decimal(delivery_weight),
            "total_delivery_weight_kg_display": ceil_decimal(delivery_weight),
            "max_weight_per_truck_kg": rates["max_rebar_delivery_weight_per_truck_kg"],
            "trucks_ordered": rebar_delivery_trucks,
        },
        "concrete": {
            "total_project_concrete_volume_m3": round_decimal(total_concrete_volume),
            "concrete_volume_with_waste_m3_raw": round_decimal(concrete_volume_with_waste),
            "concrete_volume_with_waste_m3_display": display_decimal(concrete_volume_with_waste),
            "order_concrete_volume_m3": order_concrete_volume,
            "mixer_capacity_m3": rates["mixer_capacity_m3"],
            "concrete_delivery_trips": concrete_delivery_trips,
        },
        "insulation": {
            "slab_outer_edge_length_m": round_decimal(slab_outer_edge_length),
            "insulated_beams_total_length_m": round_decimal(insulated_beams_length),
            "total_insulation_length_m": round_decimal(total_insulation_length),
            "slab_edge_insulation_area_m2": round_decimal(slab_edge_insulation_area),
            "beams_insulation_area_m2": round_decimal(beams_insulation_area),
            "edge_and_beam_insulation_area_m2": round_decimal(edge_beam_insulation_area),
            "edge_and_beam_eps_volume_m3": round_decimal(edge_beam_eps_volume),
            "bottom_slab_eps_volume_m3": round_decimal(bottom_slab_eps_volume),
            "bottom_slab_insulation_area_m2_raw": round_decimal(bottom_slab_insulation_area),
            "total_insulation_area_m2": round_decimal(total_eps_insulation_area),
            "required_eps_volume_m3_raw": round_decimal(required_eps_volume),
            "eps_packs_raw": round_decimal(eps_packs_raw),
            "eps_packs_ordered": eps_packs_ordered,
            "order_eps_volume_m3_raw": round_decimal(order_eps_volume),
            "foam_cans_raw": round_decimal(foam_cans_raw),
            "foam_cans_ordered": foam_cans_ordered,
        },
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
        "warnings": [],
    }
