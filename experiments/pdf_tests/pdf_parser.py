from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import re

from logger import get_logger


class PDFParser:
    def __init__(self) -> None:
        self.logger = get_logger()
        self.project_root = Path(__file__).resolve().parents[2]
        self.output_root = self.project_root / "data" / "output" / "pdf_experiments"
        self.output_root.mkdir(parents=True, exist_ok=True)

    def extract_text_pymupdf(self, pdf_path: str | Path) -> list[dict]:
        fitz = self._require_pymupdf()
        pdf_file = Path(pdf_path)
        results: list[dict] = []

        self.logger.info("Extracting text with PyMuPDF: %s", pdf_file)
        with fitz.open(pdf_file) as document:
            for page_index, page in enumerate(document, start=1):
                try:
                    text = page.get_text("text")
                    results.append({"page": page_index, "text": text})
                except Exception as exc:
                    self.logger.exception("Text extraction failed on page %s: %s", page_index, exc)
                    results.append({"page": page_index, "text": "", "error": str(exc)})
        return results

    def extract_blocks_pymupdf(self, pdf_path: str | Path) -> list[dict]:
        fitz = self._require_pymupdf()
        pdf_file = Path(pdf_path)
        results: list[dict] = []

        self.logger.info("Extracting blocks with PyMuPDF: %s", pdf_file)
        with fitz.open(pdf_file) as document:
            for page_index, page in enumerate(document, start=1):
                page_blocks: list[dict] = []
                try:
                    for block in page.get_text("blocks"):
                        x0, y0, x1, y1, text, *_ = block
                        cleaned_text = (text or "").strip()
                        if not cleaned_text:
                            continue
                        page_blocks.append(
                            {
                                "x0": x0,
                                "y0": y0,
                                "x1": x1,
                                "y1": y1,
                                "text": cleaned_text,
                            }
                        )
                except Exception as exc:
                    self.logger.exception("Block extraction failed on page %s: %s", page_index, exc)
                    results.append({"page": page_index, "blocks": [], "error": str(exc)})
                    continue

                results.append({"page": page_index, "blocks": page_blocks})
        return results

    def extract_tables_pdfplumber(self, pdf_path: str | Path) -> list[dict]:
        pdfplumber = self._require_pdfplumber()
        pdf_file = Path(pdf_path)
        results: list[dict] = []

        self.logger.info("Extracting tables with pdfplumber: %s", pdf_file)
        with pdfplumber.open(pdf_file) as pdf:
            for page_index, page in enumerate(pdf.pages, start=1):
                try:
                    tables = page.extract_tables()
                except Exception as exc:
                    self.logger.exception("Table extraction failed on page %s: %s", page_index, exc)
                    continue

                for table_index, table in enumerate(tables):
                    if not table:
                        continue
                    results.append(
                        {
                            "page": page_index,
                            "table_index": table_index,
                            "rows": table,
                        }
                    )
        return results

    def save_results(
        self,
        pdf_path: str | Path,
        text_pages: list[dict] | None = None,
        blocks: list[dict] | None = None,
        tables: list[dict] | None = None,
    ) -> tuple[Path, dict]:
        pdf_file = Path(pdf_path)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        safe_name = self._slugify(pdf_file.stem)
        result_dir = self.output_root / f"{safe_name}_{timestamp}"
        result_dir.mkdir(parents=True, exist_ok=True)

        if text_pages is not None:
            full_text = "\n\n".join(item.get("text", "") for item in text_pages)
            (result_dir / "full_text.txt").write_text(full_text, encoding="utf-8")
            self._save_json(result_dir / "pages_text.json", text_pages)

        if blocks is not None:
            self._save_json(result_dir / "blocks.json", blocks)

        if tables is not None:
            self._save_json(result_dir / "tables.json", tables)
            self._save_tables_xlsx(result_dir / "tables.xlsx", tables)

        summary = self._build_summary(pdf_file, text_pages, blocks, tables, result_dir)
        self._save_json(result_dir / "summary.json", summary)
        return result_dir, summary

    def get_page_count(self, pdf_path: str | Path) -> int:
        fitz = self._require_pymupdf()
        pdf_file = Path(pdf_path)
        with fitz.open(pdf_file) as document:
            return len(document)

    def _build_summary(
        self,
        pdf_file: Path,
        text_pages: list[dict] | None,
        blocks: list[dict] | None,
        tables: list[dict] | None,
        result_dir: Path,
    ) -> dict:
        text_pages = text_pages or []
        blocks = blocks or []
        tables = tables or []
        text_chars = sum(len(item.get("text", "")) for item in text_pages)
        pages_with_tables = sorted({item["page"] for item in tables})
        summary = {
            "file_name": pdf_file.name,
            "file_path": str(pdf_file),
            "pages": self.get_page_count(pdf_file),
            "text_characters": text_chars,
            "text_pages": len(text_pages),
            "block_pages": len(blocks),
            "tables_found": len(tables),
            "pages_with_tables": pages_with_tables,
            "result_dir": str(result_dir),
        }
        self.logger.info("Processed PDF: %s", pdf_file)
        self.logger.info("Pages: %s", summary["pages"])
        self.logger.info("Text characters: %s", text_chars)
        self.logger.info("Tables found: %s", len(tables))
        return summary

    def _save_json(self, path: Path, data: object) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _save_tables_xlsx(self, path: Path, tables: list[dict]) -> None:
        pandas = self._require_pandas()
        with pandas.ExcelWriter(path, engine="openpyxl") as writer:
            if not tables:
                pandas.DataFrame([{"message": "No tables found"}]).to_excel(
                    writer,
                    index=False,
                    sheet_name="summary",
                )
                return

            for table in tables:
                rows = table.get("rows", [])
                if not rows:
                    continue

                header = rows[0]
                body = rows[1:] if len(rows) > 1 else []
                max_len = max((len(row) for row in rows), default=0)
                normalized_header = self._normalize_row_length(header, max_len)
                normalized_body = [self._normalize_row_length(row, max_len) for row in body]
                dataframe = pandas.DataFrame(normalized_body, columns=normalized_header)
                sheet_name = f"p{table['page']}_t{table['table_index']}"[:31]
                dataframe.to_excel(writer, index=False, sheet_name=sheet_name)

    def _normalize_row_length(self, row: list | None, length: int) -> list:
        row = row or []
        return row + [None] * (length - len(row))

    def _slugify(self, value: str) -> str:
        value = value.strip().lower()
        value = re.sub(r"[^a-z0-9а-яё]+", "_", value)
        return value.strip("_") or "pdf"

    def _require_pymupdf(self):
        try:
            import fitz
        except ImportError as exc:
            raise ImportError("PyMuPDF is not installed. Add 'pymupdf' to the environment.") from exc
        return fitz

    def _require_pdfplumber(self):
        try:
            import pdfplumber
        except ImportError as exc:
            raise ImportError("pdfplumber is not installed. Add 'pdfplumber' to the environment.") from exc
        return pdfplumber

    def _require_pandas(self):
        try:
            import pandas
        except ImportError as exc:
            raise ImportError("pandas is not installed. Add 'pandas' and 'openpyxl' to the environment.") from exc
        return pandas
