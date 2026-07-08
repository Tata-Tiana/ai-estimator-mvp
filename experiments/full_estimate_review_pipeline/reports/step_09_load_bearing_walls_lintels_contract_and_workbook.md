# Step 09: Load-Bearing Walls And Lintels Contract

## Scope

Added the next section in the canonical review workbook order:

1. earthworks
2. foundation_slab
3. waterproofing
4. load_bearing_walls_lintels
5. floor_slab_1
6. floor_slab_2
7. flat_roof
8. schiedel_vent_channels

The new contract is a first production-oriented draft for `load_bearing_walls_lintels`.
It intentionally uses spec-based calculator modes where the calculator already supports them.

## Contract Added

File:

- `experiments/full_estimate_review_pipeline/sections/load_bearing_walls_lintels/section_contract.yaml`

Included review parameters:

- `floors_count`
- `cutoff_waterproofing_load_bearing_walls_area_m2`
- `main_wall_gas_block_400_spec_volume_m3`
- `main_wall_gas_block_250_spec_volume_m3`
- `lintel_total_length_m`
- `lintel_concrete_spec_volume_m3`
- `floor_2_masonry_volume_m3`
- `parapet_masonry_volume_m3`
- `vent_chimney_gas_block_spec_volume_m3`

Included detail tables:

- `main_wall_rebar_items`
- `lintel_rebar_items`
- `lintel_items`

Included manual/supplier review fields:

- `flat_roof_enabled`
- `concrete_delivery_trips`
- `parapet_crane_shifts`
- `waste_removal_trucks`
- `walls_consumables_tool_amortization_amount_raw`

## Production Defaults

The contract pins the production modes from the calculator documentation:

- `scaffolding_calc_method = floors_based`
- `cutoff_waterproofing_calc_method = spec_area`
- `lintel_length_calc_method = spec_total_length`
- `lintel_concrete_calc_method = spec_volume`
- `main_wall_rebar_calc_method = spec_length_items`
- `lintel_rebar_calc_method = spec_length_items`
- `main_walls_crane_calc_method = delivery_trucks_threshold`
- `upper_floor_calc_method = floor_2_spec_volume`
- `parapet_calc_method = flat_roof_spec_volume`
- `vent_chimney_cladding_calc_method = flat_roof_spec_volume`
- `vent_chimney_geometry_calc_method = spec_volume_thickness`

Numeric defaults in the contract are formula/catalog/business defaults, not project values.
They are kept because the calculator needs them for formulas and purchase rounding.

## Workbook

Generated workbook:

- `experiments/full_estimate_review_pipeline/output/step_09_load_bearing_walls_lintels_review_template.xlsx`

Build summary:

- project review rows: 44
- price rows: 68
- detail template rows: 13
- contract order used by builder:
  - `earthworks`
  - `foundation_slab`
  - `waterproofing`
  - `load_bearing_walls_lintels`
  - `schiedel_vent_channels`

The `00_Конструктор сметы` sheet still shows all eight canonical sections in order, including future sections without contracts.

## Guardrails

This step does not add project-specific values to the contract.
The workbook template is still a neutral review template: real parser/chat JSON values should be attached later by the workbook population step.

Important mapping notes:

- wall rebar and lintel rebar use spec length rows as primary input;
- lintel concrete is separate from slab concrete and beam concrete;
- vent/chimney gas block volume is separate from Schiedel piece counts;
- cutoff waterproofing is only for load-bearing walls, not partition walls;
- legacy wall-length reconstruction fields are intentionally not review rows.

## Checks

Commands run:

- `.venv/bin/python experiments/full_estimate_review_pipeline/build_review_workbook_from_contracts.py --json`
- `.venv/bin/python -m py_compile experiments/full_estimate_review_pipeline/build_review_workbook_from_contracts.py experiments/load_bearing_walls_lintels_calculator/load_bearing_walls_lintels_calculator.py experiments/load_bearing_walls_lintels_calculator/run_load_bearing_walls_lintels_calc.py`
- `.venv/bin/python experiments/load_bearing_walls_lintels_calculator/run_load_bearing_walls_lintels_calc.py experiments/load_bearing_walls_lintels_calculator/cases/test_rebar_spec_length_by_floor_component`
- contamination scan on the new contract/builder and generated workbook for old project markers/control values
- `git diff --check`

Result:

- workbook builds successfully;
- Python files compile;
- calculator smoke test runs successfully;
- no old project markers/control values found in the new contract/builder or generated workbook;
- no whitespace errors found.
