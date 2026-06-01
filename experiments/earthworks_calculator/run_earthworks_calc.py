from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from earthworks_calculator import EarthworksInput, calculate_earthworks


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
PRICING_DIR = REPO_ROOT / "experiments" / "pricing"
if str(PRICING_DIR) not in sys.path:
    sys.path.insert(0, str(PRICING_DIR))

from live_pricing import apply_live_pricing, price_sources_markdown, pricing_mode  # noqa: E402

CASES_DIR = BASE_DIR / "cases"
DEFAULT_CASE_DIR = CASES_DIR / "usv_yusupovo_village"
OUTPUT_DIR = BASE_DIR / "output"


def resolve_case_path(raw_path: str | None = None) -> tuple[str, Path, Path | None]:
    case_path = Path(raw_path) if raw_path else DEFAULT_CASE_DIR
    if not case_path.is_absolute():
        case_path = Path.cwd() / case_path
    case_path = case_path.resolve()

    if case_path.is_dir():
        case_name = case_path.name
        input_path = case_path / "input.json"
        expected_path = case_path / "expected.json"
        return case_name, input_path, expected_path if expected_path.exists() else None

    if case_path.name != "input.json":
        raise ValueError("Pass a case directory or a path to input.json")

    case_name = case_path.parent.name
    expected_path = case_path.parent / "expected.json"
    return case_name, case_path, expected_path if expected_path.exists() else None


def load_input(path: Path) -> EarthworksInput:
    with path.open("r", encoding="utf-8") as file:
        raw_data = json.load(file)
    raw_data.pop("pricing", None)
    return EarthworksInput.from_dict(raw_data)


def load_raw_input(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_expected(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")


def compare_with_expected(
    calculation: dict[str, Any],
    expected: dict[str, Any],
    tolerance: float = 0.001,
) -> list[dict[str, Any]]:
    comparison = []

    def append_comparison(
        key: str,
        expected_value: Any,
        actual_value: Any,
    ) -> None:
        if isinstance(expected_value, int) and isinstance(actual_value, int):
            is_ok = actual_value == expected_value
            diff = actual_value - expected_value
        elif isinstance(expected_value, (int, float)) and isinstance(
            actual_value, (int, float)
        ):
            diff = round(actual_value - expected_value, 6)
            is_ok = abs(diff) <= tolerance
        else:
            diff = None
            is_ok = actual_value == expected_value

        comparison.append(
            {
                "key": key,
                "expected": expected_value,
                "actual": actual_value,
                "diff": diff,
                "status": "ok" if is_ok else "mismatch",
            }
        )

    volume_result = calculation["volume_result"]
    internal_totals = calculation["internal_totals"]
    lines_by_code = {line["code"]: line for line in calculation["estimate_lines"]}
    merged_top_level = {**volume_result, **internal_totals}

    for section, expected_values in expected.items():
        if section == "volumes":
            for key, expected_value in expected_values.items():
                append_comparison(f"volumes.{key}", expected_value, volume_result.get(key))
        elif section == "internal_totals":
            for key, expected_value in expected_values.items():
                append_comparison(
                    f"internal_totals.{key}",
                    expected_value,
                    internal_totals.get(key),
                )
        elif section == "estimate_lines":
            for line_code, line_expected in expected_values.items():
                actual_line = lines_by_code.get(line_code, {})
                for key, expected_value in line_expected.items():
                    append_comparison(
                        f"estimate_lines.{line_code}.{key}",
                        expected_value,
                        actual_line.get(key),
                    )
        else:
            append_comparison(section, expected_values, merged_top_level.get(section))

    return comparison


def format_comparison_markdown(comparison: list[dict[str, Any]]) -> list[str]:
    if not comparison:
        return ["Expected values are not provided for this case."]

    lines = [
        "| Показатель | Ожидание | Получено | Разница | Статус |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for item in comparison:
        diff = "" if item["diff"] is None else item["diff"]
        lines.append(
            f"| `{item['key']}` | `{item['expected']}` | `{item['actual']}` | `{diff}` | `{item['status']}` |"
        )
    return lines


def format_dict_table(rows: dict[str, Any]) -> list[str]:
    lines = ["| Показатель | Значение |", "| --- | ---: |"]
    for key, value in rows.items():
        lines.append(f"| `{key}` | `{value}` |")
    return lines


def format_estimate_lines_markdown(lines_data: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| code | name | quantity | unit | material_unit_price | material_total | work_unit_price | work_total | line_total |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for line in lines_data:
        lines.append(
            "| "
            f"`{line['code']}` | "
            f"{line['name']} | "
            f"`{line['quantity']}` | "
            f"`{line['unit']}` | "
            f"`{line['material_unit_price']}` | "
            f"`{line['material_total']}` | "
            f"`{line['work_unit_price']}` | "
            f"`{line['work_total']}` | "
            f"`{line['line_total']}` |"
        )
    return lines


def format_markdown(
    case_name: str,
    input_data: EarthworksInput,
    calculation: dict[str, Any],
    comparison: list[dict[str, Any]],
) -> str:
    inputs = input_data.to_dict()
    input_lines = [
        f"- `{key}`: `{value}`" for key, value in inputs.items() if value is not None
    ]

    volume_lines = format_dict_table(calculation["volume_result"])
    estimate_lines = format_estimate_lines_markdown(calculation["estimate_lines"])
    totals_lines = format_dict_table(calculation["internal_totals"])
    comparison_lines = format_comparison_markdown(comparison)
    pricing_sections = []
    if calculation.get("pricing_summary", {}).get("mode") == "price_registry_with_fallback":
        pricing_sections = [
            "",
            *price_sources_markdown(calculation["estimate_lines"]),
            "",
            "## Pricing summary",
            *format_dict_table(calculation["pricing_summary"]),
        ]

    return "\n".join(
        [
            f"# Расчёт земляных работ: {case_name}",
            "",
            f"Проект: `{input_data.project_name}`",
            "",
            "## Входные параметры",
            *input_lines,
            "",
            "## Формулы",
            "- Ручная доработка котлована: `manual_pit_volume = pit_area_m2 * manual_refinement_depth_m`",
            "- Объём траншей: `trench_volume = trench_length_m * trench_depth_m * trench_width_m` или готовый `trench_volume_m3`",
            "- Общая ручная разработка: `manual_excavation_total = manual_pit_volume + trench_volume`",
            "- Песок под котлован: `compacted_sand_base = sand_base_volume_m3 * sand_compaction_coeff`",
            "- Песок в траншеи: `compacted_sand_trenches = trench_volume_m3 * sand_compaction_coeff`",
            "- Общий песок: `sand_total = compacted_sand_base + compacted_sand_trenches`",
            "- Песок к заказу: `sand_order_volume = ceil(sand_total / sand_truck_step_m3) * sand_truck_step_m3`",
            "- Геотекстиль: `geotextile_with_overlap = geotextile_area_m2 * geotextile_overlap_coeff`",
            "- Рулоны геотекстиля: `geotextile_rolls = ceil(geotextile_with_overlap / geotextile_roll_area_m2)`",
            "- Строка серой сметы: `material_total = quantity * material_unit_price`, `work_total = quantity * work_unit_price`",
            "- Итог раздела: `internal_section_total = internal_materials_total + internal_works_total`",
            "",
            "## Объёмы",
            *volume_lines,
            "",
            "## Строки серой внутренней сметы",
            *estimate_lines,
            "",
            "## Итоги серой внутренней сметы",
            *totals_lines,
            *pricing_sections,
            "",
            "## Проверка с расчётом Елены",
            *comparison_lines,
            "",
        ]
    )


def save_markdown(
    path: Path,
    case_name: str,
    input_data: EarthworksInput,
    calculation: dict[str, Any],
    comparison: list[dict[str, Any]],
) -> None:
    path.write_text(
        format_markdown(case_name, input_data, calculation, comparison),
        encoding="utf-8",
    )


def run(raw_case_path: str | None = None) -> dict[str, Any]:
    case_name, input_path, expected_path = resolve_case_path(raw_case_path)
    case_output_dir = OUTPUT_DIR / case_name
    case_output_dir.mkdir(parents=True, exist_ok=True)

    raw_input = load_raw_input(input_path)
    input_data = EarthworksInput.from_dict({k: v for k, v in raw_input.items() if k != "pricing"})
    expected = load_expected(expected_path)
    calculation = calculate_earthworks(input_data)
    calculation = apply_live_pricing(calculation, raw_input, REPO_ROOT, totals_key="internal_totals")
    comparison = compare_with_expected(calculation, expected)
    is_live_pricing = pricing_mode(raw_input) == "price_registry_with_fallback"

    result_payload = {
        "case_name": case_name,
        "input_path": str(input_path),
        "expected_path": str(expected_path) if expected_path else None,
        "inputs": calculation["inputs"],
        "volume_result": calculation["volume_result"],
        "estimate_lines": calculation["estimate_lines"],
        "internal_totals": calculation["internal_totals"],
        "expected": expected,
        "comparison": comparison,
    }
    if is_live_pricing:
        result_payload["pricing_summary"] = calculation.get("pricing_summary", {})

    save_json(case_output_dir / "earthworks_result.json", result_payload)
    save_markdown(
        case_output_dir / "earthworks_result.md",
        case_name,
        input_data,
        calculation,
        comparison,
    )
    if expected_path is None:
        save_json(input_path.parent / "result.json", result_payload)
        save_markdown(input_path.parent / "result.md", case_name, input_data, calculation, comparison)

    return calculation


if __name__ == "__main__":
    calculation_result = run(sys.argv[1] if len(sys.argv) > 1 else None)
    print(
        json.dumps(
            {
                "volume_result": calculation_result["volume_result"],
                "internal_totals": calculation_result["internal_totals"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
