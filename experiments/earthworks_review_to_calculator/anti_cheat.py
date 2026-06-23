from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from constants import (
    DEFAULT_COMMUNICATIONS_METHOD,
    DEFAULT_EXCAVATOR_SHIFTS_METHOD,
    DEFAULT_MANUAL_EXCAVATION_METHOD,
    HUMAN_REVIEW_STATUS_VALUES,
    REQUIRED_CALC_PRICE_KEYS,
    REQUIRED_PARAMETERS,
)
from normalization import cell_text


VALID_SELECTED_PRICE_SOURCES = {"price_registry", "fallback"}
VALID_EFFECTIVE_PRICE_SOURCES = {"price_registry", "fallback", "manual_override"}
EXPECTED_FORMULA_READY_LAYOUT = {
    "white_zone": ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
    "calc_zone": ["J", "K", "L", "M", "N", "O"],
    "helper_zone": ["P", "Q", "R", "S", "T", "U", "V"],
}
EXPECTED_FORMULA_READY_SUPPORTED_TYPES = [
    "ref",
    "multiply",
    "sum",
    "ceil_divide",
    "roundup_to_step",
]
LINEAGE_REQUIRED_GENERIC_DEFAULTS = {
    "assumptions.manual_excavation_override",
    "assumptions.sand_override",
    "assumptions.geotextile_override",
    "excavator_shifts_calc_method",
    "manual_excavation_calc_method",
    "communications_length_calc_method",
    "excavator_productivity_m3_per_shift",
    "manual_refinement_depth_m",
    "trench_width_m",
    "sand_compaction_coeff",
    "sand_truck_step_m3",
    "geotextile_overlap_coeff",
    "geotextile_roll_area_m2",
    "axis_marking_shifts",
    "enabled_lines",
    "quantity_overrides",
    "line_name_overrides",
}
LINEAGE_REQUIRED_PROJECT_FIELDS = {
    "project_name",
    "case_meta",
    "case_meta.review_source",
    "case_meta.human_review_status",
    "case_meta.confidence",
    "case_meta.workbook_path",
    "case_meta.section_code",
    "case_meta.section_name",
    "pit_area_m2",
    "pit_excavation_depth_m",
    "sand_base_volume_m3",
    "trench_volume_m3",
    "geotextile_area_m2",
    "geotextile_laying_area_m2",
    "communications_length_m",
    "case_meta.communications_quantity_mode",
    "case_meta.communications_length_m_from_review",
    "case_meta.communications_length_m_effective",
    "trench_routes",
    "communications_pipe_items",
    "excavator_shifts",
    "trench_length_m",
    "trench_depth_m",
    "manual_excavation_quantity_for_estimate_m3",
    "internal_prices",
    "consumables_amount",
}

FORMULA_MODEL_A1_REF_PATTERN = re.compile(r"\b[A-Z]{1,3}\d+\b")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_boolish(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "да", "y"}:
        return True
    if text in {"0", "false", "no", "нет", "n", ""}:
        return False
    return None


def _expected_prices_by_calc_key(prices: list[dict[str, Any]]) -> tuple[dict[str, float], float | None]:
    internal_prices: dict[str, float] = {}
    consumables_amount: float | None = None
    seen_keys: set[str] = set()

    for row in prices:
        estimate_line = str(row.get("estimate_line", "")).strip()
        price_role = str(row.get("price_role", "")).strip()
        calc_price_key = str(row.get("calc_price_key", "")).strip()
        selected_price = _as_number(row.get("selected_price"))
        if selected_price is None:
            continue

        if not calc_price_key:
            continue

        if calc_price_key in seen_keys:
            raise ValueError(f"duplicate calc_price_key in normalized review: {calc_price_key}")
        seen_keys.add(calc_price_key)

        if calc_price_key == "consumables_amount":
            consumables_amount = selected_price
            continue

        internal_prices[calc_price_key] = selected_price

    return internal_prices, consumables_amount


def validate_normalized_review(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    parameters = data.get("parameters", {})
    prices = data.get("prices", [])
    details = data.get("details", {})
    summary = details.get("summary", {})

    for key in REQUIRED_PARAMETERS:
        parameter = parameters.get(key)
        if parameter is None:
            errors.append(f"missing parameter: {key}")
            continue
        value = _as_number(parameter.get("value"))
        if value is None:
            errors.append(f"required parameter must be numeric: {key}")
            continue
        if key in {"pit_area_m2", "pit_excavation_depth_m", "sand_base_volume_m3", "geotextile_area_m2", "geotextile_laying_area_m2"} and value <= 0:
            errors.append(f"required parameter must be > 0: {key}")
        if key in {"trench_volume_m3", "communications_length_m"} and value < 0:
            errors.append(f"required parameter must be >= 0: {key}")

    calc_price_keys = [cell_text(row.get("calc_price_key")) for row in prices]
    if any(not key for key in calc_price_keys):
        errors.append("all price rows must have calc_price_key")
    if len(set(calc_price_keys)) != len(prices):
        errors.append("calc_price_key values must be unique across price rows")

    price_by_key = {key: row for key, row in ((cell_text(row.get("calc_price_key")), row) for row in prices) if key}
    missing_calc_keys = [key for key in REQUIRED_CALC_PRICE_KEYS if key not in price_by_key]
    if missing_calc_keys:
        errors.append(f"missing required calc_price_keys: {', '.join(missing_calc_keys)}")

    for row in prices:
        calc_price_key = cell_text(row.get("calc_price_key"))
        selected_price_source = cell_text(row.get("selected_price_source")).lower()
        effective_price_source = cell_text(row.get("effective_price_source")).lower()
        price_registry_code = cell_text(row.get("price_registry_code"))
        fallback_key = cell_text(row.get("fallback_key"))
        override_used = bool(row.get("override_used"))
        selected_price = _as_number(row.get("selected_price"))

        if selected_price_source not in VALID_SELECTED_PRICE_SOURCES:
            errors.append(f"invalid selected_price_source for {calc_price_key}: {selected_price_source}")
        if effective_price_source not in VALID_EFFECTIVE_PRICE_SOURCES:
            errors.append(f"invalid effective_price_source for {calc_price_key}: {effective_price_source}")
        if selected_price is None:
            errors.append(f"selected_price must be numeric for {calc_price_key}")
        elif selected_price < 0:
            errors.append(f"selected_price must be >= 0 for {calc_price_key}")
        if override_used and effective_price_source != "manual_override":
            errors.append(f"{calc_price_key}: override_used rows must have effective_price_source manual_override")
        if not override_used and effective_price_source != selected_price_source:
            errors.append(
                f"{calc_price_key}: effective_price_source must equal selected_price_source when no override is used"
            )
        if selected_price_source == "fallback":
            if not fallback_key.startswith("fallback."):
                errors.append(f"{calc_price_key}: fallback rows must have fallback_key starting with fallback.")
            if price_registry_code:
                errors.append(f"{calc_price_key}: fallback rows must not have price_registry_code")
        if selected_price_source == "price_registry" and not price_registry_code:
            warnings.append(f"price_registry_code is empty for price_registry row: {calc_price_key}")

    trench_routes = details.get("trench_routes", [])
    if not isinstance(trench_routes, list):
        errors.append("trench_routes must be a list")
        trench_routes = []
    for index, row in enumerate(trench_routes):
        if not isinstance(row, dict):
            errors.append(f"trench_routes[{index}] must be a mapping")
            continue
        if not cell_text(row.get("name")):
            errors.append(f"trench_routes[{index}].name is required")
        for field in ("length_m", "depth_m", "width_m", "volume_m3"):
            value = _as_number(row.get(field))
            if value is not None and value < 0:
                errors.append(f"trench_routes[{index}].{field} must be >= 0")

    communications = details.get("communications_pipe_items", [])
    if not isinstance(communications, list):
        errors.append("communications_pipe_items must be a list")
        communications = []
    for index, row in enumerate(communications):
        if not isinstance(row, dict):
            errors.append(f"communications_pipe_items[{index}] must be a mapping")
            continue
        if not cell_text(row.get("name")):
            errors.append(f"communications_pipe_items[{index}].name is required")
        total_length = _as_number(row.get("total_length_m"))
        if total_length is None:
            errors.append(f"communications_pipe_items[{index}].total_length_m must be numeric")
        elif total_length < 0:
            errors.append(f"communications_pipe_items[{index}].total_length_m must be >= 0")
        diameter = row.get("diameter_mm")
        if diameter not in {None, ""}:
            diameter_value = _as_number(diameter)
            if diameter_value is None:
                errors.append(f"communications_pipe_items[{index}].diameter_mm must be numeric")
            elif diameter_value <= 0:
                errors.append(f"communications_pipe_items[{index}].diameter_mm must be > 0")
        quantity = row.get("quantity")
        if quantity not in {None, ""}:
            quantity_value = _as_number(quantity)
            if quantity_value is None:
                errors.append(f"communications_pipe_items[{index}].quantity must be numeric")
            elif quantity_value < 0:
                errors.append(f"communications_pipe_items[{index}].quantity must be >= 0")
        included = _as_boolish(row.get("included"))
        if included is None:
            errors.append(f"communications_pipe_items[{index}].included must be boolean-like")

    summary_total = _as_number(summary.get("communications_total_length_m"))
    pipe_total = sum(
        _as_number(row.get("total_length_m")) or 0.0
        for row in communications
        if _as_boolish(row.get("included")) is True
    )
    if summary_total is None:
        errors.append("communications_total_length_m must be numeric")
    elif abs(summary_total - pipe_total) > 0.001:
        errors.append(
            f"communications_total_length_m must equal sum of pipe rows ({pipe_total}), got {summary_total}"
        )

    return errors, warnings


def validate_calculator_input(
    normalized_data: dict[str, Any],
    calculator_input: dict[str, Any],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    parameters = normalized_data.get("parameters", {})
    prices = normalized_data.get("prices", [])
    details = normalized_data.get("details", {})
    normalized_summary = details.get("summary", {})
    normalized_communications_total = _as_number(normalized_summary.get("communications_total_length_m"))
    if normalized_communications_total is None:
        normalized_communications_total = sum(
            _as_number(row.get("total_length_m")) or 0.0
            for row in details.get("communications_pipe_items", [])
            if _as_boolish(row.get("included")) is True
        )

    try:
        expected_internal_prices, expected_consumables_amount = _expected_prices_by_calc_key(prices)
    except ValueError as exc:
        errors.append(str(exc))
        expected_internal_prices, expected_consumables_amount = {}, None

    communications_parameter = parameters.get("communications_length_m", {})
    communications_override_used = bool(communications_parameter.get("override_used"))
    communications_value = _as_number(communications_parameter.get("value")) or 0.0

    pit_area_m2 = _as_number(parameters.get("pit_area_m2", {}).get("value"))
    pit_excavation_depth_m = _as_number(parameters.get("pit_excavation_depth_m", {}).get("value"))
    sand_base_volume_m3 = _as_number(parameters.get("sand_base_volume_m3", {}).get("value"))
    trench_volume_m3 = _as_number(parameters.get("trench_volume_m3", {}).get("value"))
    geotextile_area_m2 = _as_number(parameters.get("geotextile_area_m2", {}).get("value"))
    geotextile_laying_area_m2 = _as_number(
        parameters.get("geotextile_laying_area_m2", {}).get("value")
    )

    expected_excavator_method = DEFAULT_EXCAVATOR_SHIFTS_METHOD
    expected_manual_method = DEFAULT_MANUAL_EXCAVATION_METHOD
    # legacy_direct_length is valid when there are no pipe specs but manual length > 0
    _pipe_items_in_review = details.get("communications_pipe_items", [])
    if not _pipe_items_in_review and (communications_value or 0.0) > 0.0:
        expected_communications_method = "legacy_direct_length"
    else:
        expected_communications_method = DEFAULT_COMMUNICATIONS_METHOD

    if calculator_input.get("project_name") in {None, ""}:
        errors.append("project_name is required")

    case_meta = calculator_input.get("case_meta", {})
    if isinstance(case_meta, dict):
        if case_meta.get("validated_with_elena") is True:
            errors.append("case_meta must not contain validated_with_elena = True")
        human_review_status = case_meta.get("human_review_status")
        if human_review_status not in HUMAN_REVIEW_STATUS_VALUES:
            errors.append(
                f"case_meta.human_review_status must be one of "
                f"{sorted(HUMAN_REVIEW_STATUS_VALUES)}, got {human_review_status!r}"
            )

    communications_quantity_mode = case_meta.get("communications_quantity_mode") if isinstance(case_meta, dict) else None
    if communications_quantity_mode not in {DEFAULT_COMMUNICATIONS_METHOD, "legacy_direct_length"}:
        errors.append(
            f"case_meta.communications_quantity_mode must be one of "
            f"{[DEFAULT_COMMUNICATIONS_METHOD, 'legacy_direct_length']!r}, "
            f"got {communications_quantity_mode!r}"
        )

    comms_from_review = _as_number(case_meta.get("communications_length_m_from_review") if isinstance(case_meta, dict) else None)
    comms_effective = _as_number(case_meta.get("communications_length_m_effective") if isinstance(case_meta, dict) else None)
    if comms_from_review is None:
        errors.append("case_meta.communications_length_m_from_review must be numeric")
    if comms_effective is None:
        errors.append("case_meta.communications_length_m_effective must be numeric")
    if comms_from_review is not None and comms_effective is not None:
        if abs(comms_from_review - comms_effective) > 0.01:
            warnings.append(
                f"case_meta.communications_length_m_from_review ({comms_from_review}) "
                f"!= case_meta.communications_length_m_effective ({comms_effective}); "
                "sheet 01 reference value differs from sum of included pipe items"
            )

    if _as_number(calculator_input.get("pit_area_m2")) != pit_area_m2:
        errors.append("pit_area_m2 must match normalized review value")
    if _as_number(calculator_input.get("pit_excavation_depth_m")) != pit_excavation_depth_m:
        errors.append("pit_excavation_depth_m must match normalized review value")
    if _as_number(calculator_input.get("sand_base_volume_m3")) != sand_base_volume_m3:
        errors.append("sand_base_volume_m3 must match normalized review value")
    if _as_number(calculator_input.get("trench_volume_m3")) != trench_volume_m3:
        errors.append("trench_volume_m3 must match normalized review value")
    if _as_number(calculator_input.get("geotextile_area_m2")) != geotextile_area_m2:
        errors.append("geotextile_area_m2 must match normalized review value")
    if _as_number(calculator_input.get("geotextile_laying_area_m2")) != geotextile_laying_area_m2:
        errors.append("geotextile_laying_area_m2 must match normalized review value")

    if calculator_input.get("excavator_shifts_calc_method") != expected_excavator_method:
        errors.append("excavator_shifts_calc_method must match normalized review method")
    if calculator_input.get("manual_excavation_calc_method") != expected_manual_method:
        errors.append("manual_excavation_calc_method must match normalized review method")
    if calculator_input.get("communications_length_calc_method") != expected_communications_method:
        errors.append("communications_length_calc_method must match normalized review method")

    if expected_communications_method == DEFAULT_COMMUNICATIONS_METHOD:
        if _as_number(calculator_input.get("communications_length_m")) not in {0.0, 0}:
            errors.append("communications_length_m must be 0 in pipe_items mode")
    elif expected_communications_method == "legacy_direct_length":
        if _as_number(calculator_input.get("communications_length_m")) != communications_value:
            errors.append("communications_length_m must match normalized review value in legacy_direct_length mode")

    if expected_manual_method == DEFAULT_MANUAL_EXCAVATION_METHOD:
        if calculator_input.get("manual_excavation_quantity_for_estimate_m3") is not None:
            errors.append("manual_excavation_quantity_for_estimate_m3 must be null in standard_routes mode")

    if expected_excavator_method == DEFAULT_EXCAVATOR_SHIFTS_METHOD:
        if _as_number(calculator_input.get("excavator_shifts")) not in {0.0, 0}:
            errors.append("excavator_shifts must be 0 in standard_volume_productivity mode")

    internal_prices = calculator_input.get("internal_prices", {})
    if not isinstance(internal_prices, dict) or not internal_prices:
        errors.append("internal_prices must be a non-empty mapping")
    else:
        for key, expected_value in expected_internal_prices.items():
            actual = _as_number(internal_prices.get(key))
            if actual != expected_value:
                errors.append(f"internal_prices.{key} expected {expected_value}, got {actual}")
        if internal_prices.get("consumables_amount") is not None:
            errors.append("internal_prices must not contain consumables_amount")
        if len(internal_prices) != len(expected_internal_prices):
            missing = sorted(set(expected_internal_prices) - set(internal_prices))
            unexpected = sorted(set(internal_prices) - set(expected_internal_prices))
            if missing:
                errors.append(f"internal_prices missing keys: {', '.join(missing)}")
            if unexpected:
                errors.append(f"internal_prices unexpected keys: {', '.join(unexpected)}")

    if expected_consumables_amount is None:
        errors.append("consumables_amount must be mapped from review sheet")
    elif _as_number(calculator_input.get("consumables_amount")) != expected_consumables_amount:
        errors.append("consumables_amount must match normalized review value")

    trench_routes = calculator_input.get("trench_routes") or []
    if not isinstance(trench_routes, list):
        errors.append("trench_routes must be a list in calculator input")
        trench_routes = []
    for index, row in enumerate(trench_routes):
        if not isinstance(row, dict):
            errors.append(f"trench_routes[{index}] must be a mapping in calculator input")
            continue
        if not cell_text(row.get("name")):
            errors.append(f"trench_routes[{index}].name is required in calculator input")
        for field in ("length_m", "depth_m", "width_m", "volume_m3"):
            value = _as_number(row.get(field))
            if value is None:
                errors.append(f"trench_routes[{index}].{field} must be numeric in calculator input")
            elif value < 0:
                errors.append(f"trench_routes[{index}].{field} must be >= 0 in calculator input")

    communications_pipe_items = calculator_input.get("communications_pipe_items") or []
    if not isinstance(communications_pipe_items, list):
        errors.append("communications_pipe_items must be a list in calculator input")
        communications_pipe_items = []
    included_total = 0.0
    for index, row in enumerate(communications_pipe_items):
        if not isinstance(row, dict):
            errors.append(f"communications_pipe_items[{index}] must be a mapping in calculator input")
            continue
        if not cell_text(row.get("name")):
            errors.append(f"communications_pipe_items[{index}].name is required in calculator input")
        total_length = _as_number(row.get("total_length_m"))
        if total_length is None:
            errors.append(f"communications_pipe_items[{index}].total_length_m must be numeric in calculator input")
        elif total_length < 0:
            errors.append(f"communications_pipe_items[{index}].total_length_m must be >= 0 in calculator input")
        diameter = row.get("diameter_mm")
        if diameter not in {None, ""}:
            diameter_value = _as_number(diameter)
            if diameter_value is None:
                errors.append(f"communications_pipe_items[{index}].diameter_mm must be numeric in calculator input")
            elif diameter_value <= 0:
                errors.append(f"communications_pipe_items[{index}].diameter_mm must be > 0 in calculator input")
        quantity = row.get("quantity")
        if quantity not in {None, ""}:
            quantity_value = _as_number(quantity)
            if quantity_value is None:
                errors.append(f"communications_pipe_items[{index}].quantity must be numeric in calculator input")
            elif quantity_value < 0:
                errors.append(f"communications_pipe_items[{index}].quantity must be >= 0 in calculator input")
        included = _as_boolish(row.get("include_in_communications"))
        if included is None:
            included = _as_boolish(row.get("included"))
        if included is None:
            errors.append(f"communications_pipe_items[{index}].include_in_communications must be boolean-like")
        elif included and total_length is not None:
            included_total += total_length

    if abs(included_total - normalized_communications_total) > 0.001:
        errors.append(
            f"communications total length must equal normalized review total ({normalized_communications_total}), got {included_total}"
        )

    if comms_effective is not None and abs(comms_effective - included_total) > 0.001:
        errors.append(
            f"case_meta.communications_length_m_effective ({comms_effective}) "
            f"must equal sum of included calculator_input.communications_pipe_items ({included_total})"
        )

    return errors, warnings



def validate_calculation_result(
    normalized_data: dict[str, Any],
    result_dir: Path | str | None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if result_dir is None:
        errors.append("calculation result dir is required")
        return errors, warnings

    path = Path(result_dir)
    if not path.exists():
        errors.append(f"calculation result dir does not exist: {path}")
        return errors, warnings

    result_json_path: Path | None = None
    result_md_exists = False
    for candidate in ("earthworks_result.json", "result.json"):
        candidate_path = path / candidate
        if candidate_path.exists():
            result_json_path = candidate_path
            break
    for candidate in ("earthworks_result.md", "result.md"):
        if (path / candidate).exists():
            result_md_exists = True
            break

    if result_json_path is None:
        errors.append(f"no result json found in calculation result dir: {path}")
        return errors, warnings

    try:
        result_data = load_json(result_json_path)
    except Exception as exc:  # pragma: no cover - defensive
        errors.append(f"failed to read calculation result json: {exc}")
        return errors, warnings

    if not isinstance(result_data, dict):
        errors.append("calculation result json must be a mapping")
        return errors, warnings

    internal_totals = result_data.get("internal_totals", {})
    if not isinstance(internal_totals, dict) or not internal_totals:
        errors.append("calculation result internal_totals is missing")
    else:
        section_total = _as_number(internal_totals.get("internal_section_total"))
        if section_total is None or section_total <= 0:
            errors.append(
                f"internal_section_total must be > 0, got {internal_totals.get('internal_section_total')}"
            )

    volume_result = result_data.get("volume_result", {})
    communications_length = _as_number(volume_result.get("communications_length_m"))
    normalized_summary = normalized_data.get("details", {}).get("summary", {})
    expected_communications_length = _as_number(normalized_summary.get("communications_total_length_m"))
    if expected_communications_length is None:
        expected_communications_length = sum(
            _as_number(row.get("total_length_m")) or 0.0
            for row in normalized_data.get("details", {}).get("communications_pipe_items", [])
            if _as_boolish(row.get("included")) is True
        )
    # In legacy_direct_length mode (no pipe specs, manual length entered), the calculator
    # uses the manual value from sheet 01, not the pipe-items sum (which is 0).
    _norm_params = normalized_data.get("parameters", {})
    _comm_value = _as_number((_norm_params.get("communications_length_m") or {}).get("value")) or 0.0
    _pipe_items_in_norm = normalized_data.get("details", {}).get("communications_pipe_items", [])
    if not _pipe_items_in_norm and _comm_value > 0.0:
        expected_communications_length = _comm_value
    if communications_length is None:
        errors.append("calculation result communications_length_m must be numeric")
    elif abs(communications_length - expected_communications_length) > 0.001:
        errors.append(
            f"communications_length_m expected {expected_communications_length}, got {volume_result.get('communications_length_m')}"
        )

    estimate_lines = result_data.get("estimate_lines") or []
    if not isinstance(estimate_lines, list) or not estimate_lines:
        errors.append("calculation result estimate_lines is missing")

    if not result_md_exists:
        warnings.append("calculation result markdown is missing")

    return errors, warnings


def _formula_model_violations(model: Any, path: str = "formula_model") -> list[str]:
    violations: list[str] = []

    def walk(value: Any, current_path: str) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                walk(nested, f"{current_path}.{key}")
            return
        if isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, f"{current_path}[{index}]")
            return
        if isinstance(value, str):
            if value.startswith("="):
                violations.append(f"{current_path} must not start with =")
            if FORMULA_MODEL_A1_REF_PATTERN.search(value):
                violations.append(f"{current_path} must not contain Excel A1 refs")

    walk(model, path)
    return violations


def _formula_model_contains_calculator_result_ref(model: Any) -> bool:
    if isinstance(model, dict):
        for value in model.values():
            if _formula_model_contains_calculator_result_ref(value):
                return True
        return False
    if isinstance(model, list):
        return any(_formula_model_contains_calculator_result_ref(item) for item in model)
    if isinstance(model, str):
        return "calculator_result." in model
    return False


def validate_formula_ready_result(report_path: Path | str | None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if report_path is None:
        return errors, warnings

    path = Path(report_path)
    if not path.exists():
        errors.append(f"formula-ready report does not exist: {path}")
        return errors, warnings

    try:
        report = load_json(path)
    except Exception as exc:  # pragma: no cover - defensive
        errors.append(f"failed to read formula-ready json: {exc}")
        return errors, warnings

    if report.get("section_code") != "earthworks":
        errors.append(f"formula-ready section_code must be earthworks, got {report.get('section_code')}")
    if report.get("section_title") != "Земляные работы":
        errors.append("formula-ready section_title must be Земляные работы")
    if report.get("excel_export_ready") is not True:
        errors.append("formula-ready excel_export_ready must be true")
    supported_formula_types = report.get("supported_formula_types")
    if supported_formula_types != EXPECTED_FORMULA_READY_SUPPORTED_TYPES:
        errors.append(
            "formula-ready supported_formula_types must be "
            + ", ".join(EXPECTED_FORMULA_READY_SUPPORTED_TYPES)
        )

    layout_model = report.get("layout_model")
    if not isinstance(layout_model, dict):
        errors.append("formula-ready layout_model must be a mapping")
    else:
        for zone, expected_columns in EXPECTED_FORMULA_READY_LAYOUT.items():
            zone_model = layout_model.get(zone)
            if not isinstance(zone_model, dict):
                errors.append(f"formula-ready layout_model missing {zone}")
                continue
            if zone_model.get("columns") != expected_columns:
                errors.append(f"formula-ready layout_model.{zone}.columns must be {expected_columns}")

    rows = report.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("formula-ready rows must be a non-empty list")
        rows = []

    row_ids: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"formula-ready rows[{index}] must be a mapping")
            continue
        row_id = cell_text(row.get("row_id"))
        estimate_line = cell_text(row.get("estimate_line"))
        if not row_id:
            errors.append(f"formula-ready rows[{index}].row_id is required")
        elif row_id in row_ids:
            errors.append(f"duplicate formula-ready row_id: {row_id}")
        else:
            row_ids.add(row_id)
        if not estimate_line:
            errors.append(f"formula-ready rows[{index}].estimate_line is required")

        white_zone = row.get("white_zone")
        calc_zone = row.get("calc_zone")
        helper_zone = row.get("helper_zone")
        hints = row.get("excel_export_hints")
        if not isinstance(white_zone, dict):
            errors.append(f"formula-ready rows[{index}].white_zone must be a mapping")
        if not isinstance(calc_zone, dict):
            errors.append(f"formula-ready rows[{index}].calc_zone must be a mapping")
            calc_zone = {}
        if not isinstance(helper_zone, dict):
            errors.append(f"formula-ready rows[{index}].helper_zone must be a mapping")
            helper_zone = {}
        if not isinstance(hints, dict):
            errors.append(f"formula-ready rows[{index}].excel_export_hints must be a mapping")

        expected_white_zone = {
            "line_name": ("B", "estimate_line"),
            "unit": ("C", "unit"),
            "quantity": ("D", "calc_zone.quantity"),
            "material_unit_price": ("E", "calc_zone.material_unit_price"),
            "material_total": ("F", "calc_zone.material_total"),
            "work_unit_price": ("G", "calc_zone.work_unit_price"),
            "work_total": ("H", "calc_zone.work_total"),
            "row_total": ("I", "calc_zone.row_total"),
        }
        for field, (target_role, mirror_of) in expected_white_zone.items():
            item = (white_zone or {}).get(field, {})
            if not isinstance(item, dict):
                errors.append(f"formula-ready rows[{index}].white_zone.{field} must be a mapping")
                continue
            if item.get("target_col_role") != target_role:
                errors.append(f"formula-ready rows[{index}].white_zone.{field}.target_col_role must be {target_role}")
            if field in {"line_name", "unit"}:
                if item.get("source") != mirror_of:
                    errors.append(f"formula-ready rows[{index}].white_zone.{field}.source must be {mirror_of}")
            else:
                if item.get("mirror_of") != mirror_of:
                    errors.append(f"formula-ready rows[{index}].white_zone.{field}.mirror_of must be {mirror_of}")

        expected_calc_roles = {
            "quantity": "J",
            "material_unit_price": "K",
            "material_total": "L",
            "work_unit_price": "M",
            "work_total": "N",
            "row_total": "O",
        }
        for field, target_role in expected_calc_roles.items():
            item = calc_zone.get(field, {})
            if not isinstance(item, dict):
                errors.append(f"formula-ready rows[{index}].calc_zone.{field} must be a mapping")
                continue
            if item.get("target_col_role") != target_role:
                errors.append(f"formula-ready rows[{index}].calc_zone.{field}.target_col_role must be {target_role}")
            value = item.get("value")
            if field in {"quantity", "material_unit_price", "material_total", "work_unit_price", "work_total", "row_total"}:
                if _as_number(value) is None:
                    errors.append(f"formula-ready rows[{index}].calc_zone.{field}.value must be numeric")
            formula_model = item.get("formula_model")
            if field == "row_total":
                if not isinstance(formula_model, dict):
                    errors.append(f"formula-ready rows[{index}].calc_zone.row_total.formula_model is required")
            if formula_model is not None:
                violations = _formula_model_violations(formula_model, f"rows[{index}].calc_zone.{field}.formula_model")
                errors.extend(violations)
                if _formula_model_contains_calculator_result_ref(formula_model):
                    if item.get("excel_formula_exportable") is not False:
                        errors.append(
                            f"formula-ready rows[{index}].calc_zone.{field} with calculator_result ref must be marked excel_formula_exportable = false"
                        )
                    if not cell_text(item.get("reason")):
                        errors.append(
                            f"formula-ready rows[{index}].calc_zone.{field} with calculator_result ref must include a reason"
                        )

            if field in {"material_unit_price", "work_unit_price"} and item.get("price_key"):
                if cell_text(item.get("selected_price_source")).lower() not in VALID_SELECTED_PRICE_SOURCES | {""}:
                    errors.append(
                        f"formula-ready rows[{index}].calc_zone.{field}.selected_price_source must be a known price source"
                    )

        cells = helper_zone.get("cells", [])
        if not isinstance(cells, list):
            errors.append(f"formula-ready rows[{index}].helper_zone.cells must be a list")
            cells = []
        for cell_index, cell in enumerate(cells):
            if not isinstance(cell, dict):
                errors.append(f"formula-ready rows[{index}].helper_zone.cells[{cell_index}] must be a mapping")
                continue
            for required_field in ("helper_id", "target_col_role", "label", "value", "source_type", "source_path", "source_note"):
                if required_field not in cell:
                    errors.append(f"formula-ready rows[{index}].helper_zone.cells[{cell_index}].{required_field} is required")
            if isinstance(cell.get("value"), (dict, list)):
                errors.append(
                    f"formula-ready rows[{index}].helper_zone.cells[{cell_index}].value must not be raw JSON structure"
                )
            formula_model = cell.get("formula_model")
            if formula_model is not None:
                violations = _formula_model_violations(formula_model, f"rows[{index}].helper_zone.cells[{cell_index}].formula_model")
                errors.extend(violations)
                if _formula_model_contains_calculator_result_ref(formula_model):
                    if cell.get("excel_formula_exportable") is not False:
                        errors.append(
                            f"formula-ready rows[{index}].helper_zone.cells[{cell_index}] with calculator_result ref must be marked excel_formula_exportable = false"
                        )
                    if not cell_text(cell.get("reason")):
                        errors.append(
                            f"formula-ready rows[{index}].helper_zone.cells[{cell_index}] with calculator_result ref must include a reason"
                        )

    source_files = report.get("source_files", {})
    if isinstance(source_files, dict):
        for key in ("calculator_input", "calculation_result", "lineage_report"):
            value = cell_text(source_files.get(key))
            if not value:
                errors.append(f"formula-ready source_files.{key} is required")
    else:
        errors.append("formula-ready source_files must be a mapping")

    excel_export_hints = report.get("excel_export_hints", {})
    if not isinstance(excel_export_hints, dict) or excel_export_hints.get("formula_models_symbolic") is not True:
        errors.append("formula-ready excel_export_hints.formula_models_symbolic must be true")

    warnings_list = report.get("warnings", [])
    if not isinstance(warnings_list, list):
        warnings.append("formula-ready warnings should be a list")

    return errors, warnings


def validate_formula_ready_vs_result(formula_ready_path: Path | str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    path = Path(formula_ready_path)
    if not path.exists():
        errors.append(f"formula-ready result does not exist: {path}")
        return errors, warnings

    try:
        report = load_json(path)
    except Exception as exc:  # pragma: no cover - defensive
        errors.append(f"failed to read formula-ready json for cross-check: {exc}")
        return errors, warnings

    source_files = report.get("source_files", {})
    if not isinstance(source_files, dict):
        errors.append("formula-ready source_files must be a mapping")
        return errors, warnings

    calculation_result_path_str = cell_text(source_files.get("calculation_result"))
    if not calculation_result_path_str:
        errors.append("formula-ready source_files.calculation_result path is required for cross-check")
        return errors, warnings

    calculation_result_path = Path(calculation_result_path_str)
    if not calculation_result_path.is_absolute():
        calculation_result_path = path.parent / calculation_result_path_str

    if not calculation_result_path.exists():
        errors.append(f"formula-ready source_files.calculation_result does not exist: {calculation_result_path}")
        return errors, warnings

    try:
        result_data = load_json(calculation_result_path)
    except Exception as exc:  # pragma: no cover - defensive
        errors.append(f"failed to read calculation result for cross-check: {exc}")
        return errors, warnings

    estimate_lines = result_data.get("estimate_lines") or []
    result_by_code: dict[str, dict] = {
        str(line.get("code", "")): line for line in estimate_lines if line.get("code")
    }

    section_code = cell_text(report.get("section_code"))
    section_prefix = (section_code + ".") if section_code else ""

    rows = report.get("rows") or []
    tolerance = 0.01
    field_map = [
        ("quantity", "quantity"),
        ("material_total", "material_total"),
        ("work_total", "work_total"),
        ("row_total", "line_total"),
    ]
    matched = 0
    unmatched = 0

    for row in rows:
        if not isinstance(row, dict):
            continue
        row_id = str(row.get("row_id", ""))
        if not row_id:
            continue

        bare_code = row_id[len(section_prefix):] if section_prefix and row_id.startswith(section_prefix) else row_id
        result_line = result_by_code.get(bare_code) or result_by_code.get(row_id)
        if result_line is None:
            unmatched += 1
            errors.append(
                f"formula_ready row {row_id!r} has no matching calculation_result estimate line"
            )
            continue

        matched += 1
        calc_zone = row.get("calc_zone", {})
        if not isinstance(calc_zone, dict):
            errors.append(f"formula_ready row {row_id!r} calc_zone must be a mapping")
            continue

        for formula_field, result_field in field_map:
            formula_value = _as_number((calc_zone.get(formula_field) or {}).get("value"))
            result_value = _as_number(result_line.get(result_field))
            if formula_value is None:
                errors.append(
                    f"formula_ready row {row_id!r} calc_zone.{formula_field}.value is missing or non-numeric"
                )
                continue
            if result_value is None:
                errors.append(
                    f"formula_ready row {row_id!r}: calculation_result.{result_field} is missing or non-numeric"
                )
                continue
            if abs(formula_value - result_value) > tolerance:
                errors.append(
                    f"formula_ready row {row_id!r} {formula_field} ({formula_value}) "
                    f"does not match calculation_result {result_field} ({result_value}), "
                    f"tolerance={tolerance}"
                )

    if rows:
        print(
            f"  cross-check: matched_formula_ready_rows={matched}, "
            f"unmatched_formula_ready_rows={unmatched}"
        )

    return errors, warnings


def validate_comparison_report(report_path: Path | str | None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if report_path is None:
        return errors, warnings

    path = Path(report_path)
    if not path.exists():
        errors.append(f"comparison report does not exist: {path}")
        return errors, warnings

    text = path.read_text(encoding="utf-8")
    if "Diagnostic comparison" not in text and "diagnostic comparison" not in text.lower():
        errors.append("comparison report must mention diagnostic comparison")
    if "Baseline result path is provided via CLI" not in text:
        errors.append("comparison report must mention CLI baseline path")

    return errors, warnings


def validate_lineage_report(report_path: Path | str | None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if report_path is None:
        return errors, warnings

    path = Path(report_path)
    if not path.exists():
        errors.append(f"lineage report does not exist: {path}")
        return errors, warnings

    try:
        report = load_json(path)
    except Exception as exc:  # pragma: no cover - defensive
        errors.append(f"failed to read lineage report json: {exc}")
        return errors, warnings

    if report.get("verdict") != "clean":
        errors.append(f"lineage report verdict must be clean, got {report.get('verdict')}")
    if report.get("hardcoded_project_values_detected_in_source") is not False:
        errors.append("lineage report must declare hardcoded_project_values_detected_in_source = false")

    untraced_fields = report.get("untraced_fields", [])
    if untraced_fields:
        errors.append(f"lineage report must not have untraced fields: {', '.join(map(str, untraced_fields))}")

    report_text = path.read_text(encoding="utf-8").lower()
    if "old fixture" in report_text or "template source" in report_text or "template path" in report_text:
        errors.append("lineage report must not claim old fixture or template source")

    fields = report.get("fields", [])
    if not isinstance(fields, list) or not fields:
        errors.append("lineage report fields are missing")
        return errors, warnings

    field_by_path = {cell_text(row.get("input_path")): row for row in fields if cell_text(row.get("input_path"))}

    for required_path in sorted(LINEAGE_REQUIRED_PROJECT_FIELDS):
        if required_path not in field_by_path:
            errors.append(f"missing lineage trace for {required_path}")

    for required_path in sorted(LINEAGE_REQUIRED_GENERIC_DEFAULTS):
        if required_path not in field_by_path:
            errors.append(f"missing lineage trace for generic default {required_path}")
        elif cell_text(field_by_path[required_path].get("source_type")) != "GENERIC_CALCULATOR_DEFAULTS":
            errors.append(f"{required_path} must be traced to GENERIC_CALCULATOR_DEFAULTS")

    for required_key in REQUIRED_CALC_PRICE_KEYS:
        if required_key == "consumables_amount":
            path_key = "consumables_amount"
        else:
            path_key = f"internal_prices.{required_key}"
        if path_key not in field_by_path:
            errors.append(f"missing lineage trace for price key {required_key}")
            continue
        if cell_text(field_by_path[path_key].get("source_type")) != "normalized.prices by calc_price_key":
            errors.append(f"price key {required_key} must be traced by calc_price_key")

    for required_path in ("trench_routes", "communications_pipe_items"):
        row = field_by_path.get(required_path)
        if row is None:
            errors.append(f"missing lineage trace for {required_path}")
            continue
        if cell_text(row.get("source_type")) not in {
            "normalized.details.trench_routes",
            "normalized.details.communications_pipe_items",
        }:
            errors.append(f"{required_path} must be traced to normalized details")

    return errors, warnings


def run_anti_cheat(
    normalized_json_path: str | Path,
    calculator_input_path: str | Path | None = None,
    calculation_result_dir: str | Path | None = None,
    comparison_report: str | Path | None = None,
    lineage_report: str | Path | None = None,
    formula_ready_result: str | Path | None = None,
) -> bool:
    normalized_path = Path(normalized_json_path)
    normalized_data = load_json(normalized_path)

    errors, warnings = validate_normalized_review(normalized_data)

    if calculator_input_path is not None:
        calculator_input = load_json(Path(calculator_input_path))
        calc_errors, calc_warnings = validate_calculator_input(normalized_data, calculator_input)
        errors.extend(calc_errors)
        warnings.extend(calc_warnings)

    if calculation_result_dir is not None:
        result_errors, result_warnings = validate_calculation_result(normalized_data, calculation_result_dir)
        errors.extend(result_errors)
        warnings.extend(result_warnings)

    if comparison_report is not None:
        comparison_errors, comparison_warnings = validate_comparison_report(comparison_report)
        errors.extend(comparison_errors)
        warnings.extend(comparison_warnings)

    if lineage_report is not None:
        lineage_errors, lineage_warnings = validate_lineage_report(lineage_report)
        errors.extend(lineage_errors)
        warnings.extend(lineage_warnings)

    if formula_ready_result is not None:
        formula_ready_errors, formula_ready_warnings = validate_formula_ready_result(formula_ready_result)
        errors.extend(formula_ready_errors)
        warnings.extend(formula_ready_warnings)

        vs_result_errors, vs_result_warnings = validate_formula_ready_vs_result(formula_ready_result)
        errors.extend(vs_result_errors)
        warnings.extend(vs_result_warnings)

    if errors:
        print("anti-cheat errors:")
        for error in errors:
            print(f"- {error}")
        return False

    print("clean")
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Anti-cheat for earthworks review reader")
    parser.add_argument("--normalized-json", required=True, help="Path to review_values_normalized.json")
    parser.add_argument(
        "--calculator-input",
        default=None,
        help="Optional path to earthworks_calculation_input.json",
    )
    parser.add_argument(
        "--calculation-result-dir",
        default=None,
        help="Optional path to calculation_result directory",
    )
    parser.add_argument(
        "--comparison-report",
        default=None,
        help="Optional path to calculation_comparison_report.md",
    )
    parser.add_argument(
        "--lineage-report",
        default=None,
        help="Optional path to input_lineage_report.json",
    )
    parser.add_argument(
        "--formula-ready-result",
        default=None,
        help="Optional path to formula_ready_result.json",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return 0 if run_anti_cheat(
        args.normalized_json,
        args.calculator_input,
        args.calculation_result_dir,
        args.comparison_report,
        args.lineage_report,
        args.formula_ready_result,
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
