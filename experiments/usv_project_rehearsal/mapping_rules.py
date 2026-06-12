from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from openpyxl import load_workbook


REPO_ROOT = Path(__file__).resolve().parents[2]
REVIEW_PACK_PATH = REPO_ROOT / "output/elena_parameter_review_pack_updated.xlsx"
RELEVANT_STATUSES = {"AUTO_PROJECT", "SUPPLIER_INPUT", "MANUAL_REQUIRED", "OPTIONAL_CONTROL"}
EXCLUDED_FROM_REVIEW_SHEET = {
    "AUTO_CALCULATED",
    "DEFAULT_VALUE",
    "MATERIAL_CATALOG",
    "PRICE_DATABASE",
    "DEPRECATED / LEGACY_ONLY",
    "DEPRECATED / OPTIONAL_OVERRIDE",
}

SECTION_CODES = {
    "Земляные работы": "earthworks",
    "Фундаментная плита": "foundation_slab",
    "Гидроизоляция": "waterproofing",
    "Несущие стены и перемычки": "load_bearing_walls_lintels",
    "Плита перекрытия 1-го этажа": "floor_slab_1",
    "Плита перекрытия 2-го этажа": "floor_slab_2",
    "Плоская кровля": "flat_roof",
    "Вентиляционные каналы Schiedel": "schiedel_vent_channels",
}


@dataclass(frozen=True)
class CandidateSpec:
    raw_label: str
    value: Any
    unit: str
    source_pdf: str
    expected_page: int
    page_title: str
    keywords: tuple[str, ...]
    confidence: str = "high"
    notes: str = ""


CURATED_CANDIDATES: list[CandidateSpec] = [
    CandidateSpec("Площадь котлована", 322.5, "м2", "usv_2026_kr1.pdf", 8, "План котлована", ("котлован", "322")),
    CandidateSpec("Геотекстиль", 320, "м2", "usv_2026_kr1.pdf", 8, "План котлована", ("геотекстиль", "320")),
    CandidateSpec("Песок", 96.6, "м3", "usv_2026_kr1.pdf", 8, "План котлована", ("песок", "96")),
    CandidateSpec("Профилированная мембрана PLANTER", 320, "м2", "usv_2026_kr1.pdf", 8, "План котлована", ("planter", "320")),
    CandidateSpec("Бетон фундаментной плиты", 81, "м3", "usv_2026_kr1.pdf", 10, "Спецификация к плану фундаментной плиты", ("бетон", "81")),
    CandidateSpec("ЭППС 100 мм торец фундаментной плиты", 1.75, "м3", "usv_2026_kr1.pdf", 10, "Спецификация к плану фундаментной плиты", ("эппс", "100", "1.75")),
    CandidateSpec("ЭППС 50 мм низ фундаментной плиты", 13.5, "м3", "usv_2026_kr1.pdf", 10, "Спецификация к плану фундаментной плиты", ("эппс", "50", "13.5")),
    CandidateSpec("Арматура ф10 А500С фундаментной плиты", 1747, "мп", "usv_2026_kr1.pdf", 10, "Спецификация к плану фундаментной плиты", ("ф10", "1747")),
    CandidateSpec("Арматура ф12 А500С фундаментной плиты", 5950, "мп", "usv_2026_kr1.pdf", 10, "Спецификация к плану фундаментной плиты", ("ф12", "5950")),
    CandidateSpec("Площадь опалубки фундаментной плиты", 23.58, "м2", "usv_2026_kr1.pdf", 10, "Спецификация к плану фундаментной плиты", ("опалуб", "23.58")),
    CandidateSpec("Площадь утепления торцов фундаментной плиты", 17.5, "м2", "usv_2026_kr1.pdf", 10, "Спецификация к плану фундаментной плиты", ("утеплен", "17.5")),
    CandidateSpec("Плотность армирования фундаментной плиты", 195, "кг/м3", "usv_2026_kr1.pdf", 10, "Спецификация к плану фундаментной плиты", ("плотность", "195")),
    CandidateSpec("ЭППС 100 мм термовставки", 0.4, "м3", "usv_2026_kr1.pdf", 11, "План термовставок", ("термовстав", "100", "0.4")),
    CandidateSpec("ЭППС 50 мм термовставки", 0.2, "м3", "usv_2026_kr1.pdf", 11, "План термовставок", ("термовстав", "50", "0.2")),
    CandidateSpec("Длина термовставок", 22, "мп", "usv_2026_kr1.pdf", 11, "План термовставок", ("термовстав", "22")),
    CandidateSpec("Количество термовставок", 34, "шт", "usv_2026_kr1.pdf", 11, "План термовставок", ("термовстав", "34")),
    CandidateSpec("Арматура ф16 А500С термовставок", 328, "кг", "usv_2026_kr1.pdf", 11, "План термовставок", ("ф16", "328")),
    CandidateSpec("Арматура ф12 А500С термовставок", 122, "кг", "usv_2026_kr1.pdf", 11, "План термовставок", ("ф12", "122")),
    CandidateSpec("Хомуты ф6 А240 термовставок", 35, "кг", "usv_2026_kr1.pdf", 11, "План термовставок", ("ф6", "35")),
    CandidateSpec("Отсечная гидроизоляция несущие стены", 39.555, "м2", "usv_2026_kr2.pdf", 6, "Схема расположения отсечной гидроизоляции", ("гидроизоляция", "39")),
    CandidateSpec("Отсечная гидроизоляция перегородки", 5.04, "м2", "usv_2026_kr2.pdf", 6, "Схема расположения отсечной гидроизоляции", ("гидроизоляция", "5.04")),
    CandidateSpec("Бетон перемычек В22.5", 0.24, "м3", "usv_2026_kr2.pdf", 16, "План перемычек 1-го этажа", ("перемыч", "0.24")),
    CandidateSpec("Арматура перемычек ф12 А500С", 103, "кг", "usv_2026_kr2.pdf", 16, "План перемычек 1-го этажа", ("ф12", "103")),
    CandidateSpec("Арматура перемычек ф6 А240", 20.4, "кг", "usv_2026_kr2.pdf", 16, "План перемычек 1-го этажа", ("ф6", "20.4")),
    CandidateSpec("Длина перемычек в U-блоках", 21.5, "мп", "usv_2026_kr2.pdf", 16, "План перемычек 1-го этажа", ("u", "21.5")),
    CandidateSpec("Бетон плиты +3.480", 38.22, "м3", "usv_2026_kr2.pdf", 22, "Спецификация к плите перекрытия на отм. +3.480", ("38.22", "бетон")),
    CandidateSpec("Бетон балок +3.480", 2.63, "м3", "usv_2026_kr2.pdf", 22, "Спецификация к плите перекрытия на отм. +3.480", ("2.63", "бал")),
    CandidateSpec("ЭППС 100 мм низ плиты +3.480", 50.4, "м3", "usv_2026_kr2.pdf", 22, "Спецификация к плите перекрытия на отм. +3.480", ("50.4", "эппс")),
    CandidateSpec("ЭППС 100 мм торец плиты +3.480", 26.6, "м2", "usv_2026_kr2.pdf", 22, "Спецификация к плите перекрытия на отм. +3.480", ("26.6", "эппс")),
    CandidateSpec("Арматура ф10 плиты +3.480", 6320, "мп", "usv_2026_kr2.pdf", 22, "Спецификация к плите перекрытия на отм. +3.480", ("ф10", "6320")),
    CandidateSpec("Арматура ф12 плиты +3.480", 47.3, "мп", "usv_2026_kr2.pdf", 22, "Спецификация к плите перекрытия на отм. +3.480", ("ф12", "47.3")),
    CandidateSpec("Арматура ф25 плиты +3.480", 42, "мп", "usv_2026_kr2.pdf", 22, "Спецификация к плите перекрытия на отм. +3.480", ("ф25", "42")),
    CandidateSpec("Арматура ф16 плиты +3.480", 32.52, "мп", "usv_2026_kr2.pdf", 22, "Спецификация к плите перекрытия на отм. +3.480", ("ф16", "32.52")),
    CandidateSpec("Арматура ф8 плиты +3.480", 17, "мп", "usv_2026_kr2.pdf", 22, "Спецификация к плите перекрытия на отм. +3.480", ("ф8", "17")),
    CandidateSpec("Арматура ф6 плиты +3.480", 67.56, "мп", "usv_2026_kr2.pdf", 22, "Спецификация к плите перекрытия на отм. +3.480", ("ф6", "67.56")),
    CandidateSpec("Бетон плиты +4.680", 16.5, "м3", "usv_2026_kr2.pdf", 25, "План плиты перекрытия на отм. +4.680", ("16.5", "бетон")),
    CandidateSpec("ЭППС 100 мм торец плиты +4.680", 7.4, "м2", "usv_2026_kr2.pdf", 25, "План плиты перекрытия на отм. +4.680", ("7.4", "эппс")),
    CandidateSpec("Арматура ф10 плиты +4.680", 2431, "кг или мп", "usv_2026_kr2.pdf", 25, "План плиты перекрытия на отм. +4.680", ("ф10", "2431"), "low", "Единица неясна в PDF; требуется проверка."),
    CandidateSpec("Арматура ф12 плиты +4.680", 24.77, "кг или мп", "usv_2026_kr2.pdf", 25, "План плиты перекрытия на отм. +4.680", ("ф12", "24.77"), "low", "Единица неясна в PDF; требуется проверка."),
    CandidateSpec("Площадь опалубки плиты +4.680", 212.35, "м2", "usv_2026_kr2.pdf", 25, "План плиты перекрытия на отм. +4.680", ("опалуб", "212.35")),
    CandidateSpec("Плотность армирования плиты +4.680", 22, "мп/м2", "usv_2026_kr2.pdf", 25, "План плиты перекрытия на отм. +4.680", ("плотность", "22")),
    CandidateSpec("Пароизоляционный слой кровли", 294, "м2", "usv_2026_kr2.pdf", 29, "Спецификация к плану кровли", ("пароизоля", "294")),
    CandidateSpec("ЭППС ТехноНИКОЛЬ CARBON PROF кровли", 58.8, "м3", "usv_2026_kr2.pdf", 29, "Спецификация к плану кровли", ("carbon", "58.8")),
    CandidateSpec("Стеклохолст кровли", 294, "м2", "usv_2026_kr2.pdf", 29, "Спецификация к плану кровли", ("стеклохолст", "294")),
    CandidateSpec("Разуклонка кровли", "уточнить у монтажной организации", "", "usv_2026_kr2.pdf", 29, "Спецификация к плану кровли", ("разуклон", "уточнить"), "medium", "SUPPLIER_INPUT: нужна раскладка/уточнение монтажной организации."),
    CandidateSpec("Мембрана LOGICROOF", 398.4, "м2", "usv_2026_kr2.pdf", 29, "Спецификация к плану кровли", ("logicroof", "398.4")),
    CandidateSpec("Внутренние воронки", 3, "шт", "usv_2026_kr2.pdf", 29, "Спецификация к плану кровли", ("ворон", "3")),
    CandidateSpec("Парапетные воронки", 2, "шт", "usv_2026_kr2.pdf", 29, "Спецификация к плану кровли", ("ворон", "2")),
    CandidateSpec("Доска 45х195 6 м", 18, "шт", "usv_2026_kr2.pdf", 29, "Спецификация к плану кровли", ("45х195", "18")),
    CandidateSpec("Монолитный поликарбонат", 25.28, "м2", "usv_2026_kr2.pdf", 29, "Спецификация к плану кровли", ("поликарбонат", "25.28")),
    CandidateSpec("Длина примыкания к парапетам", 103.35, "мп", "usv_2026_kr2.pdf", 29, "Спецификация к плану кровли", ("парапет", "103.35")),
    CandidateSpec("Длина примыкания к стенам", 24.65, "мп", "usv_2026_kr2.pdf", 29, "Спецификация к плану кровли", ("стен", "24.65")),
    CandidateSpec("Площадь кровли на отм. +3.480", 212.35, "м2", "usv_2026_kr2.pdf", 29, "Спецификация к плану кровли", ("3.480", "212.35")),
    CandidateSpec("Площадь кровли на отм. +4.680", 82, "м2", "usv_2026_kr2.pdf", 29, "Спецификация к плану кровли", ("4.680", "82")),
    CandidateSpec("Schiedel VENT 2", 24, "шт", "usv_2026_kr2.pdf", 32, "Разрез по вентканалам", ("vent 2", "24")),
    CandidateSpec("Schiedel VENT 3", 8, "шт", "usv_2026_kr2.pdf", 32, "Разрез по вентканалам", ("vent 3", "8")),
    CandidateSpec("Газобетонный блок 600х150х250 для обкладки", 1.72, "м3", "usv_2026_kr2.pdf", 32, "Разрез по вентканалам", ("600х150х250", "1.72")),
    CandidateSpec("Общая длина кладки вентканалов", 6.52, "мп", "usv_2026_kr2.pdf", 32, "Разрез по вентканалам", ("кладк", "6.52")),
]


EXACT_PARAMETER_TO_CANDIDATE = {
    ("Земляные работы", "pit_area_m2"): "Площадь котлована",
    ("Земляные работы", "geotextile_laying_area_m2"): "Геотекстиль",
    ("Земляные работы", "trench_volume_m3"): "План котлована / траншеи",
    ("Фундаментная плита", "thermal_insert_50_length_m"): "Длина термовставок",
    ("Фундаментная плита", "thermal_insert_100_length_m"): "Длина термовставок",
    ("Фундаментная плита", "thermal_insert_50_material_spec_qty"): "ЭППС 50 мм термовставки",
    ("Фундаментная плита", "thermal_insert_100_material_spec_qty"): "ЭППС 100 мм термовставки",
    ("Гидроизоляция", "cutoff_waterproofing_load_bearing_walls_area_m2"): "Отсечная гидроизоляция несущие стены",
    ("Гидроизоляция", "cutoff_waterproofing_partitions_area_m2"): "Отсечная гидроизоляция перегородки",
    ("Несущие стены и перемычки", "cutoff_waterproofing_load_bearing_walls_area_m2"): "Отсечная гидроизоляция несущие стены",
    ("Несущие стены и перемычки", "cutoff_waterproofing_partitions_area_m2"): "Отсечная гидроизоляция перегородки",
    ("Несущие стены и перемычки", "lintel_total_length_m"): "Длина перемычек в U-блоках",
    ("Несущие стены и перемычки", "vent_chimney_gas_block_spec_volume_m3"): "Газобетонный блок 600х150х250 для обкладки",
    ("Плита перекрытия 1-го этажа", "geometry.total_concrete_volume_from_spec_m3"): "Бетон плиты +3.480",
    ("Плита перекрытия 1-го этажа", "insulation.total_eps_volume_from_spec_m3"): "ЭППС 100 мм низ плиты +3.480",
    ("Плита перекрытия 2-го этажа", "main_formwork_area_m2"): "Площадь опалубки плиты +4.680",
    ("Плита перекрытия 2-го этажа", "rebar_items[*].spec_length_m ф10"): "Арматура ф10 плиты +4.680",
    ("Плита перекрытия 2-го этажа", "rebar_items[*].spec_length_m ф12"): "Арматура ф12 плиты +4.680",
    ("Плоская кровля", "roof_area_level_1_m2"): "Площадь кровли на отм. +3.480",
    ("Плоская кровля", "roof_area_level_2_m2"): "Площадь кровли на отм. +4.680",
    ("Плоская кровля", "roof_area_total_m2"): "Площадь кровли на отм. +3.480",
    ("Плоская кровля", "parapet_and_abutment_total_length_m"): "Длина примыкания к парапетам",
    ("Вентиляционные каналы Schiedel", "vent_channel_2_count"): "Schiedel VENT 2",
    ("Вентиляционные каналы Schiedel", "schiedel_masonry_total_length_m"): "Общая длина кладки вентканалов",
}


EXTRA_REQUIREMENTS = [
    {
        "section_name": "Плита перекрытия 2-го этажа",
        "label": "Арматура плиты 2-го этажа ф10: длина из спецификации",
        "calculator_input_key": "rebar_items[*].spec_length_m ф10",
        "recommended_source_status": "AUTO_PROJECT",
        "elena_decision": "AUTO_PROJECT",
        "source_of_truth": "Project PDF/specification/review card",
        "visible_to_elena": "да",
        "risk_level": "high",
        "reason": "Production-режим арматуры плиты 2-го этажа считает закупку от spec_length_m; в PDF единица для ф10 неочевидна, поэтому значение нужно вынести на проверку.",
        "user_comment": "Добавлено rehearsal-аудитом: после рефактора калькулятора это обязательный production-параметр.",
    },
    {
        "section_name": "Плита перекрытия 2-го этажа",
        "label": "Арматура плиты 2-го этажа ф12: длина из спецификации",
        "calculator_input_key": "rebar_items[*].spec_length_m ф12",
        "recommended_source_status": "AUTO_PROJECT",
        "elena_decision": "AUTO_PROJECT",
        "source_of_truth": "Project PDF/specification/review card",
        "visible_to_elena": "да",
        "risk_level": "high",
        "reason": "Production-режим арматуры плиты 2-го этажа считает закупку от spec_length_m; в PDF единица для ф12 неочевидна, поэтому значение нужно вынести на проверку.",
        "user_comment": "Добавлено rehearsal-аудитом: после рефактора калькулятора это обязательный production-параметр.",
    },
]


def normalize_text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def load_parameter_registry(path: Path = REVIEW_PACK_PATH) -> list[dict[str, Any]]:
    wb = load_workbook(path, read_only=True, data_only=True)
    ws = wb["К_обсуждению_с_Еленой"]
    rows = list(ws.iter_rows(values_only=True))
    headers = [normalize_text(item) for item in rows[0]]
    result = []
    for row in rows[1:]:
        item = dict(zip(headers, row))
        section = normalize_text(item.get("section_name"))
        key = normalize_text(item.get("calculator_input_key"))
        if not section or not key:
            continue
        decision = normalize_text(item.get("elena_decision")) or normalize_text(item.get("recommended_source_status"))
        item["required_status"] = decision
        item["status_from_recommended_fallback"] = not bool(normalize_text(item.get("elena_decision")))
        if decision in RELEVANT_STATUSES:
            result.append(item)
    for item in EXTRA_REQUIREMENTS:
        extra = dict(item)
        extra["required_status"] = normalize_text(extra.get("elena_decision")) or normalize_text(extra.get("recommended_source_status"))
        extra["status_from_recommended_fallback"] = False
        result.append(extra)
    return result


def candidate_lookup(candidates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result = {}
    for candidate in candidates:
        result[normalize_text(candidate.get("raw_label"))] = candidate
    return result


def infer_candidate_label(parameter: dict[str, Any]) -> str | None:
    section = normalize_text(parameter.get("section_name"))
    key = normalize_text(parameter.get("calculator_input_key"))
    exact = EXACT_PARAMETER_TO_CANDIDATE.get((section, key))
    if exact:
        return exact
    if "supplier_required_volume" in key:
        if "eps50" in key:
            return "ЭППС ТехноНИКОЛЬ CARBON PROF кровли"
        match = re.search(r"slope_plate_([abjk])", key)
        if match:
            return "Разуклонка кровли"
    return None


def map_parameters(registry: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_label = candidate_lookup(candidates)
    mapped = []
    for parameter in registry:
        section = normalize_text(parameter.get("section_name"))
        key = normalize_text(parameter.get("calculator_input_key"))
        required_status = normalize_text(parameter.get("required_status"))
        candidate_label = infer_candidate_label(parameter)
        candidate = by_label.get(candidate_label or "")

        if required_status == "SUPPLIER_INPUT":
            found_status = "supplier_required"
        elif required_status == "MANUAL_REQUIRED":
            found_status = "manual_required"
        elif candidate:
            found_status = "low_confidence" if candidate.get("confidence") == "low" else "found"
        else:
            found_status = "missing"

        needs_review = found_status in {"missing", "conflict", "low_confidence", "supplier_required", "manual_required"}
        if required_status == "AUTO_PROJECT" and found_status == "found":
            needs_review = True
        mapped.append(
            {
                "section_name": section,
                "section_code": SECTION_CODES.get(section, ""),
                "calculator_input_key": key,
                "label": normalize_text(parameter.get("label")),
                "what_it_means": normalize_text(parameter.get("Зачем нужен параметр") or parameter.get("reason")),
                "required_status": required_status,
                "recommended_source_status": normalize_text(parameter.get("recommended_source_status")),
                "source_of_truth": normalize_text(parameter.get("source_of_truth")),
                "visible_to_elena": normalize_text(parameter.get("visible_to_elena")),
                "risk_level": normalize_text(parameter.get("risk_level")),
                "reason": normalize_text(parameter.get("reason")),
                "user_comment": normalize_text(parameter.get("user_comment")),
                "found_status": found_status,
                "value_from_pdf": candidate.get("raw_value") if candidate else None,
                "unit": candidate.get("unit") if candidate else "",
                "source_pdf": candidate.get("source_pdf") if candidate else "",
                "page": candidate.get("page") if candidate else None,
                "page_title": candidate.get("page_title") if candidate else "",
                "source_fragment": candidate.get("raw_context") if candidate else "",
                "confidence": candidate.get("confidence") if candidate else "",
                "needs_elena_review": needs_review,
                "notes": candidate.get("notes") if candidate else "",
                "status_from_recommended_fallback": bool(parameter.get("status_from_recommended_fallback")),
            }
        )
    return mapped
