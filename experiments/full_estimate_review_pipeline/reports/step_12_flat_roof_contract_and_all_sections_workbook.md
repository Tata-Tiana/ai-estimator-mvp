# Step 12: flat roof contract and all sections review workbook

## Result

Added the `flat_roof` review section contract and rebuilt the multi-section Google review workbook template.

Workbook:

- `experiments/full_estimate_review_pipeline/output/step_12_all_sections_review_template.xlsx`

Included section contracts, in workbook order:

1. `earthworks`
2. `foundation_slab`
3. `waterproofing`
4. `load_bearing_walls_lintels`
5. `floor_slab_1`
6. `floor_slab_2`
7. `flat_roof`
8. `schiedel_vent_channels`

## Flat roof contract

Contract:

- `experiments/full_estimate_review_pipeline/sections/flat_roof/section_contract.yaml`

The contract documents:

- AUTO_PROJECT roof geometry: roof areas by level, parapet lengths, vent wall abutment lengths, roof aerators, parapet drains, internal drains, internal drain height.
- SUPPLIER_INPUT / manual review fields: supplier-required EPS/slope plate volumes, roof work coefficient, vent shaft abutment count, gas block wall holes, crane shifts, consumables, waste removal, logistics, technical supervision, procurement/storage.
- PRICE rows for flat roof work/material lines.
- DEFAULT rows for formula/catalog parameters needed by the current calculator.
- Detail template for raw roof material specification rows.

## Workbook build check

Command:

```bash
.venv/bin/python experiments/full_estimate_review_pipeline/build_review_workbook_from_contracts.py --json
```

Build result:

- project parameter rows: 91
- price rows: 117
- detail template rows: 18
- project sheet max row: 103
- price sheet max row: 126
- details sheet max row: 46

## Calculator smoke check

Command:

```bash
.venv/bin/python experiments/flat_roof_calculator/run_case.py experiments/flat_roof_calculator/cases/test_flat_roof_detailed_project_geometry
```

Result:

- status: ok
- ok: 477
- mismatch: 0

## Production contamination check

The new flat roof contract and workbook builder were checked for old project markers and fixture/control values.

Rule preserved:

- the review workbook template must stay universal;
- no old project names, page references, control totals, or hardcoded extraction results may be used as production data;
- numeric defaults are allowed only when they are formula, catalog/package, or business defaults needed by the calculator.

