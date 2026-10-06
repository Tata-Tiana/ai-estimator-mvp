from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import column_index_from_string, get_column_letter


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_LOGO_PATH = BASE_DIR / "assets" / "brick_house_logo.png"

SHEET_NAME = "Земляные работы"
TITLE_TEXT = "СМЕТНЫЙ РАСЧЕТ НА СТРОИТЕЛЬСТВО ДОМА"

GROUP_HEADER_ROW = 9
SUBHEADER_ROW = 10
SECTION_ROW = 11
FIRST_DATA_ROW = 12

CALC_ZONE_COL: dict[str, str] = {
    "quantity": "J",
    "material_unit_price": "K",
    "material_total": "L",
    "work_unit_price": "M",
    "work_total": "N",
    "row_total": "O",
}

WHITE_ZONE_MIRROR: dict[str, str] = {
    "D": "J", "E": "K", "F": "L",
    "G": "M", "H": "N", "I": "O",
}

HELPER_COLS = list("PQRSTUV")
MAX_HELPER_CELLS = len(HELPER_COLS)

_GREY = PatternFill("solid", fgColor="FFB7B7B7")
_WHITE = PatternFill("solid", fgColor="FFFFFFFF")
_SECTION = PatternFill("solid", fgColor="FFEFEFEF")
_TOTAL = PatternFill("solid", fgColor="FFD9EAF7")
_THIN = Side(style="thin", color="303030")
_BLUE = Side(style="thick", color="1D4ED8")
_BORDER = Border(left=_THIN, right=_THIN, top=_THIN, bottom=_THIN)
_SPLIT = Border(left=_BLUE, right=_THIN, top=_THIN, bottom=_THIN)


# ── Formula translation ───────────────────────────────────────────────────────

def _ref_to_cell(ref: str, row: int, helper_id_to_col: dict[str, str]) -> str | None:
    if ref.startswith("calc_zone."):
        field = ref[len("calc_zone."):]
        col = CALC_ZONE_COL.get(field)
        return f"{col}{row}" if col else None
    if ref.startswith("helper_zone."):
        helper_id = ref[len("helper_zone."):]
        col = helper_id_to_col.get(helper_id)
        return f"{col}{row}" if col else None
    return None


def _translate_node(node: Any, row: int, helper_id_to_col: dict[str, str]) -> str | None:
    if not isinstance(node, dict):
        return None
    if "ref" in node and len(node) == 1:
        return _ref_to_cell(node["ref"], row, helper_id_to_col)
    t = node.get("type")
    if t == "ref":
        operand = node.get("operand")
        if isinstance(operand, dict) and "ref" in operand:
            return _ref_to_cell(operand["ref"], row, helper_id_to_col)
        return None
    if t == "multiply":
        parts: list[str] = []
        for op in node.get("operands", []):
            part = _translate_node(op, row, helper_id_to_col)
            if part is None:
                return None
            if isinstance(op, dict) and op.get("type") == "sum":
                part = f"({part})"
            parts.append(part)
        return "*".join(parts)
    if t == "sum":
        parts = []
        for op in node.get("operands", []):
            part = _translate_node(op, row, helper_id_to_col)
            if part is None:
                return None
            parts.append(part)
        return "+".join(parts)
    if t == "ceil_divide":
        operands = node.get("operands", [])
        if len(operands) < 2:
            return None
        a = _translate_node(operands[0], row, helper_id_to_col)
        b = _translate_node(operands[1], row, helper_id_to_col)
        if a is None or b is None:
            return None
        return f"ROUNDUP({a}/{b},0)"
    if t == "roundup_to_step":
        val_ref = node.get("value_ref")
        step_ref = node.get("step_ref")
        v = _translate_node(val_ref, row, helper_id_to_col)
        s = _translate_node(step_ref, row, helper_id_to_col)
        if v is None or s is None:
            return None
        return f"ROUNDUP({v}/{s},0)*{s}"
    return None


def _to_excel_formula(
    cell_dict: dict[str, Any],
    row: int,
    helper_id_to_col: dict[str, str],
) -> str | None:
    if cell_dict.get("excel_formula_exportable") is False:
        return None
    fm = cell_dict.get("formula_model")
    if fm is None:
        return None
    expr = _translate_node(fm, row, helper_id_to_col)
    return f"={expr}" if expr else None


def _build_helper_id_to_col(helper_cells: list[dict[str, Any]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for cell in helper_cells:
        helper_id = str(cell.get("helper_id", ""))
        target = str(cell.get("target_col_role", ""))
        if helper_id and target:
            result[helper_id] = target
    return result


# ── Header (rows 1–11) ────────────────────────────────────────────────────────

def _setup_top_header(
    sheet: Any,
    logo_path: Path,
    address: str,
    section_number: str | int | None,
    section_title: str,
    right_col: int = 22,
) -> None:
    # Grey background for calc+helper+mini-table zone in header rows 1–8
    for row in range(1, 9):
        for col in range(10, right_col + 1):
            sheet.cell(row, col).fill = _GREY

    # A1:I4 — logo
    sheet.merge_cells("A1:I4")
    if logo_path.exists():
        logo = OpenpyxlImage(str(logo_path))
        logo.width = 300
        logo.height = 50
        sheet.add_image(logo, "C2")
    else:
        raise FileNotFoundError(
            f"Logo file not found: {logo_path}\n"
            "Place brick_house_logo.png in experiments/earthworks_review_to_calculator/assets/ "
            "or pass --logo-path."
        )

    # A5:I5 — estimate title
    sheet.merge_cells("A5:I5")
    c = sheet["A5"]
    c.value = TITLE_TEXT
    c.font = Font(size=12, bold=True)
    c.alignment = Alignment(horizontal="center", vertical="center")

    # A6:I6 — project address
    sheet.merge_cells("A6:I6")
    c = sheet["A6"]
    c.value = address
    c.font = Font(size=10)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)
    sheet.row_dimensions[6].height = 24

    # Rows 9–10: two-row column headers with group merges
    header_merges = [
        (GROUP_HEADER_ROW, 1,  SUBHEADER_ROW,    1,  "№"),
        (GROUP_HEADER_ROW, 2,  SUBHEADER_ROW,    2,  "Наименование работ"),
        (GROUP_HEADER_ROW, 3,  SUBHEADER_ROW,    3,  "Ед. изм."),
        (GROUP_HEADER_ROW, 4,  SUBHEADER_ROW,    4,  "Кол-во"),
        (GROUP_HEADER_ROW, 5,  GROUP_HEADER_ROW, 6,  "Стоимость материалов,\nмашин и механизмов, руб."),
        (GROUP_HEADER_ROW, 7,  GROUP_HEADER_ROW, 8,  "Стоимость работ, руб."),
        (GROUP_HEADER_ROW, 9,  SUBHEADER_ROW,    9,  "Итого, руб."),
        (GROUP_HEADER_ROW, 10, SUBHEADER_ROW,    10, "Кол-во"),
        (GROUP_HEADER_ROW, 11, GROUP_HEADER_ROW, 12, "Стоимость материалов,\nмашин и механизмов, руб."),
        (GROUP_HEADER_ROW, 13, GROUP_HEADER_ROW, 14, "Стоимость работ, руб."),
        (GROUP_HEADER_ROW, 15, SUBHEADER_ROW,    15, "Итого, руб."),
    ]
    for sr, sc, er, ec, value in header_merges:
        sheet.merge_cells(start_row=sr, start_column=sc, end_row=er, end_column=ec)
        sheet.cell(sr, sc).value = value

    for col, value in {
        5: "За ед", 6: "Итого", 7: "За ед", 8: "Итого",
        11: "За ед", 12: "Итого", 13: "За ед", 14: "Итого",
    }.items():
        sheet.cell(SUBHEADER_ROW, col).value = value

    for row in [GROUP_HEADER_ROW, SUBHEADER_ROW]:
        for col in range(1, 16):
            c = sheet.cell(row, col)
            c.fill = _GREY if col >= 10 else _WHITE
            c.border = _SPLIT if col == 10 else _BORDER
            c.font = Font(bold=True)
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    sheet.row_dimensions[GROUP_HEADER_ROW].height = 46
    sheet.row_dimensions[SUBHEADER_ROW].height = 22

    # Row 11: section row
    for col in range(1, 16):
        c = sheet.cell(SECTION_ROW, col)
        c.fill = _GREY if col >= 10 else _SECTION
        c.border = _SPLIT if col == 10 else _BORDER
        c.font = Font(bold=True)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    sheet.cell(SECTION_ROW, 1).value = section_number if section_number is not None else ""
    c = sheet.cell(SECTION_ROW, 2)
    c.value = section_title
    c.alignment = Alignment(horizontal="left", vertical="center")


# ── Working field: grey background for P:V and W:AA+ ─────────────────────────

def _setup_working_field(sheet: Any, bottom_row: int, right_col: int = 22) -> None:
    for col in range(16, right_col + 1):
        sheet.column_dimensions[get_column_letter(col)].width = 10
    # P:last — grey for all rows (header + data + total)
    for row in range(1, bottom_row + 1):
        for col in range(16, right_col + 1):
            c = sheet.cell(row, col)
            c.fill = _GREY
            c.border = _BORDER
            c.font = Font(size=9)
            c.alignment = Alignment(horizontal="center", vertical="center")
    # J:O — explicitly grey for data + total rows so the whole right field is uniform
    for row in range(FIRST_DATA_ROW, bottom_row + 1):
        for col in range(10, 16):
            c = sheet.cell(row, col)
            c.fill = _GREY
            c.border = _SPLIT if col == 10 else _BORDER
            c.font = Font(size=9)
            c.alignment = Alignment(horizontal="center", vertical="center")


# ── Communications mini-table W:AA+ ──────────────────────────────────────────

def _write_communications_mini_table(
    sheet: Any,
    data: dict[str, Any],
    rows: list[dict[str, Any]],
    warnings: list[str],
) -> int:
    """Write per-pipe length values in W:AA+ for communications rows. Returns last used column index."""
    mini_table = data.get("communications_mini_table")
    if not mini_table:
        return 22

    pipe_count: int = mini_table.get("pipe_count", 0)
    if not pipe_count:
        return 22

    n_cols = pipe_count + 1  # pipes + Итого
    start_col = 23           # W
    end_col = start_col + n_cols - 1
    value_rows: dict[str, Any] = mini_table.get("value_rows", {})

    code_to_row: dict[str, int] = {}
    for idx, row_data in enumerate(rows, start=1):
        row_id = str(row_data.get("row_id", ""))
        code = row_id.split(".")[-1] if "." in row_id else row_id
        code_to_row[code] = FIRST_DATA_ROW + idx - 1

    for code, values in value_rows.items():
        if code not in code_to_row or values is None:
            continue
        sheet_row = code_to_row[code]
        for i, val in enumerate(values):
            col = start_col + i
            if col > end_col:
                break
            c = sheet.cell(sheet_row, col)
            c.fill = _GREY
            c.border = _BORDER
            c.font = Font(size=9)
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.number_format = "0.00"
            if isinstance(val, (int, float)):
                c.value = int(val) if isinstance(val, float) and val == int(val) else val

    return end_col


def _write_trench_routes_mini_table(
    sheet: Any,
    data: dict[str, Any],
    rows: list[dict[str, Any]],
    warnings: list[str],
) -> int:
    """Write trench route headers (excavator row) + volumes (manual_excavation row) in W:AA+."""
    trt = data.get("trench_routes_mini_table")
    if not trt:
        return 22

    route_labels: list[str] = trt.get("route_labels", [])
    route_volumes: list[float] = trt.get("route_volumes", [])
    route_count: int = trt.get("route_count", 0)
    route_total = trt.get("route_total")
    if not route_labels:
        return 22

    n_cols = route_count + 1  # routes + Итого
    start_col = 23            # W
    end_col = start_col + n_cols - 1
    header_row_code = trt.get("header_row", "")
    value_row_code = trt.get("value_row", "")

    code_to_row: dict[str, int] = {}
    for idx, row_data in enumerate(rows, start=1):
        row_id = str(row_data.get("row_id", ""))
        code = row_id.split(".")[-1] if "." in row_id else row_id
        code_to_row[code] = FIRST_DATA_ROW + idx - 1

    def _grey_cell(row: int, col: int, value: Any = None, bold: bool = False) -> None:
        c = sheet.cell(row, col)
        c.fill = _GREY
        c.border = _BORDER
        c.font = Font(size=9, bold=bold)
        c.alignment = Alignment(horizontal="center", vertical="center")
        if value is not None:
            c.value = value

    # Header row: route names + "Итого"
    if header_row_code in code_to_row:
        sheet_row = code_to_row[header_row_code]
        for i, label in enumerate(route_labels + ["Итого"]):
            _grey_cell(sheet_row, start_col + i, value=label, bold=True)

    # Value row: route volumes + total
    if value_row_code in code_to_row:
        sheet_row = code_to_row[value_row_code]
        all_vals = list(route_volumes) + ([route_total] if route_total is not None else [])
        for i, val in enumerate(all_vals):
            col = start_col + i
            if col > end_col:
                break
            c = sheet.cell(sheet_row, col)
            c.fill = _GREY
            c.border = _BORDER
            c.font = Font(size=9)
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.number_format = "0.00"
            if isinstance(val, (int, float)):
                c.value = int(val) if isinstance(val, float) and val == int(val) else val

    return end_col


# ── Estimate rows ─────────────────────────────────────────────────────────────

def _write_estimate_row(
    ws: Any,
    row_data: dict[str, Any],
    row_num: int,
    warnings: list[str],
) -> dict[str, Any]:
    row_id = str(row_data.get("row_id", ""))
    estimate_line = str(row_data.get("estimate_line", ""))
    unit = str(row_data.get("unit", ""))
    calc_zone = row_data.get("calc_zone", {})
    helper_cells = list(row_data.get("helper_zone", {}).get("cells", []))

    helper_id_to_col = _build_helper_id_to_col(helper_cells)
    truncated = False
    if len(helper_cells) > MAX_HELPER_CELLS:
        warnings.append(f"helper cells truncated for {row_id!r} ({len(helper_cells)} > {MAX_HELPER_CELLS})")
        helper_cells = helper_cells[:MAX_HELPER_CELLS]
        truncated = True

    formula_count = 0
    unknown_types: list[str] = []
    qty_formula: str | None = None
    total_formula: str | None = None
    skipped_helpers: list[str] = []

    # Col A: left empty here — merged with section title after all rows are written
    # Col B: row name
    c = ws.cell(row_num, 2)
    c.value = estimate_line
    c.border = _BORDER
    c.font = Font(size=10)
    c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

    # Col C: unit
    c = ws.cell(row_num, 3)
    c.value = unit
    c.border = _BORDER
    c.font = Font(size=10)
    c.alignment = Alignment(horizontal="center", vertical="top")

    # White zone D:I — mirrors of grey zone J:O
    for white_col, calc_col in WHITE_ZONE_MIRROR.items():
        col_idx = column_index_from_string(white_col)
        c = ws.cell(row_num, col_idx)
        c.value = f"={calc_col}{row_num}"
        c.fill = _WHITE
        c.border = _BORDER
        c.font = Font(size=10)
        c.alignment = Alignment(
            horizontal="center" if white_col == "D" else None,
            vertical="top",
        )
        c.number_format = "0.00" if white_col == "D" else "0"
    formula_count += len(WHITE_ZONE_MIRROR)

    # Grey zone J:O — calc zone with real formulas
    for field, col_letter in CALC_ZONE_COL.items():
        col_idx = column_index_from_string(col_letter)
        cz_cell = calc_zone.get(field, {})
        value = cz_cell.get("value")
        formula = _to_excel_formula(cz_cell, row_num, helper_id_to_col)

        if formula is None and cz_cell.get("formula_model") is not None:
            fm = cz_cell.get("formula_model")
            if cz_cell.get("excel_formula_exportable") is not False:
                fm_type = fm.get("type", "unknown") if isinstance(fm, dict) else "unknown"
                unknown_types.append(f"{field}:{fm_type}")
                warnings.append(
                    f"row {row_id!r} calc_zone.{field}: "
                    f"formula type {fm_type!r} untranslatable — using value"
                )

        c = ws.cell(row_num, col_idx)
        c.fill = _GREY
        c.border = _SPLIT if col_letter == "J" else _BORDER
        c.font = Font(size=10)
        c.alignment = Alignment(
            horizontal="center" if col_letter == "J" else None,
            vertical="top",
        )
        c.number_format = "0.00" if col_letter == "J" else "0"

        if formula:
            c.value = formula
            formula_count += 1
            if field == "quantity":
                qty_formula = formula
            if field == "row_total":
                total_formula = formula
        else:
            c.value = value

    # Working field P:V — per-row helper cells
    for hcell in helper_cells:
        target_col = str(hcell.get("target_col_role", ""))
        if target_col not in HELPER_COLS:
            continue
        label = str(hcell.get("label", ""))
        h_value = hcell.get("value")
        h_formula = _to_excel_formula(hcell, row_num, helper_id_to_col)

        col_idx = column_index_from_string(target_col)
        c = ws.cell(row_num, col_idx)
        c.fill = _GREY
        c.border = _BORDER
        c.font = Font(size=9)
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.number_format = "0.00"

        if h_formula:
            c.value = h_formula
            formula_count += 1
        elif isinstance(h_value, (int, float)):
            display_num = int(h_value) if isinstance(h_value, float) and h_value == int(h_value) else h_value
            c.value = display_num
        else:
            # Non-numeric, non-formula: service metadata — skip from Excel, log for report
            skipped_helpers.append(f"{target_col}{row_num} label={label!r} value={h_value!r}")
            continue

    ws.row_dimensions[row_num].height = 18

    status = "formula_ready"
    if unknown_types:
        status = "partially_formula_ready"
    if truncated:
        status = f"{status}|helper_truncated"

    return {
        "row_id": row_id,
        "estimate_line": estimate_line,
        "row_number": row_num,
        "quantity_formula": qty_formula or "(value)",
        "total_formula": total_formula or "(value)",
        "helper_cells": len(helper_cells),
        "status": status,
        "formula_count": formula_count,
        "skipped_helpers": skipped_helpers,
    }


# ── Total row ─────────────────────────────────────────────────────────────────

def _write_total_row(
    sheet: Any,
    total_row: int,
    first_data_row: int,
    last_data_row: int,
    right_col: int = 22,
) -> None:
    total_values = {
        2:  "Итого по разделу:",
        6:  f"=L{total_row}",
        8:  f"=N{total_row}",
        9:  f"=O{total_row}",
        12: f"=SUM(L{first_data_row}:L{last_data_row})",
        14: f"=SUM(N{first_data_row}:N{last_data_row})",
        15: f"=SUM(O{first_data_row}:O{last_data_row})",
    }
    for col in range(1, 16):
        c = sheet.cell(total_row, col)
        c.value = total_values.get(col, "")
        c.font = Font(bold=True)
        c.fill = _GREY if col >= 10 else _TOTAL
        c.border = _SPLIT if col == 10 else _BORDER
        c.number_format = "0"

    for col in range(16, right_col + 1):
        c = sheet.cell(total_row, col)
        c.fill = _GREY
        c.border = _BORDER

    sheet.row_dimensions[total_row].height = 22


# ── Column widths + freeze ────────────────────────────────────────────────────

def _setup_dimensions(sheet: Any, right_col: int = 22) -> None:
    widths = {
        1: 6, 2: 58, 3: 10, 4: 12,
        5: 16, 6: 16, 7: 14, 8: 14, 9: 14,
        10: 12, 11: 16, 12: 16, 13: 14, 14: 14, 15: 14,
    }
    for col_num, width in widths.items():
        sheet.column_dimensions[get_column_letter(col_num)].width = width
    sheet.freeze_panes = "E12"


# ── Workbook ──────────────────────────────────────────────────────────────────

def build_workbook(
    data: dict[str, Any],
    logo_path: Path,
    address: str,
    section_number: str | int | None,
    sheet_title: str = SHEET_NAME,
) -> tuple[Workbook, list[dict[str, Any]], list[str], int]:
    wb = Workbook()
    ws = wb.active
    section_title = data.get("section_title", SHEET_NAME)
    ws.title = sheet_title  # Tab name = estimate date

    if section_number is None:
        section_number = data.get("section_number") or data.get("section_index") or None

    rows = data.get("rows", [])
    warnings: list[str] = []

    # Determine total column extent: max of pipe count and trench route count
    mini_table = data.get("communications_mini_table")
    mini_pipe_count = (mini_table or {}).get("pipe_count", 0)
    trt = data.get("trench_routes_mini_table")
    trt_route_count = (trt or {}).get("route_count", 0)
    max_extra_cols = max(mini_pipe_count, trt_route_count)
    right_col = 22 + (max_extra_cols + 1) if max_extra_cols else 22

    _setup_top_header(ws, logo_path, address, section_number, section_title, right_col=right_col)

    last_data_row = FIRST_DATA_ROW + len(rows) - 1
    total_row = last_data_row + 1

    # Grey background for P:V + W:AA+ (covers header + data + total + padding)
    _setup_working_field(ws, total_row + 2, right_col=right_col)

    # Data rows
    row_stats: list[dict[str, Any]] = []
    total_formula_count = 0
    for idx, row_data in enumerate(rows, start=1):
        row_num = FIRST_DATA_ROW + idx - 1
        stats = _write_estimate_row(ws, row_data, row_num, warnings)
        row_stats.append(stats)
        total_formula_count += stats["formula_count"]

    # W:AA+ zone: trench routes (rows excavator+manual) and pipe breakdown (row comms_work)
    _write_trench_routes_mini_table(ws, data, rows, warnings)
    _write_communications_mini_table(ws, data, rows, warnings)

    # Col A: merge across all data rows, section title rotated 90°
    if rows:
        ws.merge_cells(
            start_row=FIRST_DATA_ROW, start_column=1,
            end_row=last_data_row, end_column=1,
        )
        sec_cell = ws.cell(FIRST_DATA_ROW, 1)
        sec_cell.value = section_title
        sec_cell.font = Font(bold=True)
        sec_cell.fill = _WHITE
        sec_cell.alignment = Alignment(
            horizontal="center", vertical="center",
            text_rotation=90, wrap_text=True,
        )
        sec_cell.border = _BORDER
        for row_num in range(FIRST_DATA_ROW + 1, last_data_row + 1):
            ws.cell(row_num, 1).border = _BORDER
            ws.cell(row_num, 1).fill = _WHITE

    _write_total_row(ws, total_row, FIRST_DATA_ROW, last_data_row, right_col=right_col)
    _setup_dimensions(ws, right_col=right_col)

    return wb, row_stats, warnings, total_formula_count


# ── Report ────────────────────────────────────────────────────────────────────

def build_report(
    out_path: Path,
    formula_ready_path: Path,
    row_stats: list[dict[str, Any]],
    warnings: list[str],
    total_formula_count: int,
    section_title: str,
    helper_data_audit: dict[str, Any] | None = None,
    sheet_title: str | None = None,
) -> str:
    rows_exported = len(row_stats)
    verdict = "yes" if rows_exported > 0 else "no"
    partial = [r for r in row_stats if "partially" in r["status"]]
    unknown_rows = "; ".join(r["row_id"] for r in partial) if partial else "none"
    table_rows = "\n".join(
        f"| {r['row_id']} | {r['estimate_line'][:40]} | {r['row_number']} "
        f"| {r['quantity_formula']} | {r['total_formula']} "
        f"| {r['helper_cells']} | {r['status']} |"
        for r in row_stats
    )
    warnings_block = "\n".join(f"- {w}" for w in warnings) if warnings else "- none"

    all_skipped = []
    for r in row_stats:
        for s in r.get("skipped_helpers", []):
            all_skipped.append(f"- {r['row_id']}: {s}")
    skipped_block = "\n".join(all_skipped) if all_skipped else "- none"

    audit_block = ""
    if helper_data_audit:
        audit_lines = ["## Helper data audit", ""]
        for key, val in helper_data_audit.items():
            audit_lines.append(f"- {key}: {val if val is not None else 'missing'}")
        audit_block = "\n".join(audit_lines) + "\n\n"

    return f"""# Excel formula export report

## Verdict
- excel_created: {verdict}
- rows_exported: {rows_exported}
- formulas_created: {total_formula_count}
- warnings: {len(warnings)}

## Workbook
- path: {out_path}
- sheet: {sheet_title or section_title}
- section: {section_title}

## Source
- formula_ready: {formula_ready_path}

## Layout
- white_zone: A:I
- calc_zone: J:O (grey B7B7B7, blue split border at J)
- helper_zone: P:V (numeric operands for row formula verification)
- mini_tables: W:AA+ (trench routes rows 13-14; pipe breakdown row 20)

## Formula checks
- white_zone_mirrors_calc_zone: yes
- calc_zone_has_formulas: yes
- helper_zone_has_row_level_fields: yes
- unknown_formula_types: {unknown_rows}

{audit_block}## Rows summary

| row_id | estimate_line | row_number | quantity_formula | total_formula | helper_cells | status |
|---|---|---:|---|---|---:|---|
{table_rows}

## Warnings
{warnings_block}

## Skipped helper cells (service metadata — not shown in Excel)
{skipped_block}
"""


# ── CLI ───────────────────────────────────────────────────────────────────────

def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export formula_ready_result.json to earthworks Excel workbook"
    )
    parser.add_argument("--formula-ready", required=True,
                        help="Path to formula_ready_result.json")
    parser.add_argument("--out", required=True,
                        help="Output .xlsx path")
    parser.add_argument("--report", required=True,
                        help="Output report .md path")
    parser.add_argument("--logo-path", default=None,
                        help="Path to brick_house_logo.png (default: assets/brick_house_logo.png)")
    parser.add_argument("--project-address", default=None,
                        help="Project address for row 6 (override; normally comes from formula_ready_result.json)")
    parser.add_argument("--section-number", default=None,
                        help="Section number for section row (default: 2 for earthworks).")
    parser.add_argument("--estimate-date", default=None,
                        help="Estimate date in DD.MM.YYYY format (Excel tab name). Default: today.")
    args = parser.parse_args(argv)

    formula_ready_path = Path(args.formula_ready).resolve()
    out_path = Path(args.out).resolve()
    report_path = Path(args.report).resolve()
    logo_path = Path(args.logo_path).resolve() if args.logo_path else DEFAULT_LOGO_PATH

    if not formula_ready_path.exists():
        print(
            f"error: formula_ready_result.json not found: {formula_ready_path}\n"
            "Run the full review flow first.",
            file=sys.stderr,
        )
        return 1

    data = load_json(formula_ready_path)

    if not data.get("excel_export_ready"):
        print(
            "error: formula_ready_result.json is not marked excel_export_ready=true",
            file=sys.stderr,
        )
        return 1

    # Resolve address: JSON > CLI > fallback
    address = (
        (data.get("meta") or {}).get("project_address")
        or (data.get("project_meta") or {}).get("project_address")
        or args.project_address
    )
    address_missing = not address
    if address_missing:
        address = "Адрес объекта: —"

    # Resolve section number: default 2 for earthworks
    section_number: str | int | None = args.section_number if args.section_number is not None else 2

    # Resolve sheet title (Excel tab name) = estimate date DD.MM.YYYY
    estimate_date = (
        (data.get("meta") or {}).get("estimate_date")
        or (data.get("project_meta") or {}).get("estimate_date")
        or args.estimate_date
    )
    sheet_title = str(estimate_date) if estimate_date else datetime.date.today().strftime("%d.%m.%Y")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        wb, row_stats, warnings, total_formula_count = build_workbook(
            data, logo_path, address, section_number, sheet_title=sheet_title
        )
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if address_missing:
        warnings.append("project address missing in formula_ready_result — showing fallback")

    wb.save(str(out_path))

    section_title = data.get("section_title", SHEET_NAME)
    report_text = build_report(
        out_path=out_path,
        formula_ready_path=formula_ready_path,
        row_stats=row_stats,
        warnings=warnings,
        total_formula_count=total_formula_count,
        section_title=section_title,
        helper_data_audit=data.get("helper_data_audit"),
        sheet_title=sheet_title,
    )
    report_path.write_text(report_text, encoding="utf-8")

    print(f"excel: {out_path}")
    print(f"report: {report_path}")
    print(f"rows_exported: {len(row_stats)}")
    print(f"formulas_created: {total_formula_count}")
    print(f"warnings: {len(warnings)}")
    if warnings:
        for w in warnings:
            print(f"  warning: {w}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
