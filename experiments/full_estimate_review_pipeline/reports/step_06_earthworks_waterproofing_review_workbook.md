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
05_Контракты
06_Raw contracts
```

Sheets `05` and `06` are technical sheets. They replace ad hoc debug output with contract-level diagnostics:

- `05_Контракты`: counts and source files per section;
- `06_Raw contracts`: raw JSON form of contract blocks.

## 4. Counts

Builder output:

| Check | Count |
|---|---:|
| project parameter rows | 9 |
| price rows | 18 |
| detail table templates | 2 |
| `01_Проверка проекта` max row | 15 |
| `02_Цены себестоимости` max row | 21 |
| `03_Детали объемов` max row | 4 |

Expected:

- earthworks project rows: 7;
- waterproofing project rows: 2;
- total project rows: 9;
- earthworks price rows: 12;
- waterproofing price rows: 6;
- total price rows: 18;
- earthworks detail tables: `trench_routes`, `communications_pipe_items`;
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

Visual rule:

- section title rows are dark gray;
- status/attention colors are reserved for real row status only:
  - found = green;
  - review/check = peach;
  - missing = red.

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
  "detail_template_rows": 2
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
