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
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "experiments" / "box_calculator"))

from metal_delivery_allocator import MetalSection, allocate_metal_deliveries  # noqa: E402

from build_review_workbook_from_contracts import (  # noqa: E402
    COMPACT_ROW_HEIGHT,
    FILL_CRITICAL_REVIEW,
    FILL_FOUND,
    FILL_HEADER,
    FILL_INPUT,
    FILL_MISSING,
    FILL_REVIEW,
    FILL_TECH,
    FILL_WHITE,
    FONT_NAME,
    ITEM_BLOCK_HEADERS,
    PROJECT_HEADERS,
    apply_table_style,
    append_block,
    autofit_row_heights,
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
    hide_diagnostic_sheets,
    load_manual_values_registry,
    load_price_registry_google_first,
    load_yaml_contract,
    merge_row_full_width,
    production_repeated_row_params,
    rebar_group_keys_for_contract,
    rebar_item_delivery_weight_kg,
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
INACTIVE_ROW_HEIGHT = 9
FILL_REBAR_SUMMARY_TITLE = PatternFill("solid", fgColor="FFE599")


def project_status_fill(status: str):
    """Visual status colors for sheet 01 rows."""
    if status.startswith("Найдено"):
        return FILL_FOUND
    if status.startswith("Проверьте"):
        return FILL_REVIEW
    if status.startswith("Не найдено"):
        return FILL_MISSING
    if status.startswith("Не требуется"):
        return FILL_WHITE
    return FILL_REVIEW


def hide_inactive_project_rows(ws) -> None:
    """Hide 'not required for this project' scalar rows on sheet 01.

    White rows with a "Не требуется..." status are traceability/diagnostics for optional
    scalar fields, not something Elena needs to review. Keep the data in the workbook for
    audit/read-back safety, but hide the row in Excel. Do not hide grey СПРАВОЧНО repeated
    tables here: non-empty reference tables still help Elena compare extracted rows with the
    PDF.
    """
    for row_idx in range(1, ws.max_row + 1):
        status = str(ws.cell(row_idx, 4).value or "")
        if not status.startswith("Не требуется"):
            continue
        ws.row_dimensions[row_idx].hidden = True
        ws.row_dimensions[row_idx].height = INACTIVE_ROW_HEIGHT
        for cell in ws[row_idx]:
            cell.fill = FILL_WHITE
            cell.font = Font(name=FONT_NAME, size=9, color="666666")
            cell.alignment = Alignment(wrap_text=False, vertical="center")


def append_blank_project_row(ws) -> None:
    """A real visual spacer on sheet 01; kept unmerged so table filters/readers ignore it."""
    ws.append([""] * len(PROJECT_HEADERS))
    for cell in ws[ws.max_row]:
        cell.fill = FILL_WHITE
    ws.row_dimensions[ws.max_row].height = COMPACT_ROW_HEIGHT


def style_rebar_summary_title_row(ws, row_idx: int) -> None:
    for cell in ws[row_idx]:
        cell.fill = FILL_REBAR_SUMMARY_TITLE
        cell.font = Font(name=FONT_NAME, bold=True, size=10)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[row_idx].height = 22


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


def group_items(found_groups: dict[str, list[Any]], group_key: str) -> list[dict[str, Any]]:
    return [item for item in found_groups.get(group_key, []) if isinstance(item, dict)]


def sum_group_numeric_field(found_groups: dict[str, list[Any]], group_key: str, field_key: str) -> float | None:
    total = 0.0
    found_any = False
    for item in group_items(found_groups, group_key):
        value = item.get("value") or {}
        field_value = value.get(field_key)
        if field_value is None:
            continue
        total += float(field_value)
        found_any = True
    return round(total, 3) if found_any else None


def sum_communications_pipe_items(found_groups: dict[str, list[Any]]) -> float | None:
    total = 0.0
    found_any = False
    for item in group_items(found_groups, "communications_pipe_items"):
        value = item.get("value") or {}
        # 2026-08-25: real ЮСВ extraction carries include_in_communications=None (key present,
        # value None - "not specified", not "explicitly excluded") on every single row. The old
        # `value.get("include_in_communications", True)` only applies the True default when the
        # KEY IS ABSENT - a present-but-None value bypasses the default entirely and returns
        # None, so `not None` was True and every row got skipped, found_any stayed False, and
        # the whole communications_length_m alternative-scalar silently came back None on a
        # project that has 115m of real, fully summable pipe data. Skip only on an EXPLICIT
        # False; None/absent both mean "no exclusion stated" and should be included.
        if value.get("include_in_communications") is False:
            continue
        explicit_total = value.get("total_length_m")
        if explicit_total is not None:
            total += float(explicit_total)
            found_any = True
            continue
        pipe_length = value.get("pipe_length_m")
        quantity = value.get("quantity")
        if pipe_length is not None and quantity is not None:
            total += float(pipe_length) * float(quantity)
            found_any = True
    return round(total, 3) if found_any else None


def min_group_confidence(found_groups: dict[str, list[Any]], group_key: str) -> str:
    values: list[float] = []
    for item in group_items(found_groups, group_key):
        try:
            values.append(float(item.get("confidence")))
        except (TypeError, ValueError):
            continue
    return f"{min(values):.2f}" if values else ""


def group_has_needs_review(found_groups: dict[str, list[Any]], group_key: str) -> bool:
    return any(bool(item.get("needs_review")) for item in group_items(found_groups, group_key))


def project_group_items_for_review(extraction: dict[str, Any], sec_code: str) -> dict[str, list[Any]]:
    """Group rows that must be visible on sheet 01: confident rows plus review rows.

    Scalars keep their old found/missing logic, but repeated groups are different: if the model
    extracted a row and marked it needs_review, Elena still needs to see that row. Otherwise a
    project can silently lose rows between extraction and the workbook (a real project case:
    K2/K3 trench routes moved from found to needs_review, and the old sheet total dropped from
    79.64 m3 to 25.71 m3).
    """
    section = (extraction.get("sections") or {}).get(sec_code) or {}
    groups: dict[str, list[Any]] = {}
    # Maps group_code -> {value_key -> index into groups[group_code]}, so a duplicate seen later
    # can still upgrade the row already kept, instead of being silently dropped.
    seen: dict[str, dict[str, int]] = {}
    for bucket_name in ("found", "needs_review"):
        for item in section.get(bucket_name) or []:
            if not isinstance(item, dict):
                continue
            group_code = item.get("group_code")
            if not group_code:
                continue
            # Some correction-pass JSONs keep the same repeated item in both found and
            # needs_review (the schema's own found/needs_review mirroring - not a genuine
            # duplicate). Sheet 01 should show one project row, not a duplicate physical item -
            # but if EITHER copy is the needs_review one, the merged row must end up
            # needs_review=True. A real, confirmed case (TRC 2026-08-18, floor_slabs "ребро 50мм в
            # теле плиты перекрытия"): the model put the same row in both found (needs_review:
            # false baked into the item) and needs_review (explaining an unresolved assumption -
            # "другие размеры не додумывались"). Since found is iterated first, the old code kept
            # that first-seen copy and just `continue`d past the needs_review copy, so the
            # needs_review=True override on line ~249 never ran - the row rendered as a normal,
            # non-critical found row with two blank fields (length_m/width_m) and no red
            # highlight, even though the model was explicitly unsure and no calculator fallback
            # exists for those fields (build_input.py routes it into beam_only_concrete_items
            # instead, material-only, no length-priced line - a real, silent scope loss vs
            # Elena's own smeta, not a bug in that reroute itself).
            value_key = json.dumps(item.get("value") or {}, ensure_ascii=False, sort_keys=True)
            group_seen = seen.setdefault(group_code, {})
            existing_index = group_seen.get(value_key)
            if existing_index is not None:
                if bucket_name == "needs_review":
                    groups[group_code][existing_index]["needs_review"] = True
                continue
            item_for_sheet = dict(item)
            if bucket_name == "needs_review":
                item_for_sheet["needs_review"] = True
            groups.setdefault(group_code, []).append(item_for_sheet)
            group_seen[value_key] = len(groups[group_code]) - 1
    return groups


class Sheet01BuildRegistry:
    """Small self-check registry for sheet 01.

    The workbook is still rendered exactly as before; this object only records what actually made
    it to the sheet so the builder can fail before saving when a contract row or extracted
    repeated item silently disappears.
    """

    def __init__(self) -> None:
        self.scalar_rows: set[tuple[str, str]] = set()
        self.repeated_items: dict[tuple[str, str], set[str]] = {}
        self.repeated_fields: dict[tuple[str, str], set[tuple[str, str | None]]] = {}

    def record_scalar(self, sec_code: str, param: dict[str, Any]) -> None:
        key = str(param.get("target_code") or param.get("key") or "")
        if key:
            self.scalar_rows.add((sec_code, key))

    def record_repeated_item(self, sec_code: str, group_key: str, item_id: str) -> None:
        self.repeated_items.setdefault((sec_code, group_key), set()).add(item_id)

    def record_repeated_field(
        self, sec_code: str, group_key: str, item_id: str, field_key: str | None
    ) -> None:
        self.record_repeated_item(sec_code, group_key, item_id)
        self.repeated_fields.setdefault((sec_code, group_key), set()).add((item_id, field_key))


def earthworks_alternative_scalar(
    target_code: str,
    found_groups: dict[str, list[Any]],
) -> tuple[Any, str, str, str, str] | None:
    """Return a sheet-01 scalar replacement when earthworks data is present as item rows."""
    if target_code == "pit_excavation_depth_m" and group_items(found_groups, "pit_items"):
        total = sum_group_numeric_field(found_groups, "pit_items", "volume_m3")
        return (
            "",
            "Не требуется (есть готовые объёмы выемки ниже)",
            "",
            f"Глубина не используется: объём механизированной выемки берётся из pit_items. Сумма: {total:g} м3.",
            min_group_confidence(found_groups, "pit_items"),
        )
    if target_code == "sand_base_volume_m3" and group_items(found_groups, "sand_items"):
        total = sum_group_numeric_field(found_groups, "sand_items", "volume_m3")
        return (
            "",
            "Не требуется (есть готовые объёмы песка ниже)",
            "",
            "Песок берётся из sand_items по категориям, не из одной строки 'под основание'. "
            f"Сумма до коэффициента: {total:g} м3.",
            min_group_confidence(found_groups, "sand_items"),
        )
    if target_code == "communications_length_m" and group_items(found_groups, "communications_pipe_items"):
        total = sum_communications_pipe_items(found_groups)
        if total is None:
            # Real 2026-08-25 case (ЮСВ): rows exist in communications_pipe_items, but none of
            # them carry a summable length (all fittings/elbows with include_in_communications
            # false, or missing total_length_m/pipe_length_m+quantity) - sum_communications_
            # pipe_items() returns None for exactly this "found rows, nothing to add" case. Fall
            # through to the normal scalar path instead of crashing on `f"{None:g}"` below.
            return None
        has_review = group_has_needs_review(found_groups, "communications_pipe_items")
        return (
            total,
            "Проверьте (автосумма строк труб ниже)" if has_review else "Найдено (автосумма строк труб ниже)",
            "",
            "Сумма включённых позиций communications_pipe_items: "
            f"{total:g} м. Позиции без линейной длины (углы, тройники, заглушки) не добавляют метры.",
            min_group_confidence(found_groups, "communications_pipe_items"),
        )
    if target_code == "trench_volume_m3" and group_items(found_groups, "trench_routes"):
        total = sum_group_numeric_field(found_groups, "trench_routes", "volume_m3")
        has_review = group_has_needs_review(found_groups, "trench_routes")
        return (
            total,
            "Проверьте (автосумма маршрутов ниже)" if has_review else "Найдено (автосумма маршрутов ниже)",
            "",
            f"Сумма volume_m3 из trench_routes: {total:g} м3.",
            min_group_confidence(found_groups, "trench_routes"),
        )
    return None


def candidate_sum_scalar(item: dict[str, Any] | None, target_code: str) -> tuple[float, str, str] | None:
    if item is None or item.get("value") is not None:
        return None
    candidates = [candidate for candidate in item.get("candidates") or [] if isinstance(candidate, dict)]
    matching_values: list[float] = []
    fragments: list[str] = []
    confidences: list[float] = []
    for candidate in candidates:
        # Same reasoning as eps100_component_area_from_candidates above: `item` is already
        # the caller's found_by_target[target_code] entry, so a null/absent candidate
        # target_code implicitly belongs to it. Only skip when a candidate explicitly names a
        # DIFFERENT target_code (real case: 2026-08-04 heavy-audit, candidates mismarked with
        # a sibling target). A bare `!=` check here always failed (null != non-null string),
        # silently returning None for every AUTO_SUM_CANDIDATE_TARGETS entry across all 4
        # sections that use this function.
        candidate_target = candidate.get("target_code")
        if candidate_target and candidate_target != target_code:
            continue
        value = candidate.get("value")
        if value is None:
            continue
        try:
            matching_values.append(float(value))
        except (TypeError, ValueError):
            continue
        raw_text = candidate.get("raw_text")
        if raw_text:
            fragments.append(str(raw_text))
        try:
            confidences.append(float(candidate.get("confidence")))
        except (TypeError, ValueError):
            pass
    if len(matching_values) < 2:
        return None
    confidence = f"{min(confidences):.2f}" if confidences else display_confidence(item)
    return round(sum(matching_values), 3), "; ".join(fragments), confidence


def candidate_component_fragments(item: dict[str, Any], limit: int = 4) -> str:
    fragments: list[str] = []
    for candidate in item.get("candidates") or []:
        if not isinstance(candidate, dict):
            continue
        value = candidate.get("value")
        unit = candidate.get("unit") or candidate.get("normalized_unit") or ""
        raw_text = candidate.get("raw_text") or candidate.get("notes") or candidate.get("item_name")
        parts = []
        if value is not None:
            parts.append(f"{value}{' ' + str(unit) if unit else ''}")
        if raw_text:
            parts.append(str(raw_text))
        if parts:
            fragments.append(" — ".join(parts))
    if len(fragments) > limit:
        fragments = fragments[:limit] + [f"... ещё {len(fragments) - limit} кандидатов"]
    return "; ".join(fragments)


def unresolved_candidate_fragment(item: dict[str, Any]) -> str:
    fragments = candidate_component_fragments(item)
    note = item.get("notes") or "Есть несколько candidates, но для этого target_code нет универсального правила автосуммы."
    if not fragments:
        return humanize_visible_text(str(note))
    return humanize_visible_text(f"{note} Автосумма не применена; проверьте компоненты: {fragments}")


def humanize_visible_text(text: str) -> str:
    return (
        text.replace("(P6, новая зональная модель)", "")
        .replace("P6-зона", "Зона раздела стен и перемычек")
        .replace("P6-калькулятор", "Калькулятор стен и перемычек")
        .replace("P6 ", "раздела стен и перемычек ")
        .replace(" P6", " раздела стен и перемычек")
        .replace("правилу P6", "правилу раздела стен и перемычек")
    )


def item_fragment(item: dict[str, Any] | None) -> str:
    if item is None:
        return ""
    raw_text = str(item.get("raw_text") or "")
    notes = str(item.get("notes") or "")
    if raw_text and notes and notes not in raw_text:
        return humanize_visible_text(f"{raw_text}\nNotes: {notes}")
    return humanize_visible_text(raw_text or notes)


AUTO_SUM_CANDIDATE_TARGETS = {
    # Kept in sync by hand with build_extraction_notes_report.py's copy of this same dict
    # (2026-08-08: the two had drifted - this file was missing the four
    # lintel_concrete_volume-family entries below, the other file was missing
    # cutoff_waterproofing_load_bearing_walls_area). If you add a new AUTO_SUM_CANDIDATE_TARGETS
    # entry, add it to both files. Note: entries here only actually fire on sheet 01 if the
    # matching section's `*_alternative_scalar` function below also dispatches to
    # candidate_sum_scalar for that target_code - the four lintel_concrete_volume-family entries
    # are listed for parity with the notes-report script but are NOT currently wired to any
    # dispatch branch here (no known real project needed them yet on the workbook side).
    "foundation_slab": {
        "membrane_area_m2": "компонентов мембраны",
    },
    "flat_roof": {
        "roof_internal_drains_count": "внутренних кровельных воронок",
        "roof_parapet_drains_count": "парапетных воронок",
    },
    "load_bearing_walls_lintels": {
        # Elena's rule 2026-07-25: external + internal load-bearing wall areas are the same
        # continuous wall body (differ only by block thickness) - sum them when the PDF gives no
        # ready total. Already in the extraction prompt (calculator_targets_compact.json), but the
        # model doesn't always apply it - this is the workbook-side safety net so it doesn't just
        # sit as an unresolved needs_review when it doesn't. See
        # cutoff_waterproofing_external_internal_sum memory.
        "cutoff_waterproofing_load_bearing_walls_area": "наружных и внутренних несущих стен",
        "lintel_concrete_volume": "компонентов бетона перемычек в U-блоках",
        "floor_2_lintel_concrete_volume": "компонентов бетона перемычек в U-блоках",
        "floor_1_lintel_monolithic_concrete_volume": "компонентов бетона монолитных перемычек",
        "floor_2_lintel_monolithic_concrete_volume": "компонентов бетона монолитных перемычек",
    },
}


def group_sources(found_groups: dict[str, list[Any]], group_key: str) -> str:
    sources: list[str] = []
    for item in group_items(found_groups, group_key):
        parts = []
        if item.get("source_pdf"):
            parts.append(str(item["source_pdf"]))
        if item.get("page_number") is not None:
            parts.append(f"стр. {item['page_number']}")
        source = ", ".join(parts)
        if source and source not in sources:
            sources.append(source)
    return "; ".join(sources)


def group_fragments(found_groups: dict[str, list[Any]], group_key: str, limit: int = 5) -> str:
    fragments: list[str] = []
    for item in group_items(found_groups, group_key):
        raw_text = item.get("raw_text") or item.get("notes")
        if raw_text:
            fragments.append(str(raw_text))
    if len(fragments) > limit:
        fragments = fragments[:limit] + [f"... ещё {len(fragments) - limit} строк"]
    return "; ".join(fragments)


THERMAL_INSERT_SCALAR_TARGETS = {
    "thermal_insert_50_length",
    "thermal_insert_100_length",
    "thermal_insert_combined_length_m",
    "thermal_insert_50_material_spec_qty",
    "thermal_insert_100_material_spec_qty",
}


def foundation_alternative_scalar(
    target_code: str,
    found: dict[str, Any] | None,
    found_groups: dict[str, list[Any]],
    found_by_target: dict[str, Any],
) -> tuple[Any, str, str, str, str] | None:
    if target_code == "membrane_area_m2":
        label = AUTO_SUM_CANDIDATE_TARGETS.get("foundation_slab", {}).get(target_code)
        if not label:
            return None
        candidate_sum = candidate_sum_scalar(found, target_code)
        if candidate_sum is None:
            return None
        total, fragments, confidence = candidate_sum
        return (
            total,
            "Проверьте (автосумма компонентов)",
            found.get("source_pdf") or "",
            f"Автосумма {label}: {fragments}. Общего итога в PDF нет.",
            confidence,
        )
    if target_code == "concrete_project_volume" and group_items(found_groups, "slab_zones"):
        total = sum_group_numeric_field(found_groups, "slab_zones", "concrete_volume_m3")
        return (
            total,
            "Найдено (через slab_zones)",
            group_sources(found_groups, "slab_zones"),
            "Единый итог бетона в PDF не указан; для расчёта используется сумма строк slab_zones. "
            f"Строки: {group_fragments(found_groups, 'slab_zones')}",
            min_group_confidence(found_groups, "slab_zones"),
        )
    if target_code in THERMAL_INSERT_SCALAR_TARGETS and group_items(found_groups, "thermal_insert_items"):
        length_total = sum_group_numeric_field(found_groups, "thermal_insert_items", "length_m")
        material_total = sum_group_numeric_field(found_groups, "thermal_insert_items", "material_spec_qty_m3")
        totals = []
        if length_total is not None:
            totals.append(f"длина {length_total:g} мп")
        if material_total is not None:
            totals.append(f"материал {material_total:g} м3")
        totals_text = f" ({', '.join(totals)})" if totals else ""
        return (
            "",
            "Не требуется (есть thermal_insert_items)",
            group_sources(found_groups, "thermal_insert_items"),
            "Скалярные поля 50/100 мм не заполняются, потому что PDF дал термовставки "
            f"произвольными типоразмерами; рабочий источник — строки thermal_insert_items{totals_text}. "
            f"Строки: {group_fragments(found_groups, 'thermal_insert_items')}",
            min_group_confidence(found_groups, "thermal_insert_items"),
        )
    combined_length_found = found_by_target.get("thermal_insert_combined_length_m")
    if target_code in {"thermal_insert_50_length", "thermal_insert_100_length"} and combined_length_found is not None:
        combined_value = combined_length_found.get("value")
        value_text = f"{combined_value:g} мп" if isinstance(combined_value, (int, float)) else ""
        return (
            "",
            "Не требуется (есть общая длина термовставок)",
            combined_length_found.get("source_pdf") or "",
            "Раздельная длина монтажа для этой толщины не заполняется: PDF даёт одну общую длину узла"
            f"{(' ' + value_text) if value_text else ''} на оба слоя термовставки — копировать её в оба "
            "раздельных поля нельзя, это задвоило бы работу по монтажу. Рабочий источник — "
            "thermal_insert_combined_length_m.",
            display_confidence(combined_length_found),
        )
    return None


def load_bearing_walls_lintels_alternative_scalar(
    target_code: str,
    found: dict[str, Any] | None,
    found_groups: dict[str, list[Any]],
) -> tuple[Any, str, str, str, str] | None:
    if target_code == "floors_count" and group_items(found_groups, "wall_block_items"):
        return (
            "",
            "Не требуется (этажность выводится из wall_block_items)",
            group_sources(found_groups, "wall_block_items"),
            "Текстовая этажность PDF не используется как главный источник: при наличии wall_block_items "
            "калькулятор определяет второй уровень по строкам кладки.",
            min_group_confidence(found_groups, "wall_block_items"),
        )
    if target_code in {
        "parapet_masonry_volume",
        "parapet_gas_block_d500_250_volume",
        "main_wall_gas_block_400_spec_volume",
        "main_wall_gas_block_250_spec_volume",
        "floor_2_masonry_volume",
    } and group_items(found_groups, "wall_block_items"):
        return (
            "",
            "Не требуется (объём есть в wall_block_items)",
            group_sources(found_groups, "wall_block_items"),
            "Фиксированный scalar объёма кладки не требуется, если объёмы пришли строками "
            "wall_block_items (по ролям main_walls/floor_2/parapet). Калькулятор берёт "
            "production repeated rows, а не старые одиночные поля.",
            min_group_confidence(found_groups, "wall_block_items"),
        )
    if target_code == "cutoff_waterproofing_load_bearing_walls_area":
        label = AUTO_SUM_CANDIDATE_TARGETS.get("load_bearing_walls_lintels", {}).get(target_code)
        candidate_sum = candidate_sum_scalar(found, target_code) if label else None
        if candidate_sum is None:
            return None
        total, fragments, confidence = candidate_sum
        return (
            total,
            "Проверьте (автосумма компонентов)",
            found.get("source_pdf") or "" if found else "",
            f"Автосумма {label}: {fragments}. Общего итога в PDF нет — наружные и внутренние "
            "несущие стены суммируются как одна стена (Elena, 2026-07-25); перегородки в сумму "
            "не входят.",
            confidence,
        )
    return None


# P5 (2026-08-10): floor_slab_1_alternative_scalar()/floor_slab_2_alternative_scalar() removed here.
# Both existed only to redirect an old flat scalar review_parameter (floor_slab_1_concrete_volume,
# floor_slab_1_beams_concrete_volume, floor_slab_2_beams_eps_material_area, etc.) to the zone/beam
# group data when the PDF gave zones instead of one combined total. The new sections/floor_slabs/
# section_contract.yaml has NO flat scalars at all for concrete/formwork/insulation - every one of
# those old target_codes is gone, replaced by floor_slab_zones[]/floor_slab_eps_items[]/
# floor_slab_beam_items[] columns rendered directly by the generic repeated_rows path below (the same
# path earthworks' trench_routes, load_bearing_walls_lintels' wall_block_items, etc. already use) - so
# there is nothing left for a floor_slabs-specific alternative-scalar function to redirect. The
# beam-concrete-total control check these functions partly did is now build_extraction_notes_report.
# py's floor_slab_beam_concrete_total_diagnostics() instead (a code-report diagnostic, not a sheet-01
# display fallback), and the readiness-per-role rule for insulation work lines lives in the new
# contract's floor_slab_eps_items notes.


ROOF_ZONES_FALLBACK_ONLY_TARGETS = {
    "roof_area_level_1",
    "roof_area_level_2",
    "roof_parapet_length_level_1",
    "roof_parapet_length_level_2",
    "roof_vent_wall_abutment_level_1",
    "roof_vent_wall_abutment_level_2",
}


def flat_roof_alternative_scalar(
    target_code: str,
    found: dict[str, Any] | None,
    found_groups: dict[str, list[Any]],
) -> tuple[Any, str, str, str, str] | None:
    if target_code in ROOF_ZONES_FALLBACK_ONLY_TARGETS and group_items(found_groups, "roof_zones"):
        return (
            "",
            "Не требуется (есть roof_zones)",
            group_sources(found_groups, "roof_zones"),
            "Fallback-поле уровня 1/2 не заполняется: площадь/парапет/примыкания уже пришли по зонам "
            f"в roof_zones ниже. Строки: {group_fragments(found_groups, 'roof_zones')}",
            min_group_confidence(found_groups, "roof_zones"),
        )
    label = AUTO_SUM_CANDIDATE_TARGETS.get("flat_roof", {}).get(target_code)
    if not label:
        return None
    candidate_sum = candidate_sum_scalar(found, target_code)
    if candidate_sum is None:
        return None
    total, fragments, confidence = candidate_sum
    return (
        total,
        "Проверьте (автосумма компонентов)",
        found.get("source_pdf") or "",
        f"Автосумма {label}: {fragments}. Общего итога в PDF нет.",
        confidence,
    )


def earthworks_group_total_row(
    sec_code: str,
    group_key: str,
    found_groups: dict[str, list[Any]],
    headers_len: int,
) -> list[Any] | None:
    if sec_code != "earthworks":
        return None
    if group_key == "pit_items":
        total = sum_group_numeric_field(found_groups, group_key, "volume_m3")
        unit = "м3"
        note = "Сумма готовых объёмов выемки грунта; используется вместо площадь*глубина."
    elif group_key == "sand_items":
        total = sum_group_numeric_field(found_groups, group_key, "volume_m3")
        unit = "м3"
        note = "Сумма готовых объёмов песка до коэффициента уплотнения."
    elif group_key == "trench_routes":
        total = sum_group_numeric_field(found_groups, group_key, "volume_m3")
        unit = "м3"
        note = "Сумма готовых объёмов траншей из строк маршрутов."
    elif group_key == "communications_pipe_items":
        total = sum_communications_pipe_items(found_groups)
        unit = "м"
        note = "Сумма включённых линейных труб; фитинги без длины в метры не входят."
    else:
        return None
    if total is None:
        return None

    row = [
        "Итого по строкам блока",
        total,
        unit,
        "Итого (авто по строкам блока)",
        min_group_confidence(found_groups, group_key),
        "",
        "",
        note,
        "",
        "",
        "",
        "",
        "",
        "",
    ]
    return row + [""] * max(0, headers_len - len(row))


def auto_calculated_by_key(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["key"]: entry for entry in (contract.get("auto_calculated") or []) if entry.get("key")}


# 2026-07-29: sections/fields that only exist for some projects (U-block lintels, monolithic
# lintels — per floor, independently) currently show the exact same "Не найдено" status whether
# the field is safely inapplicable or genuinely missing money-critical data. A real project case that
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

CONDITIONAL_ABSENT_TARGETS: dict[str, dict[str, str]] = {
    "load_bearing_walls_lintels": {
        "vent_chimney_gas_block_150_volume": "Не блокер, если в проекте нет обкладки вентканалов/дымохода газобетоном 150 мм. Это не Schiedel.",
        "floor_2_lintel_total_length": "Не блокер, если на 2-м этаже нет перемычек в U-блоках.",
        "floor_2_lintel_concrete_volume": "Не блокер, если на 2-м этаже нет перемычек в U-блоках.",
        "floor_2_lintel_monolithic_concrete_volume": "Не блокер, если на 2-м этаже нет монолитных перемычек.",
        "floor_2_lintel_monolithic_total_length": "Не блокер, если на 2-м этаже нет монолитных перемычек.",
        "floor_2_lintel_insulation_length": "Не блокер, если на 2-м этаже нет утепляемых монолитных перемычек.",
        "floor_2_lintel_formwork_horizontal_area": "Не блокер, если на 2-м этаже нет монолитных перемычек.",
        "floor_2_lintel_formwork_vertical_area": "Не блокер, если на 2-м этаже нет монолитных перемычек.",
        "floor_2_lintel_insulation_eps_volume": "Не блокер, если на 2-м этаже нет утепляемых монолитных перемычек.",
    },
}

DIAGNOSTIC_ONLY_MISSING_TARGETS: dict[str, dict[str, str]] = {
    "load_bearing_walls_lintels": {
        "floor_1_lintel_groove_length": "Диагностическое поле: перемычки в штробе пока фиксируются для будущей доработки и не участвуют в смете.",
        "floor_2_lintel_groove_length": "Диагностическое поле: перемычки в штробе пока фиксируются для будущей доработки и не участвуют в смете.",
    },
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


def classified_missing_target(sec_code: str, target_code: str) -> tuple[str, str] | None:
    diagnostic_note = DIAGNOSTIC_ONLY_MISSING_TARGETS.get(sec_code, {}).get(target_code)
    if diagnostic_note:
        return "Не требуется (диагностическое поле)", diagnostic_note
    conditional_note = CONDITIONAL_ABSENT_TARGETS.get(sec_code, {}).get(target_code)
    if conditional_note:
        return "Не требуется / условно отсутствует", conditional_note
    return None


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


def display_confidence(item: dict[str, Any] | None) -> str:
    if item is None:
        return ""
    confidence = item.get("confidence")
    if confidence is None:
        return ""
    try:
        return f"{float(confidence):.2f}"
    except (TypeError, ValueError):
        return str(confidence)


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


# floor_slabs group keys - match review_to_calculator/sections/floor_slabs/build_input.py's own
# constants exactly (kept as separate literals here rather than importing that module, since this
# file has no dependency on review_to_calculator otherwise).
ZONES_GROUP_KEY = "floor_slab_zones"
EPS_ITEMS_GROUP_KEY = "floor_slab_eps_items"
BEAM_ITEMS_GROUP_KEY = "floor_slab_beam_items"
REBAR_GROUP_KEY = "floor_slab_rebar_items"
ADDITIONAL_ITEMS_GROUP_KEY = "floor_slab_additional_items"
P6_WALLS_SECTION_CODE = "load_bearing_walls_lintels_p6"
P6_WALL_ZONES_GROUP_KEY = "wall_zones"
P6_WALL_BLOCK_ITEMS_GROUP_KEY = "wall_block_items"
P6_WALL_REBAR_GROUP_KEY = "wall_chasing_rebar_items"
P6_LINTEL_ITEMS_GROUP_KEY = "lintel_items"
P6_LINTEL_REBAR_GROUP_KEY = "lintel_rebar_items"


P6_WALL_FIELD_LABELS = {
    "cutoff_waterproofing_area_m2": "Отсечная гидроизоляция под первый ряд",
    "volume_m3": "Объём по спецификации",
    "material_unit_price": "Цена материала для нестандартного блока",
    "pallet_volume_m3": "Объём паллеты для нестандартного блока",
    "total_length_m": "Длина перемычек",
    "concrete_volume_m3": "Бетон перемычек",
    "formwork_horizontal_area_m2": "Горизонтальная опалубка перемычек",
    "formwork_vertical_area_m2": "Вертикальная опалубка перемычек",
    "insulation_length_m": "Длина утепляемой части перемычек",
    "insulation_eps_spec_volume_m3": "ЭППС перемычек по спецификации",
    "spec_length_m": "Длина по спецификации",
    "kg_per_meter": "Масса 1 м",
    "rod_length_m": "Длина хлыста",
}


P6_LINTEL_KIND_LABELS = {
    "u_block": "Перемычки в U-блоке",
    "monolithic": "Монолитные перемычки",
}


P6_WALL_ZONE_ORDER = {
    "floor_1": 10,
    "main_walls": 10,
    "floor_2": 20,
    "second_light": 20,
    "parapet": 30,
    "vent_chimney_cladding": 40,
}


def p6_groups_with_review(extraction: dict[str, Any]) -> dict[str, list[Any]]:
    return project_group_items_for_review(extraction, P6_WALLS_SECTION_CODE)


def p6_wall_zone_label(value: dict[str, Any]) -> str:
    label = str(value.get("display_name") or value.get("zone_id") or "Зона кладки")
    zone_kind = str(value.get("zone_kind") or "")
    normalized_label = label.lower().replace("ё", "е").strip()
    if zone_kind == "vent_chimney_cladding" and normalized_label in {
        "вентканалы",
        "обкладка вентканалов",
        "vent_chimney_cladding",
    }:
        return "Вентканалы — обкладка газобетоном в разделе стен"
    return label


def p6_wall_zone_sort_key(item: dict[str, Any]) -> tuple[int, str]:
    value = item.get("value") or {}
    zone_id = str(value.get("zone_id") or "")
    zone_kind = str(value.get("zone_kind") or "")
    order = P6_WALL_ZONE_ORDER.get(zone_id, P6_WALL_ZONE_ORDER.get(zone_kind, 100))
    return order, p6_wall_zone_label(value)


def p6_wall_field_label(key: str, default: str) -> str:
    return P6_WALL_FIELD_LABELS.get(key, default)


def p6_wall_item_label(group_key: str, value: dict[str, Any], fallback: str) -> str:
    if group_key == P6_WALL_ZONES_GROUP_KEY:
        return p6_wall_zone_label(value)
    if group_key == P6_WALL_BLOCK_ITEMS_GROUP_KEY:
        parts = [value.get("block_density"), value.get("block_size"), value.get("context")]
        return " ".join(str(part) for part in parts if part not in (None, "")) or fallback
    if group_key == P6_WALL_REBAR_GROUP_KEY:
        if fallback and fallback != group_key:
            return fallback
        steel = value.get("steel_class") or ""
        diameter = value.get("diameter_mm")
        parts = [str(part) for part in [steel, f"ф{diameter:g}" if isinstance(diameter, (int, float)) else diameter] if part]
        return " ".join(parts) or fallback
    if group_key == P6_LINTEL_ITEMS_GROUP_KEY:
        lintel_id = value.get("lintel_id")
        lintel_kind = P6_LINTEL_KIND_LABELS.get(str(value.get("lintel_kind") or ""), value.get("lintel_kind"))
        if lintel_id == value.get("lintel_kind") or str(lintel_id or "").startswith(("floor_1_", "floor_2_")):
            lintel_id = None
        return " ".join(str(part) for part in [lintel_id, lintel_kind] if part not in (None, "")) or fallback
    if group_key == P6_LINTEL_REBAR_GROUP_KEY:
        if fallback and fallback != group_key:
            return fallback
        lintel_id = value.get("lintel_id")
        lintel_label = P6_LINTEL_KIND_LABELS.get(str(value.get("lintel_kind") or ""), "")
        if str(lintel_id or "").startswith(("floor_1_u_block", "floor_2_u_block")):
            lintel_id = "U-блок"
        elif str(lintel_id or "").startswith(("floor_1_monolithic", "floor_2_monolithic")):
            lintel_id = "Монолитные"
        steel = value.get("steel_class") or ""
        diameter = value.get("diameter_mm")
        parts = [lintel_label or lintel_id, steel, f"ф{diameter:g}" if isinstance(diameter, (int, float)) else diameter]
        return " ".join(str(part) for part in parts if part not in (None, "")) or fallback
    return fallback


def p6_wall_visible_field_keys(group_key: str, correction_columns: list[str]) -> list[str]:
    if group_key == P6_WALL_ZONES_GROUP_KEY:
        return ["cutoff_waterproofing_area_m2"]
    if group_key == P6_WALL_BLOCK_ITEMS_GROUP_KEY:
        return ["volume_m3", "material_unit_price", "pallet_volume_m3"]
    if group_key == P6_LINTEL_ITEMS_GROUP_KEY:
        return [
            "total_length_m",
            "concrete_volume_m3",
            "formwork_horizontal_area_m2",
            "formwork_vertical_area_m2",
            "insulation_length_m",
            "insulation_eps_spec_volume_m3",
        ]
    return correction_columns


FLOOR_SLAB_EPS_ROLE_LABELS = {
    "slab_edge": "торец плиты",
    "slab_bottom": "низ плиты",
    "combined_bottom_and_edge": "торец + низ плиты",
    "unknown": "утепление плиты",
}


def floor_slab_zone_label(value: dict[str, Any]) -> str:
    return str(value.get("_zone_label") or value.get("display_name") or value.get("zone_id") or "Плита")


def floor_slab_item_label(group_key: str, value: dict[str, Any], fallback: str) -> str:
    zone_label = floor_slab_zone_label(value)
    if group_key == ZONES_GROUP_KEY:
        return zone_label
    if group_key == EPS_ITEMS_GROUP_KEY:
        role_label = FLOOR_SLAB_EPS_ROLE_LABELS.get(str(value.get("role") or ""), "утепление плиты")
        material = str(value.get("material_name") or "ЭППС").replace("-100мм", " 100 мм").replace("-50мм", " 50 мм")
        thickness = value.get("thickness_mm")
        if thickness and "мм" not in material:
            material = f"{material} {thickness:g} мм" if isinstance(thickness, (int, float)) else f"{material} {thickness} мм"
        return f"{material} — {role_label}"
    if group_key == BEAM_ITEMS_GROUP_KEY:
        return str(value.get("mark") or value.get("name") or fallback)
    if group_key == REBAR_GROUP_KEY:
        steel = value.get("steel_class") or ""
        diameter = value.get("diameter_mm")
        parts = [str(part) for part in [steel, f"⌀{diameter:g}" if isinstance(diameter, (int, float)) else diameter] if part]
        return " ".join(parts) or fallback
    if group_key == ADDITIONAL_ITEMS_GROUP_KEY:
        return str(value.get("name") or fallback)
    return f"{zone_label} — {fallback}" if fallback else zone_label


FLOOR_SLAB_FIELD_LABELS = {
    "concrete_slab_volume_m3": "Бетон плиты, объем",
    "concrete_total_with_beams_m3": "Бетон плиты + балок, контрольный итог",
    "slab_thickness_m": "Толщина плиты",
    "slab_edge_perimeter_m": "Периметр торца плиты",
    "formwork_under_slab_area_m2": "Площадь опалубки под плитой",
    "formwork_edge_area_m2": "Площадь опалубки торца плиты",
    "formwork_edge_and_beam_combined_area_m2": "Опалубка торца плиты + балок, площадь",
    "formwork_beams_side_area_m2": "Опалубка балок, боковая площадь",
    "formwork_beams_bottom_area_m2": "Опалубка балок, нижняя площадь",
    "manual_concrete_pump_shifts": "Бетононасос",
    "manual_formwork_rebar_crane_shifts": "Кран для опалубки/арматуры",
    "manual_rebar_metal_delivery_trucks": "Доставка арматуры/металла",
    "manual_technical_supervision_amount": "Технадзор",
    "manual_formwork_rental_supplier_quote_total": "КП поставщика на аренду опалубки",
    "manual_plywood_reserve_sheets": "Запас листов фанеры сверх расчёта",
    "manual_concrete_mixer_capacity_m3": "Объём миксера бетона на эту плиту",
    "volume_m3": "Объем материала",
    "area_m2": "Площадь",
    "length_m": "Длина работ",
    "height_m": "Высота",
    "spec_length_m": "Длина по спецификации",
    "kg_per_meter": "Масса 1 м",
}


def floor_slab_field_label(group_key: str, key: str, default: str) -> str:
    return FLOOR_SLAB_FIELD_LABELS.get(key, default)


def floor_slab_visible_field_keys(group_key: str, correction_columns: list[str]) -> list[str]:
    if group_key == ZONES_GROUP_KEY:
        return [
            "concrete_slab_volume_m3",
            "concrete_total_with_beams_m3",
            "beams_concrete_volume_m3",
            "slab_thickness_m",
            "slab_edge_perimeter_m",
            "formwork_under_slab_area_m2",
            "formwork_edge_area_m2",
            "formwork_edge_and_beam_combined_area_m2",
            "formwork_beams_side_area_m2",
            "formwork_beams_bottom_area_m2",
            "manual_concrete_pump_shifts",
            "manual_formwork_rebar_crane_shifts",
            "manual_rebar_metal_delivery_trucks",
            "manual_technical_supervision_amount",
            "manual_formwork_rental_supplier_quote_total",
            "manual_plywood_reserve_sheets",
            "manual_concrete_mixer_capacity_m3",
        ]
    if group_key == EPS_ITEMS_GROUP_KEY:
        return ["volume_m3", "area_m2", "length_m", "height_m"]
    return correction_columns


def visible_repeated_field_keys(
    sec_code: str,
    group_key: str,
    correction_columns: list[str],
    item_label_columns: list[str],
    columns_by_key: dict[str, dict[str, Any]],
) -> list[str]:
    if sec_code == P6_WALLS_SECTION_CODE:
        source_keys = p6_wall_visible_field_keys(group_key, correction_columns)
    else:
        source_keys = floor_slab_visible_field_keys(group_key, correction_columns)
    keys = [k for k in source_keys if k not in item_label_columns]
    # Sheet 01 must stay numeric: avoid rows such as "Ед.", "Тип эксплуатации" or "Марка" whose
    # value is a technical/string classifier, not a number Elena can check in column B. The full
    # structured row remains in row_data_json on every visible numeric row.
    keys = [
        k
        for k in keys
        if (columns_by_key.get(k, {}).get("value_kind") or "") in {"number", "money"}
    ]
    return keys


def reference_summary(
    value: dict[str, Any],
    keys: list[str],
    columns_by_key: dict[str, dict[str, Any]],
    *,
    sec_code: str = "",
    group_key: str = "",
) -> str:
    parts = []
    for key in keys:
        item_value = value.get(key)
        if item_value is None or item_value == "":
            continue
        column_def = columns_by_key.get(key, {})
        label = column_def.get("label_ru") or key
        if sec_code == "floor_slabs":
            label = floor_slab_field_label(group_key, key, label)
        if sec_code == P6_WALLS_SECTION_CODE:
            label = p6_wall_field_label(key, label)
        unit = column_def.get("unit") or ""
        parts.append(f"{label}: {display_value(item_value)}{(' ' + unit) if unit else ''}")
    return "; ".join(parts)


def is_rebar_group(group_key: str) -> bool:
    return "rebar" in (group_key or "").lower()


def rebar_diameter_breakdown(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pools rebar items by (steel_class, diameter_mm), summing spec length and delivery weight -
    the "4 rows, not the position-level zoo" summary Elena asked for 2026-08-12, matching how her
    own real smetas present rebar (checked on a real project: her final foundation_slab section shows only 4
    diameter rows, never the хомуты/лягушки/выпуски position breakdown). Same length-field
    fallback (spec_length_m, then source_length_m) and weight formula as
    rebar_item_delivery_weight_kg() elsewhere in this file - one source of truth for what a rebar
    item's length/weight is, not a second parallel definition."""
    groups: dict[tuple[str, float], dict[str, Any]] = {}
    for value in items:
        steel_class = value.get("steel_class")
        diameter = value.get("diameter_mm")
        if steel_class is None or diameter is None:
            continue
        try:
            diameter = float(diameter)
        except (TypeError, ValueError):
            continue
        key = (str(steel_class), diameter)
        length = value.get("spec_length_m")
        if length is None:
            length = value.get("source_length_m")
        length = float(length) if length not in (None, "") else 0.0
        weight = rebar_item_delivery_weight_kg(value) or 0.0
        bucket = groups.setdefault(
            key, {"steel_class": steel_class, "diameter_mm": diameter, "length_m": 0.0, "weight_kg": 0.0}
        )
        bucket["length_m"] += length
        bucket["weight_kg"] += weight
    return sorted(groups.values(), key=lambda b: (b["steel_class"], b["diameter_mm"]))


def _append_rebar_diameter_summary(
    ws, title: str, breakdown: list[dict[str, Any]], *, sec_code: str
) -> None:
    if not breakdown:
        return
    append_section_band(ws, [title], len(PROJECT_HEADERS))
    style_rebar_summary_title_row(ws, ws.max_row)
    ws.append(PROJECT_HEADERS)
    style_header_row(ws, ws.max_row, len(PROJECT_HEADERS))
    ws.row_dimensions[ws.max_row].height = COMPACT_ROW_HEIGHT
    for bucket in breakdown:
        label = f"{bucket['steel_class']} ф{bucket['diameter_mm']:g}"
        row = [
            label,
            round(bucket["length_m"], 2),
            "мп",
            "Найдено (авто, сумма по разделу)",
            "",
            (
                "Автоматически: сумма проектной длины из спецификаций по всем позициям этого диаметра "
                "в разделе. Вес в примечании ниже — поставочный, с запасом/округлением для доставки."
            ),
            "",
            f"Поставочный вес с запасом/округлением (для справки): {bucket['weight_kg']:g} кг",
            "",
            "",
            sec_code,
            "rebar_diameter_summary",
            "AUTO_CALCULATED",
            "",
        ]
        ws.append(row)
        row_idx = ws.max_row
        row_fill = project_status_fill("Найдено (авто, сумма по разделу)")
        for cell in ws[row_idx]:
            cell.fill = row_fill
        ws.row_dimensions[row_idx].height = COMPACT_ROW_HEIGHT


def rebar_reference_summary(value: dict[str, Any]) -> tuple[Any, str]:
    """Rebar is checked against the PDF, but not edited by the estimator in the workbook."""
    for key in ("spec_length_m", "source_length_m", "length_m"):
        if value.get(key) not in (None, ""):
            return display_value(value.get(key)), "мп"
    for key in ("weight_kg", "mass_kg"):
        if value.get(key) not in (None, ""):
            return display_value(value.get(key)), "кг"
    return "", ""


def repeated_item_sheet_id(sec_code: str, group_key: str, value: dict[str, Any], fallback: str) -> str:
    identity_parts = [
        value.get("zone_id"),
        value.get("beam_id"),
        value.get("code"),
        value.get("mark"),
        value.get("name"),
        value.get("item_type"),
        value.get("role"),
        value.get("steel_class"),
        value.get("diameter_mm"),
        value.get("wall_role"),
        value.get("block_density"),
        value.get("product_type"),
        value.get("quantity"),
        value.get("length_m"),
        value.get("spec_length_m"),
        value.get("source_length_m"),
        fallback,
    ]
    identity = "|".join(str(part) for part in identity_parts if part not in (None, ""))
    return f"{sec_code}:{group_key}:{identity}"


# (group_code, field_key) -> why a null value here never needs a reviewer's attention,
# verified by reading the actual consuming code (build_input.py/calculator.py), not guessed.
# 2026-08-15: replaces the old needs_review-based hide/show rule, which either hid real gaps
# (needs_review=false: a field null for a genuine, unnoticed reason) or, when flipped to "always
# show", flooded the sheet with fields that are STRUCTURALLY never going to have a value for
# this item type (pipe fittings' length, a U-block lintel's formwork) - neither needs_review nor
# "always show" can tell those two cases apart; only checking what the calculator actually reads
# for money can.
FIELD_NEVER_MONEY_RELEVANT_WHEN_EMPTY: dict[tuple[str, str], str] = {
    # Whole group never read for money in production mode (earthworks/build_input.py's own
    # docstring: "communications_pipe_items - never read here; not needed by the fixed
    # production calc_methods" - communications_length_m, a reviewed scalar, is the real source).
    ("communications_pipe_items", "pipe_length_m"): "group never read for money (earthworks uses the reviewed communications_length_m scalar instead)",
    ("communications_pipe_items", "quantity"): "group never read for money (same as pipe_length_m)",
    ("communications_pipe_items", "total_length_m"): "group never read for money (same as pipe_length_m)",
    ("communications_pipe_items", "diameter_mm"): "group never read for money (same as pipe_length_m) - purely descriptive even in the group's own cross-check sum",
    # earthworks_calculator.py's calculate_trench_routes() always uses the flat trench_width_m
    # scalar for every route (never route.get("width_m")) - the per-route field is display-only.
    ("trench_routes", "width_m"): "never read - calculate_trench_routes() always uses the flat trench_width_m scalar for every route, not this per-route field",
    # Per-beam fields with a safe fallback or zero downstream consumer (floor_slabs/build_input.py
    # + floor_slab_calculator.py, verified 2026-08-15).
    ("floor_slab_beam_items", "count"): "defaults to 1 in _beam_formwork_area_m2 when absent",
    # NOT "bottom_formwork_area_m2" - reverted 2026-08-15, found unsafe: the zone-level
    # formwork_beams_bottom_area_m2 override only helps when THAT field is also given; when both
    # it and every beam's own bottom_formwork_area_m2 are null (real, live case: slab_2f_6450 in
    # a real TRC extraction - zone field null, beam БГ-1 also null), build_input.py's
    # beams_bottom_sum silently computes 0 with no error, unlike the edge/combined pair below
    # which has an explicit required-one-of check. Must stay visible.
    ("floor_slab_beam_items", "insulated_length_m"): "not read anywhere in build_input.py/calculator.py",
    ("floor_slab_beam_items", "insulation_area_m2"): "not read anywhere in build_input.py/calculator.py",
    # Zone-level control/alternate/unused fields (floor_slabs/build_input.py, verified 2026-08-15).
    ("floor_slab_zones", "concrete_total_with_beams_m3"): "diagnostic/control only, never a money input",
    ("floor_slab_zones", "formwork_edge_and_beam_combined_area_m2"): "alternate field - safe when formwork_edge_area_m2 is given instead",
    ("floor_slab_zones", "formwork_beams_side_area_m2"): "not read anywhere in build_input.py/calculator.py",
    ("floor_slab_zones", "slab_mark"): "descriptive label only, never a money input",
    # 2026-08-17 correction: crane/pump were wrongly added here 2026-08-15 on the reasoning "has
    # a code-level default, so blank isn't lost money" - that reasoning only holds if the default
    # is actually a safe stand-in. Checked real per-pour data across all 3 projects (8 real
    # pours: TRC x4, ARK x2, USV x2): crane is 1 on 4 pours and 2 on the other 4 (no formula,
    # confirmed - a hardcoded default would be wrong exactly as often as the 0 it replaces), so 0
    # silently drops a real ~30-60k₽/pour line every time it's blank - which was every pour on
    # every project checked, since the row never rendered at all.
    # manual_rebar_metal_delivery_trucks stays hidden - genuinely AUTO_CALCULATED via a real
    # formula (box-calculator running weight total), not a guessed default.
    # manual_formwork_rental_supplier_quote_total stays hidden - confirmed never read by
    # build_input.py at all (service/reference-only field, label literally says "служебное").
    # manual_technical_supervision_amount stays hidden - out of scope for this fix (not asked).
    ("floor_slab_zones", "manual_rebar_metal_delivery_trucks"): "defaults to 0 in build_input.py when absent (or box-calculator auto-fill)",
    ("floor_slab_zones", "manual_formwork_rental_supplier_quote_total"): "never read by build_input.py at all - service/reference-only field",
    ("floor_slab_zones", "manual_technical_supervision_amount"): "defaults to 5000 in build_input.py when absent",
    # EPS area/height: build_input.py derives area_m2 from volume_m3/thickness_mm automatically
    # when area is absent; height_m is never read at all.
    ("floor_slab_eps_items", "area_m2"): "auto-derived from volume_m3/thickness_mm in _resolve_insulation when absent",
    ("floor_slab_eps_items", "material_name"): "purely descriptive - never read by _resolve_insulation or build_input.py",
    ("floor_slab_beam_items", "mark"): "purely descriptive identifier - never read for money by build_input.py/calculator.py",
    ("floor_slab_additional_items", "item_type"): "never read - _resolve_additional_concrete_items() only checks unit/quantity, item_type is descriptive only",
    # calculator_input_path is "" for this whole group (flat_roof section_contract.yaml) -
    # confirmed never referenced anywhere in flat_roof/build_input.py. Genuinely diagnostic-only
    # despite production_input: true (that flag only controls sheet-01 styling, not whether the
    # calculator reads it).
    ("roof_raw_material_spec_rows", "quantity"): "group has calculator_input_path=\"\" - never fed to calculate_flat_roof() at all, diagnostic-only",
    ("roof_raw_material_spec_rows", "unit"): "group has calculator_input_path=\"\" - never fed to calculate_flat_roof() at all, diagnostic-only",
    ("floor_slab_eps_items", "height_m"): "not read anywhere in build_input.py/calculator.py",
    # Rebar catalog-fallback fields (foundation_slab/floor_slabs/P6 walls - all 3 adapters,
    # verified 2026-08-15): code auto-generated if absent, kg_per_meter/rod_length_m filled from
    # a per-diameter catalog table in rebar_item_defaults.py regardless of what's in the JSON.
    ("foundation_rebar_items", "code"): "adapter auto-generates a code when absent",
    ("foundation_rebar_items", "kg_per_meter"): "filled from the per-diameter catalog table when absent",
    ("floor_slab_rebar_items", "code"): "never read for pooling/pricing (pools by floor/component/zone/steel_class/diameter)",
    ("floor_slab_rebar_items", "kg_per_meter"): "filled from the per-diameter catalog table when absent",
    ("floor_slab_rebar_items", "rod_length_m"): "filled from the per-diameter catalog table when absent",
    ("wall_chasing_rebar_items", "kg_per_meter"): "filled from the per-diameter catalog table when absent",
    ("wall_chasing_rebar_items", "rod_length_m"): "filled from the per-diameter catalog table when absent",
    ("lintel_rebar_items", "kg_per_meter"): "filled from the per-diameter catalog table when absent",
    ("lintel_rebar_items", "rod_length_m"): "filled from the per-diameter catalog table when absent",
    # lintel_id/lintel_kind null here means the row still counts for money - it just goes into
    # zone.unassigned_lintel_rebar_items instead of a specific lintel (P6 calculator, verified
    # 2026-08-15: iterated and priced at load_bearing_walls_lintels_p6_calculator.py line ~312).
    ("lintel_rebar_items", "lintel_id"): "still priced via zone.unassigned_lintel_rebar_items when absent",
    ("lintel_rebar_items", "lintel_kind"): "still priced via zone.unassigned_lintel_rebar_items when absent",
    # Price/catalog fields removed from the extraction schema entirely 2026-08-15 (see
    # UNIVERSALIZATION_PLAN.md) - price always comes from the price registry regardless.
    ("wall_block_items", "material_unit_price"): "price always comes from price_registry, not this field",
    ("wall_block_items", "pallet_volume_m3"): "pallet volume always comes from price_registry, not this field",
    # Calculator-computed, never read from JSON at all (load_bearing_walls_lintels_p6_calculator.py
    # _delivery_batch_id()/_crane_batch_id() compute their own grouping from zone_kind).
    ("wall_zones", "block_delivery_batch_id"): "batch grouping is computed by the calculator from zone_kind, never read from JSON",
}


def _field_never_money_relevant_when_empty(
    group_key: str,
    key: str,
    value: dict[str, Any],
    found_groups: dict[str, list[Any]] | None = None,
) -> bool:
    """True only for a (group, field) pair verified by reading the actual consuming code - see
    FIELD_NEVER_MONEY_RELEVANT_WHEN_EMPTY's own per-entry comments for the evidence. The default
    for anything NOT in this table (or not matching a conditional case below) is to show the
    field when empty - "not sure yet" must show, not hide, per the same reasoning as the
    needs_review=true fix this mirrors. found_groups is only needed for cases whose sibling
    lives on a DIFFERENT item (e.g. the item's own zone), not just within the same value dict."""
    if (group_key, key) in FIELD_NEVER_MONEY_RELEVANT_WHEN_EMPTY:
        return True
    # Conditional cases: relevance depends on a SIBLING field of the same item, not just the
    # group/field pair alone.
    if group_key == "lintel_items" and key in (
        "formwork_horizontal_area_m2",
        "formwork_vertical_area_m2",
        "insulation_length_m",
        "insulation_eps_spec_volume_m3",
    ):
        # U-block lintels are pre-cast, genuinely never have formwork/insulation (P6Rates:
        # formwork_horizontal_area_m2/formwork_vertical_area_m2 default to 0.0, correct for
        # u_block; for monolithic lintels these fields ARE real money, must stay visible).
        return value.get("lintel_kind") == "u_block"
    if group_key == "floor_slab_zones" and key == "formwork_edge_area_m2":
        # Mirrors the existing formwork_edge_and_beam_combined_area_m2 entry above (that one
        # hides when THIS field is given instead) - build_input.py's own fallback chain treats
        # the two as alternatives for the same physical quantity (edge_and_beam_value =
        # combined_area if combined_area is not None else edge_area + beams_formwork_sum), so
        # the pair must be safe in both directions, not just one. When the PDF gives the
        # combined torец+balки number, this pure-edge-only field is genuinely never populated
        # and never needed - money is already carried by the sibling.
        return value.get("formwork_edge_and_beam_combined_area_m2") is not None
    if group_key == "floor_slab_beam_items" and key == "bottom_formwork_area_m2":
        # Real TRC cross-check (2026-08-16): build_input.py's beams_bottom_override always wins
        # over summing each beam's own bottom_formwork_area_m2 (beams_bottom_override if
        # beams_bottom_override is not None else beams_bottom_sum) - so when the PDF gives one
        # zone-total number (e.g. "Плита 1 этажа": ведомость горизонтальных поверхностей на
        # стр.41 gives "Горизонтальная опалубка под ж/б балку" = 1.26 м2 for all beams together,
        # already captured as the zone's own formwork_beams_bottom_area_m2), each individual
        # beam's own value is genuinely never read and never needed. Conditional on the SIBLING
        # ZONE item (not this beam's own value dict), so this only fires when that zone total is
        # actually present - a zone with no such total (e.g. "Плита 2 этажа"/БГ-1, confirmed via
        # PDF page 43 has no per-beam formwork table at all) keeps showing the real gap.
        zone_id = value.get("zone_id")
        zones = (found_groups or {}).get(ZONES_GROUP_KEY) or []
        for zone_item in zones:
            zone_value = zone_item.get("value") or {}
            if zone_value.get("zone_id") == zone_id:
                return zone_value.get("formwork_beams_bottom_area_m2") is not None
        return False
    return False


def _render_repeated_row_block(
    ws,
    sec_code: str,
    group_key: str,
    param: dict[str, Any],
    items: list[dict[str, Any]],
    counts: dict[str, int],
    found_groups: dict[str, list[Any]],
    *,
    title: str,
    rebar_metal_delivery_allocation: dict[str, int],
    rebar_weights_by_section: dict[str, float],
    rebar_cumulative_weights: dict[str, tuple[float, float]],
    reference_only: bool = False,
    registry: Sheet01BuildRegistry | None = None,
) -> None:
    """Renders one repeated-row group as its own titled block on sheet 01. `items` is passed in
    explicitly (not read from found_groups here) so a caller can pre-filter to one physical zone
    (see build_project_sheet_from_extraction()'s floor_slabs branch) without this function needing
    to know anything about zones itself - every other section just passes found_groups[group_key]
    unfiltered, same behavior as before this was extracted into its own function."""
    headers = (ITEM_BLOCK_HEADERS if reference_only else PROJECT_HEADERS) + correction_headers(param) + ["row_data_json"]
    item_label_columns = param.get("item_label_columns") or []
    correction_columns = param.get("correction_columns") or []
    columns_by_key = {c["key"]: c for c in (param.get("columns") or [])}

    rows: list[list[Any]] = []
    # Rows where needs_review is true AND the field itself is still blank - not just "please
    # double-check", but "there is genuinely no usable number yet" (the PDF gave conflicting or
    # unreadable data and the model could not pick one). Tracked by position in `rows` so the
    # coloring pass below can give them a visibly stronger fill than ordinary needs_review rows.
    critical_row_indices: set[int] = set()
    for item in items:
        value = item.get("value") or {}
        needs_review = bool(item.get("needs_review"))

        if sec_code == "floor_slabs" and group_key == ZONES_GROUP_KEY and value.get(
            "manual_rebar_metal_delivery_trucks"
        ) is None:
            zone_id = value.get("zone_id")
            bucket_key = f"{FLOOR_SLABS_METAL_BUCKET_PREFIX}{zone_id}" if zone_id else None
            allocated = rebar_metal_delivery_allocation.get(bucket_key) if bucket_key else None
            if allocated is not None:
                # Copy so the auto-filled value doesn't silently mutate the shared extraction
                # dict for other consumers (sheet 03 mirror also reads `extraction`) beyond
                # what's intentional - it's fine for it to show there too, but explicitly, not
                # as a side effect of this loop running first.
                value = {**value, "manual_rebar_metal_delivery_trucks": allocated}
                zone_weight = rebar_weights_by_section.get(bucket_key, 0.0)
                cumulative_before, cumulative_after = rebar_cumulative_weights.get(
                    bucket_key, (0.0, zone_weight)
                )
                auto_detail = (
                    metal_delivery_note(
                        weight_kg=zone_weight,
                        cumulative_before_kg=cumulative_before,
                        cumulative_after_kg=cumulative_after,
                        allocated_trucks=allocated,
                    )
                    + " Проверьте и поправьте при необходимости."
                )
                item = {
                    **item,
                    "_metal_delivery_detail": auto_detail,
                }

        label_parts = [str(value[k]) for k in item_label_columns if value.get(k) not in (None, "")]
        item_label = " ".join(label_parts) or item.get("item_name") or group_key
        if sec_code == P6_WALLS_SECTION_CODE and is_rebar_group(group_key) and item.get("item_name"):
            item_label = str(item.get("item_name"))
        if sec_code == "floor_slabs":
            item_label = floor_slab_item_label(group_key, value, item_label)
        if sec_code == P6_WALLS_SECTION_CODE:
            item_label = p6_wall_item_label(group_key, value, item_label)

        if reference_only:
            if registry is not None:
                registry.record_repeated_item(
                    sec_code,
                    group_key,
                    repeated_item_sheet_id(sec_code, group_key, value, item_label),
                )
            summary_keys = [k for k in correction_columns if k not in item_label_columns]
            if is_rebar_group(group_key):
                summary, display_unit = rebar_reference_summary(value)
            elif sec_code == "flat_roof" and group_key == "roof_raw_material_spec_rows":
                summary = display_value(value.get("quantity"))
                display_unit = str(value.get("unit") or "")
            else:
                summary = reference_summary(
                    value,
                    summary_keys,
                    columns_by_key,
                    sec_code=sec_code,
                    group_key=group_key,
                )
                display_unit = param.get("unit", "")
            row = [
                item_label,
                summary,
                display_unit,
                "СПРАВОЧНО",
                display_confidence(item),
                "СПРАВОЧНО: проверьте построчно и сверьте с PDF.",
                item.get("source_pdf") or "",
                item_fragment(item),
                "",
                "",
                sec_code,
                group_key,
                param.get("source_class", ""),
                param.get("target_code", ""),
            ]
            row += [""] * len(correction_headers(param))
            row.append(json.dumps(value, ensure_ascii=False))
            rows.append(row)
            counts["item_rows"] += 1
            continue

        # One FIELD = one row (real user feedback 2026-08-11: column A must name what the number
        # IS and what it's for - e.g. "Плита фундамента толщиной 300мм — Бетон" - column B must
        # hold ONLY the number, column C only the unit; a cell with several "label: value ед."
        # lines crammed together doesn't scan). Only correction_columns are shown - that list is
        # each contract's own curated "worth showing to Elena" set (money/manual fields first);
        # showing every declared column instead pulled in noise nobody asked for (rebar's raw
        # "Наименование" text, wall_block_items' "Размер блока") that was never visible before
        # this change (found 2026-08-11). Fields already used to build item_label (e.g.
        # wall_block_items' context/wall_role/block_density) are excluded too - they're identity,
        # already visible in column A, showing them again just repeats column A's own text back
        # at itself. Only the FIRST populated field's row carries the real row_data_json + the
        # correction override cells (O-R) - same single JSON blob and override mechanism as
        # before, unmodified; the rest are blank-JSON display-only rows, which
        # read_production_item_rows() already skips (is_blank(raw_json)), so the same item is
        # never read back more than once.
        ordered_keys = visible_repeated_field_keys(
            sec_code,
            group_key,
            correction_columns,
            item_label_columns,
            columns_by_key,
        )
        field_rows: list[tuple[str | None, str | None, Any, str]] = []
        for key in ordered_keys:
            v = value.get(key)
            # 2026-08-15: replaced the old needs_review-based hide rule (hid real gaps whenever
            # needs_review was false) and the "always show" experiment that replaced it (flooded
            # the sheet with fields that structurally never apply to this item type - pipe
            # fittings' length, a U-block lintel's formwork). Now: hide only when
            # FIELD_NEVER_MONEY_RELEVANT_WHEN_EMPTY confirms, by reading the actual consuming
            # code, that this exact (group, field) - or this item's specific case, e.g. lintel_kind
            # - never affects money when empty. Anything not on that list still shows, regardless
            # of needs_review - "not sure yet" must show, not hide.
            if (v is None or v == "") and _field_never_money_relevant_when_empty(
                group_key, key, value, found_groups
            ):
                continue
            column_def = columns_by_key.get(key, {})
            field_label = column_def.get("label_ru") or key
            if sec_code == "floor_slabs":
                field_label = floor_slab_field_label(group_key, key, field_label)
            if sec_code == P6_WALLS_SECTION_CODE:
                field_label = p6_wall_field_label(key, field_label)
            unit = column_def.get("unit", "")
            if sec_code == "flat_roof" and group_key == "roof_raw_material_spec_rows" and key == "quantity":
                unit = str(value.get("unit") or unit)
            field_rows.append((key, field_label, display_value(v), unit))
        if not field_rows:
            if sec_code == "flat_roof":
                continue
            if len(ordered_keys) == 1:
                key = ordered_keys[0]
                column_def = columns_by_key.get(key, {})
                field_label = column_def.get("label_ru") or key
                if sec_code == P6_WALLS_SECTION_CODE:
                    field_label = p6_wall_field_label(key, field_label)
                field_rows = [(key, field_label, None, column_def.get("unit", param.get("unit", "")))]
            else:
                field_rows = [(None, None, None, param.get("unit", ""))]

        # Rebar rows (real user feedback 2026-08-11, "арматуру вот так заполняем во всех
        # разделах"): a rebar item almost always reduces to exactly one real number (its spec
        # length) - "A500C 10" is already unambiguous under an "Арматура..." block title with
        # unit "мп", so appending the field's own label_ru ("Длина по спецификации") to column A
        # is redundant noise Elena explicitly asked to drop for this group type specifically. If
        # a rebar item ever has more than one populated field (e.g. spec_length_m AND
        # kg_per_meter both given), the suffix comes back so the two rows stay distinguishable.
        suppress_field_suffix = "rebar" in group_key and len(field_rows) == 1

        status = "Проверьте (needs_review)" if needs_review else "Найдено"
        row_fill = project_status_fill(status)
        counts["needs_review" if needs_review else "found"] += 1

        item_id = repeated_item_sheet_id(sec_code, group_key, value, item_label)
        if registry is not None:
            registry.record_repeated_item(sec_code, group_key, item_id)
        for field_idx, (field_key, field_label, field_value, unit) in enumerate(field_rows):
            label = f"{item_label} — {field_label}" if field_label and not suppress_field_suffix else item_label
            if registry is not None:
                registry.record_repeated_field(sec_code, group_key, item_id, field_key)
            row_json = {
                **value,
                "_sheet_item_id": item_id,
                "_sheet_field_key": field_key,
            }
            row_status = status
            row_confidence = display_confidence(item)
            action_text = ""
            row_source = item.get("source_pdf") or ""
            row_fragment = item_fragment(item)
            if field_key == "manual_rebar_metal_delivery_trucks":
                row_status = "Найдено (авто, box-калькулятор)"
                row_confidence = ""
                action_text = (
                    "Автоматически по поставочному весу арматуры с запасом/округлением "
                    f"(накопление {int(METAL_TRUCK_CAPACITY_KG // 1000)} т) — проверьте и поправьте при необходимости."
                )
                row_source = ""
                row_fragment = item.get("_metal_delivery_detail") or item.get("notes") or ""
            elif field_key == "manual_concrete_pump_shifts" and (field_value is None or field_value == ""):
                # No formula (confirmed - depends on pump-parking distance/site height, not
                # volume), but 8/8 real pours checked across all 3 projects (TRC/АРК/ЮСВ) are
                # exactly 1 shift, never 0, never 2 - a strong enough pattern to hint, not to
                # silently assume. Critical (red): a blank here used to compute as 0, dropping a
                # real ~37-42k₽/pour line every time.
                critical_row_indices.add(len(rows))
                action_text = (
                    "⚠️ОБЯЗАТЕЛЬНО заполнить. Формулы нет, но на всех проверенных плитах "
                    "(ТРЦ/АРК/ЮСВ, 8 из 8) — ровно 1 смена. Впишите 1, если нет других данных, "
                    "или поправьте под реальный проект."
                )
            elif field_key == "manual_formwork_rebar_crane_shifts" and (field_value is None or field_value == ""):
                # No formula at all - checked real per-pour data across 3 projects: crane is 1
                # on 4 of 8 real pours and 2 on the other 4, no correlation with slab volume
                # (ARK's crane tracks volume 2->1 as volume drops 3x, but USV's stays 2->2 while
                # volume drops nearly 2x on the same kind of pour) - a hardcoded default would be
                # wrong exactly as often as the 0 it replaces, so no hint number is given here.
                critical_row_indices.add(len(rows))
                action_text = (
                    "⚠️ОБЯЗАТЕЛЬНО заполнить. Формулы нет (проверено на 3 проектах: 1 или 2 "
                    "смены без видимой зависимости от объёма плиты) — впишите вручную под "
                    "реальный проект."
                )
            elif (
                group_key == ZONES_GROUP_KEY
                and field_key == "beams_concrete_volume_m3"
                and (field_value is None or field_value == "")
            ):
                # Real, working fallback confirmed 2026-08-17 (build_input.py: only sets this key
                # when a real override is given; absent -> floor_slab_calculator.py sums
                # floor_slab_beam_items[same zone].concrete_volume_m3 instead, same as before this
                # field existed). Blank here is the NORMAL case (most projects have no ready
                # spec-table beam-concrete row) - critical/red was wrong.
                action_text = (
                    "Не обязательно — при пустом значении калькулятор сам возьмёт сумму объёма "
                    "по отдельным балкам зоны. Впишите число только если в спецификации плиты "
                    "есть готовая строка «Бетон... (балки в теле плиты)»."
                )
            elif (
                group_key == ZONES_GROUP_KEY
                and field_key == "manual_plywood_reserve_sheets"
                and (field_value is None or field_value == "")
            ):
                # Real fallback confirmed in build_input.py (2026-08-22): overrides rates.
                # reserve_plywood_sheets only when given; absent -> catalog default 0 (checked
                # against real ТРЦ/АРК/ЮСВ plywood formulas - Elena's own reserve is a genuine
                # per-pour judgment call, 0/5/10 with no formula, not something to guess a
                # universal number for). Never a silent money loss - unlike crane/pump, blank here
                # has an actually-safe default.
                action_text = (
                    "Не обязательно — при пустом значении запас не добавляется (0 листов сверх "
                    "расчёта). Впишите число, только если по факту на этой плите нужен доп. запас "
                    "фанеры сверх формулы (некратные места, торцы сложной формы и т.п.)."
                )
            elif (
                group_key == ZONES_GROUP_KEY
                and field_key == "manual_concrete_mixer_capacity_m3"
                and (field_value is None or field_value == "")
            ):
                # Real fallback confirmed in build_input.py (2026-09-07): overrides rates.
                # mixer_capacity_m3 only when given; absent -> catalog default 9 м3 (checked
                # against real ТРЦ/ЮСВ/АРК formulas - 9 м3 matches ТРЦ and ЮСВ exactly, only real
                # АРК deviates at 7 м3 with no documented reason - site access/supplier fleet).
                action_text = (
                    "Не обязательно — при пустом значении используется 9 м3 (подтверждено на "
                    "большинстве реальных проектов). Впишите число, только если известна реальная "
                    "вместимость миксера/бетоновоза именно на этом объекте (например, 7 м3)."
                )
            elif (
                group_key == P6_WALL_ZONES_GROUP_KEY
                and field_key in ("display_name", "zone_kind")
                and (field_value is None or field_value == "")
            ):
                # Real fallback confirmed in load_bearing_walls_lintels_p6/build_input.py:
                # cleaned_zone.setdefault("display_name", zone_id) / .setdefault("zone_kind",
                # "other") - both always end up with a usable value even when blank on sheet 01.
                action_text = (
                    "Не обязательно — при пустом значении калькулятор возьмёт zone_id как "
                    "название/тип зоны."
                )
            elif (
                group_key == "floor_slab_eps_items"
                and field_key == "thickness_mm"
                and (field_value is None or field_value == "")
            ):
                # Real fallback confirmed in build_input.py's _resolve_insulation():
                # thickness_mm = _num(row.get("thickness_mm")) or 100.0 - always has a usable
                # value, defaults to the standard 100mm EPS thickness.
                action_text = (
                    "Не обязательно — при пустом значении берётся стандартная толщина 100мм."
                )
            elif (
                group_key == "floor_slab_beam_items"
                and field_key in ("concrete_volume_m3", "formwork_area_m2")
                and (field_value is None or field_value == "")
                and value.get("width_m") not in (None, "")
            ):
                # Real fallback confirmed in floor_slab_calculator.py: when width_m IS given but
                # this field isn't, concrete_volume recomputes as length*width*height*count and
                # formwork_area as length*(width+2*height)*count - both safe, not silent money
                # loss. Only critical when width_m is ALSO missing (that's a hard crash -
                # "needs either width_m or concrete_volume_m3" - left as the generic critical
                # branch below handles that case correctly already).
                action_text = (
                    "Не обязательно — при пустом значении (и заполненной ширине балки) "
                    "калькулятор сам посчитает объём/площадь по длине×ширине×высоте."
                )
            elif (
                group_key == "trench_routes"
                and field_key == "volume_m3"
                and (field_value is None or field_value == "")
            ):
                # Real fallback confirmed in earthworks_calculator.py's calculate_trench_routes():
                # route.get("volume_m3") - when absent, computed as length_m*depth_m*trench_width_m
                # instead (never blocked, real value only logged as a warning if it later
                # disagrees). length_m/depth_m stay critical - route["length_m"]/["depth_m"] are
                # plain dict access with no fallback at all, genuinely required.
                action_text = (
                    "Не обязательно — при пустом значении калькулятор сам посчитает объём как "
                    "длина×глубина×ширина траншеи. Впишите число только если в PDF есть готовый "
                    "объём именно для этого маршрута."
                )
            elif (
                group_key == "roof_zones"
                and field_key == "operability"
                and (field_value is None or field_value == "")
            ):
                # Documented fallback (section_contract.yaml roof_zones notes): "If operability
                # is absent, adapter/calculator treat the zone as non_exploitable." Safe default,
                # not a silent money loss.
                action_text = (
                    "Не обязательно — при пустом значении зона считается неэксплуатируемой "
                    "(non_exploitable) по умолчанию. Впишите «exploitable», только если зона "
                    "реально эксплуатируемая (выход на кровлю и т.п.)."
                )
            elif (
                group_key == ZONES_GROUP_KEY
                and field_key in ("formwork_beams_bottom_area_m2", "formwork_beams_side_area_m2")
                and (field_value is None or field_value == "")
            ):
                # These 2 are optional overrides with a real, working calculator fallback (sums
                # floor_slab_beam_items[same zone].bottom_formwork_area_m2/formwork_area_m2 when
                # this zone-level field is absent - see section_contract.yaml's own notes). The
                # generic needs_review branch below used to mark this critical/red purely because
                # the ZONE item happened to be needs_review for an unrelated field (e.g. a beam
                # concrete-volume spec conflict) - confusing, since this specific field has no
                # conflict of its own and isn't actually going to silently lose money (the
                # fallback runs regardless, even if that fallback sums to 0 when no beam gives a
                # value either). Not critical; still shown so it's not fully invisible.
                action_text = (
                    "Не обязательно — при пустом значении калькулятор сам возьмёт сумму "
                    "нижней/боковой площади по отдельным балкам зоны (если и там пусто — 0). "
                    "Впишите число только если у Елены есть отдельная готовая цифра из PDF."
                )
            elif (
                group_key == "floor_slab_beam_items"
                and field_key == "length_m"
                and (field_value is None or field_value == "")
                and value.get("concrete_volume_m3") not in (None, "")
            ):
                # Real, confirmed silent-scope gap (TRC 2026-08-18, "ребро 50мм в теле плиты
                # перекрытия"): build_input.py reroutes any beam row with length_m absent but
                # concrete_volume_m3 given into beam_only_concrete_items - material/delivery-trip
                # accounting only, no formwork/concreting line, regardless of needs_review (the
                # item here had needs_review=false and confidence 0.99 - the model wasn't unsure,
                # the PDF genuinely has no printed length for this element). needs_review alone
                # can't be the only trigger for critical/red: this field has zero calculator
                # fallback (unlike every other case in this function), so it must be flagged
                # independent of that flag, same reasoning as the crane/pump fix.
                critical_row_indices.add(len(rows))
                action_text = (
                    "⚠️Обязательно проверить — без длины эта позиция уйдёт только в учёт "
                    "материала (объём бетона), БЕЗ строки бетонирования по длине в смете. Если "
                    "в проекте есть способ определить длину/ширину — впишите; если данных "
                    "действительно нет — оставьте пустым осознанно."
                )
            elif needs_review and (field_value is None or field_value == ""):
                critical_row_indices.add(len(rows))
                action_text = (
                    "⚠️ОБЯЗАТЕЛЬНО заполнить — в проекте нет однозначного числа для этого поля "
                    "(конфликт/нечитаемое значение в PDF, см. «Фрагмент проекта»)."
                )
            row = [
                label,
                field_value,
                unit,
                row_status,
                row_confidence,
                action_text,
                row_source,
                row_fragment,
                "",
                "",
                sec_code,
                group_key,
                param.get("source_class", ""),
                param.get("target_code", ""),
            ]
            row += ["", "", "", ""]  # correction columns - Elena fills these, not the extraction
            row.append(json.dumps(row_json, ensure_ascii=False))
            rows.append(row)
            counts["item_rows"] += 1

    # Empty repeated-row blocks used to render as a grey title + header with no data rows.
    # That looked like a broken table to Elena and carried no actionable information, so skip
    # the whole block when extraction produced no rows.
    if not rows:
        return

    append_block(ws, title, headers, rows)
    first_row_idx = ws.max_row - len(rows) + 1
    for row_idx in range(first_row_idx, ws.max_row + 1):
        status = str(ws.cell(row_idx, 4).value or "")
        if reference_only:
            row_fill = FILL_TECH
        elif (row_idx - first_row_idx) in critical_row_indices:
            row_fill = FILL_CRITICAL_REVIEW
        else:
            row_fill = project_status_fill(status)
        for cell in ws[row_idx]:
            cell.fill = row_fill
        ws.row_dimensions[row_idx].height = COMPACT_ROW_HEIGHT
    total_row = earthworks_group_total_row(sec_code, group_key, found_groups, len(headers))
    if total_row:
        ws.append(total_row)
        for cell in ws[ws.max_row]:
            cell.fill = FILL_HEADER
            cell.font = Font(name=FONT_NAME, bold=True, size=10)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[ws.max_row].height = COMPACT_ROW_HEIGHT


def repeated_item_has_visible_sheet01_row(
    sec_code: str,
    group_key: str,
    param: dict[str, Any],
    item: dict[str, Any],
    *,
    reference_only: bool,
) -> bool:
    value = item.get("value") or {}
    if reference_only:
        return True
    item_label_columns = param.get("item_label_columns") or []
    correction_columns = param.get("correction_columns") or []
    columns_by_key = {c["key"]: c for c in (param.get("columns") or [])}
    ordered_keys = visible_repeated_field_keys(
        sec_code,
        group_key,
        correction_columns,
        item_label_columns,
        columns_by_key,
    )
    if any(value.get(key) not in (None, "") for key in ordered_keys):
        return True
    if sec_code == P6_WALLS_SECTION_CODE and group_key == P6_WALL_ZONES_GROUP_KEY:
        return bool(item.get("needs_review"))
    # flat_roof intentionally skips technical rows with no numeric value. Other repeated groups
    # still render a blank "Проверьте" row so an expected calculator group cannot disappear.
    return sec_code != "flat_roof"


def expected_repeated_field_keys_for_sheet01(
    sec_code: str,
    group_key: str,
    param: dict[str, Any],
    item: dict[str, Any],
    *,
    reference_only: bool,
) -> list[str | None]:
    """The field-level counterpart to repeated_item_has_visible_sheet01_row().

    Sheet 01 now renders production repeated groups as "one visible numeric field = one row".
    A group-level count is therefore not enough: an item can be present while one required
    checkable field inside it is still hidden inside notes.
    """
    if reference_only:
        return []
    value = item.get("value") or {}
    item_label_columns = param.get("item_label_columns") or []
    correction_columns = param.get("correction_columns") or []
    columns_by_key = {c["key"]: c for c in (param.get("columns") or [])}
    ordered_keys = visible_repeated_field_keys(
        sec_code,
        group_key,
        correction_columns,
        item_label_columns,
        columns_by_key,
    )
    populated_keys = [key for key in ordered_keys if value.get(key) not in (None, "")]
    if populated_keys:
        return populated_keys
    if sec_code == "flat_roof":
        return []
    if len(ordered_keys) == 1 and repeated_item_has_visible_sheet01_row(
        sec_code,
        group_key,
        param,
        item,
        reference_only=reference_only,
    ):
        return [ordered_keys[0]]
    if repeated_item_has_visible_sheet01_row(
        sec_code,
        group_key,
        param,
        item,
        reference_only=reference_only,
    ):
        return [None]
    return []


def validate_sheet01_registry(
    contracts: list[dict[str, Any]],
    extraction: dict[str, Any],
    registry: Sheet01BuildRegistry,
) -> None:
    errors: list[str] = []

    for contract in contracts:
        sec_code = section_code(contract)
        for param in scalar_review_rows_for_contract(contract):
            key = str(param.get("target_code") or param.get("key") or "")
            if key and (sec_code, key) not in registry.scalar_rows:
                errors.append(
                    f"Поле {key} нужно листу 01 раздела {sec_code}, но строка не была создана."
                )

        if sec_code == P6_WALLS_SECTION_CODE:
            review_groups = p6_groups_with_review(extraction)
        else:
            review_groups = project_group_items_for_review(extraction, sec_code)

        for param in production_repeated_row_params(contract) + diagnostic_repeated_row_params(contract):
            group_key = param.get("key")
            if not group_key:
                continue
            items = group_items(review_groups, group_key)
            if not items:
                continue
            reference_only = param.get("production_input") is not True or is_rebar_group(group_key)
            expected_count = sum(
                1
                for item in items
                if repeated_item_has_visible_sheet01_row(
                    sec_code,
                    group_key,
                    param,
                    item,
                    reference_only=reference_only,
                )
            )
            if expected_count == 0:
                continue
            rendered_count = len(registry.repeated_items.get((sec_code, group_key), set()))
            if rendered_count < expected_count:
                errors.append(
                    f"Группа {group_key} раздела {sec_code}: в JSON есть {expected_count} строк, "
                    f"на лист 01 попало {rendered_count}."
                )
            if not reference_only:
                expected_field_count = sum(
                    len(
                        expected_repeated_field_keys_for_sheet01(
                            sec_code,
                            group_key,
                            param,
                            item,
                            reference_only=reference_only,
                        )
                    )
                    for item in items
                )
                rendered_field_count = len(registry.repeated_fields.get((sec_code, group_key), set()))
                if rendered_field_count < expected_field_count:
                    errors.append(
                        f"Группа {group_key} раздела {sec_code}: на лист 01 должно быть "
                        f"{expected_field_count} строк-полей, создано {rendered_field_count}."
                    )

    if errors:
        message = "Сборщик остановлен: лист 01 неполный.\n" + "\n".join(f"- {error}" for error in errors)
        raise RuntimeError(message)


def build_project_sheet_from_extraction(
    wb: Workbook, contracts: list[dict[str, Any]], extraction: dict[str, Any]
) -> dict[str, int]:
    ws = wb.create_sheet("01_Проверка проекта")
    project_address = (extraction.get("project_name") or "").strip()
    project_title = f"Разбор проекта: {project_address}" if project_address else "Разбор проекта"
    ws.append([project_title, "", "", "", "", "", "", "", "", "", "", "", "", ""])
    ws.append([])
    ws.append([])
    ws.append(PROJECT_HEADERS)

    counts = {
        "found": 0,
        "needs_review": 0,
        "missing": 0,
        "missing_confirmed_required": 0,
        "conditional_absent": 0,
        "item_rows": 0,
    }

    metal_order = metal_section_order(extraction)
    rebar_weights_by_section = compute_rebar_weights_by_section(contracts, extraction, metal_order)
    rebar_metal_delivery_allocation = compute_rebar_metal_delivery_allocation(rebar_weights_by_section, metal_order)
    rebar_cumulative_weights = compute_rebar_cumulative_weights(rebar_weights_by_section, metal_order)
    box_total_metal_weight_kg = round(sum(rebar_weights_by_section.values()), 1)
    all_rebar_items_for_box_summary: list[dict[str, Any]] = []
    registry = Sheet01BuildRegistry()

    for contract in contracts:
        sec_code = section_code(contract)
        found_by_target, found_groups, missing = index_extraction_section(extraction, sec_code)
        review_groups = project_group_items_for_review(extraction, sec_code)
        confirmed_required = compute_confirmed_required(found_by_target, sec_code)
        append_section_band(ws, [section_name(contract)], len(PROJECT_HEADERS))

        box_delivery_key = REBAR_METAL_DELIVERY_FIELD_BY_SECTION.get(sec_code)

        for param in scalar_review_rows_for_contract(contract):
            review_behavior = param.get("review_behavior") or {}
            target_code = param.get("target_code", "")
            found = found_by_target.get(target_code)
            row_fill = FILL_INPUT
            param_key = param.get("key")

            box_row: tuple[Any, str, str] | None = None
            if box_delivery_key is not None and param_key == box_delivery_key:
                if sec_code == P6_WALLS_SECTION_CODE:
                    # For walls, Elena asked not to show this under a separate blue section band.
                    # Render it once at the end of the walls section after the wall/lintel blocks.
                    continue
                # Box-calculator-allocated delivery trucks (2026-07-30) - computed from this
                # project's real rebar weight, not looked up in found_by_target/missing at all.
                # Crane-shift fields are NOT special-cased here anymore (Elena's ruling: no real
                # crane-shift-count formula exists, they render through the normal found/missing
                # path below like any other manual field). See
                # compute_rebar_metal_delivery_allocation/REBAR_METAL_DELIVERY_FIELD_BY_SECTION.
                box_row = (
                    rebar_metal_delivery_allocation.get(sec_code, 0),
                    "",
                    metal_delivery_note(
                        weight_kg=rebar_weights_by_section.get(sec_code, 0.0),
                        cumulative_before_kg=rebar_cumulative_weights.get(sec_code, (0.0, 0.0))[0],
                        cumulative_after_kg=rebar_cumulative_weights.get(sec_code, (0.0, 0.0))[1],
                        allocated_trucks=rebar_metal_delivery_allocation.get(sec_code, 0),
                    )
                    + " Проверьте и поправьте при необходимости.",
                )
            elif param_key == BOX_TOTAL_METAL_WEIGHT_KEY:
                box_row = (
                    box_total_metal_weight_kg,
                    "",
                    "Техническая скрытая строка: поставочный вес арматуры по всем разделам. "
                    "Елена видит этот итог один раз в конце листа.",
                )

            if box_row is not None:
                found_value, source, fragment = box_row
                status = "Найдено (авто, box-калькулятор)"
                row_fill = project_status_fill(status)
                counts["found"] += 1
                action_text = review_behavior.get("action_ru", "Проверьте значение.")
                if param_key == box_delivery_key:
                    action_text = (
                        "Автоматически по поставочному весу арматуры с запасом/округлением "
                        f"(накопление {int(METAL_TRUCK_CAPACITY_KG // 1000)} т) — проверьте и поправьте при необходимости."
                    )
                ws.append([
                    param.get("label_ru", param.get("key", "")),
                    found_value,
                    param.get("unit", ""),
                    status,
                    "",
                    action_text,
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
                registry.record_scalar(sec_code, param)
                if param_key == BOX_TOTAL_METAL_WEIGHT_KEY:
                    ws.row_dimensions[ws.max_row].hidden = True
                    ws.row_dimensions[ws.max_row].height = INACTIVE_ROW_HEIGHT
                continue

            confidence = display_confidence(found)
            alternative_scalar = earthworks_alternative_scalar(target_code, review_groups) if sec_code == "earthworks" else None
            if alternative_scalar is None and sec_code == "foundation_slab":
                alternative_scalar = foundation_alternative_scalar(target_code, found, review_groups, found_by_target)
            if alternative_scalar is None and sec_code == "load_bearing_walls_lintels":
                alternative_scalar = load_bearing_walls_lintels_alternative_scalar(target_code, found, review_groups)
            if alternative_scalar is None and sec_code == "flat_roof":
                alternative_scalar = flat_roof_alternative_scalar(target_code, found, review_groups)
            is_unresolved_needs_review = found is not None and found.get("value") is None
            if alternative_scalar is not None and (found is None or target_code in missing or is_unresolved_needs_review):
                found_value, status, source, fragment, confidence = alternative_scalar
                row_fill = project_status_fill(status)
                counts["needs_review" if status.startswith("Проверьте") else "found"] += 1
            elif target_code in confirmed_required and (is_unresolved_needs_review or (target_code in missing and found is None)):
                # A sibling field in the same presence pair was found — this project definitely
                # has this construction, so a still-blank value here (whether never attempted, in
                # section.missing, or a needs_review entry that only has candidates — e.g. a real
                # project's ПБ1/ПБ2 case where extraction correctly refused to sum 0.21+0.16 itself) is a
                # real, money-relevant gap, not a safely-skippable optional field. Escalate instead
                # of following the normal found/missing branches below. See SECTION_PRESENCE_PAIRS.
                found_value = None
                status = "Не найдено — ОБЯЗАТЕЛЬНО (раздел точно есть в проекте)"
                row_fill = FILL_MISSING
                source = found.get("source_pdf") if found is not None else ""
                fragment = item_fragment(found)
                counts["missing_confirmed_required"] += 1
            elif found is not None:
                found_value = display_value(found.get("value"))
                needs_review = bool(found.get("needs_review"))
                status = "Проверьте (needs_review)" if needs_review else "Найдено"
                row_fill = project_status_fill(status)
                source = found.get("source_pdf") or ""
                if found.get("candidates") and found.get("value") is None:
                    fragment = unresolved_candidate_fragment(found)
                else:
                    fragment = item_fragment(found)
                if (
                    sec_code == "load_bearing_walls_lintels"
                    and target_code == "floors_count"
                    and group_items(found_groups, "wall_block_items")
                ):
                    # Value stays visible (real cross-check value - a mismatch with wall_block_items'
                    # own floor_2 presence would be worth catching), but the calculator itself never
                    # reads this field once wall_block_items is present - see
                    # load_bearing_walls_lintels_alternative_scalar's floors_count branch, which only
                    # fires when this field is missing, not when it's found like here.
                    fragment = (fragment + "\n" if fragment else "") + (
                        "Справочно: калькулятор определяет этажность по наличию объёма 2-го этажа "
                        "в wall_block_items, а не по этому текстовому значению из PDF."
                    )
                counts["needs_review" if needs_review else "found"] += 1
            elif target_code and target_code in missing:
                found_value = None
                source = ""
                classified_missing = classified_missing_target(sec_code, target_code)
                if classified_missing is not None:
                    status, fragment = classified_missing
                    counts["conditional_absent"] += 1
                    row_fill = FILL_WHITE
                else:
                    status = "Не найдено"
                    fragment = ""
                    row_fill = project_status_fill(status)
                    counts["missing"] += 1
            else:
                found_value = None
                status = "Проверьте"
                row_fill = project_status_fill(status)
                source = ""
                fragment = ""

            action_text = review_behavior.get("action_ru", "Проверьте значение.")
            # Same distinction as the repeated-group rows above: a scalar this contract marks
            # required with status_if_missing="manual_required" (never PDF-derived, e.g. a
            # supplier's tapered-insulation quote) that is still blank right now genuinely blocks
            # the calculator - not an ordinary "please check" row. Both facts already exist on
            # the contract/row, no per-project guessing.
            if (
                found_value in (None, "")
                and param.get("required")
                and review_behavior.get("status_if_missing") == "manual_required"
            ):
                row_fill = FILL_CRITICAL_REVIEW
                action_text = "⚠️ОБЯЗАТЕЛЬНО заполнить — " + action_text
            ws.append([
                param.get("label_ru", param.get("key", "")),
                found_value,
                param.get("unit", ""),
                status,
                confidence,
                action_text,
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
            registry.record_scalar(sec_code, param)

        repeated_row_params = production_repeated_row_params(contract) + diagnostic_repeated_row_params(contract)

        if sec_code == "floor_slabs":
            # Real plates must read as their own visually separate group (concrete/formwork/
            # insulation/beams/rebar/manual fields together) - not one flat block per group-type
            # spanning every plate mixed together (2026-08-11, real user feedback). Reuses the
            # exact same _render_repeated_row_block() every other section below uses (same
            # status colors, same one-row-per-item + labeled multi-line summary, same band
            # styling) - just called once per zone with a pre-filtered item list. A first attempt
            # built a completely separate one-field-per-row rendering system just for floor_slabs
            # (plus its own read-back reconstruction in workbook_reader.py) - reverted 2026-08-11:
            # it made this section look and behave differently from every other one for no real
            # benefit, and duplicated logic that already existed here. Consistency with
            # earthworks/foundation_slab/load_bearing_walls_lintels's existing look (which Elena
            # confirmed is clear as-is) matters more than a bespoke per-section design.
            params_by_key = {param.get("key"): param for param in repeated_row_params}
            dependent_group_keys = [ZONES_GROUP_KEY, EPS_ITEMS_GROUP_KEY, BEAM_ITEMS_GROUP_KEY, REBAR_GROUP_KEY, ADDITIONAL_ITEMS_GROUP_KEY]
            for zone_item in review_groups.get(ZONES_GROUP_KEY, []):
                zone_value = zone_item.get("value") or {}
                zone_id = zone_value.get("zone_id")
                if zone_value.get("manual_rebar_metal_delivery_trucks") is None and zone_id:
                    bucket_key = f"{FLOOR_SLABS_METAL_BUCKET_PREFIX}{zone_id}"
                    allocated = rebar_metal_delivery_allocation.get(bucket_key)
                    if allocated is not None:
                        zone_weight = rebar_weights_by_section.get(bucket_key, 0.0)
                        cumulative_before, cumulative_after = rebar_cumulative_weights.get(
                            bucket_key, (0.0, zone_weight)
                        )
                        auto_detail = (
                            metal_delivery_note(
                                weight_kg=zone_weight,
                                cumulative_before_kg=cumulative_before,
                                cumulative_after_kg=cumulative_after,
                                allocated_trucks=allocated,
                            )
                            + " Проверьте и поправьте при необходимости."
                        )
                        zone_value = {**zone_value, "manual_rebar_metal_delivery_trucks": allocated}
                        zone_item = {
                            **zone_item,
                            "value": zone_value,
                            "_metal_delivery_detail": auto_detail,
                        }
                zone_label = zone_value.get("display_name") or zone_id or "?"
                level = zone_value.get("source_level")
                append_section_band(ws, [f"Плита: {zone_label}{f' ({level})' if level else ''}"], len(PROJECT_HEADERS))
                for group_key in dependent_group_keys:
                    param = params_by_key.get(group_key)
                    if param is None:
                        continue
                    if group_key == ZONES_GROUP_KEY:
                        zone_items = [zone_item]
                        block_label = "Расчетные параметры"
                        reference_only = False
                    else:
                        zone_items = [
                            {
                                **item,
                                "value": {
                                    **(item.get("value") or {}),
                                    "_zone_label": zone_label,
                                },
                            }
                            for item in review_groups.get(group_key, [])
                            if (item.get("value") or {}).get("zone_id") == zone_id
                        ]
                        block_label = param.get("label_ru", group_key)
                        reference_only = group_key == REBAR_GROUP_KEY
                    if not zone_items and group_key != ZONES_GROUP_KEY:
                        continue
                    title_prefix = "СПРАВОЧНО: " if reference_only else ""
                    _render_repeated_row_block(
                        ws, sec_code, group_key, param, zone_items, counts, review_groups,
                        title=f"{title_prefix}{zone_label} — {block_label}",
                        rebar_metal_delivery_allocation=rebar_metal_delivery_allocation,
                        rebar_weights_by_section=rebar_weights_by_section,
                        rebar_cumulative_weights=rebar_cumulative_weights,
                        reference_only=reference_only,
                        registry=registry,
                    )
        elif sec_code == P6_WALLS_SECTION_CODE:
            p6_found_groups = p6_groups_with_review(extraction)
            params_by_key = {param.get("key"): param for param in repeated_row_params}
            p6_delivery_param = next(
                (
                    param
                    for param in scalar_review_rows_for_contract(contract)
                    if param.get("key") == REBAR_METAL_DELIVERY_FIELD_BY_SECTION.get(P6_WALLS_SECTION_CODE)
                ),
                None,
            )
            dependent_group_keys = [
                P6_WALL_ZONES_GROUP_KEY,
                P6_WALL_BLOCK_ITEMS_GROUP_KEY,
                P6_LINTEL_ITEMS_GROUP_KEY,
                P6_WALL_REBAR_GROUP_KEY,
                P6_LINTEL_REBAR_GROUP_KEY,
            ]
            for zone_item in sorted(p6_found_groups.get(P6_WALL_ZONES_GROUP_KEY, []), key=p6_wall_zone_sort_key):
                zone_value = zone_item.get("value") or {}
                zone_id = zone_value.get("zone_id")
                zone_label = p6_wall_zone_label(zone_value)
                has_dependent_rows = any(
                    (item.get("value") or {}).get("zone_id") == zone_id
                    for dependent_group_key in dependent_group_keys
                    if dependent_group_key != P6_WALL_ZONES_GROUP_KEY
                    for item in p6_found_groups.get(dependent_group_key, [])
                )
                append_section_band(ws, [zone_label], len(PROJECT_HEADERS))
                for group_key in dependent_group_keys:
                    param = params_by_key.get(group_key)
                    if param is None:
                        continue
                    if group_key == P6_WALL_ZONES_GROUP_KEY:
                        zone_items = [zone_item]
                        block_label = "Параметры зоны"
                        reference_only = False
                        has_visible_zone_value = any(
                            (zone_value or {}).get(key) not in (None, "")
                            for key in p6_wall_visible_field_keys(group_key, param.get("correction_columns") or [])
                        )
                        if not has_visible_zone_value and not zone_item.get("needs_review") and not has_dependent_rows:
                            continue
                    else:
                        zone_items = [
                            {
                                **item,
                                "value": {
                                    **(item.get("value") or {}),
                                    "_zone_label": zone_label,
                                },
                            }
                            for item in p6_found_groups.get(group_key, [])
                            if (item.get("value") or {}).get("zone_id") == zone_id
                        ]
                        block_label = param.get("label_ru", group_key).removeprefix("СПРАВОЧНО: ").strip()
                        reference_only = is_rebar_group(group_key)
                    if not zone_items and group_key != P6_WALL_ZONES_GROUP_KEY:
                        continue
                    title_prefix = "СПРАВОЧНО: " if reference_only else ""
                    _render_repeated_row_block(
                        ws, sec_code, group_key, param, zone_items, counts, p6_found_groups,
                        title=f"{title_prefix}{zone_label} — {block_label}",
                        rebar_metal_delivery_allocation=rebar_metal_delivery_allocation,
                        rebar_weights_by_section=rebar_weights_by_section,
                        rebar_cumulative_weights=rebar_cumulative_weights,
                        reference_only=reference_only,
                        registry=registry,
                    )
            if p6_delivery_param is not None:
                cumulative_before, cumulative_after = rebar_cumulative_weights.get(
                    sec_code, (0.0, rebar_weights_by_section.get(sec_code, 0.0))
                )
                append_rebar_metal_delivery_row(
                    ws,
                    sec_code=sec_code,
                    param=p6_delivery_param,
                    value=rebar_metal_delivery_allocation.get(sec_code, 0),
                    weight_kg=rebar_weights_by_section.get(sec_code, 0.0),
                    cumulative_before_kg=cumulative_before,
                    cumulative_after_kg=cumulative_after,
                    counts=counts,
                    registry=registry,
                )
        else:
            for param in repeated_row_params:
                group_key = param.get("key")
                reference_only = param.get("production_input") is not True or is_rebar_group(group_key)
                title_prefix = "СПРАВОЧНО: " if reference_only else ""
                _render_repeated_row_block(
                    ws, sec_code, group_key, param, review_groups.get(group_key, []), counts, review_groups,
                    title=f"{title_prefix}{section_name(contract)} — {param.get('label_ru', group_key)} ({(param.get('review_behavior') or {}).get('action_ru', 'Проверьте позиции построчно.')})",
                    rebar_metal_delivery_allocation=rebar_metal_delivery_allocation,
                    rebar_weights_by_section=rebar_weights_by_section,
                    rebar_cumulative_weights=rebar_cumulative_weights,
                    reference_only=reference_only,
                    registry=registry,
                )

        # Этап 1 (2026-08-12, Elena's request): the position-level rebar "zoo" (хомуты/лягушки/
        # выпуски/etc, see the blocks above) stays for checking against the PDF - but at the end
        # of every section that has rebar, also show a short "4 rows, not 40" summary by
        # class+diameter, matching how Elena's own real smetas present rebar (checked on a real project: her
        # final smeta shows only 4 diameter rows for foundation_slab, never the position-level
        # breakdown). See rebar_diameter_breakdown()/_append_rebar_diameter_summary() below.
        section_rebar_items = [
            item.get("value") or {}
            for group_key in rebar_group_keys_for_contract(contract)
            for item in review_groups.get(group_key, [])
        ]
        _append_rebar_diameter_summary(
            ws,
            f"{section_name(contract)} — Итого арматуры раздела, по диаметрам",
            rebar_diameter_breakdown(section_rebar_items),
            sec_code=sec_code,
        )
        all_rebar_items_for_box_summary.extend(section_rebar_items)

    # Итог по коробке (2026-07-30): one cross-section summary row after all 8 sections, so
    # Elena can see the real total driving the box-calculator's delivery-truck allocation above
    # (crane shifts are manual and not related to this total - see REBAR_METAL_DELIVERY_FIELD_BY_SECTION).
    # See compute_rebar_weights_by_section/compute_rebar_metal_delivery_allocation.
    section_names_by_code = metal_bucket_display_names(contracts, extraction)
    breakdown = "; ".join(
        f"{section_names_by_code.get(code, code)}: {weight:g} кг"
        for code, weight in rebar_weights_by_section.items()
        if weight > 0
    )
    append_section_band(ws, ["Итог по коробке"], len(PROJECT_HEADERS))
    ws.append([
        "Общий поставочный вес арматуры по проекту",
        box_total_metal_weight_kg,
        "кг",
        "Найдено (авто, box-калькулятор)",
        "",
        (
            "Справочно — сумма поставочного веса арматуры с запасом/округлением; "
            "из неё считается автораспределение машин доставки арматуры/металла по разделам."
        ),
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
        cell.fill = project_status_fill("Найдено (авто, box-калькулятор)")
    ws.row_dimensions[ws.max_row].height = COMPACT_ROW_HEIGHT

    append_blank_project_row(ws)

    # Same Этап 1 request as the per-section summaries above, just for the whole project at once
    # (2026-08-12) - one "4-6 rows, not the zoo" breakdown by diameter across every section that
    # has rebar, right next to the box-wide weight total it's built from.
    for bucket in rebar_diameter_breakdown(all_rebar_items_for_box_summary):
        label = f"{bucket['steel_class']} ф{bucket['diameter_mm']:g}"
        ws.append([
            f"Итого по проекту: {label}",
            round(bucket["length_m"], 2),
            "мп",
            "Найдено (авто, box-калькулятор)",
            "",
            (
                "Автоматически: сумма проектной длины из спецификаций по всем разделам для этого диаметра. "
                "Вес в примечании ниже — поставочный, с запасом/округлением для доставки."
            ),
            "",
            f"Поставочный вес с запасом/округлением (для справки): {bucket['weight_kg']:g} кг",
            "",
            "",
            "",
            "rebar_diameter_summary_total",
            "AUTO_CALCULATED",
            "",
        ])
        for cell in ws[ws.max_row]:
            cell.fill = project_status_fill("Найдено (авто, box-калькулятор)")
        ws.row_dimensions[ws.max_row].height = COMPACT_ROW_HEIGHT

    append_blank_project_row(ws)

    total_trucks = sum(rebar_metal_delivery_allocation.values())
    allocation_breakdown = "; ".join(
        f"{section_names_by_code.get(code, code)}: {trucks} маш."
        for code, trucks in rebar_metal_delivery_allocation.items()
        if trucks
    )
    ws.append([
        "Всего машин доставки арматуры/металла по проекту",
        total_trucks,
        "маш",
        "Найдено (авто, box-калькулятор)",
        "",
        f"Справочно — машины распределяются по накоплению {int(METAL_TRUCK_CAPACITY_KG // 1000)} т.",
        "",
        allocation_breakdown or "По разделам машин доставки не распределено.",
        "",
        "",
        "",
        "total_rebar_delivery_trucks",
        "AUTO_CALCULATED",
        "",
    ])
    for cell in ws[ws.max_row]:
        cell.fill = project_status_fill("Найдено (авто, box-калькулятор)")
    ws.row_dimensions[ws.max_row].height = COMPACT_ROW_HEIGHT

    validate_sheet01_registry(contracts, extraction, registry)

    ws.cell(1, 1).font = Font(name=FONT_NAME, bold=True, size=13)
    ws.cell(1, 1).fill = FILL_HEADER
    apply_table_style(ws, header_row=4)
    restyle_section_bands(ws)
    restyle_block_sheet(ws)
    # Merged last, using the sheet's true final ws.max_column (grows as item blocks with extra
    # correction columns get added above) - merging earlier at a narrower width risks the same
    # overlapping-merge corruption already fixed once for section bands/block titles.
    merge_row_full_width(ws, 1, ws.max_column)
    # Sheet 01 only: pin columns A-C (label/value/unit) so they stay visible while scrolling
    # through the status/source/fragment columns further right.
    ws.freeze_panes = f"{get_column_letter(min(4, ws.max_column + 1))}5"
    set_widths = {
        "A": 30, "B": 26, "C": 10, "D": 20, "E": 20, "F": 62, "G": 30, "H": 64,
        "I": 28, "J": 28, "K": 20, "L": 28, "M": 18, "N": 24,
        "O": 24, "P": 24, "Q": 24, "R": 24,
    }
    for col, width in set_widths.items():
        ws.column_dimensions[col].width = width
    for column in ["K", "L", "M", "N", "O", "P", "Q", "R", "S"]:
        ws.column_dimensions[column].hidden = True

    # Column widths are final now - autofit reads them to grow any row whose wrapped text needs
    # more than COMPACT_ROW_HEIGHT's one line (see estimate_row_height docstring).
    autofit_row_heights(ws, 1, ws.max_row)
    hide_inactive_project_rows(ws)

    return counts


FLOOR_SLABS_METAL_BUCKET_PREFIX = "floor_slabs::"


def floor_slabs_zone_labels(extraction: dict[str, Any]) -> dict[str, str]:
    _, found_groups, _ = index_extraction_section(extraction, "floor_slabs")
    labels: dict[str, str] = {}
    for item in found_groups.get(ZONES_GROUP_KEY, []):
        value = item.get("value") or {}
        zone_id = value.get("zone_id")
        if zone_id:
            labels[str(zone_id)] = str(value.get("display_name") or zone_id)
    return labels


def metal_bucket_display_names(contracts: list[dict[str, Any]], extraction: dict[str, Any]) -> dict[str, str]:
    names = {section_code(contract): section_name(contract) for contract in contracts}
    if P6_WALLS_SECTION_CODE in names:
        names["load_bearing_walls_lintels"] = names[P6_WALLS_SECTION_CODE]
    for zone_id, label in floor_slabs_zone_labels(extraction).items():
        names[f"{FLOOR_SLABS_METAL_BUCKET_PREFIX}{zone_id}"] = label
    return names


def floor_slabs_zone_ids(extraction: dict[str, Any]) -> list[str]:
    """Real zone_id list for the floor_slabs section, in the order floor_slab_zones[] rows appear
    in the extraction (same order the zones were found in the PDF/pour sequence - foundation, then
    walls, then floor pours in construction order, matching the real reference smeta's own section
    order). Used to give each physical slab its own bucket in the metal-delivery allocation below,
    instead of collapsing every zone into one "floor_slabs" lump."""
    _, found_groups, _ = index_extraction_section(extraction, "floor_slabs")
    zone_ids = []
    for item in found_groups.get("floor_slab_zones", []):
        zone_id = (item.get("value") or {}).get("zone_id")
        if zone_id:
            zone_ids.append(zone_id)
    return zone_ids


def build_rebar_lookup(
    contracts: list[dict[str, Any]], extraction: dict[str, Any]
) -> dict[str, list[dict[str, Any]]]:
    """section_code -> real rebar rows (steel_class/diameter_mm) found by extraction, pooled
    across every rebar-shaped group in that section (see rebar_group_keys_for_contract). Used to
    expand sheet 02's rebar_<class>_d<diameter>_m templated price row into one row per
    diameter/class actually present in this project.

    floor_slabs is ALSO bucketed by zone_id (floor_slabs::<zone_id> keys), in addition to the plain
    "floor_slabs" key every other caller expects (build_prices_sheet's sheet-02 rebar expansion
    reads the plain section_code, unaware of zones - it just needs the union of every diameter/class
    in the section) - see metal_section_order()/compute_rebar_metal_delivery_allocation() below for
    why the zone_id buckets exist: the real reference smeta workbook (checked 2026-08-10) shows
    metal delivery trucks land in specific pours (one in
    foundation_slab, one specifically in the 2nd-floor plate, none in the 1st-floor/kitchen/
    staircase pours), not as one lump total for "floor slabs" - the box-calculator's 10-tonne
    cumulative model has to run at zone granularity to reproduce that. Losing the plain
    "floor_slabs" key when this was first added was a real regression (sheet 02 silently stopped
    expanding floor_slabs rebar price rows) - fixed 2026-08-11, populate both."""
    lookup: dict[str, list[dict[str, Any]]] = {}
    for contract in contracts:
        sec_code = section_code(contract)
        group_keys = rebar_group_keys_for_contract(contract)
        if not group_keys:
            continue
        _, found_groups, _ = index_extraction_section(extraction, sec_code)
        if sec_code == P6_WALLS_SECTION_CODE:
            found_groups = p6_groups_with_review(extraction)
        if sec_code == "floor_slabs":
            for group_key in group_keys:
                for item in found_groups.get(group_key, []):
                    value = item.get("value") or {}
                    lookup.setdefault(sec_code, []).append(value)
                    zone_id = value.get("zone_id")
                    if zone_id:
                        lookup.setdefault(f"{FLOOR_SLABS_METAL_BUCKET_PREFIX}{zone_id}", []).append(value)
            continue
        items = [
            item.get("value") or {}
            for group_key in group_keys
            for item in found_groups.get(group_key, [])
        ]
        if items:
            lookup[sec_code] = items
    return lookup


def metal_section_order(extraction: dict[str, Any]) -> list[str]:
    """Ordered list of metal-delivery buckets for this specific project.

    Walls use the active production section code: the new P6 contract when the JSON has it,
    otherwise the pre-P6 load_bearing_walls_lintels section for older extractions.
    """
    sections = extraction.get("sections") or {}
    walls_bucket = P6_WALLS_SECTION_CODE if P6_WALLS_SECTION_CODE in sections else "load_bearing_walls_lintels"
    return ["foundation_slab", walls_bucket] + [
        f"{FLOOR_SLABS_METAL_BUCKET_PREFIX}{zone_id}" for zone_id in floor_slabs_zone_ids(extraction)
    ]


# Crane-shift counts are NOT automated (Elena's 2026-07-30 ruling: no real crane-shift-count
# formula exists anywhere in the codebase - see rebar_crane_manual_and_box_delivery_final memory).
# Only rebar/metal DELIVERY TRUCKS are automated here, which is what metal_delivery_allocator.py
# was actually designed and named for.
#
# section_code -> the one review_parameters/supplier_inputs key that holds "delivery trucks for
# rebar/metal" in that section, for sections where it is still a flat scalar written once per
# section. floor_slabs is handled separately (see the per-zone injection in the floor_slab_zones
# row-building loop) since its manual_rebar_metal_delivery_trucks field lives on each zone row,
# not one section-level cell.
REBAR_METAL_DELIVERY_FIELD_BY_SECTION = {
    "foundation_slab": "rebar_metal_delivery_trucks",
    "load_bearing_walls_lintels": "rebar_metal_delivery_trucks",
    P6_WALLS_SECTION_CODE: "rebar_metal_delivery_trucks",
}
METAL_TRUCK_CAPACITY_KG = 10000.0
# foundation_slab's own field: the box-wide total weight, used only for its internal calculator
# warning (see foundation_slab_calculator.py's suggested_box_metal_delivery_trucks check) - same
# number as the "Итог по коробке" summary row below, not a separate calculation.
BOX_TOTAL_METAL_WEIGHT_KEY = "box_total_metal_weight_kg"


def compute_rebar_weights_by_section(
    contracts: list[dict[str, Any]], extraction: dict[str, Any], order: list[str]
) -> dict[str, float]:
    """bucket -> delivery/procurement rebar weight in kg.

    Weight is calculated the same way as payable rebar rows: project length x waste coefficient,
    rounded up to whole rods, then multiplied by kg/m. This matches Elena's right-side smeta
    weight cells used to justify metal delivery, instead of the pure project-control length x kg/m.
    """
    lookup = build_rebar_lookup(contracts, extraction)
    weights: dict[str, float] = {}
    for bucket in order:
        total = 0.0
        for item in lookup.get(bucket, []):
            weight = rebar_item_delivery_weight_kg(item)
            if weight is not None:
                total += weight
        weights[bucket] = total
    return weights


def compute_rebar_cumulative_weights(
    weights_by_section: dict[str, float], order: list[str]
) -> dict[str, tuple[float, float]]:
    """bucket -> (cumulative_before_kg, cumulative_after_kg)."""
    result: dict[str, tuple[float, float]] = {}
    cumulative = 0.0
    for bucket in order:
        before = cumulative
        cumulative += weights_by_section.get(bucket, 0.0)
        result[bucket] = (before, cumulative)
    return result


def metal_delivery_note(
    *,
    weight_kg: float,
    cumulative_before_kg: float,
    cumulative_after_kg: float,
    allocated_trucks: int,
) -> str:
    if allocated_trucks and cumulative_before_kg <= 0 < cumulative_after_kg:
        reason = "это первая партия металла по коробке"
    elif allocated_trucks:
        reason = (
            f"на этом участке накопление пересекло порог "
            f"{int(METAL_TRUCK_CAPACITY_KG // 1000)} т"
        )
    elif weight_kg > 0:
        reason = "порог новой машины здесь не пересечен"
    else:
        reason = "в разделе нет учитываемой арматуры"
    return (
        f"Поставочный вес арматуры раздела с учетом запаса/округления: {weight_kg:g} кг; "
        f"накоплено до раздела: {cumulative_before_kg:g} кг; "
        f"после раздела: {cumulative_after_kg:g} кг. "
        f"Машин доставки здесь: {allocated_trucks}; {reason}."
    )


def append_rebar_metal_delivery_row(
    ws,
    *,
    sec_code: str,
    param: dict[str, Any],
    value: int,
    weight_kg: float,
    cumulative_before_kg: float,
    cumulative_after_kg: float,
    counts: dict[str, int],
    registry: Sheet01BuildRegistry,
) -> None:
    status = "Найдено (авто, box-калькулятор)"
    fragment = (
        metal_delivery_note(
            weight_kg=weight_kg,
            cumulative_before_kg=cumulative_before_kg,
            cumulative_after_kg=cumulative_after_kg,
            allocated_trucks=value,
        )
        + " Проверьте и поправьте при необходимости."
    )
    ws.append([
        param.get("label_ru", param.get("key", "")),
        value,
        param.get("unit", ""),
        status,
        "",
        (
            "Автоматически по поставочному весу арматуры с запасом/округлением "
            f"(накопление {int(METAL_TRUCK_CAPACITY_KG // 1000)} т) — проверьте и поправьте при необходимости."
        ),
        "",
        fragment,
        "",
        "",
        sec_code,
        param.get("key", ""),
        param.get("source_class", ""),
        param.get("target_code", ""),
    ])
    for cell in ws[ws.max_row]:
        cell.fill = project_status_fill(status)
    ws.row_dimensions[ws.max_row].height = COMPACT_ROW_HEIGHT
    counts["found"] += 1
    registry.record_scalar(sec_code, param)


def compute_rebar_metal_delivery_allocation(weights_by_section: dict[str, float], order: list[str]) -> dict[str, int]:
    """bucket -> automatically allocated delivery trucks for rebar/metal, using the existing
    box_calculator threshold-by-10-tonnes logic (experiments/box_calculator/
    metal_delivery_allocator.py) - the first truck goes to the first bucket with any weight,
    later trucks go to whichever bucket's cumulative weight crosses the next 10-tonne boundary.
    unit_price is 0 here - this call only needs allocated_trucks, not a cost (pricing for these
    lines already comes from the normal price_keys mechanism on sheet 02)."""
    sections = [
        MetalSection(section_code=code, section_name=code, metal_weight_kg=weights_by_section.get(code, 0.0))
        for code in order
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
    if price_registry_path is not None:
        price_registry = load_price_registry_google_first(price_registry_path)
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
    hide_diagnostic_sheets(wb)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    return {"output_path": str(output_path), **counts, **detail_counts}


def next_versioned_path(path: Path) -> Path:
    """Appends/bumps a _vN suffix so repeated builds never overwrite the previous one (a real
    review session rebuilds this file many times while iterating) - review_workbook.xlsx ->
    ..._v1.xlsx, then _v2.xlsx, etc., based on the highest _vN already present in the target
    directory. Re-versions cleanly if the given path already ends in _vN."""
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
