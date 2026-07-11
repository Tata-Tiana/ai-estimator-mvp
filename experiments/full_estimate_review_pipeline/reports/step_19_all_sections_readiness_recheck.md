# Step 19 — All 8 Sections: Full Re-check and Readiness Status

Date: 2026-07-11

## Scope

Full re-verification pass across all 8 section contracts, their calculators, and the shared parser
files, after each section had been built out/fixed individually in earlier passes (steps 08–18 plus
same-day contract work not yet numbered). Triggered by a direct question ("all sections are ready —
does that show in the reports, and what are the 7 xlsx files in output/?") rather than a new section
build-out. Nothing here duplicates the per-section `parser_schema_alignment_instructions.md` files,
which remain the detailed record for each section — this report is the cross-section summary and the
place where cross-cutting fixes (found while checking *all* sections at once) are recorded.

No project-specific quantities, page numbers, filenames, or USV-only values are recorded here.

## The 7 (now regenerated) xlsx files

`experiments/full_estimate_review_pipeline/output/*.xlsx` are Excel review-workbook exports generated
by `build_review_workbook_from_contracts.py` at different milestones while the pipeline was built
(`step_06` earthworks+waterproofing, `step_07` +schiedel, `step_08` +foundation_slab, `step_09`
+load_bearing_walls_lintels, `step_10` +floor_slab_1, `step_11` +floor_slab_2, `step_12` all sections).
All 7 were dated 2026-07-08 — before essentially all of the contract build-out work done since
(foundation_slab 5→29 lines, load_bearing_walls_lintels 7→30, flat_roof 3→31, plus every fix recorded
below), so they were stale. `step_12_all_sections_review_template.xlsx` has been regenerated from the
current contracts (`build_review_workbook_from_contracts.py` with no `--contract` args already picks up
all 8 sections automatically, since it iterates the canonical section list and includes any section
whose `section_contract.yaml` exists). The older step_06–step_11 files were intentionally left as
historical snapshots of intermediate progress, not deleted or regenerated — `step_12` is the current
one to use.

## Per-section status after this pass

| Section | estimate_lines | `checks` block | Calculator tests | Parser target_codes |
|---|---:|:---:|---|---|
| earthworks | 11 | yes | 7/7 cases, 0 mismatch | 1:1 with contract |
| foundation_slab | 29 | yes | 6/6 cases, 0 mismatch | 1:1 with contract |
| waterproofing | 8 | yes | 3/3 cases, 0 mismatch | 1:1 with contract |
| load_bearing_walls_lintels | 30 | yes | 14/14 cases, 0 mismatch (2 error-expectation cases not counted, see below) | 1:1 with contract |
| floor_slab_1 | 24 | yes (added this pass) | 7/7 cases, 0 mismatch | 1:1 with contract |
| floor_slab_2 | 25 | yes | 6/6 cases, 0 mismatch | 1:1 with contract |
| flat_roof | 31 | yes | 3/3 cases, 0 mismatch | 1:1 with contract |
| schiedel_vent_channels | 9 | yes | 2/2 cases, 0 mismatch | 1:1 with contract |

`test_floors_count_three_rejected` and `test_rebar_partitions_rejected`
(`load_bearing_walls_lintels_calculator`) are negative tests with no `expected.json` — they assert the
calculator raises on invalid input, not compared here; not run in this pass since they don't produce a
comparison result, but their existence was noted as a positive sign of the calculator's own guard rails.

Every contract now has: no dangling `leaf_inputs`/price-key references, no duplicate `estimate_lines`
codes, no `price_keys` entries left unreferenced by any line's `material_unit_price_key`/
`work_unit_price_key`/`fixed_amount_key` (the sole intentional exception,
`load_bearing_walls_lintels`'s `rebar_a500_d10_unit_price_per_m`, is documented in its own `notes` as
feeding the calculator internally without ever becoming its own displayed line) — verified
programmatically across all 8 files in one pass.

## Fixes found and applied in this specific re-check pass (2026-07-11)

### Contract-schema fixes (pure YAML, no calculator touched)

- **`foundation_slab`**: `logistics_and_supply` and `consumables_tool_amortization` lines used
  `material_unit_price_key` pointing at `logistics_and_supply_amount`/
  `consumables_tool_amortization_amount`, both `supplier_inputs` keys, not `price_keys` entries —
  every other fixed-amount line in every other section correctly uses `fixed_amount_key` for this
  pattern. Moved both to `fixed_amount_key`. No calculator behavior involved; this field only
  documents intended adapter wiring.
- **`floor_slab_1`**: had no `checks:` block at all, unlike every other section. Added it
  (`expected_estimate_line_count: 24`, required review parameters, forbidden-input markers).

### Parser gaps found and fixed (`calculator_targets_compact.json` / `target_aliases_ru.yaml`)

- **`foundation_slab`**: three orphaned parser targets not referenced anywhere in the contract —
  `eps_100_edge_volume` (verified against `foundation_slab_calculator.py` that
  `eps100_required_volume_m3` is always computed geometrically, `thermal_insert_pieces *
  eps100_thickness_m * piece_height * piece_depth`, never taken as a direct spec volume),
  `sand_volume` and `geotextile_area` (both duplicated `earthworks`'s own real targets per their own
  notes, and `earthworks` already covers this data). Removed all three from both files.

### Calculator fixes (explicit user authorization each time — exception to the standing
never-touch-calculator-code rule for this pipeline stage)

**Silent legacy-mode defaults** — the risk flagged in an earlier review: several calculators had
`*_calc_method` fields that silently fell back to a legacy mode if the adapter forgot to set them
explicitly, instead of failing. In every case, validation (`if method not in {...}: raise
ValueError(...)`) already existed right after the `.get(key, <default>)` call — the fix was always
just removing the hardcoded default string, so a missing field now hits that existing validation
immediately instead of silently switching modes. 7 instances fixed across 3 files:

- `floor_slab_1_calculator.py`: `insulation.insulation_calc_method` (default was
  `"legacy_usv_geometry"`, whose branch computes hardcoded ЮСВ geometry — `d(19) * d(2) + (d(7) +
  d("13.2")) * d(2) + d("3.2") * d(2)` — instead of raising), `formwork_areas_calc_method` (default
  `"legacy_calculated_from_geometry"`), `rebar_calc_method` (default `"legacy_weight_parts"`), and a
  4th found only in this pass, `rates.formwork_rate_calc_method` (default
  `"legacy_supplier_quote_context"`).
- `floor_slab_2_calculator.py`: `formwork_area_calc_method` (default `"legacy_dimensions"`),
  `rebar_calc_method` (default `"legacy_weight_kg"`).
- `flat_roof_calculator.py`: `roof_geometry_calc_method` (default `"legacy_totals"`).

Fixture updates needed to preserve existing (deliberately legacy-mode) test coverage: 4 `floor_slab_1`
cases and 5 `floor_slab_2` cases had `formwork_areas_calc_method`/`rebar_calc_method` implicit; 2
`flat_roof` cases had `roof_geometry_calc_method` implicit. All had the field added explicitly with
its former default value. All affected calculators' full test suites re-run: 0 mismatches.

**Hardcoded `display_quantity` literals** — `foundation_slab_calculator.py` had three, one already
known and flagged-not-fixed (`formwork_timber`, `display_quantity=1.2`, from the original
`estimate_lines` build-out pass), two found only in this pass inside
`thermal_insert_estimate_lines()`'s legacy branch (`thermal_insert_mode != "standard_50_100"`, not
reachable in production): `eps50_penoplex_geo_material` (`14.44`) and `eps100_penoplex_geo_material`
(`0.56`). `display_quantity` never feeds `material_total`/`work_total`/`line_total` in this calculator
(confirmed directly in `calculate_line()`), so this was cosmetic-only. All three replaced with
`_round_decimal(quantity, "0.01")`, matching the pattern already used by every production-mode line in
the same function. `formwork_timber`'s real value moved from the hardcoded `1.2` to the correctly
computed `1.22`; `cases/test_foundation_slab/expected.json` and
`cases/test_foundation_slab_formwork_spec_area/expected.json` updated accordingly. All 6
`foundation_slab_calculator` cases pass 0 mismatches.

## Known, deliberately-not-fixed items (recorded, not risks needing action now)

- **Correction, 2026-07-11**: this report previously flagged
  `experiments/floor_slab_1_calculator/cases/test_floor_slab_1_live_prices/` as having an open,
  unresolved drift between the committed snapshot and the current `price_registry`
  (`unit_price_source` moving from `fallback_input` to `price_registry`). That was stale — the drift
  was already found and committed in `6d081a2` (the `floor_slab_1` legacy-default fix, whose commit
  message already notes it as "unrelated pre-existing drift... not part of this fix's logic").
  Re-verified just now: re-running `test_floor_slab_1_live_prices` produces a byte-identical result to
  what's committed, zero diff. Nothing open here.
- `floor_slab_1_calculator.py`'s nested dict-of-dicts input shape (unique among all 8 calculators) —
  recorded 2026-07-10, not acted on, candidate for a future dedicated flattening pass.
- The adapter layer (`review normalized_review.json` → per-section calculator input) does not exist
  yet anywhere in the repo. Every section's `calculator_input_mapping` still describes intended
  behavior only. This remains the single largest remaining gap before any of this can run end to end,
  and per earlier discussion, the adapter must fail loudly if a production `*_calc_method` is not
  explicitly set — never fall through to a calculator-side default, even now that the silent
  legacy-default fixes above make that fallback safer than before.

## What's still open after this pass

1. Build the adapter layer per section (`normalized_review.json` → calculator `input_data`).
2. Run a real chat-extraction JSON through the full pipeline for every section except
   `foundation_slab` (which already had this pass) — this was the next planned step before this
   re-check was requested, still pending.
