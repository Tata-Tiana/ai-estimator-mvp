# Step 17 — Load-Bearing Walls and Lintels: Contract vs Parser Target Cross-Check

## Scope

Cost-basis ("себестоимость") only. This checks
`sections/load_bearing_walls_lintels/section_contract.yaml` and chat-extraction files against
`experiments/load_bearing_walls_lintels_calculator/load_bearing_walls_lintels_calculator.py`, which
is the ground truth for production input names. No real project quantities, page numbers, filenames,
or old fixture totals are recorded here.

## Calculator Ground Truth

The production modes used by the section contract are:

```text
cutoff_waterproofing_calc_method = spec_area
lintel_length_calc_method = spec_total_length
lintel_concrete_calc_method = spec_volume
main_wall_rebar_calc_method = spec_length_items
lintel_rebar_calc_method = spec_length_items
upper_floor_calc_method = floor_2_spec_volume
parapet_calc_method = flat_roof_spec_volume
vent_chimney_cladding_calc_method = flat_roof_spec_volume
vent_chimney_geometry_calc_method = spec_volume_thickness
```

The production PDF/review quantities are:

```text
floors_count
cutoff_waterproofing_load_bearing_walls_area_m2
main_wall_gas_block_400_spec_volume_m3
main_wall_gas_block_250_spec_volume_m3
lintel_total_length_m
lintel_concrete_spec_volume_m3
floor_2_masonry_volume_m3
parapet_masonry_volume_m3
vent_chimney_gas_block_spec_volume_m3
main_wall_rebar_items
lintel_rebar_items
lintel_items
```

`lintel_items` is diagnostic/review detail: it preserves the mark-by-mark lintel table. The calculator
production scalar is `lintel_total_length_m`.

## Parser-Side Fixes Made

`calculator_targets_compact.json` was aligned from legacy names to production target codes:

- added `floors_count`;
- added `cutoff_waterproofing_load_bearing_walls_area`;
- renamed wall block targets to `main_wall_gas_block_400_spec_volume` and
  `main_wall_gas_block_250_spec_volume`;
- added `lintel_total_length`;
- added `floor_2_masonry_volume`;
- renamed the 150 mm wall/vent block target to `vent_chimney_gas_block_150_volume`;
- added repeated group `main_wall_rebar_items`;
- changed `lintel_rebar_items` from legacy weight rows to production spec-length rows;
- expanded `lintel_items` with `mark` and `total_length_m`;
- removed legacy wall-geometry targets from the active target list:
  `main_wall_external_length`, `main_wall_reinforcement_rows`,
  `main_wall_400_reinforcement_threads`, `main_wall_250_reinforcement_threads`.

`target_aliases_ru.yaml` was aligned to the same production target codes:

- added aliases for `floors_count`;
- added aliases for `cutoff_waterproofing_load_bearing_walls_area`;
- added aliases for `lintel_total_length`;
- added aliases for `floor_2_masonry_volume`;
- changed wall/lintel rebar aliases to production row fields:
  `spec_length_m`, `kg_per_meter`;
- removed active aliases for the old wall-geometry rebar targets.

`claude_extraction_output_schema.json` now describes:

```text
main_wall_rebar_items:
  floor
  component = load_bearing_walls
  code
  name
  steel_class
  diameter_mm
  spec_length_m
  kg_per_meter

lintel_rebar_items:
  floor
  component = lintels
  code
  name
  steel_class
  diameter_mm
  spec_length_m
  kg_per_meter

lintel_items:
  mark
  length_m
  count
  total_length_m
```

The prompt now explicitly says not to use the legacy summary target
`masonry_rebar_a500_d10_weight` for production extraction. Wall rebar goes into
`main_wall_rebar_items`; lintel rebar goes into `lintel_rebar_items`; lintel marks go into
`lintel_items`.

`build_review_workbook_preview.py` was updated so review preview mappings use production target
codes, not old bridge names.

## Contract Fix Made

The contract already matched the calculator conceptually, but one path was wrong:

```text
main_wall_rebar_items.calculator_input_path
```

It was corrected from:

```text
rebar_items
```

to:

```text
main_wall_rebar_items
```

The calculator itself was not changed.

## Legacy Fields Kept Out of Production Extraction

These calculator concepts are legacy/diagnostic for this production path and should not be active
chat extraction targets:

```text
main_wall_external_length
main_wall_reinforcement_rows
main_wall_400_reinforcement_threads
main_wall_250_reinforcement_threads
masonry_rebar_a500_d10_weight
```

The new production rebar path is row-based:

```text
main_wall_rebar_items -> component=load_bearing_walls
lintel_rebar_items -> component=lintels
```

The adapter must add non-PDF per-row data such as `rod_length_m` and `unit_price_per_m` from catalog
defaults / price registry. GPT/Claude should not invent those fields from the PDF.

## Defaults / Catalog Inputs Still Required

The calculator has required inputs that are not PDF project quantities. They are not parser targets
and must be supplied later by adapter/default catalog/price registry/manual review:

```text
gas_block_d400_pallet_volume_m3
gas_block_d500_250_pallet_volume_m3
adhesive_consumption_bag_per_m3
sand_concrete_consumption_kg_per_m2_per_10mm
sand_concrete_thickness_factor
gas_block_delivery_truck_capacity_m3
gas_block_d500_150_pallet_volume_m3
parapet_chasing_base_length_m
second_light_chasing_base_length_m
parapet_rebar_base_length_m
second_light_rebar_base_length_m
```

This is an adapter/defaults task, not an extraction task. The production pipeline must fail loudly
or show manual/default-required status if these are missing before calculator execution.

## Checks

- [x] Calculator production input names checked directly.
- [x] Contract production target codes compared with parser targets.
- [x] Missing scalar parser targets added.
- [x] Legacy wall-geometry targets removed from active extraction target list.
- [x] `main_wall_rebar_items` added as production repeated group.
- [x] `lintel_rebar_items` aligned to `spec_length_m` / `kg_per_meter`.
- [x] `lintel_items` expanded with `mark` and `total_length_m`.
- [x] Prompt updated to forbid production use of legacy `masonry_rebar_a500_d10_weight`.
- [x] Review preview aliases updated away from old bridge target names.
- [x] No calculator code changed.
- [x] No project-specific quantities or page references added.
- [ ] Build the adapter/defaults layer that fills required non-PDF calculator inputs.
- [ ] Run a real extraction JSON through the multi-section review workbook once the adapter/defaults
      layer exists.
