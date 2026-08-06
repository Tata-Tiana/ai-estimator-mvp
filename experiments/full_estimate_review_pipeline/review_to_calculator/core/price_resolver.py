"""Resolves sheet 02's read prices (`core.workbook_reader.read_prices()` output) against
a section's contract `price_keys` - which values are usable, and the single number
`sections/<code>/build_input.py` should use for each.

Placement of a resolved price into the actual calculator input (a flat `rates` dict, a
literal top-level field, an explicit `calculator_input_path`, or a per-row
`unit_price_per_m` inside a repeated_rows item) is section-specific and belongs in
`build_input.py`, not here - this module only answers "what number, if any".
"""

from __future__ import annotations

from typing import Any

from core.contract_loader import price_keys as contract_price_keys
from core.workbook_reader import template_price_keys


class PriceResolutionError(ValueError):
    pass


def resolve_prices(
    prices: dict[str, dict[str, Any] | list[dict[str, Any]]], contract: dict[str, Any]
) -> dict[str, float | dict[str, float]]:
    """Returns {calc_price_key: selected_price} for every ordinary price_key that has a
    usable selected_price, and {calc_price_key: {price_registry_code: selected_price}} for
    "template" price_keys (registry_code containing "<...>", e.g. rebar_<class>_d<diameter>_m
    - see core.workbook_reader.template_price_keys()) where sheet 02 expands one contract key
    into many real per-item rows (one per steel_class/diameter_mm actually in the project).

    Raises PriceResolutionError listing every REQUIRED *ordinary* price_key with no usable
    selected_price - never returns a partial result silently missing a required price, per
    the adapter's fail-loudly rule (ADAPTER_BUILD_PLAN.md). Template keys are deliberately NOT
    required-checked here: there is no single scalar to validate, and a specific missing
    diameter/class price is far more useful reported by build_input.py at the exact item that
    needs it than as a generic "some rebar price is missing" from this function."""
    resolved: dict[str, float | dict[str, float]] = {}
    missing: list[str] = []
    templates = template_price_keys(contract)

    for price_key in contract_price_keys(contract):
        key = price_key["key"]
        if key in templates:
            rows = prices.get(key) or []
            by_registry_code = {
                row["price_registry_code"]: row["selected_price"]
                for row in rows
                if row.get("price_registry_code") and row.get("selected_price") is not None
            }
            if by_registry_code:
                resolved[key] = by_registry_code
            continue
        row = prices.get(key)
        selected_price = row.get("selected_price") if row else None
        if selected_price is None:
            if price_key.get("required", True):
                missing.append(key)
            continue
        resolved[key] = selected_price

    if missing:
        section = contract["section"]["code"]
        raise PriceResolutionError(
            f"{section}: missing selected_price for required price_keys: {missing}. "
            "Elena must fill sheet 02's 'Цена для расчета' (or 'Исправить цену') for each."
        )

    return resolved
