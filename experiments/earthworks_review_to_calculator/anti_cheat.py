from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from constants import (
    DEFAULT_COMMUNICATIONS_METHOD,
    DEFAULT_EXCAVATOR_SHIFTS_METHOD,
    DEFAULT_MANUAL_EXCAVATION_METHOD,
    REQUIRED_CALC_PRICE_KEYS,
    REQUIRED_PARAMETERS,
)
from normalization import cell_text


VALID_SELECTED_PRICE_SOURCES = {"price_registry", "fallback"}
VALID_EFFECTIVE_PRICE_SOURCES = {"price_registry", "fallback", "manual_override"}


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
    expected_communications_method = DEFAULT_COMMUNICATIONS_METHOD

    if calculator_input.get("project_name") in {None, ""}:
        errors.append("project_name is required")

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
    else:
        if _as_number(calculator_input.get("communications_length_m")) != communications_value:
            errors.append("communications_length_m must match normalized review value")

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


def run_anti_cheat(
    normalized_json_path: str | Path,
    calculator_input_path: str | Path | None = None,
    calculation_result_dir: str | Path | None = None,
    comparison_report: str | Path | None = None,
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return 0 if run_anti_cheat(args.normalized_json, args.calculator_input, args.calculation_result_dir, args.comparison_report) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
