from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pdfplumber


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "input_pdfs"
RAW_DIR = DATA_DIR / "raw"
PAGES_TEXT_PATH = RAW_DIR / "pages_text.json"
TABLES_PATH = RAW_DIR / "tables.json"
TABLE_ROWS_PATH = RAW_DIR / "table_rows.json"


def page_title_from_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title_keywords = (
        "план",
        "спецификация",
        "схема",
        "разрез",
        "узел",
        "кровл",
        "котлован",
        "перекрытия",
        "фундамент",
    )
    for line in lines[:20]:
        low = line.lower()
        if any(keyword in low for keyword in title_keywords) and len(line) <= 140:
            return line
    return lines[0][:140] if lines else ""


def normalize_cell(value: Any) -> str:
    return "" if value is None else str(value).strip()


def extract_pdfs(pdf_dir: Path = PDF_DIR) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    pages: list[dict[str, Any]] = []
    tables: list[dict[str, Any]] = []
    table_rows: list[dict[str, Any]] = []

    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        with pdfplumber.open(pdf_path) as pdf:
            for index, page in enumerate(pdf.pages, start=1):
                text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
                page_title = page_title_from_text(text)
                pages.append(
                    {
                        "source_pdf": pdf_path.name,
                        "page": index,
                        "page_title": page_title,
                        "text": text,
                        "extraction_method": "pdfplumber_text",
                    }
                )
                extracted_tables = page.extract_tables() or []
                for table_index, table in enumerate(extracted_tables, start=1):
                    rows = [[normalize_cell(cell) for cell in row] for row in table]
                    table_obj = {
                        "source_pdf": pdf_path.name,
                        "page": index,
                        "page_title": page_title,
                        "table_index": table_index,
                        "rows": rows,
                        "extraction_method": "pdfplumber_table",
                    }
                    tables.append(table_obj)
                    for row_index, row in enumerate(rows, start=1):
                        if any(row):
                            table_rows.append(
                                {
                                    "source_pdf": pdf_path.name,
                                    "page": index,
                                    "page_title": page_title,
                                    "table_index": table_index,
                                    "row_index": row_index,
                                    "row": row,
                                    "row_text": " ".join(cell for cell in row if cell),
                                }
                            )

    PAGES_TEXT_PATH.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    TABLES_PATH.write_text(json.dumps(tables, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    TABLE_ROWS_PATH.write_text(json.dumps(table_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return pages, tables, table_rows


def main() -> int:
    pages, tables, rows = extract_pdfs()
    print(f"pages_text: {PAGES_TEXT_PATH} ({len(pages)})")
    print(f"tables: {TABLES_PATH} ({len(tables)})")
    print(f"table_rows: {TABLE_ROWS_PATH} ({len(rows)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
