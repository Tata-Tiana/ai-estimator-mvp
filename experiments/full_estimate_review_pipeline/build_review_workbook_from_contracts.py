from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation


ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DIR = ROOT / "experiments" / "full_estimate_review_pipeline"
DEFAULT_OUTPUT = PIPELINE_DIR / "output" / "step_12_all_sections_review_template.xlsx"

FONT_NAME = "Arial"
FILL_HEADER = PatternFill("solid", fgColor="D9D9D9")
FILL_SECTION = PatternFill("solid", fgColor="C5CAE9")  # light indigo — 2026-08-04 design request
FILL_FOUND = PatternFill("solid", fgColor="D9EAD3")
FILL_REVIEW = PatternFill("solid", fgColor="FCE4D6")
FILL_MISSING = PatternFill("solid", fgColor="F4CCCC")
FILL_INPUT = FILL_REVIEW
FILL_PRICE = PatternFill("solid", fgColor="D9EAD3")
FILL_DETAIL = PatternFill("solid", fgColor="DAE8FC")
# Was the same RGB as FILL_SECTION (E7E6E6) until 2026-07-29 - restyle_section_bands detects
# section-band rows by fgColor alone, so an identical color made it silently re-style every
# block-title row too (wrong font/alignment/height) the moment section bands got their own
# distinct styling. Keep this a different shade from FILL_SECTION/FILL_HEADER.
FILL_TECH = PatternFill("solid", fgColor="D0CECE")
FILL_WHITE = PatternFill("solid", fgColor="FFFFFF")
BORDER_THIN = Border(
    left=Side(style="thin", color="B7B7B7"),
    right=Side(style="thin", color="B7B7B7"),
    top=Side(style="thin", color="B7B7B7"),
    bottom=Side(style="thin", color="B7B7B7"),
)

PROJECT_HEADERS = [
    "Что проверяем",
    "Найдено в проекте",
    "Ед.",
    "Статус",
    "Уверенность",
    "Что нужно сделать",
    "Источник",
    "Фрагмент проекта",
    "Исправить / ввести значение",
    "Комментарий Елены",
    "section_code",
    "technical_key",
    "source_class",
    "target_code",
]

# Same columns as PROJECT_HEADERS, same positions (so section_code/technical_key stay at the
# same absolute column letters that review_to_calculator's workbook_reader.py depends on) -
# just blanks the "Исправить / ввести значение" header label for repeated-row item blocks
# (rebar, beams, trench_routes, ...), which have their own per-field "Исправить: <поле>"
# correction columns further right instead. Real column removal would shift technical_key/
# section_code left for item rows only and break workbook_reader's fixed-letter assumptions.
ITEM_BLOCK_HEADERS = [h if h != "Исправить / ввести значение" else "" for h in PROJECT_HEADERS]

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
    "section_code",
    "calc_price_key",
    "price_registry_code",
    "fallback_key",
    "selected_price_source",
]

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
    "section_code",
    "detail_table_key",
]

CANONICAL_SECTIONS = [
    ("earthworks", "Земляные работы"),
    ("foundation_slab", "Фундаментная плита"),
    ("waterproofing", "Гидроизоляция"),
    ("load_bearing_walls_lintels", "Стены и перемычки"),
    ("floor_slab_1", "Перекрытие 1 этажа"),
    ("floor_slab_2", "Перекрытие 2 этажа"),
    ("flat_roof", "Кровля"),
    ("schiedel_vent_channels", "Schiedel / вентканалы"),
]

GENERIC_DETAIL_TEMPLATES = [
    {
        "title": "Арматура",
        "detail_table_key": "rebar_items",
        "type": "Арматура",
        "name": "Марка / позиция арматуры",
        "diameter": "Диаметр, мм",
        "length_one": "Длина, м/п",
        "quantity": "Количество",
        "total_length": "Итоговая длина, м/п",
        "fragment": "Для foundation/floor slabs/load-bearing/lintels: spec_length_m является первичной единицей, если PDF дает м/п.",
    },
    {
        "title": "Балки",
        "detail_table_key": "beam_items",
        "type": "Балка",
        "name": "Балка / позиция",
        "length": "Длина, м",
        "depth": "Высота, м",
        "width": "Ширина, м",
        "quantity": "Количество",
        "fragment": "Для плит перекрытия с балками: геометрия балки и/или строка спецификации Ж/Б балок.",
    },
    {
        "title": "Вентканалы / сегменты",
        "detail_table_key": "vent_chimney_cladding_segments",
        "type": "Вентканал",
        "name": "Сегмент / канал",
        "length": "Длина, м",
        "quantity": "Количество",
        "fragment": "Для Schiedel и обкладки вентканалов, если PDF дает повторяющиеся сегменты.",
    },
    {
        "title": "Спецификация материалов",
        "detail_table_key": "material_spec_rows",
        "type": "Материал",
        "name": "Материал / строка спецификации",
        "volume": "Объем, м3",
        "quantity": "Количество",
        "fragment": "Для ЭППС, бетона, опалубки, мембран и других строк спецификаций, которые не являются отдельной геометрией.",
    },
    {
        "title": "Сырые строки таблиц",
        "detail_table_key": "raw_table_rows",
        "type": "Raw row",
        "name": "Сырая строка PDF",
        "fragment": "Raw table row from chat extraction before mapping to target_code.",
    },
]

DIAGNOSTIC_SHEETS_HIDDEN_BY_DEFAULT = {
    "03_Детали объемов",
    "04_Инструкция",
    "05_Кандидаты parser",
    "06_Сырые данные parser",
}


def hide_diagnostic_sheets(wb: Workbook) -> None:
    for title in DIAGNOSTIC_SHEETS_HIDDEN_BY_DEFAULT:
        if title in wb.sheetnames:
            wb[title].sheet_state = "hidden"


def load_yaml_contract(path: Path) -> dict[str, Any]:
    ruby = (
        "require 'yaml'; require 'json'; "
        "puts JSON.generate(YAML.load_file(ARGV[0]))"
    )
    result = subprocess.run(
        ["ruby", "-e", ruby, str(path)],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def default_contract_paths() -> list[Path]:
    paths = []
    for code, _name in CANONICAL_SECTIONS:
        path = PIPELINE_DIR / "sections" / code / "section_contract.yaml"
        if path.exists():
            paths.append(path)
    return paths


def cell_text(value: Any) -> str:
    return "" if value is None else str(value)


_BLOCK_TITLE_RE = re.compile(r"^Блок \d+:")


def is_block_title_row(text: str) -> bool:
    """True only for real block-title rows ('Блок 0: Summary запуска', 'Блок 1: ...'), never for
    construction data that happens to start with the same Russian word for a masonry block (e.g.
    wall_block_items labels like 'Блок 150х600х250 D500, 1 этаж...'). A bare .startswith('Блок ')
    check collided with those on sheet 01 - restyle_block_sheet was merging every wall_block_items
    data row full-width as if it were a title, wiping out columns B onward (2026-08-05 real user
    report: found/status/source/fragment all blank for every masonry-block row)."""
    return bool(_BLOCK_TITLE_RE.match(text))


def style_header_row(ws, row_idx: int, max_col: int) -> None:
    for col in range(1, max_col + 1):
        cell = ws.cell(row_idx, col)
        cell.font = Font(name=FONT_NAME, bold=True, size=10)
        cell.fill = FILL_HEADER
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = BORDER_THIN


def apply_table_style(ws, header_row: int = 1) -> None:
    style_header_row(ws, header_row, ws.max_column)
    ws.freeze_panes = f"A{header_row + 1}"
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
        for cell in row:
            cell.font = Font(name=FONT_NAME, bold=cell.font.bold, size=cell.font.sz or 10)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = BORDER_THIN


def set_widths(ws, widths: dict[str, float]) -> None:
    for column, width in widths.items():
        ws.column_dimensions[column].width = width


def merge_row_full_width(ws, row_idx: int, max_col: int) -> None:
    """Merges A<row_idx>:<max_col><row_idx>, first unmerging any existing range(s) that already
    touch this row. Re-merging a row at a NEW width without unmerging the old range first does
    not raise in openpyxl (it only rejects an exact-duplicate re-merge) - it silently writes a
    second, overlapping merged range into the same row, producing a structurally invalid xlsx
    that Excel refuses to open ("reading error", real user report 2026-07-29). This happened
    because both the row-creation call (append_section_band/append_block, sheet width not yet
    final) and a later full-sheet restyle pass (restyle_section_bands/restyle_block_sheet, using
    the sheet's now-final ws.max_column) each merged the same row at a different width. Always
    unmerging first makes repeated calls at different widths safe by construction, regardless of
    call order or count."""
    if max_col <= 1:
        return
    for rng in list(ws.merged_cells.ranges):
        if rng.min_row <= row_idx <= rng.max_row:
            ws.unmerge_cells(range_string=str(rng))
    ws.merge_cells(start_row=row_idx, start_column=1, end_row=row_idx, end_column=max_col)


def _style_section_band_row(ws, row_idx: int, max_col: int) -> None:
    for col in range(1, max_col + 1):
        cell = ws.cell(row_idx, col)
        cell.fill = FILL_SECTION
        cell.font = Font(name=FONT_NAME, bold=True, color="1A237E", size=13)
        cell.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row_idx].height = 28
    # Merge across the full row width so the section name (Фундаментная плита, ...) reads as
    # one wide banner instead of bold text sitting alone in column A, which made these rows
    # visually disappear next to the much wider block-title rows below them (2026-07-29 design
    # fix, same reasoning as the block-title merge in style_block_title_row).
    merge_row_full_width(ws, row_idx, max_col)


def append_section_band(ws, row_values: list[Any], max_col: int) -> None:
    # Blank white spacer row above every indigo section band (2026-08-05 design request) so
    # section boundaries read clearly instead of the band sitting flush against the previous
    # section's last data row.
    ws.append([""] * max(1, max_col))
    ws.append(row_values + [""] * max(0, max_col - len(row_values)))
    _style_section_band_row(ws, ws.max_row, max_col)


def restyle_section_bands(ws) -> None:
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
        if row[0].fill.fgColor.rgb == "00C5CAE9":
            _style_section_band_row(ws, row[0].row, ws.max_column)


def style_block_title_row(ws, row_idx: int, max_col: int) -> None:
    for col in range(1, max_col + 1):
        cell = ws.cell(row_idx, col)
        cell.fill = FILL_TECH
        cell.font = Font(name=FONT_NAME, bold=True, color="000000", size=10)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = BORDER_THIN
    # Merge the title across the full row width so long titles wrap across all that space
    # instead of just column A - previously the text sat in column A alone, forcing 3+ wrapped
    # lines (and a tall row) even though the row already had 13+ empty-looking cells next to it.
    merge_row_full_width(ws, row_idx, max_col)


def append_block(ws, title: str, headers: list[str], rows: list[list[Any]]) -> None:
    if ws.max_row == 1 and not ws.cell(1, 1).value:
        ws.cell(1, 1).value = title
    else:
        ws.append([])
        ws.append([title])
    style_block_title_row(ws, ws.max_row, max(len(headers), 1))
    ws.append(headers)
    style_header_row(ws, ws.max_row, len(headers))
    for row in rows:
        ws.append(row)


def restyle_block_sheet(ws) -> None:
    for row_idx in range(1, ws.max_row + 1):
        first_value = cell_text(ws.cell(row_idx, 1).value)
        if is_block_title_row(first_value):
            style_block_title_row(ws, row_idx, ws.max_column)
            if row_idx + 1 <= ws.max_row:
                style_header_row(ws, row_idx + 1, ws.max_column)


def block_header_rows(ws) -> set[int]:
    rows = set()
    for row_idx in range(1, ws.max_row + 1):
        if is_block_title_row(cell_text(ws.cell(row_idx, 1).value)) and row_idx + 1 <= ws.max_row:
            rows.add(row_idx + 1)
    return rows


def section_name(contract: dict[str, Any]) -> str:
    return contract["section"]["name_ru"]


def section_code(contract: dict[str, Any]) -> str:
    return contract["section"]["code"]


def price_role_ru(price_kind: str) -> str:
    return {
        "work": "Работа",
        "material": "Материал",
        "fixed": "Фиксированная строка",
    }.get(price_kind, price_kind)


def load_price_registry(path: Path) -> dict[str, dict[str, Any]]:
    """Reads a price_registry_filled_v*.xlsx into {price_code: {price, unit, name, comment}}.
    Rows without a price_code are skipped (they don't participate in automatic lookup)."""
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb["price_registry"] if "price_registry" in wb.sheetnames else wb[wb.sheetnames[0]]
    rows = ws.iter_rows(values_only=True)
    headers = [str(cell).strip() if cell is not None else "" for cell in next(rows)]
    registry: dict[str, dict[str, Any]] = {}
    for raw in rows:
        row = dict(zip(headers, raw))
        code = row.get("price_code")
        if not code:
            continue
        code = str(code).strip()
        registry[code] = {
            "section": row.get("Раздел") or "",
            "name": row.get("Наименование") or "",
            "unit": row.get("Ед. изм.") or "",
            "price": row.get("Цена"),
            "comment": row.get("Комментарий") or "",
        }
    return registry


def load_manual_values_registry(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    """Reads manual_values_registry.xlsx into {(section_code, key): {value, comment}} - Elena's
    typical/default numbers for MANUAL_REVIEW/SUPPLIER_INPUT scalar fields (crane shifts,
    delivery trips, fixed logistics amounts, ...), the ones with no PDF source at all. Keyed by
    (section_code, key) because `key` alone repeats across sections (e.g. concrete_pump_shifts
    exists in foundation_slab, floor_slab_1, floor_slab_2 - see estimate_key_namespace_collisions
    memory). See sheet01_manual_values_catalog plan/memory, 2026-07-29."""
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb["manual_values"] if "manual_values" in wb.sheetnames else wb[wb.sheetnames[0]]
    rows = ws.iter_rows(values_only=True)
    headers = [str(cell).strip() if cell is not None else "" for cell in next(rows)]
    registry: dict[tuple[str, str], dict[str, Any]] = {}
    for raw in rows:
        row = dict(zip(headers, raw))
        sec_code = row.get("section_code")
        key = row.get("key")
        if not sec_code or not key:
            continue
        registry[(str(sec_code).strip(), str(key).strip())] = {
            "value": row.get("Типовое значение"),
            "comment": row.get("Комментарий") or "",
        }
    return registry


# Registry codes that vary per project (rebar diameter/class, roof slope plate letter) instead of
# being a fixed literal string. Contract price_keys mark these with "<...>" placeholders. See
# reports/step_27_sheet02_price_fill_plan.md section 27.5.
ROOF_SLOPE_PLATE_LETTERS = ["a", "b", "j", "k"]


def _rebar_registry_code(steel_class: Any, diameter_mm: Any) -> str | None:
    if not steel_class or diameter_mm in (None, ""):
        return None
    try:
        diameter = int(float(diameter_mm))
    except (TypeError, ValueError):
        return None
    # steel_class as extracted is Russian text (e.g. "А500С", Cyrillic А + weldability suffix
    # С) — the registry's price_code only encodes the numeric class ("rebar_a500_d10_m"), so
    # match on digits rather than transliterating letters that vary by suffix/alphabet.
    digits = re.sub(r"\D", "", str(steel_class))
    if not digits:
        return None
    return f"rebar_a{digits}_d{diameter}_m"


def resolve_price_entry(
    registry_code: str, price_registry: dict[str, dict[str, Any]] | None
) -> tuple[Any, Any, str, str, str]:
    """Returns (price_from_registry, price_for_calc, source, needs_attention, comment) for a
    single, literal (non-templated) registry_code against the given price registry."""
    if price_registry is None:
        return None, None, "", "да", "Заполнить цену из price registry/fallback/review."
    if not registry_code:
        return None, None, "no_registry_code", "да", "В контракте не указан registry_code — цену нужно ввести вручную."
    entry = price_registry.get(registry_code)
    if entry is None:
        return None, None, "not_found", "да", "Код не найден в актуальном прайсе — уточнить цену вручную."
    if entry["price"] is None:
        return None, None, "price_registry_empty", "да", "Код найден в прайсе, но цена не заполнена — уточнить у Елены."
    return entry["price"], entry["price"], "price_registry", "нет", entry.get("comment") or ""


def review_rows_for_contract(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return (contract.get("review_parameters") or []) + (contract.get("supplier_inputs") or [])


def build_constructor_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.active
    ws.title = "00_Конструктор сметы"
    contracts_by_code = {section_code(contract): contract for contract in contracts}
    headers = [
        "Раздел сметы",
        "Код раздела",
        "Включить в смету",
        "Статус готовности",
        "Что сейчас проверяется",
        "Комментарий",
    ]
    ws.append(headers)
    for code, name in CANONICAL_SECTIONS:
        contract = contracts_by_code.get(code)
        enabled = "да" if contract is not None else "нет"
        status = contract["section"].get("status", "") if contract else "позже"
        current_check = ""
        comment = ""
        if contract:
            current_check = "проверка проектных данных, цен и деталей"
            comment = (
                f"строки проверки: {len(review_rows_for_contract(contract))}; "
                f"цены: {len(contract.get('price_keys') or [])}; "
                f"детали: {len(contract.get('detail_tables') or [])}"
            )
        ws.append([
            name,
            code,
            enabled,
            status,
            current_check,
            comment,
        ])

    validation = DataValidation(type="list", formula1='"да,нет"', allow_blank=False)
    ws.add_data_validation(validation)
    validation.add(f"C2:C{ws.max_row}")
    apply_table_style(ws)
    set_widths(ws, {
        "A": 22,
        "B": 22,
        "C": 22,
        "D": 24,
        "E": 44,
        "F": 80,
    })


CORRECTION_SLOTS = 4


def is_hidden_from_sheet01(param: dict[str, Any]) -> bool:
    """review_behavior.show_to_user: false hides a field from sheet 01 entirely (not even a
    blank placeholder row) - for data that's captured in the schema but has no calculator or
    UI use yet (e.g. foundation_wall_items/column_footing_items, awaiting a future rostverk
    calculator). Was declared in the contract schema but never read by any code until now."""
    return (param.get("review_behavior") or {}).get("show_to_user") is False


def production_repeated_row_params(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        param
        for param in (contract.get("review_parameters") or [])
        if param.get("value_kind") == "repeated_rows"
        and param.get("production_input") is True
        and not is_hidden_from_sheet01(param)
    ]


def diagnostic_repeated_row_params(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """Repeated-row groups the calculator does NOT read item-by-item (it reads a reviewed
    scalar instead, e.g. trench_routes vs trench_volume_m3) but that should still render as a
    real per-item table on sheet 01 - Elena needs to see/correct the actual length/width/depth
    per route, not a single dead summary row. See build_project_sheet_from_extraction."""
    return [
        param
        for param in (contract.get("review_parameters") or [])
        if param.get("value_kind") == "repeated_rows"
        and param.get("production_input") is not True
        and not is_hidden_from_sheet01(param)
    ]


def rebar_group_keys_for_contract(contract: dict[str, Any]) -> list[str]:
    """Repeated-row groups shaped like rebar (steel_class + diameter_mm columns) — structural
    detection by column shape, not a hardcoded group-name list, so it keeps working if a new
    rebar-shaped group is added to a contract. A section can have more than one (e.g.
    load_bearing_walls_lintels has main_wall_rebar_items and lintel_rebar_items, both priced by
    the same rebar_<class>_d<diameter>_m registry_code)."""
    keys = []
    for param in contract.get("review_parameters") or []:
        if param.get("value_kind") != "repeated_rows":
            continue
        column_keys = {c.get("key") for c in (param.get("columns") or [])}
        if {"steel_class", "diameter_mm"} <= column_keys:
            keys.append(param.get("key"))
    return keys


# Sheet 01's default row height instead of Excel's auto-fit (2026-07-29 design request - "все
# строки узкие, кроме заголовков и шапочек табличек"). Applied to every scalar and per-item data
# row; title/section-band/header rows are styled separately and never touch this constant.
COMPACT_ROW_HEIGHT = 15


def estimate_row_height(ws, row_idx: int, line_height: float = 13.5) -> float:
    """Excel does not auto-grow a row for wrap_text once an explicit height is set - openpyxl has
    no autofit API, so COMPACT_ROW_HEIGHT clips any comment/fragment cell whose text needs more
    than one line (2026-08-04 real user report: long "Комментарий Елены"/"Фрагмент проекта" text
    invisible below the fixed 15pt row). Estimates wrapped-line count per cell from that cell's own
    column width (chars) and returns the taller of that and the row's current height, so short rows
    (section bands, block titles, most scalar rows) never shrink - only rows whose actual text is
    longer than one line grow."""
    current = ws.row_dimensions[row_idx].height or COMPACT_ROW_HEIGHT
    max_lines = 1
    merged_ranges_by_anchor = {
        (rng.min_row, rng.min_col): rng for rng in ws.merged_cells.ranges if rng.min_row == row_idx
    }
    for cell in ws[row_idx]:
        if not (cell.alignment and cell.alignment.wrap_text):
            continue
        value = cell.value
        if value in (None, ""):
            continue
        col_letter = getattr(cell, "column_letter", None)
        if not col_letter or ws.column_dimensions[col_letter].hidden:
            # A hidden column (e.g. the internal row_data_json adapter payload in column S) never
            # actually wraps on screen - its text length must not inflate a visible row's height
            # (2026-08-04 fix: a 250-char hidden JSON blob was forcing 300pt+ rows).
            continue
        merged_range = merged_ranges_by_anchor.get((row_idx, cell.column))
        if merged_range is not None:
            # A merged title/section-band cell wraps across its full merged width, not just its
            # own column - using only that column's width here undercounted the available line
            # width and made these rows implausibly tall (2026-08-04 fix).
            width = sum(
                ws.column_dimensions[get_column_letter(c)].width or 10
                for c in range(merged_range.min_col, merged_range.max_col + 1)
            )
        else:
            width = ws.column_dimensions[col_letter].width or 10
        chars_per_line = max(1, int(width * 0.9))  # conservative (Arial is wider than Calibri)
        for line in str(value).split("\n"):
            max_lines = max(max_lines, -(-len(line) // chars_per_line))  # ceil division
    return max(current, max_lines * line_height)


def autofit_row_heights(ws, min_row: int, max_row: int | None = None) -> None:
    """Call once column widths are final (autofit reads them), after all rows are appended."""
    for row_idx in range(min_row, (max_row or ws.max_row) + 1):
        ws.row_dimensions[row_idx].height = estimate_row_height(ws, row_idx)


# GOST 34028-2016 standard linear mass (kg per meter) by nominal rebar diameter - a physical
# constant, identical for every project, not a business judgment call. Confirmed against two real
# projects independently (2026-07-30): USV's PDF gives kg_per_meter directly and matches this
# table exactly for every diameter seen; TRC's PDF instead gives a pre-multiplied total weight_kg
# per spec line, and dividing that by the item's length reproduces this table to the rounding
# digit for every item checked. Used only as the fallback rate when an item's own kg_per_meter
# isn't given (e.g. ARK's PDF gives length only, no mass column at all) - see
# rebar_weight_standard_gost_table memory/plan entry.
GOST_REBAR_KG_PER_METER = {
    6: 0.222,
    8: 0.395,
    10: 0.617,
    12: 0.888,
    16: 1.6,
    20: 2.47,
    25: 3.85,
}


def rebar_item_weight_kg(item: dict[str, Any]) -> float | None:
    """One rebar item's total weight in kg = length_m * rate. rate is the item's own
    kg_per_meter if the PDF/extraction gave it, else GOST_REBAR_KG_PER_METER by diameter. A
    PDF-given total weight_kg (when present, e.g. TRC) is deliberately NOT read here as an
    independent input - per the 2026-07-30 decision, length x rate is the only path to a rebar
    item's weight, so there is exactly one way to get the number, never two that could disagree.
    Returns None (does not guess) if there's no length, or no rate is available anywhere."""
    length = item.get("spec_length_m")
    if length is None:
        length = item.get("source_length_m")
    if length is None:
        return None
    rate = item.get("kg_per_meter")
    if rate is None:
        diameter = item.get("diameter_mm")
        try:
            diameter_int = int(round(float(diameter))) if diameter is not None else None
        except (TypeError, ValueError):
            diameter_int = None
        rate = GOST_REBAR_KG_PER_METER.get(diameter_int) if diameter_int is not None else None
    if rate is None:
        return None
    return float(length) * float(rate)


# source_class values with no PDF signal at all - Elena types/confirms these regardless of
# project, they're never something the parser could find. Moved off sheet 01 onto sheet 01-1
# (manual values catalog) 2026-07-29 so sheet 01 is exclusively parser-found data, per the
# user's explicit "лист 01 только для данных из парсера и больше никак".
MANUAL_VALUE_SOURCE_CLASSES = {"MANUAL_REVIEW", "SUPPLIER_INPUT"}


def scalar_review_rows_for_contract(contract: dict[str, Any]) -> list[dict[str, Any]]:
    # Every repeated-row group (production AND diagnostic-only) gets its own real per-item
    # block below instead of a row here - see production_repeated_row_params and
    # diagnostic_repeated_row_params. A single scalar-shaped row for a repeated-row group
    # can never show real data (it looks up found_by_target[group_key], but real item data
    # lives in found_groups[group_key] instead) - this used to silently render trench_routes/
    # communications_pipe_items/etc. as a permanently-blank "Проверьте" row even when the
    # extraction had real per-item data. Fields with show_to_user: false (e.g.
    # foundation_wall_items, column_footing_items - awaiting a future calculator) are hidden
    # entirely, not rendered as a dead row either. MANUAL_REVIEW/SUPPLIER_INPUT fields render on
    # sheet 01-1 instead (manual_values_rows_for_contract) - see MANUAL_VALUE_SOURCE_CLASSES.
    review_parameters = [
        param
        for param in (contract.get("review_parameters") or [])
        if param.get("value_kind") != "repeated_rows"
        and not is_hidden_from_sheet01(param)
        and param.get("source_class") not in MANUAL_VALUE_SOURCE_CLASSES
    ]
    supplier_inputs = [
        param
        for param in (contract.get("supplier_inputs") or [])
        if not is_hidden_from_sheet01(param) and param.get("source_class") not in MANUAL_VALUE_SOURCE_CLASSES
    ]
    return review_parameters + supplier_inputs


def manual_values_rows_for_contract(contract: dict[str, Any]) -> list[dict[str, Any]]:
    """MANUAL_REVIEW/SUPPLIER_INPUT scalar fields for sheet 01-1 - see MANUAL_VALUE_SOURCE_CLASSES."""
    params = (contract.get("review_parameters") or []) + (contract.get("supplier_inputs") or [])
    return [
        param
        for param in params
        if param.get("value_kind") != "repeated_rows"
        and not is_hidden_from_sheet01(param)
        and not param.get("exclude_from_manual_values_registry")
        and param.get("source_class") in MANUAL_VALUE_SOURCE_CLASSES
    ]


def correction_headers(param: dict[str, Any]) -> list[str]:
    columns_by_key = {col.get("key"): col for col in param.get("columns") or []}
    headers = []
    for key in param.get("correction_columns") or []:
        col = columns_by_key.get(key, {})
        label = col.get("label_ru", key)
        unit = col.get("unit") or ""
        headers.append(f"Исправить: {label}{', ' + unit if unit else ''}")
    while len(headers) < CORRECTION_SLOTS:
        headers.append("")
    return headers[:CORRECTION_SLOTS]


def build_project_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.create_sheet("01_Проверка проекта")
    project_title = "Разбор проекта:\n" + " + ".join(section_name(contract) for contract in contracts)
    ws.append([project_title, "", "", "", "", "", "", "", "", "", "", "", "", ""])
    review_count = sum(len(review_rows_for_contract(contract)) for contract in contracts)
    ws.append([
        "Найдено уверенно: 0",
        f"Проверьте: {review_count}",
        "Не найдено: 0",
        "Ручной ввод: 0",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
    ])
    ws.append([])
    ws.append(PROJECT_HEADERS)

    for contract in contracts:
        append_section_band(ws, [section_name(contract)], len(PROJECT_HEADERS))
        for param in scalar_review_rows_for_contract(contract):
            review_behavior = param.get("review_behavior") or {}
            ws.append([
                param.get("label_ru", param.get("key", "")),
                None,
                param.get("unit", ""),
                "Проверьте",
                "",
                review_behavior.get("action_ru", "Проверьте значение."),
                "",
                "",
                "",
                "",
                section_code(contract),
                param.get("key", ""),
                param.get("source_class", ""),
                param.get("target_code", ""),
            ])
            for cell in ws[ws.max_row]:
                cell.fill = FILL_INPUT
            ws.row_dimensions[ws.max_row].height = COMPACT_ROW_HEIGHT

        # Production repeated-row groups (rebar, beams): построчно, каждая позиция отдельной
        # строкой в тех же видимых колонках A-I, никакой отдельной "спецификационной" таблицы
        # здесь - та живет на листе 03. Видимые "Исправить: ..." колонки - по одной на реально
        # корректируемое числовое поле группы (длина/масса для арматуры, длина/ширина/высота/
        # количество для балок), а не общая "Исправить/ввести значение". Скрытая row_data_json
        # несет полный структурный набор полей строки для адаптера - никакого текста парсить не
        # придется. Шаблон контрактов не содержит реальных данных проекта, поэтому строк-примеров
        # здесь нет - только заголовок блока, как и на листе 03.
        for param in production_repeated_row_params(contract) + diagnostic_repeated_row_params(contract):
            review_behavior = param.get("review_behavior") or {}
            action_ru = review_behavior.get("action_ru", "Проверьте позиции построчно.")
            title = f"{section_name(contract)} — {param.get('label_ru', param.get('key', ''))} ({action_ru})"
            headers = ITEM_BLOCK_HEADERS + correction_headers(param) + ["row_data_json"]
            append_block(ws, title, headers, [])

    ws.cell(1, 1).font = Font(name=FONT_NAME, bold=True, size=13)
    ws.cell(1, 1).fill = FILL_HEADER
    apply_table_style(ws, header_row=4)
    restyle_section_bands(ws)
    restyle_block_sheet(ws)
    merge_row_full_width(ws, 1, ws.max_column)
    ws.freeze_panes = "A5"
    set_widths(ws, {
        "A": 30,
        "B": 22,
        "C": 10,
        "D": 16,
        "E": 20,
        "F": 62,
        "G": 48,
        "H": 64,
        "I": 28,
        "J": 28,
        "K": 20,
        "L": 28,
        "M": 18,
        "N": 24,
        "O": 24,
        "P": 24,
        "Q": 24,
    })
    for column in ["K", "L", "M", "N", "S"]:
        ws.column_dimensions[column].hidden = True


def expand_rebar_codes(rebar_items: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """Given a section's real rebar rows (steel_class/diameter_mm), returns deduped
    (label_suffix, actual_registry_code) pairs, e.g. (" — A500 Ø10", "rebar_a500_d10_m")."""
    seen: dict[str, tuple[str, str]] = {}
    for item in rebar_items:
        steel_class = item.get("steel_class")
        diameter_mm = item.get("diameter_mm")
        code = _rebar_registry_code(steel_class, diameter_mm)
        if code is None:
            continue
        seen[code] = (f" — {steel_class} Ø{diameter_mm}", code)
    return [seen[code] for code in sorted(seen)]


def find_roof_slope_code(price_registry: dict[str, dict[str, Any]], letter: str) -> str | None:
    suffix = f"_plate_{letter}_m3"
    matches = [
        code
        for code in price_registry
        if code.startswith("roof_eps_slope_") and code.endswith(suffix)
    ]
    return matches[0] if matches else None


def expand_roof_slope_codes(price_registry: dict[str, dict[str, Any]]) -> list[tuple[str, str | None]]:
    result = []
    for letter in ROOF_SLOPE_PLATE_LETTERS:
        code = find_roof_slope_code(price_registry, letter)
        result.append((f" — плита {letter.upper()}", code))
    return result


_SOURCE_LABEL_RU = {
    "price_registry": "price_registry",
    "not_found": "не найдено в прайсе",
    "price_registry_empty": "прайс: цена пустая",
    "no_registry_code": "нет registry_code",
    "price_registry_template": "шаблонный код",
}

_SOURCE_FILL = {
    "price_registry": FILL_FOUND,
    "not_found": FILL_MISSING,
    "price_registry_empty": FILL_REVIEW,
    "no_registry_code": FILL_MISSING,
    "price_registry_template": FILL_REVIEW,
}


def _append_price_row(
    ws,
    label_ru: str,
    price: dict[str, Any],
    sec_code: str,
    registry_code_actual: str,
    price_registry: dict[str, dict[str, Any]] | None,
) -> None:
    if price_registry is not None and "<" in registry_code_actual:
        # Unresolvable template (no per-project expansion available for this pattern).
        price_from, price_for_calc, source, needs_attention, comment = (
            None, None, "price_registry_template", "да",
            "Шаблонный код цены — раскрывается по фактическим строкам проекта (см. лист 01/03).",
        )
    else:
        price_from, price_for_calc, source, needs_attention, comment = resolve_price_entry(
            registry_code_actual, price_registry
        )
    source_label = _SOURCE_LABEL_RU.get(source, source) if price_registry is not None else price.get("default_source", "")
    fill = _SOURCE_FILL.get(source, FILL_REVIEW) if price_registry is not None else FILL_PRICE
    ws.append([
        label_ru,
        price_role_ru(str(price.get("price_kind", ""))),
        price.get("unit", ""),
        price_from,
        None,
        price_for_calc,
        "",
        source_label,
        needs_attention,
        comment,
        sec_code,
        price.get("key", ""),
        registry_code_actual,
        price.get("fallback_key", ""),
        source,
    ])
    for cell in ws[ws.max_row]:
        cell.fill = fill


def build_prices_sheet(
    wb: Workbook,
    contracts: list[dict[str, Any]],
    price_registry: dict[str, dict[str, Any]] | None = None,
    rebar_lookup: dict[str, list[dict[str, Any]]] | None = None,
) -> None:
    """Builds sheet 02. With no price_registry (default), behaves exactly as before: an empty
    price template. Pass price_registry (see load_price_registry) to fill it from the real
    price list. rebar_lookup (section_code -> real rebar rows with steel_class/diameter_mm,
    only available when building from a real extraction) expands the rebar_<class>_d<diameter>_m
    template into one row per diameter/class actually present in the project; without it, that
    template renders as a single flagged placeholder row. See
    reports/step_27_sheet02_price_fill_plan.md."""
    ws = wb.create_sheet("02_Цены себестоимости")
    ws.append(PRICE_HEADERS)
    for contract in contracts:
        append_section_band(ws, [section_name(contract)], len(PRICE_HEADERS))
        sec_code = section_code(contract)
        for price in contract.get("price_keys") or []:
            registry_code = price.get("registry_code", "") or ""
            label_ru = price.get("label_ru", "")

            rebar_expansion = (
                expand_rebar_codes(rebar_lookup[sec_code])
                if registry_code == "rebar_<class>_d<diameter>_m" and rebar_lookup and rebar_lookup.get(sec_code)
                else []
            )
            if rebar_expansion:
                for suffix, actual_code in rebar_expansion:
                    _append_price_row(ws, label_ru + suffix, price, sec_code, actual_code, price_registry)
            elif registry_code == "roof_eps_slope_<type>_m3" and price_registry is not None:
                for suffix, actual_code in expand_roof_slope_codes(price_registry):
                    if actual_code is None:
                        _append_price_row(ws, label_ru + suffix, price, sec_code, registry_code, price_registry)
                    else:
                        _append_price_row(ws, label_ru + suffix, price, sec_code, actual_code, price_registry)
            else:
                _append_price_row(ws, label_ru, price, sec_code, registry_code, price_registry)

    apply_table_style(ws)
    restyle_section_bands(ws)
    set_widths(ws, {
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
        "K": 20,
        "L": 30,
        "M": 30,
        "N": 30,
        "O": 22,
    })
    for column in ["K", "L", "M", "N", "O"]:
        ws.column_dimensions[column].hidden = True


MANUAL_VALUES_HEADERS = [
    "Строка",
    "Ед.",
    "Типовое значение (справочник)",
    "Исправить для этого проекта",
    "Источник",
    "Комментарий",
    "section_code",
    "key",
]


def build_manual_values_sheet(
    wb: Workbook,
    contracts: list[dict[str, Any]],
    manual_values_registry: dict[tuple[str, str], dict[str, Any]] | None = None,
) -> None:
    """Builds sheet 01-1: MANUAL_REVIEW/SUPPLIER_INPUT scalar fields (crane shifts, delivery
    trips, fixed logistics amounts, ...) that have no PDF source at all - see
    MANUAL_VALUE_SOURCE_CLASSES. These used to render on sheet 01 mixed in with real parser
    data and always blank; sheet 01 is parser-only now (2026-07-29). With no registry passed,
    this is an empty template (every value blank, flagged for attention) - pass
    manual_values_registry (see load_manual_values_registry) to pre-fill Elena's typical
    values, which she can still override per project in the "Исправить для этого проекта"
    column without touching the registry itself."""
    ws = wb.create_sheet("01-1_Ручные строки (справочник)")
    ws.append(MANUAL_VALUES_HEADERS)
    for contract in contracts:
        rows = manual_values_rows_for_contract(contract)
        if not rows:
            continue
        append_section_band(ws, [section_name(contract)], len(MANUAL_VALUES_HEADERS))
        sec_code = section_code(contract)
        for param in rows:
            entry = manual_values_registry.get((sec_code, param.get("key"))) if manual_values_registry else None
            if manual_values_registry is None:
                typical_value, source, comment, fill = None, "", "", FILL_REVIEW
            elif entry is None:
                typical_value, source, comment, fill = None, "нет в справочнике", "Добавьте типовое значение в manual_values_registry.xlsx или заполните вручную для этого проекта.", FILL_MISSING
            elif entry["value"] in (None, ""):
                typical_value, source, comment, fill = None, "справочник: значение пустое", entry["comment"], FILL_REVIEW
            else:
                typical_value, source, comment, fill = entry["value"], "справочник", entry["comment"], FILL_FOUND
            ws.append([
                param.get("label_ru", param.get("key", "")),
                param.get("unit", ""),
                typical_value,
                "",
                source,
                comment,
                sec_code,
                param.get("key", ""),
            ])
            for cell in ws[ws.max_row]:
                cell.fill = fill

    apply_table_style(ws)
    restyle_section_bands(ws)
    set_widths(ws, {"A": 44, "B": 10, "C": 22, "D": 22, "E": 22, "F": 44, "G": 22, "H": 30})
    for column in ["G", "H"]:
        ws.column_dimensions[column].hidden = True


def repeated_row_params(contract: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        param
        for param in (contract.get("review_parameters") or [])
        if param.get("value_kind") == "repeated_rows" and param.get("columns")
    ]


def repeated_row_headers(param: dict[str, Any]) -> list[str]:
    headers = []
    for col in param.get("columns") or []:
        label = col.get("label_ru", col.get("key", ""))
        unit = col.get("unit") or ""
        headers.append(f"{label}{', ' + unit if unit else ''}")
    return headers


def generic_detail_row(template: dict[str, Any]) -> list[Any]:
    return [
        template.get("type", ""),
        template.get("name", ""),
        template.get("length", ""),
        template.get("depth", ""),
        template.get("width", ""),
        template.get("volume", ""),
        template.get("diameter", ""),
        template.get("length_one", ""),
        template.get("quantity", ""),
        template.get("total_length", ""),
        "",
        "",
        template.get("fragment", ""),
        "",
        "template",
        template.get("detail_table_key", ""),
    ]


def build_details_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    # Real repeated-row groups (rebar_items, beam_items, lintel_rebar_items, etc.) are declared as
    # review_parameters entries with value_kind: repeated_rows, not a separate detail_tables key -
    # no contract has ever used detail_tables. Each such entry that opts in with
    # mirror_to_details_sheet: true gets its own titled block here, with headers taken directly
    # from that entry's own columns list (found missing 2026-07-11 - this sheet was previously
    # always empty of real project content for all 8 sections, only showing the generic templates
    # below).
    ws = wb.create_sheet("03_Детали объемов")
    has_real_block = False
    for contract in contracts:
        for param in repeated_row_params(contract):
            if not param.get("mirror_to_details_sheet"):
                continue
            headers = repeated_row_headers(param)
            if not headers:
                continue
            title = f"{section_name(contract)} — {param.get('label_ru', param.get('key', ''))}"
            append_block(
                ws,
                title,
                headers + ["Комментарий Елены", "section_code", "target_code"],
                [],
            )
            has_real_block = True

    if has_real_block:
        ws.append([])
    ws.append(["Будущие detail-шаблоны (общие заготовки, не привязаны к конкретному контракту)"])
    style_block_title_row(ws, ws.max_row, 1)
    for template in GENERIC_DETAIL_TEMPLATES:
        ws.append([])
        append_section_band(ws, [template["title"]], len(DETAIL_HEADERS))
        ws.append(DETAIL_HEADERS)
        style_header_row(ws, ws.max_row, len(DETAIL_HEADERS))
        ws.append(generic_detail_row(template))
        for cell in ws[ws.max_row]:
            cell.fill = FILL_WHITE

    apply_table_style(ws)
    restyle_block_sheet(ws)
    restyle_section_bands(ws)
    set_widths(ws, {chr(ord("A") + i): 26 for i in range(16)})


def build_instruction_sheet(wb: Workbook) -> None:
    ws = wb.create_sheet("04_Инструкция")
    ws.append(["Раздел", "Инструкция"])
    rows = [
        (0, "Выберите разделы, которые входят в смету."),
        (1, "Проверьте проектные параметры. Пустые значения должны быть заполнены parser/chat JSON или вручную."),
        (2, "Проверьте себестоимость. Цена для расчета должна прийти из price registry, fallback или ручной правки."),
        (3, "Проверьте детальные таблицы. Это проектные строки, а не строки финальной сметы."),
        (5, "Технический лист показывает, из каких контрактов собрана таблица."),
        (6, "Сырые данные parser нужны разработчику для диагностики структуры."),
    ]
    for row in rows:
        ws.append(row)
    apply_table_style(ws)
    set_widths(ws, {"A": 8, "B": 120})


def build_contracts_summary_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.create_sheet("05_Кандидаты parser")
    total_review = sum(len(review_rows_for_contract(contract)) for contract in contracts)
    total_prices = sum(len(contract.get("price_keys") or []) for contract in contracts)
    total_detail = sum(len(contract.get("detail_tables") or []) for contract in contracts)
    total_defaults = sum(len(contract.get("defaults") or []) for contract in contracts)
    total_auto = sum(len(contract.get("auto_calculated") or []) for contract in contracts)

    append_block(
        ws,
        "Блок 0: Summary запуска",
        ["Показатель", "Значение", "Комментарий"],
        [
            ["source", "section_contracts", "workbook собран локально из section_contract.yaml"],
            ["sections_count", len(contracts), "сколько section contracts загружено"],
            ["review_rows_count", total_review, "сколько строк проверки проекта, включая supplier/manual inputs"],
            ["price_rows_count", total_prices, "сколько строк цен"],
            ["detail_templates_count", total_detail + len(GENERIC_DETAIL_TEMPLATES), "сколько detail-шаблонов"],
            ["defaults_count", total_defaults, "числовые default/ручные параметры остаются в contracts"],
            ["auto_calculated_count", total_auto, "поля, которые должны считаться кодом, а не извлекаться из PDF"],
            ["parser_candidates_connected", "нет", "будет заполнено на шаге extraction JSON -> workbook"],
        ],
    )

    contract_rows = []
    for contract in contracts:
        contract_rows.append([
            section_code(contract),
            section_name(contract),
            len(review_rows_for_contract(contract)),
            len(contract.get("price_keys") or []),
            len(contract.get("detail_tables") or []),
            len(contract.get("supplier_inputs") or []),
            len(contract.get("defaults") or []),
            len(contract.get("auto_calculated") or []),
            len(contract.get("estimate_lines") or []),
            json.dumps(contract.get("source_files") or {}, ensure_ascii=False),
        ])
    append_block(
        ws,
        "Блок 1: section contracts",
        [
            "section_code",
            "section_name",
            "review_rows",
            "price_keys",
            "detail_tables",
            "supplier_inputs",
            "defaults",
            "auto_calculated",
            "estimate_lines",
            "source_files",
        ],
        contract_rows,
    )

    detail_rows = []
    for contract in contracts:
        for table in contract.get("detail_tables") or []:
            detail_rows.append([
                table.get("key", ""),
                table.get("label_ru", ""),
                "contract",
                section_code(contract),
                "детальная таблица уже описана в section_contract.yaml",
            ])
    for template in GENERIC_DETAIL_TEMPLATES:
        detail_rows.append([
            template.get("detail_table_key", ""),
            template.get("title", ""),
            template.get("type", ""),
            "future sections",
            template.get("fragment", ""),
        ])
    append_block(
        ws,
        "Блок 2: planned detail groups",
        ["detail_table_key", "title", "type", "used_for", "comment"],
        detail_rows,
    )

    apply_table_style(ws)
    restyle_block_sheet(ws)
    set_widths(ws, {
        "A": 24,
        "B": 34,
        "C": 28,
        "D": 22,
        "E": 34,
        "F": 18,
        "G": 22,
        "H": 18,
        "I": 18,
        "J": 100,
    })
    header_rows = block_header_rows(ws)
    for row in ws.iter_rows(min_row=1):
        for cell in row:
            if not is_block_title_row(cell_text(ws.cell(cell.row, 1).value)) and cell.row not in header_rows:
                cell.fill = FILL_WHITE


def build_raw_contracts_sheet(wb: Workbook, contracts: list[dict[str, Any]]) -> None:
    ws = wb.create_sheet("06_Сырые данные parser")
    append_block(
        ws,
        "Блок 0: Summary запуска",
        ["Показатель", "Значение", "Комментарий"],
        [
            ["source", "section_contracts", "сырые parser/chat данные подключаются следующим шагом"],
            ["sections_count", len(contracts), "сколько section contracts загружено"],
            ["raw_parser_json_connected", "нет", "пока лист показывает сырье contracts для диагностики"],
        ],
    )
    raw_rows = []
    for contract in contracts:
        for block in [
            "section",
            "review_parameters",
            "price_keys",
            "detail_tables",
            "supplier_inputs",
            "defaults",
            "auto_calculated",
            "estimate_lines",
        ]:
            raw_rows.append([
                section_code(contract),
                block,
                json.dumps(contract.get(block), ensure_ascii=False, indent=2),
            ])
    append_block(ws, "Блок 1: raw contract blocks", ["section_code", "block", "json"], raw_rows)
    apply_table_style(ws)
    restyle_block_sheet(ws)
    set_widths(ws, {"A": 24, "B": 24, "C": 120})
    header_rows = block_header_rows(ws)
    for row in ws.iter_rows(min_row=1):
        for cell in row:
            if not is_block_title_row(cell_text(ws.cell(cell.row, 1).value)) and cell.row not in header_rows:
                cell.fill = FILL_WHITE


def build_workbook(contract_paths: list[Path], output_path: Path) -> dict[str, Any]:
    contracts = [load_yaml_contract(path) for path in contract_paths]
    wb = Workbook()
    build_constructor_sheet(wb, contracts)
    build_project_sheet(wb, contracts)
    build_manual_values_sheet(wb, contracts)
    build_prices_sheet(wb, contracts)
    build_details_sheet(wb, contracts)
    build_instruction_sheet(wb)
    build_contracts_summary_sheet(wb, contracts)
    build_raw_contracts_sheet(wb, contracts)
    hide_diagnostic_sheets(wb)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    check = inspect_workbook(output_path)
    check["output_path"] = str(output_path)
    check["contracts"] = [str(path) for path in contract_paths]
    check["detail_groups_rendered"] = sum(
        1
        for contract in contracts
        for param in repeated_row_params(contract)
        if param.get("mirror_to_details_sheet")
    )
    return check


def inspect_workbook(path: Path) -> dict[str, Any]:
    wb = load_workbook(path, data_only=False)
    sheets = wb.sheetnames
    ws_project = wb["01_Проверка проекта"]
    ws_prices = wb["02_Цены себестоимости"]
    ws_details = wb["03_Детали объемов"]

    project_rows = 0
    project_item_blocks = 0
    for row_idx in range(5, ws_project.max_row + 1):
        technical_key = cell_text(ws_project.cell(row_idx, 11).value)
        if technical_key == "technical_key":
            # Local header row of a production repeated-row block (rebar/beams item blocks),
            # not a real parameter row - counted separately below.
            project_item_blocks += 1
            continue
        if technical_key:
            project_rows += 1

    price_rows = 0
    for row_idx in range(2, ws_prices.max_row + 1):
        if cell_text(ws_prices.cell(row_idx, 12).value):
            price_rows += 1

    return {
        "sheet_names": sheets,
        "project_parameter_rows": project_rows,
        "project_item_blocks": project_item_blocks,
        "price_rows": price_rows,
        "project_max_row": ws_project.max_row,
        "price_max_row": ws_prices.max_row,
        "details_max_row": ws_details.max_row,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--contract",
        action="append",
        dest="contracts",
        help="Path to section_contract.yaml. Can be passed multiple times.",
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    contract_paths = [Path(item) for item in args.contracts] if args.contracts else default_contract_paths()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path
    check = build_workbook(contract_paths, output_path)
    if args.json:
        print(json.dumps(check, ensure_ascii=False, indent=2))
    else:
        print(f"built: {check['output_path']}")
        print(f"sheets: {', '.join(check['sheet_names'])}")
        print(f"project_parameter_rows: {check['project_parameter_rows']}")
        print(f"project_item_blocks: {check['project_item_blocks']}")
        print(f"price_rows: {check['price_rows']}")
        print(f"detail_groups_rendered: {check['detail_groups_rendered']}")


if __name__ == "__main__":
    main()
