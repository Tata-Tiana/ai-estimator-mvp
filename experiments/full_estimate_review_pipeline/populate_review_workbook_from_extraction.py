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
import sys
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_review_workbook_from_contracts import (  # noqa: E402
    FILL_HEADER,
    FILL_INPUT,
    FONT_NAME,
    PROJECT_HEADERS,
    apply_table_style,
    append_block,
    append_section_band,
    build_constructor_sheet,
    build_contracts_summary_sheet,
    build_details_sheet,
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
)

ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DIR = Path(__file__).resolve().parent


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


def build_project_sheet_from_extraction(
    wb: Workbook, contracts: list[dict[str, Any]], extraction: dict[str, Any]
) -> dict[str, int]:
    ws = wb.create_sheet("01_Проверка проекта")
    project_title = "Разбор проекта:\n" + " + ".join(section_name(c) for c in contracts)
    ws.append([project_title, "", "", "", "", "", "", "", "", "", "", "", ""])
    ws.append([])
    ws.append([])
    ws.append(PROJECT_HEADERS)

    counts = {"found": 0, "needs_review": 0, "missing": 0, "item_rows": 0}

    for contract in contracts:
        sec_code = section_code(contract)
        found_by_target, found_groups, missing = index_extraction_section(extraction, sec_code)
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
            ws.append([
                param.get("label_ru", param.get("key", "")),
                found_value,
                param.get("unit", ""),
                status,
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
        "A": 30, "B": 26, "C": 10, "D": 20, "E": 62, "F": 30, "G": 64,
        "H": 28, "I": 28, "J": 20, "K": 28, "L": 18, "M": 24,
        "N": 24, "O": 24, "P": 24, "Q": 24,
    }
    for col, width in set_widths.items():
        ws.column_dimensions[col].width = width
    for column in ["J", "K", "L", "M", "R"]:
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
    build_details_sheet(wb, contracts)
    build_instruction_sheet(wb)
    build_contracts_summary_sheet(wb, contracts)
    build_raw_contracts_sheet(wb, contracts)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    return {"output_path": str(output_path), **counts}


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
