"""Build a deterministic estimator-facing notes report from extraction JSON.

The model-written service memo is useful, but it is not a reliable transport for
every `notes` field. This report makes parser doubts visible by collecting notes,
needs_review rows, low-confidence rows, missing targets, candidates, and parser
warnings directly from JSON.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SECTION_ORDER = [
    "earthworks",
    "foundation_slab",
    "waterproofing",
    "load_bearing_walls_lintels",
    "floor_slab_1",
    "floor_slab_2",
    "flat_roof",
    "schiedel_vent_channels",
]

SECTION_NAMES = {
    "earthworks": "Земляные работы",
    "foundation_slab": "Фундаментная плита",
    "waterproofing": "Гидроизоляция, утепление бортов плит",
    "load_bearing_walls_lintels": "Несущие стены и перемычки",
    "floor_slab_1": "Плита перекрытия 1 этажа",
    "floor_slab_2": "Плита перекрытия 2 этажа",
    "flat_roof": "Плоская кровля",
    "schiedel_vent_channels": "Вентиляционные каналы Schiedel",
}

CONDITIONAL_MISSING_ALTERNATIVES = {
    "earthworks": {
        "pit_excavation_depth_m": {
            "group": "pit_items",
            "note": "Объём выемки пришёл готовыми строками pit_items; глубина котлована для расчёта не нужна.",
        },
        "sand_base_volume_m3": {
            "group": "sand_items",
            "note": "Песок пришёл готовыми строками sand_items; один scalar 'песок под основание' не требуется.",
        },
        "communications_length_m": {
            "group": "communications_pipe_items",
            "note": "Длина коммуникаций считается из включённых строк communications_pipe_items.",
        },
        "trench_volume_m3": {
            "group": "trench_routes",
            "note": "Объём траншей считается суммой маршрутов trench_routes.",
        },
    },
    "foundation_slab": {
        "concrete_project_volume": {
            "group": "slab_zones",
            "note": "Единый scalar бетона не требуется: PDF дал бетон плиты по зонам, расчёт берёт сумму slab_zones.",
        },
        "thermal_insert_50_length": {
            "group": "thermal_insert_items",
            "note": "Скаляр 50 мм не требуется: PDF дал термовставки произвольными типоразмерами в thermal_insert_items.",
        },
        "thermal_insert_100_length": {
            "group": "thermal_insert_items",
            "note": "Скаляр 100 мм не требуется: PDF дал термовставки произвольными типоразмерами в thermal_insert_items.",
        },
        "thermal_insert_combined_length_m": {
            "group": "thermal_insert_items",
            "note": "Общая scalar-длина не требуется: рабочий источник — строки thermal_insert_items.",
        },
        "thermal_insert_50_material_spec_qty": {
            "group": "thermal_insert_items",
            "note": "Скаляр материала 50 мм не требуется: объём материала пришёл в строках thermal_insert_items.",
        },
        "thermal_insert_100_material_spec_qty": {
            "group": "thermal_insert_items",
            "note": "Скаляр материала 100 мм не требуется: объём материала пришёл в строках thermal_insert_items.",
        },
    },
    "load_bearing_walls_lintels": {
        "floors_count": {
            "group": "wall_block_items",
            "note": "Этажность из текста PDF не нужна как главный источник: при наличии wall_block_items калькулятор определяет второй уровень по строкам кладки.",
        },
        "parapet_masonry_volume": {
            "group": "wall_block_items",
            "note": "Фиксированный scalar парапета D400 не требуется: объём парапета может прийти через wall_block_items с ролью parapet.",
        },
        "parapet_gas_block_d500_250_volume": {
            "group": "wall_block_items",
            "note": "Фиксированный scalar парапета D500 не требуется: объём парапета может прийти через wall_block_items с ролью parapet.",
        },
    },
    "floor_slab_1": {
        "floor_slab_1_beams_concrete_volume": {
            "group": "beam_items",
            "note": "Готовый scalar итога бетона балок не требуется, если PDF дал балки строками: калькулятор суммирует beam_items.concrete_volume_m3. Это не относится к утеплению балок — его нельзя выводить из общей длины балок.",
        },
    },
    "floor_slab_2": {
        "floor_slab_2_beams_concrete_volume": {
            "group": "floor_slab_2_beam_items",
            "note": "Готовый scalar итога бетона балок не требуется, если PDF дал балки строками: калькулятор суммирует floor_slab_2_beam_items.concrete_volume_m3. Это не относится к утеплению балок — его нельзя выводить из общей длины балок.",
        },
    },
}

CONDITIONAL_ABSENT_TARGETS = {
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

DIAGNOSTIC_ONLY_MISSING_TARGETS = {
    "load_bearing_walls_lintels": {
        "floor_1_lintel_groove_length": "Диагностическое поле: перемычки в штробе пока фиксируются для будущей доработки и не участвуют в смете.",
        "floor_2_lintel_groove_length": "Диагностическое поле: перемычки в штробе пока фиксируются для будущей доработки и не участвуют в смете.",
    },
}

AUTO_SUM_CANDIDATE_TARGETS = {
    "foundation_slab": {
        "membrane_area_m2": "Можно автосуммировать компоненты мембраны PLANTER, если все candidates относятся к одной мембране и одному разделу фундаментной плиты.",
    },
    "load_bearing_walls_lintels": {
        "lintel_concrete_volume": "Можно автосуммировать компоненты бетона перемычек в U-блоках, если все candidates относятся к одному этажу и одному типу перемычек.",
        "floor_2_lintel_concrete_volume": "Можно автосуммировать компоненты бетона перемычек в U-блоках, если все candidates относятся к одному этажу и одному типу перемычек.",
        "floor_1_lintel_monolithic_concrete_volume": "Можно автосуммировать компоненты бетона монолитных перемычек, если все candidates относятся к одному этажу и одному типу перемычек.",
        "floor_2_lintel_monolithic_concrete_volume": "Можно автосуммировать компоненты бетона монолитных перемычек, если все candidates относятся к одному этажу и одному типу перемычек.",
    },
    "flat_roof": {
        "roof_internal_drains_count": "Можно автосуммировать внутренние кровельные воронки, если все candidates относятся к внутреннему водостоку и имеют единицу шт.",
        "roof_parapet_drains_count": "Можно автосуммировать парапетные воронки, если все candidates относятся к парапетному водостоку и имеют единицу шт.",
    },
}

BENIGN_FOUND_NOTE_PREFIXES = (
    "Количество по PDF:",
    "Масса дана явно",
)

WALL_BLOCK_ITEM_ALLOWED_ROLES = {"main_walls", "floor_2", "parapet", "partitions"}
ROOF_VENT_ABUTMENT_SCALAR_CODES = {
    "roof_vent_wall_abutment_level_1",
    "roof_vent_wall_abutment_level_2",
    "roof_vent_wall_abutment_length",
}
ROOF_VENT_ABUTMENT_TEXT_TERMS = (
    "примыкание к вк",
    "примыкания к вк",
    "примыкание к венткан",
    "примыкания к венткан",
    "примыкание к вентшах",
    "примыкания к вентшах",
)
BEAM_CONCRETE_SCALAR_CODES = {
    "floor_slab_1_beams_concrete_volume",
    "floor_slab_2_beams_concrete_volume",
}
BEAM_CONCRETE_TOTAL_TERMS = (
    "итого",
    "всего",
    "общий объем",
    "общий объём",
    "общая строка",
    "суммарный объем",
    "суммарный объём",
    "total",
)
EXPLICIT_TARGET_EXPECTED_UNITS = {
    "roof_area_level_1": "m2",
    "roof_area_level_2": "m2",
    "project_spec_roof_area": "m2",
}

# All *_rebar_items group codes from group_value_shapes (schemas/claude_extraction_output_schema.json)
# that carry an identifying (floor, component, steel_class, diameter_mm) tuple plus an optional
# explicit `code`. A row with no `code` AND a tuple that repeats another row's tuple in the same
# group is ambiguous: a calculator keyed by that tuple could silently drop/merge rows.
REBAR_ITEM_GROUP_CODES = {
    "foundation_rebar_items",
    "floor_slab_1_rebar_items",
    "floor_slab_2_rebar_items",
    "main_wall_rebar_items",
    "lintel_rebar_items",
}

ROOF_ZONE_ALLOWED_OPERABILITY = {"exploitable", "non_exploitable"}

# target_code -> raw-text/table-context terms that mean the matched value almost certainly came
# from the wrong PDF row for this target (e.g. formwork area copied into a "slab area" control
# field). Mirrors validate_claude_extraction.py's check_forbidden_target, kept here because it is a
# review-workbook/notes-report concern (same class as wall_role/beam-concrete-scalar checks above),
# not an extraction-time prompt-compliance check.
FORBIDDEN_SOURCE_TERMS = {
    "floor_slab_2_slab_area": (
        ("опалуб",),
        "Это площадь опалубки, а не площадь плиты. Инструкция по этому target прямо запрещает "
        "сопоставлять с ним строки нижней/основной опалубки. Оставьте floor_slab_2_slab_area пустым "
        "или удалите found-элемент; значение остаётся только в floor_slab_2_main_formwork_area.",
    ),
}

# Classic 50/100mm split (scalar target_codes) vs the arbitrary-size alternative group
# (thermal_insert_items) are mutually exclusive inputs for the same physical thermal inserts -
# filling both double-counts installation work. See thermal_insert_items_arbitrary_size_shipped memory.
THERMAL_INSERT_SCALAR_CODES = {
    "thermal_insert_50_length",
    "thermal_insert_100_length",
    "thermal_insert_combined_length_m",
    "thermal_insert_50_material_spec_qty",
    "thermal_insert_100_material_spec_qty",
}

# main_wall_rebar_items is load-bearing-wall rebar only; partition rebar must stay diagnostic-only
# (see main_wall_rebar_subwindow_and_partitions_exclusion memory). A row whose own text names a
# partition contradicts component=load_bearing_walls regardless of what the PDF actually says
# elsewhere - this is an internal JSON inconsistency, not a PDF-completeness question.
PARTITION_TEXT_TERMS = ("перегород",)
PARAPET_TEXT_TERMS = ("парапет",)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def iter_unique_items(section: dict[str, Any], statuses: tuple[str, ...]) -> list[dict[str, Any]]:
    """Yields each item once across the given statuses. `needs_review` items are always a subset
    of `found` (see found_item_shape in claude_extraction_output_schema.json), so scanning both
    without dedup double-counts every needs_review row - this matters not just for duplicate report
    lines but for any check that counts occurrences (e.g. rebar_duplicate_code_diagnostics)."""
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict[str, Any]] = []
    for status in statuses:
        for item in as_list(section.get(status)):
            if not isinstance(item, dict):
                continue
            key = (item_code(item), short(item.get("raw_text"), 240), short(item.get("value"), 240))
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
    return unique


def short(value: Any, limit: int = 260) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value)
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def confidence_text(item: dict[str, Any]) -> str:
    confidence = item.get("confidence")
    if confidence is None:
        return ""
    try:
        return f"{float(confidence):.2f}"
    except (TypeError, ValueError):
        return str(confidence)


def source_text(item: dict[str, Any]) -> str:
    parts = []
    if item.get("source_pdf"):
        parts.append(str(item["source_pdf"]))
    if item.get("page_number") is not None:
        parts.append(f"стр. {item['page_number']}")
    if item.get("page_title"):
        parts.append(str(item["page_title"]))
    if item.get("table_context"):
        parts.append(str(item["table_context"]))
    return " | ".join(parts)


def candidate_sum_info(item: dict[str, Any], section_code: str) -> dict[str, str] | None:
    code = item_code(item)
    rule_note = AUTO_SUM_CANDIDATE_TARGETS.get(section_code, {}).get(code)
    if not rule_note or item.get("value") is not None:
        return None
    values = []
    raw_parts = []
    for candidate in item.get("candidates") or []:
        if not isinstance(candidate, dict) or candidate.get("target_code") != code:
            continue
        value = candidate.get("value")
        if value is None:
            continue
        try:
            values.append(float(value))
        except (TypeError, ValueError):
            continue
        if candidate.get("raw_text"):
            raw_parts.append(str(candidate["raw_text"]))
    if len(values) < 2:
        return None
    total = round(sum(values), 3)
    value_expr = " + ".join(f"{value:g}" for value in values)
    return {
        "value": f"{total:g}",
        "status": "needs_review_autosum",
        "notes": (
            f"В JSON нет единого итогового значения, но есть компоненты одной позиции. "
            f"{rule_note} Проверьте компоненты и используйте автосумму."
        ),
        "auto_sum": f"{value_expr} = {total:g}. Компоненты: {'; '.join(raw_parts)}",
    }


def candidate_sum_text(item: dict[str, Any], section_code: str) -> str:
    info = candidate_sum_info(item, section_code)
    return info["auto_sum"] if info else ""


def item_code(item: dict[str, Any]) -> str:
    return str(item.get("target_code") or item.get("group_code") or "raw_table_rows")


def item_title(item: dict[str, Any]) -> str:
    name = item.get("item_name")
    code = item_code(item)
    if name:
        return f"{code}: {name}"
    return code


def is_benign_found_note(note: Any) -> bool:
    if not note:
        return False
    text = str(note).strip()
    return any(text.startswith(prefix) for prefix in BENIGN_FOUND_NOTE_PREFIXES)


def normalized_text(*values: Any) -> str:
    return " ".join(str(value).lower().replace("ё", "е") for value in values if value is not None)


def should_include_item(item: dict[str, Any], confidence_threshold: float, status: str) -> bool:
    if item.get("notes"):
        if (
            status == "found"
            and not item.get("needs_review")
            and not item.get("candidates")
            and is_benign_found_note(item.get("notes"))
        ):
            return False
        return True
    if item.get("needs_review"):
        return True
    if item.get("candidates"):
        return True
    confidence = item.get("confidence")
    try:
        if confidence is not None and float(confidence) < confidence_threshold:
            return True
    except (TypeError, ValueError):
        return True
    return False


def has_roof_zone_rows(section: dict[str, Any]) -> bool:
    for status in ("needs_review", "found", "raw_table_rows"):
        for item in as_list(section.get(status)):
            if not isinstance(item, dict):
                continue
            if item.get("group_code") == "roof_zones" or item.get("target_code") == "roof_zones":
                return True
    return False


def is_roof_vent_abutment_item(item: dict[str, Any]) -> bool:
    # Items already tied to roof_zones (its own found/needs_review row, or a raw_table_rows
    # component row whose mapped_target_codes says it feeds roof_zones) are the CORRECT home for
    # this data, not a legacy scalar sitting outside the zone — exclude them so a zone's own
    # explanatory raw_text/notes (which often names "вентканал" to show its math) doesn't trigger
    # a false positive against itself. Real bug found 2026-08-05: a zone row's raw_text literally
    # saying "вентканалы 5,42 п.м; ... = 14,92 п.м" (the correct sum) was flagged as if it were an
    # outside-zone duplicate, alongside the raw_table_rows component row for the same already-summed
    # value — both are compliant, not violations.
    if item.get("group_code") == "roof_zones" or item.get("target_code") == "roof_zones":
        return False
    if "roof_zones" in (item.get("mapped_target_codes") or []):
        return False
    code = str(item.get("target_code") or "")
    if code in ROOF_VENT_ABUTMENT_SCALAR_CODES:
        return True
    text = normalized_text(
        item.get("raw_text"),
        item.get("item_name"),
        item.get("notes"),
        item.get("table_context"),
    )
    return any(term in text for term in ROOF_VENT_ABUTMENT_TEXT_TERMS)


def expected_unit_for_target(code: str) -> str | None:
    if code in EXPLICIT_TARGET_EXPECTED_UNITS:
        return EXPLICIT_TARGET_EXPECTED_UNITS[code]
    if code.endswith("_m2") or "_area" in code:
        return "m2"
    if code.endswith("_m3") or "_volume" in code:
        return "m3"
    return None


def candidate_unit_mismatch_diagnostics(section: dict[str, Any]) -> list[dict[str, str]]:
    diagnostics: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()

    for status in ("needs_review", "found"):
        for item in as_list(section.get(status)):
            if not isinstance(item, dict) or not item.get("candidates"):
                continue
            code = item_code(item)
            if code == "raw_table_rows":
                continue
            expected_unit = expected_unit_for_target(code)
            if not expected_unit:
                continue
            for candidate in as_list(item.get("candidates")):
                if not isinstance(candidate, dict):
                    continue
                candidate_unit = candidate.get("normalized_unit")
                if not candidate_unit or candidate_unit == expected_unit:
                    continue
                key = (
                    code,
                    str(candidate_unit),
                    short(candidate.get("value"), 120),
                    short(candidate.get("raw_text"), 220),
                )
                if key in seen:
                    continue
                seen.add(key)
                diagnostics.append(
                    {
                        "status": "semantic_error",
                        "title": f"{code}: candidate unit `{candidate_unit}` does not match `{expected_unit}`",
                        "confidence": confidence_text(candidate) or confidence_text(item),
                        "value": short(candidate.get("value"), 220),
                        "source": source_text(candidate) or source_text(item),
                        "raw_text": short(candidate.get("raw_text") or item.get("raw_text"), 320),
                        "notes": (
                            "Единица кандидата не совпадает с единицей target. Такой candidate нельзя "
                            "использовать как значение поля без отдельного явного правила пересчёта. "
                            "Оставьте строку на проверку или маппьте её в target с подходящей единицей."
                        ),
                        "auto_sum": "",
                        "candidates": "",
                    }
                )
    return diagnostics


def candidate_target_code_mismatch_diagnostics(section: dict[str, Any]) -> list[dict[str, str]]:
    """A candidate's own `target_code` should match the target_code of the item it lives under.
    A mismatch means the candidate was built for a different field and got attached to the wrong
    item - the number and source may be correct, but a strict consumer keying off target_code
    would silently misfile it. Found via the 2026-08-04 heavy-audit pass on floor_slab_1_edge_eps_
    work_length, whose candidates both carried floor_slab_1_slab_edge_perimeter instead."""
    diagnostics: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()

    for item in iter_unique_items(section, ("needs_review", "found")):
        item_target = item.get("target_code")
        if not item_target or not item.get("candidates"):
            continue
        for candidate in as_list(item.get("candidates")):
            if not isinstance(candidate, dict):
                continue
            candidate_target = candidate.get("target_code")
            if not candidate_target or candidate_target == item_target:
                continue
            key = (
                str(item_target),
                str(candidate_target),
                short(candidate.get("value"), 120),
                short(candidate.get("raw_text"), 220),
            )
            if key in seen:
                continue
            seen.add(key)
            diagnostics.append(
                {
                    "status": "semantic_error",
                    "title": f"{item_target}: candidate carries mismatched target_code `{candidate_target}`",
                    "confidence": confidence_text(candidate) or confidence_text(item),
                    "value": short(candidate.get("value"), 220),
                    "source": source_text(candidate) or source_text(item),
                    "raw_text": short(candidate.get("raw_text") or item.get("raw_text"), 320),
                    "notes": (
                        f"Candidate внутри `{item_target}` несёт `target_code`='{candidate_target}' — "
                        "поле другого target. Число и источник могут быть верными, но candidate "
                        "структурно привязан не к тому полю. Приведите target_code candidate к полю, "
                        "в котором он лежит, либо перенесите candidate в тот item, которому он "
                        "действительно принадлежит."
                    ),
                    "auto_sum": "",
                    "candidates": "",
                }
            )
    return diagnostics


def roof_vent_abutment_diagnostics(section: dict[str, Any]) -> list[dict[str, str]]:
    if not has_roof_zone_rows(section):
        return []

    candidates: list[dict[str, Any]] = []
    for status in ("needs_review", "found"):
        for item in as_list(section.get(status)):
            if isinstance(item, dict) and is_roof_vent_abutment_item(item):
                candidates.append(item)

    if not candidates:
        for item in as_list(section.get("raw_table_rows")):
            if isinstance(item, dict) and is_roof_vent_abutment_item(item):
                candidates.append(item)

    diagnostics: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for item in candidates:
        key = (
            short(item.get("target_code") or item.get("group_code"), 80),
            short(item.get("value"), 120),
            short(item.get("source_pdf"), 160),
            short(item.get("raw_text"), 220),
        )
        if key in seen:
            continue
        seen.add(key)
        diagnostics.append(
            {
                "status": "semantic_error",
                "title": "roof_zones: linear vent-channel abutment outside live roof zone",
                "confidence": confidence_text(item),
                "value": short(item.get("value"), 220),
                "source": source_text(item),
                "raw_text": short(item.get("raw_text"), 320),
                "notes": (
                    "В JSON есть roof_zones[], значит production-источник геометрии кровли — зоны. "
                    "Линейные примыкания к ВК/вентканалам/вентшахтам в м.п. должны быть включены в "
                    "roof_zones[].wall_abutment_length_m соответствующей зоны, а не лежать отдельным "
                    "legacy scalar. Это не Schiedel и не штучное поле vent_shaft_abutment_count."
                ),
                "auto_sum": "",
                "candidates": "",
            }
        )
    return diagnostics


def beam_concrete_scalar_diagnostics(section: dict[str, Any]) -> list[dict[str, str]]:
    diagnostics: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for status in ("needs_review", "found"):
        for item in as_list(section.get(status)):
            if not isinstance(item, dict):
                continue
            code = item_code(item)
            if code not in BEAM_CONCRETE_SCALAR_CODES or item.get("value") in (None, ""):
                continue
            evidence_text = normalized_text(
                item.get("raw_text"),
                item.get("item_name"),
                item.get("notes"),
                item.get("table_context"),
            )
            if any(term in evidence_text for term in BEAM_CONCRETE_TOTAL_TERMS):
                continue
            key = (code, short(item.get("value"), 120), short(item.get("raw_text"), 220))
            if key in seen:
                continue
            seen.add(key)
            diagnostics.append(
                {
                    "status": "semantic_error",
                    "title": f"{code}: scalar beam concrete is filled without explicit total row",
                    "confidence": confidence_text(item),
                    "value": short(item.get("value"), 220),
                    "source": source_text(item),
                    "raw_text": short(item.get("raw_text"), 320),
                    "notes": (
                        "Scalar бетона балок можно заполнять только из явной общей строки по всем "
                        "маркам балок: Итого/Всего/общий объём. Если PDF даёт бетон по маркам, эти "
                        "строки должны идти в repeated group балок, а scalar должен оставаться пустым "
                        "или закрываться дальше кодом через сумму repeated rows."
                    ),
                    "auto_sum": "",
                    "candidates": "",
                }
            )
    return diagnostics


def rebar_duplicate_code_diagnostics(section: dict[str, Any]) -> list[dict[str, str]]:
    """A rebar row with no `code` and an identifying (floor, component, steel_class, diameter_mm)
    tuple that repeats another row's tuple in the same group is ambiguous: a calculator keyed by
    that tuple could silently drop or merge rows. An explicit, distinct `code` on each row resolves
    this even when the base tuple repeats (e.g. window vs main-wall rebar of the same diameter)."""
    diagnostics: list[dict[str, str]] = []
    by_group: dict[str, list[dict[str, Any]]] = {}
    for item in iter_unique_items(section, ("needs_review", "found")):
        group_code = item.get("group_code")
        if group_code not in REBAR_ITEM_GROUP_CODES:
            continue
        by_group.setdefault(group_code, []).append(item)

    for group_code, items in by_group.items():
        tuple_counts: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
        seen_codes: dict[str, int] = {}
        for item in items:
            value = item.get("value") if isinstance(item.get("value"), dict) else {}
            code = value.get("code")
            if code:
                seen_codes[str(code)] = seen_codes.get(str(code), 0) + 1
                continue
            key = (
                value.get("floor"),
                value.get("component"),
                value.get("steel_class"),
                value.get("diameter_mm"),
            )
            tuple_counts.setdefault(key, []).append(item)

        for key, dup_items in tuple_counts.items():
            if len(dup_items) < 2:
                continue
            example = dup_items[0]
            diagnostics.append(
                {
                    "status": "semantic_error",
                    "title": f"{group_code}: {len(dup_items)} rows share floor/component/class/diameter with no `code`",
                    "confidence": confidence_text(example),
                    "value": short(example.get("value"), 220),
                    "source": source_text(example),
                    "raw_text": short(example.get("raw_text"), 320),
                    "notes": (
                        f"floor={key[0]!r}, component={key[1]!r}, steel_class={key[2]!r}, "
                        f"diameter_mm={key[3]!r} повторяется у {len(dup_items)} строк без "
                        "уникального `code`. Калькулятор, ключующий строки по этому набору полей, "
                        "может молча учесть только одну из них. Назначьте стабильные уникальные "
                        "`code` (например, по назначению строки: подоконное армирование, второй "
                        "свет и т.п.), не полагаясь на то, что позиция в списке сохранится."
                    ),
                    "auto_sum": "",
                    "candidates": "",
                }
            )
        for code, count in seen_codes.items():
            if count < 2:
                continue
            diagnostics.append(
                {
                    "status": "semantic_error",
                    "title": f"{group_code}: code `{code}` used by {count} rows",
                    "confidence": "",
                    "value": "",
                    "source": "",
                    "raw_text": "",
                    "notes": (
                        f"Значение `code`={code!r} повторяется у {count} строк группы {group_code}. "
                        "`code` должен однозначно определять строку внутри группы."
                    ),
                    "auto_sum": "",
                    "candidates": "",
                }
            )
    return diagnostics


def forbidden_source_diagnostics(section: dict[str, Any]) -> list[dict[str, str]]:
    """Flags a found scalar whose raw evidence text matches a known wrong-source pattern for that
    target_code (e.g. a "slab area" control field actually sourced from a formwork-area row).
    Mirrors validate_claude_extraction.py's check_forbidden_target, extended with a per-target term
    list instead of one hardcoded rule."""
    diagnostics: list[dict[str, str]] = []
    for item in iter_unique_items(section, ("needs_review", "found")):
        code = item_code(item)
        rule = FORBIDDEN_SOURCE_TERMS.get(code)
        if not rule or item.get("value") in (None, ""):
            continue
        terms, note = rule
        evidence_text = normalized_text(
            item.get("raw_text"), item.get("notes"), item.get("table_context")
        )
        if not any(term in evidence_text for term in terms):
            continue
        diagnostics.append(
            {
                "status": "semantic_error",
                "title": f"{code}: value sourced from a forbidden row pattern",
                "confidence": confidence_text(item),
                "value": short(item.get("value"), 220),
                "source": source_text(item),
                "raw_text": short(item.get("raw_text"), 320),
                "notes": note,
                "auto_sum": "",
                "candidates": "",
            }
        )
    return diagnostics


def thermal_insert_conflict_diagnostics(section: dict[str, Any]) -> list[dict[str, str]]:
    """The classic 50/100mm scalar split and the arbitrary-size thermal_insert_items group are
    mutually exclusive inputs for the same physical thermal inserts; filling both double-counts
    installation work and material."""
    has_items_group = False
    filled_scalars: list[dict[str, Any]] = []
    for item in iter_unique_items(section, ("needs_review", "found")):
        if item.get("group_code") == "thermal_insert_items":
            has_items_group = True
        code = item_code(item)
        if code in THERMAL_INSERT_SCALAR_CODES and item.get("value") not in (None, ""):
            filled_scalars.append(item)

    if not has_items_group or not filled_scalars:
        return []

    diagnostics: list[dict[str, str]] = []
    for item in filled_scalars:
        code = item_code(item)
        diagnostics.append(
            {
                "status": "semantic_error",
                "title": f"{code}: filled at the same time as thermal_insert_items",
                "confidence": confidence_text(item),
                "value": short(item.get("value"), 220),
                "source": source_text(item),
                "raw_text": short(item.get("raw_text"), 320),
                "notes": (
                    "thermal_insert_items используется для произвольных типоразмеров и заменяет "
                    "классический scalar-путь 50/100 мм, а не дополняет его. Один и тот же объём "
                    "термовставок сейчас посчитан дважды. Оставьте либо scalar-поля (thermal_insert_"
                    "50/100_length, thermal_insert_combined_length_m и соответствующий material_spec_"
                    "qty), либо thermal_insert_items, не оба вместе."
                ),
                "auto_sum": "",
                "candidates": "",
            }
        )
    return diagnostics


def roof_zone_operability_diagnostics(section: dict[str, Any]) -> list[dict[str, str]]:
    diagnostics: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for status in ("needs_review", "found"):
        for item in as_list(section.get(status)):
            if not isinstance(item, dict) or item.get("group_code") != "roof_zones":
                continue
            value = item.get("value") if isinstance(item.get("value"), dict) else {}
            operability = value.get("operability")
            if operability is None or operability in ROOF_ZONE_ALLOWED_OPERABILITY:
                continue
            key = (str(operability), short(item.get("item_name"), 120))
            if key in seen:
                continue
            seen.add(key)
            diagnostics.append(
                {
                    "status": "semantic_error",
                    "title": f"roof_zones: invalid operability `{operability}`",
                    "confidence": confidence_text(item),
                    "value": short(item.get("value"), 220),
                    "source": source_text(item),
                    "raw_text": short(item.get("raw_text"), 320),
                    "notes": (
                        "Недопустимое значение operability для зоны кровли. Разрешены только "
                        "`exploitable`, `non_exploitable` — от этого признака зависит выбор мембраны "
                        "V-GR/V-RP."
                    ),
                    "auto_sum": "",
                    "candidates": "",
                }
            )
    return diagnostics


def partition_rebar_in_main_wall_diagnostics(section: dict[str, Any]) -> list[dict[str, str]]:
    diagnostics: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for status in ("needs_review", "found"):
        for item in as_list(section.get(status)):
            if not isinstance(item, dict) or item.get("group_code") != "main_wall_rebar_items":
                continue
            text = normalized_text(item.get("item_name"), item.get("raw_text"))
            if not any(term in text for term in PARTITION_TEXT_TERMS):
                continue
            key = (short(item.get("item_name"), 120), short(item.get("raw_text"), 220))
            if key in seen:
                continue
            seen.add(key)
            diagnostics.append(
                {
                    "status": "semantic_error",
                    "title": "main_wall_rebar_items: row text names a partition",
                    "confidence": confidence_text(item),
                    "value": short(item.get("value"), 220),
                    "source": source_text(item),
                    "raw_text": short(item.get("raw_text"), 320),
                    "notes": (
                        "Собственный текст строки называет перегородку, а не несущую стену, "
                        "независимо от значения component=load_bearing_walls. Арматура перегородок "
                        "запрещена в main_wall_rebar_items и не должна попадать в стоимость несущих "
                        "стен. Уберите строку из производственной группы, оставьте только "
                        "диагностически."
                    ),
                    "auto_sum": "",
                    "candidates": "",
                }
            )
    return diagnostics


def parapet_rebar_in_main_wall_diagnostics(section: dict[str, Any]) -> list[dict[str, str]]:
    """A main_wall_rebar_items row whose own text names the parapet is misfiled regardless of
    component=load_bearing_walls: the calculator folds it into the ordinary main-wall rebar total
    (material cost isn't lost, just mispriced), and the dedicated parapet_chasing_base_length /
    parapet_rebar_base_length scalars stay empty, so the separate parapet chasing/groove-cutting
    work line never fires. Real case, 2026-08-05 ТРЦ: two rows explicitly labelled 'парапеты 1/2
    этаж' (47.36 + 105.68 m) were mistagged this way."""
    diagnostics: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for status in ("needs_review", "found"):
        for item in as_list(section.get(status)):
            if not isinstance(item, dict) or item.get("group_code") != "main_wall_rebar_items":
                continue
            text = normalized_text(item.get("item_name"), item.get("raw_text"))
            if not any(term in text for term in PARAPET_TEXT_TERMS):
                continue
            key = (short(item.get("item_name"), 120), short(item.get("raw_text"), 220))
            if key in seen:
                continue
            seen.add(key)
            diagnostics.append(
                {
                    "status": "semantic_error",
                    "title": "main_wall_rebar_items: row text names the parapet",
                    "confidence": confidence_text(item),
                    "value": short(item.get("value"), 220),
                    "source": source_text(item),
                    "raw_text": short(item.get("raw_text"), 320),
                    "notes": (
                        "Собственный текст строки называет парапет, а не несущую стену, независимо "
                        "от component=load_bearing_walls. Материал не теряется (считается по цене "
                        "несущих стен), но отдельная строка штробления парапета "
                        "(parapet_chasing_base_length) остаётся пустой. Перенесите строку в "
                        "parapet_chasing_base_length/parapet_rebar_base_length (сумма по этажам), "
                        "уберите из main_wall_rebar_items."
                    ),
                    "auto_sum": "",
                    "candidates": "",
                }
            )
    return diagnostics


def semantic_diagnostics(section_code: str, section: dict[str, Any]) -> list[dict[str, str]]:
    diagnostics: list[dict[str, str]] = []
    diagnostics.extend(candidate_unit_mismatch_diagnostics(section))
    diagnostics.extend(candidate_target_code_mismatch_diagnostics(section))
    diagnostics.extend(rebar_duplicate_code_diagnostics(section))
    diagnostics.extend(forbidden_source_diagnostics(section))

    if section_code == "flat_roof":
        diagnostics.extend(roof_vent_abutment_diagnostics(section))
        diagnostics.extend(roof_zone_operability_diagnostics(section))
    if section_code in {"floor_slab_1", "floor_slab_2"}:
        diagnostics.extend(beam_concrete_scalar_diagnostics(section))
    if section_code == "foundation_slab":
        diagnostics.extend(thermal_insert_conflict_diagnostics(section))

    if section_code != "load_bearing_walls_lintels":
        return diagnostics

    diagnostics.extend(partition_rebar_in_main_wall_diagnostics(section))
    diagnostics.extend(parapet_rebar_in_main_wall_diagnostics(section))

    seen: set[tuple[str, str, str]] = set()
    for status in ("needs_review", "found", "raw_table_rows"):
        for item in as_list(section.get(status)):
            if not isinstance(item, dict) or item.get("group_code") != "wall_block_items":
                continue
            value = item.get("value") if isinstance(item.get("value"), dict) else {}
            wall_role = value.get("wall_role")
            if wall_role in WALL_BLOCK_ITEM_ALLOWED_ROLES:
                continue
            key = (str(wall_role), short(item.get("raw_text"), 180), short(item.get("item_name"), 120))
            if key in seen:
                continue
            seen.add(key)
            diagnostics.append(
                {
                    "status": "semantic_error",
                    "title": f"wall_block_items: invalid wall_role `{wall_role}`",
                    "confidence": confidence_text(item),
                    "value": short(item.get("value"), 220),
                    "source": source_text(item),
                    "raw_text": short(item.get("raw_text"), 320),
                    "notes": (
                        "Недопустимая роль стены для калькулятора. Разрешены только "
                        "`main_walls`, `floor_2`, `parapet`, `partitions`. "
                        "Наружные/внутренние несущие стены должны различаться через context, "
                        "а не через wall_role; обкладка вентканалов не относится к wall_block_items."
                    ),
                    "auto_sum": "",
                    "candidates": "",
                }
            )
    return diagnostics


def collect_section_items(
    section_code: str,
    section: dict[str, Any],
    confidence_threshold: float,
) -> tuple[list[dict[str, str]], list[str]]:
    collected: list[dict[str, str]] = []
    missing_codes: list[str] = []
    seen: set[tuple[str, str, str, str]] = set()
    seen_evidence_notes: set[tuple[str, str]] = set()
    alternative_notes: dict[str, str] = {}

    found_group_codes = {
        item.get("group_code")
        for item in as_list(section.get("found"))
        if isinstance(item, dict) and item.get("group_code")
    }
    closed_by_alternative: set[str] = set()
    classified_missing: list[dict[str, str]] = []

    def close_by_alternative(code: str) -> bool:
        rule = CONDITIONAL_MISSING_ALTERNATIVES.get(section_code, {}).get(code)
        if isinstance(rule, dict):
            alternative_group = rule.get("group")
            note = rule.get("note") or "Scalar не требуется: данные пришли в виде повторяющихся строк."
        else:
            alternative_group = rule
            note = "Scalar не требуется: данные пришли в виде повторяющихся строк, которые закрывают этот сценарий расчёта."
        if alternative_group and alternative_group in found_group_codes:
            title = f"{code} -> {alternative_group}"
            closed_by_alternative.add(title)
            alternative_notes[title] = note
            return True
        return False

    def classify_missing(code: str) -> bool:
        diagnostic_note = DIAGNOSTIC_ONLY_MISSING_TARGETS.get(section_code, {}).get(code)
        if diagnostic_note:
            classified_missing.append(
                {
                    "status": "diagnostic_only",
                    "title": code,
                    "notes": diagnostic_note,
                }
            )
            return True
        conditional_note = CONDITIONAL_ABSENT_TARGETS.get(section_code, {}).get(code)
        if conditional_note:
            classified_missing.append(
                {
                    "status": "conditional_absent_ok",
                    "title": code,
                    "notes": conditional_note,
                }
            )
            return True
        return False

    def add(status: str, item: dict[str, Any]) -> None:
        code = item_code(item)
        if status in {"needs_review", "found", "missing"} and item.get("value") in (None, "") and close_by_alternative(code):
            return
        if not should_include_item(item, confidence_threshold, status):
            return
        evidence_key = (short(item.get("raw_text"), 240), short(item.get("notes"), 240))
        if status == "raw_table_rows" and evidence_key in seen_evidence_notes:
            return
        key = (
            item_code(item),
            short(item.get("raw_text"), 180),
            short(item.get("notes"), 180),
            short(item.get("candidates"), 180),
        )
        if key in seen:
            return
        seen.add(key)
        if evidence_key != ("", ""):
            seen_evidence_notes.add(evidence_key)
        auto_sum = candidate_sum_info(item, section_code)
        display_status = auto_sum["status"] if auto_sum else status
        display_value = auto_sum["value"] if auto_sum else short(item.get("value"), 220)
        display_notes = auto_sum["notes"] if auto_sum else short(item.get("notes"), 420)
        display_auto_sum = auto_sum["auto_sum"] if auto_sum else ""
        # When the report can render candidates as a clear autosum, do not also print the raw
        # candidates JSON wall. The raw JSON remains in extraction_output.json; this report is for
        # human review.
        display_candidates = "" if auto_sum else short(item.get("candidates"), 420)
        collected.append(
            {
                "status": display_status,
                "title": item_title(item),
                "confidence": confidence_text(item),
                "value": display_value,
                "source": source_text(item),
                "raw_text": short(item.get("raw_text"), 320),
                "notes": display_notes,
                "auto_sum": short(display_auto_sum, 520),
                "candidates": display_candidates,
            }
        )

    for item in as_list(section.get("needs_review")):
        if isinstance(item, dict):
            add("needs_review", item)

    for item in as_list(section.get("found")):
        if isinstance(item, dict):
            add("found", item)

    for item in as_list(section.get("raw_table_rows")):
        if isinstance(item, dict):
            add("raw_table_rows", item)

    for item in as_list(section.get("missing")):
        if isinstance(item, str):
            if not close_by_alternative(item) and not classify_missing(item):
                missing_codes.append(item)
        elif isinstance(item, dict):
            add("missing", item)

    for item in classified_missing:
        collected.append(
            {
                "status": item["status"],
                "title": item["title"],
                "confidence": "",
                "value": "",
                "source": "",
                "raw_text": "",
                "notes": item["notes"],
                "auto_sum": "",
                "candidates": "",
            }
        )

    collected.extend(semantic_diagnostics(section_code, section))

    for text in sorted(closed_by_alternative):
        collected.append(
            {
                "status": "not_required_alt",
                "title": text,
                "confidence": "",
                "value": "",
                "source": "",
                "raw_text": "",
                "notes": alternative_notes.get(
                    text,
                    "Scalar не требуется: данные пришли в виде повторяющихся строк, которые закрывают этот сценарий расчёта.",
                ),
                "auto_sum": "",
                "candidates": "",
            }
        )

    return collected, missing_codes


def render_report(extraction: dict[str, Any], input_path: Path, confidence_threshold: float) -> str:
    project_name = extraction.get("project_name") or "проект не указан"
    sections = extraction.get("sections") or {}
    ordered_codes = [code for code in SECTION_ORDER if code in sections]
    ordered_codes.extend(sorted(code for code in sections if code not in set(ordered_codes)))

    section_reports: list[tuple[str, list[dict[str, str]], list[str]]] = []
    status_counts: dict[str, int] = {}
    total_items = 0
    for section_code in ordered_codes:
        section_items, missing_codes = collect_section_items(
            section_code,
            sections.get(section_code) or {},
            confidence_threshold,
        )
        if not section_items and not missing_codes:
            continue
        section_reports.append((section_code, section_items, missing_codes))
        total_items += len(section_items) + len(missing_codes)
        for item in section_items:
            status = item.get("status") or "unknown"
            status_counts[status] = status_counts.get(status, 0) + 1
        if missing_codes:
            status_counts["missing_code"] = status_counts.get("missing_code", 0) + len(missing_codes)

    warnings = extraction.get("extraction_warnings") or []
    lines = [
        "# Приложение к служебной записке: все notes из extraction JSON",
        "",
        f"Источник JSON: `{input_path}`",
        f"Проект: {project_name}",
        "",
        "Это техническое приложение собрано кодом из JSON, а не написано нейронкой.",
        "Сюда попадают: `needs_review`, значимые `notes`, кандидаты, низкая уверенность и `missing`.",
        "Безопасные технические notes вида `Количество по PDF` для найденных строк не выводятся, чтобы не прятать реальные сомнения в шуме.",
        f"Порог низкой уверенности: ниже {confidence_threshold:.2f}.",
        "",
    ]

    lines.extend(["## Сводка", ""])
    lines.append(f"- Общие предупреждения parser: {len(warnings)}")
    lines.append(f"- Пунктов в приложении: {total_items}")
    if status_counts:
        status_text = ", ".join(f"`{status}`: {count}" for status, count in sorted(status_counts.items()))
        lines.append(f"- По статусам: {status_text}")
    if section_reports:
        section_text = "; ".join(
            f"{SECTION_NAMES.get(code, code)}: {len(items) + len(missing)}"
            for code, items, missing in section_reports
        )
        lines.append(f"- По разделам: {section_text}")
    lines.append("")

    if warnings:
        lines.extend(["## Общие предупреждения parser", ""])
        for warning in warnings:
            lines.append(f"- {short(warning, 500)}")
        lines.append("")

    for section_code, section_items, missing_codes in section_reports:
        section_name = SECTION_NAMES.get(section_code, section_code)
        lines.extend([f"## {section_name}", ""])
        for index, item in enumerate(section_items, start=1):
            lines.append(f"### {index}. {item['title']}")
            lines.append(f"- Статус: `{item['status']}`")
            if item["confidence"]:
                lines.append(f"- Уверенность: {item['confidence']}")
            if item["value"]:
                lines.append(f"- Значение: {item['value']}")
            if item["source"]:
                lines.append(f"- Источник: {item['source']}")
            if item["raw_text"]:
                lines.append(f"- Строка PDF: {item['raw_text']}")
            if item["notes"]:
                lines.append(f"- Notes: {item['notes']}")
            if item["auto_sum"]:
                lines.append(f"- Автосумма: {item['auto_sum']}")
            if item["candidates"]:
                lines.append(f"- Candidates: {item['candidates']}")
            lines.append("")
        if missing_codes:
            lines.append("### Не найдено в JSON")
            lines.append("")
            lines.append("Целевые параметры раздела, которые parser не заполнил:")
            lines.append("")
            for code in missing_codes:
                lines.append(f"- `{code}`")
            lines.append("")

    if total_items == 0:
        lines.append("Замечаний, notes, candidates, needs_review и missing не найдено.")
        lines.append("")
    else:
        lines.append(f"Итого пунктов в приложении: {total_items}.")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Path to extraction_output.json")
    parser.add_argument("--output", type=Path, required=True, help="Path to write markdown/txt report")
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.90,
        help="Include rows with confidence below this value even if notes are empty.",
    )
    args = parser.parse_args()

    extraction = load_json(args.input)
    report = render_report(extraction, args.input, args.confidence_threshold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"notes report -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
