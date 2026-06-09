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
    excavator_shifts_calc_method: str = "legacy_manual_shifts"
    pit_excavation_depth_m: float | None = None
    excavator_productivity_m3_per_shift: float = 80.0
    manual_excavation_calc_method: str = "legacy_manual_override"
    manual_refinement_depth_m: float = 0.08
    trench_volume_m3: float | None = None
    trench_length_m: float | None = None
    trench_depth_m: float | None = None
    trench_width_m: float | None = 0.4
    trench_routes: list[dict[str, Any]] | None = None
    sand_base_volume_m3: float = 0.0
    sand_compaction_coeff: float = 1.3
    sand_truck_step_m3: float = 20.0
    geotextile_area_m2: float = 0.0
    geotextile_overlap_coeff: float = 1.10
    geotextile_roll_area_m2: float = 100.0
    communications_length_calc_method: str = "legacy_direct_length"
    communications_length_m: float = 0.0
    communications_pipe_items: list[dict[str, Any]] | None = None
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
        if self.excavator_shifts_calc_method not in {
            "legacy_manual_shifts",
            "standard_volume_productivity",
        }:
            raise ValueError(
                "excavator_shifts_calc_method must be legacy_manual_shifts or standard_volume_productivity"
            )
        if self.manual_excavation_calc_method not in {
            "legacy_manual_override",
            "standard_routes",
        }:
            raise ValueError(
                "manual_excavation_calc_method must be legacy_manual_override or standard_routes"
            )
        if self.communications_length_calc_method not in {
            "legacy_direct_length",
            "pipe_items",
        }:
            raise ValueError(
                "communications_length_calc_method must be legacy_direct_length or pipe_items"
            )

        _require_non_negative("pit_area_m2", self.pit_area_m2)
        _require_positive(
            "excavator_productivity_m3_per_shift",
            self.excavator_productivity_m3_per_shift,
        )
        _require_positive("manual_refinement_depth_m", self.manual_refinement_depth_m)
        _require_non_negative("sand_base_volume_m3", self.sand_base_volume_m3)
        _require_positive("sand_compaction_coeff", self.sand_compaction_coeff)
        _require_positive("sand_truck_step_m3", self.sand_truck_step_m3)
        _require_non_negative("geotextile_area_m2", self.geotextile_area_m2)
        _require_positive("geotextile_overlap_coeff", self.geotextile_overlap_coeff)
        _require_positive("geotextile_roll_area_m2", self.geotextile_roll_area_m2)
        _require_non_negative("communications_length_m", self.communications_length_m)
        if self.communications_length_calc_method == "pipe_items":
            if not self.communications_pipe_items:
                raise ValueError("communications_pipe_items is required for pipe_items")
            for index, item in enumerate(self.communications_pipe_items):
                prefix = f"communications_pipe_items[{index}]"
                if not item.get("code"):
                    raise ValueError(f"{prefix}.code is required")
                if item.get("total_length_m") is not None:
                    _require_non_negative(f"{prefix}.total_length_m", item["total_length_m"])
                else:
                    _require_non_negative(f"{prefix}.pipe_length_m", item.get("pipe_length_m"))
                    _require_non_negative(f"{prefix}.quantity", item.get("quantity"))
        _require_non_negative("axis_marking_shifts", self.axis_marking_shifts)
        _require_non_negative("excavator_shifts", self.excavator_shifts)
        if self.excavator_shifts_calc_method == "standard_volume_productivity":
            _require_non_negative("pit_excavation_depth_m", self.pit_excavation_depth_m)
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

        if self.manual_excavation_calc_method == "standard_routes":
            _require_positive("trench_width_m", self.trench_width_m)
            if self.trench_volume_m3 is not None:
                _require_non_negative("trench_volume_m3", self.trench_volume_m3)
                return
            if not self.trench_routes:
                raise ValueError(
                    "trench_volume_m3 or trench_routes is required for standard_routes"
                )
            for index, route in enumerate(self.trench_routes):
                prefix = f"trench_routes[{index}]"
                if not route.get("route_code"):
                    raise ValueError(f"{prefix}.route_code is required")
                _require_non_negative(f"{prefix}.length_m", route.get("length_m"))
                _require_non_negative(f"{prefix}.depth_m", route.get("depth_m"))
            return

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
    price_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        if self.price_code is None:
            result.pop("price_code")
        return result


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


def calculate_excavator_shifts(
    excavator_shifts_calc_method: str,
    excavator_shifts: float,
    pit_area_m2: float,
    pit_excavation_depth_m: float | None,
    excavator_productivity_m3_per_shift: float,
) -> tuple[str, float | None, float]:
    if excavator_shifts_calc_method == "legacy_manual_shifts":
        return "legacy_manual_shifts", None, _round_decimal(_to_decimal(excavator_shifts))

    pit_area = _to_decimal(pit_area_m2)
    pit_depth = _to_decimal(pit_excavation_depth_m)
    productivity = _to_decimal(excavator_productivity_m3_per_shift)
    if pit_depth is None:
        raise ValueError("pit_excavation_depth_m is required for standard_volume_productivity")

    machine_excavation_volume_m3 = _round_decimal(pit_area * pit_depth)
    if machine_excavation_volume_m3 == 0:
        return "standard_volume_productivity", machine_excavation_volume_m3, 0.0

    calculated_shifts = ceil(machine_excavation_volume_m3 / float(productivity))
    return "standard_volume_productivity", machine_excavation_volume_m3, float(calculated_shifts)


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


def calculate_trench_routes(
    trench_routes: list[dict[str, Any]],
    trench_width_m: float,
) -> tuple[list[dict[str, Any]], float]:
    route_results = []
    total = Decimal("0")
    width = _to_decimal(trench_width_m)

    for route in trench_routes:
        length = _to_decimal(route["length_m"])
        depth = _to_decimal(route["depth_m"])
        volume = length * depth * width
        total += volume
        route_results.append(
            {
                "route_code": route["route_code"],
                "name": route.get("name", route["route_code"]),
                "length_m": _round_decimal(length),
                "depth_m": _round_decimal(depth),
                "width_m": _round_decimal(width),
                "volume_m3": _round_decimal(volume),
            }
        )

    return route_results, _round_decimal(total)


def calculate_manual_excavation_total(
    manual_pit_volume_m3: float,
    trench_volume_m3: float,
) -> float:
    result = _to_decimal(manual_pit_volume_m3) + _to_decimal(trench_volume_m3)
    return _round_decimal(result)


def calculate_communications_length(
    communications_length_calc_method: str,
    communications_length_m: float,
    communications_pipe_items: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], float]:
    if communications_length_calc_method == "legacy_direct_length":
        return [], _round_decimal(_to_decimal(communications_length_m))

    if not communications_pipe_items:
        raise ValueError("communications_pipe_items is required for pipe_items")

    item_results = []
    total = Decimal("0")
    for item in communications_pipe_items:
        include = item.get("include_in_communications", True)
        if item.get("total_length_m") is not None:
            item_total = _to_decimal(item["total_length_m"])
            pipe_length = item.get("pipe_length_m")
            quantity = item.get("quantity")
        else:
            pipe_length_decimal = _to_decimal(item["pipe_length_m"])
            quantity_decimal = _to_decimal(item["quantity"])
            item_total = pipe_length_decimal * quantity_decimal
            pipe_length = _round_decimal(pipe_length_decimal)
            quantity = _round_decimal(quantity_decimal)

        if include:
            total += item_total

        item_results.append(
            {
                "code": item["code"],
                "name": item.get("name", item["code"]),
                "pipe_length_m": pipe_length,
                "quantity": quantity,
                "total_length_m": _round_decimal(item_total),
                "include_in_communications": include,
            }
        )

    return item_results, _round_decimal(total)


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
    price_code: str | None = None,
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
        price_code=price_code,
    )


def calculate_internal_estimate_lines(
    data: EarthworksInput,
    volume_result: dict[str, Any],
) -> list[EstimateLineResult]:
    manual_excavation_quantity = (
        data.manual_excavation_quantity_for_estimate_m3
        if data.manual_excavation_calc_method == "legacy_manual_override"
        and data.manual_excavation_quantity_for_estimate_m3 is not None
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
    communications_length_m = volume_result["communications_length_m"]
    excavator_shifts = volume_result["excavator_shifts"]

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
            price_code="axis_marking_shift",
        ),
        calculate_line(
            code="excavator_jcb",
            name=_line_name(
                data,
                "excavator_jcb",
                "Механизированная разработка грунта, Экскаватор JCB",
            ),
            unit="смена",
            quantity=excavator_shifts,
            material_unit_price=_price(data, "excavator_material_unit_price"),
            work_unit_price=_price(data, "excavator_work_unit_price"),
            price_code="excavator_jcb_shift",
        ),
        calculate_line(
            code="manual_excavation",
            name=_line_name(data, "manual_excavation", "Разработка грунта вручную"),
            unit="м3",
            quantity=manual_excavation_quantity,
            work_unit_price=_price(data, "manual_excavation_work_unit_price"),
            price_code="manual_excavation_m3",
        ),
        calculate_line(
            code="geotextile_laying",
            name=_line_name(data, "geotextile_laying", "Укладка геотекстиля"),
            unit="м2",
            quantity=data.geotextile_laying_area_m2,
            work_unit_price=_price(data, "geotextile_laying_work_unit_price"),
            price_code="geotextile_laying_m2",
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
            price_code="geotextile_dornit_300_m2",
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
            price_code="sand_filling_work_m3",
        ),
        calculate_line(
            code="sand_material",
            name=_line_name(data, "sand_material", "Песок строительный"),
            unit="м3",
            quantity=sand_order_volume_m3,
            material_unit_price=_price(data, "sand_material_unit_price"),
            price_code="sand_m3",
        ),
        calculate_line(
            code="sand_manual_moving",
            name=_line_name(data, "sand_manual_moving", "Перемещение песка вручную"),
            unit="м3",
            quantity=sand_order_volume_m3,
            work_unit_price=_price(data, "sand_manual_moving_work_unit_price"),
            price_code="sand_manual_moving_m3",
        ),
        calculate_line(
            code="communications_work",
            name=_line_name(
                data,
                "communications_work",
                "Закладка технологических входов коммуникаций до границы дома",
            ),
            unit="мп",
            quantity=communications_length_m,
            work_unit_price=_price(data, "communications_work_unit_price"),
            price_code="communications_installation_m",
        ),
        calculate_line(
            code="communications_material",
            name=_line_name(
                data,
                "communications_material",
                "Материалы для устройства входов коммуникаций",
            ),
            unit="мп",
            quantity=communications_length_m,
            material_unit_price=_price(data, "communications_material_unit_price"),
            price_code="communications_material_m",
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
    (
        excavator_shifts_source,
        machine_excavation_volume_m3,
        excavator_shifts,
    ) = calculate_excavator_shifts(
        data.excavator_shifts_calc_method,
        data.excavator_shifts,
        data.pit_area_m2,
        data.pit_excavation_depth_m,
        data.excavator_productivity_m3_per_shift,
    )

    trench_routes_result: list[dict[str, Any]] = []
    trench_volume_source = "legacy"
    if data.manual_excavation_calc_method == "standard_routes":
        if data.trench_volume_m3 is not None:
            trench_volume_m3 = calculate_trench_volume(trench_volume_m3=data.trench_volume_m3)
            trench_volume_source = "spec_volume"
        else:
            trench_routes_result, trench_volume_m3 = calculate_trench_routes(
                data.trench_routes or [],
                data.trench_width_m,
            )
            trench_volume_source = "routes_calculated"
    else:
        trench_volume_m3 = calculate_trench_volume(
            trench_volume_m3=data.trench_volume_m3,
            trench_length_m=data.trench_length_m,
            trench_depth_m=data.trench_depth_m,
            trench_width_m=data.trench_width_m,
        )
        trench_volume_source = (
            "legacy_direct_volume"
            if data.trench_volume_m3 is not None
            else "legacy_dimensions"
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
    communications_pipe_items_result, communications_length_m = calculate_communications_length(
        data.communications_length_calc_method,
        data.communications_length_m,
        data.communications_pipe_items,
    )

    volume_result = {
        "excavator_shifts_calc_method": data.excavator_shifts_calc_method,
        "excavator_shifts_source": excavator_shifts_source,
        "pit_excavation_depth_m": data.pit_excavation_depth_m,
        "machine_excavation_volume_m3": machine_excavation_volume_m3,
        "excavator_productivity_m3_per_shift": data.excavator_productivity_m3_per_shift,
        "excavator_shifts": excavator_shifts,
        "manual_excavation_calc_method": data.manual_excavation_calc_method,
        "manual_pit_volume_m3": manual_pit_volume_m3,
        "manual_refinement_depth_m": data.manual_refinement_depth_m,
        "trench_width_m": data.trench_width_m,
        "trench_volume_source": trench_volume_source,
        "trench_routes": trench_routes_result,
        "trench_volume_total_m3": trench_volume_m3,
        "trench_volume_m3": trench_volume_m3,
        "manual_excavation_total_m3": manual_excavation_total_m3,
        "compacted_sand_base_m3": compacted_sand_base_m3,
        "compacted_sand_trenches_m3": compacted_sand_trenches_m3,
        "sand_total_m3": sand_total_m3,
        "sand_order_volume_m3": sand_order_volume_m3,
        "geotextile_with_overlap_m2": geotextile_with_overlap_m2,
        "geotextile_rolls": geotextile_rolls,
        "communications_length_calc_method": data.communications_length_calc_method,
        "communications_pipe_items": communications_pipe_items_result,
        "communications_length_m": communications_length_m,
    }
    estimate_lines = calculate_internal_estimate_lines(data, volume_result)
    internal_totals = calculate_internal_totals(estimate_lines)

    return {
        "inputs": data.to_dict(),
        "volume_result": volume_result,
        "estimate_lines": [line.to_dict() for line in estimate_lines],
        "internal_totals": internal_totals,
    }
