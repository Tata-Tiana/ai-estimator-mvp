# Step 16 — Waterproofing: Contract vs Parser Target Cross-Check

## Scope

Cost-basis ("себестоимость") only. This checks the waterproofing contract and chat-extraction
targets against `experiments/waterproofing_calculator/waterproofing_calculator.py`, which is the
ground truth for production input names. No real project quantities, page numbers, filenames, or old
fixture totals are recorded here.

## Calculator Ground Truth

Production mode is:

```text
waterproofing_area_calc_method = spec_area
```

The calculator requires exactly two project quantities from the PDF/review layer:

```text
waterproofing_area_m2
eps100_wall_volume_m3
```

Legacy fields stay out of production extraction:

```text
slab_formwork_perimeter_m
slab_edge_height_m
non_insulated_edge_lengths_m
```

Those legacy fields are still supported by the calculator for old locked cases, but they are not
production parser targets.

## Contract Check

`sections/waterproofing/section_contract.yaml` already matches the calculator:

- `review_parameters.waterproofing_area_m2`
  - `target_code: waterproofing_area_m2`
  - `calculator_input_path: waterproofing_area_m2`
- `review_parameters.eps100_wall_volume_m3`
  - `target_code: eps100_wall_volume_m3`
  - `calculator_input_path: eps100_wall_volume_m3`

No contract rename is needed.

## Calculator Display-Quantity Risk

One calculator-level issue was found outside parser/schema alignment:

```text
eps100_wall_penoplex_geo_material -> display_quantity=1.94
```

The calculator always calculated the real EPS100 order volume correctly in `quantity`
(`eps100_wall_order_volume_m3`); `display_quantity` is a separate, cosmetic-only field (verified: it
never feeds `material_total`/`work_total`/`line_total`, only appears in the exported line dict). The
literal `1.94` was not an unrelated leaked number — it is exactly `round(1.9432, 2)`, the real
production test case's own order volume rounded to 2 decimals. So the *value* was correct for this
one fixture; the *risk* was that it was frozen as a hardcoded literal instead of computed, so a
different project's EPS100 volume would still have displayed `1.94` regardless of the real number.

**Fix applied 2026-07-09** (calculator code change, explicitly requested and reviewed — this is the
one exception to the "never touch calculator code" rule for this stage, called out here on purpose so
it isn't missed on a later read):

`experiments/waterproofing_calculator/waterproofing_calculator.py`, the
`eps100_wall_penoplex_geo_material` estimate line — changed

```python
display_quantity=1.94,
```

to

```python
display_quantity=_round_decimal(
    waterproofing["eps100_wall_order_volume_m3"], "0.01"
),
```

matching the same live-rounding pattern already used for `display_quantity` elsewhere in the codebase
(e.g. `foundation_slab_calculator.py`'s EPS50 order volume rounding), instead of inventing a new
convention.

**Result**: all 3 existing test cases (`test_waterproofing_spec_area`,
`test_waterproofing_foundation_slab`, `test_waterproofing_foundation_slab_live_prices`) still pass
with identical output — `display_quantity` still resolves to `1.94` for the current fixture, because
`round(1.9432, 2) == 1.94`, but it is now computed from the real `eps100_wall_order_volume_m3` on every
run, so a future project with a different EPS100 volume will display its own correct rounded number
instead of the frozen `1.94`. No other field changed. `material_total`/`work_total`/`line_total` were
unaffected in all three cases (they were never derived from `display_quantity` to begin with).

## Parser-Side Fixes Made

The parser target list previously had only the waterproofing EPS value under:

```text
eps_100_edge_volume
```

That name is valid as a foundation-slab diagnostic/source concept, but it is not the production input
name for the waterproofing calculator. Per the Naming Alignment Rule in `HANDOFF.md`, the parser-side
files were aligned to the calculator instead of adding a bridge in the contract:

- `calculator_targets_compact.json`
  - added `waterproofing_area_m2`;
  - renamed the waterproofing EPS target to `eps100_wall_volume_m3`.
- `target_aliases_ru.yaml`
  - added `waterproofing_area_m2`;
  - renamed the waterproofing EPS alias key to `eps100_wall_volume_m3`.
- `claude_estimate_extraction_prompt.md`
  - added the rule that `waterproofing_area_m2` may reuse the foundation slab side formwork area.

The foundation-slab target `eps_100_edge_volume` was intentionally not removed: it belongs to the
foundation-slab extraction namespace and has its own finding in `step_13`.

## Allowed Shared Source Rule

If the PDF has no separate waterproofing-area row, the chat extraction may use the same raw PDF row
as the foundation slab side formwork area:

```text
waterproofing.waterproofing_area_m2 = foundation_slab.slab_side_formwork_area
```

The output should keep the same source evidence and set `needs_review: true`, with a note that the
waterproofing area was accepted from the side formwork area by Elena's method.

## Formula Context

The parser must extract only project quantities. It must not calculate these:

```text
primer_units = ceil(waterproofing_area_m2 * primer_consumption_l_per_m2 / primer_canister_volume_l)
mastic_units = ceil(waterproofing_area_m2 * mastic_consumption_kg_per_m2_per_layer * mastic_layers / mastic_bucket_weight_kg)
eps100_wall_insulation_area_m2 = eps100_wall_volume_m3 / eps100_wall_thickness_m
eps100_wall_order_volume_m3 = ceil((eps100_wall_volume_m3 * eps_waste_coeff) / eps100_pack_volume_m3) * eps100_pack_volume_m3
```

Those are calculator/formula-ready responsibilities. Consumption rates, bucket/can sizes, EPS
thickness, pack volume, waste coefficient, logistics coefficient, and consumables coefficient remain
`DEFAULT` / catalog / business settings, not PDF extraction targets.

## Checks

- [x] Calculator production inputs verified.
- [x] Contract names match calculator input names.
- [x] Parser-side target for waterproofing EPS matches `eps100_wall_volume_m3`.
- [x] `waterproofing_area_m2` added to parser targets and aliases.
- [x] Shared-source rule documented for side formwork area -> waterproofing area.
- [x] No calculator code changed.
- [x] No project-specific quantities or page references added.
- [x] `display_quantity=1.94` fixed 2026-07-09 — now computed live from `eps100_wall_order_volume_m3`
      instead of hardcoded; see "Calculator Display-Quantity Risk" above for the exact change and test
      results. This was a deliberate, explicitly requested calculator-code edit, not a parser/contract
      fix.
