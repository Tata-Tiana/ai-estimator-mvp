from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from typing import Any


def _to_decimal(value: float | int | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _round_decimal(value: Decimal | float | int, places: str = "0.001") -> float:
    decimal_value = value if isinstance(value, Decimal) else _to_decimal(value)
    return float(decimal_value.quantize(Decimal(places), rounding=ROUND_HALF_UP))


def _round_money(value: Decimal | float | int) -> int:
    decimal_value = value if isinstance(value, Decimal) else _to_decimal(value)
    return int(decimal_value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _require_positive(name: str, value: float | int | None) -> None:
    if value is None:
        raise ValueError(f"{name} is required")
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")


def _require_non_negative(name: str, value: float | int | None) -> None:
    if value is None:
        raise ValueError(f"{name} is required")
    if value < 0:
        raise ValueError(f"{name} must be greater than or equal to 0")


def _optional_non_negative(name: str, value: float | int | None) -> float:
    if value is None:
        return 0.0
    if value < 0:
        raise ValueError(f"{name} must be greater than or equal to 0")
    return float(value)


def round_up_to_step(value: float, step: float) -> float:
    _require_non_negative("value", value)
    _require_positive("step", step)
    return _round_decimal(_to_decimal(ceil(value / step)) * _to_decimal(step))


def round_up_to_multiple(value: float, multiple: float | None) -> float:
    _require_non_negative("value", value)
    if multiple is None or multiple <= 0:
        return _round_decimal(value, "0.0001")
    return _round_decimal(
        _to_decimal(ceil(value / multiple)) * _to_decimal(multiple),
        "0.0001",
    )


@dataclass(frozen=True)
class RebarItemInput:
    code: str
    name: str
    steel_class: str
    diameter_mm: int
    kg_per_meter: float
    rod_length_m: float
    unit_price_per_m: float
    weight_parts_kg: list[float] = field(default_factory=list)
    source_length_m: float | None = None
    length_parts_m: list[float] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RebarItemInput":
        return cls(**data)

    def validate(self, rebar_calc_method: str = "legacy_weight_to_length") -> None:
        if not self.code:
            raise ValueError("rebar_items.code is required")
        if not self.name:
            raise ValueError(f"rebar_items.{self.code}.name is required")
        _require_positive(f"rebar_items.{self.code}.diameter_mm", self.diameter_mm)
        _require_positive(f"rebar_items.{self.code}.kg_per_meter", self.kg_per_meter)
        _require_positive(f"rebar_items.{self.code}.rod_length_m", self.rod_length_m)
        _require_non_negative(
            f"rebar_items.{self.code}.unit_price_per_m",
            self.unit_price_per_m,
        )
        if rebar_calc_method == "legacy_weight_to_length":
            if not self.weight_parts_kg:
                raise ValueError(f"rebar_items.{self.code}.weight_parts_kg is required")
            for index, value in enumerate(self.weight_parts_kg):
                _require_non_negative(
                    f"rebar_items.{self.code}.weight_parts_kg[{index}]",
                    value,
                )
        elif rebar_calc_method == "spec_length_m":
            if not self.length_parts_m and self.source_length_m is None:
                raise ValueError(
                    f"rebar_items.{self.code}.source_length_m or length_parts_m is required"
                )
            if self.source_length_m is not None:
                _require_non_negative(
                    f"rebar_items.{self.code}.source_length_m",
                    self.source_length_m,
                )
            for index, value in enumerate(self.length_parts_m):
                _require_non_negative(
                    f"rebar_items.{self.code}.length_parts_m[{index}]",
                    value,
                )
        else:
            raise ValueError(
                "rebar_calc_method must be 'legacy_weight_to_length' or 'spec_length_m'"
            )

    def source_length_from_spec_m(self) -> float:
        if self.length_parts_m:
            return _round_decimal(sum(self.length_parts_m), "0.0001")
        if self.source_length_m is None:
            raise ValueError(f"rebar_items.{self.code}.source_length_m is required")
        return _round_decimal(self.source_length_m, "0.0001")


@dataclass(frozen=True)
class SlabZone:
    context: str
    concrete_volume_m3: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SlabZone":
        return cls(**data)


@dataclass(frozen=True)
class ThermalInsertItem:
    eps_size: str
    length_m: float
    material_spec_qty_m3: float
    pack_multiple_qty: float
    material_unit_price: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ThermalInsertItem":
        return cls(**data)


@dataclass(frozen=True)
class FoundationSlabInput:
    project_name: str
    membrane_area_m2: float
    membrane_installation_work_unit_price: float
    membrane_overlap_coeff: float
    membrane_roll_area_m2: float
    planter_standard_roll_unit_price: float
    planterband_per_membrane_roll: float
    planterband_unit_price: float
    formwork_installation_work_unit_price: float
    plywood_unit_price: float
    timber_thickness_m: float
    timber_unit_price: float
    eps50_under_slab_volume_m3: float
    eps50_thickness_m: float
    eps50_laying_work_unit_price: float
    eps_waste_coeff: float
    eps50_pack_volume_m3: float
    eps50_unit_price: float
    rebar_crane_shifts: float
    rebar_crane_unit_price: float
    rebar_waste_coeff: float
    rebar_items: list[RebarItemInput | dict[str, Any]]
    rebar_metal_delivery_trucks: float
    rebar_metal_delivery_unit_price: float
    box_total_metal_weight_kg: float
    concrete_project_volume_m3: float
    concreting_work_unit_price: float
    concrete_waste_coeff: float
    concrete_round_step_m3: float
    concrete_unit_price: float
    concrete_mixer_volume_m3: float
    concrete_delivery_unit_price: float
    concrete_pump_shifts: float
    concrete_pump_unit_price: float
    formwork_dismantling_work_unit_price: float
    logistics_and_supply_amount: float
    consumables_tool_amortization_amount: float
    technical_supervision_amount: float
    logistics_and_supply_calc_method: str = "legacy_fixed_amount"
    logistics_and_supply_rate: float = 0.0
    consumables_tool_amortization_calc_method: str = "legacy_fixed_amount"
    consumables_tool_amortization_rate: float = 0.0
    plywood_calc_method: str = "actual_area_with_waste"
    plywood_sheet_working_area_m2: float = 2.25
    plywood_sheet_width_m: float = 1.52
    plywood_sheet_height_m: float = 1.52
    plywood_waste_coeff: float = 1.05
    slab_edge_height_strategy: str = "max_thickness"
    box_metal_delivery_capacity_kg: float = 10000
    rebar_calc_method: str = "legacy_weight_to_length"
    formwork_calc_method: str = "legacy_perimeter_height"
    slab_side_formwork_area_m2: float | None = None
    slab_formwork_perimeter_m: float | None = None
    slab_edge_height_m: float | None = None
    thermal_insert_mode: str = "legacy"
    thermal_insert_length_m: float | None = None
    thermal_insert_piece_length_m: float | None = None
    thermal_insert_piece_width_m: float | None = None
    thermal_insert_piece_height_m: float | None = None
    thermal_insert_piece_depth_for_work_m: float | None = None
    thermal_insert_piece_depth_for_eps_m: float | None = None
    thermal_insert_installation_work_unit_price: float | None = None
    eps100_thickness_m: float | None = None
    eps100_pack_volume_m3: float | None = None
    eps100_unit_price: float | None = None
    thermal_insert_50_length_m: float | None = None
    thermal_insert_100_length_m: float | None = None
    thermal_insert_50_work_unit_price: float | None = None
    thermal_insert_100_work_unit_price: float | None = None
    thermal_insert_50_material_spec_qty: float | None = None
    thermal_insert_100_material_spec_qty: float | None = None
    thermal_insert_material_waste_coeff: float | None = None
    thermal_insert_50_pack_multiple_qty: float | None = None
    thermal_insert_100_pack_multiple_qty: float | None = None
    thermal_insert_50_material_unit_price: float | None = None
    thermal_insert_100_material_unit_price: float | None = None
    thermal_insert_combined_length_m: float | None = None
    thermal_insert_combined_work_unit_price: float | None = None
    thermal_insert_items: list[ThermalInsertItem | dict[str, Any]] | None = None
    thermal_insert_items_work_unit_price: float | None = None
    slab_zones: list[SlabZone | dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "rebar_items",
            [
                item if isinstance(item, RebarItemInput) else RebarItemInput.from_dict(item)
                for item in self.rebar_items
            ],
        )
        object.__setattr__(
            self,
            "slab_zones",
            [
                zone if isinstance(zone, SlabZone) else SlabZone.from_dict(zone)
                for zone in (self.slab_zones or [])
            ],
        )
        object.__setattr__(
            self,
            "thermal_insert_items",
            [
                item if isinstance(item, ThermalInsertItem) else ThermalInsertItem.from_dict(item)
                for item in (self.thermal_insert_items or [])
            ],
        )
        if self.slab_zones:
            # Purely additive: overriding concrete_project_volume_m3 here means every
            # downstream usage in this file (rebar density, concrete order volume,
            # delivery trips, the concreting-work estimate line) gets the correct
            # summed value with zero other code changes. Empty/absent slab_zones
            # leaves the originally-supplied scalar untouched.
            object.__setattr__(
                self,
                "concrete_project_volume_m3",
                _round_decimal(sum(_to_decimal(zone.concrete_volume_m3) for zone in self.slab_zones)),
            )
        self.validate()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FoundationSlabInput":
        return cls(**data)

    def validate(self) -> None:
        if not self.project_name:
            raise ValueError("project_name is required")

        positive_fields = [
            "membrane_overlap_coeff",
            "membrane_roll_area_m2",
            "planterband_per_membrane_roll",
            "timber_thickness_m",
            "eps50_thickness_m",
            "eps_waste_coeff",
            "eps50_pack_volume_m3",
            "rebar_waste_coeff",
            "concrete_waste_coeff",
            "concrete_round_step_m3",
            "concrete_mixer_volume_m3",
            "plywood_sheet_width_m",
            "plywood_sheet_height_m",
            "plywood_waste_coeff",
            "box_metal_delivery_capacity_kg",
        ]
        for field_name in positive_fields:
            _require_positive(field_name, getattr(self, field_name))

        non_negative_fields = [
            "membrane_area_m2",
            "membrane_installation_work_unit_price",
            "planter_standard_roll_unit_price",
            "planterband_unit_price",
            "formwork_installation_work_unit_price",
            "plywood_unit_price",
            "timber_unit_price",
            "eps50_under_slab_volume_m3",
            "eps50_laying_work_unit_price",
            "eps50_unit_price",
            "rebar_crane_shifts",
            "rebar_crane_unit_price",
            "rebar_metal_delivery_trucks",
            "rebar_metal_delivery_unit_price",
            "box_total_metal_weight_kg",
            "concrete_project_volume_m3",
            "concreting_work_unit_price",
            "concrete_unit_price",
            "concrete_delivery_unit_price",
            "concrete_pump_shifts",
            "concrete_pump_unit_price",
            "formwork_dismantling_work_unit_price",
            "logistics_and_supply_amount",
            "consumables_tool_amortization_amount",
            "technical_supervision_amount",
            "logistics_and_supply_rate",
            "consumables_tool_amortization_rate",
        ]
        for field_name in non_negative_fields:
            _require_non_negative(field_name, getattr(self, field_name))

        if self.logistics_and_supply_calc_method not in {
            "legacy_fixed_amount",
            "section_total_rate",
        }:
            raise ValueError(
                "logistics_and_supply_calc_method must be "
                "'legacy_fixed_amount' or 'section_total_rate'"
            )
        if self.consumables_tool_amortization_calc_method not in {
            "legacy_fixed_amount",
            "section_total_rate",
        }:
            raise ValueError(
                "consumables_tool_amortization_calc_method must be "
                "'legacy_fixed_amount' or 'section_total_rate'"
            )

        for zone in self.slab_zones or []:
            if not zone.context:
                raise ValueError("slab_zones.context is required")
            _require_non_negative(f"slab_zones.{zone.context}.concrete_volume_m3", zone.concrete_volume_m3)

        if not self.rebar_items:
            raise ValueError("rebar_items is required")
        if self.rebar_calc_method not in {
            "legacy_weight_to_length",
            "spec_length_m",
        }:
            raise ValueError(
                "rebar_calc_method must be 'legacy_weight_to_length' or 'spec_length_m'"
            )
        for item in self.rebar_items:
            item.validate(self.rebar_calc_method)

        if self.plywood_calc_method not in {"working_area", "actual_area_with_waste"}:
            raise ValueError(
                "plywood_calc_method must be 'working_area' or 'actual_area_with_waste'"
            )
        if self.plywood_calc_method == "working_area":
            _require_positive(
                "plywood_sheet_working_area_m2",
                self.plywood_sheet_working_area_m2,
            )
        if self.formwork_calc_method not in {
            "legacy_perimeter_height",
            "spec_area",
        }:
            raise ValueError(
                "formwork_calc_method must be 'legacy_perimeter_height' or 'spec_area'"
            )
        if self.formwork_calc_method == "spec_area":
            _require_non_negative(
                "slab_side_formwork_area_m2",
                self.slab_side_formwork_area_m2,
            )
        else:
            _require_positive("slab_formwork_perimeter_m", self.slab_formwork_perimeter_m)
            _require_positive("slab_edge_height_m", self.slab_edge_height_m)

        if self.thermal_insert_mode not in {"legacy", "standard_50_100", "items", "none"}:
            raise ValueError(
                "thermal_insert_mode must be 'legacy', 'standard_50_100', 'items' or 'none'"
            )
        if self.thermal_insert_mode == "none":
            pass
        elif self.thermal_insert_mode == "items":
            # Arbitrary-size thermal inserts (real project case, 2026-07-26): a project can give
            # a single EPS size (or any number of sizes) instead of the fixed 50mm+100mm pair
            # standard_50_100 assumes. Material stays per-size (spec qty * waste, rounded to
            # that size's pack multiple); installation work is one combined line by total
            # length across all sizes, same convention as thermal_insert_combined_length_m.
            _require_positive(
                "thermal_insert_material_waste_coeff",
                self.thermal_insert_material_waste_coeff,
            )
            _require_non_negative(
                "thermal_insert_items_work_unit_price",
                self.thermal_insert_items_work_unit_price,
            )
            if not self.thermal_insert_items:
                raise ValueError(
                    "thermal_insert_items is required for thermal_insert_mode 'items'"
                )
            for item in self.thermal_insert_items:
                if not item.eps_size:
                    raise ValueError("thermal_insert_items.eps_size is required")
                prefix = f"thermal_insert_items.{item.eps_size}"
                _require_non_negative(f"{prefix}.length_m", item.length_m)
                _require_non_negative(
                    f"{prefix}.material_spec_qty_m3", item.material_spec_qty_m3
                )
                _require_positive(f"{prefix}.pack_multiple_qty", item.pack_multiple_qty)
                _require_non_negative(
                    f"{prefix}.material_unit_price", item.material_unit_price
                )
        elif self.thermal_insert_mode == "legacy":
            for field_name in [
                "thermal_insert_piece_length_m",
                "thermal_insert_piece_width_m",
                "thermal_insert_piece_height_m",
                "thermal_insert_piece_depth_for_work_m",
                "thermal_insert_piece_depth_for_eps_m",
                "eps100_thickness_m",
                "eps100_pack_volume_m3",
            ]:
                _require_positive(field_name, getattr(self, field_name))
            for field_name in [
                "thermal_insert_length_m",
                "thermal_insert_installation_work_unit_price",
                "eps100_unit_price",
            ]:
                _require_non_negative(field_name, getattr(self, field_name))
        else:
            _require_positive(
                "thermal_insert_material_waste_coeff",
                self.thermal_insert_material_waste_coeff,
            )
            thermal_insert_50_material_spec_qty = _optional_non_negative(
                "thermal_insert_50_material_spec_qty",
                self.thermal_insert_50_material_spec_qty,
            )
            thermal_insert_100_material_spec_qty = _optional_non_negative(
                "thermal_insert_100_material_spec_qty",
                self.thermal_insert_100_material_spec_qty,
            )
            if (
                thermal_insert_50_material_spec_qty <= 0
                and thermal_insert_100_material_spec_qty <= 0
                and self.thermal_insert_combined_length_m is None
                and self.thermal_insert_50_length_m is None
                and self.thermal_insert_100_length_m is None
            ):
                raise ValueError(
                    "thermal_insert_mode 'standard_50_100' requires at least one "
                    "thermal insert length or material quantity; use mode 'none' "
                    "when the project has no thermal inserts"
                )
            if thermal_insert_50_material_spec_qty > 0:
                _require_non_negative(
                    "thermal_insert_50_material_unit_price",
                    self.thermal_insert_50_material_unit_price,
                )
            if thermal_insert_100_material_spec_qty > 0:
                _require_non_negative(
                    "thermal_insert_100_material_unit_price",
                    self.thermal_insert_100_material_unit_price,
                )
            # Combined-length alternative: some projects give one combined installation
            # length for both 50mm and 100mm layers of the same thermal insert run, with
            # no way to split it per layer (real project case, Elena 2026-07-25) — material
            # stays split by thickness regardless, only the installation work length/price
            # collapses into one line instead of two. Additive: split lengths still work
            # unchanged when combined length is absent.
            combined_length_given = self.thermal_insert_combined_length_m is not None
            split_length_given = (
                self.thermal_insert_50_length_m is not None
                or self.thermal_insert_100_length_m is not None
            )
            if combined_length_given and split_length_given:
                raise ValueError(
                    "Provide either thermal_insert_combined_length_m or split "
                    "thermal_insert_50_length_m/thermal_insert_100_length_m, not both"
                )
            if combined_length_given:
                _require_non_negative(
                    "thermal_insert_combined_length_m", self.thermal_insert_combined_length_m
                )
                _require_non_negative(
                    "thermal_insert_combined_work_unit_price",
                    self.thermal_insert_combined_work_unit_price,
                )
            else:
                thermal_insert_50_length_m = _optional_non_negative(
                    "thermal_insert_50_length_m",
                    self.thermal_insert_50_length_m,
                )
                thermal_insert_100_length_m = _optional_non_negative(
                    "thermal_insert_100_length_m",
                    self.thermal_insert_100_length_m,
                )
                if thermal_insert_50_length_m > 0:
                    _require_non_negative(
                        "thermal_insert_50_work_unit_price",
                        self.thermal_insert_50_work_unit_price,
                    )
                if thermal_insert_100_length_m > 0:
                    _require_non_negative(
                        "thermal_insert_100_work_unit_price",
                        self.thermal_insert_100_work_unit_price,
                    )
            for field_name in [
                "thermal_insert_50_pack_multiple_qty",
                "thermal_insert_100_pack_multiple_qty",
            ]:
                value = getattr(self, field_name)
                if value is not None and value < 0:
                    raise ValueError(f"{field_name} must be greater than or equal to 0")

    def to_dict(self) -> dict[str, Any]:
        result = {key: value for key, value in asdict(self).items() if value is not None}
        if self.rebar_calc_method == "spec_length_m":
            for item in result.get("rebar_items", []):
                if isinstance(item, dict) and not item.get("weight_parts_kg"):
                    item.pop("weight_parts_kg", None)
        if self.formwork_calc_method == "spec_area":
            result.pop("slab_formwork_perimeter_m", None)
            result.pop("slab_edge_height_m", None)
            result.pop("slab_edge_height_strategy", None)
        if self.plywood_calc_method == "actual_area_with_waste":
            result.pop("plywood_sheet_working_area_m2", None)
        return result


@dataclass(frozen=True)
class EstimateLineResult:
    code: str
    name: str
    unit: str
    quantity: float
    material_unit_price: float
    material_total: int
    work_unit_price: float
    work_total: int
    line_total: int
    display_quantity: float | None = None
    line_type: str | None = None
    price_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        if self.display_quantity is None:
            result.pop("display_quantity")
        if self.line_type is None:
            result.pop("line_type")
        if self.price_code is None:
            result.pop("price_code")
        return result


def calculate_line(
    code: str,
    name: str,
    unit: str,
    quantity: float,
    material_unit_price: float = 0.0,
    work_unit_price: float = 0.0,
    display_quantity: float | None = None,
    line_type: str | None = None,
    price_code: str | None = None,
) -> EstimateLineResult:
    quantity_rounded = _round_decimal(quantity, "0.0001")
    material_total = _round_money(
        _to_decimal(quantity_rounded) * _to_decimal(material_unit_price)
    )
    work_total = _round_money(_to_decimal(quantity_rounded) * _to_decimal(work_unit_price))

    return EstimateLineResult(
        code=code,
        name=name,
        unit=unit,
        quantity=quantity_rounded,
        display_quantity=display_quantity,
        material_unit_price=material_unit_price,
        material_total=material_total,
        work_unit_price=work_unit_price,
        work_total=work_total,
        line_total=material_total + work_total,
        line_type=line_type,
        price_code=price_code,
    )


def rebar_price_code(steel_class: str, diameter_mm: int) -> str:
    return f"rebar_{steel_class.lower()}_d{diameter_mm}_m"


def calculate_membrane_block(data: FoundationSlabInput) -> dict[str, Any]:
    membrane_area_with_overlap_m2 = _round_decimal(
        _to_decimal(data.membrane_area_m2) * _to_decimal(data.membrane_overlap_coeff)
    )
    membrane_raw_rolls = _round_decimal(
        _to_decimal(membrane_area_with_overlap_m2) / _to_decimal(data.membrane_roll_area_m2),
        "0.0001",
    )
    membrane_rolls = int(ceil(membrane_raw_rolls))
    planterband_quantity = int(membrane_rolls * data.planterband_per_membrane_roll)

    return {
        "membrane_area_with_overlap_m2": membrane_area_with_overlap_m2,
        "membrane_raw_rolls": membrane_raw_rolls,
        "membrane_rolls": membrane_rolls,
        "planterband_quantity": planterband_quantity,
    }


def calculate_formwork_block(data: FoundationSlabInput) -> dict[str, Any]:
    if data.formwork_calc_method == "spec_area":
        formwork_area_m2 = _round_decimal(data.slab_side_formwork_area_m2)
        formwork_block = {
            "formwork_calc_method": data.formwork_calc_method,
            "slab_side_formwork_area_m2": data.slab_side_formwork_area_m2,
            "formwork_area_m2": formwork_area_m2,
            "plywood_calc_method": data.plywood_calc_method,
        }
    else:
        formwork_area_m2 = _round_decimal(
            _to_decimal(data.slab_formwork_perimeter_m)
            * _to_decimal(data.slab_edge_height_m)
        )
        formwork_block = {
            "formwork_calc_method": data.formwork_calc_method,
            "formwork_area_m2": formwork_area_m2,
            "slab_formwork_perimeter_m": data.slab_formwork_perimeter_m,
            "slab_edge_height_m": data.slab_edge_height_m,
            "slab_edge_height_strategy": data.slab_edge_height_strategy,
            "plywood_calc_method": data.plywood_calc_method,
        }

    if data.plywood_calc_method == "actual_area_with_waste":
        plywood_sheet_area_m2 = _round_decimal(
            _to_decimal(data.plywood_sheet_width_m)
            * _to_decimal(data.plywood_sheet_height_m),
            "0.0001",
        )
        plywood_raw_sheets = _round_decimal(
            _to_decimal(formwork_area_m2)
            * _to_decimal(data.plywood_waste_coeff)
            / _to_decimal(plywood_sheet_area_m2),
            "0.0001",
        )
        formwork_block.update(
            {
                "plywood_sheet_width_m": data.plywood_sheet_width_m,
                "plywood_sheet_height_m": data.plywood_sheet_height_m,
                "plywood_sheet_area_m2": plywood_sheet_area_m2,
                "plywood_waste_coeff": data.plywood_waste_coeff,
            }
        )
    else:
        plywood_raw_sheets = _round_decimal(
            _to_decimal(formwork_area_m2)
            / _to_decimal(data.plywood_sheet_working_area_m2),
            "0.0001",
        )
        formwork_block["plywood_sheet_working_area_m2"] = (
            data.plywood_sheet_working_area_m2
        )

    plywood_sheets = int(ceil(plywood_raw_sheets))
    timber_raw_volume_m3 = _round_decimal(
        _to_decimal(formwork_area_m2) * _to_decimal(data.timber_thickness_m)
    )

    formwork_block.update(
        {
            "plywood_raw_sheets": plywood_raw_sheets,
            "plywood_sheets": plywood_sheets,
            "timber_raw_volume_m3": timber_raw_volume_m3,
        }
    )
    return formwork_block


def calculate_thermal_insert_block(data: FoundationSlabInput) -> dict[str, Any]:
    if data.thermal_insert_mode == "none":
        return {
            "mode": data.thermal_insert_mode,
            "thermal_insert_50_length_m": None,
            "thermal_insert_100_length_m": None,
            "thermal_insert_combined_length_m": None,
            "thermal_insert_50_material_spec_qty": 0,
            "thermal_insert_100_material_spec_qty": 0,
            "thermal_insert_50_material_raw_qty": 0,
            "thermal_insert_100_material_raw_qty": 0,
            "thermal_insert_50_material_purchase_qty": 0,
            "thermal_insert_100_material_purchase_qty": 0,
            "warnings": [],
        }

    if data.thermal_insert_mode == "standard_50_100":
        warnings = []
        thermal_insert_50_material_spec_qty = _optional_non_negative(
            "thermal_insert_50_material_spec_qty",
            data.thermal_insert_50_material_spec_qty,
        )
        thermal_insert_100_material_spec_qty = _optional_non_negative(
            "thermal_insert_100_material_spec_qty",
            data.thermal_insert_100_material_spec_qty,
        )
        if thermal_insert_50_material_spec_qty > 0 and not data.thermal_insert_50_pack_multiple_qty:
            warnings.append(
                "thermal_insert_50_pack_multiple_qty отсутствует или равен 0; "
                "закупочное количество 50 мм не округлено до пачки."
            )
        if thermal_insert_100_material_spec_qty > 0 and not data.thermal_insert_100_pack_multiple_qty:
            warnings.append(
                "thermal_insert_100_pack_multiple_qty отсутствует или равен 0; "
                "закупочное количество 100 мм не округлено до пачки."
            )

        thermal_insert_50_material_raw_qty = _round_decimal(
            _to_decimal(thermal_insert_50_material_spec_qty)
            * _to_decimal(data.thermal_insert_material_waste_coeff),
            "0.0001",
        )
        thermal_insert_100_material_raw_qty = _round_decimal(
            _to_decimal(thermal_insert_100_material_spec_qty)
            * _to_decimal(data.thermal_insert_material_waste_coeff),
            "0.0001",
        )
        thermal_insert_50_material_purchase_qty = round_up_to_multiple(
            thermal_insert_50_material_raw_qty,
            data.thermal_insert_50_pack_multiple_qty,
        )
        thermal_insert_100_material_purchase_qty = round_up_to_multiple(
            thermal_insert_100_material_raw_qty,
            data.thermal_insert_100_pack_multiple_qty,
        )

        return {
            "mode": data.thermal_insert_mode,
            "thermal_insert_50_length_m": data.thermal_insert_50_length_m,
            "thermal_insert_100_length_m": data.thermal_insert_100_length_m,
            "thermal_insert_combined_length_m": data.thermal_insert_combined_length_m,
            "thermal_insert_50_material_spec_qty": thermal_insert_50_material_spec_qty,
            "thermal_insert_100_material_spec_qty": thermal_insert_100_material_spec_qty,
            "thermal_insert_material_waste_coeff": data.thermal_insert_material_waste_coeff,
            "thermal_insert_50_material_raw_qty": thermal_insert_50_material_raw_qty,
            "thermal_insert_100_material_raw_qty": thermal_insert_100_material_raw_qty,
            "thermal_insert_50_pack_multiple_qty": data.thermal_insert_50_pack_multiple_qty,
            "thermal_insert_100_pack_multiple_qty": data.thermal_insert_100_pack_multiple_qty,
            "thermal_insert_50_material_purchase_qty": thermal_insert_50_material_purchase_qty,
            "thermal_insert_100_material_purchase_qty": thermal_insert_100_material_purchase_qty,
            "warnings": warnings,
        }

    if data.thermal_insert_mode == "items":
        items_result = []
        combined_length_m = Decimal("0")
        for item in data.thermal_insert_items:
            material_raw_qty_m3 = _round_decimal(
                _to_decimal(item.material_spec_qty_m3)
                * _to_decimal(data.thermal_insert_material_waste_coeff),
                "0.0001",
            )
            material_purchase_qty_m3 = round_up_to_multiple(
                material_raw_qty_m3,
                item.pack_multiple_qty,
            )
            combined_length_m += _to_decimal(item.length_m)
            items_result.append(
                {
                    "eps_size": item.eps_size,
                    "length_m": item.length_m,
                    "material_spec_qty_m3": item.material_spec_qty_m3,
                    "material_raw_qty_m3": material_raw_qty_m3,
                    "pack_multiple_qty": item.pack_multiple_qty,
                    "material_purchase_qty_m3": material_purchase_qty_m3,
                    "material_unit_price": item.material_unit_price,
                }
            )
        return {
            "mode": data.thermal_insert_mode,
            "items": items_result,
            "combined_length_m": _round_decimal(combined_length_m),
            "thermal_insert_items_work_unit_price": data.thermal_insert_items_work_unit_price,
            "warnings": [],
        }

    thermal_insert_raw_pieces = _round_decimal(
        _to_decimal(data.thermal_insert_length_m)
        / _to_decimal(data.thermal_insert_piece_length_m),
        "0.0001",
    )
    thermal_insert_pieces = int(ceil(thermal_insert_raw_pieces))
    thermal_insert_control_volume_m3 = _round_decimal(
        _to_decimal(thermal_insert_pieces)
        * _to_decimal(data.thermal_insert_piece_width_m)
        * _to_decimal(data.thermal_insert_piece_height_m)
        * _to_decimal(data.thermal_insert_piece_depth_for_work_m)
    )

    warnings = []
    if data.thermal_insert_piece_depth_for_eps_m != data.slab_edge_height_m:
        warnings.append(
            "thermal_insert_piece_depth_for_eps_m отличается от slab_edge_height_m; "
            "Елена уточнила, что обычно берём высоту плиты, но в текущем кейсе "
            "Excel использует/даёт значение, которое после округления не меняет закупку."
        )

    return {
        "mode": data.thermal_insert_mode,
        "thermal_insert_raw_pieces": thermal_insert_raw_pieces,
        "thermal_insert_pieces": thermal_insert_pieces,
        "thermal_insert_control_volume_m3": thermal_insert_control_volume_m3,
        "thermal_insert_piece_depth_for_eps_m": data.thermal_insert_piece_depth_for_eps_m,
        "slab_edge_height_m": data.slab_edge_height_m,
        "warnings": warnings,
    }


def calculate_eps_block(
    data: FoundationSlabInput,
    thermal_insert_block: dict[str, Any],
) -> dict[str, Any]:
    eps50_laying_area_m2 = _round_decimal(
        _to_decimal(data.eps50_under_slab_volume_m3) / _to_decimal(data.eps50_thickness_m)
    )
    eps50_under_slab_required_volume_m3 = _round_decimal(
        _to_decimal(eps50_laying_area_m2)
        * _to_decimal(data.eps50_thickness_m)
        * _to_decimal(data.eps_waste_coeff)
    )
    if data.thermal_insert_mode in {"standard_50_100", "items", "none"}:
        eps50_required_volume_m3 = eps50_under_slab_required_volume_m3
        eps50_raw_packs = _round_decimal(
            _to_decimal(eps50_required_volume_m3) / _to_decimal(data.eps50_pack_volume_m3),
            "0.0001",
        )
        eps50_packs = int(ceil(eps50_raw_packs))
        eps50_order_volume_m3 = _round_decimal(
            _to_decimal(eps50_packs) * _to_decimal(data.eps50_pack_volume_m3),
            "0.0001",
        )
        return {
            "mode": data.thermal_insert_mode,
            "eps50_laying_area_m2": eps50_laying_area_m2,
            "eps50_under_slab_required_volume_m3": eps50_under_slab_required_volume_m3,
            "eps50_thermal_insert_volume_m3": 0,
            "eps50_required_volume_m3": eps50_required_volume_m3,
            "eps50_raw_packs": eps50_raw_packs,
            "eps50_packs": eps50_packs,
            "eps50_order_volume_m3": eps50_order_volume_m3,
            "eps100_required_volume_m3": 0,
            "eps100_raw_packs": 0,
            "eps100_packs": 0,
            "eps100_order_volume_m3": 0,
        }

    thermal_insert_pieces = thermal_insert_block["thermal_insert_pieces"]
    eps50_thermal_insert_volume_m3 = _round_decimal(
        _to_decimal(thermal_insert_pieces)
        * _to_decimal(data.eps50_thickness_m)
        * _to_decimal(data.thermal_insert_piece_height_m)
        * _to_decimal(data.thermal_insert_piece_depth_for_eps_m)
    )
    eps50_required_volume_m3 = _round_decimal(
        _to_decimal(eps50_under_slab_required_volume_m3)
        + _to_decimal(eps50_thermal_insert_volume_m3)
    )
    eps50_raw_packs = _round_decimal(
        _to_decimal(eps50_required_volume_m3) / _to_decimal(data.eps50_pack_volume_m3),
        "0.0001",
    )
    eps50_packs = int(ceil(eps50_raw_packs))
    eps50_order_volume_m3 = _round_decimal(
        _to_decimal(eps50_packs) * _to_decimal(data.eps50_pack_volume_m3),
        "0.0001",
    )

    eps100_required_volume_m3 = _round_decimal(
        _to_decimal(thermal_insert_pieces)
        * _to_decimal(data.eps100_thickness_m)
        * _to_decimal(data.thermal_insert_piece_height_m)
        * _to_decimal(data.thermal_insert_piece_depth_for_eps_m)
    )
    eps100_raw_packs = _round_decimal(
        _to_decimal(eps100_required_volume_m3) / _to_decimal(data.eps100_pack_volume_m3),
        "0.0001",
    )
    eps100_packs = int(ceil(eps100_raw_packs))
    eps100_order_volume_m3 = _round_decimal(
        _to_decimal(eps100_packs) * _to_decimal(data.eps100_pack_volume_m3),
        "0.0001",
    )

    return {
        "mode": data.thermal_insert_mode,
        "eps50_laying_area_m2": eps50_laying_area_m2,
        "eps50_under_slab_required_volume_m3": eps50_under_slab_required_volume_m3,
        "eps50_thermal_insert_volume_m3": eps50_thermal_insert_volume_m3,
        "eps50_required_volume_m3": eps50_required_volume_m3,
        "eps50_raw_packs": eps50_raw_packs,
        "eps50_packs": eps50_packs,
        "eps50_order_volume_m3": eps50_order_volume_m3,
        "eps100_required_volume_m3": eps100_required_volume_m3,
        "eps100_raw_packs": eps100_raw_packs,
        "eps100_packs": eps100_packs,
        "eps100_order_volume_m3": eps100_order_volume_m3,
    }


def calculate_rebar_line(
    item: RebarItemInput,
    rebar_waste_coeff: float,
    rebar_calc_method: str = "legacy_weight_to_length",
) -> tuple[EstimateLineResult, dict[str, Any]]:
    if rebar_calc_method == "spec_length_m":
        source_length_m = item.source_length_from_spec_m()
        design_weight_kg = _round_decimal(
            _to_decimal(source_length_m) * _to_decimal(item.kg_per_meter),
            "0.0001",
        )
        rebar_raw_length_m = source_length_m
        rebar_total_weight_kg = design_weight_kg
    else:
        rebar_total_weight_kg = _round_decimal(sum(item.weight_parts_kg), "0.0001")
        rebar_raw_length_m = _round_decimal(
            _to_decimal(rebar_total_weight_kg) / _to_decimal(item.kg_per_meter),
            "0.0001",
        )
        source_length_m = rebar_raw_length_m
        design_weight_kg = rebar_total_weight_kg

    rebar_length_with_waste_m = _round_decimal(
        _to_decimal(rebar_raw_length_m) * _to_decimal(rebar_waste_coeff),
        "0.0001",
    )
    rebar_raw_rods = _round_decimal(
        _to_decimal(rebar_length_with_waste_m) / _to_decimal(item.rod_length_m),
        "0.0001",
    )
    rebar_rods = int(ceil(rebar_raw_rods))
    rebar_order_length_m = _round_decimal(
        _to_decimal(rebar_rods) * _to_decimal(item.rod_length_m),
        "0.0001",
    )
    rebar_control_weight_kg = _round_decimal(
        _to_decimal(rebar_length_with_waste_m) * _to_decimal(item.kg_per_meter),
        "0.0001",
    )
    delivery_weight_kg = _round_decimal(
        _to_decimal(rebar_order_length_m) * _to_decimal(item.kg_per_meter),
        "0.0001",
    )

    line = calculate_line(
        code=item.code,
        name=item.name,
        unit="мп",
        quantity=rebar_order_length_m,
        material_unit_price=item.unit_price_per_m,
        price_code=rebar_price_code(item.steel_class, item.diameter_mm),
    )
    control = {
        "name": item.name,
        "steel_class": item.steel_class,
        "diameter_mm": item.diameter_mm,
        "calculation_method": rebar_calc_method,
        "total_weight_kg": rebar_total_weight_kg,
        "raw_length_m": rebar_raw_length_m,
        "source_length_m": source_length_m,
        "length_with_waste_m": rebar_length_with_waste_m,
        "raw_rods": rebar_raw_rods,
        "rods": rebar_rods,
        "order_length_m": rebar_order_length_m,
        "kg_per_meter": item.kg_per_meter,
        "rod_length_m": item.rod_length_m,
        "unit_price_per_m": item.unit_price_per_m,
        "design_weight_kg": design_weight_kg,
        "delivery_weight_kg": delivery_weight_kg,
        "control_weight_kg": rebar_control_weight_kg,
    }
    if item.weight_parts_kg:
        control["weight_parts_kg"] = item.weight_parts_kg
    if item.length_parts_m:
        control["length_parts_m"] = item.length_parts_m
    return line, control


def calculate_rebar_block(
    data: FoundationSlabInput,
) -> tuple[dict[str, Any], list[EstimateLineResult]]:
    rebar_lines = []
    items: dict[str, Any] = {}

    for item in data.rebar_items:
        line, control = calculate_rebar_line(
            item,
            data.rebar_waste_coeff,
            data.rebar_calc_method,
        )
        rebar_lines.append(line)
        items[item.code] = control

    rebar_frame_assembly_quantity_m = _round_decimal(
        sum(line.quantity for line in rebar_lines),
        "0.0001",
    )
    foundation_slab_rebar_control_weight_kg = _round_decimal(
        sum(item["control_weight_kg"] for item in items.values()),
        "0.0001",
    )
    foundation_slab_rebar_design_weight_kg = _round_decimal(
        sum(item["design_weight_kg"] for item in items.values()),
        "0.0001",
    )
    foundation_slab_rebar_delivery_weight_kg = _round_decimal(
        sum(item["delivery_weight_kg"] for item in items.values()),
        "0.0001",
    )
    suggested_box_metal_delivery_trucks = int(
        ceil(data.box_total_metal_weight_kg / data.box_metal_delivery_capacity_kg)
    )
    suggested_foundation_rebar_delivery_trucks = int(
        ceil(
            foundation_slab_rebar_delivery_weight_kg
            / data.box_metal_delivery_capacity_kg
        )
    )
    reinforcement_density_design_kg_per_m3 = _round_decimal(
        _to_decimal(foundation_slab_rebar_design_weight_kg)
        / _to_decimal(data.concrete_project_volume_m3),
        "0.0001",
    )
    reinforcement_density_delivery_kg_per_m3 = _round_decimal(
        _to_decimal(foundation_slab_rebar_delivery_weight_kg)
        / _to_decimal(data.concrete_project_volume_m3),
        "0.0001",
    )
    warnings = []
    if data.rebar_metal_delivery_trucks != suggested_box_metal_delivery_trucks:
        warnings.append(
            "rebar_metal_delivery_trucks отличается от suggested_box_metal_delivery_trucks; "
            "строка доставки арматуры остаётся manual/fixed и не меняется автоматически."
        )

    return (
        {
            "rebar_calc_method": data.rebar_calc_method,
            "items": items,
            "rebar_frame_assembly_quantity_m": rebar_frame_assembly_quantity_m,
            "foundation_slab_rebar_control_weight_kg": foundation_slab_rebar_control_weight_kg,
            "foundation_slab_rebar_design_weight_kg": foundation_slab_rebar_design_weight_kg,
            "foundation_slab_rebar_delivery_weight_kg": foundation_slab_rebar_delivery_weight_kg,
            "concrete_project_volume_m3": data.concrete_project_volume_m3,
            "reinforcement_density_design_kg_per_m3": reinforcement_density_design_kg_per_m3,
            "reinforcement_density_delivery_kg_per_m3": reinforcement_density_delivery_kg_per_m3,
            "box_total_metal_weight_kg": data.box_total_metal_weight_kg,
            "box_metal_delivery_capacity_kg": data.box_metal_delivery_capacity_kg,
            "suggested_foundation_rebar_delivery_trucks": suggested_foundation_rebar_delivery_trucks,
            "suggested_box_metal_delivery_trucks": suggested_box_metal_delivery_trucks,
            "actual_rebar_metal_delivery_trucks": data.rebar_metal_delivery_trucks,
            "warnings": warnings,
        },
        rebar_lines,
    )


def calculate_concrete_block(
    data: FoundationSlabInput,
    rebar_block: dict[str, Any],
) -> dict[str, Any]:
    concrete_raw_order_volume_m3 = _round_decimal(
        _to_decimal(data.concrete_project_volume_m3) * _to_decimal(data.concrete_waste_coeff)
    )
    concrete_order_volume_m3 = round_up_to_step(
        concrete_raw_order_volume_m3,
        data.concrete_round_step_m3,
    )
    concrete_delivery_raw_trips = _round_decimal(
        _to_decimal(concrete_order_volume_m3) / _to_decimal(data.concrete_mixer_volume_m3),
        "0.0001",
    )
    concrete_delivery_trips = int(ceil(concrete_delivery_raw_trips))
    reinforcement_density_kg_per_m3 = _round_decimal(
        _to_decimal(rebar_block["foundation_slab_rebar_control_weight_kg"])
        / _to_decimal(data.concrete_project_volume_m3),
        "0.0001",
    )
    reinforcement_density_kg_per_m3_rounded = _round_money(reinforcement_density_kg_per_m3)

    return {
        "concrete_raw_order_volume_m3": concrete_raw_order_volume_m3,
        "concrete_order_volume_m3": concrete_order_volume_m3,
        "concrete_delivery_raw_trips": concrete_delivery_raw_trips,
        "concrete_delivery_trips": concrete_delivery_trips,
        "reinforcement_density_kg_per_m3": reinforcement_density_kg_per_m3,
        "reinforcement_density_kg_per_m3_rounded": reinforcement_density_kg_per_m3_rounded,
        "reinforcement_density_design_kg_per_m3": rebar_block[
            "reinforcement_density_design_kg_per_m3"
        ],
        "reinforcement_density_delivery_kg_per_m3": rebar_block[
            "reinforcement_density_delivery_kg_per_m3"
        ],
    }


def calculate_manual_lines_block(data: FoundationSlabInput) -> dict[str, Any]:
    logistics_amount = data.logistics_and_supply_amount
    consumables_amount = data.consumables_tool_amortization_amount
    return {
        "rebar_crane_supply": {
            "quantity": data.rebar_crane_shifts,
            "unit_price": data.rebar_crane_unit_price,
            "line_type": "fixed/manual",
        },
        "rebar_metal_delivery": {
            "quantity": data.rebar_metal_delivery_trucks,
            "unit_price": data.rebar_metal_delivery_unit_price,
            "line_type": "fixed/manual",
        },
        "concrete_pump_32m": {
            "quantity": data.concrete_pump_shifts,
            "unit_price": data.concrete_pump_unit_price,
            "line_type": "fixed/manual",
        },
        "logistics_and_supply": {
            "quantity": 1,
            "unit_price": logistics_amount,
            "calc_method": data.logistics_and_supply_calc_method,
            "rate": data.logistics_and_supply_rate,
            "line_type": "fixed/manual or section_total_rate",
        },
        "consumables_tool_amortization": {
            "quantity": 1,
            "unit_price": consumables_amount,
            "calc_method": data.consumables_tool_amortization_calc_method,
            "rate": data.consumables_tool_amortization_rate,
            "line_type": "fixed/manual or section_total_rate",
        },
        "technical_supervision": {
            "quantity": 1,
            "unit_price": data.technical_supervision_amount,
            "line_type": "fixed/manual",
        },
    }


def calculate_internal_estimate_lines(
    data: FoundationSlabInput,
    calculation_blocks: dict[str, Any],
    rebar_lines: list[EstimateLineResult],
) -> list[EstimateLineResult]:
    membrane = calculation_blocks["membrane"]
    formwork = calculation_blocks["formwork"]
    eps = calculation_blocks["eps"]
    thermal_insert = calculation_blocks["thermal_insert"]
    concrete = calculation_blocks["concrete"]

    lines = [
        calculate_line(
            code="planter_membrane_installation",
            name="Монтаж мембраны PLANTER стандарт",
            unit="м2",
            quantity=data.membrane_area_m2,
            work_unit_price=data.membrane_installation_work_unit_price,
            price_code="planter_membrane_installation_work_m2",
        ),
        calculate_line(
            code="planter_standard_material",
            name="Planter Standard Технониколь",
            unit="рул",
            quantity=membrane["membrane_rolls"],
            material_unit_price=data.planter_standard_roll_unit_price,
            price_code="planter_standard_roll",
        ),
        calculate_line(
            code="planterband_material",
            name="PLANTERBAND 10м х 10см",
            unit="шт",
            quantity=membrane["planterband_quantity"],
            material_unit_price=data.planterband_unit_price,
            price_code="planterband_item",
        ),
        calculate_line(
            code="formwork_installation",
            name="Монтаж опалубки из пиломатериалов для отбортовки плиты",
            unit="м2",
            quantity=formwork["formwork_area_m2"],
            work_unit_price=data.formwork_installation_work_unit_price,
            price_code="timber_formwork_installation_work_m2",
        ),
        calculate_line(
            code="formwork_plywood",
            name="Фанера ФК 1,52 * 1,52 толщиной 18 мм",
            unit="шт",
            quantity=formwork["plywood_sheets"],
            material_unit_price=data.plywood_unit_price,
            price_code="plywood_1520x1520_18mm_sheet",
        ),
        calculate_line(
            code="formwork_timber",
            name="Пиломатериал обрезной хвойных пород ГОСТ",
            unit="м3",
            quantity=formwork["timber_raw_volume_m3"],
            display_quantity=_round_decimal(formwork["timber_raw_volume_m3"], "0.01"),
            material_unit_price=data.timber_unit_price,
            price_code="timber_m3",
        ),
        calculate_line(
            code="eps50_laying_under_slab",
            name="Укладка ЭППС 50мм под плитой",
            unit="м2",
            quantity=eps["eps50_laying_area_m2"],
            work_unit_price=data.eps50_laying_work_unit_price,
            price_code="eps_laying_work_m2",
        ),
        *thermal_insert_estimate_lines(data, eps, thermal_insert),
        calculate_line(
            code="rebar_crane_supply",
            name="Подача арматуры автокраном",
            unit="смена",
            quantity=data.rebar_crane_shifts,
            material_unit_price=data.rebar_crane_unit_price,
            price_code="crane_shift",
        ),
        calculate_line(
            code="rebar_frame_assembly",
            name="Изготовление и монтаж каркаса армирования фундаментной плиты из арматуры",
            unit="мп",
            quantity=calculation_blocks["rebar"]["rebar_frame_assembly_quantity_m"],
        ),
        *rebar_lines,
        calculate_line(
            code="rebar_metal_delivery",
            name="Доставка арматуры, металла",
            unit="маш",
            quantity=data.rebar_metal_delivery_trucks,
            material_unit_price=data.rebar_metal_delivery_unit_price,
            price_code="metal_delivery_truck",
        ),
        calculate_line(
            code="foundation_slab_concreting_work",
            name="Бетонирование фундаментной плиты в опалубке бетоном В22,5 (М300)",
            unit="м3",
            quantity=data.concrete_project_volume_m3,
            work_unit_price=data.concreting_work_unit_price,
            price_code="concrete_placing_work_m3",
        ),
        calculate_line(
            code="concrete_b22_5_m300_material",
            name="Бетон марки В22,5 (М300)",
            unit="м3",
            quantity=concrete["concrete_order_volume_m3"],
            material_unit_price=data.concrete_unit_price,
            price_code="concrete_b22_5_m3",
        ),
        calculate_line(
            code="concrete_delivery",
            name="Доставка бетона до объекта",
            unit="рейс",
            quantity=concrete["concrete_delivery_trips"],
            material_unit_price=data.concrete_delivery_unit_price,
            price_code="concrete_delivery_trip",
        ),
        calculate_line(
            code="concrete_pump_32m",
            name="Работа бетононасоса 32м + гаситель",
            unit="смена",
            quantity=data.concrete_pump_shifts,
            material_unit_price=data.concrete_pump_unit_price,
            price_code="concrete_pump_32m_shift",
        ),
        calculate_line(
            code="formwork_dismantling",
            name="Демонтаж опалубки после завершения бетонирования",
            unit="м2",
            quantity=formwork["formwork_area_m2"],
            work_unit_price=data.formwork_dismantling_work_unit_price,
            price_code="formwork_dismantling_work_m2",
        ),
    ]

    direct_cost_base = sum(line.line_total for line in lines)
    logistics_amount = data.logistics_and_supply_amount
    if data.logistics_and_supply_calc_method == "section_total_rate":
        logistics_amount = _round_money(
            _to_decimal(direct_cost_base) * _to_decimal(data.logistics_and_supply_rate)
        )
    consumables_amount = data.consumables_tool_amortization_amount
    if data.consumables_tool_amortization_calc_method == "section_total_rate":
        consumables_amount = _round_money(
            _to_decimal(direct_cost_base)
            * _to_decimal(data.consumables_tool_amortization_rate)
        )

    lines.extend(
        [
            calculate_line(
                code="logistics_and_supply",
                name="Логистика и снабжение",
                unit="-",
                quantity=1,
                material_unit_price=logistics_amount,
                line_type="calculated_percentage_addon"
                if data.logistics_and_supply_calc_method == "section_total_rate"
                else None,
            ),
            calculate_line(
                code="consumables_tool_amortization",
                name="Расходные материалы, амортизация инструмента",
                unit="комплект",
                quantity=1,
                material_unit_price=consumables_amount,
                line_type="calculated_percentage_addon"
                if data.consumables_tool_amortization_calc_method == "section_total_rate"
                else None,
            ),
            calculate_line(
                code="technical_supervision",
                name="Технический надзор",
                unit="-",
                quantity=1,
                work_unit_price=data.technical_supervision_amount,
                price_code="technical_supervision_fixed",
            ),
            calculate_line(
                code="procurement_warehouse_costs_excel_structure",
                name="Заготовительно-складские расходы",
                unit="-",
                quantity=1,
                line_type="zero_excel_structure_line",
            ),
            calculate_line(
                code="overhead_general_business_costs_excel_structure",
                name="Накладные и общехозяйственные расходы",
                unit="-",
                quantity=1,
                line_type="zero_excel_structure_line",
            ),
            calculate_line(
                code="estimated_profit_excel_structure",
                name="Сметная прибыль",
                unit="-",
                quantity=1,
                line_type="zero_excel_structure_line",
            ),
        ]
    )

    return lines


def thermal_insert_estimate_lines(
    data: FoundationSlabInput,
    eps: dict[str, Any],
    thermal_insert: dict[str, Any],
) -> list[EstimateLineResult]:
    eps50_under_slab_line = calculate_line(
        code="eps50_penoplex_geo_material",
        name="Пеноплэкс ГЕО 50 мм под плитой",
        unit="м3",
        quantity=eps["eps50_order_volume_m3"],
        display_quantity=_round_decimal(eps["eps50_order_volume_m3"], "0.01"),
        material_unit_price=data.eps50_unit_price,
        price_code="eps_geo_50_m3",
    )

    if data.thermal_insert_mode == "none":
        return [eps50_under_slab_line]

    if data.thermal_insert_mode == "standard_50_100":
        if data.thermal_insert_combined_length_m is not None:
            # PDF gives one combined installation length for both layers of the same
            # thermal insert run, with no way to split it per thickness (real project
            # case, Elena 2026-07-25) — one work line instead of two; material stays split.
            installation_lines = [
                calculate_line(
                    code="thermal_insert_combined_installation",
                    name="Устройство и монтаж термовставок 50+100 мм",
                    unit="мп",
                    quantity=data.thermal_insert_combined_length_m,
                    work_unit_price=data.thermal_insert_combined_work_unit_price,
                    price_code="thermal_insert_combined_installation_work_m",
                ),
            ]
        else:
            installation_lines = []
            if _optional_non_negative(
                "thermal_insert_50_length_m",
                data.thermal_insert_50_length_m,
            ) > 0:
                installation_lines.append(
                    calculate_line(
                        code="thermal_insert_50_installation",
                        name="Устройство и монтаж термовставок 50 мм",
                        unit="мп",
                        quantity=data.thermal_insert_50_length_m,
                        work_unit_price=data.thermal_insert_50_work_unit_price,
                        price_code="thermal_insert_50_installation_work_m",
                    )
                )
            if _optional_non_negative(
                "thermal_insert_100_length_m",
                data.thermal_insert_100_length_m,
            ) > 0:
                installation_lines.append(
                    calculate_line(
                        code="thermal_insert_100_installation",
                        name="Устройство и монтаж термовставок 100 мм",
                        unit="мп",
                        quantity=data.thermal_insert_100_length_m,
                        work_unit_price=data.thermal_insert_100_work_unit_price,
                        price_code="thermal_insert_100_installation_work_m",
                    )
                )

        lines = installation_lines + [eps50_under_slab_line]
        if thermal_insert["thermal_insert_50_material_purchase_qty"] > 0:
            lines.append(
                calculate_line(
                    code="thermal_insert_50_material",
                    name="Материал термовставок 50 мм",
                    unit="м3",
                    quantity=thermal_insert["thermal_insert_50_material_purchase_qty"],
                    display_quantity=_round_decimal(
                        thermal_insert["thermal_insert_50_material_purchase_qty"],
                        "0.01",
                    ),
                    material_unit_price=data.thermal_insert_50_material_unit_price,
                    price_code="thermal_insert_50_material_m3",
                )
            )
        if thermal_insert["thermal_insert_100_material_purchase_qty"] > 0:
            lines.append(
                calculate_line(
                    code="thermal_insert_100_material",
                    name="Материал термовставок 100 мм",
                    unit="м3",
                    quantity=thermal_insert["thermal_insert_100_material_purchase_qty"],
                    display_quantity=_round_decimal(
                        thermal_insert["thermal_insert_100_material_purchase_qty"],
                        "0.01",
                    ),
                    material_unit_price=data.thermal_insert_100_material_unit_price,
                    price_code="thermal_insert_100_material_m3",
                )
            )
        return lines

    if data.thermal_insert_mode == "items":
        lines = [
            calculate_line(
                code="thermal_insert_items_installation",
                name="Устройство и монтаж термовставок",
                unit="мп",
                quantity=thermal_insert["combined_length_m"],
                work_unit_price=data.thermal_insert_items_work_unit_price,
                price_code="thermal_insert_items_installation_work_m",
            ),
        ]
        for index, item in enumerate(thermal_insert["items"]):
            lines.append(
                calculate_line(
                    code=f"thermal_insert_material_item_{index}",
                    name=f"Материал термовставок {item['eps_size']}",
                    unit="м3",
                    quantity=item["material_purchase_qty_m3"],
                    display_quantity=_round_decimal(item["material_purchase_qty_m3"], "0.01"),
                    material_unit_price=item["material_unit_price"],
                    price_code="thermal_insert_item_material_m3",
                )
            )
        lines.append(eps50_under_slab_line)
        return lines

    return [
        calculate_line(
            code="thermal_insert_installation",
            name="Устройство и монтаж термовкладыша 150*400*250мм шаг 200мм",
            unit="мп",
            quantity=data.thermal_insert_length_m,
            work_unit_price=data.thermal_insert_installation_work_unit_price,
            price_code="thermal_insert_installation_work_m",
        ),
        calculate_line(
            code="eps50_penoplex_geo_material",
            name="Пеноплэкс ГЕО 50 мм",
            unit="м3",
            quantity=eps["eps50_order_volume_m3"],
            display_quantity=_round_decimal(eps["eps50_order_volume_m3"], "0.01"),
            material_unit_price=data.eps50_unit_price,
            price_code="eps_geo_50_m3",
        ),
        calculate_line(
            code="eps100_penoplex_geo_material",
            name="Пеноплэкс ГЕО 100 мм",
            unit="м3",
            quantity=eps["eps100_order_volume_m3"],
            display_quantity=_round_decimal(eps["eps100_order_volume_m3"], "0.01"),
            material_unit_price=data.eps100_unit_price,
            price_code="eps_geo_100_m3",
        ),
    ]


def calculate_internal_totals(lines: list[EstimateLineResult]) -> dict[str, int]:
    internal_materials_total = sum(line.material_total for line in lines)
    internal_works_total = sum(line.work_total for line in lines)

    return {
        "internal_materials_total": internal_materials_total,
        "internal_works_total": internal_works_total,
        "internal_section_total": internal_materials_total + internal_works_total,
    }


def collect_warnings(calculation_blocks: dict[str, Any]) -> list[str]:
    warnings = []
    for block_name, block in calculation_blocks.items():
        if isinstance(block, dict):
            for warning in block.get("warnings", []):
                warnings.append(f"{block_name}: {warning}")
    return warnings


def confirmed_rules(
    thermal_insert_mode: str = "legacy",
    formwork_calc_method: str = "legacy_perimeter_height",
    rebar_calc_method: str = "legacy_weight_to_length",
    plywood_calc_method: str = "working_area",
) -> list[str]:
    rules = [
        "PLANTERBAND = количество рулонов мембраны * 4.",
        "Пиломатериал = площадь опалубки * 0.05, без дополнительного запаса.",
        "Пеноплэкс = ЭППС.",
        "Доставка металла ориентируется на 10 тонн на машину по листу Коробка.",
    ]
    if plywood_calc_method == "actual_area_with_waste":
        rules.extend(
            [
                "Фанера в production-стандарте считается по листу 1.52 x 1.52 м.",
                "Запас на фанеру фундаментной плиты = 5%.",
                "Количество листов фанеры округляется вверх до целого.",
                "plywood_calc_method, размер листа и запас являются системными настройками, а не ручными полями Елены.",
            ]
        )
    else:
        rules.append(
            "Legacy-фанера: текущий старый кейс считает через рабочую площадь 2.25 м2."
        )
    if formwork_calc_method == "spec_area":
        rules.extend(
            [
                "В новом стандарте площадь опалубки бортов фундаментной плиты берётся из спецификации.",
                "Периметр и высота борта не являются обязательными входами для расчёта опалубки в production-стандарте.",
                "Фанера, пиломатериал, монтаж и демонтаж опалубки считаются от готовой площади опалубки.",
            ]
        )
    else:
        rules.extend(
            [
                "Legacy-опалубка: борта = внешний периметр фундаментной плиты.",
                "Legacy-опалубка: при разных толщинах плит можно брать максимальную толщину.",
            ]
        )

    if thermal_insert_mode == "standard_50_100":
        rules.extend(
            [
                "Термовставки стандартного типа считаются по тем слоям, которые явно есть в проекте: 50 мм, 100 мм или одна общая длина для двух слоёв.",
                "Работы по термовставкам считаются по длине в м.п. из спецификации.",
                "Материал термовставок берётся из спецификации, умножается на запас и округляется до кратности пачки.",
                "Старая логика через элемент, шаг 600 мм и термовкладыш 150 мм не используется в новом стандарте.",
            ]
        )
    elif thermal_insert_mode == "items":
        rules.extend(
            [
                "Термовставки произвольного типоразмера (не только 50/100 мм) считаются построчно по eps_size.",
                "Работа по термовставкам — одна общая строка по сумме длин всех типоразмеров.",
                "Материал каждого типоразмера — из спецификации, умножается на запас и округляется до кратности своей пачки.",
            ]
        )
    elif thermal_insert_mode == "none":
        rules.append("Термовставок в проекте нет: строки работ и материалов термовставок не формируются.")
    else:
        rules.append("ЭППС 50 мм + ЭППС 100 мм = термовкладыш 150 мм.")

    if rebar_calc_method == "spec_length_m":
        rules.extend(
            [
                "Арматура в новом стандарте приходит из спецификации в м.п., а не в кг.",
                "Закупочная длина арматуры = м.п. из спецификации * запас, затем округление до целых хлыстов.",
                "Стоимость арматуры считается по закупочной длине в м.п.",
                "Вес арматуры считается через kg_per_meter для доставки и контроля плотности армирования.",
                "Доставка металла окончательно агрегируется на уровне коробки дома, а строка доставки в разделе остаётся manual/fixed.",
            ]
        )
    else:
        rules.append(
            "Legacy-арматура: вес из спецификации переводится в м.п. через kg_per_meter, затем запас, хлысты и стоимость по м.п."
        )
    return rules


def calculate_foundation_slab(data: FoundationSlabInput) -> dict[str, Any]:
    membrane_block = calculate_membrane_block(data)
    formwork_block = calculate_formwork_block(data)
    thermal_insert_block = calculate_thermal_insert_block(data)
    eps_block = calculate_eps_block(data, thermal_insert_block)
    rebar_block, rebar_lines = calculate_rebar_block(data)
    concrete_block = calculate_concrete_block(data, rebar_block)
    manual_lines_block = calculate_manual_lines_block(data)

    calculation_blocks = {
        "confirmed_rules": confirmed_rules(
            data.thermal_insert_mode,
            data.formwork_calc_method,
            data.rebar_calc_method,
            data.plywood_calc_method,
        ),
        "membrane": membrane_block,
        "formwork": formwork_block,
        "eps": eps_block,
        "thermal_insert": thermal_insert_block,
        "rebar": rebar_block,
        "concrete": concrete_block,
        "manual_lines": manual_lines_block,
        "slab_zones": {
            "used": bool(data.slab_zones),
            "zone_count": len(data.slab_zones or []),
            "concrete_project_volume_m3": data.concrete_project_volume_m3,
        },
    }
    estimate_lines = calculate_internal_estimate_lines(
        data,
        calculation_blocks,
        rebar_lines,
    )
    internal_totals = calculate_internal_totals(estimate_lines)
    warnings = collect_warnings(calculation_blocks)

    return {
        "inputs": data.to_dict(),
        "calculation_blocks": calculation_blocks,
        "warnings": warnings,
        "estimate_lines": [line.to_dict() for line in estimate_lines],
        "internal_totals": internal_totals,
    }
