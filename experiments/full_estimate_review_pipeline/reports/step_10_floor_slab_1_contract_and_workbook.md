# Step 10: Floor Slab 1 Contract

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

The new contract is a first production-oriented draft for `floor_slab_1`.
It is intentionally compact, but it includes the inputs most likely to be requested by the calculator reader.

## Contract Added

File:

- `experiments/full_estimate_review_pipeline/sections/floor_slab_1/section_contract.yaml`

Included review parameters:

- `total_concrete_volume_from_spec_m3`
- `slab_thickness_m`
- `slab_edge_perimeter_m`
- `main_formwork_area_m2`
- `edge_formwork_area_m2`
- `beams_formwork_area_m2`
- `slab_outer_edge_eps_work_length_m`
- `edge_insulation_height_m`
- `slab_edge_eps_material_area_m2`
- `bottom_slab_eps_work_area_m2`
- `total_eps_volume_from_spec_m3`

Included detail tables:

- `floor_slab_1_rebar_items`
- `beam_items`
- `beam_table_controls`

Included manual/supplier review fields:

- `formwork_rebar_crane_shifts`
- `concrete_pump_shifts`

## Production Defaults

The contract pins the production modes from the calculator documentation:

- `formwork_areas_calc_method = spec_formwork_areas`
- `rebar_calc_method = spec_length_items`
- `insulation_calc_method = spec_work_quantities`
- `formwork_rate_calc_method = direct_section_rate`
- `formwork_delivery_calc_method = area_threshold`
- `metal_delivery_calc_method = section_output_only`

Numeric defaults in the contract are formula/catalog/business defaults, not project values.

## Critical Separations

The contract keeps these quantities separate:

- slab concrete vs beam concrete;
- EPS material volume in m3 vs formwork area in m2;
- EPS bottom work area vs under-slab formwork area;
- EPS edge material area vs edge formwork area;
- beam rows vs total/control rows in a beam table;
- current section rebar weight output vs box-level metal delivery.

## Workbook

Generated workbook:

- `experiments/full_estimate_review_pipeline/output/step_10_floor_slab_1_review_template.xlsx`

Build summary:

- project review rows: 57
- price rows: 85
- detail template rows: 16
- contract order used by builder:
  - `earthworks`
  - `foundation_slab`
  - `waterproofing`
  - `load_bearing_walls_lintels`
  - `floor_slab_1`
  - `schiedel_vent_channels`

The `00_Конструктор сметы` sheet still shows all eight canonical sections in order, including future sections without contracts.

## Guardrails

This step does not add project-specific values to the contract.
The workbook template remains neutral: real parser/chat values should be attached later by the workbook population step or by manual review.

## Checks

Commands run:

- `.venv/bin/python experiments/full_estimate_review_pipeline/build_review_workbook_from_contracts.py --json`
- `.venv/bin/python -m py_compile experiments/full_estimate_review_pipeline/build_review_workbook_from_contracts.py experiments/floor_slab_1_calculator/floor_slab_1_calculator.py experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py`
- `.venv/bin/python experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py experiments/floor_slab_1_calculator/cases/test_floor_slab_1_rebar_spec_lengths`
- contamination scan on the new contract/builder/report and generated workbook for old project markers/control values
- `git diff --check`

Result:

- workbook builds successfully;
- Python files compile;
- calculator smoke test runs successfully;
- no old project markers/control values found in the new contract/builder/report or generated workbook;
- no whitespace errors found.
