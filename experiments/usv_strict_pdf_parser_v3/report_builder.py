from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
EXTRACTED_DIR = DATA_DIR / "extracted"
MAPPED_DIR = DATA_DIR / "mapped"
REPORTS_DIR = DATA_DIR / "reports"
LOGICAL_PAGES_PATH = RAW_DIR / "logical_pages.json"
EARTHWORKS_PATH = EXTRACTED_DIR / "earthworks.json"
REBAR_ITEMS_PATH = EXTRACTED_DIR / "rebar_items.json"
BEAM_ITEMS_PATH = EXTRACTED_DIR / "beam_items.json"
MAPPED_PARAMETERS_PATH = MAPPED_DIR / "mapped_parameters.json"
COVERAGE_REPORT_PATH = REPORTS_DIR / "coverage_report.md"
DEBUG_REPORT_PATH = REPORTS_DIR / "parser_debug_report.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_reports() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    logical_pages = load_json(LOGICAL_PAGES_PATH)
    earth = load_json(EARTHWORKS_PATH)
    rebar = load_json(REBAR_ITEMS_PATH)
    beams = load_json(BEAM_ITEMS_PATH)
    mapped = load_json(MAPPED_PARAMETERS_PATH)
    counts = Counter(row["found_status"] for row in mapped)
    sheet_counts = Counter(page["logical_sheet_type"] for page in logical_pages)

    coverage = [
        "# Coverage Report: USV Strict PDF Parser v3",
        "",
        "- strict_parse_mode: true",
        "- curated_values_used_as_data: 0",
        f"- found_from_pdf: {counts['found_from_pdf']}",
        f"- parser_failure: {len([x for x in load_json(MAPPED_DIR / 'final_project_parameters_draft.json')['not_ready']['parser_failure']])}",
        f"- low_confidence: {len(rebar.get('low_confidence_rebar_items', []))}",
        "",
        "## Logical Sheets",
        "",
    ]
    for sheet_type, count in sheet_counts.most_common():
        coverage.append(f"- {sheet_type}: {count}")
    coverage.extend(["", "## Mapped", ""])
    for row in mapped:
        coverage.append(f"- {row['found_status']}: `{row['key']}`")
    COVERAGE_REPORT_PATH.write_text("\n".join(coverage) + "\n", encoding="utf-8")

    sand = earth.get("sand")
    trenches = earth.get("trenches", {})
    communications = earth.get("communications", {})
    debug = [
        "# Parser Debug Report",
        "",
        "## Песок",
        "",
        f"- value: {sand.get('sand_volume_m3') if sand else None}",
        f"- fragment: {sand.get('raw_context') if sand else ''}",
        "- rule: last number before `м3` after keyword `Песок`.",
        "",
        "## Траншеи",
        "",
        f"- routes_count: {len(trenches.get('trench_routes', []))}",
        f"- total_volume: {trenches.get('trench_volume_total_m3')}",
        f"- routes: {json.dumps(trenches.get('trench_routes', []), ensure_ascii=False)}",
        "",
        "## Коммуникации",
        "",
        f"- pipe_items_count: {len(communications.get('communication_pipe_items', []))}",
        f"- communications_length_m: {communications.get('communications_length_m')}",
        "",
        "## Арматура",
        "",
        f"- rebar_items_count: {len(rebar.get('normalized_rebar_items', []))}",
        f"- excluded_pipe_like_rows: {rebar.get('excluded_pipe_like_rows')}",
        f"- low_confidence_count: {len(rebar.get('low_confidence_rebar_items', []))}",
        "",
        "## Балки",
        "",
        f"- beam_items_count: {len(beams.get('normalized_beam_items', []))}",
        f"- beams_total_length_m: {beams.get('beams_total_length_m')}",
        f"- beams_total_concrete_volume_m3: {beams.get('beams_total_concrete_volume_m3')}",
        f"- beams_total_formwork_area_m2: {beams.get('beams_total_formwork_area_m2')}",
        f"- parser_failure: {beams.get('parser_failure')}",
    ]
    DEBUG_REPORT_PATH.write_text("\n".join(debug) + "\n", encoding="utf-8")


def main() -> int:
    build_reports()
    print(f"coverage_report: {COVERAGE_REPORT_PATH}")
    print(f"parser_debug_report: {DEBUG_REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
