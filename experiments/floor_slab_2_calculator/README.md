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

In this mode the specification is the source of truth for three formwork areas:

- `main_formwork_area_m2` — slab deck formwork area, used by `formwork_rental_set`
  ("Комплект опалубки");
- `edge_formwork_area_m2` — slab edge formwork area;
- `beams_formwork_area_m2` — beam formwork area.

For the current floor slab 2 USV case there are no beams, so `beams_formwork_area_m2 = 0`.
The production area for edge/beam formwork is:

```text
edge_and_beam_formwork_area_m2 = edge_formwork_area_m2 + beams_formwork_area_m2
```

This value is used for the edge formwork control line, plywood, and timber. It is not derived
from `slab_edge_perimeter_m * edge_formwork_height_m` in production.

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
edge_insulation_height_m
```

`slab_edge_perimeter_m` is the project/specification length of the insulated slab edge in running
meters. It is not mandatory to derive it from the rectangular perimeter because the actual insulated
edge can differ from `2 * (slab_length_m + slab_width_m)`.

`edge_insulation_height_m` is the project/specification height of edge insulation. For the current
USV case the confirmed value is `0.18 m`; `200 mm` in the section title is treated as a naming
error and is not used as a calculation source.

For control only, if `slab_edge_perimeter_m` and `edge_formwork_height_m` are provided, the
calculator writes:

```text
calculated_edge_formwork_area_m2 = slab_edge_perimeter_m * edge_formwork_height_m
edge_formwork_area_delta_m2 = edge_formwork_area_m2 - calculated_edge_formwork_area_m2
```

The control delta does not replace the specification value.

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

## Production Rebar

The calculator supports two rebar modes:

```text
rebar_calc_method = "legacy_weight_kg"
rebar_calc_method = "spec_length_items"
```

If the method is omitted, `legacy_weight_kg` is used for backward compatibility with the locked USV
case.

`legacy_weight_kg` keeps the old calculation:

```text
source_weight_kg / kg_per_meter = raw_length_m
raw_length_m * waste_coeff = length_with_waste_m
order_length_m = ceil(length_with_waste_m / rod_length_m) * rod_length_m
```

`spec_length_items` is the production mode. The project/specification provides only:

- `rebar_items[*].steel_class`;
- `rebar_items[*].diameter_mm`;
- `rebar_items[*].spec_length_m`;
- `rebar_items[*].unit_price_per_m` until global price registry wiring is added.

The local catalog provides:

- `code`;
- `name`;
- `kg_per_meter`;
- `rod_length_m`;
- `price_code`.

Current catalog values:

- A500 D16: `kg_per_meter = 1.58`, `rod_length_m = 11.7`;
- A500 D12: `kg_per_meter = 0.888`, `rod_length_m = 11.7`;
- A500 D10: `kg_per_meter = 0.617`, `rod_length_m = 11.7`.

Parameter statuses:

AUTO_PROJECT:

- `rebar_items[*].steel_class`;
- `rebar_items[*].diameter_mm`;
- `rebar_items[*].spec_length_m`.

AUTO_CALCULATED:

- `rebar_items[*].code`;
- `rebar_items[*].name`;
- `rebar_items[*].order_length_m`;
- `rebar_items[*].rods`;
- `rebar_items[*].order_weight_kg`;
- `total_rebar_order_length_m`;
- `total_rebar_order_weight_kg`.

MATERIAL_CATALOG:

- `rebar_items[*].kg_per_meter`;
- `rebar_items[*].rod_length_m`;
- `rebar_items[*].price_code`.

PRICE_DATABASE / LIVE_PRICING / INPUT:

- `rebar_items[*].unit_price_per_m`.

DEPRECATED / LEGACY_ONLY:

- `rebar_items[*].source_weight_kg` as mandatory production source;
- `rebar_items[*].code` as input field;
- `rebar_items[*].name` as input field;
- `rebar_items[*].kg_per_meter` as input field;
- `rebar_items[*].rod_length_m` as input field.

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
