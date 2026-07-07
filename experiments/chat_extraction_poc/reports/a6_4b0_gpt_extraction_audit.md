# A6.4b-0. Audit GPT extraction_output.json against calculators and Google Sheet flow

Date: 2026-07-07

## Scope

Input files reviewed:

- `/Users/tatanamedzidova/Downloads/extraction_output (2).json`
- `/Users/tatanamedzidova/Downloads/service_memo.txt`
- `experiments/chat_extraction_poc/data/calculator_targets_compact.json`
- `experiments/pdf_parser_pipeline/section_schema.py`
- existing earthworks Google Sheet flow in:
  - `experiments/earthworks_parser_google_stage1/google_sheets/review_workbook_builder.py`
  - `experiments/earthworks_review_to_calculator/review_workbook_reader.py`
  - `experiments/earthworks_review_to_calculator/calculator_input_builder.py`

This is an architecture/audit pass, not an implementation pass.

## Short conclusion

The GPT extraction JSON is usable as a new upstream source, but it should not be sent directly into calculators.

The correct pattern is the same as the current earthworks path:

1. import extraction JSON;
2. build a human review workbook;
3. let Elena confirm or correct values;
4. read the reviewed workbook using stable technical keys;
5. convert reviewed data into calculator input with section-specific adapters.

The key insight from earthworks is that the Google Sheet is not only a display table. It is a controlled interface with hidden technical columns, validation, detail rows, and deterministic post-review calculation.

## Existing earthworks logic worth reusing

The earthworks flow already has the right product shape:

- `01_Проверка проекта` contains human-readable rows plus hidden technical columns:
  - `technical_key`
  - `extraction_status`
  - `confidence`
- `03_Детали объемов` contains repeated/table data:
  - trench routes
  - communications pipe items
- `02_Цены себестоимости` contains estimate price rows plus hidden calculator price keys.
- `review_workbook_reader.py` ignores unknown visual rows and reads only known technical keys.
- `calculator_input_builder.py` makes deterministic transformations after review, for example communications length is calculated from included pipe rows.

This should become the general rule for all sections:

- scalar targets go to review rows;
- object/list/group targets go to detail sheets;
- calculated values are produced by code after review, not by GPT;
- unknown or helper rows can be shown to Elena but must not silently enter calculator input.

## GPT JSON structure check

The JSON is valid and contains all 8 target sections:

- `earthworks`
- `foundation_slab`
- `waterproofing`
- `load_bearing_walls_lintels`
- `floor_slab_1`
- `floor_slab_2`
- `flat_roof`
- `schiedel_vent_channels`

Each section has the expected high-level buckets: `raw_table_rows`, `found`, `missing`, and review notes.

Important value shapes found:

- scalar numbers: concrete, EPS, areas, counts;
- strings: some ambiguous units/source fields;
- objects: rebar items, trench routes, EPS split objects;
- repeated rows with same `target_code` or `group_code`: rebar, beams, communications, masonry reinforcement.

Therefore a flat "one JSON item = one calculator parameter" adapter is not enough.

## Target-code compatibility

The extraction uses many canonical target codes from `calculator_targets_compact.json`, but group rows are not represented in the compact file as ordinary target codes. They need to be handled as detail groups.

Rows outside direct compact targets:

- group/detail rows that should be accepted as detail data:
  - `trench_routes`
  - `communications_pipe_items`
  - `foundation_rebar_items`
  - `lintel_items`
  - `lintel_rebar_items`
  - `floor_slab_1_rebar_items`
  - `beam_items`
  - `floor_slab_2_rebar_items`
- helper/outside rows that can be shown but should not feed calculators without a mapping decision:
  - `waterproofing_cutoff_material_area`
  - `floor_slab_1_beam_concrete_volume`
  - `floor_slab_2_edge_formwork_area_outside_targets`
  - `roof_parapet_abutment_total_length`
  - `roof_wall_abutment_total_length`
  - `vent_chimney_cladding_length_total`

Recommendation: introduce two categories in the review adapter:

- `calculator_target`: known direct target from compact/schema;
- `review_helper`: useful source/control row, visible in Google Sheet but blocked from calculator input unless a section adapter explicitly consumes it.

## Proposed review workbook for all sections

Use the requested columns as the visible interface:

1. `Что проверяем`
2. `Найдено в проекте`
3. `Ед.`
4. `Статус`
5. `Что нужно сделать`
6. `Источник`
7. `Фрагмент проекта`
8. `Исправить / ввести значение`
9. `Комментарий Елены`

Add hidden technical columns, following earthworks:

- `section_code`
- `target_code`
- `group_code`
- `row_kind`
- `value_kind`
- `calculator_input_key`
- `extraction_status`
- `confidence`
- `source_json_path`
- `adapter_status`

Suggested sheets:

- `00_Конструктор сметы`
- `01_Проверка проекта`
- `02_Цены себестоимости`
- `03_Детали объемов`
- `04_Арматура`
- `05_Кандидаты / helper rows`
- `06_raw_table_rows`
- `07_raw_json`
- `08_Инструкция`

For MVP this can be simplified to:

- `01_Проверка проекта`
- `03_Детали объемов`
- `04_Арматура`
- `06_raw_table_rows`

## Flattening rules

### Scalar values

Numbers and strings become one review row:

- display value in `Найдено в проекте`;
- unit in `Ед.`;
- hidden `target_code`;
- hidden `calculator_input_key` from `section_schema.py` when available.

### Object values

Objects should not be dumped as JSON into a calculator row.

Rules:

- if the object is a known group item, put it on a detail sheet;
- if the object splits one target into child values, show child rows plus a calculated/review row;
- keep source JSON path for traceability.

### Lists or repeated target codes

Repeated rows become detail tables.

Examples:

- `trench_routes` -> route detail table;
- `communications_pipe_items` -> communications detail table;
- `foundation_rebar_items`, `floor_slab_1_rebar_items`, `floor_slab_2_rebar_items`, `lintel_rebar_items` -> rebar detail table;
- `beam_items` -> beam detail table.

## Special cases

### Earthworks

The GPT data fits the existing earthworks logic, but field names differ:

- GPT uses `route_name`; current detail reader expects `name`.
- GPT uses `piece_length_m`, `quantity_pcs`, `linear_length_m`; current reader expects `pipe_length_m`, `quantity`, `total_length_m`.

Adapter rule:

- for pipe pieces: `total_length_m = piece_length_m * quantity_pcs`;
- for linear rows: `total_length_m = linear_length_m`;
- fittings without length can be visible helper rows but should not contribute to `communications_length_m`.

The trench route mismatch from service memo should become a warning, not an auto-correction. Keep PDF volume and dimensions visible.

### Rebar

The GPT output now follows the intended rule:

- primary PDF unit is `м/п`;
- values contain `length_m`;
- some rows contain `mass_per_m_kg`;
- `weight_kg` is usually `null`.

Do not force GPT to calculate weight. The post-review adapter should calculate weight only after Elena confirms the row:

`calculated_weight_kg = length_m * mass_per_m_kg`

Then map to calculator format:

- foundation slab can use `rebar_calc_method = spec_length_m`;
- floor slab 1 and floor slab 2 can use `rebar_calc_method = spec_length_items`;
- load-bearing walls/lintels can use `main_wall_rebar_calc_method = spec_length_items` and `lintel_rebar_calc_method = spec_length_items` where supported.

Rows without `mass_per_m_kg` need either catalog lookup by diameter/class or manual review.

### Floor slab 1 EPS

GPT returns:

- `bottom_volume_m3`
- `edge_volume_m3`

The calculator target is currently one field:

- `total_eps_volume_from_spec_m3`

Do not lose the split. Show two child rows in review and one calculated total row. Feed the calculator only after review:

`total_eps_volume_from_spec_m3 = bottom_volume_m3 + edge_volume_m3`

This prevents mixing EPS volume with formwork area.

### Floor slab 2 EPS and formwork

GPT correctly keeps:

- `floor_slab_2_eps100_edge_volume` = EPS volume, m3;
- `floor_slab_2_main_formwork_area` = main formwork, m2;
- `floor_slab_2_edge_formwork_area_outside_targets` = edge formwork helper, m2.

The helper edge formwork row should be visible but blocked from calculators until the target is added to compact/schema or explicitly mapped.

This is the case that prevents confusing `0.74 м3` EPS with `7.4 м2` formwork.

### Thermal inserts

GPT found one length and duplicated it into both:

- `thermal_insert_50_length`
- `thermal_insert_100_length`

Service memo correctly flags this as uncertain. In review, these should be marked `Проверьте`, with the same source fragment, and not treated as independent high-confidence findings.

### Flat roof

GPT found:

- `project_spec_roof_area` = 294 m2, needs review;
- `roof_area_level_1` = 212.35 m2;
- `roof_area_level_2` = 82 m2;
- `roof_pvc_membrane_area` = 398.4, unit missing/ambiguous;
- total parapet/wall abutments outside target structure.

Calculator wants level-specific geometry, including level-specific parapet/abutment values. Total abutment rows must be helper rows until Elena splits them by level.

`project_spec_roof_area` from vapor barrier/spec material should remain a control/review row, not automatically override level areas.

### Schiedel vent channels

GPT found product counts:

- `schiedel_vent_channel_2x_count`
- `schiedel_vent_channel_3x_count`

It also found:

- `vent_channel_2_count`, apparently duplicate/control;
- `vent_chimney_cladding_length_total`, helper for cladding/masonry;
- missing heights.

Schiedel calculator currently needs count and masonry total length. If heights are missing, the adapter should either block with "manual value required" or use an explicitly reviewed cladding/masonry helper value. It should not infer heights from product counts.

## Telegram flow implication

Current Telegram bot accepts only PDFs. New flow should add a separate JSON branch:

- PDF upload keeps existing earthworks parser path;
- `.json` upload creates a chat-extraction review job;
- validate JSON structure;
- build Google Sheet review workbook;
- return the Google Sheet link.

The service memo should not be required for MVP, because Elena wants to upload only `extraction_output.json`. If uploaded later, it can become an optional notes sheet.

## Recommended implementation order

1. Add a `chat_extraction_review_to_calculator` experiment or module.
2. Implement a read-only JSON importer and validator.
3. Build a review workbook using the earthworks visible columns plus hidden technical columns.
4. Implement detail sheets for:
   - earthworks routes/communications;
   - rebar;
   - floor slab beams;
   - roof level geometry/helper rows.
5. Implement a reviewed-workbook reader that outputs normalized reviewed JSON.
6. Implement section adapters one by one, starting with earthworks and foundation/floor slab rebar because their calculator inputs already support length-based rebar.
7. Add Telegram `.json` upload branch without changing the existing PDF flow.

## Main risks

- Treating helper rows as calculator inputs will create silent wrong estimates.
- Flattening object/list values into strings will make later calculator adapters brittle.
- Rebar should remain length-based until post-review code calculates or maps it.
- Flat roof and Schiedel need blocking/manual states for missing level splits and missing heights.
- `calculator_targets_compact.json` should be extended to describe group codes, not only scalar targets.

