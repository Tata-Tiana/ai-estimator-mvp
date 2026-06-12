from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
EXTRACTED_DIR = DATA_DIR / "extracted"
PAGES_TEXT_PATH = RAW_DIR / "pages_text.json"
TABLE_ROWS_PATH = RAW_DIR / "table_rows.json"
SPEC_ROWS_PATH = EXTRACTED_DIR / "spec_rows.json"
CANDIDATES_PATH = EXTRACTED_DIR / "candidates.json"

def token(*parts: str) -> str:
    return "".join(parts)


FORBIDDEN_CANDIDATE_TYPES = {
    token("curated", "_control"),
    token("expected", "_value"),
    token("manual", "_seed"),
    token("known", "_usv", "_value"),
    token("qa", "_expected"),
}
NUMBER_RE = r"\d+(?:[ \u00a0]\d{3})+|\d+(?:[,.]\d+)?"
UNIT_RE = r"м3|м2|м/п|м\.п\.|п\.м\.|шт|кг|т|м"
NUMERIC_RE = re.compile(rf"(?P<label>[-А-Яа-яA-Za-z0-9+.,/() ×хёЁ]+?)\s+(?P<value>{NUMBER_RE})\s*(?P<unit>{UNIT_RE})", re.IGNORECASE)
REBAR_RE = re.compile(
    rf"(?P<label>(?:ф|ø|d)\s*(?P<diameter>\d{{1,2}})\s*(?P<steel>A\d{{3}}\w*)?.{{0,90}}?)"
    rf"(?P<value>{NUMBER_RE})\s*(?P<unit>{UNIT_RE})?",
    re.IGNORECASE,
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_number(value: Any) -> float | str:
    if isinstance(value, (int, float)):
        return value
    text = str(value).strip()
    if not text or not re.search(r"\d", text):
        return text
    return float(text.replace("\u00a0", " ").replace(" ", "").replace(",", "."))


def normalize_unit(unit: str | None) -> str:
    if not unit:
        return ""
    unit = unit.lower().replace(".", "")
    if unit in {"мп", "пм"}:
        return "м/п"
    return unit


def make_candidate_id(payload: dict[str, Any]) -> str:
    base = "|".join(
        str(payload.get(key, ""))
        for key in ("source_pdf", "page", "candidate_type", "raw_label", "raw_value", "unit", "raw_context")
    )
    return "cand_" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]


def candidate(payload: dict[str, Any]) -> dict[str, Any]:
    if payload["candidate_type"] in FORBIDDEN_CANDIDATE_TYPES:
        raise ValueError(f"Forbidden candidate_type: {payload['candidate_type']}")
    payload["unit"] = normalize_unit(payload.get("unit"))
    payload["candidate_id"] = make_candidate_id(payload)
    return payload


def candidates_from_spec_rows(spec_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for row in spec_rows:
        result.append(
            candidate(
                {
                    "source_pdf": row["source_pdf"],
                    "page": row["page"],
                    "page_title": row.get("page_title", ""),
                    "raw_label": row.get("name", ""),
                    "raw_value": row.get("quantity"),
                    "unit": row.get("unit", ""),
                    "raw_context": row.get("raw_fragment") or " ".join(row.get("raw_row", [])),
                    "candidate_type": "parsed_spec_row",
                    "extraction_method": row.get("extraction_method", "pdf_table_row"),
                    "confidence": row.get("confidence", "medium"),
                    "notes": "",
                }
            )
        )
    return result


def candidates_from_page_text(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for page in pages:
        for line in (page.get("text") or "").splitlines():
            raw = line.strip()
            if len(raw) < 5:
                continue
            for match in NUMERIC_RE.finditer(raw):
                label = match.group("label").strip(" -—:;")
                if len(label) < 3:
                    continue
                result.append(
                    candidate(
                        {
                            "source_pdf": page["source_pdf"],
                            "page": page["page"],
                            "page_title": page.get("page_title", ""),
                            "raw_label": label[-160:],
                            "raw_value": parse_number(match.group("value")),
                            "unit": match.group("unit"),
                            "raw_context": raw,
                            "candidate_type": "regex_from_pdf_text",
                            "extraction_method": "line_numeric_regex",
                            "confidence": "medium",
                            "notes": "",
                        }
                    )
                )
            if re.search(r"(ф|ø|d)\s*\d{1,2}", raw, re.IGNORECASE):
                for match in REBAR_RE.finditer(raw):
                    unit = normalize_unit(match.group("unit"))
                    confidence = "medium" if unit else "low"
                    notes = "" if unit else "Не удалось надежно извлечь единицу измерения арматуры из PDF."
                    result.append(
                        candidate(
                            {
                                "source_pdf": page["source_pdf"],
                                "page": page["page"],
                                "page_title": page.get("page_title", ""),
                                "raw_label": match.group("label").strip(),
                                "raw_value": parse_number(match.group("value")),
                                "unit": unit or "unknown",
                                "raw_context": raw,
                                "candidate_type": "regex_from_pdf_text",
                                "extraction_method": "rebar_regex_from_line",
                                "confidence": confidence,
                                "notes": notes,
                            }
                        )
                    )
            if "уточнить" in raw.lower():
                result.append(
                    candidate(
                        {
                            "source_pdf": page["source_pdf"],
                            "page": page["page"],
                            "page_title": page.get("page_title", ""),
                            "raw_label": raw[:180],
                            "raw_value": "уточнить",
                            "unit": "",
                            "raw_context": raw,
                            "candidate_type": "regex_from_pdf_text",
                            "extraction_method": "supplier_required_text",
                            "confidence": "medium",
                            "notes": "В PDF значение требует уточнения у поставщика/монтажной организации.",
                        }
                    )
                )
    return result


def candidates_from_table_rows(table_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for row in table_rows:
        row_text = row.get("row_text") or ""
        for match in NUMERIC_RE.finditer(row_text):
            label = match.group("label").strip(" -—:;")
            if len(label) < 3:
                continue
            result.append(
                candidate(
                    {
                        "source_pdf": row["source_pdf"],
                        "page": row["page"],
                        "page_title": row.get("page_title", ""),
                        "raw_label": label[-160:],
                        "raw_value": parse_number(match.group("value")),
                        "unit": match.group("unit"),
                        "raw_context": row_text,
                        "candidate_type": "regex_from_pdf_table",
                        "extraction_method": "table_row_numeric_regex",
                        "confidence": "medium",
                        "notes": "",
                    }
                )
            )
    return result


def extract_candidates() -> list[dict[str, Any]]:
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    pages = load_json(PAGES_TEXT_PATH)
    table_rows = load_json(TABLE_ROWS_PATH)
    spec_rows = load_json(SPEC_ROWS_PATH)

    candidates = []
    seen: set[str] = set()
    for item in candidates_from_spec_rows(spec_rows) + candidates_from_page_text(pages) + candidates_from_table_rows(table_rows):
        if item["candidate_id"] not in seen:
            seen.add(item["candidate_id"])
            candidates.append(item)

    forbidden = [item for item in candidates if item.get("candidate_type") in FORBIDDEN_CANDIDATE_TYPES]
    if forbidden:
        raise ValueError(f"Forbidden candidates detected: {forbidden[:3]}")

    CANDIDATES_PATH.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return candidates


def main() -> int:
    candidates = extract_candidates()
    print(f"candidates: {CANDIDATES_PATH} ({len(candidates)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
