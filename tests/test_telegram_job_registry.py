from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = REPO_ROOT / "experiments" / "earthworks_review_to_calculator"
MODULE_PATH = MODULE_DIR / "telegram_bot.py"

os.environ["TELEGRAM_BOT_TOKEN"] = "123456:TEST_TOKEN"
for key in (
    "TELEGRAM_PROXY_SCHEME",
    "TELEGRAM_PROXY_HOST",
    "TELEGRAM_PROXY_PORT",
    "TELEGRAM_PROXY_USERNAME",
    "TELEGRAM_PROXY_PASSWORD",
):
    os.environ.pop(key, None)
sys.path.insert(0, str(MODULE_DIR))

SPEC = importlib.util.spec_from_file_location("telegram_bot_job_registry", MODULE_PATH)
assert SPEC and SPEC.loader
telegram_bot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(telegram_bot)


def test_update_user_job_url_creates_missing_registry(monkeypatch, tmp_path: Path) -> None:
    registry_dir = tmp_path / "telegram_user_jobs"
    monkeypatch.setattr(telegram_bot, "USER_JOBS_DIR", registry_dir)

    telegram_bot._update_user_job_url(
        42,
        "ark_20260930_143041",
        "https://docs.google.test/ark",
        drive_folder_id="folder-1",
        drive_folder_name="АРК — 06.10.2026",
        drive_folder_url="https://drive.google.test/folder-1",
        project_name="АРК",
    )

    payload = json.loads((registry_dir / "42.json").read_text(encoding="utf-8"))
    assert payload["chat_id"] == 42
    assert payload["jobs"][0]["job_id"] == "ark_20260930_143041"
    assert payload["jobs"][0]["spreadsheet_url"] == "https://docs.google.test/ark"
    assert payload["jobs"][0]["project_name"] == "АРК"


def test_sheet_metadata_repairs_registry(monkeypatch, tmp_path: Path) -> None:
    registry_dir = tmp_path / "telegram_user_jobs"
    job_dir = tmp_path / "ark_20260930_143041"
    job_dir.mkdir()
    monkeypatch.setattr(telegram_bot, "USER_JOBS_DIR", registry_dir)

    telegram_bot._save_json_job_sheet_metadata(
        job_dir,
        chat_id=42,
        job_id=job_dir.name,
        project_name="АРК",
        spreadsheet_url="https://docs.google.test/ark",
        drive_folder_id="folder-1",
        drive_folder_name="АРК — 06.10.2026",
        drive_folder_url="https://drive.google.test/folder-1",
    )

    result = telegram_bot._json_flow_job_spreadsheet_url(42, job_dir.name, job_dir)

    assert result == "https://docs.google.test/ark"
    repaired = json.loads((registry_dir / "42.json").read_text(encoding="utf-8"))
    assert repaired["jobs"][0]["spreadsheet_url"] == result


def test_job_metadata_restores_owner_access(monkeypatch, tmp_path: Path) -> None:
    registry_dir = tmp_path / "telegram_user_jobs"
    outputs_dir = tmp_path / "outputs"
    job_dir = outputs_dir / "ark_20260930_143041"
    job_dir.mkdir(parents=True)
    monkeypatch.setattr(telegram_bot, "USER_JOBS_DIR", registry_dir)
    monkeypatch.setattr(telegram_bot, "CHAT_EXTRACTION_OUTPUTS_DIR", outputs_dir)
    monkeypatch.setattr(telegram_bot, "ADMIN_CHAT_IDS", set())
    telegram_bot._save_json_job_sheet_metadata(
        job_dir,
        chat_id=42,
        job_id=job_dir.name,
        project_name="АРК",
        spreadsheet_url="https://docs.google.test/ark",
    )

    assert telegram_bot._user_can_access_job(42, job_dir.name) is True
    assert telegram_bot._user_can_access_job(43, job_dir.name) is False


def test_log_entry_is_readable_and_uses_moscow_time() -> None:
    entry = {
        "timestamp": "2026-10-07T11:40:39",
        "level": "ERROR",
        "event": "build_failed",
        "job_id": "ark_20260930_143041",
        "reason": "spreadsheet_url_missing",
    }

    assert telegram_bot._format_event_entry(entry) == (
        "07.10 14:40 ОШИБКА Смета не собрана "
        "job=ark_20260930_143041 — у job не сохранена ссылка на Google-таблицу"
    )
