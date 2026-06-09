"""Registry for running existing section calculators from generated inputs."""

from __future__ import annotations

from typing import Any


RUNNER_REGISTRY: dict[str, dict[str, Any]] = {
    "earthworks": {
        "section_code": "earthworks",
        "section_name": "Земляные работы",
        "generated_input_filename": "earthworks_input.json",
        "template_case_dir": "experiments/earthworks_calculator/cases/usv_yusupovo_village",
        "runner_command": "../.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py {case_dir}",
        "output_result_candidates": [
            "experiments/earthworks_calculator/output/{case_name}/earthworks_result.json",
            "{case_dir}/result.json",
        ],
        "output_report_candidates": [
            "experiments/earthworks_calculator/output/{case_name}/earthworks_result.md",
            "{case_dir}/result.md",
        ],
    },
    "foundation_slab": {
        "section_code": "foundation_slab",
        "section_name": "Фундаментная плита",
        "generated_input_filename": "foundation_slab_input.json",
        "template_case_dir": "experiments/foundation_slab_calculator/cases/test_foundation_slab_formwork_spec_area",
        "runner_command": "../.venv/bin/python3 experiments/foundation_slab_calculator/run_foundation_slab_calc.py {case_dir}",
        "output_result_candidates": [
            "experiments/foundation_slab_calculator/output/{case_name}/foundation_slab_result.json",
            "{case_dir}/result.json",
        ],
        "output_report_candidates": [
            "experiments/foundation_slab_calculator/output/{case_name}/foundation_slab_result.md",
            "{case_dir}/result.md",
        ],
    },
    "waterproofing": {
        "section_code": "waterproofing",
        "section_name": "Гидроизоляция",
        "generated_input_filename": "waterproofing_input.json",
        "template_case_dir": "experiments/waterproofing_calculator/cases/test_waterproofing_foundation_slab",
        "runner_command": "../.venv/bin/python3 experiments/waterproofing_calculator/run_waterproofing_calc.py {case_dir}",
        "output_result_candidates": [
            "experiments/waterproofing_calculator/output/{case_name}/waterproofing_result.json",
            "{case_dir}/result.json",
        ],
        "output_report_candidates": [
            "experiments/waterproofing_calculator/output/{case_name}/waterproofing_result.md",
            "{case_dir}/result.md",
        ],
    },
    "load_bearing_walls_lintels": {
        "section_code": "load_bearing_walls_lintels",
        "section_name": "Несущие стены и перемычки",
        "generated_input_filename": "load_bearing_walls_lintels_input.json",
        "template_case_dir": "experiments/load_bearing_walls_lintels_calculator/cases/test_load_bearing_walls_lintels",
        "runner_command": "../.venv/bin/python3 experiments/load_bearing_walls_lintels_calculator/run_load_bearing_walls_lintels_calc.py {case_dir}",
        "output_result_candidates": [
            "experiments/load_bearing_walls_lintels_calculator/output/{case_name}/load_bearing_walls_lintels_result.json",
            "{case_dir}/result.json",
        ],
        "output_report_candidates": [
            "experiments/load_bearing_walls_lintels_calculator/output/{case_name}/load_bearing_walls_lintels_result.md",
            "{case_dir}/result.md",
        ],
    },
    "floor_slab_1": {
        "section_code": "floor_slab_1",
        "section_name": "Плита перекрытия 1-го этажа",
        "generated_input_filename": "floor_slab_1_input.json",
        "template_case_dir": "experiments/floor_slab_1_calculator/cases/test_floor_slab_1",
        "runner_command": "../.venv/bin/python3 experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py {case_dir}",
        "output_result_candidates": [
            "experiments/floor_slab_1_calculator/output/{case_name}/floor_slab_1_result.json",
            "{case_dir}/result.json",
        ],
        "output_report_candidates": [
            "experiments/floor_slab_1_calculator/output/{case_name}/floor_slab_1_result.md",
            "{case_dir}/result.md",
        ],
    },
    "floor_slab_2": {
        "section_code": "floor_slab_2",
        "section_name": "Плита перекрытия 2-го этажа",
        "generated_input_filename": "floor_slab_2_input.json",
        "template_case_dir": "experiments/floor_slab_2_calculator/cases/test_floor_slab_2",
        "runner_command": "../.venv/bin/python3 experiments/floor_slab_2_calculator/run_case.py {case_dir}",
        "output_result_candidates": ["{case_dir}/result.json"],
        "output_report_candidates": ["{case_dir}/result.md"],
    },
    "flat_roof": {
        "section_code": "flat_roof",
        "section_name": "Плоская кровля",
        "generated_input_filename": "flat_roof_input.json",
        "template_case_dir": "experiments/flat_roof_calculator/cases/test_flat_roof_usv",
        "runner_command": "../.venv/bin/python3 experiments/flat_roof_calculator/run_case.py {case_dir}",
        "output_result_candidates": ["{case_dir}/result.json"],
        "output_report_candidates": ["{case_dir}/result.md"],
    },
    "schiedel_vent_channels": {
        "section_code": "schiedel_vent_channels",
        "section_name": "Вентиляционные каналы Schiedel",
        "generated_input_filename": "schiedel_vent_channels_input.json",
        "template_case_dir": "experiments/schiedel_vent_channels_calculator/cases/test_schiedel_vent_channels_usv",
        "runner_command": "../.venv/bin/python3 experiments/schiedel_vent_channels_calculator/run_case.py {case_dir}",
        "output_result_candidates": ["{case_dir}/result.json"],
        "output_report_candidates": ["{case_dir}/result.md"],
    },
}


def enabled_sections(config_sections: dict[str, bool] | None) -> list[str]:
    if not config_sections:
        return list(RUNNER_REGISTRY)
    return [
        section_code
        for section_code in RUNNER_REGISTRY
        if bool(config_sections.get(section_code, False))
    ]
