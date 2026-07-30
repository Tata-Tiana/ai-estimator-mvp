"""Builds the review workbook the same way build_review_workbook_from_contracts.py
does, but fills sheet 01 with real values from a chat-extraction extraction_output.json
instead of leaving it blank. This is the missing "step 2" from ADAPTER_BUILD_PLAN.md's
"Полный путь PDF -> смета" section - the first real test of it against a real JSON.

Sheet 01 is filled from the extraction JSON, sheet 02 (prices) is filled from a
price_registry_filled_v*.xlsx (see build_rebar_lookup for the one templated-code
expansion that needs project data; see reports/step_27_sheet02_price_fill_plan.md for
the rest). Sheet 03 is filled from raw_table_rows in the extraction JSON. Sheets 00/04-06
are unchanged, built the same way as the empty-template script.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "experiments" / "box_calculator"))

from metal_delivery_allocator import MetalSection, allocate_metal_deliveries  # noqa: E402

from build_review_workbook_from_contracts import (  # noqa: E402
    COMPACT_ROW_HEIGHT,
    FILL_HEADER,
    FILL_INPUT,
    FILL_MISSING,
    FILL_WHITE,
    FONT_NAME,
    ITEM_BLOCK_HEADERS,
    PROJECT_HEADERS,
    apply_table_style,
    append_block,
    append_section_band,
    build_constructor_sheet,
    build_contracts_summary_sheet,
    build_instruction_sheet,
    build_manual_values_sheet,
    build_prices_sheet,
    build_raw_contracts_sheet,
    correction_headers,
    default_contract_paths,
    diagnostic_repeated_row_params,
    load_manual_values_registry,
    load_price_registry,
    load_yaml_contract,
    merge_row_full_width,
    production_repeated_row_params,
    rebar_group_keys_for_contract,
    rebar_item_weight_kg,
    restyle_block_sheet,
    restyle_section_bands,
    scalar_review_rows_for_contract,
    section_code,
    section_name,
    set_widths,
    style_block_title_row,
    style_header_row,
)

ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DIR = Path(__file__).resolve().parent
DEFAULT_PRICE_REGISTRY = ROOT / "output" / "price_registry_filled_v4.xlsx"
DEFAULT_MANUAL_VALUES_REGISTRY = ROOT / "output" / "manual_values_registry.xlsx"


# Narrow, purpose-built support for the "sum(included <group>.<field>)" auto_calculated formula
# shape only — not a general expression evaluator. Most auto_calculated entries in
# section_contract.yaml are internal computation notes never meant to reach sheet 01 (see plan
# section 34); only entries a review_parameters row explicitly opts into via cross_check_key get
# rendered, and only this one formula shape is understood. If a future cross-check needs a
# different formula shape, extend this function narrowly rather than building a generic parser.
_SUM_INCLUDED_RE = re.compile(r"^sum\(included (\w+)\.(\w+)\)$")


def compute_cross_check_value(formula: str, found_groups: dict[str, list[Any]]) -> float | None:
    match = _SUM_INCLUDED_RE.match(formula.strip())
    if not match:
        return None
    group_key, field = match.groups()
    rows = found_groups.get(group_key) or []
    total = 0.0
    found_any = False
    for item in rows:
        value = item.get("value") or {}
        include = value.get("include_in_communications", value.get("include", True))
        if not include:
            continue
        explicit_total = value.get(field)
        if explicit_total is not None:
            total += float(explicit_total)
            found_any = True
            continue
        # Mirror earthworks_calculator.py's own pipe_items fallback: pipe_length_m * quantity when
        # no explicit total_length_m is given on the row (e.g. straight pipe segments). Rows with
        # no length component at all (elbows, tees, plugs) contribute 0, not an error.
        pipe_length = value.get("pipe_length_m")
        quantity = value.get("quantity")
        if pipe_length is not None and quantity is not None:
            total += float(pipe_length) * float(quantity)
            found_any = True
    return total if found_any else None


def auto_calculated_by_key(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["key"]: entry for entry in (contract.get("auto_calculated") or []) if entry.get("key")}


# 2026-07-29: sections/fields that only exist for some projects (U-block lintels, monolithic
# lintels — per floor, independently) currently show the exact same "Не найдено" status whether
# the field is safely inapplicable or genuinely missing money-critical data. Real ARK case that
# motivated this: floor_1_lintel_monolithic_total_length_m was found (5.4, proving monolithic
# lintels exist on this floor) but floor_1_lintel_monolithic_concrete_volume_m3 was missing — the
# calculator used to silently price concrete material as 0 while still billing the concreting
# work by length (see plan section 41 / calculate_monolithic_lintel_block fix). Each inner list is
# a "presence pair": if extraction found a truthy value for ANY code in the pair, the others are
# confirmed required — this project definitely has this construction, so a still-missing sibling
# is a real gap, not a safely-blank optional field. Scoped to the 4 pairs with a proven money-loss
# bug (U-block + monolithic lintels, floor 1 and floor 2); other conditional sections (floor_2
# masonry, parapet, vent chimney cladding, beam_items presence) don't have a sibling-field risk
# today, so are not included here — extend this table if a similar bug is found for them.
SECTION_PRESENCE_PAIRS: dict[str, list[list[str]]] = {
    "load_bearing_walls_lintels": [
        ["lintel_total_length", "lintel_concrete_volume"],
        ["floor_2_lintel_total_length", "floor_2_lintel_concrete_volume"],
        ["floor_1_lintel_monolithic_total_length", "floor_1_lintel_monolithic_concrete_volume"],
        ["floor_2_lintel_monolithic_total_length", "floor_2_lintel_monolithic_concrete_volume"],
    ],
}


def compute_confirmed_required(found_by_target: dict[str, Any], sec_code: str) -> set[str]:
    """Returns target_codes that are confirmed required for this project because a sibling
    code in the same presence pair was found with a truthy value. See SECTION_PRESENCE_PAIRS."""
    confirmed: set[str] = set()
    for pair in SECTION_PRESENCE_PAIRS.get(sec_code, []):
        signal_fired = False
        for code in pair:
            found = found_by_target.get(code)
            if found is not None and found.get("value") not in (None, 0, 0.0):
                signal_fired = True
                break
        if signal_fired:
            confirmed.update(pair)
    return confirmed


def index_extraction_section(extraction: dict[str, Any], sec_code: str) -> tuple[dict, dict, set]:
    section = (extraction.get("sections") or {}).get(sec_code) or {}
    found_by_target: dict[str, Any] = {}
    found_groups: dict[str, list[Any]] = {}
    for item in section.get("found") or []:
        group_code = item.get("group_code")
        if group_code:
            found_groups.setdefault(group_code, []).append(item)
        else:
            target_code = item.get("target_code")
            if target_code:
                found_by_target[target_code] = item
    missing = set(section.get("missing") or [])
    return found_by_target, found_groups, missing


def display_value(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


DETAIL_RAW_HEADERS = [
    "№",
    "Исходные колонки PDF",
    "Исходные ячейки PDF",
    "Сырая строка PDF",
    "Ед.",
    "Норм. ед.",
    "Target codes",
    "Needs review",
    "Комментарий parser",
    "Комментарий Елены",
    "section_code",
    "source_pdf",
    "page_number",
    "page_title",
    "table_id",
    "row_index",
    "mapped_target_codes_json",
]


def joined(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " | ".join("" if item is None else str(item) for item in value)
    return str(value)


def table_title(row: dict[str, Any]) -> str:
    title = row.get("table_title")
    if title:
        return str(title)
    page_title = row.get("page_title") or "Лист без названия"
    table_id = row.get("table_id") or "unknown_table"
    return f"{page_title} — таблица {table_id}"


def table_group_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("section_code") or "",
        row.get("source_pdf") or "",
        row.get("page_number") or "",
        row.get("page_title") or "",
        row.get("table_id") or "",
        row.get("table_title") or "",
    )


def iter_raw_table_groups(extraction: dict[str, Any]) -> list[tuple[tuple[Any, ...], list[dict[str, Any]]]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for section in (extraction.get("sections") or {}).values():
        for row in section.get("raw_table_rows") or []:
            if not isinstance(row, dict):
                continue
            groups.setdefault(table_group_key(row), []).append(row)
    return list(groups.items())


def build_details_sheet_from_extraction(wb: Workbook, extraction: dict[str, Any]) -> dict[str, int]:
    ws = wb.create_sheet("03_Детали объемов")
    groups = iter_raw_table_groups(extraction)
    max_col = len(DETAIL_RAW_HEADERS)

    for _group_key, rows in groups:
        first = rows[0]
        title = table_title(first)
        context = (
            f"Раздел: {first.get('section_code') or ''} | "
            f"PDF: {first.get('source_pdf') or ''} | "
            f"стр. {first.get('page_number') or ''} | "
            f"Лист: {first.get('page_title') or ''}"
        )

        if ws.max_row == 1 and not ws.cell(1, 1).value:
            ws.cell(1, 1).value = title
        else:
            ws.append([])
            ws.append([title])
        style_block_title_row(ws, ws.max_row, max_col)
        ws.append([context])
        for cell in ws[ws.max_row]:
            cell.fill = FILL_WHITE
            cell.font = Font(name=FONT_NAME, size=10, italic=True)
            cell.alignment = Alignment(wrap_text=True, vertical="top")

        ws.append(DETAIL_RAW_HEADERS)
        style_header_row(ws, ws.max_row, max_col)

        for row in rows:
            mapped = row.get("mapped_target_codes") or []
            ws.append([
                row.get("row_index"),
                joined(row.get("columns")),
                joined(row.get("cells")),
                row.get("raw_text") or "",
                row.get("unit") or "",
                row.get("normalized_unit") or "",
                joined(mapped),
                "да" if row.get("needs_review") else "нет",
                row.get("notes") or "",
                "",
                row.get("section_code") or "",
                row.get("source_pdf") or "",
                row.get("page_number") or "",
                row.get("page_title") or "",
                row.get("table_id") or "",
                row.get("row_index") or "",
                json.dumps(mapped, ensure_ascii=False),
            ])
            for cell in ws[ws.max_row]:
                cell.font = Font(name=FONT_NAME, size=11)
                cell.alignment = Alignment(wrap_text=True, vertical="top")

    if not groups:
        ws.append(["Сырые таблицы parser не найдены в extraction JSON."])
        style_block_title_row(ws, 1, 1)

    set_widths(ws, {
        "A": 8,
        "B": 44,
        "C": 58,
        "D": 72,
        "E": 12,
        "F": 12,
        "G": 32,
        "H": 14,
        "I": 52,
        "J": 30,
        "K": 20,
        "L": 34,
        "M": 10,
        "N": 34,
        "O": 28,
        "P": 12,
        "Q": 32,
    })
    for column in ["K", "L", "M", "N", "O", "P", "Q"]:
        ws.column_dimensions[column].hidden = True
    ws.freeze_panes = "A1"

    return {"detail_table_blocks": len(groups), "raw_detail_rows": sum(len(rows) for _, rows in groups)}


def build_project_sheet_from_extraction(
    wb: Workbook, contracts: list[dict[str, Any]], extraction: dict[str, Any]
) -> dict[str, int]:
    ws = wb.create_sheet("01_Проверка проекта")
    project_title = "Разбор проекта:\n" + " + ".join(section_name(c) for c in contracts)
    ws.append([project_title, "", "", "", "", "", "", "", "", "", "", "", "", ""])
    ws.append([])
    ws.append([])
    ws.append(PROJECT_HEADERS)

    counts = {"found": 0, "needs_review": 0, "missing": 0, "missing_confirmed_required": 0, "item_rows": 0}

    rebar_weights_by_section = compute_rebar_weights_by_section(contracts, extraction)
    rebar_crane_allocation = compute_rebar_crane_allocation(rebar_weights_by_section)

    for contract in contracts:
        sec_code = section_code(contract)
        found_by_target, found_groups, missing = index_extraction_section(extraction, sec_code)
        confirmed_required = compute_confirmed_required(found_by_target, sec_code)
        auto_calculated = auto_calculated_by_key(contract)
        append_section_band(ws, [section_name(contract)], len(PROJECT_HEADERS))

        box_crane_key = REBAR_CRANE_FIELD_BY_SECTION.get(sec_code)

        for param in scalar_review_rows_for_contract(contract):
            review_behavior = param.get("review_behavior") or {}
            target_code = param.get("target_code", "")
            found = found_by_target.get(target_code)
            row_fill = FILL_INPUT

            if box_crane_key is not None and param.get("key") == box_crane_key:
                # Box-calculator-allocated crane shifts (2026-07-30) - computed from this
                # project's real rebar weight, not looked up in found_by_target/missing at all.
                # See compute_rebar_crane_allocation/REBAR_CRANE_FIELD_BY_SECTION.
                found_value = rebar_crane_allocation.get(sec_code, 0)
                status = "Найдено (авто, box-калькулятор)"
                source = ""
                fragment = (
                    f"Вес арматуры раздела: {rebar_weights_by_section.get(sec_code, 0):g} кг. "
                    f"Автораспределение по накоплению {int(METAL_TRUCK_CAPACITY_KG // 1000)} т — "
                    "проверьте и поправьте при необходимости."
                )
                counts["found"] += 1
                ws.append([
                    param.get("label_ru", param.get("key", "")),
                    found_value,
                    param.get("unit", ""),
                    status,
                    "",
                    review_behavior.get("action_ru", "Проверьте значение."),
                    source,
                    fragment,
                    "",
                    "",
                    sec_code,
                    param.get("key", ""),
                    param.get("source_class", ""),
                    target_code,
                ])
                for cell in ws[ws.max_row]:
                    cell.fill = row_fill
                ws.row_dimensions[ws.max_row].height = COMPACT_ROW_HEIGHT
                continue

            is_unresolved_needs_review = found is not None and found.get("value") is None
            if target_code in confirmed_required and (is_unresolved_needs_review or (target_code in missing and found is None)):
                # A sibling field in the same presence pair was found — this project definitely
                # has this construction, so a still-blank value here (whether never attempted, in
                # section.missing, or a needs_review entry that only has candidates — e.g. the real
                # ARK ПБ1/ПБ2 case where extraction correctly refused to sum 0.21+0.16 itself) is a
                # real, money-relevant gap, not a safely-skippable optional field. Escalate instead
                # of following the normal found/missing branches below. See SECTION_PRESENCE_PAIRS.
                found_value = None
                status = "Не найдено — ОБЯЗАТЕЛЬНО (раздел точно есть в проекте)"
                row_fill = FILL_MISSING
                source = found.get("source_pdf") if found is not None else ""
                fragment = (found.get("raw_text") or found.get("notes") or "") if found is not None else ""
                counts["missing_confirmed_required"] += 1
            elif found is not None:
                found_value = display_value(found.get("value"))
                needs_review = bool(found.get("needs_review"))
                status = "Проверьте (needs_review)" if needs_review else "Найдено"
                source = found.get("source_pdf") or ""
                fragment = found.get("raw_text") or found.get("notes") or ""
                counts["needs_review" if needs_review else "found"] += 1
            elif target_code and target_code in missing:
                found_value = None
                status = "Не найдено"
                source = ""
                fragment = ""
                counts["missing"] += 1
            else:
                found_value = None
                status = "Проверьте"
                source = ""
                fragment = ""

            cross_check_display = ""
            cross_check_key = param.get("cross_check_key")
            if cross_check_key:
                cc_entry = auto_calculated.get(cross_check_key)
                if cc_entry:
                    cc_value = compute_cross_check_value(cc_entry.get("formula", ""), found_groups)
                    if cc_value is not None:
                        cross_check_display = f"{cc_value:g} — {cc_entry.get('label_ru', cross_check_key)}"

            ws.append([
                param.get("label_ru", param.get("key", "")),
                found_value,
                param.get("unit", ""),
                status,
                cross_check_display,
                review_behavior.get("action_ru", "Проверьте значение."),
                source,
                fragment,
                "",
                "",
                sec_code,
                param.get("key", ""),
                param.get("source_class", ""),
                target_code,
            ])
            for cell in ws[ws.max_row]:
                cell.fill = row_fill
            ws.row_dimensions[ws.max_row].height = COMPACT_ROW_HEIGHT

        for param in production_repeated_row_params(contract) + diagnostic_repeated_row_params(contract):
            review_behavior = param.get("review_behavior") or {}
            action_ru = review_behavior.get("action_ru", "Проверьте позиции построчно.")
            group_key = param.get("key")
            title = f"{section_name(contract)} — {param.get('label_ru', group_key)} ({action_ru})"
            headers = ITEM_BLOCK_HEADERS + correction_headers(param) + ["row_data_json"]

            item_label_columns = param.get("item_label_columns") or []
            correction_columns = param.get("correction_columns") or []
            columns_by_key = {c["key"]: c for c in (param.get("columns") or [])}

            rows: list[list[Any]] = []
            for item in found_groups.get(group_key, []):
                value = item.get("value") or {}
                needs_review = bool(item.get("needs_review"))

                label_parts = [str(value[k]) for k in item_label_columns if value.get(k) not in (None, "")]
                label = " ".join(label_parts) or item.get("item_name") or group_key

                summary_parts = []
                for key in correction_columns:
                    v = value.get(key)
                    if v is None:
                        continue
                    unit = columns_by_key.get(key, {}).get("unit", "")
                    summary_parts.append(f"{v}{' ' + unit if unit else ''}")
                summary = ", ".join(summary_parts)

                status = "Проверьте (needs_review)" if needs_review else "Найдено"
                counts["needs_review" if needs_review else "found"] += 1
                counts["item_rows"] += 1

                row = [
                    label,
                    summary,
                    param.get("unit", ""),
                    status,
                    "",
                    "",  # action_ru already stated once in the block title above, not per row -
                         # repeating a ~100-char sentence on every item row was the main cause of
                         # tall wrapped rows (2026-07-29 design fix)
                    item.get("source_pdf") or "",
                    item.get("raw_text") or item.get("notes") or "",
                    "",
                    "",
                    sec_code,
                    group_key,
                    param.get("source_class", ""),
                    param.get("target_code", ""),
                ]
                row += ["", "", "", ""]  # correction columns - Elena fills these, not the extraction
                row.append(json.dumps(value, ensure_ascii=False))
                rows.append(row)

            append_block(ws, title, headers, rows)
            if rows:
                for row_idx in range(ws.max_row - len(rows) + 1, ws.max_row + 1):
                    ws.row_dimensions[row_idx].height = COMPACT_ROW_HEIGHT

    # Итог по коробке (2026-07-30): one cross-section summary row after all 8 sections, so
    # Elena can see the real total before deciding how to redistribute crane shifts between
    # sections herself. See compute_rebar_weights_by_section/compute_rebar_crane_allocation.
    section_names_by_code = {section_code(c): section_name(c) for c in contracts}
    grand_total_weight = sum(rebar_weights_by_section.values())
    breakdown = "; ".join(
        f"{section_names_by_code.get(code, code)}: {weight:g} кг"
        for code, weight in rebar_weights_by_section.items()
        if weight > 0
    )
    append_section_band(ws, ["Итог по коробке"], len(PROJECT_HEADERS))
    ws.append([
        "Общий вес арматуры по проекту (все разделы с арматурой), кг",
        round(grand_total_weight, 1),
        "кг",
        "Найдено (авто, box-калькулятор)",
        "",
        "Справочно — используется для решения, где ставить больше 1 крана на разделе.",
        "",
        breakdown,
        "",
        "",
        "",
        "total_rebar_weight_kg",
        "AUTO_CALCULATED",
        "",
    ])
    for cell in ws[ws.max_row]:
        cell.fill = FILL_INPUT
    ws.row_dimensions[ws.max_row].height = COMPACT_ROW_HEIGHT

    ws.cell(1, 1).font = Font(name=FONT_NAME, bold=True, size=13)
    ws.cell(1, 1).fill = FILL_HEADER
    apply_table_style(ws, header_row=4)
    restyle_section_bands(ws)
    restyle_block_sheet(ws)
    # Merged last, using the sheet's true final ws.max_column (grows as item blocks with extra
    # correction columns get added above) - merging earlier at a narrower width risks the same
    # overlapping-merge corruption already fixed once for section bands/block titles.
    merge_row_full_width(ws, 1, ws.max_column)
    ws.freeze_panes = "A5"
    set_widths = {
        "A": 30, "B": 26, "C": 10, "D": 20, "E": 20, "F": 62, "G": 30, "H": 64,
        "I": 28, "J": 28, "K": 20, "L": 28, "M": 18, "N": 24,
        "O": 24, "P": 24, "Q": 24,
    }
    for col, width in set_widths.items():
        ws.column_dimensions[col].width = width
    for column in ["K", "L", "M", "N", "S"]:
        ws.column_dimensions[column].hidden = True

    return counts


def build_rebar_lookup(
    contracts: list[dict[str, Any]], extraction: dict[str, Any]
) -> dict[str, list[dict[str, Any]]]:
    """section_code -> real rebar rows (steel_class/diameter_mm) found by extraction, pooled
    across every rebar-shaped group in that section (see rebar_group_keys_for_contract). Used to
    expand sheet 02's rebar_<class>_d<diameter>_m templated price row into one row per
    diameter/class actually present in this project."""
    lookup: dict[str, list[dict[str, Any]]] = {}
    for contract in contracts:
        sec_code = section_code(contract)
        group_keys = rebar_group_keys_for_contract(contract)
        if not group_keys:
            continue
        _, found_groups, _ = index_extraction_section(extraction, sec_code)
        items = [
            item.get("value") or {}
            for group_key in group_keys
            for item in found_groups.get(group_key, [])
        ]
        if items:
            lookup[sec_code] = items
    return lookup


# section_code -> the one review_parameters/supplier_inputs key that holds "crane shifts for
# rebar delivery" in that section. Only the 4 sections with rebar have one; must match
# METAL_SECTION_ORDER's box_calculator convention (experiments/box_calculator/section_registry.py)
# so allocation order lines up with these keys 1:1.
REBAR_CRANE_FIELD_BY_SECTION = {
    "foundation_slab": "rebar_crane_shifts",
    "load_bearing_walls_lintels": "wall_rebar_crane_shifts",
    "floor_slab_1": "formwork_rebar_crane_shifts",
    "floor_slab_2": "crane_shifts",
}
METAL_SECTION_ORDER = list(REBAR_CRANE_FIELD_BY_SECTION.keys())
METAL_TRUCK_CAPACITY_KG = 10000.0


def compute_rebar_weights_by_section(
    contracts: list[dict[str, Any]], extraction: dict[str, Any]
) -> dict[str, float]:
    """section_code -> total rebar weight in kg for that section, length x rate summed across
    every rebar item found (see rebar_item_weight_kg - rate is the item's own kg_per_meter if
    given, else the fixed GOST catalog by diameter). Only the 4 rebar-bearing sections can appear;
    a section with items but zero computable weight (no length/diameter data at all) still gets an
    entry of 0.0, not omitted, so downstream code doesn't have to guess whether "missing" means
    "no rebar" or "rebar present but unweighable"."""
    lookup = build_rebar_lookup(contracts, extraction)
    weights: dict[str, float] = {}
    for sec_code in METAL_SECTION_ORDER:
        total = 0.0
        for item in lookup.get(sec_code, []):
            weight = rebar_item_weight_kg(item)
            if weight is not None:
                total += weight
        weights[sec_code] = total
    return weights


def compute_rebar_crane_allocation(weights_by_section: dict[str, float]) -> dict[str, int]:
    """section_code -> automatically allocated crane/truck shifts for rebar delivery, using the
    existing box_calculator threshold-by-10-tonnes logic (experiments/box_calculator/
    metal_delivery_allocator.py) - the first truck goes to the first section with any weight,
    later trucks go to whichever section's cumulative weight crosses the next 10-tonne boundary.
    unit_price is 0 here - this call only needs allocated_trucks, not a cost (pricing for these
    lines already comes from the normal price_keys mechanism on sheet 02)."""
    sections = [
        MetalSection(section_code=code, section_name=code, metal_weight_kg=weights_by_section.get(code, 0.0))
        for code in METAL_SECTION_ORDER
    ]
    result = allocate_metal_deliveries(sections=sections, capacity_kg=METAL_TRUCK_CAPACITY_KG, unit_price=0.0)
    return {item["section_code"]: item["allocated_trucks"] for item in result["sections"]}


def build_workbook_from_extraction(
    contract_paths: list[Path],
    extraction_path: Path,
    output_path: Path,
    price_registry_path: Path | None = DEFAULT_PRICE_REGISTRY,
    manual_values_registry_path: Path | None = DEFAULT_MANUAL_VALUES_REGISTRY,
) -> dict[str, Any]:
    contracts = [load_yaml_contract(path) for path in contract_paths]
    extraction = json.loads(extraction_path.read_text(encoding="utf-8"))

    price_registry = None
    if price_registry_path is not None and price_registry_path.exists():
        price_registry = load_price_registry(price_registry_path)
    manual_values_registry = None
    if manual_values_registry_path is not None and manual_values_registry_path.exists():
        manual_values_registry = load_manual_values_registry(manual_values_registry_path)
    rebar_lookup = build_rebar_lookup(contracts, extraction)

    wb = Workbook()
    build_constructor_sheet(wb, contracts)
    counts = build_project_sheet_from_extraction(wb, contracts, extraction)
    build_manual_values_sheet(wb, contracts, manual_values_registry=manual_values_registry)
    build_prices_sheet(wb, contracts, price_registry=price_registry, rebar_lookup=rebar_lookup)
    detail_counts = build_details_sheet_from_extraction(wb, extraction)
    build_instruction_sheet(wb)
    build_contracts_summary_sheet(wb, contracts)
    build_raw_contracts_sheet(wb, contracts)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    return {"output_path": str(output_path), **counts, **detail_counts}


def next_versioned_path(path: Path) -> Path:
    """Appends/bumps a _vN suffix so repeated builds never overwrite the previous one (a real
    review session rebuilds this file many times while iterating) - ark_review_workbook_with_
    prices.xlsx -> ..._v1.xlsx, then _v2.xlsx, etc., based on the highest _vN already present
    in the target directory. Re-versions cleanly if the given path already ends in _vN."""
    match = re.match(r"^(.*)_v(\d+)$", path.stem)
    base_stem = match.group(1) if match else path.stem
    max_version = 0
    if path.parent.exists():
        for existing in path.parent.glob(f"{base_stem}_v*{path.suffix}"):
            existing_match = re.match(rf"^{re.escape(base_stem)}_v(\d+)$", existing.stem)
            if existing_match:
                max_version = max(max_version, int(existing_match.group(1)))
    return path.parent / f"{base_stem}_v{max_version + 1}{path.suffix}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("extraction_json", help="Path to a real extraction_output.json")
    parser.add_argument(
        "--output",
        default=str(PIPELINE_DIR / "output" / "step_20_populated_from_real_extraction.xlsx"),
    )
    parser.add_argument(
        "--price-registry",
        default=str(DEFAULT_PRICE_REGISTRY),
        help="Path to a price_registry_filled_v*.xlsx; pass an empty string to skip price fill.",
    )
    parser.add_argument(
        "--manual-values-registry",
        default=str(DEFAULT_MANUAL_VALUES_REGISTRY),
        help="Path to manual_values_registry.xlsx; pass an empty string to skip sheet 01-1 fill.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    price_registry_path = Path(args.price_registry) if args.price_registry else None
    manual_values_registry_path = Path(args.manual_values_registry) if args.manual_values_registry else None
    output_path = next_versioned_path(Path(args.output))
    result = build_workbook_from_extraction(
        default_contract_paths(),
        Path(args.extraction_json),
        output_path,
        price_registry_path,
        manual_values_registry_path,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
