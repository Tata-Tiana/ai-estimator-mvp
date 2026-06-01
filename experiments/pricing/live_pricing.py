from __future__ import annotations

from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from price_reader import load_price_registry, load_project_price_overrides, resolve_price


D0 = Decimal("0")


def d(value: Any) -> Decimal:
    if value is None or value == "":
        return D0
    return value if isinstance(value, Decimal) else Decimal(str(value))


def money(value: Any) -> int:
    return int(d(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def dec_str(value: Any) -> str:
    value_dec = d(value)
    if value_dec == value_dec.to_integral_value():
        return str(value_dec.quantize(Decimal("1")))
    return format(value_dec.normalize(), "f")


def pricing_mode(input_data: dict[str, Any]) -> str:
    return (input_data.get("pricing") or {}).get("mode", "locked_case_prices")


def registry_path(input_data: dict[str, Any], repo_root: Path) -> Path:
    raw_path = (input_data.get("pricing") or {}).get(
        "registry_path",
        "output/price_registry_filled_v3.xlsx",
    )
    path = Path(raw_path)
    return path if path.is_absolute() else repo_root / path


def _line_quantity(line: dict[str, Any]) -> Decimal:
    for key in ("quantity_raw", "quantity"):
        if key in line:
            return d(line[key])
    return D0


def _flat_reprice_line(
    line: dict[str, Any],
    resolved: dict[str, Any],
) -> None:
    quantity = _line_quantity(line)
    used_price = resolved["price"]
    if used_price is None:
        return

    material_unit = d(line.get("material_unit_price"))
    work_unit = d(line.get("work_unit_price"))

    if material_unit != D0:
        material_raw = quantity * d(used_price)
        line["material_unit_price"] = float(used_price)
        line["material_total_raw"] = float(material_raw)
        line["material_total"] = money(material_raw)
    if material_unit == D0 and work_unit != D0:
        work_raw = quantity * d(used_price)
        line["work_unit_price"] = float(used_price)
        line["work_total_raw"] = float(work_raw)
        line["work_total"] = money(work_raw)
    if material_unit == D0 and work_unit == D0:
        if d(line.get("material_total_raw", line.get("material_total", 0))) != D0:
            material_raw = quantity * d(used_price)
            line["material_unit_price"] = float(used_price)
            line["material_total_raw"] = float(material_raw)
            line["material_total"] = money(material_raw)
        elif d(line.get("work_total_raw", line.get("work_total", 0))) != D0:
            work_raw = quantity * d(used_price)
            line["work_unit_price"] = float(used_price)
            line["work_total_raw"] = float(work_raw)
            line["work_total"] = money(work_raw)

    material_raw = d(line.get("material_total_raw"))
    work_raw = d(line.get("work_total_raw"))
    line_raw = material_raw + work_raw
    line["line_total_raw"] = float(line_raw)
    line["line_total"] = money(line_raw)


def _nested_reprice_line(
    line: dict[str, Any],
    resolved: dict[str, Any],
) -> None:
    cost = line["internal_cost"]
    quantity = _line_quantity(line)
    used_price = resolved["price"]
    if used_price is None:
        return

    material_unit = d(cost.get("material_unit_price"))
    work_unit = d(cost.get("work_unit_price"))

    if material_unit != D0:
        material_raw = quantity * d(used_price)
        cost["material_unit_price"] = dec_str(used_price)
        cost["material_total_raw"] = dec_str(material_raw)
        cost["material_total"] = money(material_raw)
    if material_unit == D0 and work_unit != D0:
        work_raw = quantity * d(used_price)
        cost["work_unit_price"] = dec_str(used_price)
        cost["work_total_raw"] = dec_str(work_raw)
        cost["work_total"] = money(work_raw)
    if material_unit == D0 and work_unit == D0:
        if d(cost.get("material_total_raw", cost.get("material_total", 0))) != D0:
            material_raw = quantity * d(used_price)
            cost["material_unit_price"] = dec_str(used_price)
            cost["material_total_raw"] = dec_str(material_raw)
            cost["material_total"] = money(material_raw)
        elif d(cost.get("work_total_raw", cost.get("work_total", 0))) != D0:
            work_raw = quantity * d(used_price)
            cost["work_unit_price"] = dec_str(used_price)
            cost["work_total_raw"] = dec_str(work_raw)
            cost["work_total"] = money(work_raw)

    material_raw = d(cost.get("material_total_raw"))
    work_raw = d(cost.get("work_total_raw"))
    line_raw = material_raw + work_raw
    cost["line_total_raw"] = dec_str(line_raw)
    cost["line_total"] = money(line_raw)


def _line_prices(line: dict[str, Any]) -> tuple[Decimal, Decimal]:
    if "internal_cost" in line:
        cost = line["internal_cost"]
        return d(cost.get("material_total_raw")), d(cost.get("work_total_raw"))
    return d(line.get("material_total_raw", line.get("material_total", 0))), d(
        line.get("work_total_raw", line.get("work_total", 0))
    )


def _line_totals(line: dict[str, Any]) -> tuple[int, int]:
    if "internal_cost" in line:
        cost = line["internal_cost"]
        return int(cost.get("material_total", 0)), int(cost.get("work_total", 0))
    return int(line.get("material_total", 0)), int(line.get("work_total", 0))


def _original_unit_price(line: dict[str, Any]) -> Decimal | None:
    if "internal_cost" in line:
        cost = line["internal_cost"]
        material = d(cost.get("material_unit_price"))
        work = d(cost.get("work_unit_price"))
    else:
        material = d(line.get("material_unit_price"))
        work = d(line.get("work_unit_price"))
    if material != D0:
        return material
    if work != D0:
        return work
    return None


def apply_live_pricing(
    result: dict[str, Any],
    input_data: dict[str, Any],
    repo_root: Path,
    totals_key: str = "totals",
) -> dict[str, Any]:
    mode = pricing_mode(input_data)
    if mode != "price_registry_with_fallback":
        return result

    live_result = deepcopy(result)
    path = registry_path(input_data, repo_root)
    registry = load_price_registry(path)
    overrides = load_project_price_overrides(path)

    summary = {
        "mode": mode,
        "registry_path": str(path),
        "prices_from_price_registry": 0,
        "prices_from_project_overrides": 0,
        "prices_from_fallback_input": 0,
        "warnings_count": 0,
    }
    warnings: list[str] = []

    for line in live_result.get("estimate_lines", []):
        price_code = line.get("price_code")
        original_price = _original_unit_price(line)
        if price_code:
            resolved = resolve_price(price_code, original_price, registry, overrides)
            source = resolved["source"]
            if source == "price_registry":
                summary["prices_from_price_registry"] += 1
            elif source == "project_price_overrides":
                summary["prices_from_project_overrides"] += 1
            else:
                summary["prices_from_fallback_input"] += 1
            if resolved["warning"]:
                warnings.append(f"{price_code}: {resolved['warning']}")
            if "internal_cost" in line:
                _nested_reprice_line(line, resolved)
            else:
                _flat_reprice_line(line, resolved)
            used_price = resolved["price"]
            line["unit_price_source"] = source
            line["unit_price_original"] = dec_str(original_price) if original_price is not None else None
            line["unit_price_used"] = dec_str(used_price) if used_price is not None else None
            line["price_warning"] = resolved["warning"]
        else:
            line["unit_price_source"] = "locked_case_prices"
            line["unit_price_original"] = dec_str(original_price) if original_price is not None else None
            line["unit_price_used"] = dec_str(original_price) if original_price is not None else None
            line["price_warning"] = None

    summary["warnings_count"] = len(warnings)
    live_result["warnings"] = [*live_result.get("warnings", []), *warnings]
    live_result["pricing_summary"] = summary

    materials_raw = sum((_line_prices(line)[0] for line in live_result.get("estimate_lines", [])), D0)
    works_raw = sum((_line_prices(line)[1] for line in live_result.get("estimate_lines", [])), D0)
    displayed_materials = sum((_line_totals(line)[0] for line in live_result.get("estimate_lines", [])), 0)
    displayed_works = sum((_line_totals(line)[1] for line in live_result.get("estimate_lines", [])), 0)

    totals = live_result.get(totals_key) or live_result.get("internal_totals") or {}
    target_key = totals_key if totals_key in live_result else "internal_totals"
    if target_key == "internal_totals":
        live_result[target_key] = {
            **totals,
            "internal_materials_total_raw": dec_str(materials_raw),
            "internal_materials_total": money(materials_raw),
            "internal_works_total_raw": dec_str(works_raw),
            "internal_works_total": money(works_raw),
            "internal_section_total_raw": dec_str(materials_raw + works_raw),
            "internal_section_total": money(materials_raw + works_raw),
        }
        if "sum_of_displayed_line_material_totals" in totals:
            live_result[target_key]["sum_of_displayed_line_material_totals"] = displayed_materials
        if "sum_of_displayed_line_work_totals" in totals:
            live_result[target_key]["sum_of_displayed_line_work_totals"] = displayed_works
        if "sum_of_displayed_line_totals" in totals:
            live_result[target_key]["sum_of_displayed_line_totals"] = displayed_materials + displayed_works
    else:
        live_result[target_key] = {
            **totals,
            "internal_materials_total_raw": dec_str(materials_raw),
            "internal_materials_total": money(materials_raw),
            "internal_works_total_raw": dec_str(works_raw),
            "internal_works_total": money(works_raw),
            "internal_section_total_raw": dec_str(materials_raw + works_raw),
            "internal_section_total": money(materials_raw + works_raw),
            "sum_of_displayed_line_material_totals": displayed_materials,
            "sum_of_displayed_line_work_totals": displayed_works,
            "sum_of_displayed_line_totals": displayed_materials + displayed_works,
        }
    return live_result


def price_sources_markdown(lines: list[dict[str, Any]]) -> list[str]:
    rows = [
        "## Источники цен",
        "",
        "| Строка сметы | price_code | старая цена | использованная цена | источник | предупреждение |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for line in lines:
        rows.append(
            "| "
            f"{line.get('name', '')} | "
            f"`{line.get('price_code', '')}` | "
            f"`{line.get('unit_price_original', '')}` | "
            f"`{line.get('unit_price_used', '')}` | "
            f"`{line.get('unit_price_source', '')}` | "
            f"{line.get('price_warning') or ''} |"
        )
    return rows
