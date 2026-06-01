from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from calculator import calculate_schiedel_vent_channels


COMPARE_LINE_FIELDS = [
    "name",
    "unit",
    "line_type",
    "quantity_raw",
    "quantity_display",
    "quantity_source",
    "price_code",
]

COMPARE_COST_FIELDS = [
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


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
                "status": "ok" if actual_value == expected_value else "mismatch",
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
            expected_value = expected_line.get(field)
            actual_value = actual_line.get(field)
            checks.append(
                {
                    "scope": "estimate_lines",
                    "code": code,
                    "field": field,
                    "expected": expected_value,
                    "actual": actual_value,
                    "status": "ok" if actual_value == expected_value else "mismatch",
                }
            )
        for field in COMPARE_COST_FIELDS:
            if field not in expected_line.get("internal_cost", {}):
                continue
            expected_value = expected_line["internal_cost"].get(field)
            actual_value = actual_line.get("internal_cost", {}).get(field)
            checks.append(
                {
                    "scope": "estimate_lines",
                    "code": code,
                    "field": f"internal_cost.{field}",
                    "expected": expected_value,
                    "actual": actual_value,
                    "status": "ok" if actual_value == expected_value else "mismatch",
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
        number = float(str(value))
    except ValueError:
        return str(value)
    if number.is_integer():
        return f"{int(number):,}".replace(",", " ")
    return f"{number:,.2f}".replace(",", " ").rstrip("0").rstrip(".")


def build_markdown(result: dict[str, Any]) -> str:
    comparison = result.get("comparison", {})
    totals = result["totals"]
    is_live_pricing = (
        result.get("pricing_summary", {}).get("mode") == "price_registry_with_fallback"
    )
    lines = [
        "# Расчётный отчёт: ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel",
        "",
        "AI не используется для расчёта. Калькулятор считает только серую внутреннюю себестоимость.",
        "Клиентская часть и коммерческие коэффициенты вне текущего scope.",
        "",
        "## Исходные параметры раздела",
        "",
        f"- project_name: `{result['project_name']}`",
        f"- schiedel_masonry_total_length_m: `{result['inputs']['schiedel_masonry_total_length_m']}`",
        f"- schiedel_vent_channel_2x_count: `{result['inputs']['schiedel_vent_channel_2x_count']}`",
        f"- schiedel_vent_channel_3x_count: `{result['inputs']['schiedel_vent_channel_3x_count']}`",
        f"- schiedel_delivery_trips: `{result['inputs']['schiedel_delivery_trips']}`",
        "",
        "## Важные правила",
        "",
        "- Кладка считается от raw `15.82 мп`, не от отображаемых `16 мп`.",
        "- Количества `24 шт` и `8 шт` по материалам Schiedel являются ручными/спецификационными значениями.",
        "- Контрольные правые числа сохранены как справочные и не используются для quantity.",
        "- Расходные материалы считаются как `3%` от прямой базы `114456`.",
        "- Последние 4 строки являются нулевыми строками структуры Excel.",
        "",
        "## Построчный расчёт",
        "",
    ]

    for index, line in enumerate(result.get("estimate_lines", []), start=1):
        cost = line["internal_cost"]
        lines.extend(
            [
                f"### {index}. {line['name']}",
                "",
                f"- Код: `{line['code']}`",
                f"- Тип строки: `{line['line_type']}`",
                f"- Ед. изм.: `{line['unit']}`",
                f"- Количество raw/display: `{line['quantity_raw']}` / `{line['quantity_display']}`",
                f"- Источник количества: `{line['quantity_source']}`",
            ]
        )
        if line.get("price_code"):
            lines.append(f"- price_code: `{line['price_code']}`")
        if line.get("formula"):
            lines.extend(["", "Формула и контроль:"])
            for key, value in line["formula"].items():
                lines.append(f"- {key}: `{value}`")
        lines.extend(
            [
                "",
                "Итог:",
                f"- Материалы raw/display: `{cost['material_total_raw']}` / `{money(cost['material_total'])}`",
                f"- Работы raw/display: `{cost['work_total_raw']}` / `{money(cost['work_total'])}`",
                f"- Итого raw/display: `{cost['line_total_raw']}` / `{money(cost['line_total'])}`",
            ]
        )
        for note in line.get("notes", []):
            lines.append(f"- Примечание: {note}")
        lines.append("")

    lines.extend(
        [
            "## Warnings",
            "",
        ]
    )
    lines.extend([f"- {warning}" for warning in result.get("warnings", [])] or ["- Нет предупреждений."])
    if is_live_pricing:
        lines.extend(
            [
                "",
                "## Источники цен",
                "",
                "| Строка сметы | price_code | старая цена | использованная цена | источник | предупреждение |",
                "| --- | --- | ---: | ---: | --- | --- |",
            ]
        )
        for line in result.get("estimate_lines", []):
            lines.append(
                "| "
                f"{line['name']} | "
                f"`{line.get('price_code', '')}` | "
                f"`{line.get('unit_price_original', '')}` | "
                f"`{line.get('unit_price_used', '')}` | "
                f"`{line.get('unit_price_source', '')}` | "
                f"{line.get('price_warning') or ''} |"
            )
        lines.extend(
            [
                "",
                "## Pricing summary",
                "",
                "| Показатель | Значение |",
                "| --- | ---: |",
            ]
        )
        for key, value in result.get("pricing_summary", {}).items():
            lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Итоги",
            "",
            f"- Материалы: `{money(totals['internal_materials_total'])}`",
            f"- Работы: `{money(totals['internal_works_total'])}`",
            f"- Всего: `{money(totals['internal_section_total'])}`",
            f"- internal_materials_total_raw: `{totals['internal_materials_total_raw']}`",
            f"- internal_works_total_raw: `{totals['internal_works_total_raw']}`",
            f"- internal_section_total_raw: `{totals['internal_section_total_raw']}`",
            "",
            "## Проверка",
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
            f"| {check['scope']} | `{check['code']}` | `{check['field']}` | {check['expected']} | {check['actual']} | {check['status']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python run_case.py path/to/case")
        return 2

    case_dir = Path(sys.argv[1]).resolve()
    result = calculate_schiedel_vent_channels(load_json(case_dir / "input.json"))
    expected = load_expected(case_dir / "expected.json")
    comparison = compare_result(result, expected)
    is_live_pricing = (
        result.get("pricing_summary", {}).get("mode") == "price_registry_with_fallback"
    )
    if not is_live_pricing:
        result.pop("pricing_summary", None)
    result["expected"] = expected
    result["comparison"] = comparison

    dump_json(case_dir / "result.json", result)
    (case_dir / "result.md").write_text(build_markdown(result), encoding="utf-8")

    print(f"status: {comparison['status']}")
    print(f"ok: {comparison['ok_count']}")
    print(f"mismatch: {comparison['mismatch_count']}")
    for check in comparison["checks"]:
        if check["status"] != "ok":
            print(
                "mismatch: "
                f"{check['scope']} {check['code']} {check['field']} "
                f"expected={check['expected']} actual={check['actual']}"
            )
    return 0 if comparison["mismatch_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
