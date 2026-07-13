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


class PriceResolutionError(ValueError):
    pass


def resolve_prices(prices: dict[str, dict[str, Any]], contract: dict[str, Any]) -> dict[str, float]:
    """Returns {calc_price_key: selected_price} for every price_key that has a usable
    selected_price. Raises PriceResolutionError listing every REQUIRED price_key with no
    usable selected_price - never returns a partial result silently missing a required
    price, per the adapter's fail-loudly rule (ADAPTER_BUILD_PLAN.md)."""
    resolved: dict[str, float] = {}
    missing: list[str] = []

    for price_key in contract_price_keys(contract):
        key = price_key["key"]
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
