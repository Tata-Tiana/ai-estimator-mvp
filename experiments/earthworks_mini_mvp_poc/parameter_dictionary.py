from __future__ import annotations


SOURCE_STATUS_RU = {
    "AUTO_PROJECT": "Из проекта / PDF",
    "AUTO_CALCULATED": "Рассчитано автоматически",
    "DEFAULT_VALUE": "Стандартное значение",
    "MATERIAL_CATALOG": "Каталог материала",
    "PRICE_DATABASE": "Цена / прайс",
    "SUPPLIER_INPUT": "Данные поставщика",
    "MANUAL_REQUIRED": "Ручной ввод",
    "OPTIONAL_CONTROL": "Контрольное значение",
    "DEPRECATED / LEGACY_ONLY": "Legacy, не использовать",
}


def _entry(
    ru_label: str,
    project_wording: str,
    source_status: str,
    used_in: str,
    visible_to_elena: bool,
    needs_review: bool,
) -> dict[str, object]:
    return {
        "ru_label": ru_label,
        "project_wording": project_wording,
        "source_group_ru": SOURCE_STATUS_RU[source_status],
        "source_status": source_status,
        "used_in": used_in,
        "visible_to_elena": visible_to_elena,
        "needs_review": needs_review,
    }


EARTHWORKS_PARAMETER_DICTIONARY = {
    "pit_area_m2": _entry(
        "Площадь котлована",
        "Площадь котлована / Площадь ктлована",
        "AUTO_PROJECT",
        "Расчет машинной разработки, ручной доработки дна котлована и смен экскаватора",
        True,
        True,
    ),
    "pit_excavation_depth_m": _entry(
        "Глубина котлована",
        "Глубина котлована - ... мм",
        "AUTO_PROJECT",
        "Расчет машинной разработки грунта и смен экскаватора",
        True,
        True,
    ),
    "sand_base_volume_m3": _entry(
        "Объем песка под основание",
        "Песок (300 мм) Купл=... ... м3",
        "AUTO_PROJECT",
        "Расчет общего песка с коэффициентом уплотнения и округлением к заказу",
        True,
        True,
    ),
    "trench_routes": _entry(
        "Трассы траншей",
        "Таблица К1 / К2 / Вода / Эл. кабель",
        "AUTO_PROJECT",
        "Контроль и расчет объема траншей, если итоговый объем не дан",
        True,
        True,
    ),
    "trench_volume_m3": _entry(
        "Объем траншей",
        "Итого в строке м3 таблицы траншей",
        "AUTO_PROJECT",
        "Расчет ручной разработки и песка для траншей",
        True,
        True,
    ),
    "communications_pipe_items": _entry(
        "Трубы коммуникаций",
        "Труба 1 м. ф110 / Труба ф110 гофрированная",
        "AUTO_PROJECT",
        "Расчет длины коммуникаций из состава труб",
        True,
        True,
    ),
    "communications_length_m": _entry(
        "Длина коммуникаций",
        "Сумма длин труб коммуникаций",
        "AUTO_CALCULATED",
        "Количество для строк работ и материалов коммуникаций",
        False,
        False,
    ),
    "geotextile_area_m2": _entry(
        "Площадь геотекстиля по проекту",
        "Геотекстиль ... м2",
        "AUTO_PROJECT",
        "Расчет геотекстиля с нахлестом и округлением до рулонов",
        True,
        True,
    ),
    "geotextile_laying_area_m2": _entry(
        "Площадь укладки геотекстиля",
        "Площадь укладки геотекстиля",
        "AUTO_PROJECT",
        "Количество работ по укладке геотекстиля",
        True,
        True,
    ),
    "manual_refinement_depth_m": _entry(
        "Глубина ручной доработки",
        "Стандартное правило 0.08 м",
        "DEFAULT_VALUE",
        "Расчет ручной доработки дна котлована",
        False,
        False,
    ),
    "trench_width_m": _entry(
        "Ширина траншей по умолчанию",
        "Стандартное значение 0.4 м",
        "DEFAULT_VALUE",
        "Fallback для расчета траншей по маршрутам",
        False,
        False,
    ),
    "sand_compaction_coeff": _entry(
        "Коэффициент уплотнения песка",
        "Стандартное правило",
        "DEFAULT_VALUE",
        "Расчет закупочного объема песка",
        False,
        False,
    ),
    "sand_truck_step_m3": _entry(
        "Шаг заказа песка машиной",
        "Стандартное правило 20 м3",
        "DEFAULT_VALUE",
        "Округление заказа песка",
        False,
        False,
    ),
    "geotextile_overlap_coeff": _entry(
        "Коэффициент нахлеста геотекстиля",
        "Стандартное правило",
        "DEFAULT_VALUE",
        "Расчет площади геотекстиля с нахлестом",
        False,
        False,
    ),
    "geotextile_roll_area_m2": _entry(
        "Площадь рулона геотекстиля",
        "Каталожная площадь рулона",
        "MATERIAL_CATALOG",
        "Округление геотекстиля до рулонов",
        False,
        False,
    ),
    "excavator_productivity_m3_per_shift": _entry(
        "Производительность экскаватора",
        "Стандартное правило 80 м3/смена",
        "DEFAULT_VALUE",
        "Расчет смен экскаватора",
        False,
        False,
    ),
    "axis_marking_shifts": _entry(
        "Смены выноса осей",
        "Стандартное правило",
        "DEFAULT_VALUE",
        "Строка выноса осей",
        False,
        False,
    ),
    "consumables_amount": _entry(
        "Расходные материалы",
        "POC default",
        "DEFAULT_VALUE",
        "Строка расходных материалов",
        False,
        False,
    ),
    "manual_required_smoke_test": _entry(
        "Тестовый ручной параметр для проверки процесса",
        "Заполняется вручную только для проверки gate",
        "MANUAL_REQUIRED",
        "Не передается в калькулятор; нужен только для проверки, что calculate блокируется без ручного ввода",
        True,
        True,
    ),
}


def parameter_meta(key: str) -> dict[str, object]:
    return EARTHWORKS_PARAMETER_DICTIONARY[key]
