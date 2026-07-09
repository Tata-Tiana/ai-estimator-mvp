"""A6.0: render every page of a PDF to a PNG image, no page selection.

Deliberately renders the whole document — the point of this POC is an
honest full-project run, not a hand-picked set of "good" pages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import fitz  # PyMuPDF


def render_pdf_pages(pdf_path: Path, out_dir: Path, zoom: float = 2.0) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    matrix = fitz.Matrix(zoom, zoom)
    manifest: list[dict] = []
    pdf_stem = pdf_path.stem
    for page_index in range(doc.page_count):
        page_number = page_index + 1
        pix = doc[page_index].get_pixmap(matrix=matrix)
        image_path = out_dir / f"{pdf_stem}_page_{page_number:03d}.png"
        pix.save(image_path)
        manifest.append({
            "source_pdf": pdf_path.name,
            "page_number": page_number,
            "image_path": str(image_path),
            "width_px": pix.width,
            "height_px": pix.height,
            "zoom": zoom,
        })
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-path", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--zoom", type=float, default=2.0, help="PyMuPDF zoom factor (2.0 ~= 144 DPI)")
    args = parser.parse_args()

    manifest = render_pdf_pages(args.pdf_path, args.out_dir, zoom=args.zoom)

    manifest_path = args.out_dir / "manifest.json"
    existing: list[dict] = []
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        existing = [m for m in existing if m["source_pdf"] != args.pdf_path.name]
    manifest_path.write_text(
        json.dumps(existing + manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"rendered {len(manifest)} pages from {args.pdf_path.name} -> {args.out_dir}")
    print(f"manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
