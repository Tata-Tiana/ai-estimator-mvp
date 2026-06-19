from __future__ import annotations

from pathlib import Path


SECTION_CODE = "earthworks"
SECTION_NAME_RU = "Земляные работы"
PROJECT_NAME = "earthworks_review"

STAGE1_DIR = Path("experiments/earthworks_parser_google_stage1")
DEFAULT_WORKBOOK_PATH = STAGE1_DIR / "review_workbook.xlsx"
STAGE1_JOBS_DIR = STAGE1_DIR / "data" / "jobs"

OUTPUT_DIR = Path("experiments/earthworks_review_to_calculator/outputs")
NORMALIZED_JSON_FILENAME = "review_values_normalized.json"
REPORT_MD_FILENAME = "review_reader_report.md"
CALCULATOR_INPUT_FILENAME = "earthworks_calculation_input.json"
CALCULATOR_INPUT_REPORT_FILENAME = "calculator_input_report.md"
CALCULATOR_TEMPLATE_PATH = Path(
    "experiments/earthworks_calculator/cases/usv_yusupovo_village/input.json"
)

SHEET_01_NAME = "01_Проверка проекта"
SHEET_02_NAME = "02_Цены себестоимости"
SHEET_03_NAME = "03_Детали объемов"

REQUIRED_PARAMETERS = [
    "pit_area_m2",
    "pit_excavation_depth_m",
    "sand_base_volume_m3",
    "trench_volume_m3",
    "geotextile_area_m2",
    "geotextile_laying_area_m2",
    "communications_length_m",
]

PRICE_EXPECTED_MIN_ROWS = 12
PRICE_REQUIRED_LINES = [
    "Расходные материалы",
    "Геотекстиль Дорнит 300 г.м2",
]

PRICE_TO_INTERNAL_KEY_MAP: dict[tuple[str, str], str] = {
    ("Вынос осей", "Работа"): "axis_marking_work_unit_price",
    ("Экскаватор JCB", "Аренда/механизм"): "excavator_material_unit_price",
    ("Экскаватор JCB", "Работа оператора/бригады"): "excavator_work_unit_price",
    ("Разработка грунта вручную", "Работа"): "manual_excavation_work_unit_price",
    ("Укладка геотекстиля", "Работа"): "geotextile_laying_work_unit_price",
    ("Геотекстиль Дорнит 300 г.м2", "Материал"): "geotextile_material_unit_price",
    ("Отсыпка песком с трамбованием", "Работа"): "sand_filling_work_unit_price",
    ("Песок строительный", "Материал"): "sand_material_unit_price",
    ("Перемещение песка вручную", "Работа"): "sand_manual_moving_work_unit_price",
    ("Технологические вводы коммуникаций", "Работа"): "communications_work_unit_price",
    ("Материалы для вводов коммуникаций", "Материал"): "communications_material_unit_price",
}
CONSUMABLES_PRICE_KEY = ("Расходные материалы", "Фиксированная сумма")

DEFAULT_EXCAVATOR_SHIFTS_METHOD = "standard_volume_productivity"
DEFAULT_MANUAL_EXCAVATION_METHOD = "standard_routes"
DEFAULT_COMMUNICATIONS_METHOD = "pipe_items"

DETAIL_REQUIRED_TRENCH_NAMES = ["К 1", "К 2", "Вода", "Эл. кабель"]
DETAIL_REQUIRED_COMM_NAMES = [
    "ГОСТ 32412-2013 Труба 2 м. ф110 (рыжая) 7 шт",
    "ГОСТ 32412-2013 Труба 1 м. ф110 (рыжая) 12 шт",
    "ГОСТ 32412-2013 Труба 3 м. ф110 (рыжая) 18 шт",
    "ГОСТ 32412-2013 Труба ф110 гофрированная 35 м/п",
]
