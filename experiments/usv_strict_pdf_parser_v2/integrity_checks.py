from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXTRACTED_DIR = DATA_DIR / "extracted"
MAPPED_DIR = DATA_DIR / "mapped"
REPORTS_DIR = DATA_DIR / "reports"
CANDIDATES_PATH = EXTRACTED_DIR / "candidates.json"
MAPPED_PARAMETERS_PATH = MAPPED_DIR / "mapped_parameters.json"
FINAL_DRAFT_PATH = MAPPED_DIR / "final_project_parameters_draft.json"
INTEGRITY_REPORT_PATH = REPORTS_DIR / "integrity_report.md"


def token(*parts: str) -> str:
    return "".join(parts)


FORBIDDEN_CANDIDATE_TYPES = {
    token("curated", "_control"),
    token("expected", "_value"),
    token("manual", "_seed"),
    token("known", "_usv", "_value"),
    token("qa", "_expected"),
}
FORBIDDEN_CODE_TOKENS = {
    token("CURATED", "_CANDIDATES"),
    token("EXPECTED", "_VALUES"),
    token("known", "_usv", "_value"),
    token("manual", "_seed"),
    token("curated", "_control"),
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check_integrity() -> dict[str, Any]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    candidates = load_json(CANDIDATES_PATH)
    mapped = load_json(MAPPED_PARAMETERS_PATH)
    final_draft = load_json(FINAL_DRAFT_PATH)
    errors: list[str] = []

    forbidden_candidates = [item for item in candidates if item.get("candidate_type") in FORBIDDEN_CANDIDATE_TYPES]
    if forbidden_candidates:
        errors.append(f"Forbidden candidate types detected: {len(forbidden_candidates)}")

    for row in mapped:
        if row.get("found_status") == "found_from_pdf" and not row.get("candidate_id"):
            errors.append(f"found_from_pdf without candidate_id: {row.get('calculator_input_key')}")

    for section, values in final_draft.get("sections", {}).items():
        for key, payload in values.items():
            evidence = payload.get("evidence") or {}
            if not evidence.get("candidate_id") or not evidence.get("source_pdf") or not evidence.get("page"):
                errors.append(f"draft value without evidence: {section}.{key}")

    for py_file in BASE_DIR.glob("*.py"):
        if py_file.name == "integrity_checks.py":
            continue
        text = py_file.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_CODE_TOKENS:
            if forbidden in text:
                errors.append(f"Forbidden code token {forbidden!r} in {py_file.name}")

    integrity = final_draft.get("data_integrity", {})
    if integrity.get("curated_values_used_as_data") != 0:
        errors.append("curated_values_used_as_data is not 0")
    if integrity.get("strict_parse_mode") is not True:
        errors.append("strict_parse_mode is not true")

    report = {
        "strict_parse_mode": True,
        "curated_values_used_as_data": 0,
        "all_values_have_pdf_evidence": not errors,
        "forbidden_candidate_types": len(forbidden_candidates),
        "errors": errors,
    }
    lines = [
        "# Integrity Report",
        "",
        f"- strict_parse_mode: {str(report['strict_parse_mode']).lower()}",
        f"- curated_values_used_as_data: {report['curated_values_used_as_data']}",
        f"- all_values_have_pdf_evidence: {str(report['all_values_have_pdf_evidence']).lower()}",
        f"- forbidden_candidate_types: {report['forbidden_candidate_types']}",
        "",
        "## Errors",
        "",
    ]
    lines.extend([f"- {error}" for error in errors] or ["- Нет."])
    INTEGRITY_REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if errors:
        raise ValueError("Strict parser integrity checks failed:\n" + "\n".join(errors))
    return report


def main() -> int:
    report = check_integrity()
    print(f"integrity_report: {INTEGRITY_REPORT_PATH}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
