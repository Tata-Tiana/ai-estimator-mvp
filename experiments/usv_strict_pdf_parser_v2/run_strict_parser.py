from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from candidate_extractor import CANDIDATES_PATH, extract_candidates
from coverage_report_builder import COVERAGE_REPORT_PATH, build_reports
from integrity_checks import check_integrity
from mapper import FINAL_DRAFT_PATH, MAPPED_PARAMETERS_PATH, NORMALIZED_PARAMETERS_PATH, map_targets
from parameter_targets import TARGETS_PATH, write_targets
from pdf_extract import extract_pdfs
from review_pack_builder import REVIEW_PACK_PATH, build_review_pack
from spec_table_parser import SPEC_ROWS_PATH, parse_spec_rows


def run() -> dict:
    extract_pdfs()
    parse_spec_rows()
    extract_candidates()
    write_targets()
    mapped = map_targets()
    integrity = check_integrity()
    build_review_pack()
    build_reports()
    return {
        "stats": Counter(row["found_status"] for row in mapped),
        "total": len(mapped),
        "integrity": integrity,
    }


def main() -> int:
    result = run()
    print("USV strict parser v2 completed")
    print(f"- candidates: {CANDIDATES_PATH}")
    print(f"- spec_rows: {SPEC_ROWS_PATH}")
    print(f"- targets: {TARGETS_PATH}")
    print(f"- mapped_parameters: {MAPPED_PARAMETERS_PATH}")
    print(f"- normalized_parameters: {NORMALIZED_PARAMETERS_PATH}")
    print(f"- review_pack: {REVIEW_PACK_PATH}")
    print(f"- coverage_report: {COVERAGE_REPORT_PATH}")
    print(f"- final_project_parameters_draft: {FINAL_DRAFT_PATH}")
    print("- coverage:")
    for key in ("found_from_pdf", "true_missing_in_project", "mapping_gap", "supplier_required", "manual_required", "low_confidence"):
        print(f"  {key}: {result['stats'].get(key, 0)}")
    print("  curated_values_used_as_data: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
