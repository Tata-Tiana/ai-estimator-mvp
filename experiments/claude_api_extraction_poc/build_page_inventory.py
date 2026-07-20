"""Build a neutral page inventory before Claude mapping.

This layer does not decide calculator values. It extracts observable page
features that can make the model's work less fuzzy:
- text lines with coordinates from PyMuPDF;
- rough tables from pdfplumber;
- numeric/unit candidates;
- Russian alias hits from target_aliases_ru.yaml.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import fitz
import pdfplumber
import yaml


HERE = Path(__file__).resolve().parent
PACK_DIR = HERE / "pack"

NUMBER_UNIT_RE = re.compile(
    r"(?P<number>[-+]?\d+(?:[ \u00a0]\d{3})*(?:[,.]\d+)?)\s*"
    r"(?P<unit>м2|м²|кв\.?\s*м|м3|м³|куб\.?\s*м|м\.?\s*пог\.?|п\.?\s*м\.?|м/п|мп|м|мм|шт|штук|комплект|рул|баллон)",
    re.IGNORECASE,
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_text(value: Any) -> str:
    text = str(value or "").lower().replace("ё", "е")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_number(raw: str) -> float | None:
    cleaned = raw.replace("\u00a0", "").replace(" ", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_page_ref(ref: str) -> tuple[str, int]:
    if ":" not in ref:
        raise ValueError(f"page ref must look like 'source.pdf:23', got: {ref}")
    source_pdf, page_number = ref.rsplit(":", 1)
    return source_pdf, int(page_number)


def select_manifest_pages(manifest: dict[str, Any], page_refs: list[str] | None) -> list[dict[str, Any]]:
    pages = list(manifest.get("pages") or [])
    if not page_refs:
        return pages
    wanted = {parse_page_ref(ref) for ref in page_refs}
    selected = [
        page
        for page in pages
        if (page["source_pdf"], int(page["page_number"])) in wanted
    ]
    found = {(page["source_pdf"], int(page["page_number"])) for page in selected}
    missing = sorted(wanted - found)
    if missing:
        raise ValueError(f"page refs not found in manifest: {missing}")
    return selected


def load_alias_entries(section_codes: set[str] | None) -> list[dict[str, Any]]:
    aliases_path = PACK_DIR / "data" / "target_aliases_ru.yaml"
    raw = yaml.safe_load(aliases_path.read_text(encoding="utf-8"))
    entries: list[dict[str, Any]] = []
    for target_code, data in raw.items():
        if target_code.startswith("_") or not isinstance(data, dict):
            continue
        section_code = data.get("section_code")
        if section_codes and section_code not in section_codes:
            continue
        aliases = data.get("pdf_aliases") or []
        for alias in aliases:
            alias_norm = normalize_text(alias)
            if len(alias_norm) < 3:
                continue
            entries.append(
                {
                    "target_code": target_code,
                    "section_code": section_code,
                    "ru_label": data.get("ru_label"),
                    "alias": alias,
                    "alias_norm": alias_norm,
                    "expected_unit": data.get("expected_unit"),
                }
            )
    return entries


def find_numbers(text: str) -> list[dict[str, Any]]:
    numbers: list[dict[str, Any]] = []
    for match in NUMBER_UNIT_RE.finditer(text):
        numbers.append(
            {
                "raw": match.group(0),
                "value": parse_number(match.group("number")),
                "unit": match.group("unit"),
                "span": [match.start(), match.end()],
            }
        )
    return numbers


def find_alias_hits(text: str, alias_entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    text_norm = normalize_text(text)
    hits: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for entry in alias_entries:
        alias_norm = entry["alias_norm"]
        if alias_norm in text_norm:
            key = (entry["target_code"], alias_norm)
            if key in seen:
                continue
            seen.add(key)
            hits.append(
                {
                    "target_code": entry["target_code"],
                    "section_code": entry["section_code"],
                    "ru_label": entry["ru_label"],
                    "alias": entry["alias"],
                    "expected_unit": entry["expected_unit"],
                }
            )
    return hits


def text_lines_from_page(pdf_path: Path, page_index: int) -> list[dict[str, Any]]:
    document = fitz.open(pdf_path)
    page = document[page_index]
    data = page.get_text("dict")
    lines: list[dict[str, Any]] = []
    line_no = 0
    for block in data.get("blocks") or []:
        for line in block.get("lines") or []:
            spans = line.get("spans") or []
            text = "".join(span.get("text", "") for span in spans).strip()
            if not text:
                continue
            line_no += 1
            lines.append(
                {
                    "line_no": line_no,
                    "text": text,
                    "bbox": [round(float(x), 2) for x in line.get("bbox", [])],
                }
            )
    return lines


def tables_from_page(pdf_path: Path, page_index: int) -> list[dict[str, Any]]:
    tables: list[dict[str, Any]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        page = pdf.pages[page_index]
        for table_index, table in enumerate(page.extract_tables() or []):
            rows = []
            for row_index, row in enumerate(table):
                cells = [cell if cell is not None else None for cell in row]
                row_text = " | ".join(str(cell) for cell in cells if cell not in (None, ""))
                rows.append(
                    {
                        "row_index": row_index,
                        "cells": cells,
                        "raw_text": row_text,
                    }
                )
            tables.append({"table_index": table_index, "rows": rows})
    return tables


def make_candidate(
    *,
    source_type: str,
    source_pdf: str,
    page_number: int,
    text: str,
    alias_entries: list[dict[str, Any]],
    extra: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    numbers = find_numbers(text)
    alias_hits = find_alias_hits(text, alias_entries)
    if not numbers and not alias_hits:
        return None
    candidate = {
        "source_type": source_type,
        "source_pdf": source_pdf,
        "page_number": page_number,
        "text": text,
        "numbers": numbers,
        "alias_hits": alias_hits,
    }
    if extra:
        candidate.update(extra)
    return candidate


def build_inventory(
    manifest: dict[str, Any],
    pages: list[dict[str, Any]],
    section_codes: set[str] | None,
) -> dict[str, Any]:
    alias_entries = load_alias_entries(section_codes)
    by_pdf: dict[str, fitz.Document] = {}
    candidates: list[dict[str, Any]] = []
    inventory_pages: list[dict[str, Any]] = []
    target_hit_counts: dict[str, int] = defaultdict(int)

    for page in pages:
        pdf_path = Path(page["source_pdf_path"])
        page_index = int(page["page_index"])
        source_pdf = page["source_pdf"]
        page_number = int(page["page_number"])

        lines = text_lines_from_page(pdf_path, page_index)
        tables = tables_from_page(pdf_path, page_index)
        page_candidates: list[dict[str, Any]] = []

        for line in lines:
            candidate = make_candidate(
                source_type="text_line",
                source_pdf=source_pdf,
                page_number=page_number,
                text=line["text"],
                alias_entries=alias_entries,
                extra={"line_no": line["line_no"], "bbox": line["bbox"]},
            )
            if candidate:
                page_candidates.append(candidate)

        for table in tables:
            for row in table["rows"]:
                candidate = make_candidate(
                    source_type="pdfplumber_table_row",
                    source_pdf=source_pdf,
                    page_number=page_number,
                    text=row["raw_text"],
                    alias_entries=alias_entries,
                    extra={
                        "table_index": table["table_index"],
                        "row_index": row["row_index"],
                        "cells": row["cells"],
                    },
                )
                if candidate:
                    page_candidates.append(candidate)

        for candidate_index, candidate in enumerate(page_candidates):
            candidate["candidate_id"] = f"{source_pdf}:{page_number}:candidate_{candidate_index + 1:03d}"
            for hit in candidate["alias_hits"]:
                target_hit_counts[hit["target_code"]] += 1
        candidates.extend(page_candidates)

        inventory_pages.append(
            {
                "source_pdf": source_pdf,
                "page_number": page_number,
                "page_title_guess": page.get("title_guess"),
                "text_chars": page.get("text_chars"),
                "text_lines_count": len(lines),
                "tables_count": len(tables),
                "table_rows_count": sum(len(table["rows"]) for table in tables),
                "candidates_count": len(page_candidates),
                "image_path": page.get("image_path"),
                "text_path": page.get("text_path"),
            }
        )

    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project_code": manifest.get("project_code"),
        "section_codes": sorted(section_codes) if section_codes else None,
        "method": {
            "text_lines": "PyMuPDF page.get_text('dict')",
            "tables": "pdfplumber page.extract_tables()",
            "alias_dictionary": "pack/data/target_aliases_ru.yaml",
            "decision_policy": "inventory does not choose final calculator values",
        },
        "pages": inventory_pages,
        "target_hit_counts": dict(sorted(target_hit_counts.items())),
        "candidates": candidates,
    }


def render_markdown(inventory: dict[str, Any]) -> str:
    lines = [
        "# Page Inventory",
        "",
        f"Project: `{inventory.get('project_code')}`",
        f"Sections: `{inventory.get('section_codes')}`",
        "",
        "## Pages",
        "",
    ]
    for page in inventory.get("pages") or []:
        lines.append(
            f"- `{page['source_pdf']}:{page['page_number']}` — "
            f"lines: {page['text_lines_count']}, tables: {page['tables_count']}, "
            f"table rows: {page['table_rows_count']}, candidates: {page['candidates_count']}"
        )
    lines.extend(["", "## Target Hits", ""])
    for target_code, count in (inventory.get("target_hit_counts") or {}).items():
        lines.append(f"- `{target_code}`: {count}")
    lines.extend(["", "## Candidates", ""])
    for candidate in inventory.get("candidates") or []:
        hits = ", ".join(hit["target_code"] for hit in candidate.get("alias_hits") or []) or "-"
        nums = ", ".join(num["raw"] for num in candidate.get("numbers") or []) or "-"
        lines.append(f"### {candidate['candidate_id']}")
        lines.append(f"- source_type: `{candidate['source_type']}`")
        lines.append(f"- aliases: {hits}")
        lines.append(f"- numbers: {nums}")
        lines.append("")
        lines.append(candidate["text"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--page-ref", action="append", help="Use 'source.pdf:23'. If omitted, all pages are used.")
    parser.add_argument("--section-code", action="append", help="Limit alias hits to selected section codes.")
    args = parser.parse_args()

    manifest = read_json(args.manifest)
    pages = select_manifest_pages(manifest, args.page_ref)
    section_codes = set(args.section_code or []) or None
    inventory = build_inventory(manifest, pages, section_codes)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.out_dir / "page_inventory.json"
    md_path = args.out_dir / "page_inventory.md"
    write_json(json_path, inventory)
    md_path.write_text(render_markdown(inventory), encoding="utf-8")

    print(f"pages: {len(inventory['pages'])}")
    print(f"candidates: {len(inventory['candidates'])}")
    print(f"inventory -> {json_path}")
    print(f"markdown -> {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
