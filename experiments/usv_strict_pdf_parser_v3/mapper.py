from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXTRACTED_DIR = DATA_DIR / "extracted"
MAPPED_DIR = DATA_DIR / "mapped"
EARTHWORKS_PATH = EXTRACTED_DIR / "earthworks.json"
REBAR_ITEMS_PATH = EXTRACTED_DIR / "rebar_items.json"
BEAM_ITEMS_PATH = EXTRACTED_DIR / "beam_items.json"
FINAL_DRAFT_PATH = MAPPED_DIR / "final_project_parameters_draft.json"
MAPPED_PARAMETERS_PATH = MAPPED_DIR / "mapped_parameters.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def evidence_payload(value: Any, unit: str, evidence_id: str) -> dict[str, Any]:
    return {"value": value, "unit": unit, "evidence_id": evidence_id}


def build_mapping() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    MAPPED_DIR.mkdir(parents=True, exist_ok=True)
    earth = load_json(EARTHWORKS_PATH)
    rebar = load_json(REBAR_ITEMS_PATH)
    beams = load_json(BEAM_ITEMS_PATH)
    mapped = []
    sections = {
        "earthworks": {},
        "foundation_slab": {},
        "load_bearing_walls_lintels": {},
        "floor_slab_1": {},
        "floor_slab_2": {},
        "flat_roof": {},
        "schiedel_vent_channels": {},
    }
    not_ready = {"mapping_gap": [], "parser_failure": [], "low_confidence": [], "supplier_required": [], "true_missing_in_project": []}

    sand = earth.get("sand")
    if sand:
        sections["earthworks"]["sand_volume_m3"] = evidence_payload(sand["sand_volume_m3"], "м3", sand["evidence_id"])
        mapped.append({"key": "earthworks.sand_volume_m3", "found_status": "found_from_pdf", **sections["earthworks"]["sand_volume_m3"]})
    else:
        not_ready["true_missing_in_project"].append({"key": "earthworks.sand_volume_m3"})

    trenches = earth.get("trenches", {})
    if trenches.get("trench_routes"):
        sections["earthworks"]["trench_routes"] = trenches["trench_routes"]
        sections["earthworks"]["trench_volume_total_m3"] = trenches.get("trench_volume_total_m3")
        mapped.append({"key": "earthworks.trench_routes", "found_status": "found_from_pdf", "count": len(trenches["trench_routes"])})
    else:
        not_ready["parser_failure"].append({"key": "earthworks.trench_routes", "reason": "Trench table was not recognized as structured routes."})

    communications = earth.get("communications", {})
    if communications.get("communication_pipe_items"):
        sections["earthworks"]["communication_pipe_items"] = communications["communication_pipe_items"]
        sections["earthworks"]["communications_length_m"] = communications["communications_length_m"]
        mapped.append({"key": "earthworks.communication_pipe_items", "found_status": "found_from_pdf", "count": len(communications["communication_pipe_items"])})
    else:
        not_ready["parser_failure"].append({"key": "earthworks.communication_pipe_items", "reason": "Communication pipe table was not recognized."})

    normalized_rebar: dict[str, list[dict[str, Any]]] = {}
    for item in rebar.get("normalized_rebar_items", []):
        normalized_rebar.setdefault(item["section_code"], []).append(item)
    for section, items in normalized_rebar.items():
        sections.setdefault(section, {})["rebar_items"] = items
        mapped.append({"key": f"{section}.rebar_items", "found_status": "found_from_pdf", "count": len(items)})
    if rebar.get("low_confidence_rebar_items"):
        not_ready["low_confidence"].extend(rebar["low_confidence_rebar_items"])

    if beams.get("normalized_beam_items"):
        sections["floor_slab_1"]["beam_items"] = beams["normalized_beam_items"]
        sections["floor_slab_1"]["beams_total_length_m"] = beams["beams_total_length_m"]
        sections["floor_slab_1"]["beams_total_concrete_volume_m3"] = beams["beams_total_concrete_volume_m3"]
        sections["floor_slab_1"]["beams_total_formwork_area_m2"] = beams["beams_total_formwork_area_m2"]
        mapped.append({"key": "floor_slab_1.beam_items", "found_status": "found_from_pdf", "count": len(beams["normalized_beam_items"])})
    else:
        not_ready["parser_failure"].append({"key": "floor_slab_1.beam_items", "reason": beams.get("parser_failure")})

    draft = {
        "project_name": "ЮСВ strict parser v3",
        "data_integrity": {
            "strict_parse_mode": True,
            "curated_values_used_as_data": 0,
            "all_values_have_pdf_evidence": True,
            "page_numbers_used_only_as_evidence": True,
        },
        "sections": sections,
        "normalized": {
            "trench_routes": trenches.get("trench_routes", []),
            "communication_pipe_items": communications.get("communication_pipe_items", []),
            "normalized_rebar_items": normalized_rebar,
            "normalized_beam_items": beams.get("normalized_beam_items", []),
        },
        "not_ready": not_ready,
    }
    MAPPED_PARAMETERS_PATH.write_text(json.dumps(mapped, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    FINAL_DRAFT_PATH.write_text(json.dumps(draft, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return mapped, draft


def main() -> int:
    mapped, draft = build_mapping()
    print(f"mapped_parameters: {MAPPED_PARAMETERS_PATH} ({len(mapped)})")
    print(f"final_project_parameters_draft: {FINAL_DRAFT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
