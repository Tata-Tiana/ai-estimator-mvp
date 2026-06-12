from __future__ import annotations

import re
from typing import Any


NUMBER_RE = r"\d+(?:[ \u00a0]\d{3})+|\d+(?:[,.]\d+)?"
UNIT_RE = r"м3|м2|м/п|м\.п\.|п\.м\.|шт|кг|т|м"


def parse_number(text: str) -> float:
    return float(text.replace("\u00a0", " ").replace(" ", "").replace(",", "."))


def normalize_unit(unit: str) -> str:
    unit = unit.lower().replace(".", "")
    if unit in {"мп", "пм"}:
        return "м/п"
    return unit


def numbers_before_unit(text: str, unit: str) -> list[float]:
    unit_pattern = re.escape(unit).replace("/", r"\/")
    result = []
    for match in re.finditer(rf"(?P<prefix>.{{0,100}}?)(?P<value>{NUMBER_RE})\s*{unit_pattern}", text, re.IGNORECASE):
        result.append(parse_number(match.group("value")))
    return result


def last_number_before_unit_after_keyword(text: str, keyword: str, unit: str) -> tuple[float | None, str]:
    low = text.lower().replace("ё", "е")
    index = low.find(keyword.lower().replace("ё", "е"))
    if index < 0:
        return None, ""
    fragment = text[index:]
    values = numbers_before_unit(fragment, unit)
    if not values:
        return None, fragment[:240]
    return values[-1], fragment[:240]


def row_text(row: list[str]) -> str:
    return " ".join(cell for cell in row if cell).strip()


def table_row_objects(tables: list[dict[str, Any]], logical_pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    page_index = {(p["source_pdf"], p["physical_page_number"]): p for p in logical_pages}
    rows = []
    for table in tables:
        page = page_index.get((table["source_pdf"], table["physical_page_number"]), {})
        for row_index, row in enumerate(table.get("rows") or [], start=1):
            text = row_text(row)
            if not text:
                continue
            rows.append(
                {
                    "source_pdf": table["source_pdf"],
                    "physical_page_number": table["physical_page_number"],
                    "table_index": table["table_index"],
                    "row_index": row_index,
                    "row": row,
                    "row_text": text,
                    "logical_sheet_title": page.get("logical_sheet_title", ""),
                    "logical_sheet_type": page.get("logical_sheet_type", "unknown"),
                    "section_code": page.get("section_code", ""),
                    "drawing_sheet_number": page.get("drawing_sheet_number", ""),
                }
            )
    return rows
