# Floor Slab 2 Calculator

Experimental deterministic calculator for:

`Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 2-го этажа на отм. +4.680 (200мм)`

## Scope

- Calculates only internal gray cost: materials, machinery, works, and internal totals.
- Does not calculate client/commercial/white-zone values.
- Does not use AI.
- Does not use Excel cell addresses as identifiers or logic inputs.
- Does not calculate beams. This floor slab 2 case is a small slab / second-light area.

## Run

From the repository root:

```bash
../.venv/bin/python3 experiments/floor_slab_2_calculator/run_case.py experiments/floor_slab_2_calculator/cases/test_floor_slab_2
```

Compile check:

```bash
../.venv/bin/python3 -m py_compile experiments/floor_slab_2_calculator/calculator.py experiments/floor_slab_2_calculator/run_case.py
```

## Files

- `cases/test_floor_slab_2/input.json` — deterministic input.
- `cases/test_floor_slab_2/expected.json` — expected totals and estimate lines.
- `cases/test_floor_slab_2/result.json` — generated calculation result.
- `cases/test_floor_slab_2/result.md` — generated human-readable report.

## Raw vs Display

The calculator stores raw and display values separately. Line totals are rounded with `Decimal` and `ROUND_HALF_UP`, but section totals are also stored as raw totals.

For this case:

- `internal_section_total_raw` is calculated from raw line totals.
- `sum_of_displayed_line_totals` is the sum of rounded displayed line totals.
- These differ by 1 ruble in the current case; both values are intentionally preserved.

## Not Calculated

- Client-side prices.
- White-zone Excel prices.
- Taxes, client overheads, commercial profit.
- Beam concrete or beam formwork.
