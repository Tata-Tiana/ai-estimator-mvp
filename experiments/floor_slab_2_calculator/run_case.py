from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from calculator import calculate_floor_slab_2


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
PRICING_DIR = REPO_ROOT / "experiments" / "pricing"
if str(PRICING_DIR) not in sys.path:
    sys.path.insert(0, str(PRICING_DIR))

from live_pricing import apply_live_pricing, price_sources_markdown, pricing_mode  # noqa: E402


COMPARE_LINE_FIELDS = [
    "name",
    "unit",
    "line_type",
    "quantity_raw",
    "quantity_display",
    "material_unit_price",
    "material_total_raw",
    "material_total",
    "work_unit_price",
    "work_total_raw",
    "work_total",
    "line_total_raw",
    "line_total",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_expected(path: Path) -> dict[str, Any]:
    return load_json(path) if path.exists() else {}


def values_equal(actual: Any, expected: Any) -> bool:
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return abs(float(actual) - float(expected)) < 0.00001
    return actual == expected


def compare_result(result: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for key, expected_value in expected.get("totals", {}).items():
        actual_value = result.get("totals", {}).get(key)
        checks.append(
            {
                "scope": "totals",
                "code": key,
                "field": key,
                "expected": expected_value,
                "actual": actual_value,
                "status": "ok" if values_equal(actual_value, expected_value) else "mismatch",
            }
        )

    actual_lines = {line["code"]: line for line in result.get("estimate_lines", [])}
    for expected_line in expected.get("estimate_lines", []):
        code = expected_line["code"]
        actual_line = actual_lines.get(code)
        if actual_line is None:
            checks.append(
                {
                    "scope": "estimate_lines",
                    "code": code,
                    "field": "__line__",
                    "expected": "present",
                    "actual": "missing",
                    "status": "mismatch",
                }
            )
            continue
        for field in COMPARE_LINE_FIELDS:
            if field not in expected_line:
                continue
            expected_value = expected_line[field]
            actual_value = actual_line.get(field)
            checks.append(
                {
                    "scope": "estimate_lines",
                    "code": code,
                    "field": field,
                    "expected": expected_value,
                    "actual": actual_value,
                    "status": "ok" if values_equal(actual_value, expected_value) else "mismatch",
                }
            )

    ok_count = sum(1 for check in checks if check["status"] == "ok")
    mismatch_count = sum(1 for check in checks if check["status"] != "ok")
    return {
        "status": "ok" if mismatch_count == 0 else "mismatch",
        "ok_count": ok_count,
        "mismatch_count": mismatch_count,
        "checks": checks,
    }


def money(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number.is_integer():
        return f"{int(number):,}".replace(",", " ")
    return f"{number:,.2f}".replace(",", " ").rstrip("0").rstrip(".")


def build_markdown(result: dict[str, Any]) -> str:
    comparison = result.get("comparison", {})
    lines = [
        f"# {result['section_title']}",
        "",
        "## Inputs",
        "",
        f"- project_name: `{result['project_name']}`",
        f"- slab_area_m2: `{result['inputs']['slab_area_m2']}`",
        f"- slab_edge_perimeter_m: `{result['inputs']['slab_edge_perimeter_m']}`",
        f"- concrete_placing_volume_m3: `{result['inputs']['concrete_placing_volume_m3']}`",
        "",
        "## Calculation Blocks",
        "",
    ]
    for block_name, block in result.get("calculation_blocks", {}).items():
        lines.extend([f"### {block_name}", ""])
        if isinstance(block, dict):
            for key, value in block.items():
                if key == "items":
                    lines.append(f"- {key}: {len(value)} items")
                else:
                    lines.append(f"- {key}: `{value}`")
        lines.append("")

    lines.extend(
        [
            "## Estimate Lines",
            "",
            "| # | code | name | unit | qty raw | qty display | material | work | total |",
            "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for index, line in enumerate(result.get("estimate_lines", []), start=1):
        lines.append(
            "| "
            f"{index} | `{line['code']}` | {line['name']} | {line['unit']} | "
            f"{money(line['quantity_raw'])} | {money(line['quantity_display'])} | "
            f"{money(line['material_total'])} | {money(line['work_total'])} | {money(line['line_total'])} |"
        )

    lines.extend(["", "## Post-Line Explanations", ""])
    for index, line in enumerate(result.get("estimate_lines", []), start=1):
        lines.extend(
            [
                f"### {index}. {line['name']}",
                "",
                f"- Тип строки: `{line['line_type']}`",
                f"- Количество raw/display: `{line['quantity_raw']}` / `{line['quantity_display']}`",
                f"- Материалы raw/display: `{line['material_total_raw']}` / `{line['material_total']}`",
                f"- Работы raw/display: `{line['work_total_raw']}` / `{line['work_total']}`",
                f"- Итого raw/display: `{line['line_total_raw']}` / `{line['line_total']}`",
            ]
        )
        for note in line.get("notes", []):
            lines.append(f"- Примечание: {note}")
        lines.append("")

    totals = result.get("totals", {})
    lines.extend(
        [
            "## Totals",
            "",
            f"- internal_materials_total_raw: `{totals.get('internal_materials_total_raw')}`",
            f"- internal_materials_total: `{totals.get('internal_materials_total')}`",
            f"- internal_works_total_raw: `{totals.get('internal_works_total_raw')}`",
            f"- internal_works_total: `{totals.get('internal_works_total')}`",
            f"- internal_section_total_raw: `{totals.get('internal_section_total_raw')}`",
            f"- internal_section_total: `{totals.get('internal_section_total')}`",
            f"- sum_of_displayed_line_material_totals: `{totals.get('sum_of_displayed_line_material_totals')}`",
            f"- sum_of_displayed_line_work_totals: `{totals.get('sum_of_displayed_line_work_totals')}`",
            f"- sum_of_displayed_line_totals: `{totals.get('sum_of_displayed_line_totals')}`",
            "",
            "## Warnings",
            "",
        ]
    )
    lines.extend([f"- {warning}" for warning in result.get("warnings", [])] or ["- Нет предупреждений."])
    if result.get("pricing_summary", {}).get("mode") == "price_registry_with_fallback":
        lines.extend(["", *price_sources_markdown(result.get("estimate_lines", [])), "", "## Pricing summary", ""])
        for key, value in result.get("pricing_summary", {}).items():
            lines.append(f"- {key}: `{value}`")

    lines.extend(
        [
            "",
            "## Comparison",
            "",
            f"- status: `{comparison.get('status')}`",
            f"- ok: `{comparison.get('ok_count')}`",
            f"- mismatch: `{comparison.get('mismatch_count')}`",
            "",
            "| scope | code | field | expected | actual | status |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for check in comparison.get("checks", []):
        lines.append(
            "| "
            f"{check['scope']} | `{check['code']}` | `{check['field']}` | "
            f"{check['expected']} | {check['actual']} | {check['status']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python run_case.py path/to/case")
        return 2

    case_dir = Path(sys.argv[1]).resolve()
    input_path = case_dir / "input.json"
    expected_path = case_dir / "expected.json"
    result_path = case_dir / "result.json"
    result_md_path = case_dir / "result.md"

    input_data = load_json(input_path)
    result = calculate_floor_slab_2(input_data)
    result = apply_live_pricing(result, input_data, REPO_ROOT, totals_key="totals")
    expected = load_expected(expected_path)
    comparison = compare_result(result, expected)
    is_live_pricing = pricing_mode(input_data) == "price_registry_with_fallback"
    if not is_live_pricing:
        result.pop("pricing_summary", None)
    result["expected"] = expected
    result["comparison"] = comparison

    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    result_md_path.write_text(build_markdown(result), encoding="utf-8")

    print(f"result: {result_path}")
    print(f"report: {result_md_path}")
    print(f"comparison: {comparison['ok_count']} ok / {comparison['mismatch_count']} mismatch")
    return 0 if comparison["mismatch_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
