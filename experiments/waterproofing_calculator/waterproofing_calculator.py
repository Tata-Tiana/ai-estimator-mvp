from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PRICING_DIR = REPO_ROOT / "experiments" / "pricing"
if str(PRICING_DIR) not in sys.path:
    sys.path.insert(0, str(PRICING_DIR))

from price_reader import (  # noqa: E402
    load_price_registry,
    load_project_price_overrides,
    resolve_price,
)


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
    eps_waste_coeff: float
    eps100_pack_volume_m3: float
    eps100_unit_price: float
    glue_foam_coverage_m2_per_can: float
    glue_foam_min_units: int
    glue_foam_unit_price: float
    waterproofing_logistics_coeff: float
    waterproofing_consumables_coeff: float
    waterproofing_area_calc_method: str = "legacy_perimeter_height"
    waterproofing_area_m2: float | None = None
    slab_formwork_perimeter_m: float | None = None
    slab_edge_height_m: float | None = None
    non_insulated_edge_lengths_m: list[float] = field(default_factory=list)
    pricing: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        self.validate()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WaterproofingInput":
        return cls(**data)

    def validate(self) -> None:
        if not self.project_name:
            raise ValueError("project_name is required")
        if self.waterproofing_area_calc_method not in {
            "legacy_perimeter_height",
            "spec_area",
        }:
            raise ValueError(
                "waterproofing_area_calc_method must be legacy_perimeter_height or spec_area"
            )

        positive_fields = [
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

        if self.waterproofing_area_calc_method == "spec_area":
            _require_positive("waterproofing_area_m2", self.waterproofing_area_m2)
        else:
            _require_positive("slab_formwork_perimeter_m", self.slab_formwork_perimeter_m)
            _require_positive("slab_edge_height_m", self.slab_edge_height_m)

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
    price_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        if self.display_quantity is None:
            result.pop("display_quantity")
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
        price_code=price_code,
    )


PRICE_FIELD_BY_CODE = {
    "waterproofing_bitumen_mastic_work": "waterproofing_work_unit_price",
    "bitumen_primer_aquamast_18l": "primer_unit_price",
    "bitumen_mastic_aquamast_18kg": "mastic_unit_price",
    "eps100_wall_insulation_work": "eps100_wall_insulation_work_unit_price",
    "eps100_wall_penoplex_geo_material": "eps100_unit_price",
    "eps_glue_foam": "glue_foam_unit_price",
}

PRICE_CODE_BY_FIELD = {
    "waterproofing_work_unit_price": "bitumen_waterproofing_work_m2",
    "primer_unit_price": "bitumen_primer_aquamast_18l_item",
    "mastic_unit_price": "bitumen_mastic_aquamast_18kg_item",
    "eps100_wall_insulation_work_unit_price": "eps_wall_insulation_work_m2",
    "eps100_unit_price": "eps_geo_100_m3",
    "glue_foam_unit_price": "eps_foam_glue_can",
}


def pricing_mode(data: WaterproofingInput) -> str:
    return (data.pricing or {}).get("mode", "locked_case_prices")


def resolve_registry_path(data: WaterproofingInput) -> Path:
    raw_path = (data.pricing or {}).get(
        "registry_path",
        "output/price_registry_filled_v3.xlsx",
    )
    path = Path(raw_path)
    return path if path.is_absolute() else REPO_ROOT / path


def build_effective_pricing(
    data: WaterproofingInput,
) -> tuple[WaterproofingInput, dict[str, Any], list[str]]:
    mode = pricing_mode(data)
    if mode == "locked_case_prices":
        return data, {
            "mode": mode,
            "prices_from_price_registry": 0,
            "prices_from_project_overrides": 0,
            "prices_from_fallback_input": 0,
            "warnings_count": 0,
            "price_resolutions_by_code": {},
        }, []

    if mode != "price_registry_with_fallback":
        raise ValueError(f"Unsupported pricing mode: {mode}")

    registry_path = resolve_registry_path(data)
    registry = load_price_registry(registry_path)
    overrides = load_project_price_overrides(registry_path)

    raw_data = data.to_dict()
    resolutions_by_code: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    summary = {
        "mode": mode,
        "registry_path": str(registry_path),
        "prices_from_price_registry": 0,
        "prices_from_project_overrides": 0,
        "prices_from_fallback_input": 0,
        "warnings_count": 0,
        "price_resolutions_by_code": resolutions_by_code,
    }

    for field_name, price_code in PRICE_CODE_BY_FIELD.items():
        original_price = getattr(data, field_name)
        resolved = resolve_price(price_code, original_price, registry, overrides)
        source = resolved["source"]
        if source == "price_registry":
            summary["prices_from_price_registry"] += 1
        elif source == "project_price_overrides":
            summary["prices_from_project_overrides"] += 1
        else:
            summary["prices_from_fallback_input"] += 1

        if resolved["warning"]:
            warnings.append(f"{price_code}: {resolved['warning']}")

        used_price = resolved["price"]
        raw_data[field_name] = float(used_price) if used_price is not None else original_price
        resolutions_by_code[price_code] = {
            "price_code": price_code,
            "unit_price_source": source,
            "unit_price_original": str(original_price),
            "unit_price_used": str(used_price) if used_price is not None else None,
            "price_warning": resolved["warning"],
        }

    summary["warnings_count"] = len(warnings)
    return WaterproofingInput.from_dict(raw_data), summary, warnings


def enrich_lines_with_pricing(
    lines: list[dict[str, Any]],
    pricing_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    if pricing_summary["mode"] == "locked_case_prices":
        return lines

    resolutions = pricing_summary.get("price_resolutions_by_code", {})
    enriched = []
    for line in lines:
        item = dict(line)
        price_code = item.get("price_code")
        if price_code in resolutions:
            item.update(resolutions[price_code])
        else:
            original_price = item.get("material_unit_price") or item.get("work_unit_price")
            item.setdefault("price_code", price_code)
            item["unit_price_source"] = "locked_case_prices"
            item["unit_price_original"] = str(original_price)
            item["unit_price_used"] = str(original_price)
            item["price_warning"] = None
        enriched.append(item)
    return enriched


def calculate_waterproofing_area(data: WaterproofingInput) -> tuple[float, str]:
    if data.waterproofing_area_calc_method == "spec_area":
        return _round_decimal(_to_decimal(data.waterproofing_area_m2)), "spec_area"

    if data.waterproofing_area_calc_method == "legacy_perimeter_height":
        area = _to_decimal(data.slab_formwork_perimeter_m) * _to_decimal(
            data.slab_edge_height_m
        )
        return _round_decimal(area), "legacy_perimeter_height"

    raise ValueError(f"Unsupported waterproofing_area_calc_method: {data.waterproofing_area_calc_method}")


def calculate_waterproofing_block(data: WaterproofingInput) -> dict[str, Any]:
    waterproofing_area_m2, waterproofing_area_source = calculate_waterproofing_area(data)
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
    geometry_check_enabled = (
        data.slab_formwork_perimeter_m is not None
        and data.slab_edge_height_m is not None
        and bool(data.non_insulated_edge_lengths_m)
    )
    non_insulated_edge_lengths_total_m = None
    insulated_edge_length_m = None
    eps100_wall_geometry_check_area_m2 = None
    if geometry_check_enabled:
        non_insulated_edge_lengths_total_m = _round_decimal(
            sum(data.non_insulated_edge_lengths_m)
        )
        insulated_edge_length_m = _round_decimal(
            _to_decimal(data.slab_formwork_perimeter_m)
            - _to_decimal(non_insulated_edge_lengths_total_m)
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
        "waterproofing_area_calc_method": data.waterproofing_area_calc_method,
        "waterproofing_area_source": waterproofing_area_source,
        "legacy_slab_formwork_perimeter_m": data.slab_formwork_perimeter_m,
        "legacy_slab_edge_height_m": data.slab_edge_height_m,
        "waterproofing_area_m2": waterproofing_area_m2,
        "primer_required_liters": primer_required_liters,
        "primer_raw_units": primer_raw_units,
        "primer_units": primer_units,
        "mastic_required_kg": mastic_required_kg,
        "mastic_raw_units": mastic_raw_units,
        "mastic_units": mastic_units,
        "eps100_wall_insulation_area_m2": eps100_wall_insulation_area_m2,
        "eps100_wall_geometry_check_enabled": geometry_check_enabled,
        "non_insulated_edge_lengths_total_m": non_insulated_edge_lengths_total_m,
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
            price_code="bitumen_waterproofing_work_m2",
        ),
        calculate_line(
            code="bitumen_primer_aquamast_18l",
            name="Праймер битумный AquaMast, 18 л",
            unit="шт",
            quantity=waterproofing["primer_units"],
            material_unit_price=data.primer_unit_price,
            price_code="bitumen_primer_aquamast_18l_item",
        ),
        calculate_line(
            code="bitumen_mastic_aquamast_18kg",
            name="Мастика гидроизоляционная битумная для фундаментов AquaMast, 18 кг",
            unit="шт",
            quantity=waterproofing["mastic_units"],
            material_unit_price=data.mastic_unit_price,
            price_code="bitumen_mastic_aquamast_18kg_item",
        ),
        calculate_line(
            code="eps100_wall_insulation_work",
            name="Утепление стен плиты ЭППС 100 мм",
            unit="м2",
            quantity=waterproofing["eps100_wall_insulation_area_m2"],
            work_unit_price=data.eps100_wall_insulation_work_unit_price,
            price_code="eps_wall_insulation_work_m2",
        ),
        calculate_line(
            code="eps100_wall_penoplex_geo_material",
            name="Пеноплэкс ГЕО 100 мм",
            unit="м3",
            quantity=waterproofing["eps100_wall_order_volume_m3"],
            display_quantity=_round_decimal(
                waterproofing["eps100_wall_order_volume_m3"], "0.01"
            ),
            material_unit_price=data.eps100_unit_price,
            price_code="eps_geo_100_m3",
        ),
        calculate_line(
            code="eps_glue_foam",
            name="Клей-пена для ЭППС",
            unit="баллон",
            quantity=waterproofing["glue_foam_units"],
            material_unit_price=data.glue_foam_unit_price,
            price_code="eps_foam_glue_can",
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
    effective_data, pricing_summary, pricing_warnings = build_effective_pricing(data)
    waterproofing_block = calculate_waterproofing_block(effective_data)
    estimate_lines = calculate_internal_estimate_lines(effective_data, waterproofing_block)
    internal_totals = calculate_internal_totals(
        estimate_lines,
        waterproofing_block["waterproofing_base_subtotal"],
    )
    estimate_lines_data = enrich_lines_with_pricing(
        [line.to_dict() for line in estimate_lines],
        pricing_summary,
    )
    inputs = data.to_dict()
    if inputs.get("pricing") is None:
        inputs.pop("pricing")

    return {
        "inputs": inputs,
        "calculation_blocks": {"waterproofing": waterproofing_block},
        "estimate_lines": estimate_lines_data,
        "internal_totals": internal_totals,
        "pricing_summary": {
            key: value
            for key, value in pricing_summary.items()
            if key != "price_resolutions_by_code"
        },
        "warnings": pricing_warnings,
    }
