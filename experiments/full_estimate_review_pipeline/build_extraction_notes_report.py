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
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


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


def should_include_item(item: dict[str, Any], confidence_threshold: float) -> bool:
    if item.get("notes"):
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


def collect_section_items(
    section_code: str,
    section: dict[str, Any],
    confidence_threshold: float,
) -> tuple[list[dict[str, str]], list[str]]:
    collected: list[dict[str, str]] = []
    missing_codes: list[str] = []
    seen: set[tuple[str, str, str, str]] = set()
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
        if not should_include_item(item, confidence_threshold):
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
    lines = [
        "# Приложение к служебной записке: все notes из extraction JSON",
        "",
        f"Источник JSON: `{input_path}`",
        f"Проект: {project_name}",
        "",
        "Это техническое приложение собрано кодом из JSON, а не написано нейронкой.",
        "Сюда попадают: `needs_review`, все непустые `notes`, кандидаты, низкая уверенность и `missing`.",
        f"Порог низкой уверенности: ниже {confidence_threshold:.2f}.",
        "",
    ]

    warnings = extraction.get("extraction_warnings") or []
    if warnings:
        lines.extend(["## Общие предупреждения parser", ""])
        for warning in warnings:
            lines.append(f"- {short(warning, 500)}")
        lines.append("")

    sections = extraction.get("sections") or {}
    ordered_codes = [code for code in SECTION_ORDER if code in sections]
    ordered_codes.extend(sorted(code for code in sections if code not in set(ordered_codes)))

    total_items = 0
    for section_code in ordered_codes:
        section_items, missing_codes = collect_section_items(
            section_code,
            sections.get(section_code) or {},
            confidence_threshold,
        )
        if not section_items and not missing_codes:
            continue
        total_items += len(section_items) + len(missing_codes)
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
