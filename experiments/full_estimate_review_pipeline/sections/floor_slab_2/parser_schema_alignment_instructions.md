# Parser/schema alignment instructions — floor_slab_2

Purpose: keep the chat extraction files, review workbook contract, and calculator input shape aligned. The calculator field names are the ground truth; do not rename calculator fields to match an older parser output.

## Ground truth

- Section: `floor_slab_2`
- Contract: `sections/floor_slab_2/section_contract.yaml`
- Calculator: `experiments/floor_slab_2_calculator/calculator.py`
- Extraction files to keep aligned:
  - `experiments/chat_extraction_poc/data/calculator_targets_compact.json`
  - `experiments/chat_extraction_poc/data/target_aliases_ru.yaml`
  - `experiments/chat_extraction_poc/schemas/claude_extraction_output_schema.json`
  - `experiments/chat_extraction_poc/prompts/claude_estimate_extraction_prompt.md`

## Current status

Contract exists, but this section still needs the same parser/schema cross-check pass that foundation slab already received.

Known risk: this contract currently expects `floor_slab_2_rebar_items` rows with `spec_length_m`. Active parser/schema files must be checked and aligned to the calculator, not to old generic names.

## AUTO_PROJECT values expected from PDF/chat JSON

- `main_formwork_area_m2`
- `edge_formwork_area_m2`
- `beams_formwork_area_m2`
- `slab_edge_perimeter_m`
- `edge_insulation_height_m`
- `concrete_placing_volume_m3`
- `slab_area_m2`
- `floor_slab_2_rebar_items`

## Repeated-row shape

`floor_slab_2_rebar_items`:

- `steel_class`
- `diameter_mm`
- `spec_length_m`

## Critical extraction rules

- Keep slab formwork, edge formwork, and beam formwork as separate rows.
- Keep slab perimeter and edge insulation height separate; the calculator uses both for edge EPS.
- Keep concrete volume for this slab separate from foundation slab, floor slab 1, beams, walls, and lintels.
- Rebar rows must stay row-by-row; do not calculate total weight in GPT/Claude unless PDF explicitly gives it and the calculator expects it.

## Check before marking section ready

1. Read the calculator input shape directly, especially rebar item fields.
2. Confirm whether parser/schema should use `spec_length_m` for `floor_slab_2_rebar_items`.
3. Compare all scalar target codes with contract and calculator.
4. Confirm prompt distinguishes EPS edge volume/area from formwork area.
5. Run JSON/YAML validation after edits.
6. Confirm no project-specific values, page numbers, or USV-only facts were added to production config.

