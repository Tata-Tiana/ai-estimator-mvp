"""waterproofing: normalized_review -> WaterproofingInput-shaped dict.

Pilot adapter for the review_to_calculator pipeline - see ../../ADAPTER_BUILD_PLAN.md,
Этап 1. waterproofing was picked as the pilot because it is a flat single-dataclass
calculator input (no repeated_rows groups, no nested rates/geometry sub-dicts, no
per-section *_calc_method fan-out) with 0 required supplier_inputs.

Field sourcing, verified against WaterproofingInput's 32 real dataclass fields
(experiments/waterproofing_calculator/waterproofing_calculator.py) and the contract's own
checks.forbidden_production_inputs list:

- project_name: from the review workbook's own title (core.workbook_reader.read_project_name),
  not from defaults/review_parameters - the contract's own default entry documents this
  ("Set by job/project metadata, not extracted from section table").
- waterproofing_area_calc_method: fixed to the contract default ("spec_area") - the only
  production mode; legacy_perimeter_height is old-case reference behavior only.
- waterproofing_area_m2, eps100_wall_volume_m3: required review_parameters.
- eps100_wall_insulation_area_m2, eps50_wall_volume_m3: optional review_parameters (most
  projects have no second 50mm edge-insulation layer - stays None, not 0, when absent).
- Every remaining field (22 total: defaults' 16 entries minus the 2 handled explicitly
  above, plus all 8 price_keys) comes mechanically from the contract's defaults/price_keys
  by exact key-name match to the dataclass field name - verified 1:1, no gaps, no extras
  (remaining_dataclass_fields == defaults_keys | price_keys_keys).
- slab_formwork_perimeter_m, slab_edge_height_m, non_insulated_edge_lengths_m, pricing:
  intentionally never set here - they're in checks.forbidden_production_inputs (legacy
  fields from an old calc method) and already have safe dataclass defaults (None / []).
"""

from __future__ import annotations

from typing import Any

from core.contract_loader import default_by_key, load_contract, price_keys as contract_price_keys

REQUIRED_REVIEW_PARAMETERS = ("waterproofing_area_m2", "eps100_wall_volume_m3")
OPTIONAL_REVIEW_PARAMETERS = ("eps100_wall_insulation_area_m2", "eps50_wall_volume_m3")


def build_calculator_input(normalized_review: dict[str, Any]) -> dict[str, Any]:
    contract = load_contract("waterproofing")
    defaults = default_by_key(contract)
    scalars = normalized_review["scalar_parameters"]
    resolved_prices = normalized_review["resolved_prices"]

    result: dict[str, Any] = {
        "project_name": normalized_review["project_name"],
        "waterproofing_area_calc_method": defaults["waterproofing_area_calc_method"]["value"],
    }

    for key in REQUIRED_REVIEW_PARAMETERS:
        row = scalars.get(key)
        value = row["value_number"] if row else None
        if value is None:
            raise ValueError(
                f"waterproofing: required review parameter '{key}' is missing/blank on "
                "sheet 01 (check 'Найдено в проекте' / 'Исправить / ввести значение')"
            )
        result[key] = value

    for key in OPTIONAL_REVIEW_PARAMETERS:
        row = scalars.get(key)
        result[key] = row["value_number"] if row else None

    for key, entry in defaults.items():
        if key in result:
            continue
        result[key] = entry["value"]

    for price_key in contract_price_keys(contract):
        key = price_key["key"]
        if key in resolved_prices:
            result[key] = resolved_prices[key]
        elif price_key.get("required", True):
            # resolve_prices() already raises before build_calculator_input() runs when a
            # required price is missing - reaching here would mean job_runner wiring changed.
            raise ValueError(f"waterproofing: required price '{key}' has no resolved value")
        else:
            result[key] = None

    return result
