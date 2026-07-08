# Step 0 — Pipeline Architecture

Status: completed

Goal: зафиксировать общий pipeline до работы по отдельным разделам. Этот шаг нужен, чтобы не смешивать проверочную Google-таблицу с финальной сметой и не превращать `AUTO_PROJECT` параметры в строки сметы напрямую.

## 1. Canonical Pipeline

```text
chat extraction / parser output
-> review Google workbook
-> normalized review JSON
-> calculator inputs
-> calculator results
-> formula_ready rows
-> final estimate workbook
```

This is the only architecture to preserve while adding more sections.

## 2. Workbook Boundary

There are two different workbook concepts.

Review Google workbook:

- checks project inputs extracted by chat or parser;
- contains human-reviewable parameters, detail tables, prices, evidence, and statuses;
- should stay close to the source PDF/parser output;
- is not the final estimate;
- should be small enough for a human to review.

Final estimate workbook:

- contains estimate rows;
- contains formulas, helper cells, totals, and final quantities;
- is produced after calculators run;
- should not be used as the source of project extraction truth.

## 3. Data Responsibilities

| Layer | Responsibility |
|---|---|
| chat extraction / parser output | Raw project values, raw table rows, evidence, source units. |
| review Google workbook | Human validation of extracted inputs and prices. |
| normalized review JSON | Deterministic machine-readable version of reviewed workbook values. |
| calculator inputs | Section-specific JSON shaped exactly for the calculator. |
| calculator results | Quantities, formulas, helper values, and computed section results. |
| formula_ready rows | Stable row model for estimate export. |
| final estimate workbook | Client-facing or production-facing estimate workbook. |

## 4. Guardrails

- This is a universal production pipeline: it must accept a fresh chat/parser JSON for any project.
- Old calculator fixtures and old project runs are audit evidence only.
- Do not hardcode project-specific volumes, areas, lengths, counts, prices, totals, display quantities, page numbers, filenames, or expected Excel totals.
- Do not let legacy reconstruction modes become production defaults when the correct source is a reviewed project/specification value.
- Do not confuse `AUTO_PROJECT` calculator parameters with final estimate rows.
- Do not copy all calculator parameters into the review workbook just because they exist.
- Ask from the project only the leaf inputs that cannot be computed safely.
- Keep defaults in contracts/calculators, not as required project rows.
- Keep calculated values in calculator/formula-ready layers.
- Keep supplier/manual business inputs separate from project extraction inputs.
- Every section must be able to explain:
  - what comes from the project;
  - what comes from defaults;
  - what is calculated;
  - what becomes a final estimate line.

## 5. Earthworks Proof

The `earthworks` flow already proves the architecture:

```text
review workbook rows -> normalized review JSON -> calculator input JSON
-> earthworks calculator -> formula_ready rows -> exported estimate workbook
```

Reference documentation:

- `reports/step_01_earthworks_reference.md`

## 6. Acceptance Checks

- [x] One canonical pipeline is documented.
- [x] Review workbook and final estimate workbook are described as separate entities.
- [x] Each layer has one clear responsibility.
- [x] Universal production rule forbids project-specific quantities/totals from old runs.
- [x] Guardrails explain why `AUTO_PROJECT` does not equal final estimate rows.
- [x] Earthworks is named as the reference implementation.

## 7. Next Step

Step 1 documents `earthworks` as the reference section and measures its real counts.
