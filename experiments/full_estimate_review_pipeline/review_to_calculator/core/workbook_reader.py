"""Reads a filled review_workbook.xlsx (sheets 01 + 02 only) into a normalized dict.

⚠️ Sheet 03 (`03_Детали объемов`) is never read here. It is a read-only mirror for Elena
to compare against the PDF spec table by eye - the adapter's only two data sources are
sheet 01 (`01_Проверка проекта`) and sheet 02 (`02_Цены себестоимости`). See
../ADAPTER_BUILD_PLAN.md, "Критическое правило", for why.

Sheet 01 has two kinds of rows:
- Scalar rows (true scalar parameters + supplier_inputs only): one row per `technical_key`,
  value in "Найдено в проекте" unless "Исправить / ввести значение" is filled, which then
  wins.
- Repeated_rows item rows (rebar/beams, AND diagnostic-only groups like trench_routes/
  communications_pipe_items since 2026-07-29 - see `core.contract_loader.
  production_repeated_row_params` / `diagnostic_repeated_row_params`): one row per real item,
  found in a block below a local header. The row's structured data lives in the hidden
  `row_data_json` column; the visible "Исправить: <поле>" columns (fixed positions N-Q,
  in the same order as the contract's own `correction_columns` list) override individual
  fields of that JSON when Elena has typed something into them. Column letters N-Q carry
  a different field meaning per block/group - only `contract_loader`'s per-group
  `correction_columns` order tells you which is which, not the sheet itself. Diagnostic
  groups' item data is NOT read back into calculator input by `read_production_item_rows`
  (production_repeated_row_params still filters to production_input: true only) - it exists
  on sheet 01 for Elena to see/correct against the PDF, not as a calculator source; the
  calculator still reads the reviewed scalar (e.g. trench_volume_m3) as before.
"""

from __future__ import annotations

import json
from typing import Any

from openpyxl.utils import column_index_from_string

from core.contract_loader import (
    all_review_parameters,
    all_supplier_inputs,
    diagnostic_repeated_row_params,
    price_keys as contract_price_keys,
    production_repeated_row_params,
)
from core.normalization import cell_text, is_blank, parse_number

SHEET_01_NAME = "01_Проверка проекта"
SHEET_01_1_NAME = "01-1_Ручные строки (справочник)"
SHEET_02_NAME = "02_Цены себестоимости"

# 2026-08-05: PROJECT_HEADERS (A-N, 14 columns incl. target_code) grew by one column since this
# was first written 2026-07-13 against a 13-column layout - correction slots and row_data_json
# shifted right by one (O-R + S, not N-Q + R). Verified against build_review_workbook_from_
# contracts.py's PROJECT_HEADERS/CORRECTION_SLOTS/ITEM_BLOCK_HEADERS directly, not by trial.
CORRECTION_COLUMN_LETTERS = ["O", "P", "Q", "R"]
JSON_COLUMN_LETTER = "S"
TECHNICAL_KEY_HEADER = "technical_key"


def find_header_row(ws, required_headers: list[str]) -> int:
    required = {header.lower() for header in required_headers}
    for row_idx in range(1, ws.max_row + 1):
        row_values = {cell_text(ws.cell(row_idx, col).value).lower() for col in range(1, ws.max_column + 1)}
        if required.issubset(row_values):
            return row_idx
    raise ValueError(f"Cannot find header row for {required_headers} in sheet {ws.title!r}")


def header_map(ws, header_row: int) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for col in range(1, ws.max_column + 1):
        header = cell_text(ws.cell(header_row, col).value)
        if header and header not in mapping:
            mapping[header] = col
    return mapping


def cell_by_header(ws, row_idx: int, col_map: dict[str, int], header: str) -> Any:
    col = col_map.get(header)
    return ws.cell(row_idx, col).value if col else None


def read_scalar_parameters(wb, contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Reads sheet 01's flat rows: true scalar review_parameters and supplier_inputs only.
    All repeated_rows groups (production AND diagnostic-only) render as per-item blocks
    instead of a flat row now - use `read_production_item_rows` for those."""
    known_keys = {
        param["key"]
        for param in all_review_parameters(contract) + all_supplier_inputs(contract)
    }
    repeated_row_keys = {
        param["key"]
        for param in production_repeated_row_params(contract) + diagnostic_repeated_row_params(contract)
    }
    scalar_keys = known_keys - repeated_row_keys
    section = contract["section"]["code"]

    ws = wb[SHEET_01_NAME]
    header_row = find_header_row(ws, [TECHNICAL_KEY_HEADER])
    col_map = header_map(ws, header_row)

    result: dict[str, dict[str, Any]] = {}
    for row_idx in range(header_row + 1, ws.max_row + 1):
        # `technical_key` is not unique across sections (e.g. beam_items/beams_concrete_volume_m3
        # are declared by both floor_slab_1 and floor_slab_2) - section_code disambiguates.
        if cell_text(cell_by_header(ws, row_idx, col_map, "section_code")) != section:
            continue
        technical_key = cell_text(cell_by_header(ws, row_idx, col_map, TECHNICAL_KEY_HEADER))
        if technical_key not in scalar_keys:
            continue
        found_value = cell_by_header(ws, row_idx, col_map, "Найдено в проекте")
        override_value = cell_by_header(ws, row_idx, col_map, "Исправить / ввести значение")
        override_text = cell_text(override_value)
        selected = override_value if not is_blank(override_text) else found_value
        result[technical_key] = {
            "value": selected,
            "value_number": parse_number(selected),
            "unit": cell_text(cell_by_header(ws, row_idx, col_map, "Ед.")),
            "override_used": not is_blank(override_text),
            "found_value": found_value,
            "override_value": override_value,
            "source_class": cell_text(cell_by_header(ws, row_idx, col_map, "source_class")),
            "target_code": cell_text(cell_by_header(ws, row_idx, col_map, "target_code")),
        }

    # 2026-08-05: fields with source_class in {MANUAL_REVIEW, SUPPLIER_INPUT} never render on
    # sheet 01 at all (see build_review_workbook_from_contracts.py's scalar_review_rows_for_
    # contract() / MANUAL_VALUE_SOURCE_CLASSES) - they render on sheet 01-1 instead, in a
    # completely different column layout. Found via schiedel_vent_channels.schiedel_delivery_trips:
    # `known_keys` above already included every supplier_inputs key (the set union on line 85 was
    # correct), but nothing ever read sheet 01-1 to actually populate them, so every such field -
    # not just this one, every section's required crane/pump/delivery-truck manual field - was
    # silently absent from scalar_parameters no matter what Elena filled in. Merging sheet 01-1's
    # values in here (rather than a separate top-level key in read_review_workbook()'s return)
    # keeps every existing build_input.py's `scalars.get(key)` lookup working unchanged regardless
    # of which sheet the field actually lives on.
    result.update(read_manual_values(wb, contract))
    return result


def read_manual_values(wb, contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Reads sheet 01-1's rows - MANUAL_REVIEW/SUPPLIER_INPUT scalar fields, a different
    layout from sheet 01 (no "Найдено в проекте"/"technical_key" headers; project value wins
    over the sheet's own "Типовое значение (справочник)" when filled). Returns the same
    per-key dict shape as read_scalar_parameters() so callers can treat both sources
    identically."""
    if SHEET_01_1_NAME not in wb.sheetnames:
        return {}
    known_keys = {
        param["key"]
        for param in all_review_parameters(contract) + all_supplier_inputs(contract)
    }
    section = contract["section"]["code"]

    ws = wb[SHEET_01_1_NAME]
    header_row = find_header_row(ws, ["key", "section_code"])
    col_map = header_map(ws, header_row)

    result: dict[str, dict[str, Any]] = {}
    for row_idx in range(header_row + 1, ws.max_row + 1):
        if cell_text(cell_by_header(ws, row_idx, col_map, "section_code")) != section:
            continue
        key = cell_text(cell_by_header(ws, row_idx, col_map, "key"))
        if key not in known_keys:
            continue
        typical_value = cell_by_header(ws, row_idx, col_map, "Типовое значение (справочник)")
        override_value = cell_by_header(ws, row_idx, col_map, "Исправить для этого проекта")
        override_text = cell_text(override_value)
        selected = override_value if not is_blank(override_text) else typical_value
        result[key] = {
            "value": selected,
            "value_number": parse_number(selected),
            "unit": cell_text(cell_by_header(ws, row_idx, col_map, "Ед.")),
            "override_used": not is_blank(override_text),
            "found_value": typical_value,
            "override_value": override_value,
            "source_class": "",
            "target_code": "",
        }
    return result


def read_production_item_rows(wb, contract: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Reads real per-item rows for production repeated_rows groups (rebar/beams).
    Returns {group_key: [item_dict, ...]}, empty lists for groups with no rows yet
    (an empty template, or a section whose beams/rebar group is legitimately empty)."""
    groups = {param["key"]: param for param in production_repeated_row_params(contract)}
    result: dict[str, list[dict[str, Any]]] = {key: [] for key in groups}
    if not groups:
        return result

    section = contract["section"]["code"]
    ws = wb[SHEET_01_NAME]
    header_row = find_header_row(ws, [TECHNICAL_KEY_HEADER])
    col_map = header_map(ws, header_row)
    technical_key_col = col_map[TECHNICAL_KEY_HEADER]
    section_code_col = col_map["section_code"]
    json_col = column_index_from_string(JSON_COLUMN_LETTER)
    correction_cols = [column_index_from_string(letter) for letter in CORRECTION_COLUMN_LETTERS]

    for row_idx in range(header_row + 1, ws.max_row + 1):
        # technical_key alone is not unique across sections (e.g. beam_items is declared
        # by both floor_slab_1 and floor_slab_2) - must also match section_code.
        if cell_text(ws.cell(row_idx, section_code_col).value) != section:
            continue
        technical_key = cell_text(ws.cell(row_idx, technical_key_col).value)
        if technical_key not in groups:
            continue
        raw_json = ws.cell(row_idx, json_col).value
        if is_blank(raw_json):
            continue
        try:
            item = json.loads(raw_json)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError(
                f"{contract['section']['code']}: sheet 01 row {row_idx}, group "
                f"{technical_key!r} has an unreadable row_data_json: {raw_json!r}"
            ) from exc

        correction_keys = groups[technical_key].get("correction_columns") or []
        for slot_idx, field_key in enumerate(correction_keys):
            if slot_idx >= len(correction_cols):
                break
            override_text = cell_text(ws.cell(row_idx, correction_cols[slot_idx]).value)
            override_value = parse_number(override_text)
            if override_value is not None:
                item[field_key] = override_value

        result[technical_key].append(item)

    return result


def template_price_keys(contract: dict[str, Any]) -> set[str]:
    """Keys whose contract-declared registry_code is the rebar per-item placeholder pattern
    (contains "<class>" and "<diameter>", e.g. "rebar_<class>_d<diameter>_m") rather than one
    real registry code. Sheet 02 expands these into one row per steel_class/diameter_mm
    actually found in the project (see build_review_workbook_from_contracts.py's
    expand_rebar_codes()/_append_price_row()) - every expanded row shares the SAME
    calc_price_key (the static contract key) but carries its own real price_registry_code, so
    a plain {calc_price_key: row} dict would silently collide and keep only the last row. See
    resolve_prices()/build_input.py for how these are consumed.

    Matches specifically on "<class>"/"<diameter>", not a bare "<" - a bare check wrongly
    caught flat_roof's slope_plate_unit_price_per_m3 (registry_code
    "roof_eps_slope_<type>_m3"), which is NOT a per-item expansion: sheet 02 only ever has one
    row for it, "<type>" is just documentation-style placeholder text in the contract. The
    bare check would have made resolve_prices() return a single-entry {registry_code: price}
    dict instead of a plain float for it, and - more seriously - silently skip the "required
    price missing" check that template keys are deliberately exempted from. Found 2026-08-05
    while building the flat_roof adapter; confirmed by grepping every section_contract.yaml
    that no other registry_code uses any other placeholder pattern."""
    return {
        price["key"]
        for price in contract_price_keys(contract)
        if "<class>" in (price.get("registry_code") or "") and "<diameter>" in (price.get("registry_code") or "")
    }


def read_prices(wb, contract: dict[str, Any]) -> dict[str, dict[str, Any] | list[dict[str, Any]]]:
    known_keys = {price["key"] for price in contract_price_keys(contract)}
    templates = template_price_keys(contract)
    section = contract["section"]["code"]

    ws = wb[SHEET_02_NAME]
    header_row = find_header_row(ws, ["calc_price_key"])
    col_map = header_map(ws, header_row)

    result: dict[str, dict[str, Any] | list[dict[str, Any]]] = {}
    for row_idx in range(header_row + 1, ws.max_row + 1):
        # calc_price_key is not unique across sections (e.g. eps100_unit_price is declared
        # by waterproofing, floor_slab_2, and foundation_slab) - section_code disambiguates.
        if cell_text(cell_by_header(ws, row_idx, col_map, "section_code")) != section:
            continue
        calc_price_key = cell_text(cell_by_header(ws, row_idx, col_map, "calc_price_key"))
        if calc_price_key not in known_keys:
            continue
        registry_value = parse_number(cell_by_header(ws, row_idx, col_map, "Цена из прайса"))
        fallback_value = parse_number(cell_by_header(ws, row_idx, col_map, "Цена fallback"))
        price_for_calculation = parse_number(cell_by_header(ws, row_idx, col_map, "Цена для расчета"))
        override_text = cell_by_header(ws, row_idx, col_map, "Исправить цену")
        override_value = parse_number(override_text)
        selected_price = override_value if override_value is not None else price_for_calculation
        row_data = {
            "price_registry_value": registry_value,
            "fallback_value": fallback_value,
            "price_for_calculation": price_for_calculation,
            "override_value": override_value,
            "selected_price": selected_price,
            "override_used": override_value is not None,
            "price_registry_code": cell_text(cell_by_header(ws, row_idx, col_map, "price_registry_code")),
            "fallback_key": cell_text(cell_by_header(ws, row_idx, col_map, "fallback_key")),
        }
        if calc_price_key in templates:
            # Multiple rows share this calc_price_key (one per steel_class/diameter_mm) -
            # accumulate into a list instead of overwriting a single dict.
            result.setdefault(calc_price_key, [])
            result[calc_price_key].append(row_data)
        else:
            result[calc_price_key] = row_data
    return result


def read_project_name(wb) -> str:
    """Sheet 01's merged A1 title is "Разбор проекта: <адрес с титульного листа>" (set by
    populate_review_workbook_from_extraction.py's build_project_sheet_from_extraction()) - the
    only place a real project label exists on the reviewed workbook. Strips the fixed prefix;
    falls back to the raw cell text if the prefix isn't there (e.g. an empty-template workbook
    with no extraction JSON behind it yet)."""
    ws = wb[SHEET_01_NAME]
    title = cell_text(ws["A1"].value)
    prefix = "Разбор проекта: "
    if title.startswith(prefix):
        return title[len(prefix):]
    return title


def read_review_workbook(wb, contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "section_code": contract["section"]["code"],
        "project_name": read_project_name(wb),
        "scalar_parameters": read_scalar_parameters(wb, contract),
        "production_items": read_production_item_rows(wb, contract),
        "prices": read_prices(wb, contract),
    }
