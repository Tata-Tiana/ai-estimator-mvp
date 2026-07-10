# Step 13 — Foundation Slab: Contract vs Real Extraction Cross-Check

## Scope

Cost-basis ("себестоимость") only, per the Cross-Check Stage in `HANDOFF.md`. Checks
`sections/foundation_slab/section_contract.yaml` against three independent real project
chat-extraction passes for the same project (ЮСВ, both КР1/КР2 PDFs): two earlier passes and one
later, more careful pass with explicit arithmetic self-checks and lower-confidence flagging on
ambiguous OCR reads. No literal project quantities are recorded in this file — only structural
findings (field names, source classes, presence/absence), per the hard rule in the Cross-Check
Stage section of `HANDOFF.md`.

## What was checked

Every `review_parameters` entry in the contract was matched against the real extraction JSON's
`sections.foundation_slab.found` / `needs_review` / `missing` arrays and against the underlying
`raw_table_rows` for the same section.

## Confirmed matches (target_code + source_class align, no action needed)

- `slab_side_formwork_area_m2` → real target_code `slab_side_formwork_area` — found, high confidence.
- `eps50_under_slab_volume_m3` → real target_code `eps_50_under_slab_volume` — found, high confidence.
- `concrete_project_volume_m3` → real target_code `concrete_project_volume` — found, high confidence.
- `thermal_insert_50_material_spec_qty` / `thermal_insert_100_material_spec_qty` → matching real
  target_codes — found, high confidence. These are now real per-project values in the improved
  extraction pass, not template placeholders (see prior session note about the older
  `mvp_usv_demo` pipeline run, where these same fields were `missing`/`not_found`).
- `thermal_insert_50_length_m` / `thermal_insert_100_length_m` → matching real target_codes —
  present but `needs_review: true` in the real extraction. Root cause confirmed structurally: the
  PDF's thermal-insert-plan table has a single combined "Длина термовставок" row, not two separate
  rows for 50mm and 100mm. The parser correctly used the one available value as a *candidate* for
  both targets and flagged both `needs_review`. This is expected PDF-structure behavior, not a
  parser defect — likely to recur on other projects with the same drawing convention.
- `foundation_rebar_items` (repeated_rows group) → matching group `target_code`. In the third
  extraction pass, found for all 5 real rebar positions in this project's PDF (see finding 3 below
  for the reliability history of the 5th position across passes).

## Findings / corrections needed

### 1. `target_code` mismatch: `membrane_area_m2` vs `planter_membrane_area` — RESOLVED, parser renamed

The contract's `membrane_area_m2` entry declares `parser_mapping.target_codes: ["membrane_area_m2"]`,
matching `foundation_slab_calculator.py`'s real field name. The extraction pipeline used to emit this
value under a different code, `planter_membrane_area`.

**Resolution (per the Naming Alignment Rule added to `HANDOFF.md` this pass)**: rather than editing
the contract to point at the parser's old name, the parser-side files were renamed instead —
`planter_membrane_area` → `membrane_area_m2` in `data/calculator_targets_compact.json` (both the
`earthworks` cross-reference entry and the `foundation_slab` target entry) and
`data/target_aliases_ru.yaml`. The contract needed **no change at all**: once the parser's code
matched the calculator's field name, the contract's existing `target_codes: ["membrane_area_m2"]` was
already correct. This is now the standing approach for every future naming mismatch found in this
stage — see `HANDOFF.md`'s Naming Alignment Rule.

### 2. `foundation_rebar_items` column-name mismatch — contract is correct, extraction files are the mismatch

**Correction (retracts the original version of this finding)**: the original recommendation here was
to rename the contract's `source_length_m`/`kg_per_meter` columns to `length_m`/`mass_per_m_kg` to
match the extraction pipeline's field names. That was checked against the wrong ground truth. Per the
project's stated priority — the calculator's own input shape is the ultimate ground truth for what
the parser should find — `foundation_slab_calculator.py`'s `RebarItemInput` dataclass was read
directly (`source_length_m`, `kg_per_meter` are the real field names it requires; confirmed again by
grep this pass). So `section_contract.yaml`'s existing columns are **already correct** and must not be
renamed.

The real mismatch is upstream, in the chat-extraction pipeline's own files
(`data/target_aliases_ru.yaml`, `data/calculator_targets_compact.json`,
`schemas/claude_extraction_output_schema.json`), which currently instruct/describe the model to emit
`length_m`/`mass_per_m_kg` instead of the calculator's real names. There is no adapter step today that
renames these before they'd reach the contract's `calculator_input_mapping`.

**Suggested fix (revised)**: rename the field keys in those three extraction-pipeline files
(`foundation_rebar_items` entries) from `length_m`/`mass_per_m_kg` to `source_length_m`/`kg_per_meter`
so the extraction output matches the calculator's real input shape directly — leave
`section_contract.yaml` unchanged. The same rename should be independently verified (not assumed by
analogy) against each of the other four rebar groups' own calculators
(`floor_slab_1_rebar_items`, `floor_slab_2_rebar_items`, `lintel_rebar_items`,
`masonry_rebar_a500_d10_weight`) before touching those.

### 3. Extraction-pipeline reliability: a rebar row is easy to lose between `raw_table_rows` and `found`

The thermal-insert-plan table (source: PDF, thermal-insert drawing page) contains a hoop/stirrup
rebar row (steel class A240, diameter 6mm). In the first two extraction passes this row was tagged
correctly in `raw_table_rows` (`mapped_target_codes: ["foundation_rebar_items"]`) but then
**silently disappeared** from the final `found` array — not present there, not present in
`missing` either. That was a real aggregation-stage defect, not a contract issue.

**Update from the third, more careful extraction pass**: the same row now survives into `found`,
but with low confidence and `needs_review: true`, because the model could not unambiguously match
the unit of measurement (m.п. vs pcs) to this specific number during OCR reading, and said so
explicitly instead of guessing. This is the correct behavior — the earlier two passes' silent drop
was the actual bug, and it did not reproduce in the third pass. This suggests the failure mode is
prompt/model-quality dependent rather than a structural limitation, but it is still worth flagging
to whoever maintains the chat-extraction prompt: a less careful pass can silently drop a real,
PDF-confirmed rebar position with no trace in either `found` or `missing`.

**Recommended action**: no `section_contract.yaml` change (the contract only describes what a
*correct* extraction should look like, not the extraction logic itself). Worth noting in the
chat-extraction prompt/schema that every `raw_table_rows` entry with a non-empty
`mapped_target_codes` must end up in exactly one of `found` / `needs_review` / `missing` — never
silently absent from all three.

### 4. `eps_100_edge_volume` — resolved: no calculator wiring in either mode, correctly out of the contract

**Resolved** (was an open question in the original version of this finding). Checked directly against
`foundation_slab_calculator.py`: grepped the whole file for `eps100|eps_100|edge_volume` — no such
input field exists in any dataclass, in either mode.

- In **legacy** mode, EPS100 volume is computed geometrically from
  `thermal_insert_pieces × eps100_thickness_m × thermal_insert_piece_height_m ×
  thermal_insert_piece_depth_for_eps_m` — never read from a PDF-given volume at all.
- In **production** mode (`standard_50_100`), this geometric block is hardcoded to return `0`; the
  real EPS100 material need is captured entirely separately through
  `thermal_insert_100_material_spec_qty` (see finding resolution below).

So `eps_100_edge_volume`, even though the parser finds it correctly in the PDF, has no path into any
calculator input in either mode today. It is correctly out of scope for `calculator_input_mapping`.
It could only ever be a diagnostic/QA-only field (comparable to `reinforcement_density`) — not worth
adding to the contract unless a future cross-check specifically wants a redundant sanity comparison
against `thermal_insert_100_material_spec_qty`. No contract change needed.

### 5. `thermal_insert_100_material_spec_qty` — confirmed wired end-to-end, but exposes a systemic null-default risk

Traced the full path in `foundation_slab_calculator.py`: `FoundationSlabInput.thermal_insert_100_material_spec_qty`
(already correctly named, matches both the contract's `calculator_input_path` and the parser's
`target_code` — no naming mismatch here) → `calculate_thermal_insert_block`
(`raw_qty = spec_qty * thermal_insert_material_waste_coeff`, then
`purchase_qty = round_up_to_multiple(raw_qty, thermal_insert_100_pack_multiple_qty)`) → a real, final
estimate line (`code="thermal_insert_100_material"`, `unit="м3"`,
`price_code="thermal_insert_100_material_m3"`). This is a genuine, functioning smeta line, not
dead/unused code.

**Parser side confirmed working**: all three independent extraction passes found
`thermal_insert_100_material_spec_qty` with a real per-project value, high confidence, not flagged
`needs_review` — the extraction→calculator wiring for this field is real and working today.

**Real risk found**: `section_contract.yaml`'s `defaults` list currently has
`thermal_insert_100_pack_multiple_qty: value: null` (and the sibling `thermal_insert_50_pack_multiple_qty`
and `eps50_pack_volume_m3` are also `value: null`). These are catalog/package-size constants, not
PDF-extractable data, so the extraction pipeline will never fill them — but if any of them are left
`null` when the calculator actually runs, `round_up_to_multiple(raw_qty, None)` breaks the
calculation. The code only logs a `warnings` entry today; it does not block the run.

**Recommended action (not yet built, tracked here as a to-do)**: this pattern — `DEFAULT` entries with
`value: null` for catalog/package constants — is expected to recur in every future section's contract,
not just foundation_slab's. Rather than filling these three in one at a time per section, build a
shared defaults/catalog reference (a "справочник") that every calculator's contract can pull package
sizes, pack multiples, and similar constants from, so a missing value is caught before a calculation
run rather than crashing during one. Until that catalog exists, each contract's `null`-valued
`defaults` should be treated as a blocking pre-run checklist item for that section, checked manually
project by project.

## Confirmed NOT in real extraction (expected — correctly out of scope for this stage)

None of the following appear anywhere in the real extraction JSON for `foundation_slab` (`raw_table_rows`, `found`, `needs_review`, or `missing`), which is correct — they are `DEFAULT` / `SUPPLIER_INPUT` / `MANUAL_REVIEW` per the contract, not PDF-extractable project data:

- `rebar_crane_shifts`, `rebar_metal_delivery_trucks`, `box_total_metal_weight_kg`, `concrete_pump_shifts` (supplier_inputs)
- `logistics_and_supply_amount`, `consumables_tool_amortization_amount`, `technical_supervision_amount` (price_keys / supplier_inputs)
- plywood/timber sheet dimensions, waste coefficients, rod length, concrete round step, mixer volume, box delivery capacity (all `defaults`)

## Corroboration across three independent extraction passes

Findings 1 and 2 (target_code naming, column-key naming) hold identically across all three
extraction passes — not a one-off artifact of a single model run. Finding 3 (rebar-row reliability)
improved between passes: silently dropped in the first two, present-but-flagged-low-confidence in
the third. No new contract-relevant mismatches surfaced in the third pass beyond what is already
listed here.

## Verdict

- 8 of 9 `review_parameters` fully confirmed against real extraction with no contract changes needed
  (includes `eps_100_edge_volume`'s resolution: correctly out of scope, no calculator wiring exists;
  and finding 1, `membrane_area_m2`, resolved by renaming the parser, contract untouched).
- 1 field's original recommendation (finding 2, rebar columns) is **retracted** — the contract is
  already correct; the real fix is upstream, in the extraction-pipeline's own data files.
- 1 extraction-pipeline reliability issue (finding 3), outside this repo's contract layer — flagged,
  not fixed here; appears to be improving with better extraction passes rather than a hard limit.
- 1 systemic risk (finding 5): `null`-valued catalog `defaults` (pack multiples, package volumes) can
  crash a calculation if left unfilled; no contract change fixes this alone — needs a shared
  defaults/catalog reference across all calculators (not yet built).
- `thermal_insert_50/100_length_m` ambiguity (single combined PDF value) is expected PDF-structure
  behavior, correctly surfaced via `needs_review`, no contract change needed.

## Next steps

1. ~~Apply finding 1~~ — done: parser renamed `planter_membrane_area` → `membrane_area_m2`, contract
   left untouched.
2. ~~Apply finding 2~~ — done: parser renamed `length_m`/`mass_per_m_kg` → `source_length_m`/
   `kg_per_meter` for `foundation_rebar_items` only. The other four rebar groups
   (`floor_slab_1_rebar_items`, `floor_slab_2_rebar_items`, `lintel_rebar_items`,
   `masonry_rebar_a500_d10_weight`) are intentionally left unrenamed — their own calculators use
   different field names (`spec_length_m`, not `source_length_m`) and need their own independent
   Cross-Check pass, not a rename by analogy.
3. Track finding 5 (null catalog defaults) as a to-do against the planned shared defaults/catalog
   reference; until it exists, treat each section's `null`-valued `defaults` as a manual pre-run
   checklist item.
4. `foundation_slab` is closed out for the input side (review_parameters ↔ calculator, parser files)
   of this stage. Continue Cross-Check Stage for the next section in the agreed order.

## `estimate_lines` build-out (2026-07-10)

Separate from the input-side cross-check above: `section_contract.yaml`'s `estimate_lines` block only
had 5 of the calculator's real ~29 lines documented, even though `price_keys`/`defaults`/
`auto_calculated` were already essentially complete. The missing 24 were already drafted in
`catalogs/estimate_line_catalog.yaml` (26 base lines + 3 structural rows, `status: draft_cataloged`) —
spot-checked several against `foundation_slab_calculator.py` directly (thermal-insert mode gating,
structural row codes, the `rebar_items` dynamic expansion) before porting, all confirmed accurate.
Ported all entries into `section_contract.yaml` in the calculator's real execution order; added one
missing `auto_calculated.membrane_rolls` entry the ported lines needed; added 2 price keys
(`thermal_insert_installation_work_unit_price`, `eps100_unit_price`) for the two legacy-only,
`enabled_by_default: false` thermal-insert lines that don't run in production
(`thermal_insert_mode=standard_50_100`). `expected_estimate_line_count` in `checks` corrected from the
old rough estimate of 30 to the verified 29. Zero dangling `leaf_inputs`/price-key references,
checked programmatically.

Found, not fixed, flagged in the `formwork_timber` line's own notes: the calculator has a hardcoded
`display_quantity=1.2` for that line — the same category of issue already fixed for waterproofing's
`display_quantity` (step_16), and explicitly forbidden by this contract's own
`checks.forbidden_production_inputs: display_quantity_overrides`. Needs the same explicit go-ahead
before touching calculator code again.
