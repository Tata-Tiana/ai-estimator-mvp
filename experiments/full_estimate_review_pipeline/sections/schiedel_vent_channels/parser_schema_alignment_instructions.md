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

Full parser/schema cross-check pass done 2026-07-10. Contract's `review_parameters`/`supplier_inputs`
`target_code`s now match `calculator_targets_compact.json` 1:1 (7 codes: 5 scalar targets + 1 extract
group, verified programmatically — zero missing, zero orphaned).

**Contract fix applied 2026-07-10** (pure contract-side change, no calculator code touched):
`calculate_schiedel_vent_channels()` reads `input_data["vent_channel_1_height_m"]`,
`input_data["vent_channel_2_height_m"]` and `input_data["vent_channel_2_count"]` unconditionally (no
`.get()`, no calculator-side default) to build a diagnostic-only `masonry_control_length` formula —
but the contract marked all three `required: false` / `status_if_missing: "optional_control"` with
`fallback: null` in `calculator_input_mapping`, which would crash the calculator (`KeyError` or
`decimal.InvalidOperation`) whenever the PDF doesn't give separate channel heights. Changed
`fallback: null` → `fallback: 0` for all three — safe because they only feed a display-only control
formula, never the paid `schiedel_masonry_work` quantity (that always comes from
`schiedel_masonry_total_length_m`, read separately and always required).

**Two real parser gaps found and fixed 2026-07-10**:
1. `schiedel_masonry_total_length_m` — the section's single most important required scalar target —
   was completely absent from both `calculator_targets_compact.json` and `target_aliases_ru.yaml`.
   Added to both, using the aliases already declared in the contract's own `parser_mapping`.
2. `vent_chimney_cladding_segments` (this section's diagnostic spec-table breakdown, never read by
   the calculator) used a bare group_code that collides with a *different*, calculator-consumed
   extract_group of the same name under `load_bearing_walls_lintels` (gas-block cladding segments,
   `length_m`/`count` shape, feeds `legacy_segments_rows` mode there) — a real ambiguity risk in the
   flat alias/schema namespace, since `target_aliases_ru.yaml` and the schema's `group_value_shapes`
   are both keyed by group_code with no per-section scoping. Renamed this section's own copy to
   `schiedel_vent_chimney_cladding_segments` everywhere (contract `key`/`target_code`/
   `normalized_json_path`/`group_codes`, `calculator_targets_compact.json`, `target_aliases_ru.yaml`,
   and the extraction schema's `group_value_shapes`) — `load_bearing_walls_lintels`'s own
   `vent_chimney_cladding_segments` group was left untouched.

**One stale target removed 2026-07-10**: `schiedel_gas_block_150_volume` was present in both parser
files but not referenced by any `target_code` in this contract — `calculate_schiedel_vent_channels()`
has no gas-block-volume field at all. Its own notes said "may share the same source as
`load_bearing_walls_lintels vent_chimney_gas_block_150_volume`" — that section's real target
(`vent_chimney_gas_block_150_volume`, feeding `vent_chimney_gas_block_spec_volume_m3`) already covers
this data properly; this was dead weight left over from before that assignment settled. Removed from
both parser files.

**Known but not fixed, flagged only (diagnostic-only, no calculator behavior impact)**: the
calculator's `formula`/`control_metrics` output fields for both channel-type material lines contain
hardcoded literal strings (`"control_blocks_raw": "65.51515152"`, `"secondary_control_value": "28"`
for VENT 2; `"14.57575758"`/`"6"` for VENT 3, plus matching entries in `calculation_blocks.control_metrics`)
— not computed from any input, and explicitly documented in the code's own `notes` as
"контрольные числа сохранены справочно и не участвуют в quantity" (reference-only, not used in
quantity). Same class of issue as waterproofing's fixed `display_quantity=1.94`, but this one never
touches `material_total`/`work_total`/`line_total` or any payable quantity — purely cosmetic
diagnostic output. Not fixed here; would need the same explicit go-ahead as any other calculator-code
touch.

## AUTO_PROJECT values expected from PDF/chat JSON

- `schiedel_masonry_total_length_m`
- `vent_channel_1_height_m`
- `vent_channel_2_height_m`
- `vent_channel_2_count`
- `schiedel_vent_chimney_cladding_segments`

## Repeated-row shape

`schiedel_vent_chimney_cladding_segments` (renamed 2026-07-10, see "Current status" above):

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

