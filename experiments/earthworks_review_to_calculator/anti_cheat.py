from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from constants import (
    DETAIL_REQUIRED_COMM_NAMES,
    DETAIL_REQUIRED_TRENCH_NAMES,
    PRICE_EXPECTED_MIN_ROWS,
    PRICE_REQUIRED_LINES,
    REQUIRED_PARAMETERS,
)
from normalization import cell_text


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_anti_cheat(normalized_json_path: str | Path) -> bool:
    path = Path(normalized_json_path)
    data = load_json(path)

    errors: list[str] = []
    parameters = data.get("parameters", {})
    prices = data.get("prices", [])
    details = data.get("details", {})

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

    summary = details.get("summary", {})
    if summary.get("communications_total_length_m") != 115.0:
        errors.append(f"communications_total_length_m expected 115.0, got {summary.get('communications_total_length_m')}")

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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return 0 if run_anti_cheat(args.normalized_json) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

