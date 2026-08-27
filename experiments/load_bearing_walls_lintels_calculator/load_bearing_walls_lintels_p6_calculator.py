from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from math import ceil
from typing import Any, Callable

from load_bearing_walls_lintels_calculator import (
    EstimateLineResult,
    d,
    gas_block_order,
    line,
    q,
    rebar_price_code,
    totals,
)

# 2026-08-26: row-order fix. Elena's real smetas (ЮСВ + ТРЦ, both cross-checked line-by-line
# against the delivered xlsx) never mix line types across zones - every line for a zone (floor_1,
# floor_2, парапет+вентканалы) is printed together, in this fixed order, before moving to the next
# zone. This calculator used to compute in that shape but EMIT in a different one (per-zone
# masonry/blocks loop, then a separate global pass for ALL zones' adhesive, then a separate global
# pass for ALL zones' rebar, then a separate global pass for ALL batches' delivery/crane) - visually
# jumping between zones 4 times instead of finishing one zone's block before the next. Rather than
# restructure the computation (risk of changing actual quantities), every line below is tagged with
# a (zone_rank, category) sort key at the point it's created, and the whole `lines` list is sorted
# once at the end - arithmetic is untouched, only final row order changes.
_RANK_BEFORE_ZONES = -1
_RANK_AFTER_ZONES = 1_000_000

_CAT_WATERPROOFING = 0
_CAT_MASONRY = 1
_CAT_BLOCK_MATERIAL = 2
_CAT_ADHESIVE = 3
_CAT_SAND_CONCRETE = 4
_CAT_LINTEL_CUTTING = 5
_CAT_CHASING = 6
_CAT_CHASING_REBAR = 7
_CAT_DELIVERY = 8
_CAT_UNLOADING = 9
_CAT_CRANE = 10
_CAT_LINTEL_FORMWORK_MONOLITH = 11
_CAT_LINTEL_FRAME_ASSEMBLY = 12
_CAT_LINTEL_REBAR = 13
_CAT_LINTEL_CONCRETING = 14
_CAT_LINTEL_CONCRETE_MATERIAL = 15
_CAT_LINTEL_CONCRETE_DELIVERY = 16
_CAT_LINTEL_CONCRETE_LIFTING = 17
_CAT_LINTEL_INSULATION = 18


def _lintel_line_category(code: str) -> int:
    if code.endswith("_u_block_lintel_cutting"):
        return _CAT_LINTEL_CUTTING
    if code.endswith("_u_block_lintel_concreting_work") or code.endswith("_monolithic_lintel_concreting_work"):
        return _CAT_LINTEL_CONCRETING
    if code.endswith(("_lintel_formwork_installation", "_lintel_formwork_plywood_material", "_lintel_formwork_timber_material")):
        return _CAT_LINTEL_FORMWORK_MONOLITH
    if code.endswith(("_lintel_edge_insulation_work", "_lintel_edge_insulation_eps_material", "_lintel_edge_insulation_glue_foam")):
        return _CAT_LINTEL_INSULATION
    if code.endswith("_lintel_concrete_b22_5_m300_material"):
        return _CAT_LINTEL_CONCRETE_MATERIAL
    if code.endswith("_lintel_concrete_delivery"):
        return _CAT_LINTEL_CONCRETE_DELIVERY
    if code.endswith("_manual_concrete_lifting"):
        return _CAT_LINTEL_CONCRETE_LIFTING
    raise ValueError(f"Unrecognized lintel line code for sort category: {code}")


@dataclass(frozen=True)
class P6BlockItem:
    item_id: str
    block_density: str
    block_size: str
    volume_m3: float
    context: str | None = None
    material_unit_price: float | None = None
    pallet_volume_m3: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "P6BlockItem":
        return cls(**data)


@dataclass(frozen=True)
class P6RebarItem:
    item_id: str
    purpose: str
    steel_class: str
    diameter_mm: int
    spec_length_m: float
    kg_per_meter: float
    rod_length_m: float
    unit_price_per_m: float
    source_label: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "P6RebarItem":
        return cls(**data)


@dataclass(frozen=True)
class P6LintelItem:
    lintel_id: str
    lintel_kind: str
    total_length_m: float = 0.0
    concrete_volume_m3: float = 0.0
    rebar_items: list[P6RebarItem | dict[str, Any]] = field(default_factory=list)
    formwork_horizontal_area_m2: float = 0.0
    formwork_vertical_area_m2: float = 0.0
    insulation_length_m: float = 0.0
    insulation_eps_spec_volume_m3: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "P6LintelItem":
        parsed = {
            **data,
            "rebar_items": [
                item if isinstance(item, P6RebarItem) else P6RebarItem.from_dict(item)
                for item in data.get("rebar_items", [])
            ],
        }
        return cls(**parsed)


@dataclass(frozen=True)
class P6WallZone:
    zone_id: str
    display_name: str
    zone_kind: str
    block_items: list[P6BlockItem | dict[str, Any]] = field(default_factory=list)
    chasing_rebar_items: list[P6RebarItem | dict[str, Any]] = field(default_factory=list)
    unassigned_lintel_rebar_items: list[P6RebarItem | dict[str, Any]] = field(default_factory=list)
    lintel_items: list[P6LintelItem | dict[str, Any]] = field(default_factory=list)
    cutoff_waterproofing_area_m2: float = 0.0
    block_delivery_batch_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "P6WallZone":
        parsed = {
            **data,
            "block_items": [
                item if isinstance(item, P6BlockItem) else P6BlockItem.from_dict(item)
                for item in data.get("block_items", [])
            ],
            "chasing_rebar_items": [
                item if isinstance(item, P6RebarItem) else P6RebarItem.from_dict(item)
                for item in data.get("chasing_rebar_items", [])
            ],
            "unassigned_lintel_rebar_items": [
                item if isinstance(item, P6RebarItem) else P6RebarItem.from_dict(item)
                for item in data.get("unassigned_lintel_rebar_items", [])
            ],
            "lintel_items": [
                item if isinstance(item, P6LintelItem) else P6LintelItem.from_dict(item)
                for item in data.get("lintel_items", [])
            ],
        }
        return cls(**parsed)


@dataclass(frozen=True)
class P6Rates:
    scaffolding_setup_work_unit_price: float
    scaffolding_timber_unit_price: float
    cutoff_waterproofing_material_unit_price: float
    cutoff_waterproofing_work_unit_price: float
    masonry_work_unit_price: float
    gas_block_d400_unit_price: float
    gas_block_d500_250_unit_price: float
    gas_block_d500_150_unit_price: float
    vent_chimney_cladding_work_unit_price: float
    adhesive_unit_price: float
    sand_concrete_unit_price: float
    block_delivery_unit_price: float
    block_unloading_manipulator_unit_price: float
    crane_25t_unit_price: float
    u_block_cutting_work_unit_price: float
    lintel_concreting_work_unit_price: float
    lintel_monolithic_concreting_work_unit_price: float
    concrete_m300_unit_price: float
    concrete_delivery_unit_price: float
    manual_concrete_lifting_work_unit_price: float
    lintel_formwork_plywood_unit_price: float
    lintel_formwork_timber_unit_price: float
    lintel_insulation_work_unit_price: float
    lintel_insulation_eps_unit_price: float
    lintel_glue_foam_unit_price: float
    waste_removal_truck_unit_price: float
    waste_removal_work_unit_price: float
    rebar_metal_delivery_unit_price: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "P6Rates":
        return cls(**data)


@dataclass(frozen=True)
class P6Defaults:
    gas_block_waste_coeff: float = 1.05
    gas_block_d400_pallet_volume_m3: float = 2.15
    gas_block_d500_250_pallet_volume_m3: float = 1.8
    gas_block_d500_150_pallet_volume_m3: float = 1.8
    adhesive_consumption_bag_per_m3: float = 1.2
    adhesive_waste_coeff: float = 1.05
    sand_concrete_consumption_kg_per_m2_per_10mm: float = 19.0
    sand_concrete_thickness_factor: float = 2.0
    sand_concrete_bag_weight_kg: float = 40.0
    gas_block_length_m: float = 0.6
    gas_block_delivery_truck_capacity_m3: float = 32.0
    vent_chimney_block_thickness_m: float = 0.15
    crane_trucks_per_shift: float = 3.0
    rebar_waste_coeff: float = 1.05
    concrete_waste_coeff: float = 1.05
    lintel_concrete_min_order_volume_m3: float = 1.0
    lintel_formwork_plywood_sheet_area_m2: float = 2.3
    lintel_formwork_board_thickness_m: float = 0.05
    lintel_insulation_eps_waste_coeff: float = 1.05
    lintel_insulation_eps_pack_volume_m3: float = 0.2773
    lintel_glue_foam_coverage_m_per_can: float = 12.0
    lintel_glue_foam_min_units: float = 1.0
    scaffolding_setup_quantity: float = 2.0
    scaffolding_timber_quantity_m3: float = 2.0
    waste_removal_trucks: float = 3.0
    walls_consumables_rate: float = 0.03
    # 10000, not routed through the price registry - checked 3 real projects' delivered smetas
    # 2026-08-15: walls technical supervision is 10000 in all 3, no exceptions.
    technical_supervision_amount: float = 10000.0

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "P6Defaults":
        return cls(**(data or {}))


@dataclass(frozen=True)
class P6LoadBearingWallsLintelsInput:
    project_name: str
    wall_zones: list[P6WallZone | dict[str, Any]]
    rates: P6Rates | dict[str, Any]
    defaults: P6Defaults | dict[str, Any] = field(default_factory=P6Defaults)
    rebar_metal_delivery_trucks: float = 0.0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "P6LoadBearingWallsLintelsInput":
        parsed = {
            **data,
            "wall_zones": [
                item if isinstance(item, P6WallZone) else P6WallZone.from_dict(item)
                for item in data.get("wall_zones", [])
            ],
            "rates": data["rates"] if isinstance(data["rates"], P6Rates) else P6Rates.from_dict(data["rates"]),
            "defaults": data.get("defaults") if isinstance(data.get("defaults"), P6Defaults) else P6Defaults.from_dict(data.get("defaults")),
        }
        return cls(**parsed)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _block_material_key(item: P6BlockItem) -> tuple[str, str]:
    normalized_size = item.block_size.replace(" ", "").lower().replace("х", "x")
    normalized_density = item.block_density.upper().replace("-", "").replace(" ", "")
    return (normalized_density, normalized_size)


def _block_size_parts(size: str) -> tuple[int, ...]:
    try:
        return tuple(sorted(int(float(part)) for part in size.split("x")))
    except (TypeError, ValueError):
        return ()


def _same_block_size(size: str, expected: tuple[int, int, int]) -> bool:
    return _block_size_parts(size) == tuple(sorted(expected))


def _block_unit_price(item: P6BlockItem, rates: P6Rates) -> float:
    if item.material_unit_price is not None:
        return item.material_unit_price
    density, size = _block_material_key(item)
    if density == "D400" and _same_block_size(size, (600, 400, 250)):
        return rates.gas_block_d400_unit_price
    if density == "D500" and _same_block_size(size, (600, 250, 250)):
        return rates.gas_block_d500_250_unit_price
    if density == "D500" and _same_block_size(size, (600, 150, 250)):
        return rates.gas_block_d500_150_unit_price
    raise ValueError(f"Unsupported block material without explicit material_unit_price: {item.block_density} {item.block_size}")


def _block_pallet_volume(item: P6BlockItem, defaults: P6Defaults) -> float:
    if item.pallet_volume_m3 is not None:
        return item.pallet_volume_m3
    density, size = _block_material_key(item)
    if density == "D400" and _same_block_size(size, (600, 400, 250)):
        return defaults.gas_block_d400_pallet_volume_m3
    if density == "D500" and _same_block_size(size, (600, 250, 250)):
        return defaults.gas_block_d500_250_pallet_volume_m3
    if density == "D500" and _same_block_size(size, (600, 150, 250)):
        return defaults.gas_block_d500_150_pallet_volume_m3
    raise ValueError(f"Unsupported block material without explicit pallet_volume_m3: {item.block_density} {item.block_size}")


def _block_price_code(item: P6BlockItem) -> str | None:
    density, size = _block_material_key(item)
    if density == "D400" and _same_block_size(size, (600, 400, 250)):
        return "gas_block_d400_m3"
    if density == "D500" and _same_block_size(size, (600, 250, 250)):
        return "gas_block_d500_m3"
    if density == "D500" and _same_block_size(size, (600, 150, 250)):
        return "gas_block_d500_150_m3"
    return None


def _delivery_batch_id(zone: P6WallZone) -> str:
    if zone.block_delivery_batch_id:
        return zone.block_delivery_batch_id
    if zone.zone_kind in {"floor_2", "second_light", "parapet", "vent_chimney_cladding"}:
        return "upper_parapet_vent"
    return zone.zone_id


def _crane_batch_id(zone: P6WallZone) -> str:
    """Crane mobilization is booked per real pour/lift, never pooled across zones just because
    their block deliveries share a truck (Elena: crane/pump/metal-delivery/tech-supervision are
    per-pour, each real pour has its own - see elena_per_pour_manual_costs_ruling). Confirmed on
    real project data: floor_2 and parapet blocks are delivered together on one truck batch (same
    delivery_batch_id), but the crane still lifts them in two separate trips - floor_2's masonry
    lift, then a second dedicated trip for parapet - billed as two separate crane-shift lines even
    though it's one truck delivery. So parapet always gets its own crane batch, independent of
    which delivery batch its blocks were pooled into; every other zone_kind still shares the
    delivery batch's crane batch (vent_chimney_cladding's small volume rides along with floor_2,
    matching real data - no separate crane line for vent alone)."""
    if zone.zone_kind == "parapet":
        return "parapet"
    return _delivery_batch_id(zone)


def _zone_has_regular_masonry(zone: P6WallZone) -> bool:
    return zone.zone_kind not in {"vent_chimney_cladding", "partitions"}


def _zone_vent_chimney_cladding_area(zone: P6WallZone, defaults: P6Defaults) -> Decimal:
    if zone.zone_kind != "vent_chimney_cladding":
        return Decimal("0")
    spec_volume = sum(d(item.volume_m3) for item in zone.block_items)
    if spec_volume <= 0:
        return Decimal("0")
    return spec_volume / d(defaults.vent_chimney_block_thickness_m)


def _pool_rebar_by_zone_purpose(
    zones: list[P6WallZone],
    defaults: P6Defaults,
    rank_of: Callable[[str], int],
    sort_keys: dict[str, tuple[int, int]],
) -> tuple[dict[str, Any], list[EstimateLineResult], Decimal]:
    groups: dict[tuple[str, str, str, int], list[P6RebarItem]] = {}
    order: list[tuple[str, str, str, int]] = []
    zone_names = {zone.zone_id: zone.display_name for zone in zones}
    for zone in zones:
        for item in zone.chasing_rebar_items:
            key = (zone.zone_id, item.purpose, item.steel_class, item.diameter_mm)
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(item)
        for item in zone.unassigned_lintel_rebar_items:
            key = (zone.zone_id, item.purpose, item.steel_class, item.diameter_mm)
            if key not in groups:
                groups[key] = []
                order.append(key)
            groups[key].append(item)
        for lintel in zone.lintel_items:
            for item in lintel.rebar_items:
                key = (zone.zone_id, item.purpose, item.steel_class, item.diameter_mm)
                if key not in groups:
                    groups[key] = []
                    order.append(key)
                groups[key].append(item)

    controls: dict[str, Any] = {}
    lines: list[EstimateLineResult] = []
    delivery_weight_total = Decimal("0")
    lintel_frame_totals: dict[str, Decimal] = {}
    for zone_id, purpose, steel_class, diameter_mm in order:
        items = groups[(zone_id, purpose, steel_class, diameter_mm)]
        kg_per_meter = items[0].kg_per_meter
        rod_length_m = items[0].rod_length_m
        unit_price_per_m = items[0].unit_price_per_m
        for other in items[1:]:
            if (
                other.kg_per_meter != kg_per_meter
                or other.rod_length_m != rod_length_m
                or other.unit_price_per_m != unit_price_per_m
            ):
                raise ValueError(
                    f"Cannot pool rebar safely for zone={zone_id}, purpose={purpose}, "
                    f"steel={steel_class}, diameter={diameter_mm}: row defaults differ."
                )
        spec_length = sum(d(item.spec_length_m) for item in items)
        length_with_waste = spec_length * d(defaults.rebar_waste_coeff)
        raw_rods = length_with_waste / d(rod_length_m)
        rods = int(ceil(raw_rods))
        order_length = d(rods) * d(rod_length_m)
        delivery_weight = order_length * d(kg_per_meter)
        delivery_weight_total += delivery_weight
        code = f"{zone_id}_{purpose}_rebar_{steel_class.lower()}_d{diameter_mm}"
        controls[code] = {
            "zone_id": zone_id,
            "purpose": purpose,
            "steel_class": steel_class,
            "diameter_mm": diameter_mm,
            "spec_length_m": q(spec_length),
            "length_with_waste_m": q(length_with_waste),
            "raw_rods": q(raw_rods),
            "rods": rods,
            "order_length_m": q(order_length),
            "delivery_weight_kg": q(delivery_weight),
        }
        purpose_label = {
            "masonry_chasing": "кладки",
            "lintels": "перемычек",
            "parapet_chasing": "парапета",
        }.get(purpose, purpose)
        lines.append(
            line(
                code,
                f"Арматура {steel_class} Ø{diameter_mm} для {purpose_label}: {zone_names.get(zone_id, zone_id)}",
                "мп",
                q(order_length),
                material_unit_price=unit_price_per_m,
                price_code=rebar_price_code(steel_class, diameter_mm),
            )
        )
        sort_keys[code] = (rank_of(zone_id), _CAT_LINTEL_REBAR if purpose == "lintels" else _CAT_CHASING_REBAR)
        if purpose == "lintels":
            lintel_frame_totals[zone_id] = lintel_frame_totals.get(zone_id, Decimal("0")) + order_length

    # Изготовление и монтаж каркаса армирования перемычек: zero-rate structural line, confirmed
    # present on all 3 real projects (ТРЦ, АРК, ЮСВ) for every lintel-bearing zone/section - always
    # billed to the client (real work rate) but always 0 internally (себестоимость), and always
    # exactly the sum of that same zone's own lintel rebar order-length lines above (verified
    # against real numbers: ТРЦ floor_1 117+84=201мп, floor_2 11.7+93.6+72=177.3мп - both match the
    # real smeta's own quantity exactly). foundation_slab_calculator.py and floor_slab_calculator.py
    # already have the equivalent line for their own rebar; this was the one rebar-bearing
    # calculator missing it.
    for zone_id, total_length in lintel_frame_totals.items():
        frame_code = f"{zone_id}_lintel_rebar_frame_assembly"
        lines.append(
            line(
                frame_code,
                f"Изготовление и монтаж каркаса армирования перемычек из арматуры: {zone_names.get(zone_id, zone_id)}",
                "мп",
                q(total_length),
                notes="Нулевая строка — подтверждено на 3 реальных проектах (себестоимость всегда 0, работа входит в клиентскую наценку, не в себестоимость).",
            )
        )
        sort_keys[frame_code] = (rank_of(zone_id), _CAT_LINTEL_FRAME_ASSEMBLY)
    return controls, lines, delivery_weight_total


def _calculate_lintel_blocks(
    zone: P6WallZone, data: P6LoadBearingWallsLintelsInput
) -> tuple[dict[str, Any], list[EstimateLineResult]]:
    rates = data.rates
    defaults = data.defaults
    blocks: dict[str, Any] = {}
    lines: list[EstimateLineResult] = []
    ublock_length = sum(d(item.total_length_m) for item in zone.lintel_items if item.lintel_kind == "u_block")
    monolithic_length = sum(d(item.total_length_m) for item in zone.lintel_items if item.lintel_kind == "monolithic")
    monolithic_concrete = sum(d(item.concrete_volume_m3) for item in zone.lintel_items if item.lintel_kind == "monolithic")
    ublock_concrete = sum(d(item.concrete_volume_m3) for item in zone.lintel_items if item.lintel_kind == "u_block")
    concrete_required = (ublock_concrete + monolithic_concrete) * d(defaults.concrete_waste_coeff)
    concrete_order = (
        max(d(defaults.lintel_concrete_min_order_volume_m3), Decimal(ceil(concrete_required)))
        if concrete_required > 0
        else Decimal("0")
    )
    if ublock_length > 0:
        lines.extend(
            [
                line(
                    f"{zone.zone_id}_u_block_lintel_cutting",
                    f"Резка блока под перемычку (U-блок): {zone.display_name}",
                    "шт",
                    q(ublock_length / d(defaults.gas_block_length_m)),
                    work_unit_price=rates.u_block_cutting_work_unit_price,
                    price_code="u_block_lintel_cutting_item",
                ),
                line(
                    f"{zone.zone_id}_u_block_lintel_concreting_work",
                    f"Бетонирование перемычек в U-блоке: {zone.display_name}",
                    "мп",
                    q(ublock_length),
                    work_unit_price=rates.lintel_concreting_work_unit_price,
                    price_code="lintel_concreting_work_m",
                ),
            ]
        )
    if monolithic_length > 0:
        total_formwork_area = sum(
            d(item.formwork_horizontal_area_m2) + d(item.formwork_vertical_area_m2)
            for item in zone.lintel_items
            if item.lintel_kind == "monolithic"
        )
        plywood_qty = Decimal(ceil(total_formwork_area / d(defaults.lintel_formwork_plywood_sheet_area_m2)))
        timber_volume = total_formwork_area * d(defaults.lintel_formwork_board_thickness_m)
        insulation_length = sum(d(item.insulation_length_m) for item in zone.lintel_items if item.lintel_kind == "monolithic")
        eps_spec = sum(d(item.insulation_eps_spec_volume_m3) for item in zone.lintel_items if item.lintel_kind == "monolithic")
        eps_required = eps_spec * d(defaults.lintel_insulation_eps_waste_coeff)
        eps_packs = int(ceil(eps_required / d(defaults.lintel_insulation_eps_pack_volume_m3))) if insulation_length > 0 and eps_required > 0 else 0
        eps_order = d(eps_packs) * d(defaults.lintel_insulation_eps_pack_volume_m3)
        foam_units = (
            max(int(defaults.lintel_glue_foam_min_units), int(ceil(insulation_length / d(defaults.lintel_glue_foam_coverage_m_per_can))))
            if insulation_length > 0
            else 0
        )
        lines.extend(
            [
                line(
                    f"{zone.zone_id}_lintel_formwork_installation",
                    f"Монтаж опалубки из доски для заливки перемычек: {zone.display_name}",
                    "м2",
                    q(total_formwork_area),
                    notes="Нулевая строка — подтверждено на 3 реальных проектах (себестоимость всегда 0, работа входит в ставку бетонирования). Площадь — база для фанеры/пиломатериала ниже.",
                ),
                line(
                    f"{zone.zone_id}_monolithic_lintel_concreting_work",
                    f"Бетонирование монолитных перемычек: {zone.display_name}",
                    "мп",
                    q(monolithic_length),
                    work_unit_price=rates.lintel_monolithic_concreting_work_unit_price,
                    notes="Работа считается по длине монолитных перемычек, не по объёму бетона.",
                    price_code="lintel_monolithic_concreting_work_m",
                ),
                line(
                    f"{zone.zone_id}_lintel_formwork_plywood_material",
                    f"Фанера для опалубки монолитных перемычек: {zone.display_name}",
                    "шт",
                    q(plywood_qty),
                    material_unit_price=rates.lintel_formwork_plywood_unit_price,
                    price_code="lintel_formwork_plywood_sheet",
                ),
                line(
                    f"{zone.zone_id}_lintel_formwork_timber_material",
                    f"Пиломатериал обрезной для опалубки монолитных перемычек: {zone.display_name}",
                    "м3",
                    q(timber_volume),
                    material_unit_price=rates.lintel_formwork_timber_unit_price,
                    price_code="lintel_formwork_timber_m3",
                ),
            ]
        )
        if insulation_length > 0:
            lines.extend(
                [
                    line(
                        f"{zone.zone_id}_lintel_edge_insulation_work",
                        f"Устройство утепления по наружной стороне монолитной перемычки: {zone.display_name}",
                        "мп",
                        q(insulation_length),
                        work_unit_price=rates.lintel_insulation_work_unit_price,
                        price_code="lintel_edge_insulation_work_m",
                    ),
                    line(
                        f"{zone.zone_id}_lintel_edge_insulation_eps_material",
                        f"Экструдированный пенополистирол Пеноплэкс Основа: {zone.display_name}",
                        "м3",
                        q(eps_order),
                        display_quantity=q(eps_order, "0.01"),
                        material_unit_price=rates.lintel_insulation_eps_unit_price,
                        price_code="eps_penoplex_osnova_100_m3",
                    ),
                    line(
                        f"{zone.zone_id}_lintel_edge_insulation_glue_foam",
                        f"Клей-пена для ЭППС: {zone.display_name}",
                        "баллон",
                        foam_units,
                        material_unit_price=rates.lintel_glue_foam_unit_price,
                        price_code="eps_foam_glue_can",
                    ),
                ]
            )
    if concrete_order > 0:
        lines.extend(
            [
                line(
                    f"{zone.zone_id}_lintel_concrete_b22_5_m300_material",
                    f"Бетон марки В22,5 (М300): {zone.display_name}",
                    "м3",
                    q(concrete_order),
                    material_unit_price=rates.concrete_m300_unit_price,
                    notes="Минимум заказа бетона применяется к сумме U-блоков и монолитных перемычек зоны.",
                    price_code="concrete_b22_5_m3",
                ),
                line(
                    f"{zone.zone_id}_lintel_concrete_delivery",
                    "Доставка бетона до объекта",
                    "рейс",
                    1,
                    material_unit_price=rates.concrete_delivery_unit_price,
                    price_code="concrete_delivery_trip",
                ),
                line(
                    f"{zone.zone_id}_manual_concrete_lifting",
                    "Перенос, подъем бетона вручную",
                    "м3",
                    q(concrete_order),
                    work_unit_price=rates.manual_concrete_lifting_work_unit_price,
                    price_code="manual_concrete_lifting_m3",
                ),
            ]
        )
    blocks[zone.zone_id] = {
        "ublock_length_m": q(ublock_length),
        "monolithic_length_m": q(monolithic_length),
        "concrete_required_volume_m3": q(concrete_required),
        "concrete_order_volume_m3": q(concrete_order),
    }
    return blocks, lines


def _merge_zones_by_kind(
    zones: list[P6WallZone], kind: str, merged_zone_id: str, merged_display_name: str
) -> list[P6WallZone]:
    """Elena's real smetas always bill a given zone_kind as ONE section, no matter how many
    physical sub-zones the source spec breaks it into - confirmed on all 3 real projects
    (P6_WALLS_LINTELS_DATA_CONTRACT.md: one real project's КР2 gives парапеты1эт/парапеты2эт as two
    spec rows, another even has two separate drawing sheets for it, a third doesn't split it at
    all - all 3 real smetas still show exactly one "Парапет"/"Парапеты" section). Universal by
    zone_kind, not by a fixed count: merges however many zones of this kind exist (1, 2, or more)
    into one - a project with 3 parapet sub-zones or with none at all both work the same way,
    nothing here assumes exactly 2 the way one real project happens to have. If 0 or 1 zone of
    this kind exist, returns zones unchanged (nothing to merge)."""
    matching = [zone for zone in zones if zone.zone_kind == kind]
    if len(matching) <= 1:
        return zones
    merged = P6WallZone(
        zone_id=merged_zone_id,
        display_name=merged_display_name,
        zone_kind=kind,
        block_items=[item for zone in matching for item in zone.block_items],
        chasing_rebar_items=[item for zone in matching for item in zone.chasing_rebar_items],
        unassigned_lintel_rebar_items=[
            item for zone in matching for item in zone.unassigned_lintel_rebar_items
        ],
        lintel_items=[item for zone in matching for item in zone.lintel_items],
        cutoff_waterproofing_area_m2=sum(zone.cutoff_waterproofing_area_m2 for zone in matching),
        block_delivery_batch_id=next(
            (zone.block_delivery_batch_id for zone in matching if zone.block_delivery_batch_id),
            None,
        ),
    )
    result: list[P6WallZone] = []
    inserted = False
    for zone in zones:
        if zone.zone_kind != kind:
            result.append(zone)
        elif not inserted:
            result.append(merged)
            inserted = True
    return result


def calculate_load_bearing_walls_lintels_p6(data: P6LoadBearingWallsLintelsInput) -> dict[str, Any]:
    rates = data.rates
    defaults = data.defaults
    wall_zones = _merge_zones_by_kind(data.wall_zones, "parapet", "parapet", "Парапет")
    lines: list[EstimateLineResult] = [
        line(
            "scaffolding_setup_dismantling",
            "Устройство лесов, подмостей для кладки, демонтаж лесов",
            "компл",
            defaults.scaffolding_setup_quantity,
            work_unit_price=rates.scaffolding_setup_work_unit_price,
            price_code="scaffolding_setup_dismantling_work_set",
        ),
        line(
            "scaffolding_timber_material",
            "Пиломатериал для устройства лесов",
            "м3",
            defaults.scaffolding_timber_quantity_m3,
            material_unit_price=rates.scaffolding_timber_unit_price,
            price_code="timber_m3",
        ),
    ]
    sort_keys: dict[str, tuple[int, int]] = {
        "scaffolding_setup_dismantling": (_RANK_BEFORE_ZONES, 0),
        "scaffolding_timber_material": (_RANK_BEFORE_ZONES, 1),
    }
    calculation_blocks: dict[str, Any] = {"zones": {}, "delivery_batches": {}, "crane_batches": {}, "rebar": {}}
    delivery_batches: dict[str, Decimal] = {}
    crane_batches: dict[str, Decimal] = {}
    delivery_batch_rank: dict[str, int] = {}
    crane_batch_rank: dict[str, int] = {}

    # A zone with no masonry work of its own (_zone_has_regular_masonry() - today only
    # vent_chimney_cladding) never buys blocks as its own separate delivery - real project data
    # (ТРЦ 2026-08-16) confirms Elena buys its adhesive together with whichever real zone precedes
    # it (парапет), one shared bag count, not two independently-rounded ones: парапет 19.15м3 +
    # вентканалы 0.66м3 rounds to 25 bags pooled, vs 25+1=26 bags rounded separately - the extra
    # bag was a real, if small, overcount. Pooled the same way rebar/blocks already are elsewhere
    # in this calculator (raw quantity summed BEFORE rounding, never after) - generalizes to any
    # zone_kind sharing this property, not hardcoded to vent_chimney_cladding by name.
    zone_names = {zone.zone_id: zone.display_name for zone in wall_zones}
    adhesive_pool_target: dict[str, str] = {}
    last_real_zone_id: str | None = None
    for zone in wall_zones:
        if _zone_has_regular_masonry(zone):
            last_real_zone_id = zone.zone_id
        adhesive_pool_target[zone.zone_id] = last_real_zone_id if last_real_zone_id is not None else zone.zone_id
    adhesive_pools: dict[str, Decimal] = {}

    # Same grouping as adhesive_pool_target above, reused for row order: a satellite zone with no
    # masonry of its own (vent_chimney_cladding) is visually part of the preceding real zone's
    # block in Elena's real smetas too (её "Обкладка дымохода" печатается ВНУТРИ парапетного блока,
    # не отдельным блоком после него) - give it the same sort rank as that zone.
    _group_rank_order: list[str] = []
    for zone in wall_zones:
        owner = adhesive_pool_target[zone.zone_id]
        if owner not in _group_rank_order:
            _group_rank_order.append(owner)
    _zone_group_rank = {owner: idx for idx, owner in enumerate(_group_rank_order)}

    def rank_of(zone_id: str) -> int:
        return _zone_group_rank[adhesive_pool_target[zone_id]]

    for zone in wall_zones:
        block_spec_total = sum(d(item.volume_m3) for item in zone.block_items)
        regular_masonry = _zone_has_regular_masonry(zone)
        if regular_masonry and block_spec_total > 0:
            masonry_code = f"{zone.zone_id}_masonry_work"
            lines.append(
                line(
                    masonry_code,
                    zone.display_name,
                    "м3",
                    q(block_spec_total),
                    work_unit_price=rates.masonry_work_unit_price,
                    notes="Работа по проектному объёму без запаса.",
                    price_code="gas_block_masonry_work_m3",
                )
            )
            sort_keys[masonry_code] = (rank_of(zone.zone_id), _CAT_MASONRY)
        vent_chimney_cladding_area = _zone_vent_chimney_cladding_area(zone, defaults)
        if vent_chimney_cladding_area > 0:
            cladding_code = f"{zone.zone_id}_gas_block_cladding_work"
            lines.append(
                line(
                    cladding_code,
                    "Обкладка дымохода и вентканалов 150 мм",
                    "м2",
                    q(vent_chimney_cladding_area),
                    work_unit_price=rates.vent_chimney_cladding_work_unit_price,
                    notes="Площадь работ считается как проектный объём блока 150 мм / 0.15 м.",
                    price_code="gas_block_cladding_work_m2",
                )
            )
            sort_keys[cladding_code] = (rank_of(zone.zone_id), _CAT_MASONRY)
        if zone.cutoff_waterproofing_area_m2 > 0:
            waterproofing_code = f"{zone.zone_id}_cutoff_waterproofing_under_first_row_blocks"
            lines.append(
                line(
                    waterproofing_code,
                    f"Гидроизоляция поверхности под первый ряд блоков: {zone.display_name}",
                    "м2",
                    zone.cutoff_waterproofing_area_m2,
                    material_unit_price=rates.cutoff_waterproofing_material_unit_price,
                    work_unit_price=rates.cutoff_waterproofing_work_unit_price,
                    price_code="cutoff_waterproofing_under_blocks_m2",
                )
            )
            sort_keys[waterproofing_code] = (rank_of(zone.zone_id), _CAT_WATERPROOFING)

        zone_order_volume = Decimal("0")
        zone_block_controls: dict[str, Any] = {}
        # Pool raw volume by material (density+size) BEFORE pallet-rounding, same principle
        # already proven for rebar (rebar_from_spec_length_items_pooled's own docstring, and the
        # 2026-08-14 parapet-zone merge above): rounding each raw row to its own pallet
        # independently can waste a partial pallet that pooling-then-rounding-once would not. Real
        # zones sometimes carry more than one raw block_item of the same material (e.g. a merged
        # parapet zone combining two spec sub-zones) - group them into one purchase line instead
        # of one line per raw item, matching Elena's real smetas (one block-material line per
        # zone, not one per spec row).
        block_groups: dict[tuple[str, str], list[P6BlockItem]] = {}
        block_group_order: list[tuple[str, str]] = []
        for block in zone.block_items:
            key = _block_material_key(block)
            if key not in block_groups:
                block_groups[key] = []
                block_group_order.append(key)
            block_groups[key].append(block)
        for key in block_group_order:
            group_items = block_groups[key]
            first = group_items[0]
            spec_volume_total = sum(d(item.volume_m3) for item in group_items)
            order = gas_block_order(
                spec_volume_total, defaults.gas_block_waste_coeff, _block_pallet_volume(first, defaults)
            )
            zone_order_volume += d(order["order_volume_m3"])
            code = f"{zone.zone_id}_block_{first.item_id}"
            for item in group_items:
                zone_block_controls[item.item_id] = {
                    "spec_volume_m3": q(item.volume_m3),
                    "pooled_with": [i.item_id for i in group_items if i.item_id != item.item_id],
                    **order,
                }
            lines.append(
                line(
                    code,
                    f"Газобетонный блок {first.block_density} {first.block_size}: {zone.display_name}",
                    "м3",
                    order["order_volume_m3"],
                    material_unit_price=_block_unit_price(first, rates),
                    price_code=_block_price_code(first),
                )
            )
            sort_keys[code] = (rank_of(zone.zone_id), _CAT_BLOCK_MATERIAL)
        if zone_order_volume > 0:
            batch_id = _delivery_batch_id(zone)
            delivery_batches[batch_id] = delivery_batches.get(batch_id, Decimal("0")) + zone_order_volume
            delivery_batch_rank.setdefault(batch_id, rank_of(zone.zone_id))
            crane_batch_id = _crane_batch_id(zone)
            crane_batches[crane_batch_id] = crane_batches.get(crane_batch_id, Decimal("0")) + zone_order_volume
            crane_batch_rank.setdefault(crane_batch_id, rank_of(zone.zone_id))
            adhesive_target = adhesive_pool_target[zone.zone_id]
            adhesive_pools[adhesive_target] = adhesive_pools.get(adhesive_target, Decimal("0")) + block_spec_total
        if zone.cutoff_waterproofing_area_m2 > 0:
            sand_raw = (
                d(zone.cutoff_waterproofing_area_m2)
                * d(defaults.sand_concrete_consumption_kg_per_m2_per_10mm)
                * d(defaults.sand_concrete_thickness_factor)
                / d(defaults.sand_concrete_bag_weight_kg)
            )
            sand_code = f"{zone.zone_id}_sand_concrete_m300_first_row"
            lines.append(
                line(
                    sand_code,
                    f"Пескобетон М300 40 кг: {zone.display_name}",
                    "шт",
                    int(ceil(sand_raw)),
                    material_unit_price=rates.sand_concrete_unit_price,
                    price_code="sand_concrete_bag",
                )
            )
            sort_keys[sand_code] = (rank_of(zone.zone_id), _CAT_SAND_CONCRETE)
        if zone.chasing_rebar_items:
            chasing_length = sum(d(item.spec_length_m) for item in zone.chasing_rebar_items)
            chasing_code = f"{zone.zone_id}_chasing_for_reinforcement"
            lines.append(
                line(
                    chasing_code,
                    f"Штробление блоков под дополнительное усиление: {zone.display_name}",
                    "мп",
                    q(chasing_length),
                    notes="Нулевая строка — работа входит в ставку кладки. База для арматуры.",
                )
            )
            sort_keys[chasing_code] = (rank_of(zone.zone_id), _CAT_CHASING)
        lintel_blocks, lintel_lines = _calculate_lintel_blocks(zone, data)
        lines.extend(lintel_lines)
        for lintel_line in lintel_lines:
            sort_keys[lintel_line.code] = (rank_of(zone.zone_id), _lintel_line_category(lintel_line.code))
        calculation_blocks["zones"][zone.zone_id] = {
            "display_name": zone.display_name,
            "zone_kind": zone.zone_kind,
            "block_spec_volume_m3": q(block_spec_total),
            "block_order_volume_m3": q(zone_order_volume),
            "vent_chimney_cladding_area_m2": q(vent_chimney_cladding_area),
            "block_items": zone_block_controls,
            "lintels": lintel_blocks.get(zone.zone_id, {}),
        }

    for target_zone_id, pooled_block_spec_total in adhesive_pools.items():
        adhesive_raw = pooled_block_spec_total * d(defaults.adhesive_consumption_bag_per_m3) * d(defaults.adhesive_waste_coeff)
        adhesive_code = f"{target_zone_id}_block_adhesive"
        lines.append(
            line(
                adhesive_code,
                f"Монтажный клей для блоков 25 кг: {zone_names.get(target_zone_id, target_zone_id)}",
                "мешок",
                int(ceil(adhesive_raw)),
                material_unit_price=rates.adhesive_unit_price,
                price_code="block_adhesive_bag",
            )
        )
        sort_keys[adhesive_code] = (rank_of(target_zone_id), _CAT_ADHESIVE)

    rebar_controls, rebar_lines, rebar_delivery_weight = _pool_rebar_by_zone_purpose(
        wall_zones, defaults, rank_of, sort_keys
    )
    lines.extend(rebar_lines)
    calculation_blocks["rebar"] = {
        "items": rebar_controls,
        "delivery_weight_kg": q(rebar_delivery_weight),
    }
    if data.rebar_metal_delivery_trucks > 0:
        lines.append(
            line(
                "rebar_metal_delivery",
                "Доставка арматуры, металла",
                "маш",
                data.rebar_metal_delivery_trucks,
                material_unit_price=rates.rebar_metal_delivery_unit_price,
                notes="Количество машин приходит с уровня коробки: накопление поставочного веса арматуры по разделам, порог 10 т.",
                price_code="metal_delivery_truck",
            )
        )
        sort_keys["rebar_metal_delivery"] = (_RANK_AFTER_ZONES, -1)

    for batch_id, order_volume in delivery_batches.items():
        trucks = int(ceil(order_volume / d(defaults.gas_block_delivery_truck_capacity_m3)))
        calculation_blocks["delivery_batches"][batch_id] = {
            "block_order_volume_m3": q(order_volume),
            "raw_trucks": q(order_volume / d(defaults.gas_block_delivery_truck_capacity_m3)),
            "trucks": trucks,
        }
        delivery_code = f"{batch_id}_blocks_delivery"
        unloading_code = f"{batch_id}_blocks_unloading_manipulator"
        lines.extend(
            [
                line(
                    delivery_code,
                    "Доставка блоков, смеси",
                    "маш",
                    trucks,
                    material_unit_price=rates.block_delivery_unit_price,
                    notes=f"Партия поставки {batch_id}; по закупочному объёму после поддонов.",
                    price_code="block_delivery_truck",
                ),
                line(
                    unloading_code,
                    "Разгрузка блоков, смеси манипулятором",
                    "маш",
                    trucks,
                    material_unit_price=rates.block_unloading_manipulator_unit_price,
                    price_code="block_unloading_manipulator_truck",
                ),
            ]
        )
        sort_keys[delivery_code] = (delivery_batch_rank[batch_id], _CAT_DELIVERY)
        sort_keys[unloading_code] = (delivery_batch_rank[batch_id], _CAT_UNLOADING)

    for crane_batch_id, crane_order_volume in crane_batches.items():
        crane_trucks = int(ceil(crane_order_volume / d(defaults.gas_block_delivery_truck_capacity_m3)))
        crane_shifts = (
            max(1, int(ceil(Decimal(crane_trucks) / d(defaults.crane_trucks_per_shift)))) if crane_trucks > 0 else 0
        )
        calculation_blocks["crane_batches"][crane_batch_id] = {
            "block_order_volume_m3": q(crane_order_volume),
            "raw_trucks": q(crane_order_volume / d(defaults.gas_block_delivery_truck_capacity_m3)),
            "crane_shifts": crane_shifts,
        }
        crane_code = f"{crane_batch_id}_blocks_crane_moving"
        lines.append(
            line(
                crane_code,
                "Перемещение блоков, смеси автокраном 25 т",
                "смена",
                crane_shifts,
                material_unit_price=rates.crane_25t_unit_price,
                notes="Кран считается отдельно от партии доставки — минимум 1 смена на каждый реальный подъём, далее ceil(эквивалент машин/3).",
                price_code="crane_shift",
            )
        )
        sort_keys[crane_code] = (crane_batch_rank[crane_batch_id], _CAT_CRANE)

    direct_cost_base_raw = sum(d(item.line_total_raw) for item in lines)
    consumables_amount_raw = direct_cost_base_raw * d(defaults.walls_consumables_rate)
    lines.extend(
        [
            line(
                "walls_consumables_tool_amortization",
                "Расходные материалы, амортизация инструмента",
                "комплект",
                1,
                material_unit_price=q(consumables_amount_raw, "0.000001"),
                material_total_raw_override=q(consumables_amount_raw, "0.000001"),
                notes="Процент от прямой себестоимости раздела до расходников.",
            ),
            line(
                "construction_waste_removal",
                "Вывоз мусора с объекта",
                "маш",
                defaults.waste_removal_trucks,
                material_unit_price=rates.waste_removal_truck_unit_price,
                work_unit_price=rates.waste_removal_work_unit_price,
                price_code="waste_removal_truck",
            ),
            line(
                "walls_technical_supervision",
                "Технический надзор",
                "-",
                1,
                work_unit_price=defaults.technical_supervision_amount,
                price_code="technical_supervision_walls_lintels",
            ),
            line("procurement_warehouse_costs", "Заготовительно-складские расходы", "-", 1),
            line("overhead_general_business_costs", "Накладные и общехозяйственные расходы", "-", 1),
            line("estimated_profit", "Сметная прибыль", "-", 1),
        ]
    )
    sort_keys.update(
        {
            "walls_consumables_tool_amortization": (_RANK_AFTER_ZONES, 0),
            "construction_waste_removal": (_RANK_AFTER_ZONES, 1),
            "walls_technical_supervision": (_RANK_AFTER_ZONES, 2),
            "procurement_warehouse_costs": (_RANK_AFTER_ZONES, 3),
            "overhead_general_business_costs": (_RANK_AFTER_ZONES, 4),
            "estimated_profit": (_RANK_AFTER_ZONES, 5),
        }
    )
    # Row-order fix (2026-08-26): every line above carries a (zone_rank, category) sort key
    # matching Elena's real per-zone row order (see the module-level comment near the category
    # constants). Stable sort - lines with equal keys keep their original relative order, which is
    # what keeps парапет's own lines ahead of vent_chimney_cladding's tied-rank lines below.
    lines.sort(key=lambda item: sort_keys[item.code])
    return {
        "inputs": data.to_dict(),
        "calculation_blocks": calculation_blocks,
        "estimate_lines": [item.to_dict() for item in lines],
        "internal_totals": totals(lines),
        "warnings": [],
    }
