from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
    _HAS_DOTENV = True
except ImportError:
    _HAS_DOTENV = False

import telebot
from telebot import apihelper

# ── paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
sys.path.insert(0, str(BASE_DIR))
from project_job_naming import project_drive_folder_name, project_label_from_extraction, review_sheet_title
from telegram_proxy import configure_telegram_proxy

if _HAS_DOTENV:
    load_dotenv(REPO_ROOT / ".env")

DATA_DIR     = BASE_DIR / "data"
UPLOADS_DIR  = DATA_DIR / "telegram_uploads"
LOGS_DIR     = DATA_DIR / "telegram_logs"
SESSIONS_DIR = DATA_DIR / "telegram_sessions"
EVENTS_DIR   = LOGS_DIR / "events"
SESSION_BACKUPS_DIR = BASE_DIR / "backups" / "telegram_sessions"
ADMIN_EXPORTS_DIR   = DATA_DIR / "admin_exports"
USER_JOBS_DIR       = DATA_DIR / "telegram_user_jobs"
EXTRACTION_SESSIONS_DIR = DATA_DIR / "telegram_extraction_sessions"

for _d in (UPLOADS_DIR, LOGS_DIR, SESSIONS_DIR, EVENTS_DIR, SESSION_BACKUPS_DIR, ADMIN_EXPORTS_DIR, USER_JOBS_DIR, EXTRACTION_SESSIONS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

CREATE_JOB  = BASE_DIR / "create_job_from_pdf.py"
RECREATE    = BASE_DIR / "recreate_review_sheet.py"
RERUN       = BASE_DIR / "rerun_parser.py"
BUILD_JOB   = BASE_DIR / "build_job.py"
SHOW_STATUS = BASE_DIR / "show_job_status.py"

# ── новый (2026-08-25) JSON-приёмник: extraction JSON от внешнего ChatGPT-чата,
# отдельный от старого PDF/session-flow выше — repetition plan, фаза 1-4.
FULL_PIPELINE_DIR = REPO_ROOT / "experiments" / "full_estimate_review_pipeline"
CHAT_EXTRACTION_OUTPUTS_DIR = REPO_ROOT / "experiments" / "chat_extraction_poc" / "outputs"
NOTES_REPORT_SCRIPT = FULL_PIPELINE_DIR / "build_extraction_notes_report.py"
POPULATE_WORKBOOK_SCRIPT = FULL_PIPELINE_DIR / "populate_review_workbook_from_extraction.py"
# 2026-08-26: the JSON-flow's final-build step. build_job.py/build_from_google_sheet.py (used by
# the PDF-flow's /build below) are the OLD single-section earthworks-only pipeline - hardcoded row
# positions, hardcoded old job layout - and structurally cannot run the new 7-section review
# workbook. These two are the actual new-pipeline equivalent (see build_all_section_results.py's
# own docstring for why it exists as a separate driver).
BUILD_ALL_SECTIONS_SCRIPT = FULL_PIPELINE_DIR / "build_all_section_results.py"
EXPORT_ESTIMATE_SCRIPT = FULL_PIPELINE_DIR / "export_calculator_results_to_estimate_workbook.py"
EXTRACTION_SESSION_MAX_AGE_HOURS = 2  # после этого новый JSON от того же чата считается новым проектом

GOOGLE_STAGE1_DIR = REPO_ROOT / "experiments" / "earthworks_parser_google_stage1"
GOOGLE_SHEET_SHARING = "anyone_writer"  # тот же режим, что уже используется в остальном боте

TIMEOUTS = {
    "create_job":        1200,
    "rerun":             1200,
    "recreate":           600,
    "build":              600,
    "status":             120,
    "notes_report":       120,
    "populate_workbook":  300,
    "publish_sheet":      120,
    "download_sheet":     120,
    "build_all_sections": 300,
    "export_estimate":    180,
}

# Seconds of silence after last PDF before parser fires
QUIET_SECONDS = 5
DONE_REQUESTED_TIMEOUT_MINUTES = 15
QUEUED_TIMEOUT_MINUTES = 15
PROCESSING_TIMEOUT_MINUTES = 60

SESSION_STATUSES = {
    "collecting",
    "done_requested",
    "queued",
    "processing",
    "completed",
    "failed",
    "stale",
    "cancelled",
}

# ── config ─────────────────────────────────────────────────────────────────
BOT_STARTED_AT: datetime = datetime.now()

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN is not set.", file=sys.stderr)
    sys.exit(1)

def _parse_chat_ids(raw: str) -> set[int]:
    ids: set[int] = set()
    for item in raw.split(","):
        value = item.strip()
        if not value:
            continue
        try:
            ids.add(int(value))
        except ValueError:
            print(f"WARNING: ignored invalid chat id: {value}", file=sys.stderr)
    return ids


_raw_ids = os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "")
ALLOWED_CHAT_IDS: set[int] = _parse_chat_ids(_raw_ids)
_raw_admin_ids = os.environ.get("TELEGRAM_ADMIN_CHAT_IDS", "")
ADMIN_CHAT_IDS: set[int] = _parse_chat_ids(_raw_admin_ids)
ALLOW_ALL_USERS = os.environ.get("ALLOW_ALL_USERS", "").strip().lower() in ("true", "1", "yes")

try:
    TELEGRAM_PROXY_ENABLED = configure_telegram_proxy(apihelper)
except ValueError as exc:
    print(f"ERROR: invalid Telegram proxy configuration: {exc}", file=sys.stderr)
    sys.exit(1)

bot = telebot.TeleBot(TOKEN, parse_mode=None)


# ── per-chat locks ─────────────────────────────────────────────────────────
# Protects the SESSION_LOCKS dict itself
_LOCKS_MUTEX: threading.Lock = threading.Lock()
SESSION_LOCKS: dict[int, threading.Lock] = {}
_EVENT_LOG_LOCK: threading.Lock = threading.Lock()


def get_chat_lock(chat_id: int) -> threading.Lock:
    with _LOCKS_MUTEX:
        if chat_id not in SESSION_LOCKS:
            SESSION_LOCKS[chat_id] = threading.Lock()
        return SESSION_LOCKS[chat_id]


# ── session management ─────────────────────────────────────────────────────

def _session_path(chat_id: int) -> Path:
    return SESSIONS_DIR / f"{chat_id}.json"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _safe_filename_part(value: object) -> str:
    text = str(value or "unknown")
    return re.sub(r"[^0-9A-Za-zА-Яа-я_.-]+", "_", text, flags=re.UNICODE).strip("_") or "unknown"


def _new_session(chat_id: int) -> dict:
    now = _now()
    return {
        "chat_id": chat_id,
        "status": "collecting",
        "status_changed_at": now,
        "pdfs": [],
        "done_requested": False,
        "done_requested_at": None,
        "processing_started": False,
        "processing_started_at": None,
        "queued_at": None,
        "completed_at": None,
        "failed_at": None,
        "cancelled_at": None,
        "last_pdf_added_at": None,
        "updated_at": None,
        "last_error": None,
        "last_error_type": None,
        "job_id": None,
        "spreadsheet_url": None,
        "processing_run_id": None,
    }


def _normalize_session(chat_id: int, session: dict) -> dict:
    now = _now()
    session["chat_id"] = int(session.get("chat_id") or chat_id)
    session.setdefault("pdfs", [])

    status = session.get("status")
    if status not in SESSION_STATUSES:
        if session.get("processing_started"):
            status = "processing"
        elif session.get("done_requested"):
            status = "done_requested"
        else:
            status = "collecting"
        session["status"] = status

    session.setdefault("status_changed_at", session.get("updated_at") or session.get("created_at") or now)
    session.setdefault("done_requested", status in {"done_requested", "queued", "processing"})
    session.setdefault("done_requested_at", None)
    session.setdefault("queued_at", None)
    session.setdefault("processing_started", status == "processing")
    session.setdefault("processing_started_at", None)
    session.setdefault("completed_at", None)
    session.setdefault("failed_at", None)
    session.setdefault("cancelled_at", None)
    session.setdefault("last_pdf_added_at", None)
    session.setdefault("updated_at", None)
    session.setdefault("last_error", None)
    session.setdefault("last_error_type", None)
    session.setdefault("job_id", None)
    session.setdefault("spreadsheet_url", None)
    session.setdefault("processing_run_id", None)
    return session


def _redact_string(value: str) -> str:
    patterns = [
        r"TELEGRAM_BOT_TOKEN\s*=\s*[^\s]+",
        r"OPENAI_API_KEY\s*=\s*[^\s]+",
        r"ANTHROPIC_API_KEY\s*=\s*[^\s]+",
        r"Authorization:\s*Bearer\s+[A-Za-z0-9._~+/=-]+",
        r"Bearer\s+[A-Za-z0-9._~+/=-]+",
        r"-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----",
        r"BEGIN PRIVATE KEY",
        r"proxy password[:=]\s*[^\s]+",
    ]
    redacted = value
    for pattern in patterns:
        redacted = re.sub(pattern, "[REDACTED]", redacted, flags=re.IGNORECASE | re.DOTALL)
    return redacted


def _sanitize(value):
    if isinstance(value, str):
        return _redact_string(value)
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value


def _log_event(
    event: str,
    chat_id: int | None = None,
    session: dict | None = None,
    level: str = "INFO",
    safe_message: str = "",
    **payload,
) -> None:
    timestamp = _now()
    entry = {
        "timestamp": timestamp,
        "level": level,
        "event": event,
        "chat_id": chat_id if chat_id is not None else (session or {}).get("chat_id"),
        "session_id": (session or {}).get("session_id"),
        "job_id": (session or {}).get("job_id") or payload.pop("job_id", None),
        "processing_run_id": (session or {}).get("processing_run_id") or payload.pop("processing_run_id", None),
        "safe_message": safe_message,
    }
    entry.update(payload)
    path = EVENTS_DIR / f"{timestamp[:10]}.jsonl"
    with _EVENT_LOG_LOCK:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(_sanitize(entry), ensure_ascii=False, sort_keys=True) + "\n")


def _archive_session(chat_id: int, session: dict, reason: str) -> Path:
    session_id = _safe_filename_part(session.get("session_id") or "unknown")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = SESSION_BACKUPS_DIR / f"{chat_id}_{session_id}_{_safe_filename_part(reason)}_{timestamp}.json"
    backup_path.write_text(json.dumps(session, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _log_event(
        "session_archived",
        chat_id=chat_id,
        session=session,
        safe_message=f"Session archived as {reason}",
        reason=reason,
        backup_path=str(backup_path),
    )
    return backup_path


def _archive_corrupt_session(chat_id: int, path: Path, error: Exception) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = SESSION_BACKUPS_DIR / f"{chat_id}_unknown_corrupt_{timestamp}.json"
    path.replace(backup_path)
    _log_event(
        "session_corrupt_archived",
        chat_id=chat_id,
        level="ERROR",
        safe_message="Corrupt Telegram session archived",
        error=str(error),
        backup_path=str(backup_path),
    )


def _load_session(chat_id: int) -> dict:
    path = _session_path(chat_id)
    if path.exists():
        try:
            return _normalize_session(chat_id, json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:
            _archive_corrupt_session(chat_id, path, exc)
    return _new_session(chat_id)


def _save_session(chat_id: int, session: dict) -> None:
    session["updated_at"] = _now()
    path = _session_path(chat_id)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(session, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _clear_session(chat_id: int) -> None:
    p = _session_path(chat_id)
    if p.exists():
        p.unlink()


# ── user job registry ───────────────────────────────────────────────────────
_MAX_USER_JOBS = 20


def _user_jobs_path(chat_id: int) -> Path:
    return USER_JOBS_DIR / f"{chat_id}.json"


def _register_user_job(
    chat_id: int,
    job_id: str,
    project_name: str,
    spreadsheet_url: str,
    pdf_count: int,
    drive_folder_id: str = "",
    drive_folder_name: str = "",
    drive_folder_url: str = "",
) -> None:
    path = _user_jobs_path(chat_id)
    try:
        existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:
        existing = {}
    jobs: list[dict] = existing.get("jobs", [])
    jobs = [j for j in jobs if j.get("job_id") != job_id]
    jobs.insert(0, {
        "job_id": job_id,
        "project_name": project_name or "",
        "spreadsheet_url": spreadsheet_url or "",
        "drive_folder_id": drive_folder_id or "",
        "drive_folder_name": drive_folder_name or "",
        "drive_folder_url": drive_folder_url or "",
        "pdf_count": pdf_count,
        "created_at": _now(),
        "last_action_at": _now(),
    })
    jobs = jobs[:_MAX_USER_JOBS]
    payload = {"chat_id": chat_id, "jobs": jobs}
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _update_user_job_url(
    chat_id: int,
    job_id: str,
    spreadsheet_url: str,
    *,
    drive_folder_id: str = "",
    drive_folder_name: str = "",
    drive_folder_url: str = "",
) -> None:
    path = _user_jobs_path(chat_id)
    if not path.exists():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return
    jobs: list[dict] = data.get("jobs", [])
    for job in jobs:
        if job.get("job_id") == job_id:
            job["spreadsheet_url"] = spreadsheet_url or ""
            if drive_folder_id:
                job["drive_folder_id"] = drive_folder_id
            if drive_folder_name:
                job["drive_folder_name"] = drive_folder_name
            if drive_folder_url:
                job["drive_folder_url"] = drive_folder_url
            job["last_action_at"] = _now()
            break
    data["jobs"] = jobs
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _user_job_record(chat_id: int, job_id: str) -> dict | None:
    path = _user_jobs_path(chat_id)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return next((job for job in data.get("jobs", []) if job.get("job_id") == job_id), None)


def _user_can_access_job(chat_id: int, job_id: str) -> bool:
    if chat_id in ADMIN_CHAT_IDS:
        return True
    path = _user_jobs_path(chat_id)
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return any(j.get("job_id") == job_id for j in data.get("jobs", []))


def _deny_job_access(message: telebot.types.Message, job_id: str) -> None:
    bot.reply_to(message, "У вас нет доступа к этому заказу.")
    _log_event(
        "job_access_denied",
        chat_id=message.chat.id,
        safe_message="User denied access to job",
        job_id=job_id,
    )


def _set_status(session: dict, status: str) -> None:
    if status not in SESSION_STATUSES:
        raise ValueError(f"Unknown session status: {status}")
    if session.get("status") != status:
        session["status"] = status
        session["status_changed_at"] = _now()


def _mark_failed(session: dict, error_type: str, error: str) -> None:
    _set_status(session, "failed")
    session["failed_at"] = _now()
    session["processing_started"] = False
    session["done_requested"] = False
    session["done_requested_at"] = None
    session["queued_at"] = None
    session["last_error_type"] = error_type
    session["last_error"] = error


def _new_processing_run_id(chat_id: int) -> str:
    return f"{chat_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(2)}"


def _stale_reason(session: dict, now: datetime | None = None) -> str | None:
    now = now or datetime.now()
    status = session.get("status")
    if status == "done_requested":
        start = _parse_dt(session.get("done_requested_at") or session.get("status_changed_at"))
        if start and now - start > timedelta(minutes=DONE_REQUESTED_TIMEOUT_MINUTES):
            return f"done_requested older than {DONE_REQUESTED_TIMEOUT_MINUTES} minutes"
    if status == "queued":
        start = _parse_dt(session.get("queued_at") or session.get("status_changed_at"))
        if start and now - start > timedelta(minutes=QUEUED_TIMEOUT_MINUTES):
            return f"queued older than {QUEUED_TIMEOUT_MINUTES} minutes"
    if status == "processing":
        start = _parse_dt(session.get("processing_started_at") or session.get("status_changed_at"))
        if start and now - start > timedelta(minutes=PROCESSING_TIMEOUT_MINUTES):
            return f"processing older than {PROCESSING_TIMEOUT_MINUTES} minutes"
    return None


def _recover_stale_session_locked(chat_id: int, session: dict) -> dict | None:
    reason = _stale_reason(session)
    if not reason:
        return session
    _set_status(session, "stale")
    session["stale_detected_at"] = _now()
    session["stale_reason"] = reason
    session["processing_started"] = False
    session["done_requested"] = False
    _save_session(chat_id, session)
    _log_event(
        "session_stale_detected",
        chat_id=chat_id,
        session=session,
        level="WARNING",
        safe_message="Stale Telegram session detected",
        stale_reason=reason,
    )
    _archive_session(chat_id, session, "stale")
    _clear_session(chat_id)
    return None


def _normalize_project_name(filename: str) -> str:
    name = re.sub(r"\.pdf$", "", filename, flags=re.IGNORECASE)
    name = re.sub(r"\bКР\s*\d+\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\bАР\b", "", name, flags=re.IGNORECASE)
    name = name.replace("_", " ").replace("-", " ")
    name = re.sub(r"\s+", " ", name).strip()
    return name or "Проект"


def _unique_upload_path(upload_dir: Path, filename: str) -> Path:
    candidate = upload_dir / filename
    if not candidate.exists():
        return candidate
    source_name = Path(filename)
    stem = source_name.stem or "document"
    suffix = source_name.suffix or ".pdf"
    index = 2
    while True:
        candidate = upload_dir / f"{stem}__{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


# ── extraction JSON intake (2026-08-25, repetition plan фаза 1-3) ───────────

_CYRILLIC_TO_LATIN = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "",
    "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def _slugify_project_name(raw: str, max_len: int = 40) -> str:
    """Транслитерация/санитайз произвольного текста (имени файла или адреса) в
    безопасное имя папки: только [a-z0-9_], без ведущих/повторных подчёркиваний.
    Пустой/нечитаемый ввод -> "project"."""
    text = (raw or "").strip().lower()
    out = []
    for ch in text:
        if ch in _CYRILLIC_TO_LATIN:
            out.append(_CYRILLIC_TO_LATIN[ch])
        elif ch.isalnum() and ch.isascii():
            out.append(ch)
        else:
            out.append("_")
    slug = re.sub(r"_+", "_", "".join(out)).strip("_")
    return (slug[:max_len].rstrip("_") or "project")


def _extraction_session_path(chat_id: int) -> Path:
    return EXTRACTION_SESSIONS_DIR / f"{chat_id}.json"


def _load_extraction_session(chat_id: int) -> dict | None:
    path = _extraction_session_path(chat_id)
    if not path.exists():
        return None
    try:
        session = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    started_at = _parse_dt(session.get("started_at"))
    if started_at and datetime.now() - started_at > timedelta(hours=EXTRACTION_SESSION_MAX_AGE_HOURS):
        return None
    return session


def _save_extraction_session(chat_id: int, session: dict) -> None:
    path = _extraction_session_path(chat_id)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(session, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _extraction_project_dir(chat_id: int, source_filename: str, project_label: str = "") -> tuple[Path, str, bool]:
    """Возвращает (папка проекта, job_id, is_new_run).

    job_id = "<slug названия проекта>_<YYYYMMDD_HHMMSS>". Название проекта берётся
    из имён исходных PDF в `source_files`; имя загруженного JSON используется только
    как fallback. Это та же временная схема,
    что уже используется в старом пайплайне (earthworks_parser_google_stage1.make_job_id,
    create_job_from_pdf._make_job_id): имя проекта берётся из имени файла, дата/время
    вшиты прямо в job_id, каждый новый прогон получает свою папку.

    "Один прогон" = первый JSON + его же исправленная версия: пока в сессии этого чата
    есть активный (не старше EXTRACTION_SESSION_MAX_AGE_HOURS) job_id, следующая JSON-
    загрузка попадает в ТУ ЖЕ папку, а не создаёт новую - иначе исправленный JSON
    полностью новый прогон, значит новая папка."""
    session = _load_extraction_session(chat_id)
    if session and session.get("job_id"):
        job_id = session["job_id"]
        out_dir = CHAT_EXTRACTION_OUTPUTS_DIR / job_id
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir, job_id, False

    slug = _slugify_project_name(project_label or Path(source_filename).stem)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = f"{slug}_{stamp}"
    out_dir = CHAT_EXTRACTION_OUTPUTS_DIR / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    _save_extraction_session(chat_id, {
        "chat_id": chat_id,
        "job_id": job_id,
        "source_filename": source_filename,
        "project_label": project_label,
        "started_at": _now(),
        "uploads": [],
    })
    return out_dir, job_id, True


def _record_extraction_upload(chat_id: int, filename: str, notes_report_path: str | None) -> None:
    session = _load_extraction_session(chat_id) or {}
    uploads = session.setdefault("uploads", [])
    uploads.append({
        "filename": filename,
        "uploaded_at": _now(),
        "notes_report_path": notes_report_path,
    })
    _save_extraction_session(chat_id, session)


def _run_notes_report(input_json_path: Path, output_path: Path) -> subprocess.CompletedProcess:
    cmd = [
        _python(), str(NOTES_REPORT_SCRIPT),
        "--input", str(input_json_path),
        "--output", str(output_path),
    ]
    return _run(cmd, TIMEOUTS["notes_report"])


def _run_populate_workbook(input_json_path: Path, output_path: Path) -> subprocess.CompletedProcess:
    cmd = [
        _python(), str(POPULATE_WORKBOOK_SCRIPT),
        str(input_json_path),
        "--output", str(output_path),
    ]
    return _run(cmd, TIMEOUTS["populate_workbook"])


def _resolve_json_job_dir(job_id: str) -> tuple[Path | None, str | None]:
    """Resolves a job_id to its CHAT_EXTRACTION_OUTPUTS_DIR folder, tolerating the common typo of
    dropping the "extraction_output_" prefix the bot itself adds (see _extraction_project_dir/
    _slugify_project_name) - confirmed 2026-08-26 as a real user mistake, not hypothetical.
    Returns (resolved_dir, error_message); error_message is set (and resolved_dir is None) only
    for the ambiguous multi-candidate case - a plain "no such job" is just (None, None), same as
    before this helper existed, since callers already have their own not-a-JSON-flow-job fallback."""
    exact = CHAT_EXTRACTION_OUTPUTS_DIR / job_id
    if exact.is_dir():
        return exact, None
    candidates = [d for d in CHAT_EXTRACTION_OUTPUTS_DIR.iterdir() if d.is_dir() and d.name.endswith(job_id)]
    if len(candidates) == 1:
        return candidates[0], None
    if len(candidates) > 1:
        return None, (
            "Не могу однозначно определить job_id — под это окончание подходит несколько папок:\n"
            + "\n".join(f"- {c.name}" for c in candidates)
            + "\n\nУкажите job_id полностью."
        )
    return None, None


def _json_flow_job_spreadsheet_url(chat_id: int, job_id: str) -> str | None:
    """The JSON-flow's Google Sheet URL per job lives in the per-chat user_jobs registry
    (_register_user_job/_update_user_job_url) - the JSON-flow has never used state.json/
    resolve_stage1_job_dir (that is _find_spreadsheet_url's PDF-flow-only lookup)."""
    job = _user_job_record(chat_id, job_id)
    return (job or {}).get("spreadsheet_url") or None


def _publish_review_workbook(
    workbook_path: Path,
    title: str,
    *,
    folder_id: str = "",
    folder_name: str = "",
) -> dict:
    """Публикует review workbook в Google Drive - переиспользует уже рабочий
    google_sheet_publisher.py из earthworks_parser_google_stage1 (проверено
    2026-08-25, реальная публикация прошла). Импорт лениво, внутри функции, чтобы
    не тянуть google-* зависимости при обычном PDF-flow бота, если их вдруг снова
    не будет в окружении - в этом случае публикация просто скипается, как и
    задумано в самом publish_workbook_if_configured."""
    if str(GOOGLE_STAGE1_DIR) not in sys.path:
        sys.path.insert(0, str(GOOGLE_STAGE1_DIR))
    from google_sheets.google_sheet_publisher import publish_workbook_if_configured
    return publish_workbook_if_configured(
        workbook_path,
        title,
        sharing=GOOGLE_SHEET_SHARING,
        folder_id=folder_id,
        folder_name=folder_name,
    )


def _download_review_workbook(spreadsheet_url: str, output_path: Path) -> dict:
    """Reverse of _publish_review_workbook - pulls the CURRENT state of the Sheet (Elena's/the
    user's edits) back down as .xlsx so /build works on what's actually in the Sheet, not a stale
    local snapshot from before publishing."""
    if str(GOOGLE_STAGE1_DIR) not in sys.path:
        sys.path.insert(0, str(GOOGLE_STAGE1_DIR))
    from google_sheets.google_sheet_publisher import download_spreadsheet_as_xlsx
    return download_spreadsheet_as_xlsx(spreadsheet_url, output_path)


def _run_build_all_sections(workbook_path: Path, results_dir: Path) -> subprocess.CompletedProcess:
    cmd = [
        _python(), str(BUILD_ALL_SECTIONS_SCRIPT),
        "--workbook", str(workbook_path),
        "--results-dir", str(results_dir),
    ]
    return _run(cmd, TIMEOUTS["build_all_sections"])


def _run_export_estimate(results_dir: Path, review_workbook_path: Path, output_path: Path) -> subprocess.CompletedProcess:
    cmd = [
        _python(), str(EXPORT_ESTIMATE_SCRIPT),
        "--results-dir", str(results_dir),
        "--review-workbook", str(review_workbook_path),
        "--out", str(output_path),
    ]
    return _run(cmd, TIMEOUTS["export_estimate"])


def _format_section_failures(stdout: str) -> str:
    """build_all_section_results.py prints one clear 'CODE: first error line' per failed section
    to stdout - reuse that instead of dumping the whole raw output at the user."""
    lines = []
    in_failed = False
    for line in stdout.splitlines():
        if line.startswith("FAILED ("):
            in_failed = True
            continue
        if in_failed:
            stripped = line.strip()
            if not stripped:
                break
            if stripped.startswith("- "):
                lines.append(stripped[2:])
    return "\n".join(f"⚠️ {line}" for line in lines) if lines else short_text(stdout, 800)


def short_text(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "..."


# ── helpers ────────────────────────────────────────────────────────────────

def _python() -> str:
    return sys.executable


def _allowed(chat_id: int) -> bool:
    return ALLOW_ALL_USERS or chat_id in ALLOWED_CHAT_IDS or chat_id in ADMIN_CHAT_IDS


def _admin_allowed(chat_id: int) -> bool:
    return chat_id in ADMIN_CHAT_IDS


def _deny_access(message: telebot.types.Message, command_name: str, admin_required: bool = False) -> None:
    _log_event(
        "access_denied",
        chat_id=message.chat.id,
        level="WARNING",
        safe_message="Access denied",
        command=command_name,
        admin_required=admin_required,
    )
    bot.reply_to(message, "У вас нет доступа к этой команде.")


def _require_user_access(message: telebot.types.Message, command_name: str) -> bool:
    if _allowed(message.chat.id):
        return True
    _deny_access(message, command_name)
    return False


def _require_admin_access(message: telebot.types.Message, command_name: str) -> bool:
    if _admin_allowed(message.chat.id):
        return True
    _deny_access(message, command_name, admin_required=True)
    return False


def _format_bytes(value: int) -> str:
    size = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024 or unit == "TiB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024


def _format_timedelta(delta: timedelta) -> str:
    seconds = int(delta.total_seconds())
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def _get_git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
            cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            return result.stdout.strip() or "unknown"
    except Exception:
        pass
    return "unknown"


def _run(cmd: list, timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
        cwd=str(REPO_ROOT),
    )


def _log(chat_id: int, label: str, returncode: int, stdout: str, stderr: str) -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = LOGS_DIR / str(chat_id)
    log_dir.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": ts,
        "chat_id": chat_id,
        "command": label,
        "returncode": returncode,
        "stdout": stdout[:10_000],
        "stderr": stderr[:10_000],
    }
    (log_dir / f"{ts}_{label}.json").write_text(
        json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _parse_json(stdout: str) -> dict | None:
    try:
        return json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        return None


def _find_excel(job_id: str) -> Path | None:
    try:
        from job_locator import resolve_stage1_job_dir
        from job_state import load_job_state
        job_dir = resolve_stage1_job_dir(job_id)
        state = load_job_state(job_dir)
        build = state.get("last_build", {})
        out_dir = build.get("out_dir", "")
        final_excel = build.get("final_excel", "")
        if out_dir and final_excel:
            return REPO_ROOT / out_dir / final_excel
    except Exception:
        pass
    return None


def _find_spreadsheet_url(job_id: str) -> str | None:
    try:
        from job_locator import resolve_stage1_job_dir
        from job_state import load_job_state
        job_dir = resolve_stage1_job_dir(job_id)
        state = load_job_state(job_dir)
        return state.get("google_sheet", {}).get("url")
    except Exception:
        return None


# ── quiet-window processing ────────────────────────────────────────────────

def schedule_process_after_quiet(chat_id: int) -> None:
    """Fire try_process_done_session after QUIET_SECONDS."""
    t = threading.Timer(QUIET_SECONDS, try_process_done_session, args=(chat_id,))
    t.daemon = True
    t.start()


def try_process_done_session(chat_id: int) -> None:
    """
    Called after quiet window. If enough time has passed since the last PDF
    and done was requested, launch the parser. Otherwise reschedule.
    """
    lock = get_chat_lock(chat_id)
    with lock:
        session = _load_session(chat_id)
        session = _recover_stale_session_locked(chat_id, session)
        if session is None:
            return

        if session.get("status") not in {"done_requested", "queued"}:
            return
        if not session.get("pdfs"):
            return

        last_pdf_str = session.get("last_pdf_added_at")
        if last_pdf_str:
            last_pdf_dt = datetime.fromisoformat(last_pdf_str)
            elapsed = (datetime.now() - last_pdf_dt).total_seconds()
            if elapsed < QUIET_SECONDS:
                # Still within quiet window — reschedule
                remaining = QUIET_SECONDS - elapsed + 0.5
                session_copy = None  # don't need to pass session
        else:
            elapsed = QUIET_SECONDS  # no timestamp → proceed

        if last_pdf_str and elapsed < QUIET_SECONDS:
            # Release lock and reschedule
            t = threading.Timer(remaining, try_process_done_session, args=(chat_id,))
            t.daemon = True
            t.start()
            return

        _set_status(session, "queued")
        session["queued_at"] = _now()
        _save_session(chat_id, session)
        _log_event(
            "create_job_queued",
            chat_id=chat_id,
            session=session,
            safe_message="Create job queued after quiet window",
            pdf_count=len(session.get("pdfs", [])),
        )

        session["processing_started"] = True
        session["processing_started_at"] = _now()
        session["processing_run_id"] = _new_processing_run_id(chat_id)
        _set_status(session, "processing")
        _save_session(chat_id, session)
        _log_event(
            "create_job_started",
            chat_id=chat_id,
            session=session,
            safe_message="Create job subprocess started",
            pdf_count=len(session.get("pdfs", [])),
        )
        pdfs = list(session["pdfs"])
        project_name = session.get("project_name") or "Проект"

    # Lock released — run parser outside lock
    _run_create_job(chat_id, pdfs, project_name)


def _run_create_job(chat_id: int, pdfs: list, project_name: str) -> None:
    cmd = [
        _python(), str(CREATE_JOB),
        "--project-name", project_name,
        "--sharing", "anyone_writer",
        "--json",
    ]
    for entry in pdfs:
        cmd += ["--pdf", entry["local_path"]]

    try:
        result = _run(cmd, TIMEOUTS["create_job"])
    except subprocess.TimeoutExpired:
        _log(chat_id, "create_job", -1, "", "timeout")
        _mark_create_job_failed(chat_id, "timeout", "create_job timeout")
        bot.send_message(chat_id,
            "Не удалось создать заказ ⚠️\n\n"
            "PDF-набор сохранён.\nМожно попробовать ещё раз: /done"
        )
        return

    _log(chat_id, "create_job", result.returncode, result.stdout, result.stderr)

    if result.returncode != 0:
        _mark_create_job_failed(chat_id, "create_job_failed", (result.stderr or result.stdout)[-1000:])
        bot.send_message(chat_id,
            "Не удалось создать заказ ⚠️\n\n"
            "PDF-набор сохранён.\nМожно попробовать ещё раз: /done"
        )
        return

    data = _parse_json(result.stdout)
    if data is None:
        _mark_create_job_failed(chat_id, "invalid_create_job_json", "create_job stdout is not valid JSON")
        bot.send_message(chat_id,
            "Не удалось создать заказ ⚠️\n\n"
            "PDF-набор сохранён.\nМожно попробовать ещё раз: /done"
        )
        return

    job_id = data.get("job_id", "?")
    url    = data.get("spreadsheet_url", "нет")
    pr     = data.get("parser_run", {})
    cands  = pr.get("candidates_count", "?")
    parser_errors = pr.get("errors", [])
    ac     = data.get("anti_cheat", {})
    ac_status = ac.get("status", "")
    ac_errors = ac.get("errors_count", 0)

    pdf_list = "\n".join(f"{i+1}. {e['filename']}" for i, e in enumerate(pdfs))

    text = (
        f"Готово ✅\n\n"
        f"Заказ:\n{job_id}\n\n"
        f"PDF в заказе: {len(pdfs)}\n{pdf_list}\n\n"
        f"Таблица для проверки:\n{url}\n\n"
        f"Парсер нашёл кандидатов: {cands}"
    )
    if parser_errors:
        text += f"\n⚠️ Ошибки парсера: {len(parser_errors)}"
    if ac_status == "warnings" and ac_errors > 0:
        n = ac_errors
        suffix = "е" if n == 1 else ("я" if n < 5 else "й")
        text += f"\n\nℹ️ Автопроверка нашла {n} замечани{suffix} — это не блокирует работу."
    text += (
        f"\n\nПроверьте и заполните Google Sheet.\nПосле проверки отправьте:\n\n"
        f"/build {job_id}\n\n"
        f"Если таблица потерялась или сломалась:\n"
        f"/recreate {job_id}\n\n"
        f"Если PDF распознался плохо и нужно запустить парсер заново:\n"
        f"/rerun {job_id}"
    )

    lock = get_chat_lock(chat_id)
    with lock:
        session = _load_session(chat_id)
        _set_status(session, "completed")
        session["completed_at"] = _now()
        session["processing_started"] = False
        session["done_requested"] = False
        session["job_id"] = job_id
        session["spreadsheet_url"] = url
        _save_session(chat_id, session)
        _log_event(
            "create_job_completed",
            chat_id=chat_id,
            session=session,
            safe_message="Create job completed",
            pdf_count=len(pdfs),
            candidates_count=cands,
        )
        _archive_session(chat_id, session, "completed")
        _clear_session(chat_id)

    _register_user_job(
        chat_id,
        job_id=job_id,
        project_name=project_name,
        spreadsheet_url=url,
        pdf_count=len(pdfs),
    )
    bot.send_message(chat_id, text)


def _mark_create_job_failed(chat_id: int, error_type: str, error: str) -> None:
    lock = get_chat_lock(chat_id)
    with lock:
        session = _load_session(chat_id)
        _mark_failed(session, error_type, error)
        _save_session(chat_id, session)
        _log_event(
            "create_job_failed",
            chat_id=chat_id,
            session=session,
            level="ERROR",
            safe_message="Create job failed",
            error_type=error_type,
            error=error,
        )
        _log_event(
            "session_failed",
            chat_id=chat_id,
            session=session,
            level="WARNING",
            safe_message="Telegram session marked as failed",
            error_type=error_type,
        )


def _session_next_action(status: str) -> str:
    if status == "collecting":
        return "Пришлите ещё PDF или напишите /done."
    if status in {"done_requested", "queued"}:
        return "Команда /done принята, ожидаю quiet-window."
    if status == "processing":
        return "Обработка уже запущена, дождитесь результата."
    if status == "failed":
        return "Предыдущая обработка упала. PDF сохранены, можно повторить /done."
    return "Сейчас нет активной загрузки. Отправьте PDF проекта."


def _format_session_status(session: dict | None) -> str:
    if not session or not session.get("pdfs"):
        return "Сейчас нет активной загрузки.\n\nОтправьте PDF проекта."
    status = session.get("status", "collecting")
    lines = [
        "Текущая загрузка:",
        f"- status: {status}",
        f"- project_name: {session.get('project_name') or 'не задан'}",
        f"- session_id: {session.get('session_id') or 'не задан'}",
        f"- PDF: {len(session.get('pdfs', []))}",
        f"- done_requested: {bool(session.get('done_requested'))}",
        f"- processing_started: {bool(session.get('processing_started'))}",
        f"- last_pdf_added_at: {session.get('last_pdf_added_at') or 'нет'}",
        f"- updated_at: {session.get('updated_at') or 'нет'}",
    ]
    if session.get("last_error_type"):
        lines.append(f"- last_error_type: {session.get('last_error_type')}")
    lines.extend(["", _session_next_action(status)])
    return "\n".join(lines)


# ── /start ─────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["start"])
def cmd_start(message: telebot.types.Message) -> None:
    if not _require_user_access(message, "/start"):
        return
    bot.reply_to(message,
        "Работа начинается с JSON из ChatGPT-чата.\n\n"
        "1. Пришлите первый JSON файлом.\n"
        "2. Бот пришлёт отчёт для проверки — отдайте его в тот же ChatGPT-чат.\n"
        "3. Пришлите сюда исправленный JSON.\n"
        "4. Бот соберёт Google-таблицу. Проверьте её и затем отправьте /build <job_id>.\n\n"
        "Подробная инструкция: /help"
    )


@bot.message_handler(commands=["help"])
def cmd_help(message: telebot.types.Message) -> None:
    if not _require_user_access(message, "/help"):
        return
    text = (
        "Как работать с ботом:\n\n"
        "1. Пришлите первый JSON из ChatGPT-чата.\n"
        "Бот сохранит проект и пришлёт файл с замечаниями для проверки.\n\n"
        "2. Отправьте файл с замечаниями обратно в тот же ChatGPT-чат.\n"
        "Когда ChatGPT выдаст исправленный JSON, пришлите его сюда.\n\n"
        "3. Бот соберёт Google-таблицу и пришлёт ссылку.\n"
        "Проверьте таблицу и заполните нужные поля.\n\n"
        "4. Когда таблица проверена, отправьте:\n"
        "/build <job_id>\n\n"
        "Команды:\n"
        "/new_project — начать новый проект\n"
        "/update_json <job_id> — загрузить новый исправленный JSON в старый проект\n"
        "/recreate <job_id> — пересобрать Google-таблицу из последнего JSON\n"
        "/build <job_id> — собрать итоговую смету"
    )
    if _admin_allowed(message.chat.id):
        text += "\n\nАдминские команды: /admin_help"
    bot.reply_to(message, text)


# ── extraction JSON (2026-08-25, repetition plan фаза 1-3) ──────────────────
def _handle_extraction_json_upload(message: telebot.types.Message, doc: telebot.types.Document) -> None:
    chat_id = message.chat.id

    file_info = bot.get_file(doc.file_id)
    raw = bot.download_file(file_info.file_path)

    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        bot.reply_to(message, f"Это не читается как JSON ⚠️\n\n{exc}")
        _log_event("extraction_json_invalid", chat_id=chat_id, safe_message="Uploaded file is not valid JSON",
                    filename=doc.file_name, error=str(exc))
        return

    if not isinstance(data, dict) or "sections" not in data:
        bot.reply_to(message,
            "Файл — валидный JSON, но не похож на extraction_output "
            "(нет ключа \"sections\") ⚠️\n\nПроверьте файл и пришлите заново."
        )
        _log_event("extraction_json_wrong_shape", chat_id=chat_id, filename=doc.file_name,
                    safe_message="Uploaded JSON lacks expected 'sections' key")
        return

    project_name = str(data.get("project_name") or "")
    project_label = project_label_from_extraction(data, doc.file_name or "project")
    out_dir, job_id, is_new_run = _extraction_project_dir(
        chat_id,
        doc.file_name or "project",
        project_label,
    )
    extraction_session = _load_extraction_session(chat_id) or {}
    created_at = extraction_session.get("started_at") or _now()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"extraction_output_bot_{ts}.json"
    json_path.write_bytes(raw)

    section_count = len(data.get("sections") or {})
    warnings_count = len(data.get("extraction_warnings") or [])

    bot.reply_to(message,
        f"JSON принят ✅ ({'новый прогон' if is_new_run else 'исправленный JSON, этот же прогон'})\n\n"
        f"Job: {job_id}\n"
        f"Короткое название: {project_label}\n"
        f"Проект (из JSON): {project_name or '(без имени)'}\n"
        f"Разделов в JSON: {section_count}\n"
        f"Общих предупреждений парсера: {warnings_count}"
    )

    if is_new_run:
        # Первая загрузка прогона - собрать отчёт работы над ошибками и ждать исправленный JSON.
        # Google-таблицу на этом шаге НЕ собираем (2026-08-25: раньше собирали отчёт на КАЖДОЙ
        # загрузке, включая уже исправленную - пользователь получал повторную просьбу "отправьте
        # в ChatGPT" даже когда уже прислал исправленный файл; реальная путаница, см. чат).
        bot.send_message(chat_id, "Собираю приложение к служебной записке (работа над ошибками)…")

        report_path = out_dir / f"code_notes_report_bot_{ts}.txt"
        result = _run_notes_report(json_path, report_path)
        _log(chat_id, "notes_report", result.returncode, result.stdout, result.stderr)

        if result.returncode != 0 or not report_path.exists():
            bot.reply_to(message,
                "JSON сохранён, но отчёт работы над ошибками собрать не удалось ⚠️\n\n"
                f"{(result.stderr or result.stdout)[-1500:]}"
            )
            _record_extraction_upload(chat_id, json_path.name, None)
            _log_event("notes_report_failed", chat_id=chat_id, safe_message="build_extraction_notes_report.py failed",
                        filename=json_path.name, job_id=job_id, returncode=result.returncode)
            return

        _record_extraction_upload(chat_id, json_path.name, str(report_path))
        _log_event("extraction_json_processed", chat_id=chat_id, safe_message="Extraction JSON saved and notes report built",
                    filename=json_path.name, job_id=job_id, section_count=section_count)

        with open(report_path, "rb") as f:
            bot.send_document(chat_id, f,
                caption=(
                    f"Отчёт готов ✅ (Job: {job_id})\n\n"
                    "Отправьте этот файл вместе с "
                    "prompts/notes_report_correction_prompt.md в тот же ChatGPT-чат, "
                    "где делали извлечение — и пришлите сюда исправленный JSON, "
                    "когда будет готов (попадёт в тот же прогон, без повторного отчёта - "
                    "сразу соберу таблицу)."
                )
            )
        return

    # Это уже не первая загрузка этого прогона -> считаем её исправленным JSON, отчёт над
    # ошибками не повторяем, сразу собираем review workbook и публикуем в Google (фаза 4).
    _record_extraction_upload(chat_id, json_path.name, None)
    _log_event("extraction_json_processed", chat_id=chat_id, safe_message="Corrected extraction JSON received",
                filename=json_path.name, job_id=job_id, section_count=section_count)
    bot.send_message(chat_id, "Это исправленный JSON — собираю Google-таблицу для проверки…")

    workbook_target = out_dir / "review_workbook.xlsx"
    wb_result = _run_populate_workbook(json_path, workbook_target)
    _log(chat_id, "populate_workbook", wb_result.returncode, wb_result.stdout, wb_result.stderr)

    wb_info = _parse_json(wb_result.stdout)
    workbook_path = Path(wb_info["output_path"]) if wb_info and wb_info.get("output_path") else None
    if wb_result.returncode != 0 or not workbook_path or not workbook_path.exists():
        bot.reply_to(message,
            "Google-таблицу собрать не удалось ⚠️\n\n"
            f"{(wb_result.stderr or wb_result.stdout)[-1500:]}"
        )
        _log_event("populate_workbook_failed", chat_id=chat_id, job_id=job_id,
                    safe_message="populate_review_workbook_from_extraction.py failed",
                    returncode=wb_result.returncode)
        return

    try:
        drive_folder_name = project_drive_folder_name(project_label, created_at)
        publish_result = _publish_review_workbook(
            workbook_path,
            title=review_sheet_title(project_label, created_at),
            folder_name=drive_folder_name,
        )
    except Exception as exc:
        bot.reply_to(message, f"Таблица собрана локально, но публикация в Google упала ⚠️\n\n{exc}")
        _log_event("publish_sheet_exception", chat_id=chat_id, job_id=job_id,
                    safe_message="publish_workbook_if_configured raised", error=str(exc))
        return

    _log_event("publish_sheet_result", chat_id=chat_id, job_id=job_id,
                safe_message="publish_workbook_if_configured finished", result=publish_result)

    if publish_result.get("status") != "published":
        reason = publish_result.get("reason") or publish_result.get("status")
        bot.reply_to(message,
            f"Таблица собрана локально ({workbook_path.name}), но не опубликована в Google ⚠️\n\n"
            f"Причина: {reason}"
        )
        return

    url = publish_result.get("url", "")
    folder_url = publish_result.get("drive_folder_url", "")
    _register_user_job(
        chat_id,
        job_id,
        project_label,
        url,
        pdf_count=0,
        drive_folder_id=publish_result.get("drive_folder_id", ""),
        drive_folder_name=publish_result.get("drive_folder_name", ""),
        drive_folder_url=folder_url,
    )
    folder_line = f"\nПапка проекта: {folder_url}\n" if folder_url else ""
    bot.reply_to(message,
        f"Google-таблица готова ✅\n\n{url}\n"
        f"{folder_line}\n"
        "Проверьте и заполните лист «01_Проверка проекта», затем можно собирать смету."
    )


# ── документы: основной JSON-flow; PDF-flow оставлен как legacy ─────────────
@bot.message_handler(content_types=["document"])
def handle_document(message: telebot.types.Message) -> None:
    if not _require_user_access(message, "document"):
        return

    doc = message.document
    name_lower = (doc.file_name or "").lower()

    if name_lower.endswith(".json"):
        _handle_extraction_json_upload(message, doc)
        return

    if not name_lower.endswith(".pdf"):
        bot.reply_to(message,
            "Пожалуйста, отправьте JSON-файл из ChatGPT-чата.\n\n"
            "Если это новый проект — просто пришлите первый JSON. "
            "Если это исправленная версия — пришлите исправленный JSON в тот же чат бота."
        )
        return

    # Download PDF before taking the lock
    file_info = bot.get_file(doc.file_id)
    raw = bot.download_file(file_info.file_path)
    sha256 = hashlib.sha256(raw).hexdigest()

    lock = get_chat_lock(message.chat.id)
    with lock:
        session = _load_session(message.chat.id)
        session = _recover_stale_session_locked(message.chat.id, session) or _new_session(message.chat.id)
        status = session.get("status", "collecting")

        if status == "processing":
            bot.reply_to(message,
                "Парсер уже запущен для текущего набора.\n"
                "Дождитесь результата, затем отправьте PDF для нового заказа."
            )
            return

        if status in {"stale", "cancelled", "completed"}:
            session = _new_session(message.chat.id)
        elif status == "failed":
            _set_status(session, "collecting")
            session["last_error"] = None
            session["last_error_type"] = None
            session["failed_at"] = None
            session["processing_started"] = False
            session["done_requested"] = False
            session["done_requested_at"] = None
            session["queued_at"] = None

        if not session.get("session_id"):
            session["session_id"] = datetime.now().strftime("%Y%m%d_%H%M%S")
            session["created_at"] = datetime.now().isoformat(timespec="seconds")
            _log_event(
                "session_created",
                chat_id=message.chat.id,
                session=session,
                safe_message="New Telegram upload session created",
            )

        upload_dir = UPLOADS_DIR / str(message.chat.id) / session["session_id"]
        upload_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = _unique_upload_path(upload_dir, doc.file_name)
        pdf_path.write_bytes(raw)

        if not session.get("project_name"):
            session["project_name"] = _normalize_project_name(doc.file_name)

        session.setdefault("pdfs", []).append({
            "filename": doc.file_name,
            "local_path": str(pdf_path),
            "sha256": sha256,
        })
        session["last_pdf_added_at"] = datetime.now().isoformat(timespec="seconds")
        if session.get("status") not in {"done_requested", "queued"}:
            _set_status(session, "collecting")

        _save_session(message.chat.id, session)
        count = len(session["pdfs"])
        _log_event(
            "pdf_received",
            chat_id=message.chat.id,
            session=session,
            safe_message="PDF received from Telegram",
            filename=doc.file_name,
            sha256=sha256,
        )
        _log_event(
            "pdf_saved",
            chat_id=message.chat.id,
            session=session,
            safe_message="PDF saved to local upload storage",
            filename=doc.file_name,
            local_path=str(pdf_path),
            pdf_count=count,
        )

    if count == 1:
        hint = "Пришлите остальные PDF этого проекта.\nКогда все файлы проекта отправлены, напишите:\n\n/done"
    else:
        hint = "Когда все файлы проекта отправлены, напишите:\n\n/done"

    bot.reply_to(message,
        f"PDF добавлен ✅\n\n"
        f"Сейчас в заказе: {count} PDF.\n\n"
        f"{hint}"
    )


# ── /done ──────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["done"])
def cmd_done(message: telebot.types.Message) -> None:
    if not _require_user_access(message, "/done"):
        return

    lock = get_chat_lock(message.chat.id)
    with lock:
        session = _load_session(message.chat.id)
        session = _recover_stale_session_locked(message.chat.id, session)
        if session is None:
            bot.reply_to(message,
                "Предыдущая загрузка устарела и была закрыта.\n\n"
                "Пожалуйста, отправьте PDF заново."
            )
            return
        pdfs = session.get("pdfs", [])
        status = session.get("status", "collecting")

        if not pdfs:
            bot.reply_to(message,
                "Пока нет PDF для обработки.\n\n"
                "Сначала отправьте один или несколько PDF проекта.\n"
                "Когда все файлы будут отправлены — напишите /done."
            )
            return

        if status == "processing":
            bot.reply_to(message, "Парсер уже запущен, дождитесь результата.")
            return

        if status in {"done_requested", "queued"}:
            bot.reply_to(message, "Команда /done уже принята, дождитесь результата.")
            return

        if status in {"stale", "cancelled", "completed"}:
            bot.reply_to(message, "Сейчас нет активной загрузки. Отправьте PDF проекта заново.")
            return

        _set_status(session, "done_requested")
        session["failed_at"] = None
        session["last_error"] = None
        session["last_error_type"] = None
        session["done_requested"] = True
        session["done_requested_at"] = _now()
        session["queued_at"] = None
        session["processing_started"] = False
        _save_session(message.chat.id, session)
        _log_event(
            "done_requested",
            chat_id=message.chat.id,
            session=session,
            safe_message="User requested processing with /done",
            pdf_count=len(pdfs),
        )

    bot.reply_to(message,
        "Принято ✅\n\n"
        "Проверяю, что все PDF успели загрузиться.\n"
        f"Если новых файлов не будет, через {QUIET_SECONDS} секунд запущу парсер."
    )

    schedule_process_after_quiet(message.chat.id)


# ── /status ────────────────────────────────────────────────────────────────
# ── /cancel ────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["cancel"])
def cmd_cancel(message: telebot.types.Message) -> None:
    if not _require_user_access(message, "/cancel"):
        return
    lock = get_chat_lock(message.chat.id)
    with lock:
        path = _session_path(message.chat.id)
        if not path.exists():
            bot.reply_to(message, "Сейчас нет активной загрузки.")
            return
        session = _load_session(message.chat.id)
        session = _recover_stale_session_locked(message.chat.id, session)
        if session is None:
            bot.reply_to(message, "Сейчас нет активной загрузки.")
            return
        status = session.get("status", "collecting")
        if status == "processing":
            bot.reply_to(message, "Обработка уже запущена. Дождитесь результата или обратитесь к администратору.")
            return
        if status not in {"collecting", "done_requested", "queued", "failed"}:
            bot.reply_to(message, "Сейчас нет активной загрузки.")
            return
        _set_status(session, "cancelled")
        session["cancelled_at"] = _now()
        session["processing_started"] = False
        session["done_requested"] = False
        _save_session(message.chat.id, session)
        _log_event(
            "session_cancelled",
            chat_id=message.chat.id,
            session=session,
            safe_message="Telegram upload session cancelled by user",
        )
        _archive_session(message.chat.id, session, "cancelled")
        _clear_session(message.chat.id)
    bot.reply_to(message, "Текущая загрузка отменена. Можете отправить PDF заново.")


# ── /new_project ───────────────────────────────────────────────────────────
@bot.message_handler(commands=["new_project"])
def cmd_new_project(message: telebot.types.Message) -> None:
    """Явно закрывает текущий JSON-прогон этого чата (repetition plan фаза 1-4), не дожидаясь
    истечения EXTRACTION_SESSION_MAX_AGE_HOURS - следующий загруженный JSON начнёт новый job_id/
    новую папку, а не попадёт "исправленным" в старый прогон."""
    if not _require_user_access(message, "/new_project"):
        return
    path = _extraction_session_path(message.chat.id)
    had_session = path.exists()
    if had_session:
        path.unlink(missing_ok=True)
    _log_event(
        "extraction_session_reset",
        chat_id=message.chat.id,
        safe_message="Extraction JSON session manually reset via /new_project",
        had_active_session=had_session,
    )
    bot.reply_to(message,
        "Готово ✅ Следующий загруженный JSON начнёт новый прогон (новая папка, новый job_id)."
        if had_session else
        "Активного прогона и так не было — следующий JSON и так начнёт новый прогон."
    )


# ── /update_json ───────────────────────────────────────────────────────────
@bot.message_handler(commands=["update_json"])
def cmd_update_json(message: telebot.types.Message) -> None:
    """Attach the next uploaded extraction JSON to an existing JSON-flow job.

    This covers the normal production case where the estimator asked ChatGPT to correct the JSON
    in words after the original 2-hour upload window expired. The next JSON should update the same
    job and rebuild the Google review workbook, not create a fresh project folder.
    """
    if not _require_user_access(message, "/update_json"):
        return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Укажите job_id: /update_json <job_id>")
        return

    requested_job_id = parts[1].strip()
    json_job_dir, resolve_error = _resolve_json_job_dir(requested_job_id)
    if resolve_error:
        bot.reply_to(message, resolve_error)
        return
    if json_job_dir is None:
        bot.reply_to(message, f"Не нашла такой JSON-проект: {requested_job_id}")
        return

    job_id = json_job_dir.name
    if not _user_can_access_job(message.chat.id, job_id):
        _deny_job_access(message, job_id)
        return

    _save_extraction_session(message.chat.id, {
        "chat_id": message.chat.id,
        "job_id": job_id,
        "source_filename": "",
        "started_at": _now(),
        "uploads": [],
        "mode": "update_existing_json_job",
    })
    _log_event(
        "extraction_session_update_requested",
        chat_id=message.chat.id,
        safe_message="Next JSON upload will update existing JSON-flow job",
        job_id=job_id,
    )
    bot.reply_to(message,
        f"Готово ✅\n\n"
        f"Следующий JSON-файл попадёт в этот же проект:\n{job_id}\n\n"
        "После загрузки бот сразу пересоберёт и опубликует Google-таблицу."
    )


# ── /build ─────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["build"])
def cmd_build(message: telebot.types.Message) -> None:
    if not _require_user_access(message, "/build"):
        return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Укажите job_id: /build <job_id>")
        return
    job_id = parts[1].strip()

    if not _user_can_access_job(message.chat.id, job_id):
        _deny_job_access(message, job_id)
        return

    bot.reply_to(message, "Собираю смету... Это может занять несколько минут.")

    # JSON-flow jobs: build_job.py/build_from_google_sheet.py below are the OLD single-section
    # earthworks-only pipeline (hardcoded old job layout + hardcoded row positions matching that
    # workbook's shape) - structurally incompatible with the new 7-section review workbook, not
    # just a wrong path (confirmed 2026-08-26: fails with the same "Job directory not found" as
    # the old /recreate did, for an unrelated reason - the whole script is the wrong pipeline).
    # The real new-pipeline equivalent is download the Sheet's current state -> run every section's
    # calculator (build_all_section_results.py) -> assemble the final priced smeta
    # (export_calculator_results_to_estimate_workbook.py) - wired here for the first time.
    json_job_dir, resolve_error = _resolve_json_job_dir(job_id)
    if resolve_error:
        bot.reply_to(message, resolve_error)
        return
    if json_job_dir is not None:
        job_id = json_job_dir.name  # see cmd_recreate's identical comment - registry keys on the full name
        spreadsheet_url = _json_flow_job_spreadsheet_url(message.chat.id, job_id)
        if not spreadsheet_url:
            bot.reply_to(message, "Не нашла ссылку на Google-таблицу для этого job — соберите таблицу через /recreate сначала.")
            _log_event("build_failed", chat_id=message.chat.id, level="ERROR",
                       safe_message="Build (json flow) no spreadsheet url", job_id=job_id)
            return

        downloaded_path = json_job_dir / "review_workbook_downloaded.xlsx"
        download_result = _download_review_workbook(spreadsheet_url, downloaded_path)
        _log_event("build_download_sheet", chat_id=message.chat.id,
                   safe_message="Build (json flow) sheet download", job_id=job_id,
                   status=download_result.get("status"))
        if download_result.get("status") != "downloaded":
            bot.reply_to(message, f"Не смогла скачать таблицу ⚠️\n\n{download_result.get('reason', 'неизвестная причина')}")
            _log_event("build_failed", chat_id=message.chat.id, level="ERROR",
                       safe_message="Build (json flow) download failed", job_id=job_id,
                       reason=download_result.get("reason"))
            return

        results_dir = json_job_dir / "section_results"
        sections_result = _run_build_all_sections(downloaded_path, results_dir)
        _log(message.chat.id, "build_all_sections", sections_result.returncode, sections_result.stdout, sections_result.stderr)
        if sections_result.returncode != 0:
            bot.reply_to(
                message,
                "Смету пока нельзя собрать ⚠️\n\n"
                f"{_format_section_failures(sections_result.stdout)}\n\n"
                f"Исправьте в таблице:\n{spreadsheet_url}\n\n"
                f"После исправлений повторите:\n/build {job_id}",
            )
            _log_event("build_failed", chat_id=message.chat.id, level="ERROR",
                       safe_message="Build (json flow) section build failed", job_id=job_id)
            return

        final_path = json_job_dir / f"estimate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        export_result = _run_export_estimate(results_dir, downloaded_path, final_path)
        _log(message.chat.id, "build_export_estimate", export_result.returncode, export_result.stdout, export_result.stderr)
        if export_result.returncode != 0 or not final_path.exists():
            bot.reply_to(message, f"Все разделы посчитались, но сборка итоговой сметы упала ⚠️\n\n{short_text((export_result.stderr or export_result.stdout), 500)}")
            _log_event("build_failed", chat_id=message.chat.id, level="ERROR",
                       safe_message="Build (json flow) export_estimate failed", job_id=job_id)
            return

        with open(final_path, "rb") as f:
            bot.send_document(message.chat.id, f, caption=f"Смета готова ✅\nJob: {job_id}")
        _log_event("build_completed", chat_id=message.chat.id,
                   safe_message="Build (json flow) completed", job_id=job_id)
        return

    today = datetime.now().strftime("%d.%m.%Y")
    cmd = [
        _python(), str(BUILD_JOB),
        "--job-id", job_id,
        "--section-number", "2",
        "--estimate-date", today,
    ]
    try:
        result = _run(cmd, TIMEOUTS["build"])
    except subprocess.TimeoutExpired:
        bot.reply_to(message, "⏱ Превышено время ожидания (10 мин).")
        return

    _log(message.chat.id, "build", result.returncode, result.stdout, result.stderr)

    if result.returncode != 0:
        url = _find_spreadsheet_url(job_id)
        url_line = f"\n{url}" if url else ""
        bot.reply_to(message,
            f"Смету пока нельзя собрать ⚠️\n\n"
            f"Проверьте и заполните активную таблицу:{url_line}\n\n"
            f"После исправлений повторите:\n/build {job_id}"
        )
        return

    excel_path = _find_excel(job_id)
    if excel_path and excel_path.exists():
        with open(excel_path, "rb") as f:
            bot.send_document(message.chat.id, f, caption=f"Смета готова ✅\nJob: {job_id}")
    else:
        bot.reply_to(message, f"Смета собрана ✅\nJob: {job_id}\n\nExcel не найден локально.")


# ── admin helpers ──────────────────────────────────────────────────────────

def _admin_started(message: telebot.types.Message, command: str, **payload) -> None:
    _log_event(
        "admin_command_started",
        chat_id=message.chat.id,
        safe_message="Admin command started",
        command=command,
        admin_chat_id=message.chat.id,
        **payload,
    )


def _admin_completed(message: telebot.types.Message, command: str, **payload) -> None:
    _log_event(
        "admin_command_completed",
        chat_id=message.chat.id,
        safe_message="Admin command completed",
        command=command,
        admin_chat_id=message.chat.id,
        **payload,
    )


def _admin_failed(message: telebot.types.Message, command: str, error: str, **payload) -> None:
    _log_event(
        "admin_command_failed",
        chat_id=message.chat.id,
        level="ERROR",
        safe_message="Admin command failed",
        command=command,
        admin_chat_id=message.chat.id,
        error=error,
        **payload,
    )


def _read_event_entries(limit: int, levels: set[str] | None = None) -> list[dict]:
    today = datetime.now().date()
    paths = [
        EVENTS_DIR / f"{(today - timedelta(days=1)).isoformat()}.jsonl",
        EVENTS_DIR / f"{today.isoformat()}.jsonl",
    ]
    entries: list[dict] = []
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if levels and entry.get("level") not in levels:
                continue
            entries.append(entry)
    return entries[-limit:]


def _format_event_entry(entry: dict) -> str:
    timestamp = str(entry.get("timestamp") or "")
    time_part = timestamp[11:16] if len(timestamp) >= 16 else "??:??"
    parts = [
        time_part,
        str(entry.get("level") or "INFO"),
        str(entry.get("event") or "event"),
    ]
    for key, label in (("chat_id", "chat_id"), ("session_id", "session"), ("job_id", "job")):
        value = entry.get(key)
        if value is not None and value != "":
            parts.append(f"{label}={value}")
    message = entry.get("safe_message")
    if message:
        parts.append(str(message))
    return " ".join(parts)


def _events_today_stats() -> tuple[int, int]:
    path = EVENTS_DIR / f"{datetime.now().date().isoformat()}.jsonl"
    if not path.exists():
        return 0, 0
    total = 0
    warning_or_error = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        total += 1
        if entry.get("level") in {"WARNING", "ERROR"}:
            warning_or_error += 1
    return total, warning_or_error


def _read_session_file_for_admin(path: Path) -> tuple[int | None, dict | None, str | None]:
    try:
        chat_id = int(path.stem)
    except ValueError:
        chat_id = None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        _log_event(
            "sessions_corrupt_file_detected",
            chat_id=chat_id,
            level="WARNING",
            safe_message="Corrupt session file detected by /sessions",
            path=str(path),
            error=str(exc),
        )
        return chat_id, None, "corrupt"
    if chat_id is not None:
        data = _normalize_session(chat_id, data)
    return chat_id, data, None


def _session_sort_key(item: tuple[int | None, dict | None, str | None]) -> datetime:
    _chat_id, session, _error = item
    if not session:
        return datetime.min
    return _parse_dt(session.get("updated_at") or session.get("status_changed_at")) or datetime.min


def _session_age_text(session: dict | None) -> str:
    if not session:
        return "unknown"
    start = _parse_dt(session.get("updated_at") or session.get("status_changed_at"))
    if not start:
        return "unknown"
    return _format_timedelta(datetime.now() - start)


def _session_rows(limit: int = 20) -> tuple[list[str], int]:
    items = [_read_session_file_for_admin(path) for path in SESSIONS_DIR.glob("*.json")]
    items.sort(key=_session_sort_key, reverse=True)
    rows: list[str] = []
    for chat_id, session, error in items[:limit]:
        if error == "corrupt":
            rows.append(f"- chat_id={chat_id or 'unknown'} status=corrupt")
            continue
        if not session:
            continue
        reason = _stale_reason(session)
        stale = "yes" if reason else "no"
        line = (
            f"- chat_id={chat_id} "
            f"session={session.get('session_id') or 'unknown'} "
            f"project={session.get('project_name') or 'не задан'} "
            f"status={session.get('status')} "
            f"pdfs={len(session.get('pdfs', []))} "
            f"updated_at={session.get('updated_at') or 'нет'} "
            f"age={_session_age_text(session)} "
            f"stale_candidate={stale}"
        )
        if reason:
            line += f" reason={reason}"
        rows.append(line)
    return rows, len(items)


def _recover_sessions_admin() -> dict:
    checked = 0
    archived_stale = 0
    corrupt_archived = 0
    active_left = 0
    errors = 0
    for path in sorted(SESSIONS_DIR.glob("*.json")):
        try:
            chat_id = int(path.stem)
        except ValueError:
            errors += 1
            continue
        lock = get_chat_lock(chat_id)
        with lock:
            if not path.exists():
                continue
            checked += 1
            try:
                try:
                    json.loads(path.read_text(encoding="utf-8"))
                except Exception:
                    _load_session(chat_id)
                    corrupt_archived += 1
                    continue
                session = _load_session(chat_id)
                before_exists = _session_path(chat_id).exists()
                recovered = _recover_stale_session_locked(chat_id, session)
                after_exists = _session_path(chat_id).exists()
                if before_exists and not after_exists and recovered is None:
                    archived_stale += 1
                elif after_exists:
                    active_left += 1
            except Exception as exc:
                errors += 1
                _log_event(
                    "recover_sessions_error",
                    chat_id=chat_id,
                    level="ERROR",
                    safe_message="Manual recovery failed for session",
                    error=str(exc),
                )
    return {
        "checked": checked,
        "archived_stale": archived_stale,
        "corrupt_archived": corrupt_archived,
        "active_left": active_left,
        "errors": errors,
    }


# ── admin commands ─────────────────────────────────────────────────────────

@bot.message_handler(commands=["admin_help"])
def cmd_admin_help(message: telebot.types.Message) -> None:
    if not _require_admin_access(message, "/admin_help"):
        return
    _admin_started(message, "/admin_help")
    bot.reply_to(message,
        "/admin_status — состояние процесса бота\n"
        "/sessions — сводка по чатам пользователей\n"
        "/sessions <chat_id> — подробности по конкретному чату\n"
        "/active_sessions — активные legacy-сессии загрузки\n"
        "/reset_session <chat_id> — аварийно архивировать и сбросить session\n"
        "/recover_sessions — вручную запустить recovery старых sessions\n"
        "/logs — последние события\n"
        "/tail_errors — последние ошибки\n"
        "/job_status <job_id> — статус конкретного job\n"
        "/export_logs [today|yesterday|7d|all] — Excel-диагностика\n"
        "/recreate <job_id> — пересобрать Google Sheet из последнего JSON\n\n"
        "Legacy PDF-команды, не основной сценарий:\n"
        "/done — запустить старую обработку после загрузки PDF\n"
        "/cancel — отменить старую PDF-загрузку\n"
        "/rerun <job_id> — legacy-перепарсинг PDF\n"
        "/confirm_rerun <job_id> — подтвердить legacy-перепарсинг PDF"
    )
    _admin_completed(message, "/admin_help")


@bot.message_handler(commands=["admin_status"])
def cmd_admin_status(message: telebot.types.Message) -> None:
    if not _require_admin_access(message, "/admin_status"):
        return
    _admin_started(message, "/admin_status")
    rows, total_sessions = _session_rows(limit=1000)
    status_counts: dict[str, int] = {}
    stale_candidates = 0
    for path in SESSIONS_DIR.glob("*.json"):
        chat_id, session, error = _read_session_file_for_admin(path)
        if error or not session:
            status_counts["corrupt"] = status_counts.get("corrupt", 0) + 1
            continue
        status = session.get("status") or "unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
        if _stale_reason(session):
            stale_candidates += 1
    events_today, warnings_today = _events_today_stats()
    disk = shutil.disk_usage(REPO_ROOT)
    uptime = _format_timedelta(datetime.now() - BOT_STARTED_AT)
    status_lines = "\n".join(f"- {key}: {value}" for key, value in sorted(status_counts.items())) or "- none: 0"
    text = (
        "Bot status: OK\n"
        f"Started at: {BOT_STARTED_AT.isoformat(timespec='seconds')}\n"
        f"Uptime: {uptime}\n"
        f"Repo root: {REPO_ROOT}\n"
        f"Data dir: {DATA_DIR}\n"
        f"Git commit: {_get_git_commit()}\n"
        f"Allowed users: {len(ALLOWED_CHAT_IDS)}\n"
        f"Admin users: {len(ADMIN_CHAT_IDS)}\n"
        f"Allow all users: {'yes' if ALLOW_ALL_USERS else 'no'}\n\n"
        f"Active sessions: {total_sessions}\n"
        f"{status_lines}\n"
        f"- stale candidates: {stale_candidates}\n\n"
        f"Events today: {events_today}\n"
        f"Warnings/errors today: {warnings_today}\n\n"
        "Disk:\n"
        f"- free: {_format_bytes(disk.free)}\n"
        f"- used: {_format_bytes(disk.used)}\n"
        f"- total: {_format_bytes(disk.total)}"
    )
    bot.reply_to(message, text[:4000])
    _admin_completed(message, "/admin_status")


@bot.message_handler(commands=["active_sessions"])
def cmd_active_sessions(message: telebot.types.Message) -> None:
    if not _require_admin_access(message, "/active_sessions"):
        return
    _admin_started(message, "/active_sessions")
    rows, total = _session_rows(limit=20)
    if not rows:
        text = "Активных загрузок PDF сейчас нет."
    else:
        text = "Активные загрузки PDF:\n" + "\n".join(rows)
        if total > 20:
            text += f"\n\nПоказаны первые 20 из {total}."
    bot.reply_to(message, text[:4000])
    _admin_completed(message, "/active_sessions", total_sessions=total)


# ── /sessions helpers ───────────────────────────────────────────────────────

def _session_pdf_count(session: dict) -> int:
    pdfs = session.get("pdfs")
    if isinstance(pdfs, list):
        return len(pdfs)
    return int(session.get("pdf_count") or 0)


_CHAT_STATE_MAP: dict[str, str] = {
    "collecting": "active_upload",
    "done_requested": "done_requested",
    "queued": "queued",
    "processing": "processing",
    "failed": "failed",
    "cancelled": "cancelled",
    "stale": "stale",
    "completed": "idle",
}

_NEXT_ACTION: dict[str, str] = {
    "active_upload":      "пользователь отправляет PDF, ждём /done",
    "done_requested":     "команда /done принята, ждём запуск обработки",
    "queued":             "команда /done принята, ждём запуск обработки",
    "processing":         "парсер работает",
    "waiting_for_review": "ждём проверку Google Sheet, потом /build",
    "failed":             "ошибка, смотреть /tail_errors или /export_logs",
    "cancelled":          "загрузка отменена",
    "stale":              "session устарела/заархивирована",
    "idle":               "нет активной работы",
}


def _archive_latest_by_chat() -> dict[int, tuple[datetime, dict]]:
    """Return {chat_id: (archive_dt, session_data)} for the latest archive per chat."""
    latest: dict[int, tuple[datetime, dict]] = {}
    for path in SESSION_BACKUPS_DIR.glob("*.json"):
        parts = path.stem.split("_")
        try:
            chat_id = int(parts[0])
        except (ValueError, IndexError):
            continue
        try:
            archive_dt = datetime.strptime(parts[-2] + parts[-1], "%Y%m%d%H%M%S")
        except (ValueError, IndexError):
            archive_dt = datetime.fromtimestamp(path.stat().st_mtime)
        if chat_id not in latest or archive_dt > latest[chat_id][0]:
            try:
                data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                continue
            if isinstance(data, dict):
                latest[chat_id] = (archive_dt, data)
    return latest


def _events_last_ts_by_chat() -> dict[int, datetime]:
    """Return {chat_id: latest_event_datetime} from all JSONL event files."""
    result: dict[int, datetime] = {}
    for jsonl_path in sorted(EVENTS_DIR.glob("*.jsonl")):
        try:
            text = jsonl_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            try:
                chat_id = int(ev.get("chat_id") or 0)
            except (ValueError, TypeError):
                continue
            if not chat_id:
                continue
            ts = _parse_dt(ev.get("timestamp"))
            if ts and (chat_id not in result or ts > result[chat_id]):
                result[chat_id] = ts
    return result


def _build_chat_summary() -> list[dict]:
    """
    Collect per-chat state from active sessions, archives, and events.
    Returns list sorted by last_activity_at desc.
    """
    chats: dict[int, dict] = {}

    # Active sessions (highest priority)
    for path in SESSIONS_DIR.glob("*.json"):
        cid, session, error = _read_session_file_for_admin(path)
        if cid is None:
            continue
        if error == "corrupt" or not session:
            chats[cid] = {"chat_id": cid, "state": "corrupt", "last_activity_at": None,
                          "project_name": "", "pdf_count": 0, "job_id": "",
                          "spreadsheet_url": "", "last_error_type": "", "last_error": ""}
            continue
        status = session.get("status", "collecting")
        state = _CHAT_STATE_MAP.get(status, status)
        chats[cid] = {
            "chat_id": cid,
            "state": state,
            "last_activity_at": _parse_dt(session.get("updated_at") or session.get("status_changed_at")),
            "project_name": session.get("project_name") or "",
            "pdf_count": _session_pdf_count(session),
            "job_id": session.get("job_id") or "",
            "spreadsheet_url": session.get("spreadsheet_url") or "",
            "last_error_type": session.get("last_error_type") or "",
            "last_error": session.get("last_error") or "",
        }

    # Latest archived sessions (for chats not already in active)
    for cid, (archive_dt, data) in _archive_latest_by_chat().items():
        if cid in chats:
            continue
        status = data.get("status", "")
        if status == "completed" and (data.get("job_id") or data.get("spreadsheet_url")):
            state = "waiting_for_review"
        else:
            state = _CHAT_STATE_MAP.get(status, "idle")
        chats[cid] = {
            "chat_id": cid,
            "state": state,
            "last_activity_at": archive_dt,
            "project_name": data.get("project_name") or "",
            "pdf_count": _session_pdf_count(data),
            "job_id": data.get("job_id") or "",
            "spreadsheet_url": data.get("spreadsheet_url") or "",
            "last_error_type": data.get("last_error_type") or "",
            "last_error": data.get("last_error") or "",
        }

    # Events: fill in chats not seen in files, and update missing last_activity_at
    for cid, ts in _events_last_ts_by_chat().items():
        if cid not in chats:
            chats[cid] = {"chat_id": cid, "state": "idle", "last_activity_at": ts,
                          "project_name": "", "pdf_count": 0, "job_id": "",
                          "spreadsheet_url": "", "last_error_type": "", "last_error": ""}
        elif chats[cid]["last_activity_at"] is None:
            chats[cid]["last_activity_at"] = ts

    return sorted(chats.values(), key=lambda c: c["last_activity_at"] or datetime.min, reverse=True)


def _format_chat_card(cid: int) -> str:
    """Detailed card for a single chat_id."""
    lines: list[str] = [f"chat_id={cid}"]

    # Active session
    active: dict | None = None
    apath = _session_path(cid)
    if apath.exists():
        _, active, _ = _read_session_file_for_admin(apath)

    if active:
        status = active.get("status", "unknown")
        lines += [
            f"active_session: yes (status={status})",
            f"updated_at: {active.get('updated_at') or 'нет'}",
            f"project_name: {active.get('project_name') or 'не задан'}",
            f"pdf_count: {_session_pdf_count(active)}",
            f"job_id: {active.get('job_id') or 'нет'}",
            f"spreadsheet_url: {active.get('spreadsheet_url') or 'нет'}",
            f"last_error_type: {active.get('last_error_type') or 'нет'}",
        ]
        if active.get("last_error"):
            lines.append(f"last_error: {str(active['last_error'])[:200]}")
    else:
        lines.append("active_session: нет")

    # Latest archived session
    archive_map = _archive_latest_by_chat()
    if cid in archive_map:
        arc_dt, arc = archive_map[cid]
        arc_status = arc.get("status", "unknown")
        lines += [
            "",
            f"last archived: status={arc_status}",
            f"archive_time: {arc_dt.isoformat(timespec='seconds')}",
            f"project_name: {arc.get('project_name') or 'не задан'}",
            f"pdf_count: {_session_pdf_count(arc)}",
            f"job_id: {arc.get('job_id') or 'нет'}",
            f"spreadsheet_url: {arc.get('spreadsheet_url') or 'нет'}",
            f"last_error_type: {arc.get('last_error_type') or 'нет'}",
        ]
        if arc.get("last_error"):
            lines.append(f"last_error: {str(arc['last_error'])[:200]}")
    else:
        lines += ["", "last archived: нет"]

    # State and next action
    summary = _build_chat_summary()
    chat_data = next((c for c in summary if c["chat_id"] == cid), None)
    if chat_data:
        state = chat_data["state"]
        last = chat_data["last_activity_at"]
        last_str = last.strftime("%Y-%m-%d %H:%M") if last else "нет"
        lines += [
            "",
            f"state: {state}",
            f"last_activity_at: {last_str}",
            f"next: {_NEXT_ACTION.get(state, state)}",
        ]

    return "\n".join(lines)


@bot.message_handler(commands=["sessions"])
def cmd_sessions(message: telebot.types.Message) -> None:
    if not _require_admin_access(message, "/sessions"):
        return
    _admin_started(message, "/sessions")

    parts = message.text.strip().split(maxsplit=1)

    if len(parts) > 1:
        # Detailed card for one chat_id
        try:
            target = int(parts[1].strip())
        except ValueError:
            bot.reply_to(message, "chat_id должен быть числом.")
            _admin_failed(message, "/sessions", "invalid chat_id")
            return
        text = _format_chat_card(target)
        bot.reply_to(message, text[:4000])
        _admin_completed(message, "/sessions", target_chat_id=target)
        return

    # Summary list
    chats = _build_chat_summary()
    MAX_CHATS = 20
    if not chats:
        bot.reply_to(message, "Данных по чатам нет.")
        _admin_completed(message, "/sessions", total_chats=0)
        return

    lines = ["Чаты пользователей:"]
    for i, c in enumerate(chats[:MAX_CHATS], 1):
        last = c["last_activity_at"]
        last_str = last.strftime("%Y-%m-%d %H:%M") if last else "нет"
        line = (
            f"{i}. chat_id={c['chat_id']}\n"
            f"   state={c['state']}\n"
            f"   last={last_str}"
        )
        if c["project_name"]:
            line += f"\n   project={c['project_name']}"
        if c["pdf_count"]:
            line += f"\n   pdfs={c['pdf_count']}"
        if c["job_id"]:
            line += f"\n   job={c['job_id']}"
        line += f"\n   next={_NEXT_ACTION.get(c['state'], c['state'])}"
        lines.append(line)

    if len(chats) > MAX_CHATS:
        lines.append(f"\nПоказаны первые {MAX_CHATS} из {len(chats)}.")

    bot.reply_to(message, "\n".join(lines)[:4000])
    _admin_completed(message, "/sessions", total_chats=len(chats))


@bot.message_handler(commands=["reset_session"])
def cmd_reset_session(message: telebot.types.Message) -> None:
    if not _require_admin_access(message, "/reset_session"):
        return
    _admin_started(message, "/reset_session")
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Укажите chat_id: /reset_session <chat_id>")
        _admin_failed(message, "/reset_session", "missing chat_id")
        return
    try:
        target_chat_id = int(parts[1].strip())
    except ValueError:
        bot.reply_to(message, "chat_id должен быть числом.")
        _admin_failed(message, "/reset_session", "invalid chat_id")
        return
    lock = get_chat_lock(target_chat_id)
    with lock:
        path = _session_path(target_chat_id)
        if not path.exists():
            bot.reply_to(message, "Нет активной session.")
            _admin_completed(message, "/reset_session", target_chat_id=target_chat_id, result="not_found")
            return
        session = _load_session(target_chat_id)
        _set_status(session, "cancelled")
        session["cancelled_at"] = _now()
        session["processing_started"] = False
        session["done_requested"] = False
        session["reset_by_admin_chat_id"] = message.chat.id
        session["reset_at"] = _now()
        session["reset_reason"] = "admin_reset"
        _save_session(target_chat_id, session)
        _log_event(
            "admin_reset_session",
            chat_id=target_chat_id,
            session=session,
            level="WARNING",
            safe_message="Session reset by admin",
            admin_chat_id=message.chat.id,
            target_chat_id=target_chat_id,
        )
        _archive_session(target_chat_id, session, "admin_reset")
        _clear_session(target_chat_id)
    bot.reply_to(message, f"Session для chat_id={target_chat_id} сброшена и архивирована.")
    _admin_completed(message, "/reset_session", target_chat_id=target_chat_id, result="archived")


@bot.message_handler(commands=["recover_sessions"])
def cmd_recover_sessions(message: telebot.types.Message) -> None:
    if not _require_admin_access(message, "/recover_sessions"):
        return
    _admin_started(message, "/recover_sessions")
    _log_event(
        "recover_sessions_started",
        chat_id=message.chat.id,
        safe_message="Manual stale recovery started",
        admin_chat_id=message.chat.id,
    )
    summary = _recover_sessions_admin()
    _log_event(
        "recover_sessions_completed",
        chat_id=message.chat.id,
        safe_message="Manual stale recovery completed",
        admin_chat_id=message.chat.id,
        **summary,
    )
    bot.reply_to(message,
        "Recovery завершён.\n"
        f"- checked: {summary['checked']}\n"
        f"- archived_stale: {summary['archived_stale']}\n"
        f"- corrupt_archived: {summary['corrupt_archived']}\n"
        f"- active_left: {summary['active_left']}\n"
        f"- errors: {summary['errors']}"
    )
    _admin_completed(message, "/recover_sessions", **summary)


@bot.message_handler(commands=["logs"])
def cmd_logs(message: telebot.types.Message) -> None:
    if not _require_admin_access(message, "/logs"):
        return
    _admin_started(message, "/logs")
    parts = message.text.strip().split(maxsplit=1)
    limit = 20
    if len(parts) > 1:
        try:
            limit = min(max(int(parts[1].strip()), 1), 50)
        except ValueError:
            pass
    entries = _read_event_entries(limit)
    text = "Последние события:\n" + "\n".join(_format_event_entry(entry) for entry in entries) if entries else "Events не найдены."
    bot.reply_to(message, text[:4000])
    _admin_completed(message, "/logs", rows=len(entries))


@bot.message_handler(commands=["tail_errors"])
def cmd_tail_errors(message: telebot.types.Message) -> None:
    if not _require_admin_access(message, "/tail_errors"):
        return
    _admin_started(message, "/tail_errors")
    parts = message.text.strip().split(maxsplit=1)
    limit = 10
    if len(parts) > 1:
        try:
            limit = min(max(int(parts[1].strip()), 1), 30)
        except ValueError:
            pass
    entries = _read_event_entries(limit, levels={"WARNING", "ERROR"})
    if entries:
        text = "Последние WARNING/ERROR:\n" + "\n".join(_format_event_entry(entry) for entry in entries)
    else:
        text = "Ошибок в events не найдено."
    bot.reply_to(message, text[:4000])
    _admin_completed(message, "/tail_errors", rows=len(entries))


@bot.message_handler(commands=["job_status"])
def cmd_job_status(message: telebot.types.Message) -> None:
    if not _require_admin_access(message, "/job_status"):
        return
    _admin_started(message, "/job_status")
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Укажите job_id: /job_status <job_id>")
        _admin_failed(message, "/job_status", "missing job_id")
        return
    job_id = parts[1].strip()
    cmd = [_python(), str(SHOW_STATUS), "--job-id", job_id]
    try:
        result = _run(cmd, TIMEOUTS["status"])
    except subprocess.TimeoutExpired:
        bot.reply_to(message, "⏱ Превышено время ожидания.")
        _admin_failed(message, "/job_status", "timeout", job_id=job_id)
        return
    _log(message.chat.id, "job_status", result.returncode, result.stdout, result.stderr)
    output = result.stdout.strip() or result.stderr.strip() or "Нет данных."
    bot.reply_to(message, output[:4000])
    _admin_completed(message, "/job_status", job_id=job_id, returncode=result.returncode)


# ── /recreate ──────────────────────────────────────────────────────────────
@bot.message_handler(commands=["recreate"])
def cmd_recreate(message: telebot.types.Message) -> None:
    if not _require_user_access(message, "/recreate"):
        return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Укажите job_id: /recreate <job_id>")
        return
    job_id = parts[1].strip()

    if not _user_can_access_job(message.chat.id, job_id):
        _deny_job_access(message, job_id)
        return

    _log_event("recreate_started", chat_id=message.chat.id,
               safe_message="Recreate started", job_id=job_id)
    bot.reply_to(message, "Пересоздаю Google Sheet...")

    # JSON-flow jobs (job_id/extraction_output_bot_*.json under CHAT_EXTRACTION_OUTPUTS_DIR)
    # never went through recreate_review_sheet.py (that script only knows the PDF-flow's
    # earthworks_parser_google_stage1/data/jobs/<job_id> layout - it fails with "Job directory
    # not found" for every JSON-flow job, confirmed 2026-08-26 on a real /recreate attempt).
    # Handle those here directly with the same populate+publish helpers the upload handler uses,
    # instead of shelling out to a script that structurally cannot find them.
    json_job_dir, resolve_error = _resolve_json_job_dir(job_id)
    if resolve_error:
        bot.reply_to(message, resolve_error)
        _log_event("recreate_failed", chat_id=message.chat.id, level="ERROR",
                   safe_message="Recreate suffix match ambiguous", job_id=job_id)
        return
    if json_job_dir is not None:
        # Use the resolved directory name from here on, not the (possibly suffix-typed) input -
        # _update_user_job_url below keys on an exact job_id match against the registry, which
        # was populated with the full name at upload time; passing the truncated typed value
        # silently failed to find a row to update (confirmed 2026-08-26: the registry kept
        # pointing at the pre-recreate Sheet URL after a "successful" /recreate for this reason).
        job_id = json_job_dir.name
        extraction_files = sorted(json_job_dir.glob("extraction_output_bot_*.json"))
        if not extraction_files:
            bot.reply_to(message, f"В папке job {job_id} нет extraction JSON (extraction_output_bot_*.json).")
            _log_event("recreate_failed", chat_id=message.chat.id, level="ERROR",
                       safe_message="Recreate found job dir but no extraction JSON", job_id=job_id)
            return
        latest_json = extraction_files[-1]
        try:
            latest_extraction = json.loads(latest_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            bot.reply_to(message, f"Не удалось прочитать последний extraction JSON: {exc}")
            return
        job_record = _user_job_record(message.chat.id, job_id) or {}
        project_label = project_label_from_extraction(latest_extraction, latest_json.name)
        created_at = job_record.get("created_at") or _now()
        workbook_target = json_job_dir / "review_workbook.xlsx"
        wb_result = _run_populate_workbook(latest_json, workbook_target)
        _log(message.chat.id, "recreate_populate_workbook", wb_result.returncode, wb_result.stdout, wb_result.stderr)
        wb_info = _parse_json(wb_result.stdout)
        workbook_path = Path(wb_info["output_path"]) if wb_info and wb_info.get("output_path") else None
        if wb_result.returncode != 0 or not workbook_path or not workbook_path.exists():
            bot.reply_to(message, f"Не удалось собрать таблицу ⚠️\n\n{(wb_result.stderr or wb_result.stdout)[-500:]}")
            _log_event("recreate_failed", chat_id=message.chat.id, level="ERROR",
                       safe_message="Recreate (json flow) populate_workbook failed", job_id=job_id,
                       returncode=wb_result.returncode)
            return
        try:
            publish_result = _publish_review_workbook(
                workbook_path,
                title=review_sheet_title(project_label, created_at),
                folder_id=job_record.get("drive_folder_id", ""),
                folder_name=(
                    "" if job_record.get("drive_folder_id")
                    else project_drive_folder_name(project_label, created_at)
                ),
            )
        except Exception as exc:
            bot.reply_to(message, f"Таблица собрана локально, но публикация в Google упала ⚠️\n\n{exc}")
            _log_event("recreate_failed", chat_id=message.chat.id, level="ERROR",
                       safe_message="Recreate (json flow) publish raised", job_id=job_id, error=str(exc))
            return
        if publish_result.get("status") != "published":
            bot.reply_to(message, f"Публикация не удалась: {publish_result.get('reason', 'неизвестная причина')}")
            _log_event("recreate_failed", chat_id=message.chat.id, level="ERROR",
                       safe_message="Recreate (json flow) publish status not published", job_id=job_id,
                       reason=publish_result.get("reason"))
            return
        url = publish_result.get("url", "")
        folder_url = publish_result.get("drive_folder_url", "") or job_record.get("drive_folder_url", "")
        folder_line = f"\nПапка проекта: {folder_url}\n" if folder_url else ""
        bot.reply_to(
            message,
            f"Новая Google Sheet создана ✅\n{url}\n{folder_line}\nПарсер не запускался заново.",
        )
        _update_user_job_url(
            message.chat.id,
            job_id,
            url,
            drive_folder_id=publish_result.get("drive_folder_id", ""),
            drive_folder_name=publish_result.get("drive_folder_name", ""),
            drive_folder_url=folder_url,
        )
        _log_event("recreate_completed", chat_id=message.chat.id,
                   safe_message="Recreate (json flow) completed", job_id=job_id)
        return

    cmd = [
        _python(), str(RECREATE),
        "--job-id", job_id,
        "--sharing", "anyone_writer",
        "--reason", "telegram_recreate",
        "--json",
    ]
    try:
        result = _run(cmd, TIMEOUTS["recreate"])
    except subprocess.TimeoutExpired:
        bot.reply_to(message, "⏱ Превышено время ожидания (10 мин).")
        _log_event("recreate_failed", chat_id=message.chat.id, level="ERROR",
                   safe_message="Recreate timeout", job_id=job_id, error="timeout")
        return

    _log(message.chat.id, "recreate", result.returncode, result.stdout, result.stderr)

    if result.returncode != 0:
        bot.reply_to(message, f"Ошибка: {(result.stderr or result.stdout)[-500:]}")
        _log_event("recreate_failed", chat_id=message.chat.id, level="ERROR",
                   safe_message="Recreate command failed", job_id=job_id,
                   returncode=result.returncode)
        return

    data = _parse_json(result.stdout)
    url = (data or {}).get("new_google_sheet", {}).get("spreadsheet_url", "нет")
    bot.reply_to(message,
        f"Новая Google Sheet создана ✅\n{url}\n\nПарсер не запускался заново."
    )
    _update_user_job_url(message.chat.id, job_id, url)
    _log_event("recreate_completed", chat_id=message.chat.id,
               safe_message="Recreate completed", job_id=job_id,
               returncode=result.returncode)


# ── /rerun ─────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["rerun"])
def cmd_rerun(message: telebot.types.Message) -> None:
    if not _require_user_access(message, "/rerun"):
        return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Укажите job_id: /rerun <job_id>")
        return
    job_id = parts[1].strip()

    if not _user_can_access_job(message.chat.id, job_id):
        _deny_job_access(message, job_id)
        return

    bot.reply_to(message,
        f"Вы хотите заново запустить парсер для заказа:\n{job_id}\n\n"
        "Это может занять несколько минут и создаст новую Google Sheet.\n\n"
        "Для подтверждения отправьте:\n"
        f"/confirm_rerun {job_id}"
    )


# ── /confirm_rerun ──────────────────────────────────────────────────────────
@bot.message_handler(commands=["confirm_rerun"])
def cmd_confirm_rerun(message: telebot.types.Message) -> None:
    if not _require_user_access(message, "/confirm_rerun"):
        return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Укажите job_id: /confirm_rerun <job_id>")
        return
    job_id = parts[1].strip()

    if not _user_can_access_job(message.chat.id, job_id):
        _deny_job_access(message, job_id)
        return

    _log_event("rerun_started", chat_id=message.chat.id,
               safe_message="Rerun confirmed and started", job_id=job_id)
    bot.reply_to(message, "Запускаю парсер заново... Это может занять несколько минут.")

    cmd = [
        _python(), str(RERUN),
        "--job-id", job_id,
        "--sharing", "anyone_writer",
        "--reason", "telegram_rerun",
        "--json",
    ]
    try:
        result = _run(cmd, TIMEOUTS["rerun"])
    except subprocess.TimeoutExpired:
        bot.reply_to(message, "⏱ Превышено время ожидания (20 мин).")
        _log_event("rerun_failed", chat_id=message.chat.id, level="ERROR",
                   safe_message="Rerun timeout", job_id=job_id, error="timeout")
        return

    _log(message.chat.id, "rerun", result.returncode, result.stdout, result.stderr)

    if result.returncode != 0:
        data = _parse_json(result.stdout)
        if (data or {}).get("status") == "parser_failed":
            bot.reply_to(message,
                "Перепарсинг не удался.\n"
                "Старый parser_run и старая Google Sheet сохранены."
            )
        else:
            bot.reply_to(message, f"Ошибка: {(result.stderr or result.stdout)[-500:]}")
        _log_event("rerun_failed", chat_id=message.chat.id, level="ERROR",
                   safe_message="Rerun command failed", job_id=job_id,
                   returncode=result.returncode)
        return

    data = _parse_json(result.stdout) or {}
    new_run = data.get("new_parser_run", {}).get("run", "?")
    url     = data.get("new_google_sheet", {}).get("spreadsheet_url", "нет")
    bot.reply_to(message,
        f"PDF перепарсен заново ✅\n"
        f"Новый parser_run: {new_run}\n"
        f"Новая Google Sheet:\n{url}"
    )
    _update_user_job_url(message.chat.id, job_id, url)
    _log_event("rerun_completed", chat_id=message.chat.id,
               safe_message="Rerun completed", job_id=job_id,
               returncode=result.returncode)


# ── /export_logs ───────────────────────────────────────────────────────────
_EXPORT_LOGS_PERIODS = ("today", "yesterday", "7d", "all")


@bot.message_handler(commands=["export_logs"])
def cmd_export_logs(message: telebot.types.Message) -> None:
    if not _require_admin_access(message, "/export_logs"):
        return

    parts = message.text.strip().split(maxsplit=1)
    period = parts[1].strip().lower() if len(parts) > 1 else "today"

    if period not in _EXPORT_LOGS_PERIODS:
        bot.reply_to(message,
            "Неизвестный период. Используйте:\n"
            "/export_logs today\n"
            "/export_logs yesterday\n"
            "/export_logs 7d\n"
            "/export_logs all"
        )
        return

    _log_event(
        "export_logs_started",
        chat_id=message.chat.id,
        safe_message="Admin export_logs started",
        admin_chat_id=message.chat.id,
        period=period,
    )
    bot.reply_to(message, f"Готовлю выгрузку логов ({period})...")

    try:
        from log_exporter import export_logs_to_xlsx
        xlsx_path = export_logs_to_xlsx(
            period=period,
            events_dir=EVENTS_DIR,
            sessions_dir=SESSIONS_DIR,
            backups_dir=SESSION_BACKUPS_DIR,
            logs_dir=LOGS_DIR,
            output_dir=ADMIN_EXPORTS_DIR,
        )
        with open(xlsx_path, "rb") as f:
            bot.send_document(
                message.chat.id, f,
                caption=f"Готово ✅\nВыгрузка логов: {period}"
            )
        _log_event(
            "export_logs_completed",
            chat_id=message.chat.id,
            safe_message="Admin export_logs completed",
            admin_chat_id=message.chat.id,
            period=period,
            output_path=str(xlsx_path),
        )
    except Exception as exc:
        err_short = str(exc)[:300]
        bot.reply_to(message, f"Не удалось выгрузить логи ⚠️\n{err_short}")
        _log_event(
            "export_logs_failed",
            chat_id=message.chat.id,
            level="ERROR",
            safe_message="Admin export_logs failed",
            admin_chat_id=message.chat.id,
            period=period,
            error=str(exc)[:1000],
        )


def _send_message_safely(chat_id: int, text: str, event: str, session: dict | None = None) -> None:
    try:
        bot.send_message(chat_id, text)
    except Exception as exc:
        _log_event(
            event,
            chat_id=chat_id,
            session=session,
            level="WARNING",
            safe_message="Telegram recovery message failed",
            error=str(exc),
        )


def _recover_sessions_on_startup() -> None:
    for path in sorted(SESSIONS_DIR.glob("*.json")):
        try:
            chat_id = int(path.stem)
        except ValueError:
            continue
        lock = get_chat_lock(chat_id)
        with lock:
            if not path.exists():
                continue
            session = _load_session(chat_id)
            recovered = _recover_stale_session_locked(chat_id, session)
            if recovered is None:
                continue
            session = recovered
            status = session.get("status", "collecting")
            if status in {"done_requested", "queued"}:
                _set_status(session, "collecting")
                session["done_requested"] = False
                session["done_requested_at"] = None
                session["queued_at"] = None
                session["processing_started"] = False
                session["restart_recovered_at"] = _now()
                _save_session(chat_id, session)
                _log_event(
                    "session_restart_recovered",
                    chat_id=chat_id,
                    session=session,
                    safe_message="Session restored to collecting after bot restart",
                    previous_status=status,
                )
                message = (
                    "Бот перезапустился. Ваш PDF-набор сохранён.\n"
                    "Напишите /done, чтобы продолжить обработку."
                )
            elif status == "processing":
                _mark_failed(
                    session,
                    "bot_restarted_during_processing",
                    "Bot restarted while create_job was processing",
                )
                session["restart_recovered_at"] = _now()
                _save_session(chat_id, session)
                _log_event(
                    "session_restart_recovered",
                    chat_id=chat_id,
                    session=session,
                    level="WARNING",
                    safe_message="Processing session marked failed after bot restart",
                    previous_status=status,
                )
                message = (
                    "Бот перезапустился во время обработки.\n"
                    "PDF-набор сохранён. Напишите /done, чтобы запустить обработку заново."
                )
            else:
                continue
        _send_message_safely(chat_id, message, "session_restart_recovery_message_failed", session)


# ── main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if not ALLOW_ALL_USERS and not ALLOWED_CHAT_IDS:
        print(
            "ERROR: TELEGRAM_ALLOWED_CHAT_IDS is not set. "
            "For local testing set ALLOW_ALL_USERS=true explicitly.",
            file=sys.stderr,
        )
        sys.exit(1)
    print("Bot started. Polling...")
    if TELEGRAM_PROXY_ENABLED:
        print("Telegram proxy enabled.")
    _log_event("bot_started", safe_message="Telegram bot process started")
    if ALLOW_ALL_USERS:
        print("WARNING: ALLOW_ALL_USERS=true — all users can access the bot.", file=sys.stderr)
        _log_event(
            "access_mode_allow_all",
            level="WARNING",
            safe_message="ALLOW_ALL_USERS enabled; all users can access the bot",
        )
    if not ADMIN_CHAT_IDS:
        print("WARNING: TELEGRAM_ADMIN_CHAT_IDS is not set — admin commands are disabled.", file=sys.stderr)
    admins_not_allowed = sorted(ADMIN_CHAT_IDS - ALLOWED_CHAT_IDS)
    if admins_not_allowed and not ALLOW_ALL_USERS:
        print(
            f"WARNING: admin chat IDs are not in TELEGRAM_ALLOWED_CHAT_IDS: {admins_not_allowed}",
            file=sys.stderr,
        )
        _log_event(
            "admin_not_in_allowed",
            level="WARNING",
            safe_message="Admin chat IDs are allowed through admin list but absent from user allowlist",
            admin_chat_ids=admins_not_allowed,
        )
    _recover_sessions_on_startup()
    if ALLOWED_CHAT_IDS:
        print(f"Allowed chat IDs: {ALLOWED_CHAT_IDS}")
    if ADMIN_CHAT_IDS:
        print(f"Admin chat IDs: {ADMIN_CHAT_IDS}")

    # 2026-08-25 (repetition plan фаза 6): telebot's own infinity_polling() already retries
    # `Exception`s raised inside its request loop (see telebot/__init__.py, try/except around
    # self.polling() with a 3s sleep) - most of the network ConnectionErrors seen in production
    # logs today were already handled that way, no process restart. But real logs from today
    # still show a handful of full process deaths (launchd had to relaunch, "Bot started"
    # printed fresh each time) - something occasionally escapes even that inner retry (a
    # BaseException, or an exception raised outside self.polling()'s own try, e.g. during
    # startup/session recovery or inside a handler callback thread). Wrap the whole call in one
    # more outer retry loop so an ordinary network hiccup never needs the OS-level launchd
    # restart (which loses in-memory retry state and looks like a crash in the logs even when
    # nothing was actually broken) - only a deliberate Ctrl-C/SIGTERM should end the process.
    consecutive_failures = 0
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
            break  # infinity_polling only returns on bot.stop_polling(), a deliberate stop
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as exc:  # noqa: BLE001 - this is the last line of defense, by design
            consecutive_failures += 1
            backoff = min(60, 3 * consecutive_failures)
            print(
                f"ERROR: infinity_polling escaped with {type(exc).__name__}: {exc} "
                f"- restarting polling in-process in {backoff}s (attempt {consecutive_failures})",
                file=sys.stderr,
            )
            _log_event(
                "polling_escaped_exception",
                level="ERROR",
                safe_message="infinity_polling raised past its own internal retry loop",
                exception_type=type(exc).__name__,
                error=str(exc),
                consecutive_failures=consecutive_failures,
            )
            time.sleep(backoff)
