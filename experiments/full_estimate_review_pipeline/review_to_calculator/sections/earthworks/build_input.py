"""earthworks: normalized_review -> EarthworksInput-shaped dict.

Second adapter for review_to_calculator (see ../../ADAPTER_BUILD_PLAN.md, Этап 2).
Earthworks is significantly more involved than the waterproofing pilot: 4 independent
`*_calc_method` fields (each with a fixed production mode, not decided dynamically by
this adapter - all 4 are plain `defaults:` entries in the contract) and 2 real
production repeated_rows groups (`pit_items`, `sand_items`).

Field sourcing, verified against EarthworksInput's real dataclass fields
(experiments/earthworks_calculator/earthworks_calculator.py) and the contract's own
review_parameters/defaults/price_keys:

Fixed production calc_method defaults (all `allow_override_later: false` in the
contract - not inferred from data presence, always these four):
- excavator_shifts_calc_method: "standard_volume_productivity"
- manual_excavation_calc_method: "standard_routes"
- communications_length_calc_method: "legacy_direct_length" — do NOT switch to
  "pipe_items" even though `communications_pipe_items` is `production_input: true` on
  sheet 01 (real per-row data may well be present); the contract's own note says the
  production source stays the reviewed scalar `communications_length_m`. See that
  field's note in the contract before ever changing this.
- consumables_calc_method: "section_total_rate"

review_parameters (scalars) pulled by key when required, otherwise included only when
present (letting the dataclass's own default apply when absent - e.g.
`communications_length_m` defaults to 0.0, `pit_excavation_depth_m` to `None`):
- pit_area_m2 (required), geotextile_area_m2 (required), geotextile_laying_area_m2
  (required), trench_volume_m3 (required - already reflects any trench_routes autosum
  the review-workbook layer applied; `trench_routes` itself is `production_input:
  false`, diagnostic-only, never read here).
- pit_excavation_depth_m, sand_base_volume_m3, communications_length_m (all optional).

Production repeated_rows (via normalized_review["production_items"]):
- pit_items, sand_items - passed through as-is when non-empty, omitted (-> None) when
  empty so the calculator's own area*depth / sand_base_volume_m3 fallback applies
  (see calculate_excavator_shifts_context()/sand section in the calculator - real
  project rows always win over recomputed geometry when given).
- communications_pipe_items, trench_routes - never read here; not needed by the fixed
  production calc_methods above (see docstring note on communications_length_calc_method).

Every remaining field not covered above (~11: excavator_productivity_m3_per_shift,
trench_width_m, sand_compaction_coeff, sand_truck_step_m3,
geotextile_overlap_coeff, geotextile_roll_area_m2, axis_marking_shifts,
consumables_rate + the 4 calc_method fields themselves) comes mechanically from the
contract's `defaults` by exact key-name match to the dataclass field name.
manual_refinement_depth_m and geotextile_laying_overlap_coeff are SUPPLIER_INPUT
(sheet 01-1) as of 2026-08-08, not DEFAULT - see OPTIONAL_SCALARS.

`internal_prices` is built directly from `normalized_review["resolved_prices"]` - the
calculator's own `_price(data, key)` helper reads this flat dict by the exact
`price_keys[].key` name, verified 1:1 (11 keys, no gaps/extras) against every
`_price(data, "...")` call site in the calculator (one extra call site,
`geotextile_material_work_unit_price`, is a legacy optional fallback the calculator
itself only reads when the key is already present - never populated by this adapter).

Intentionally never set (real values only matter for the *other*, non-production
calc_method branch - see calculator source): `excavator_shifts` (legacy_manual_shifts
only), `manual_excavation_quantity_for_estimate_m3` (legacy_manual_override only),
`communications_pipe_items`/`trench_length_m`/`trench_depth_m` (legacy_direct_length /
non-standard_routes only). `case_meta`, `assumptions`, `quantity_overrides`,
`line_name_overrides`, `enabled_lines`, `consumables_amount` - left to their own
dataclass defaults (empty dict/None/0.0), no production source for any of them.
"""

from __future__ import annotations

from typing import Any

from core.contract_loader import default_by_key, load_contract, price_keys as contract_price_keys

REQUIRED_SCALARS = ("pit_area_m2", "geotextile_area_m2", "geotextile_laying_area_m2", "trench_volume_m3")
# manual_refinement_depth_m and geotextile_laying_overlap_coeff moved here 2026-08-08 from the
# contract's `defaults:` block (was source_class: DEFAULT, silently hardcoded, no per-project
# visibility) - both are now SUPPLIER_INPUT/sheet 01-1, so they land in scalars (when Elena fills
# them in) rather than defaults. Left unset when absent, same as every other optional scalar here
# - the calculator's own dataclass defaults (0.08 / 1.0) apply.
OPTIONAL_SCALARS = (
    "pit_excavation_depth_m",
    "sand_base_volume_m3",
    "communications_length_m",
    "manual_refinement_depth_m",
    "geotextile_laying_overlap_coeff",
)
PRODUCTION_ITEM_GROUPS = ("pit_items", "sand_items")


def build_calculator_input(normalized_review: dict[str, Any]) -> dict[str, Any]:
    contract = load_contract("earthworks")
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
                f"earthworks: required review parameter '{key}' is missing/blank on "
                "sheet 01 (check 'Найдено в проекте' / 'Исправить / ввести значение')"
            )
        result[key] = value

    for key in OPTIONAL_SCALARS:
        row = scalars.get(key)
        if row and row["value_number"] is not None:
            result[key] = row["value_number"]
        # else: leave unset, dataclass's own default applies (None or 0.0)

    for key in PRODUCTION_ITEM_GROUPS:
        items = production_items.get(key)
        if items:
            result[key] = items
        # else: leave unset (-> None), calculator falls back to scalar geometry

    for key, entry in defaults.items():
        if key in result:
            continue
        result[key] = entry["value"]

    internal_prices: dict[str, float] = {}
    for price_key in contract_price_keys(contract):
        key = price_key["key"]
        if key in resolved_prices:
            internal_prices[key] = resolved_prices[key]
        elif price_key.get("required", True):
            raise ValueError(f"earthworks: required price '{key}' has no resolved value")
    result["internal_prices"] = internal_prices

    return result
