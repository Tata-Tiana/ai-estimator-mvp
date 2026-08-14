from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal
from math import ceil
from typing import Any

from load_bearing_walls_lintels_calculator import (
    EstimateLineResult,
    d,
    gas_block_order,
    line,
    q,
    totals,
)


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
    technical_supervision_amount: float
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
    sand_concrete_consumption_kg_per_m2_per_10mm: float = 18.0
    sand_concrete_thickness_factor: float = 1.0
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
    return (item.block_density.upper(), item.block_size.replace(" ", "").lower())


def _block_unit_price(item: P6BlockItem, rates: P6Rates) -> float:
    if item.material_unit_price is not None:
        return item.material_unit_price
    density, size = _block_material_key(item)
    if density == "D400" and "600x400x250" in size:
        return rates.gas_block_d400_unit_price
    if density == "D500" and "600x250x250" in size:
        return rates.gas_block_d500_250_unit_price
    if density == "D500" and "600x150x250" in size:
        return rates.gas_block_d500_150_unit_price
    raise ValueError(f"Unsupported block material without explicit material_unit_price: {item.block_density} {item.block_size}")


def _block_pallet_volume(item: P6BlockItem, defaults: P6Defaults) -> float:
    if item.pallet_volume_m3 is not None:
        return item.pallet_volume_m3
    density, size = _block_material_key(item)
    if density == "D400" and "600x400x250" in size:
        return defaults.gas_block_d400_pallet_volume_m3
    if density == "D500" and "600x250x250" in size:
        return defaults.gas_block_d500_250_pallet_volume_m3
    if density == "D500" and "600x150x250" in size:
        return defaults.gas_block_d500_150_pallet_volume_m3
    raise ValueError(f"Unsupported block material without explicit pallet_volume_m3: {item.block_density} {item.block_size}")


def _block_price_code(item: P6BlockItem) -> str | None:
    density, size = _block_material_key(item)
    if density == "D400" and "600x400x250" in size:
        return "gas_block_d400_m3"
    if density == "D500" and "600x250x250" in size:
        return "gas_block_d500_m3"
    if density == "D500" and "600x150x250" in size:
        return "gas_block_d500_150_m3"
    return None


def _delivery_batch_id(zone: P6WallZone) -> str:
    if zone.block_delivery_batch_id:
        return zone.block_delivery_batch_id
    if zone.zone_kind in {"floor_2", "second_light", "parapet", "vent_chimney_cladding"}:
        return "upper_parapet_vent"
    return zone.zone_id


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
    zones: list[P6WallZone], defaults: P6Defaults
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
                price_code=f"rebar_{steel_class.lower()}_d{diameter_mm}_m",
            )
        )
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


def calculate_load_bearing_walls_lintels_p6(data: P6LoadBearingWallsLintelsInput) -> dict[str, Any]:
    rates = data.rates
    defaults = data.defaults
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
    calculation_blocks: dict[str, Any] = {"zones": {}, "delivery_batches": {}, "rebar": {}}
    delivery_batches: dict[str, Decimal] = {}

    for zone in data.wall_zones:
        block_spec_total = sum(d(item.volume_m3) for item in zone.block_items)
        regular_masonry = _zone_has_regular_masonry(zone)
        if regular_masonry and block_spec_total > 0:
            lines.append(
                line(
                    f"{zone.zone_id}_masonry_work",
                    zone.display_name,
                    "м3",
                    q(block_spec_total),
                    work_unit_price=rates.masonry_work_unit_price,
                    notes="Работа по проектному объёму без запаса.",
                    price_code="gas_block_masonry_work_m3",
                )
            )
        vent_chimney_cladding_area = _zone_vent_chimney_cladding_area(zone, defaults)
        if vent_chimney_cladding_area > 0:
            lines.append(
                line(
                    f"{zone.zone_id}_gas_block_cladding_work",
                    "Обкладка дымохода и вентканалов 150 мм",
                    "м2",
                    q(vent_chimney_cladding_area),
                    work_unit_price=rates.vent_chimney_cladding_work_unit_price,
                    notes="Площадь работ считается как проектный объём блока 150 мм / 0.15 м.",
                    price_code="gas_block_cladding_work_m2",
                )
            )
        if zone.cutoff_waterproofing_area_m2 > 0:
            lines.append(
                line(
                    f"{zone.zone_id}_cutoff_waterproofing_under_first_row_blocks",
                    f"Гидроизоляция поверхности под первый ряд блоков: {zone.display_name}",
                    "м2",
                    zone.cutoff_waterproofing_area_m2,
                    material_unit_price=rates.cutoff_waterproofing_material_unit_price,
                    work_unit_price=rates.cutoff_waterproofing_work_unit_price,
                    price_code="cutoff_waterproofing_under_blocks_m2",
                )
            )

        zone_order_volume = Decimal("0")
        zone_block_controls: dict[str, Any] = {}
        for block in zone.block_items:
            order = gas_block_order(block.volume_m3, defaults.gas_block_waste_coeff, _block_pallet_volume(block, defaults))
            zone_order_volume += d(order["order_volume_m3"])
            code = f"{zone.zone_id}_block_{block.item_id}"
            zone_block_controls[block.item_id] = {
                "spec_volume_m3": q(block.volume_m3),
                **order,
            }
            lines.append(
                line(
                    code,
                    f"Газобетонный блок {block.block_density} {block.block_size}: {zone.display_name}",
                    "м3",
                    order["order_volume_m3"],
                    material_unit_price=_block_unit_price(block, rates),
                    price_code=_block_price_code(block),
                )
            )
        if zone_order_volume > 0:
            batch_id = _delivery_batch_id(zone)
            delivery_batches[batch_id] = delivery_batches.get(batch_id, Decimal("0")) + zone_order_volume
            adhesive_raw = block_spec_total * d(defaults.adhesive_consumption_bag_per_m3) * d(defaults.adhesive_waste_coeff)
            lines.append(
                line(
                    f"{zone.zone_id}_block_adhesive",
                    f"Монтажный клей для блоков 25 кг: {zone.display_name}",
                    "мешок",
                    int(ceil(adhesive_raw)),
                    material_unit_price=rates.adhesive_unit_price,
                    price_code="block_adhesive_bag",
                )
            )
        if zone.cutoff_waterproofing_area_m2 > 0:
            sand_raw = (
                d(zone.cutoff_waterproofing_area_m2)
                * d(defaults.sand_concrete_consumption_kg_per_m2_per_10mm)
                * d(defaults.sand_concrete_thickness_factor)
                / d(defaults.sand_concrete_bag_weight_kg)
            )
            lines.append(
                line(
                    f"{zone.zone_id}_sand_concrete_m300_first_row",
                    f"Пескобетон М300 40 кг: {zone.display_name}",
                    "шт",
                    int(ceil(sand_raw)),
                    material_unit_price=rates.sand_concrete_unit_price,
                    price_code="sand_concrete_bag",
                )
            )
        if zone.chasing_rebar_items:
            chasing_length = sum(d(item.spec_length_m) for item in zone.chasing_rebar_items)
            lines.append(
                line(
                    f"{zone.zone_id}_chasing_for_reinforcement",
                    f"Штробление блоков под дополнительное усиление: {zone.display_name}",
                    "мп",
                    q(chasing_length),
                    notes="Нулевая строка — работа входит в ставку кладки. База для арматуры.",
                )
            )
        lintel_blocks, lintel_lines = _calculate_lintel_blocks(zone, data)
        lines.extend(lintel_lines)
        calculation_blocks["zones"][zone.zone_id] = {
            "display_name": zone.display_name,
            "zone_kind": zone.zone_kind,
            "block_spec_volume_m3": q(block_spec_total),
            "block_order_volume_m3": q(zone_order_volume),
            "vent_chimney_cladding_area_m2": q(vent_chimney_cladding_area),
            "block_items": zone_block_controls,
            "lintels": lintel_blocks.get(zone.zone_id, {}),
        }

    rebar_controls, rebar_lines, rebar_delivery_weight = _pool_rebar_by_zone_purpose(data.wall_zones, defaults)
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

    for batch_id, order_volume in delivery_batches.items():
        trucks = int(ceil(order_volume / d(defaults.gas_block_delivery_truck_capacity_m3)))
        crane_shifts = max(1, int(ceil(Decimal(trucks) / d(defaults.crane_trucks_per_shift)))) if trucks > 0 else 0
        calculation_blocks["delivery_batches"][batch_id] = {
            "block_order_volume_m3": q(order_volume),
            "raw_trucks": q(order_volume / d(defaults.gas_block_delivery_truck_capacity_m3)),
            "trucks": trucks,
            "crane_shifts": crane_shifts,
        }
        lines.extend(
            [
                line(
                    f"{batch_id}_blocks_delivery",
                    "Доставка блоков, смеси",
                    "маш",
                    trucks,
                    material_unit_price=rates.block_delivery_unit_price,
                    notes=f"Партия поставки {batch_id}; по закупочному объёму после поддонов.",
                    price_code="block_delivery_truck",
                ),
                line(
                    f"{batch_id}_blocks_unloading_manipulator",
                    "Разгрузка блоков, смеси манипулятором",
                    "маш",
                    trucks,
                    material_unit_price=rates.block_unloading_manipulator_unit_price,
                    price_code="block_unloading_manipulator_truck",
                ),
                line(
                    f"{batch_id}_blocks_crane_moving",
                    "Перемещение блоков, смеси автокраном 25 т",
                    "смена",
                    crane_shifts,
                    material_unit_price=rates.crane_25t_unit_price,
                    notes="Калькулятор: минимум 1 смена при положительной партии, далее ceil(машины/3).",
                    price_code="crane_shift",
                ),
            ]
        )

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
                work_unit_price=rates.technical_supervision_amount,
                price_code="technical_supervision_walls_lintels",
            ),
            line("procurement_warehouse_costs", "Заготовительно-складские расходы", "-", 1),
            line("overhead_general_business_costs", "Накладные и общехозяйственные расходы", "-", 1),
            line("estimated_profit", "Сметная прибыль", "-", 1),
        ]
    )
    return {
        "inputs": data.to_dict(),
        "calculation_blocks": calculation_blocks,
        "estimate_lines": [item.to_dict() for item in lines],
        "internal_totals": totals(lines),
        "warnings": [],
    }
