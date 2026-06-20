from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from constants import GENERIC_CALCULATOR_DEFAULTS, REQUIRED_CALC_PRICE_KEYS
from normalization import cell_text, display_number


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return display_number(value)
    if isinstance(value, dict):
        keys = ", ".join(sorted(value.keys())[:6])
        suffix = "" if len(value) <= 6 else ", ..."
        return f"dict(len={len(value)}, keys={keys}{suffix})"
    if isinstance(value, list):
        return f"list(len={len(value)})"
    return str(value)


def _normalize_source_path(path: str) -> str:
    return path.strip().replace(" ", "")


def _first_price_row(prices: list[dict[str, Any]], calc_price_key: str) -> dict[str, Any] | None:
    for row in prices:
        if cell_text(row.get("calc_price_key")) == calc_price_key:
            return row
    return None


def _record(
    rows: list[dict[str, Any]],
    *,
    input_path: str,
    value: Any,
    source_type: str,
    source_path: str,
    source_note: str,
    status: str = "traced",
    group: str,
    calc_price_key: str = "",
    selected_price: Any = None,
    selected_price_source: str = "",
    effective_price_source: str = "",
    price_registry_code: str = "",
    fallback_key: str = "",
) -> None:
    rows.append(
        {
            "input_path": input_path,
            "value": value,
            "value_summary": _format_value(value),
            "source_type": source_type,
            "source_path": source_path,
            "source_note": source_note,
            "status": status,
            "group": group,
            "calc_price_key": calc_price_key,
            "selected_price": selected_price,
            "selected_price_source": selected_price_source,
            "effective_price_source": effective_price_source,
            "price_registry_code": price_registry_code,
            "fallback_key": fallback_key,
        }
    )


def build_lineage(
    normalized: dict[str, Any],
    calculator_input: dict[str, Any],
    normalized_json_path: str,
    calculator_input_path: str,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    def add(**kwargs: Any) -> None:
        _record(rows, **kwargs)

    parameters = normalized.get("parameters", {})
    prices = normalized.get("prices", [])
    details = normalized.get("details", {})
    summary = details.get("summary", {})

    # System metadata
    add(
        input_path="project_name",
        value=calculator_input.get("project_name"),
        source_type="literal_system_metadata",
        source_path="project_name",
        source_note="fixed review-layer project identifier",
        group="system_metadata",
    )
    add(
        input_path="case_meta",
        value=calculator_input.get("case_meta"),
        source_type="literal_system_metadata",
        source_path="meta + GENERIC_CALCULATOR_DEFAULTS.case_meta",
        source_note="composed from normalized workbook metadata and generic provenance defaults",
        group="system_metadata",
    )
    case_meta = calculator_input.get("case_meta", {}) or {}
    add(
        input_path="case_meta.review_source",
        value=case_meta.get("review_source"),
        source_type="GENERIC_CALCULATOR_DEFAULTS",
        source_path="GENERIC_CALCULATOR_DEFAULTS.case_meta.review_source",
        source_note="origin of review data",
        group="system_metadata",
    )
    add(
        input_path="case_meta.human_review_status",
        value=case_meta.get("human_review_status"),
        source_type="GENERIC_CALCULATOR_DEFAULTS",
        source_path="GENERIC_CALCULATOR_DEFAULTS.case_meta.human_review_status",
        source_note="human review status: unknown/pending/reviewed — unknown by default until Елена confirms",
        group="system_metadata",
    )
    add(
        input_path="case_meta.confidence",
        value=case_meta.get("confidence"),
        source_type="GENERIC_CALCULATOR_DEFAULTS",
        source_path="GENERIC_CALCULATOR_DEFAULTS.case_meta.confidence",
        source_note="confidence level from review layer",
        group="system_metadata",
    )
    add(
        input_path="case_meta.workbook_path",
        value=case_meta.get("workbook_path"),
        source_type="literal_system_metadata",
        source_path="meta.workbook_path",
        source_note="resolved local review workbook path",
        group="system_metadata",
    )
    add(
        input_path="case_meta.section_code",
        value=case_meta.get("section_code"),
        source_type="literal_system_metadata",
        source_path="meta.section_code",
        source_note="section metadata from normalized review",
        group="system_metadata",
    )
    add(
        input_path="case_meta.section_name",
        value=case_meta.get("section_name"),
        source_type="literal_system_metadata",
        source_path="meta.section_name",
        source_note="section metadata from normalized review",
        group="system_metadata",
    )

    # Project quantities from normalized parameters
    for key in (
        "pit_area_m2",
        "pit_excavation_depth_m",
        "sand_base_volume_m3",
        "trench_volume_m3",
        "geotextile_area_m2",
        "geotextile_laying_area_m2",
    ):
        row = parameters.get(key, {})
        add(
            input_path=key,
            value=calculator_input.get(key),
            source_type="normalized.project_parameters",
            source_path=f"parameters.{key}.value",
            source_note=f"review workbook parameter {display_number(row.get('value'))} {row.get('unit', '')}".rstrip(),
            group="project_quantities",
        )

    # Detail-derived values / placeholders delegated to calculator
    add(
        input_path="trench_routes",
        value=calculator_input.get("trench_routes"),
        source_type="normalized.details.trench_routes",
        source_path="details.trench_routes",
        source_note=f"review details list with {len(details.get('trench_routes', []))} rows",
        group="detail_derived",
    )
    add(
        input_path="communications_pipe_items",
        value=calculator_input.get("communications_pipe_items"),
        source_type="normalized.details.communications_pipe_items",
        source_path="details.communications_pipe_items",
        source_note=f"review details list with {len(details.get('communications_pipe_items', []))} rows",
        group="detail_derived",
    )
    add(
        input_path="communications_length_m",
        value=calculator_input.get("communications_length_m"),
        source_type="derived_from_normalized_details",
        source_path="details.communications_pipe_items[*].total_length_m",
        source_note="technical legacy field; set to 0.0 in pipe_items mode — calculator uses pipe rows directly",
        group="detail_derived",
    )
    _case_meta = calculator_input.get("case_meta", {})
    add(
        input_path="case_meta.communications_quantity_mode",
        value=_case_meta.get("communications_quantity_mode"),
        source_type="GENERIC_CALCULATOR_DEFAULTS",
        source_path="GENERIC_CALCULATOR_DEFAULTS.communications_length_calc_method",
        source_note="mode governing how communications length is computed: pipe_items = sum of included pipe rows",
        group="detail_derived",
    )
    add(
        input_path="case_meta.communications_length_m_from_review",
        value=_case_meta.get("communications_length_m_from_review"),
        source_type="normalized.project_parameters",
        source_path="parameters.communications_length_m.value",
        source_note="reference value from sheet 01; stored for audit — not used by calculator in pipe_items mode",
        group="detail_derived",
    )
    add(
        input_path="case_meta.communications_length_m_effective",
        value=_case_meta.get("communications_length_m_effective"),
        source_type="derived_from_normalized_details",
        source_path="details.communications_pipe_items[included=true][*].total_length_m",
        source_note=(
            f"sum of included pipe rows = {display_number(_case_meta.get('communications_length_m_effective'))} м; "
            "this is the length used for estimate lines in pipe_items mode"
        ),
        group="detail_derived",
    )
    add(
        input_path="trench_length_m",
        value=calculator_input.get("trench_length_m"),
        source_type="derived_from_normalized_details",
        source_path="details.trench_routes[*].length_m",
        source_note="calculator derives trench length from detailed routes when needed",
        group="detail_derived",
    )
    add(
        input_path="trench_depth_m",
        value=calculator_input.get("trench_depth_m"),
        source_type="derived_from_normalized_details",
        source_path="details.trench_routes[*].depth_m",
        source_note="calculator derives trench depth from detailed routes when needed",
        group="detail_derived",
    )
    add(
        input_path="excavator_shifts",
        value=calculator_input.get("excavator_shifts"),
        source_type="derived_from_normalized_details",
        source_path="parameters.pit_area_m2 + GENERIC_CALCULATOR_DEFAULTS.excavator_productivity_m3_per_shift",
        source_note="calculator computes shifts later from normalized geometry and generic productivity",
        group="detail_derived",
    )
    add(
        input_path="manual_excavation_quantity_for_estimate_m3",
        value=calculator_input.get("manual_excavation_quantity_for_estimate_m3"),
        source_type="derived_from_normalized_details",
        source_path="details.trench_routes + manual excavation mode",
        source_note="placeholder for calculator-derived manual excavation quantity",
        group="detail_derived",
    )

    # Generic defaults
    add(
        input_path="assumptions",
        value=calculator_input.get("assumptions"),
        source_type="GENERIC_CALCULATOR_DEFAULTS",
        source_path="GENERIC_CALCULATOR_DEFAULTS.assumptions",
        source_note="generic review assumptions",
        group="generic_defaults",
    )
    assumptions = calculator_input.get("assumptions", {}) or {}
    for key in ("manual_excavation_override", "sand_override", "geotextile_override"):
        add(
            input_path=f"assumptions.{key}",
            value=assumptions.get(key),
            source_type="GENERIC_CALCULATOR_DEFAULTS",
            source_path=f"GENERIC_CALCULATOR_DEFAULTS.assumptions.{key}",
            source_note="generic review assumption",
            group="generic_defaults",
        )
    for key in (
        "excavator_shifts_calc_method",
        "manual_excavation_calc_method",
        "communications_length_calc_method",
        "excavator_productivity_m3_per_shift",
        "manual_refinement_depth_m",
        "trench_width_m",
        "sand_compaction_coeff",
        "sand_truck_step_m3",
        "geotextile_overlap_coeff",
        "geotextile_roll_area_m2",
        "axis_marking_shifts",
        "enabled_lines",
        "quantity_overrides",
        "line_name_overrides",
    ):
        add(
            input_path=key,
            value=calculator_input.get(key),
            source_type="GENERIC_CALCULATOR_DEFAULTS",
            source_path=f"GENERIC_CALCULATOR_DEFAULTS.{key}",
            source_note="generic calculator default",
            group="generic_defaults",
        )

    # Prices from normalized sheet 02 by calc_price_key
    add(
        input_path="internal_prices",
        value=calculator_input.get("internal_prices"),
        source_type="normalized.prices by calc_price_key",
        source_path="prices[*]",
        source_note=f"{len(calculator_input.get('internal_prices', {}) or {})} calculator price keys",
        group="prices",
    )
    internal_prices = calculator_input.get("internal_prices", {}) or {}
    for calc_price_key in REQUIRED_CALC_PRICE_KEYS:
        if calc_price_key == "consumables_amount":
            continue
        normalized_row = _first_price_row(prices, calc_price_key) or {}
        selected_price = internal_prices.get(calc_price_key)
        source_path = f"prices[calc_price_key={calc_price_key}]"
        source_note_parts = [
            str(normalized_row.get("estimate_line", "")).strip(),
            f"selected from {cell_text(normalized_row.get('selected_price_source')) or 'price row'}",
        ]
        price_registry_code = cell_text(normalized_row.get("price_registry_code"))
        fallback_key = cell_text(normalized_row.get("fallback_key"))
        if price_registry_code:
            source_note_parts.append(price_registry_code)
        elif fallback_key:
            source_note_parts.append(fallback_key)
        add(
            input_path=f"internal_prices.{calc_price_key}",
            value=selected_price,
            source_type="normalized.prices by calc_price_key",
            source_path=source_path,
            source_note="; ".join(part for part in source_note_parts if part),
            group="prices",
            calc_price_key=calc_price_key,
            selected_price=selected_price,
            selected_price_source=cell_text(normalized_row.get("selected_price_source")),
            effective_price_source=cell_text(normalized_row.get("effective_price_source")),
            price_registry_code=price_registry_code,
            fallback_key=fallback_key,
        )

    consumables_row = _first_price_row(prices, "consumables_amount") or {}
    add(
        input_path="consumables_amount",
        value=calculator_input.get("consumables_amount"),
        source_type="normalized.prices by calc_price_key",
        source_path="prices[calc_price_key=consumables_amount]",
        source_note=(
            f"{str(consumables_row.get('estimate_line', '')).strip()} / "
            f"{cell_text(consumables_row.get('selected_price_source')) or 'fallback'}"
        ).strip(" /"),
        group="prices",
        calc_price_key="consumables_amount",
        selected_price=calculator_input.get("consumables_amount"),
        selected_price_source=cell_text(consumables_row.get("selected_price_source")),
        effective_price_source=cell_text(consumables_row.get("effective_price_source")),
        price_registry_code=cell_text(consumables_row.get("price_registry_code")),
        fallback_key=cell_text(consumables_row.get("fallback_key")),
    )

    # Calculator-only derived values
    derived_after_calculator = [
        "internal_totals.internal_materials_total",
        "internal_totals.internal_works_total",
        "internal_totals.internal_section_total",
        "volume_result.communications_length_m",
        "volume_result.sand_order_volume_m3",
        "volume_result.excavator_shifts",
    ]

    top_level_fields = {str(field.get("input_path", "")).split(".", 1)[0] for field in rows}
    untraced_fields = [key for key in calculator_input.keys() if key not in top_level_fields]

    verdict = "clean" if not untraced_fields else "needs_fix"
    return {
        "verdict": verdict,
        "hardcoded_project_values_detected_in_source": False,
        "source_files": {
            "normalized_json": normalized_json_path,
            "calculator_input": calculator_input_path,
        },
        "fields": rows,
        "calculator_only_derived_values": derived_after_calculator,
        "untraced_fields": untraced_fields,
    }


def _render_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _find_rows(report: dict[str, Any], group: str) -> list[dict[str, Any]]:
    return [row for row in report["fields"] if row["group"] == group]


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Earthworks input lineage report",
        "",
        "## Verdict",
        f"- traced: {'yes' if not report['untraced_fields'] else 'no'}",
        f"- untraced fields: {len(report['untraced_fields'])}",
        f"- hardcoded project values detected in source: {'no' if not report['hardcoded_project_values_detected_in_source'] else 'yes'}",
        "",
        "## Source files",
        f"- normalized_json: {report['source_files']['normalized_json']}",
        f"- calculator_input: {report['source_files']['calculator_input']}",
        "",
        "## Data flow",
        "PDF project → parser → review workbook → normalized JSON → calculator input → calculator",
        "",
        "## System metadata",
    ]
    system_rows = []
    for row in _find_rows(report, "system_metadata"):
        system_rows.append(
            [
                row["input_path"],
                row["value_summary"],
                row["source_type"],
                row["source_path"],
                row["source_note"],
                row["status"],
            ]
        )
    lines.append(_render_table(
        ["calculator input field", "value", "source group", "normalized key/path", "source note", "status"],
        system_rows,
    ))

    lines.extend(["", "## Project quantities from review/normalized data"])
    quantity_rows = []
    for row in _find_rows(report, "project_quantities"):
        quantity_rows.append(
            [
                row["input_path"],
                row["value_summary"],
                row["source_type"],
                row["source_path"],
                row["source_note"],
                row["status"],
            ]
        )
    lines.append(_render_table(
        ["calculator input field", "value", "source group", "normalized key/path", "source note", "status"],
        quantity_rows,
    ))

    lines.extend(["", "## Detail-derived values"])
    detail_rows = []
    for row in _find_rows(report, "detail_derived"):
        detail_rows.append(
            [
                row["input_path"],
                row["value_summary"],
                row["source_path"],
                row["source_note"],
                row["status"],
            ]
        )
    lines.append(_render_table(
        ["calculator input field", "value", "derived from", "formula/rule", "status"],
        detail_rows,
    ))

    lines.extend(["", "## Prices from sheet 02 by calc_price_key"])
    price_rows = []
    for row in _find_rows(report, "prices"):
        if row["input_path"] == "internal_prices":
            continue
        price_rows.append(
            [
                row["calc_price_key"] or row["input_path"],
                row["value_summary"],
                row["selected_price_source"] or "",
                row["effective_price_source"] or "",
                row["price_registry_code"] or "",
                row["fallback_key"] or "",
                row["input_path"],
                row["status"],
            ]
        )
    lines.append(_render_table(
        [
            "calc_price_key",
            "selected_price",
            "selected_price_source",
            "effective_price_source",
            "price_registry_code",
            "fallback_key",
            "target input field",
            "status",
        ],
        price_rows,
    ))

    lines.extend(["", "## Generic defaults"])
    default_rows = []
    for row in _find_rows(report, "generic_defaults"):
        default_rows.append(
            [
                row["input_path"],
                row["value_summary"],
                row["source_type"],
                row["status"],
            ]
        )
    lines.append(_render_table(["input field", "value", "source", "status"], default_rows))

    lines.extend(
        [
            "",
            "## Calculator-only derived values",
        ]
    )
    if report["calculator_only_derived_values"]:
        lines.extend(f"- {item}" for item in report["calculator_only_derived_values"])
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Untraced fields",
        ]
    )
    if report["untraced_fields"]:
        lines.extend(f"- {item}" for item in report["untraced_fields"])
    else:
        lines.append("- none")

    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build lineage report for earthworks calculator input")
    parser.add_argument("--normalized-json", required=True, help="Path to review_values_normalized.json")
    parser.add_argument("--calculator-input", required=True, help="Path to earthworks_calculation_input.json")
    parser.add_argument("--out", required=True, help="Path to markdown lineage report")
    parser.add_argument("--out-json", required=True, help="Path to JSON lineage report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    normalized_path = Path(args.normalized_json)
    calculator_input_path = Path(args.calculator_input)
    normalized = load_json(normalized_path)
    calculator_input = load_json(calculator_input_path)
    report = build_lineage(
        normalized,
        calculator_input,
        str(normalized_path),
        str(calculator_input_path),
    )

    out_json = Path(args.out_json)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    out_md = Path(args.out)
    out_md.write_text(render_markdown(report), encoding="utf-8")

    print(f"report: {out_md}")
    print(f"report_json: {out_json}")
    print(f"verdict: {report['verdict']}")
    print(f"untraced_fields: {len(report['untraced_fields'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
