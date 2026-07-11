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

Contract has received a full pass matching the calculator, including the beam changes below — parser/schema files (`calculator_targets_compact.json`, `target_aliases_ru.yaml`, extraction schema, prompt) are the remaining not-yet-checked layer for this section.

Known risk: `floor_slab_2_rebar_items` rows now need `spec_length_m`, `kg_per_meter` and `rod_length_m` from the PDF (see "Repeated-row shapes" below — the calculator no longer has a fallback catalog for the latter two). Active parser/schema files must be checked and aligned to the calculator, not to old generic names.

**Calculator change applied 2026-07-10** (explicitly requested, out of the usual "never touch calculator code" rule for this stage — recorded here on purpose): `experiments/floor_slab_2_calculator/calculator.py` previously hardcoded the assumption "floor slab 2 has no beams" — `beams_formwork_area_m2` silently defaulted to 0 with that exact warning text if not supplied, and there was no way to feed beam geometry at all. Per Elena, a beam may or may not exist on either floor slab independently — it is not tied to which floor. Added an optional `beams: {"items": [...]}` input (same row shape as `floor_slab_1_calculator.py`: `code`, `name`, `length_m`, `width_m`, `height_m`, `count`), applied to all three places beams actually affect the floor_slab_1 calculation (audited by reading `floor_slab_1_calculator.py` in full first, to make sure nothing was missed):

1. **Formwork**: `beams_formwork_area_m2` is derived from the sum of item `formwork_area_m2` when the scalar input is absent; if both are given, the scalar wins with a delta warning past 0.01 m2 — same priority as `floor_slab_1_calculator.py`.
2. **EPS100 edge insulation**: each beam's `length_m * height_m * count` now adds to the insulation material area (`edge_and_beam_insulation_area_m2`, drives EPS pack count and foam-glue can count), and each beam's `length_m * count` adds to `total_insulation_length_m`, which is now the real quantity on the `edge_insulation_work` estimate line (previously always `slab_edge_perimeter_m` alone, silently ignoring beams).
3. **Concrete**: `slab_concrete_volume_m3 = concrete_placing_volume_m3 - beams_items_concrete_volume_m3` is now the quantity on `concrete_placing_work` (slab-only work); a new `beam_concreting_work` estimate line prices the beam concrete separately, using a new optional `beam_concreting_work_unit_price` input that is only read when `beams.items` is non-empty (so it is never required on projects without beams).

Backward compatible in every case: no `beams` input at all → every one of the above stays numerically identical to before (0 contribution everywhere, `beam_concreting_work` line present with quantity/total 0, no new required input is read). All 6 existing test cases in `cases/` still pass with 0 mismatches after this change; also manually verified with a synthetic beam that formwork/insulation/concrete all move together consistently.

Rebar row shape is the same flat list (differentiated by diameter/class) as every other section — no beam-specific rebar group needed here, matching `floor_slab_1`.

**Second calculator change, also applied 2026-07-10** (explicitly requested — user's own words: "первый вариант он универсальный, берёт то, что в ПДФ и всё"): `calculate_rebar_item`'s `spec_length_items` production path used to hardcode a 3-entry `REBAR_CATALOG` (A500 ⌀16/12/10 only) — `kg_per_meter`, `rod_length_m`, `code`, `name` and `price_code` were all looked up from this fixed dict by `(steel_class, diameter_mm)`, and any other combination raised `"Unsupported rebar catalog item"`. On top of that, the estimate-line builder unconditionally expected exactly those three codes (`rebar_by_code["rebar_a500_d16"]`, etc.) — a project with a different rebar diameter/class, or missing one of the three, would crash or silently drop a line.

Removed the catalog entirely and made floor_slab_2's rebar handling identical to floor_slab_1's:
- `kg_per_meter` and `rod_length_m` are now read directly from each `rebar_items` row (real PDF/spec values), same as `legacy_weight_kg` mode already did — there is no longer a behavioral difference between the two calc methods on this point.
- `code`, `name`, `price_code` are optional per row, auto-derived from `steel_class` + `diameter_mm` when absent (`make_rebar_code`/`make_rebar_name`, copied verbatim from `floor_slab_1_calculator.py`).
- Estimate lines are generated dynamically, one per actual `rebar_items` row (`rebar_estimate_lines = [estimate_line(item["code"], ...) for item in rebar_items]`, spliced into `lines` with `*rebar_estimate_lines`), replacing the three hardcoded `rebar_a500_d16`/`d12`/`d10` blocks. Any diameter, any class, any count of rows now works — manually verified with A400 ⌀14 and A500 ⌀8 (neither in the old catalog), no crash.
- All 6 existing test cases still pass with 0 mismatches; `cases/test_floor_slab_2_rebar_spec_lengths/input.json` needed `kg_per_meter`/`rod_length_m` added to its three rebar rows (previously supplied invisibly by the catalog) using the exact same numeric values the catalog had, so the expected output is unchanged. One cosmetic fixture fix: the old catalog's hardcoded names used Cyrillic "А500" (а homoglyph typo); auto-generated names use whatever `steel_class` the row actually has, which is Latin "A500" everywhere in this codebase (matches `floor_slab_1`'s own fixtures) — `expected.json` updated to Latin, not a functional change.

**Contract updated 2026-07-10** to match both calculator changes above and several pre-existing gaps found while doing it (none needed a calculator change, only contract text):

- `review_parameters.beams_formwork_area_m2` and the old `defaults.beams_formwork_area_default_m2` both still claimed "Current calculator scope has no beams" — false since the beam change above. The stale `defaults` entry was **removed outright**, not just reworded: sending an explicit `0` for `beams_formwork_area_m2` is no longer harmless — the calculator now treats any non-null scalar as an authoritative override, so a hardcoded `DEFAULT: 0` would silently suppress the real `beam_items` sum whenever beams exist. Leaving the field genuinely null is now the correct "no override" signal.
- Added a new `review_parameters` entry for `beam_items` (repeated_rows: `code`, `name`, `length_m`, `width_m`, `height_m`, `count`), `row_key_field: code`, optional, mirrored to sheet 03 like `floor_slab_1`.
- `row_key_field` for `floor_slab_2_rebar_items`: `steel_class` (not unique — every position used to be A500) → `code`. Went through `diameter_mm` as an intermediate step while the catalog still existed (code wasn't a real input concept then); once the catalog was removed, `code` became optional-and-derivable exactly like `floor_slab_1`, so it was switched to `code` for full consistency with that section.
- `floor_slab_2_rebar_items.columns` gained `kg_per_meter` and `rod_length_m` (now real per-row PDF/spec values, not catalog-derived) and `unit_price_per_m` (adapter-filled, not from PDF — the calculator reads it directly from each row in both calc methods, which the contract never declared before).
- `price_keys.rebar_unit_price_by_item` — one generic key (`registry_code: rebar_<class>_d<diameter>_m`, resolved per row by the adapter), matching `floor_slab_1`'s exact convention. (This went through three separate per-diameter keys briefly, while the catalog still existed; collapsed back to one generic key once the catalog was removed, since there's no longer a fixed set of diameters to name keys after.)
- `estimate_lines` for rebar: one `rebar_items_dynamic` entry (`line_role: dynamic_material_rows`), matching `floor_slab_1`'s exact convention, instead of a fixed set of per-diameter entries.
- Found and fixed two independent, pre-existing gaps unrelated to beams/rebar: `eps100_pack_volume_m3` was used in a production formula but had no `defaults` entry anywhere (added, value `0.2773`, same catalog constant as `floor_slab_1`); `formwork_rental_supplier_quote_total` is read unconditionally by the calculator (`input_data["formwork_rental_supplier_quote_total"]`, no fallback) but was not declared anywhere in the contract at all — a real, previously undocumented crash risk. Added as a `supplier_inputs` entry.
- Added `auto_calculated` entries (14 total, none existed before) for every derived quantity the beam change and the estimate-line build-out needed: `beams_concrete_volume_m3`, `slab_concrete_volume_m3`, `edge_and_beam_formwork_area_m2`, `total_insulation_length_m`, `edge_and_beam_insulation_area_m2`, `formwork_delivery_trips`, `plywood_sheets`, `timber_volume_m3`, `total_rebar_order_length_m`, `concrete_order_volume_m3`, `concrete_delivery_trips`, `eps100_order_volume_m3`, `foam_cans_ordered`, `direct_cost_base_before_addons`.
- `estimate_lines.concrete_placing_work.quantity.formula` changed from the raw `concrete_placing_volume_m3` scalar to `auto_calculated.slab_concrete_volume_m3` (the post-beam-split value), and a new `beam_concreting_work` estimate line was added with its own new `beam_concreting_work_unit_price` price key (`required: false` — only read by the calculator when `beam_items` is non-empty).
- **Full `estimate_lines` build-out**: this section was previously stopped at 3 of the lines the calculator actually returns (`formwork_rental_set`, `concrete_placing_work`, `eps100_penoplex_material` — the file ended immediately after, with no `workbook_layout` or `checks` block at all, a pre-existing gap unrelated to beams/rebar). All 25 contract entries (one of which, `rebar_items_dynamic`, represents a variable number of real calculator lines) are now documented, verified programmatically against `calculator.py`'s real `estimate_line(...)` call order, and checked for zero dangling `leaf_inputs`/price-key references.

Related, not done here: `floor_slab_1`'s own contract has the same latent gap `floor_slab_2` had — `rod_length_m` and `unit_price_per_m` are real per-row calculator inputs but aren't declared as `floor_slab_1_rebar_items` columns. Worth checking when that section gets its own full contract pass.

## AUTO_PROJECT values expected from PDF/chat JSON

- `main_formwork_area_m2`
- `edge_formwork_area_m2`
- `beams_formwork_area_m2`
- `slab_edge_perimeter_m`
- `edge_insulation_height_m`
- `concrete_placing_volume_m3`
- `slab_area_m2`
- `floor_slab_2_rebar_items`
- `beam_items`

## Repeated-row shapes

`floor_slab_2_rebar_items` (any diameter/class — no hardcoded catalog since 2026-07-10):

- `steel_class`
- `diameter_mm`
- `spec_length_m`
- `kg_per_meter` (real PDF/spec value, no longer catalog-derived)
- `rod_length_m` (real PDF/spec value, no longer catalog-derived)
- `unit_price_per_m` (adapter-filled from `rebar_unit_price_by_item`, not a PDF value — do not ask the parser for this)

`beam_items` (optional; this floor slab may have zero, one, or several beams, independently of floor_slab_1):

- `code`
- `name`
- `length_m`
- `width_m`
- `height_m`
- `count`

## Critical extraction rules

- Keep slab formwork, edge formwork, and beam formwork as separate rows.
- Keep slab perimeter and edge insulation height separate; the calculator uses both for edge EPS.
- Keep concrete volume for this slab separate from foundation slab, floor slab 1, beams, walls, and lintels.
- Rebar rows must stay row-by-row; do not calculate total weight in GPT/Claude unless PDF explicitly gives it and the calculator expects it.
- Do not assume this floor slab has no beams, or that it must have them — extract a `beam_items` table only if the PDF actually shows one for this specific slab; leave it empty otherwise.

## `floor_slab_2_rebar_items` parser fields fixed (2026-07-10)

Found while doing `floor_slab_1`'s parser/schema crosscheck: `floor_slab_2_rebar_items` in
`calculator_targets_compact.json` (`extract_groups[].fields`) and
`claude_extraction_output_schema.json` still had the *pre-rebar-catalog-removal* field names
(`length_m`, `mass_per_m_kg`, `weight_kg`) — stale since the "Second calculator change" section
above, which switched the calculator and contract to `spec_length_m`/`kg_per_meter`/`rod_length_m`.
Fixed both files to the real field names, and dropped `weight_kg` (not read anywhere in
`spec_length_items` mode). Also fixed `target_aliases_ru.yaml`'s `unit_policy` text, which likewise
still told the parser to use `length_m`/`mass_per_m_kg`.

`rod_length_m` was missing everywhere (parser had never been told to look for it at all, even before
today). Added it to `calculator_targets_compact.json`, the schema, `target_aliases_ru.yaml`, and the
extraction prompt, with the same guidance used for `floor_slab_1_rebar_items`/`main_wall_rebar_items`/
`lintel_rebar_items` (same class of gap, fixed together): it's usually a catalog/standard rod length
by diameter (e.g. 11.7 m), not something PDFs normally state per row, so only take it from the PDF if
an explicit rod-length table is present — otherwise leave it null for an adapter/catalog fallback,
don't invent a number.

## Remaining scalar targets and beam_items crosschecked (2026-07-10)

Finished the rest of the parser/schema crosscheck against `section_contract.yaml`'s 9
`target_code`s. Found `calculator_targets_compact.json` and `target_aliases_ru.yaml` both missing
3 real targets the contract needs — `floor_slab_2_edge_formwork_area` (present in aliases but not
in `calculator_targets_compact.json`), `floor_slab_2_beams_formwork_area`, and `floor_slab_2_slab_area`
— plus the entire `floor_slab_2_beam_items` extract_group (contract's own `target_code` for its beam
group, distinct from `floor_slab_1`'s bare `beam_items` — each section names its own beam group per
its contract, not a bug, just not shared). Added all 4 to both files, plus a `floor_slab_2_beam_items`
shape entry in the schema's `group_value_shapes` (schema already had a generic `beam_items` shape,
which only matches `floor_slab_1`'s group code, not this section's prefixed one).

Also found and removed `floor_slab_2_eps100_edge_volume`, present in both parser files but not
referenced by any `target_code` in the current contract — verified against `calculator.py` that
`floor_slab_2`'s EPS100 volume is fully derived (`slab_edge_perimeter_m * edge_insulation_height_m`
+ beam contribution, times thickness/waste/pack-rounding), not taken as a direct PDF total the way
`floor_slab_1`'s `total_eps_volume_from_spec_m3` is — this section's architecture never asks for an
EPS volume scalar, so the old target was dead weight from before that design was settled, not a gap.

After this pass, `calculator_targets_compact.json`'s `floor_slab_2` section has exactly the 7 scalar
targets and 2 extract_groups (`floor_slab_2_beam_items`, `floor_slab_2_rebar_items`) the contract's 9
`target_code`s require — verified programmatically, 1:1 match, no extras, no gaps.

## Calculator silent legacy defaults fixed (2026-07-11)

While re-auditing all 8 calculators for the "adapter forgets a `*_calc_method` field, calculator
silently falls back to a legacy mode" risk (same class as `floor_slab_1`'s `insulation_calc_method`
finding), found two instances in `calculator.py`: `formwork_area_calc_method` silently defaulted to
`"legacy_dimensions"`, and `rebar_calc_method` silently defaulted to `"legacy_weight_kg"`. Both already
had `if method not in {...}: raise ValueError(...)` validation right after the `.get()` call, so the
fix was just removing the hardcoded default string from each — a missing field now raises immediately
instead of silently switching modes.

`rebar_calc_method` was relied on implicitly (never set) by 5 of the 6 test fixtures
(`test_floor_slab_2`, `test_floor_slab_2_formwork_delivery_threshold_180`,
`test_floor_slab_2_formwork_delivery_threshold_above_180`, `test_floor_slab_2_live_prices`,
`test_floor_slab_2_spec_formwork_area`) — added `"rebar_calc_method": "legacy_weight_kg"` explicitly to
each to preserve their existing tested behavior. `formwork_area_calc_method` was already explicit in
every fixture. All 6 cases still pass 0 mismatches.

## Check before marking section ready

1. Read the calculator input shape directly, especially rebar item fields.
2. Confirm whether parser/schema should use `spec_length_m` for `floor_slab_2_rebar_items` — done, see above.
3. Compare all scalar target codes with contract and calculator.
4. Confirm prompt distinguishes EPS edge volume/area from formwork area.
5. Confirm prompt/schema/aliases cover `beam_items` the same way `floor_slab_1`'s beam group is covered, once that section's parser files are done.
6. Run JSON/YAML validation after edits.
7. Confirm no project-specific values, page numbers, or USV-only facts were added to production config.

