from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from typing import Any


def _to_decimal(value: float | int | None) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _round_decimal(value: Decimal, places: str = "0.001") -> float:
    rounded = value.quantize(Decimal(places), rounding=ROUND_HALF_UP)
    return float(rounded)


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


@dataclass(frozen=True)
class EarthworksInput:
    project_name: str
    pit_area_m2: float
    case_meta: dict[str, Any] = field(default_factory=dict)
    assumptions: dict[str, bool] = field(default_factory=dict)
    manual_refinement_depth_m: float = 0.08
    trench_volume_m3: float | None = None
    trench_length_m: float | None = None
    trench_depth_m: float | None = None
    trench_width_m: float | None = None
    sand_base_volume_m3: float = 0.0
    sand_compaction_coeff: float = 1.3
    sand_truck_step_m3: float = 20.0
    geotextile_area_m2: float = 0.0
    geotextile_overlap_coeff: float = 1.10
    geotextile_roll_area_m2: float = 100.0
    communications_length_m: float = 0.0
    axis_marking_shifts: float = 0.0
    excavator_shifts: float = 0.0
    geotextile_laying_area_m2: float = 0.0
    manual_excavation_quantity_for_estimate_m3: float | None = None
    consumables_amount: float = 0.0
    enabled_lines: list[str] | None = None
    quantity_overrides: dict[str, float] = field(default_factory=dict)
    line_name_overrides: dict[str, str] = field(default_factory=dict)
    internal_prices: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.validate()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EarthworksInput":
        return cls(**data)

    def validate(self) -> None:
        if not self.project_name:
            raise ValueError("project_name is required")

        _require_non_negative("pit_area_m2", self.pit_area_m2)
        _require_positive("manual_refinement_depth_m", self.manual_refinement_depth_m)
        _require_non_negative("sand_base_volume_m3", self.sand_base_volume_m3)
        _require_positive("sand_compaction_coeff", self.sand_compaction_coeff)
        _require_positive("sand_truck_step_m3", self.sand_truck_step_m3)
        _require_non_negative("geotextile_area_m2", self.geotextile_area_m2)
        _require_positive("geotextile_overlap_coeff", self.geotextile_overlap_coeff)
        _require_positive("geotextile_roll_area_m2", self.geotextile_roll_area_m2)
        _require_non_negative("communications_length_m", self.communications_length_m)
        _require_non_negative("axis_marking_shifts", self.axis_marking_shifts)
        _require_non_negative("excavator_shifts", self.excavator_shifts)
        _require_non_negative(
            "geotextile_laying_area_m2",
            self.geotextile_laying_area_m2,
        )
        _require_non_negative("consumables_amount", self.consumables_amount)

        if self.manual_excavation_quantity_for_estimate_m3 is not None:
            _require_non_negative(
                "manual_excavation_quantity_for_estimate_m3",
                self.manual_excavation_quantity_for_estimate_m3,
            )

        for key, value in self.internal_prices.items():
            _require_non_negative(f"internal_prices.{key}", value)

        for key, value in self.quantity_overrides.items():
            _require_non_negative(f"quantity_overrides.{key}", value)

        if self.trench_volume_m3 is not None:
            _require_non_negative("trench_volume_m3", self.trench_volume_m3)
            return

        _require_non_negative("trench_length_m", self.trench_length_m)
        _require_non_negative("trench_depth_m", self.trench_depth_m)
        _require_non_negative("trench_width_m", self.trench_width_m)

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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _round_money(value: Decimal | float | int) -> int:
    decimal_value = value if isinstance(value, Decimal) else _to_decimal(value)
    return int(decimal_value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _price(data: EarthworksInput, key: str) -> float:
    return data.internal_prices.get(key, 0.0)


def _quantity(data: EarthworksInput, key: str, default: float) -> float:
    return data.quantity_overrides.get(key, default)


def _line_name(data: EarthworksInput, code: str, default: str) -> str:
    return data.line_name_overrides.get(code, default)


def calculate_manual_pit_volume(
    pit_area_m2: float,
    manual_refinement_depth_m: float = 0.08,
) -> float:
    result = _to_decimal(pit_area_m2) * _to_decimal(manual_refinement_depth_m)
    return _round_decimal(result)


def calculate_trench_volume(
    trench_volume_m3: float | None = None,
    trench_length_m: float | None = None,
    trench_depth_m: float | None = None,
    trench_width_m: float | None = None,
) -> float:
    if trench_volume_m3 is not None:
        return _round_decimal(_to_decimal(trench_volume_m3))

    length = _to_decimal(trench_length_m)
    depth = _to_decimal(trench_depth_m)
    width = _to_decimal(trench_width_m)

    if length is None or depth is None or width is None:
        raise ValueError(
            "Provide trench_volume_m3 or trench_length_m, trench_depth_m, trench_width_m"
        )

    return _round_decimal(length * depth * width)


def calculate_manual_excavation_total(
    manual_pit_volume_m3: float,
    trench_volume_m3: float,
) -> float:
    result = _to_decimal(manual_pit_volume_m3) + _to_decimal(trench_volume_m3)
    return _round_decimal(result)


def calculate_compacted_sand(volume_m3: float, compaction_coeff: float = 1.3) -> float:
    result = _to_decimal(volume_m3) * _to_decimal(compaction_coeff)
    return _round_decimal(result)


def round_up_to_step(value: float, step: float) -> int:
    _require_non_negative("value", value)
    _require_positive("step", step)
    return int(ceil(value / step) * step)


def calculate_geotextile_with_overlap(
    geotextile_area_m2: float,
    overlap_coeff: float = 1.10,
) -> float:
    result = _to_decimal(geotextile_area_m2) * _to_decimal(overlap_coeff)
    return _round_decimal(result)


def calculate_rolls(area_m2: float, roll_area_m2: float) -> int:
    _require_non_negative("area_m2", area_m2)
    _require_positive("roll_area_m2", roll_area_m2)
    return int(ceil(area_m2 / roll_area_m2))


def calculate_line(
    code: str,
    name: str,
    unit: str,
    quantity: float,
    material_unit_price: float = 0.0,
    work_unit_price: float = 0.0,
) -> EstimateLineResult:
    quantity_rounded = _round_decimal(_to_decimal(quantity))
    material_total = _round_money(
        _to_decimal(quantity_rounded) * _to_decimal(material_unit_price)
    )
    work_total = _round_money(_to_decimal(quantity_rounded) * _to_decimal(work_unit_price))

    return EstimateLineResult(
        code=code,
        name=name,
        unit=unit,
        quantity=quantity_rounded,
        material_unit_price=material_unit_price,
        material_total=material_total,
        work_unit_price=work_unit_price,
        work_total=work_total,
        line_total=material_total + work_total,
    )


def calculate_internal_estimate_lines(
    data: EarthworksInput,
    volume_result: dict[str, Any],
) -> list[EstimateLineResult]:
    manual_excavation_quantity = (
        data.manual_excavation_quantity_for_estimate_m3
        if data.manual_excavation_quantity_for_estimate_m3 is not None
        else volume_result["manual_excavation_total_m3"]
    )
    sand_order_volume_m3 = _quantity(
        data,
        "sand_order_volume_m3",
        volume_result["sand_order_volume_m3"],
    )
    geotextile_material_quantity_m2 = _quantity(
        data,
        "geotextile_material_quantity_m2",
        volume_result["geotextile_rolls"] * data.geotextile_roll_area_m2,
    )

    lines = [
        calculate_line(
            code="axis_marking",
            name=_line_name(
                data,
                "axis_marking",
                "Вынос осей фундамента, котлована на участок",
            ),
            unit="смена",
            quantity=data.axis_marking_shifts,
            work_unit_price=_price(data, "axis_marking_work_unit_price"),
        ),
        calculate_line(
            code="excavator_jcb",
            name=_line_name(
                data,
                "excavator_jcb",
                "Механизированная разработка грунта, Экскаватор JCB",
            ),
            unit="смена",
            quantity=data.excavator_shifts,
            material_unit_price=_price(data, "excavator_material_unit_price"),
            work_unit_price=_price(data, "excavator_work_unit_price"),
        ),
        calculate_line(
            code="manual_excavation",
            name=_line_name(data, "manual_excavation", "Разработка грунта вручную"),
            unit="м3",
            quantity=manual_excavation_quantity,
            work_unit_price=_price(data, "manual_excavation_work_unit_price"),
        ),
        calculate_line(
            code="geotextile_laying",
            name=_line_name(data, "geotextile_laying", "Укладка геотекстиля"),
            unit="м2",
            quantity=data.geotextile_laying_area_m2,
            work_unit_price=_price(data, "geotextile_laying_work_unit_price"),
        ),
        calculate_line(
            code="geotextile_material",
            name=_line_name(
                data,
                "geotextile_material",
                "Геотекстиль Дорнит 300 г.м2 (100м2)",
            ),
            unit="м2",
            quantity=geotextile_material_quantity_m2,
            material_unit_price=_price(data, "geotextile_material_unit_price"),
            work_unit_price=_price(data, "geotextile_material_work_unit_price"),
        ),
        calculate_line(
            code="sand_filling",
            name=_line_name(
                data,
                "sand_filling",
                "Отсыпка дна котлована, засыпка под плитой песком с трамбованием",
            ),
            unit="м3",
            quantity=sand_order_volume_m3,
            work_unit_price=_price(data, "sand_filling_work_unit_price"),
        ),
        calculate_line(
            code="sand_material",
            name=_line_name(data, "sand_material", "Песок строительный"),
            unit="м3",
            quantity=sand_order_volume_m3,
            material_unit_price=_price(data, "sand_material_unit_price"),
        ),
        calculate_line(
            code="sand_manual_moving",
            name=_line_name(data, "sand_manual_moving", "Перемещение песка вручную"),
            unit="м3",
            quantity=sand_order_volume_m3,
            work_unit_price=_price(data, "sand_manual_moving_work_unit_price"),
        ),
        calculate_line(
            code="communications_work",
            name=_line_name(
                data,
                "communications_work",
                "Закладка технологических входов коммуникаций до границы дома",
            ),
            unit="мп",
            quantity=data.communications_length_m,
            work_unit_price=_price(data, "communications_work_unit_price"),
        ),
        calculate_line(
            code="communications_material",
            name=_line_name(
                data,
                "communications_material",
                "Материалы для устройства входов коммуникаций",
            ),
            unit="мп",
            quantity=data.communications_length_m,
            material_unit_price=_price(data, "communications_material_unit_price"),
        ),
        calculate_line(
            code="consumables",
            name=_line_name(
                data,
                "consumables",
                "Расходные материалы, амортизация инструмента",
            ),
            unit="комплект",
            quantity=1,
            material_unit_price=data.consumables_amount,
        ),
    ]

    if data.enabled_lines is None:
        return lines

    enabled_codes = set(data.enabled_lines)
    return [line for line in lines if line.code in enabled_codes]


def calculate_internal_totals(lines: list[EstimateLineResult]) -> dict[str, int]:
    internal_materials_total = sum(line.material_total for line in lines)
    internal_works_total = sum(line.work_total for line in lines)

    return {
        "internal_materials_total": internal_materials_total,
        "internal_works_total": internal_works_total,
        "internal_section_total": internal_materials_total + internal_works_total,
    }


def calculate_earthworks(data: EarthworksInput) -> dict[str, Any]:
    trench_volume_m3 = calculate_trench_volume(
        trench_volume_m3=data.trench_volume_m3,
        trench_length_m=data.trench_length_m,
        trench_depth_m=data.trench_depth_m,
        trench_width_m=data.trench_width_m,
    )
    manual_pit_volume_m3 = calculate_manual_pit_volume(
        data.pit_area_m2,
        data.manual_refinement_depth_m,
    )
    manual_excavation_total_m3 = calculate_manual_excavation_total(
        manual_pit_volume_m3,
        trench_volume_m3,
    )

    compacted_sand_base_m3 = calculate_compacted_sand(
        data.sand_base_volume_m3,
        data.sand_compaction_coeff,
    )
    compacted_sand_trenches_m3 = calculate_compacted_sand(
        trench_volume_m3,
        data.sand_compaction_coeff,
    )
    sand_total_m3 = _round_decimal(
        _to_decimal(compacted_sand_base_m3) + _to_decimal(compacted_sand_trenches_m3)
    )
    sand_order_volume_m3 = round_up_to_step(sand_total_m3, data.sand_truck_step_m3)

    geotextile_with_overlap_m2 = calculate_geotextile_with_overlap(
        data.geotextile_area_m2,
        data.geotextile_overlap_coeff,
    )
    geotextile_rolls = calculate_rolls(
        geotextile_with_overlap_m2,
        data.geotextile_roll_area_m2,
    )

    volume_result = {
        "manual_pit_volume_m3": manual_pit_volume_m3,
        "trench_volume_m3": trench_volume_m3,
        "manual_excavation_total_m3": manual_excavation_total_m3,
        "compacted_sand_base_m3": compacted_sand_base_m3,
        "compacted_sand_trenches_m3": compacted_sand_trenches_m3,
        "sand_total_m3": sand_total_m3,
        "sand_order_volume_m3": sand_order_volume_m3,
        "geotextile_with_overlap_m2": geotextile_with_overlap_m2,
        "geotextile_rolls": geotextile_rolls,
    }
    estimate_lines = calculate_internal_estimate_lines(data, volume_result)
    internal_totals = calculate_internal_totals(estimate_lines)

    return {
        "inputs": data.to_dict(),
        "volume_result": volume_result,
        "estimate_lines": [line.to_dict() for line in estimate_lines],
        "internal_totals": internal_totals,
    }
