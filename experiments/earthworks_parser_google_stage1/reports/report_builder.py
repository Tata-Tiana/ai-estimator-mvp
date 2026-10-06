from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_reports(
    job_dir: Path,
    extracted: dict[str, Any],
    price_resolution: dict[str, Any],
    publisher_result: dict[str, str],
    registry_warnings: list[str],
) -> None:
    reports_dir = job_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    resolved = price_resolution["resolved_components"]
    counts = {
        "price_registry": sum(1 for row in resolved if row["source"] == "price_registry"),
        "base_case_fallback": sum(1 for row in resolved if row["source"] == "base_case_fallback"),
        "manual_override": sum(1 for row in resolved if row["source"] == "manual_override"),
        "missing_price": sum(1 for row in resolved if row["source"] == "missing_price"),
        "needs_attention": sum(1 for row in resolved if row["needs_attention"]),
    }

    parser_lines = [
        "# Earthworks Stage1 Parser Report",
        "",
        "- Google Sheet UX version: `v6`",
        "- Visible technical sheets: `yes`",
        "- Technical sheets are intentionally not hidden.",
        f"- Google Sheet/workbook status: `{publisher_result.get('status')}`",
        f"- Google Sheet URL: {publisher_result.get('url', '')}",
        f"- Project parameters found: `{sum(1 for p in extracted['parameters'].values() if p.get('value') is not None)}`",
        f"- Parser warnings: `{len(extracted.get('warnings', []))}`",
        "",
        "## Parameters",
    ]
    for key, parameter in extracted["parameters"].items():
        ev = parameter.get("evidence") or {}
        parser_lines.append(
            f"- `{key}` = `{parameter.get('value')}` `{parameter.get('unit', '')}`; "
            f"source: {ev.get('logical_sheet_title', '')}, page {ev.get('physical_page_number', '')}"
        )
    (reports_dir / "parser_report.md").write_text("\n".join(parser_lines) + "\n", encoding="utf-8")

    price_lines = [
        "# Earthworks Price Resolution Report",
        "",
        "- Google price_registry is read-only for calculator runs.",
        "- Missing calculator prices are not auto-published into price_registry.",
        "- Base case ЮСВ fallback is used only inside this job.",
        "",
        "## Counts",
        *[f"- {key}: `{value}`" for key, value in counts.items()],
        "",
        "## Registry warnings",
        *[f"- {warning}" for warning in registry_warnings],
        "",
        "## Components",
        "| component | line | kind | unit | price | source | attention |",
        "|---|---|---|---|---:|---|---|",
    ]
    for row in resolved:
        price_lines.append(
            f"| `{row['component_code']}` | {row['estimate_line_name_ru']} | {row['price_kind_ru']} | "
            f"{row['unit']} | {row['price']} | {row['source_label_ru']} | {'да' if row['needs_attention'] else 'нет'} |"
        )
    absent = price_resolution.get("absent_structural_components") or {}
    if absent:
        price_lines.extend(["", "## Not shown because absent by estimate logic"])
        for key, reason in absent.items():
            price_lines.append(f"- `{key}`: {reason}")
    (reports_dir / "earthworks_price_resolution_report.md").write_text("\n".join(price_lines) + "\n", encoding="utf-8")

    see_details_keys = {"trench_routes", "trench_volume_m3", "communications_pipe_items", "communications_length_m"}
    needs_review_keys = {"pit_excavation_depth_m", "geotextile_area_m2", "geotextile_laying_area_m2"}
    coverage_counts = {
        "found_confident": 0,
        "needs_review": 0,
        "see_details": 0,
        "missing": 0,
        "manual_required": 0,
        "auto_calculated": 0,
        "price_rows": len(resolved),
    }
    for key, parameter in extracted["parameters"].items():
        if parameter.get("value") is None:
            coverage_counts["missing"] += 1
        elif key in see_details_keys:
            coverage_counts["see_details"] += 1
        elif key in needs_review_keys:
            coverage_counts["needs_review"] += 1
        else:
            coverage_counts["found_confident"] += 1

    coverage_lines = [
        "# Coverage Report",
        "",
        "## Summary",
        *[f"- {key}: `{value}`" for key, value in coverage_counts.items()],
        "",
        "| technical_key | status | confidence |",
        "|---|---|---|",
    ]
    for key, parameter in extracted["parameters"].items():
        ev = parameter.get("evidence") or {}
        status = "found" if parameter.get("value") is not None else "missing"
        coverage_lines.append(f"| `{key}` | {status} | {ev.get('confidence', '')} |")
    (reports_dir / "coverage_report.md").write_text("\n".join(coverage_lines) + "\n", encoding="utf-8")

    (reports_dir / "stage1_summary.json").write_text(
        json.dumps(
            {
                "publisher": publisher_result,
                "price_counts": counts,
                "registry_warnings": registry_warnings,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
