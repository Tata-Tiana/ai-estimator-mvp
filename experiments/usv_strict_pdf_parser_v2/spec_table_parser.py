from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
EXTRACTED_DIR = DATA_DIR / "extracted"
TABLE_ROWS_PATH = RAW_DIR / "table_rows.json"
PAGES_TEXT_PATH = RAW_DIR / "pages_text.json"
SPEC_ROWS_PATH = EXTRACTED_DIR / "spec_rows.json"

NUMBER_RE = r"\d+(?:[ \u00a0]\d{3})+|\d+(?:[,.]\d+)?"
UNIT_RE = r"м3|м2|м/п|м\.п\.|п\.м\.|шт|кг|т|м"
QUANTITY_RE = re.compile(rf"(?P<value>{NUMBER_RE})\s*(?P<unit>{UNIT_RE})", re.IGNORECASE)
REBAR_RE = re.compile(rf"(ф|ø|d)\s*(?P<diameter>\d{{1,2}})\s*(?P<steel>A\d{{3}}\w*)?.{{0,80}}?(?P<value>{NUMBER_RE})\s*(?P<unit>{UNIT_RE})", re.IGNORECASE)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_number(value: str) -> float:
    cleaned = value.replace("\u00a0", " ").replace(" ", "").replace(",", ".")
    return float(cleaned)


def normalize_unit(unit: str) -> str:
    unit = unit.lower().replace(".", "")
    if unit in {"мп", "пм"}:
        return "м/п"
    return unit


def has_spec_markers(text: str) -> bool:
    low = text.lower()
    markers = ("поз", "обознач", "наименование", "кол-во", "масса", "примеч")
    return sum(marker in low for marker in markers) >= 2


def parse_quantity_from_text(text: str) -> tuple[float | None, str]:
    matches = list(QUANTITY_RE.finditer(text))
    if not matches:
        return None, ""
    match = matches[-1]
    return parse_number(match.group("value")), normalize_unit(match.group("unit"))


def parse_quantity_from_cells(row: list[str]) -> tuple[float | None, str]:
    for index, cell in enumerate(row):
        unit_match = re.fullmatch(rf"\s*(?P<unit>{UNIT_RE})\s*", cell, flags=re.IGNORECASE)
        if not unit_match:
            continue
        for previous in reversed(row[:index]):
            previous = previous.strip()
            if re.fullmatch(NUMBER_RE, previous):
                return parse_number(previous), normalize_unit(unit_match.group("unit"))
            for line in previous.splitlines():
                line = line.strip()
                if re.fullmatch(NUMBER_RE, line):
                    return parse_number(line), normalize_unit(unit_match.group("unit"))
    return None, ""


def spec_row_from_table_row(row_obj: dict[str, Any]) -> dict[str, Any] | None:
    row = row_obj.get("row") or []
    row_text = row_obj.get("row_text", "")
    if not row_text or has_spec_markers(row_text):
        return None
    if not re.search(UNIT_RE, row_text, flags=re.IGNORECASE):
        return None
    quantity, unit = parse_quantity_from_cells(row)
    if quantity is None:
        quantity, unit = parse_quantity_from_text(row_text)
    if quantity is None:
        return None
    name_cells = [cell for cell in row if cell and not re.fullmatch(r"\d+", cell.strip())]
    name = max(name_cells, key=len) if name_cells else row_text
    return {
        "source_pdf": row_obj["source_pdf"],
        "page": row_obj["page"],
        "page_title": row_obj.get("page_title", ""),
        "raw_row": row,
        "raw_fragment": row_text,
        "name": name,
        "quantity": quantity,
        "unit": unit,
        "mass_per_unit": None,
        "designation": "",
        "confidence": "medium",
        "extraction_method": "pdf_table_row",
    }


def spec_rows_from_page_text(page_obj: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    text = page_obj.get("text") or ""
    for line in text.splitlines():
        raw = line.strip()
        if not raw:
            continue
        has_material_word = any(
            word in raw.lower()
            for word in (
                "бетон",
                "эппс",
                "армат",
                "фанер",
                "опалуб",
                "мембран",
                "геотекст",
                "пароизоля",
                "газобет",
                "schiedel",
                "logicroof",
                "воронк",
                "примыкан",
                "поликарбонат",
                "термовстав",
                "песок",
                "котлован",
            )
        )
        if not has_material_word:
            continue
        quantity, unit = parse_quantity_from_text(raw)
        if quantity is None and "длина" in raw.lower():
            number_match = re.search(NUMBER_RE, raw)
            if number_match:
                quantity = parse_number(number_match.group(0))
                unit = "м/п"
        if quantity is None:
            if "уточнить" in raw.lower():
                rows.append(
                    {
                        "source_pdf": page_obj["source_pdf"],
                        "page": page_obj["page"],
                        "page_title": page_obj.get("page_title", ""),
                        "raw_row": [],
                        "raw_fragment": raw,
                        "name": raw,
                        "quantity": "уточнить",
                        "unit": "",
                        "mass_per_unit": None,
                        "designation": "",
                        "confidence": "medium",
                        "extraction_method": "regex_from_page_text",
                    }
                )
            continue
        rows.append(
            {
                "source_pdf": page_obj["source_pdf"],
                "page": page_obj["page"],
                "page_title": page_obj.get("page_title", ""),
                "raw_row": [],
                "raw_fragment": raw,
                "name": raw,
                "quantity": quantity,
                "unit": unit,
                "mass_per_unit": None,
                "designation": "",
                "confidence": "high" if len(raw) < 220 else "medium",
                "extraction_method": "regex_from_page_text",
            }
        )
    return rows


def parse_spec_rows() -> list[dict[str, Any]]:
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    table_rows = load_json(TABLE_ROWS_PATH)
    pages = load_json(PAGES_TEXT_PATH)
    spec_rows: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()

    for row_obj in table_rows:
        parsed = spec_row_from_table_row(row_obj)
        if parsed:
            key = (parsed["source_pdf"], parsed["page"], parsed["raw_fragment"])
            if key not in seen:
                seen.add(key)
                spec_rows.append(parsed)

    for page_obj in pages:
        for parsed in spec_rows_from_page_text(page_obj):
            key = (parsed["source_pdf"], parsed["page"], parsed["raw_fragment"])
            if key not in seen:
                seen.add(key)
                spec_rows.append(parsed)

    SPEC_ROWS_PATH.write_text(json.dumps(spec_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return spec_rows


def main() -> int:
    spec_rows = parse_spec_rows()
    print(f"spec_rows: {SPEC_ROWS_PATH} ({len(spec_rows)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
