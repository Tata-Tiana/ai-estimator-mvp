"""A6.0: deterministic sanity checks on raw vision extraction output.

Per page, per item: unit normalization, internal arithmetic checks
(volume ~= length*depth*width, table totals ~= sum of items), and
low-confidence / missing-raw_text flags. Does not compare against any
reference data (that is compare_vision_with_reference.py's job) and does
not aggregate across pages (a value repeated on two pages is not
"double counted" here — cross-page matching needs the same reference
semantics compare.py already needs, so it isn't duplicated here).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

VOLUME_MISMATCH_TOLERANCE = 0.20  # 20% - hand-typed dims/volumes rarely match exactly
TOTALS_MISMATCH_TOLERANCE = 0.10
LOW_CONFIDENCE_THRESHOLD = 0.5

UNIT_NORMALIZATION = {
    "m2": "m2", "м2": "m2", "кв.м": "m2", "кв. м": "m2", "м²": "m2",
    "m3": "m3", "м3": "m3", "куб.м": "m3", "куб. м": "m3", "м³": "m3",
    "linear_m": "linear_m", "м": "linear_m", "м.п": "linear_m", "м.п.": "linear_m",
    "пог.м": "linear_m", "пог. м": "linear_m", "мп": "linear_m",
    "pcs": "pcs", "шт": "pcs", "шт.": "pcs",
    "kg": "kg", "кг": "kg",
    "mm": "mm", "мм": "mm",
    "cm": "cm", "см": "cm",
}


def normalize_unit(raw_unit: Any) -> str | None:
    if not raw_unit or not isinstance(raw_unit, str):
        return None
    key = raw_unit.strip().lower()
    return UNIT_NORMALIZATION.get(key, key or None)


def approx_equal(a: float, b: float, tolerance: float) -> bool:
    if b == 0:
        return abs(a) < 1e-6
    return abs(a - b) / abs(b) <= tolerance


def validate_trench_routes_table(table: dict) -> list[str]:
    issues: list[str] = []
    items = table.get("items") or []
    items_volume_sum = 0.0
    for item in items:
        length_m = item.get("length_m")
        depth_m = item.get("depth_m")
        width_m = item.get("width_m")
        volume_m3 = item.get("volume_m3")
        name = item.get("name", "?")
        if volume_m3 is not None:
            items_volume_sum += volume_m3
        if None not in (length_m, depth_m, width_m, volume_m3):
            implied = length_m * depth_m * width_m
            if not approx_equal(volume_m3, implied, VOLUME_MISMATCH_TOLERANCE):
                issues.append(
                    f"trench_routes '{name}': stated volume_m3={volume_m3} vs "
                    f"length*depth*width={implied:.2f} (>{VOLUME_MISMATCH_TOLERANCE:.0%} off)"
                )
    for total in table.get("totals") or []:
        total_volume = total.get("total_volume_m3")
        if total_volume is not None and items and not approx_equal(
            items_volume_sum, total_volume, TOTALS_MISMATCH_TOLERANCE
        ):
            issues.append(
                f"trench_routes totals: total_volume_m3={total_volume} vs "
                f"sum(items.volume_m3)={items_volume_sum:.2f} (>{TOTALS_MISMATCH_TOLERANCE:.0%} off)"
            )
    return issues


def validate_pipe_items_table(table: dict) -> list[str]:
    issues: list[str] = []
    for item in table.get("items") or []:
        name = item.get("name", "?")
        if item.get("piece_length_m") is None or item.get("quantity_pcs") is None:
            issues.append(f"pipe_items '{name}': missing piece_length_m or quantity_pcs")
    return issues


def validate_table(table: dict) -> dict:
    issues: list[str] = list(table.get("_issues") or [])
    table_type = table.get("table_type")
    if table_type == "trench_routes":
        issues += validate_trench_routes_table(table)
    elif table_type == "pipe_items":
        issues += validate_pipe_items_table(table)
    if not (table.get("raw_text") or "").strip():
        issues.append("missing raw_text - cannot verify against source image")
    confidence = table.get("confidence")
    if confidence is not None and confidence < LOW_CONFIDENCE_THRESHOLD:
        issues.append(f"low confidence ({confidence})")
    table = dict(table)
    table["normalized_unit"] = None
    table["validation_issues"] = issues
    table["needs_review"] = bool(issues)
    return table


def validate_flat_item(item: dict) -> dict:
    issues: list[str] = []
    if not (item.get("raw_text") or "").strip():
        issues.append("missing raw_text - cannot verify against source image")
    confidence = item.get("confidence")
    if confidence is not None and confidence < LOW_CONFIDENCE_THRESHOLD:
        issues.append(f"low confidence ({confidence})")
    normalized = normalize_unit(item.get("unit"))
    if item.get("unit") and normalized is None:
        issues.append(f"unrecognized unit '{item.get('unit')}'")
    item = dict(item)
    item["normalized_unit"] = normalized
    item["validation_issues"] = issues
    item["needs_review"] = bool(issues)
    return item


def validate_page_extraction(extracted: dict) -> dict:
    validated = dict(extracted)
    validated["tables"] = [validate_table(t) for t in extracted.get("tables") or []]
    validated["materials"] = [validate_flat_item(m) for m in extracted.get("materials") or []]
    validated["scalar_values"] = [validate_flat_item(s) for s in extracted.get("scalar_values") or []]
    return validated


def validate_page(page: dict) -> dict:
    result = dict(page)
    if "error" in page:
        result["status"] = "error"
        return result
    extracted = page.get("extracted")
    if extracted is None:
        result["status"] = "no_data"
        return result
    validated_extracted = validate_page_extraction(extracted)
    result["extracted"] = validated_extracted
    any_issue = any(
        item.get("needs_review")
        for group in ("tables", "materials", "scalar_values")
        for item in validated_extracted.get(group, [])
    )
    result["status"] = "needs_review" if any_issue else "ok"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vision-json", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.vision_json.read_text(encoding="utf-8"))
    pages = [validate_page(p) for p in data.get("pages", [])]

    status_counts: dict[str, int] = {}
    for p in pages:
        status_counts[p["status"]] = status_counts.get(p["status"], 0) + 1

    output = dict(data)
    output["pages"] = pages
    output["status_counts"] = status_counts

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"validated {len(pages)} pages: {status_counts} -> {args.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
