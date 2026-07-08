# Step 11: Floor Slab 2 Contract

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

The new contract is a first production-oriented draft for `floor_slab_2`.
It follows the calculator's current scope: slab 2 has no beam calculation block, but keeps `beams_formwork_area_m2` as a spec field/default-zero for a consistent workbook shape.

## Contract Added

File:

- `experiments/full_estimate_review_pipeline/sections/floor_slab_2/section_contract.yaml`

Included review parameters:

- `main_formwork_area_m2`
- `edge_formwork_area_m2`
- `beams_formwork_area_m2`
- `slab_edge_perimeter_m`
- `edge_insulation_height_m`
- `concrete_placing_volume_m3`
- `slab_area_m2`

Included detail table:

- `floor_slab_2_rebar_items`

Included manual/supplier review fields:

- `crane_shifts`
- `concrete_pump_shifts`

## Production Defaults

The contract pins the production modes from the calculator documentation:

- `formwork_area_calc_method = spec_formwork_area`
- `formwork_delivery_calc_method = area_threshold`
- `rebar_calc_method = spec_length_items`

Numeric defaults in the contract are formula/catalog/business defaults, not project values.

## Critical Separations

The contract keeps these quantities separate:

- main/deck formwork area vs edge formwork area;
- edge perimeter in running meters vs edge formwork area in square meters;
- EPS material volume in m3 vs formwork area in m2;
- concrete volume as a direct spec value, not derived from slab area and thickness;
- slab 1 and slab 2 formwork/rebar/concrete rows.

## Workbook

Generated workbook:

- `experiments/full_estimate_review_pipeline/output/step_11_floor_slab_2_review_template.xlsx`

Build summary:

- project review rows: 66
- price rows: 99
- detail template rows: 17
- contract order used by builder:
  - `earthworks`
  - `foundation_slab`
  - `waterproofing`
  - `load_bearing_walls_lintels`
  - `floor_slab_1`
  - `floor_slab_2`
  - `schiedel_vent_channels`

The `00_Конструктор сметы` sheet still shows all eight canonical sections in order, including future sections without contracts.

## Guardrails

This step does not add project-specific values to the contract.
The workbook template remains neutral: real parser/chat values should be attached later by the workbook population step or by manual review.

## Checks

Commands run:

- `.venv/bin/python experiments/full_estimate_review_pipeline/build_review_workbook_from_contracts.py --json`
- `.venv/bin/python -m py_compile experiments/full_estimate_review_pipeline/build_review_workbook_from_contracts.py experiments/floor_slab_2_calculator/calculator.py experiments/floor_slab_2_calculator/run_case.py`
- `.venv/bin/python experiments/floor_slab_2_calculator/run_case.py experiments/floor_slab_2_calculator/cases/test_floor_slab_2_rebar_spec_lengths`
- contamination scan on the new contract/builder/report and generated workbook for old project markers/control values
- `git diff --check`

Result:

- workbook builds successfully;
- Python files compile;
- calculator smoke test passes with 93 ok / 0 mismatch;
- no old project markers/control values found in the new contract/builder/report or generated workbook;
- no whitespace errors found.
