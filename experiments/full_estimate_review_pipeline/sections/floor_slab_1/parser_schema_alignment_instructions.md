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

**Contract updated 2026-07-10** — the calculator change above made the calculator itself tolerant of missing beams, but the contract still said `beams_formwork_area_m2.required: true` and `beam_items.required: true`, left over from before that fix. Both changed to `required: false` (`beams_formwork_area_m2`: `status_if_missing: optional_default_zero`; `beam_items`: `status_if_missing: optional`), matching `floor_slab_2`'s already-correct pattern.

Two more pre-existing gaps found and fixed in the same pass, unrelated to beams:
- `floor_slab_1_rebar_items.columns` was missing `rod_length_m` and `unit_price_per_m` — both are real per-row calculator inputs (`item["rod_length_m"]`, `item["unit_price_per_m"]`, no fallback in either), just never declared as columns. Added, matching `floor_slab_2`'s equivalent fix.
- `price_keys.eps_unit_price_per_m3` and `price_keys.foam_unit_price_per_can` had no explicit `calculator_input_path` — most price keys in this contract implicitly go into the calculator's `rates` sub-dict, but the calculator actually reads these two from `insulation` (`insulation_in["eps_unit_price_per_m3"]`, `insulation_in["foam_unit_price_per_can"]`). Added explicit `calculator_input_path: "insulation.<key>"` to both, same convention this file already used for `technical_supervision_amount` → `manual_lines.technical_supervision_amount`.

**Architectural note, recorded 2026-07-10, not acted on**: while auditing the above, checked all 8 section calculators — `floor_slab_1_calculator.py` is the *only* one whose input is a nested dict-of-dicts (`geometry`, `rates`, `insulation`, `overheads`, `manual_lines`, `beams`). Every other section (including `floor_slab_2` after yesterday's rebar-catalog removal) takes a flat set of top-level fields. The nesting isn't buying anything a flat structure couldn't do just as well, and it directly caused the `eps_unit_price_per_m3`/`foam_unit_price_per_can` gap above (a flat structure has no "wrong sub-dict" to fall into). Best guess: `floor_slab_1` predates the flat convention the other 7 sections converged on, and nobody went back to flatten it. Not fixing now — flattening `floor_slab_1_calculator.py` would be a real refactor (the nested dicts are threaded through most of the file's functions), out of scope for a contract-alignment pass. Worth doing eventually for consistency, on its own, deliberately reviewed pass — not bundled into this one.

**Calculator change applied 2026-07-10, second pass** (explicitly requested by the user after an
independent review flagged this as the section's biggest remaining risk — same "explicit exception
to the never-touch-calculator-code rule" as above): `floor_slab_1_calculator.py` had three separate
`*_calc_method` fields (`insulation.insulation_calc_method`, `formwork_areas_calc_method`,
`rebar_calc_method`) that silently defaulted to a legacy mode if the adapter forgot to set them
explicitly — and the `legacy_usv_geometry` insulation branch contains hardcoded ЮСВ-project geometry
literals (`d(19) * d(2) + (d(7) + d("13.2")) * d(2) + d("3.2") * d(2)` at what was line 308). A
forgotten field would silently compute a different project's numbers instead of failing.

All three already had `if method not in {...}: raise ValueError(...)` validation right after the
`.get(key, <legacy default>)` call — the fix was simply removing the hardcoded default string from
each `.get()` call (`insulation.get("insulation_calc_method")`, `input_data.get("formwork_areas_calc_method")`,
`input_data.get("rebar_calc_method")`), so a missing field now hits the *existing* validation and
raises immediately instead of silently falling back. No new validation logic was added — just removed
the silent fallback value.

`formwork_areas_calc_method` was relied on implicitly (never set) by 4 of the 7 test fixtures
(`test_floor_slab_1_direct_formwork_rate`, `test_floor_slab_1_formwork_delivery_threshold`,
`test_floor_slab_1_insulation_spec_quantities`, `test_floor_slab_1_rebar_spec_lengths`) — added it
explicitly as `"legacy_calculated_from_geometry"` to each of those 4 `input.json` files to preserve
their existing tested (deliberately legacy-mode) behavior. `insulation_calc_method` and
`rebar_calc_method` were already explicit in every fixture, no fixture changes needed for those two.
All 7 cases still pass 0 mismatches. Manually verified the new failure mode: deleting
`insulation.insulation_calc_method` from a valid input now raises
`ValueError: insulation.insulation_calc_method must be legacy_usv_geometry or spec_work_quantities`
instead of silently computing ЮСВ's geometry.

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
- `rod_length_m` (real PDF/spec/catalog value; added 2026-07-10, was missing despite the calculator always requiring it)
- `unit_price_per_m` (adapter-filled from `rebar_unit_price_by_item`, not a PDF value — do not ask the parser for this)

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

## Parser/schema crosscheck against the contract (2026-07-10)

Compared every `review_parameters` entry in `section_contract.yaml` against
`calculator_targets_compact.json`, `target_aliases_ru.yaml`, `claude_extraction_output_schema.json`
and the extraction prompt. All 11 scalar `target_code`s match exactly (including
`floor_slab_1_edge_formwork_height`, which is correctly AUTO_CALCULATED and reuses
`floor_slab_1_slab_thickness` rather than having its own parser target). `beam_items` and
`beam_table_controls` repeated-row groups also match.

Found one real gap, shared with 3 other sections' rebar groups: `floor_slab_1_rebar_items`'s
`extract_groups[].fields` in `calculator_targets_compact.json` and its shape in
`claude_extraction_output_schema.json` were both missing `rod_length_m`, even though the contract's
own `columns` list already required it (added earlier this session, since the calculator reads
`item["rod_length_m"]` directly with no fallback). Fixed in both files, plus added a
`rod_length_m`-usage note to `target_aliases_ru.yaml` and the extraction prompt — it's usually a
catalog/standard rod length by diameter (e.g. 11.7 m), not something PDFs normally state per row, so
the parser should only fill it from an explicit rod-length table and otherwise leave it null for a
catalog/adapter fallback rather than inventing a number.

While fixing this, found the same `rod_length_m` gap on `main_wall_rebar_items`/`lintel_rebar_items`
(`load_bearing_walls_lintels`, whose contract also gained `rod_length_m` as a required column earlier
today) and a fully stale `floor_slab_2_rebar_items` entry (`length_m`/`mass_per_m_kg` field names,
left over from before today's rebar-catalog removal in that calculator) — fixed all of them in the
same pass since they're the identical class of bug across shared parser files. See
`floor_slab_2/parser_schema_alignment_instructions.md` for that section's own note.

## Check before marking section ready

1. Read the calculator input shape directly, especially rebar and beam item dataclasses.
2. Confirm whether parser/schema should use `spec_length_m/kg_per_meter` for `floor_slab_1_rebar_items`.
3. Compare all scalar target codes with contract and calculator.
4. Confirm `beam_items` shape matches calculator expectations.
5. Run JSON/YAML validation after edits.
6. Confirm no project-specific values, page numbers, or USV-only facts were added to production config.

