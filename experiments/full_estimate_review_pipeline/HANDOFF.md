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

## Sheet 01/02/03 Rule (fixed 2026-07-09, read this before touching any section_contract.yaml)

**There is no `DETAIL_TABLE` source class and no separate "detail table" data source.**
It existed in this pipeline's schema/contracts from Step 2 onward and was removed on
2026-07-09 from the template and all 8 section contracts after the user caught it: it had
calculator adapters silently reading project quantities from sheet 03 instead of from the
reviewed sheet 01 row (confirmed as a real, live bug for earthworks
`communications_length_m`, not just a naming issue — see the fix in
`sections/earthworks/section_contract.yaml`). If you see `DETAIL_TABLE` anywhere (a stale
report, a half-finished branch, model memory from before this fix), it is wrong; do not
recreate it.

The rule, in one paragraph: **every piece of project data extracted from the PDF/chat JSON —
scalar or repeated-row group (rebar by diameter, trench routes, pipe items, beam items,
lintel items, ...) — is a row on sheet `01_Проверка проекта`, one row per value or per
repeated item.** All prices are rows on sheet `02_Цены себестоимости`. **The calculator input
adapter reads only from sheet 01 and sheet 02** (plus contract `defaults`/`supplier_inputs`,
which are not project data). Sheet `03_Детали объемов` is a **read-only reference mirror**:
the workbook builder may copy the same repeated-row groups onto it, formatted like the PDF
spec table, purely so Elena can eyeball it without opening the PDF — but it is generated FROM
sheet 01, Elena does not edit it as the primary correction surface, and the adapter must never
read it back as an independent input.

In `section_contract.yaml` terms:

- A repeated-row group is a `review_parameters` entry with `value_kind: repeated_rows` and a
  `columns:` list (not a separate `detail_tables:` block).
- `source_class` stays `AUTO_PROJECT` for repeated-row groups exactly like for scalars — it is
  still project data from the PDF, just shaped as multiple rows instead of one cell.
- Set `mirror_to_details_sheet: true` on entries that should also render on sheet 03 for
  convenience, with a `mirror_notes` field explaining that sheet 03 is a copy, not a source.
- `calculator_input_mapping` / `auto_calculated` / `estimate_lines` leaf inputs reference
  `review_parameters.<key>`, never `detail_tables.<key>`.

Known follow-up (not yet done as of 2026-07-09): `build_review_workbook_from_contracts.py`
still reads `contract.get("detail_tables")` in several places to populate sheet 03
(`build_review_workbook_from_contracts.py:311,507,573,600,615,627,689`). Now that no contract
has a `detail_tables` key, sheet 03 will render empty for what used to be detail tables until
the builder is updated to read `review_parameters` entries with `mirror_to_details_sheet: true`
instead. Fix the builder before assuming sheet 03 output is complete.

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

### Numeric Defaults Rule

Do not delete numeric defaults just because they are numbers.

For every numeric constant or coefficient in a calculator, first check the June Elena/manual review
materials and section reports (`elena_parameter_review_pack`, paid calculator change reports,
calculator README/report files). Then classify it:

- `AUTO_PROJECT`: project quantity from parser/chat JSON or reviewed workbook — scalar or
  repeated-row group, always a sheet-01 row (see the Sheet 01/02/03 Rule above; there is no
  separate detail-table class);
- `PRICE`: price registry/project price/reviewed price row;
- `DEFAULT`: formula default, method constant, business coefficient, or catalog/package value;
- `AUTO_CALCULATED`: derived by adapter/calculator/formula-ready;
- `SUPPLIER_INPUT`: external supplier layout/quote input;
- `MANUAL_REVIEW`: real human decision that is not a default and not in the project JSON.

Production contracts must keep confirmed `DEFAULT` numeric values when formulas require them.
Otherwise the calculator input adapter will produce incomplete inputs and formulas will fail.

Only remove or null a number when it is project-specific, fixture-only, an old expected total,
a display quantity copied from an old workbook, or a legacy override. If unsure, leave it out of
project extraction but document the uncertainty as `MANUAL_REVIEW` or `DEFAULT` pending confirmation;
do not silently drop a formula coefficient.

Forbidden in production contracts, adapters, review workbook builders, normalized JSON, and formula-ready builders:

- project-specific volumes, areas, lengths, counts, prices, totals, display quantities, page numbers, or filenames;
- copying values from old fixtures, old result JSON, old Excel snapshots, screenshots, or old parser outputs;
- hardcoded "expected total" or "Excel match" values;
- treating legacy reconstruction modes as production defaults when a specification/project value should be read from JSON;
- using any old project name as logic, filter, path convention, or data source.

Before committing any future step, run a text search for old project names and known fixture-only phrases in the files touched by that step. If a match remains, it must be either removed or explicitly documented as non-production reference evidence.

## Universalization Workstream (started 2026-07-18)

Customer explicitly asked to validate calculators/parser against several more real projects and make
the whole box-shell estimate system adaptive to different architectural/structural variations, not
tuned to one house. ЮСВ shaped the original 8 contracts; ТРЦ (2026-07-13..15) forced real optional
structure into `load_bearing_walls_lintels`/`waterproofing`; a third project (АРК) surfaced five more
rigid spots plus one correction to a rule derived from ТРЦ (D400/D500-by-block-width is a default, not
a hard constant).

Read, in this order, before touching any section_contract.yaml for this workstream:

- `reports/step_20_ark_third_project_stress_test.md` — structural findings, per section, with an
  explicit out-of-scope list (canopies, above-grade columns, windows, blind-area apron — all
  confirmed excluded 2026-07-18).
- `UNIVERSALIZATION_PLAN.md` (this directory) — the P1/P2/P3 prioritized checklist those findings
  drive. Update its checkboxes as items land; do not start a P2 item before its P1 prerequisites in
  the same section are done.
- `reports/step_21_ark_real_extraction_crosscheck.md` — the real chat-extraction pass against АРК
  (2026-07-18), crosschecked against step_20/the plan. Confirms every prediction in the plan (several
  turned out worse than the manual-PDF read suggested); adds two new P1/P2 items (both resolved by
  2026-07-19 after reading the actual calculator code — see the file for corrections).
- `reports/step_22_trc_real_extraction_audit.md` — a real chat-extraction pass against ТРЦ (2026-07-19,
  files supplied by the user), auditing whether ТРЦ is fully ready for the pipeline and how much of
  its remaining gaps the ARK-derived plan already covers. Most do; three plan items needed expanding
  (`slab_zones[]` scope, a new "source more aggregated than contract" rule, Schiedel shaft-count vs
  module-count). One finding — several КР2 pages carry a different project's title block — is a
  standing precondition requiring architect confirmation, not a code fix.

No contract edit from this workstream has shipped yet as of 2026-07-19 — real chat-extraction passes
against both АРК (step_21) and ТРЦ (step_22) are now done; next is P1 implementation with explicit
authorization before any calculator.py edit.

Since then (2026-07-20/21), the P1 calculator.py items have shipped (`wall_block_items[]`,
`slab_zones[]` for foundation_slab/floor_slab_1, `edge_and_beam_formwork_area_combined_m2` for
floor_slab_1) — see `UNIVERSALIZATION_PLAN.md` checkboxes and memory (`p1_wall_block_items_shipped`,
`p1_slab_zones_shipped`, `p1_floor_slab_1_combined_formwork_shipped`).

## Section-Within-Section & Capture Status (started 2026-07-22)

Read `SECTION_WITHIN_SECTION_AND_CAPTURE_STATUS_PLAN.md` (this directory) before touching
`populate_review_workbook_from_extraction.py`, `build_review_workbook_from_contracts.py`, any
`section_contract.yaml`, or the extraction prompt. Covers a verified, non-hypothetical problem: data
that's already captured in schema (`wall_block_items`, `foundation_wall_items`, `column_footing_items`
— partitions/columns/foundation walls) does not actually reach Elena on sheet 01 today (three
compounding bugs), and separately, a real extraction run mistagged partition rebar in a way that would
let it slip past the calculator's own guardrail and get silently priced as load-bearing-wall rebar.
Also defines the `capture_status` model (active/in_development/outside_schema, field-level granularity)
and a `future_section:*` tag for the Elena-approved roadmap of sections that don't exist yet (see
memory `future_estimate_sections_roadmap`). Nothing implemented yet as of 2026-07-22 — plan only.

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

- [x] Reuse earthworks reference behavior without rewriting it blindly.
- [x] Build a review workbook from section contracts for `earthworks + waterproofing`.
- [x] Keep review workbook separate from final estimate workbook.
- [x] Verify sheet counts and key rows.
- [x] Commit step 6 separately.

Builder:

- `build_review_workbook_from_contracts.py`

Local workbook:

- `output/step_06_earthworks_waterproofing_review.xlsx`

Step 6 builds the local `.xlsx` review workbook from contracts. Publishing that workbook to a real Google Sheet is the next separate checkpoint, and downloading it back after Elena edits is the checkpoint after that. The downloaded workbook is the source of truth for normalized review JSON and calculator inputs. Hidden technical columns must survive, but the main check is that visible user corrections are read from the downloaded Google Sheet and used by calculators.

Do not merge these checks:

1. local workbook builder check;
2. Google publish check;
3. downloaded edited workbook -> normalized JSON -> calculator input check.

Step report:

- `reports/step_06_earthworks_waterproofing_review_workbook.md`

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

## Cross-Check Stage — Section Contract vs Real Extraction JSON (No Value Leakage)

Use this stage when the user says "проверяем контракт по [раздел] на реальных данных" or
"сверяем со сметой [проект]", or when resuming a chat that stopped mid cross-check.

### Why this stage exists

`sections/*/section_contract.yaml` files (through `foundation_slab`, `flat_roof`,
`load_bearing_walls_lintels`, `floor_slab_1`, `floor_slab_2`, `schiedel_vent_channels`,
`waterproofing`, `earthworks` — see `reports/step_05..step_12`) were drafted from calculator
source, calculator docs, `docs/elena_parameter_review_pack_audit.md`, and
`experiments/chat_extraction_poc/data/{calculator_targets_compact.json,target_aliases_ru.yaml}`.
They were never checked against a real per-project chat/parser extraction JSON. This stage closes
that gap, one finished real-project estimate at a time, without repeating the earthworks mistake
(project-specific numbers silently becoming pipeline expectations — see the Universal Production
Rule above and `reports/step_03b_production_contamination_audit.md`).

Scope: cost-basis ("себестоимость", the internal/grey estimate) only. The client-facing
white/markup part of the estimate is out of scope for this stage entirely.

### What the user provides

A finished, hand-built real-project estimate for one section (screenshot or pasted rows: label +
unit, sometimes a value) for a project this pipeline has real chat-extraction JSON for (currently
ЮСВ, `experiments/chat_extraction_poc/`). The estimate was built by hand by an estimator and is
**not** an automated pipeline output — it is only used here as a source of real row labels/units to
cross-check contract coverage, never as a target value.

### What the assistant does per row

1. Find the matching field in the section's calculator (`experiments/<section>_calculator/*.py`)
   and in `sections/<section>/section_contract.yaml`. If nothing matches, say so explicitly — that
   is a real finding, not a search failure.
2. Classify/confirm its `source_class` per the enum already used in section contracts:
   `AUTO_PROJECT`, `DEFAULT`, `AUTO_CALCULATED`, `PRICE`, `SUPPLIER_INPUT`, `MANUAL_REVIEW`.
   A repeated-row group (rebar by diameter, trench routes, pipe items, ...) is still
   `AUTO_PROJECT` — see the Sheet 01/02/03 Rule above, there is no separate detail-table class.
   Add a `ZERO_STRUCTURE_LINE` case for rows that exist only as an empty Excel-structure
   placeholder filled in by hand after export (confirmed pattern in
   `foundation_slab_calculator.py`, `floor_slab_2_calculator.py`, `flat_roof_calculator.py` for
   "Технический надзор" / "Заготовительно-складские расходы" / "Накладные и общехозяйственные
   расходы" / "Сметная прибыль" — earthworks has none of these four rows at all, not even as a
   placeholder).
3. If `source_class` is `AUTO_PROJECT` (scalar or repeated-row group), check whether a matching
   `target_code` / `group_code` actually exists in the real project's chat-extraction JSON
   (`experiments/chat_extraction_poc/outputs/*.json` when present). Report found / not found /
   found-but-wrong-shape. This is the check that matters: can the parser realistically supply this
   field on a real project, not just in the contract's own `parser_mapping.aliases_ru` guess.

### Hard rule: no project values in any written file

The output of this stage is **only**:

- confirmed/corrected `source_class`;
- confirmed/corrected `parser_mapping` (target codes, aliases, expected unit);
- found/not-found verdict against the real extraction JSON;
- missing calculator/contract coverage (row exists in the real estimate, nothing matches it in the
  contract or the calculator).

A literal number from the user's real project (81, 320, 18.29, etc.) may appear **only inside the
chat turn itself**, to let the assistant locate the right field. It must never be written into
`section_contract.yaml`, a `reports/*.md` file, or any other file in this repo — not even in a
scratch file "to delete later". If the assistant needs working notes across several rows in one
session, keep them in the chat, not in a file. Do not create a temporary/scratch file for this at
all; there is nothing in it that survives the session except the structural findings above, and
those go straight into the real report/contract.

### Naming Alignment Rule (fixed 2026-07-09 — read this before "fixing" any target_code mismatch)

When a cross-check finds that the contract's `parser_mapping.target_codes` (or a repeated-row group's
`columns` keys) don't match what the parser actually emits, **do not build a translation/bridge inside
the contract.** Rename the parser-side files instead
(`experiments/chat_extraction_poc/data/target_aliases_ru.yaml`,
`data/calculator_targets_compact.json`, `schemas/claude_extraction_output_schema.json`, and the prompt
if it names the field explicitly) so the parser's `target_code`/field names become **identical** to
the calculator's real dataclass field names for that section. After the fix, within one section:
`section_contract.yaml`'s `calculator_input_path` == its `parser_mapping.target_codes` == what the
parser actually outputs — no separate "bridge" name anywhere.

**Never rename a calculator's own field names to fix this.** Calculators are tested, working
financial-calculation code; renaming their fields is a real code change with real risk, not a
config/schema edit. If the calculator's name is awkward or inconsistent with another section, that's
a separate, deliberate future cleanup (see the naming-divergence note below), not something to fix as
a side effect of a cross-check.

This replaces the earlier, inconsistent approach (see `step_13`'s `membrane_area_m2` finding, fixed
by editing the contract, versus its `foundation_rebar_items` finding, fixed by editing the parser) —
going forward, always fix the parser side, for every section, no exceptions decided case by case.

**Fact, not a bug, to keep in mind while doing this**: different section calculators were built
independently and do **not** use one shared name for the same physical material/process across
sections — e.g. rebar's "length from spec" field is `source_length_m` in `foundation_slab_calculator.py`
but `spec_length_m` in `floor_slab_1_calculator.py`, `floor_slab_2_calculator.py`, and
`load_bearing_walls_lintels_calculator.py`. This means the parser's canonical field name for "rebar
length from spec" legitimately differs per section-specific extraction group
(`foundation_rebar_items` vs `floor_slab_1_rebar_items` etc.) — don't assume one group's fix applies to
another by analogy; verify each calculator's real field names independently. A shared naming
dictionary/catalog across all calculators (one name per physical concept, everywhere) would be a good
future cleanup, but is out of scope for now — it means touching tested calculator code across every
section, not a config-only change like the fixes in this stage.

### Where findings land

- Structural corrections to an existing section: edit `sections/<section>/section_contract.yaml`
  directly (only `source_class`, `parser_mapping`, `notes` fields — never add a `default_value` or
  `example` populated with a real project number). Per the Naming Alignment Rule above, most naming
  fixes actually land in the parser-side files, not the contract.
- A running log of the cross-check itself (what was checked, what didn't match, what's missing
  entirely from the contract or calculator): `reports/step_13_<section>_extraction_crosscheck.md`
  (bump the number per section if more than one cross-check report is open at once).

### Order

Start with `foundation_slab` (has a contract already — step 8 — but zero real-JSON cross-check).
Then repeat per section in the Step 10 order once foundation_slab is done. `earthworks` and
`waterproofing` are also in scope for this stage even though they aren't in the Step 10 list (they
were built earlier, in steps 1/5/6, before this stage existed) — see `reports/step_15_*` for
earthworks and `reports/step_16_waterproofing_extraction_crosscheck.md` for waterproofing. Do the
cross-check itself before the Step 11 migration below; the migration should build on a contract
that's already been checked against parser/calculator names, not the other way round.

## Step 11 — Earthworks Migration Off Its Own Hardcoded Pipeline

- [ ] Read `experiments/earthworks_review_to_calculator/*.py` and
      `experiments/earthworks_parser_google_stage1/google_sheets/review_workbook_builder.py` in full;
      confirm exactly which pieces are earthworks-hardcoded (`PARAM_META`, `SUMMARY_RULES`, and
      similar dicts) versus reusable logic.
- [ ] Finish Step 15's earthworks Cross-Check first (`reports/step_15_earthworks_extraction_crosscheck.md`)
      so the contract itself is correct before anything is built on top of it.
- [ ] Build (or extend `build_review_workbook_from_contracts.py` with) a real extraction-JSON ingestion
      path — this does not exist yet for any section (see the "no extraction-JSON input" gap noted for
      `build_review_workbook_from_contracts.py`'s `parse_args`/`build_project_sheet`), earthworks
      migration depends on it same as every other section eventually will.
- [ ] Replace `calculator_input_mapping.transform: earthworks_review_to_calculator_adapter` in
      `sections/earthworks/section_contract.yaml` with the same generic
      `review_parameters + defaults + price_keys -> calculator input` mapping style used by the other
      7 contracts, once the generic adapter can actually produce it correctly (regression check
      against the existing hardcoded flow's known-good output before retiring it).
- [ ] Only after the generic path is proven equivalent: retire/archive the earthworks-specific scripts,
      update `section.status` in the contract away from `reference_ready`, and update the "Reference
      Earthworks Flow" section above (it currently documents the old flow as canonical).
- [ ] Commit step 11 separately.

Not started. Recorded 2026-07-09 per explicit user decision to stop treating earthworks as a permanent
special case and bring it onto the same contract-driven path as the other 7 sections.

## Guardrails For Every Step

Before marking a step complete, run these checks mentally and, where possible, with scripts.

### 1. Workbook Role Check

Question: Am I building a review workbook or a final estimate workbook?

Fail if a review row is treated as a final estimate line without passing through calculator/formula-ready.

### 2. Source Class Check

For each leaf input and numeric coefficient, confirm its source class against the June Elena/manual
review materials before removing it from the contract.

Ask:

- Is this value extracted from the new project JSON?
- Is this value a price?
- Is this value a formula default/catalog package/business coefficient that formulas need?
- Is this value calculated downstream?
- Is this value a real manual/supplier decision?
- Is this value only an old project fixture or expected-total artifact?

Fail if a required formula coefficient is dropped just because it is numeric.

Every leaf input must be one of:

- `AUTO_PROJECT` (scalar or repeated-row group — see the Sheet 01/02/03 Rule; there is no
  separate `DETAIL_TABLE` class)
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

Completed (checklist above under-reports this — verified against files on disk):

- Steps 0–3b as listed in the checklist.
- Draft `section_contract.yaml` now exists for all 8 sections: `earthworks`, `waterproofing`,
  `schiedel_vent_channels`, `foundation_slab`, `load_bearing_walls_lintels`, `floor_slab_1`,
  `floor_slab_2`, `flat_roof` — see `reports/step_05..step_12`.
- Local review-workbook prototypes were built and re-built incrementally through step 12
  (`output/step_06_*.xlsx` .. `output/step_12_all_sections_review_template.xlsx`), each adding one
  more section's contract into the combined workbook.
- The formal Step Checklist above (steps 6–10 checkboxes) was not kept in sync with this work —
  treat the checkboxes as stale and the `reports/` + `sections/` file list as the source of truth
  for what's actually done.
- Cross-check reports now exist for `foundation_slab`, `earthworks`, and `waterproofing`
  (`reports/step_13_*`, `reports/step_15_*`, `reports/step_16_*`). Treat each report's scope
  carefully: some checks are against real extraction JSON, some are structural parser/contract/
  calculator-name checks. The remaining sections still need the same pass.

Next:

- Continue Cross-Check Stage for the remaining sections, per the no-value-leakage rule.
- Steps 7 and 9 (multi-section normalized review JSON; waterproofing review-to-calculator adapter)
  are still genuinely not started — do not assume the contract work above means the
  adapter/normalized-JSON layer exists too. It doesn't yet.

Do not start coding all 8 sections' adapters at once.
