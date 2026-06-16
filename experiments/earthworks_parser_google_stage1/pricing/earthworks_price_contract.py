from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EarthworksPriceComponent:
    component_code: str
    estimate_line_code: str
    estimate_line_name_ru: str
    price_kind_ru: str
    unit: str
    internal_price_key: str
    price_registry_codes: list[str]
    fallback_allowed: bool
    required_for_calculation: bool
    comment_ru: str

    def to_dict(self) -> dict:
        return asdict(self)


EARTHWORKS_PRICE_COMPONENTS: tuple[EarthworksPriceComponent, ...] = (
    EarthworksPriceComponent(
        component_code="axis_marking_work",
        estimate_line_code="axis_marking",
        estimate_line_name_ru="Вынос осей",
        price_kind_ru="Работа",
        unit="смена",
        internal_price_key="axis_marking_work_unit_price",
        price_registry_codes=[],
        fallback_allowed=True,
        required_for_calculation=True,
        comment_ru="",
    ),
    EarthworksPriceComponent(
        component_code="excavator_jcb_machine",
        estimate_line_code="excavator_jcb",
        estimate_line_name_ru="Экскаватор JCB",
        price_kind_ru="Аренда/механизм",
        unit="смена",
        internal_price_key="excavator_material_unit_price",
        price_registry_codes=[],
        fallback_allowed=True,
        required_for_calculation=True,
        comment_ru="",
    ),
    EarthworksPriceComponent(
        component_code="excavator_jcb_work",
        estimate_line_code="excavator_jcb",
        estimate_line_name_ru="Экскаватор JCB",
        price_kind_ru="Работа оператора/бригады",
        unit="смена",
        internal_price_key="excavator_work_unit_price",
        price_registry_codes=[],
        fallback_allowed=True,
        required_for_calculation=True,
        comment_ru="",
    ),
    EarthworksPriceComponent(
        component_code="manual_excavation_work",
        estimate_line_code="manual_excavation",
        estimate_line_name_ru="Разработка грунта вручную",
        price_kind_ru="Работа",
        unit="м3",
        internal_price_key="manual_excavation_work_unit_price",
        price_registry_codes=[],
        fallback_allowed=True,
        required_for_calculation=True,
        comment_ru="",
    ),
    EarthworksPriceComponent(
        component_code="geotextile_laying_work",
        estimate_line_code="geotextile_laying",
        estimate_line_name_ru="Укладка геотекстиля",
        price_kind_ru="Работа",
        unit="м2",
        internal_price_key="geotextile_laying_work_unit_price",
        price_registry_codes=[],
        fallback_allowed=True,
        required_for_calculation=True,
        comment_ru="",
    ),
    EarthworksPriceComponent(
        component_code="geotextile_dornit_material",
        estimate_line_code="geotextile_material",
        estimate_line_name_ru="Геотекстиль Дорнит 300 г.м2",
        price_kind_ru="Материал",
        unit="м2",
        internal_price_key="geotextile_material_unit_price",
        price_registry_codes=["geotextile_dornit_300_m2"],
        fallback_allowed=True,
        required_for_calculation=True,
        comment_ru="Цена приведена к единице калькулятора: м2; ранее в прайсе была строка за рулон.",
    ),
    EarthworksPriceComponent(
        component_code="sand_filling_work",
        estimate_line_code="sand_filling",
        estimate_line_name_ru="Отсыпка песком с трамбованием",
        price_kind_ru="Работа",
        unit="м3",
        internal_price_key="sand_filling_work_unit_price",
        price_registry_codes=[],
        fallback_allowed=True,
        required_for_calculation=True,
        comment_ru="",
    ),
    EarthworksPriceComponent(
        component_code="sand_material",
        estimate_line_code="sand_material",
        estimate_line_name_ru="Песок строительный",
        price_kind_ru="Материал",
        unit="м3",
        internal_price_key="sand_material_unit_price",
        price_registry_codes=[],
        fallback_allowed=True,
        required_for_calculation=True,
        comment_ru="",
    ),
    EarthworksPriceComponent(
        component_code="sand_manual_moving_work",
        estimate_line_code="sand_manual_moving",
        estimate_line_name_ru="Перемещение песка вручную",
        price_kind_ru="Работа",
        unit="м3",
        internal_price_key="sand_manual_moving_work_unit_price",
        price_registry_codes=[],
        fallback_allowed=True,
        required_for_calculation=False,
        comment_ru="",
    ),
    EarthworksPriceComponent(
        component_code="communications_work",
        estimate_line_code="communications_work",
        estimate_line_name_ru="Технологические вводы коммуникаций",
        price_kind_ru="Работа",
        unit="мп",
        internal_price_key="communications_work_unit_price",
        price_registry_codes=[],
        fallback_allowed=True,
        required_for_calculation=True,
        comment_ru="",
    ),
    EarthworksPriceComponent(
        component_code="communications_material",
        estimate_line_code="communications_material",
        estimate_line_name_ru="Материалы для вводов коммуникаций",
        price_kind_ru="Материал",
        unit="мп",
        internal_price_key="communications_material_unit_price",
        price_registry_codes=[],
        fallback_allowed=True,
        required_for_calculation=True,
        comment_ru="",
    ),
    EarthworksPriceComponent(
        component_code="consumables_fixed",
        estimate_line_code="consumables",
        estimate_line_name_ru="Расходные материалы",
        price_kind_ru="Фиксированная сумма",
        unit="комплект",
        internal_price_key="consumables_amount",
        price_registry_codes=[],
        fallback_allowed=True,
        required_for_calculation=True,
        comment_ru="",
    ),
)


ABSENT_STRUCTURAL_COMPONENTS = {
    "geotextile_material_work_unit_price": "Компонент отсутствует по сметной логике: Геотекстиль Дорнит является material-only строкой.",
}


def contract_as_dicts() -> list[dict]:
    return [component.to_dict() for component in EARTHWORKS_PRICE_COMPONENTS]
