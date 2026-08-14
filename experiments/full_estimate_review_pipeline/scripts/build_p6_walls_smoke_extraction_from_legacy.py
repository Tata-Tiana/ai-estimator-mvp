from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


LEGACY_SECTION = "load_bearing_walls_lintels"
P6_SECTION = "load_bearing_walls_lintels_p6"


WALL_ROLE_TO_ZONE = {
    "main_walls": ("floor_1", "Кладка стен 1-го этажа", "main_walls"),
    "floor_2": ("floor_2", "Кладка стен 2-го этажа", "second_light"),
    "parapet": ("parapet", "Парапет", "parapet"),
}


def _found_items(section: dict[str, Any], *, target_code: str | None = None, group_code: str | None = None) -> list[dict[str, Any]]:
    result = []
    for item in section.get("found") or []:
        if target_code is not None and item.get("target_code") != target_code:
            continue
        if group_code is not None and item.get("group_code") != group_code:
            continue
        result.append(item)
    return result


def _first_value(section: dict[str, Any], target_code: str) -> Any:
    for item in section.get("found") or []:
        if item.get("target_code") == target_code and item.get("group_code") in (None, ""):
            return item.get("value")
    return None


def _clone_item(source_item: dict[str, Any], group_code: str, value: dict[str, Any]) -> dict[str, Any]:
    cloned = {
        key: copy.deepcopy(source_item.get(key))
        for key in ("confidence", "needs_review", "source_pdf", "page_number", "page_title", "raw_text", "table_context", "notes")
        if key in source_item
    }
    cloned.update(
        {
            "target_code": group_code,
            "group_code": group_code,
            "value": value,
        }
    )
    return cloned


def _zone_item(zone_id: str, display_name: str, zone_kind: str, source_item: dict[str, Any] | None, cutoff_area: Any = None) -> dict[str, Any]:
    base = source_item or {}
    value = {
        "zone_id": zone_id,
        "display_name": display_name,
        "zone_kind": zone_kind,
    }
    if cutoff_area not in (None, ""):
        value["cutoff_waterproofing_area_m2"] = cutoff_area
    return _clone_item(base, "wall_zones", value)


def _normalize_rebar_value(value: dict[str, Any], *, zone_id: str, purpose: str) -> dict[str, Any]:
    kg_per_meter = value.get("kg_per_meter")
    if kg_per_meter in (None, "") and value.get("weight_kg") not in (None, "") and value.get("spec_length_m") not in (None, ""):
        try:
            kg_per_meter = float(value["weight_kg"]) / float(value["spec_length_m"])
        except (TypeError, ValueError, ZeroDivisionError):
            kg_per_meter = None
    out = {
        "zone_id": zone_id,
        "item_id": value.get("code") or value.get("name") or f"{zone_id}_{purpose}",
        "purpose": purpose,
        "steel_class": value.get("steel_class"),
        "diameter_mm": value.get("diameter_mm"),
        "spec_length_m": value.get("spec_length_m"),
        "kg_per_meter": kg_per_meter,
        "rod_length_m": value.get("rod_length_m"),
    }
    return {k: v for k, v in out.items() if v not in (None, "")}


def _wall_rebar_zone(value: dict[str, Any]) -> tuple[str, str] | None:
    component = value.get("component")
    floor = value.get("floor")
    name = str(value.get("name") or "").lower()
    if component == "parapet" or "парапет" in name:
        return "parapet", "parapet_chasing"
    if component == "load_bearing_walls":
        if floor == 2:
            return "floor_2", "masonry_chasing"
        return "floor_1", "masonry_chasing"
    return None


def _lintel_zone_from_legacy_target(target_code: str) -> str | None:
    if target_code.startswith("floor_2_lintel_"):
        return "floor_2"
    if target_code.startswith("floor_1_lintel_") or target_code in {"lintel_total_length", "lintel_concrete_volume"}:
        return "floor_1"
    return None


def _add_lintel_item(found: list[dict[str, Any]], source_items_by_target: dict[str, dict[str, Any]], *, zone_id: str, lintel_id: str, lintel_kind: str, fields: dict[str, str]) -> None:
    value: dict[str, Any] = {"zone_id": zone_id, "lintel_id": lintel_id, "lintel_kind": lintel_kind}
    source_item = None
    for p6_key, legacy_target in fields.items():
        item = source_items_by_target.get(legacy_target)
        if item is None:
            continue
        value[p6_key] = item.get("value")
        source_item = source_item or item
    if len(value) > 3 and source_item is not None:
        found.append(_clone_item(source_item, "lintel_items", value))


def build_p6_extraction(extraction: dict[str, Any]) -> dict[str, Any]:
    old_section = (extraction.get("sections") or {}).get(LEGACY_SECTION)
    if not old_section:
        raise ValueError(f"No {LEGACY_SECTION!r} section found")

    p6_found: list[dict[str, Any]] = []
    zone_source: dict[str, dict[str, Any]] = {}
    cutoff_area = _first_value(old_section, "cutoff_waterproofing_load_bearing_walls_area")

    for item in _found_items(old_section, group_code="wall_block_items"):
        value = item.get("value") or {}
        wall_role = value.get("wall_role")
        zone = WALL_ROLE_TO_ZONE.get(wall_role)
        if zone is None:
            continue
        zone_id, display_name, zone_kind = zone
        zone_source.setdefault(zone_id, item)
        block_value = {
            "zone_id": zone_id,
            "item_id": value.get("context") or f"{zone_id}_{value.get('block_density')}_{value.get('block_size')}",
            "block_density": value.get("block_density"),
            "block_size": value.get("block_size"),
            "volume_m3": value.get("volume_m3"),
            "context": value.get("context"),
            "material_unit_price": value.get("material_unit_price"),
        }
        p6_found.append(_clone_item(item, "wall_block_items", {k: v for k, v in block_value.items() if v not in (None, "")}))

    vent_volume_item = next(iter(_found_items(old_section, target_code="vent_chimney_gas_block_150_volume")), None)
    if vent_volume_item is not None:
        zone_id = "vent_chimney_cladding"
        zone_source.setdefault(zone_id, vent_volume_item)
        p6_found.append(
            _clone_item(
                vent_volume_item,
                "wall_block_items",
                {
                    "zone_id": zone_id,
                    "item_id": "vent_chimney_gas_block_150",
                    "block_density": "D500",
                    "block_size": "150x600x250",
                    "volume_m3": vent_volume_item.get("value"),
                    "context": "Обкладка дымохода и вентканалов",
                },
            )
        )

    for zone_id, display_name, zone_kind in [
        ("floor_1", "Кладка стен 1-го этажа", "main_walls"),
        ("floor_2", "Кладка стен 2-го этажа", "second_light"),
        ("parapet", "Парапет", "parapet"),
        ("vent_chimney_cladding", "Обкладка дымохода и вентканалов", "vent_chimney_cladding"),
    ]:
        if zone_id in zone_source:
            p6_found.insert(
                0,
                _zone_item(
                    zone_id,
                    display_name,
                    zone_kind,
                    zone_source[zone_id],
                    cutoff_area if zone_id == "floor_1" else None,
                ),
            )

    for item in _found_items(old_section, group_code="main_wall_rebar_items"):
        value = item.get("value") or {}
        zone_purpose = _wall_rebar_zone(value)
        if zone_purpose is None:
            continue
        zone_id, purpose = zone_purpose
        p6_found.append(_clone_item(item, "wall_chasing_rebar_items", _normalize_rebar_value(value, zone_id=zone_id, purpose=purpose)))

    parapet_rebar_item = next(iter(_found_items(old_section, target_code="parapet_rebar_base_length")), None)
    if parapet_rebar_item is not None:
        p6_found.append(
            _clone_item(
                parapet_rebar_item,
                "wall_chasing_rebar_items",
                {
                    "zone_id": "parapet",
                    "item_id": "parapet_rebar_a500_d10",
                    "purpose": "parapet_chasing",
                    "steel_class": "А500С",
                    "diameter_mm": 10,
                    "spec_length_m": parapet_rebar_item.get("value"),
                },
            )
        )

    by_target = {item.get("target_code"): item for item in old_section.get("found") or [] if item.get("group_code") in (None, "")}
    _add_lintel_item(
        p6_found,
        by_target,
        zone_id="floor_1",
        lintel_id="floor_1_u_block",
        lintel_kind="u_block",
        fields={"total_length_m": "lintel_total_length", "concrete_volume_m3": "lintel_concrete_volume"},
    )
    _add_lintel_item(
        p6_found,
        by_target,
        zone_id="floor_2",
        lintel_id="floor_2_u_block",
        lintel_kind="u_block",
        fields={"total_length_m": "floor_2_lintel_total_length", "concrete_volume_m3": "floor_2_lintel_concrete_volume"},
    )
    _add_lintel_item(
        p6_found,
        by_target,
        zone_id="floor_1",
        lintel_id="floor_1_monolithic",
        lintel_kind="monolithic",
        fields={
            "total_length_m": "floor_1_lintel_monolithic_total_length",
            "concrete_volume_m3": "floor_1_lintel_monolithic_concrete_volume",
            "formwork_horizontal_area_m2": "floor_1_lintel_formwork_horizontal_area",
            "formwork_vertical_area_m2": "floor_1_lintel_formwork_vertical_area",
            "insulation_eps_spec_volume_m3": "floor_1_lintel_insulation_eps_volume",
        },
    )
    _add_lintel_item(
        p6_found,
        by_target,
        zone_id="floor_2",
        lintel_id="floor_2_monolithic",
        lintel_kind="monolithic",
        fields={
            "total_length_m": "floor_2_lintel_monolithic_total_length",
            "concrete_volume_m3": "floor_2_lintel_monolithic_concrete_volume",
            "formwork_horizontal_area_m2": "floor_2_lintel_formwork_horizontal_area",
            "formwork_vertical_area_m2": "floor_2_lintel_formwork_vertical_area",
        },
    )

    for item in _found_items(old_section, group_code="lintel_rebar_items"):
        value = item.get("value") or {}
        zone_id = "floor_2" if value.get("floor") == 2 else "floor_1"
        lintel_id = "floor_2_u_block" if zone_id == "floor_2" else "floor_1_u_block"
        p6_found.append(
            _clone_item(
                item,
                "lintel_rebar_items",
                {
                    **_normalize_rebar_value(value, zone_id=zone_id, purpose="lintels"),
                    "lintel_id": lintel_id,
                    "lintel_kind": "u_block",
                },
            )
        )

    converted = copy.deepcopy(extraction)
    converted.setdefault("sections", {})[P6_SECTION] = {"found": p6_found, "missing": []}
    return converted


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("legacy_extraction_json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    data = json.loads(Path(args.legacy_extraction_json).read_text(encoding="utf-8"))
    converted = build_p6_extraction(data)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(converted, ensure_ascii=False, indent=2), encoding="utf-8")
    found_count = len(converted["sections"][P6_SECTION]["found"])
    print(json.dumps({"output": str(output), "p6_found": found_count}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
