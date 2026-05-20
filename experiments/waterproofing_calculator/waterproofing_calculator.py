from __future__ import annotations

from dataclasses import asdict, dataclass
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


@dataclass(frozen=True)
class WaterproofingInput:
    project_name: str
    slab_formwork_perimeter_m: float
    slab_edge_height_m: float
    waterproofing_work_unit_price: float
    primer_consumption_l_per_m2: float
    primer_canister_volume_l: float
    primer_unit_price: float
    mastic_consumption_kg_per_m2_per_layer: float
    mastic_layers: float
    mastic_bucket_weight_kg: float
    mastic_unit_price: float
    eps100_wall_volume_m3: float
    eps100_wall_thickness_m: float
    eps100_wall_insulation_work_unit_price: float
    non_insulated_edge_lengths_m: list[float]
    eps_waste_coeff: float
    eps100_pack_volume_m3: float
    eps100_unit_price: float
    glue_foam_coverage_m2_per_can: float
    glue_foam_min_units: int
    glue_foam_unit_price: float
    waterproofing_logistics_coeff: float
    waterproofing_consumables_coeff: float

    def __post_init__(self) -> None:
        self.validate()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WaterproofingInput":
        return cls(**data)

    def validate(self) -> None:
        if not self.project_name:
            raise ValueError("project_name is required")

        positive_fields = [
            "slab_formwork_perimeter_m",
            "slab_edge_height_m",
            "primer_consumption_l_per_m2",
            "primer_canister_volume_l",
            "mastic_consumption_kg_per_m2_per_layer",
            "mastic_layers",
            "mastic_bucket_weight_kg",
            "eps100_wall_thickness_m",
            "eps_waste_coeff",
            "eps100_pack_volume_m3",
            "glue_foam_coverage_m2_per_can",
        ]
        for field_name in positive_fields:
            _require_positive(field_name, getattr(self, field_name))

        non_negative_fields = [
            "waterproofing_work_unit_price",
            "primer_unit_price",
            "mastic_unit_price",
            "eps100_wall_volume_m3",
            "eps100_wall_insulation_work_unit_price",
            "eps100_unit_price",
            "glue_foam_min_units",
            "glue_foam_unit_price",
            "waterproofing_logistics_coeff",
            "waterproofing_consumables_coeff",
        ]
        for field_name in non_negative_fields:
            _require_non_negative(field_name, getattr(self, field_name))

        for index, length in enumerate(self.non_insulated_edge_lengths_m):
            _require_non_negative(f"non_insulated_edge_lengths_m[{index}]", length)

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

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        if self.display_quantity is None:
            result.pop("display_quantity")
        return result


def calculate_line(
    code: str,
    name: str,
    unit: str,
    quantity: float,
    material_unit_price: float = 0.0,
    work_unit_price: float = 0.0,
    display_quantity: float | None = None,
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
    )


def calculate_waterproofing_block(data: WaterproofingInput) -> dict[str, Any]:
    waterproofing_area_m2 = _round_decimal(
        _to_decimal(data.slab_formwork_perimeter_m) * _to_decimal(data.slab_edge_height_m)
    )
    primer_required_liters = _round_decimal(
        _to_decimal(waterproofing_area_m2)
        * _to_decimal(data.primer_consumption_l_per_m2)
    )
    primer_raw_units = _round_decimal(
        _to_decimal(primer_required_liters) / _to_decimal(data.primer_canister_volume_l),
        "0.0001",
    )
    primer_units = int(ceil(primer_raw_units))

    mastic_required_kg = _round_decimal(
        _to_decimal(waterproofing_area_m2)
        * _to_decimal(data.mastic_consumption_kg_per_m2_per_layer)
        * _to_decimal(data.mastic_layers)
    )
    mastic_raw_units = _round_decimal(
        _to_decimal(mastic_required_kg) / _to_decimal(data.mastic_bucket_weight_kg),
        "0.0001",
    )
    mastic_units = int(ceil(mastic_raw_units))

    eps100_wall_insulation_area_m2 = _round_decimal(
        _to_decimal(data.eps100_wall_volume_m3) / _to_decimal(data.eps100_wall_thickness_m)
    )
    insulated_edge_length_m = _round_decimal(
        _to_decimal(data.slab_formwork_perimeter_m)
        - _to_decimal(sum(data.non_insulated_edge_lengths_m))
    )
    eps100_wall_geometry_check_area_m2 = _round_decimal(
        _to_decimal(insulated_edge_length_m) * _to_decimal(data.slab_edge_height_m)
    )

    eps100_wall_required_volume_m3 = _round_decimal(
        _to_decimal(eps100_wall_insulation_area_m2)
        * _to_decimal(data.eps100_wall_thickness_m)
        * _to_decimal(data.eps_waste_coeff),
        "0.0001",
    )
    eps100_wall_raw_packs = _round_decimal(
        _to_decimal(eps100_wall_required_volume_m3)
        / _to_decimal(data.eps100_pack_volume_m3),
        "0.0001",
    )
    eps100_wall_packs = int(ceil(eps100_wall_raw_packs))
    eps100_wall_order_volume_m3 = _round_decimal(
        _to_decimal(eps100_wall_packs) * _to_decimal(data.eps100_pack_volume_m3),
        "0.0001",
    )

    glue_foam_raw_units = _round_decimal(
        _to_decimal(eps100_wall_insulation_area_m2)
        / _to_decimal(data.glue_foam_coverage_m2_per_can),
        "0.0001",
    )
    glue_foam_units = max(data.glue_foam_min_units, int(ceil(glue_foam_raw_units)))

    return {
        "waterproofing_area_m2": waterproofing_area_m2,
        "primer_required_liters": primer_required_liters,
        "primer_raw_units": primer_raw_units,
        "primer_units": primer_units,
        "mastic_required_kg": mastic_required_kg,
        "mastic_raw_units": mastic_raw_units,
        "mastic_units": mastic_units,
        "eps100_wall_insulation_area_m2": eps100_wall_insulation_area_m2,
        "non_insulated_edge_lengths_total_m": _round_decimal(
            sum(data.non_insulated_edge_lengths_m)
        ),
        "insulated_edge_length_m": insulated_edge_length_m,
        "eps100_wall_geometry_check_area_m2": eps100_wall_geometry_check_area_m2,
        "eps100_wall_required_volume_m3": eps100_wall_required_volume_m3,
        "eps100_wall_raw_packs": eps100_wall_raw_packs,
        "eps100_wall_packs": eps100_wall_packs,
        "eps100_wall_order_volume_m3": eps100_wall_order_volume_m3,
        "glue_foam_raw_units": glue_foam_raw_units,
        "glue_foam_units": glue_foam_units,
    }


def calculate_primary_estimate_lines(
    data: WaterproofingInput,
    waterproofing: dict[str, Any],
) -> list[EstimateLineResult]:
    return [
        calculate_line(
            code="waterproofing_bitumen_mastic_work",
            name="Гидроизоляция фундаментной плиты битумной мастикой в 2 слоя",
            unit="м2",
            quantity=waterproofing["waterproofing_area_m2"],
            work_unit_price=data.waterproofing_work_unit_price,
        ),
        calculate_line(
            code="bitumen_primer_aquamast_18l",
            name="Праймер битумный AquaMast, 18 л",
            unit="шт",
            quantity=waterproofing["primer_units"],
            material_unit_price=data.primer_unit_price,
        ),
        calculate_line(
            code="bitumen_mastic_aquamast_18kg",
            name="Мастика гидроизоляционная битумная для фундаментов AquaMast, 18 кг",
            unit="шт",
            quantity=waterproofing["mastic_units"],
            material_unit_price=data.mastic_unit_price,
        ),
        calculate_line(
            code="eps100_wall_insulation_work",
            name="Утепление стен плиты ЭППС 100 мм",
            unit="м2",
            quantity=waterproofing["eps100_wall_insulation_area_m2"],
            work_unit_price=data.eps100_wall_insulation_work_unit_price,
        ),
        calculate_line(
            code="eps100_wall_penoplex_geo_material",
            name="Пеноплэкс ГЕО 100 мм",
            unit="м3",
            quantity=waterproofing["eps100_wall_order_volume_m3"],
            display_quantity=1.94,
            material_unit_price=data.eps100_unit_price,
        ),
        calculate_line(
            code="eps_glue_foam",
            name="Клей-пена для ЭППС",
            unit="баллон",
            quantity=waterproofing["glue_foam_units"],
            material_unit_price=data.glue_foam_unit_price,
        ),
    ]


def calculate_internal_estimate_lines(
    data: WaterproofingInput,
    waterproofing: dict[str, Any],
) -> list[EstimateLineResult]:
    primary_lines = calculate_primary_estimate_lines(data, waterproofing)
    waterproofing_base_subtotal = sum(line.line_total for line in primary_lines)
    logistics_amount_raw = _round_decimal(
        _to_decimal(waterproofing_base_subtotal)
        * _to_decimal(data.waterproofing_logistics_coeff),
        "0.01",
    )
    consumables_amount_raw = _round_decimal(
        _to_decimal(waterproofing_base_subtotal)
        * _to_decimal(data.waterproofing_consumables_coeff),
        "0.01",
    )

    waterproofing["waterproofing_base_subtotal"] = waterproofing_base_subtotal
    waterproofing["logistics_amount_raw"] = logistics_amount_raw
    waterproofing["consumables_amount_raw"] = consumables_amount_raw

    return [
        *primary_lines,
        calculate_line(
            code="waterproofing_logistics_and_supply",
            name="Логистика и снабжение",
            unit="-",
            quantity=1,
            material_unit_price=logistics_amount_raw,
        ),
        calculate_line(
            code="waterproofing_consumables_tool_amortization",
            name="Расходные материалы, амортизация инструмента",
            unit="комплект",
            quantity=1,
            material_unit_price=consumables_amount_raw,
        ),
    ]


def calculate_internal_totals(
    lines: list[EstimateLineResult],
    waterproofing_base_subtotal: int,
) -> dict[str, int]:
    internal_materials_total = sum(line.material_total for line in lines)
    internal_works_total = sum(line.work_total for line in lines)

    return {
        "waterproofing_base_subtotal": waterproofing_base_subtotal,
        "internal_materials_total": internal_materials_total,
        "internal_works_total": internal_works_total,
        "internal_section_total": internal_materials_total + internal_works_total,
    }


def calculate_waterproofing(data: WaterproofingInput) -> dict[str, Any]:
    waterproofing_block = calculate_waterproofing_block(data)
    estimate_lines = calculate_internal_estimate_lines(data, waterproofing_block)
    internal_totals = calculate_internal_totals(
        estimate_lines,
        waterproofing_block["waterproofing_base_subtotal"],
    )

    return {
        "inputs": data.to_dict(),
        "calculation_blocks": {"waterproofing": waterproofing_block},
        "estimate_lines": [line.to_dict() for line in estimate_lines],
        "internal_totals": internal_totals,
        "warnings": [],
    }
