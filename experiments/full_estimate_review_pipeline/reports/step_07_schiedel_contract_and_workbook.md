# Step 7 — Add Schiedel Vent Channels Contract

Status: completed local contract + review workbook template

Goal: add the next compact section contract after `waterproofing`, without copying old project values or deriving Schiedel material counts from legacy control numbers.

## 1. What Was Added

New contract:

```text
experiments/full_estimate_review_pipeline/sections/schiedel_vent_channels/section_contract.yaml
```

Builder default now includes:

```text
earthworks
waterproofing
schiedel_vent_channels
```

Generated workbook:

```text
experiments/full_estimate_review_pipeline/output/step_07_earthworks_waterproofing_schiedel_review.xlsx
```

## 2. Schiedel Contract Shape

Review rows:

- `schiedel_masonry_total_length_m` — primary project quantity for masonry work;
- `vent_channel_1_height_m` — optional control value;
- `vent_channel_2_height_m` — optional control value;
- `vent_channel_2_count` — optional control value;
- `schiedel_vent_channel_2x_count` — supplier/manual purchase quantity;
- `schiedel_vent_channel_3x_count` — supplier/manual purchase quantity;
- `schiedel_delivery_trips` — manual logistics quantity.

Price rows:

- `schiedel_masonry_work_rate_per_m`;
- `schiedel_vent_channel_2x_unit_price`;
- `schiedel_vent_channel_3x_unit_price`;
- `schiedel_delivery_truck_price`;
- `schiedel_delivery_work_price`.

Detail table:

- `vent_chimney_cladding_segments` — optional diagnostic/specification rows for Schiedel/vent channels.

## 3. Production Rules

Important rule preserved from the calculator docs:

```text
Schiedel 2x/3x material counts are supplier/manual specification inputs.
Do not derive them automatically from old control values.
```

The contract does not include old fixture totals, old expected results, old display quantity overrides, or old project markers.

Allowed numeric defaults:

- `consumables_rate = 0.03`, a business/formula coefficient used by the calculator.

## 4. Workbook Counts

Builder output:

| Check | Count |
|---|---:|
| project/review rows | 16 |
| price rows | 23 |
| detail table templates | 9 |
| `01_Проверка проекта` max row | 23 |
| `02_Цены себестоимости` max row | 27 |
| `03_Детали объемов` max row | 27 |

Schiedel contribution:

| Item | Count |
|---|---:|
| review rows | 7 |
| price rows | 5 |
| detail tables | 1 |
| supplier/manual rows | 3 |
| estimate lines | 9 |

## 5. Checks Run

Build:

```text
.venv/bin/python experiments/full_estimate_review_pipeline/build_review_workbook_from_contracts.py --json
```

Schiedel calculator smoke test was run against the existing calculator fixture outside the production contract.

Result:

```text
status: ok
ok: 138
mismatch: 0
```

Workbook spot checks:

- `00_Конструктор сметы`: Schiedel is included;
- `01_Проверка проекта`: Schiedel rows include AUTO_PROJECT, SUPPLIER_INPUT, and MANUAL_REVIEW rows;
- `02_Цены себестоимости`: Schiedel price section has 5 rows;
- `03_Детали объемов`: Schiedel detail table is present;
- all workbook sheets have `auto_filter = None`.
