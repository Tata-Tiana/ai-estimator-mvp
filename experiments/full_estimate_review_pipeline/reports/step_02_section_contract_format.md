# Step 2 — Common Section Contract Format

Status: completed draft

Goal: define a shared `section_contract.yaml` shape that can describe each estimate section from review workbook inputs to calculator/formula-ready/final estimate rows.

Template:

- `experiments/full_estimate_review_pipeline/templates/section_contract.template.yaml`

This step does not implement any new section. It defines the format we will use in Step 3 for `waterproofing`.

## 1. Why This Contract Exists

The earthworks reference showed the key pattern:

```text
small review contract
-> deterministic calculator input
-> calculator estimate lines
-> formula-ready rows
-> final estimate workbook
```

The new multi-section work must not treat all `AUTO_PROJECT` rows as estimate rows. A contract makes every row explain itself:

- project value to review;
- repeating detail table;
- price row;
- default;
- auto-calculated value;
- supplier input;
- final estimate line.

If a row cannot be classified, it should not be added to the production-like workbook yet.

## 2. Contract File Location

Each section will eventually have:

```text
experiments/full_estimate_review_pipeline/sections/<section_code>/section_contract.yaml
```

Example future paths:

- `sections/waterproofing/section_contract.yaml`
- `sections/schiedel_vent_channels/section_contract.yaml`
- `sections/foundation_slab/section_contract.yaml`

The template lives at:

```text
experiments/full_estimate_review_pipeline/templates/section_contract.template.yaml
```

## 3. Required Top-Level Blocks

### `contract_version`

Schema version for this contract format. Current draft:

```yaml
contract_version: 0.1
```

### `section`

Section metadata.

Required fields:

- `code`
- `name_ru`
- `calculator_module`
- `status`

Purpose: identify the section and the calculator that will eventually consume the generated input.

### `source_files`

Human-readable provenance for contract creation.

Typical fields:

- calculator source;
- calculator README;
- existing test cases;
- related reports/docs;
- extraction target dictionaries.

Purpose: make the contract auditable by a future chat or developer.

### `review_parameters`

Rows intended for `01_Проверка проекта`.

These are not final estimate rows. They are scalar or object-like values that a human can check, override, or mark as missing.

Required fields per parameter:

- `key`
- `label_ru`
- `unit`
- `source_class`
- `required`
- `review_sheet`
- `calculator_input_path`
- `normalized_json_path`
- `value_kind`
- `review_behavior`
- `validation`

Allowed `source_class` values:

- `AUTO_PROJECT`
- `MANUAL_REVIEW`
- `SUPPLIER_INPUT`

`AUTO_CALCULATED` values should usually not be shown as primary review parameters unless they are shown for audit/control only.

### `detail_tables`

Repeating rows intended for `03_Детали объемов`.

Examples from earthworks:

- `trench_routes`
- `communications_pipe_items`

Required fields per table:

- `key`
- `label_ru`
- `source_class: DETAIL_TABLE`
- `required`
- `review_sheet`
- `normalized_json_path`
- `calculator_input_path`
- `columns`
- `validation`

Each column must have:

- `key`
- `label_ru`
- `unit`
- `value_kind`
- `required`

### `price_keys`

Rows intended for `02_Цены себестоимости`.

Required fields per price:

- `key`
- `estimate_line_code`
- `label_ru`
- `price_kind`
- `unit`
- `required`
- `default_source`
- `fallback_key`
- `allow_manual_override`

If a calculator estimate line uses a price, it must reference a `price_key`, unless the price is explicitly zero/fixed and documented.

### `defaults`

Values not asked from the project because they are generic assumptions, modes, coefficients, catalog constants, or local defaults.

Examples from earthworks:

- `manual_refinement_depth_m`
- `sand_compaction_coeff`
- `geotextile_overlap_coeff`
- `axis_marking_shifts`

Required fields per default:

- `key`
- `label_ru`
- `source_class: DEFAULT`
- `value`
- `calculator_input_path`
- `source_note`
- `allow_override_later`

### `auto_calculated`

Derived values that are not copied directly from the project.

Examples from earthworks:

- `manual_pit_volume_m3 = pit_area_m2 * manual_refinement_depth_m`
- `sand_order_volume_m3 = roundup_to_step(sand_total_m3, sand_truck_step_m3)`
- `communications_length_m_effective = sum(included pipe item lengths)`

Required fields:

- `key`
- `label_ru`
- `source_class: AUTO_CALCULATED`
- `formula`
- `leaf_inputs`

Every leaf input must reference a known review parameter, detail table, default, supplier input, or another auto-calculated field.

### `supplier_inputs`

External values from supplier/layout work that cannot be derived from project PDF or local defaults.

Examples likely later:

- roof insulation supplier layout quantities;
- supplier-only slopes or custom materials.

Required fields:

- `key`
- `label_ru`
- `source_class: SUPPLIER_INPUT`
- `unit`
- `required`
- `review_sheet`
- `calculator_input_path`

### `calculator_input_mapping`

Deterministic adapter map from normalized review JSON to calculator input.

Required fields per mapping:

- `input_path`
- `from.ref`
- `from.source_class`
- `required`
- `transform`
- `fallback`

Purpose: prevent hand-copying values from old fixtures into calculator input.

### `estimate_lines`

Final estimate rows produced by calculator/formula-ready. These are not rows of `01_Проверка проекта`.

Required fields per line:

- `code`
- `name_ru`
- `unit`
- `enabled_by_default`
- `calculator_result_path`
- `quantity`
- `prices`
- `helper_cells`
- `validation`

Quantity block must have either:

- `formula` and `leaf_inputs`; or
- an explicit non-formula reason.

Price block must have:

- `material_unit_price_key`, or `null`;
- `work_unit_price_key`, or `null`;
- `fixed_amount_key`, or `null`.

If all price keys are null, the line must explain why.

### `workbook_layout`

Describes where the section appears in review/final workbooks.

Required concepts:

- review workbook sheets;
- final estimate workbook zones;
- section order/section row rules.

This keeps the two workbooks separate:

- review workbook: `00` to `06` style sheets;
- final estimate workbook: smeta rows with white/calc/helper zones.

### `checks`

Machine-readable or human-readable fail conditions.

At minimum:

- allowed source classes;
- fail conditions copied from Step 1 guardrails;
- section-specific checks later.

## 4. Source Classes

Allowed values:

| Source class | Meaning | Typical destination |
|---|---|---|
| `AUTO_PROJECT` | Value should be extracted from project/PDF and reviewed by human | `01_Проверка проекта` |
| `DETAIL_TABLE` | Repeating project rows, often used by calculator as list input | `03_Детали объемов` |
| `DEFAULT` | Local assumption/mode/coefficient/catalog value | calculator input / helper cells |
| `AUTO_CALCULATED` | Derived from other inputs by adapter/calculator/formula-ready | formula-ready/helper cells |
| `PRICE` | Price row keyed by `calc_price_key` | `02_Цены себестоимости` |
| `SUPPLIER_INPUT` | External supplier/layout quantity | `01_Проверка проекта` or supplier sheet later |
| `MANUAL_REVIEW` | Human-only decision not reliably extractable from parser | `01_Проверка проекта` |

## 5. Workbook Construction Semantics

### Universal Production Semantics

Every `section_contract.yaml` must be reusable with a fresh chat/parser JSON for a different project.

The contract may contain:

- field names;
- aliases;
- expected units;
- formula dependencies;
- source classes;
- default/catalog references;
- validation rules.

The contract must not contain:

- old project quantities, prices, totals, display quantities, page numbers, filenames, or expected Excel totals;
- fixture values copied from calculator cases;
- hardcoded old workbook values used to force equality with a previous estimate;
- old project names used as logic or path filters.

### Review Workbook

The review workbook is built from:

- `review_parameters` -> `01_Проверка проекта`;
- `price_keys` -> `02_Цены себестоимости`;
- `detail_tables` -> `03_Детали объемов`;
- parser candidates/raw rows -> technical sheets;
- `section` metadata -> `00_Конструктор сметы`.

Review workbook rows must never be assumed to be final estimate lines.

### Normalized Review JSON

Expected future shape:

```json
{
  "sections": {
    "waterproofing": {
      "parameters": {},
      "details": {},
      "prices": [],
      "validation": {}
    }
  }
}
```

### Calculator Input

`calculator_input_mapping` defines deterministic conversion:

```text
normalized review JSON + defaults + detail tables + price rows
-> calculator input JSON
```

### Formula-Ready

`estimate_lines` defines expected rows and helper cells. The calculator result must be the source of final quantities/totals, while formula-ready explains how those values should become Excel formulas.

## 6. Earthworks Fit Check

The template can express the earthworks reference:

- review parameters: 7 scalar parameters;
- detail tables: `trench_routes`, `communications_pipe_items`;
- price keys: 12 `REQUIRED_CALC_PRICE_KEYS`;
- defaults: `GENERIC_CALCULATOR_DEFAULTS`;
- auto-calculated: manual excavation volume, sand order volume, geotextile rolls, communications effective length;
- estimate lines: 11 calculator lines;
- helper cells: 27 formula-ready helper cells.

This satisfies the Step 1 lesson: small review contract, richer calculator/formula-ready output.

## 7. Acceptance Checks For Step 2

- [x] Contract distinguishes review parameters, detail tables, prices, defaults, auto-calculated values, supplier inputs, and estimate lines.
- [x] Each future review row can be classified by contract block.
- [x] Each future estimate line must expose `estimate_line -> quantity_formula -> leaf_inputs -> source_class`.
- [x] Each leaf input has a constrained source class.
- [x] Price mapping uses explicit `price_key` fields, not Russian labels alone.
- [x] Detail tables declare columns and calculator input path.
- [x] Contract keeps review workbook and final estimate workbook separate.
- [x] Contract forbids project-specific values from old fixtures/runs.
- [x] Earthworks can be represented by this format.
- [x] Fail conditions are present in the template.

## 8. Fail Conditions

Do not proceed to Step 3 for a section if:

- an estimate line has no quantity formula and no explicit non-formula reason;
- a quantity formula references a leaf input with unknown source class;
- a price-bearing line has no price key and no explicit zero/fixed reason;
- a review row cannot be classified as parameter/detail/price/default/auto/supplier/manual;
- there is no deterministic path from review JSON to calculator input;
- formula-ready row count differs from calculator result estimate-line count without explanation;
- a section contract uses old fixture values instead of reviewed/derived values;
- the contract contains project-specific quantities, prices, totals, display quantities, page numbers, filenames, or expected Excel totals from old runs.

## 9. Next Step

Step 3: build the all-sections quantity matrix.

Step 4: apply this format to `waterproofing`.

Required work before the waterproofing contract:

1. Read `experiments/waterproofing_calculator/`.
2. Read waterproofing docs/reports.
3. Build the matrix:

```text
estimate line -> quantity formula -> leaf inputs -> source class
```

4. Create `sections/waterproofing/section_contract.yaml`.
5. Write `reports/step_04_waterproofing_contract.md`.
6. Run the Step 2 checks manually against the waterproofing contract.
