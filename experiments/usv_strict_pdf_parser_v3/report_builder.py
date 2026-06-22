from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any

import parser_paths


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_reports() -> None:
    parser_paths.reports_dir().mkdir(parents=True, exist_ok=True)
    logical_pages = load_json(parser_paths.logical_pages_path())
    earth = load_json(parser_paths.earthworks_path())
    rebar = load_json(parser_paths.rebar_items_path())
    beams = load_json(parser_paths.beam_items_path())
    mapped = load_json(parser_paths.mapped_parameters_path())
    counts = Counter(row["found_status"] for row in mapped)
    sheet_counts = Counter(page["logical_sheet_type"] for page in logical_pages)

    coverage = [
        "# Coverage Report: USV Strict PDF Parser v3",
        "",
        "- strict_parse_mode: true",
        "- curated_values_used_as_data: 0",
        f"- found_from_pdf: {counts['found_from_pdf']}",
        f"- parser_failure: {len([x for x in load_json(parser_paths.final_draft_path())['not_ready']['parser_failure']])}",
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
    parser_paths.coverage_report_path().write_text("\n".join(coverage) + "\n", encoding="utf-8")

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
    parser_paths.debug_report_path().write_text("\n".join(debug) + "\n", encoding="utf-8")


def main() -> int:
    build_reports()
    print(f"coverage_report: {parser_paths.coverage_report_path()}")
    print(f"parser_debug_report: {parser_paths.debug_report_path()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
