"""schiedel_vent_channels: normalized_review -> plain dict for calculate_schiedel_vent_channels().

Third adapter for review_to_calculator (see ../../ADAPTER_BUILD_PLAN.md, Этап 2). This
calculator takes a plain dict (no typed dataclass, no from_dict()) - see
core/job_runner.py's _prepare_calculator_argument() docstring for which of the 8
calculators use which convention.

Two real contract gaps found and fixed while building this adapter (2026-08-05, explicit
authorization both times) - see the contract's own notes on each new entry for details:
1. price_keys only had entries for the 2x/3x channel types and no masonry-gas-block
   prices at all, even though the calculator supports 1x/2x/3x/4x/cvent channels and
   D400/D500 masonry densities. TRC's own real data uses 1x, ARK's uses 4x - a real
   production KeyError risk. Added the 5 missing price_keys (1x/4x/cvent channels,
   D400/D500 masonry - 1x/4x required since real projects already use them, cvent/D400/
   D500 optional since they're rare/conditional).
2. `schiedel_masonry_gas_block_items` (the repeated-rows group itself, not just its
   prices) was never declared in review_parameters at all - the calculator already read
   it, but sheet 01 had no row for it, so real parser-found data was invisible to Elena
   and never reached the calculator through the review workbook. Added, mirroring the
   already-correct `schiedel_channel_items` entry.

Pricing mode: deliberately does NOT set an input_data["pricing"] key. The calculator's
own build_effective_pricing() defaults to "locked_case_prices" when absent, which uses
whatever flat price fields are given directly - i.e. this adapter's own resolved sheet-02
prices, not the calculator re-reading a price registry file itself. Do not add a
`pricing` key without a deliberate reason; see pricing_mode()/build_effective_pricing()
in calculator.py.

Field sourcing:
- project_name: from the review workbook's own title.
- schiedel_masonry_total_length_m: required review_parameter.
- schiedel_delivery_trips: required supplier_input (manual, no PDF/formula source -
  read the same way as any other scalar, read_scalar_parameters() doesn't distinguish
  review_parameters from supplier_inputs).
- schiedel_channel_items, schiedel_masonry_gas_block_items: both optional production
  repeated_rows groups - passed through as-is when non-empty, omitted (calculator
  treats missing/empty the same as an all-zero breakdown) when empty.
- consumables_rate: mechanical default.
- Every price field (10 total: masonry work rate, 5 channel types, 2 masonry
  densities, 2 delivery) built into a single internal_prices-shaped... no, this
  calculator does NOT use an internal_prices dict like earthworks/waterproofing - each
  price is its own flat top-level field (input_data["schiedel_vent_channel_2x_unit_price"]
  etc., see calculator.py's PRICE_CODE_BY_FIELD and CHANNEL_TYPE_SPECS/
  SCHIEDEL_MASONRY_GAS_BLOCK_SPECS). Filled directly by contract price_keys[].key name
  (which already equals the calculator's own field name in every case).
"""

from __future__ import annotations

from typing import Any

from core.contract_loader import default_by_key, load_contract, price_keys as contract_price_keys

REQUIRED_SCALARS = ("schiedel_masonry_total_length_m", "schiedel_delivery_trips")
PRODUCTION_ITEM_GROUPS = ("schiedel_channel_items", "schiedel_masonry_gas_block_items")


def _normalize_channel_product_type(value: Any) -> str:
    text = str(value or "").strip().lower().replace("х", "x")
    for product_type in ("1x", "2x", "3x", "4x"):
        if text == product_type or text.startswith(product_type) or f" {product_type}" in text:
            return product_type
    if "cvent" in text or "сvent" in text or "сивент" in text:
        return "cvent"
    return str(value or "").strip()


def build_calculator_input(normalized_review: dict[str, Any]) -> dict[str, Any]:
    contract = load_contract("schiedel_vent_channels")
    defaults = default_by_key(contract)
    scalars = normalized_review["scalar_parameters"]
    production_items = normalized_review["production_items"]
    resolved_prices = normalized_review["resolved_prices"]

    result: dict[str, Any] = {
        "project_name": normalized_review["project_name"],
    }

    for key in REQUIRED_SCALARS:
        row = scalars.get(key)
        value = row["value_number"] if row else None
        if value is None:
            raise ValueError(
                f"schiedel_vent_channels: required parameter '{key}' is missing/blank on "
                "sheet 01 (check 'Найдено в проекте' / 'Исправить / ввести значение')"
            )
        result[key] = value

    for key in PRODUCTION_ITEM_GROUPS:
        items = production_items.get(key)
        if items:
            if key == "schiedel_channel_items":
                result[key] = [
                    {**item, "product_type": _normalize_channel_product_type(item.get("product_type"))}
                    for item in items
                ]
            else:
                result[key] = items

    for key, entry in defaults.items():
        if key in result:
            continue
        result[key] = entry["value"]

    for price_key in contract_price_keys(contract):
        key = price_key["key"]
        if key in resolved_prices:
            result[key] = resolved_prices[key]
        elif price_key.get("required", True):
            raise ValueError(f"schiedel_vent_channels: required price '{key}' has no resolved value")
        # else: leave unset - only accessed by the calculator if a matching item row is
        # actually present (e.g. schiedel_vent_channel_cvent_unit_price is only read when
        # a schiedel_channel_items row has product_type=cvent).

    return result
