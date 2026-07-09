# Parser/schema alignment instructions — flat_roof

Purpose: keep the chat extraction files, review workbook contract, and calculator input shape aligned. The calculator field names are the ground truth; do not rename calculator fields to match an older parser output.

## Ground truth

- Section: `flat_roof`
- Contract: `sections/flat_roof/section_contract.yaml`
- Calculator: `experiments/flat_roof_calculator/calculator.py`
- Extraction files to keep aligned:
  - `experiments/chat_extraction_poc/data/calculator_targets_compact.json`
  - `experiments/chat_extraction_poc/data/target_aliases_ru.yaml`
  - `experiments/chat_extraction_poc/schemas/claude_extraction_output_schema.json`
  - `experiments/chat_extraction_poc/prompts/claude_estimate_extraction_prompt.md`

## Current status

Contract exists, but this section still needs the same parser/schema cross-check pass that foundation slab already received.

## AUTO_PROJECT values expected from PDF/chat JSON

- `roof_area_level_1_m2`
- `roof_area_level_2_m2`
- `project_spec_roof_area_m2`
- `parapet_length_level_1_m`
- `parapet_length_level_2_m`
- `vent_wall_abutment_level_1_m`
- `vent_wall_abutment_level_2_m`
- `roof_aerators_count`
- `parapet_roof_drains_count`
- `internal_roof_drains_count`
- `internal_drain_height_per_drain_m`
- `roof_raw_material_spec_rows`

## Repeated-row shape

`roof_raw_material_spec_rows`:

- `name`
- `quantity`
- `unit`

## Critical extraction rules

- Roof PVC membrane/waterproofing must not be mixed with foundation waterproofing or PLANTER membrane.
- Level 1 and level 2 roof areas must stay separate if the PDF separates them.
- Parapet lengths, vent-wall abutments, aerators, and drains are separate calculator inputs.
- Supplier-required material volumes remain manual/supplier inputs unless the calculator contract explicitly marks them as AUTO_PROJECT.

## Check before marking section ready

1. Read the calculator input shape directly.
2. Compare scalar target codes with contract and calculator.
3. Compare `roof_raw_material_spec_rows` shape with parser/schema.
4. Confirm prompt/aliases distinguish roof materials from foundation membrane and waterproofing.
5. Run JSON/YAML validation after edits.
6. Confirm no project-specific values, page numbers, or USV-only facts were added to production config.

