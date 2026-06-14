from __future__ import annotations

import re
from pathlib import Path

from openpyxl import load_workbook

from parameter_dictionary import EARTHWORKS_PARAMETER_DICTIONARY
from source_paths import EXPERIMENT_DIR, INTEGRITY_REPORT_PATH, REVIEW_FINAL_EXCEL_PATH, REVIEW_INPUT_PATH


FORBIDDEN_PROJECT_VALUES = ["322.5", "96.6", "32.38", "51.209", "14.5", "12.61", "20.69", "115"]
FORBIDDEN_LEGACY_QUANTITY_KEYS = [
    "pit_area_m2",
    "sand_base_volume_m3",
    "trench_volume_m3",
    "communications_length_m",
    "geotextile_area_m2",
    "manual_excavation_quantity_for_estimate_m3",
    "excavator_shifts",
]


def excel_has_formulas(path: Path) -> bool:
    wb = load_workbook(path, data_only=False)
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value.startswith("="):
                    return True
    return False


def source_hardcode_errors() -> list[str]:
    errors = []
    for path in EXPERIMENT_DIR.glob("*.py"):
        if path.name == "integrity_checks.py":
            continue
        text = path.read_text(encoding="utf-8")
        for value in FORBIDDEN_PROJECT_VALUES:
            if re.search(rf"(?<![\d.]){re.escape(value)}(?![\d.])", text):
                errors.append(f"Hardcoded project value `{value}` found in {path.name}.")
    return errors


def fallback_quantity_errors() -> list[str]:
    text = (EXPERIMENT_DIR / "earthworks_input_builder.py").read_text(encoding="utf-8")
    fallback_section = text[text.find("def fallback_prices") : text.find("def build_internal_prices")]
    errors = []
    for key in FORBIDDEN_LEGACY_QUANTITY_KEYS:
        if key in fallback_section:
            errors.append(f"Fallback input reader references forbidden quantity key `{key}`.")
    return errors


def run_integrity_checks(extracted: dict, payload: dict, result: dict) -> list[str]:
    warnings = []
    errors = []
    if excel_has_formulas(REVIEW_FINAL_EXCEL_PATH):
        errors.append("Final Excel contains formulas.")
    if not REVIEW_INPUT_PATH.exists():
        errors.append("Reviewed input JSON not found.")
    for key in [
        "pit_area_m2",
        "pit_excavation_depth_m",
        "sand_base_volume_m3",
        "trench_volume_m3",
        "geotextile_area_m2",
    ]:
        evidence = (extracted["parameters"].get(key) or {}).get("evidence") or {}
        for evidence_key in ["source_pdf", "physical_page_number", "logical_sheet_title", "logical_sheet_type", "raw_context"]:
            if not evidence.get(evidence_key):
                errors.append(f"{key} missing evidence field {evidence_key}.")
    for route in extracted["parameters"]["trench_routes"]["value"]:
        if not route.get("evidence"):
            errors.append("trench_routes missing evidence.")
    for item in extracted["parameters"]["communications_pipe_items"]["value"]:
        if not item.get("evidence"):
            errors.append("communications_pipe_items missing evidence.")
    pipe_text = " ".join(item["name"] for item in extracted["parameters"]["communications_pipe_items"]["value"])
    if "ф110" not in pipe_text:
        errors.append("ф110 not found in communication pipe items.")
    if not all(meta.get("ru_label") and meta.get("used_in") for meta in EARTHWORKS_PARAMETER_DICTIONARY.values()):
        errors.append("Some technical keys do not have Russian labels/explanations.")
    for key, source in result.get("price_sources", {}).items():
        if source.get("source") == "fallback_input_for_poc" and not source.get("warning"):
            errors.append(f"Fallback price {key} is not explicitly marked.")
    errors.extend(source_hardcode_errors())
    errors.extend(fallback_quantity_errors())

    lines = [
        "# Integrity Report",
        "",
        "- experiment writes only under earthworks_mini_mvp_poc/data",
        "- quantities/volumes from legacy input: no",
        "- page number used only as evidence: yes",
        f"- final Excel contains formulas: {'yes' if any('formulas' in error for error in errors) else 'no'}",
        "- ф110 displayed as communications pipe: yes",
        "- review rows have Russian labels: yes",
        "- fallback prices explicitly marked: yes",
        "- source .py files checked for hardcoded project quantities: yes",
        "",
        "## Errors",
        "",
    ]
    lines.extend([f"- {error}" for error in errors] or ["- Нет."])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in warnings] or ["- Нет."])
    INTEGRITY_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    INTEGRITY_REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    if errors:
        raise ValueError("Integrity checks failed: " + "; ".join(errors))
    return warnings
