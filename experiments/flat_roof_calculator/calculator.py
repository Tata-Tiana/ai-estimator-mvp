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


def require_non_negative(input_data: dict[str, Any], key: str) -> Decimal:
    if key not in input_data:
        raise ValueError(f"{key} is required")
    value = d(input_data[key])
    if value < D0:
        raise ValueError(f"{key} must be >= 0")
    return value


def calculate_roof_geometry(input_data: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    method = input_data.get("roof_geometry_calc_method")
    if method not in {"legacy_totals", "detailed_project_geometry", "roof_zones"}:
        raise ValueError(f"Unsupported roof_geometry_calc_method: {method}")

    # Only roof_zones can mark a zone "exploitable" (V-GR membrane) today — legacy_totals
    # and detailed_project_geometry have no per-zone operability concept, so 100% of their
    # area/length stays "non_exploitable" (V-RP), exactly matching pre-2026-07-26 behavior.
    exploitable_area_total = D0
    exploitable_parapet_and_abutment_total = D0

    if method == "legacy_totals":
        roof_area = require_non_negative(input_data, "roof_area_total_m2")
        parapet_and_abutment = require_non_negative(input_data, "parapet_and_abutment_total_length_m")
        calculated_roof_area = None
        calculated_parapet_and_abutment = None
        roof_area_source = "legacy_totals"
        parapet_and_abutment_source = "legacy_totals"
    elif method == "roof_zones":
        # roof_zones[]: sums any number of roof zones (by floor, by type, including a
        # staircase roof zone with no special-casing) — real project case, 2026-07-26:
        # a PDF can split roof area into more than two zones (e.g. 1st floor Type1/Type2,
        # 2nd floor Type2, staircase roof) which don't fit detailed_project_geometry's
        # fixed level_1/level_2 shape. Each zone's area sums into roof_area_total_m2;
        # each zone's parapet_length_m + wall_abutment_length_m sum into
        # parapet_and_abutment_total_length_m, same combined concept
        # detailed_project_geometry already produces from its four length fields.
        roof_zones_in = input_data.get("roof_zones") or []
        if not roof_zones_in:
            raise ValueError("roof_zones is required for roof_geometry_calc_method=roof_zones")
        zone_area_total = D0
        zone_parapet_and_abutment_total = D0
        # exploitable ("эксплуатируемая") zones get V-GR membrane, everything else
        # (explicitly "неэксплуатируемая" or no operability given at all) gets V-RP —
        # real project rule, 2026-07-26. Tracked per zone here so the membrane material
        # split (see calculate_flat_roof) can price each zone's area with the right brand.
        for zone in roof_zones_in:
            if not zone.get("context"):
                raise ValueError("roof_zones[].context is required")
            zone_area = d(zone["area_m2"])
            if zone_area < D0:
                raise ValueError(f"roof_zones.{zone['context']}.area_m2 must be >= 0")
            zone_parapet_length = d(zone.get("parapet_length_m") or 0)
            zone_wall_abutment_length = d(zone.get("wall_abutment_length_m") or 0)
            if zone_parapet_length < D0 or zone_wall_abutment_length < D0:
                raise ValueError(f"roof_zones.{zone['context']} lengths must be >= 0")
            zone_operability = zone.get("operability") or "non_exploitable"
            if zone_operability not in {"exploitable", "non_exploitable"}:
                raise ValueError(
                    f"roof_zones.{zone['context']}.operability must be 'exploitable' or 'non_exploitable'"
                )
            zone_length = zone_parapet_length + zone_wall_abutment_length
            zone_area_total += zone_area
            zone_parapet_and_abutment_total += zone_length
            if zone_operability == "exploitable":
                exploitable_area_total += zone_area
                exploitable_parapet_and_abutment_total += zone_length
        roof_area = zone_area_total
        parapet_and_abutment = zone_parapet_and_abutment_total
        calculated_roof_area = zone_area_total
        calculated_parapet_and_abutment = zone_parapet_and_abutment_total
        roof_area_source = "calculated_from_roof_zones"
        parapet_and_abutment_source = "calculated_from_roof_zones"
    else:
        roof_area_level_1 = require_non_negative(input_data, "roof_area_level_1_m2")
        roof_area_level_2 = require_non_negative(input_data, "roof_area_level_2_m2")
        parapet_level_1 = require_non_negative(input_data, "parapet_length_level_1_m")
        parapet_level_2 = require_non_negative(input_data, "parapet_length_level_2_m")
        vent_level_1 = require_non_negative(input_data, "vent_wall_abutment_level_1_m")
        vent_level_2 = require_non_negative(input_data, "vent_wall_abutment_level_2_m")

        calculated_roof_area = roof_area_level_1 + roof_area_level_2
        calculated_parapet_and_abutment = parapet_level_1 + parapet_level_2 + vent_level_1 + vent_level_2
        roof_area = calculated_roof_area
        parapet_and_abutment = calculated_parapet_and_abutment
        roof_area_source = "calculated_from_roof_area_levels"
        parapet_and_abutment_source = "calculated_from_detailed_abutment_lengths"

    input_roof_area = d(input_data["roof_area_total_m2"]) if "roof_area_total_m2" in input_data else None
    input_parapet_and_abutment = (
        d(input_data["parapet_and_abutment_total_length_m"])
        if "parapet_and_abutment_total_length_m" in input_data
        else None
    )
    if input_roof_area is not None and input_roof_area < D0:
        raise ValueError("roof_area_total_m2 must be >= 0")
    if input_parapet_and_abutment is not None and input_parapet_and_abutment < D0:
        raise ValueError("parapet_and_abutment_total_length_m must be >= 0")

    roof_area_delta = None
    if input_roof_area is not None:
        roof_area_delta = input_roof_area - roof_area
        if abs(roof_area_delta) > Decimal("0.01"):
            warnings.append("Provided roof_area_total_m2 differs from calculated detailed roof areas.")

    parapet_and_abutment_delta = None
    if input_parapet_and_abutment is not None:
        parapet_and_abutment_delta = input_parapet_and_abutment - parapet_and_abutment
        if abs(parapet_and_abutment_delta) > Decimal("0.01"):
            warnings.append(
                "Provided parapet_and_abutment_total_length_m differs from calculated detailed abutment lengths."
            )

    return {
        "roof_geometry_calc_method": method,
        "roof_area": roof_area,
        "parapet_and_abutment": parapet_and_abutment,
        "roof_area_total_source": roof_area_source,
        "parapet_and_abutment_total_length_source": parapet_and_abutment_source,
        "input_roof_area_total_m2": input_roof_area,
        "calculated_roof_area_total_m2": calculated_roof_area,
        "roof_area_total_delta_m2": roof_area_delta,
        "input_parapet_and_abutment_total_length_m": input_parapet_and_abutment,
        "calculated_parapet_and_abutment_total_length_m": calculated_parapet_and_abutment,
        "parapet_and_abutment_total_delta_m": parapet_and_abutment_delta,
        "exploitable_roof_area_m2": exploitable_area_total,
        "exploitable_parapet_and_abutment_length_m": exploitable_parapet_and_abutment_total,
        "non_exploitable_roof_area_m2": roof_area - exploitable_area_total,
        "non_exploitable_parapet_and_abutment_length_m": parapet_and_abutment - exploitable_parapet_and_abutment_total,
    }


def optional_decimal_str(value: Any) -> str | None:
    return None if value is None else decimal_str(value)


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
        "project_spec_roof_area_m2 is not used without human review; current calculation uses roof geometry totals.",
        "Slope insulation plate volumes are project/specification values; calculator field names keep supplier_required for compatibility.",
        "Roof consumables/logistics/technical supervision/procurement-storage can be calculated by rates; legacy fixed totals are still accepted for old cases.",
    ]
    geometry = calculate_roof_geometry(input_data, warnings)
    roof_area = geometry["roof_area"]
    parapet_and_abutment = geometry["parapet_and_abutment"]
    exploitable_roof_area = geometry["exploitable_roof_area_m2"]
    exploitable_parapet_and_abutment = geometry["exploitable_parapet_and_abutment_length_m"]
    non_exploitable_roof_area = geometry["non_exploitable_roof_area_m2"]
    non_exploitable_parapet_and_abutment = geometry["non_exploitable_parapet_and_abutment_length_m"]

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
                "rate_context": "reviewed combined work rate from price registry/review",
            },
            notes=["Ставка работы принимается как готовая проверенная ставка из прайса/ревью."],
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
            formula={
                "required_volume_m3": decimal_str(eps100_required),
                "packs_ordered": eps100_packs,
                "ordered_volume_m3": decimal_str(eps100_ordered),
            },
        )
    )

    slope_specs = [
        ("eps50_technonikol_carbon_eco", "Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON ECO (50мм)", "roof_eps50_technonikol_carbon_eco_m3", "eps50"),
        ("eps_slope_2_1_plate_a", "Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты A)", "roof_eps_slope_2_1_plate_a_m3", "slope_plate_a"),
        ("eps_slope_2_1_plate_b", "Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты B)", "roof_eps_slope_2_1_plate_b_m3", "slope_plate_b"),
        ("eps_slope_4_2_plate_j", "Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты J)", "roof_eps_slope_4_2_plate_j_m3", "slope_plate_j"),
        ("eps_slope_4_2_plate_k", "Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты K)", "roof_eps_slope_4_2_plate_k_m3", "slope_plate_k"),
    ]
    for code, name, price_code, prefix in slope_specs:
        notes = ["Объем SLOPE берется из проектной спецификации кровли; имя поля сохранено для совместимости."]
        lines.append(
            supplier_pack_material_line(
                code=code,
                name=name,
                price_code=price_code,
                supplier_required_volume=d(input_data[f"{prefix}_supplier_required_volume_m3"]),
                pack_volume=d(input_data[f"{prefix}_pack_volume_m3"]),
                unit_price=d(input_data[f"{prefix}_unit_price_per_m3"]),
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
        ]
    )

    vent_shaft_abutment_count = d(input_data.get("vent_shaft_abutment_count") or 0)
    if vent_shaft_abutment_count > D0:
        lines.append(
            estimate_line(
                code="vent_shaft_abutment_installation",
                name="Монтаж примыкания к вентшахтам",
                unit="шт",
                line_type="work",
                quantity_raw=vent_shaft_abutment_count,
                quantity_source="vent_shaft_abutment_count",
                work_unit_price=input_data["vent_shaft_abutment_work_rate_per_item"],
                work_total_raw=vent_shaft_abutment_count * d(input_data["vent_shaft_abutment_work_rate_per_item"]),
            )
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

    # Membrane material splits by brand per zone exploitability (real project rule,
    # 2026-07-26): V-RP covers the non-exploitable area/abutment (everything when no
    # roof_zones operability is used at all — byte-identical to pre-2026-07-26 behavior
    # since exploitable_roof_area is then always 0), V-GR covers only the exploitable
    # portion. Installation WORK above stays one combined line regardless of brand (same
    # physical laying operation) — only material purchase splits.
    membrane_flat_area = non_exploitable_roof_area * d(input_data["pvc_membrane_flat_coeff"])
    membrane_abutment_area = non_exploitable_parapet_and_abutment * d(input_data["pvc_membrane_parapet_coeff"])
    membrane_required_area = membrane_flat_area + membrane_abutment_area
    membrane_roll_area = d(input_data["pvc_membrane_roll_width_m"]) * d(input_data["pvc_membrane_roll_length_m"])
    membrane_rolls = 0
    if membrane_required_area > D0:
        membrane_rolls = ceil_decimal(membrane_required_area / membrane_roll_area)
        lines.append(
            estimate_line(
                code="pvc_membrane_logicroof_vrp_1_5mm_gray",
                name="Полимерная мембрана ПВХ Logicroof V-RP 1,5 мм мембрана серая, 2,10х20",
                unit="рул",
                line_type="materials",
                quantity_raw=membrane_rolls,
                quantity_source="non-exploitable flat and abutment membrane areas rounded to rolls",
                price_code="roof_pvc_membrane_logicroof_vrp_1_5mm_gray_roll",
                material_unit_price=input_data["pvc_membrane_unit_price_per_roll_display"],
                material_total_raw=d(membrane_rolls) * d(input_data["pvc_membrane_unit_price_per_roll_display"]),
                formula={
                    "flat_area_m2": decimal_str(membrane_flat_area),
                    "abutment_area_m2": decimal_str(membrane_abutment_area),
                    "required_area_m2": decimal_str(membrane_required_area),
                    "roll_area_m2": decimal_str(membrane_roll_area),
                    "rolls_ordered": membrane_rolls,
                },
            )
        )

    vgr_membrane_flat_area = exploitable_roof_area * d(input_data["pvc_membrane_flat_coeff"])
    vgr_membrane_abutment_area = exploitable_parapet_and_abutment * d(input_data["pvc_membrane_parapet_coeff"])
    vgr_membrane_required_area = vgr_membrane_flat_area + vgr_membrane_abutment_area
    vgr_membrane_roll_area = D0
    vgr_membrane_rolls = 0
    if vgr_membrane_required_area > D0:
        # pvc_membrane_vgr_* fields only need to exist when a project actually has an
        # exploitable zone — every existing project/case without one never touches them.
        vgr_membrane_roll_area = d(input_data["pvc_membrane_vgr_roll_width_m"]) * d(
            input_data["pvc_membrane_vgr_roll_length_m"]
        )
        vgr_membrane_rolls = ceil_decimal(vgr_membrane_required_area / vgr_membrane_roll_area)
        lines.append(
            estimate_line(
                code="pvc_membrane_logicroof_vgr_1_5mm_gray",
                name="Полимерная мембрана ПВХ Logicroof V-GR 1,5 мм мембрана серая, 2,10х20",
                unit="рул",
                line_type="materials",
                quantity_raw=vgr_membrane_rolls,
                quantity_source="exploitable flat and abutment membrane areas rounded to rolls",
                price_code="roof_pvc_membrane_logicroof_vgr_1_5mm_gray_roll",
                material_unit_price=input_data["pvc_membrane_vgr_unit_price_per_roll_display"],
                material_total_raw=d(vgr_membrane_rolls) * d(input_data["pvc_membrane_vgr_unit_price_per_roll_display"]),
                formula={
                    "flat_area_m2": decimal_str(vgr_membrane_flat_area),
                    "abutment_area_m2": decimal_str(vgr_membrane_abutment_area),
                    "required_area_m2": decimal_str(vgr_membrane_required_area),
                    "roll_area_m2": decimal_str(vgr_membrane_roll_area),
                    "rolls_ordered": vgr_membrane_rolls,
                },
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
            material_and_work("internal_roof_drain_with_heating", "Установка воронки кровельной (с обжимным мет. фланцем с обогревом 110х450мм) (без пробивки отверстий)", "шт", input_data["internal_roof_drains_count"], "internal_roof_drains_count", "roof_internal_drain_with_heating_item", input_data["internal_roof_drain_unit_price"], input_data["internal_roof_drain_installation_rate"]),
        ]
    )

    gas_block_wall_holes_count = d(input_data.get("gas_block_wall_holes_count") or 0)
    if gas_block_wall_holes_count > D0:
        lines.append(
            estimate_line(
                code="gas_block_wall_hole_drilling",
                name="Пробивка отверстий в стенах из газоблока толщ.400мм",
                unit="шт",
                line_type="work",
                quantity_raw=gas_block_wall_holes_count,
                quantity_source="gas_block_wall_holes_count",
                work_unit_price=input_data["gas_block_wall_hole_drilling_rate"],
                work_total_raw=gas_block_wall_holes_count * d(input_data["gas_block_wall_hole_drilling_rate"]),
                notes=["Special-case only: Elena 2026-07-30 confirmed this is not a standard roof work item."],
            )
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

    direct_cost_base_raw = sum((d(line["internal_cost"]["line_total_raw"]) for line in lines), D0)
    direct_material_base_raw = sum((d(line["internal_cost"]["material_total_raw"]) for line in lines), D0)
    direct_work_base_raw = sum((d(line["internal_cost"]["work_total_raw"]) for line in lines), D0)

    roof_consumables_total_raw = d(input_data.get("roof_consumables_total_raw", 0))
    if input_data.get("roof_consumables_calc_method", "legacy_fixed_amount") == "section_total_rate":
        roof_consumables_total_raw = direct_cost_base_raw * d(input_data.get("roof_consumables_rate", 0))
    roof_logistics_and_supply_total_raw = d(input_data.get("roof_logistics_and_supply_total_raw", 0))
    if input_data.get("roof_logistics_and_supply_calc_method", "legacy_fixed_amount") == "section_total_rate":
        roof_logistics_and_supply_total_raw = direct_cost_base_raw * d(input_data.get("roof_logistics_and_supply_rate", 0))
    technical_supervision_work_total = d(input_data.get("technical_supervision_work_total", 0))
    if input_data.get("technical_supervision_calc_method", "legacy_fixed_amount") == "section_work_rate":
        technical_supervision_work_total = direct_work_base_raw * d(input_data.get("technical_supervision_rate", 0))
    procurement_storage_work_total = d(input_data.get("procurement_storage_work_total", 0))
    if input_data.get("procurement_storage_calc_method", "legacy_fixed_amount") == "section_material_rate":
        procurement_storage_work_total = direct_material_base_raw * d(input_data.get("procurement_storage_rate", 0))

    lines.append(
        estimate_line(
            code="roof_consumables_tool_depreciation",
            name="Расходные материалы, амортизация инструмента",
            unit="комплект",
            line_type="calculated_percentage_addon"
            if input_data.get("roof_consumables_calc_method") == "section_total_rate"
            else "manual_percentage_addon",
            quantity_raw=1,
            quantity_source="direct_cost_base_raw * roof_consumables_rate"
            if input_data.get("roof_consumables_calc_method") == "section_total_rate"
            else "provided roof_consumables_total_raw",
            material_total_raw=roof_consumables_total_raw,
            formula={
                "direct_cost_base_raw": decimal_str(direct_cost_base_raw),
                "roof_consumables_rate": decimal_str(input_data.get("roof_consumables_rate", 0)),
            }
            if input_data.get("roof_consumables_calc_method") == "section_total_rate"
            else {},
            notes=["Calculated from direct roof cost base before overhead rows."]
            if input_data.get("roof_consumables_calc_method") == "section_total_rate"
            else ["Uses provided legacy raw total."],
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
            line_type="calculated_percentage_addon"
            if input_data.get("roof_logistics_and_supply_calc_method") == "section_total_rate"
            else "manual_fixed_material",
            quantity_raw=1,
            quantity_source="direct_cost_base_raw * roof_logistics_and_supply_rate"
            if input_data.get("roof_logistics_and_supply_calc_method") == "section_total_rate"
            else "provided roof_logistics_and_supply_total_raw",
            material_unit_price=roof_logistics_and_supply_total_raw,
            material_total_raw=roof_logistics_and_supply_total_raw,
            formula={
                "direct_cost_base_raw": decimal_str(direct_cost_base_raw),
                "roof_logistics_and_supply_rate": decimal_str(input_data.get("roof_logistics_and_supply_rate", 0)),
            }
            if input_data.get("roof_logistics_and_supply_calc_method") == "section_total_rate"
            else {},
            notes=["Calculated from direct roof cost base before overhead rows."]
            if input_data.get("roof_logistics_and_supply_calc_method") == "section_total_rate"
            else ["Строка включена по уточнению: это серая внутренняя себестоимость текущего раздела."],
        )
    )
    lines.append(
        estimate_line(
            code="technical_supervision",
            name="Технический надзор",
            unit="-",
            line_type="calculated_percentage_addon"
            if input_data.get("technical_supervision_calc_method") == "section_work_rate"
            else "manual_fixed_work",
            quantity_raw=1,
            quantity_source="direct_work_base_raw * technical_supervision_rate"
            if input_data.get("technical_supervision_calc_method") == "section_work_rate"
            else "provided technical_supervision_work_total",
            work_unit_price=technical_supervision_work_total,
            work_total_raw=technical_supervision_work_total,
            formula={
                "direct_work_base_raw": decimal_str(direct_work_base_raw),
                "technical_supervision_rate": decimal_str(input_data.get("technical_supervision_rate", 0)),
            }
            if input_data.get("technical_supervision_calc_method") == "section_work_rate"
            else {},
            notes=["Calculated from direct roof work subtotal before overhead rows."]
            if input_data.get("technical_supervision_calc_method") == "section_work_rate"
            else ["Строка включена по уточнению: это серая внутренняя работа текущего раздела."],
        )
    )
    lines.append(
        estimate_line(
            code="procurement_storage",
            name="Заготовительно-складские расходы",
            unit="-",
            line_type="calculated_percentage_addon"
            if input_data.get("procurement_storage_calc_method") == "section_material_rate"
            else "manual_fixed_work",
            quantity_raw=1,
            quantity_source="direct_material_base_raw * procurement_storage_rate"
            if input_data.get("procurement_storage_calc_method") == "section_material_rate"
            else "provided procurement_storage_work_total",
            work_unit_price=procurement_storage_work_total,
            work_total_raw=procurement_storage_work_total,
            formula={
                "direct_material_base_raw": decimal_str(direct_material_base_raw),
                "procurement_storage_rate": decimal_str(input_data.get("procurement_storage_rate", 0)),
            }
            if input_data.get("procurement_storage_calc_method") == "section_material_rate"
            else {},
            notes=["Calculated from direct roof material subtotal before overhead rows."]
            if input_data.get("procurement_storage_calc_method") == "section_material_rate"
            else ["Строка включена по сверке с серой зоной: это внутренняя себестоимость."],
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

    effective_material_raw = sum((d(line["internal_cost"]["material_total_raw"]) for line in lines), D0)
    effective_work_raw = sum((d(line["internal_cost"]["work_total_raw"]) for line in lines), D0)

    return {
        "section_code": "flat_roof",
        "section_name": "КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА",
        "project_name": input_data["project_name"],
        "inputs": input_data,
        "calculation_blocks": {
            "geometry": {
                "roof_geometry_calc_method": geometry["roof_geometry_calc_method"],
                "roof_area_level_1_m2": decimal_str(input_data["roof_area_level_1_m2"]),
                "roof_area_level_2_m2": decimal_str(input_data["roof_area_level_2_m2"]),
                "roof_area_total_m2": decimal_str(roof_area),
                "roof_area_total_source": geometry["roof_area_total_source"],
                "project_spec_roof_area_m2": decimal_str(input_data["project_spec_roof_area_m2"]),
                "parapet_length_level_1_m": decimal_str(input_data["parapet_length_level_1_m"]),
                "parapet_length_level_2_m": decimal_str(input_data["parapet_length_level_2_m"]),
                "vent_wall_abutment_level_1_m": decimal_str(input_data["vent_wall_abutment_level_1_m"]),
                "vent_wall_abutment_level_2_m": decimal_str(input_data["vent_wall_abutment_level_2_m"]),
                "parapet_and_abutment_total_length_m": decimal_str(parapet_and_abutment),
                "parapet_and_abutment_total_length_source": geometry["parapet_and_abutment_total_length_source"],
                "input_roof_area_total_m2": optional_decimal_str(geometry["input_roof_area_total_m2"]),
                "calculated_roof_area_total_m2": optional_decimal_str(geometry["calculated_roof_area_total_m2"]),
                "roof_area_total_delta_m2": optional_decimal_str(geometry["roof_area_total_delta_m2"]),
                "input_parapet_and_abutment_total_length_m": optional_decimal_str(
                    geometry["input_parapet_and_abutment_total_length_m"]
                ),
                "calculated_parapet_and_abutment_total_length_m": optional_decimal_str(
                    geometry["calculated_parapet_and_abutment_total_length_m"]
                ),
                "parapet_and_abutment_total_delta_m": optional_decimal_str(
                    geometry["parapet_and_abutment_total_delta_m"]
                ),
            },
            "internal_drain": {"internal_drain_total_length_m": decimal_str(internal_drain_length)},
            "pvc_membrane": {
                "required_area_m2": decimal_str(membrane_required_area),
                "roll_area_m2": decimal_str(membrane_roll_area),
                "rolls_ordered": membrane_rolls,
            },
            "pvc_membrane_vgr": {
                "exploitable_roof_area_m2": decimal_str(exploitable_roof_area),
                "exploitable_parapet_and_abutment_length_m": decimal_str(exploitable_parapet_and_abutment),
                "required_area_m2": decimal_str(vgr_membrane_required_area),
                "roll_area_m2": decimal_str(vgr_membrane_roll_area),
                "rolls_ordered": vgr_membrane_rolls,
            },
            "overheads": {
                "direct_cost_base_raw": decimal_str(direct_cost_base_raw),
                "direct_material_base_raw": decimal_str(direct_material_base_raw),
                "direct_work_base_raw": decimal_str(direct_work_base_raw),
                "roof_consumables_calc_method": input_data.get("roof_consumables_calc_method", "legacy_fixed_amount"),
                "roof_consumables_rate": decimal_str(input_data.get("roof_consumables_rate", 0)),
                "roof_consumables_total_raw": decimal_str(roof_consumables_total_raw),
                "roof_logistics_and_supply_calc_method": input_data.get("roof_logistics_and_supply_calc_method", "legacy_fixed_amount"),
                "roof_logistics_and_supply_rate": decimal_str(input_data.get("roof_logistics_and_supply_rate", 0)),
                "roof_logistics_and_supply_total_raw": decimal_str(roof_logistics_and_supply_total_raw),
                "technical_supervision_calc_method": input_data.get("technical_supervision_calc_method", "legacy_fixed_amount"),
                "technical_supervision_rate": decimal_str(input_data.get("technical_supervision_rate", 0)),
                "technical_supervision_work_total": decimal_str(technical_supervision_work_total),
                "procurement_storage_calc_method": input_data.get("procurement_storage_calc_method", "legacy_fixed_amount"),
                "procurement_storage_rate": decimal_str(input_data.get("procurement_storage_rate", 0)),
                "procurement_storage_work_total": decimal_str(procurement_storage_work_total),
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
