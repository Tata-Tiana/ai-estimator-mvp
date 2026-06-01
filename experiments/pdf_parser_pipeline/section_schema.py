"""Section schema for the PDF parser pipeline MVP.

The schema describes what calculators need. Parser findings are only used to
pre-fill values where a source can be shown.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]


SECTION_DEFS: list[dict[str, Any]] = [
    {
        "section_code": "earthworks",
        "section_name": "Земляные работы",
        "input_path": "experiments/earthworks_calculator/cases/usv_yusupovo_village/input.json",
        "source_hints": [{"source_id": "kr1_foundation", "pages": [8], "titles": ["План котлована"]}],
    },
    {
        "section_code": "foundation_slab",
        "section_name": "Фундаментная плита",
        "input_path": "experiments/foundation_slab_calculator/cases/test_foundation_slab/input.json",
        "source_hints": [
            {"source_id": "kr1_foundation", "pages": [6], "titles": ["Основное сечение по фундаменту"]},
            {"source_id": "kr1_foundation", "pages": [8], "titles": ["План котлована"]},
            {"source_id": "kr1_foundation", "pages": [9], "titles": ["План фундаментной плиты"]},
            {"source_id": "kr1_foundation", "pages": [10], "titles": ["План термовставок"]},
        ],
    },
    {
        "section_code": "waterproofing",
        "section_name": "Гидроизоляция",
        "input_path": "experiments/waterproofing_calculator/cases/test_waterproofing_foundation_slab/input.json",
        "source_hints": [
            {"source_id": "kr1_foundation", "pages": [3], "titles": ["Пояснительная записка"]},
            {"source_id": "kr1_foundation", "pages": [6], "titles": ["Основное сечение по фундаменту"]},
            {"source_id": "kr1_foundation", "pages": [9], "titles": ["План фундаментной плиты"]},
        ],
    },
    {
        "section_code": "load_bearing_walls_lintels",
        "section_name": "Несущие стены и перемычки",
        "input_path": "experiments/load_bearing_walls_lintels_calculator/cases/test_load_bearing_walls_lintels/input.json",
        "source_hints": [
            {"source_id": "kr2_above_zero", "pages": [3], "titles": ["Пояснительная записка"]},
            {"source_id": "kr2_above_zero", "pages": [13], "titles": ["Кладочный план"]},
            {"source_id": "kr2_above_zero", "pages": [15], "titles": ["План перемычек"]},
        ],
    },
    {
        "section_code": "floor_slab_1",
        "section_name": "Плита перекрытия 1-го этажа",
        "input_path": "experiments/floor_slab_1_calculator/cases/test_floor_slab_1/input.json",
        "source_hints": [
            {"source_id": "kr2_above_zero", "pages": [20], "titles": ["План плиты перекрытия на отм. +3.480"]},
            {"source_id": "kr2_above_zero", "pages": [21], "titles": ["Спецификация к плите перекрытия на отм. +3.480"]},
            {"source_id": "kr2_above_zero", "pages": [22, 23], "titles": ["Дополнительное армирование"]},
        ],
    },
    {
        "section_code": "floor_slab_2",
        "section_name": "Плита перекрытия 2-го этажа",
        "input_path": "experiments/floor_slab_2_calculator/cases/test_floor_slab_2/input.json",
        "source_hints": [
            {"source_id": "kr2_above_zero", "pages": [24], "titles": ["План плиты перекрытия на отм. +3.680"]},
            {"source_id": "kr2_above_zero", "pages": [25, 26], "titles": ["Дополнительное армирование"]},
        ],
    },
    {
        "section_code": "flat_roof",
        "section_name": "Плоская кровля",
        "input_path": "experiments/flat_roof_calculator/cases/test_flat_roof_usv/input.json",
        "source_hints": [
            {"source_id": "kr2_above_zero", "pages": [27], "titles": ["План кровли"]},
            {"source_id": "kr2_above_zero", "pages": [28], "titles": ["Спецификация к плану кровли"]},
            {"source_id": "kr2_above_zero", "pages": [29, 30], "titles": ["Узлы кровли"]},
            {"source_id": "ar_architecture", "pages": [], "titles": ["Архитектура"]},
        ],
    },
    {
        "section_code": "schiedel_vent_channels",
        "section_name": "Вентиляционные каналы Schiedel",
        "input_path": "experiments/schiedel_vent_channels_calculator/cases/test_schiedel_vent_channels_usv/input.json",
        "source_hints": [{"source_id": "kr2_above_zero", "pages": [31], "titles": ["Разрез по вентканалам"]}],
    },
]


def p(
    parameter_code: str,
    calculator_input_key: str,
    label: str,
    unit: str,
    input_type: str,
    required: bool,
    search_hints: list[str],
    regex_patterns: list[str],
    default_value: Any = None,
    description: str = "",
) -> dict[str, Any]:
    return {
        "parameter_code": parameter_code,
        "calculator_input_key": calculator_input_key,
        "label": label,
        "unit": unit,
        "input_type": input_type,
        "required": required,
        "default_value": default_value,
        "search_hints": search_hints,
        "regex_patterns": regex_patterns,
        "description": description or label,
    }


EXPLICIT_PARAMETERS: dict[str, list[dict[str, Any]]] = {
    "earthworks": [
        p("sand_volume", "sand_base_volume_m3", "Песок", "м3", "parsed", True, ["Песок"], [r"Песок.*?Купл=0,95\s*(?P<value>\d+[,.]\d+)"]),
        p("geotextile_area", "geotextile_area_m2", "Геотекстиль", "м2", "parsed", True, ["Геотекстиль"], [r"Геотекстиль.*?(?P<value>\d+[,.]?\d*)\s*м2"]),
        p("planter_membrane_area", "foundation_slab.membrane_area_m2", "Профилированная мембрана PLANTER", "м2", "parsed", False, ["PLANTER"], [r"PLANTER\s*(?P<value>\d+[,.]?\d*)\s*м2"]),
    ],
    "foundation_slab": [
        p("foundation_type", "control.foundation_type", "Тип фундамента", "-", "control_only", False, ["Ж/б плита фундамента"], [r"(?P<value>Ж/б плита фундамента)\s*300\s*мм"]),
        p("foundation_slab_thickness", "control.foundation_slab_thickness", "Толщина фундаментной плиты", "мм", "control_only", False, ["Ж/б плита фундамента"], [r"Ж/б плита фундамента\s*(?P<value>\d+)\s*мм"]),
        p("concrete_class", "control.concrete_class", "Класс бетона", "-", "control_only", False, ["Бетон"], [r"Бетон\s*(?P<value>В\s*22[.,]?\s*5\.?\s*W6\s*F150\s*П4)"]),
        p("concrete_project_volume", "concrete_project_volume_m3", "Проектный объем бетона фундаментной плиты", "м3", "parsed", True, ["Бетон", "м3"], [r"Бетон\s*В\s*22.*?(?P<value>\d+[,.]?\d*)\s*м3"]),
        p("eps_50_under_slab_volume", "eps50_under_slab_volume_m3", "ЭППС 50 мм, низ плиты", "м3", "parsed", True, ["ЭППС 50 мм", "низ"], [r"ЭППС\s*50\s*мм\s*\(низ\)\s*(?P<value>\d+[,.]\d+)"]),
        p("eps_100_edge_volume", "eps100_edge_volume_m3", "ЭППС 100 мм, торец", "м3", "parsed", False, ["ЭППС 100 мм", "торец"], [r"ЭППС\s*100\s*мм\s*\(торец\)\s*(?P<value>\d+[,.]\d+)"]),
        p("eps_150_thermal_insert_volume", "thermal_insert_eps150_volume_m3", "ЭППС 150 мм, термовставки", "м3", "manual", False, ["ЭППС 150 мм"], [r"ЭППС\s*150\s*мм\s*(?P<value>\d+[,.]\d+)"]),
        p("rebar_a500c_d12_main_grid_weight", "rebar_items[1].weight_parts_kg", "Арматура A500C d12, сетка фундаментной плиты", "кг", "parsed", True, ["ф12 А500С", "сетка"], [r"ф12\s*А500С\s*\(сетка\)\s*(?P<value>\d+[,.]?\d*)\s*кг"]),
        p("rebar_a500c_d12_thermal_insert_weight", "rebar_items[1].weight_parts_kg", "Арматура A500C d12, сетка термовставок", "кг", "parsed", True, ["ф12 А500С", "термовстав"], [r"ф12\s*А500С\s*\(ар-я сетка\)\s*кг\s*(?P<value>\d+[,.]?\d*)"]),
        p("rebar_a500c_d10_weight", "rebar_items[2].weight_parts_kg", "Арматура A500C d10", "кг", "parsed", True, ["ф10 А500С"], [r"ф10\s*А500С.*?(?P<value>\d+[,.]?\d*)\s*кг"]),
        p("rebar_a500c_d16_thermal_insert_weight", "rebar_items[0].weight_parts_kg", "Арматура A500C d16 для термовставок", "кг", "parsed", True, ["ф16 А500С"], [r"ф16\s*А500С.*?кг\s*(?P<value>\d+[,.]?\d*)"]),
        p("rebar_a240_d6_thermal_insert_weight", "rebar_items[3].weight_parts_kg", "Арматура A240 d6 для термовставок", "кг", "parsed", True, ["ф6 А240"], [r"(?P<value>\d+[,.]?\d*)\s*ф6\s*А240|ф6\s*А240.*?кг\s*(?P<value2>\d+[,.]?\d*)"]),
        p("sand_volume", "earthworks.sand_base_volume_m3", "Песок", "м3", "parsed", True, ["Песок"], [r"Песок.*?Купл=0,95\s*(?P<value>\d+[,.]\d+)"]),
        p("geotextile_area", "earthworks.geotextile_area_m2", "Геотекстиль", "м2", "parsed", True, ["Геотекстиль"], [r"Геотекстиль.*?(?P<value>\d+[,.]?\d*)\s*м2"]),
        p("planter_membrane_area", "membrane_area_m2", "Профилированная мембрана PLANTER", "м2", "parsed", True, ["PLANTER"], [r"PLANTER\s*(?P<value>\d+[,.]?\d*)\s*м2"]),
        p("foundation_section_levels", "control.foundation_section_levels", "Отметки / уровни для проверки сечения", "отм.", "control_only", False, ["-0,200", "-0,500"], [r"(?P<value>0,000.*?-0,500.*?-0,200)"]),
    ],
    "waterproofing": [
        p("waterproofing_type", "control.waterproofing_type", "Тип вертикальной гидроизоляции", "-", "control_only", False, ["битумной мастики в 2 слоя"], [r"(?P<value>битумной мастики в 2 слоя)"]),
        p("eps_100_edge_volume", "eps100_wall_volume_m3", "ЭППС 100 мм, торец/вертикальное утепление", "м3", "parsed", True, ["ЭППС 100 мм", "торец"], [r"ЭППС\s*100\s*мм\s*\(торец\)\s*(?P<value>\d+[,.]\d+)"]),
    ],
    "load_bearing_walls_lintels": [
        p("gas_block_d400_volume", "main_wall_gas_block_400_spec_volume_m3", "Газобетонный блок 600х400х250", "м3", "parsed", True, ["Газобетонный блок 600х400х250"], [r"Газобетонный блок\s*600х400х250\s*(?P<value>\d+[,.]\d+)\s*м3"]),
        p("gas_block_d500_250_volume", "main_wall_gas_block_250_spec_volume_m3", "Газобетонный блок 600х250х250", "м3", "parsed", True, ["Газобетонный блок 600х250х250"], [r"Газобетонный блок\s*600х250х250\s*Газобетонный блок\s*600х150х250\s*(?P<value>\d+[,.]\d+)"]),
        p("gas_block_d500_150_volume", "vent_chimney_gas_block_spec_volume_m3", "Газобетонный блок 600х150х250", "м3", "parsed", False, ["Газобетонный блок 600х150х250"], [r"Газобетонный блок\s*600х250х250\s*Газобетонный блок\s*600х150х250\s*\d+[,.]\d+\s*(?P<value>\d+[,.]\d+)"]),
        p("masonry_rebar_a500_d10_weight", "rebar_a500_d10_source_weight_kg", "Арматура ф10 А500С для кладки", "кг", "parsed", True, ["ф10 А500С", "армирование кладки"], [r"ф10\s*А500С\s*\(армирование кладки\)\s*(?P<value>\d+[,.]?\d*)\s*кг"]),
        p("lintel_concrete_volume", "lintel_concrete_volume_m3", "Бетон перемычек", "м3", "parsed", True, ["Бетон В-22,5"], [r"Бетон\s*В-22,5\s*(?P<value>\d+[,.]\d+)\s*м3"]),
        p("lintel_rebar_a500_d12_weight", "lintel_rebar_items[0].weight_kg", "Арматура ф12 А500С для перемычек", "кг", "parsed", True, ["ф12 А500С"], [r"ф12\s*А500С\s*кг\s*(?P<value>\d+[,.]?\d*)"]),
        p("lintel_rebar_a240_d6_weight", "lintel_rebar_items[1].weight_kg", "Арматура ф6 А240 для перемычек", "кг", "parsed", True, ["ф6 А240"], [r"ф6\s*А240\s*\(хомуты\)\s*(?P<value>\d+[,.]\d*)\s*кг"]),
    ],
    "floor_slab_1": [
        p("floor_slab_1_concrete_volume", "total_concrete_volume_from_spec_m3", "Бетон плиты перекрытия +3.480", "м3", "parsed", True, ["40,53 м3"], [r"(?P<value>40[,.]53)\s*м3"]),
        p("floor_slab_1_eps100_volume", "total_eps_volume_from_spec_m3", "ЭППС 100 мм торец и низ плиты", "м3", "parsed", True, ["ЭППС 100 мм"], [r"ЭППС\s*100\s*мм.*?(?P<value>\d+[,.]\d+)\s*ГОСТ"]),
        p("floor_slab_1_rebar_a500_d10_weight", "rebar_items[3].source_weight_parts_kg", "Арматура ф10 А500С", "кг", "parsed", True, ["ф10 А500С"], [r"ф10\s*А500С.*?кг\s*(?P<value>\d+[,.]?\d*)"]),
        p("floor_slab_1_rebar_a500_d12_weight", "rebar_items[2].source_weight_kg", "Арматура ф12 А500С", "кг", "parsed", True, ["ф12 А500С"], [r"ф12\s*А500С.*?(?P<value>\d+[,.]?\d*)\s*кг"]),
        p("floor_slab_1_rebar_a500_d25_weight", "rebar_items[0].source_weight_kg", "Арматура ф25 А500С", "кг", "parsed", True, ["ф25 А500С"], [r"ф25\s*А500С.*?ф16\s*А500С.*?ф6\s*А240.*?(?P<value>162)\s+52[,.]04\s+15"]),
        p("floor_slab_1_rebar_a500_d16_weight", "rebar_items[1].source_weight_parts_kg", "Арматура ф16 А500С", "кг", "parsed", True, ["ф16 А500С"], [r"ф25\s*А500С.*?ф16\s*А500С.*?ф6\s*А240.*?162\s+(?P<value>52[,.]04)\s+15"]),
        p("floor_slab_1_rebar_a240_d6_weight", "rebar_items[5].source_weight_parts_kg", "Арматура ф6 А240", "кг", "parsed", True, ["ф6 А240"], [r"ф25\s*А500С.*?ф16\s*А500С.*?ф6\s*А240.*?162\s+52[,.]04\s+(?P<value>15)"]),
        p("floor_slab_1_rebar_a240_d8_weight", "rebar_items[4].source_weight_kg", "Арматура ф8 А240", "кг", "parsed", True, ["ф8 А240"], [r"ф8\s*А240.*?(?P<value>\d+[,.]?\d*)\s*кг"]),
    ],
    "floor_slab_2": [
        p("floor_slab_2_concrete_volume", "concrete_placing_volume_m3", "Бетон плиты перекрытия +3.680/+4.680", "м3", "parsed", True, ["16,5 м3"], [r"(?P<value>16[,.]5)\s*м3"]),
        p("floor_slab_2_eps100_edge_volume", "eps100_edge_volume_m3", "ЭППС 100 мм торец плиты", "м3", "parsed", False, ["ЭППС 100 мм"], [r"ЭППС\s*100\s*мм\s*\(торец плиты\)\s*(?P<value>\d+[,.]\d+)"]),
        p("floor_slab_2_rebar_a500_d10_weight_main", "rebar_items[2].source_weight_kg", "Арматура ф10 А500С, основная", "кг", "parsed", True, ["ф10 А500С"], [r"ф10\s*А500С.*?кг\s*(?P<value>1500)"]),
        p("floor_slab_2_rebar_a500_d10_weight_extra_1", "rebar_items[2].source_weight_kg", "Арматура ф10 А500С, доп. лист 25", "кг", "parsed", True, ["ф10 А500С"], [r"ф10\s*А500С\s*кг\s*(?P<value>42[,.]57)"]),
        p("floor_slab_2_rebar_a500_d10_weight_extra_2", "rebar_items[2].source_weight_kg", "Арматура ф10 А500С, доп. лист 26", "кг", "parsed", True, ["ф10 А500С"], [r"кг\s*(?P<value>35[,.]1)\s*ф10\s*А500С"]),
        p("floor_slab_2_rebar_a500_d12_weight", "rebar_items[1].source_weight_kg", "Арматура ф12 А500С", "кг", "parsed", True, ["ф12 А500С"], [r"ф12\s*А500С.*?(?P<value>22)\s*кг"]),
        p("floor_slab_2_rebar_a500_d16_weight", "rebar_items[0].source_weight_kg", "Арматура ф16 А500С", "кг", "parsed", True, ["ф16 А500С"], [r"ф16\s*А500С\s*кг\s*(?P<value>142[,.]4)"]),
    ],
    "flat_roof": [
        p("project_spec_roof_area", "project_spec_roof_area_m2", "Площадь кровли по спецификации", "м2", "parsed", False, ["Пароизоляционный слой"], [r"Пароизоляционный слой.*?(?P<value>294)\s*м3"]),
        p("roof_eps_main_volume", "eps100_supplier_volume_control_m3", "ЭППС кровли по спецификации", "м3", "parsed", False, ["ЭППС ТехноНИКОЛЬ"], [r"ЭППС\s*ТехноНИКОЛЬ.*?(?P<value>29[,.]4)"]),
        p("roof_pvc_membrane_area", "pvc_membrane_area_control_m2", "Полимерная мембрана LOGICROOF V-RP", "м2", "parsed", False, ["LOGICROOF"], [r"Полимерная мембрана\s*LOGICROOF\s*V-RP\s*(?P<value>\d+[,.]\d+)"]),
        p("roof_internal_drains_count", "internal_roof_drains_count", "Воронки внутреннего водостока", "шт", "parsed", True, ["внутреннего водостока"], [r"воронкой\s*внутреннего водостока\s*шт\s*(?P<value>\d+)"]),
        p("roof_parapet_drains_count", "parapet_roof_drains_count", "Парапетные воронки", "шт", "parsed", True, ["Парапетная воронка"], [r"Парапетная воронка\s*шт\s*(?P<value>\d+)"]),
        p("roof_geotextile_material", "control.roof_geotextile_material", "Геотекстиль/стеклохолст кровли", "-", "control_only", False, ["Стеклохолст", "Геотекстиль"], [r"(?P<value>Стеклохолст\s*ТЕХНОНИКОЛЬ\s*100\s*г/м2)"]),
    ],
    "schiedel_vent_channels": [
        p("schiedel_vent_channel_2x_count", "schiedel_vent_channel_2x_count", "Вентиляционный канал Schiedel VENT 2", "шт", "manual", True, ["VENT 2"], [r"VENT\s*2\s*\(360х250\s*мм\)\s*(?P<value>\d+)\s*шт"]),
        p("schiedel_vent_channel_3x_count", "schiedel_vent_channel_3x_count", "Вентиляционный канал Schiedel VENT 3", "шт", "manual", True, ["VENT 3"], [r"VENT\s*3\s*\(520х250\s*мм\)\s*(?P<value>\d+)\s*шт"]),
        p("vent_channel_levels_control", "control.vent_channel_levels", "Отметки вентканалов", "отм.", "control_only", False, ["-0,200", "4,940"], [r"(?P<value>-0,200.*?4,940)"]),
        p("schiedel_gas_block_150_volume", "load_bearing_walls_lintels.vent_chimney_gas_block_spec_volume_m3", "Газобетонный блок 600х150х250 для вентканалов", "м3", "parsed", False, ["Газобетонный блок 600х150х250"], [r"Газобетонный блок\s*600х150х250\s*(?P<value>\d+[,.]\d+)\s*м3"]),
    ],
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten_input(value: Any, prefix: str = "") -> Iterable[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "pricing":
                continue
            yield from flatten_input(child, f"{prefix}.{key}" if prefix else key)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from flatten_input(child, f"{prefix}[{index}]")
    else:
        yield prefix, value


def parameter_code_from_key(section_code: str, key: str) -> str:
    slug = re.sub(r"\[(\d+)\]", r"_\1", key)
    slug = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ]+", "_", slug).strip("_").lower()
    return f"{section_code}_{slug}"


def infer_input_type(key: str, value: Any) -> str:
    lowered = key.lower()
    if "control" in lowered or lowered.endswith("project_name") or lowered.startswith("case_meta"):
        return "control_only"
    if any(token in lowered for token in ("unit_price", "work_rate", "rate_per", "_price", "_amount", "total_raw")):
        return "price"
    if any(token in lowered for token in ("coeff", "waste", "thickness", "pack_volume", "rod_length", "kg_per", "coverage", "capacity", "round_step", "factor")):
        return "calculation_constant"
    if any(token in lowered for token in ("manual", "override", "trips", "shifts", "count", "enabled", "method", "strategy")):
        return "manual"
    if any(token in lowered for token in ("area", "volume", "length", "perimeter", "height", "width", "weight", "roof", "wall", "slab", "rebar", "concrete", "sand", "geotextile", "membrane")):
        return "parsed"
    return "manual"


def infer_unit(key: str, value: Any) -> str:
    leaf = re.sub(r"\[\d+\]", "", key.split(".")[-1])
    for suffix, unit in [
        ("_m2", "м2"),
        ("_m3", "м3"),
        ("_kg", "кг"),
        ("_m", "м"),
        ("_mm", "мм"),
        ("_count", "шт"),
        ("_trips", "рейс"),
        ("_shifts", "смена"),
    ]:
        if leaf.endswith(suffix):
            return unit
    if "price" in leaf or "rate" in leaf or "amount" in leaf:
        return "руб."
    if isinstance(value, bool):
        return "bool"
    return "-"


def label_from_key(key: str) -> str:
    leaf = re.sub(r"\[\d+\]", "", key.split(".")[-1])
    return leaf.replace("_", " ")


def get_section_schema(repo_root: Path | None = None) -> list[dict[str, Any]]:
    root = repo_root or REPO_ROOT
    sections: list[dict[str, Any]] = []

    for section in SECTION_DEFS:
        params: list[dict[str, Any]] = []
        seen_keys: set[str] = set()
        for item in EXPLICIT_PARAMETERS.get(section["section_code"], []):
            params.append(dict(item))
            seen_keys.add(item["calculator_input_key"])

        input_path = root / section["input_path"]
        if input_path.exists():
            input_data = load_json(input_path)
            for key, value in flatten_input(input_data):
                if key in seen_keys:
                    continue
                input_type = infer_input_type(key, value)
                params.append({
                    "parameter_code": parameter_code_from_key(section["section_code"], key),
                    "calculator_input_key": key,
                    "label": label_from_key(key),
                    "unit": infer_unit(key, value),
                    "input_type": input_type,
                    "required": input_type != "control_only",
                    "default_value": value if input_type in {"price", "calculation_constant"} else None,
                    "search_hints": [],
                    "regex_patterns": [],
                    "description": f"Параметр из input.json калькулятора: {key}",
                })

        sections.append({
            "section_code": section["section_code"],
            "section_name": section["section_name"],
            "source_hints": section["source_hints"],
            "parameters": params,
        })
    return sections
