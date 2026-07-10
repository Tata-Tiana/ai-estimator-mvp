# Step 17 — Load-Bearing Walls and Lintels: Contract vs Parser Target Cross-Check

## Scope

Cost-basis ("себестоимость") only. This checks
`sections/load_bearing_walls_lintels/section_contract.yaml` and chat-extraction files against
`experiments/load_bearing_walls_lintels_calculator/load_bearing_walls_lintels_calculator.py`, which
is the ground truth for production input names. No real project quantities, page numbers, filenames,
or old fixture totals are recorded here.

## Calculator Ground Truth

The production modes used by the section contract are:

```text
cutoff_waterproofing_calc_method = spec_area
lintel_length_calc_method = spec_total_length
lintel_concrete_calc_method = spec_volume
main_wall_rebar_calc_method = spec_length_items
lintel_rebar_calc_method = spec_length_items
upper_floor_calc_method = floor_2_spec_volume
parapet_calc_method = flat_roof_spec_volume
vent_chimney_cladding_calc_method = flat_roof_spec_volume
vent_chimney_geometry_calc_method = spec_volume_thickness
```

The production PDF/review quantities are:

```text
floors_count
cutoff_waterproofing_load_bearing_walls_area_m2
main_wall_gas_block_400_spec_volume_m3
main_wall_gas_block_250_spec_volume_m3
lintel_total_length_m
lintel_concrete_spec_volume_m3
floor_2_masonry_volume_m3
parapet_masonry_volume_m3
vent_chimney_gas_block_spec_volume_m3
main_wall_rebar_items
lintel_rebar_items
lintel_items
```

`lintel_items` is diagnostic/review detail: it preserves the mark-by-mark lintel table. The calculator
production scalar is `lintel_total_length_m`.

## Parser-Side Fixes Made

`calculator_targets_compact.json` was aligned from legacy names to production target codes:

- added `floors_count`;
- added `cutoff_waterproofing_load_bearing_walls_area`;
- renamed wall block targets to `main_wall_gas_block_400_spec_volume` and
  `main_wall_gas_block_250_spec_volume`;
- added `lintel_total_length`;
- added `floor_2_masonry_volume`;
- renamed the 150 mm wall/vent block target to `vent_chimney_gas_block_150_volume`;
- added repeated group `main_wall_rebar_items`;
- changed `lintel_rebar_items` from legacy weight rows to production spec-length rows;
- expanded `lintel_items` with `mark` and `total_length_m`;
- removed legacy wall-geometry targets from the active target list:
  `main_wall_external_length`, `main_wall_reinforcement_rows`,
  `main_wall_400_reinforcement_threads`, `main_wall_250_reinforcement_threads`.

`target_aliases_ru.yaml` was aligned to the same production target codes:

- added aliases for `floors_count`;
- added aliases for `cutoff_waterproofing_load_bearing_walls_area`;
- added aliases for `lintel_total_length`;
- added aliases for `floor_2_masonry_volume`;
- changed wall/lintel rebar aliases to production row fields:
  `spec_length_m`, `kg_per_meter`;
- removed active aliases for the old wall-geometry rebar targets.

`claude_extraction_output_schema.json` now describes:

```text
main_wall_rebar_items:
  floor
  component = load_bearing_walls
  code
  name
  steel_class
  diameter_mm
  spec_length_m
  kg_per_meter

lintel_rebar_items:
  floor
  component = lintels
  code
  name
  steel_class
  diameter_mm
  spec_length_m
  kg_per_meter

lintel_items:
  mark
  length_m
  count
  total_length_m
```

The prompt now explicitly says not to use the legacy summary target
`masonry_rebar_a500_d10_weight` for production extraction. Wall rebar goes into
`main_wall_rebar_items`; lintel rebar goes into `lintel_rebar_items`; lintel marks go into
`lintel_items`.

`build_review_workbook_preview.py` was updated so review preview mappings use production target
codes, not old bridge names.

## Contract Fix Made

The contract already matched the calculator conceptually, but one path was wrong:

```text
main_wall_rebar_items.calculator_input_path
```

It was corrected from:

```text
rebar_items
```

to:

```text
main_wall_rebar_items
```

The calculator itself was not changed.

## Legacy Fields Kept Out of Production Extraction

These calculator concepts are legacy/diagnostic for this production path and should not be active
chat extraction targets:

```text
main_wall_external_length
main_wall_reinforcement_rows
main_wall_400_reinforcement_threads
main_wall_250_reinforcement_threads
masonry_rebar_a500_d10_weight
```

The new production rebar path is row-based:

```text
main_wall_rebar_items -> component=load_bearing_walls
lintel_rebar_items -> component=lintels
```

The adapter must add non-PDF per-row data such as `rod_length_m` and `unit_price_per_m` from catalog
defaults / price registry. GPT/Claude should not invent those fields from the PDF.

## Defaults / Catalog Inputs Still Required

The calculator has required inputs that are not PDF project quantities. They are not parser targets
and must be supplied later by adapter/default catalog/price registry/manual review:

```text
gas_block_d400_pallet_volume_m3
gas_block_d500_250_pallet_volume_m3
adhesive_consumption_bag_per_m3
sand_concrete_consumption_kg_per_m2_per_10mm
sand_concrete_thickness_factor
gas_block_delivery_truck_capacity_m3
gas_block_d500_150_pallet_volume_m3
parapet_chasing_base_length_m
second_light_chasing_base_length_m
parapet_rebar_base_length_m
second_light_rebar_base_length_m
```

This is an adapter/defaults task, not an extraction task. The production pipeline must fail loudly
or show manual/default-required status if these are missing before calculator execution.

## Checks

- [x] Calculator production input names checked directly.
- [x] Contract production target codes compared with parser targets.
- [x] Missing scalar parser targets added.
- [x] Legacy wall-geometry targets removed from active extraction target list.
- [x] `main_wall_rebar_items` added as production repeated group.
- [x] `lintel_rebar_items` aligned to `spec_length_m` / `kg_per_meter`.
- [x] `lintel_items` expanded with `mark` and `total_length_m`.
- [x] Prompt updated to forbid production use of legacy `masonry_rebar_a500_d10_weight`.
- [x] Review preview aliases updated away from old bridge target names.
- [x] No calculator code changed.
- [x] No project-specific quantities or page references added.
- [x] Declare the adapter/defaults layer that fills required non-PDF calculator inputs — done
      2026-07-10 in `section_contract.yaml`'s `defaults`/`price_keys` (see the new section below).
      The `build_load_bearing_walls_lintels_input` adapter function itself is still not implemented
      anywhere in the repo; only the contract-level declaration exists so far.
- [ ] Run a real extraction JSON through the multi-section review workbook once the adapter/defaults
      layer exists.

## `estimate_lines` build-out and defaults/price_keys gap fix (2026-07-10)

`section_contract.yaml` previously declared only 7 of the calculator's 30 possible production
`estimate_lines` (23 always-present + up to 7 conditional when `floors_count = 2` and
`flat_roof_enabled` with positive parapet/vent volumes). Rebuilt the full list by reading
`load_bearing_walls_lintels_calculator.py` directly (`calculate_lines()`, `calculate_blocks()`,
`LoadBearingWallsLintelsInput` dataclass) end to end, not from the `catalogs/estimate_line_catalog.yaml`
draft alone (its own header's `calculator_estimate_line_count: 27` turned out to be stale — real max
is 30). All 23 missing lines added, including the two dynamic rebar-row lines
(`main_wall_rebar_items`, `lintel_rebar_items`, one estimate line generated per input row, any
diameter/class — same convention as `floor_slab_1`/`floor_slab_2`) and the two zero-priced control
rows (`main_wall_chasing_for_d10_reinforcement`, `lintel_rebar_frame_assembly`).

Also completed the 11-item adapter/defaults gap list from this report's earlier section above (all
now real `defaults`/`price_keys` entries with catalog-value sourcing, not invented numbers — every
numeric default was cross-checked against every input.json fixture under
`experiments/load_bearing_walls_lintels_calculator/cases/`, which agree on all of them), plus found 9
more required `LoadBearingWallsLintelsInput` fields with no dataclass default that the earlier pass's
scan had missed entirely: `rebar_a500_d10_kg_per_m`, `rebar_a500_d10_rod_length_m`,
`rebar_a500_d10_unit_price_per_m` (needed even in production because `calculate_blocks()`
unconditionally builds the parapet/second-light base-length rebar helper), and 6 legacy
wall-geometry fields (`main_wall_external_length_m`, `main_wall_internal_250_control_length_m`,
`main_wall_reinforcement_rows`, `main_wall_400_reinforcement_threads`,
`main_wall_250_reinforcement_threads`, `main_wall_reinforcement_overlap_coeff`) that are dead in
production `spec_length_items` mode but still required just to construct the dataclass. The four
legacy base-length fields and the six legacy geometry fields are documented as safe `0` placeholders
(neither group is in the calculator's `require_positive` list); the three `rebar_a500_d10_*` fields
got real catalog values (`0.617` kg/m, `11.7` m rod length — same numbers already used elsewhere in
this project for A500 Ø10) since two of them are in `require_positive`.

The contract also had no `auto_calculated:` or `checks:` sections at all before this pass — both
added, following the same structure already used by `foundation_slab`/`floor_slab_2`.

Two real bugs found and fixed purely at the contract-YAML level (no calculator code touched):
1. `lintel_concrete_b22_5_m300_material`'s formula multiplied `lintel_concrete_spec_volume_m3` by
   `concrete_waste_coeff` — verified against `calculate_lintel_concrete()` that production
   `spec_volume` mode never applies this coefficient (only the legacy `legacy_length_section` mode
   does). Fixed to reference the corrected `auto_calculated.lintel_concrete_order_volume_m3`.
2. `vent_chimney_gas_block_cladding_work`'s gate said "when flat_roof_enabled" but
   `calculate_blocks()` requires `flat_roof_enabled and vent_chimney_gas_block_spec_volume_m3 > 0`
   — fixed to match, and mirrored the same `> 0` condition onto the sibling
   `vent_chimney_gas_block_d500_600x150x250_material` line.

Verified programmatically after every edit: YAML parses, zero duplicate `estimate_lines` codes, zero
dangling `leaf_inputs` refs across `review_parameters`/`defaults`/`supplier_inputs`/`auto_calculated`/
`price_keys`, and every `estimate_lines[].prices.*_key` resolves to a real `price_keys` or
`supplier_inputs` entry. `rebar_a500_d10_unit_price_per_m` is intentionally the only unreferenced
`price_keys` entry — it feeds `calculate_blocks()` internally but never becomes its own displayed
`estimate_lines` row in production, as documented in that key's own `notes`.

## Future note (2026-07-09, non-blocking — nothing to do now)

`lintel_items` (mark-by-mark diagnostic breakdown: `mark`, `length_m`, `count`, `total_length_m`) is
correctly kept out of the calculator's production input path — only the scalar `lintel_total_length_m`
is used while `lintel_length_calc_method = spec_total_length`. Worth remembering for later: if that
mode is ever deliberately switched to `legacy_length_count_items`, these rows would feed
`LintelLength.from_dict()`, whose dataclass only declares `length_m`/`count` — the extra `mark`/
`total_length_m` keys would raise a `TypeError` on `**data` unpacking unless stripped first. Not
relevant today; just don't forget it if that mode switch ever happens. See the matching note on
`section_contract.yaml`'s `lintel_items` entry.
