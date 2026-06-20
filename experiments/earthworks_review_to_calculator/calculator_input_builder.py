from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from constants import (
    DEFAULT_COMMUNICATIONS_METHOD,
    DEFAULT_EXCAVATOR_SHIFTS_METHOD,
    DEFAULT_MANUAL_EXCAVATION_METHOD,
    GENERIC_CALCULATOR_DEFAULTS,
    PROJECT_NAME,
    REQUIRED_PARAMETERS,
    SECTION_CODE,
    SECTION_NAME_RU,
)
from normalization import display_number, is_blank, parse_number


_TRANSLIT_MAP = str.maketrans(
    {
        "А": "A",
        "Б": "B",
        "В": "V",
        "Г": "G",
        "Д": "D",
        "Е": "E",
        "Ё": "E",
        "Ж": "Zh",
        "З": "Z",
        "И": "I",
        "Й": "I",
        "К": "K",
        "Л": "L",
        "М": "M",
        "Н": "N",
        "О": "O",
        "П": "P",
        "Р": "R",
        "С": "S",
        "Т": "T",
        "У": "U",
        "Ф": "F",
        "Х": "H",
        "Ц": "C",
        "Ч": "Ch",
        "Ш": "Sh",
        "Щ": "Shch",
        "Ы": "Y",
        "Э": "E",
        "Ю": "Yu",
        "Я": "Ya",
        "Ъ": "",
        "Ь": "",
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "i",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "c",
        "ч": "ch",
        "ш": "sh",
        "щ": "shch",
        "ы": "y",
        "э": "e",
        "ю": "yu",
        "я": "ya",
        "ъ": "",
        "ь": "",
    }
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _as_number(value: Any) -> float | None:
    if is_blank(value):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    parsed = parse_number(value)
    if parsed is not None:
        return parsed
    return None


def _value_or_none(value: Any) -> float | int | None:
    number = _as_number(value)
    if number is None:
        return None
    return number


def _slugify_identifier(value: Any, default: str = "item") -> str:
    text = str(value or "").translate(_TRANSLIT_MAP).lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or default


def _get_parameter(parameters: dict[str, dict[str, Any]], key: str) -> dict[str, Any]:
    if key not in parameters:
        raise KeyError(f"Missing required parameter in normalized review: {key}")
    return parameters[key]


def _parameter_value(parameters: dict[str, dict[str, Any]], key: str) -> float | int | None:
    return _value_or_none(_get_parameter(parameters, key).get("value"))


def _build_trench_routes(details: dict[str, Any]) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for index, item in enumerate(details.get("trench_routes") or [], start=1):
        name = str(item.get("name", "")).strip()
        route_code = _slugify_identifier(name, default=f"route_{index}")
        routes.append(
            {
                "route_code": route_code,
                "name": name,
                "length_m": _value_or_none(item.get("length_m")),
                "depth_m": _value_or_none(item.get("depth_m")),
                "width_m": _value_or_none(item.get("width_m")),
                "volume_m3": _value_or_none(item.get("volume_m3")),
                "source": str(item.get("source", "")).strip(),
                "fragment": str(item.get("fragment", "")).strip(),
            }
        )
    return routes


def _build_communications_pipe_items(details: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for index, item in enumerate(details.get("communications_pipe_items") or [], start=1):
        name = str(item.get("name", "")).strip()
        code = _slugify_identifier(name, default=f"pipe_item_{index}")
        items.append(
            {
                "code": code,
                "name": name,
                "diameter_mm": int(_value_or_none(item.get("diameter_mm")) or 0),
                "pipe_length_m": _value_or_none(item.get("pipe_length_m")),
                "quantity": _value_or_none(item.get("quantity")),
                "total_length_m": _value_or_none(item.get("total_length_m")),
                "include_in_communications": bool(item.get("included")),
                "source": str(item.get("source", "")).strip(),
                "fragment": str(item.get("fragment", "")).strip(),
            }
        )
    return items


def _build_internal_prices(
    prices: list[dict[str, Any]],
) -> tuple[dict[str, float], float | None, list[str]]:
    internal_prices: dict[str, float] = {}
    consumables_amount: float | None = None
    warnings: list[str] = []
    seen_keys: set[str] = set()

    for row in prices:
        estimate_line = str(row.get("estimate_line", "")).strip()
        price_role = str(row.get("price_role", "")).strip()
        calc_price_key = str(row.get("calc_price_key", "")).strip()
        selected_price = _as_number(row.get("selected_price"))
        if selected_price is None:
            warnings.append(f"price row without selected_price: {estimate_line} / {price_role}")
            continue

        if not calc_price_key:
            warnings.append(f"price row without calc_price_key: {estimate_line} / {price_role}")
            continue

        if calc_price_key in seen_keys:
            warnings.append(f"duplicate calc_price_key: {calc_price_key}")
        seen_keys.add(calc_price_key)

        if calc_price_key == "consumables_amount":
            consumables_amount = selected_price
            continue

        internal_prices[calc_price_key] = selected_price

    return internal_prices, consumables_amount, warnings


def build_calculator_input(normalized_data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    meta = normalized_data.get("meta", {})
    parameters = normalized_data.get("parameters", {})
    prices = normalized_data.get("prices", [])
    details = normalized_data.get("details", {})
    summary = details.get("summary", {})
    defaults = copy.deepcopy(GENERIC_CALCULATOR_DEFAULTS)

    pit_area_m2 = _parameter_value(parameters, "pit_area_m2")
    pit_excavation_depth_m = _parameter_value(parameters, "pit_excavation_depth_m")
    sand_base_volume_m3 = _parameter_value(parameters, "sand_base_volume_m3")
    trench_volume_m3 = _parameter_value(parameters, "trench_volume_m3")
    geotextile_area_m2 = _parameter_value(parameters, "geotextile_area_m2")
    geotextile_laying_area_m2 = _parameter_value(parameters, "geotextile_laying_area_m2")

    trench_routes = _build_trench_routes(details)
    communications_pipe_items = _build_communications_pipe_items(details)

    # Compute communications length from included pipe rows (source of truth in pipe_items mode).
    # communications_length_m_from_review: what Елена entered on sheet 01 (reference/audit value).
    # communications_length_m_effective: sum of included pipe rows (used by calculator).
    communications_length_m_from_review = _parameter_value(parameters, "communications_length_m")
    communications_length_m_effective = float(sum(
        (item.get("total_length_m") or 0.0)
        for item in communications_pipe_items
        if item.get("include_in_communications")
    ))
    communications_quantity_mode = defaults.get(
        "communications_length_calc_method", DEFAULT_COMMUNICATIONS_METHOD
    )

    internal_prices, consumables_amount, price_warnings = _build_internal_prices(prices)
    if consumables_amount is None:
        consumables_amount = 0.0

    payload: dict[str, Any] = {}
    payload["project_name"] = PROJECT_NAME
    payload["case_meta"] = copy.deepcopy(defaults.get("case_meta", {}))
    payload["case_meta"]["workbook_path"] = str(meta.get("workbook_path", ""))
    payload["case_meta"]["section_code"] = meta.get("section_code", SECTION_CODE)
    payload["case_meta"]["section_name"] = meta.get("section_name", SECTION_NAME_RU)
    payload["assumptions"] = copy.deepcopy(defaults.get("assumptions", {}))

    payload["excavator_shifts_calc_method"] = defaults.get(
        "excavator_shifts_calc_method", DEFAULT_EXCAVATOR_SHIFTS_METHOD
    )
    payload["pit_area_m2"] = pit_area_m2 if pit_area_m2 is not None else 0.0
    payload["pit_excavation_depth_m"] = pit_excavation_depth_m
    payload["excavator_productivity_m3_per_shift"] = defaults["excavator_productivity_m3_per_shift"]
    payload["excavator_shifts"] = 0.0
    payload["axis_marking_shifts"] = defaults["axis_marking_shifts"]

    payload["manual_excavation_calc_method"] = defaults.get(
        "manual_excavation_calc_method", DEFAULT_MANUAL_EXCAVATION_METHOD
    )
    payload["manual_refinement_depth_m"] = defaults["manual_refinement_depth_m"]
    payload["trench_volume_m3"] = trench_volume_m3
    payload["trench_length_m"] = None
    payload["trench_depth_m"] = None
    payload["trench_width_m"] = defaults["trench_width_m"]
    payload["trench_routes"] = trench_routes

    payload["sand_base_volume_m3"] = sand_base_volume_m3 if sand_base_volume_m3 is not None else 0.0
    payload["sand_compaction_coeff"] = defaults["sand_compaction_coeff"]
    payload["sand_truck_step_m3"] = defaults["sand_truck_step_m3"]
    payload["geotextile_area_m2"] = geotextile_area_m2 if geotextile_area_m2 is not None else 0.0
    payload["geotextile_overlap_coeff"] = defaults["geotextile_overlap_coeff"]
    payload["geotextile_roll_area_m2"] = defaults["geotextile_roll_area_m2"]

    payload["communications_length_calc_method"] = defaults.get(
        "communications_length_calc_method", DEFAULT_COMMUNICATIONS_METHOD
    )
    # Technical field required by the calculator in pipe_items mode; kept as 0.0 (legacy input).
    # The actual length used for estimate lines is communications_length_m_effective below.
    payload["communications_length_m"] = 0.0
    payload["communications_pipe_items"] = communications_pipe_items
    # Audit/lineage fields — stored in case_meta so the calculator ignores them.
    payload["case_meta"]["communications_quantity_mode"] = communications_quantity_mode
    payload["case_meta"]["communications_length_m_from_review"] = communications_length_m_from_review
    payload["case_meta"]["communications_length_m_effective"] = communications_length_m_effective

    payload["geotextile_laying_area_m2"] = (
        geotextile_laying_area_m2 if geotextile_laying_area_m2 is not None else 0.0
    )
    payload["manual_excavation_quantity_for_estimate_m3"] = None
    payload["consumables_amount"] = consumables_amount
    payload["enabled_lines"] = copy.deepcopy(defaults["enabled_lines"])
    payload["quantity_overrides"] = copy.deepcopy(defaults["quantity_overrides"])
    payload["line_name_overrides"] = copy.deepcopy(defaults["line_name_overrides"])
    payload["internal_prices"] = internal_prices

    summary_info = {
        "source_type": meta.get("source_type", "local_review_workbook"),
        "workbook_path": meta.get("workbook_path", ""),
        "section_code": meta.get("section_code", SECTION_CODE),
        "section_name": meta.get("section_name", SECTION_NAME_RU),
        "created_at": meta.get("created_at", ""),
        "details_summary": summary,
        "price_rows": len(prices),
        "price_warnings": price_warnings,
    }
    return payload, summary_info


def render_calculator_input_report(
    normalized_data: dict[str, Any],
    calculator_input: dict[str, Any],
    summary_info: dict[str, Any],
    output_path: Path | str | None = None,
) -> str:
    meta = normalized_data.get("meta", {})
    parameters = normalized_data.get("parameters", {})
    prices = normalized_data.get("prices", [])
    details = normalized_data.get("details", {})
    validation = normalized_data.get("validation", {})
    summary = details.get("summary", {})

    lines = [
        "# Calculator input report",
        "",
        "## Source",
        f"- normalized_json: {meta.get('workbook_path', '')}",
        f"- output: {output_path or ''}",
        f"- created_at: {meta.get('created_at', '')}",
        "",
        "## Modes",
        f"- excavator_shifts_calc_method: `{calculator_input.get('excavator_shifts_calc_method', '')}`",
        f"- manual_excavation_calc_method: `{calculator_input.get('manual_excavation_calc_method', '')}`",
        f"- communications_length_calc_method: `{calculator_input.get('communications_length_calc_method', '')}`",
        "",
        "## Values from review sheet",
    ]

    for key in REQUIRED_PARAMETERS:
        parameter = parameters.get(key, {})
        value = parameter.get("value")
        unit = parameter.get("unit", "")
        source_column = parameter.get("source_column", "")
        override_used = "yes" if parameter.get("override_used") else "no"
        lines.append(
            f"- {key}: {display_number(value)} {unit} (source: `{source_column}`, override: `{override_used}`)"
        )

    lines.extend(
        [
            "",
            "## Communications length semantics",
            f"- communications_quantity_mode: `{calculator_input.get('case_meta', {}).get('communications_quantity_mode', '')}`",
            f"- communications_length_m_from_review: {display_number(calculator_input.get('case_meta', {}).get('communications_length_m_from_review'))} м (reference value from sheet 01)",
            f"- communications_length_m_effective: {display_number(calculator_input.get('case_meta', {}).get('communications_length_m_effective'))} м (sum of included pipe rows — used for estimate lines)",
            f"- communications_length_m: {display_number(calculator_input.get('communications_length_m'))} (technical legacy field, 0.0 in pipe_items mode)",
            "",
            "## Details",
            f"- trench_routes: {len(details.get('trench_routes', []))}",
            f"- communications_pipe_items: {len(details.get('communications_pipe_items', []))}",
            f"- communications_total_length_m: {display_number(summary.get('communications_total_length_m'))}",
            "",
            "## Prices",
            f"- rows read: {len(prices)}",
            f"- internal_prices keys: {', '.join(sorted(calculator_input.get('internal_prices', {}).keys()))}",
            f"- consumables_amount: {display_number(calculator_input.get('consumables_amount'))}",
            "",
            "## Price mapping by calc_price_key",
        ]
    )

    for row in prices:
        calc_price_key = str(row.get("calc_price_key", "")).strip()
        selected_price = display_number(row.get("selected_price"))
        selected_source = str(row.get("selected_price_source", "")).strip()
        fallback_key = str(row.get("fallback_key", "")).strip()
        price_registry_code = str(row.get("price_registry_code", "")).strip()
        details_parts = [selected_price, selected_source]
        if price_registry_code:
            details_parts.append(price_registry_code)
        elif fallback_key:
            details_parts.append(fallback_key)
        lines.append(f"- {calc_price_key}: {' / '.join(details_parts)}")

    lines.extend(
        [
            "",
            "## Deprecated mapping",
            "- russian label mapping used: no",
            "",
            "## Defaults from generic calculator defaults",
            f"- project_name: {calculator_input.get('project_name', '')}",
            f"- case_meta: {calculator_input.get('case_meta', {})}",
            f"- assumptions: {calculator_input.get('assumptions', {})}",
            f"- excavator_productivity_m3_per_shift: {display_number(calculator_input.get('excavator_productivity_m3_per_shift'))}",
            f"- manual_refinement_depth_m: {display_number(calculator_input.get('manual_refinement_depth_m'))}",
            f"- trench_width_m: {display_number(calculator_input.get('trench_width_m'))}",
            f"- sand_compaction_coeff: {display_number(calculator_input.get('sand_compaction_coeff'))}",
            f"- sand_truck_step_m3: {display_number(calculator_input.get('sand_truck_step_m3'))}",
            f"- geotextile_overlap_coeff: {display_number(calculator_input.get('geotextile_overlap_coeff'))}",
            f"- geotextile_roll_area_m2: {display_number(calculator_input.get('geotextile_roll_area_m2'))}",
            f"- axis_marking_shifts: {display_number(calculator_input.get('axis_marking_shifts'))}",
            f"- excavator_shifts: {display_number(calculator_input.get('excavator_shifts'))}",
            f"- manual_excavation_quantity_for_estimate_m3: {display_number(calculator_input.get('manual_excavation_quantity_for_estimate_m3')) or 'null'}",
            f"- communications_length_m: {display_number(calculator_input.get('communications_length_m'))}",
            f"- enabled_lines: {calculator_input.get('enabled_lines')}",
            f"- quantity_overrides: {calculator_input.get('quantity_overrides')}",
            f"- line_name_overrides: {calculator_input.get('line_name_overrides')}",
            "",
            "## Validation",
            f"- errors: {len(validation.get('errors', []))}",
            f"- warnings: {len(validation.get('warnings', []))}",
        ]
    )

    if summary_info.get("price_warnings"):
        lines.extend(["", "### Price warnings"])
        lines.extend(f"- {warning}" for warning in summary_info["price_warnings"])

    if validation.get("errors"):
        lines.extend(["", "### Errors"])
        lines.extend(f"- {error}" for error in validation["errors"])

    if validation.get("warnings"):
        lines.extend(["", "### Warnings"])
        lines.extend(f"- {warning}" for warning in validation["warnings"])

    return "\n".join(lines) + "\n"
