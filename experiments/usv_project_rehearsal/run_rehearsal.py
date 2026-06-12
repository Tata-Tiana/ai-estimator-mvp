from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from build_coverage_report import build_coverage_report
from build_review_pack import build_review_pack
from extract_project_candidates import extract_project_candidates
from mapping_rules import SECTION_CODES, load_parameter_registry, map_parameters


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MAPPED_PATH = DATA_DIR / "mapped_parameters.json"
FINAL_DRAFT_PATH = DATA_DIR / "final_project_parameters_draft.json"


def dump_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_final_project_parameters_draft(mapped: list[dict]) -> dict:
    sections = {code: {} for code in SECTION_CODES.values()}
    missing = []
    conflicts = []
    supplier_required = []
    manual_required = []

    for row in mapped:
        status = row.get("found_status")
        section_code = row.get("section_code") or SECTION_CODES.get(row.get("section_name"), "")
        key = row.get("calculator_input_key")
        if status == "found" and row.get("confidence") in {"high", "medium"} and row.get("required_status") == "AUTO_PROJECT":
            if section_code and key:
                sections.setdefault(section_code, {})[key] = {
                    "value": row.get("value_from_pdf"),
                    "unit": row.get("unit"),
                    "source_pdf": row.get("source_pdf"),
                    "page": row.get("page"),
                    "confidence": row.get("confidence"),
                }
        elif status == "missing":
            missing.append(row)
        elif status == "conflict" or status == "low_confidence":
            conflicts.append(row)
        elif status == "supplier_required":
            supplier_required.append(row)
        elif status == "manual_required":
            manual_required.append(row)

    def slim(rows: list[dict]) -> list[dict]:
        return [
            {
                "section_name": row.get("section_name"),
                "calculator_input_key": row.get("calculator_input_key"),
                "label": row.get("label"),
                "found_status": row.get("found_status"),
                "value_from_pdf": row.get("value_from_pdf"),
                "unit": row.get("unit"),
                "source_pdf": row.get("source_pdf"),
                "page": row.get("page"),
                "confidence": row.get("confidence"),
                "notes": row.get("notes"),
            }
            for row in rows
        ]

    return {
        "project_name": "ЮСВ 2026 rehearsal",
        "sources": ["usv_2026_kr1.pdf", "usv_2026_kr2.pdf"],
        "sections": sections,
        "missing": slim(missing),
        "conflicts": slim(conflicts),
        "supplier_required": slim(supplier_required),
        "manual_required": slim(manual_required),
    }


def run_rehearsal() -> dict:
    candidates = extract_project_candidates()
    registry = load_parameter_registry()
    mapped = map_parameters(registry, candidates)
    dump_json(MAPPED_PATH, mapped)
    final_draft = build_final_project_parameters_draft(mapped)
    dump_json(FINAL_DRAFT_PATH, final_draft)
    review_pack = build_review_pack()
    coverage_report = build_coverage_report()
    counts = Counter(row["found_status"] for row in mapped)
    return {
        "review_pack": review_pack,
        "coverage_report": coverage_report,
        "mapped_parameters": MAPPED_PATH,
        "final_project_parameters_draft": FINAL_DRAFT_PATH,
        "stats": counts,
        "total_mapped": len(mapped),
    }


def main() -> int:
    result = run_rehearsal()
    print("USV project rehearsal completed")
    print(f"- review_pack: {result['review_pack']}")
    print(f"- coverage_report: {result['coverage_report']}")
    print(f"- mapped_parameters: {result['mapped_parameters']}")
    print(f"- final_project_parameters_draft: {result['final_project_parameters_draft']}")
    print(f"- total_mapped: {result['total_mapped']}")
    print("- coverage:")
    for status, count in result["stats"].most_common():
        print(f"  {status}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
