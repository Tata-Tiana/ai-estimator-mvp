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


WALL_BLOCK_ITEM_ROLES = {"main_walls", "floor_2", "parapet", "partitions"}
WALL_BLOCK_ITEM_DENSITIES = {"D400", "D500"}
# Only these (role, density) combinations have a priced material/work path today.
# Any combination not listed here fails loudly instead of silently dropping volume.
WALL_BLOCK_ITEM_PRICED_KEYS = {
    ("main_walls", "D400"),
    ("main_walls", "D500"),
    ("floor_2", "D400"),
    ("floor_2", "D500"),
    ("parapet", "D400"),
    ("parapet", "D500"),
}


@dataclass(frozen=True)
class WallBlockItem:
    context: str
    wall_role: str
    volume_m3: float
    block_density: str | None = None
    block_size: str | None = None
    # Escape hatch for a rare non-D400/D500 block (Elena, 2026-07-28: "могут быть, но очень
    # редко"). Required only when block_density isn't D400/D500 — see validate(). Priced directly
    # from this value (no registry lookup, no waste/pallet rounding) since it's a one-off material,
    # not a stocked SKU with a known pallet volume.
    material_unit_price: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WallBlockItem":
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
    block_chasing_reinforcement_work_unit_price: float
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
    lintel_monolithic_concreting_work_unit_price: float
    lintel_formwork_plywood_unit_price: float
    lintel_formwork_timber_unit_price: float
    lintel_insulation_work_unit_price: float
    lintel_insulation_eps_unit_price: float
    lintel_glue_foam_unit_price: float
    lintel_insulation_eps_waste_coeff: float
    lintel_insulation_eps_pack_volume_m3: float
    lintel_glue_foam_coverage_m_per_can: float
    lintel_glue_foam_min_units: float
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
    floor_2_lintel_ublock_total_length_m: float | None = None
    floor_2_lintel_concrete_spec_volume_m3: float | None = None
    floor_2_concrete_delivery_trips: float | None = None
    floor_1_lintel_monolithic_concrete_volume_m3: float | None = None
    floor_1_lintel_monolithic_total_length_m: float | None = None
    floor_1_lintel_monolithic_insulation_length_m: float | None = None
    floor_1_lintel_formwork_horizontal_area_m2: float | None = None
    floor_1_lintel_formwork_vertical_area_m2: float | None = None
    floor_1_lintel_insulation_eps_spec_volume_m3: float | None = None
    floor_2_lintel_monolithic_concrete_volume_m3: float | None = None
    floor_2_lintel_monolithic_total_length_m: float | None = None
    floor_2_lintel_monolithic_insulation_length_m: float | None = None
    floor_2_lintel_formwork_horizontal_area_m2: float | None = None
    floor_2_lintel_formwork_vertical_area_m2: float | None = None
    floor_2_lintel_insulation_eps_spec_volume_m3: float | None = None
    lintel_formwork_plywood_sheet_area_m2: float = 2.3
    lintel_formwork_board_thickness_m: float = 0.05
    main_wall_rebar_calc_method: str = "legacy_wall_geometry"
    main_wall_rebar_items: list[SpecRebarItem | dict[str, Any]] | None = None
    wall_block_items: list[WallBlockItem | dict[str, Any]] | None = None
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
    parapet_gas_block_d500_250_spec_volume_m3: float | None = None
    vent_chimney_cladding_calc_method: str = "legacy_manual_toggle"
    vent_chimney_cladding_enabled: bool | None = None
    walls_consumables_calc_method: str = "legacy_fixed_amount"
    walls_consumables_rate: float = 0.0
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
        object.__setattr__(
            self,
            "wall_block_items",
            [
                x if isinstance(x, WallBlockItem) else WallBlockItem.from_dict(x)
                for x in (self.wall_block_items or [])
            ],
        )
        self.validate()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LoadBearingWallsLintelsInput":
        data.setdefault("block_chasing_reinforcement_work_unit_price", 0.0)
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
            # Not required even when flat_roof_enabled: Elena, 2026-07-15 — a flat-roof
            # parapet can rarely be entirely D500 (600x250x250) instead of D400, so the
            # D400 volume alone must not be mandatory. See parapet_gas_block_d500_250_spec_volume_m3.
            if self.parapet_masonry_volume_m3 is not None:
                require_non_negative("parapet_masonry_volume_m3", self.parapet_masonry_volume_m3)
            if self.parapet_gas_block_d500_250_spec_volume_m3 is not None:
                require_non_negative(
                    "parapet_gas_block_d500_250_spec_volume_m3", self.parapet_gas_block_d500_250_spec_volume_m3
                )
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
            # Optional: a floor may have no U-block lintels at all (only monolithic, or
            # no lintels of any kind) — Elena, 2026-07-15. None means absent, not zero.
            if self.lintel_total_length_m is not None:
                require_non_negative("lintel_total_length_m", self.lintel_total_length_m)
        for item in self.wall_block_items or []:
            if item.wall_role not in WALL_BLOCK_ITEM_ROLES:
                raise ValueError(f"wall_block_items wall_role must be one of {sorted(WALL_BLOCK_ITEM_ROLES)}")
            require_non_negative("wall_block_items.volume_m3", item.volume_m3)
            if item.wall_role == "partitions":
                continue
            if item.block_density in WALL_BLOCK_ITEM_DENSITIES:
                if (item.wall_role, item.block_density) not in WALL_BLOCK_ITEM_PRICED_KEYS:
                    raise ValueError(
                        f"wall_block_items combination wall_role={item.wall_role!r}/block_density={item.block_density!r} "
                        f"has no priced material path yet (context={item.context!r})"
                    )
            else:
                # Rare non-standard block (Elena, 2026-07-28) — priced directly from this row
                # instead of the shared D400/D500 price, since its size/density isn't a known SKU.
                if item.material_unit_price is None:
                    raise ValueError(
                        f"wall_block_items block_density={item.block_density!r} is not one of "
                        f"{sorted(WALL_BLOCK_ITEM_DENSITIES)} for wall_role={item.wall_role!r} "
                        f"(context={item.context!r}) — supply an explicit material_unit_price on "
                        "this row for a rare non-standard block, or use D400/D500."
                    )
                require_non_negative("wall_block_items.material_unit_price", item.material_unit_price)
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
            # Optional, same reasoning as lintel_total_length_m above: a floor may have
            # only monolithic lintels (no U-block concrete need) or no lintels at all.
            if self.lintel_concrete_spec_volume_m3 is not None:
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
            "lintel_insulation_eps_waste_coeff",
            "lintel_insulation_eps_pack_volume_m3",
            "lintel_glue_foam_coverage_m_per_can",
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


def wall_block_items_totals(items: list[WallBlockItem]) -> dict[str, Decimal]:
    """Bucket wall_block_items[] rows by (wall_role, block_density) into the same
    named volumes the legacy scalar-field path already produces, so everything
    downstream of this point (gas_block_order, adhesive, delivery, crane) is
    unchanged whether the volume came from wall_block_items or the old fields."""
    totals = {
        "main_walls_d400": Decimal("0"),
        "main_walls_d500": Decimal("0"),
        "main_walls_other": Decimal("0"),
        "floor_2_d400": Decimal("0"),
        "floor_2_d500": Decimal("0"),
        "floor_2_other": Decimal("0"),
        "parapet_d400": Decimal("0"),
        "parapet_d500": Decimal("0"),
        "parapet_other": Decimal("0"),
        "partitions": Decimal("0"),
    }
    for item in items:
        if item.wall_role == "partitions":
            totals["partitions"] += d(item.volume_m3)
            continue
        if item.block_density in WALL_BLOCK_ITEM_DENSITIES:
            key = f"{item.wall_role}_{item.block_density.lower()}"
        else:
            # Rare non-D400/D500 block — bucketed separately so "is there any floor_2/parapet
            # volume at all" checks (floor_2_enabled, scaffolding, parapet_enabled) don't have to
            # rely on D400 specifically being present.
            key = f"{item.wall_role}_other"
        totals[key] += d(item.volume_m3)
    return totals


def wall_block_items_roles_present(items: list["WallBlockItem"] | None) -> set[str]:
    """Which wall_role values actually have at least one row in wall_block_items[]. Used so a
    real project can mix sources per role - e.g. main_walls given as the old scalar total
    (main_wall_gas_block_400/250_spec_volume_m3) while floor_2/parapet/partitions are given as
    wall_block_items rows - without one role's presence silently discarding another role's real
    data. Before this helper existed, every "wall_block_totals is not None" check below treated
    "wall_block_items has ANY row" as "trust wall_block_items for EVERY role", which zeroed out
    main_walls volume for a real project (TRC, 2026-08-07) whose extraction put main_walls only
    in the legacy scalar fields and everything else in wall_block_items."""
    if not items:
        return set()
    return {item.wall_role for item in items}


def wall_block_other_density_lines(items: list["WallBlockItem"], wall_role: str) -> list[EstimateLineResult]:
    """One priced line per rare non-D400/D500 row for the given role (Elena, 2026-07-28: 'могут
    быть, но очень редко'). Density/size are trusted exactly as given in the project spec, price
    comes directly from the row — no registry lookup, no waste/pallet rounding, since it's a
    one-off material rather than a stocked SKU with a known pallet volume."""
    result: list[EstimateLineResult] = []
    for index, item in enumerate(items):
        if item.wall_role != wall_role or item.block_density in WALL_BLOCK_ITEM_DENSITIES:
            continue
        size_label = f", {item.block_size}" if item.block_size else ""
        density_label = item.block_density or "плотность не указана по спецификации"
        result.append(
            line(
                f"wall_block_other_{wall_role}_{index}",
                f"Газобетонный блок {density_label}{size_label} — {item.context}",
                "м3",
                item.volume_m3,
                material_unit_price=item.material_unit_price,
                notes="Нестандартная плотность/размер блока (редкий случай, подтверждено Еленой "
                "2026-07-28) — цена берётся напрямую из данных проекта, без округления по поддонам.",
            )
        )
    return result


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


def calculate_scaffolding(
    data: LoadBearingWallsLintelsInput,
    wall_block_totals: dict[str, Decimal] | None = None,
    floor_2_in_wall_block_items: bool = False,
) -> dict[str, Any]:
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
        # Prefer the fact of real captured floor_2 wall data (same signal already used to gate
        # floor_2 masonry pricing) over the PDF-text-derived floors_count field — floors_count
        # describes an architectural concept ("этажность") that real projects express
        # inconsistently (misleading, correct, or entirely absent — see
        # fact_of_data_vs_text_signal_principle memory / ARK_TRC_USV_WALL_ROOF_LINTEL_FINDINGS_PLAN.md
        # section 10), while wall_block_items either contains a real floor_2-role row or it doesn't.
        # Falls back to floors_count when wall_block_items has no floor_2-role row - either
        # because wall_block_items isn't used at all (every pre-2026-08-07 regression case is
        # byte-identical), or because it's used for OTHER roles only (fixed 2026-08-07 - see
        # wall_block_items_roles_present()).
        if floor_2_in_wall_block_items:
            # Checks all three density buckets (not just D400) so a floor_2 built entirely from a
            # rare non-D400/D500 block (Elena, 2026-07-28: "могут быть, но очень редко") still
            # correctly triggers 2-tier scaffolding instead of silently under-counting to 1.
            floor_2_any_volume = (
                wall_block_totals["floor_2_d400"] + wall_block_totals["floor_2_d500"] + wall_block_totals["floor_2_other"]
            )
            effective_floors_count = 2 if floor_2_any_volume > 0 else 1
            floors_count_source = "wall_block_items"
        else:
            if data.floors_count is None:
                raise ValueError("floors_count is required for floors_based scaffolding calculation when wall_block_items is not provided")
            effective_floors_count = data.floors_count
            floors_count_source = "floors_count"
        setup_quantity = d(effective_floors_count) * d(data.scaffolding_setup_units_per_floor)
        timber_quantity = d(effective_floors_count) * d(data.scaffolding_timber_m3_per_floor)
        return {
            "scaffolding_calc_method": data.scaffolding_calc_method,
            "scaffolding_source": "floors_based",
            "floors_count": effective_floors_count,
            "floors_count_source": floors_count_source,
            "floors_count_input": data.floors_count,
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
        return {
            "lintel_length_calc_method": data.lintel_length_calc_method,
            "lintel_length_source": "spec_total_length",
            "lintel_total_length_m": q(d(data.lintel_total_length_m or 0)),
        }

    raise ValueError(f"Unknown lintel_length_calc_method: {data.lintel_length_calc_method}")


def calculate_lintel_concrete(data: LoadBearingWallsLintelsInput, lintel_total_length_m: Decimal) -> dict[str, Any]:
    if data.lintel_concrete_calc_method == "legacy_length_section":
        raw_concrete = lintel_total_length_m * d(data.lintel_section_width_m) * d(data.lintel_section_height_m)
        required_concrete = raw_concrete * d(data.concrete_waste_coeff)
        source = "legacy_length_section"
        spec_volume = None
    elif data.lintel_concrete_calc_method == "spec_volume":
        raw_concrete = d(data.lintel_concrete_spec_volume_m3 or 0)
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


def calculate_floor_2_ublock_lintels(data: LoadBearingWallsLintelsInput) -> dict[str, Any]:
    """U-block lintels on floor 2. Independent of floor 1's lintels — both, either,
    or neither type/floor may have lintels at all (Elena, 2026-07-15)."""
    length = d(data.floor_2_lintel_ublock_total_length_m or 0)
    enabled = length > 0
    u_block_quantity = length / d(data.gas_block_length_m) if enabled else Decimal("0")
    return {
        "enabled": enabled,
        "ublock_total_length_m": q(length),
        "u_block_quantity": q(u_block_quantity),
        "concrete_spec_volume_m3": q(d(data.floor_2_lintel_concrete_spec_volume_m3 or 0)),
    }


def calculate_monolithic_lintel_block(
    concrete_volume_m3: float | None,
    total_length_m: float | None,
    insulation_length_m: float | None,
    eps_spec_volume_m3: float | None,
    data: LoadBearingWallsLintelsInput,
    formwork_horizontal_area_m2: float | None = None,
    formwork_vertical_area_m2: float | None = None,
) -> dict[str, Any]:
    """Monolithic (poured-in-place) lintels — a floor's second lintel construction
    method alongside U-block lintels. Present in at least 50% of real projects
    (Elena, 2026-07-15), independent of U-block lintels and independent per floor.
    Formwork here is board + plywood only (material, no install-work line — Elena:
    "в СС работы на устройство опалубки нет"). Updated 2026-07-29 (Elena): monolithic
    lintels are not always insulated, and when insulated may cover only part of their
    length — insulation now has its own `insulation_enabled` gate instead of sharing
    the concrete/length block's `enabled`.

    Formwork plywood/timber are always derived from horizontal+vertical area — real
    project PDFs never give a ready sheet count or timber m3 for lintel formwork,
    only area, same as beam/slab formwork elsewhere in this pipeline. There is no
    direct-quantity input path (removed 2026-07-25 — Elena: confirmed this data
    never appears in source drawings)."""
    concrete_volume = d(concrete_volume_m3 or 0)
    total_length = d(total_length_m or 0)
    if concrete_volume > 0 and total_length_m is None:
        raise ValueError("monolithic lintel concreting work requires total_length_m when concrete_volume_m3 is present")
    if total_length > 0 and concrete_volume_m3 is None:
        # 2026-07-29: symmetric guard for the real ARK case — the spec gives a combined
        # total_length_m (e.g. 5.4m for ПБ1+ПБ2) but no combined concrete_volume_m3 (each
        # lintel's concrete is only given separately, 0.21+0.16, and must not be summed by
        # the extraction itself). Without this guard, concreting work still gets billed by
        # length while concrete material silently defaults to 0 — real money lost with no
        # error raised. See sheet01_required_field_unenforced_and_section_enabled_gap memory.
        raise ValueError("monolithic lintel concrete material requires concrete_volume_m3 when total_length_m is present")
    enabled = concrete_volume > 0 or total_length > 0
    insulation_length = d(insulation_length_m or 0)
    insulation_enabled = insulation_length > 0
    total_formwork_area = d(formwork_horizontal_area_m2 or 0) + d(formwork_vertical_area_m2 or 0)
    plywood_raw = total_formwork_area / d(data.lintel_formwork_plywood_sheet_area_m2)
    plywood = Decimal(ceil(plywood_raw)) if enabled else Decimal("0")
    timber = total_formwork_area * d(data.lintel_formwork_board_thickness_m)
    eps_spec = d(eps_spec_volume_m3 or 0)
    eps_required = eps_spec * d(data.lintel_insulation_eps_waste_coeff)
    eps_raw_packs = eps_required / d(data.lintel_insulation_eps_pack_volume_m3) if insulation_enabled else Decimal("0")
    eps_packs = int(ceil(eps_raw_packs)) if insulation_enabled else 0
    eps_order_volume = d(eps_packs) * d(data.lintel_insulation_eps_pack_volume_m3)
    foam_raw = insulation_length / d(data.lintel_glue_foam_coverage_m_per_can) if insulation_enabled else Decimal("0")
    foam_units = max(int(data.lintel_glue_foam_min_units), int(ceil(foam_raw))) if insulation_enabled else 0
    return {
        "enabled": enabled,
        "insulation_enabled": insulation_enabled,
        "monolithic_concrete_volume_m3": q(concrete_volume),
        "monolithic_total_length_m": q(total_length),
        "monolithic_insulation_length_m": q(insulation_length),
        "formwork_horizontal_area_m2": formwork_horizontal_area_m2,
        "formwork_vertical_area_m2": formwork_vertical_area_m2,
        "formwork_plywood_qty": q(plywood),
        "formwork_timber_volume_m3": q(timber),
        "insulation_eps_spec_volume_m3": q(eps_spec),
        "insulation_eps_required_volume_m3": q(eps_required),
        "insulation_eps_raw_packs": q(eps_raw_packs),
        "insulation_eps_packs": eps_packs,
        "insulation_eps_order_volume_m3": q(eps_order_volume),
        "glue_foam_raw_units": q(foam_raw),
        "glue_foam_units": foam_units,
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
        line_code = control["line_code"]
        if line_code in controls:
            raise ValueError(
                f"main_wall_rebar_items: duplicate line_code '{line_code}' "
                f"(floor={item.floor}, component={item.component}, steel_class={item.steel_class}, "
                f"diameter_mm={item.diameter_mm}) — two rows resolve to the same auto-generated code and "
                "would silently overwrite each other's control totals. Set an explicit unique `code` on "
                "at least one of the colliding rows (e.g. a '_subwindow' suffix)."
            )
        controls[line_code] = control
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
        line_code = control["line_code"]
        if line_code in controls:
            raise ValueError(
                f"lintel_rebar_items: duplicate line_code '{line_code}' "
                f"(floor={item.floor}, component={item.component}, steel_class={item.steel_class}, "
                f"diameter_mm={item.diameter_mm}) — two rows resolve to the same auto-generated code and "
                "would silently overwrite each other's control totals. Set an explicit unique `code` on "
                "at least one of the colliding rows."
            )
        controls[line_code] = control
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
    wall_block_totals = wall_block_items_totals(data.wall_block_items) if data.wall_block_items else None
    # Per-role, not all-or-nothing (fixed 2026-08-07, real TRC project bug): wall_block_items[]
    # can legitimately carry only SOME roles (e.g. floor_2/parapet/partitions) while another role
    # (main_walls) was given via the old scalar fields instead - a normal mixed-source situation,
    # not an error. Trusting wall_block_totals for a role that has zero rows in wall_block_items
    # silently produced 0 m3 of main-wall masonry for a real project even though the real 80.48
    # m3 was sitting right there in main_wall_gas_block_400/250_spec_volume_m3. See
    # wall_block_items_roles_present() and the same fix applied below to floor_2/parapet/scaffolding.
    wall_block_roles = wall_block_items_roles_present(data.wall_block_items)
    if "main_walls" in wall_block_roles:
        main_400_volume = wall_block_totals["main_walls_d400"]
        main_500_250_volume = wall_block_totals["main_walls_d500"]
        main_other_volume = wall_block_totals["main_walls_other"]
    else:
        main_400_volume = d(data.main_wall_gas_block_400_spec_volume_m3)
        main_500_250_volume = d(data.main_wall_gas_block_250_spec_volume_m3)
        main_other_volume = Decimal("0")
    main_masonry_volume = main_400_volume + main_500_250_volume + main_other_volume
    main_d400 = gas_block_order(main_400_volume, data.gas_block_waste_coeff, data.gas_block_d400_pallet_volume_m3)
    main_d500_250 = gas_block_order(main_500_250_volume, data.gas_block_waste_coeff, data.gas_block_d500_250_pallet_volume_m3)
    adhesive_raw = main_masonry_volume * d(data.adhesive_consumption_bag_per_m3) * d(data.adhesive_waste_coeff)
    sand_raw = cutoff_area * d(data.sand_concrete_consumption_kg_per_m2_per_10mm) * d(data.sand_concrete_thickness_factor) / d(data.sand_concrete_bag_weight_kg)
    u_block_quantity = lintel_total_length / d(data.gas_block_length_m)
    main_wall_reinforcement, _ = calculate_main_wall_reinforcement(data)
    lintel_rebar, _ = calculate_lintel_rebar(data)
    lintel_concrete = calculate_lintel_concrete(data, lintel_total_length)
    floor_2_ublock_lintels = calculate_floor_2_ublock_lintels(data)
    floor_1_monolithic_lintels = calculate_monolithic_lintel_block(
        data.floor_1_lintel_monolithic_concrete_volume_m3,
        data.floor_1_lintel_monolithic_total_length_m,
        data.floor_1_lintel_monolithic_insulation_length_m,
        data.floor_1_lintel_insulation_eps_spec_volume_m3,
        data,
        formwork_horizontal_area_m2=data.floor_1_lintel_formwork_horizontal_area_m2,
        formwork_vertical_area_m2=data.floor_1_lintel_formwork_vertical_area_m2,
    )
    floor_2_monolithic_lintels = calculate_monolithic_lintel_block(
        data.floor_2_lintel_monolithic_concrete_volume_m3,
        data.floor_2_lintel_monolithic_total_length_m,
        data.floor_2_lintel_monolithic_insulation_length_m,
        data.floor_2_lintel_insulation_eps_spec_volume_m3,
        data,
        formwork_horizontal_area_m2=data.floor_2_lintel_formwork_horizontal_area_m2,
        formwork_vertical_area_m2=data.floor_2_lintel_formwork_vertical_area_m2,
    )
    # Concrete material purchase is combined across U-block + monolithic lintels per floor
    # (same truck either way, Elena 2026-07-15) even though the work lines stay split by method.
    floor_1_lintel_concrete_combined_required = d(lintel_concrete["lintel_required_concrete_volume_m3"]) + d(
        floor_1_monolithic_lintels["monolithic_concrete_volume_m3"]
    )
    floor_1_lintel_concrete_enabled = floor_1_lintel_concrete_combined_required > 0
    floor_1_lintel_concrete_order_volume_m3 = (
        max(d(data.lintel_concrete_min_order_volume_m3), Decimal(ceil(floor_1_lintel_concrete_combined_required)))
        if floor_1_lintel_concrete_enabled
        else Decimal("0")
    )
    floor_1_ublock_enabled = lintel_total_length > 0
    floor_2_lintel_concrete_combined_required = d(floor_2_ublock_lintels["concrete_spec_volume_m3"]) + d(
        floor_2_monolithic_lintels["monolithic_concrete_volume_m3"]
    )
    floor_2_lintel_concrete_enabled = floor_2_lintel_concrete_combined_required > 0
    floor_2_lintel_concrete_order_volume_m3 = (
        max(d(data.lintel_concrete_min_order_volume_m3), Decimal(ceil(floor_2_lintel_concrete_combined_required)))
        if floor_2_lintel_concrete_enabled
        else Decimal("0")
    )
    floor_2_in_wall_block_items = "floor_2" in wall_block_roles
    if floor_2_in_wall_block_items and data.upper_floor_calc_method != "legacy_second_light_addon":
        # wall_block_items[] has a floor_2-role row: gate floor_2 by whether a floor_2-role item
        # actually exists, not by floors_count (a real project's floors_count is
        # sometimes physically absent from the PDF, so gating on it is impossible
        # in principle — see floor_2_walls_incomplete_and_floors_count_risk memory).
        # Checks all three density buckets (not just D400) so a floor_2 built entirely from a
        # rare non-D400/D500 block (Elena, 2026-07-28) still gets detected as present.
        floor_2_enabled = (
            wall_block_totals["floor_2_d400"] + wall_block_totals["floor_2_d500"] + wall_block_totals["floor_2_other"]
        ) > 0
    else:
        floor_2_enabled = data.floors_count == 2
    if data.upper_floor_calc_method == "legacy_second_light_addon":
        second_light_enabled = bool(data.second_light_masonry_enabled)
        second_light_case_specific = bool(data.second_light_masonry_case_specific)
        second_light_input_volume = d(data.second_light_masonry_volume_m3 or 0)
        second_light_volume = second_light_input_volume if second_light_enabled else Decimal("0")
        floor_2_volume = Decimal("0")
        floor_2_d500_volume = Decimal("0")
        floor_2_other_volume = Decimal("0")
    else:
        second_light_enabled = False
        second_light_case_specific = False
        second_light_input_volume = Decimal("0")
        second_light_volume = Decimal("0")
        floor_2_volume = (
            wall_block_totals["floor_2_d400"]
            if floor_2_in_wall_block_items
            else (d(data.floor_2_masonry_volume_m3 or 0) if floor_2_enabled else Decimal("0"))
        )
        # D500 (internal walls) on floor 2, same principle as floor 1 — Elena confirmed 2026-07-24:
        # external walls are D400, internal load-bearing walls are D500, on any floor. Only
        # reachable via wall_block_items; the legacy scalar path has no D500 field for floor_2.
        floor_2_d500_volume = wall_block_totals["floor_2_d500"] if floor_2_in_wall_block_items else Decimal("0")
        # Rare non-D400/D500 block on floor 2 (Elena, 2026-07-28) — priced per-row separately,
        # see wall_block_other_density_lines(); only its volume feeds the combined masonry work.
        floor_2_other_volume = wall_block_totals["floor_2_other"] if floor_2_in_wall_block_items else Decimal("0")

    parapet_uses_wall_block_items = "parapet" in wall_block_roles and data.parapet_calc_method != "legacy_manual_toggle"
    if data.parapet_calc_method == "legacy_manual_toggle":
        parapet_enabled = bool(data.parapet_enabled)
    elif parapet_uses_wall_block_items:
        parapet_enabled = bool(
            data.flat_roof_enabled
            and (
                wall_block_totals["parapet_d400"] > 0
                or wall_block_totals["parapet_d500"] > 0
                or wall_block_totals["parapet_other"] > 0
            )
        )
    else:
        parapet_enabled = bool(
            data.flat_roof_enabled
            and (
                d(data.parapet_masonry_volume_m3 or 0) > 0
                or d(data.parapet_gas_block_d500_250_spec_volume_m3 or 0) > 0
            )
        )
    if parapet_uses_wall_block_items:
        parapet_volume = wall_block_totals["parapet_d400"] if parapet_enabled else Decimal("0")
        parapet_d500_volume = wall_block_totals["parapet_d500"] if parapet_enabled else Decimal("0")
        parapet_other_volume = wall_block_totals["parapet_other"] if parapet_enabled else Decimal("0")
    else:
        parapet_volume = d(data.parapet_masonry_volume_m3 or 0) if parapet_enabled else Decimal("0")
        parapet_d500_volume = d(data.parapet_gas_block_d500_250_spec_volume_m3 or 0) if parapet_enabled else Decimal("0")
        parapet_other_volume = Decimal("0")

    if data.vent_chimney_cladding_calc_method == "legacy_manual_toggle":
        vent_enabled = bool(data.vent_chimney_cladding_enabled)
    else:
        vent_enabled = bool(data.flat_roof_enabled and d(data.vent_chimney_gas_block_spec_volume_m3 or 0) > 0)
    vent_spec_volume = d(data.vent_chimney_gas_block_spec_volume_m3 or 0) if vent_enabled else Decimal("0")

    floor_2_d400 = gas_block_order(q(floor_2_volume), data.gas_block_waste_coeff, data.gas_block_d400_pallet_volume_m3)
    floor_2_d500 = gas_block_order(
        q(floor_2_d500_volume), data.gas_block_waste_coeff, data.gas_block_d500_250_pallet_volume_m3
    )
    # Masonry work is one line regardless of block density (same as main walls/parapet) —
    # D400, D500 and any rare "other" volume are combined here, split back out per density
    # (and per row for "other") only for materials.
    floor_2_total_masonry_volume = floor_2_volume + floor_2_d500_volume + floor_2_other_volume
    floor_2_adhesive_raw = floor_2_total_masonry_volume * d(data.adhesive_consumption_bag_per_m3) * d(data.adhesive_waste_coeff)
    floor_2_adhesive_bags = int(ceil(floor_2_adhesive_raw))
    parapet_d400 = gas_block_order(q(parapet_volume), data.gas_block_waste_coeff, data.gas_block_d400_pallet_volume_m3)
    parapet_d500_250 = gas_block_order(
        q(parapet_d500_volume), data.gas_block_waste_coeff, data.gas_block_d500_250_pallet_volume_m3
    )
    parapet_total_masonry_volume = parapet_volume + parapet_d500_volume + parapet_other_volume
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
        delivery_total = d(main_d400["order_volume_m3"]) + d(main_d500_250["order_volume_m3"]) + d(floor_2_d400["order_volume_m3"]) + d(floor_2_d500["order_volume_m3"]) + d(parapet_d400["order_volume_m3"]) + d(parapet_d500_250["order_volume_m3"]) + d(vent_d500["order_volume_m3"])
    delivery_trucks = int(ceil(delivery_total / d(data.gas_block_delivery_truck_capacity_m3)))
    main_walls_crane = calculate_main_walls_crane(data, delivery_trucks)
    second_light_adhesive_raw = second_light_volume * d(data.adhesive_consumption_bag_per_m3) * d(data.adhesive_waste_coeff)
    second_light_adhesive_bags = int(ceil(second_light_adhesive_raw))
    parapet_vent_adhesive_raw = (parapet_total_masonry_volume + vent_spec_volume) * d(data.adhesive_consumption_bag_per_m3) * d(data.adhesive_waste_coeff)
    parapet_vent_adhesive_bags = int(ceil(parapet_vent_adhesive_raw))
    second_light_rebar = rebar_from_base_length(data.second_light_rebar_base_length_m, data.rebar_a500_d10_rod_length_m, data.rebar_waste_coeff, data.rebar_a500_d10_unit_price_per_m)
    parapet_rebar = rebar_from_base_length(data.parapet_rebar_base_length_m, data.rebar_a500_d10_rod_length_m, data.rebar_waste_coeff, data.rebar_a500_d10_unit_price_per_m)
    if data.upper_floor_calc_method == "legacy_second_light_addon":
        parapet_delivery_note = "Delivery split from combined parapet+second-light D400 order volume."
    else:
        parapet_delivery_note = "Production parapet order volume calculated separately."

    blocks = {
        "scaffolding": calculate_scaffolding(data, wall_block_totals, floor_2_in_wall_block_items),
        "cutoff_waterproofing": cutoff_waterproofing,
        "main_walls": {"main_masonry_volume_m3": q(main_masonry_volume)},
        "wall_block_items": {
            "used": wall_block_totals is not None,
            # Captured but deliberately not priced yet (2026-07-20 decision) — partitions
            # masonry/rebar has no cost-structure rate assigned in this calculator.
            "partitions_captured_volume_m3": q(wall_block_totals["partitions"]) if wall_block_totals is not None else 0.0,
        },
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
            "lintel_concrete_combined_order_volume_m3": q(floor_1_lintel_concrete_order_volume_m3),
            "ublock_enabled": floor_1_ublock_enabled,
            "concrete_enabled": floor_1_lintel_concrete_enabled,
        },
        "floor_2_ublock_lintels": floor_2_ublock_lintels,
        "floor_2_lintel_concrete": {
            "enabled": floor_2_lintel_concrete_enabled,
            "combined_required_volume_m3": q(floor_2_lintel_concrete_combined_required),
            "combined_order_volume_m3": q(floor_2_lintel_concrete_order_volume_m3),
        },
        "floor_1_monolithic_lintels": floor_1_monolithic_lintels,
        "floor_2_monolithic_lintels": floor_2_monolithic_lintels,
        "main_wall_reinforcement": main_wall_reinforcement,
        "floor_2_load_bearing_walls": {
            "floors_count": data.floors_count,
            "upper_floor_calc_method": data.upper_floor_calc_method,
            "enabled": floor_2_enabled if data.upper_floor_calc_method == "floor_2_spec_volume" else second_light_enabled,
            "floor_2_load_bearing_walls_enabled": floor_2_enabled,
            "floor_2_masonry_volume_m3": q(floor_2_volume),
            "floor_2_d400": floor_2_d400,
            "floor_2_gas_block_d500_spec_volume_m3": q(floor_2_d500_volume),
            "floor_2_d500": floor_2_d500,
            "floor_2_total_masonry_volume_m3": q(floor_2_total_masonry_volume),
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
            "parapet_gas_block_d500_250_spec_volume_m3": q(parapet_d500_volume),
            "parapet_d500_250": parapet_d500_250,
            "parapet_total_masonry_volume_m3": q(parapet_total_masonry_volume),
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
            "walls_consumables_calc_method": data.walls_consumables_calc_method,
            "walls_consumables_rate": data.walls_consumables_rate,
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
        *wall_block_other_density_lines(data.wall_block_items or [], "main_walls"),
        line("main_gas_block_adhesive", "Монтажный клей для блоков 25 кг", "мешок", adh["main_adhesive_bags"], material_unit_price=data.adhesive_unit_price, price_code="block_adhesive_bag"),
        line("sand_concrete_m300_first_row", "Пескобетон М300 40 кг", "шт", adh["sand_concrete_bags"], material_unit_price=data.sand_concrete_unit_price, price_code="sand_concrete_bag"),
        line("main_wall_chasing_for_d10_reinforcement", "Штробление блоков под дополнительное усиление, армирование арматурой диаметром 10 мм", "мп", reinf["main_wall_chasing_quantity_m"], work_unit_price=data.block_chasing_reinforcement_work_unit_price, notes="База для арматуры Ø10", price_code="block_chasing_reinforcement_work_m"),
        *main_wall_rebar_lines,
        line("gas_blocks_and_mix_delivery", "Доставка блоков, смеси", "маш", delivery["gas_block_delivery_trucks"], material_unit_price=data.gas_block_delivery_unit_price, notes="По закупочным объёмам после поддонов", price_code="block_delivery_truck"),
        line("gas_blocks_unloading_manipulator", "Разгрузка блоков, смеси манипулятором", "маш", delivery["gas_block_delivery_trucks"], material_unit_price=data.gas_block_unloading_manipulator_unit_price, price_code="block_unloading_manipulator_truck"),
        line("main_walls_blocks_crane_moving_25t", "Перемещение блоков, смеси автокраном 25 т", "смена", delivery["main_walls_crane_shifts"], material_unit_price=data.crane_25t_unit_price, notes="legacy manual or delivery-trucks threshold", price_code="crane_shift"),
        line("lintel_rebar_frame_assembly", "Изготовление и монтаж каркаса армирования перемычек", "мп", lintels["lintel_rebar_frame_assembly_quantity_m"], notes="Нулевая агрегирующая строка"),
        *lintel_rebar_lines,
    ]

    if lintels["ublock_enabled"]:
        lines.extend([
            line("u_block_lintel_cutting", "Резка блока под перемычку (U-блок)", "шт", lintels["u_block_quantity"], work_unit_price=data.u_block_cutting_work_unit_price, price_code="u_block_lintel_cutting_item"),
            line("lintel_concreting_work", "Бетонирование перемычек", "мп", lintels["lintel_total_length_m"], work_unit_price=data.lintel_concreting_work_unit_price, price_code="lintel_concreting_work_m"),
        ])

    if lintels["concrete_enabled"]:
        lines.extend([
            line("lintel_concrete_b22_5_m300_material", "Бетон В22,5 М300 для перемычек", "м3", lintels["lintel_concrete_combined_order_volume_m3"], material_unit_price=data.concrete_m300_unit_price, notes="Минимум 1 м3; объём U-блока и монолита 1-го этажа объединены в одну закупку", price_code="concrete_b22_5_m3"),
            line("lintel_concrete_delivery", "Доставка бетона до объекта", "рейс", data.concrete_delivery_trips, material_unit_price=data.concrete_delivery_unit_price, price_code="concrete_delivery_trip"),
            line("manual_concrete_lifting", "Перенос, подъём бетона вручную", "м3", lintels["lintel_concrete_combined_order_volume_m3"], work_unit_price=data.manual_concrete_lifting_work_unit_price, price_code="manual_concrete_lifting_m3"),
        ])

    floor_2_ublock = b["floor_2_ublock_lintels"]
    if floor_2_ublock["enabled"]:
        lines.extend([
            line("floor_2_u_block_lintel_cutting", "Резка блока под перемычку (U-блок), 2-й этаж", "шт", floor_2_ublock["u_block_quantity"], work_unit_price=data.u_block_cutting_work_unit_price, price_code="u_block_lintel_cutting_item"),
            line("floor_2_lintel_concreting_work", "Бетонирование перемычек в U-блоке, 2-й этаж", "мп", floor_2_ublock["ublock_total_length_m"], work_unit_price=data.lintel_concreting_work_unit_price, price_code="lintel_concreting_work_m"),
        ])

    floor_2_lintel_concrete = b["floor_2_lintel_concrete"]
    if floor_2_lintel_concrete["enabled"]:
        lines.extend([
            line("floor_2_lintel_concrete_b22_5_m300_material", "Бетон В22,5 М300 для перемычек, 2-й этаж", "м3", floor_2_lintel_concrete["combined_order_volume_m3"], material_unit_price=data.concrete_m300_unit_price, notes="Минимум 1 м3; объём U-блока и монолита 2-го этажа объединены в одну закупку", price_code="concrete_b22_5_m3"),
            line("floor_2_lintel_concrete_delivery", "Доставка бетона до объекта, 2-й этаж", "рейс", data.floor_2_concrete_delivery_trips or 0, material_unit_price=data.concrete_delivery_unit_price, price_code="concrete_delivery_trip"),
            line("floor_2_manual_concrete_lifting", "Перенос, подъём бетона вручную, 2-й этаж", "м3", floor_2_lintel_concrete["combined_order_volume_m3"], work_unit_price=data.manual_concrete_lifting_work_unit_price, price_code="manual_concrete_lifting_m3"),
        ])

    floor_1_monolithic = b["floor_1_monolithic_lintels"]
    floor_2_monolithic = b["floor_2_monolithic_lintels"]
    for floor_label, floor_number, monolithic in (("1-й этаж", 1, floor_1_monolithic), ("2-й этаж", 2, floor_2_monolithic)):
        if not monolithic["enabled"]:
            continue
        prefix = f"floor_{floor_number}"
        lines.extend([
            line(f"{prefix}_lintel_monolithic_concreting_work", f"Бетонирование монолитных перемычек, {floor_label}", "мп", monolithic["monolithic_total_length_m"], work_unit_price=data.lintel_monolithic_concreting_work_unit_price, notes="С 2026-07-28 работа по бетонированию монолитных перемычек считается по общей длине перемычек, а не по объему бетона.", price_code="lintel_monolithic_concreting_work_m"),
            line(f"{prefix}_lintel_formwork_plywood_material", f"Фанера для опалубки монолитных перемычек, {floor_label}", "шт", monolithic["formwork_plywood_qty"], material_unit_price=data.lintel_formwork_plywood_unit_price, price_code="lintel_formwork_plywood_sheet"),
            line(f"{prefix}_lintel_formwork_timber_material", f"Пиломатериал обрезной для опалубки монолитных перемычек, {floor_label}", "м3", monolithic["formwork_timber_volume_m3"], material_unit_price=data.lintel_formwork_timber_unit_price, price_code="lintel_formwork_timber_m3"),
            line(f"{prefix}_lintel_edge_insulation_work", f"Устройство утепления по наружной стороне монолитной перемычки, {floor_label}", "мп", monolithic["monolithic_insulation_length_m"], work_unit_price=data.lintel_insulation_work_unit_price, price_code="lintel_edge_insulation_work_m"),
            line(f"{prefix}_lintel_edge_insulation_eps_material", f"Экструдированный пенополистирол Пеноплэкс Основа, {floor_label}", "м3", monolithic["insulation_eps_order_volume_m3"], display_quantity=q(monolithic["insulation_eps_order_volume_m3"], "0.01"), material_unit_price=data.lintel_insulation_eps_unit_price, price_code="eps_penoplex_osnova_100_m3"),
            line(f"{prefix}_lintel_edge_insulation_glue_foam", f"Клей-пена для ЭППС, {floor_label}", "баллон", monolithic["glue_foam_units"], material_unit_price=data.lintel_glue_foam_unit_price, price_code="eps_foam_glue_can"),
        ])

    if data.upper_floor_calc_method == "legacy_second_light_addon":
        lines.extend([
            line("parapet_and_upper_level_masonry_work", "Кладка парапета и верхнего уровня", "м3", parapet["parapet_upper_level_total_volume_m3"], work_unit_price=data.parapet_masonry_work_unit_price, is_case_specific=second_case_specific, notes="Парапет постоянный; второй свет case_specific addon", price_code="gas_block_masonry_work_m3"),
            line("parapet_and_upper_level_gas_block_d400_material", "Газобетонный блок D400 для парапета и верхнего уровня", "м3", parapet["parapet_and_upper_level_d400"]["order_volume_m3"], material_unit_price=data.gas_block_d400_unit_price, is_case_specific=second_case_specific, notes="Объединено, чтобы не перезакладывать лишний поддон", price_code="gas_block_d400_m3"),
        ])
    else:
        if floor_2["enabled"]:
            lines.extend([
                line("floor_2_masonry_work", "Кладка несущих стен 2-го этажа из газобетонных блоков", "м3", floor_2["floor_2_total_masonry_volume_m3"], work_unit_price=data.main_wall_masonry_work_unit_price, notes="Production-блок 2-го этажа по спецификации; объём D400+D500 объединён, т.к. кладка — одна работа независимо от плотности блока", price_code="gas_block_masonry_work_m3"),
                line("floor_2_gas_block_d400_material", "Газобетонный блок D400 для несущих стен 2-го этажа", "м3", floor_2["floor_2_d400"]["order_volume_m3"], material_unit_price=data.gas_block_d400_unit_price, price_code="gas_block_d400_m3"),
                line("floor_2_masonry_glue", "Монтажный клей для блоков 2-го этажа", "мешок", floor_2["floor_2_adhesive_bags"], material_unit_price=data.adhesive_unit_price, price_code="block_adhesive_bag"),
            ])
            if floor_2["floor_2_gas_block_d500_spec_volume_m3"] > 0:
                lines.append(
                    line("floor_2_gas_block_d500_material", "Газобетонный блок D500 для несущих стен 2-го этажа", "м3", floor_2["floor_2_d500"]["order_volume_m3"], material_unit_price=data.gas_block_d500_250_unit_price, notes="Добавлено 2026-07-24. Внутренние несущие стены 2-го этажа — тот же принцип D400 снаружи/D500 внутри, что и на 1-м этаже и в парапете.", price_code="gas_block_d500_m3")
                )
            lines.extend(wall_block_other_density_lines(data.wall_block_items or [], "floor_2"))
        if parapet["parapet_enabled_calculated"]:
            lines.append(
                line("parapet_masonry_work", "Кладка парапета", "м3", parapet["parapet_total_masonry_volume_m3"], work_unit_price=data.parapet_masonry_work_unit_price, notes="Production-блок парапета из спецификации кровли; объём D400+D500 объединён, т.к. кладка — одна работа независимо от плотности блока", price_code="gas_block_masonry_work_m3")
            )
            if parapet["parapet_masonry_volume_m3"] > 0:
                lines.append(
                    line("parapet_gas_block_d400_material", "Газобетонный блок D400 600x400x250 мм для парапета", "м3", parapet["parapet_d400"]["order_volume_m3"], material_unit_price=data.gas_block_d400_unit_price, price_code="gas_block_d400_m3")
                )
            if parapet["parapet_gas_block_d500_250_spec_volume_m3"] > 0:
                lines.append(
                    line("parapet_gas_block_d500_250_material", "Газобетонный блок D500 600x250x250 мм для парапета", "м3", parapet["parapet_d500_250"]["order_volume_m3"], material_unit_price=data.gas_block_d500_250_unit_price, notes="Добавлено 2026-07-15. Елена: парапет обычно D400 (80-90%), но может быть частично или полностью D500 600x250x250, тот же блок, что и второй материал основных стен.", price_code="gas_block_d500_m3")
                )
            lines.extend(wall_block_other_density_lines(data.wall_block_items or [], "parapet"))
            if d(data.parapet_chasing_base_length_m) > 0:
                lines.append(
                    line("parapet_chasing_for_d10_reinforcement", "Штробление блоков парапета под дополнительное усиление, армирование арматурой диаметром 10 мм", "мп", data.parapet_chasing_base_length_m, work_unit_price=data.block_chasing_reinforcement_work_unit_price, notes="Базовая длина берется из проектной спецификации парапета.", price_code="block_chasing_reinforcement_work_m")
                )
            if d(data.parapet_rebar_base_length_m) > 0:
                lines.append(
                    line("parapet_rebar_a500_d10", "Арматура A500 Ø10 для парапета", "мп", overheads["parapet_rebar"]["order_length_m"], material_unit_price=data.rebar_a500_d10_unit_price_per_m, material_total_raw_override=overheads["parapet_rebar"]["material_total_raw"], notes="Закупочная длина считается из проектной базовой длины парапета с запасом и округлением до прутка.", price_code="rebar_a500_d10_m")
                )

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
        line("parapet_and_second_light_chasing_for_d10_reinforcement", "Штробление парапета и второго света", "мп", d(data.parapet_chasing_base_length_m) + d(data.second_light_chasing_base_length_m), work_unit_price=data.block_chasing_reinforcement_work_unit_price, is_case_specific=second_case_specific, notes="База для арматуры Ø10", price_code="block_chasing_reinforcement_work_m"),
        line("parapet_and_second_light_rebar_a500_d10", "Арматура A500 Ø10 для парапета и второго света", "мп", overheads["parapet_and_second_light_rebar_order_length_m"], material_unit_price=data.rebar_a500_d10_unit_price_per_m, material_total_raw_override=overheads["parapet_rebar"]["material_total_raw"] + overheads["second_light_rebar"]["material_total_raw"], is_case_specific=second_case_specific, notes="Две группы округления и закупки прутков", price_code="rebar_a500_d10_m"),
        ])

    if data.walls_consumables_calc_method not in {"legacy_fixed_amount", "section_total_rate"}:
        raise ValueError(
            "walls_consumables_calc_method must be legacy_fixed_amount or section_total_rate"
        )
    require_non_negative("walls_consumables_rate", data.walls_consumables_rate)
    walls_consumables_amount_raw = data.walls_consumables_tool_amortization_amount_raw
    if data.walls_consumables_calc_method == "section_total_rate":
        direct_cost_base_raw = sum(d(item.line_total_raw) for item in lines)
        walls_consumables_amount_raw = q(
            direct_cost_base_raw * d(data.walls_consumables_rate),
            "0.000001",
        )

    lines.extend([
        line(
            "walls_consumables_tool_amortization",
            "Расходные материалы, амортизация инструмента",
            "комплект",
            1,
            material_unit_price=money(walls_consumables_amount_raw),
            material_total_raw_override=walls_consumables_amount_raw,
            notes=(
                "section_total_rate from direct cost base before consumables"
                if data.walls_consumables_calc_method == "section_total_rate"
                else "manual/fixed amount"
            ),
        ),
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
