# Parser/schema alignment instructions — earthworks

Purpose: keep the chat extraction files, review workbook contract, and calculator input shape aligned. The calculator field names are the ground truth; do not rename calculator fields to match an older parser output.

## Ground truth

- Section: `earthworks`
- Contract: `sections/earthworks/section_contract.yaml`
- Calculator: `experiments/earthworks_calculator/earthworks_calculator.py`
- Extraction files to keep aligned:
  - `experiments/chat_extraction_poc/data/calculator_targets_compact.json`
  - `experiments/chat_extraction_poc/data/target_aliases_ru.yaml`
  - `experiments/chat_extraction_poc/schemas/claude_extraction_output_schema.json`
  - `experiments/chat_extraction_poc/prompts/claude_estimate_extraction_prompt.md`

## Current status

Earthworks has been realigned from the old earthworks-only parser names to calculator/contract names.

Use the scalar values on sheet `01_Проверка проекта` as calculator sources. Detail rows can be mirrored for Elena's review, but they must not become the hidden calculation source unless a specific adapter mode is deliberately implemented.

Important calculator-mode note: for communications, production review currently uses the calculator's `legacy_direct_length` mode because that is the mode that reads the reviewed scalar `communications_length_m`. The name is legacy inside the calculator, but the data flow is the new production review flow.

## AUTO_PROJECT values expected from PDF/chat JSON

- `pit_area_m2`
- `pit_excavation_depth_m`
- `sand_base_volume_m3`
- `trench_volume_m3`
- `geotextile_area_m2`
- `geotextile_laying_area_m2`
- `communications_length_m`
- `trench_routes`
- `communications_pipe_items`

## Repeated-row shapes

`trench_routes`:

- `route_code`
- `name`
- `length_m`
- `depth_m`
- `width_m`
- `volume_m3`

`communications_pipe_items`:

- `code`
- `name`
- `diameter_mm`
- `pipe_length_m`
- `quantity`
- `total_length_m`
- `include_in_communications`

## Critical extraction rules

- `trench_volume_m3` is a scalar only when the PDF has an explicit ready total. Do not sum routes in chat.
- `communications_length_m` is a scalar only when the PDF has an explicit ready total. Do not sum pipe rows in chat.
- `geotextile_area_m2` and `geotextile_laying_area_m2` may come from the same PDF row, but keep the same raw source and mark/review the reuse.
- Manual excavation is calculated by the calculator from pit/trench values; do not ask GPT for a fake project row.

## Check before marking section ready

1. Confirm old parser names are not used as active targets: `sand_volume`, `geotextile_area`, `geotextile_laying_area`, `pit_area`, `pit_excavation_depth`, `trench_volume_total`, `manual_excavation_quantity_for_estimate`.
2. Compare scalar target codes with `section_contract.yaml`.
3. Compare repeated-row shapes with schema and prompt.
4. Confirm detail rows are display/review support, not the primary calculator source.
5. Confirm earthworks active parser targets do not include `membrane_area_m2`; this belongs to `foundation_slab` even if the PDF row is visible on an earthworks/foundation drawing.
6. Confirm `communications_pipe_items.row_key_field` is `code`, because the calculator requires `code`.
7. Confirm `communications_length_calc_method` is `legacy_direct_length` unless a deliberate adapter mode uses pipe rows as the reviewed source.
8. Run JSON/YAML validation after edits.
9. Confirm no project-specific values, page numbers, or USV-only facts were added to production config.
