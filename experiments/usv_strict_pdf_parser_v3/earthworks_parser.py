from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from candidate_store import CandidateStore
from spec_row_parser import NUMBER_RE, last_number_before_unit_after_keyword, parse_number, table_row_objects


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
EXTRACTED_DIR = DATA_DIR / "extracted"
LOGICAL_PAGES_PATH = RAW_DIR / "logical_pages.json"
TABLES_PATH = RAW_DIR / "tables.json"
EARTHWORKS_PATH = EXTRACTED_DIR / "earthworks.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_sand(logical_pages: list[dict[str, Any]], store: CandidateStore) -> dict[str, Any] | None:
    for page in logical_pages:
        if page.get("logical_sheet_type") != "earthworks_pit_plan":
            continue
        for line in page.get("raw_page_text", "").splitlines():
            if "песок" not in line.lower() or "м3" not in line.lower():
                continue
            value, fragment = last_number_before_unit_after_keyword(line, "песок", "м3")
            if value is None:
                continue
            evidence = store.add(
                source_pdf=page["source_pdf"],
                physical_page_number=page["physical_page_number"],
                drawing_sheet_number=page.get("drawing_sheet_number", ""),
                logical_sheet_title=page.get("logical_sheet_title", ""),
                logical_sheet_type=page["logical_sheet_type"],
                section_code="earthworks",
                candidate_type="earthworks_sand_volume",
                raw_label="Объем песка",
                value=value,
                unit="м3",
                raw_context=fragment,
                confidence="high",
                extraction_method="last_number_before_m3_after_keyword",
                notes="Selected last number before m3 after keyword песок.",
            )
            return {"sand_volume_m3": value, "evidence_id": evidence["evidence_id"], "raw_context": fragment}
    tables = load_json(TABLES_PATH)
    rows = table_row_objects(tables, logical_pages)
    for row in rows:
        if row["logical_sheet_type"] != "earthworks_pit_plan":
            continue
        text = row["row_text"]
        if "песок" not in text.lower() or "м3" not in text.lower():
            continue
        value, fragment = last_number_before_unit_after_keyword(text, "песок", "м3")
        if value is None:
            continue
        evidence = store.add(
            source_pdf=row["source_pdf"],
            physical_page_number=row["physical_page_number"],
            drawing_sheet_number=row.get("drawing_sheet_number", ""),
            logical_sheet_title=row.get("logical_sheet_title", ""),
            logical_sheet_type=row["logical_sheet_type"],
            section_code="earthworks",
            candidate_type="earthworks_sand_volume",
            raw_label="Объем песка",
            value=value,
            unit="м3",
            raw_context=fragment,
            confidence="high",
            extraction_method="table_last_number_before_m3_after_keyword",
            notes="Selected last number before m3 after keyword песок in PDF table row.",
        )
        return {"sand_volume_m3": value, "evidence_id": evidence["evidence_id"], "raw_context": fragment}
    return None


def parse_trench_block(text: str) -> dict[str, Any] | None:
    if not all(marker in text.lower() for marker in ("длина", "глубина", "ширина", "м3")):
        return None
    route_match = re.search(r"К\s*1.*?К\s*2.*?Во\s*д\s*а.*?Эл\.?\s*кабель.*?И\s*т\s*о\s*го", text, re.IGNORECASE | re.DOTALL)
    length_match = re.search(r"Длина\s+(?P<values>.+?)\s+Глубина", text, re.IGNORECASE | re.DOTALL)
    depth_match = re.search(r"Глубина\s+(?P<values>.+?)\s+Ширина", text, re.IGNORECASE | re.DOTALL)
    width_match = re.search(r"Ширина\s+(?P<values>.+?)\s+(?:1\s+2\s+3|м3)", text, re.IGNORECASE | re.DOTALL)
    volume_match = re.search(r"м3\s+(?P<values>.+?)(?:Проект|Примечание|$)", text, re.IGNORECASE | re.DOTALL)
    if not (route_match and length_match and depth_match and width_match and volume_match):
        return None

    def nums(fragment: str) -> list[float]:
        return [parse_number(match.group(0)) for match in re.finditer(NUMBER_RE, fragment)]

    lengths = nums(length_match.group("values"))
    depths = nums(depth_match.group("values"))
    widths = nums(width_match.group("values"))
    volumes = nums(volume_match.group("values"))
    route_names = ["К1", "К2", "Вода", "Эл. кабель"]
    if len(lengths) < 4 or len(depths) < 4 or len(widths) < 4 or len(volumes) < 5:
        return None
    return {
        "routes": [
            {
                "route_name": route_names[index],
                "length_m": lengths[index],
                "depth_m": depths[index],
                "width_m": widths[index],
                "volume_m3": volumes[index],
            }
            for index in range(4)
        ],
        "total": volumes[4],
    }


def parse_trench_table_rows(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], str] | None:
    header_index = None
    for index, row in enumerate(rows):
        cells = [cell or "" for cell in row.get("row") or []]
        text = " ".join(cells)
        if "К 1" in text and "Итого" in text and "кабель" in text:
            header_index = index
            break
    if header_index is None:
        return None

    length_row = None
    width_row = None
    for row in rows[header_index + 1 : header_index + 8]:
        cells = [cell or "" for cell in row.get("row") or []]
        text = " ".join(cells)
        if "Длина" in text and "Глубина" in text:
            length_row = cells
        if "Ширина" in text and "м3" in text:
            width_row = cells
    if not length_row or not width_row:
        return None

    def nums(cell: str) -> list[float]:
        return [parse_number(match.group(0)) for match in re.finditer(NUMBER_RE, cell)]

    def non_empty_tail(cells: list[str]) -> list[str]:
        return [cell for cell in cells if cell.strip()][-4:]

    length_cells = non_empty_tail(length_row)
    width_cells = non_empty_tail(width_row)
    if len(length_cells) < 4 or len(width_cells) < 4:
        return None

    k1_ld = nums(length_cells[1])
    k2_water_ld = nums(length_cells[2])
    cable_ld = nums(length_cells[3])
    k1_wv = nums(width_cells[0])
    k2_water_wv = nums(width_cells[1])
    cable_wv = nums(width_cells[2])
    total_values = nums(width_cells[-1])
    if (
        len(k1_ld) < 2
        or len(k2_water_ld) < 4
        or len(cable_ld) < 2
        or len(k1_wv) < 2
        or len(k2_water_wv) < 4
        or len(cable_wv) < 2
        or not total_values
    ):
        return None

    routes = [
        {
            "route_name": "К1",
            "length_m": k1_ld[0],
            "depth_m": k1_ld[1],
            "width_m": k1_wv[0],
            "volume_m3": k1_wv[1],
        },
        {
            "route_name": "К2",
            "length_m": k2_water_ld[0],
            "depth_m": k2_water_ld[2],
            "width_m": k2_water_wv[0],
            "volume_m3": k2_water_wv[2],
        },
        {
            "route_name": "Вода",
            "length_m": k2_water_ld[1],
            "depth_m": k2_water_ld[3],
            "width_m": k2_water_wv[1],
            "volume_m3": k2_water_wv[3],
        },
        {
            "route_name": "Эл. кабель",
            "length_m": cable_ld[0],
            "depth_m": cable_ld[1],
            "width_m": cable_wv[0],
            "volume_m3": cable_wv[1],
        },
    ]
    raw_context = "\n".join(
        " | ".join(cell for cell in [*(rows[header_index].get("row") or []), *length_row, *width_row] if cell)
        .splitlines()
    )
    return {"routes": routes, "total": total_values[0]}, raw_context


def parse_trenches(logical_pages: list[dict[str, Any]], tables: list[dict[str, Any]], store: CandidateStore) -> dict[str, Any]:
    rows = table_row_objects(tables, logical_pages)
    pit_rows = [row for row in rows if row["logical_sheet_type"] == "earthworks_pit_plan"]
    by_table: dict[tuple[str, int, int], list[dict[str, Any]]] = {}
    for row in pit_rows:
        key = (row["source_pdf"], row["physical_page_number"], row["table_index"])
        by_table.setdefault(key, []).append(row)
    for table_rows in by_table.values():
        parsed_with_context = parse_trench_table_rows(table_rows)
        if not parsed_with_context:
            continue
        parsed, raw_context = parsed_with_context
        first_row = table_rows[0]
        evidence = store.add(
            source_pdf=first_row["source_pdf"],
            physical_page_number=first_row["physical_page_number"],
            drawing_sheet_number=first_row.get("drawing_sheet_number", ""),
            logical_sheet_title=first_row.get("logical_sheet_title", ""),
            logical_sheet_type=first_row["logical_sheet_type"],
            section_code="earthworks",
            candidate_type="earthworks_trench_table_cells",
            raw_label="Таблица траншей",
            value=parsed["total"],
            unit="mixed",
            raw_context=raw_context,
            confidence="high",
            extraction_method="trench_table_cell_parser",
        )
        routes = [{**route, "evidence_id": evidence["evidence_id"]} for route in parsed["routes"]]
        return {"trench_routes": routes, "trench_volume_total_m3": parsed["total"], "evidence_ids": [evidence["evidence_id"]]}

    candidate_rows = [row for row in pit_rows if any(word in row["row_text"].lower() for word in ("к1", "к2", "вода", "кабель", "итого", "транше"))]
    for row in candidate_rows:
        parsed = parse_trench_block(row["row_text"])
        if not parsed:
            continue
        evidence = store.add(
            source_pdf=row["source_pdf"],
            physical_page_number=row["physical_page_number"],
            drawing_sheet_number=row.get("drawing_sheet_number", ""),
            logical_sheet_title=row.get("logical_sheet_title", ""),
            logical_sheet_type=row["logical_sheet_type"],
            section_code="earthworks",
            candidate_type="earthworks_trench_table_row",
            raw_label="Таблица траншей",
            value=parsed["total"],
            unit="mixed",
            raw_context=row["row_text"],
            confidence="high",
            extraction_method="trench_block_parser",
        )
        routes = [{**route, "evidence_id": evidence["evidence_id"]} for route in parsed["routes"]]
        return {"trench_routes": routes, "trench_volume_total_m3": parsed["total"], "evidence_ids": [evidence["evidence_id"]]}
    return {"trench_routes": [], "trench_volume_total_m3": None, "evidence_ids": []}


def parse_communications(logical_pages: list[dict[str, Any]], tables: list[dict[str, Any]], store: CandidateStore) -> dict[str, Any]:
    rows = table_row_objects(tables, logical_pages)
    comm_rows = [row for row in rows if row["logical_sheet_type"] == "communications_scheme"]
    items = []
    for row in comm_rows:
        text = row["row_text"]
        low = text.lower()
        if "труба" not in low:
            continue
        qty_match = re.search(rf"(?P<qty>{NUMBER_RE})\s*шт", text, re.IGNORECASE)
        length_match = re.search(rf"труба\s+(?P<len>{NUMBER_RE})\s*м", text, re.IGNORECASE)
        mp_match = re.search(rf"(?P<len>{NUMBER_RE})\s*(?:м/п|м\.п\.|п\.м\.)", text, re.IGNORECASE)
        if length_match and qty_match:
            piece = parse_number(length_match.group("len"))
            qty = parse_number(qty_match.group("qty"))
            total = piece * qty
        elif mp_match:
            piece = None
            qty = None
            total = parse_number(mp_match.group("len"))
        else:
            continue
        evidence = store.add(
            source_pdf=row["source_pdf"],
            physical_page_number=row["physical_page_number"],
            drawing_sheet_number=row.get("drawing_sheet_number", ""),
            logical_sheet_title=row.get("logical_sheet_title", ""),
            logical_sheet_type=row["logical_sheet_type"],
            section_code="earthworks",
            candidate_type="communication_pipe_item",
            raw_label="Труба коммуникаций",
            value=total,
            unit="м",
            raw_context=text,
            confidence="high",
            extraction_method="pipe_length_qty_regex",
        )
        items.append(
            {
                "name": text[:120],
                "piece_length_m": piece,
                "qty": qty,
                "total_length_m": total,
                "evidence_id": evidence["evidence_id"],
            }
        )
    return {"communication_pipe_items": items, "communications_length_m": sum(item["total_length_m"] for item in items)}


def parse_earthworks(store: CandidateStore) -> dict[str, Any]:
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    logical_pages = load_json(LOGICAL_PAGES_PATH)
    tables = load_json(TABLES_PATH)
    result = {
        "sand": parse_sand(logical_pages, store),
        "trenches": parse_trenches(logical_pages, tables, store),
        "communications": parse_communications(logical_pages, tables, store),
    }
    EARTHWORKS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    store = CandidateStore()
    result = parse_earthworks(store)
    store.write()
    print(f"earthworks: {EARTHWORKS_PATH}")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
