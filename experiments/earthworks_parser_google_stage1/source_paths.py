from __future__ import annotations

from pathlib import Path

from config import DATA_DIR, REPO_ROOT


V3_DIR = REPO_ROOT / "experiments" / "usv_strict_pdf_parser_v3"
V3_EARTHWORKS_PATH = V3_DIR / "data" / "extracted" / "earthworks.json"
V3_CANDIDATES_PATH = V3_DIR / "data" / "extracted" / "candidates.json"
V3_LOGICAL_PAGES_PATH = V3_DIR / "data" / "raw" / "logical_pages.json"
V3_TABLES_PATH = V3_DIR / "data" / "raw" / "tables.json"
V3_EVIDENCE_PATH = V3_DIR / "data" / "extracted" / "evidence.json"
V3_GENERIC_CANDIDATES_PATH = V3_DIR / "data" / "extracted" / "generic_candidates.json"

LOCAL_PRICE_REGISTRY_PATH = REPO_ROOT / "output" / "price_registry_filled_v3.xlsx"
FALLBACK_LIVE_INPUT_PATH = (
    REPO_ROOT
    / "experiments"
    / "earthworks_calculator"
    / "cases"
    / "usv_yusupovo_village_live_prices"
    / "input.json"
)


def job_dir(job_id: str) -> Path:
    return DATA_DIR / "jobs" / job_id
