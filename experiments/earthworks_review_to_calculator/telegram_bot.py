from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import telebot

# ── paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
sys.path.insert(0, str(BASE_DIR))  # so job_locator / job_state are importable

DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "telegram_uploads"
LOGS_DIR = DATA_DIR / "telegram_logs"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

CREATE_JOB = BASE_DIR / "create_job_from_pdf.py"
RECREATE    = BASE_DIR / "recreate_review_sheet.py"
RERUN       = BASE_DIR / "rerun_parser.py"
BUILD_JOB   = BASE_DIR / "build_job.py"
SHOW_STATUS = BASE_DIR / "show_job_status.py"

TIMEOUTS = {
    "create_job": 1200,
    "rerun":      1200,
    "recreate":    600,
    "build":       600,
    "status":      120,
}

# ── config ─────────────────────────────────────────────────────────────────
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
if not TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN is not set.", file=sys.stderr)
    sys.exit(1)

_raw_ids = os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "")
ALLOWED_CHAT_IDS: set[int] = (
    {int(x.strip()) for x in _raw_ids.split(",") if x.strip()}
    if _raw_ids else set()
)
if not ALLOWED_CHAT_IDS:
    print("WARNING: TELEGRAM_ALLOWED_CHAT_IDS is not set — all users can access the bot.")

bot = telebot.TeleBot(TOKEN, parse_mode=None)

# ── helpers ────────────────────────────────────────────────────────────────
def _python() -> str:
    return sys.executable


def _allowed(chat_id: int) -> bool:
    return not ALLOWED_CHAT_IDS or chat_id in ALLOWED_CHAT_IDS


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


# ── /start ─────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["start"])
def cmd_start(message: telebot.types.Message) -> None:
    if not _allowed(message.chat.id):
        return
    bot.reply_to(message,
        "Пришлите PDF проекта.\n"
        "Я создам заказ, запущу парсер и пришлю ссылку на Google Sheet для проверки.\n\n"
        "После проверки таблицы:\n"
        "/build <job_id> — собрать Excel\n"
        "/status <job_id> — статус заказа\n"
        "/recreate <job_id> — пересоздать Google Sheet без парсера\n"
        "/rerun <job_id> — заново перепарсить тот же PDF"
    )


# ── PDF ────────────────────────────────────────────────────────────────────
@bot.message_handler(content_types=["document"])
def handle_document(message: telebot.types.Message) -> None:
    if not _allowed(message.chat.id):
        return

    doc = message.document
    if not (doc.file_name or "").lower().endswith(".pdf"):
        bot.reply_to(message, "Пожалуйста, отправьте PDF-файл.")
        return

    bot.reply_to(message,
        "PDF получил ✅\n"
        "Создаю заказ и запускаю парсер. Это может занять несколько минут..."
    )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    upload_dir = UPLOADS_DIR / str(message.chat.id) / ts
    upload_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = upload_dir / doc.file_name

    file_info = bot.get_file(doc.file_id)
    pdf_path.write_bytes(bot.download_file(file_info.file_path))

    project_name = pdf_path.stem.replace("_", " ").replace("-", " ").strip() or "Проект"

    cmd = [
        _python(), str(CREATE_JOB),
        "--project-name", project_name,
        "--pdf", str(pdf_path),
        "--sharing", "anyone_writer",
        "--json",
    ]
    try:
        result = _run(cmd, TIMEOUTS["create_job"])
    except subprocess.TimeoutExpired:
        bot.reply_to(message, "⏱ Превышено время ожидания (20 мин). Попробуйте позже.")
        return

    _log(message.chat.id, "create_job", result.returncode, result.stdout, result.stderr)

    if result.returncode != 0:
        bot.reply_to(message,
            f"Ошибка при создании заказа.\n\n{(result.stderr or result.stdout)[-800:]}"
        )
        return

    data = _parse_json(result.stdout)
    if data is None:
        bot.reply_to(message,
            f"Заказ создан, но не удалось прочитать результат.\n\n{result.stdout[:500]}"
        )
        return

    job_id   = data.get("job_id", "?")
    url      = data.get("spreadsheet_url", "нет")
    pr       = data.get("parser_run", {})
    cands    = pr.get("candidates_count", "?")
    errors   = pr.get("errors", [])

    text = (
        f"Готово ✅\n\n"
        f"Заказ: {job_id}\n"
        f"Таблица для проверки:\n{url}\n\n"
        f"Парсер нашёл кандидатов: {cands}"
    )
    if errors:
        text += f"\n⚠️ Ошибки парсера: {len(errors)}"
    text += f"\n\nПроверьте и заполните Google Sheet.\nПосле проверки отправьте:\n/build {job_id}"

    bot.reply_to(message, text)


# ── /status ────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["status"])
def cmd_status(message: telebot.types.Message) -> None:
    if not _allowed(message.chat.id):
        return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Укажите job_id: /status <job_id>")
        return
    job_id = parts[1].strip()

    cmd = [_python(), str(SHOW_STATUS), "--job-id", job_id]
    try:
        result = _run(cmd, TIMEOUTS["status"])
    except subprocess.TimeoutExpired:
        bot.reply_to(message, "⏱ Превышено время ожидания.")
        return

    _log(message.chat.id, "status", result.returncode, result.stdout, result.stderr)

    output = result.stdout.strip() or result.stderr.strip() or "Нет данных."
    bot.reply_to(message, output[:4000])


# ── /build ─────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["build"])
def cmd_build(message: telebot.types.Message) -> None:
    if not _allowed(message.chat.id):
        return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Укажите job_id: /build <job_id>")
        return
    job_id = parts[1].strip()

    bot.reply_to(message, "Собираю смету... Это может занять несколько минут.")

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
        bot.reply_to(message,
            "Смету пока нельзя собрать: не хватает данных в Google Sheet.\n"
            "Проверьте и заполните таблицу, затем повторите:\n"
            f"/build {job_id}"
        )
        return

    excel_path = _find_excel(job_id)
    if excel_path and excel_path.exists():
        with open(excel_path, "rb") as f:
            bot.send_document(message.chat.id, f, caption=f"Смета готова ✅\nJob: {job_id}")
    else:
        bot.reply_to(message, f"Смета собрана ✅\nJob: {job_id}\n\nExcel не найден локально.")


# ── /recreate ──────────────────────────────────────────────────────────────
@bot.message_handler(commands=["recreate"])
def cmd_recreate(message: telebot.types.Message) -> None:
    if not _allowed(message.chat.id):
        return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Укажите job_id: /recreate <job_id>")
        return
    job_id = parts[1].strip()

    bot.reply_to(message, "Пересоздаю Google Sheet...")

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
        return

    _log(message.chat.id, "recreate", result.returncode, result.stdout, result.stderr)

    if result.returncode != 0:
        bot.reply_to(message, f"Ошибка: {(result.stderr or result.stdout)[-500:]}")
        return

    data = _parse_json(result.stdout)
    url = (data or {}).get("new_google_sheet", {}).get("spreadsheet_url", "нет")
    bot.reply_to(message,
        f"Новая Google Sheet создана ✅\n{url}\n\nПарсер не запускался заново."
    )


# ── /rerun ─────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["rerun"])
def cmd_rerun(message: telebot.types.Message) -> None:
    if not _allowed(message.chat.id):
        return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Укажите job_id: /rerun <job_id>")
        return
    job_id = parts[1].strip()

    bot.reply_to(message, "Перезапускаю парсер... Это может занять несколько минут.")

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
        return

    data = _parse_json(result.stdout) or {}
    new_run = data.get("new_parser_run", {}).get("run", "?")
    url     = data.get("new_google_sheet", {}).get("spreadsheet_url", "нет")
    bot.reply_to(message,
        f"PDF перепарсен заново ✅\n"
        f"Новый parser_run: {new_run}\n"
        f"Новая Google Sheet:\n{url}"
    )


# ── main ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    print("Bot started. Polling...")
    if ALLOWED_CHAT_IDS:
        print(f"Allowed chat IDs: {ALLOWED_CHAT_IDS}")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
