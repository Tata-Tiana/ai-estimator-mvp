"""Builds the review workbook the same way build_review_workbook_from_contracts.py
does, but fills sheet 01 with real values from a chat-extraction extraction_output.json
instead of leaving it blank. This is the missing "step 2" from ADAPTER_BUILD_PLAN.md's
"Полный путь PDF -> смета" section - the first real test of it against a real JSON.

Only sheet 01 is filled here. Sheet 02 (prices) still needs the separate
price_registry-based fill (not in scope for this pass). Sheets 03-06 are unchanged,
built the same way as the empty-template script.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_review_workbook_from_contracts import (  # noqa: E402
    FILL_HEADER,
    FILL_INPUT,
    FILL_WHITE,
    FONT_NAME,
    PROJECT_HEADERS,
    apply_table_style,
    append_block,
    append_section_band,
    build_constructor_sheet,
    build_contracts_summary_sheet,
    build_instruction_sheet,
    build_prices_sheet,
    build_raw_contracts_sheet,
    correction_headers,
    default_contract_paths,
    load_yaml_contract,
    production_repeated_row_params,
    restyle_block_sheet,
    restyle_section_bands,
    scalar_review_rows_for_contract,
    section_code,
    section_name,
    set_widths,
    style_block_title_row,
    style_header_row,
)

ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DIR = Path(__file__).resolve().parent


# Narrow, purpose-built support for the "sum(included <group>.<field>)" auto_calculated formula
# shape only — not a general expression evaluator. Most auto_calculated entries in
# section_contract.yaml are internal computation notes never meant to reach sheet 01 (see plan
# section 34); only entries a review_parameters row explicitly opts into via cross_check_key get
# rendered, and only this one formula shape is understood. If a future cross-check needs a
# different formula shape, extend this function narrowly rather than building a generic parser.
_SUM_INCLUDED_RE = re.compile(r"^sum\(included (\w+)\.(\w+)\)$")


def compute_cross_check_value(formula: str, found_groups: dict[str, list[Any]]) -> float | None:
    match = _SUM_INCLUDED_RE.match(formula.strip())
    if not match:
        return None
    group_key, field = match.groups()
    rows = found_groups.get(group_key) or []
    total = 0.0
    found_any = False
    for item in rows:
        value = item.get("value") or {}
        include = value.get("include_in_communications", value.get("include", True))
        if not include:
            continue
        explicit_total = value.get(field)
        if explicit_total is not None:
            total += float(explicit_total)
            found_any = True
            continue
        # Mirror earthworks_calculator.py's own pipe_items fallback: pipe_length_m * quantity when
        # no explicit total_length_m is given on the row (e.g. straight pipe segments). Rows with
        # no length component at all (elbows, tees, plugs) contribute 0, not an error.
        pipe_length = value.get("pipe_length_m")
        quantity = value.get("quantity")
        if pipe_length is not None and quantity is not None:
            total += float(pipe_length) * float(quantity)
            found_any = True
    return total if found_any else None


def auto_calculated_by_key(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["key"]: entry for entry in (contract.get("auto_calculated") or []) if entry.get("key")}


def index_extraction_section(extraction: dict[str, Any], sec_code: str) -> tuple[dict, dict, set]:
    section = (extraction.get("sections") or {}).get(sec_code) or {}
    found_by_target: dict[str, Any] = {}
    found_groups: dict[str, list[Any]] = {}
    for item in section.get("found") or []:
        group_code = item.get("group_code")
        if group_code:
            found_groups.setdefault(group_code, []).append(item)
        else:
            target_code = item.get("target_code")
            if target_code:
                found_by_target[target_code] = item
    missing = set(section.get("missing") or [])
    return found_by_target, found_groups, missing


def display_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


DETAIL_RAW_HEADERS = [
    "№",
    "Исходные колонки PDF",
    "Исходные ячейки PDF",
    "Сырая строка PDF",
    "Ед.",
    "Норм. ед.",
    "Target codes",
    "Needs review",
    "Комментарий parser",
    "Комментарий Елены",
    "section_code",
    "source_pdf",
    "page_number",
    "page_title",
    "table_id",
    "row_index",
    "mapped_target_codes_json",
]


def joined(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " | ".join("" if item is None else str(item) for item in value)
    return str(value)


def table_title(row: dict[str, Any]) -> str:
    title = row.get("table_title")
    if title:
        return str(title)
    page_title = row.get("page_title") or "Лист без названия"
    table_id = row.get("table_id") or "unknown_table"
    return f"{page_title} — таблица {table_id}"


def table_group_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("section_code") or "",
        row.get("source_pdf") or "",
        row.get("page_number") or "",
        row.get("page_title") or "",
        row.get("table_id") or "",
        row.get("table_title") or "",
    )


def iter_raw_table_groups(extraction: dict[str, Any]) -> list[tuple[tuple[Any, ...], list[dict[str, Any]]]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for section in (extraction.get("sections") or {}).values():
        for row in section.get("raw_table_rows") or []:
            if not isinstance(row, dict):
                continue
            groups.setdefault(table_group_key(row), []).append(row)
    return list(groups.items())


def build_details_sheet_from_extraction(wb: Workbook, extraction: dict[str, Any]) -> dict[str, int]:
    ws = wb.create_sheet("03_Детали объемов")
    groups = iter_raw_table_groups(extraction)
    max_col = len(DETAIL_RAW_HEADERS)

    for _group_key, rows in groups:
        first = rows[0]
        title = table_title(first)
        context = (
            f"Раздел: {first.get('section_code') or ''} | "
            f"PDF: {first.get('source_pdf') or ''} | "
            f"стр. {first.get('page_number') or ''} | "
            f"Лист: {first.get('page_title') or ''}"
        )

        if ws.max_row == 1 and not ws.cell(1, 1).value:
            ws.cell(1, 1).value = title
        else:
            ws.append([])
            ws.append([title])
        style_block_title_row(ws, ws.max_row, max_col)
        ws.append([context])
        for cell in ws[ws.max_row]:
            cell.fill = FILL_WHITE
            cell.font = Font(name=FONT_NAME, size=10, italic=True)
            cell.alignment = Alignment(wrap_text=True, vertical="top")

        ws.append(DETAIL_RAW_HEADERS)
        style_header_row(ws, ws.max_row, max_col)

        for row in rows:
            mapped = row.get("mapped_target_codes") or []
            ws.append([
                row.get("row_index"),
                joined(row.get("columns")),
                joined(row.get("cells")),
                row.get("raw_text") or "",
                row.get("unit") or "",
                row.get("normalized_unit") or "",
                joined(mapped),
                "да" if row.get("needs_review") else "нет",
                row.get("notes") or "",
                "",
                row.get("section_code") or "",
                row.get("source_pdf") or "",
                row.get("page_number") or "",
                row.get("page_title") or "",
                row.get("table_id") or "",
                row.get("row_index") or "",
                json.dumps(mapped, ensure_ascii=False),
            ])
            for cell in ws[ws.max_row]:
                cell.font = Font(name=FONT_NAME, size=11)
                cell.alignment = Alignment(wrap_text=True, vertical="top")

    if not groups:
        ws.append(["Сырые таблицы parser не найдены в extraction JSON."])
        style_block_title_row(ws, 1, 1)

    set_widths(ws, {
        "A": 8,
        "B": 44,
        "C": 58,
        "D": 72,
        "E": 12,
        "F": 12,
        "G": 32,
        "H": 14,
        "I": 52,
        "J": 30,
        "K": 20,
        "L": 34,
        "M": 10,
        "N": 34,
        "O": 28,
        "P": 12,
        "Q": 32,
    })
    for column in ["K", "L", "M", "N", "O", "P", "Q"]:
        ws.column_dimensions[column].hidden = True
    ws.freeze_panes = "A1"

    return {"detail_table_blocks": len(groups), "raw_detail_rows": sum(len(rows) for _, rows in groups)}


def build_project_sheet_from_extraction(
    wb: Workbook, contracts: list[dict[str, Any]], extraction: dict[str, Any]
) -> dict[str, int]:
    ws = wb.create_sheet("01_Проверка проекта")
    project_title = "Разбор проекта:\n" + " + ".join(section_name(c) for c in contracts)
    ws.append([project_title, "", "", "", "", "", "", "", "", "", "", "", "", ""])
    ws.append([])
    ws.append([])
    ws.append(PROJECT_HEADERS)

    counts = {"found": 0, "needs_review": 0, "missing": 0, "item_rows": 0}

    for contract in contracts:
        sec_code = section_code(contract)
        found_by_target, found_groups, missing = index_extraction_section(extraction, sec_code)
        auto_calculated = auto_calculated_by_key(contract)
        append_section_band(ws, [section_name(contract)], len(PROJECT_HEADERS))

        for param in scalar_review_rows_for_contract(contract):
            review_behavior = param.get("review_behavior") or {}
            target_code = param.get("target_code", "")
            found = found_by_target.get(target_code)
            if found is not None:
                found_value = display_value(found.get("value"))
                needs_review = bool(found.get("needs_review"))
                status = "Проверьте (needs_review)" if needs_review else "Найдено"
                source = found.get("source_pdf") or ""
                fragment = found.get("raw_text") or found.get("notes") or ""
                counts["needs_review" if needs_review else "found"] += 1
            elif target_code and target_code in missing:
                found_value = None
                status = "Не найдено"
                source = ""
                fragment = ""
                counts["missing"] += 1
            else:
                found_value = None
                status = "Проверьте"
                source = ""
                fragment = ""

            cross_check_display = ""
            cross_check_key = param.get("cross_check_key")
            if cross_check_key:
                cc_entry = auto_calculated.get(cross_check_key)
                if cc_entry:
                    cc_value = compute_cross_check_value(cc_entry.get("formula", ""), found_groups)
                    if cc_value is not None:
                        cross_check_display = f"{cc_value:g} — {cc_entry.get('label_ru', cross_check_key)}"

            ws.append([
                param.get("label_ru", param.get("key", "")),
                found_value,
                param.get("unit", ""),
                status,
                cross_check_display,
                review_behavior.get("action_ru", "Проверьте значение."),
                source,
                fragment,
                "",
                "",
                sec_code,
                param.get("key", ""),
                param.get("source_class", ""),
                target_code,
            ])
            for cell in ws[ws.max_row]:
                cell.fill = FILL_INPUT

        for param in production_repeated_row_params(contract):
            review_behavior = param.get("review_behavior") or {}
            action_ru = review_behavior.get("action_ru", "Проверьте позиции построчно.")
            group_key = param.get("key")
            title = f"{section_name(contract)} — {param.get('label_ru', group_key)} ({action_ru})"
            headers = PROJECT_HEADERS + correction_headers(param) + ["row_data_json"]

            item_label_columns = param.get("item_label_columns") or []
            correction_columns = param.get("correction_columns") or []
            columns_by_key = {c["key"]: c for c in (param.get("columns") or [])}

            rows: list[list[Any]] = []
            for item in found_groups.get(group_key, []):
                value = item.get("value") or {}
                needs_review = bool(item.get("needs_review"))

                label_parts = [str(value[k]) for k in item_label_columns if value.get(k) not in (None, "")]
                label = " ".join(label_parts) or item.get("item_name") or group_key

                summary_parts = []
                for key in correction_columns:
                    v = value.get(key)
                    if v is None:
                        continue
                    unit = columns_by_key.get(key, {}).get("unit", "")
                    summary_parts.append(f"{v}{' ' + unit if unit else ''}")
                summary = ", ".join(summary_parts)

                status = "Проверьте (needs_review)" if needs_review else "Найдено"
                counts["needs_review" if needs_review else "found"] += 1
                counts["item_rows"] += 1

                row = [
                    label,
                    summary,
                    param.get("unit", ""),
                    status,
                    "",
                    action_ru,
                    item.get("source_pdf") or "",
                    item.get("raw_text") or item.get("notes") or "",
                    "",
                    "",
                    sec_code,
                    group_key,
                    param.get("source_class", ""),
                    param.get("target_code", ""),
                ]
                row += ["", "", "", ""]  # correction columns - Elena fills these, not the extraction
                row.append(json.dumps(value, ensure_ascii=False))
                rows.append(row)

            append_block(ws, title, headers, rows)

    ws.cell(1, 1).font = Font(name=FONT_NAME, bold=True, size=13)
    ws.cell(1, 1).fill = FILL_HEADER
    apply_table_style(ws, header_row=4)
    restyle_section_bands(ws)
    restyle_block_sheet(ws)
    ws.freeze_panes = "A5"
    set_widths = {
        "A": 30, "B": 26, "C": 10, "D": 20, "E": 20, "F": 62, "G": 30, "H": 64,
        "I": 28, "J": 28, "K": 20, "L": 28, "M": 18, "N": 24,
        "O": 24, "P": 24, "Q": 24,
    }
    for col, width in set_widths.items():
        ws.column_dimensions[col].width = width
    for column in ["K", "L", "M", "N", "S"]:
        ws.column_dimensions[column].hidden = True

    return counts


def build_workbook_from_extraction(
    contract_paths: list[Path], extraction_path: Path, output_path: Path
) -> dict[str, Any]:
    contracts = [load_yaml_contract(path) for path in contract_paths]
    extraction = json.loads(extraction_path.read_text(encoding="utf-8"))

    wb = Workbook()
    build_constructor_sheet(wb, contracts)
    counts = build_project_sheet_from_extraction(wb, contracts, extraction)
    build_prices_sheet(wb, contracts)
    detail_counts = build_details_sheet_from_extraction(wb, extraction)
    build_instruction_sheet(wb)
    build_contracts_summary_sheet(wb, contracts)
    build_raw_contracts_sheet(wb, contracts)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    return {"output_path": str(output_path), **counts, **detail_counts}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("extraction_json", help="Path to a real extraction_output.json")
    parser.add_argument(
        "--output",
        default=str(PIPELINE_DIR / "output" / "step_20_populated_from_real_extraction.xlsx"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_workbook_from_extraction(
        default_contract_paths(), Path(args.extraction_json), Path(args.output)
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
