"""A6.1: compare a Claude-chat extraction JSON against the human-validated
earthworks input.json for usv_yusupovo_village.

Only run this AFTER extraction is done and validate_claude_extraction.py
has been run. The validated input.json must never be shown to Claude
during extraction (see README.md) or this comparison is meaningless.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MATCH_TOLERANCE = 0.10
CLOSE_TOLERANCE = 0.25

EARTHWORKS_SCALAR_TARGETS = [
    {"target_code": "pit_area_m2", "validated_key": "pit_area_m2", "unit": "m2"},
    {"target_code": "pit_excavation_depth_m", "validated_key": "pit_excavation_depth_m", "unit": "m"},
    {"target_code": "geotextile_area_m2", "validated_key": "geotextile_area_m2", "unit": "m2"},
    {"target_code": "geotextile_laying_area_m2", "validated_key": "geotextile_laying_area_m2", "unit": "m2"},
    {"target_code": "sand_base_volume_m3", "validated_key": "sand_base_volume_m3", "unit": "m3"},
    {"target_code": "trench_volume_m3", "validated_key": "trench_volume_m3", "unit": "m3", "notes": "Only the explicit 'ИТОГО' line, if Claude found one - see trench_volume_m3_from_routes for the computed cross-check."},
    {"target_code": "communications_length_m", "validated_key": "communications_length_m", "unit": "linear_m", "notes": "Only if explicit total/general communication length exists in PDF."},
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def approx_status(claude_value, validated_value) -> str:
    if validated_value is None:
        return "no_reference"
    if claude_value is None:
        return "missing_in_claude"
    if validated_value == 0:
        return "match" if abs(claude_value) < 1e-6 else "mismatch"
    ratio = abs(claude_value - validated_value) / abs(validated_value)
    if ratio <= MATCH_TOLERANCE:
        return "match"
    if ratio <= CLOSE_TOLERANCE:
        return "close"
    return "mismatch"


def find_found_items(claude_data: dict, section_code: str) -> list[dict]:
    section = (claude_data.get("sections") or {}).get(section_code) or {}
    return section.get("found") or []


def find_by_target_code(items: list[dict], target_code: str) -> dict | None:
    for item in items:
        if item.get("target_code") == target_code and item.get("group_code") is None:
            return item
    return None


def compute_trench_volume_from_routes(items: list[dict]) -> tuple[float | None, list[dict]]:
    routes = [it for it in items if it.get("group_code") == "trench_routes" and isinstance(it.get("value"), dict)]
    if not routes:
        return None, []
    total = 0.0
    any_value = False
    for r in routes:
        v = r["value"].get("volume_m3")
        if v is not None:
            total += v
            any_value = True
    return (round(total, 3) if any_value else None), routes


def compute_communications_length_from_pipe_items(items: list[dict]) -> tuple[float | None, list[dict]]:
    pipe_items = [it for it in items if it.get("group_code") == "communications_pipe_items" and isinstance(it.get("value"), dict)]
    if not pipe_items:
        return None, []
    total = 0.0
    any_value = False
    for it in pipe_items:
        total_length_m = it["value"].get("total_length_m")
        pipe_length_m = it["value"].get("pipe_length_m")
        quantity = it["value"].get("quantity")
        if total_length_m is not None:
            total += total_length_m
            any_value = True
        elif pipe_length_m is not None and quantity is not None:
            total += pipe_length_m * quantity
            any_value = True
    return (round(total, 3) if any_value else None), pipe_items


def build_scalar_rows(claude_data: dict, validated_input: dict) -> list[dict]:
    items = find_found_items(claude_data, "earthworks")
    rows = []
    for target in EARTHWORKS_SCALAR_TARGETS:
        found = find_by_target_code(items, target["target_code"])
        claude_value = found.get("value") if found else None
        validated_value = validated_input.get(target["validated_key"])
        rows.append({
            "parameter": target["validated_key"],
            "unit": target["unit"],
            "validated_reference_value": validated_value,
            "claude_value": claude_value,
            "status": approx_status(claude_value, validated_value),
            "needs_review": bool(found.get("needs_review")) if found else False,
            "notes": target.get("notes", ""),
        })
    return rows


def build_computed_rows(claude_data: dict, validated_input: dict) -> list[dict]:
    items = find_found_items(claude_data, "earthworks")
    trench_total, routes = compute_trench_volume_from_routes(items)
    comms_total, pipe_items = compute_communications_length_from_pipe_items(items)
    rows = [
        {
            "parameter": "trench_volume_m3_from_routes (computed = sum(trench_routes.volume_m3))",
            "unit": "m3",
            "validated_reference_value": validated_input.get("trench_volume_m3"),
            "claude_value": trench_total,
            "status": approx_status(trench_total, validated_input.get("trench_volume_m3")),
            "needs_review": any(r.get("needs_review") for r in routes),
            "notes": f"{len(routes)} trench_routes items found",
        },
        {
            "parameter": "communications_length_m_from_pipe_items (computed only for comparison)",
            "unit": "linear_m",
            "validated_reference_value": validated_input.get("communications_length_m"),
            "claude_value": comms_total,
            "status": approx_status(comms_total, validated_input.get("communications_length_m")),
            "needs_review": any(r.get("needs_review") for r in pipe_items),
            "notes": f"{len(pipe_items)} communications_pipe_items found",
        },
    ]
    return rows, routes, pipe_items


def render_report(scalar_rows: list[dict], computed_rows: list[dict], routes: list[dict], pipe_items: list[dict]) -> str:
    lines = ["# A6.1 — Claude-chat extraction vs validated ЮСВ input.json", ""]
    lines.append(
        "Primary reference: human-validated `input.json` "
        "(`experiments/earthworks_calculator/cases/usv_yusupovo_village/input.json`, "
        "`validated_with_elena: true`). This file must not have been shown to Claude during extraction."
    )
    lines.append("")
    lines.append("## Scalar targets")
    lines.append("")
    lines.append("| parameter | unit | validated | claude | status | needs_review | notes |")
    lines.append("|---|---|---|---|---|---|---|")
    for row in scalar_rows:
        lines.append(
            f"| {row['parameter']} | {row['unit']} | {row['validated_reference_value']} | "
            f"{row['claude_value']} | {row['status']} | {row['needs_review']} | {row['notes']} |"
        )
    lines.append("")
    lines.append("## Computed from groups (trench_routes / communications_pipe_items)")
    lines.append("")
    lines.append("| parameter | unit | validated | claude (computed) | status | needs_review | notes |")
    lines.append("|---|---|---|---|---|---|---|")
    for row in computed_rows:
        lines.append(
            f"| {row['parameter']} | {row['unit']} | {row['validated_reference_value']} | "
            f"{row['claude_value']} | {row['status']} | {row['needs_review']} | {row['notes']} |"
        )
    lines.append("")

    lines.append("## Detail: trench_routes found by Claude")
    lines.append("")
    if routes:
        lines.append("| route_code | name | length_m | depth_m | width_m | volume_m3 | needs_review |")
        lines.append("|---|---|---|---|---|---|---|")
        for r in routes:
            v = r["value"]
            lines.append(
                f"| {v.get('route_code')} | {v.get('name')} | {v.get('length_m')} | {v.get('depth_m')} | "
                f"{v.get('width_m')} | {v.get('volume_m3')} | {r.get('needs_review')} |"
            )
    else:
        lines.append("(none found)")
    lines.append("")

    lines.append("## Detail: communications_pipe_items found by Claude")
    lines.append("")
    if pipe_items:
        lines.append("| code | name | diameter_mm | pipe_length_m | quantity | total_length_m | needs_review |")
        lines.append("|---|---|---|---|---|---|---|")
        for it in pipe_items:
            v = it["value"]
            lines.append(
                f"| {v.get('code')} | {v.get('name')} | {v.get('diameter_mm')} | {v.get('pipe_length_m')} | "
                f"{v.get('quantity')} | {v.get('total_length_m')} | {it.get('needs_review')} |"
            )
    else:
        lines.append("(none found)")
    lines.append("")

    all_statuses = [r["status"] for r in scalar_rows] + [r["status"] for r in computed_rows]
    summary: dict[str, int] = {}
    for s in all_statuses:
        summary[s] = summary.get(s, 0) + 1
    lines.append(f"## Summary: {summary}")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude-json", type=Path, required=True)
    parser.add_argument("--validated-input", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    claude_data = load_json(args.claude_json)
    validated_input = load_json(args.validated_input)

    scalar_rows = build_scalar_rows(claude_data, validated_input)
    computed_rows, routes, pipe_items = build_computed_rows(claude_data, validated_input)
    report = render_report(scalar_rows, computed_rows, routes, pipe_items)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print(f"report written -> {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
