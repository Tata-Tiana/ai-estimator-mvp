from __future__ import annotations

from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[1]
DATA_DIR = EXPERIMENT_DIR / "data"

V3_DIR = REPO_ROOT / "experiments" / "usv_strict_pdf_parser_v3"
V3_EARTHWORKS_PATH = V3_DIR / "data" / "extracted" / "earthworks.json"
V3_CANDIDATES_PATH = V3_DIR / "data" / "extracted" / "candidates.json"
V3_DRAFT_PATH = V3_DIR / "data" / "mapped" / "final_project_parameters_draft.json"
V3_PAGES_TEXT_PATH = V3_DIR / "data" / "raw" / "pages_text.json"
V3_LOGICAL_PAGES_PATH = V3_DIR / "data" / "raw" / "logical_pages.json"
V3_TABLES_PATH = V3_DIR / "data" / "raw" / "tables.json"
V3_DEBUG_REPORT_PATH = V3_DIR / "data" / "reports" / "parser_debug_report.md"

PRICE_REGISTRY_PATH = REPO_ROOT / "output" / "price_registry_filled_v3.xlsx"
FALLBACK_LIVE_INPUT_PATH = (
    REPO_ROOT
    / "experiments"
    / "earthworks_calculator"
    / "cases"
    / "usv_yusupovo_village_live_prices"
    / "input.json"
)

EXTRACTED_DIR = DATA_DIR / "extracted"
REVIEW_DIR = DATA_DIR / "review"
MAPPED_DIR = DATA_DIR / "mapped"
CALCULATED_DIR = DATA_DIR / "calculated"
REPORTS_DIR = DATA_DIR / "reports"
EXCEL_DIR = DATA_DIR / "excel"

EXTRACTED_PARAMETERS_PATH = EXTRACTED_DIR / "earthworks_extracted_parameters.json"
REVIEW_TABLE_PATH = REVIEW_DIR / "earthworks_parameter_review.xlsx"
REVIEW_HINTS_PATH = REVIEW_DIR / "earthworks_review_hints.xlsx"
POC_INPUT_PATH = MAPPED_DIR / "earthworks_input_poc.json"
REVIEW_INPUT_PATH = MAPPED_DIR / "earthworks_input_from_review.json"
CALC_RESULT_JSON_PATH = CALCULATED_DIR / "earthworks_result_poc.json"
CALC_RESULT_MD_PATH = CALCULATED_DIR / "earthworks_result_poc.md"
REVIEW_RESULT_JSON_PATH = CALCULATED_DIR / "earthworks_result_from_review.json"
REVIEW_RESULT_MD_PATH = CALCULATED_DIR / "earthworks_result_from_review.md"
FINAL_EXCEL_PATH = EXCEL_DIR / "earthworks_mini_mvp_poc.xlsx"
REVIEW_FINAL_EXCEL_PATH = EXCEL_DIR / "earthworks_final_from_review.xlsx"
MINI_MVP_REPORT_PATH = REPORTS_DIR / "mini_mvp_report.md"
PREPARE_REPORT_PATH = REPORTS_DIR / "prepare_report.md"
VALIDATION_REPORT_PATH = REPORTS_DIR / "review_validation_report.md"
CALCULATE_BLOCKED_REPORT_PATH = REPORTS_DIR / "calculate_blocked_report.md"
CALCULATE_REPORT_PATH = REPORTS_DIR / "calculate_report.md"
INTEGRITY_REPORT_PATH = REPORTS_DIR / "integrity_report.md"
OPERATOR_LOG_PATH = REPORTS_DIR / "operator_log.json"
