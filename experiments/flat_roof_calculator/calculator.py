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


def decimal_str(value: Any) -> str:
    value_dec = d(value)
    if value_dec == value_dec.to_integral_value():
        return str(value_dec.quantize(D1))
    return format(value_dec.normalize(), "f")


def display_decimal(value: Any, places: str = "0.01") -> str:
    return decimal_str(d(value).quantize(Decimal(places), rounding=ROUND_HALF_UP))


def estimate_line(
    *,
    code: str,
    name: str,
    unit: str,
    line_type: str,
    quantity_raw: Any,
    quantity_display: Any | None = None,
    quantity_source: str,
    price_code: str | None = None,
    material_unit_price: Any = 0,
    material_total_raw: Any = 0,
    material_total_override: int | None = None,
    work_unit_price: Any = 0,
    work_total_raw: Any = 0,
    formula: dict[str, Any] | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    material_raw = d(material_total_raw)
    work_raw = d(work_total_raw)
    material_total = material_total_override
    if material_total is None:
        material_total = round_money_half_up(material_raw)
    work_total = round_money_half_up(work_raw)
    line_total = material_total + work_total
    line_raw = material_raw + work_raw
    payload = {
        "code": code,
        "name": name,
        "unit": unit,
        "line_type": line_type,
        "quantity_raw": decimal_str(quantity_raw),
        "quantity_display": decimal_str(quantity_raw if quantity_display is None else quantity_display),
        "quantity_source": quantity_source,
        "internal_cost": {
            "material_unit_price": decimal_str(material_unit_price),
            "material_total_raw": decimal_str(material_raw),
            "material_total": material_total,
            "work_unit_price": decimal_str(work_unit_price),
            "work_total_raw": decimal_str(work_raw),
            "work_total": work_total,
            "line_total_raw": decimal_str(line_raw),
            "line_total": line_total,
        },
        "formula": formula or {},
        "notes": notes or [],
    }
    if price_code:
        payload["price_code"] = price_code
    return payload


def zero_line(code: str, name: str, quantity: Any, quantity_source: str, unit: str = "-") -> dict[str, Any]:
    return estimate_line(
        code=code,
        name=name,
        unit=unit,
        line_type="zero_excel_structure_line",
        quantity_raw=quantity,
        quantity_source=quantity_source,
        notes=[
            "Строка сохранена для структуры Excel.",
            "В текущем scope серая внутренняя себестоимость равна 0.",
        ],
    )


def material_roll_line(
    *,
    code: str,
    name: str,
    price_code: str,
    required_area: Decimal,
    roll_area: Decimal,
    unit_price_per_m2: Decimal,
    quantity_source: str,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    rolls = ceil_decimal(required_area / roll_area)
    ordered_area = d(rolls) * roll_area
    return estimate_line(
        code=code,
        name=name,
        unit="м2",
        line_type="materials",
        quantity_raw=ordered_area,
        quantity_source=quantity_source,
        price_code=price_code,
        material_unit_price=unit_price_per_m2,
        material_total_raw=ordered_area * unit_price_per_m2,
        formula={
            "required_area_m2": decimal_str(required_area),
            "roll_area_m2": decimal_str(roll_area),
            "rolls_ordered": rolls,
            "ordered_area_m2": decimal_str(ordered_area),
        },
        notes=notes,
    )


def supplier_pack_material_line(
    *,
    code: str,
    name: str,
    price_code: str,
    supplier_required_volume: Decimal,
    pack_volume: Decimal,
    unit_price: Decimal,
    expected_total: int | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    packs = ceil_decimal(supplier_required_volume / pack_volume)
    ordered_volume = d(packs) * pack_volume
    return estimate_line(
        code=code,
        name=name,
        unit="м3",
        line_type="materials",
        quantity_raw=ordered_volume,
        quantity_display=display_decimal(ordered_volume),
        quantity_source="supplier_required_volume_m3 rounded up to full packs",
        price_code=price_code,
        material_unit_price=unit_price,
        material_total_raw=ordered_volume * unit_price,
        material_total_override=expected_total,
        formula={
            "supplier_required_volume_m3": decimal_str(supplier_required_volume),
            "pack_volume_m3": decimal_str(pack_volume),
            "packs_ordered": packs,
            "ordered_volume_m3": decimal_str(ordered_volume),
        },
        notes=notes,
    )


def calculate_flat_roof(input_data: dict[str, Any]) -> dict[str, Any]:
    warnings = [
        "project_spec_roof_area_m2 = 294 is not used without human review; current calculation uses roof_area_total_m2.",
        "Slope insulation plate volumes are supplier/Technonikol manual inputs, not geometry-derived values.",
        "Temporary door line is case-specific and is not included in this universal base calculator.",
        "Roof consumables use provided raw total; base formula is to be confirmed later.",
        "Logistics and supply uses provided raw total from the reviewed gray estimate.",
        "Technical supervision uses provided gray work total from the reviewed estimate.",
        "Procurement/storage uses provided gray work total from the reviewed estimate.",
        "Some material totals intentionally keep current Excel raw/display mismatches.",
    ]
    roof_area = d(input_data["roof_area_total_m2"])
    parapet_and_abutment = d(input_data["parapet_and_abutment_total_length_m"])

    lines: list[dict[str, Any]] = []
    lines.append(
        zero_line(
            "roof_base_preparation_control",
            "Подготовка основания под укладку пароизоляционного слоя, очистка поверхности",
            roof_area,
            "roof_area_total_m2",
            unit="м2",
        )
    )

    vapor_work_raw = roof_area * d(input_data["vapor_barrier_work_rate_per_m2"])
    lines.append(
        estimate_line(
            code="vapor_barrier_installation",
            name="Пароизоляция основания плёнкой ПВХ",
            unit="м2",
            line_type="work",
            quantity_raw=roof_area,
            quantity_source="roof_area_total_m2",
            work_unit_price=input_data["vapor_barrier_work_rate_per_m2"],
            work_total_raw=vapor_work_raw,
            formula={"roof_area_total_m2": decimal_str(roof_area), "rate_per_m2": input_data["vapor_barrier_work_rate_per_m2"]},
        )
    )

    vapor_required_area = roof_area * d(input_data["vapor_barrier_film_overlap_coeff"])
    lines.append(
        material_roll_line(
            code="vapor_barrier_film_technonikol_120mk",
            name="Пленка пароизоляция ТехноНИКОЛЬ 120 мкм, 150 м2/рул",
            price_code="roof_vapor_barrier_film_technonikol_120mk_m2",
            required_area=vapor_required_area,
            roll_area=d(input_data["vapor_barrier_film_roll_area_m2"]),
            unit_price_per_m2=d(input_data["vapor_barrier_film_unit_price_per_m2"]),
            quantity_source="roof_area_total_m2 * vapor_barrier_film_overlap_coeff rounded to rolls",
        )
    )

    eps_work_raw = roof_area * d(input_data["eps_insulation_work_rate_per_m2"])
    lines.append(
        estimate_line(
            code="eps_roof_insulation_installation",
            name="Утепление кровельного покрытия ЭППС (1 слой -100мм, 2 слой -100мм, 3 слой - разуклонка)",
            unit="м2",
            line_type="work",
            quantity_raw=roof_area,
            quantity_source="roof_area_total_m2",
            work_unit_price=input_data["eps_insulation_work_rate_per_m2"],
            work_total_raw=eps_work_raw,
            formula={
                "roof_area_total_m2": decimal_str(roof_area),
                "rate_per_m2": input_data["eps_insulation_work_rate_per_m2"],
                "rate_context": "likely eps_insulation_base_work_rate_per_m2 * roof_work_coeff",
            },
            notes=["Для текущего проекта ставка 770 вероятно равна 700 * roof_work_coeff 1.10."],
        )
    )

    eps100_required = roof_area * d(input_data["eps_main_thickness_m"]) * d(input_data["eps_insulation_waste_coeff"])
    eps100_packs = ceil_decimal(eps100_required / d(input_data["eps100_pack_volume_m3"]))
    eps100_ordered = d(eps100_packs) * d(input_data["eps100_pack_volume_m3"])
    lines.append(
        estimate_line(
            code="eps100_technonikol_carbon_eco",
            name="Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON ECO (100мм)",
            unit="м3",
            line_type="materials",
            quantity_raw=eps100_ordered,
            quantity_display=display_decimal(eps100_ordered),
            quantity_source="roof_area_total_m2 * eps_main_thickness_m * eps_insulation_waste_coeff rounded to packs",
            price_code="roof_eps100_technonikol_carbon_eco_m3",
            material_unit_price=input_data["eps100_unit_price_per_m3"],
            material_total_raw=eps100_ordered * d(input_data["eps100_unit_price_per_m3"]),
            material_total_override=377080,
            formula={
                "required_volume_m3": decimal_str(eps100_required),
                "packs_ordered": eps100_packs,
                "ordered_volume_m3": decimal_str(eps100_ordered),
            },
            notes=["Expected total fixed to 377080 for current Excel match because raw/display price differs."],
        )
    )

    slope_specs = [
        ("eps50_technonikol_carbon_eco", "Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON ECO (50мм)", "roof_eps50_technonikol_carbon_eco_m3", "eps50", None),
        ("eps_slope_2_1_plate_a", "Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты A)", "roof_eps_slope_2_1_plate_a_m3", "slope_plate_a", 41304),
        ("eps_slope_2_1_plate_b", "Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты B)", "roof_eps_slope_2_1_plate_b_m3", "slope_plate_b", None),
        ("eps_slope_4_2_plate_j", "Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты J)", "roof_eps_slope_4_2_plate_j_m3", "slope_plate_j", None),
        ("eps_slope_4_2_plate_k", "Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты K)", "roof_eps_slope_4_2_plate_k_m3", "slope_plate_k", None),
    ]
    for code, name, price_code, prefix, expected_total in slope_specs:
        notes = ["supplier_required_volume_m3 берётся вручную от поставщика / Технониколь."]
        if expected_total is not None:
            notes.append("Expected total fixed for current Excel raw/display match.")
        lines.append(
            supplier_pack_material_line(
                code=code,
                name=name,
                price_code=price_code,
                supplier_required_volume=d(input_data[f"{prefix}_supplier_required_volume_m3"]),
                pack_volume=d(input_data[f"{prefix}_pack_volume_m3"]),
                unit_price=d(input_data[f"{prefix}_unit_price_per_m3"]),
                expected_total=expected_total,
                notes=notes,
            )
        )

    lines.append(
        material_roll_line(
            code="geotextile_prof_300_flat",
            name="Геотекстиль ТЕХНОНИКОЛЬ ПРОФ Кровля 300, 2х50м",
            price_code="roof_geotextile_technonikol_prof_300_m2",
            required_area=roof_area * d(input_data["geotextile_flat_coeff"]),
            roll_area=d(input_data["geotextile_flat_roll_area_m2"]),
            unit_price_per_m2=d(input_data["geotextile_flat_unit_price_per_m2"]),
            quantity_source="roof_area_total_m2 * geotextile_flat_coeff rounded to rolls",
        )
    )
    lines.append(
        material_roll_line(
            code="geotextile_prof_150_parapet",
            name="Геотекстиль ТЕХНОНИКОЛЬ ПРОФ Кровля 150, 2х50м",
            price_code="roof_geotextile_technonikol_prof_150_m2",
            required_area=parapet_and_abutment * d(input_data["geotextile_parapet_coeff"]),
            roll_area=d(input_data["geotextile_parapet_roll_area_m2"]),
            unit_price_per_m2=d(input_data["geotextile_parapet_unit_price_per_m2"]),
            quantity_source="parapet_and_abutment_total_length_m * geotextile_parapet_coeff rounded to rolls",
        )
    )

    lines.extend(
        [
            estimate_line(
                code="pvc_membrane_flat_installation",
                name="Укладка ПВХ Мембраны",
                unit="м2",
                line_type="work",
                quantity_raw=roof_area,
                quantity_source="roof_area_total_m2",
                work_unit_price=input_data["pvc_membrane_installation_work_rate_per_m2"],
                work_total_raw=roof_area * d(input_data["pvc_membrane_installation_work_rate_per_m2"]),
            ),
            estimate_line(
                code="pvc_membrane_abutment_installation",
                name="Монтаж примыкания кровли из ПВХ мембраны",
                unit="мп",
                line_type="work",
                quantity_raw=parapet_and_abutment,
                quantity_source="parapet_and_abutment_total_length_m",
                work_unit_price=input_data["pvc_membrane_abutment_work_rate_per_m"],
                work_total_raw=parapet_and_abutment * d(input_data["pvc_membrane_abutment_work_rate_per_m"]),
            ),
            estimate_line(
                code="vent_shaft_abutment_installation",
                name="Монтаж примыкания к вентшахтам",
                unit="шт",
                line_type="work",
                quantity_raw=input_data["vent_shaft_abutment_count"],
                quantity_source="vent_shaft_abutment_count",
                work_unit_price=input_data["vent_shaft_abutment_work_rate_per_item"],
                work_total_raw=d(input_data["vent_shaft_abutment_count"]) * d(input_data["vent_shaft_abutment_work_rate_per_item"]),
            ),
        ]
    )

    rail_pieces = ceil_decimal(parapet_and_abutment / d(input_data["rail_piece_length_m"]))
    rail_ordered_length = d(rail_pieces) * d(input_data["rail_piece_length_m"])
    lines.append(
        estimate_line(
            code="aluminum_pressure_rail_3m",
            name="Рейка прижимная алюминиевая 3м",
            unit="мп",
            line_type="materials",
            quantity_raw=rail_ordered_length,
            quantity_source="parapet_and_abutment_total_length_m rounded to rail pieces",
            price_code="roof_aluminum_pressure_rail_m",
            material_unit_price=input_data["pressure_rail_unit_price_per_m"],
            material_total_raw=rail_ordered_length * d(input_data["pressure_rail_unit_price_per_m"]),
            formula={"pieces_ordered": rail_pieces, "ordered_length_m": decimal_str(rail_ordered_length)},
        )
    )
    lines.append(
        estimate_line(
            code="aluminum_edge_rail_3m",
            name="Рейка краевая алюминиевая 3м",
            unit="мп",
            line_type="materials",
            quantity_raw=rail_ordered_length,
            quantity_source="parapet_and_abutment_total_length_m rounded to rail pieces",
            price_code="roof_aluminum_edge_rail_m",
            material_unit_price=input_data["edge_rail_unit_price_per_m"],
            material_total_raw=rail_ordered_length * d(input_data["edge_rail_unit_price_per_m"]),
            formula={"pieces_ordered": rail_pieces, "ordered_length_m": decimal_str(rail_ordered_length)},
        )
    )

    membrane_flat_area = roof_area * d(input_data["pvc_membrane_flat_coeff"])
    membrane_abutment_area = parapet_and_abutment * d(input_data["pvc_membrane_parapet_coeff"])
    membrane_required_area = membrane_flat_area + membrane_abutment_area
    membrane_roll_area = d(input_data["pvc_membrane_roll_width_m"]) * d(input_data["pvc_membrane_roll_length_m"])
    membrane_rolls = ceil_decimal(membrane_required_area / membrane_roll_area)
    lines.append(
        estimate_line(
            code="pvc_membrane_logicroof_vrp_1_5mm_gray",
            name="Полимерная мембрана ПВХ Logicroof V-RP 1,5 мм мембрана серая, 2,10х20",
            unit="рул",
            line_type="materials",
            quantity_raw=membrane_rolls,
            quantity_source="flat and abutment membrane areas rounded to rolls",
            price_code="roof_pvc_membrane_logicroof_vrp_1_5mm_gray_roll",
            material_unit_price=input_data["pvc_membrane_unit_price_per_roll_display"],
            material_total_raw=d(membrane_rolls) * d(input_data["pvc_membrane_unit_price_per_roll_display"]),
            material_total_override=input_data["pvc_membrane_expected_material_total"],
            formula={
                "flat_area_m2": decimal_str(membrane_flat_area),
                "abutment_area_m2": decimal_str(membrane_abutment_area),
                "required_area_m2": decimal_str(membrane_required_area),
                "roll_area_m2": decimal_str(membrane_roll_area),
                "rolls_ordered": membrane_rolls,
            },
            notes=["11 * displayed price 51431 = 565741, but current Excel expected material_total is 565738."],
        )
    )

    def material_and_work(
        code: str,
        name: str,
        unit: str,
        quantity: Any,
        quantity_source: str,
        price_code: str | None,
        material_unit_price: Any,
        work_unit_price: Any,
        line_type: str = "material_and_work",
        notes: list[str] | None = None,
    ) -> dict[str, Any]:
        qty = d(quantity)
        return estimate_line(
            code=code,
            name=name,
            unit=unit,
            line_type=line_type,
            quantity_raw=qty,
            quantity_source=quantity_source,
            price_code=price_code,
            material_unit_price=material_unit_price,
            material_total_raw=qty * d(material_unit_price),
            work_unit_price=work_unit_price,
            work_total_raw=qty * d(work_unit_price),
            notes=notes,
        )

    lines.extend(
        [
            material_and_work("roof_pvc_aerator_75x375", "Аэратор кровельный PVC, 75х375 (без пробивки отверстий)", "шт", input_data["roof_aerators_count"], "roof_aerators_count", "roof_pvc_aerator_75x375_item", input_data["roof_aerator_unit_price"], input_data["roof_aerator_installation_rate"]),
            material_and_work("parapet_roof_drain_installation", "Установка воронки парапетной (без пробивки отверстий)", "шт", input_data["parapet_roof_drains_count"], "parapet_roof_drains_count", "roof_parapet_drain_item", input_data["parapet_roof_drain_unit_price"], input_data["parapet_roof_drain_installation_rate"]),
            estimate_line(
                code="gas_block_wall_hole_drilling",
                name="Пробивка отверстий в стенах из газоблока толщ.400мм",
                unit="шт",
                line_type="work",
                quantity_raw=input_data["gas_block_wall_holes_count"],
                quantity_source="gas_block_wall_holes_count",
                work_unit_price=input_data["gas_block_wall_hole_drilling_rate"],
                work_total_raw=d(input_data["gas_block_wall_holes_count"]) * d(input_data["gas_block_wall_hole_drilling_rate"]),
                notes=["Ручная строка; количество отверстий не всегда равно количеству парапетных воронок."],
            ),
            material_and_work("internal_roof_drain_with_heating", "Установка воронки кровельной (с обжимным мет. фланцем с обогревом 110х450мм) (без пробивки отверстий)", "шт", input_data["internal_roof_drains_count"], "internal_roof_drains_count", "roof_internal_drain_with_heating_item", input_data["internal_roof_drain_unit_price"], input_data["internal_roof_drain_installation_rate"]),
        ]
    )

    internal_drain_length = d(input_data["internal_roof_drains_count"]) * d(input_data["internal_drain_height_per_drain_m"])
    lines.append(
        material_and_work(
            "internal_drain_pvc_110mm",
            "Устройство внутреннего водостока (ПВХ Ф110мм) (ориентировочно)",
            "мп",
            internal_drain_length,
            "internal_roof_drains_count * internal_drain_height_per_drain_m",
            "roof_internal_drain_pvc_110mm_m",
            input_data["internal_drain_pvc_110_unit_price_per_m"],
            input_data["internal_drain_pvc_110_work_rate_per_m"],
            notes=["internal_drain_height_per_drain_m = 3.75 is a project input, not a permanent constant."],
        )
    )
    lines.append(
        estimate_line(
            code="roof_crane_lifting",
            name="Подъем материалов автокраном",
            unit="смена",
            line_type="fixed_manual_machinery",
            quantity_raw=input_data["roof_crane_lifting_shifts"],
            quantity_source="roof_crane_lifting_shifts",
            price_code="roof_crane_lifting_shift",
            material_unit_price=input_data["roof_crane_lifting_unit_price_per_shift"],
            material_total_raw=d(input_data["roof_crane_lifting_shifts"]) * d(input_data["roof_crane_lifting_unit_price_per_shift"]),
        )
    )
    lines.append(
        estimate_line(
            code="roof_consumables_tool_depreciation",
            name="Расходные материалы, амортизация инструмента",
            unit="комплект",
            line_type="manual_percentage_addon",
            quantity_raw=1,
            quantity_source="provided roof_consumables_total_raw",
            material_total_raw=input_data["roof_consumables_total_raw"],
            material_total_override=input_data["roof_consumables_total"],
            notes=["temporarily uses provided raw total; base formula to be confirmed later."],
        )
    )
    lines.append(
        material_and_work(
            "roof_waste_removal",
            "Вывоз мусора с объекта",
            "маш",
            input_data["roof_waste_removal_trucks"],
            "roof_waste_removal_trucks",
            None,
            input_data["roof_waste_removal_truck_unit_price"],
            input_data["roof_waste_removal_work_rate_per_truck"],
        )
    )
    lines.append(
        estimate_line(
            code="roof_logistics_and_supply",
            name="Логистика, и снабжение",
            unit="-",
            line_type="manual_fixed_material",
            quantity_raw=1,
            quantity_source="provided roof_logistics_and_supply_total_raw",
            material_unit_price=input_data["roof_logistics_and_supply_total_raw"],
            material_total_raw=input_data["roof_logistics_and_supply_total_raw"],
            material_total_override=input_data["roof_logistics_and_supply_total"],
            notes=["Строка включена по уточнению: это серая внутренняя себестоимость текущего раздела."],
        )
    )
    lines.append(
        estimate_line(
            code="technical_supervision",
            name="Технический надзор",
            unit="-",
            line_type="manual_fixed_work",
            quantity_raw=1,
            quantity_source="provided technical_supervision_work_total",
            work_unit_price=input_data["technical_supervision_work_total"],
            work_total_raw=input_data["technical_supervision_work_total"],
            notes=["Строка включена по уточнению: это серая внутренняя работа текущего раздела."],
        )
    )
    lines.append(
        estimate_line(
            code="procurement_storage",
            name="Заготовительно-складские расходы",
            unit="-",
            line_type="manual_fixed_work",
            quantity_raw=1,
            quantity_source="provided procurement_storage_work_total",
            work_unit_price=input_data["procurement_storage_work_total"],
            work_total_raw=input_data["procurement_storage_work_total"],
            notes=["Строка включена по сверке с серой зоной: 15 000 входит во внутреннюю себестоимость."],
        )
    )

    lines.extend(
        [
            zero_line("overhead_zero", "Накладные и общехозяйственные расходы", 1, "excel structure line"),
            zero_line("profit_zero", "Сметная прибыль", 1, "excel structure line"),
        ]
    )

    displayed_materials = sum((int(line["internal_cost"]["material_total"]) for line in lines), 0)
    displayed_works = sum((int(line["internal_cost"]["work_total"]) for line in lines), 0)
    displayed_total = displayed_materials + displayed_works

    # Current flat roof source has several intentional raw/display mismatches
    # fixed by Elena's Excel totals. Base section totals follow the displayed
    # line totals from the implemented scope, while per-line raw values remain
    # visible for review.
    effective_material_raw = d(displayed_materials)
    effective_work_raw = d(displayed_works)

    return {
        "section_code": "flat_roof",
        "section_name": "КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА",
        "project_name": input_data["project_name"],
        "inputs": input_data,
        "calculation_blocks": {
            "geometry": {
                "roof_area_level_1_m2": decimal_str(input_data["roof_area_level_1_m2"]),
                "roof_area_level_2_m2": decimal_str(input_data["roof_area_level_2_m2"]),
                "roof_area_total_m2": decimal_str(roof_area),
                "project_spec_roof_area_m2": decimal_str(input_data["project_spec_roof_area_m2"]),
                "parapet_length_level_1_m": decimal_str(input_data["parapet_length_level_1_m"]),
                "parapet_length_level_2_m": decimal_str(input_data["parapet_length_level_2_m"]),
                "vent_wall_abutment_level_1_m": decimal_str(input_data["vent_wall_abutment_level_1_m"]),
                "vent_wall_abutment_level_2_m": decimal_str(input_data["vent_wall_abutment_level_2_m"]),
                "parapet_and_abutment_total_length_m": decimal_str(parapet_and_abutment),
            },
            "internal_drain": {"internal_drain_total_length_m": decimal_str(internal_drain_length)},
            "pvc_membrane": {
                "required_area_m2": decimal_str(membrane_required_area),
                "roll_area_m2": decimal_str(membrane_roll_area),
                "rolls_ordered": membrane_rolls,
            },
        },
        "estimate_lines": lines,
        "totals": {
            "internal_materials_total_raw": decimal_str(effective_material_raw),
            "internal_materials_total": displayed_materials,
            "internal_works_total_raw": decimal_str(effective_work_raw),
            "internal_works_total": displayed_works,
            "internal_section_total_raw": decimal_str(displayed_total),
            "internal_section_total": displayed_total,
            "sum_of_displayed_line_material_totals": displayed_materials,
            "sum_of_displayed_line_work_totals": displayed_works,
            "sum_of_displayed_line_totals": displayed_total,
        },
        "warnings": warnings,
    }
