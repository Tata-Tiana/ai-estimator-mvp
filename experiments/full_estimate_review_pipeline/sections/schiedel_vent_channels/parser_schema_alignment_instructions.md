# Parser/schema alignment instructions — schiedel_vent_channels

Purpose: keep the chat extraction files, review workbook contract, and calculator input shape aligned. The calculator field names are the ground truth; do not rename calculator fields to match an older parser output.

## Ground truth

- Section: `schiedel_vent_channels`
- Contract: `sections/schiedel_vent_channels/section_contract.yaml`
- Calculator: `experiments/schiedel_vent_channels_calculator/calculator.py`
- Extraction files to keep aligned:
  - `experiments/chat_extraction_poc/data/calculator_targets_compact.json`
  - `experiments/chat_extraction_poc/data/target_aliases_ru.yaml`
  - `experiments/chat_extraction_poc/schemas/claude_extraction_output_schema.json`
  - `experiments/chat_extraction_poc/prompts/claude_estimate_extraction_prompt.md`

## Current status

Contract exists, but this section still needs the same parser/schema cross-check pass that foundation slab already received.

## AUTO_PROJECT values expected from PDF/chat JSON

- `schiedel_masonry_total_length_m`
- `vent_channel_1_height_m`
- `vent_channel_2_height_m`
- `vent_channel_2_count`
- `vent_chimney_cladding_segments`

## Repeated-row shape

`vent_chimney_cladding_segments`:

- `name`
- `length_m`
- `quantity`
- `total_length_m`

## Check before marking section ready

1. Read the calculator input shape directly.
2. Compare contract `calculator_input_path` values with the calculator.
3. Compare target codes and repeated-row columns with `calculator_targets_compact.json`.
4. Compare repeated-row shape with `claude_extraction_output_schema.json`.
5. Confirm prompt/aliases do not ask GPT to infer quantities that the calculator should calculate.
6. Run JSON/YAML validation after edits.
7. Confirm no project-specific values, page numbers, or USV-only facts were added to production config.

