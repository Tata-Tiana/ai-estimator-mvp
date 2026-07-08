# Step 8 — Add Foundation Slab Contract In 00-Sheet Order

Status: completed first production contract pass + local review workbook template

Goal: add `foundation_slab` as the next section strictly in the order shown on `00_Конструктор сметы`.

## 1. What Was Added

New contract:

```text
experiments/full_estimate_review_pipeline/sections/foundation_slab/section_contract.yaml
```

Builder default order now follows `CANONICAL_SECTIONS` and only includes contracts that exist:

```text
earthworks
foundation_slab
waterproofing
schiedel_vent_channels
```

Generated workbook:

```text
experiments/full_estimate_review_pipeline/output/step_08_foundation_slab_review_template.xlsx
```

## 2. Foundation Contract Shape

This is a production-first contract pass. It uses the standards already confirmed in calculator docs:

- `formwork_calc_method = spec_area`;
- `thermal_insert_mode = standard_50_100`;
- `rebar_calc_method = spec_length_m`;
- `plywood_calc_method = actual_area_with_waste`.

Main review rows:

- membrane area;
- side formwork area from specification;
- EPS 50 mm under slab volume;
- concrete project volume;
- thermal insert 50/100 mm work lengths;
- thermal insert 50/100 mm material quantities;
- manual/supplier rows for crane, metal delivery, box metal control weight, concrete pump, logistics, consumables.

Detail table:

- `foundation_rebar_items` with steel class, diameter, specification length in linear meters, and mass per meter.

## 3. Critical Rules

Do not use legacy modes in the production review workbook:

- no perimeter x edge height formwork reconstruction;
- no rebar extraction by kg as the primary PDF unit;
- no old display quantity overrides;
- no old expected totals.

Critical distinctions:

- EPS 50 mm under slab is a volume in `м3`; EPS laying area is calculated;
- side formwork area is `м2`; it must not be confused with EPS edge volume;
- foundation slab concrete is separate from floor slab, beam, lintel, or wall concrete.

## 4. Workbook Counts

Builder output:

| Check | Count |
|---|---:|
| project/review rows | 30 |
| price rows | 44 |
| detail table templates | 10 |
| `01_Проверка проекта` max row | 38 |
| `02_Цены себестоимости` max row | 49 |
| `03_Детали объемов` max row | 30 |

Foundation contribution:

| Item | Count |
|---|---:|
| review rows | 14 |
| price rows | 21 |
| detail tables | 1 |
| supplier/manual rows | 6 |

## 5. Checks Run

Build:

```text
.venv/bin/python experiments/full_estimate_review_pipeline/build_review_workbook_from_contracts.py --json
```

Foundation calculator smoke test was run against the existing `rebar spec length` fixture outside the production contract and completed successfully.

Workbook spot checks:

- section order on `01`, `02`, and `03` follows `00_Конструктор сметы`;
- `foundation_slab` appears between `earthworks` and `waterproofing`;
- all workbook sheets have `auto_filter = None`;
- no old project markers or old fixture totals are stored in the new contract/report.

