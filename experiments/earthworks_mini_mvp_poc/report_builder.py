from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from earthworks_input_builder import review_statistics
from source_paths import (
    CALCULATE_BLOCKED_REPORT_PATH,
    CALCULATE_REPORT_PATH,
    FINAL_EXCEL_PATH,
    MINI_MVP_REPORT_PATH,
    OPERATOR_LOG_PATH,
    PREPARE_REPORT_PATH,
    REVIEW_FINAL_EXCEL_PATH,
    VALIDATION_REPORT_PATH,
)


def write_operator_log(event: str, messages: list[str], stats: dict[str, Any] | None = None) -> None:
    payload = []
    if OPERATOR_LOG_PATH.exists():
        payload = json.loads(OPERATOR_LOG_PATH.read_text(encoding="utf-8"))
    payload.append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "event": event,
            "messages_for_elena": messages,
            "stats": stats or {},
        }
    )
    OPERATOR_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    OPERATOR_LOG_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_prepare_report(extracted: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    stats = review_statistics(rows)
    found_pdf = []
    for key, payload in extracted["parameters"].items():
        if not isinstance(payload, dict):
            continue
        value = payload.get("value")
        if value is None or value == "" or value == []:
            continue
        found_pdf.append(key)
    messages = [
        f"Подготовлена таблица проверки по разделу Земляные работы.",
        f"Найдено параметров из PDF/parser: {len(found_pdf)}.",
        f"Требуют внимания Елены: {stats['need_review']}.",
        f"Ожидают проверки: {stats['waiting']}.",
        "prepare не запускал расчет.",
    ]
    lines = [
        "# Prepare Report",
        "",
        "## Сообщения для Елены",
        "",
        *[f"- {message}" for message in messages],
        "",
        "## Найдено из PDF/parser",
        "",
        *[f"- `{key}`" for key in found_pdf],
        "",
        "## Gate",
        "",
        "- `manual_required_smoke_test` должен быть заполнен вручную для проверки процесса.",
        "- `pit_excavation_depth_m` должен быть проверен или исправлен, потому что это интерпретация диапазона.",
    ]
    PREPARE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    PREPARE_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    write_operator_log("prepare", messages, stats)


def build_validation_report(errors: list[str], warnings: list[str], rows: list[dict[str, Any]]) -> None:
    stats = review_statistics(rows)
    messages = []
    if errors:
        messages.append("Расчет пока нельзя запускать.")
        messages.append(f"Ошибок gate: {len(errors)}.")
    else:
        messages.append("Проверка пройдена, расчет можно запускать.")
    if warnings:
        messages.append(f"Предупреждений: {len(warnings)}.")
    lines = [
        "# Review Validation Report",
        "",
        "## Сообщения для Елены",
        "",
        *[f"- {message}" for message in messages],
        "",
        "## Errors",
        "",
        *([f"- {error}" for error in errors] or ["- Нет."]),
        "",
        "## Warnings",
        "",
        *([f"- {warning}" for warning in warnings] or ["- Нет."]),
        "",
        "## Stats",
        "",
        *[f"- {key}: {value}" for key, value in stats.items()],
    ]
    VALIDATION_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    write_operator_log("validate", messages, {**stats, "errors": len(errors), "warnings": len(warnings)})


def build_blocked_report(errors: list[str], warnings: list[str]) -> None:
    messages = ["Расчет заблокирован.", "Не заполнены / не проверены обязательные поля:"]
    messages.extend(errors)
    lines = [
        "# Calculate Blocked Report",
        "",
        *[f"- {message}" for message in messages],
        "",
        "## Warnings",
        "",
        *([f"- {warning}" for warning in warnings] or ["- Нет."]),
    ]
    CALCULATE_BLOCKED_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CALCULATE_BLOCKED_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    write_operator_log("calculate_blocked", messages, {"errors": len(errors), "warnings": len(warnings)})


def build_calculate_report(payload: dict[str, Any], result: dict[str, Any]) -> None:
    totals = result["internal_totals"]
    messages = [
        "Расчет выполнен из проверенной таблицы.",
        f"Материалы: {totals.get('internal_materials_total')}.",
        f"Работы: {totals.get('internal_works_total')}.",
        f"Итого раздел: {totals.get('internal_section_total')}.",
        f"Итоговый Excel: {REVIEW_FINAL_EXCEL_PATH}.",
    ]
    lines = [
        "# Calculate Report",
        "",
        "## Сообщения для Елены",
        "",
        *[f"- {message}" for message in messages],
        "",
        "## Цены",
        "",
    ]
    for warning in result.get("price_warnings", []):
        lines.append(f"- WARNING: {warning}")
    lines.extend(["", "## Assumptions", ""])
    for assumption in payload.get("assumptions", []):
        lines.append(f"- {assumption}")
    CALCULATE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CALCULATE_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    write_operator_log("calculate", messages, {"section_total": totals.get("internal_section_total")})


def build_report(extracted: dict[str, Any], poc_payload: dict[str, Any], result: dict[str, Any]) -> None:
    lines = [
        "# Earthworks Mini-MVP POC Report",
        "",
        "Legacy report name kept for compatibility. Use prepare/calculate reports for the CLI flow.",
        "",
        f"- Excel: `{FINAL_EXCEL_PATH}`",
    ]
    MINI_MVP_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    MINI_MVP_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
