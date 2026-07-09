"""A6.0: dual-channel comparison — vision extraction vs validated ground
truth (primary) vs old hardcoded text parser raw output (secondary).

Only compares the earthworks parameters we actually have a
human-validated reference for (experiments/earthworks_calculator/cases/
usv_yusupovo_village/input.json). Everything else the vision model finds
is listed separately as "other findings" — not scored, just visibility
into what else showed up across the 8 estimate sections.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

TOLERANCE = 0.10

TARGETS = [
    {
        "parameter": "pit_area_m2",
        "unit": "m2",
        "keywords": ["котлован"],
        "parser_path": None,
    },
    {
        "parameter": "trench_volume_m3",
        "unit": "m3",
        "special": "trench_routes_total",
        "parser_path": ("trenches", "trench_volume_total_m3"),
    },
    {
        "parameter": "sand_base_volume_m3",
        "unit": "m3",
        "keywords": ["песок", "песчан"],
        "parser_path": ("sand", "sand_volume_m3"),
    },
    {
        "parameter": "geotextile_area_m2",
        "unit": "m2",
        "keywords": ["геотекстил"],
        "parser_path": None,
    },
    {
        "parameter": "geotextile_laying_area_m2",
        "unit": "m2",
        "keywords": ["геотекстил", "укладк"],
        "parser_path": None,
    },
    {
        "parameter": "communications_length_m",
        "unit": "linear_m",
        "special": "pipe_items_total",
        "parser_path": ("communications", "communications_length_m"),
    },
    {
        "parameter": "manual_excavation_quantity_for_estimate_m3",
        "unit": "m3",
        "keywords": ["ручн", "разработк"],
        "parser_path": None,
    },
]


def approx_equal(a: float, b: float, tolerance: float = TOLERANCE) -> bool:
    if b == 0:
        return abs(a) < 1e-6
    return abs(a - b) / abs(b) <= tolerance


def get_path(data: dict, path: tuple | None) -> Any:
    if path is None:
        return None
    value: Any = data
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def iter_page_extractions(vision_data: dict):
    for page in vision_data.get("pages", []):
        extracted = page.get("extracted")
        if extracted:
            yield page["source_pdf"], page["page_number"], extracted


def collect_keyword_matches(vision_data: dict, keywords: list[str], unit: str) -> list[dict]:
    matches = []
    keywords_lower = [k.lower() for k in keywords]
    for source_pdf, page_number, extracted in iter_page_extractions(vision_data):
        for group in ("scalar_values", "materials"):
            for item in extracted.get(group, []) or []:
                haystack = " ".join(
                    str(item.get(field, "")) for field in ("parameter_hint", "name", "raw_text")
                ).lower()
                if not any(k in haystack for k in keywords_lower):
                    continue
                if item.get("value") is None and item.get("quantity") is None:
                    continue
                matches.append({
                    "source_pdf": source_pdf,
                    "page_number": page_number,
                    "value": item.get("value", item.get("quantity")),
                    "unit": item.get("unit"),
                    "normalized_unit": item.get("normalized_unit"),
                    "raw_text": item.get("raw_text"),
                    "confidence": item.get("confidence"),
                    "needs_review": item.get("needs_review", False),
                })
    return matches


def collect_trench_routes_total(vision_data: dict) -> tuple[float | None, list[dict], bool]:
    routes_by_name: dict[str, list[dict]] = {}
    for source_pdf, page_number, extracted in iter_page_extractions(vision_data):
        for table in extracted.get("tables", []) or []:
            if table.get("table_type") != "trench_routes":
                continue
            for item in table.get("items") or []:
                name = (item.get("name") or "?").strip().lower()
                routes_by_name.setdefault(name, []).append({
                    "source_pdf": source_pdf, "page_number": page_number,
                    "volume_m3": item.get("volume_m3"), "raw_name": item.get("name"),
                })
    if not routes_by_name:
        return None, [], False

    conflict = False
    total = 0.0
    details = []
    for name, occurrences in routes_by_name.items():
        volumes = {o["volume_m3"] for o in occurrences if o["volume_m3"] is not None}
        if len(volumes) > 1:
            conflict = True
        if volumes:
            total += max(volumes)
        details.extend(occurrences)
    return (round(total, 3) if details else None), details, conflict


def collect_pipe_items_total(vision_data: dict) -> tuple[float | None, list[dict]]:
    items_found = []
    total = 0.0
    any_usable = False
    for source_pdf, page_number, extracted in iter_page_extractions(vision_data):
        for table in extracted.get("tables", []) or []:
            if table.get("table_type") != "pipe_items":
                continue
            for item in table.get("items") or []:
                piece_length_m = item.get("piece_length_m")
                quantity_pcs = item.get("quantity_pcs")
                contribution = None
                if piece_length_m is not None and quantity_pcs is not None:
                    contribution = piece_length_m * quantity_pcs
                    total += contribution
                    any_usable = True
                items_found.append({
                    "source_pdf": source_pdf, "page_number": page_number,
                    "name": item.get("name"), "diameter_mm": item.get("diameter_mm"),
                    "piece_length_m": piece_length_m, "quantity_pcs": quantity_pcs,
                    "contribution_m": contribution,
                })
    return (round(total, 3) if any_usable else None), items_found


def resolve_target(target: dict, vision_data: dict) -> dict:
    result: dict[str, Any] = {"parameter": target["parameter"], "unit": target["unit"], "notes": []}

    if target.get("special") == "trench_routes_total":
        vision_value, details, conflict = collect_trench_routes_total(vision_data)
        result["vision_value"] = vision_value
        result["vision_detail"] = details
        if conflict:
            result["notes"].append("same route name reported with different volumes on different pages")
    elif target.get("special") == "pipe_items_total":
        vision_value, details = collect_pipe_items_total(vision_data)
        result["vision_value"] = vision_value
        result["vision_detail"] = details
        if details and vision_value is None:
            result["notes"].append("pipe items found but missing piece_length_m/quantity_pcs, could not sum")
    else:
        matches = collect_keyword_matches(vision_data, target["keywords"], target["unit"])
        distinct_values = {m["value"] for m in matches}
        result["vision_detail"] = matches
        if len(distinct_values) == 1:
            result["vision_value"] = next(iter(distinct_values))
        elif len(distinct_values) > 1:
            result["vision_value"] = None
            result["notes"].append(f"{len(distinct_values)} conflicting candidate values found: {sorted(distinct_values)}")
        else:
            result["vision_value"] = None

    if any(m.get("needs_review") for m in result.get("vision_detail", []) if isinstance(m, dict) and "needs_review" in m):
        result["notes"].append("at least one contributing candidate flagged needs_review by validate step")

    return result


def classify_status(vision_value, parser_value, validated_value) -> str:
    if vision_value is None and parser_value is None:
        return "missing"
    if vision_value is None:
        return "parser_only"
    if parser_value is None:
        return "vision_only"
    if validated_value is not None:
        vision_ok = approx_equal(vision_value, validated_value)
        parser_ok = approx_equal(parser_value, validated_value)
        if vision_ok and parser_ok:
            return "agree"
        if vision_ok and not parser_ok:
            return "vision_closer_to_reference"
        if parser_ok and not vision_ok:
            return "parser_closer_to_reference"
        return "conflict"
    return "agree" if approx_equal(vision_value, parser_value) else "conflict"


def build_comparison(vision_data: dict, validated_input: dict, parser_earthworks: dict) -> list[dict]:
    rows = []
    for target in TARGETS:
        resolved = resolve_target(target, vision_data)
        validated_value = validated_input.get(target["parameter"])
        parser_value = get_path(parser_earthworks, target.get("parser_path"))
        status = classify_status(resolved["vision_value"], parser_value, validated_value)
        rows.append({
            **resolved,
            "validated_reference_value": validated_value,
            "text_parser_value": parser_value,
            "status": status,
        })
    return rows


def collect_other_findings(vision_data: dict, matched_targets: list[dict], limit: int = 40) -> list[dict]:
    matched_raw_texts = set()
    for row in matched_targets:
        for m in row.get("vision_detail", []):
            if isinstance(m, dict) and m.get("raw_text"):
                matched_raw_texts.add(m["raw_text"])

    seen = set()
    others = []
    for source_pdf, page_number, extracted in iter_page_extractions(vision_data):
        for group in ("scalar_values", "materials"):
            for item in extracted.get(group, []) or []:
                raw_text = item.get("raw_text")
                key = (item.get("section"), item.get("name", item.get("parameter_hint")), item.get("value", item.get("quantity")), item.get("unit"))
                if raw_text in matched_raw_texts or key in seen:
                    continue
                seen.add(key)
                others.append({
                    "source_pdf": source_pdf, "page_number": page_number,
                    "section": item.get("section"),
                    "name": item.get("name", item.get("parameter_hint")),
                    "value": item.get("value", item.get("quantity")),
                    "unit": item.get("unit"),
                })
                if len(others) >= limit:
                    return others
    return others


def render_report(rows: list[dict], other_findings: list[dict], vision_data: dict) -> str:
    lines = ["# A6.0 — Vision PDF extraction POC: comparison report", ""]
    lines.append(f"Model: `{vision_data.get('model')}`. Pages processed: {vision_data.get('page_count')}.")
    status_counts = vision_data.get("status_counts")
    if status_counts:
        lines.append(f"Per-page validation status: {status_counts}.")
    lines.append("")
    lines.append(
        "Primary reference = human-validated `input.json` "
        "(`experiments/earthworks_calculator/cases/usv_yusupovo_village/input.json`, "
        "`validated_with_elena: true`). Secondary reference = old hardcoded "
        "text-parser raw output (`earthworks_parser.py`), known to be project-specific "
        "and non-generalizing to other projects (see A5.1a report)."
    )
    lines.append("")
    lines.append("## Earthworks parameters")
    lines.append("")
    lines.append("| parameter | unit | validated (truth) | text parser | vision | status | notes |")
    lines.append("|---|---|---|---|---|---|---|")
    for row in rows:
        notes = "; ".join(row["notes"]) if row["notes"] else ""
        lines.append(
            f"| {row['parameter']} | {row['unit']} | {row['validated_reference_value']} | "
            f"{row['text_parser_value']} | {row['vision_value']} | {row['status']} | {notes} |"
        )
    lines.append("")

    status_summary: dict[str, int] = {}
    for row in rows:
        status_summary[row["status"]] = status_summary.get(row["status"], 0) + 1
    lines.append(f"Summary: {status_summary}")
    lines.append("")

    lines.append("## Detail: trench routes (vision)")
    lines.append("")
    trench_row = next((r for r in rows if r["parameter"] == "trench_volume_m3"), None)
    if trench_row and trench_row.get("vision_detail"):
        lines.append("| source_pdf | page | route name | volume_m3 |")
        lines.append("|---|---|---|---|")
        for d in trench_row["vision_detail"]:
            lines.append(f"| {d['source_pdf']} | {d['page_number']} | {d['raw_name']} | {d['volume_m3']} |")
    else:
        lines.append("(no trench_routes tables found by vision)")
    lines.append("")

    lines.append("## Detail: pipe items (vision)")
    lines.append("")
    comms_row = next((r for r in rows if r["parameter"] == "communications_length_m"), None)
    if comms_row and comms_row.get("vision_detail"):
        lines.append("| source_pdf | page | name | diameter_mm | piece_length_m | quantity_pcs | contribution_m |")
        lines.append("|---|---|---|---|---|---|---|")
        for d in comms_row["vision_detail"]:
            lines.append(
                f"| {d['source_pdf']} | {d['page_number']} | {d['name']} | {d['diameter_mm']} | "
                f"{d['piece_length_m']} | {d['quantity_pcs']} | {d['contribution_m']} |"
            )
    else:
        lines.append("(no pipe_items tables found by vision)")
    lines.append("")

    lines.append("## Other findings (not matched to a scored target, informational only)")
    lines.append("")
    if other_findings:
        lines.append("| source_pdf | page | section | name | value | unit |")
        lines.append("|---|---|---|---|---|---|")
        for o in other_findings:
            lines.append(
                f"| {o['source_pdf']} | {o['page_number']} | {o['section']} | {o['name']} | {o['value']} | {o['unit']} |"
            )
    else:
        lines.append("(none)")
    lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vision-json", type=Path, required=True)
    parser.add_argument("--validated-input", type=Path, required=True)
    parser.add_argument("--parser-earthworks-json", type=Path, required=True)
    parser.add_argument("--out-report", type=Path, required=True)
    args = parser.parse_args()

    vision_data = json.loads(args.vision_json.read_text(encoding="utf-8"))
    validated_input = json.loads(args.validated_input.read_text(encoding="utf-8"))
    parser_earthworks = json.loads(args.parser_earthworks_json.read_text(encoding="utf-8"))

    rows = build_comparison(vision_data, validated_input, parser_earthworks)
    other_findings = collect_other_findings(vision_data, rows)
    report = render_report(rows, other_findings, vision_data)

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text(report, encoding="utf-8")
    print(f"report written -> {args.out_report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
