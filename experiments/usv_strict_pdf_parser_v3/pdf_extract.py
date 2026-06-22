from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pdfplumber

import parser_paths


def normalize_cell(value: Any) -> str:
    return "" if value is None else str(value).strip()


def preliminary_title(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title_words = ("план", "спецификация", "схема", "разрез", "узлы", "ведомость")
    for line in lines[:25]:
        low = line.lower()
        if any(word in low for word in title_words) and len(line) <= 160:
            return line
    return lines[0][:160] if lines else ""


def extract_pdf_data() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    parser_paths.raw_dir().mkdir(parents=True, exist_ok=True)
    pages: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    for pdf_path in sorted(parser_paths.input_dir().glob("*.pdf")):
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
                words = page.extract_words(x_tolerance=1, y_tolerance=3, keep_blank_chars=False) or []
                page_obj = {
                    "source_pdf": pdf_path.name,
                    "physical_page_number": page_number,
                    "preliminary_page_title": preliminary_title(text),
                    "raw_page_text": text,
                    "words": words,
                    "extraction_method": "pdfplumber",
                }
                pages.append(page_obj)
                for table_index, table in enumerate(page.extract_tables() or [], start=1):
                    tables.append(
                        {
                            "source_pdf": pdf_path.name,
                            "physical_page_number": page_number,
                            "table_index": table_index,
                            "rows": [[normalize_cell(cell) for cell in row] for row in table],
                        }
                    )
    parser_paths.pages_text_path().write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    parser_paths.tables_path().write_text(json.dumps(tables, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return pages, tables


def main() -> int:
    pages, tables = extract_pdf_data()
    print(f"pages_text: {parser_paths.pages_text_path()} ({len(pages)})")
    print(f"tables: {parser_paths.tables_path()} ({len(tables)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
