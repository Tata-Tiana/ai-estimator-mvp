from __future__ import annotations

from pathlib import Path


EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[1]
DATA_DIR = EXPERIMENT_DIR / "data"

SECTION_CODE = "earthworks"
SECTION_NAME_RU = "Земляные работы"

DEFAULT_PROJECT_NAME = "ЮСВ"

DEFAULTS = {
    "manual_refinement_depth_m": 0.08,
    "trench_width_m": 0.4,
    "sand_compaction_coeff": 1.3,
    "sand_truck_step_m3": 20.0,
    "geotextile_overlap_coeff": 1.1,
    "geotextile_roll_area_m2": 100.0,
    "excavator_productivity_m3_per_shift": 80.0,
    "axis_marking_shifts": 1.0,
    "consumables_amount": 0.0,
}

PRODUCTION_METHODS = {
    "excavator_shifts_calc_method": "standard_volume_productivity",
    "manual_excavation_calc_method": "standard_routes",
    "communications_length_calc_method": "pipe_items",
}

RISKY_PROJECT_KEYS = {"pit_excavation_depth_m"}
