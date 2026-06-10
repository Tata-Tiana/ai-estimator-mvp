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
class SpecRebarItem:
    floor: int
    component: str
    steel_class: str
    diameter_mm: int
    spec_length_m: float
    kg_per_meter: float | None = None
    rod_length_m: float | None = None
    unit_price_per_m: float | None = None
    code: str | None = None
    name: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SpecRebarItem":
        return cls(**data)


@dataclass(frozen=True)
class LoadBearingWallsLintelsInput:
    project_name: str
    scaffolding_setup_work_unit_price: float
    scaffolding_timber_unit_price: float
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
    crane_25t_unit_price: float
    lintel_rebar_items: list[RebarItem | SpecRebarItem | dict[str, Any]]
    lintel_concreting_work_unit_price: float
    concrete_waste_coeff: float
    concrete_m300_unit_price: float
    concrete_delivery_trips: float
    concrete_delivery_unit_price: float
    manual_concrete_lifting_work_unit_price: float
    parapet_masonry_work_unit_price: float
    vent_chimney_cladding_work_unit_price: float
    gas_block_d500_150_pallet_volume_m3: float
    gas_block_d500_150_unit_price: float
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
    lintel_section_width_m: float = 0.125
    lintel_section_height_m: float = 0.125
    lintel_concrete_calc_method: str = "legacy_length_section"
    lintel_concrete_spec_volume_m3: float | None = None
    lintel_concrete_min_order_volume_m3: float = 1.0
    scaffolding_calc_method: str = "legacy_direct_quantity"
    scaffolding_setup_quantity: float | None = None
    scaffolding_timber_quantity_m3: float | None = None
    floors_count: int = 1
    scaffolding_setup_units_per_floor: float = 1.0
    scaffolding_timber_m3_per_floor: float = 1.0
    cutoff_waterproofing_calc_method: str = "legacy_lengths_by_wall_thickness"
    cutoff_waterproofing_load_bearing_walls_area_m2: float | None = None
    cutoff_waterproofing_wall_400_lengths_m: list[float] | None = None
    cutoff_waterproofing_wall_250_lengths_m: list[float] | None = None
    wall_400_thickness_m: float | None = None
    wall_250_thickness_m: float | None = None
    lintel_length_calc_method: str = "legacy_length_count_items"
    lintel_total_length_m: float | None = None
    lintel_lengths_m: list[LintelLength | dict[str, Any]] | None = None
    main_wall_rebar_calc_method: str = "legacy_wall_geometry"
    main_wall_rebar_items: list[SpecRebarItem | dict[str, Any]] | None = None
    lintel_rebar_calc_method: str = "legacy_weight_items"
    main_walls_crane_calc_method: str = "legacy_manual_shifts"
    main_walls_crane_shifts: float | None = None
    upper_floor_calc_method: str = "legacy_second_light_addon"
    floor_2_masonry_volume_m3: float | None = None
    second_light_masonry_enabled: bool | None = None
    second_light_masonry_case_specific: bool | None = None
    second_light_masonry_volume_m3: float | None = None
    parapet_calc_method: str = "legacy_manual_toggle"
    flat_roof_enabled: bool = False
    parapet_enabled: bool | None = None
    parapet_masonry_volume_m3: float | None = None
    vent_chimney_cladding_calc_method: str = "legacy_manual_toggle"
    vent_chimney_cladding_enabled: bool | None = None
    vent_chimney_gas_block_spec_volume_m3: float | None = None
    vent_chimney_geometry_calc_method: str = "legacy_segments_rows"
    vent_chimney_block_thickness_m: float = 0.15
    vent_chimney_segment_lengths_m: list[dict[str, Any]] | None = None
    vent_chimney_rows: float | None = None
    block_height_m: float = 0.25

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "lintel_lengths_m",
            [x if isinstance(x, LintelLength) else LintelLength.from_dict(x) for x in (self.lintel_lengths_m or [])],
        )
        object.__setattr__(
            self,
            "lintel_rebar_items",
            [
                x
                if isinstance(x, (RebarItem, SpecRebarItem))
                else (SpecRebarItem.from_dict(x) if self.lintel_rebar_calc_method == "spec_length_items" else RebarItem.from_dict(x))
                for x in self.lintel_rebar_items
            ],
        )
        object.__setattr__(
            self,
            "main_wall_rebar_items",
            [
                x if isinstance(x, SpecRebarItem) else SpecRebarItem.from_dict(x)
                for x in (self.main_wall_rebar_items or [])
            ],
        )
        self.validate()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LoadBearingWallsLintelsInput":
        return cls(**data)

    def validate(self) -> None:
        if not self.project_name:
            raise ValueError("project_name is required")
        if self.floors_count not in {1, 2}:
            raise ValueError("floors_count must be 1 or 2. Three-storey houses are out of MVP scope.")
        if self.upper_floor_calc_method not in {"legacy_second_light_addon", "floor_2_spec_volume"}:
            raise ValueError("upper_floor_calc_method must be legacy_second_light_addon or floor_2_spec_volume")
        if self.upper_floor_calc_method == "legacy_second_light_addon":
            if self.second_light_masonry_enabled is None:
                raise ValueError("second_light_masonry_enabled is required for legacy_second_light_addon")
            if self.second_light_masonry_case_specific is None:
                raise ValueError("second_light_masonry_case_specific is required for legacy_second_light_addon")
            if self.second_light_masonry_volume_m3 is None:
                raise ValueError("second_light_masonry_volume_m3 is required for legacy_second_light_addon")
        if self.upper_floor_calc_method == "floor_2_spec_volume":
            if self.floors_count == 2 and self.floor_2_masonry_volume_m3 is None:
                raise ValueError("floor_2_masonry_volume_m3 is required for floor_2_spec_volume when floors_count is 2")
            if self.floor_2_masonry_volume_m3 is not None:
                require_non_negative("floor_2_masonry_volume_m3", self.floor_2_masonry_volume_m3)
        if self.parapet_calc_method not in {"legacy_manual_toggle", "flat_roof_spec_volume"}:
            raise ValueError("parapet_calc_method must be legacy_manual_toggle or flat_roof_spec_volume")
        if self.parapet_calc_method == "legacy_manual_toggle":
            if self.parapet_enabled is None:
                raise ValueError("parapet_enabled is required for legacy_manual_toggle")
            if self.parapet_masonry_volume_m3 is None:
                raise ValueError("parapet_masonry_volume_m3 is required for legacy_manual_toggle")
        if self.parapet_calc_method == "flat_roof_spec_volume":
            if self.flat_roof_enabled and self.parapet_masonry_volume_m3 is None:
                raise ValueError("parapet_masonry_volume_m3 is required for flat_roof_spec_volume when flat_roof_enabled is true")
            if self.parapet_masonry_volume_m3 is not None:
                require_non_negative("parapet_masonry_volume_m3", self.parapet_masonry_volume_m3)
        if self.vent_chimney_cladding_calc_method not in {"legacy_manual_toggle", "flat_roof_spec_volume"}:
            raise ValueError("vent_chimney_cladding_calc_method must be legacy_manual_toggle or flat_roof_spec_volume")
        if self.vent_chimney_cladding_calc_method == "legacy_manual_toggle":
            if self.vent_chimney_cladding_enabled is None:
                raise ValueError("vent_chimney_cladding_enabled is required for legacy_manual_toggle")
            if self.vent_chimney_gas_block_spec_volume_m3 is None:
                raise ValueError("vent_chimney_gas_block_spec_volume_m3 is required for legacy_manual_toggle")
        if self.vent_chimney_cladding_calc_method == "flat_roof_spec_volume":
            if self.flat_roof_enabled and self.vent_chimney_gas_block_spec_volume_m3 is None:
                raise ValueError("vent_chimney_gas_block_spec_volume_m3 is required for flat_roof_spec_volume when flat_roof_enabled is true")
            if self.vent_chimney_gas_block_spec_volume_m3 is not None:
                require_non_negative("vent_chimney_gas_block_spec_volume_m3", self.vent_chimney_gas_block_spec_volume_m3)
        if self.vent_chimney_geometry_calc_method not in {"legacy_segments_rows", "spec_volume_thickness"}:
            raise ValueError("vent_chimney_geometry_calc_method must be legacy_segments_rows or spec_volume_thickness")
        require_positive("vent_chimney_block_thickness_m", self.vent_chimney_block_thickness_m)
        if self.vent_chimney_geometry_calc_method == "legacy_segments_rows":
            if self.vent_chimney_segment_lengths_m is None:
                raise ValueError("vent_chimney_segment_lengths_m is required for legacy_segments_rows")
            if self.vent_chimney_rows is None:
                raise ValueError("vent_chimney_rows is required for legacy_segments_rows")
            require_positive("vent_chimney_rows", self.vent_chimney_rows)
            require_positive("block_height_m", self.block_height_m)
            for segment in self.vent_chimney_segment_lengths_m:
                require_non_negative("vent_chimney_segment_lengths_m.length_m", segment["length_m"])
                require_non_negative("vent_chimney_segment_lengths_m.count", segment["count"])
        if self.scaffolding_calc_method not in {"legacy_direct_quantity", "floors_based"}:
            raise ValueError("scaffolding_calc_method must be legacy_direct_quantity or floors_based")
        if self.scaffolding_calc_method == "legacy_direct_quantity":
            if self.scaffolding_setup_quantity is None:
                raise ValueError("scaffolding_setup_quantity is required for legacy_direct_quantity")
            if self.scaffolding_timber_quantity_m3 is None:
                raise ValueError("scaffolding_timber_quantity_m3 is required for legacy_direct_quantity")
        if self.scaffolding_calc_method == "floors_based":
            require_non_negative("scaffolding_setup_units_per_floor", self.scaffolding_setup_units_per_floor)
            require_non_negative("scaffolding_timber_m3_per_floor", self.scaffolding_timber_m3_per_floor)
        if self.cutoff_waterproofing_calc_method not in {"legacy_lengths_by_wall_thickness", "spec_area"}:
            raise ValueError("cutoff_waterproofing_calc_method must be legacy_lengths_by_wall_thickness or spec_area")
        if self.cutoff_waterproofing_calc_method == "legacy_lengths_by_wall_thickness":
            if self.cutoff_waterproofing_wall_400_lengths_m is None:
                raise ValueError("cutoff_waterproofing_wall_400_lengths_m is required for legacy_lengths_by_wall_thickness")
            if self.cutoff_waterproofing_wall_250_lengths_m is None:
                raise ValueError("cutoff_waterproofing_wall_250_lengths_m is required for legacy_lengths_by_wall_thickness")
            if self.wall_400_thickness_m is None:
                raise ValueError("wall_400_thickness_m is required for legacy_lengths_by_wall_thickness")
            if self.wall_250_thickness_m is None:
                raise ValueError("wall_250_thickness_m is required for legacy_lengths_by_wall_thickness")
            require_positive("wall_400_thickness_m", self.wall_400_thickness_m)
            require_positive("wall_250_thickness_m", self.wall_250_thickness_m)
        if self.cutoff_waterproofing_calc_method == "spec_area":
            if self.cutoff_waterproofing_load_bearing_walls_area_m2 is None:
                raise ValueError("cutoff_waterproofing_load_bearing_walls_area_m2 is required for spec_area")
            require_non_negative(
                "cutoff_waterproofing_load_bearing_walls_area_m2",
                self.cutoff_waterproofing_load_bearing_walls_area_m2,
            )
        if self.lintel_length_calc_method not in {"legacy_length_count_items", "spec_total_length"}:
            raise ValueError("lintel_length_calc_method must be legacy_length_count_items or spec_total_length")
        if self.lintel_length_calc_method == "legacy_length_count_items":
            if not self.lintel_lengths_m:
                raise ValueError("lintel_lengths_m is required for legacy_length_count_items")
        if self.lintel_length_calc_method == "spec_total_length":
            if self.lintel_total_length_m is None:
                raise ValueError("lintel_total_length_m is required for spec_total_length")
            require_non_negative("lintel_total_length_m", self.lintel_total_length_m)
        if self.main_wall_rebar_calc_method not in {"legacy_wall_geometry", "spec_length_items"}:
            raise ValueError("main_wall_rebar_calc_method must be legacy_wall_geometry or spec_length_items")
        if self.main_wall_rebar_calc_method == "spec_length_items":
            if not self.main_wall_rebar_items:
                raise ValueError("main_wall_rebar_items is required for spec_length_items")
            for item in self.main_wall_rebar_items:
                validate_spec_rebar_item(item, "load_bearing_walls")
        if self.lintel_rebar_calc_method not in {"legacy_weight_items", "spec_length_items"}:
            raise ValueError("lintel_rebar_calc_method must be legacy_weight_items or spec_length_items")
        if self.lintel_rebar_calc_method == "legacy_weight_items":
            for item in self.lintel_rebar_items:
                if not isinstance(item, RebarItem):
                    raise ValueError("legacy_weight_items requires weight-based lintel_rebar_items")
        if self.lintel_rebar_calc_method == "spec_length_items":
            for item in self.lintel_rebar_items:
                if not isinstance(item, SpecRebarItem):
                    raise ValueError("spec_length_items requires spec-length lintel_rebar_items")
                validate_spec_rebar_item(item, "lintels")
        if self.lintel_concrete_calc_method not in {"legacy_length_section", "spec_volume"}:
            raise ValueError("lintel_concrete_calc_method must be legacy_length_section or spec_volume")
        if self.lintel_concrete_calc_method == "spec_volume":
            if self.lintel_concrete_spec_volume_m3 is None:
                raise ValueError("lintel_concrete_spec_volume_m3 is required for spec_volume")
            require_non_negative("lintel_concrete_spec_volume_m3", self.lintel_concrete_spec_volume_m3)
        if self.main_walls_crane_calc_method not in {"legacy_manual_shifts", "delivery_trucks_threshold"}:
            raise ValueError("main_walls_crane_calc_method must be legacy_manual_shifts or delivery_trucks_threshold")
        if self.main_walls_crane_calc_method == "legacy_manual_shifts" and self.main_walls_crane_shifts is None:
            raise ValueError("main_walls_crane_shifts is required for legacy_manual_shifts")
        for name in [
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
            "lintel_concrete_min_order_volume_m3",
            "gas_block_d500_150_pallet_volume_m3",
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
    price_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        if self.display_quantity is None:
            result.pop("display_quantity")
        if self.price_code is None:
            result.pop("price_code")
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
    price_code: str | None = None,
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
        price_code=price_code,
    )


def rebar_price_code(steel_class: str, diameter_mm: int) -> str:
    return f"rebar_{steel_class.lower()}_d{diameter_mm}_m"


def make_rebar_price_code(steel_class: str, diameter_mm: int) -> str:
    return rebar_price_code(steel_class, diameter_mm)


def component_label(component: str) -> str:
    labels = {
        "load_bearing_walls": "несущих стен",
        "lintels": "перемычек",
    }
    return labels.get(component, component)


def make_rebar_line_code(component: str, floor: int, steel_class: str, diameter_mm: int) -> str:
    return f"{component}_floor_{floor}_rebar_{steel_class.lower()}_d{diameter_mm}"


def make_rebar_name(component: str, floor: int, steel_class: str, diameter_mm: int) -> str:
    return f"Арматура {steel_class} Ø{diameter_mm} для {component_label(component)}, этаж {floor}"


def validate_spec_rebar_item(item: SpecRebarItem, expected_component: str) -> None:
    if item.component == "partitions":
        raise ValueError("partitions rebar must be calculated in partitions calculator, not in load_bearing_walls_lintels_calculator")
    if item.component != expected_component:
        raise ValueError(f"rebar component must be {expected_component}")
    if item.floor < 1:
        raise ValueError("rebar floor must be greater than or equal to 1")
    require_positive("diameter_mm", item.diameter_mm)
    require_non_negative("spec_length_m", item.spec_length_m)
    if item.kg_per_meter is None:
        raise ValueError("kg_per_meter is required for spec_length_items")
    if item.rod_length_m is None:
        raise ValueError("rod_length_m is required for spec_length_items")
    if item.unit_price_per_m is None:
        raise ValueError("unit_price_per_m is required for spec_length_items")
    require_positive("kg_per_meter", item.kg_per_meter)
    require_positive("rod_length_m", item.rod_length_m)
    require_non_negative("unit_price_per_m", item.unit_price_per_m)


def gas_block_order(spec_volume: float, waste_coeff: float, pallet_volume: float) -> dict[str, Any]:
    required = d(spec_volume) * d(waste_coeff)
    raw_pallets = required / d(pallet_volume)
    pallets = int(ceil(raw_pallets))
    order_volume = d(pallets) * d(pallet_volume)
    blocks = {
        "spec_volume_m3": q(spec_volume),
        "required_volume_m3": q(required),
        "raw_pallets": q(raw_pallets),
        "pallets": pallets,
        "order_volume_m3": q(order_volume),
    }
    return blocks


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
        price_code=rebar_price_code(item.steel_class, item.diameter_mm),
    )


def rebar_from_spec_length(item: SpecRebarItem, waste_coeff: float) -> tuple[dict[str, Any], EstimateLineResult]:
    if item.kg_per_meter is None or item.rod_length_m is None or item.unit_price_per_m is None:
        raise ValueError("spec rebar item requires kg_per_meter, rod_length_m and unit_price_per_m")
    base_length = d(item.spec_length_m)
    length_with_waste = base_length * d(waste_coeff)
    raw_rods = length_with_waste / d(item.rod_length_m)
    rods = int(ceil(raw_rods))
    order_length = d(rods) * d(item.rod_length_m)
    delivery_weight = order_length * d(item.kg_per_meter)
    line_code = item.code or make_rebar_line_code(item.component, item.floor, item.steel_class, item.diameter_mm)
    line_name = item.name or make_rebar_name(item.component, item.floor, item.steel_class, item.diameter_mm)
    price_code = make_rebar_price_code(item.steel_class, item.diameter_mm)
    control = {
        "floor": item.floor,
        "component": item.component,
        "steel_class": item.steel_class,
        "diameter_mm": item.diameter_mm,
        "spec_length_m": q(base_length),
        "length_with_waste_m": q(length_with_waste),
        "raw_rods": q(raw_rods),
        "rods": rods,
        "order_length_m": q(order_length),
        "kg_per_meter": item.kg_per_meter,
        "delivery_weight_kg": q(delivery_weight),
        "unit_price_per_m": item.unit_price_per_m,
        "price_code": price_code,
        "line_code": line_code,
        "line_name": line_name,
    }
    return control, line(
        code=line_code,
        name=line_name,
        unit="мп",
        quantity=q(order_length),
        material_unit_price=item.unit_price_per_m,
        price_code=price_code,
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


def calculate_scaffolding(data: LoadBearingWallsLintelsInput) -> dict[str, Any]:
    if data.scaffolding_calc_method == "legacy_direct_quantity":
        if data.scaffolding_setup_quantity is None or data.scaffolding_timber_quantity_m3 is None:
            raise ValueError("legacy scaffolding calculation requires direct setup and timber quantities")
        return {
            "scaffolding_calc_method": data.scaffolding_calc_method,
            "scaffolding_source": "legacy_direct_quantity",
            "floors_count": data.floors_count,
            "setup_units_per_floor": data.scaffolding_setup_units_per_floor,
            "timber_m3_per_floor": data.scaffolding_timber_m3_per_floor,
            "setup_quantity": q(data.scaffolding_setup_quantity),
            "timber_quantity_m3": q(data.scaffolding_timber_quantity_m3),
        }

    if data.scaffolding_calc_method == "floors_based":
        if data.floors_count is None:
            raise ValueError("floors_count is required for floors_based scaffolding calculation")
        setup_quantity = d(data.floors_count) * d(data.scaffolding_setup_units_per_floor)
        timber_quantity = d(data.floors_count) * d(data.scaffolding_timber_m3_per_floor)
        return {
            "scaffolding_calc_method": data.scaffolding_calc_method,
            "scaffolding_source": "floors_based",
            "floors_count": data.floors_count,
            "setup_units_per_floor": data.scaffolding_setup_units_per_floor,
            "timber_m3_per_floor": data.scaffolding_timber_m3_per_floor,
            "setup_quantity": q(setup_quantity),
            "timber_quantity_m3": q(timber_quantity),
        }

    raise ValueError(f"Unknown scaffolding_calc_method: {data.scaffolding_calc_method}")


def calculate_cutoff_waterproofing(data: LoadBearingWallsLintelsInput) -> dict[str, Any]:
    if data.cutoff_waterproofing_calc_method == "legacy_lengths_by_wall_thickness":
        if (
            data.cutoff_waterproofing_wall_400_lengths_m is None
            or data.cutoff_waterproofing_wall_250_lengths_m is None
            or data.wall_400_thickness_m is None
            or data.wall_250_thickness_m is None
        ):
            raise ValueError("legacy cutoff waterproofing calculation requires wall lengths and thicknesses")
        wall_400_length = d(sum(data.cutoff_waterproofing_wall_400_lengths_m))
        wall_250_length = d(sum(data.cutoff_waterproofing_wall_250_lengths_m))
        cutoff_area = wall_400_length * d(data.wall_400_thickness_m) + wall_250_length * d(data.wall_250_thickness_m)
        return {
            "cutoff_waterproofing_calc_method": data.cutoff_waterproofing_calc_method,
            "cutoff_waterproofing_source": "legacy_lengths_by_wall_thickness",
            "cutoff_waterproofing_load_bearing_walls_area_m2": None,
            "wall_400_length_m": q(wall_400_length),
            "wall_250_length_m": q(wall_250_length),
            "cutoff_waterproofing_area_m2": q(cutoff_area),
        }

    if data.cutoff_waterproofing_calc_method == "spec_area":
        if data.cutoff_waterproofing_load_bearing_walls_area_m2 is None:
            raise ValueError("cutoff_waterproofing_load_bearing_walls_area_m2 is required for spec_area")
        return {
            "cutoff_waterproofing_calc_method": data.cutoff_waterproofing_calc_method,
            "cutoff_waterproofing_source": "spec_area",
            "cutoff_waterproofing_load_bearing_walls_area_m2": q(data.cutoff_waterproofing_load_bearing_walls_area_m2),
            "wall_400_length_m": None,
            "wall_250_length_m": None,
            "cutoff_waterproofing_area_m2": q(data.cutoff_waterproofing_load_bearing_walls_area_m2),
        }

    raise ValueError(f"Unknown cutoff_waterproofing_calc_method: {data.cutoff_waterproofing_calc_method}")


def calculate_main_walls_crane(data: LoadBearingWallsLintelsInput, gas_block_delivery_trucks: int) -> dict[str, Any]:
    if data.main_walls_crane_calc_method == "legacy_manual_shifts":
        if data.main_walls_crane_shifts is None:
            raise ValueError("main_walls_crane_shifts is required for legacy_manual_shifts")
        return {
            "main_walls_crane_calc_method": data.main_walls_crane_calc_method,
            "main_walls_crane_source": "legacy_manual_shifts",
            "gas_block_delivery_trucks": gas_block_delivery_trucks,
            "main_walls_crane_threshold_trucks": None,
            "main_walls_crane_shifts": q(data.main_walls_crane_shifts),
        }

    if data.main_walls_crane_calc_method == "delivery_trucks_threshold":
        crane_shifts = 1 if gas_block_delivery_trucks <= 3 else 2
        return {
            "main_walls_crane_calc_method": data.main_walls_crane_calc_method,
            "main_walls_crane_source": "delivery_trucks_threshold",
            "gas_block_delivery_trucks": gas_block_delivery_trucks,
            "main_walls_crane_threshold_trucks": 3,
            "main_walls_crane_shifts": crane_shifts,
        }

    raise ValueError(f"Unknown main_walls_crane_calc_method: {data.main_walls_crane_calc_method}")


def calculate_lintel_total_length(data: LoadBearingWallsLintelsInput) -> dict[str, Any]:
    if data.lintel_length_calc_method == "legacy_length_count_items":
        lintel_total_length = sum(d(x.length_m) * d(x.count) for x in data.lintel_lengths_m or [])
        return {
            "lintel_length_calc_method": data.lintel_length_calc_method,
            "lintel_length_source": "legacy_length_count_items",
            "lintel_total_length_m": q(lintel_total_length),
        }

    if data.lintel_length_calc_method == "spec_total_length":
        if data.lintel_total_length_m is None:
            raise ValueError("lintel_total_length_m is required for spec_total_length")
        return {
            "lintel_length_calc_method": data.lintel_length_calc_method,
            "lintel_length_source": "spec_total_length",
            "lintel_total_length_m": q(data.lintel_total_length_m),
        }

    raise ValueError(f"Unknown lintel_length_calc_method: {data.lintel_length_calc_method}")


def calculate_lintel_concrete(data: LoadBearingWallsLintelsInput, lintel_total_length_m: Decimal) -> dict[str, Any]:
    if data.lintel_concrete_calc_method == "legacy_length_section":
        raw_concrete = lintel_total_length_m * d(data.lintel_section_width_m) * d(data.lintel_section_height_m)
        required_concrete = raw_concrete * d(data.concrete_waste_coeff)
        source = "legacy_length_section"
        spec_volume = None
    elif data.lintel_concrete_calc_method == "spec_volume":
        if data.lintel_concrete_spec_volume_m3 is None:
            raise ValueError("lintel_concrete_spec_volume_m3 is required for spec_volume")
        raw_concrete = d(data.lintel_concrete_spec_volume_m3)
        required_concrete = raw_concrete
        source = "spec_volume"
        spec_volume = q(raw_concrete)
    else:
        raise ValueError(f"Unknown lintel_concrete_calc_method: {data.lintel_concrete_calc_method}")

    order_concrete = max(d(data.lintel_concrete_min_order_volume_m3), Decimal(ceil(required_concrete)))
    return {
        "lintel_concrete_calc_method": data.lintel_concrete_calc_method,
        "lintel_concrete_source": source,
        "lintel_concrete_spec_volume_m3": spec_volume,
        "lintel_section_width_m": data.lintel_section_width_m,
        "lintel_section_height_m": data.lintel_section_height_m,
        "lintel_raw_concrete_volume_m3": q(raw_concrete),
        "lintel_required_concrete_volume_m3": q(required_concrete),
        "lintel_concrete_min_order_volume_m3": q(data.lintel_concrete_min_order_volume_m3),
        "lintel_concrete_order_volume_m3": q(order_concrete),
    }


def calculate_main_wall_reinforcement(data: LoadBearingWallsLintelsInput) -> tuple[dict[str, Any], list[EstimateLineResult]]:
    if data.main_wall_rebar_calc_method == "legacy_wall_geometry":
        main_chasing_raw = (
            d(data.main_wall_reinforcement_rows) * d(data.main_wall_external_length_m) * d(data.main_wall_400_reinforcement_threads)
            + d(data.main_wall_internal_250_control_length_m) * d(data.main_wall_reinforcement_rows) * d(data.main_wall_250_reinforcement_threads)
        ) * d(data.main_wall_reinforcement_overlap_coeff)
        main_chasing_quantity = Decimal(ceil(main_chasing_raw))
        main_rebar = rebar_from_base_length(q(main_chasing_quantity), data.rebar_a500_d10_rod_length_m, data.rebar_waste_coeff, data.rebar_a500_d10_unit_price_per_m)
        block = {
            "main_wall_rebar_calc_method": data.main_wall_rebar_calc_method,
            "main_wall_rebar_source": "legacy_wall_geometry",
            "main_wall_chasing_raw_length_m": q(main_chasing_raw, "0.000001"),
            "main_wall_chasing_quantity_m": q(main_chasing_quantity),
            "main_wall_rebar_a500_d10": main_rebar,
            "main_wall_rebar_control_weight_kg": q(d(main_rebar["order_length_m"]) * d(data.rebar_a500_d10_kg_per_m)),
        }
        lines = [
            line("main_wall_rebar_a500_d10", "Арматура A500 Ø10 для несущих стен", "мп", main_rebar["order_length_m"], material_unit_price=data.rebar_a500_d10_unit_price_per_m, price_code="rebar_a500_d10_m")
        ]
        return block, lines

    controls: dict[str, Any] = {}
    rebar_lines: list[EstimateLineResult] = []
    for item in data.main_wall_rebar_items or []:
        control, rebar_line = rebar_from_spec_length(item, data.rebar_waste_coeff)
        controls[control["line_code"]] = control
        rebar_lines.append(rebar_line)
    base_length = sum(d(control["spec_length_m"]) for control in controls.values())
    order_length = sum(d(control["order_length_m"]) for control in controls.values())
    delivery_weight = sum(d(control["delivery_weight_kg"]) for control in controls.values())
    return {
        "main_wall_rebar_calc_method": data.main_wall_rebar_calc_method,
        "main_wall_rebar_source": "spec_length_items",
        "items": controls,
        "main_wall_rebar_base_length_m": q(base_length),
        "main_wall_rebar_order_length_m": q(order_length),
        "main_wall_rebar_delivery_weight_kg": q(delivery_weight),
        "main_wall_chasing_quantity_m": q(base_length),
    }, rebar_lines


def calculate_lintel_rebar(data: LoadBearingWallsLintelsInput) -> tuple[dict[str, Any], list[EstimateLineResult]]:
    controls: dict[str, Any] = {}
    rebar_lines: list[EstimateLineResult] = []
    if data.lintel_rebar_calc_method == "legacy_weight_items":
        for item in data.lintel_rebar_items:
            if not isinstance(item, RebarItem):
                raise ValueError("legacy lintel rebar requires RebarItem")
            control, rebar_line = rebar_from_weight(item, data.rebar_waste_coeff)
            controls[item.code] = control
            rebar_lines.append(rebar_line)
        frame_quantity = sum(d(x.quantity) for x in rebar_lines)
        delivery_weight = sum(d(control["order_length_m"]) * d(item.kg_per_meter) for control, item in zip(controls.values(), data.lintel_rebar_items))
        return {
            "lintel_rebar_calc_method": data.lintel_rebar_calc_method,
            "lintel_rebar_source": "legacy_weight_items",
            "rebar": controls,
            "lintel_rebar_frame_assembly_quantity_m": q(frame_quantity),
            "lintel_rebar_order_length_m": q(frame_quantity),
            "lintel_rebar_delivery_weight_kg": q(delivery_weight),
        }, rebar_lines

    for item in data.lintel_rebar_items:
        if not isinstance(item, SpecRebarItem):
            raise ValueError("spec lintel rebar requires SpecRebarItem")
        control, rebar_line = rebar_from_spec_length(item, data.rebar_waste_coeff)
        controls[control["line_code"]] = control
        rebar_lines.append(rebar_line)
    base_length = sum(d(control["spec_length_m"]) for control in controls.values())
    order_length = sum(d(control["order_length_m"]) for control in controls.values())
    delivery_weight = sum(d(control["delivery_weight_kg"]) for control in controls.values())
    return {
        "lintel_rebar_calc_method": data.lintel_rebar_calc_method,
        "lintel_rebar_source": "spec_length_items",
        "rebar": controls,
        "lintel_rebar_base_length_m": q(base_length),
        "lintel_rebar_order_length_m": q(order_length),
        "lintel_rebar_delivery_weight_kg": q(delivery_weight),
        "lintel_rebar_frame_assembly_quantity_m": q(order_length),
    }, rebar_lines


def calculate_blocks(data: LoadBearingWallsLintelsInput) -> dict[str, Any]:
    cutoff_waterproofing = calculate_cutoff_waterproofing(data)
    cutoff_area = d(cutoff_waterproofing["cutoff_waterproofing_area_m2"])
    lintel_length = calculate_lintel_total_length(data)
    lintel_total_length = d(lintel_length["lintel_total_length_m"])
    main_masonry_volume = d(data.main_wall_gas_block_400_spec_volume_m3) + d(data.main_wall_gas_block_250_spec_volume_m3)
    main_d400 = gas_block_order(data.main_wall_gas_block_400_spec_volume_m3, data.gas_block_waste_coeff, data.gas_block_d400_pallet_volume_m3)
    main_d500_250 = gas_block_order(data.main_wall_gas_block_250_spec_volume_m3, data.gas_block_waste_coeff, data.gas_block_d500_250_pallet_volume_m3)
    adhesive_raw = main_masonry_volume * d(data.adhesive_consumption_bag_per_m3) * d(data.adhesive_waste_coeff)
    sand_raw = cutoff_area * d(data.sand_concrete_consumption_kg_per_m2_per_10mm) * d(data.sand_concrete_thickness_factor) / d(data.sand_concrete_bag_weight_kg)
    u_block_quantity = lintel_total_length / d(data.gas_block_length_m)
    main_wall_reinforcement, _ = calculate_main_wall_reinforcement(data)
    lintel_rebar, _ = calculate_lintel_rebar(data)
    lintel_concrete = calculate_lintel_concrete(data, lintel_total_length)
    floor_2_enabled = data.floors_count == 2
    if data.upper_floor_calc_method == "legacy_second_light_addon":
        second_light_enabled = bool(data.second_light_masonry_enabled)
        second_light_case_specific = bool(data.second_light_masonry_case_specific)
        second_light_input_volume = d(data.second_light_masonry_volume_m3 or 0)
        second_light_volume = second_light_input_volume if second_light_enabled else Decimal("0")
        floor_2_volume = Decimal("0")
    else:
        second_light_enabled = False
        second_light_case_specific = False
        second_light_input_volume = Decimal("0")
        second_light_volume = Decimal("0")
        floor_2_volume = d(data.floor_2_masonry_volume_m3 or 0) if floor_2_enabled else Decimal("0")

    if data.parapet_calc_method == "legacy_manual_toggle":
        parapet_enabled = bool(data.parapet_enabled)
    else:
        parapet_enabled = bool(data.flat_roof_enabled and d(data.parapet_masonry_volume_m3 or 0) > 0)
    parapet_volume = d(data.parapet_masonry_volume_m3 or 0) if parapet_enabled else Decimal("0")

    if data.vent_chimney_cladding_calc_method == "legacy_manual_toggle":
        vent_enabled = bool(data.vent_chimney_cladding_enabled)
    else:
        vent_enabled = bool(data.flat_roof_enabled and d(data.vent_chimney_gas_block_spec_volume_m3 or 0) > 0)
    vent_spec_volume = d(data.vent_chimney_gas_block_spec_volume_m3 or 0) if vent_enabled else Decimal("0")

    floor_2_d400 = gas_block_order(q(floor_2_volume), data.gas_block_waste_coeff, data.gas_block_d400_pallet_volume_m3)
    floor_2_adhesive_raw = floor_2_volume * d(data.adhesive_consumption_bag_per_m3) * d(data.adhesive_waste_coeff)
    floor_2_adhesive_bags = int(ceil(floor_2_adhesive_raw))
    parapet_d400 = gas_block_order(q(parapet_volume), data.gas_block_waste_coeff, data.gas_block_d400_pallet_volume_m3)
    parapet_upper_total_volume = parapet_volume + second_light_volume
    parapet_upper_d400 = gas_block_order(q(parapet_upper_total_volume), data.gas_block_waste_coeff, data.gas_block_d400_pallet_volume_m3)
    second_light_d400 = gas_block_order(q(second_light_input_volume), data.gas_block_waste_coeff, data.gas_block_d400_pallet_volume_m3)
    # For delivery the Excel sheet splits the combined parapet+second-light purchase
    # into 15.05 and 23.65 m3, avoiding an extra pallet in the parapet subgroup.
    parapet_delivery_order_volume = d(parapet_upper_d400["order_volume_m3"]) - d(second_light_d400["order_volume_m3"])
    vent_area = vent_spec_volume / d(data.vent_chimney_block_thickness_m) if vent_enabled else Decimal("0")
    vent_d500 = gas_block_order(q(vent_spec_volume), data.gas_block_waste_coeff, data.gas_block_d500_150_pallet_volume_m3)
    vent_block = {
        "vent_chimney_cladding_calc_method": data.vent_chimney_cladding_calc_method,
        "vent_chimney_geometry_calc_method": data.vent_chimney_geometry_calc_method,
        "flat_roof_enabled": data.flat_roof_enabled,
        "vent_chimney_cladding_enabled_calculated": vent_enabled,
        "vent_chimney_gas_block_spec_volume_m3": q(vent_spec_volume),
        "vent_chimney_block_thickness_m": data.vent_chimney_block_thickness_m,
        "vent_chimney_cladding_area_m2": q(vent_area, "0.0000000001"),
        "vent_chimney_display_area_m2": q(vent_area, "0.01"),
        "vent_chimney_d500_150": vent_d500,
    }
    if data.vent_chimney_geometry_calc_method == "legacy_segments_rows":
        vent_total_length = sum(d(x["length_m"]) * d(x["count"]) for x in (data.vent_chimney_segment_lengths_m or []))
        vent_height = d(data.block_height_m) * d(data.vent_chimney_rows or 0)
        vent_geometry_volume = vent_total_length * vent_height * d(data.vent_chimney_block_thickness_m) if vent_enabled else Decimal("0")
        vent_block.update({
            "vent_chimney_segment_lengths_m": data.vent_chimney_segment_lengths_m,
            "vent_chimney_rows": data.vent_chimney_rows,
            "block_height_m": data.block_height_m,
            "vent_chimney_total_length_m": q(vent_total_length),
            "vent_chimney_height_m": q(vent_height),
            "vent_chimney_geometry_volume_m3": q(vent_geometry_volume),
        })
    if data.upper_floor_calc_method == "legacy_second_light_addon":
        delivery_total = d(main_d400["order_volume_m3"]) + d(main_d500_250["order_volume_m3"]) + d(second_light_d400["order_volume_m3"]) + parapet_delivery_order_volume + d(vent_d500["order_volume_m3"])
    else:
        delivery_total = d(main_d400["order_volume_m3"]) + d(main_d500_250["order_volume_m3"]) + d(floor_2_d400["order_volume_m3"]) + d(parapet_d400["order_volume_m3"]) + d(vent_d500["order_volume_m3"])
    delivery_trucks = int(ceil(delivery_total / d(data.gas_block_delivery_truck_capacity_m3)))
    main_walls_crane = calculate_main_walls_crane(data, delivery_trucks)
    second_light_adhesive_raw = second_light_volume * d(data.adhesive_consumption_bag_per_m3) * d(data.adhesive_waste_coeff)
    second_light_adhesive_bags = int(ceil(second_light_adhesive_raw))
    parapet_vent_adhesive_raw = (parapet_volume + vent_spec_volume) * d(data.adhesive_consumption_bag_per_m3) * d(data.adhesive_waste_coeff)
    parapet_vent_adhesive_bags = int(ceil(parapet_vent_adhesive_raw))
    second_light_rebar = rebar_from_base_length(data.second_light_rebar_base_length_m, data.rebar_a500_d10_rod_length_m, data.rebar_waste_coeff, data.rebar_a500_d10_unit_price_per_m)
    parapet_rebar = rebar_from_base_length(data.parapet_rebar_base_length_m, data.rebar_a500_d10_rod_length_m, data.rebar_waste_coeff, data.rebar_a500_d10_unit_price_per_m)
    if data.upper_floor_calc_method == "legacy_second_light_addon":
        parapet_delivery_note = "Delivery split from combined parapet+second-light D400 order volume."
    else:
        parapet_delivery_note = "Production parapet order volume calculated separately."

    blocks = {
        "scaffolding": calculate_scaffolding(data),
        "cutoff_waterproofing": cutoff_waterproofing,
        "main_walls": {"main_masonry_volume_m3": q(main_masonry_volume)},
        "main_gas_blocks": {"d400": main_d400, "d500_250": main_d500_250},
        "adhesive_and_sand_concrete": {
            "main_adhesive_raw_bags": q(adhesive_raw),
            "main_adhesive_bags": int(ceil(adhesive_raw)),
            "sand_concrete_raw_bags": q(sand_raw),
            "sand_concrete_bags": int(ceil(sand_raw)),
        },
        "lintels": {
            "lintel_length_calc_method": lintel_length["lintel_length_calc_method"],
            "lintel_length_source": lintel_length["lintel_length_source"],
            "lintel_total_length_m": q(lintel_total_length),
            "gas_block_length_m": data.gas_block_length_m,
            "u_block_quantity": q(u_block_quantity),
            "lintel_200mm_steps": q(lintel_total_length / d("0.2")),
            **lintel_concrete,
            **lintel_rebar,
        },
        "main_wall_reinforcement": main_wall_reinforcement,
        "floor_2_load_bearing_walls": {
            "floors_count": data.floors_count,
            "upper_floor_calc_method": data.upper_floor_calc_method,
            "enabled": floor_2_enabled if data.upper_floor_calc_method == "floor_2_spec_volume" else second_light_enabled,
            "floor_2_load_bearing_walls_enabled": floor_2_enabled,
            "floor_2_masonry_volume_m3": q(floor_2_volume),
            "floor_2_d400": floor_2_d400,
            "floor_2_adhesive_raw_bags": q(floor_2_adhesive_raw),
            "floor_2_adhesive_bags": floor_2_adhesive_bags,
        },
        "deliveries_and_cranes": {
            "gas_block_delivery_total_volume_m3": q(delivery_total),
            "gas_block_delivery_raw_trucks": q(delivery_total / d(data.gas_block_delivery_truck_capacity_m3)),
            **main_walls_crane,
        },
        "parapet": {
            "parapet_calc_method": data.parapet_calc_method,
            "flat_roof_enabled": data.flat_roof_enabled,
            "parapet_enabled_calculated": parapet_enabled,
            "parapet_masonry_volume_m3": q(parapet_volume),
            "parapet_d400": parapet_d400,
            "parapet_upper_level_total_volume_m3": q(parapet_upper_total_volume),
            "parapet_and_upper_level_d400": parapet_upper_d400,
            "parapet_d400_delivery_control": {
                "order_volume_m3": q(parapet_delivery_order_volume),
                "notes": parapet_delivery_note,
            },
            "parapet_chasing_base_length_m": data.parapet_chasing_base_length_m,
            "parapet_rebar_base_length_m": data.parapet_rebar_base_length_m,
            "parapet_rebar_order_length_m": parapet_rebar["order_length_m"],
            "parapet_crane_shifts": data.parapet_crane_shifts,
        },
        "vent_chimney_cladding": vent_block,
        "overheads": {
            "second_light_adhesive_raw_bags": q(second_light_adhesive_raw),
            "second_light_adhesive_bags": second_light_adhesive_bags,
            "parapet_vent_adhesive_raw_bags": q(parapet_vent_adhesive_raw),
            "parapet_vent_adhesive_bags": parapet_vent_adhesive_bags,
            "parapet_upper_level_adhesive_bags": second_light_adhesive_bags + parapet_vent_adhesive_bags,
            "floor_2_adhesive_raw_bags": q(floor_2_adhesive_raw),
            "floor_2_adhesive_bags": floor_2_adhesive_bags,
            "parapet_rebar": parapet_rebar,
            "second_light_rebar": second_light_rebar,
            "parapet_and_second_light_rebar_order_length_m": q(d(parapet_rebar["order_length_m"]) + d(second_light_rebar["order_length_m"])),
            "walls_consumables_tool_amortization_amount_raw": data.walls_consumables_tool_amortization_amount_raw,
        },
    }
    if data.upper_floor_calc_method != "legacy_second_light_addon":
        for key in (
            "second_light_adhesive_raw_bags",
            "second_light_adhesive_bags",
            "second_light_rebar",
            "parapet_and_second_light_rebar_order_length_m",
        ):
            blocks["overheads"].pop(key, None)

    if data.upper_floor_calc_method == "legacy_second_light_addon":
        blocks["second_light_addon"] = {
            "upper_floor_calc_method": data.upper_floor_calc_method,
            "second_light_masonry_enabled": second_light_enabled,
            "second_light_masonry_case_specific": second_light_case_specific,
            "second_light_masonry_volume_m3": q(second_light_volume),
            "second_light_d400_delivery_control": second_light_d400,
            "second_light_chasing_base_length_m": data.second_light_chasing_base_length_m,
            "second_light_chasing_case_specific": second_light_case_specific,
            "second_light_rebar_base_length_m": data.second_light_rebar_base_length_m,
            "second_light_rebar_order_length_m": second_light_rebar["order_length_m"],
            "second_light_rebar_case_specific": second_light_case_specific,
        }
    return blocks


def calculate_lines(data: LoadBearingWallsLintelsInput, b: dict[str, Any]) -> list[EstimateLineResult]:
    cutoff = b["cutoff_waterproofing"]
    main = b["main_walls"]
    gas = b["main_gas_blocks"]
    adh = b["adhesive_and_sand_concrete"]
    lintels = b["lintels"]
    reinf = b["main_wall_reinforcement"]
    delivery = b["deliveries_and_cranes"]
    parapet = b["parapet"]
    floor_2 = b["floor_2_load_bearing_walls"]
    second = b.get("second_light_addon", {})
    vent = b["vent_chimney_cladding"]
    overheads = b["overheads"]
    scaffolding = b["scaffolding"]
    second_case_specific = bool(second.get("second_light_masonry_case_specific", data.second_light_masonry_case_specific))

    _, main_wall_rebar_lines = calculate_main_wall_reinforcement(data)
    _, lintel_rebar_lines = calculate_lintel_rebar(data)

    lines = [
        line("scaffolding_setup_dismantling", "Устройство лесов, подмостей для кладки, демонтаж лесов", "компл", scaffolding["setup_quantity"], work_unit_price=data.scaffolding_setup_work_unit_price, notes="legacy direct or floors-based quantity", price_code="scaffolding_setup_dismantling_work_set"),
        line("scaffolding_timber_material", "Пиломатериал для устройства лесов", "м3", scaffolding["timber_quantity_m3"], material_unit_price=data.scaffolding_timber_unit_price, notes="legacy direct or floors-based quantity", price_code="timber_m3"),
        line("cutoff_waterproofing_under_first_row_blocks", "Гидроизоляция поверхности под первый ряд блоков", "м2", cutoff["cutoff_waterproofing_area_m2"], material_unit_price=data.cutoff_waterproofing_material_unit_price, work_unit_price=data.cutoff_waterproofing_work_unit_price, notes="Не включает перегородки 150 мм", price_code="cutoff_waterproofing_under_blocks_m2"),
        line("main_load_bearing_wall_masonry_work", "Кладка внешних, внутренних стен из газобетонных блоков", "м3", main["main_masonry_volume_m3"], work_unit_price=data.main_wall_masonry_work_unit_price, notes="Работа по проектному объёму без запаса", price_code="gas_block_masonry_work_m3"),
        line("main_gas_block_d400_600x400x250_material", "Газобетонный блок D400 600x400x250 мм", "м3", gas["d400"]["order_volume_m3"], material_unit_price=data.gas_block_d400_unit_price, price_code="gas_block_d400_m3"),
        line("main_gas_block_d500_600x250x250_material", "Газобетонный блок D500 600x250x250 мм", "м3", gas["d500_250"]["order_volume_m3"], material_unit_price=data.gas_block_d500_250_unit_price, price_code="gas_block_d500_m3"),
        line("main_gas_block_adhesive", "Монтажный клей для блоков 25 кг", "мешок", adh["main_adhesive_bags"], material_unit_price=data.adhesive_unit_price, price_code="block_adhesive_bag"),
        line("sand_concrete_m300_first_row", "Пескобетон М300 40 кг", "шт", adh["sand_concrete_bags"], material_unit_price=data.sand_concrete_unit_price, price_code="sand_concrete_bag"),
        line("u_block_lintel_cutting", "Резка блока под перемычку (U-блок)", "шт", lintels["u_block_quantity"], work_unit_price=data.u_block_cutting_work_unit_price, price_code="u_block_lintel_cutting_item"),
        line("main_wall_chasing_for_d10_reinforcement", "Штробление блоков под армирование Ø10", "мп", reinf["main_wall_chasing_quantity_m"], notes="Нулевая строка серой части, база для арматуры Ø10"),
        *main_wall_rebar_lines,
        line("gas_blocks_and_mix_delivery", "Доставка блоков, смеси", "маш", delivery["gas_block_delivery_trucks"], material_unit_price=data.gas_block_delivery_unit_price, notes="По закупочным объёмам после поддонов", price_code="block_delivery_truck"),
        line("gas_blocks_unloading_manipulator", "Разгрузка блоков, смеси манипулятором", "маш", delivery["gas_block_delivery_trucks"], material_unit_price=data.gas_block_unloading_manipulator_unit_price, price_code="block_unloading_manipulator_truck"),
        line("main_walls_blocks_crane_moving_25t", "Перемещение блоков, смеси автокраном 25 т", "смена", delivery["main_walls_crane_shifts"], material_unit_price=data.crane_25t_unit_price, notes="legacy manual or delivery-trucks threshold", price_code="crane_shift"),
        line("lintel_rebar_frame_assembly", "Изготовление и монтаж каркаса армирования перемычек", "мп", lintels["lintel_rebar_frame_assembly_quantity_m"], notes="Нулевая агрегирующая строка"),
        *lintel_rebar_lines,
        line("lintel_concreting_work", "Бетонирование перемычек", "мп", lintels["lintel_total_length_m"], work_unit_price=data.lintel_concreting_work_unit_price, price_code="lintel_concreting_work_m"),
        line("lintel_concrete_b22_5_m300_material", "Бетон В22,5 М300 для перемычек", "м3", lintels["lintel_concrete_order_volume_m3"], material_unit_price=data.concrete_m300_unit_price, notes="Минимум 1 м3", price_code="concrete_b22_5_m3"),
        line("lintel_concrete_delivery", "Доставка бетона до объекта", "рейс", data.concrete_delivery_trips, material_unit_price=data.concrete_delivery_unit_price, price_code="concrete_delivery_trip"),
        line("manual_concrete_lifting", "Перенос, подъём бетона вручную", "м3", lintels["lintel_concrete_order_volume_m3"], work_unit_price=data.manual_concrete_lifting_work_unit_price, price_code="manual_concrete_lifting_m3"),
    ]

    if data.upper_floor_calc_method == "legacy_second_light_addon":
        lines.extend([
            line("parapet_and_upper_level_masonry_work", "Кладка парапета и верхнего уровня", "м3", parapet["parapet_upper_level_total_volume_m3"], work_unit_price=data.parapet_masonry_work_unit_price, is_case_specific=second_case_specific, notes="Парапет постоянный; второй свет case_specific addon", price_code="gas_block_masonry_work_m3"),
            line("parapet_and_upper_level_gas_block_d400_material", "Газобетонный блок D400 для парапета и верхнего уровня", "м3", parapet["parapet_and_upper_level_d400"]["order_volume_m3"], material_unit_price=data.gas_block_d400_unit_price, is_case_specific=second_case_specific, notes="Объединено, чтобы не перезакладывать лишний поддон", price_code="gas_block_d400_m3"),
        ])
    else:
        if floor_2["enabled"]:
            lines.extend([
                line("floor_2_masonry_work", "Кладка несущих стен 2-го этажа из газобетонных блоков", "м3", floor_2["floor_2_masonry_volume_m3"], work_unit_price=data.main_wall_masonry_work_unit_price, notes="Production-блок 2-го этажа по спецификации", price_code="gas_block_masonry_work_m3"),
                line("floor_2_gas_block_d400_material", "Газобетонный блок D400 для несущих стен 2-го этажа", "м3", floor_2["floor_2_d400"]["order_volume_m3"], material_unit_price=data.gas_block_d400_unit_price, price_code="gas_block_d400_m3"),
                line("floor_2_masonry_glue", "Монтажный клей для блоков 2-го этажа", "мешок", floor_2["floor_2_adhesive_bags"], material_unit_price=data.adhesive_unit_price, price_code="block_adhesive_bag"),
            ])
        if parapet["parapet_enabled_calculated"]:
            lines.extend([
                line("parapet_masonry_work", "Кладка парапета", "м3", parapet["parapet_masonry_volume_m3"], work_unit_price=data.parapet_masonry_work_unit_price, notes="Production-блок парапета из спецификации кровли", price_code="gas_block_masonry_work_m3"),
                line("parapet_gas_block_d400_material", "Газобетонный блок D400 для парапета", "м3", parapet["parapet_d400"]["order_volume_m3"], material_unit_price=data.gas_block_d400_unit_price, price_code="gas_block_d400_m3"),
            ])

    if vent["vent_chimney_cladding_enabled_calculated"]:
        lines.extend([
        line(
            "vent_chimney_gas_block_cladding_work",
            "Обкладка дымохода и вентканалов 150 мм",
            "м2",
            vent["vent_chimney_cladding_area_m2"],
            display_quantity=vent["vent_chimney_display_area_m2"],
            work_unit_price=data.vent_chimney_cladding_work_unit_price,
            work_total_raw_override=d(vent["vent_chimney_gas_block_spec_volume_m3"]) / d(data.vent_chimney_block_thickness_m) * d(data.vent_chimney_cladding_work_unit_price),
            price_code="gas_block_cladding_work_m2",
        ),
        line("vent_chimney_gas_block_d500_600x150x250_material", "Газобетонный блок D500 600x150x250 мм", "м3", vent["vent_chimney_d500_150"]["order_volume_m3"], material_unit_price=data.gas_block_d500_150_unit_price, price_code="gas_block_d500_150_m3"),
        ])

    if data.upper_floor_calc_method == "legacy_second_light_addon":
        lines.extend([
        line("parapet_upper_level_adhesive", "Монтажный клей для парапета и верхнего уровня", "мешок", overheads["parapet_upper_level_adhesive_bags"], material_unit_price=data.adhesive_unit_price, is_case_specific=second_case_specific, notes="Две группы округления: second_light отдельно; parapet + vent/chimney вместе", price_code="block_adhesive_bag"),
        line("parapet_blocks_crane_moving", "Перемещение блоков, смеси автокраном для парапета", "смена", data.parapet_crane_shifts, material_unit_price=data.crane_25t_unit_price, price_code="crane_shift"),
        line("parapet_and_second_light_chasing_for_d10_reinforcement", "Штробление парапета и второго света", "мп", d(data.parapet_chasing_base_length_m) + d(data.second_light_chasing_base_length_m), is_case_specific=second_case_specific, notes="Нулевая строка серой части"),
        line("parapet_and_second_light_rebar_a500_d10", "Арматура A500 Ø10 для парапета и второго света", "мп", overheads["parapet_and_second_light_rebar_order_length_m"], material_unit_price=data.rebar_a500_d10_unit_price_per_m, material_total_raw_override=overheads["parapet_rebar"]["material_total_raw"] + overheads["second_light_rebar"]["material_total_raw"], is_case_specific=second_case_specific, notes="Две группы округления и закупки прутков", price_code="rebar_a500_d10_m"),
        ])

    lines.extend([
        line("walls_consumables_tool_amortization", "Расходные материалы, амортизация инструмента", "комплект", 1, material_unit_price=money(data.walls_consumables_tool_amortization_amount_raw), material_total_raw_override=data.walls_consumables_tool_amortization_amount_raw, notes="manual/fixed amount, формула требует подтверждения"),
        line("construction_waste_removal", "Вывоз мусора с объекта", "маш", data.waste_removal_trucks, material_unit_price=data.waste_removal_truck_unit_price, work_unit_price=data.waste_removal_work_unit_price, notes="manual/fixed line", price_code="waste_removal_truck"),
        line("walls_technical_supervision", "Технический надзор", "-", 1, work_unit_price=data.technical_supervision_amount, price_code="technical_supervision_fixed"),
    ])
    return lines


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
