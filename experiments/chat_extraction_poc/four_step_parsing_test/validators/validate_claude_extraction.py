"""A6.1: deterministic checks on a Claude-chat extraction JSON.

Does not fix or reinterpret anything, only reports. Run this before
compare_with_validated_input.py so obviously broken items (missing
sources, unit mismatches, arithmetic that doesn't add up) are visible
before comparing against the ground truth.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
VOLUME_MISMATCH_TOLERANCE = 0.20
TOTALS_MISMATCH_TOLERANCE = 0.10
HIGH_CONFIDENCE_THRESHOLD = 0.8
MIN_MEANINGFUL_RAW_TEXT_LEN = 8

FORBIDDEN_DIRECT_TARGETS = {"communications_length", "earthworks_communications_length_m"}
PRICE_LIKE_TOKENS = ["цена", "стоимост", "price", "unit_price", "тариф", "ставка"]

STEEL_CLASS_TOKENS = ["а240", "a240", "а500", "a500", "вр-1", "вр1"]
REBAR_GROUP_CODES = {
    "foundation_rebar_items",
    "floor_slab_1_rebar_items",
    "floor_slab_2_rebar_items",
    "main_wall_rebar_items",
    "lintel_rebar_items",
}
REBAR_DIRECT_TARGETS: set[str] = set()
LINEAR_REBAR_UNIT_TOKENS = ["м/п", "м.п", "п.м", "мп", "linear_m"]
MASS_PER_M_TOKENS = ["масса ед", "масса 1", "кг/м", "кг / м", "кг/п.м", "кг/м.п"]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def approx_equal(a: float, b: float, tolerance: float) -> bool:
    if b == 0:
        return abs(a) < 1e-6
    return abs(a - b) / abs(b) <= tolerance


def check_sourcing(item: dict, path: str, warnings: list[str]) -> None:
    if item.get("value") is None:
        return
    missing_fields = [f for f in ("source_pdf", "page_number", "confidence") if item.get(f) is None]
    if missing_fields:
        warnings.append(f"{path}: missing required source field(s) {missing_fields}")
    raw_text = item.get("raw_text") or ""
    table_context = item.get("table_context") or ""
    if not raw_text.strip() and not table_context.strip():
        warnings.append(f"{path}: value present but no raw_text/table_context - cannot verify against source")
    confidence = item.get("confidence")
    if confidence is not None:
        if confidence > HIGH_CONFIDENCE_THRESHOLD and len(raw_text.strip()) < MIN_MEANINGFUL_RAW_TEXT_LEN and not table_context.strip():
            warnings.append(f"{path}: confidence={confidence} but raw_text is very short/generic ('{raw_text}')")
        if confidence < HIGH_CONFIDENCE_THRESHOLD and not item.get("needs_review", False):
            warnings.append(f"{path}: confidence={confidence} (<{HIGH_CONFIDENCE_THRESHOLD}) but needs_review is not set")


def check_unit(item: dict, path: str, unit_guide: dict, warnings: list[str]) -> None:
    normalized = item.get("normalized_unit")
    if normalized is None:
        return
    valid_normalized = set(unit_guide.values())
    if normalized not in valid_normalized:
        warnings.append(f"{path}: normalized_unit '{normalized}' not in unit_normalization_guide.json values {sorted(valid_normalized)}")


def check_forbidden_target(item: dict, path: str, warnings: list[str]) -> None:
    code = str(item.get("target_code") or "").lower()
    if code in FORBIDDEN_DIRECT_TARGETS:
        warnings.append(
            f"{path}: '{item.get('target_code')}' looks like a direct communications_length extraction - "
            "prompt requires pipe_items instead, this value should not be trusted as-is"
        )
    if code == "communications_length_m":
        notes = f"{item.get('raw_text') or ''} {item.get('table_context') or ''}".lower()
        if not any(token in notes for token in ("итого", "общ", "суммар", "total")):
            warnings.append(
                f"{path}: communications_length_m is allowed only when PDF has an explicit total/general length; "
                "do not trust it if it was calculated from pipe rows in chat"
            )
    name = str(item.get("item_name") or item.get("target_code") or "").lower()
    if any(tok in name for tok in PRICE_LIKE_TOKENS):
        warnings.append(f"{path}: item name/code '{name}' looks price-related, prompt asked not to extract prices")


def _is_rebar_item(group_code: str | None, item: dict) -> bool:
    target_code = str(item.get("target_code") or "")
    return group_code in REBAR_GROUP_CODES or target_code in REBAR_DIRECT_TARGETS


def _looks_like_linear_rebar_source(item: dict) -> bool:
    normalized = str(item.get("normalized_unit") or "").lower()
    unit = str(item.get("unit") or "").lower()
    raw_text = str(item.get("raw_text") or "").lower()
    haystack = " ".join([normalized, unit, raw_text])
    return normalized == "linear_m" or any(tok in haystack for tok in LINEAR_REBAR_UNIT_TOKENS)


def _raw_mentions_mass_per_m(item: dict) -> bool:
    raw_text = str(item.get("raw_text") or "").lower()
    table_context = str(item.get("table_context") or "").lower()
    return any(tok in f"{raw_text} {table_context}" for tok in MASS_PER_M_TOKENS)


def check_rebar_item(group_code: str | None, item: dict, path: str, warnings: list[str]) -> None:
    value = item.get("value")
    if not isinstance(value, dict):
        return

    diameter_mm = value.get("diameter_mm")
    if diameter_mm is not None and not (2 <= diameter_mm <= 40):
        warnings.append(f"{path}: rebar diameter_mm={diameter_mm} outside plausible 2-40mm range")

    steel_class = str(value.get("steel_class") or "").lower()
    if steel_class and not any(tok in steel_class for tok in STEEL_CLASS_TOKENS):
        warnings.append(f"{path}: steel_class '{value.get('steel_class')}' doesn't look like a recognized rebar class (А240/А500...)")

    length_field = "source_length_m" if value.get("source_length_m") is not None else (
        "spec_length_m" if value.get("spec_length_m") is not None else "length_m"
    )
    mass_per_m_field = "kg_per_meter" if value.get("kg_per_meter") is not None else "mass_per_m_kg"

    length_m = value.get(length_field)
    if length_m is not None and not isinstance(length_m, (int, float)):
        warnings.append(f"{path}: {length_field} is not numeric: {length_m!r}")

    mass_per_m_kg = value.get(mass_per_m_field)
    if mass_per_m_kg is not None and not isinstance(mass_per_m_kg, (int, float)):
        warnings.append(f"{path}: {mass_per_m_field} is not numeric: {mass_per_m_kg!r}")

    weight_kg = value.get("weight_kg")
    if weight_kg is not None and not isinstance(weight_kg, (int, float)):
        warnings.append(f"{path}: weight_kg is not numeric: {weight_kg!r}")

    if not _looks_like_linear_rebar_source(item):
        return

    if length_m is None:
        warnings.append(
            f"{path}: rebar row in linear meters should preserve source/spec length; "
            "source value is length, not calculated weight"
        )
    if _raw_mentions_mass_per_m(item) and mass_per_m_kg is None:
        warnings.append(f"{path}: rebar row mentions mass per meter but value.{mass_per_m_field} is missing")
    if weight_kg is not None:
        warnings.append(
            f"{path}: model appears to have calculated rebar weight; "
            "weight_kg should be null unless kg is explicit as the row quantity in PDF"
        )


def check_group_item(group_code: str, item: dict, path: str, warnings: list[str]) -> None:
    value = item.get("value")
    if not isinstance(value, dict):
        return
    if group_code == "trench_routes":
        length_m, depth_m, width_m, volume_m3 = (value.get(k) for k in ("length_m", "depth_m", "width_m", "volume_m3"))
        if None not in (length_m, depth_m, width_m, volume_m3):
            implied = length_m * depth_m * width_m
            if not approx_equal(volume_m3, implied, VOLUME_MISMATCH_TOLERANCE):
                warnings.append(
                    f"{path}: trench route volume_m3={volume_m3} vs length*depth*width={implied:.2f} "
                    f"(>{VOLUME_MISMATCH_TOLERANCE:.0%} off)"
                )
    if group_code in REBAR_GROUP_CODES:
        check_rebar_item(group_code, item, path, warnings)


def check_trench_routes_total(found_items: list[dict], warnings: list[str], section_path: str) -> None:
    routes = [it for it in found_items if it.get("group_code") == "trench_routes" and isinstance(it.get("value"), dict)]
    total_items = [it for it in found_items if it.get("target_code") in ("trench_volume_m3",)]
    if not routes or not total_items:
        return
    routes_sum = sum(r["value"].get("volume_m3") or 0 for r in routes)
    for total_item in total_items:
        total_value = total_item.get("value")
        if isinstance(total_value, (int, float)) and not approx_equal(routes_sum, total_value, TOTALS_MISMATCH_TOLERANCE):
            warnings.append(
                f"{section_path}: trench_volume_m3={total_value} vs sum(trench_routes.volume_m3)={routes_sum:.2f} "
                f"(>{TOTALS_MISMATCH_TOLERANCE:.0%} off)"
            )


def validate(data: dict, unit_guide: dict) -> tuple[list[str], dict[str, int]]:
    warnings: list[str] = []
    stats = {"sections": 0, "raw_table_rows": 0, "found_items": 0, "missing_items": 0, "needs_review_items": 0}

    if "sections" not in data or not isinstance(data["sections"], dict):
        warnings.append("top-level 'sections' object is missing or not a dict")
        return warnings, stats

    for section_code, section in data["sections"].items():
        stats["sections"] += 1
        raw_table_rows = section.get("raw_table_rows") or []
        stats["raw_table_rows"] += len(raw_table_rows)
        found_items = section.get("found") or []
        stats["found_items"] += len(found_items)
        stats["missing_items"] += len(section.get("missing") or [])
        stats["needs_review_items"] += len(section.get("needs_review") or [])

        if found_items and not raw_table_rows:
            warnings.append(
                f"{section_code}: found items present but raw_table_rows is empty - "
                "A6.4 requires extracting table rows before target mapping"
            )

        for i, row in enumerate(raw_table_rows):
            path = f"{section_code}.raw_table_rows[{i}]"
            if not row.get("source_pdf") or row.get("page_number") is None:
                warnings.append(f"{path}: missing source_pdf/page_number")
            if not row.get("raw_text") and not row.get("cells"):
                warnings.append(f"{path}: missing raw_text/cells")
            check_unit(row, path, unit_guide, warnings)
            row_text = " ".join(
                str(part or "")
                for part in [row.get("table_title"), row.get("raw_text"), " ".join(map(str, row.get("cells") or []))]
            ).lower()
            if "арматур" in row_text and _looks_like_linear_rebar_source(row) and "масса" in row_text:
                mapped = row.get("mapped_target_codes") or []
                if not mapped:
                    warnings.append(
                        f"{path}: raw rebar row in linear meters has no mapped_target_codes; "
                        "check that found item preserves source/spec length and kg_per_meter/mass_per_m_kg"
                    )

        for i, item in enumerate(found_items):
            path = f"{section_code}.found[{i}] ({item.get('target_code')})"
            check_sourcing(item, path, warnings)
            check_unit(item, path, unit_guide, warnings)
            check_forbidden_target(item, path, warnings)
            group_code = item.get("group_code")
            if group_code:
                check_group_item(group_code, item, path, warnings)
            elif _is_rebar_item(group_code, item):
                check_rebar_item(group_code, item, path, warnings)

        check_trench_routes_total(found_items, warnings, section_code)

    return warnings, stats


def render_report(warnings: list[str], stats: dict[str, int]) -> str:
    lines = ["# A6.1 — Claude-chat extraction validation report", ""]
    lines.append(
        f"Sections: {stats['sections']}. Raw table rows: {stats['raw_table_rows']}. Found items: {stats['found_items']}. "
        f"Missing items: {stats['missing_items']}. Needs-review items: {stats['needs_review_items']}."
    )
    lines.append("")
    lines.append(f"## Warnings ({len(warnings)})")
    lines.append("")
    if warnings:
        for w in warnings:
            lines.append(f"- {w}")
    else:
        lines.append("(none)")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    data = load_json(args.input)
    unit_guide = load_json(HERE.parent / "data" / "unit_normalization_guide.json")
    unit_guide = {k: v for k, v in unit_guide.items() if not k.startswith("_")}

    warnings, stats = validate(data, unit_guide)
    report = render_report(warnings, stats)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print(f"validated: {stats}, {len(warnings)} warnings -> {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
