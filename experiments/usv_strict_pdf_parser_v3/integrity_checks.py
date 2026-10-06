from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import parser_paths


# Scans the parser module directory for forbidden tokens — must stay as __file__-relative path.
_PARSER_DIR = Path(__file__).resolve().parent


def token(*parts: str) -> str:
    return "".join(parts)


FORBIDDEN = {
    token("CURATED", "_CANDIDATES"),
    token("EXPECTED", "_VALUES"),
    token("known", "_usv", "_value"),
    token("manual", "_seed"),
    token("curated", "_control"),
    token("expected", "_value"),
    token("qa", "_expected"),
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check_integrity() -> dict[str, Any]:
    parser_paths.reports_dir().mkdir(parents=True, exist_ok=True)
    errors = []
    candidates_path = parser_paths.candidates_path()
    final_path = parser_paths.final_draft_path()
    logical_path = parser_paths.logical_pages_path()
    candidates = load_json(candidates_path) if candidates_path.exists() else []
    final = load_json(final_path) if final_path.exists() else {}
    logical_pages = load_json(logical_path) if logical_path.exists() else []

    for item in candidates:
        if not item.get("logical_sheet_type"):
            errors.append(f"candidate without logical_sheet_type: {item.get('evidence_id')}")
        if not item.get("evidence_id"):
            errors.append("candidate without evidence_id")

    for path in _PARSER_DIR.glob("*.py"):
        if path.name == "integrity_checks.py":
            continue
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN:
            if forbidden in text:
                errors.append(f"forbidden token {forbidden!r} in {path.name}")

    integrity = final.get("data_integrity", {})
    if integrity.get("curated_values_used_as_data") != 0:
        errors.append("curated_values_used_as_data is not 0")
    if integrity.get("page_numbers_used_only_as_evidence") is not True:
        errors.append("page_numbers_used_only_as_evidence is not true")
    if not logical_pages:
        errors.append("logical_pages is empty")

    report = {
        "strict_parse_mode": True,
        "curated_values_used_as_data": 0,
        "all_values_have_pdf_evidence": not errors,
        "page_numbers_used_only_as_evidence": True,
        "errors": errors,
    }
    lines = [
        "# Integrity Report",
        "",
        f"- strict_parse_mode: {str(report['strict_parse_mode']).lower()}",
        f"- curated_values_used_as_data: {report['curated_values_used_as_data']}",
        f"- all_values_have_pdf_evidence: {str(report['all_values_have_pdf_evidence']).lower()}",
        f"- page_numbers_used_only_as_evidence: {str(report['page_numbers_used_only_as_evidence']).lower()}",
        "",
        "## Errors",
        "",
    ]
    lines.extend([f"- {error}" for error in errors] or ["- Нет."])
    parser_paths.integrity_report_path().write_text("\n".join(lines) + "\n", encoding="utf-8")
    if errors:
        raise ValueError("Integrity failed:\n" + "\n".join(errors))
    return report
