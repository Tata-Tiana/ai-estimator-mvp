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
    match = re.fullmatch(r"(К)\s*(\d+)", text)
    if match:
        return f"{match.group(1)} {match.group(2)}"
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
    append_table(ws, PRICE_HEADERS, price_rows(price_resolution))
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
        },
    )
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
    ws.append(["Технический лист для разработчика. Здесь показаны все кандидаты parser-а, включая невыбранные."])
    ws.cell(1, 1).font = Font(name=FONT_NAME, bold=True, size=12)
    candidate_headers = ["Параметр", "technical_key", "candidate_value", "unit", "confidence", "extraction_rule", "logical_sheet_title", "logical_sheet_type", "source_pdf", "page", "raw_fragment", "analysis_notes", "candidate_id"]
    ws.append(candidate_headers)
    for key, parameter in extracted["parameters"].items():
        ev = parameter.get("evidence") or {}
        ws.append([
            PARAM_META.get(key, (key, ""))[0],
            key,
            excel_value(parameter.get("value")),
            parameter.get("unit", ""),
            ev.get("confidence", ""),
            parameter.get("source", ""),
            ev.get("logical_sheet_title", ""),
            ev.get("logical_sheet_type", ""),
            ev.get("source_pdf", ""),
            ev.get("physical_page_number", ""),
            ev.get("raw_context", ""),
            parameter.get("interpretation", ""),
            ev.get("evidence_id", ""),
        ])
    style_sheet_basic(
        ws,
        header_row=2,
        widths={
            "A": 28,
            "B": 28,
            "C": 24,
            "D": 10,
            "E": 14,
            "F": 28,
            "G": 28,
            "H": 28,
            "I": 22,
            "J": 10,
            "K": 86,
            "L": 28,
            "M": 24,
        },
    )

    ws = wb.create_sheet("06_Сырые данные parser")
    logical_pages = read_json(V3_LOGICAL_PAGES_PATH, [])
    raw_candidates = read_json(V3_CANDIDATES_PATH, [])
    raw_tables = read_json(V3_TABLES_PATH, [])
    ws.append(["Блок 1: logical sheets"])
    ws.append(["source_pdf", "physical_page_number", "drawing_sheet_number", "logical_sheet_title", "logical_sheet_type", "confidence", "matched_terms"])
    for page in logical_pages:
        ws.append([page.get("source_pdf", ""), page.get("physical_page_number", ""), page.get("drawing_sheet_number", ""), page.get("logical_sheet_title", ""), page.get("logical_sheet_type", ""), page.get("confidence", ""), excel_value(page.get("matched_terms", ""))])
    ws.append([])
    ws.append(["Блок 2: extracted parameters raw"])
    ws.append(["technical_key", "ru_label", "value", "unit", "extraction_status", "confidence", "source_pdf", "page", "logical_sheet_title", "logical_sheet_type", "raw_fragment", "all_candidates", "analysis_notes"])
    for key, parameter in extracted["parameters"].items():
        ev = parameter.get("evidence") or {}
        ws.append([key, PARAM_META.get(key, (key, ""))[0], excel_value(parameter.get("value")), parameter.get("unit", ""), "found" if parameter.get("value") is not None else "missing", ev.get("confidence", ""), ev.get("source_pdf", ""), ev.get("physical_page_number", ""), ev.get("logical_sheet_title", ""), ev.get("logical_sheet_type", ""), ev.get("raw_context", ""), ev.get("evidence_id", ""), parameter.get("interpretation", "")])
    ws.append([])
    ws.append(["Блок 3: raw parser counters"])
    counters = {
        "pages_count": len(logical_pages),
        "tables_count": len(raw_tables),
        "logical_sheets_count": len(logical_pages),
        "candidates_count": len(raw_candidates),
        "found_count": sum(1 for parameter in extracted["parameters"].values() if parameter.get("value") is not None),
        "attention_count": review,
        "missing_count": sum(1 for parameter in extracted["parameters"].values() if parameter.get("value") is None),
    }
    for key, value in counters.items():
        ws.append([key, value])
    apply_table_theme(ws)
    set_widths(
        ws,
        {
            "A": 34,
            "B": 16,
            "C": 18,
            "D": 10,
            "E": 20,
            "F": 16,
            "G": 22,
            "H": 16,
            "I": 30,
            "J": 28,
            "K": 86,
            "L": 32,
            "M": 32,
        },
    )

    out = job_dir / "google" / "review_workbook.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return out
