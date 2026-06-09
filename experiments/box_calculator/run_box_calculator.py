from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from box_calculator import calculate_box


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")


def resolve_case_path(raw_path: str) -> tuple[str, Path, Path | None]:
    case_path = Path(raw_path)
    if not case_path.is_absolute():
        case_path = Path.cwd() / case_path
    case_path = case_path.resolve()
    if not case_path.is_dir():
        raise ValueError("Pass a case directory")
    expected_path = case_path / "expected.json"
    return case_path.name, case_path / "input.json", expected_path if expected_path.exists() else None


def get_nested_value(data: dict[str, Any], dotted_path: str) -> Any:
    current: Any = data
    for part in dotted_path.split("."):
        if isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def compare_with_expected(result: dict[str, Any], expected: dict[str, Any]) -> list[dict[str, Any]]:
    comparison = []
    for key, expected_value in expected.items():
        actual_value = get_nested_value(result, key)
        if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
            diff = round(actual_value - expected_value, 6)
            status = "ok" if abs(diff) <= 0.001 else "mismatch"
        else:
            diff = None
            status = "ok" if actual_value == expected_value else "mismatch"
        comparison.append(
            {
                "key": key,
                "expected": expected_value,
                "actual": actual_value,
                "diff": diff,
                "status": status,
            }
        )
    return comparison


def format_money(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return f"{int(value)}"
    return str(value)


def format_markdown(result: dict[str, Any], comparison: list[dict[str, Any]]) -> str:
    allocation = result.get("recommended_metal_delivery_allocation") or {}
    section_rows = [
        "| Раздел | Вес металла, кг | Накопленный вес, кг | Машин доставки | Сумма доставки |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for item in allocation.get("sections", []):
        section_rows.append(
            "| "
            f"{item['section_name']} | "
            f"{format_money(item['metal_weight_kg'])} | "
            f"{format_money(item['cumulative_weight_kg'])} | "
            f"{item['allocated_trucks']} | "
            f"{format_money(item['delivery_cost'])} |"
        )

    comparison_rows = [
        "| Показатель | Ожидание | Получено | Разница | Статус |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for item in comparison:
        diff = "" if item["diff"] is None else item["diff"]
        comparison_rows.append(
            f"| `{item['key']}` | `{item['expected']}` | `{item['actual']}` | `{diff}` | `{item['status']}` |"
        )

    warnings = result.get("warnings", [])
    warning_lines = [f"- {warning}" for warning in warnings] if warnings else ["Предупреждений нет."]

    return "\n".join(
        [
            "# Box calculator result",
            "",
            f"Проект: `{result.get('project_name', '')}`",
            "",
            "## Доставка арматуры и металла",
            "",
            f"- Общий вес металла коробки: `{allocation.get('total_box_metal_weight_kg')}` кг",
            f"- Грузоподъёмность машины: `{allocation.get('capacity_kg')}` кг",
            f"- Количество машин: `{allocation.get('total_trucks')}`",
            f"- Цена за машину: `{allocation.get('unit_price')}`",
            f"- Итоговая стоимость доставки: `{allocation.get('total_delivery_cost')}`",
            "",
            *section_rows,
            "",
            "## Totals policy",
            "",
            "- Allocation показан отдельно как recommended block.",
            "- Section totals не пересчитываются.",
            "- Доставка металла не добавляется поверх legacy totals.",
            "",
            "## Warnings",
            "",
            *warning_lines,
            "",
            "## Проверка",
            "",
            *comparison_rows,
            "",
        ]
    )


def run(raw_case_path: str) -> dict[str, Any]:
    case_name, input_path, expected_path = resolve_case_path(raw_case_path)
    input_data = load_json(input_path)
    expected = load_json(expected_path) if expected_path else {}
    result = calculate_box(input_data)
    comparison = compare_with_expected(result, expected)
    result_payload = {
        **result,
        "case_name": case_name,
        "input_path": str(input_path),
        "expected_path": str(expected_path) if expected_path else None,
        "expected": expected,
        "comparison": comparison,
    }

    case_dir = input_path.parent
    output_dir = OUTPUT_DIR / case_name
    save_json(case_dir / "result.json", result_payload)
    save_json(output_dir / "result.json", result_payload)
    markdown = format_markdown(result_payload, comparison)
    (case_dir / "result.md").write_text(markdown, encoding="utf-8")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "result.md").write_text(markdown, encoding="utf-8")
    return result_payload


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: run_box_calculator.py <case_dir>")
    payload = run(sys.argv[1])
    ok_count = sum(1 for item in payload["comparison"] if item["status"] == "ok")
    mismatch_count = sum(1 for item in payload["comparison"] if item["status"] != "ok")
    print(json.dumps(payload["recommended_metal_delivery_allocation"], ensure_ascii=False, indent=2))
    print(f"comparison: {ok_count} ok / {mismatch_count} mismatch")
