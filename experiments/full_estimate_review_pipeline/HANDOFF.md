# Full Estimate Review Pipeline — Handoff And Checklist

Use this file when a new chat starts.

If the user says "прочитай инструкцию и продолжай", read this file first, then read the current step report in `reports/`.

## Current Goal

Build a Google review workbook for all 8 estimate sections, then make it flow into calculators and final estimate export the same way the earthworks flow already does.

This is a universal production pipeline. It must accept a new chat/parser JSON for any project and produce review/calculator/final-estimate artifacts from that JSON. Old calculator fixtures and old project runs are reference behavior only; they are not allowed to provide production quantities, prices, display quantities, totals, or hidden overrides.

The important distinction:

- Review workbook = human-checkable inputs, prices, details, parser evidence.
- Final estimate workbook = estimate rows, formulas, helper cells, totals.

Do not confuse `AUTO_PROJECT` rows with final estimate rows.

## Canonical Pipeline

The target pipeline is:

```text
chat extraction / parser output
-> Google review workbook
-> normalized review JSON
-> calculator input JSON
-> calculator result JSON
-> formula_ready rows
-> final estimate workbook
```

The earthworks section already proves this pattern.

## Universal Production Rule

Every step must protect against project-specific contamination.

Allowed:

- source field names;
- formulas;
- source classes;
- unit normalization rules;
- calculator code paths;
- representative line counts used only for coverage checks;
- default/catalog values explicitly marked as defaults.

Forbidden in production contracts, adapters, review workbook builders, normalized JSON, and formula-ready builders:

- project-specific volumes, areas, lengths, counts, prices, totals, display quantities, page numbers, or filenames;
- copying values from old fixtures, old result JSON, old Excel snapshots, screenshots, or old parser outputs;
- hardcoded "expected total" or "Excel match" values;
- treating legacy reconstruction modes as production defaults when a specification/project value should be read from JSON;
- using any old project name as logic, filter, path convention, or data source.

Before committing any future step, run a text search for old project names and known fixture-only phrases in the files touched by that step. If a match remains, it must be either removed or explicitly documented as non-production reference evidence.

## Reference Earthworks Flow

Start with:

- `experiments/full_estimate_review_pipeline/reports/step_01_earthworks_reference.md`

Earthworks reference files:

- review workbook: project-specific reference workbook, exact path documented only in the step report if needed for audit.
- review reader: `experiments/earthworks_review_to_calculator/review_workbook_reader.py`
- calculator input adapter: `experiments/earthworks_review_to_calculator/calculator_input_builder.py`
- calculator: `experiments/earthworks_calculator/earthworks_calculator.py`
- formula-ready builder: `experiments/earthworks_review_to_calculator/build_formula_ready_result.py`
- Excel export: `experiments/earthworks_review_to_calculator/export_formula_ready_to_excel.py`

Earthworks baseline counts:

- normalized parameters: 7
- price rows: 12
- detail groups: `trench_routes`, `communications_pipe_items`
- calculator estimate lines: 11
- formula-ready rows: 11
- helper cells: 27

Lesson: earthworks review input is small; the calculator/formula-ready layer expands it into estimate rows.

## Step Checklist

### Step 0 — Pipeline Architecture

- [x] Document the canonical pipeline:
  - chat extraction / parser output;
  - review Google workbook;
  - normalized review JSON;
  - calculator inputs;
  - calculator results;
  - formula_ready rows;
  - final estimate workbook.
- [x] State that review workbook and final estimate workbook are different entities.
- [x] State that review workbook checks inputs and final estimate workbook shows estimate rows.
- [x] State that the pipeline is universal and cannot depend on old project values.
- [x] Commit step 0 separately.

Step report:

- `reports/step_00_architecture.md`

### Step 1 — Earthworks Reference

- [x] Identify earthworks reference files.
- [x] Measure baseline counts.
- [x] List review parameters, price keys, detail groups, estimate lines.
- [x] Define guardrails for the next sections.
- [x] Mark the earthworks run as reference behavior, not production data.
- [x] Commit step 1 separately.

Step report:

- `reports/step_01_earthworks_reference.md`

### Step 2 — Common Section Contract Format

- [x] Design `section_contract.yaml` schema.
- [x] Include required blocks:
  - section metadata;
  - review parameters;
  - detail tables;
  - price keys;
  - defaults;
  - auto-calculated fields;
  - supplier inputs;
  - calculator input mapping;
  - estimate lines;
  - formula-ready/helper fields;
  - validation checks.
- [x] Create a report describing the schema and acceptance checks.
- [x] Do not yet implement every section.
- [x] Include project-specific contamination checks in the contract rules.
- [x] Commit step 2 separately.

Suggested report:

- `reports/step_02_section_contract_format.md`

Template:

- `templates/section_contract.template.yaml`

### Step 3 — All New Sections Quantity Matrix

- [x] Read calculators for 7 new sections.
- [x] Build "estimate line -> quantity formula -> leaf inputs -> source class" matrix.
- [x] Identify what must come from project, what is default/price/supplier/manual, and what is calculated.
- [x] Do not write new calculator code.
- [x] Flag old fixture/result values as audit evidence only, not production inputs.
- [x] Commit step 3 separately.

Step report:

- `reports/step_03_all_sections_quantity_matrix.md`

### Step 4 — Section Order

- [x] Choose low-risk section order.
- [x] Start with `earthworks` as reference behavior.
- [x] Use `waterproofing` as the first new contract.
- [x] Keep the hardest sections for later.
- [x] Commit step 4 separately.

Selected order:

1. `earthworks`
2. `waterproofing`
3. `schiedel_vent_channels`
4. `foundation_slab`
5. `floor_slab_2`
6. `floor_slab_1`
7. `flat_roof`
8. `load_bearing_walls_lintels`

Step report:

- `reports/step_04_section_order.md`

### Step 5 — WaterProofing Contract

- [x] Read `experiments/waterproofing_calculator/`.
- [x] Read `reports/step_03_all_sections_quantity_matrix.md`.
- [x] Create draft contract for `waterproofing`.
- [x] Run contract checks manually in the report.
- [x] Commit step 5 separately.

Suggested files:

- `sections/waterproofing/section_contract.yaml`
- `reports/step_05_waterproofing_contract.md`

### Step 6 — Earthworks + Waterproofing Review Workbook Prototype

- [ ] Reuse earthworks reference behavior without rewriting it blindly.
- [ ] Build a review workbook from section contracts for `earthworks + waterproofing`.
- [ ] Keep review workbook separate from final estimate workbook.
- [ ] Verify sheet counts and key rows.
- [ ] Commit step 6 separately.

### Step 7 — Multi-Section Normalized Review JSON

- [ ] Read prototype workbook.
- [ ] Produce normalized JSON shaped by section:

```json
{
  "sections": {
    "earthworks": {},
    "waterproofing": {}
  }
}
```

- [ ] Prove that manual overrides are preserved.
- [ ] Commit step 7 separately.

### Step 8 — Waterproofing Review-To-Calculator Adapter

- [ ] Convert normalized waterproofing review data into calculator input.
- [ ] Add defaults and prices deterministically.
- [ ] Run existing waterproofing calculator.
- [ ] Commit step 8 separately.

### Step 9 — Waterproofing Formula-Ready

- [ ] Convert waterproofing calculator result into formula-ready rows.
- [ ] Each estimate line must have quantity, prices, formula model or explicit reason.
- [ ] Formula-ready row count must match calculator estimate line count.
- [ ] Commit step 9 separately.

### Step 10 — Repeat Section By Section

Recommended order:

- [ ] `schiedel_vent_channels`
- [ ] `foundation_slab`
- [ ] `floor_slab_2`
- [ ] `floor_slab_1`
- [ ] `flat_roof`
- [ ] `load_bearing_walls_lintels`

Each section gets its own contract, adapter, formula-ready report, and commit.

## Guardrails For Every Step

Before marking a step complete, run these checks mentally and, where possible, with scripts.

### 1. Workbook Role Check

Question: Am I building a review workbook or a final estimate workbook?

Fail if a review row is treated as a final estimate line without passing through calculator/formula-ready.

### 2. Source Class Check

Every leaf input must be one of:

- `AUTO_PROJECT`
- `DETAIL_TABLE`
- `DEFAULT`
- `AUTO_CALCULATED`
- `PRICE`
- `SUPPLIER_INPUT`
- `MANUAL_REVIEW`

Fail if the source is "kind of from somewhere".

### 3. End-To-Start Trace Check

For every estimate line:

```text
estimate line -> quantity formula -> leaf inputs -> source class
```

Fail if quantity formula or leaf inputs are missing.

### 4. Adapter Check

There must be a deterministic path:

```text
review workbook -> normalized JSON -> calculator input
```

Fail if the calculator input is manually copied from old fixture JSON.

### 5. Calculator Check

The existing calculator for the section must run from generated input.

Fail if the section bypasses the calculator.

### 6. Formula-Ready Check

Every calculator estimate line must appear in formula-ready.

Fail if:

- calculator result has N lines;
- formula-ready has a different count;
- and the difference is not explicitly explained.

### 7. Price Check

Every price used by a calculator line must have a `calc_price_key` or explicit zero/fixed reason.

Fail if price mapping depends only on a Russian row label.

### 8. Project-Specific Contamination Check

Question: can this step run from a fresh chat/parser JSON for a different project?

Fail if touched production files contain:

- old project names or old job path fragments;
- fixture-only values copied as quantities, totals, display quantities, or prices;
- hardcoded expected totals used to force old Excel equality;
- old parser/page/table evidence treated as a universal rule.

Allowed only in reports: old project references used to explain why a legacy calculator mode is risky. They must never become contract defaults or adapter output.

### 9. Dirty Worktree Check

Before commits:

```bash
git status --short
```

Only stage files from the current step. Do not use `git add .` in this repo unless the user explicitly asks and the diff was reviewed.

## Commit Policy

Commit each accepted step separately.

Suggested commit messages:

- `docs(full-estimate): record earthworks reference contract`
- `docs(full-estimate): define section contract format`
- `docs(full-estimate): map section quantity sources`
- `feat(full-estimate): add waterproofing section contract`
- `feat(full-estimate): build earthworks waterproofing review workbook`

Before committing:

1. Run `git status --short`.
2. Stage only current-step files.
3. Run `git diff --cached --stat`.
4. Commit.
5. Tell the user the commit hash and what was included.

## Current State

Completed:

- Step 0 pipeline architecture was documented.
- Step 1 reference report was created.
- Step 2 common section contract format was defined.
- Step 3 all new sections quantity matrix was drafted.
- Step 3b production contamination audit was documented.
- Step 4 section order was selected.
- Step 5 waterproofing section contract was drafted.

Next:

- Step 6: build the `earthworks + waterproofing` review workbook prototype.

Do not start coding all 8 sections at once.
