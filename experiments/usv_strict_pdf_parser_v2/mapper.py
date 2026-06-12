from __future__ import annotations

from collections import defaultdict
import json
import re
from pathlib import Path
from typing import Any

from parameter_targets import SECTION_CODES, build_targets


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXTRACTED_DIR = DATA_DIR / "extracted"
MAPPED_DIR = DATA_DIR / "mapped"
CANDIDATES_PATH = EXTRACTED_DIR / "candidates.json"
SPEC_ROWS_PATH = EXTRACTED_DIR / "spec_rows.json"
MAPPED_PARAMETERS_PATH = MAPPED_DIR / "mapped_parameters.json"
NORMALIZED_PARAMETERS_PATH = MAPPED_DIR / "normalized_parameters.json"
FINAL_DRAFT_PATH = MAPPED_DIR / "final_project_parameters_draft.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def norm(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).lower().replace("ё", "е").replace(",", ".")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"(\d)\.\s+(\d)", r"\1.\2", text)
    return text


def unit_matches(candidate_unit: str, target_units: list[str]) -> bool:
    if not target_units:
        return True
    candidate_unit = norm(candidate_unit).replace(".", "")
    normalized_targets = {norm(unit).replace(".", "") for unit in target_units}
    if candidate_unit in normalized_targets:
        return True
    if candidate_unit in {"мп", "пм"} and "м/п" in normalized_targets:
        return True
    return False


def keyword_score(text: str, keywords: list[str]) -> tuple[int, list[str]]:
    low = norm(text)
    matched = [keyword for keyword in keywords if norm(keyword) in low]
    return len(matched), matched


def page_score(text: str, hints: list[str]) -> tuple[int, list[str]]:
    low = norm(text)
    matched = [hint for hint in hints if norm(hint) in low]
    return len(matched), matched


def candidate_text(candidate: dict[str, Any]) -> str:
    return " ".join(
        str(candidate.get(key, ""))
        for key in ("page_title", "raw_label", "raw_context")
    )


def score_candidate(target: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    hints = target.get("mapping_hints") or {}
    keywords = hints.get("keywords") or []
    page_titles = hints.get("page_titles") or []
    units = hints.get("units") or []
    text = candidate_text(candidate)
    label_text = " ".join(str(candidate.get(key, "")) for key in ("raw_label", "page_title"))
    kw_count, matched_keywords = keyword_score(label_text, keywords)
    context_kw_count, context_keywords = keyword_score(text, keywords)
    page_count, matched_pages = page_score(text, page_titles)
    unit_ok = unit_matches(candidate.get("unit", ""), units)
    score = kw_count * 3 + page_count * 2 + (2 if unit_ok else 0)
    if candidate.get("candidate_type") == "parsed_spec_row":
        score += 1
    return {
        "score": score,
        "matched_keywords": matched_keywords,
        "context_keywords": context_keywords,
        "context_kw_count": context_kw_count,
        "matched_pages": matched_pages,
        "unit_ok": unit_ok,
    }


def choose_candidate(target: dict[str, Any], candidates: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, str, str]:
    scored = []
    for candidate in candidates:
        score = score_candidate(target, candidate)
        if score["score"] > 0:
            scored.append((score["score"], score, candidate))
    scored.sort(key=lambda item: item[0], reverse=True)
    if not scored:
        return None, "true_missing_in_project", "No similar PDF candidate matched target hints."

    best_score, best_meta, best = scored[0]
    keywords = target.get("mapping_hints", {}).get("keywords") or []
    keyword_threshold = max(1, min(2, len(keywords)))
    if any(re.search(r"\d", keyword) for keyword in keywords):
        keyword_threshold = len(keywords)
    page_ok = not target.get("mapping_hints", {}).get("page_titles") or len(best_meta["matched_pages"]) > 0
    strong = len(best_meta["matched_keywords"]) >= keyword_threshold and best_meta["unit_ok"] and page_ok
    similar = best_meta["context_kw_count"] > 0 or len(best_meta["matched_pages"]) > 0

    if strong:
        if best.get("confidence") == "low" or best.get("unit") == "unknown":
            return best, "low_confidence", "Matched target hints, but source candidate has low confidence or unknown unit."
        return best, "found_from_pdf", (
            "Matched by keywords "
            + ", ".join(best_meta["matched_keywords"])
            + (f"; page hints {', '.join(best_meta['matched_pages'])}" if best_meta["matched_pages"] else "")
            + f"; unit {best.get('unit')}"
        )
    if similar:
        return best, "mapping_gap", "PDF has similar data, but keywords/unit/page context are not strong enough for automatic mapping."
    return None, "true_missing_in_project", "No sufficiently similar PDF candidate found."


def map_targets() -> list[dict[str, Any]]:
    MAPPED_DIR.mkdir(parents=True, exist_ok=True)
    targets = build_targets()
    candidates = load_json(CANDIDATES_PATH)
    mapped = []

    for target in targets:
        if target["required_status"] == "SUPPLIER_INPUT":
            candidate, status, reason = choose_candidate(target, candidates)
            found_status = "supplier_required"
        elif target["required_status"] == "MANUAL_REQUIRED":
            candidate, status, reason = None, "manual_required", "Manual estimator decision required."
            found_status = "manual_required"
        else:
            candidate, found_status, reason = choose_candidate(target, candidates)

        value = candidate.get("raw_value") if candidate else None
        unit = candidate.get("unit") if candidate else target.get("unit", "")
        confidence = candidate.get("confidence") if candidate else ""
        needs_review = found_status != "found_from_pdf" or target.get("show_to_elena", True)
        mapped.append(
            {
                "section_name": target["section_name"],
                "section_code": target["section_code"],
                "calculator_input_key": target["calculator_input_key"],
                "target_label": target["label"],
                "required_status": target["required_status"],
                "found_status": found_status,
                "value": value,
                "unit": unit,
                "candidate_id": candidate.get("candidate_id") if candidate else "",
                "source_pdf": candidate.get("source_pdf") if candidate else "",
                "page": candidate.get("page") if candidate else None,
                "page_title": candidate.get("page_title") if candidate else "",
                "source_fragment": candidate.get("raw_context") if candidate else "",
                "confidence": confidence,
                "needs_elena_review": needs_review,
                "mapping_reason": reason,
                "mapping_hints": target.get("mapping_hints", {}),
            }
        )

    dump_json(MAPPED_PARAMETERS_PATH, mapped)
    normalized = build_normalized_parameters(candidates, load_json(SPEC_ROWS_PATH))
    dump_json(NORMALIZED_PARAMETERS_PATH, normalized)
    dump_json(FINAL_DRAFT_PATH, build_final_project_parameters_draft(mapped, normalized))
    return mapped


def parse_rebar_from_text(text: str) -> dict[str, Any] | None:
    match = re.search(r"(?:ф|ø|d)\s*(?P<diameter>\d{1,2}).{0,20}?(?P<steel>A\d{3}\w*)?", text, re.IGNORECASE)
    if not match:
        return None
    return {
        "diameter_mm": int(match.group("diameter")),
        "steel_class": (match.group("steel") or "").upper(),
    }


def build_normalized_parameters(candidates: list[dict[str, Any]], spec_rows: list[dict[str, Any]]) -> dict[str, Any]:
    normalized_rebar_items: dict[str, list[dict[str, Any]]] = defaultdict(list)
    normalized_roof_abutments: list[dict[str, Any]] = []
    normalized_wall_block_volumes: list[dict[str, Any]] = []
    communication_pipe_items: list[dict[str, Any]] = []
    trench_routes: list[dict[str, Any]] = []
    normalized_beam_items: list[dict[str, Any]] = []

    for candidate in candidates:
        text = candidate_text(candidate)
        low = norm(text)
        rebar = parse_rebar_from_text(text)
        if rebar and candidate.get("unit") in {"м/п", "кг", "unknown"}:
            section = "unknown"
            if "фундамент" in low:
                section = "foundation_slab"
            elif "3.480" in low or "3,480" in low:
                section = "floor_slab_1"
            elif "4.680" in low or "4,680" in low:
                section = "floor_slab_2"
            elif "перемыч" in low:
                section = "load_bearing_walls_lintels"
            item = {
                **rebar,
                "quantity_value": candidate.get("raw_value"),
                "quantity_unit": candidate.get("unit"),
                "spec_length_m": candidate.get("raw_value") if candidate.get("unit") == "м/п" else None,
                "source_weight_kg": candidate.get("raw_value") if candidate.get("unit") == "кг" else None,
                "candidate_id": candidate["candidate_id"],
                "source_pdf": candidate["source_pdf"],
                "page": candidate["page"],
                "raw_context": candidate.get("raw_context", ""),
                "confidence": candidate.get("confidence", ""),
            }
            normalized_rebar_items[section].append(item)
        if "примыкан" in low and candidate.get("unit") == "м/п":
            normalized_roof_abutments.append(
                {
                    "label": candidate.get("raw_label"),
                    "length_m": candidate.get("raw_value"),
                    "candidate_id": candidate["candidate_id"],
                    "source_pdf": candidate["source_pdf"],
                    "page": candidate["page"],
                    "raw_context": candidate.get("raw_context", ""),
                }
            )
        if "газобет" in low and candidate.get("unit") == "м3":
            normalized_wall_block_volumes.append(
                {
                    "label": candidate.get("raw_label"),
                    "volume_m3": candidate.get("raw_value"),
                    "candidate_id": candidate["candidate_id"],
                    "source_pdf": candidate["source_pdf"],
                    "page": candidate["page"],
                    "raw_context": candidate.get("raw_context", ""),
                }
            )
        if "транше" in low or re.search(r"\bк[12]\b", low):
            if candidate.get("unit") in {"м", "м3"}:
                trench_routes.append(
                    {
                        "label": candidate.get("raw_label"),
                        "value": candidate.get("raw_value"),
                        "unit": candidate.get("unit"),
                        "candidate_id": candidate["candidate_id"],
                        "source_pdf": candidate["source_pdf"],
                        "page": candidate["page"],
                        "raw_context": candidate.get("raw_context", ""),
                    }
                )
        if any(word in low for word in ("труба", "канализация", "вода", "кабель")) and candidate.get("unit") in {"м", "м/п", "шт"}:
            communication_pipe_items.append(
                {
                    "name": candidate.get("raw_label"),
                    "value": candidate.get("raw_value"),
                    "unit": candidate.get("unit"),
                    "candidate_id": candidate["candidate_id"],
                    "source_pdf": candidate["source_pdf"],
                    "page": candidate["page"],
                    "raw_context": candidate.get("raw_context", ""),
                }
            )
        if re.search(r"\bб-\d\b", low) or "балк" in low:
            normalized_beam_items.append(
                {
                    "raw_label": candidate.get("raw_label"),
                    "value": candidate.get("raw_value"),
                    "unit": candidate.get("unit"),
                    "candidate_id": candidate["candidate_id"],
                    "source_pdf": candidate["source_pdf"],
                    "page": candidate["page"],
                    "raw_context": candidate.get("raw_context", ""),
                }
            )

    return {
        "normalized_rebar_items": dict(normalized_rebar_items),
        "normalized_beam_items": normalized_beam_items,
        "trench_routes": trench_routes,
        "communication_pipe_items": communication_pipe_items,
        "normalized_roof_abutments": normalized_roof_abutments,
        "normalized_wall_block_volumes": normalized_wall_block_volumes,
    }


def build_final_project_parameters_draft(mapped: list[dict[str, Any]], normalized: dict[str, Any]) -> dict[str, Any]:
    sections = {code: {} for code in SECTION_CODES.values()}
    not_ready = {
        "true_missing_in_project": [],
        "low_confidence": [],
        "mapping_gap": [],
        "supplier_required": [],
        "manual_required": [],
    }
    for row in mapped:
        status = row["found_status"]
        if status == "found_from_pdf" and row.get("confidence") in {"high", "medium"} and row.get("candidate_id"):
            sections[row["section_code"]][row["calculator_input_key"]] = {
                "value": row["value"],
                "unit": row["unit"],
                "evidence": {
                    "candidate_id": row["candidate_id"],
                    "source_pdf": row["source_pdf"],
                    "page": row["page"],
                    "source_fragment": row["source_fragment"],
                },
            }
        elif status in not_ready:
            not_ready[status].append(
                {
                    "section_name": row["section_name"],
                    "calculator_input_key": row["calculator_input_key"],
                    "label": row["target_label"],
                    "value": row.get("value"),
                    "unit": row.get("unit"),
                    "candidate_id": row.get("candidate_id"),
                    "source_pdf": row.get("source_pdf"),
                    "page": row.get("page"),
                    "confidence": row.get("confidence"),
                    "mapping_reason": row.get("mapping_reason"),
                }
            )
    return {
        "project_name": "ЮСВ 2026 strict parser v2",
        "data_integrity": {
            "strict_parse_mode": True,
            "curated_values_used_as_data": 0,
            "all_values_have_pdf_evidence": True,
        },
        "sections": sections,
        "normalized": normalized,
        "not_ready": not_ready,
    }


def main() -> int:
    mapped = map_targets()
    print(f"mapped_parameters: {MAPPED_PARAMETERS_PATH} ({len(mapped)})")
    print(f"normalized_parameters: {NORMALIZED_PARAMETERS_PATH}")
    print(f"final_project_parameters_draft: {FINAL_DRAFT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
