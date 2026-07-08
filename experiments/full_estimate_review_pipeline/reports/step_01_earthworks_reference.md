# Step 1 — Earthworks Reference Contract

Status: completed draft

Goal: фиксируем раздел `earthworks` как эталонный путь от Google review workbook до calculator/formula-ready/export. Этот файл нужен как страховка от ошибки "сделали красивую таблицу, но она не собирается в калькулятор".

## 1. Source Files

Reference job artifacts:

- review workbook from an old project-specific run;
- normalized review JSON from that run;
- calculator input from that run;
- calculator result from that run;
- formula-ready result from that run;
- exported estimate workbook from that run.

The exact old job path is deliberately not used as a production instruction. It can be recovered from git history or local job folders only when auditing the reference behavior. It must not become a path convention, data source, or filter in new pipeline code.

Code path:

- Google/review builder: `experiments/earthworks_parser_google_stage1/google_sheets/review_workbook_builder.py`
- review reader: `experiments/earthworks_review_to_calculator/review_workbook_reader.py`
- calculator input adapter: `experiments/earthworks_review_to_calculator/calculator_input_builder.py`
- calculator: `experiments/earthworks_calculator/earthworks_calculator.py`
- formula-ready builder: `experiments/earthworks_review_to_calculator/build_formula_ready_result.py`
- Excel export: `experiments/earthworks_review_to_calculator/export_formula_ready_to_excel.py`

## 2. Observed Counts

These are measured from the reference job and are the current baseline.
They are artifact counts, not reusable project quantities.

| Artifact | Count |
|---|---:|
| `01_Проверка проекта` max rows | 14 |
| `01_Проверка проекта` non-empty rows | 13 |
| normalized scalar parameters | 7 |
| `02_Цены себестоимости` non-empty rows | 13 |
| price rows read by normalized JSON | 12 |
| `03_Детали объемов` non-empty rows | 11 |
| detail groups | 2 + summary |
| raw parser rows sheet non-empty rows | 80 |
| calculator estimate lines | 11 |
| formula-ready rows | 11 |
| formula-ready helper cells | 27 |
| rows with formula model | 11 |
| rows with control fields | 8 |

## 3. Earthworks Review Contract

The review workbook is not the final estimate. It is the human-checkable source of inputs.

Required scalar parameters:

- `pit_area_m2`
- `pit_excavation_depth_m`
- `sand_base_volume_m3`
- `trench_volume_m3`
- `geotextile_area_m2`
- `geotextile_laying_area_m2`
- `communications_length_m`

Detail tables:

- `trench_routes`
- `communications_pipe_items`

Price rows:

- `axis_marking_work_unit_price`
- `excavator_material_unit_price`
- `excavator_work_unit_price`
- `manual_excavation_work_unit_price`
- `geotextile_laying_work_unit_price`
- `geotextile_material_unit_price`
- `sand_filling_work_unit_price`
- `sand_material_unit_price`
- `sand_manual_moving_work_unit_price`
- `communications_work_unit_price`
- `communications_material_unit_price`
- `consumables_amount`

Defaults are not asked from the project unless explicitly overridden:

- `excavator_productivity_m3_per_shift`
- `manual_refinement_depth_m`
- `trench_width_m`
- `sand_compaction_coeff`
- `sand_truck_step_m3`
- `geotextile_overlap_coeff`
- `geotextile_roll_area_m2`
- `axis_marking_shifts`
- calculation modes and assumptions from `GENERIC_CALCULATOR_DEFAULTS`

## 4. Estimate Lines Produced

The calculator expands the small review contract into 11 estimate lines:

- `axis_marking`
- `excavator_jcb`
- `manual_excavation`
- `geotextile_laying`
- `geotextile_material`
- `sand_filling`
- `sand_material`
- `sand_manual_moving`
- `communications_work`
- `communications_material`
- `consumables`

This is the central lesson: estimate rows are produced by calculator/formula-ready logic, not by copying all `AUTO_PROJECT` parameters into the review workbook.

## 5. Guardrails For All Next Sections

Every new section must pass these checks before we call it production-like.

### 0. Universal Production Check

The next section must work from a fresh chat/parser JSON for a different project.

Fail condition: contract, adapter, workbook builder, or formula-ready code copies a project-specific quantity, price, total, display quantity, old filename, old page/table evidence, or old expected Excel total from a reference run.

Allowed: use the reference run to understand shape, line counts, formulas, and code paths.

### A. Contract Shape Check

For the section, we must have an explicit list of:

- review parameters;
- detail tables;
- price keys;
- defaults;
- auto-calculated fields;
- supplier inputs, if any;
- final estimate lines.

Fail condition: a row appears in the workbook and we cannot say whether it is a project parameter, price, detail row, default, auto-calculated value, supplier input, or estimate line.

### B. End-To-Start Trace Check

For every final estimate line:

```text
estimate line -> quantity formula -> leaf inputs -> source class
```

Source class must be one of:

- `AUTO_PROJECT`
- `DETAIL_TABLE`
- `DEFAULT`
- `AUTO_CALCULATED`
- `PRICE`
- `SUPPLIER_INPUT`
- `MANUAL_REVIEW`

Fail condition: an estimate line has no declared quantity formula or has leaf inputs with unknown source.

### C. Review-To-Calculator Check

The section must have an adapter path:

```text
review workbook rows -> normalized review JSON -> calculator input JSON
```

Fail condition: the review workbook looks right but no deterministic adapter can build calculator input.

### D. Calculator Result Check

The existing section calculator must run from the generated calculator input.

Fail condition: calculator input is assembled manually, hardcoded from a fixture, or bypasses the reviewed values.

### E. Formula-Ready Check

For every calculator estimate line, formula-ready must define:

- row id;
- visible line name;
- unit;
- quantity value;
- formula model or explicit reason why not formula-exportable;
- material/work price linkage;
- helper cells when the quantity formula has intermediate values.

Fail condition: a line exists in calculator result but is missing from formula-ready output.

### F. Workbook Separation Check

We keep two different workbook concepts separate:

- review workbook: inputs, prices, details, parser evidence;
- final estimate workbook: estimate rows, formulas, totals.

Fail condition: we treat 87 `AUTO_PROJECT` rows as if they were final estimate rows.

### G. Count Sanity Check

Counts do not have to match earthworks, but each section must report:

- review parameter count;
- detail row count;
- price row count;
- calculator estimate line count;
- formula-ready row count.

Fail condition: formula-ready row count differs from calculator estimate line count without an explicit explanation.

## 6. Step 1 Acceptance Criteria

- [x] Earthworks reference source files identified.
- [x] Earthworks baseline counts measured.
- [x] Review contract listed.
- [x] Estimate lines listed.
- [x] Guardrails for next sections defined.
- [x] Reference run marked as non-production data.
- [ ] Next section contract created.

## 7. Next Step

Step 2 should create the common section contract format, then Step 3 should apply it first to `waterproofing`.
