# Step 6 — Earthworks + Waterproofing Review Workbook

Status: completed local workbook prototype

Goal: build the first real multi-section review workbook from `section_contract.yaml` files, not from a flat preview list and not from old project workbook rows.

## 1. What Was Built

Builder:

```text
experiments/full_estimate_review_pipeline/build_review_workbook_from_contracts.py
```

Contracts used:

```text
experiments/full_estimate_review_pipeline/sections/earthworks/section_contract.yaml
experiments/full_estimate_review_pipeline/sections/waterproofing/section_contract.yaml
```

Generated local workbook:

```text
experiments/full_estimate_review_pipeline/output/step_06_earthworks_waterproofing_review.xlsx
```

This local `.xlsx` is the checkable artifact before publishing to Google Sheets.

## 2. Google Sheet Build Stage

The Google review table stage is split into two checkable substeps:

1. Local workbook build:
   `section_contract.yaml -> review workbook .xlsx`.
2. Google publish:
   reviewed local `.xlsx -> Google Sheet`.
3. Review download:
   `Google Sheet with Elena edits -> downloaded .xlsx -> normalized review JSON -> calculator inputs`.

Step 6 completes substep 1. Substeps 2 and 3 should be checked separately after the local workbook structure is approved, because publishing tests OAuth/network/sheet behavior, while downloading back tests the real production handoff: Elena's corrections must be read from the downloaded workbook and then passed into calculators.

Hidden technical columns are part of that download-back check, but they are not the whole point. The real acceptance condition is:

```text
Elena edits Google Sheet
-> system downloads the edited workbook
-> reader builds normalized review JSON from the downloaded workbook
-> calculator adapters use those reviewed values
```

## 3. Workbook Sheets

The generated workbook contains:

```text
00_Конструктор сметы
01_Проверка проекта
02_Цены себестоимости
03_Детали объемов
04_Инструкция
05_Кандидаты parser
06_Сырые данные parser
```

Sheets `05` and `06` are technical sheets, named to match the existing Google review workbook convention. In this contract-only prototype they use block-style diagnostics:

- `05_Кандидаты parser`: run summary, section contract counts, and planned detail groups until real parser candidates are connected;
- `06_Сырые данные parser`: run summary and raw JSON form of contract blocks until real raw parser data is connected.

## 4. Counts

Builder output:

| Check | Count |
|---|---:|
| project parameter rows | 9 |
| price rows | 18 |
| detail table templates | 8 |
| `01_Проверка проекта` max row | 15 |
| `02_Цены себестоимости` max row | 21 |
| `03_Детали объемов` max row | 24 |

Expected:

- earthworks project rows: 7;
- waterproofing project rows: 2;
- total project rows: 9;
- earthworks price rows: 12;
- waterproofing price rows: 6;
- total price rows: 18;
- earthworks detail tables: `trench_routes`, `communications_pipe_items`;
- generic future detail templates: `rebar_items`, `beam_items`, `lintel_items`, `vent_chimney_cladding_segments`, `material_spec_rows`, `raw_table_rows`;
- waterproofing detail tables: none.

## 5. Layout Decisions

Rows are grouped by section:

```text
Раздел
  parameter row
  parameter row
Раздел
  parameter row
```

This matches the estimate-like grouping requested for the review workbook, while keeping the review workbook separate from the final estimate workbook.

`02_Цены себестоимости` is also grouped by section, so Elena can review prices in the same mental order as the estimate sections. The visible price sheet keeps only user-facing columns; technical keys remain hidden.

`03_Детали объемов` now contains the two earthworks reference detail tables plus empty future templates for the repeated PDF/table structures we already know will be needed:

- trenches;
- communications;
- rebar;
- beams;
- lintels;
- Schiedel / vent-channel segments;
- material specification rows;
- raw PDF table rows before target mapping.

Visual rule:

- table header rows are light gray (`D9D9D9`), with black bold Arial 10;
- section/block title rows are the same light gray used by the earthworks review workbook (`E7E6E6`), with black bold Arial 10;
- normal data rows use Arial 11;
- status/attention colors are reserved for real row status only:
  - found = green;
  - review/check = peach;
  - missing = red.
- header filter arrows are not enabled in the local workbook; Google Sheets may show its own UI controls only if filters are later turned on manually.
- `04_Инструкция` keeps a narrow numeric first column to avoid spreadsheet "number stored as text" indicators.
- `03_Детали объемов` follows the earthworks reference layout: gray block rows, white data rows, and a blank row between detail blocks.

Hidden technical columns are kept for deterministic readers:

- `01_Проверка проекта`: section/technical/source fields;
- `02_Цены себестоимости`: price key/registry/fallback/source fields;
- `03_Детали объемов`: section/detail table keys.

The workbook does not add project values. It creates empty cells for parser/chat JSON or manual review to fill later.

## 6. Checks Run

Command:

```text
.venv/bin/python experiments/full_estimate_review_pipeline/build_review_workbook_from_contracts.py --json
```

Result:

```json
{
  "project_parameter_rows": 9,
  "price_rows": 18,
  "detail_template_rows": 8
}
```

Project contamination check:

- no old project names or markers are needed by the builder;
- no old project values are copied into workbook rows;
- numeric defaults remain in contracts/default blocks, not in project extraction cells.

## 7. Next Checkpoint

Before Step 7 reads the workbook into normalized JSON, verify the local workbook visually:

```text
experiments/full_estimate_review_pipeline/output/step_06_earthworks_waterproofing_review.xlsx
```

After visual approval, add a separate Google publish step:

```text
local review workbook .xlsx
-> Google Sheet
-> Elena edits/checks values
-> downloaded workbook
-> normalized review JSON
-> calculator input
```

That publish/download step should confirm both things:

- Elena's corrections in visible columns are read back and override parser values;
- Google Sheets did not drop hidden technical columns needed by the reader.
