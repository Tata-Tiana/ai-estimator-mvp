# Step 18 — Load-Bearing Walls and Lintels: Instruction Check

## Scope

This check applies the same logic used for the foundation slab status note:

```text
section_contract.yaml = section passport
calculator = ground truth for input names and estimate rows
parser/schema/aliases/prompt = extraction layer that must follow the contract
catalogs = shared production layer for defaults and estimate-line registry
```

No project-specific quantities, page numbers, filenames, or USV-only values are recorded here.

## What Is Already Aligned

The section has a contract:

```text
experiments/full_estimate_review_pipeline/sections/load_bearing_walls_lintels/section_contract.yaml
```

The contract points to the production calculator:

```text
experiments/load_bearing_walls_lintels_calculator/load_bearing_walls_lintels_calculator.py
```

The parser-side production targets are aligned with the contract for the current extraction layer:

```text
floors_count
cutoff_waterproofing_load_bearing_walls_area
main_wall_gas_block_400_spec_volume
main_wall_gas_block_250_spec_volume
lintel_total_length
lintel_concrete_volume
floor_2_masonry_volume
parapet_masonry_volume
vent_chimney_gas_block_150_volume
main_wall_rebar_items
lintel_rebar_items
lintel_items
```

`calculator_targets_compact.json`, `target_aliases_ru.yaml`, and
`claude_extraction_output_schema.json` agree on these target codes.

The repeated-row shapes are aligned:

```text
main_wall_rebar_items:
  floor
  component
  code
  name
  steel_class
  diameter_mm
  spec_length_m
  kg_per_meter

lintel_rebar_items:
  floor
  component
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

The prompt explicitly forbids using the old summary target
`masonry_rebar_a500_d10_weight` for production extraction. Wall reinforcement must be extracted
row-by-row into `main_wall_rebar_items`; lintel reinforcement must be extracted row-by-row into
`lintel_rebar_items`.

## What The Calculator Still Needs Outside PDF Extraction

The calculator has required non-PDF inputs. These must come from defaults, packaging catalogs,
price registry, supplier/manual input, or business settings, not from GPT/Claude:

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

This is a catalog/adapter task. The extraction layer should fail loudly or mark the row as
default/manual-required if the value is missing.

## Important Gap Found

The contract is not yet a full estimate-line passport for the walls calculator.

Current contract:

```text
review_parameters: 12
price_keys: 24
defaults: 24
supplier_inputs: 5
estimate_lines: 7
```

The calculator can currently return 35 distinct estimate line codes. The following calculator lines
are not yet described in `section_contract.yaml`:

```text
main_wall_rebar_a500_d10
scaffolding_timber_material
main_gas_block_d400_600x400x250_material
main_gas_block_d500_600x250x250_material
main_gas_block_adhesive
sand_concrete_m300_first_row
u_block_lintel_cutting
main_wall_chasing_for_d10_reinforcement
gas_blocks_and_mix_delivery
gas_blocks_unloading_manipulator
main_walls_blocks_crane_moving_25t
lintel_rebar_frame_assembly
lintel_concrete_delivery
manual_concrete_lifting
parapet_and_upper_level_masonry_work
parapet_and_upper_level_gas_block_d400_material
floor_2_gas_block_d400_material
floor_2_masonry_glue
parapet_masonry_work
parapet_gas_block_d400_material
vent_chimney_gas_block_d500_600x150x250_material
parapet_upper_level_adhesive
parapet_blocks_crane_moving
parapet_and_second_light_chasing_for_d10_reinforcement
parapet_and_second_light_rebar_a500_d10
walls_consumables_tool_amortization
construction_waste_removal
walls_technical_supervision
```

This is not a parser/schema problem. It means the section passport still needs the same full
estimate-line cataloging that was started for earthworks.

## Shared Catalog Status

The shared catalogs currently contain earthworks only:

```text
experiments/full_estimate_review_pipeline/catalogs/defaults_catalog.yaml
experiments/full_estimate_review_pipeline/catalogs/estimate_line_catalog.yaml
```

Before the walls adapter is considered production-ready, these catalogs need a
`load_bearing_walls_lintels` section with:

- non-PDF defaults and packaging values;
- manual/supplier fields;
- all estimate lines the calculator may output;
- zero/structural lines marked as such;
- price keys separated from formula defaults.

## Checks Run

- [x] Read the section instruction in `sections/load_bearing_walls_lintels/`.
- [x] Applied the foundation-slab style status checklist from the attached note.
- [x] Compared contract parser target codes with `calculator_targets_compact.json`.
- [x] Confirmed all active wall/lintel parser target codes have aliases.
- [x] Confirmed schema shapes for `main_wall_rebar_items`, `lintel_rebar_items`, and `lintel_items`.
- [x] Confirmed legacy geometry/summary targets are not active parser targets.
- [x] Validated JSON/YAML syntax for touched extraction and contract files.
- [x] Ran Python compile check for extraction helper scripts.
- [x] Confirmed `git diff --check` is clean.
- [ ] Expand the walls contract / shared estimate-line catalog to cover all calculator result lines.
- [ ] Add walls defaults to the shared defaults catalog.
- [ ] Build the adapter: review workbook / normalized review JSON -> calculator input.
