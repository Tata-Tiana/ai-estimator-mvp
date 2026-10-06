from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from candidate_store import CandidateStore
from spec_row_parser import NUMBER_RE, parse_number, table_row_objects

import parser_paths


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_beams(store: CandidateStore) -> dict[str, Any]:
    logical_pages = load_json(parser_paths.logical_pages_path())
    tables = load_json(parser_paths.tables_path())
    rows = table_row_objects(tables, logical_pages)
    beam_rows = []
    for row in rows:
        if row["logical_sheet_type"] != "floor_slab_1_spec":
            continue
        cells = row.get("row") or []
        if cells and re.fullmatch(r"\s*Б-\d\s*", cells[0], flags=re.IGNORECASE):
            beam_rows.append(row)
    items = []
    for row in beam_rows:
        text = row["row_text"]
        code_match = re.search(r"\bБ-\d\b", text, re.IGNORECASE)
        cells = row.get("row") or []
        nums = [parse_number(cell) for cell in cells[1:] if re.fullmatch(NUMBER_RE, cell.strip())]
        if not code_match or len(nums) < 3:
            continue
        evidence = store.add(
            source_pdf=row["source_pdf"],
            physical_page_number=row["physical_page_number"],
            drawing_sheet_number=row.get("drawing_sheet_number", ""),
            logical_sheet_title=row.get("logical_sheet_title", ""),
            logical_sheet_type=row["logical_sheet_type"],
            section_code="floor_slab_1",
            candidate_type="beam_table_row",
            raw_label=code_match.group(0),
            value=nums,
            unit="mixed",
            raw_context=text,
            confidence="medium",
            extraction_method="beam_row_numbers",
        )
        items.append(
            {
                "code": code_match.group(0).upper(),
                "raw_numbers": nums,
                "length_m": nums[0] if len(nums) > 0 else None,
                "width_m": nums[1] if len(nums) > 1 else None,
                "height_m": nums[2] if len(nums) > 2 else None,
                "concrete_volume_m3": nums[3] if len(nums) > 3 else None,
                "formwork_area_m2": nums[4] if len(nums) > 4 else None,
                "source_pdf": row["source_pdf"],
                "physical_page_number": row["physical_page_number"],
                "logical_sheet_title": row.get("logical_sheet_title", ""),
                "raw_context": text,
                "confidence": "medium",
                "evidence_id": evidence["evidence_id"],
            }
        )
    result = {
        "normalized_beam_items": items,
        "beams_total_length_m": sum(item["length_m"] or 0 for item in items),
        "beams_total_concrete_volume_m3": sum(item["concrete_volume_m3"] or 0 for item in items),
        "beams_total_formwork_area_m2": sum(item["formwork_area_m2"] or 0 for item in items),
        "parser_failure": None if items else "Beam table was not recognized as structured B-1/B-2/B-3 rows.",
    }
    parser_paths.beam_items_path().write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    store = CandidateStore()
    result = parse_beams(store)
    store.write()
    print(f"beam_items: {parser_paths.beam_items_path()}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
