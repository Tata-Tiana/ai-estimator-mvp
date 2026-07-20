"""Prepare PDF pages for section-by-section Claude API extraction.

The output is intentionally project-data local and belongs under outputs/.
It contains:
- one text file per PDF page;
- one rendered PNG per PDF page;
- manifest.json describing the prepared pages.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fitz


def slugify(value: str) -> str:
    slug = re.sub(r"[^\w.-]+", "_", value, flags=re.UNICODE).strip("_")
    return slug or "pdf"


def guess_page_title(text: str) -> str | None:
    for line in text.splitlines():
        clean = " ".join(line.split())
        if clean:
            return clean[:160]
    return None


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare_pdf(
    pdf_path: Path,
    out_dir: Path,
    dpi: int,
    max_pages: int | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    document = fitz.open(pdf_path)
    pdf_slug = slugify(pdf_path.stem)
    text_dir = out_dir / "pages_text" / pdf_slug
    image_dir = out_dir / "pages_images" / pdf_slug
    text_dir.mkdir(parents=True, exist_ok=True)
    image_dir.mkdir(parents=True, exist_ok=True)

    pages: list[dict[str, Any]] = []
    page_count = len(document)
    limit = min(page_count, max_pages) if max_pages else page_count
    matrix = fitz.Matrix(dpi / 72, dpi / 72)

    for page_index in range(limit):
        page_number = page_index + 1
        page = document[page_index]
        text = page.get_text("text")
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)

        text_path = text_dir / f"page_{page_number:03d}.txt"
        image_path = image_dir / f"page_{page_number:03d}.png"
        text_path.write_text(text, encoding="utf-8")
        pixmap.save(image_path)

        pages.append(
            {
                "page_uid": f"{pdf_slug}:page_{page_number:03d}",
                "source_pdf": pdf_path.name,
                "source_pdf_path": str(pdf_path),
                "page_number": page_number,
                "page_index": page_index,
                "title_guess": guess_page_title(text),
                "text_path": str(text_path),
                "image_path": str(image_path),
                "text_chars": len(text),
                "image_bytes": image_path.stat().st_size,
                "image_width_px": pixmap.width,
                "image_height_px": pixmap.height,
            }
        )

    pdf_info = {
        "source_pdf": pdf_path.name,
        "source_pdf_path": str(pdf_path),
        "file_size_bytes": pdf_path.stat().st_size,
        "page_count": page_count,
        "prepared_pages": limit,
    }
    return pdf_info, pages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-code", required=True, help="Neutral run id, for example ark/trc/usv.")
    parser.add_argument("--pdf", action="append", type=Path, required=True, help="Project PDF. Pass multiple times.")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=160)
    parser.add_argument("--max-pages", type=int, default=None, help="Debug limit per PDF.")
    args = parser.parse_args()

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_infos: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    full_text_parts: list[str] = []

    for pdf in args.pdf:
        pdf_path = pdf.expanduser().resolve()
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)
        pdf_info, pdf_pages = prepare_pdf(pdf_path, out_dir, args.dpi, args.max_pages)
        pdf_infos.append(pdf_info)
        pages.extend(pdf_pages)
        full_text_parts.append(f"# PDF: {pdf_path.name}\n")
        for page in pdf_pages:
            page_text = Path(page["text_path"]).read_text(encoding="utf-8")
            full_text_parts.append(f"\n## {pdf_path.name}, page {page['page_number']}\n\n{page_text}\n")

    manifest = {
        "project_code": args.project_code,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dpi": args.dpi,
        "pdfs": pdf_infos,
        "pages": pages,
    }
    write_json(out_dir / "manifest.json", manifest)
    (out_dir / "project_full_text.md").write_text("\n".join(full_text_parts), encoding="utf-8")

    print(f"prepared pages: {len(pages)}")
    print(f"manifest -> {out_dir / 'manifest.json'}")
    print(f"full text -> {out_dir / 'project_full_text.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
