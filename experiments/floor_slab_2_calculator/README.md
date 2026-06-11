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
- `cases/test_floor_slab_2_spec_formwork_area/` — production-case where formwork area is read from specification.

## Production Formwork Area

Production mode uses:

```text
formwork_area_calc_method = "spec_formwork_area"
```

In this mode `main_formwork_area_m2` is the source of truth for the line `formwork_rental_set`
("Комплект опалубки"). It comes from the project specification and is not derived from
`slab_length_m * slab_width_m`.

The fields below are optional control values in production:

- `slab_length_m`;
- `slab_width_m`;
- `slab_area_m2`.

If length and width are provided, the calculator writes geometry-check values to
`calculation_blocks.geometry`:

- `calculated_slab_area_m2`;
- `calculated_slab_edge_perimeter_m`;
- `area_delta_m2`;
- `formwork_area_delta_m2`.

For edge insulation the production input should provide:

```text
slab_edge_perimeter_m
```

This is the project/specification length of the insulated slab edge in running meters. It is not
mandatory to derive it from the rectangular perimeter because the actual insulated edge can differ
from `2 * (slab_length_m + slab_width_m)`.

Legacy mode is still supported:

```text
formwork_area_calc_method = "legacy_dimensions"
```

It reproduces the original USV case:

```text
slab_area_m2 = slab_length_m * slab_width_m
slab_edge_perimeter_m = 2 * (slab_length_m + slab_width_m)
main_formwork_area_m2 = slab_area_m2
```

## Production Formwork Delivery

Production mode uses:

```text
formwork_delivery_calc_method = "area_threshold"
```

If the method is omitted, `area_threshold` is used by default.

Rule:

- `main_formwork_area_m2 <= 180` — 2 trips: 1 delivery + 1 return;
- `main_formwork_area_m2 > 180` — 4 trips: 2 deliveries + 2 returns.

The calculated value is written to:

```text
calculation_blocks.formwork.formwork_delivery_trips
```

Manual override is only for exceptions:

```text
formwork_delivery_calc_method = "manual_override"
manual_lines.formwork_delivery_trips_override = ...
```

The old direct `formwork_delivery_trips` field can remain in legacy inputs for compatibility, but
it is not used when `formwork_delivery_calc_method = "area_threshold"`.

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
