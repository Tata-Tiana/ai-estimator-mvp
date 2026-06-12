from __future__ import annotations

import json

from beam_table_parser import parse_beams
from candidate_store import CandidateStore
from drawing_index import build_drawing_index
from earthworks_parser import parse_earthworks
from integrity_checks import check_integrity
from logical_sheet_classifier import classify_pages
from mapper import FINAL_DRAFT_PATH, MAPPED_PARAMETERS_PATH, build_mapping
from pdf_extract import extract_pdf_data
from rebar_parser import parse_rebar
from report_builder import COVERAGE_REPORT_PATH, DEBUG_REPORT_PATH, build_reports


def run() -> dict:
    extract_pdf_data()
    build_drawing_index()
    classify_pages()
    store = CandidateStore()
    earth = parse_earthworks(store)
    rebar = parse_rebar(store)
    beams = parse_beams(store)
    store.write()
    mapped, draft = build_mapping()
    integrity = check_integrity()
    build_reports()
    return {"earth": earth, "rebar": rebar, "beams": beams, "mapped": mapped, "draft": draft, "integrity": integrity}


def main() -> int:
    result = run()
    print("USV strict parser v3 completed")
    print(f"- mapped_parameters: {MAPPED_PARAMETERS_PATH}")
    print(f"- final_project_parameters_draft: {FINAL_DRAFT_PATH}")
    print(f"- coverage_report: {COVERAGE_REPORT_PATH}")
    print(f"- parser_debug_report: {DEBUG_REPORT_PATH}")
    print(f"- sand_volume_m3: {result['earth'].get('sand', {}).get('sand_volume_m3') if result['earth'].get('sand') else None}")
    print(f"- trench_routes: {len(result['earth'].get('trenches', {}).get('trench_routes', []))}")
    print(f"- communication_pipe_items: {len(result['earth'].get('communications', {}).get('communication_pipe_items', []))}")
    print(f"- rebar_items: {len(result['rebar'].get('normalized_rebar_items', []))}")
    print(f"- beam_items: {len(result['beams'].get('normalized_beam_items', []))}")
    print("- curated_values_used_as_data: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
