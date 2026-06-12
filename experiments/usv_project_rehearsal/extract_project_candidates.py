from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pdfplumber

from mapping_rules import CURATED_CANDIDATES


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "input_pdfs"
RAW_DIR = DATA_DIR / "raw_extraction"
PAGES_TEXT_PATH = RAW_DIR / "pages_text.json"
TABLES_PATH = RAW_DIR / "tables.json"
CANDIDATES_PATH = DATA_DIR / "extracted_candidates.json"


UNIT_RE = r"(м2|м²|м3|м³|м/п|мп|п\\.м\\.|шт|кг|кг/м3|м\\.п\\.)"
NUMBER_RE = re.compile(rf"(?P<label>[-А-Яа-яA-Za-z0-9+.,/() ×х]+?)\s+(?P<value>\d+[\d\s]*[,.]?\d*)\s*(?P<unit>{UNIT_RE})")


def normalize_number(raw: str) -> float | int | str:
    text = raw.replace(" ", "").replace(",", ".")
    try:
        value = float(text)
    except ValueError:
        return raw
    return int(value) if value.is_integer() else value


def compact_context(text: str, needle: str, width: int = 180) -> str:
    normalized = text.replace("\n", " ")
    index = normalized.lower().find(needle.lower())
    if index < 0:
        return normalized[:width].strip()
    start = max(0, index - width // 2)
    end = min(len(normalized), index + len(needle) + width // 2)
    return normalized[start:end].strip()


def page_title(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if len(line) > 3 and not line.isdigit():
            return line[:120]
    return ""


def extract_pages_and_tables() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    pages: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
        with pdfplumber.open(pdf_path) as pdf:
            for page_index, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                pages.append(
                    {
                        "source_pdf": pdf_path.name,
                        "page": page_index,
                        "page_title": page_title(text),
                        "text": text,
                    }
                )
                try:
                    extracted_tables = page.extract_tables() or []
                except Exception as exc:  # pragma: no cover - PDF parser defensive guard.
                    extracted_tables = []
                    tables.append(
                        {
                            "source_pdf": pdf_path.name,
                            "page": page_index,
                            "error": str(exc),
                            "tables": [],
                        }
                    )
                for table_index, table in enumerate(extracted_tables, start=1):
                    tables.append(
                        {
                            "source_pdf": pdf_path.name,
                            "page": page_index,
                            "table_index": table_index,
                            "rows": table,
                        }
                    )
    PAGES_TEXT_PATH.write_text(json.dumps(pages, ensure_ascii=False, indent=2), encoding="utf-8")
    TABLES_PATH.write_text(json.dumps(tables, ensure_ascii=False, indent=2), encoding="utf-8")
    return pages, tables


def generic_numeric_candidates(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for page in pages:
        text = page["text"]
        for match in NUMBER_RE.finditer(text.replace("\n", " ")):
            raw_label = " ".join(match.group("label").split())[-100:]
            if len(raw_label) < 3:
                continue
            candidates.append(
                {
                    "source_pdf": page["source_pdf"],
                    "page": page["page"],
                    "page_title": page["page_title"],
                    "raw_label": raw_label,
                    "raw_value": normalize_number(match.group("value")),
                    "unit": match.group("unit").replace("м²", "м2").replace("м³", "м3").replace("м.п.", "мп"),
                    "raw_context": compact_context(text, match.group("value")),
                    "confidence": "low",
                    "candidate_type": "generic_numeric",
                    "notes": "Автоматически найденное число с единицей; требуется маппинг/проверка.",
                }
            )
    return candidates


def curated_candidates(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_source_page = {(page["source_pdf"], page["page"]): page for page in pages}
    result: list[dict[str, Any]] = []
    for spec in CURATED_CANDIDATES:
        page = by_source_page.get((spec.source_pdf, spec.expected_page), {})
        text = page.get("text", "")
        value_text = str(spec.value).replace(".", ",")
        fragment = compact_context(text, value_text)
        lower_text = text.lower().replace(",", ".")
        keyword_hits = sum(1 for keyword in spec.keywords if keyword.lower().replace(",", ".") in lower_text)
        confidence = spec.confidence
        if confidence == "high" and keyword_hits == 0:
            confidence = "medium"
        result.append(
            {
                "source_pdf": spec.source_pdf,
                "page": spec.expected_page,
                "page_title": spec.page_title or page.get("page_title", ""),
                "raw_label": spec.raw_label,
                "raw_value": spec.value,
                "unit": spec.unit,
                "raw_context": fragment,
                "confidence": confidence,
                "candidate_type": "curated_control",
                "keyword_hits": keyword_hits,
                "notes": spec.notes,
            }
        )
    return result


def extract_project_candidates() -> list[dict[str, Any]]:
    pages, _tables = extract_pages_and_tables()
    candidates = curated_candidates(pages)
    candidates.extend(generic_numeric_candidates(pages))
    CANDIDATES_PATH.write_text(json.dumps(candidates, ensure_ascii=False, indent=2), encoding="utf-8")
    return candidates


def main() -> int:
    candidates = extract_project_candidates()
    print(f"pages_text: {PAGES_TEXT_PATH}")
    print(f"tables: {TABLES_PATH}")
    print(f"candidates: {CANDIDATES_PATH}")
    print(f"candidate_count: {len(candidates)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
