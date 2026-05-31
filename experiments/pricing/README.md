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

## Files

- `price_reader.py` reads prices and resolves fallback.
- `validate_price_registry.py` validates `output/price_registry_filled_v3.xlsx`.
- `check_required_codes_against_registry.py` compares required calculator codes with
  the registry and `rows_to_add`.
- `test_price_reader_demo.py` prints a small demo of registry and fallback behavior.

## Commands

From the repository root:

```bash
../.venv/bin/python3 experiments/pricing/validate_price_registry.py
../.venv/bin/python3 experiments/pricing/check_required_codes_against_registry.py
../.venv/bin/python3 experiments/pricing/test_price_reader_demo.py
```

Generated reports:

- `experiments/pricing/output/price_registry_validation_report.md`
- `experiments/pricing/output/required_codes_coverage_report.md`

## Notes

- Only `price_code` is used.
- `material_price_code` and `work_rate_code` are intentionally not introduced.
- The source price registry is not overwritten.
- Old calculators are not modified by this layer.
