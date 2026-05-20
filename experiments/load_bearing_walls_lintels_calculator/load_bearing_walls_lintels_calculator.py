from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from typing import Any


def d(value: float | int | str | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def money(value: Decimal | float | int) -> int:
    return int(d(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def q(value: Decimal | float | int, places: str = "0.0001") -> float:
    return float(d(value).quantize(Decimal(places), rounding=ROUND_HALF_UP))


def require_positive(name: str, value: float | int) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")


def require_non_negative(name: str, value: float | int) -> None:
    if value < 0:
        raise ValueError(f"{name} must be greater than or equal to 0")


@dataclass(frozen=True)
class LintelLength:
    length_m: float
    count: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LintelLength":
        return cls(**data)


@dataclass(frozen=True)
class RebarItem:
    code: str
    name: str
    steel_class: str
    diameter_mm: int
    weight_kg: float
    kg_per_meter: float
    rod_length_m: float
    unit_price_per_m: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RebarItem":
        return cls(**data)


@dataclass(frozen=True)
class LoadBearingWallsLintelsInput:
    project_name: str
    scaffolding_setup_quantity: float
    scaffolding_setup_work_unit_price: float
    scaffolding_timber_quantity_m3: float
    scaffolding_timber_unit_price: float
    cutoff_waterproofing_wall_400_lengths_m: list[float]
    cutoff_waterproofing_wall_250_lengths_m: list[float]
    wall_400_thickness_m: float
    wall_250_thickness_m: float
    cutoff_waterproofing_material_unit_price: float
    cutoff_waterproofing_work_unit_price: float
    main_wall_gas_block_400_spec_volume_m3: float
    main_wall_gas_block_250_spec_volume_m3: float
    main_wall_masonry_work_unit_price: float
    gas_block_waste_coeff: float
    gas_block_d400_pallet_volume_m3: float
    gas_block_d400_unit_price: float
    gas_block_d500_250_pallet_volume_m3: float
    gas_block_d500_250_unit_price: float
    adhesive_consumption_bag_per_m3: float
    adhesive_waste_coeff: float
    adhesive_unit_price: float
    sand_concrete_consumption_kg_per_m2_per_10mm: float
    sand_concrete_thickness_factor: float
    sand_concrete_bag_weight_kg: float
    sand_concrete_unit_price: float
    lintel_lengths_m: list[LintelLength | dict[str, Any]]
    gas_block_length_m: float
    u_block_cutting_work_unit_price: float
    main_wall_external_length_m: float
    main_wall_internal_250_control_length_m: float
    main_wall_reinforcement_rows: float
    main_wall_400_reinforcement_threads: float
    main_wall_250_reinforcement_threads: float
    main_wall_reinforcement_overlap_coeff: float
    rebar_waste_coeff: float
    rebar_a500_d10_kg_per_m: float
    rebar_a500_d10_rod_length_m: float
    rebar_a500_d10_unit_price_per_m: float
    gas_block_delivery_truck_capacity_m3: float
    gas_block_delivery_unit_price: float
    gas_block_unloading_manipulator_unit_price: float
    main_walls_crane_shifts: float
    crane_25t_unit_price: float
    lintel_rebar_items: list[RebarItem | dict[str, Any]]
    lintel_concreting_work_unit_price: float
    lintel_section_width_m: float
    lintel_section_height_m: float
    concrete_waste_coeff: float
    lintel_concrete_min_order_volume_m3: float
    concrete_m300_unit_price: float
    concrete_delivery_trips: float
    concrete_delivery_unit_price: float
    manual_concrete_lifting_work_unit_price: float
    parapet_enabled: bool
    parapet_masonry_volume_m3: float
    parapet_masonry_work_unit_price: float
    second_light_masonry_enabled: bool
    second_light_masonry_case_specific: bool
    second_light_masonry_volume_m3: float
    vent_chimney_cladding_enabled: bool
    vent_chimney_gas_block_spec_volume_m3: float
    vent_chimney_block_thickness_m: float
    vent_chimney_cladding_work_unit_price: float
    gas_block_d500_150_pallet_volume_m3: float
    gas_block_d500_150_unit_price: float
    vent_chimney_segment_lengths_m: list[dict[str, Any]]
    vent_chimney_rows: float
    block_height_m: float
    parapet_crane_shifts: float
    parapet_chasing_base_length_m: float
    second_light_chasing_base_length_m: float
    parapet_rebar_base_length_m: float
    second_light_rebar_base_length_m: float
    walls_consumables_tool_amortization_amount_raw: float
    waste_removal_trucks: float
    waste_removal_truck_unit_price: float
    waste_removal_work_unit_price: float
    technical_supervision_amount: float

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "lintel_lengths_m",
            [x if isinstance(x, LintelLength) else LintelLength.from_dict(x) for x in self.lintel_lengths_m],
        )
        object.__setattr__(
            self,
            "lintel_rebar_items",
            [x if isinstance(x, RebarItem) else RebarItem.from_dict(x) for x in self.lintel_rebar_items],
        )
        self.validate()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LoadBearingWallsLintelsInput":
        return cls(**data)

    def validate(self) -> None:
        if not self.project_name:
            raise ValueError("project_name is required")
        for name in [
            "wall_400_thickness_m",
            "wall_250_thickness_m",
            "gas_block_waste_coeff",
            "gas_block_d400_pallet_volume_m3",
            "gas_block_d500_250_pallet_volume_m3",
            "adhesive_consumption_bag_per_m3",
            "adhesive_waste_coeff",
            "sand_concrete_bag_weight_kg",
            "gas_block_length_m",
            "rebar_waste_coeff",
            "rebar_a500_d10_kg_per_m",
            "rebar_a500_d10_rod_length_m",
            "gas_block_delivery_truck_capacity_m3",
            "lintel_section_width_m",
            "lintel_section_height_m",
            "concrete_waste_coeff",
            "gas_block_d500_150_pallet_volume_m3",
            "vent_chimney_block_thickness_m",
            "block_height_m",
        ]:
            require_positive(name, getattr(self, name))
        for name, value in self.to_dict().items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                require_non_negative(name, value)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EstimateLineResult:
    code: str
    name: str
    unit: str
    quantity: float
    material_unit_price: float
    material_total_raw: float
    material_total: int
    work_unit_price: float
    work_total_raw: float
    work_total: int
    line_total_raw: float
    line_total: int
    display_quantity: float | None = None
    is_case_specific: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        if self.display_quantity is None:
            result.pop("display_quantity")
        return result


def line(
    code: str,
    name: str,
    unit: str,
    quantity: float,
    material_unit_price: float = 0.0,
    work_unit_price: float = 0.0,
    display_quantity: float | None = None,
    is_case_specific: bool = False,
    notes: str = "",
    material_total_raw_override: float | None = None,
    work_total_raw_override: float | None = None,
) -> EstimateLineResult:
    quantity_value = q(quantity)
    material_raw = (
        d(material_total_raw_override)
        if material_total_raw_override is not None
        else d(quantity_value) * d(material_unit_price)
    )
    work_raw = (
        d(work_total_raw_override)
        if work_total_raw_override is not None
        else d(quantity_value) * d(work_unit_price)
    )
    total_raw = material_raw + work_raw
    return EstimateLineResult(
        code=code,
        name=name,
        unit=unit,
        quantity=quantity_value,
        display_quantity=display_quantity,
        material_unit_price=material_unit_price,
        material_total_raw=q(material_raw, "0.000001"),
        material_total=money(material_raw),
        work_unit_price=work_unit_price,
        work_total_raw=q(work_raw, "0.000001"),
        work_total=money(work_raw),
        line_total_raw=q(total_raw, "0.000001"),
        line_total=money(total_raw),
        is_case_specific=is_case_specific,
        notes=notes,
    )


def gas_block_order(spec_volume: float, waste_coeff: float, pallet_volume: float) -> dict[str, Any]:
    required = d(spec_volume) * d(waste_coeff)
    raw_pallets = required / d(pallet_volume)
    pallets = int(ceil(raw_pallets))
    order_volume = d(pallets) * d(pallet_volume)
    return {
        "spec_volume_m3": q(spec_volume),
        "required_volume_m3": q(required),
        "raw_pallets": q(raw_pallets),
        "pallets": pallets,
        "order_volume_m3": q(order_volume),
    }


def rebar_from_weight(item: RebarItem, waste_coeff: float) -> tuple[dict[str, Any], EstimateLineResult]:
    raw_length = d(item.weight_kg) / d(item.kg_per_meter)
    length_with_waste = raw_length * d(waste_coeff)
    raw_rods = length_with_waste / d(item.rod_length_m)
    rods = int(ceil(raw_rods))
    order_length = d(rods) * d(item.rod_length_m)
    control = {
        "weight_kg": item.weight_kg,
        "raw_length_m": q(raw_length),
        "length_with_waste_m": q(length_with_waste),
        "raw_rods": q(raw_rods),
        "rods": rods,
        "order_length_m": q(order_length),
    }
    return control, line(
        code=item.code,
        name=item.name,
        unit="мп",
        quantity=q(order_length),
        material_unit_price=item.unit_price_per_m,
    )


def rebar_from_base_length(base_length: float, rod_length: float, waste_coeff: float, unit_price: float) -> dict[str, Any]:
    raw_rods = d(base_length) * d(waste_coeff) / d(rod_length)
    rods = int(ceil(raw_rods))
    order_length = d(rods) * d(rod_length)
    return {
        "base_length_m": q(base_length),
        "raw_rods": q(raw_rods),
        "rods": rods,
        "order_length_m": q(order_length),
        "material_total_raw": q(order_length * d(unit_price), "0.000001"),
        "material_total": money(order_length * d(unit_price)),
    }


def calculate_blocks(data: LoadBearingWallsLintelsInput) -> dict[str, Any]:
    wall_400_length = d(sum(data.cutoff_waterproofing_wall_400_lengths_m))
    wall_250_length = d(sum(data.cutoff_waterproofing_wall_250_lengths_m))
    cutoff_area = wall_400_length * d(data.wall_400_thickness_m) + wall_250_length * d(data.wall_250_thickness_m)
    main_masonry_volume = d(data.main_wall_gas_block_400_spec_volume_m3) + d(data.main_wall_gas_block_250_spec_volume_m3)
    main_d400 = gas_block_order(data.main_wall_gas_block_400_spec_volume_m3, data.gas_block_waste_coeff, data.gas_block_d400_pallet_volume_m3)
    main_d500_250 = gas_block_order(data.main_wall_gas_block_250_spec_volume_m3, data.gas_block_waste_coeff, data.gas_block_d500_250_pallet_volume_m3)
    adhesive_raw = main_masonry_volume * d(data.adhesive_consumption_bag_per_m3) * d(data.adhesive_waste_coeff)
    sand_raw = cutoff_area * d(data.sand_concrete_consumption_kg_per_m2_per_10mm) * d(data.sand_concrete_thickness_factor) / d(data.sand_concrete_bag_weight_kg)
    lintel_total_length = sum(d(x.length_m) * d(x.count) for x in data.lintel_lengths_m)
    u_block_quantity = lintel_total_length / d(data.gas_block_length_m)
    main_chasing_raw = (
        d(data.main_wall_reinforcement_rows) * d(data.main_wall_external_length_m) * d(data.main_wall_400_reinforcement_threads)
        + d(data.main_wall_internal_250_control_length_m) * d(data.main_wall_reinforcement_rows) * d(data.main_wall_250_reinforcement_threads)
    ) * d(data.main_wall_reinforcement_overlap_coeff)
    main_chasing_quantity = Decimal(ceil(main_chasing_raw))
    main_rebar = rebar_from_base_length(q(main_chasing_quantity), data.rebar_a500_d10_rod_length_m, data.rebar_waste_coeff, data.rebar_a500_d10_unit_price_per_m)
    lintel_rebar_controls = {}
    lintel_rebar_lines = []
    for item in data.lintel_rebar_items:
        control, rebar_line = rebar_from_weight(item, data.rebar_waste_coeff)
        lintel_rebar_controls[item.code] = control
        lintel_rebar_lines.append(rebar_line)
    lintel_rebar_frame_quantity = sum(d(x.quantity) for x in lintel_rebar_lines)
    lintel_raw_concrete = lintel_total_length * d(data.lintel_section_width_m) * d(data.lintel_section_height_m)
    lintel_required_concrete = lintel_raw_concrete * d(data.concrete_waste_coeff)
    lintel_order_concrete = max(d(data.lintel_concrete_min_order_volume_m3), Decimal(ceil(lintel_required_concrete)))
    second_light_volume = d(data.second_light_masonry_volume_m3) if data.second_light_masonry_enabled else Decimal("0")
    parapet_volume = d(data.parapet_masonry_volume_m3) if data.parapet_enabled else Decimal("0")
    parapet_upper_total_volume = parapet_volume + second_light_volume
    parapet_upper_d400 = gas_block_order(q(parapet_upper_total_volume), data.gas_block_waste_coeff, data.gas_block_d400_pallet_volume_m3)
    second_light_d400 = gas_block_order(data.second_light_masonry_volume_m3, data.gas_block_waste_coeff, data.gas_block_d400_pallet_volume_m3)
    # For delivery the Excel sheet splits the combined parapet+second-light purchase
    # into 15.05 and 23.65 m3, avoiding an extra pallet in the parapet subgroup.
    parapet_delivery_order_volume = d(parapet_upper_d400["order_volume_m3"]) - d(second_light_d400["order_volume_m3"])
    vent_area = d(data.vent_chimney_gas_block_spec_volume_m3) / d(data.vent_chimney_block_thickness_m)
    vent_d500 = gas_block_order(data.vent_chimney_gas_block_spec_volume_m3, data.gas_block_waste_coeff, data.gas_block_d500_150_pallet_volume_m3)
    vent_total_length = sum(d(x["length_m"]) * d(x["count"]) for x in data.vent_chimney_segment_lengths_m)
    vent_height = d(data.block_height_m) * d(data.vent_chimney_rows)
    vent_geometry_volume = vent_total_length * vent_height * d(data.vent_chimney_block_thickness_m)
    delivery_total = d(main_d400["order_volume_m3"]) + d(main_d500_250["order_volume_m3"]) + d(second_light_d400["order_volume_m3"]) + parapet_delivery_order_volume + d(vent_d500["order_volume_m3"])
    delivery_trucks = int(ceil(delivery_total / d(data.gas_block_delivery_truck_capacity_m3)))
    second_light_adhesive_raw = second_light_volume * d(data.adhesive_consumption_bag_per_m3) * d(data.adhesive_waste_coeff)
    second_light_adhesive_bags = int(ceil(second_light_adhesive_raw))
    parapet_vent_adhesive_raw = (parapet_volume + d(data.vent_chimney_gas_block_spec_volume_m3)) * d(data.adhesive_consumption_bag_per_m3) * d(data.adhesive_waste_coeff)
    parapet_vent_adhesive_bags = int(ceil(parapet_vent_adhesive_raw))
    second_light_rebar = rebar_from_base_length(data.second_light_rebar_base_length_m, data.rebar_a500_d10_rod_length_m, data.rebar_waste_coeff, data.rebar_a500_d10_unit_price_per_m)
    parapet_rebar = rebar_from_base_length(data.parapet_rebar_base_length_m, data.rebar_a500_d10_rod_length_m, data.rebar_waste_coeff, data.rebar_a500_d10_unit_price_per_m)

    return {
        "scaffolding": {"setup_quantity": data.scaffolding_setup_quantity, "timber_quantity_m3": data.scaffolding_timber_quantity_m3},
        "cutoff_waterproofing": {
            "wall_400_length_m": q(wall_400_length),
            "wall_250_length_m": q(wall_250_length),
            "cutoff_waterproofing_area_m2": q(cutoff_area),
        },
        "main_walls": {"main_masonry_volume_m3": q(main_masonry_volume)},
        "main_gas_blocks": {"d400": main_d400, "d500_250": main_d500_250},
        "adhesive_and_sand_concrete": {
            "main_adhesive_raw_bags": q(adhesive_raw),
            "main_adhesive_bags": int(ceil(adhesive_raw)),
            "sand_concrete_raw_bags": q(sand_raw),
            "sand_concrete_bags": int(ceil(sand_raw)),
        },
        "lintels": {
            "lintel_total_length_m": q(lintel_total_length),
            "u_block_quantity": q(u_block_quantity),
            "lintel_200mm_steps": q(lintel_total_length / d("0.2")),
            "rebar": lintel_rebar_controls,
            "lintel_rebar_frame_assembly_quantity_m": q(lintel_rebar_frame_quantity),
            "lintel_raw_concrete_volume_m3": q(lintel_raw_concrete),
            "lintel_required_concrete_volume_m3": q(lintel_required_concrete),
            "lintel_concrete_order_volume_m3": q(lintel_order_concrete),
        },
        "main_wall_reinforcement": {
            "main_wall_chasing_raw_length_m": q(main_chasing_raw, "0.000001"),
            "main_wall_chasing_quantity_m": q(main_chasing_quantity),
            "main_wall_rebar_a500_d10": main_rebar,
            "main_wall_rebar_control_weight_kg": q(d(main_rebar["order_length_m"]) * d(data.rebar_a500_d10_kg_per_m)),
        },
        "deliveries_and_cranes": {
            "gas_block_delivery_total_volume_m3": q(delivery_total),
            "gas_block_delivery_raw_trucks": q(delivery_total / d(data.gas_block_delivery_truck_capacity_m3)),
            "gas_block_delivery_trucks": delivery_trucks,
            "main_walls_crane_shifts": data.main_walls_crane_shifts,
        },
        "parapet": {
            "parapet_masonry_volume_m3": q(parapet_volume),
            "parapet_upper_level_total_volume_m3": q(parapet_upper_total_volume),
            "parapet_and_upper_level_d400": parapet_upper_d400,
            "parapet_d400_delivery_control": {
                "order_volume_m3": q(parapet_delivery_order_volume),
                "notes": "Delivery split from combined parapet+second-light D400 order volume.",
            },
            "parapet_chasing_base_length_m": data.parapet_chasing_base_length_m,
            "parapet_rebar_base_length_m": data.parapet_rebar_base_length_m,
            "parapet_rebar_order_length_m": parapet_rebar["order_length_m"],
            "parapet_crane_shifts": data.parapet_crane_shifts,
        },
        "second_light_addon": {
            "second_light_masonry_enabled": data.second_light_masonry_enabled,
            "second_light_masonry_case_specific": data.second_light_masonry_case_specific,
            "second_light_masonry_volume_m3": q(second_light_volume),
            "second_light_d400_delivery_control": second_light_d400,
            "second_light_chasing_base_length_m": data.second_light_chasing_base_length_m,
            "second_light_chasing_case_specific": data.second_light_masonry_case_specific,
            "second_light_rebar_base_length_m": data.second_light_rebar_base_length_m,
            "second_light_rebar_order_length_m": second_light_rebar["order_length_m"],
            "second_light_rebar_case_specific": data.second_light_masonry_case_specific,
        },
        "vent_chimney_cladding": {
            "vent_chimney_cladding_area_m2": q(vent_area, "0.0000000001"),
            "vent_chimney_display_area_m2": q(vent_area, "0.01"),
            "vent_chimney_d500_150": vent_d500,
            "vent_chimney_total_length_m": q(vent_total_length),
            "vent_chimney_height_m": q(vent_height),
            "vent_chimney_geometry_volume_m3": q(vent_geometry_volume),
        },
        "overheads": {
            "second_light_adhesive_raw_bags": q(second_light_adhesive_raw),
            "second_light_adhesive_bags": second_light_adhesive_bags,
            "parapet_vent_adhesive_raw_bags": q(parapet_vent_adhesive_raw),
            "parapet_vent_adhesive_bags": parapet_vent_adhesive_bags,
            "parapet_upper_level_adhesive_bags": second_light_adhesive_bags + parapet_vent_adhesive_bags,
            "parapet_rebar": parapet_rebar,
            "second_light_rebar": second_light_rebar,
            "parapet_and_second_light_rebar_order_length_m": q(d(parapet_rebar["order_length_m"]) + d(second_light_rebar["order_length_m"])),
            "walls_consumables_tool_amortization_amount_raw": data.walls_consumables_tool_amortization_amount_raw,
        },
    }


def calculate_lines(data: LoadBearingWallsLintelsInput, b: dict[str, Any]) -> list[EstimateLineResult]:
    cutoff = b["cutoff_waterproofing"]
    main = b["main_walls"]
    gas = b["main_gas_blocks"]
    adh = b["adhesive_and_sand_concrete"]
    lintels = b["lintels"]
    reinf = b["main_wall_reinforcement"]
    delivery = b["deliveries_and_cranes"]
    parapet = b["parapet"]
    second = b["second_light_addon"]
    vent = b["vent_chimney_cladding"]
    overheads = b["overheads"]

    lintel_rebar_lines = []
    for item in data.lintel_rebar_items:
        _, rebar_line = rebar_from_weight(item, data.rebar_waste_coeff)
        lintel_rebar_lines.append(rebar_line)

    return [
        line("scaffolding_setup_dismantling", "Устройство лесов, подмостей для кладки, демонтаж лесов", "компл", data.scaffolding_setup_quantity, work_unit_price=data.scaffolding_setup_work_unit_price, notes="standard/fixed work line"),
        line("scaffolding_timber_material", "Пиломатериал для устройства лесов", "м3", data.scaffolding_timber_quantity_m3, material_unit_price=data.scaffolding_timber_unit_price, notes="standard/fixed material line"),
        line("cutoff_waterproofing_under_first_row_blocks", "Гидроизоляция поверхности под первый ряд блоков", "м2", cutoff["cutoff_waterproofing_area_m2"], material_unit_price=data.cutoff_waterproofing_material_unit_price, work_unit_price=data.cutoff_waterproofing_work_unit_price, notes="Не включает перегородки 150 мм"),
        line("main_load_bearing_wall_masonry_work", "Кладка внешних, внутренних стен из газобетонных блоков", "м3", main["main_masonry_volume_m3"], work_unit_price=data.main_wall_masonry_work_unit_price, notes="Работа по проектному объёму без запаса"),
        line("main_gas_block_d400_600x400x250_material", "Газобетонный блок D400 600x400x250 мм", "м3", gas["d400"]["order_volume_m3"], material_unit_price=data.gas_block_d400_unit_price),
        line("main_gas_block_d500_600x250x250_material", "Газобетонный блок D500 600x250x250 мм", "м3", gas["d500_250"]["order_volume_m3"], material_unit_price=data.gas_block_d500_250_unit_price),
        line("main_gas_block_adhesive", "Монтажный клей для блоков 25 кг", "мешок", adh["main_adhesive_bags"], material_unit_price=data.adhesive_unit_price),
        line("sand_concrete_m300_first_row", "Пескобетон М300 40 кг", "шт", adh["sand_concrete_bags"], material_unit_price=data.sand_concrete_unit_price),
        line("u_block_lintel_cutting", "Резка блока под перемычку (U-блок)", "шт", lintels["u_block_quantity"], work_unit_price=data.u_block_cutting_work_unit_price),
        line("main_wall_chasing_for_d10_reinforcement", "Штробление блоков под армирование Ø10", "мп", reinf["main_wall_chasing_quantity_m"], notes="Нулевая строка серой части, база для арматуры Ø10"),
        line("main_wall_rebar_a500_d10", "Арматура A500 Ø10 для несущих стен", "мп", reinf["main_wall_rebar_a500_d10"]["order_length_m"], material_unit_price=data.rebar_a500_d10_unit_price_per_m),
        line("gas_blocks_and_mix_delivery", "Доставка блоков, смеси", "маш", delivery["gas_block_delivery_trucks"], material_unit_price=data.gas_block_delivery_unit_price, notes="По закупочным объёмам после поддонов"),
        line("gas_blocks_unloading_manipulator", "Разгрузка блоков, смеси манипулятором", "маш", delivery["gas_block_delivery_trucks"], material_unit_price=data.gas_block_unloading_manipulator_unit_price),
        line("main_walls_blocks_crane_moving_25t", "Перемещение блоков, смеси автокраном 25 т", "смена", data.main_walls_crane_shifts, material_unit_price=data.crane_25t_unit_price, notes="manual/fixed по сменам"),
        line("lintel_rebar_frame_assembly", "Изготовление и монтаж каркаса армирования перемычек", "мп", lintels["lintel_rebar_frame_assembly_quantity_m"], notes="Нулевая агрегирующая строка"),
        *lintel_rebar_lines,
        line("lintel_concreting_work", "Бетонирование перемычек", "мп", lintels["lintel_total_length_m"], work_unit_price=data.lintel_concreting_work_unit_price),
        line("lintel_concrete_b22_5_m300_material", "Бетон В22,5 М300 для перемычек", "м3", lintels["lintel_concrete_order_volume_m3"], material_unit_price=data.concrete_m300_unit_price, notes="Минимум 1 м3"),
        line("lintel_concrete_delivery", "Доставка бетона до объекта", "рейс", data.concrete_delivery_trips, material_unit_price=data.concrete_delivery_unit_price),
        line("manual_concrete_lifting", "Перенос, подъём бетона вручную", "м3", lintels["lintel_concrete_order_volume_m3"], work_unit_price=data.manual_concrete_lifting_work_unit_price),
        line("parapet_and_upper_level_masonry_work", "Кладка парапета и верхнего уровня", "м3", parapet["parapet_upper_level_total_volume_m3"], work_unit_price=data.parapet_masonry_work_unit_price, is_case_specific=data.second_light_masonry_case_specific, notes="Парапет постоянный; второй свет case_specific addon"),
        line("parapet_and_upper_level_gas_block_d400_material", "Газобетонный блок D400 для парапета и верхнего уровня", "м3", parapet["parapet_and_upper_level_d400"]["order_volume_m3"], material_unit_price=data.gas_block_d400_unit_price, is_case_specific=data.second_light_masonry_case_specific, notes="Объединено, чтобы не перезакладывать лишний поддон"),
        line(
            "vent_chimney_gas_block_cladding_work",
            "Обкладка дымохода и вентканалов 150 мм",
            "м2",
            vent["vent_chimney_cladding_area_m2"],
            display_quantity=vent["vent_chimney_display_area_m2"],
            work_unit_price=data.vent_chimney_cladding_work_unit_price,
            work_total_raw_override=d(data.vent_chimney_gas_block_spec_volume_m3) / d(data.vent_chimney_block_thickness_m) * d(data.vent_chimney_cladding_work_unit_price),
        ),
        line("vent_chimney_gas_block_d500_600x150x250_material", "Газобетонный блок D500 600x150x250 мм", "м3", vent["vent_chimney_d500_150"]["order_volume_m3"], material_unit_price=data.gas_block_d500_150_unit_price),
        line("parapet_upper_level_adhesive", "Монтажный клей для парапета и верхнего уровня", "мешок", overheads["parapet_upper_level_adhesive_bags"], material_unit_price=data.adhesive_unit_price, is_case_specific=data.second_light_masonry_case_specific, notes="Две группы округления: second_light отдельно; parapet + vent/chimney вместе"),
        line("parapet_blocks_crane_moving", "Перемещение блоков, смеси автокраном для парапета", "смена", data.parapet_crane_shifts, material_unit_price=data.crane_25t_unit_price),
        line("parapet_and_second_light_chasing_for_d10_reinforcement", "Штробление парапета и второго света", "мп", d(data.parapet_chasing_base_length_m) + d(data.second_light_chasing_base_length_m), is_case_specific=data.second_light_masonry_case_specific, notes="Нулевая строка серой части"),
        line("parapet_and_second_light_rebar_a500_d10", "Арматура A500 Ø10 для парапета и второго света", "мп", overheads["parapet_and_second_light_rebar_order_length_m"], material_unit_price=data.rebar_a500_d10_unit_price_per_m, material_total_raw_override=overheads["parapet_rebar"]["material_total_raw"] + overheads["second_light_rebar"]["material_total_raw"], is_case_specific=data.second_light_masonry_case_specific, notes="Две группы округления и закупки прутков"),
        line("walls_consumables_tool_amortization", "Расходные материалы, амортизация инструмента", "комплект", 1, material_unit_price=money(data.walls_consumables_tool_amortization_amount_raw), material_total_raw_override=data.walls_consumables_tool_amortization_amount_raw, notes="manual/fixed amount, формула требует подтверждения"),
        line("construction_waste_removal", "Вывоз мусора с объекта", "маш", data.waste_removal_trucks, material_unit_price=data.waste_removal_truck_unit_price, work_unit_price=data.waste_removal_work_unit_price, notes="manual/fixed line"),
        line("walls_technical_supervision", "Технический надзор", "-", 1, work_unit_price=data.technical_supervision_amount),
    ]


def totals(lines: list[EstimateLineResult]) -> dict[str, Any]:
    material_raw = sum(d(x.material_total_raw) for x in lines)
    work_raw = sum(d(x.work_total_raw) for x in lines)
    total_raw = material_raw + work_raw
    return {
        "internal_materials_total_raw": q(material_raw, "0.001"),
        "internal_materials_total": money(material_raw),
        "internal_works_total_raw": q(work_raw, "0.001"),
        "internal_works_total": money(work_raw),
        "internal_section_total_raw": q(total_raw, "0.001"),
        "internal_section_total": money(total_raw),
        "sum_of_displayed_line_material_totals": sum(x.material_total for x in lines),
        "sum_of_displayed_line_work_totals": sum(x.work_total for x in lines),
        "sum_of_displayed_line_totals": sum(x.line_total for x in lines),
    }


def calculate_load_bearing_walls_lintels(data: LoadBearingWallsLintelsInput) -> dict[str, Any]:
    blocks = calculate_blocks(data)
    lines = calculate_lines(data, blocks)
    return {
        "inputs": data.to_dict(),
        "calculation_blocks": blocks,
        "estimate_lines": [x.to_dict() for x in lines],
        "internal_totals": totals(lines),
        "warnings": [],
    }
