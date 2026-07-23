"""Validate step1 raw project-table JSON for the 4-step chat extraction test.

Step 1 is not the final estimate extraction. It is a raw transcription layer:
PDF -> page_map + raw_table_rows. This validator checks only mechanical
structure and source traceability. It does not map target_code and does not
judge estimate correctness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def as_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def validate(data: dict[str, Any]) -> tuple[list[str], dict[str, int]]:
    warnings: list[str] = []
    page_map = data.get("page_map")
    raw_rows = data.get("raw_table_rows")
    extraction_warnings = data.get("extraction_warnings") or []

    stats = {
        "page_map_items": 0,
        "raw_table_rows": 0,
        "rows_with_legend_ref": 0,
        "extraction_warnings": len(extraction_warnings),
    }

    if not isinstance(page_map, list) or not page_map:
        warnings.append("top-level page_map is missing or empty")
        page_map = []
    if not isinstance(raw_rows, list):
        warnings.append("top-level raw_table_rows is missing or not a list")
        raw_rows = []

    stats["page_map_items"] = len(page_map)
    stats["raw_table_rows"] = len(raw_rows)

    pages_seen: set[int] = set()
    sheet_numbers: list[int] = []
    sheets_total_values: set[int] = set()

    for i, page in enumerate(page_map):
        if not isinstance(page, dict):
            warnings.append(f"page_map[{i}] is not an object")
            continue
        page_number = as_int(page.get("page_number"))
        sheet_number = as_int(page.get("sheet_number"))
        sheets_total = as_int(page.get("sheets_total"))
        if page_number is None:
            warnings.append(f"page_map[{i}]: missing/invalid page_number")
        else:
            pages_seen.add(page_number)
        if sheet_number is not None:
            sheet_numbers.append(sheet_number)
        if sheets_total is not None:
            sheets_total_values.add(sheets_total)
        if not page.get("page_title") and not page.get("title_block_raw_text"):
            warnings.append(f"page_map[{i}]: no page_title/title_block_raw_text")

    if len(sheets_total_values) > 1:
        warnings.append(f"page_map: multiple sheets_total values found: {sorted(sheets_total_values)}")
    if sheets_total_values:
        sheets_total = next(iter(sheets_total_values))
        if len(page_map) != sheets_total:
            warnings.append(f"page_map: len(page_map)={len(page_map)} but sheets_total={sheets_total}")
    for page in page_map:
        page_number = as_int(page.get("page_number"))
        sheet_number = as_int(page.get("sheet_number"))
        if page_number is not None and sheet_number is not None and page_number != sheet_number:
            warnings.append(
                f"page_map: PDF page_number={page_number} differs from sheet_number={sheet_number}; "
                "check references in notes"
            )

    row_ids: set[str] = set()
    for i, row in enumerate(raw_rows):
        if not isinstance(row, dict):
            warnings.append(f"raw_table_rows[{i}] is not an object")
            continue
        path = f"raw_table_rows[{i}]"
        row_id = row.get("row_id")
        if not row_id:
            warnings.append(f"{path}: missing row_id")
        elif row_id in row_ids:
            warnings.append(f"{path}: duplicate row_id {row_id!r}")
        else:
            row_ids.add(str(row_id))

        page_number = as_int(row.get("page_number"))
        if not row.get("source_pdf") or page_number is None:
            warnings.append(f"{path}: missing source_pdf/page_number")
        elif pages_seen and page_number not in pages_seen:
            warnings.append(f"{path}: page_number={page_number} is absent from page_map")

        if not row.get("raw_text") and not row.get("cells"):
            warnings.append(f"{path}: missing raw_text/cells")
        if not row.get("columns"):
            warnings.append(f"{path}: missing columns")

        raw_text = str(row.get("raw_text") or "").lower()
        cells_text = " ".join(str(cell) for cell in (row.get("cells") or [])).lower()
        has_graphic_marker = any(token in raw_text or token in cells_text for token in ("<", "штрих", "заливк", "маркер"))
        legend_ref = row.get("legend_ref")
        if legend_ref:
            stats["rows_with_legend_ref"] += 1
            if not isinstance(legend_ref, dict):
                warnings.append(f"{path}: legend_ref is not an object")
            elif not (legend_ref.get("legend_text") or legend_ref.get("marker_raw")):
                warnings.append(f"{path}: legend_ref has no legend_text/marker_raw")
        elif has_graphic_marker:
            warnings.append(f"{path}: graphic marker-like text found, but legend_ref is missing")

    return warnings, stats


def render_report(warnings: list[str], stats: dict[str, int]) -> str:
    lines = [
        "# Step 1 Raw Tables Validation Report",
        "",
        (
            f"Page map items: {stats['page_map_items']}. Raw table rows: {stats['raw_table_rows']}. "
            f"Rows with legend_ref: {stats['rows_with_legend_ref']}. "
            f"Extraction warnings: {stats['extraction_warnings']}."
        ),
        "",
        f"## Warnings ({len(warnings)})",
        "",
    ]
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("(none)")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    data = load_json(args.input)
    if not isinstance(data, dict):
        raise TypeError("Step1 JSON must be a top-level object")

    warnings, stats = validate(data)
    report = render_report(warnings, stats)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print(f"validated step1: {stats}, {len(warnings)} warnings -> {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
