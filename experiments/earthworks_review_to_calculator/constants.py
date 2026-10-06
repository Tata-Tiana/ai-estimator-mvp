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

DEFAULT_EXCAVATOR_SHIFTS_METHOD = "standard_volume_productivity"
DEFAULT_MANUAL_EXCAVATION_METHOD = "standard_routes"
DEFAULT_COMMUNICATIONS_METHOD = "pipe_items"

HUMAN_REVIEW_STATUS_VALUES = {"unknown", "pending", "reviewed"}

GENERIC_CALCULATOR_DEFAULTS = {
    "case_meta": {
        "review_source": "review_workbook",
        "human_review_status": "unknown",
        "confidence": "from_review_layer",
    },
    "assumptions": {
        "manual_excavation_override": False,
        "sand_override": False,
        "geotextile_override": False,
    },
    "excavator_shifts_calc_method": "standard_volume_productivity",
    "manual_excavation_calc_method": "standard_routes",
    "communications_length_calc_method": "pipe_items",
    "excavator_productivity_m3_per_shift": 80.0,
    "manual_refinement_depth_m": 0.08,
    "trench_width_m": 0.4,
    "sand_compaction_coeff": 1.3,
    "sand_truck_step_m3": 20.0,
    "geotextile_overlap_coeff": 1.10,
    "geotextile_roll_area_m2": 100.0,
    "axis_marking_shifts": 1.0,
    "consumables_calc_method": "section_total_rate",
    "consumables_rate": 0.03,
    "enabled_lines": None,
    "quantity_overrides": {},
    "line_name_overrides": {},
}

REQUIRED_CALC_PRICE_KEYS = [
    "axis_marking_work_unit_price",
    "excavator_material_unit_price",
    "excavator_work_unit_price",
    "manual_excavation_work_unit_price",
    "geotextile_laying_work_unit_price",
    "geotextile_material_unit_price",
    "sand_filling_work_unit_price",
    "sand_material_unit_price",
    "sand_manual_moving_work_unit_price",
    "communications_work_unit_price",
    "communications_material_unit_price",
]
