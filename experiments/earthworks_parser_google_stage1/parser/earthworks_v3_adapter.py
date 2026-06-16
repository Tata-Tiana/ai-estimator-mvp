from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from source_paths import V3_CANDIDATES_PATH, V3_EARTHWORKS_PATH, V3_LOGICAL_PAGES_PATH, V3_TABLES_PATH


NUMBER_RE = r"\d+(?:[ \u00a0]\d{3})+|\d+(?:[,.]\d+)?"
NUMBER_GROUP_RE = rf"(?:{NUMBER_RE})"


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def parse_number(text: str) -> float:
    return float(text.replace("\u00a0", " ").replace(" ", "").replace(",", "."))


def evidence_from_candidate(candidate: dict[str, Any] | None) -> dict[str, Any]:
    candidate = candidate or {}
    return {
        "evidence_id": candidate.get("evidence_id"),
        "source_pdf": candidate.get("source_pdf"),
        "physical_page_number": candidate.get("physical_page_number"),
        "drawing_sheet_number": candidate.get("drawing_sheet_number"),
        "logical_sheet_title": candidate.get("logical_sheet_title"),
        "logical_sheet_type": candidate.get("logical_sheet_type"),
        "raw_context": (candidate.get("raw_context") or "")[:1200],
        "confidence": candidate.get("confidence", "medium"),
    }


def blank_evidence(raw_context: str = "") -> dict[str, Any]:
    return {
        "evidence_id": None,
        "source_pdf": None,
        "physical_page_number": None,
        "drawing_sheet_number": None,
        "logical_sheet_title": None,
        "logical_sheet_type": None,
        "raw_context": raw_context,
        "confidence": "missing",
    }


def candidates_by_evidence() -> dict[str, dict[str, Any]]:
    candidates = read_json(V3_CANDIDATES_PATH, [])
    return {candidate["evidence_id"]: candidate for candidate in candidates if candidate.get("evidence_id")}


def logical_pages() -> list[dict[str, Any]]:
    return read_json(V3_LOGICAL_PAGES_PATH, [])


def earthworks_page_text(sheet_type: str) -> str:
    parts = []
    for page in logical_pages():
        if page.get("logical_sheet_type") == sheet_type:
            parts.append(page.get("raw_page_text") or page.get("text") or "")
    return "\n".join(parts)


def first_page_for(sheet_type: str) -> dict[str, Any] | None:
    for page in logical_pages():
        if page.get("logical_sheet_type") == sheet_type:
            return page
    return None


def extract_pit_area() -> dict[str, Any]:
    text = earthworks_page_text("earthworks_pit_plan")
    match = re.search(
        rf"Площадь\s+(?:котлована|ктлована|разработки)\s+(?P<value>{NUMBER_RE})\s*м\s*2",
        text,
        re.IGNORECASE,
    )
    if not match:
        return {"value": None, "unit": "м2", "evidence": blank_evidence("Площадь котлована не найдена")}
    page = first_page_for("earthworks_pit_plan") or {}
    return {
        "value": parse_number(match.group("value")),
        "unit": "м2",
        "evidence": {
            "source_pdf": page.get("source_pdf"),
            "physical_page_number": page.get("physical_page_number"),
            "drawing_sheet_number": page.get("drawing_sheet_number"),
            "logical_sheet_title": page.get("logical_sheet_title"),
            "logical_sheet_type": "earthworks_pit_plan",
            "raw_context": match.group(0),
            "confidence": "high",
        },
    }


def extract_pit_depth() -> dict[str, Any]:
    text = earthworks_page_text("earthworks_pit_plan")
    match = re.search(
        rf"Глубина\s+(?:котлована|разработки|выемки)\s*-\s*(?P<raw>{NUMBER_GROUP_RE}\s*-\s*{NUMBER_GROUP_RE}\s*мм)",
        text,
        re.IGNORECASE,
    )
    if not match:
        return {"value": None, "unit": "м", "evidence": blank_evidence("Глубина котлована не найдена")}
    page = first_page_for("earthworks_pit_plan") or {}
    raw = match.group("raw")
    values = [parse_number(item.group(0)) for item in re.finditer(NUMBER_RE, raw)]
    value_m = max(values) / 1000
    return {
        "value": value_m,
        "unit": "м",
        "raw_value": raw,
        "interpretation": "взят максимум из диапазона",
        "needs_elena_review": True,
        "evidence": {
            "source_pdf": page.get("source_pdf"),
            "physical_page_number": page.get("physical_page_number"),
            "drawing_sheet_number": page.get("drawing_sheet_number"),
            "logical_sheet_title": page.get("logical_sheet_title"),
            "logical_sheet_type": "earthworks_pit_plan",
            "raw_context": match.group(0),
            "confidence": "medium",
        },
    }


def extract_geotextile_area() -> dict[str, Any]:
    text = earthworks_page_text("earthworks_pit_plan")
    match = re.search(rf"Геотекст[^\n]{{0,160}}?(?P<value>{NUMBER_RE})\s*м\s*2", text, re.IGNORECASE)
    if match:
        page = first_page_for("earthworks_pit_plan") or {}
        return {
            "value": parse_number(match.group("value")),
            "unit": "м2",
            "evidence": {
                "source_pdf": page.get("source_pdf"),
                "physical_page_number": page.get("physical_page_number"),
                "drawing_sheet_number": page.get("drawing_sheet_number"),
                "logical_sheet_title": page.get("logical_sheet_title"),
                "logical_sheet_type": "earthworks_pit_plan",
                "raw_context": match.group(0),
                "confidence": "medium",
            },
        }

    tables = read_json(V3_TABLES_PATH, [])
    page = first_page_for("earthworks_pit_plan") or {}
    for table in tables:
        if table.get("source_pdf") != page.get("source_pdf"):
            continue
        if table.get("physical_page_number") != page.get("physical_page_number"):
            continue
        for row in table.get("rows") or []:
            row_text = " ".join(cell or "" for cell in row)
            compact = row_text.replace(" ", "")
            if "Геотекст" not in row_text and "53225" not in row_text:
                continue
            if "м2" not in compact:
                continue
            label_match = re.search(r"Геотекст[а-яА-Я\s]*", row_text, re.IGNORECASE)
            after_label = row_text[label_match.end() :] if label_match else row_text
            values = [parse_number(item.group(0)) for item in re.finditer(NUMBER_RE, after_label)]
            project_values = [value for value in values if value >= 10]
            if not project_values:
                continue
            return {
                "value": project_values[0],
                "unit": "м2",
                "evidence": {
                    "source_pdf": page.get("source_pdf"),
                    "physical_page_number": page.get("physical_page_number"),
                    "drawing_sheet_number": page.get("drawing_sheet_number"),
                    "logical_sheet_title": page.get("logical_sheet_title"),
                    "logical_sheet_type": "earthworks_pit_plan",
                    "raw_context": row_text[:1200],
                    "confidence": "medium",
                },
            }
    return {"value": None, "unit": "м2", "evidence": blank_evidence("Геотекстиль не найден")}


def route_code(name: str) -> str:
    return {
        "К1": "K1",
        "К2": "K2",
        "Вода": "water",
        "Эл. кабель": "electric_cable",
    }.get(name, name)


def code_for_pipe(item: dict[str, Any]) -> str:
    text = (item.get("name") or "").lower()
    if "гофр" in text:
        return "corrugated_pipe"
    length = item.get("piece_length_m")
    diameter = item.get("diameter_mm") or 110
    if length is not None:
        return f"pipe_{int(length)}m_d{diameter}"
    return f"pipe_d{diameter}"


def normalize_communication_items(
    items: list[dict[str, Any]],
    evidence_index: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    normalized = []
    seen_codes: set[str] = set()

    def context_len(item: dict[str, Any]) -> int:
        evidence = evidence_index.get(item.get("evidence_id"), {})
        return len(evidence.get("raw_context") or item.get("name") or "")

    for item in sorted(items, key=context_len):
        evidence = evidence_from_candidate(evidence_index.get(item.get("evidence_id")))
        raw_context = evidence.get("raw_context") or item.get("name") or ""
        code = code_for_pipe(item)
        if code in seen_codes and len(raw_context) > 240:
            continue
        if code in seen_codes:
            continue
        seen_codes.add(code)
        normalized.append(
            {
                "code": code,
                "name": item.get("name") or raw_context.splitlines()[0],
                "pipe_length_m": item.get("piece_length_m"),
                "quantity": item.get("qty"),
                "total_length_m": item.get("total_length_m"),
                "include_in_communications": True,
                "evidence": evidence,
            }
        )
    return normalized


def extract_earthworks_parameters() -> dict[str, Any]:
    earthworks = read_json(V3_EARTHWORKS_PATH, {})
    evidence_index = candidates_by_evidence()
    warnings: list[str] = []
    if not earthworks:
        warnings.append(f"Не найден v3 earthworks output: {V3_EARTHWORKS_PATH}")

    sand = earthworks.get("sand") or {}
    trenches = earthworks.get("trenches") or {}
    communications = earthworks.get("communications") or {}

    sand_ev = evidence_from_candidate(evidence_index.get(sand.get("evidence_id")))
    trench_ev = evidence_from_candidate(evidence_index.get((trenches.get("evidence_ids") or [None])[0]))

    routes = []
    for route in trenches.get("trench_routes") or []:
        routes.append(
            {
                "route_code": route_code(route.get("route_name", "")),
                "name": route.get("route_name"),
                "length_m": route.get("length_m"),
                "depth_m": route.get("depth_m"),
                "width_m": route.get("width_m"),
                "volume_m3": route.get("volume_m3"),
                "evidence": trench_ev,
            }
        )

    communication_items = normalize_communication_items(
        communications.get("communication_pipe_items") or [],
        evidence_index,
    )

    geotextile = extract_geotextile_area()
    return {
        "warnings": warnings,
        "parameters": {
            "pit_area_m2": extract_pit_area(),
            "pit_excavation_depth_m": extract_pit_depth(),
            "sand_base_volume_m3": {"value": sand.get("sand_volume_m3"), "unit": "м3", "evidence": sand_ev},
            "trench_routes": {"value": routes, "unit": "таблица", "evidence": trench_ev},
            "trench_volume_m3": {
                "value": trenches.get("trench_volume_total_m3"),
                "unit": "м3",
                "source": "spec_volume" if trenches.get("trench_volume_total_m3") is not None else "routes_calculated",
                "evidence": trench_ev,
            },
            "communications_pipe_items": {"value": communication_items, "unit": "поз.", "evidence": None},
            "communications_length_m": {
                "value": sum(item.get("total_length_m") or 0 for item in communication_items),
                "unit": "м",
                "source": "calculated_from_pipe_items",
                "evidence": None,
            },
            "geotextile_area_m2": geotextile,
            "geotextile_laying_area_m2": {
                "value": geotextile.get("value"),
                "unit": "м2",
                "source": "poc_assumption_equal_to_geotextile_area",
                "evidence": geotextile.get("evidence"),
            },
        },
    }
