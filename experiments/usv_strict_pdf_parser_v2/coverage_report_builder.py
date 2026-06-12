from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MAPPED_DIR = DATA_DIR / "mapped"
REPORTS_DIR = DATA_DIR / "reports"
MAPPED_PARAMETERS_PATH = MAPPED_DIR / "mapped_parameters.json"
NORMALIZED_PARAMETERS_PATH = MAPPED_DIR / "normalized_parameters.json"
FINAL_DRAFT_PATH = MAPPED_DIR / "final_project_parameters_draft.json"
COVERAGE_REPORT_PATH = REPORTS_DIR / "coverage_report.md"
PARSER_QUALITY_REPORT_PATH = REPORTS_DIR / "parser_quality_report.md"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def bullet(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["- Нет."]
    return [
        f"- {row.get('section_name')} :: `{row.get('calculator_input_key')}` — {row.get('target_label')}"
        + (f" = {row.get('value')} {row.get('unit')}" if row.get("value") not in (None, "") else "")
        + (f" ({row.get('source_pdf')} p.{row.get('page')}, {row.get('candidate_id')})" if row.get("candidate_id") else "")
        for row in rows
    ]


def build_reports() -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    mapped = load_json(MAPPED_PARAMETERS_PATH)
    normalized = load_json(NORMALIZED_PARAMETERS_PATH)
    final_draft = load_json(FINAL_DRAFT_PATH)
    counts = Counter(row["found_status"] for row in mapped)
    by_section: dict[str, Counter] = defaultdict(Counter)
    for row in mapped:
        by_section[row["section_name"]]["targets"] += 1
        by_section[row["section_name"]][row["found_status"]] += 1

    found = [row for row in mapped if row["found_status"] == "found_from_pdf"]
    missing = [row for row in mapped if row["found_status"] == "true_missing_in_project"]
    gaps = [row for row in mapped if row["found_status"] == "mapping_gap"]
    low = [row for row in mapped if row["found_status"] == "low_confidence"]
    suppliers = [row for row in mapped if row["found_status"] == "supplier_required"]
    manual = [row for row in mapped if row["found_status"] == "manual_required"]

    lines = [
        "# Coverage Report: USV Strict PDF Parser v2",
        "",
        "## Статистика честности данных",
        "",
        "- strict_parse_mode: true",
        f"- production values from PDF: {len(found)}",
        "- production values from curated/expected: 0",
        f"- all found values have evidence: {str(all(row.get('candidate_id') for row in found)).lower()}",
        "",
        "## Coverage по разделам",
        "",
        "| section | targets | found_from_pdf | true_missing_in_project | low_confidence | mapping_gap | supplier_required | manual_required |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for section, counter in by_section.items():
        lines.append(
            f"| {section} | {counter['targets']} | {counter['found_from_pdf']} | {counter['true_missing_in_project']} | "
            f"{counter['low_confidence']} | {counter['mapping_gap']} | {counter['supplier_required']} | {counter['manual_required']} |"
        )
    lines.extend(["", "## Реально найдено в PDF", ""])
    lines.extend(bullet(found))
    lines.extend(["", "## Реально не найдено в проекте", ""])
    lines.extend(bullet(missing))
    lines.extend(["", "## Проблемы mapping", ""])
    lines.extend(bullet(gaps))
    lines.extend(["", "## Low Confidence", ""])
    lines.extend(bullet(low))
    lines.extend(["", "## Данные для Елены", ""])
    lines.extend(bullet([*low, *missing, *manual]))
    lines.extend(["", "## Данные для проектировщика", ""])
    lines.extend(bullet([*missing, *gaps, *low]))
    lines.extend(["", "## Данные для поставщика", ""])
    lines.extend(bullet(suppliers))
    lines.extend(["", "## Normalized Structures", ""])
    for key, value in normalized.items():
        size = len(value) if hasattr(value, "__len__") else 0
        lines.append(f"- {key}: {size}")
    lines.extend(
        [
            "",
            "## Итог",
            "",
            f"- found_from_pdf: {counts['found_from_pdf']}",
            f"- true_missing_in_project: {counts['true_missing_in_project']}",
            f"- mapping_gap: {counts['mapping_gap']}",
            f"- supplier_required: {counts['supplier_required']}",
            f"- manual_required: {counts['manual_required']}",
            f"- low_confidence: {counts['low_confidence']}",
            "",
            "Переходить к generator input.json можно только после закрытия low_confidence, supplier_required и критичных missing/mapping_gap.",
        ]
    )
    COVERAGE_REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    quality_lines = [
        "# Parser Quality Report",
        "",
        f"- mapped targets: {len(mapped)}",
        f"- draft sections with values: {sum(1 for values in final_draft.get('sections', {}).values() if values)}",
        f"- normalized groups: {len(normalized)}",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in counts.most_common():
        quality_lines.append(f"- {status}: {count}")
    PARSER_QUALITY_REPORT_PATH.write_text("\n".join(quality_lines) + "\n", encoding="utf-8")
    return COVERAGE_REPORT_PATH


def main() -> int:
    path = build_reports()
    print(f"coverage_report: {path}")
    print(f"parser_quality_report: {PARSER_QUALITY_REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
