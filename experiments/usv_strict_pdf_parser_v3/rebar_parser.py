from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from candidate_store import CandidateStore
from spec_row_parser import NUMBER_RE, parse_number, table_row_objects


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
EXTRACTED_DIR = DATA_DIR / "extracted"
LOGICAL_PAGES_PATH = RAW_DIR / "logical_pages.json"
TABLES_PATH = RAW_DIR / "tables.json"
REBAR_ITEMS_PATH = EXTRACTED_DIR / "rebar_items.json"

ALLOWED_SHEETS = {
    "foundation_slab_spec",
    "thermal_inserts_plan",
    "walls_blocks_spec",
    "lintels_plan",
    "floor_slab_1_spec",
    "floor_slab_2_spec",
}
EXCLUDE_WORDS = ("труба", "ф110", "канализация", "водосток", "гофр", "угол", "тройник", "заглуш")
KG_PER_METER_VALUES = {0.222, 0.395, 0.617, 0.888, 1.58, 1.6, 2.47, 3.85}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_steel(text: str) -> str:
    text = text.upper().replace("А", "A").replace("С", "C")
    if "A500" in text:
        return "A500"
    if "A240" in text:
        return "A240"
    return ""


def section_code(sheet_type: str) -> str:
    return {
        "foundation_slab_spec": "foundation_slab",
        "thermal_inserts_plan": "foundation_slab",
        "walls_blocks_spec": "load_bearing_walls_lintels",
        "lintels_plan": "load_bearing_walls_lintels",
        "floor_slab_1_spec": "floor_slab_1",
        "floor_slab_2_spec": "floor_slab_2",
    }.get(sheet_type, "")


def is_rebar_text(text: str) -> bool:
    low = text.lower()
    if any(word in low for word in EXCLUDE_WORDS):
        return False
    has_gost = "34028" in low or "5781" in low
    has_diameter_steel = re.search(r"(?:ф|ø|d)\s*\d{1,2}.{0,30}(?:a|а)\s*500|(?:a|а)\s*240", low)
    has_words = any(word in low for word in ("армат", "ар-я", "хомут", "сетка"))
    return bool(has_gost or has_diameter_steel or has_words)


def parse_rebar_row(row: dict[str, Any], store: CandidateStore) -> dict[str, Any] | None:
    text = row["row_text"]
    if row["logical_sheet_type"] not in ALLOWED_SHEETS or not is_rebar_text(text):
        return None
    diameter_match = re.search(r"(?:ф|ø|d)\s*(?P<d>\d{1,2})", text, re.IGNORECASE)
    if not diameter_match:
        return None
    steel = normalize_steel(text)
    if not steel:
        return None
    numbers = [parse_number(match.group(0)) for match in re.finditer(NUMBER_RE, text)]
    numbers_after_diameter = [value for value in numbers if value != float(diameter_match.group("d"))]
    if not numbers_after_diameter:
        return None
    quantity_unit = ""
    quantity = None
    kg_per_meter = None
    low = text.lower()
    if "кг" in low and "м/п" not in low and "м.п" not in low:
        quantity_unit = "кг"
        quantity = numbers_after_diameter[-1]
    else:
        small = [value for value in numbers_after_diameter if round(value, 3) in KG_PER_METER_VALUES]
        kg_per_meter = small[-1] if small else None
        quantity_candidates = [value for value in numbers_after_diameter if value != kg_per_meter and value > 5]
        if quantity_candidates:
            quantity = quantity_candidates[-1]
            quantity_unit = "м/п"
    if quantity is None:
        return None
    evidence = store.add(
        source_pdf=row["source_pdf"],
        physical_page_number=row["physical_page_number"],
        drawing_sheet_number=row.get("drawing_sheet_number", ""),
        logical_sheet_title=row.get("logical_sheet_title", ""),
        logical_sheet_type=row["logical_sheet_type"],
        section_code=section_code(row["logical_sheet_type"]),
        candidate_type="rebar_item",
        raw_label=f"{steel} D{diameter_match.group('d')}",
        value=quantity,
        unit=quantity_unit,
        raw_context=text,
        confidence="high" if quantity_unit else "low",
        extraction_method="rebar_domain_parser",
    )
    return {
        "section_code": section_code(row["logical_sheet_type"]),
        "logical_sheet_type": row["logical_sheet_type"],
        "steel_class": steel,
        "diameter_mm": int(diameter_match.group("d")),
        "quantity": quantity,
        "quantity_unit": quantity_unit,
        "spec_length_m": quantity if quantity_unit == "м/п" else None,
        "source_weight_kg": quantity if quantity_unit == "кг" else None,
        "kg_per_meter": kg_per_meter,
        "source_pdf": row["source_pdf"],
        "physical_page_number": row["physical_page_number"],
        "logical_sheet_title": row.get("logical_sheet_title", ""),
        "raw_context": text,
        "confidence": "high" if quantity_unit else "low",
        "evidence_id": evidence["evidence_id"],
    }


def parse_rebar(store: CandidateStore) -> dict[str, Any]:
    logical_pages = load_json(LOGICAL_PAGES_PATH)
    tables = load_json(TABLES_PATH)
    rows = table_row_objects(tables, logical_pages)
    items = []
    excluded_pipe_like = 0
    for row in rows:
        if any(word in row["row_text"].lower() for word in EXCLUDE_WORDS):
            excluded_pipe_like += 1
            continue
        item = parse_rebar_row(row, store)
        if item:
            items.append(item)
    result = {
        "normalized_rebar_items": items,
        "low_confidence_rebar_items": [item for item in items if item["confidence"] == "low"],
        "excluded_pipe_like_rows": excluded_pipe_like,
    }
    REBAR_ITEMS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    store = CandidateStore()
    result = parse_rebar(store)
    store.write()
    print(f"rebar_items: {REBAR_ITEMS_PATH}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
