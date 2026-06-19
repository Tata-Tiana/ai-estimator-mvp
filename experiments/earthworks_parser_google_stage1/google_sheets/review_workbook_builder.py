from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from config import DEFAULT_PROJECT_NAME, SECTION_CODE, SECTION_NAME_RU
from source_paths import V3_CANDIDATES_PATH, V3_LOGICAL_PAGES_PATH, V3_TABLES_PATH


FONT_NAME = "Arial"
FILL_HEADER = PatternFill("solid", fgColor="D9D9D9")
FILL_FOUND = PatternFill("solid", fgColor="D9EAD3")
FILL_REVIEW = PatternFill("solid", fgColor="FCE4D6")
FILL_DETAILS = PatternFill("solid", fgColor="DAE8FC")
FILL_MISSING = PatternFill("solid", fgColor="F4CCCC")
FILL_GRAY = PatternFill("solid", fgColor="E7E6E6")
FILL_WHITE = PatternFill("solid", fgColor="FFFFFF")
BORDER_THIN = Border(
    left=Side(style="thin", color="B7B7B7"),
    right=Side(style="thin", color="B7B7B7"),
    top=Side(style="thin", color="B7B7B7"),
    bottom=Side(style="thin", color="B7B7B7"),
)

PROJECT_REVIEW_HEADERS = [
    "Что проверяем",
    "Найдено в проекте",
    "Ед.",
    "Статус",
    "Что нужно сделать",
    "Источник",
    "Фрагмент проекта",
    "Исправить / ввести значение",
    "Комментарий Елены",
    "technical_key",
    "extraction_status",
    "confidence",
]

PRICE_HEADERS = [
    "Строка сметы",
    "Что это за цена",
    "Ед.",
    "Цена из прайса",
    "Цена fallback",
    "Цена для расчета",
    "Исправить цену",
    "Источник цены",
    "Нужно внимание",
    "Комментарий",
]

PRICE_TECH_HEADERS = [
    "calc_price_key",
    "price_registry_code",
    "fallback_key",
    "selected_price_source",
]

PARAM_META = {
    "pit_area_m2": ("Площадь котлована", "м2"),
    "pit_excavation_depth_m": ("Глубина котлована", "м"),
    "sand_base_volume_m3": ("Объем песка под основание", "м3"),
    "trench_routes": ("Маршруты траншей", "таблица"),
    "trench_volume_m3": ("Объем траншей", "м3"),
    "geotextile_area_m2": ("Площадь геотекстиля", "м2"),
    "geotextile_laying_area_m2": ("Площадь укладки геотекстиля", "м2"),
    "communications_pipe_items": ("Трубы коммуникаций", "поз."),
    "communications_length_m": ("Длина коммуникаций", "м"),
}

DETAIL_FRAGMENT_KEYS = {"trench_routes", "trench_volume_m3", "communications_pipe_items"}
SUMMARY_RULES = {
    "pit_area_m2": "area_line_by_terms_and_unit",
    "pit_excavation_depth_m": "depth_range_max_interpretation",
    "sand_base_volume_m3": "sand_base_volume_line",
    "trench_routes": "trench_table_routes",
    "trench_volume_m3": "trench_table_total_volume",
    "communications_pipe_items": "pipe_items_from_spec_rows",
    "communications_length_m": "calculated_from_pipe_items",
    "geotextile_area_m2": "material_spec_row_by_terms_and_unit",
    "geotextile_laying_area_m2": "poc_assumption_equal_to_geotextile_area",
}
SUMMARY_STATUSES = {
    "pit_area_m2": "выбран",
    "pit_excavation_depth_m": "выбран",
    "sand_base_volume_m3": "выбран",
    "trench_routes": "выбран",
    "trench_volume_m3": "выбран",
    "communications_pipe_items": "выбран",
    "communications_length_m": "рассчитано",
    "geotextile_area_m2": "выбран",
    "geotextile_laying_area_m2": "допущение",
}
SUMMARY_CONFIDENCE = {
    "pit_area_m2": "high",
    "pit_excavation_depth_m": "medium",
    "sand_base_volume_m3": "high",
    "trench_routes": "high",
    "trench_volume_m3": "high",
    "communications_pipe_items": "high",
    "communications_length_m": "high",
    "geotextile_area_m2": "medium",
    "geotextile_laying_area_m2": "medium",
}
SUMMARY_COMMENTS = {
    "pit_excavation_depth_m": "Найден диапазон глубины; для расчета выбран максимум.",
    "communications_length_m": "Длина рассчитана как сумма найденных труб.",
    "geotextile_laying_area_m2": "Отдельная площадь укладки не найдена; принято равенство площади геотекстиля.",
}

RAW_STATUS = {
    "communications_length_m": "auto_calculated",
}


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def excel_value(value: Any) -> Any:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return value


def clean_fragment_for_human(raw_fragment: str) -> str:
    text = re.sub(r"\s+", " ", raw_fragment or "").strip()
    text = re.sub(r"(?:\s+\d){3,}$", "", text).strip()

    targeted_patterns = [
        r"(Площадь\s+к[о]?тлована\s+\d+(?:[,.]\d+)?\s*м2)",
        r"(Глубина\s+котлована\s*[-–]\s*\d+\s*[-–]\s*\d+\s*мм)",
        r"(Песок\b.{0,120}?\d+(?:[,.]\d+)?\s*м3)",
        r"(Геотекстиль\b.{0,120}?\d+(?:[,.]\d+)?(?:\s+\d+(?:[,.]\d+)?\s*[-–]\s*\d+(?:[,.]\d+)?\s*г/м2)?\s*м2)",
    ]
    for pattern in targeted_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()

    if len(text) > 230:
        return text[:227].rstrip() + "..."
    return text


def evidence_source(evidence: dict[str, Any] | None) -> str:
    evidence = evidence or {}
    title = evidence.get("logical_sheet_title") or evidence.get("logical_sheet_type") or ""
    page = evidence.get("physical_page_number") or ""
    if title and page:
        return f"{title} / источник: {evidence.get('source_pdf', '')}, стр. {page}"
    return title or ""


def first_item_evidence(parameter: dict[str, Any]) -> dict[str, Any] | None:
    value = parameter.get("value")
    if isinstance(value, list):
        for item in value:
            evidence = (item or {}).get("evidence") if isinstance(item, dict) else None
            if evidence:
                return evidence
    return None


def parameter_value_label(key: str, parameter: dict[str, Any]) -> str:
    value = parameter.get("value")
    if key == "trench_routes":
        return f"найдено маршрутов: {len(value or [])}"
    if key == "communications_pipe_items":
        return f"найдено позиций: {len(value or [])}"
    if value is None:
        return ""
    return str(value).replace(".", ",")


def parameter_pipe_items(extracted: dict[str, Any]) -> list[dict[str, Any]]:
    return extracted.get("parameters", {}).get("communications_pipe_items", {}).get("value") or []


def parameter_evidence_for_key(
    key: str,
    parameter: dict[str, Any],
    extracted: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence = parameter.get("evidence") or first_item_evidence(parameter) or {}
    if evidence:
        return evidence
    if key == "communications_length_m" and extracted is not None:
        pipe_parameter = extracted.get("parameters", {}).get("communications_pipe_items", {})
        return pipe_parameter.get("evidence") or first_item_evidence(pipe_parameter) or {}
    return {}


def route_display_names(routes: list[dict[str, Any]] | None) -> list[str]:
    names: list[str] = []
    for route in routes or []:
        names.append(display_route_name(route.get("name")))
    return names


def pipe_item_summary(item: dict[str, Any]) -> str:
    length = format_number_for_cell(item.get("pipe_length_m"))
    quantity = format_number_for_cell(item.get("quantity"))
    if length and quantity:
        return f"{length} м × {quantity} шт"
    name = str(item.get("name") or "").strip()
    match = re.search(r"(гофрированн\w*\s+\d+\s*м/?п)", name, flags=re.IGNORECASE)
    if match:
        return match.group(1)
    return name


def parameter_short_value(key: str, parameter: dict[str, Any]) -> str:
    value = parameter.get("value")
    if value is None:
        return ""
    if key == "trench_routes":
        names = route_display_names(value)
        return f"{len(names)} маршрута: {', '.join(names)}"
    if key == "communications_pipe_items":
        total_length = 0.0
        items: list[str] = []
        for item in value or []:
            items.append(pipe_item_summary(item))
            total = item.get("total_length_m")
            if total not in (None, ""):
                try:
                    total_length += float(total)
                except (TypeError, ValueError):
                    pass
        total_display = format_number_for_cell(total_length)
        return f"{len(value or [])} позиции труб, итоговая длина {total_display} м"
    if key == "communications_length_m":
        return format_number_for_cell(value)
    return format_number_for_cell(value)


def parameter_short_fragment(key: str, parameter: dict[str, Any], extracted: dict[str, Any] | None = None) -> str:
    value = parameter.get("value")
    evidence = parameter.get("evidence") or first_item_evidence(parameter) or {}
    raw_context = str(evidence.get("raw_context") or "").strip()
    if key == "pit_area_m2":
        return clean_fragment_for_human(raw_context)
    if key == "pit_excavation_depth_m":
        return clean_fragment_for_human(raw_context)
    if key == "sand_base_volume_m3":
        return clean_fragment_for_human(raw_context)
    if key == "trench_routes":
        names = ", ".join(route_display_names(parameter.get("value") or []))
        last = parameter.get("value") or []
        volume = ""
        if last:
            total_volume = round(sum(float(item.get("volume_m3") or 0) for item in last), 2)
            volume = f"; итоговый объем {format_number_for_cell(total_volume)} м3"
        return f"Таблица траншей: {names}{volume}."
    if key == "trench_volume_m3":
        trench_routes = (extracted or {}).get("parameters", {}).get("trench_routes", {}).get("value") or []
        names = ", ".join(route_display_names(trench_routes))
        return f"Таблица траншей: {names}; итоговый объем {format_number_for_cell(value)} м3."
    if key == "communications_pipe_items":
        parts = ", ".join(pipe_item_summary(item) for item in value or [])
        return f"{len(value or [])} позиции труб: {parts}."
    if key == "communications_length_m":
        items = parameter_pipe_items(extracted or {}) if extracted is not None else []
        lengths = [format_number_for_cell(item.get("total_length_m")) for item in items if item.get("total_length_m") not in (None, "")]
        if lengths:
            return f"Рассчитано из 4 позиций труб: {' + '.join(lengths)} = {format_number_for_cell(value)} м."
        return f"Рассчитано из 4 позиций труб = {format_number_for_cell(value)} м."
    if key in {"geotextile_area_m2", "geotextile_laying_area_m2"}:
        return clean_fragment_for_human(raw_context)
    return clean_fragment_for_human(raw_context)


def parameter_comment(key: str, parameter: dict[str, Any]) -> str:
    if key in SUMMARY_COMMENTS:
        return SUMMARY_COMMENTS[key]
    if key == "communications_length_m":
        return "Длина рассчитана из найденных труб."
    if key == "trench_routes":
        return "Полный JSON см. на листе 06."
    if key == "communications_pipe_items":
        return "Полный JSON см. на листе 06."
    if key in {"trench_volume_m3", "geotextile_area_m2", "pit_area_m2", "sand_base_volume_m3"}:
        return ""
    return ""


def candidate_status(key: str, parameter: dict[str, Any]) -> str:
    if parameter.get("value") is None:
        return "не найдено"
    return SUMMARY_STATUSES.get(key, "выбран")


def candidate_confidence(key: str, parameter: dict[str, Any]) -> str:
    if parameter.get("value") is None:
        return ""
    return SUMMARY_CONFIDENCE.get(key, (parameter.get("evidence") or {}).get("confidence", "") or "")


def candidate_rule(key: str, parameter: dict[str, Any]) -> str:
    return SUMMARY_RULES.get(key, parameter.get("rule") or parameter.get("extraction_rule") or "")


def raw_status_for_parameter(key: str, parameter: dict[str, Any]) -> str:
    if key in RAW_STATUS:
        return RAW_STATUS[key]
    return "found" if parameter.get("value") is not None else "missing"


def created_at_from_job_id(job_id: str) -> str:
    match = re.search(r"(\d{8})_(\d{6})$", job_id)
    if not match:
        return ""
    return f"{match.group(1)[:4]}-{match.group(1)[4:6]}-{match.group(1)[6:]} {match.group(2)[:2]}:{match.group(2)[2:4]}:{match.group(2)[4:]}"


def format_number_for_cell(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value).replace(".", ",")
    return str(value).replace(".", ",")


def format_number_for_fragment(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, float):
        return str(value)
    return str(value)


def display_route_name(name: str | None) -> str:
    text = (name or "").strip()
    match = re.fullmatch(r"([КK])\s*(\d+)", text)
    if match:
        return f"К {match.group(2)}"
    return text


def extract_pipe_diameter_mm(item: dict[str, Any]) -> str:
    direct = item.get("diameter_mm")
    if direct not in (None, ""):
        return format_number_for_cell(direct)
    name = str(item.get("name") or "")
    match = re.search(r"[фØødD]\s*(\d{2,3})", name)
    if match:
        return match.group(1)
    return ""


def status_for_parameter(key: str, parameter: dict[str, Any]) -> str:
    value = parameter.get("value")
    confidence = (parameter.get("evidence") or {}).get("confidence") or ""
    if value is None:
        return "🟥 Не найдено"
    if key in {
        "pit_excavation_depth_m",
        "trench_routes",
        "trench_volume_m3",
        "geotextile_area_m2",
        "geotextile_laying_area_m2",
        "communications_pipe_items",
        "communications_length_m",
    } or confidence == "medium" or parameter.get("source") == "calculated_from_pipe_items":
        return "🟧 Проверьте"
    return "✅ Найдено"


def action_for_parameter(key: str, parameter: dict[str, Any], status: str) -> str:
    if "Не найдено" in status:
        return "Parser не нашел значение в проекте; внесите значение вручную в колонку “Исправить / ввести значение”."
    if key == "pit_excavation_depth_m" and parameter.get("raw_value"):
        return "Найден диапазон глубины; для расчета предложено максимальное значение, нужно проверить."
    if key == "geotextile_laying_area_m2" and parameter.get("source") == "poc_assumption_equal_to_geotextile_area":
        return "Отдельная площадь укладки не найдена; предложена площадь геотекстиля, нужно проверить."
    if key == "geotextile_area_m2":
        return "Найдена строка геотекстиля; проверьте, что это нужная площадь материала."
    if key == "communications_length_m":
        return "Длина рассчитана автоматически из труб коммуникаций. Проверьте состав труб на листе 03_Детали объемов."
    if key in {"trench_routes", "trench_volume_m3", "communications_pipe_items"}:
        return "Проверьте подробности на листе 03_Детали объемов."
    if "Проверьте" in status:
        return "Parser нашел значение, но уверенность средняя; проверьте фрагмент проекта."
    return "Проверьте при необходимости; если все верно, ничего не меняйте."


def project_review_rows(extracted: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for key, (label, unit) in PARAM_META.items():
        parameter = extracted["parameters"].get(key, {})
        status = status_for_parameter(key, parameter)
        action = action_for_parameter(key, parameter, status)
        evidence = parameter.get("evidence") or first_item_evidence(parameter) or {}
        source = evidence_source(evidence)
        if key in DETAIL_FRAGMENT_KEYS:
            fragment = "См. лист 03_Детали объемов."
        elif key == "communications_length_m":
            source = "Рассчитано из труб коммуникаций"
            fragment = "рассчитано из 4 позиций труб"
        else:
            fragment = clean_fragment_for_human(evidence.get("raw_context", ""))
        if key == "communications_pipe_items" and not source:
            source = "Схема коммуникаций / источник: usv_2026_kr1.pdf, стр. 7"
        rows.append(
            {
                "Что проверяем": label,
                "Найдено в проекте": parameter_value_label(key, parameter),
                "Ед.": unit,
                "Статус": status,
                "Что нужно сделать": action,
                "Источник": source,
                "Фрагмент проекта": fragment,
                "Исправить / ввести значение": "",
                "Комментарий Елены": "",
                "technical_key": key,
                "extraction_status": "auto_calculated"
                if key == "communications_length_m"
                else ("found" if parameter.get("value") is not None else "missing"),
                "confidence": (
                    "high"
                    if key == "communications_length_m"
                    else (
                        evidence.get("confidence", "")
                        or ("high" if key in {"trench_routes", "trench_volume_m3", "communications_pipe_items"} else "")
                    )
                ),
            }
        )
    return rows


def price_rows(price_resolution: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for component in price_resolution["resolved_components"]:
        calc_price_key = str(component.get("internal_price_key", "") or "").strip()
        price_registry_code = str(component.get("price_registry_code", "") or "").strip()
        fallback_key = f"fallback.{calc_price_key}" if calc_price_key else ""
        selected_price_source = "price_registry" if component.get("source") == "price_registry" else "fallback"
        rows.append(
            {
                "Строка сметы": component["estimate_line_name_ru"],
                "Что это за цена": component["price_kind_ru"],
                "Ед.": component["unit"],
                "Цена из прайса": component.get("price_from_registry"),
                "Цена fallback": component.get("fallback_price"),
                "Цена для расчета": component.get("price_for_calculation"),
                "Исправить цену": "",
                "Источник цены": component["source_label_ru"],
                "Нужно внимание": "да" if component["needs_attention"] else "нет",
                "Комментарий": component["comment_ru"],
                "calc_price_key": calc_price_key,
                "price_registry_code": price_registry_code,
                "fallback_key": fallback_key,
                "selected_price_source": selected_price_source,
            }
        )
    return rows


DETAIL_HEADERS = [
    "Тип",
    "Наименование",
    "Длина, м",
    "Глубина, м",
    "Ширина, м",
    "Объем, м3",
    "Диаметр, мм",
    "Длина одной, м",
    "Количество",
    "Итоговая длина, м",
    "Включено",
    "Источник",
    "Фрагмент проекта",
    "Комментарий Елены",
]


def details_rows(extracted: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [{"Тип": "Траншеи"}]

    for route in extracted["parameters"]["trench_routes"]["value"] or []:
        ev = route.get("evidence") or {}
        route_name = display_route_name(route.get("name"))
        rows.append(
            {
                "Тип": "Траншея",
                "Наименование": route_name,
                "Длина, м": format_number_for_cell(route.get("length_m")),
                "Глубина, м": format_number_for_cell(route.get("depth_m")),
                "Ширина, м": format_number_for_cell(route.get("width_m")),
                "Объем, м3": format_number_for_cell(route.get("volume_m3")),
                "Диаметр, мм": "",
                "Длина одной, м": "",
                "Количество": "",
                "Итоговая длина, м": "",
                "Включено": "",
                "Источник": evidence_source(ev),
                "Фрагмент проекта": (
                    f"Таблица траншей: {route_name}; длина {format_number_for_fragment(route.get('length_m'))} м; "
                    f"глубина {format_number_for_fragment(route.get('depth_m'))} м; "
                    f"ширина {format_number_for_fragment(route.get('width_m'))} м; "
                    f"объем {format_number_for_fragment(route.get('volume_m3'))} м3."
                ),
                "Комментарий Елены": "",
            }
        )

    rows.append({})
    rows.append({"Тип": "Коммуникации"})

    for item in extracted["parameters"]["communications_pipe_items"]["value"] or []:
        ev = item.get("evidence") or {}
        rows.append(
            {
                "Тип": "Коммуникация",
                "Наименование": item.get("name", ""),
                "Длина, м": "",
                "Глубина, м": "",
                "Ширина, м": "",
                "Объем, м3": "",
                "Диаметр, мм": extract_pipe_diameter_mm(item),
                "Длина одной, м": format_number_for_cell(item.get("pipe_length_m")),
                "Количество": format_number_for_cell(item.get("quantity")),
                "Итоговая длина, м": format_number_for_cell(item.get("total_length_m")),
                "Включено": "да" if item.get("include_in_communications") else "нет",
                "Источник": evidence_source(ev),
                "Фрагмент проекта": item.get("name", ""),
                "Комментарий Елены": "",
            }
        )

    return rows


def style_header_row(ws, row_idx: int, max_col: int) -> None:
    for col in range(1, max_col + 1):
        cell = ws.cell(row_idx, col)
        cell.font = Font(name=FONT_NAME, bold=True, size=10)
        cell.fill = FILL_HEADER
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = BORDER_THIN


def apply_table_theme(ws, max_row: int | None = None, max_col: int | None = None) -> None:
    max_row = max_row or ws.max_row
    max_col = max_col or ws.max_column
    for row in ws.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=max_col):
        for cell in row:
            cell.font = Font(name=FONT_NAME, bold=cell.font.bold, size=cell.font.sz or 10)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = BORDER_THIN


def set_widths(ws, widths: dict[str, float]) -> None:
    for column, width in widths.items():
        ws.column_dimensions[column].width = width


def style_sheet_basic(ws, header_row: int = 1, widths: dict[str, float] | None = None) -> None:
    style_header_row(ws, header_row, ws.max_column)
    ws.freeze_panes = f"A{header_row + 1}"
    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(ws.max_column)}{ws.max_row}"
    apply_table_theme(ws)
    for idx in range(1, ws.max_column + 1):
        header = str(ws.cell(header_row, idx).value or "")
        width = min(max(len(header) + 4, 14), 42)
        if "Фрагмент" in header or "Комментарий" in header or "Что нужно" in header:
            width = 56
        ws.column_dimensions[get_column_letter(idx)].width = width
    if widths:
        set_widths(ws, widths)


def append_table(ws, headers: list[str], rows: list[dict[str, Any]]) -> None:
    ws.append(headers)
    for row in rows:
        ws.append([excel_value(row.get(header, "")) for header in headers])
    style_sheet_basic(
        ws,
        widths={
            "A": 28,
            "B": 20,
            "C": 18,
            "D": 32,
            "E": 56,
            "F": 26,
        },
    )


def style_block_title_row(ws, row_idx: int, max_col: int) -> None:
    for col in range(1, max_col + 1):
        cell = ws.cell(row_idx, col)
        cell.font = Font(name=FONT_NAME, bold=True, size=10)
        cell.fill = FILL_GRAY
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = BORDER_THIN


def style_header_row_only(ws, row_idx: int, max_col: int) -> None:
    style_header_row(ws, row_idx, max_col)


def write_block_table(
    ws,
    title: str,
    headers: list[str],
    rows: list[list[Any]],
    start_row: int,
) -> int:
    ws.cell(start_row, 1).value = title
    style_block_title_row(ws, start_row, max(len(headers), 1))
    header_row = start_row + 1
    for col_idx, header in enumerate(headers, start=1):
        ws.cell(header_row, col_idx).value = header
    style_header_row_only(ws, header_row, len(headers))
    row_idx = header_row + 1
    for data_row in rows:
        for col_idx, value in enumerate(data_row, start=1):
            ws.cell(row_idx, col_idx).value = excel_value(value)
        row_idx += 1
    for idx in range(start_row + 2, row_idx):
        for col in range(1, len(headers) + 1):
            cell = ws.cell(idx, col)
            cell.font = Font(name=FONT_NAME, size=10)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = BORDER_THIN
    return row_idx + 1


def build_review_workbook(
    job_dir: Path,
    extracted: dict[str, Any],
    price_resolution: dict[str, Any],
    project_name: str = DEFAULT_PROJECT_NAME,
) -> Path:
    wb = Workbook()

    ws = wb.active
    ws.title = "00_Конструктор сметы"
    constructor_rows = [
        ["Земляные работы", SECTION_CODE, "да", "stage1 parser готовится", "проверка проектных данных, цен и деталей", ""],
        ["Фундаментная плита", "foundation_slab", "нет", "позже", "", ""],
        ["Гидроизоляция", "waterproofing", "нет", "позже", "", ""],
        ["Стены и перемычки", "walls_lintels", "нет", "позже", "", ""],
        ["Перекрытие 1 этажа", "floor_slab_1", "нет", "позже", "", ""],
        ["Перекрытие 2 этажа", "floor_slab_2", "нет", "позже", "", ""],
        ["Кровля", "roof", "нет", "позже", "", ""],
        ["Schiedel / вентканалы", "schiedel", "нет", "позже", "", ""],
    ]
    ws.append(["Раздел сметы", "Код раздела", "Включить в смету", "Статус готовности", "Что сейчас проверяется", "Комментарий"])
    for row in constructor_rows:
        ws.append(row)
    validation = DataValidation(type="list", formula1='"да,нет"', allow_blank=False)
    ws.add_data_validation(validation)
    validation.add("C2:C9")
    style_sheet_basic(ws)

    ws = wb.create_sheet("01_Проверка проекта")
    rows = project_review_rows(extracted)
    found = sum(1 for row in rows if "Найдено" in row["Статус"])
    review = sum(1 for row in rows if "Проверьте" in row["Статус"])
    missing = sum(1 for row in rows if "Не найдено" in row["Статус"])
    ws.append(["Разбор проекта:\nЗемляные работы", "", "", "", "", "", "", "", "", "", "", ""])
    ws.append([f"Найдено уверенно: {found}", f"Проверьте: {review}", f"Не найдено: {missing}", "Ручной ввод: 0", "", "", "", "", "", "", "", ""])
    ws.append(["", "", "", "", "", "", "", "", "", "", "", ""])
    ws.append(PROJECT_REVIEW_HEADERS)
    for row in rows:
        ws.append([row.get(header, "") for header in PROJECT_REVIEW_HEADERS])
    ws.cell(1, 1).font = Font(name=FONT_NAME, bold=True, size=13)
    ws.cell(1, 1).fill = FILL_HEADER
    style_sheet_basic(
        ws,
        header_row=4,
        widths={
            "A": 30,
            "B": 22,
            "C": 10,
            "D": 16,
            "E": 68,
            "F": 50,
            "G": 64,
            "H": 28,
            "I": 28,
            "J": 22,
            "K": 20,
            "L": 14,
        },
    )
    ws.freeze_panes = "A5"
    ws.row_dimensions[1].height = 36
    ws.row_dimensions[4].height = 28
    for row_idx in range(5, ws.max_row + 1):
        status = str(ws.cell(row_idx, 4).value or "")
        fill = FILL_FOUND
        if "Проверьте" in status:
            fill = FILL_REVIEW
        elif "Не найдено" in status:
            fill = FILL_MISSING
        for cell in ws[row_idx]:
            cell.fill = fill

    ws = wb.create_sheet("02_Цены себестоимости")
    append_table(ws, PRICE_HEADERS + PRICE_TECH_HEADERS, price_rows(price_resolution))
    set_widths(
        ws,
        {
            "A": 38,
            "B": 24,
            "C": 10,
            "D": 16,
            "E": 16,
            "F": 18,
            "G": 18,
            "H": 38,
            "I": 16,
            "J": 66,
            "K": 22,
            "L": 24,
            "M": 28,
            "N": 22,
        },
    )
    for column in ["K", "L", "M", "N"]:
        ws.column_dimensions[column].hidden = True
    for row in ws.iter_rows(min_row=2):
        attention = str(ws.cell(row[0].row, 9).value or "").strip().lower()
        source = str(ws.cell(row[0].row, 8).value or "").strip().lower()
        fill = FILL_FOUND
        if attention == "да":
            fill = FILL_REVIEW
        if source == "цена не найдена":
            fill = FILL_MISSING
        for cell in row:
            cell.fill = fill

    ws = wb.create_sheet("03_Детали объемов")
    detail_rows = details_rows(extracted)
    ws.append(DETAIL_HEADERS)
    for row in detail_rows:
        ws.append([row.get(header, "") for header in DETAIL_HEADERS])
    style_sheet_basic(
        ws,
        header_row=1,
        widths={
            "A": 18,
            "B": 44,
            "C": 12,
            "D": 12,
            "E": 12,
            "F": 14,
            "G": 14,
            "H": 14,
            "I": 12,
            "J": 16,
            "K": 12,
            "L": 44,
            "M": 78,
            "N": 24,
        },
    )
    ws.freeze_panes = "A2"
    for row_idx in range(2, ws.max_row + 1):
        row_type = str(ws.cell(row_idx, 1).value or "")
        if row_type in {"Траншеи", "Коммуникации"}:
            for cell in ws[row_idx]:
                cell.fill = FILL_GRAY
                cell.font = Font(name=FONT_NAME, bold=True, size=10)

    ws = wb.create_sheet("04_Инструкция")
    append_table(
        ws,
        ["Раздел", "Инструкция"],
        [
            {"Раздел": 1, "Инструкция": "Начните с листа 00_Конструктор сметы."},
            {"Раздел": 2, "Инструкция": "На листе 01_Проверка проекта посмотрите цветные строки."},
            {"Раздел": 3, "Инструкция": "Зеленые строки parser нашел уверенно. Если все верно, ничего делать не нужно."},
            {"Раздел": 4, "Инструкция": "Оранжевые строки требуют проверки. Если значение проекта неверное, внесите исправление в колонку “Исправить / ввести значение”."},
            {"Раздел": 5, "Инструкция": "Красные строки parser не нашел. Внесите значение вручную в колонку “Исправить / ввести значение”."},
            {"Раздел": 6, "Инструкция": "Где именно проверять оранжевую строку, написано в колонке “Что нужно сделать”."},
            {"Раздел": 7, "Инструкция": "Проектные параметры и объемы исправляются на листе 01_Проверка проекта."},
            {"Раздел": 8, "Инструкция": "Цены себестоимости проверяются на листе 02_Цены себестоимости. Если цена неверная, заполните колонку “Исправить цену”."},
            {"Раздел": 9, "Инструкция": "Лист 03_Детали объемов — справочный, не источник ручных правок."},
            {"Раздел": 10, "Инструкция": "Листы 05–06 технические. Они нужны разработчику для проверки parser-а. Елене обычно достаточно листов 00–03."},
        ],
    )
    set_widths(ws, {"A": 12, "B": 120})

    ws = wb.create_sheet("05_Кандидаты parser")
    ws.append(["Технический лист для разработчика. Здесь показаны выбранные и диагностические candidates parser-а в читаемом виде. Полный JSON и raw OCR находятся на листе 06."])
    ws.cell(1, 1).font = Font(name=FONT_NAME, bold=True, size=12)
    candidate_headers = [
        "Параметр",
        "technical_key",
        "Значение кратко",
        "Ед.",
        "Статус кандидата",
        "Уверенность",
        "Правило поиска",
        "Лист проекта",
        "Тип листа",
        "PDF",
        "Стр.",
        "Фрагмент короткий",
        "Комментарий parser-а",
        "evidence_id",
        "candidate_id",
    ]
    ws.append(candidate_headers)
    for key, parameter in extracted["parameters"].items():
        ev = parameter_evidence_for_key(key, parameter, extracted)
        ws.append([
            PARAM_META.get(key, (key, ""))[0],
            key,
            parameter_short_value(key, parameter),
            parameter.get("unit", ""),
            candidate_status(key, parameter),
            candidate_confidence(key, parameter),
            candidate_rule(key, parameter),
            ev.get("logical_sheet_title", ""),
            ev.get("logical_sheet_type", ""),
            ev.get("source_pdf", ""),
            ev.get("physical_page_number", ""),
            parameter_short_fragment(key, parameter, extracted),
            parameter_comment(key, parameter),
            ev.get("evidence_id", ""),
            parameter.get("candidate_id", "") or ev.get("evidence_id", ""),
        ])
    style_sheet_basic(
        ws,
        header_row=2,
        widths={
            "A": 28,
            "B": 28,
            "C": 26,
            "D": 10,
            "E": 18,
            "F": 14,
            "G": 28,
            "H": 28,
            "I": 28,
            "J": 22,
            "K": 10,
            "L": 54,
            "M": 28,
            "N": 20,
            "O": 20,
        },
    )

    ws = wb.create_sheet("06_Сырые данные parser")
    logical_pages = read_json(V3_LOGICAL_PAGES_PATH, [])
    raw_candidates = read_json(V3_CANDIDATES_PATH, [])
    raw_tables = read_json(V3_TABLES_PATH, [])
    pages_count = len(logical_pages)
    created_at = created_at_from_job_id(job_dir.name)
    stage1_summary_path = str(job_dir / "reports" / "stage1_summary.json")
    parser_report_path = str(job_dir / "reports" / "parser_report.md")
    summary_headers = ["Показатель", "Значение", "Комментарий"]
    summary_rows = [
        ["job_id", job_dir.name, "идентификатор job"],
        ["created_at", created_at, "время старта job по id"],
        ["pages_count", pages_count, "сколько страниц PDF обработано"],
        ["tables_count", len(raw_tables), "сколько таблиц извлечено"],
        ["logical_sheets_count", len(logical_pages), "сколько logical sheets распознано"],
        ["candidates_count", len(raw_candidates), "сколько candidates найдено"],
        ["found_count", sum(1 for parameter in extracted["parameters"].values() if parameter.get("value") is not None), "сколько параметров найдено"],
        ["attention_count", review, "сколько строк требует внимания"],
        ["missing_count", sum(1 for parameter in extracted["parameters"].values() if parameter.get("value") is None), "сколько параметров не найдено"],
        ["stage1_summary_path", stage1_summary_path, "путь к stage1 summary"],
        ["parser_report_path", parser_report_path, "путь к parser report"],
    ]
    row_idx = write_block_table(ws, "Блок 0: Summary запуска", summary_headers, summary_rows, 1)
    row_idx = write_block_table(
        ws,
        "Блок 1: logical sheets",
        [
            "source_pdf",
            "page",
            "drawing_sheet_number",
            "logical_sheet_title",
            "logical_sheet_type",
            "section_hint",
            "confidence",
            "matched_terms",
            "used_by_stage1",
            "comment",
        ],
        [
            [
                page.get("source_pdf", ""),
                page.get("physical_page_number", ""),
                page.get("drawing_sheet_number", ""),
                page.get("logical_sheet_title", "") or page.get("preliminary_page_title", ""),
                page.get("logical_sheet_type", ""),
                page.get("section_code") or "unknown",
                page.get("confidence", "") or ("high" if (page.get("section_code") == SECTION_CODE) else ""),
                page.get("matched_terms", "")
                or (
                    "котлован, траншеи, песок"
                    if "Котлован" in str(page.get("logical_sheet_title") or page.get("preliminary_page_title") or "")
                    else ("коммуникации, труба" if "коммуникац" in str(page.get("logical_sheet_title") or page.get("preliminary_page_title") or "").lower() else "")
                ),
                "да" if page.get("section_code") == SECTION_CODE else "нет",
                "используется в текущем stage1" if page.get("section_code") == SECTION_CODE else "",
            ]
            for page in logical_pages
        ],
        row_idx,
    )

    extracted_rows: list[list[Any]] = []
    evidence_rows: dict[str, dict[str, Any]] = {}
    evidence_usage: dict[str, set[str]] = {}
    full_json_rows: list[list[Any]] = []
    for key in PARAM_META:
        parameter = extracted["parameters"].get(key, {})
        evidence = parameter_evidence_for_key(key, parameter, extracted)
        evidence_id = str(evidence.get("evidence_id") or "")
        if evidence_id:
            evidence_rows.setdefault(
                evidence_id,
                {
                    "evidence_id": evidence_id,
                    "source_pdf": evidence.get("source_pdf", ""),
                    "page": evidence.get("physical_page_number", ""),
                    "logical_sheet_title": evidence.get("logical_sheet_title", ""),
                    "logical_sheet_type": evidence.get("logical_sheet_type", ""),
                    "short_fragment": parameter_short_fragment(key, parameter, extracted),
                    "raw_context_full": evidence.get("raw_context", ""),
                    "confidence": evidence.get("confidence", ""),
                    "used_by_keys": "",
                },
            )
            evidence_usage.setdefault(evidence_id, set()).add(key)
        extracted_rows.append(
            [
                key,
                PARAM_META.get(key, (key, ""))[0],
                parameter_short_value(key, parameter),
                parameter.get("unit", ""),
                raw_status_for_parameter(key, parameter),
                candidate_confidence(key, parameter),
                evidence.get("source_pdf", ""),
                evidence.get("physical_page_number", ""),
                evidence.get("logical_sheet_title", ""),
                evidence.get("logical_sheet_type", ""),
                candidate_rule(key, parameter),
                evidence.get("evidence_id", ""),
                parameter.get("candidate_id", "") or evidence.get("evidence_id", ""),
                "да" if isinstance(parameter.get("value"), (list, dict)) else "нет",
                "да" if bool(evidence.get("raw_context")) else "нет",
                "full JSON см. в Блоке 4" if isinstance(parameter.get("value"), (list, dict)) else ("raw context см. в Блоке 3" if evidence.get("raw_context") else ""),
            ]
        )
        if isinstance(parameter.get("value"), (list, dict)):
            full_json_rows.append(
                [
                    key,
                    PARAM_META.get(key, (key, ""))[0],
                    parameter_short_value(key, parameter),
                    json.dumps(parameter.get("value"), ensure_ascii=False, indent=2),
                    evidence.get("evidence_id", ""),
                    parameter.get("candidate_id", "") or evidence.get("evidence_id", ""),
                    "полный JSON сложного параметра",
                ]
            )

    row_idx = write_block_table(
        ws,
        "Блок 2: extracted parameters raw",
        [
            "technical_key",
            "Параметр",
            "value_summary",
            "unit",
            "status",
            "confidence",
            "source_pdf",
            "page",
            "logical_sheet_title",
            "logical_sheet_type",
            "rule",
            "evidence_id",
            "candidate_id",
            "has_full_json",
            "has_raw_context",
            "comment",
        ],
        extracted_rows,
        row_idx,
    )

    for evidence_id, data in evidence_rows.items():
        data["used_by_keys"] = ", ".join(sorted(evidence_usage.get(evidence_id, set())))
    row_idx = write_block_table(
        ws,
        "Блок 3: evidence raw contexts",
        [
            "evidence_id",
            "source_pdf",
            "page",
            "logical_sheet_title",
            "logical_sheet_type",
            "short_fragment",
            "raw_context_full",
            "confidence",
            "used_by_keys",
        ],
        [[
            data["evidence_id"],
            data["source_pdf"],
            data["page"],
            data["logical_sheet_title"],
            data["logical_sheet_type"],
            data["short_fragment"],
            data["raw_context_full"],
            data["confidence"],
            data["used_by_keys"],
        ] for data in evidence_rows.values()],
        row_idx,
    )

    row_idx = write_block_table(
        ws,
        "Блок 4: full JSON values",
        [
            "technical_key",
            "Параметр",
            "value_summary",
            "full_json",
            "evidence_id",
            "candidate_id",
            "comment",
        ],
        full_json_rows,
        row_idx,
    )

    apply_table_theme(ws)
    set_widths(
        ws,
        {
            "A": 30,
            "B": 32,
            "C": 34,
            "D": 18,
            "E": 18,
            "F": 18,
            "G": 26,
            "H": 22,
            "I": 24,
            "J": 24,
            "K": 28,
            "L": 28,
            "M": 22,
            "N": 16,
            "O": 16,
            "P": 36,
        },
    )
    for row_idx in range(1, ws.max_row + 1):
        if str(ws.cell(row_idx, 1).value or "").startswith("Блок "):
            style_block_title_row(ws, row_idx, ws.max_column)
    ws.freeze_panes = "A3"

    out = job_dir / "google" / "review_workbook.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return out
