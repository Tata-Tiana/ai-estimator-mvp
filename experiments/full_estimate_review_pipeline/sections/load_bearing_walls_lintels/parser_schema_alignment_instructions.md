# Parser/schema alignment instructions — load_bearing_walls_lintels

Purpose: keep the chat extraction files, review workbook contract, and calculator input shape aligned. The calculator field names are the ground truth; do not rename calculator fields to match an older parser output.

## Ground truth

- Section: `load_bearing_walls_lintels`
- Contract: `sections/load_bearing_walls_lintels/section_contract.yaml`
- Calculator: `experiments/load_bearing_walls_lintels_calculator/load_bearing_walls_lintels_calculator.py`
- Extraction files to keep aligned:
  - `experiments/chat_extraction_poc/data/calculator_targets_compact.json`
  - `experiments/chat_extraction_poc/data/target_aliases_ru.yaml`
  - `experiments/chat_extraction_poc/schemas/claude_extraction_output_schema.json`
  - `experiments/chat_extraction_poc/prompts/claude_estimate_extraction_prompt.md`

## Current status

Contract exists, but this section still needs the same parser/schema cross-check pass that foundation slab already received.

Known risk: this section has multiple rebar-like repeated groups. Do not reuse foundation slab field names by analogy. Check each calculator item shape directly.

## AUTO_PROJECT values expected from PDF/chat JSON

- `floors_count`
- `cutoff_waterproofing_load_bearing_walls_area_m2`
- `main_wall_gas_block_400_spec_volume_m3`
- `main_wall_gas_block_250_spec_volume_m3`
- `lintel_total_length_m`
- `lintel_concrete_spec_volume_m3`
- `floor_2_masonry_volume_m3`
- `parapet_masonry_volume_m3`
- `vent_chimney_gas_block_spec_volume_m3`
- `main_wall_rebar_items`
- `lintel_rebar_items`
- `lintel_items`

## Repeated-row shapes

`main_wall_rebar_items`:

- `floor`
- `component`
- `steel_class`
- `diameter_mm`
- `spec_length_m`
- `kg_per_meter`

`lintel_rebar_items`:

- `floor`
- `component`
- `steel_class`
- `diameter_mm`
- `spec_length_m`
- `kg_per_meter`

`lintel_items`:

- `mark`
- `length_m`
- `count`
- `total_length_m`

## Critical extraction rules

- Keep wall gas block 400 mm and 250 mm volumes separate.
- Keep lintel total length separate from lintel concrete volume.
- Keep lintel concrete separate from slab, beam, foundation, and wall concrete.
- Keep vent chimney gas block volume separate from Schiedel vent channel kit quantities.
- Rebar rows must stay row-by-row; do not calculate total weight in GPT/Claude unless PDF explicitly gives it and the calculator expects it.

## Check before marking section ready

1. Read the calculator input shape directly, especially `main_wall_rebar_items` and `lintel_rebar_items`.
2. Confirm parser/schema field names match the calculator, not older generic `length_m/mass_per_m_kg` names.
3. Compare all scalar target codes with contract and calculator.
4. Confirm prompt/aliases separate walls, lintels, parapets, and vent chimney blocks.
5. Run JSON/YAML validation after edits.
6. Confirm no project-specific values, page numbers, or USV-only facts were added to production config.

