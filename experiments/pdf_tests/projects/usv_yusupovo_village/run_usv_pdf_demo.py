from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_DIR.parents[3]
PDF_TESTS_DIR = REPO_ROOT / "experiments" / "pdf_tests"

sys.path.insert(0, str(PDF_TESTS_DIR))

from pdf_parser import PDFParser  # noqa: E402


SOURCES = [
    {
        "source_id": "kr1_foundation",
        "source_file": "ЮСВ КР1.pdf",
        "title": "КР-1: фундаментная часть",
    },
    {
        "source_id": "kr2_above_zero",
        "source_file": "ЮСВ КР2.pdf",
        "title": "КР-2: выше нуля",
    },
    {
        "source_id": "ar_architecture",
        "source_file": "ЮСВ АР.pdf",
        "title": "АР: архитектура",
    },
]


PARAMETER_PATTERNS = [
    {
        "parameter_code": "elevation_mark",
        "name": "Отметка",
        "regex": r"(?:отм\.?|отметк[аи])\s*[+\-]?[0-9]+(?:[\.,][0-9]+)?",
    },
    {
        "parameter_code": "concrete_grade",
        "name": "Класс/марка бетона",
        "regex": r"(?:В|B)\s*\d{1,2}(?:[\.,]\d)?\s*(?:\(?\s*М\s*\d{2,3}\s*\)?)?",
    },
    {
        "parameter_code": "rebar_class_diameter",
        "name": "Арматура",
        "regex": r"А\s*(?:400|500|240)\s*[Øфdд]?\s*\d{1,2}|А(?:400|500|240)\s*диаметром\s*\d{1,2}\s*мм",
    },
    {
        "parameter_code": "thickness_mm",
        "name": "Толщина",
        "regex": r"(?:толщин[ао]й?|h\s*=?)\s*\d{2,3}\s*мм|\d{2,3}\s*мм",
    },
    {
        "parameter_code": "gas_block",
        "name": "Газобетонный блок",
        "regex": r"газобетон\w*[^\n]{0,80}",
    },
    {
        "parameter_code": "foundation",
        "name": "Фундамент",
        "regex": r"фундамент\w*[^\n]{0,80}",
    },
    {
        "parameter_code": "slab",
        "name": "Плита",
        "regex": r"плит[ауы][^\n]{0,100}",
    },
    {
        "parameter_code": "roof",
        "name": "Кровля",
        "regex": r"кровл\w+[^\n]{0,100}",
    },
]


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def prepare_clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def remove_existing_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


def render_page_images(pdf_path: Path, output_dir: Path) -> list[dict[str, Any]]:
    import fitz

    images_dir = output_dir / "page_images"
    images_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[dict[str, Any]] = []
    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            image_name = f"page_{page_index:03d}.png"
            image_path = images_dir / image_name
            pixmap.save(image_path)
            rendered.append(
                {
                    "page": page_index,
                    "image_file": str(image_path.relative_to(PROJECT_DIR)),
                    "width": pixmap.width,
                    "height": pixmap.height,
                }
            )
    return rendered


def first_page_title(blocks_by_page: dict[int, list[dict[str, Any]]], page_number: int) -> str:
    blocks = blocks_by_page.get(page_number, [])
    for block in blocks:
        text = " ".join((block.get("text") or "").split())
        if text.startswith("GSPublisherVersion"):
            continue
        if 5 <= len(text) <= 160:
            return text
    return ""


def extract_parameters(parsed_sources: list[dict[str, Any]]) -> dict[str, Any]:
    parameters: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, int]] = set()

    for source in parsed_sources:
        parsed_dir = PROJECT_DIR / source["parsed_dir"]
        pages = load_json(parsed_dir / "pages_text.json")
        blocks = load_json(parsed_dir / "blocks.json")
        blocks_by_page = {item["page"]: item.get("blocks", []) for item in blocks}

        for page in pages:
            page_number = page["page"]
            text = page.get("text", "")
            section_title = first_page_title(blocks_by_page, page_number)
            for pattern in PARAMETER_PATTERNS:
                for match in re.finditer(pattern["regex"], text, flags=re.IGNORECASE):
                    value = " ".join(match.group(0).split())
                    key = (pattern["parameter_code"], value.lower(), source["source_file"], page_number)
                    if key in seen:
                        continue
                    seen.add(key)
                    parameters.append(
                        {
                            "parameter_code": pattern["parameter_code"],
                            "name": pattern["name"],
                            "value": value,
                            "source_file": source["source_file"],
                            "source_id": source["source_id"],
                            "page": page_number,
                            "section_title": section_title,
                            "confidence": "demo_regex",
                            "review_status": "needs_human_review",
                        }
                    )

    return {
        "project": "usv_yusupovo_village",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "extraction_method": "deterministic_regex_demo_no_ai",
        "parameters": parameters,
    }


def write_full_text_by_sources(parsed_sources: list[dict[str, Any]], merged_dir: Path) -> None:
    chunks = ["# USV Yusupovo Village: full text by sources", ""]
    for source in parsed_sources:
        parsed_dir = PROJECT_DIR / source["parsed_dir"]
        chunks.extend(
            [
                f"## {source['title']}",
                "",
                f"- source_file: `{source['source_file']}`",
                f"- source_id: `{source['source_id']}`",
                "",
            ]
        )
        pages = load_json(parsed_dir / "pages_text.json")
        for page in pages:
            chunks.extend(
                [
                    f"### {source['source_id']} / page {page['page']}",
                    "",
                    page.get("text", "").strip(),
                    "",
                ]
            )
    (merged_dir / "project_full_text_by_sources.md").write_text("\n".join(chunks), encoding="utf-8")


def write_report(manifest: dict[str, Any], extracted: dict[str, Any], merged_dir: Path) -> None:
    lines = [
        "# Extraction Report: usv_yusupovo_village",
        "",
        "## Summary",
        "",
        f"- generated_at: `{manifest['generated_at']}`",
        f"- sources: `{len(manifest['sources'])}`",
        f"- demo_parameters_for_review: `{len(extracted['parameters'])}`",
        "- AI: `not used`",
        "",
        "## Sources",
        "",
        "| source_id | source_file | pages | parsed_dir |",
        "| --- | --- | ---: | --- |",
    ]
    for source in manifest["sources"]:
        lines.append(
            f"| `{source['source_id']}` | `{source['source_file']}` | `{source['pages']}` | `{source['parsed_dir']}` |"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            "Each parsed source keeps separate raw parser artifacts:",
            "",
            "- `full_text.txt`",
            "- `pages_text.json`",
            "- `blocks.json`",
            "- `tables.json`",
            "- `tables.xlsx`",
            "- `summary.json`",
            "- `page_images/`",
            "",
            "Merged files keep source boundaries and page references. They do not replace source-specific parsed folders.",
            "",
            "## Notes",
            "",
            "- `extracted_parameters_for_review.json` is a deterministic demo extraction.",
            "- Every extracted parameter has `source_file`, `source_id`, `page`, and `section_title`.",
            "- Parameters are marked `needs_human_review`.",
        ]
    )
    (merged_dir / "extraction_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parsed_dir = PROJECT_DIR / "parsed"
    merged_dir = PROJECT_DIR / "merged"
    parsed_dir.mkdir(parents=True, exist_ok=True)
    prepare_clean_dir(merged_dir)

    parser = PDFParser(project_name="usv_yusupovo_village")
    parser.output_root = parsed_dir

    parsed_sources: list[dict[str, Any]] = []
    for source in SOURCES:
        pdf_path = PROJECT_DIR / "input" / source["source_file"]
        if not pdf_path.exists():
            raise FileNotFoundError(f"Missing source PDF: {pdf_path}")

        target_dir = parsed_dir / source["source_id"]
        remove_existing_dir(target_dir)

        text_pages = parser.extract_text_pymupdf(pdf_path)
        blocks = parser.extract_blocks_pymupdf(pdf_path)
        tables = parser.extract_tables_pdfplumber(pdf_path)
        result_dir, summary = parser.save_results(
            pdf_path,
            text_pages=text_pages,
            blocks=blocks,
            tables=tables,
            run_name=source["source_id"],
        )
        if result_dir != target_dir:
            raise RuntimeError(f"Unexpected parser output dir: {result_dir}; expected {target_dir}")
        page_images = render_page_images(pdf_path, result_dir)
        summary["page_images_count"] = len(page_images)
        summary["source_id"] = source["source_id"]
        save_json(result_dir / "summary.json", summary)

        parsed_sources.append(
            {
                **source,
                "input_path": str(pdf_path.relative_to(PROJECT_DIR)),
                "parsed_dir": str(result_dir.relative_to(PROJECT_DIR)),
                "pages": summary["pages"],
                "text_characters": summary["text_characters"],
                "tables_found": summary["tables_found"],
                "page_images_count": len(page_images),
                "artifacts": [
                    "full_text.txt",
                    "pages_text.json",
                    "blocks.json",
                    "tables.json",
                    "tables.xlsx",
                    "summary.json",
                    "page_images/",
                ],
            }
        )

    manifest = {
        "project": "usv_yusupovo_village",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "sources": parsed_sources,
    }
    save_json(merged_dir / "project_manifest.json", manifest)
    write_full_text_by_sources(parsed_sources, merged_dir)
    extracted = extract_parameters(parsed_sources)
    save_json(merged_dir / "extracted_parameters_for_review.json", extracted)
    write_report(manifest, extracted, merged_dir)

    print(
        json.dumps(
            {
                "project": manifest["project"],
                "sources": [
                    {
                        "source_id": item["source_id"],
                        "pages": item["pages"],
                        "tables_found": item["tables_found"],
                        "page_images_count": item["page_images_count"],
                    }
                    for item in parsed_sources
                ],
                "parameters_for_review": len(extracted["parameters"]),
                "merged_dir": str(merged_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
