# Parser/schema alignment instructions — floor_slab_1

Purpose: keep the chat extraction files, review workbook contract, and calculator input shape aligned. The calculator field names are the ground truth; do not rename calculator fields to match an older parser output.

## Ground truth

- Section: `floor_slab_1`
- Contract: `sections/floor_slab_1/section_contract.yaml`
- Calculator: `experiments/floor_slab_1_calculator/floor_slab_1_calculator.py`
- Extraction files to keep aligned:
  - `experiments/chat_extraction_poc/data/calculator_targets_compact.json`
  - `experiments/chat_extraction_poc/data/target_aliases_ru.yaml`
  - `experiments/chat_extraction_poc/schemas/claude_extraction_output_schema.json`
  - `experiments/chat_extraction_poc/prompts/claude_estimate_extraction_prompt.md`

## Current status

Contract exists, but this section still needs the same parser/schema cross-check pass that foundation slab already received.

Known risk: do not copy the foundation slab rebar field names blindly. This contract currently expects `floor_slab_1_rebar_items` rows with `spec_length_m` and `kg_per_meter`. Active parser/schema files must be checked and aligned to the calculator, not to old generic names.

**Calculator change applied 2026-07-10** (explicitly requested, out of the usual "never touch calculator code" rule for this stage — recorded here on purpose): `floor_slab_1_calculator.py`'s beam math (formwork area, EPS100 edge insulation length/area, concrete split into slab vs. beam with its own priced work line) was already correct, but the calculator required the caller to explicitly declare "no beams" in three separate places, or it crashed instead of defaulting to 0:

1. `input_data["beams"]` was a hard-required key (`KeyError` if absent) in two read sites (`calculate_floor_slab_1` and `calculate_insulation_context`) — now `input_data.get("beams")`, defaulting `beam_items` to `[]` when absent.
2. `beams_formwork_area_m2` was hard-required in `spec_formwork_areas` mode (`raise ValueError` if absent) even though the sum-of-`beams.items` fallback value was already computed and passed into the same function — now falls back to that sum (0 when there are no items) instead of raising, matching `floor_slab_2_calculator.py`'s new behavior.
3. `rates["beam_concreting_work_rate_per_m3"]` was read unconditionally, so it was required even on projects with zero beams — now only read when `beam_items` is non-empty, otherwise the rate is 0.

This makes floor_slab_1 match the same "no beams found by the parser → 0 everywhere, nothing breaks" behavior floor_slab_2 now has, so both sections can be fed the exact same way regardless of which floor (if any) actually has beams on a given project. All 6 existing test cases (which do supply beams) still pass with 0 mismatches; manually verified the no-beams path produces a zero-valued `beam_concreting_work` line and no crash.

## AUTO_PROJECT values expected from PDF/chat JSON

- `total_concrete_volume_from_spec_m3`
- `slab_thickness_m`
- `slab_edge_perimeter_m`
- `main_formwork_area_m2`
- `edge_formwork_area_m2`
- `beams_formwork_area_m2`
- `slab_outer_edge_eps_work_length_m`
- `edge_insulation_height_m`
- `slab_edge_eps_material_area_m2`
- `bottom_slab_eps_work_area_m2`
- `total_eps_volume_from_spec_m3`
- `floor_slab_1_rebar_items`
- `beam_items`
- `beam_table_controls`

## Repeated-row shapes

`floor_slab_1_rebar_items`:

- `floor`
- `component`
- `steel_class`
- `diameter_mm`
- `spec_length_m`
- `kg_per_meter`

`beam_items`:

- `code`
- `name`
- `length_m`
- `width_m`
- `height_m`
- `count`

`beam_table_controls`:

- `label`
- `value`
- `unit`

## Critical extraction rules

- Keep slab concrete separate from beam concrete and foundation concrete.
- Keep bottom EPS area, edge EPS area, and EPS volume separate.
- Keep under-slab formwork area separate from edge formwork and beam formwork.
- Rebar rows must stay row-by-row; do not ask GPT to calculate total weight unless PDF explicitly gives it.

## Check before marking section ready

1. Read the calculator input shape directly, especially rebar and beam item dataclasses.
2. Confirm whether parser/schema should use `spec_length_m/kg_per_meter` for `floor_slab_1_rebar_items`.
3. Compare all scalar target codes with contract and calculator.
4. Confirm `beam_items` shape matches calculator expectations.
5. Run JSON/YAML validation after edits.
6. Confirm no project-specific values, page numbers, or USV-only facts were added to production config.

