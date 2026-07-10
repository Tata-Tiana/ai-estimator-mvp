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

Full pass done 2026-07-10: calculator hardcode fix, `estimate_lines` build-out (3 -> 31), and
parser/schema cross-check, all in one session.

**Calculator fix applied 2026-07-10** (explicit user authorization — exception to the usual
"never touch calculator code" rule for this stage): `flat_roof_calculator.py` had several literal,
project-specific Excel-match numbers baked directly into production code paths —
`material_total_override=377080` on `eps100_technonikol_carbon_eco`, `expected_total=41304` on
`eps_slope_2_1_plate_a`, a required-but-unused-for-computation external field
`pvc_membrane_expected_material_total` overriding the PVC membrane line, similar override fields
for `roof_consumables_total`/`roof_logistics_and_supply_total`, and section-level raw totals that
were literally defined as equal to the *displayed* totals rather than true raw sums. All removed;
every line's `material_total` is now `round_half_up(material_total_raw)`, and section raw totals are
genuine per-line sums. Real computed values differ from the old hardcoded ones by 1-3 currency units
(rounding artifacts in the original Excel sheet). Full writeup, before/after numbers, and updated
`expected.json` fixtures: see `docs/report_flat_roof_calculator.md` (dated addendum) and the calculator's
own git history. Both cases with `expected.json` coverage pass 0 mismatches after the fix.

**`estimate_lines` built out 2026-07-10**: contract previously declared only 3 of the calculator's 31
real output lines. Rebuilt the full list directly from `calculate_flat_roof()`'s line-by-line
execution order (matches `docs/report_flat_roof_calculator.md`'s own "31 lines" count). Added a new
`auto_calculated` section (6 entries: `roof_area_total_m2`, `parapet_and_abutment_total_length_m`,
`rail_ordered_length_m`, `pvc_membrane_required_area_m2`, `pvc_membrane_rolls`,
`internal_drain_total_length_m`) and a `checks` section, neither of which existed before.

**18 previously-undeclared required calculator inputs found and added** (without them the adapter
could not have constructed a valid calculator input at all, in any mode): 6 catalog pack-volume
`defaults` (`eps100_pack_volume_m3`, `eps50_pack_volume_m3`, `slope_plate_{a,b,j,k}_pack_volume_m3`)
and 8 new work/material `price_keys` (`gas_block_wall_hole_drilling_rate`,
`internal_drain_pvc_110_unit_price_per_m`, `internal_drain_pvc_110_work_rate_per_m`,
`internal_roof_drain_installation_rate`, `parapet_roof_drain_installation_rate`,
`roof_waste_removal_truck_unit_price`, `roof_waste_removal_work_rate_per_truck`,
`vent_shaft_abutment_work_rate_per_item`). Also found that the calculator reads 4 *separate fixed*
fields for slope plate prices (`slope_plate_a/b/j/k_unit_price_per_m3`, not dynamic rows) — the
pre-existing single `slope_plate_unit_price_per_m3` price_key is kept as-is (all 4 real prices are
identical in every production test case) but its notes now document that it fans out to 4
`calculator_input_mapping` targets, not one.

**Parser gaps found and fixed 2026-07-10** in `calculator_targets_compact.json` and
`target_aliases_ru.yaml`:
- 5 target codes used a bare name instead of this section's own `roof_`-prefixed convention that the
  contract already used (`parapet_length_level_1/2` -> `roof_parapet_length_level_1/2`,
  `vent_wall_abutment_level_1/2` -> `roof_vent_wall_abutment_level_1/2`,
  `internal_drain_height_per_drain` -> `roof_internal_drain_height_per_drain`) — renamed to match the
  contract, consistent with every other section's self-prefixed target-code convention.
- `roof_eps_main_volume` and `roof_pvc_membrane_area` were both present as parser targets but never
  referenced by any `target_code` in the contract — verified against `calculate_flat_roof()` that
  neither a combined EPS volume nor a direct membrane area is ever read (EPS100/EPS50/4 slope plates
  are always separate; membrane material is always computed from area × coefficients into rolls, not
  taken as a direct area input). Removed both as dead weight.
- `roof_raw_material_spec_rows` (the diagnostic spec-table breakdown declared in the contract) was
  completely missing from `calculator_targets_compact.json`'s `extract_groups`,
  `target_aliases_ru.yaml`, and the schema's `group_value_shapes`. Added to all three.
- `vent_shaft_abutment_count` and `gas_block_wall_holes_count` were already present as *grounded*
  parser targets (verified against real candidate PDFs) but the contract's `supplier_inputs` entries
  for them had no `target_code` at all, so any extracted value had nowhere to land. Added
  `target_code` to both `supplier_inputs` entries — still `SUPPLIER_INPUT`/`manual_required` (try to
  extract, but always confirm manually), same pattern as `schiedel_vent_channels`'s material counts.

After this pass, `calculator_targets_compact.json`'s `flat_roof` section matches the contract's 14
`target_code`s (12 `review_parameters` + 2 `supplier_inputs`) 1:1 — verified programmatically, zero
missing, zero orphaned.

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

