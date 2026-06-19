from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


COMPARE_METRICS: list[tuple[str, list[str]]] = [
    ("internal_materials_total", ["internal_totals.internal_materials_total"]),
    ("internal_works_total", ["internal_totals.internal_works_total"]),
    ("internal_section_total", ["internal_totals.internal_section_total"]),
    ("communications_length_m", ["volume_result.communications_length_m", "inputs.communications_length_m"]),
    ("sand_order_volume_m3", ["volume_result.sand_order_volume_m3", "expected.volumes.sand_order_volume_m3"]),
    ("excavator_shifts", ["volume_result.excavator_shifts", "inputs.excavator_shifts"]),
]

TOLERANCE = 0.01


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_path(data: Any, dotted_path: str) -> Any:
    current = data
    for part in dotted_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _as_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_value(value: Any) -> str:
    number = _as_number(value)
    if number is not None:
        if number.is_integer():
            return str(int(number))
        return f"{number:.2f}".rstrip("0").rstrip(".")
    if value is None:
        return "MISSING"
    return str(value)


def _first_present(data: dict[str, Any], paths: Iterable[str]) -> tuple[str | None, Any]:
    for path in paths:
        value = _resolve_path(data, path)
        if value is not None:
            return path, value
    return None, None


def compare_results(baseline: dict[str, Any], review: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], bool, bool]:
    rows: list[dict[str, Any]] = []
    missing_fields: list[str] = []
    exact_match = True
    has_differences = False

    for metric, paths in COMPARE_METRICS:
        baseline_path, baseline_value = _first_present(baseline, paths)
        review_path, review_value = _first_present(review, paths)

        baseline_number = _as_number(baseline_value)
        review_number = _as_number(review_value)

        if baseline_value is None:
            missing_fields.append(f"{metric}: missing in baseline")
        if review_value is None:
            missing_fields.append(f"{metric}: missing in review")

        if baseline_number is not None and review_number is not None:
            diff = review_number - baseline_number
            status = "OK" if abs(diff) <= TOLERANCE else "DIFF"
            if status == "DIFF":
                exact_match = False
                has_differences = True
            rows.append(
                {
                    "metric": metric,
                    "baseline": _format_value(baseline_number),
                    "review": _format_value(review_number),
                    "diff": _format_value(diff),
                    "status": status,
                    "baseline_path": baseline_path or "",
                    "review_path": review_path or "",
                }
            )
            continue

        if baseline_value is not None and review_value is not None and baseline_value == review_value:
            rows.append(
                {
                    "metric": metric,
                    "baseline": _format_value(baseline_value),
                    "review": _format_value(review_value),
                    "diff": "0",
                    "status": "OK",
                    "baseline_path": baseline_path or "",
                    "review_path": review_path or "",
                }
            )
            continue

        exact_match = False
        has_differences = True
        rows.append(
            {
                "metric": metric,
                "baseline": _format_value(baseline_value),
                "review": _format_value(review_value),
                "diff": "MISSING" if baseline_value is None or review_value is None else "N/A",
                "status": "MISSING",
                "baseline_path": baseline_path or "",
                "review_path": review_path or "",
            }
        )

    if missing_fields:
        has_differences = True
        exact_match = False

    return rows, missing_fields, exact_match, has_differences


def render_report(
    baseline_path: Path,
    review_path: Path,
    rows: list[dict[str, Any]],
    missing_fields: list[str],
    exact_match: bool,
    has_differences: bool,
) -> str:
    lines = [
        "# Calculation comparison report",
        "",
        "## Source",
        f"- baseline_result: {baseline_path}",
        f"- review_result: {review_path}",
        "",
        "## Verdict",
        "- compared: yes",
        f"- exact_match: {'yes' if exact_match else 'no'}",
        f"- has_differences: {'yes' if has_differences else 'no'}",
        "",
        "## Key totals comparison",
        "",
        "| metric | baseline | review | diff | status |",
        "|---|---:|---:|---:|---|",
    ]

    for row in rows:
        lines.append(
            f"| {row['metric']} | {row['baseline']} | {row['review']} | {row['diff']} | {row['status']} |"
        )

    lines.extend(
        [
            "",
            "## Missing fields",
        ]
    )
    if missing_fields:
        lines.extend(f"- {item}" for item in missing_fields)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Notes",
            "- This is a diagnostic comparison only.",
            "- Baseline result path is provided via CLI.",
            "- Review-layer source does not depend on the baseline fixture.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare baseline and review calculation results")
    parser.add_argument("--baseline-result", required=True, help="Path to baseline result.json")
    parser.add_argument("--review-result", required=True, help="Path to review result.json")
    parser.add_argument("--out", required=True, help="Path to diagnostic comparison report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    baseline_path = Path(args.baseline_result)
    review_path = Path(args.review_result)
    out_path = Path(args.out)

    baseline = load_json(baseline_path)
    review = load_json(review_path)
    rows, missing_fields, exact_match, has_differences = compare_results(baseline, review)
    report = render_report(baseline_path, review_path, rows, missing_fields, exact_match, has_differences)
    out_path.write_text(report, encoding="utf-8")
    print(f"report: {out_path}")
    print(f"exact_match: {'yes' if exact_match else 'no'}")
    print(f"has_differences: {'yes' if has_differences else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
