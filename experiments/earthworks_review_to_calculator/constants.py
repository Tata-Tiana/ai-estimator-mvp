from __future__ import annotations

from pathlib import Path


SECTION_CODE = "earthworks"
SECTION_NAME_RU = "Земляные работы"

STAGE1_DIR = Path("experiments/earthworks_parser_google_stage1")
DEFAULT_WORKBOOK_PATH = STAGE1_DIR / "review_workbook.xlsx"
STAGE1_JOBS_DIR = STAGE1_DIR / "data" / "jobs"

OUTPUT_DIR = Path("experiments/earthworks_review_to_calculator/outputs")
NORMALIZED_JSON_FILENAME = "review_values_normalized.json"
REPORT_MD_FILENAME = "review_reader_report.md"

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

DETAIL_REQUIRED_TRENCH_NAMES = ["К 1", "К 2", "Вода", "Эл. кабель"]
DETAIL_REQUIRED_COMM_NAMES = [
    "ГОСТ 32412-2013 Труба 2 м. ф110 (рыжая) 7 шт",
    "ГОСТ 32412-2013 Труба 1 м. ф110 (рыжая) 12 шт",
    "ГОСТ 32412-2013 Труба 3 м. ф110 (рыжая) 18 шт",
    "ГОСТ 32412-2013 Труба ф110 гофрированная 35 м/п",
]

