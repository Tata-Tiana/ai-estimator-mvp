from __future__ import annotations

import json
import re
from typing import Any

import parser_paths


def norm(text: Any) -> str:
    text = "" if text is None else str(text)
    text = text.lower().replace("ё", "е").replace(",", ".")
    return re.sub(r"\s+", " ", text)


def classify(text: str, title: str, source_pdf: str) -> str:
    """Classify a logical sheet into a sheet_type using generic construction keywords.

    Rules use only domain vocabulary — no project names, no page numbers,
    no hardcoded elevation values (+3.480 / +4.680 etc.).
    Order matters: more specific patterns before broader ones.
    """
    hay = norm(title + " " + text)

    # drawing index
    if "ведомость" in hay and "чертеж" in hay:
        return "drawing_index"

    # schiedel — unambiguous brand name, check early
    if "schiedel" in hay or "вентканал" in hay or "вентиляционный канал" in hay:
        return "schiedel_vent_spec"

    # earthworks
    if "план котлован" in hay or "схема котлован" in hay:
        return "earthworks_pit_plan"
    if "котлован" in hay and "песок" in hay:
        return "earthworks_pit_plan"
    if ("схема коммуникац" in hay
            or ("труба" in hay and "ф110" in hay)
            or "трасса к1" in hay or "трасса к2" in hay
            or "трасса к3" in hay):
        return "communications_scheme"
    if "дренаж" in hay and ("труб" in hay or "схем" in hay):
        return "communications_scheme"

    # waterproofing — needs "гидроизоляц" + qualifier to avoid false positives
    if "гидроизоляц" in hay and (
        "отсечн" in hay or "вертикальн" in hay or "обмазочн" in hay
    ):
        return "cutoff_waterproofing_scheme"

    # flat roof — check before foundation
    if "кровл" in hay and (
        "logicroof" in hay or "пароизоляц" in hay
        or "примыкани" in hay or "парапет" in hay or "аэратор" in hay
    ):
        return "flat_roof_spec"
    if "план кровл" in hay:
        return "flat_roof_spec"
    if "спецификац" in hay and "кровл" in hay:
        return "flat_roof_spec"

    # foundation slab — broadened rules cover missed pages
    if "фундаментн" in hay and "спецификац" in hay:
        return "foundation_slab_spec"
    if "план фундаментной плит" in hay:
        return "foundation_slab_spec"
    if "общий вид фундамент" in hay:
        return "foundation_slab_spec"
    if "фундаментная плит" in hay:
        return "foundation_slab_spec"
    if "термовстав" in hay:
        return "thermal_inserts_plan"

    # walls / lintels
    if ("спецификация по газобетон" in hay
            or ("газобетонный блок" in hay and "перегород" in hay)
            or "армирование кладки" in hay):
        return "walls_blocks_spec"
    if "перемыч" in hay:
        return "lintels_plan"
    if "кладочный план" in hay:
        return "walls_layout_plan"
    if "план этажа" in hay:
        return "walls_layout_plan"

    # floor slabs — explicit floor-number keywords only, NO elevation values
    if (
        "перекрытие 1 этаж" in hay or "перекрытия 1 этаж" in hay
        or "перекрытие над 1 этаж" in hay
        or ("плит" in hay and "перекрыт" in hay
            and ("1 этаж" in hay or "первого этаж" in hay))
    ):
        return "floor_slab_1_spec"
    if (
        "перекрытие 2 этаж" in hay or "перекрытия 2 этаж" in hay
        or "перекрытие над 2 этаж" in hay
        or ("плит" in hay and "перекрыт" in hay
            and ("2 этаж" in hay or "второго этаж" in hay))
    ):
        return "floor_slab_2_spec"
    if "плита перекрытия" in hay or "плите перекрытия" in hay or "плиты перекрытия" in hay:
        return "floor_slab_unknown_spec"

    return "unknown"


def section_code(sheet_type: str) -> str:
    mapping = {
        "earthworks_pit_plan": "earthworks",
        "communications_scheme": "earthworks",
        "foundation_slab_spec": "foundation_slab",
        "thermal_inserts_plan": "foundation_slab",
        "cutoff_waterproofing_scheme": "waterproofing",
        "walls_blocks_spec": "load_bearing_walls_lintels",
        "lintels_plan": "load_bearing_walls_lintels",
        "walls_layout_plan": "load_bearing_walls_lintels",
        "floor_slab_1_spec": "floor_slab_1",
        "floor_slab_2_spec": "floor_slab_2",
        "floor_slab_unknown_spec": "floor_slab_unknown",
        "flat_roof_spec": "flat_roof",
        "schiedel_vent_spec": "schiedel_vent_channels",
    }
    return mapping.get(sheet_type, "")


def classify_pages() -> list[dict[str, Any]]:
    pages = json.loads(parser_paths.pages_text_path().read_text(encoding="utf-8"))
    drawing_index_file = parser_paths.drawing_index_path()
    drawing_index = json.loads(drawing_index_file.read_text(encoding="utf-8")) if drawing_index_file.exists() else []
    index_by_pdf_title = defaultdict_index(drawing_index)
    logical_pages: list[dict[str, Any]] = []
    for page in pages:
        text = page.get("raw_page_text", "")
        preliminary = page.get("preliminary_page_title", "")
        logical_type = classify(text, preliminary, page["source_pdf"])
        logical_title = preliminary
        drawing_number = ""
        for indexed in index_by_pdf_title.get(page["source_pdf"], []):
            if norm(indexed["drawing_sheet_title"]) in norm(text):
                logical_title = indexed["drawing_sheet_title"]
                drawing_number = indexed["drawing_sheet_number"]
                break
        logical_pages.append(
            {
                **page,
                "logical_sheet_title": logical_title,
                "logical_sheet_type": logical_type,
                "section_code": section_code(logical_type),
                "drawing_sheet_number": drawing_number,
            }
        )
    parser_paths.logical_pages_path().write_text(json.dumps(logical_pages, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return logical_pages


def defaultdict_index(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        result.setdefault(row["source_pdf"], []).append(row)
    return result


def main() -> int:
    rows = classify_pages()
    print(f"logical_pages: {parser_paths.logical_pages_path()} ({len(rows)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
