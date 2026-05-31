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


def round_up_to_step(value: float, step: float) -> float:
    _require_non_negative("value", value)
    _require_positive("step", step)
    return _round_decimal(_to_decimal(ceil(value / step)) * _to_decimal(step))


@dataclass(frozen=True)
class RebarItemInput:
    code: str
    name: str
    steel_class: str
    diameter_mm: int
    weight_parts_kg: list[float]
    kg_per_meter: float
    rod_length_m: float
    unit_price_per_m: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RebarItemInput":
        return cls(**data)

    def validate(self) -> None:
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
        if not self.weight_parts_kg:
            raise ValueError(f"rebar_items.{self.code}.weight_parts_kg is required")
        for index, value in enumerate(self.weight_parts_kg):
            _require_non_negative(
                f"rebar_items.{self.code}.weight_parts_kg[{index}]",
                value,
            )


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
    slab_formwork_perimeter_m: float
    slab_edge_height_m: float
    formwork_installation_work_unit_price: float
    plywood_sheet_working_area_m2: float
    plywood_unit_price: float
    timber_thickness_m: float
    timber_unit_price: float
    eps50_under_slab_volume_m3: float
    eps50_thickness_m: float
    eps50_laying_work_unit_price: float
    eps_waste_coeff: float
    thermal_insert_length_m: float
    thermal_insert_piece_length_m: float
    thermal_insert_piece_width_m: float
    thermal_insert_piece_height_m: float
    thermal_insert_piece_depth_for_work_m: float
    thermal_insert_piece_depth_for_eps_m: float
    thermal_insert_installation_work_unit_price: float
    eps50_pack_volume_m3: float
    eps50_unit_price: float
    eps100_thickness_m: float
    eps100_pack_volume_m3: float
    eps100_unit_price: float
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
    plywood_calc_method: str = "working_area"
    plywood_sheet_width_m: float = 1.52
    plywood_sheet_height_m: float = 1.52
    plywood_waste_coeff: float = 1.05
    slab_edge_height_strategy: str = "max_thickness"
    box_metal_delivery_capacity_kg: float = 10000

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "rebar_items",
            [
                item if isinstance(item, RebarItemInput) else RebarItemInput.from_dict(item)
                for item in self.rebar_items
            ],
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
            "slab_formwork_perimeter_m",
            "slab_edge_height_m",
            "plywood_sheet_working_area_m2",
            "timber_thickness_m",
            "eps50_thickness_m",
            "eps_waste_coeff",
            "thermal_insert_piece_length_m",
            "thermal_insert_piece_width_m",
            "thermal_insert_piece_height_m",
            "thermal_insert_piece_depth_for_work_m",
            "thermal_insert_piece_depth_for_eps_m",
            "eps50_pack_volume_m3",
            "eps100_thickness_m",
            "eps100_pack_volume_m3",
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
            "thermal_insert_length_m",
            "thermal_insert_installation_work_unit_price",
            "eps50_unit_price",
            "eps100_unit_price",
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
        ]
        for field_name in non_negative_fields:
            _require_non_negative(field_name, getattr(self, field_name))

        if not self.rebar_items:
            raise ValueError("rebar_items is required")
        for item in self.rebar_items:
            item.validate()

        if self.plywood_calc_method not in {"working_area", "actual_area_with_waste"}:
            raise ValueError(
                "plywood_calc_method must be 'working_area' or 'actual_area_with_waste'"
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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
    formwork_area_m2 = _round_decimal(
        _to_decimal(data.slab_formwork_perimeter_m) * _to_decimal(data.slab_edge_height_m)
    )

    formwork_block = {
        "formwork_area_m2": formwork_area_m2,
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
    thermal_insert_pieces = thermal_insert_block["thermal_insert_pieces"]
    eps50_laying_area_m2 = _round_decimal(
        _to_decimal(data.eps50_under_slab_volume_m3) / _to_decimal(data.eps50_thickness_m)
    )
    eps50_under_slab_required_volume_m3 = _round_decimal(
        _to_decimal(eps50_laying_area_m2)
        * _to_decimal(data.eps50_thickness_m)
        * _to_decimal(data.eps_waste_coeff)
    )
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
) -> tuple[EstimateLineResult, dict[str, Any]]:
    rebar_total_weight_kg = _round_decimal(sum(item.weight_parts_kg), "0.0001")
    rebar_raw_length_m = _round_decimal(
        _to_decimal(rebar_total_weight_kg) / _to_decimal(item.kg_per_meter),
        "0.0001",
    )
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
        "weight_parts_kg": item.weight_parts_kg,
        "total_weight_kg": rebar_total_weight_kg,
        "raw_length_m": rebar_raw_length_m,
        "length_with_waste_m": rebar_length_with_waste_m,
        "raw_rods": rebar_raw_rods,
        "rods": rebar_rods,
        "order_length_m": rebar_order_length_m,
        "control_weight_kg": rebar_control_weight_kg,
    }
    return line, control


def calculate_rebar_block(
    data: FoundationSlabInput,
) -> tuple[dict[str, Any], list[EstimateLineResult]]:
    rebar_lines = []
    items: dict[str, Any] = {}

    for item in data.rebar_items:
        line, control = calculate_rebar_line(item, data.rebar_waste_coeff)
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
    suggested_box_metal_delivery_trucks = int(
        ceil(data.box_total_metal_weight_kg / data.box_metal_delivery_capacity_kg)
    )
    warnings = []
    if data.rebar_metal_delivery_trucks != suggested_box_metal_delivery_trucks:
        warnings.append(
            "rebar_metal_delivery_trucks отличается от suggested_box_metal_delivery_trucks; "
            "строка доставки арматуры остаётся manual/fixed и не меняется автоматически."
        )

    return (
        {
            "items": items,
            "rebar_frame_assembly_quantity_m": rebar_frame_assembly_quantity_m,
            "foundation_slab_rebar_control_weight_kg": foundation_slab_rebar_control_weight_kg,
            "box_total_metal_weight_kg": data.box_total_metal_weight_kg,
            "box_metal_delivery_capacity_kg": data.box_metal_delivery_capacity_kg,
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
    }


def calculate_manual_lines_block(data: FoundationSlabInput) -> dict[str, Any]:
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
            "unit_price": data.logistics_and_supply_amount,
            "line_type": "fixed/manual",
        },
        "consumables_tool_amortization": {
            "quantity": 1,
            "unit_price": data.consumables_tool_amortization_amount,
            "line_type": "fixed/manual",
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
            display_quantity=1.2,
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
            display_quantity=14.44,
            material_unit_price=data.eps50_unit_price,
            price_code="eps_geo_50_m3",
        ),
        calculate_line(
            code="eps100_penoplex_geo_material",
            name="Пеноплэкс ГЕО 100 мм",
            unit="м3",
            quantity=eps["eps100_order_volume_m3"],
            display_quantity=0.56,
            material_unit_price=data.eps100_unit_price,
            price_code="eps_geo_100_m3",
        ),
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
        calculate_line(
            code="logistics_and_supply",
            name="Логистика и снабжение",
            unit="-",
            quantity=1,
            material_unit_price=data.logistics_and_supply_amount,
        ),
        calculate_line(
            code="consumables_tool_amortization",
            name="Расходные материалы, амортизация инструмента",
            unit="комплект",
            quantity=1,
            material_unit_price=data.consumables_tool_amortization_amount,
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

    return lines


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


def confirmed_rules() -> list[str]:
    return [
        "PLANTERBAND = количество рулонов мембраны * 4.",
        "Борта = внешний периметр фундаментной плиты.",
        "При разных толщинах плит можно брать максимальную толщину.",
        "Пиломатериал = площадь опалубки * 0.05, без дополнительного запаса.",
        "Пеноплэкс = ЭППС.",
        "ЭППС 50 мм + ЭППС 100 мм = термовкладыш 150 мм.",
        "Доставка металла ориентируется на 10 тонн на машину по листу Коробка.",
        "Фанера зависит от раскроя; текущий кейс считает через рабочую площадь 2.25 м2.",
    ]


def calculate_foundation_slab(data: FoundationSlabInput) -> dict[str, Any]:
    membrane_block = calculate_membrane_block(data)
    formwork_block = calculate_formwork_block(data)
    thermal_insert_block = calculate_thermal_insert_block(data)
    eps_block = calculate_eps_block(data, thermal_insert_block)
    rebar_block, rebar_lines = calculate_rebar_block(data)
    concrete_block = calculate_concrete_block(data, rebar_block)
    manual_lines_block = calculate_manual_lines_block(data)

    calculation_blocks = {
        "confirmed_rules": confirmed_rules(),
        "membrane": membrane_block,
        "formwork": formwork_block,
        "eps": eps_block,
        "thermal_insert": thermal_insert_block,
        "rebar": rebar_block,
        "concrete": concrete_block,
        "manual_lines": manual_lines_block,
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
