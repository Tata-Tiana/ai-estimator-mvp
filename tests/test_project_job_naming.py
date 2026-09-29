from __future__ import annotations

import importlib.util
from datetime import datetime
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "earthworks_review_to_calculator"
    / "project_job_naming.py"
)
SPEC = importlib.util.spec_from_file_location("project_job_naming", MODULE_PATH)
assert SPEC and SPEC.loader
project_job_naming = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(project_job_naming)


def test_project_label_comes_from_common_trc_filename_token() -> None:
    extraction = {
        "project_name": "Длинный адрес объекта",
        "source_files": [
            "КР-1_ТРЦ _01,07,2026(11).pdf",
            "КР2_ТРЦ_30,07,2026(6).pdf",
        ],
    }

    assert project_job_naming.project_label_from_extraction(extraction) == "ТРЦ"


def test_project_label_comes_from_common_ark_filename_token() -> None:
    extraction = {
        "source_files": [
            "АРК КР1 для ИИ(10).pdf",
            "АРК КР2 для ИИ(11).pdf",
        ],
    }

    assert project_job_naming.project_label_from_extraction(extraction) == "АРК"


def test_drive_folder_contains_project_name_and_job_date() -> None:
    created_at = datetime(2026, 9, 29, 18, 30)

    assert (
        project_job_naming.project_drive_folder_name("ТРЦ", created_at)
        == "ТРЦ — 29.09.2026"
    )
    assert (
        project_job_naming.review_sheet_title("ТРЦ", created_at)
        == "Проверка — ТРЦ — 29.09.2026"
    )
