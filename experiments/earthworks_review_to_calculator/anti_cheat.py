from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from constants import (
    CONSUMABLES_PRICE_KEY,
    DETAIL_REQUIRED_COMM_NAMES,
    DETAIL_REQUIRED_TRENCH_NAMES,
    DEFAULT_COMMUNICATIONS_METHOD,
    DEFAULT_EXCAVATOR_SHIFTS_METHOD,
    DEFAULT_MANUAL_EXCAVATION_METHOD,
    PRICE_EXPECTED_MIN_ROWS,
    PRICE_REQUIRED_LINES,
    PRICE_TO_INTERNAL_KEY_MAP,
    REQUIRED_PARAMETERS,
)
from normalization import cell_text


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


def _expected_internal_prices(prices: list[dict[str, Any]]) -> tuple[dict[str, float], float | None]:
    internal_prices: dict[str, float] = {}
    consumables_amount: float | None = None

    for row in prices:
        estimate_line = str(row.get("estimate_line", "")).strip()
        price_role = str(row.get("price_role", "")).strip()
        selected_price = _as_number(row.get("selected_price"))
        if selected_price is None:
            continue

        if (estimate_line, price_role) == CONSUMABLES_PRICE_KEY:
            consumables_amount = selected_price
            continue

        internal_key = PRICE_TO_INTERNAL_KEY_MAP.get((estimate_line, price_role))
        if internal_key is not None:
            internal_prices[internal_key] = selected_price

    return internal_prices, consumables_amount


def validate_normalized_review(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    parameters = data.get("parameters", {})
    prices = data.get("prices", [])
    details = data.get("details", {})
    summary = details.get("summary", {})

    for key in REQUIRED_PARAMETERS:
        if key not in parameters:
            errors.append(f"missing parameter: {key}")

    expected_values = {
        "pit_area_m2": 322.5,
        "pit_excavation_depth_m": 0.3,
        "sand_base_volume_m3": 96.6,
        "trench_volume_m3": 32.38,
        "geotextile_area_m2": 320.0,
        "geotextile_laying_area_m2": 320.0,
        "communications_length_m": 115.0,
    }
    for key, expected in expected_values.items():
        actual = parameters.get(key, {}).get("value")
        if actual != expected:
            errors.append(f"{key} expected {expected}, got {actual}")

    if len(prices) < PRICE_EXPECTED_MIN_ROWS:
        errors.append(f"prices rows expected >= {PRICE_EXPECTED_MIN_ROWS}, got {len(prices)}")

    price_map = {row.get("estimate_line"): row for row in prices}
    for required_line in PRICE_REQUIRED_LINES:
        if required_line not in price_map:
            errors.append(f"missing price row: {required_line}")

    if price_map.get("Расходные материалы", {}).get("selected_price") != 23447.18:
        errors.append("Расходные материалы selected_price must be 23447.18")
    if price_map.get("Геотекстиль Дорнит 300 г.м2", {}).get("selected_price") != 109.0:
        errors.append("Геотекстиль Дорнит 300 г.м2 selected_price must be 109.0")

    trench_routes = details.get("trench_routes", [])
    communications = details.get("communications_pipe_items", [])
    if len(trench_routes) != 4:
        errors.append(f"trench_routes count expected 4, got {len(trench_routes)}")
    if len(communications) != 4:
        errors.append(f"communications_pipe_items count expected 4, got {len(communications)}")

    trench_names = [cell_text(row.get("name")) for row in trench_routes]
    for required_name in DETAIL_REQUIRED_TRENCH_NAMES:
        if required_name not in trench_names:
            errors.append(f"missing trench name: {required_name}")

    comm_names = [cell_text(row.get("name")) for row in communications]
    for required_name in DETAIL_REQUIRED_COMM_NAMES:
        if required_name not in comm_names:
            errors.append(f"missing communication item: {required_name}")

    for row in communications:
        if row.get("diameter_mm") != 110:
            errors.append(f"communication diameter must be 110: {row.get('name')}")

    if summary.get("communications_total_length_m") != 115.0:
        errors.append(
            f"communications_total_length_m expected 115.0, got {summary.get('communications_total_length_m')}"
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

    expected_internal_prices, expected_consumables_amount = _expected_internal_prices(prices)

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

    expected_excavator_method = (
        DEFAULT_EXCAVATOR_SHIFTS_METHOD if pit_excavation_depth_m is not None else "legacy_manual_shifts"
    )
    expected_manual_method = (
        DEFAULT_MANUAL_EXCAVATION_METHOD
        if (details.get("trench_routes") or trench_volume_m3 is not None)
        else "legacy_manual_override"
    )
    expected_communications_method = (
        "legacy_direct_length" if communications_override_used else DEFAULT_COMMUNICATIONS_METHOD
    )

    if calculator_input.get("project_name") in {None, ""}:
        errors.append("project_name is required")

    if _as_number(calculator_input.get("pit_area_m2")) != pit_area_m2:
        errors.append(f"pit_area_m2 expected {pit_area_m2}, got {calculator_input.get('pit_area_m2')}")
    if _as_number(calculator_input.get("pit_excavation_depth_m")) != pit_excavation_depth_m:
        errors.append(
            f"pit_excavation_depth_m expected {pit_excavation_depth_m}, got {calculator_input.get('pit_excavation_depth_m')}"
        )
    if _as_number(calculator_input.get("sand_base_volume_m3")) != sand_base_volume_m3:
        errors.append(
            f"sand_base_volume_m3 expected {sand_base_volume_m3}, got {calculator_input.get('sand_base_volume_m3')}"
        )
    if _as_number(calculator_input.get("trench_volume_m3")) != trench_volume_m3:
        errors.append(
            f"trench_volume_m3 expected {trench_volume_m3}, got {calculator_input.get('trench_volume_m3')}"
        )
    if _as_number(calculator_input.get("geotextile_area_m2")) != geotextile_area_m2:
        errors.append(
            f"geotextile_area_m2 expected {geotextile_area_m2}, got {calculator_input.get('geotextile_area_m2')}"
        )
    if _as_number(calculator_input.get("geotextile_laying_area_m2")) != geotextile_laying_area_m2:
        errors.append(
            f"geotextile_laying_area_m2 expected {geotextile_laying_area_m2}, got {calculator_input.get('geotextile_laying_area_m2')}"
        )

    if calculator_input.get("excavator_shifts_calc_method") != expected_excavator_method:
        errors.append(
            f"excavator_shifts_calc_method expected {expected_excavator_method}, got {calculator_input.get('excavator_shifts_calc_method')}"
        )
    if calculator_input.get("manual_excavation_calc_method") != expected_manual_method:
        errors.append(
            f"manual_excavation_calc_method expected {expected_manual_method}, got {calculator_input.get('manual_excavation_calc_method')}"
        )
    if calculator_input.get("communications_length_calc_method") != expected_communications_method:
        errors.append(
            f"communications_length_calc_method expected {expected_communications_method}, got {calculator_input.get('communications_length_calc_method')}"
        )

    if expected_communications_method == DEFAULT_COMMUNICATIONS_METHOD:
        if _as_number(calculator_input.get("communications_length_m")) not in {0.0, 0}:
            errors.append(
                f"communications_length_m expected 0 for pipe_items mode, got {calculator_input.get('communications_length_m')}"
            )
    else:
        if _as_number(calculator_input.get("communications_length_m")) != communications_value:
            errors.append(
                f"communications_length_m expected {communications_value}, got {calculator_input.get('communications_length_m')}"
            )

    if expected_manual_method == DEFAULT_MANUAL_EXCAVATION_METHOD:
        if calculator_input.get("manual_excavation_quantity_for_estimate_m3") is not None:
            errors.append(
                "manual_excavation_quantity_for_estimate_m3 must be null in standard_routes mode"
            )

    if expected_excavator_method == DEFAULT_EXCAVATOR_SHIFTS_METHOD:
        if _as_number(calculator_input.get("excavator_shifts")) not in {0.0, 0}:
            errors.append(
                f"excavator_shifts expected 0 in standard_volume_productivity mode, got {calculator_input.get('excavator_shifts')}"
            )

    internal_prices = calculator_input.get("internal_prices", {})
    if not isinstance(internal_prices, dict) or not internal_prices:
        errors.append("internal_prices must be a non-empty mapping")
    else:
        for key, expected_value in expected_internal_prices.items():
            actual = _as_number(internal_prices.get(key))
            if actual != expected_value:
                errors.append(f"internal_prices.{key} expected {expected_value}, got {actual}")

    if expected_consumables_amount is None:
        errors.append("consumables_amount must be mapped from review sheet")
    elif _as_number(calculator_input.get("consumables_amount")) != expected_consumables_amount:
        errors.append(
            f"consumables_amount expected {expected_consumables_amount}, got {calculator_input.get('consumables_amount')}"
        )

    trench_routes = calculator_input.get("trench_routes") or []
    if expected_manual_method == DEFAULT_MANUAL_EXCAVATION_METHOD:
        if len(trench_routes) != 4:
            errors.append(f"trench_routes count expected 4, got {len(trench_routes)}")
        trench_names = [cell_text(row.get("name")) for row in trench_routes]
        for required_name in DETAIL_REQUIRED_TRENCH_NAMES:
            if required_name not in trench_names:
                errors.append(f"missing trench name in calculator input: {required_name}")

    communications_pipe_items = calculator_input.get("communications_pipe_items") or []
    if expected_communications_method == DEFAULT_COMMUNICATIONS_METHOD:
        if len(communications_pipe_items) != 4:
            errors.append(
                f"communications_pipe_items count expected 4, got {len(communications_pipe_items)}"
            )
        comm_names = [cell_text(row.get("name")) for row in communications_pipe_items]
        for required_name in DETAIL_REQUIRED_COMM_NAMES:
            if required_name not in comm_names:
                errors.append(f"missing communication item in calculator input: {required_name}")

        for row in communications_pipe_items:
            if _as_number(row.get("diameter_mm")) != 110:
                errors.append(f"calculator input communication diameter must be 110: {row.get('name')}")

        total_length = sum(
            _as_number(row.get("total_length_m")) or 0.0
            for row in communications_pipe_items
            if row.get("include_in_communications", True)
        )
        if total_length != 115.0:
            errors.append(f"communications total length expected 115.0, got {total_length}")

    return errors, warnings


def run_anti_cheat(
    normalized_json_path: str | Path,
    calculator_input_path: str | Path | None = None,
) -> bool:
    normalized_path = Path(normalized_json_path)
    normalized_data = load_json(normalized_path)

    errors, warnings = validate_normalized_review(normalized_data)

    if calculator_input_path is not None:
        calculator_input = load_json(Path(calculator_input_path))
        calc_errors, calc_warnings = validate_calculator_input(normalized_data, calculator_input)
        errors.extend(calc_errors)
        warnings.extend(calc_warnings)

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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return 0 if run_anti_cheat(args.normalized_json, args.calculator_input) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

