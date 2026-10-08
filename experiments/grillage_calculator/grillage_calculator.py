from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from typing import Any


ALLOWED_ELEMENT_TYPES = {
    "grillage",
    "rib_up",
    "rib_down",
    "foundation_wall",
    "strip",
    "beam",
    "column_footing",
    "pad",
    "other_grillage",
}


def d(value: float | int | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def q(value: float | int | Decimal, step: str = "0.0001") -> float:
    return float(d(value).quantize(Decimal(step), rounding=ROUND_HALF_UP))


def money(value: float | int | Decimal) -> int:
    return int(d(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def ceil_step(value: float, step: float) -> float:
    if value < 0 or step <= 0:
        raise ValueError("ceil_step requires value >= 0 and step > 0")
    return q(d(ceil(value / step)) * d(step))


def require_non_negative(name: str, value: float | int | None) -> None:
    if value is None or value < 0:
        raise ValueError(f"{name} must be present and >= 0")


def require_positive(name: str, value: float | int | None) -> None:
    if value is None or value <= 0:
        raise ValueError(f"{name} must be present and > 0")


@dataclass(frozen=True)
class GrillageElement:
    element_id: str
    display_name: str
    element_type: str
    level: str | None = None
    width_m: float | None = None
    height_m: float | None = None
    length_m: float | None = None
    count: float | None = None
    concrete_grade: str | None = None
    concrete_volume_m3: float | None = None
    membrane_area_m2: float | None = None
    inventory_formwork_area_m2: float | None = None
    timber_formwork_area_m2: float | None = None
    horizontal_insulation_material: str | None = None
    horizontal_insulation_thickness_mm: float | None = None
    horizontal_insulation_area_m2: float | None = None
    horizontal_insulation_volume_m3: float | None = None
    include_in_estimate: bool = True

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "GrillageElement":
        return cls(**value)


@dataclass(frozen=True)
class GrillageRebarItem:
    code: str
    name: str
    steel_class: str
    diameter_mm: int
    source_length_m: float
    kg_per_meter: float
    rod_length_m: float
    unit_price_per_m: float
    element_id: str | None = None

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "GrillageRebarItem":
        return cls(**value)


@dataclass(frozen=True)
class GrillageInput:
    project_name: str
    grillage_elements: list[GrillageElement | dict[str, Any]]
    rebar_items: list[GrillageRebarItem | dict[str, Any]]

    membrane_installation_work_unit_price: float
    membrane_overlap_coeff: float
    membrane_roll_area_m2: float
    planter_standard_roll_unit_price: float
    planterband_per_membrane_roll: float
    planterband_unit_price: float

    inventory_formwork_installation_work_unit_price: float
    inventory_formwork_rental_unit_price: float
    formwork_transport_unit_price: float
    inventory_formwork_consumables_unit_price: float
    crane_unit_price: float
    timber_formwork_installation_work_unit_price: float
    plywood_unit_price: float
    timber_unit_price: float
    formwork_dismantling_work_unit_price: float
    formwork_cleaning_work_unit_price: float

    rebar_frame_assembly_work_unit_price: float
    rebar_waste_coeff: float
    rebar_metal_delivery_trucks: float
    rebar_metal_delivery_unit_price: float

    concreting_work_unit_price: float
    concrete_waste_coeff: float
    concrete_round_step_m3: float
    concrete_unit_price: float
    concrete_mixer_volume_m3: float
    concrete_delivery_unit_price: float
    concrete_pump_shifts: float
    concrete_pump_unit_price: float
    manual_concrete_transfer_volume_m3: float
    manual_concrete_transfer_work_unit_price: float

    eps_laying_work_unit_price: float
    eps_waste_coeff: float
    eps_pack_volume_m3: float
    eps_unit_price: float

    technical_supervision_amount: float
    horizontal_insulation_default_thickness_mm: float = 50
    logistics_and_supply_rate: float = 0.02
    consumables_tool_amortization_rate: float = 0.03
    plywood_sheet_width_m: float = 1.52
    plywood_sheet_height_m: float = 1.52
    plywood_waste_coeff: float = 1.05
    timber_thickness_m: float = 0.05
    timber_round_step_m3: float = 0.1
    formwork_transport_threshold_m2: float = 200
    crane_threshold_m2: float = 150
    planter_purchase_area_m2: float | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "grillage_elements",
            [
                item if isinstance(item, GrillageElement) else GrillageElement.from_dict(item)
                for item in self.grillage_elements
            ],
        )
        object.__setattr__(
            self,
            "rebar_items",
            [
                item if isinstance(item, GrillageRebarItem) else GrillageRebarItem.from_dict(item)
                for item in self.rebar_items
            ],
        )
        self.validate()

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "GrillageInput":
        return cls(**value)

    def validate(self) -> None:
        if not self.project_name:
            raise ValueError("project_name is required")
        active = [item for item in self.grillage_elements if item.include_in_estimate]
        ids = [item.element_id for item in active]
        if not active:
            raise ValueError("at least one included grillage_elements row is required")
        if any(not item_id for item_id in ids) or len(ids) != len(set(ids)):
            raise ValueError("included grillage_elements.element_id values must be non-empty and unique")

        for item in active:
            if item.element_type not in ALLOWED_ELEMENT_TYPES:
                raise ValueError(
                    f"grillage_elements.{item.element_id}.element_type={item.element_type!r} "
                    "does not belong to grillage"
                )
            for field_name in (
                "width_m",
                "height_m",
                "length_m",
                "count",
                "concrete_volume_m3",
                "membrane_area_m2",
                "inventory_formwork_area_m2",
                "timber_formwork_area_m2",
                "horizontal_insulation_thickness_mm",
                "horizontal_insulation_area_m2",
                "horizontal_insulation_volume_m3",
            ):
                value = getattr(item, field_name)
                if value is not None:
                    require_non_negative(f"grillage_elements.{item.element_id}.{field_name}", value)
            insulation_present = any(
                value is not None
                for value in (
                    item.horizontal_insulation_thickness_mm,
                    item.horizontal_insulation_area_m2,
                    item.horizontal_insulation_volume_m3,
                )
            )
            if insulation_present:
                material = (item.horizontal_insulation_material or "ЭППС").upper()
                if "ЭППС" not in material and "XPS" not in material:
                    raise ValueError(
                        f"grillage_elements.{item.element_id} has unsupported horizontal "
                        f"insulation material {material!r}"
                    )
                if (
                    item.horizontal_insulation_thickness_mm is not None
                    and item.horizontal_insulation_thickness_mm
                    != self.horizontal_insulation_default_thickness_mm
                ):
                    raise ValueError(
                        f"grillage_elements.{item.element_id} cannot use the configured EPS 50 line"
                    )
                if (
                    item.horizontal_insulation_area_m2 is not None
                    and item.horizontal_insulation_volume_m3 is not None
                ):
                    expected_volume = q(
                        d(item.horizontal_insulation_area_m2)
                        * d(
                            item.horizontal_insulation_thickness_mm
                            or self.horizontal_insulation_default_thickness_mm
                        )
                        / Decimal("1000")
                    )
                    if abs(expected_volume - item.horizontal_insulation_volume_m3) > 0.001:
                        raise ValueError(
                            f"grillage_elements.{item.element_id} horizontal insulation "
                            f"area/thickness gives {expected_volume} m3 but the specified "
                            f"volume is {item.horizontal_insulation_volume_m3} m3"
                        )
        active_ids = set(ids)
        if not self.rebar_items:
            raise ValueError("grillage_rebar_items is required")
        for item in self.rebar_items:
            if not item.code or not item.name or not item.steel_class:
                raise ValueError("each grillage_rebar_items row requires code/name/steel_class")
            for field_name in (
                "diameter_mm",
                "kg_per_meter",
                "rod_length_m",
            ):
                require_positive(f"grillage_rebar_items.{item.code}.{field_name}", getattr(item, field_name))
            for field_name in ("source_length_m", "unit_price_per_m"):
                require_non_negative(
                    f"grillage_rebar_items.{item.code}.{field_name}", getattr(item, field_name)
                )
            if item.element_id and item.element_id not in active_ids:
                raise ValueError(
                    f"grillage_rebar_items.{item.code}.element_id={item.element_id!r} "
                    "does not match an included grillage element"
                )

        for field_name in (
            "membrane_overlap_coeff",
            "membrane_roll_area_m2",
            "planterband_per_membrane_roll",
            "rebar_waste_coeff",
            "concrete_waste_coeff",
            "concrete_round_step_m3",
            "concrete_mixer_volume_m3",
            "eps_waste_coeff",
            "eps_pack_volume_m3",
            "horizontal_insulation_default_thickness_mm",
            "plywood_sheet_width_m",
            "plywood_sheet_height_m",
            "plywood_waste_coeff",
            "timber_thickness_m",
            "timber_round_step_m3",
            "formwork_transport_threshold_m2",
            "crane_threshold_m2",
        ):
            require_positive(field_name, getattr(self, field_name))

        non_negative_fields = (
            "membrane_installation_work_unit_price",
            "planter_standard_roll_unit_price",
            "planterband_unit_price",
            "inventory_formwork_installation_work_unit_price",
            "inventory_formwork_rental_unit_price",
            "formwork_transport_unit_price",
            "inventory_formwork_consumables_unit_price",
            "crane_unit_price",
            "timber_formwork_installation_work_unit_price",
            "plywood_unit_price",
            "timber_unit_price",
            "formwork_dismantling_work_unit_price",
            "formwork_cleaning_work_unit_price",
            "rebar_frame_assembly_work_unit_price",
            "rebar_metal_delivery_trucks",
            "rebar_metal_delivery_unit_price",
            "concreting_work_unit_price",
            "concrete_unit_price",
            "concrete_delivery_unit_price",
            "concrete_pump_shifts",
            "concrete_pump_unit_price",
            "manual_concrete_transfer_volume_m3",
            "manual_concrete_transfer_work_unit_price",
            "eps_laying_work_unit_price",
            "eps_unit_price",
            "technical_supervision_amount",
            "logistics_and_supply_rate",
            "consumables_tool_amortization_rate",
        )
        for field_name in non_negative_fields:
            require_non_negative(field_name, getattr(self, field_name))


@dataclass(frozen=True)
class EstimateLine:
    code: str
    name: str
    unit: str
    quantity: float
    material_unit_price: float = 0
    work_unit_price: float = 0
    price_code: str | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        material_total = money(d(self.quantity) * d(self.material_unit_price))
        work_total = money(d(self.quantity) * d(self.work_unit_price))
        return {
            "code": self.code,
            "name": self.name,
            "unit": self.unit,
            "quantity": q(self.quantity),
            "display_quantity": q(self.quantity, "0.01"),
            "material_unit_price": self.material_unit_price,
            "material_total": material_total,
            "work_unit_price": self.work_unit_price,
            "work_total": work_total,
            "line_total": material_total + work_total,
            "price_code": self.price_code,
            "notes": self.notes,
        }


def _sum(elements: list[GrillageElement], field_name: str) -> float:
    return q(sum((d(getattr(item, field_name) or 0) for item in elements), Decimal("0")))


def _rebar_lines(data: GrillageInput) -> tuple[list[EstimateLine], dict[str, Any]]:
    pools: dict[tuple[str, int], list[GrillageRebarItem]] = {}
    for item in data.rebar_items:
        pools.setdefault((item.steel_class, int(item.diameter_mm)), []).append(item)

    lines: list[EstimateLine] = []
    controls: list[dict[str, Any]] = []
    total_order_length = Decimal("0")
    total_delivery_weight = Decimal("0")
    for (steel_class, diameter), items in pools.items():
        reference = items[0]
        for item in items[1:]:
            if (
                item.kg_per_meter != reference.kg_per_meter
                or item.rod_length_m != reference.rod_length_m
                or item.unit_price_per_m != reference.unit_price_per_m
            ):
                raise ValueError(
                    f"cannot pool grillage rebar {steel_class} D{diameter}: catalog values differ"
                )
        source_length = sum((d(item.source_length_m) for item in items), Decimal("0"))
        with_waste = source_length * d(data.rebar_waste_coeff)
        rods = ceil(with_waste / d(reference.rod_length_m))
        order_length = d(rods) * d(reference.rod_length_m)
        delivery_weight = order_length * d(reference.kg_per_meter)
        total_order_length += order_length
        total_delivery_weight += delivery_weight
        class_digits = "".join(char for char in steel_class if char.isdigit())
        code_class = f"a{class_digits}" if class_digits else steel_class.lower()
        lines.append(
            EstimateLine(
                code=f"rebar_{code_class}_d{diameter}_m",
                name=f"Арматура класса {steel_class} диаметром {diameter} мм",
                unit="мп",
                quantity=q(order_length),
                material_unit_price=reference.unit_price_per_m,
                price_code=f"rebar_{code_class}_d{diameter}_m",
            )
        )
        controls.append(
            {
                "steel_class": steel_class,
                "diameter_mm": diameter,
                "source_length_m": q(source_length),
                "length_with_waste_m": q(with_waste),
                "rods": rods,
                "order_length_m": q(order_length),
                "delivery_weight_kg": q(delivery_weight),
                "item_codes": [item.code for item in items],
            }
        )
    return lines, {
        "pools": controls,
        "order_length_m": q(total_order_length),
        "delivery_weight_kg": q(total_delivery_weight),
    }


def calculate_grillage(data: GrillageInput) -> dict[str, Any]:
    elements = [item for item in data.grillage_elements if item.include_in_estimate]
    membrane_area = _sum(elements, "membrane_area_m2")
    inventory_formwork_area = _sum(elements, "inventory_formwork_area_m2")
    timber_formwork_area = _sum(elements, "timber_formwork_area_m2")
    concrete_volume = _sum(elements, "concrete_volume_m3")
    eps_volume_decimal = Decimal("0")
    eps_area_decimal = Decimal("0")
    for element in elements:
        thickness_m = d(
            element.horizontal_insulation_thickness_mm
            or data.horizontal_insulation_default_thickness_mm
        ) / Decimal("1000")
        element_volume = element.horizontal_insulation_volume_m3
        element_area = element.horizontal_insulation_area_m2
        if element_volume is None and element_area is not None:
            element_volume = q(d(element_area) * thickness_m)
        if element_area is None and element_volume is not None:
            element_area = q(d(element_volume) / thickness_m)
        eps_volume_decimal += d(element_volume or 0)
        eps_area_decimal += d(element_area or 0)
    eps_volume = q(eps_volume_decimal)
    eps_area = q(eps_area_decimal)

    purchase_area = data.planter_purchase_area_m2
    if purchase_area is None:
        purchase_area = membrane_area
        planter_basis = "grillage_only_preview"
    else:
        require_non_negative("planter_purchase_area_m2", purchase_area)
        if purchase_area < membrane_area:
            raise ValueError("planter_purchase_area_m2 cannot be smaller than grillage membrane area")
        planter_basis = "shared_foundation_purchase"
    membrane_required_area = q(d(purchase_area) * d(data.membrane_overlap_coeff))
    membrane_rolls = ceil(d(membrane_required_area) / d(data.membrane_roll_area_m2))
    planterband_quantity = q(d(membrane_rolls) * d(data.planterband_per_membrane_roll))

    formwork_transport_trips = 0
    crane_shifts = 0
    if inventory_formwork_area > 0:
        formwork_transport_trips = 2 if inventory_formwork_area <= data.formwork_transport_threshold_m2 else 4
        crane_shifts = 1 if inventory_formwork_area <= data.crane_threshold_m2 else 2

    plywood_sheet_area = d(data.plywood_sheet_width_m) * d(data.plywood_sheet_height_m)
    plywood_sheets = ceil(
        d(timber_formwork_area) * d(data.plywood_waste_coeff) / plywood_sheet_area
    ) if timber_formwork_area > 0 else 0
    timber_volume = ceil_step(
        q(d(timber_formwork_area) * d(data.timber_thickness_m)),
        data.timber_round_step_m3,
    ) if timber_formwork_area > 0 else 0
    dismantling_area = q(d(inventory_formwork_area) + d(timber_formwork_area))

    rebar_material_lines, rebar = _rebar_lines(data)
    concrete_required = q(d(concrete_volume) * d(data.concrete_waste_coeff))
    concrete_order = ceil_step(concrete_required, data.concrete_round_step_m3)
    concrete_delivery_trips = ceil(d(concrete_order) / d(data.concrete_mixer_volume_m3))
    eps_required = q(d(eps_volume) * d(data.eps_waste_coeff))
    eps_packs = ceil(d(eps_required) / d(data.eps_pack_volume_m3)) if eps_required > 0 else 0
    eps_order = q(d(eps_packs) * d(data.eps_pack_volume_m3))

    lines = [
        EstimateLine("planter_membrane_installation", "Монтаж мембраны PLANTER", "м2", membrane_area, work_unit_price=data.membrane_installation_work_unit_price, price_code="planter_membrane_installation_work_m2"),
        EstimateLine("planter_standard_material", "Planter Standard Технониколь", "рул", membrane_rolls, material_unit_price=data.planter_standard_roll_unit_price, price_code="planter_standard_roll", notes="До общей сборки плиты и ростверка закупка является предварительной, если planter_purchase_area_m2 не передан."),
        EstimateLine("planterband_material", "PLANTERBAND", "шт", planterband_quantity, material_unit_price=data.planterband_unit_price, price_code="planterband_item"),
        EstimateLine("inventory_formwork_installation", "Монтаж инвентарной опалубки", "м2", inventory_formwork_area, work_unit_price=data.inventory_formwork_installation_work_unit_price),
        EstimateLine("inventory_formwork_rental", "Амортизация инвентарной опалубки", "м2", inventory_formwork_area, material_unit_price=data.inventory_formwork_rental_unit_price),
        EstimateLine("formwork_transport", "Доставка и вывоз опалубки манипулятором", "маш", formwork_transport_trips, material_unit_price=data.formwork_transport_unit_price),
        EstimateLine("inventory_formwork_consumables", "Расходники инвентарной опалубки", "м2", inventory_formwork_area, material_unit_price=data.inventory_formwork_consumables_unit_price),
        EstimateLine("formwork_rebar_crane", "Подача опалубки и арматуры автокраном", "смена", crane_shifts, material_unit_price=data.crane_unit_price),
        EstimateLine("timber_formwork_installation", "Деревянная опалубка подколонников и подпятников", "м2", timber_formwork_area, work_unit_price=data.timber_formwork_installation_work_unit_price),
        EstimateLine("formwork_plywood", "Фанера ФК 1,52 x 1,52 толщиной 18 мм", "шт", plywood_sheets, material_unit_price=data.plywood_unit_price, price_code="plywood_1520x1520_18mm_sheet"),
        EstimateLine("formwork_timber", "Пиломатериал обрезной", "м3", timber_volume, material_unit_price=data.timber_unit_price, price_code="timber_m3"),
        EstimateLine("rebar_frame_assembly", "Изготовление и монтаж армокаркаса", "мп", rebar["order_length_m"], work_unit_price=data.rebar_frame_assembly_work_unit_price),
        *rebar_material_lines,
        EstimateLine("rebar_metal_delivery", "Доставка арматуры, металла", "маш", data.rebar_metal_delivery_trucks, material_unit_price=data.rebar_metal_delivery_unit_price, price_code="metal_delivery_truck"),
        EstimateLine("grillage_concreting_work", "Бетонирование ростверка", "м3", concrete_volume, work_unit_price=data.concreting_work_unit_price, price_code="concrete_placing_work_m3"),
        EstimateLine("concrete_material", "Бетон", "м3", concrete_order, material_unit_price=data.concrete_unit_price, price_code="concrete_b22_5_m3"),
        EstimateLine("concrete_delivery", "Доставка бетона", "рейс", concrete_delivery_trips, material_unit_price=data.concrete_delivery_unit_price, price_code="concrete_delivery_trip"),
        EstimateLine("concrete_pump", "Бетононасос", "смена", data.concrete_pump_shifts, material_unit_price=data.concrete_pump_unit_price, price_code="concrete_pump_32m_shift"),
        EstimateLine("manual_concrete_transfer", "Ручной перенос, подъём бетона", "м3", data.manual_concrete_transfer_volume_m3, work_unit_price=data.manual_concrete_transfer_work_unit_price),
        EstimateLine("formwork_dismantling", "Демонтаж опалубки", "м2", dismantling_area, work_unit_price=data.formwork_dismantling_work_unit_price),
        EstimateLine("formwork_cleaning", "Зачистка ленты, замоноличивание рустов", "м2", dismantling_area, work_unit_price=data.formwork_cleaning_work_unit_price),
    ]
    if eps_volume > 0 or eps_area > 0:
        lines.extend(
            [
                EstimateLine("horizontal_eps_laying", "Укладка горизонтального ЭППС под ростверком", "м2", eps_area, work_unit_price=data.eps_laying_work_unit_price, price_code="eps_laying_work_m2"),
                EstimateLine("horizontal_eps_material", "ЭППС под ростверком", "м3", eps_order, material_unit_price=data.eps_unit_price, price_code="eps_geo_50_m3"),
            ]
        )

    subtotal_before_rates = sum(line.to_dict()["line_total"] for line in lines)
    logistics_amount = money(d(subtotal_before_rates) * d(data.logistics_and_supply_rate))
    consumables_amount = money(
        d(subtotal_before_rates) * d(data.consumables_tool_amortization_rate)
    )
    lines.extend(
        [
            EstimateLine("logistics_and_supply", "Логистика, снабжение", "-", 1, material_unit_price=logistics_amount),
            EstimateLine("consumables_tool_amortization", "Расходники, амортизация инструмента", "-", 1, material_unit_price=consumables_amount),
            EstimateLine("technical_supervision", "Технический надзор", "-", 1, work_unit_price=data.technical_supervision_amount),
            EstimateLine("procurement_storage_zero", "Заготовительно-складские расходы", "-", 1),
            EstimateLine("overhead_zero", "Накладные и общехозяйственные расходы", "-", 1),
            EstimateLine("profit_zero", "Сметная прибыль", "-", 1),
        ]
    )

    line_dicts = [line.to_dict() for line in lines]
    material_total = sum(item["material_total"] for item in line_dicts)
    work_total = sum(item["work_total"] for item in line_dicts)
    return {
        "inputs": asdict(data),
        "calculation_blocks": {
            "elements": {
                "included": [asdict(item) for item in elements],
                "excluded_count": len(data.grillage_elements) - len(elements),
            },
            "quantities": {
                "membrane_area_m2": membrane_area,
                "inventory_formwork_area_m2": inventory_formwork_area,
                "timber_formwork_area_m2": timber_formwork_area,
                "dismantling_area_m2": dismantling_area,
                "concrete_project_volume_m3": concrete_volume,
                "horizontal_insulation_area_m2": eps_area,
                "horizontal_insulation_volume_m3": eps_volume,
            },
            "planter_purchase": {
                "basis": planter_basis,
                "purchase_area_m2": purchase_area,
                "required_area_m2": membrane_required_area,
                "rolls": membrane_rolls,
                "planterband_quantity": planterband_quantity,
            },
            "formwork": {
                "transport_trips": formwork_transport_trips,
                "crane_shifts": crane_shifts,
                "plywood_sheets": plywood_sheets,
                "timber_order_volume_m3": timber_volume,
            },
            "rebar": rebar,
            "concrete": {
                "required_volume_m3": concrete_required,
                "order_volume_m3": concrete_order,
                "delivery_trips": concrete_delivery_trips,
            },
            "horizontal_insulation": {
                "required_volume_m3": eps_required,
                "packs": eps_packs,
                "order_volume_m3": eps_order,
            },
            "rate_base": {
                "subtotal_before_rates": subtotal_before_rates,
                "logistics_amount": logistics_amount,
                "consumables_amount": consumables_amount,
            },
        },
        "warnings": (
            ["PLANTER purchase is a grillage-only preview; final slab+grillage pooling is required."]
            if planter_basis == "grillage_only_preview" and membrane_area > 0
            else []
        ),
        "estimate_lines": line_dicts,
        "internal_totals": {
            "materials_total": material_total,
            "works_total": work_total,
            "section_total": material_total + work_total,
        },
    }
