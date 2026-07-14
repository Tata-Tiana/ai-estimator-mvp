# Pricing MVP Layer

This folder contains a safe price-reading layer for the estimator MVP.

The existing calculators remain deterministic and keep their current input prices by
default. This module is a separate integration layer for future runs where prices can
come from the registry.

## Modes

### locked_case_prices

Default behavior for existing calculators.

- Prices are read from each case `input.json` or existing calculator parameters.
- Existing formulas and `expected.json` files do not change.
- This mode is the source of truth for already validated cases.

### price_registry_with_fallback

Future integration mode.

Priority:

1. `project_price_overrides`
2. `price_registry`
3. input fallback

If a price is not found in the registry, the resolver returns the fallback input price
and a warning. It does not silently fail.

## Rule: registry is always checked first, fallback is last resort

This is not optional and not per-calculator — it is how `resolve_price()` works for every
`price_code`, in every section, with no exceptions. Confirmed 2026-07-14 while adding a
brand-new price_code (`eps_wall_insulation_work_50_m2`, waterproofing) that did not exist
in the registry yet: the resolver still checked the registry and `project_price_overrides`
first, only fell back to the `input.json` value, and logged a warning saying so
(`"eps_wall_insulation_work_50_m2: price_code not found in price_registry, fallback input
price used"`). Nothing in `price_reader.py` needs to change when a code is added to the
registry later — the next run in `price_registry_with_fallback` mode picks it up
automatically.

**What this means for anyone wiring calculator input in production (adapters,
`build_input.py` per section, future `box_calculator`):** always set
`pricing.mode = "price_registry_with_fallback"` explicitly. Never leave `pricing` absent
and rely on the default — the default is `locked_case_prices`, which reads prices straight
from the input dict and never consults the registry or overrides at all. A calculator
running in `locked_case_prices` mode will keep using whatever number was baked into its
input forever, even after Elena adds a real price to the registry, because it never looks.

## Files

- `price_reader.py` reads prices and resolves fallback.
- `validate_price_registry.py` validates `output/price_registry_filled_v3.xlsx`.
- `check_required_codes_against_registry.py` compares required calculator codes with
  the registry and `rows_to_add`.
- `test_price_reader_demo.py` prints a small demo of registry and fallback behavior.

## Commands

From the repository root:

```bash
.venv/bin/python3 experiments/pricing/validate_price_registry.py
.venv/bin/python3 experiments/pricing/check_required_codes_against_registry.py
.venv/bin/python3 experiments/pricing/test_price_reader_demo.py
```

Generated reports:

- `experiments/pricing/output/price_registry_validation_report.md`
- `experiments/pricing/output/required_codes_coverage_report.md`

## Notes

- Only `price_code` is used.
- `material_price_code` and `work_rate_code` are intentionally not introduced.
- The source price registry is not overwritten.
- Old calculators are not modified by this layer.
