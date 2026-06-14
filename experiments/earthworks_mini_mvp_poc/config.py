from __future__ import annotations


PROJECT_NAME = "usv_earthworks_mini_mvp_poc"
SECTION_NAME_RU = "Земляные работы"
REVIEW_STATUSES = {
    "ожидает проверки",
    "проверено",
    "исправлено",
    "ручной ввод",
    "не найдено",
    "не требуется",
}
RISKY_REVIEW_REQUIRED_KEYS = {"pit_excavation_depth_m"}
SMOKE_TEST_KEY = "manual_required_smoke_test"

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

PRICE_CODE_TO_INTERNAL_PRICE_KEY = {
    "axis_marking_shift": "axis_marking_work_unit_price",
    "excavator_jcb_shift": (
        "excavator_material_unit_price",
        "excavator_work_unit_price",
    ),
    "manual_excavation_m3": "manual_excavation_work_unit_price",
    "geotextile_laying_m2": "geotextile_laying_work_unit_price",
    "geotextile_dornit_300_m2": "geotextile_material_unit_price",
    "sand_filling_work_m3": "sand_filling_work_unit_price",
    "sand_m3": "sand_material_unit_price",
    "sand_manual_moving_m3": "sand_manual_moving_work_unit_price",
    "communications_installation_m": "communications_work_unit_price",
    "communications_material_m": "communications_material_unit_price",
}

EXPECTED_PRICE_REGISTRY_UNITS = {
    "axis_marking_shift": "смена",
    "excavator_jcb_shift": "смена",
    "manual_excavation_m3": "м3",
    "geotextile_laying_m2": "м2",
    "geotextile_dornit_300_m2": "м2",
    "sand_filling_work_m3": "м3",
    "sand_m3": "м3",
    "sand_manual_moving_m3": "м3",
    "communications_installation_m": "мп",
    "communications_material_m": "мп",
}
