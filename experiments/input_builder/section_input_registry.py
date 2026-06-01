"""Registry of calculator input templates for the MVP input builder."""

from __future__ import annotations

from typing import Any


SECTION_INPUT_REGISTRY: dict[str, dict[str, Any]] = {
    "earthworks": {
        "section_name": "Земляные работы",
        "calculator_case_template_input_path": "experiments/earthworks_calculator/cases/usv_yusupovo_village/input.json",
        "generated_input_filename": "earthworks_input.json",
    },
    "foundation_slab": {
        "section_name": "Фундаментная плита",
        "calculator_case_template_input_path": "experiments/foundation_slab_calculator/cases/test_foundation_slab/input.json",
        "generated_input_filename": "foundation_slab_input.json",
    },
    "waterproofing": {
        "section_name": "Гидроизоляция",
        "calculator_case_template_input_path": "experiments/waterproofing_calculator/cases/test_waterproofing_foundation_slab/input.json",
        "generated_input_filename": "waterproofing_input.json",
    },
    "load_bearing_walls_lintels": {
        "section_name": "Несущие стены и перемычки",
        "calculator_case_template_input_path": "experiments/load_bearing_walls_lintels_calculator/cases/test_load_bearing_walls_lintels/input.json",
        "generated_input_filename": "load_bearing_walls_lintels_input.json",
    },
    "floor_slab_1": {
        "section_name": "Плита перекрытия 1-го этажа",
        "calculator_case_template_input_path": "experiments/floor_slab_1_calculator/cases/test_floor_slab_1/input.json",
        "generated_input_filename": "floor_slab_1_input.json",
    },
    "floor_slab_2": {
        "section_name": "Плита перекрытия 2-го этажа",
        "calculator_case_template_input_path": "experiments/floor_slab_2_calculator/cases/test_floor_slab_2/input.json",
        "generated_input_filename": "floor_slab_2_input.json",
    },
    "flat_roof": {
        "section_name": "Плоская кровля",
        "calculator_case_template_input_path": "experiments/flat_roof_calculator/cases/test_flat_roof_usv/input.json",
        "generated_input_filename": "flat_roof_input.json",
    },
    "schiedel_vent_channels": {
        "section_name": "Вентиляционные каналы Schiedel",
        "calculator_case_template_input_path": "experiments/schiedel_vent_channels_calculator/cases/test_schiedel_vent_channels_usv/input.json",
        "generated_input_filename": "schiedel_vent_channels_input.json",
    },
}


def enabled_sections(config_sections: dict[str, bool] | None) -> list[str]:
    if not config_sections:
        return list(SECTION_INPUT_REGISTRY)
    return [
        section_code
        for section_code in SECTION_INPUT_REGISTRY
        if bool(config_sections.get(section_code, False))
    ]
