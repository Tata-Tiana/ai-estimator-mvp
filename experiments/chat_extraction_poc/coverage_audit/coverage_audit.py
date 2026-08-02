"""Coverage audit for a chat-extraction run.

Compares the full list of expected targets/groups in calculator_targets_compact.json (the live
source under experiments/chat_extraction_poc/data/, not the static copy kept in this folder for
reference) against a real extraction_output.json, per section. Finds targets/groups the model never
mentioned anywhere at all (not in found, not in missing, not in needs_review) — a gap
validate_claude_extraction.py does not check, since it only validates the quality of items that are
already present.

Does not fix or reinterpret anything, only reports.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
LIVE_TARGETS_PATH = HERE.parent / "data" / "calculator_targets_compact.json"

OPTIONAL_IF_PRESENT: dict[str, dict[str, str]] = {
    "earthworks": {
        "pit_items": "Optional detail group: only needed when the project gives pit/foundation excavation as separate item rows.",
        "sand_items": "Optional detail group: only needed when the project gives sand volumes as separate item rows.",
    },
    "foundation_slab": {
        "column_footing_items": "Optional future/detail group: only needed when the project has column footings below zero.",
        "foundation_wall_items": "Optional future/detail group: only needed when the project has foundation/rostverк walls below zero.",
    },
    "floor_slab_1": {
        "slab_zones": "Optional alternative input: only needed when the project gives floor-slab concrete by zones with no ready total.",
    },
    "load_bearing_walls_lintels": {
        "vent_chimney_cladding_segments": "Optional detail group: only needed when the project has gas-block cladding around vent/chimney shafts.",
    },
    "schiedel_vent_channels": {
        "schiedel_masonry_gas_block_items": "Optional detail group: only needed when the Schiedel/vent section has separate gas-block masonry rows.",
    },
}

DIAGNOSTIC_OR_FUTURE: dict[str, dict[str, str]] = {
    "load_bearing_walls_lintels": {
        "lintel_groove_rebar_items": "Diagnostic/future group: captures groove lintel rebar for later logic; current calculator does not require it.",
    },
}


def classify_never_mentioned(section_code: str, code: str) -> dict[str, str]:
    optional_note = OPTIONAL_IF_PRESENT.get(section_code, {}).get(code)
    if optional_note:
        return {"code": code, "severity": "optional_absent", "note": optional_note}
    diagnostic_note = DIAGNOSTIC_OR_FUTURE.get(section_code, {}).get(code)
    if diagnostic_note:
        return {"code": code, "severity": "legacy_ignored", "note": diagnostic_note}
    return {
        "code": code,
        "severity": "blocker_or_schema_gap",
        "note": "Expected by calculator_targets_compact.json but not mentioned in found/missing/needs_review.",
    }


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_codes(items: list[Any]) -> set[str]:
    codes: set[str] = set()
    for item in items:
        if isinstance(item, str):
            codes.add(item)
        elif isinstance(item, dict):
            code = item.get("group_code") or item.get("target_code")
            if code:
                codes.add(code)
    return codes


def audit(targets_schema: dict, extraction: dict) -> list[dict[str, Any]]:
    schema_by_section = {s["section_code"]: s for s in targets_schema["sections"]}
    extraction_sections = extraction.get("sections") or {}

    results: list[dict[str, Any]] = []
    for section_code in sorted(set(schema_by_section) | set(extraction_sections)):
        schema_sec = schema_by_section.get(section_code)
        extraction_sec = extraction_sections.get(section_code)

        if schema_sec is None:
            results.append(
                {
                    "section_code": section_code,
                    "status": "unknown_section",
                    "note": "section present in extraction JSON but not in calculator_targets_compact.json (typo in section_code?)",
                }
            )
            continue

        expected_targets = {t["code"] for t in schema_sec.get("targets", [])}
        expected_groups = {g["group_code"] for g in schema_sec.get("extract_groups", [])}
        expected_all = expected_targets | expected_groups

        if extraction_sec is None:
            results.append(
                {
                    "section_code": section_code,
                    "status": "section_missing_from_extraction",
                    "expected_total": len(expected_all),
                    "never_mentioned": sorted(expected_all),
                }
            )
            continue

        found_codes = collect_codes(extraction_sec.get("found") or [])
        missing_codes = collect_codes(extraction_sec.get("missing") or [])
        needs_review_codes = collect_codes(extraction_sec.get("needs_review") or [])
        mentioned = found_codes | missing_codes | needs_review_codes

        never_mentioned = sorted(expected_all - mentioned)
        classified_never_mentioned = [classify_never_mentioned(section_code, code) for code in never_mentioned]
        severity_counts: dict[str, int] = {}
        for item in classified_never_mentioned:
            severity_counts[item["severity"]] = severity_counts.get(item["severity"], 0) + 1
        unknown_codes = sorted(mentioned - expected_all)
        has_blocking_gap = bool(severity_counts.get("blocker_or_schema_gap")) or bool(unknown_codes)

        results.append(
            {
                "section_code": section_code,
                "status": "ok" if not never_mentioned and not unknown_codes else ("gaps_found" if has_blocking_gap else "optional_only"),
                "expected_total": len(expected_all),
                "found_count": len(found_codes & expected_all),
                "missing_count": len(missing_codes & expected_all),
                "needs_review_count": len(needs_review_codes & expected_all),
                "never_mentioned": never_mentioned,
                "classified_never_mentioned": classified_never_mentioned,
                "severity_counts": severity_counts,
                "never_mentioned_count": len(never_mentioned),
                "unknown_codes_used": unknown_codes,
            }
        )
    return results


def render_report(results: list[dict[str, Any]], extraction_path: Path) -> str:
    lines = ["# Coverage audit — chat-extraction completeness", ""]
    lines.append(f"Extraction file: `{extraction_path}`")
    lines.append("")

    total_expected = sum(r.get("expected_total", 0) for r in results)
    total_never_mentioned = sum(r.get("never_mentioned_count", 0) for r in results)
    severity_totals: dict[str, int] = {}
    for r in results:
        for severity, count in (r.get("severity_counts") or {}).items():
            severity_totals[severity] = severity_totals.get(severity, 0) + count
    lines.append(
        f"Sections checked: {len(results)}. Total expected targets/groups: {total_expected}. "
        f"Never mentioned anywhere: {total_never_mentioned}."
    )
    if severity_totals:
        lines.append(
            "Never-mentioned severity: "
            + ", ".join(f"{severity}={count}" for severity, count in sorted(severity_totals.items()))
            + "."
        )
    lines.append("")

    for r in results:
        lines.append(f"## {r['section_code']} — {r['status']}")
        lines.append("")
        if r["status"] == "unknown_section":
            lines.append(f"- {r['note']}")
            lines.append("")
            continue
        if r["status"] == "section_missing_from_extraction":
            lines.append(f"- Entire section absent from extraction JSON. Expected {r['expected_total']} targets/groups, none present.")
            for code in r["never_mentioned"]:
                lines.append(f"  - `{code}`")
            lines.append("")
            continue

        lines.append(
            f"- Expected: {r['expected_total']} | found: {r['found_count']} | "
            f"missing: {r['missing_count']} | needs_review: {r['needs_review_count']} | "
            f"**never mentioned: {r['never_mentioned_count']}**"
        )
        if r["classified_never_mentioned"]:
            lines.append("")
            lines.append("Never mentioned anywhere (not found/missing/needs_review), classified:")
            for item in r["classified_never_mentioned"]:
                lines.append(f"  - `{item['code']}` — {item['severity']}: {item['note']}")
        if r["unknown_codes_used"]:
            lines.append("")
            lines.append("Codes used by the model that aren't in the current schema (typo, or schema drifted):")
            for code in r["unknown_codes_used"]:
                lines.append(f"  - `{code}`")
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Path to a real extraction_output.json")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument(
        "--targets",
        type=Path,
        default=LIVE_TARGETS_PATH,
        help="Path to calculator_targets_compact.json (defaults to the live copy under data/, not the static snapshot in this folder)",
    )
    args = parser.parse_args()

    targets_schema = load_json(args.targets)
    extraction = load_json(args.input)

    results = audit(targets_schema, extraction)
    report = render_report(results, args.input)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")

    total_expected = sum(r.get("expected_total", 0) for r in results)
    total_never_mentioned = sum(r.get("never_mentioned_count", 0) for r in results)
    print(f"audited: {len(results)} sections, {total_expected} expected, {total_never_mentioned} never mentioned -> {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
