# Step 3 — All New Sections Quantity Matrix

Status: completed draft

Goal: пройти 7 новых разделов без кода и выписать трассировку:

```text
estimate line -> quantity formula -> leaf inputs -> source class
```

This report is the bridge between the common `section_contract.yaml` format and real per-section contracts.
It answers three questions before we build any workbook:

- what must be extracted from project/PDF;
- what should stay as default/catalog/price/manual input;
- what the calculator must calculate by itself.

This is not a source of production values. Calculator cases and old result JSON files are used here only
to discover line codes and formulas. Per-section contracts must use source fields and formulas, never
old fixture quantities, prices, display quantities, totals, filenames, or expected Excel-match values.

## 1. Scope

Earthworks is excluded from this step because it is already documented as the reference section in
`reports/step_01_earthworks_reference.md`.

New sections covered here:

| Section | Calculator source | Representative line count checked |
|---|---|---:|
| `waterproofing` | `experiments/waterproofing_calculator/waterproofing_calculator.py` | 8 |
| `foundation_slab` | `experiments/foundation_slab_calculator/foundation_slab_calculator.py` | 30 |
| `floor_slab_1` | `experiments/floor_slab_1_calculator/floor_slab_1_calculator.py` | 28 |
| `floor_slab_2` | `experiments/floor_slab_2_calculator/calculator.py` | 26 |
| `flat_roof` | `experiments/flat_roof_calculator/calculator.py` | 31 |
| `schiedel_vent_channels` | `experiments/schiedel_vent_channels_calculator/calculator.py` | 9 |
| `load_bearing_walls_lintels` | `experiments/load_bearing_walls_lintels_calculator/load_bearing_walls_lintels_calculator.py` | 27 |

## 2. Source Classes

| Source class | Meaning for review workbook |
|---|---|
| `AUTO_PROJECT` | Extract from project/specification/PDF and show for human review. |
| `DETAIL_TABLE` | Extract as a table/list, not as one scalar row. |
| `DEFAULT` | Calculator/catalog assumption; do not ask from project unless overridden. |
| `AUTO_CALCULATED` | Derived by adapter/calculator/formula-ready. |
| `PRICE` | Price registry or reviewed price row. |
| `SUPPLIER_INPUT` | External supplier/Elena/manual quantity; reviewable, but not parsed as project geometry. |
| `MANUAL_REVIEW` | Human decision/override, usually not a parser target. |

## 3. Global Checks For This Step

- [x] No code was added or changed for calculators.
- [x] Matrix is based on calculator files, not on English target names only.
- [x] Every new section has at least one matrix block.
- [x] For every matrix block, quantity formula and source classes are stated.
- [x] Repeated dynamic rows are represented as line families with expansion rules.
- [x] Floor slab checks explicitly distinguish:
  - slab concrete vs beam concrete;
  - bottom EPS volume/work area vs edge EPS work length/material area;
  - under-slab/deck formwork area vs edge/beam formwork area;
  - rebar specification length in `мп`, not primary PDF weight.
- [x] Review workbook and final estimate workbook remain separate concepts.
- [x] Old fixture/result values are treated as audit evidence only.

Fail condition for the next step: do not build a review workbook row if this matrix says the value is
`DEFAULT`, `AUTO_CALCULATED`, or final estimate output only.
Also fail if a future contract copies any old fixture/result value as a production default.

## 4. Waterproofing

Primary project inputs:

- `waterproofing_area_m2` when `waterproofing_area_calc_method = spec_area` (`AUTO_PROJECT`);
- legacy control inputs `slab_formwork_perimeter_m`, `slab_edge_height_m`, `non_insulated_edge_lengths_m` (`AUTO_PROJECT`, control/legacy);
- `eps100_wall_volume_m3` (`AUTO_PROJECT`);
- `eps100_wall_thickness_m` (`DEFAULT`, normally 0.1);
- consumption, pack, coverage coefficients (`DEFAULT`);
- unit prices (`PRICE`);
- logistics/consumables coefficients (`DEFAULT` or business rule).

| Estimate line | Quantity formula | Leaf inputs | Source | Price |
|---|---|---|---|---|
| `waterproofing_bitumen_mastic_work` | `waterproofing_area_m2` | `waterproofing_area_m2` or legacy `perimeter * edge_height` | `AUTO_PROJECT` / legacy calculated | `bitumen_waterproofing_work_m2` |
| `bitumen_primer_aquamast_18l` | `ceil(waterproofing_area_m2 * primer_consumption_l_per_m2 / primer_canister_volume_l)` | area, primer consumption, canister volume | area `AUTO_PROJECT`; coeffs `DEFAULT` | `bitumen_primer_aquamast_18l_item` |
| `bitumen_mastic_aquamast_18kg` | `ceil(area * mastic_consumption_kg_per_m2_per_layer * mastic_layers / mastic_bucket_weight_kg)` | area, consumption, layers, bucket weight | area `AUTO_PROJECT`; coeffs `DEFAULT` | `bitumen_mastic_aquamast_18kg_item` |
| `eps100_wall_insulation_work` | `eps100_wall_volume_m3 / eps100_wall_thickness_m` | EPS wall volume, EPS thickness | volume `AUTO_PROJECT`; thickness `DEFAULT` | `eps_wall_insulation_work_m2` |
| `eps100_wall_penoplex_geo_material` | `ceil((eps_area * thickness * eps_waste_coeff) / eps100_pack_volume_m3) * eps100_pack_volume_m3` | EPS volume/thickness, waste coeff, pack volume | volume `AUTO_PROJECT`; coeff/pack `DEFAULT` | `eps_geo_100_m3` |
| `eps_glue_foam` | `max(glue_foam_min_units, ceil(eps_area / glue_foam_coverage_m2_per_can))` | EPS area, coverage, minimum units | EPS area `AUTO_CALCULATED`; coverage/min `DEFAULT` | `eps_foam_glue_can` |
| `waterproofing_logistics_and_supply` | `base_subtotal * waterproofing_logistics_coeff` | subtotal, coeff | `AUTO_CALCULATED` + `DEFAULT` | no direct price key |
| `waterproofing_consumables_tool_amortization` | `base_subtotal * waterproofing_consumables_coeff` | subtotal, coeff | `AUTO_CALCULATED` + `DEFAULT` | no direct price key |

Review workbook should ask for `waterproofing_area_m2` and `eps100_wall_volume_m3`; it should not ask for primer cans, mastic buckets, packs, glue cans, logistics amount, or consumables amount as project extraction targets.

## 5. Foundation Slab

Primary project inputs:

- `membrane_area_m2`;
- `slab_side_formwork_area_m2` in `formwork_calc_method = spec_area`;
- `eps50_under_slab_volume_m3`;
- thermal insert 50/100 lengths and material spec quantities in standard mode;
- `rebar_items[*].source_length_m` or `length_parts_m` in `rebar_calc_method = spec_length_m`;
- `concrete_project_volume_m3`;
- manual logistics/crane/pump/supervision amounts where calculator treats them as fixed/manual.

| Estimate line | Quantity formula | Leaf inputs | Source | Price |
|---|---|---|---|---|
| `planter_membrane_installation` | `membrane_area_m2` | membrane area | `AUTO_PROJECT` | `planter_membrane_installation_work_m2` |
| `planter_standard_material` | `ceil(membrane_area_m2 * membrane_overlap_coeff / membrane_roll_area_m2)` | membrane area, overlap, roll area | area `AUTO_PROJECT`; coeff/roll `DEFAULT` | `planter_standard_roll` |
| `planterband_material` | `membrane_rolls * planterband_per_membrane_roll` | membrane rolls, planterband per roll | `AUTO_CALCULATED` + `DEFAULT` | `planterband_item` |
| `formwork_installation` | `slab_side_formwork_area_m2` in spec mode; legacy `perimeter * edge_height` | side formwork area | `AUTO_PROJECT` | `timber_formwork_installation_work_m2` |
| `formwork_plywood` | `ceil(formwork_area_m2 * plywood_waste_coeff / sheet_area_m2)` | formwork area, sheet size, waste | area `AUTO_PROJECT`; sheet/waste `DEFAULT` | `plywood_1520x1520_18mm_sheet` |
| `formwork_timber` | `formwork_area_m2 * timber_thickness_m` | formwork area, timber thickness | area `AUTO_PROJECT`; thickness `DEFAULT` | `timber_m3` |
| `eps50_laying_under_slab` | `eps50_under_slab_volume_m3 / eps50_thickness_m` | EPS 50 volume, thickness | volume `AUTO_PROJECT`; thickness `DEFAULT` | `eps_laying_work_m2` |
| `thermal_insert_50_installation` | `thermal_insert_50_length_m` | 50 mm thermal insert length | `AUTO_PROJECT` | `thermal_insert_50_installation_work_m` |
| `thermal_insert_100_installation` | `thermal_insert_100_length_m` | 100 mm thermal insert length | `AUTO_PROJECT` | `thermal_insert_100_installation_work_m` |
| `eps50_penoplex_geo_material` | `ceil((eps50_under_slab_volume_m3 * eps_waste_coeff) / eps50_pack_volume_m3) * eps50_pack_volume_m3` | EPS 50 volume, waste, pack | volume `AUTO_PROJECT`; coeff/pack `DEFAULT` | `eps_geo_50_m3` |
| `thermal_insert_50_material` | `round_up(thermal_insert_50_material_spec_qty * waste_coeff, pack_multiple)` | 50 mm material spec qty, waste, pack multiple | spec qty `AUTO_PROJECT`; waste/pack `DEFAULT` | `thermal_insert_50_material_m3` |
| `thermal_insert_100_material` | `round_up(thermal_insert_100_material_spec_qty * waste_coeff, pack_multiple)` | 100 mm material spec qty, waste, pack multiple | spec qty `AUTO_PROJECT`; waste/pack `DEFAULT` | `thermal_insert_100_material_m3` |
| `rebar_crane_supply` | `rebar_crane_shifts` | crane shifts | `MANUAL_REVIEW` | `crane_shift` |
| `rebar_frame_assembly` | `sum(rebar order_length_m)` | rebar items | `AUTO_CALCULATED` control line | no direct price key |
| `rebar_*` | `ceil((spec_length_m * rebar_waste_coeff) / rod_length_m) * rod_length_m` | rebar class, diameter, spec length, kg/m, rod length | spec length `AUTO_PROJECT`; kg/m/rod `DEFAULT` catalog | `rebar_<class>_d<diameter>_m` |
| `rebar_metal_delivery` | `rebar_metal_delivery_trucks` | delivery trucks | `MANUAL_REVIEW` now; suggested trucks calculated for control | `metal_delivery_truck` |
| `foundation_slab_concreting_work` | `concrete_project_volume_m3` | project concrete volume | `AUTO_PROJECT` | `concrete_placing_work_m3` |
| `concrete_b22_5_m300_material` | `ceil_to_step(concrete_project_volume_m3 * concrete_waste_coeff, concrete_round_step_m3)` | concrete volume, waste, round step | volume `AUTO_PROJECT`; waste/step `DEFAULT` | `concrete_b22_5_m3` |
| `concrete_delivery` | `ceil(concrete_order_volume_m3 / concrete_mixer_volume_m3)` | ordered concrete volume, mixer volume | `AUTO_CALCULATED` + `DEFAULT` | `concrete_delivery_trip` |
| `concrete_pump_32m` | `concrete_pump_shifts` | pump shifts | `MANUAL_REVIEW` | `concrete_pump_32m_shift` |
| `formwork_dismantling` | `formwork_area_m2` | side formwork area | `AUTO_PROJECT` | `formwork_dismantling_work_m2` |
| `logistics_and_supply` | fixed amount | amount | `MANUAL_REVIEW` / business input | no direct price key |
| `consumables_tool_amortization` | fixed amount | amount | `MANUAL_REVIEW` / business input | no direct price key |
| `technical_supervision` | `1` | fixed amount | `MANUAL_REVIEW` | `technical_supervision_fixed` |
| `procurement_warehouse_costs_excel_structure` | `1` | none | `AUTO_CALCULATED` zero structure | none |
| `overhead_general_business_costs_excel_structure` | `1` | none | `AUTO_CALCULATED` zero structure | none |
| `estimated_profit_excel_structure` | `1` | none | `AUTO_CALCULATED` zero structure | none |

Do not confuse `eps50_under_slab_volume_m3` with EPS laying area: volume is project input, area is calculated for work.

## 6. Floor Slab 1

Primary project inputs:

- formwork areas: `main_formwork_area_m2`, `edge_formwork_area_m2`, `beams_formwork_area_m2`;
- concrete: slab and beam quantities through spec/concrete block;
- rebar: `rebar_items[*].spec_length_m` by steel class/diameter, floor/component;
- insulation production inputs: edge work length, bottom work area, EPS material area/volume;
- beam detail table for beam EPS work/material controls;
- manual lines for crane/pump/supervision when fixed.

| Estimate line | Quantity formula | Leaf inputs | Source | Price |
|---|---|---|---|---|
| `slab_formwork_installation_control` | `main_formwork_area_m2` | main formwork area | `AUTO_PROJECT` control | none |
| `formwork_set_rental_material` | `main_formwork_area_m2` | main formwork area, formwork rate | area `AUTO_PROJECT`; rate `SUPPLIER_INPUT`/`PRICE` | `formwork_rental_m2` |
| `formwork_delivery_return_manipulator` | `2 if main_formwork_area_m2 <= 180 else 4`, or manual override | main formwork area | `AUTO_CALCULATED`; override `MANUAL_REVIEW` | `formwork_delivery_truck` |
| `formwork_rebar_crane_supply` | `formwork_rebar_crane_shifts` | crane shifts | `MANUAL_REVIEW` | `crane_shift` |
| `formwork_consumables` | `main_formwork_area_m2 * formwork_consumables_rate_per_m2` | main formwork area, rate | `AUTO_CALCULATED` + `DEFAULT`/`PRICE` | `formwork_consumables_m2` |
| `edge_beam_formwork_installation_control` | `edge_formwork_area_m2 + beams_formwork_area_m2` | edge and beam formwork areas | `AUTO_PROJECT` control | none |
| `plywood_fk_18mm_for_edges_and_non_multiple_places` | `ceil(edge_and_beam_formwork_area / plywood_sheet_area)` | edge/beam formwork area, sheet area | area `AUTO_PROJECT`; sheet `DEFAULT` | `plywood_1520x1520_18mm_sheet` |
| `formwork_timber_gost` | `edge_and_beam_formwork_area * timber_thickness_m` | edge/beam formwork area, timber thickness | area `AUTO_PROJECT`; thickness `DEFAULT` | `timber_m3` |
| `floor_slab_rebar_frame_assembly_control` | `sum(rebar order_length_m)` | rebar items | `AUTO_CALCULATED` control | none |
| `rebar_*` | `ceil(spec_length_m * waste_coeff / rod_length_m) * rod_length_m` | steel class, diameter, spec length, catalog kg/m, rod length | spec length `AUTO_PROJECT`; catalog `DEFAULT` | `rebar_<class>_d<diameter>_m` |
| `floor_slab_concreting_work` | `slab_concrete_volume` | slab concrete volume | `AUTO_PROJECT` or calculated from total minus beams depending mode | `concrete_placing_work_m3` |
| `beam_concreting_work` | `beams_concrete_volume` | beam concrete volume/detail table | `AUTO_PROJECT` / `DETAIL_TABLE` | `beam_concrete_placing_work_m3` |
| `concrete_b22_5_m300_material` | `ceil(total_concrete_volume * concrete_waste_coeff)` | slab concrete + beam concrete, waste | volumes `AUTO_PROJECT`; waste `DEFAULT` | `concrete_b22_5_m3` |
| `concrete_delivery` | `ceil(concrete_volume_with_waste / mixer_capacity_m3)` | concrete volume, mixer capacity | `AUTO_CALCULATED` + `DEFAULT` | `concrete_delivery_trip` |
| `concrete_pump_32m` | `concrete_pump_shifts` | pump shifts | `MANUAL_REVIEW` | `concrete_pump_32m_shift` |
| `formwork_dismantling_zero_internal` | `main_formwork_area_m2` | main formwork area | `AUTO_PROJECT` zero/internal | none |
| `edge_beam_insulation_work` | `slab_outer_edge_eps_work_length_m + sum(beam.length_m * beam.count)` | edge length, beam rows | `AUTO_PROJECT` + `DETAIL_TABLE` | `edge_insulation_work_m` |
| `bottom_slab_insulation_work` | `bottom_slab_eps_work_area_m2` | bottom EPS work area | `AUTO_PROJECT` | `eps_bottom_slab_insulation_work_m2` |
| `eps_penoplex_osnova_100mm` | `ceil(total_eps_volume_from_spec_m3 * eps_waste_coeff / eps_pack_volume_m3) * eps_pack_volume_m3` | EPS spec volume, waste, pack | volume `AUTO_PROJECT`; waste/pack `DEFAULT` | `eps_penoplex_osnova_100_m3` |
| `eps_glue_foam` | `ceil((edge_and_beam_eps_material_area_m2 + bottom_slab_eps_work_area_m2) / foam_coverage_m2_per_can)` | EPS material/work areas, foam coverage | areas `AUTO_PROJECT`/`AUTO_CALCULATED`; coverage `DEFAULT` | `eps_foam_glue_can` |
| `logistics_and_supply` | `base_subtotal * logistics_and_supply_percent` | subtotal, percent | `AUTO_CALCULATED` + `DEFAULT` | none |
| `consumables_tool_depreciation` | `base_subtotal * consumables_and_tool_percent` | subtotal, percent | `AUTO_CALCULATED` + `DEFAULT` | none |
| `technical_supervision` | `1` fixed amount | fixed amount | `MANUAL_REVIEW` | `technical_supervision_fixed` |

Critical distinction: `floor_slab_concreting_work` and `beam_concreting_work` are separate estimate lines and must not be merged into one "total concrete" review row.

## 7. Floor Slab 2

Primary project inputs:

- `main_formwork_area_m2`, `edge_formwork_area_m2`, `beams_formwork_area_m2`;
- `slab_edge_perimeter_m`, `edge_insulation_height_m`;
- `rebar_items[*].steel_class`, `diameter_mm`, `spec_length_m`;
- `concrete_placing_volume`;
- EPS edge volume/work values as defined by calculator input;
- fixed/manual crane/pump where needed.

| Estimate line | Quantity formula | Leaf inputs | Source | Price |
|---|---|---|---|---|
| `floor_slab_2_formwork_installation_control` | `main_formwork_area_m2` | main formwork area | `AUTO_PROJECT` control | none |
| `formwork_rental_set` | `main_formwork_area_m2` | main formwork area, formwork rate | area `AUTO_PROJECT`; rate `PRICE`/`SUPPLIER_INPUT` | `formwork_rental_m2` |
| `formwork_delivery_manipulator` | `2 if main_formwork_area_m2 <= 180 else 4`, or override | main formwork area | `AUTO_CALCULATED` / `MANUAL_REVIEW` | `formwork_delivery_truck` |
| `crane_supply_formwork_rebar` | `crane_shifts` | crane shifts | `MANUAL_REVIEW` | `crane_shift` |
| `formwork_consumables` | `main_formwork_area_m2 * formwork_consumables_rate_per_m2` | formwork area, rate | `AUTO_CALCULATED` + `DEFAULT` | `formwork_consumables_m2` |
| `edge_formwork_installation_control` | `edge_formwork_area_m2 + beams_formwork_area_m2` | edge/beam formwork areas | `AUTO_PROJECT` control | none |
| `plywood_for_edges` | `ceil(edge_and_beam_formwork_area / plywood sheet logic)` | edge/beam formwork area, sheet defaults | area `AUTO_PROJECT`; sheet `DEFAULT` | `plywood_1520x1520_18mm_sheet` |
| `timber_for_formwork` | `edge_and_beam_formwork_area * timber_thickness_m` | edge/beam formwork area, thickness | area `AUTO_PROJECT`; thickness `DEFAULT` | `timber_m3` |
| `rebar_frame_assembly_control` | `sum(rebar order_length_m)` | rebar items | `AUTO_CALCULATED` control | none |
| `rebar_a500_d16`, `rebar_a500_d12`, `rebar_a500_d10` | `ceil(spec_length_m * waste_coeff / rod_length_m) * rod_length_m` | class, diameter, spec length | spec length `AUTO_PROJECT`; catalog `DEFAULT` | corresponding rebar price |
| `concrete_placing_work` | `concrete_placing_volume` | concrete volume | `AUTO_PROJECT` | `concrete_placing_work_m3` |
| `concrete_b22_5_m300_material` | `ceil_to_step(concrete_placing_volume * waste_coeff, step)` | concrete volume, waste/rounding | volume `AUTO_PROJECT`; coeff `DEFAULT` | `concrete_b22_5_m3` |
| `concrete_delivery` | `ceil(concrete_order_volume / mixer_capacity_m3)` | ordered concrete, mixer capacity | `AUTO_CALCULATED` + `DEFAULT` | `concrete_delivery_trip` |
| `concrete_pump_32m` | `concrete_pump_shifts` | pump shifts | `MANUAL_REVIEW` | `concrete_pump_32m_shift` |
| `formwork_dismantling_control` | `main_formwork_area_m2` | main formwork area | `AUTO_PROJECT` zero/control | none |
| `edge_insulation_work` | `slab_edge_perimeter_m` | insulated edge perimeter | `AUTO_PROJECT` | `edge_insulation_work_m` |
| `eps100_penoplex_material` | EPS order volume from edge insulation area/height/pack logic | edge geometry/EPS volume, pack | project geometry `AUTO_PROJECT`; pack `DEFAULT` | `eps_penoplex_osnova_100_m3` |
| `eps_foam_glue` | `ceil(EPS area / foam coverage)` | EPS area, coverage | area `AUTO_CALCULATED`; coverage `DEFAULT` | `eps_foam_glue_can` |
| `logistics_and_supply` | `direct_cost_base * logistics_rate` | subtotal, rate | `AUTO_CALCULATED` + `DEFAULT` | none |
| `consumables_tool_depreciation` | `direct_cost_base * consumables_rate` | subtotal, rate | `AUTO_CALCULATED` + `DEFAULT` | none |
| `technical_supervision`, `procurement_storage_costs`, `overhead_general_business_costs`, `estimated_profit` | `1` | none/fixed structure | `AUTO_CALCULATED` zero structure | none |

Critical distinction: `main_formwork_area_m2` is the deck/under-slab formwork area; `edge_formwork_area_m2` is not the same value. EPS material volume in `м3` is not formwork area in `м2`.

## 8. Flat Roof

Primary project inputs:

- roof geometry totals or detailed geometry: roof level areas, parapet lengths, vent wall abutment lengths;
- supplier/Technonikol required volumes for slope insulation plates;
- counts for aerators, drains, wall holes, crane shifts, waste trucks;
- manual gray totals for consumables/logistics/procurement in current calculator scope.

| Estimate line / family | Quantity formula | Leaf inputs | Source | Price |
|---|---|---|---|---|
| `roof_base_preparation_control` | `roof_area` | roof area from totals or detailed levels | `AUTO_PROJECT` control | none |
| `vapor_barrier_installation` | `roof_area` | roof area | `AUTO_PROJECT` | work rate input |
| `vapor_barrier_film_technonikol_120mk` | `ceil(roof_area * overlap_coeff / roll_area) * roll_area` | roof area, overlap, roll area | area `AUTO_PROJECT`; coeff/roll `DEFAULT` | `roof_vapor_barrier_film_technonikol_120mk_m2` |
| `eps_roof_insulation_installation` | `roof_area` | roof area | `AUTO_PROJECT` | work rate input |
| `eps100_technonikol_carbon_eco` | `ceil(roof_area * eps_main_thickness_m * waste_coeff / pack_volume) * pack_volume` | roof area, thickness, waste, pack | area `AUTO_PROJECT`; coeffs `DEFAULT` | `roof_eps100_technonikol_carbon_eco_m3` |
| `eps50_technonikol_carbon_eco` and slope plate rows `A/B/J/K` | `ceil(supplier_required_volume_m3 / pack_volume_m3) * pack_volume_m3` | supplier required volume, pack volume | `SUPPLIER_INPUT` + `DEFAULT` | corresponding roof EPS price |
| `geotextile_prof_300_flat` | `ceil(roof_area * geotextile_flat_coeff / roll_area) * roll_area` | roof area, coeff, roll area | area `AUTO_PROJECT`; coeff/roll `DEFAULT` | `roof_geotextile_technonikol_prof_300_m2` |
| `geotextile_prof_150_parapet` | `ceil(parapet_and_abutment_length * coeff / roll_area) * roll_area` | parapet/abutment length, coeff, roll area | length `AUTO_PROJECT`; coeff/roll `DEFAULT` | `roof_geotextile_technonikol_prof_150_m2` |
| `pvc_membrane_flat_installation` | `roof_area` | roof area | `AUTO_PROJECT` | work rate input |
| `pvc_membrane_abutment_installation` | `parapet_and_abutment_length` | parapet/abutment length | `AUTO_PROJECT` | work rate input |
| `vent_shaft_abutment_installation` | `vent_shaft_abutment_count` | count | `AUTO_PROJECT` / `MANUAL_REVIEW` | work rate input |
| `aluminum_pressure_rail_3m`, `aluminum_edge_rail_3m` | `ceil(parapet_and_abutment_length / rail_piece_length_m) * rail_piece_length_m` | parapet/abutment length, rail length | length `AUTO_PROJECT`; piece length `DEFAULT` | rail price |
| `pvc_membrane_logicroof_vrp_1_5mm_gray` | `ceil((roof_area * flat_coeff + parapet_length * parapet_coeff) / roll_area)` | roof area, parapet length, coeffs, roll size | geometry `AUTO_PROJECT`; coeffs `DEFAULT` | `roof_pvc_membrane_logicroof_vrp_1_5mm_gray_roll` |
| `roof_pvc_aerator_75x375` | `roof_aerators_count` | aerator count | `AUTO_PROJECT` / `MANUAL_REVIEW` | `roof_pvc_aerator_75x375_item` |
| `parapet_roof_drain_installation` | `parapet_roof_drains_count` | parapet drain count | `AUTO_PROJECT` / `MANUAL_REVIEW` | `roof_parapet_drain_item` |
| `gas_block_wall_hole_drilling` | `gas_block_wall_holes_count` | holes count | `MANUAL_REVIEW` | none |
| `internal_roof_drain_with_heating` | `internal_roof_drains_count` | internal drain count | `AUTO_PROJECT` / `MANUAL_REVIEW` | `roof_internal_drain_with_heating_item` |
| `internal_drain_pvc_110mm` | `internal_roof_drains_count * internal_drain_height_per_drain_m` | count, height per drain | count `AUTO_PROJECT`; height `AUTO_PROJECT`/`DEFAULT` | `roof_internal_drain_pvc_110mm_m` |
| `roof_crane_lifting` | `roof_crane_lifting_shifts` | crane shifts | `MANUAL_REVIEW` | `roof_crane_lifting_shift` |
| `roof_consumables_tool_depreciation` | provided raw total | raw total | `MANUAL_REVIEW` pending formula | none |
| `roof_waste_removal` | `roof_waste_removal_trucks` | trucks | `MANUAL_REVIEW` | none |
| `roof_logistics_and_supply` | provided raw total | raw total | `MANUAL_REVIEW` pending formula | none |
| `technical_supervision`, `procurement_storage` | provided fixed totals | fixed totals | `MANUAL_REVIEW` | none |
| `overhead_zero`, `profit_zero` | `1` | none | `AUTO_CALCULATED` zero structure | none |

Flat roof warning: slope EPS plate volumes are supplier inputs, not geometry-derived values.

## 9. Schiedel Vent Channels

Primary project/supplier inputs:

- `schiedel_masonry_total_length_m`;
- Schiedel 2x/3x material counts from specification/Elena table;
- delivery trips;
- prices and consumables rate.

| Estimate line | Quantity formula | Leaf inputs | Source | Price |
|---|---|---|---|---|
| `schiedel_masonry_work` | `schiedel_masonry_total_length_m` | masonry total length | `AUTO_PROJECT` / `SUPPLIER_INPUT` | `schiedel_masonry_work_m` |
| `schiedel_vent_channel_2x_36_25` | `schiedel_vent_channel_2x_count` | material count | `SUPPLIER_INPUT` | `schiedel_vent_channel_2x_36_25_item` |
| `schiedel_vent_channel_3x_52_25` | `schiedel_vent_channel_3x_count` | material count | `SUPPLIER_INPUT` | `schiedel_vent_channel_3x_52_25_item` |
| `schiedel_delivery` | `schiedel_delivery_trips` | trips | `MANUAL_REVIEW` | `schiedel_delivery_truck` |
| `schiedel_consumables_tool_depreciation` | `direct_cost_base_before_consumables * consumables_rate` | subtotal, rate | `AUTO_CALCULATED` + `DEFAULT` | none |
| `technical_supervision_zero`, `procurement_storage_zero`, `overhead_zero`, `profit_zero` | `1` | none | `AUTO_CALCULATED` zero structure | none |

Do not derive Schiedel 2x/3x counts from old control values. The calculator notes that material counts require confirmation from specification/Elena table.

## 10. Load-Bearing Walls And Lintels

Primary project inputs:

- main wall block spec volumes: D400 400 mm, D500 250 mm;
- second floor wall volume when `floor_2_spec_volume`;
- parapet and vent/chimney spec volumes when flat roof enabled;
- cutoff waterproofing area in production `spec_area`;
- lintel total length and lintel concrete spec volume in production modes;
- main wall and lintel rebar spec length tables;
- scaffolding floors count or legacy direct quantities;
- fixed/manual delivery, waste, supervision values where the calculator keeps them manual.

| Estimate line / family | Quantity formula | Leaf inputs | Source | Price |
|---|---|---|---|---|
| `scaffolding_setup_dismantling` | legacy direct quantity or `floors_count * scaffolding_setup_units_per_floor` | floors count or direct quantity | `AUTO_PROJECT`/`DEFAULT`; legacy `MANUAL_REVIEW` | `scaffolding_setup_dismantling_work_set` |
| `scaffolding_timber_material` | legacy direct m3 or `floors_count * scaffolding_timber_m3_per_floor` | floors count or direct quantity | `AUTO_PROJECT`/`DEFAULT`; legacy `MANUAL_REVIEW` | `timber_m3` |
| `cutoff_waterproofing_under_first_row_blocks` | `cutoff_waterproofing_load_bearing_walls_area_m2` in spec mode | cutoff waterproofing area | `AUTO_PROJECT` | `cutoff_waterproofing_under_blocks_m2` |
| `main_load_bearing_wall_masonry_work` | `main_wall_gas_block_400_spec_volume_m3 + main_wall_gas_block_250_spec_volume_m3` | main wall spec volumes | `AUTO_PROJECT` | `gas_block_masonry_work_m3` |
| `main_gas_block_d400_600x400x250_material` | `ceil((d400_spec_volume * waste_coeff) / pallet_volume) * pallet_volume` | D400 spec volume, waste, pallet | volume `AUTO_PROJECT`; coeff/pallet `DEFAULT` | `gas_block_d400_m3` |
| `main_gas_block_d500_600x250x250_material` | `ceil((d500_250_spec_volume * waste_coeff) / pallet_volume) * pallet_volume` | D500 250 spec volume, waste, pallet | volume `AUTO_PROJECT`; coeff/pallet `DEFAULT` | `gas_block_d500_m3` |
| `main_gas_block_adhesive` | `ceil(main_masonry_volume * adhesive_consumption * adhesive_waste_coeff)` | masonry volume, consumption, waste | volume `AUTO_PROJECT`; coeffs `DEFAULT` | `block_adhesive_bag` |
| `sand_concrete_m300_first_row` | first-row area/consumption formula from wall block | wall geometry/spec values, consumption | mostly `AUTO_CALCULATED` + `DEFAULT` | `sand_concrete_bag` |
| `u_block_lintel_cutting` | `lintel_total_length_m / gas_block_length_m` | lintel total length, block length | length `AUTO_PROJECT`; block length `DEFAULT` | `u_block_lintel_cutting_item` |
| `main_wall_chasing_for_d10_reinforcement` | legacy wall geometry or sum main wall rebar base length | wall rebar input | `AUTO_CALCULATED` control | none |
| `main_wall_rebar_*` | `ceil(spec_length_m * waste_coeff / rod_length_m) * rod_length_m` in spec mode | main wall rebar table | spec length `DETAIL_TABLE`; catalog `DEFAULT` | `rebar_<class>_d<diameter>_m` |
| `gas_blocks_and_mix_delivery` | `ceil(total_ordered_block_volume / truck_capacity_m3)` | ordered block volume, capacity | `AUTO_CALCULATED` + `DEFAULT` | `block_delivery_truck` |
| `gas_blocks_unloading_manipulator` | same as gas block delivery trucks | delivery trucks | `AUTO_CALCULATED` | `block_unloading_manipulator_truck` |
| `main_walls_blocks_crane_moving_25t` | legacy manual shifts or delivery-truck threshold | delivery trucks/manual shifts | `AUTO_CALCULATED` / `MANUAL_REVIEW` | `crane_shift` |
| `lintel_rebar_frame_assembly` | `sum(lintel rebar order_length_m)` | lintel rebar table | `AUTO_CALCULATED` control | none |
| `lintel_rebar_*` | `ceil(spec_length_m * waste_coeff / rod_length_m) * rod_length_m` | lintel rebar table | `DETAIL_TABLE` + catalog `DEFAULT` | corresponding rebar price |
| `lintel_concreting_work` | `lintel_total_length_m` | lintel total length | `AUTO_PROJECT` | `lintel_concreting_work_m` |
| `lintel_concrete_b22_5_m300_material` | `max(lintel_concrete_spec_volume_m3 * waste_coeff, min_order_volume)` in spec mode | lintel concrete spec volume, waste, min order | volume `AUTO_PROJECT`; coeff/min `DEFAULT` | `concrete_b22_5_m3` |
| `lintel_concrete_delivery` | `concrete_delivery_trips` | delivery trips | `MANUAL_REVIEW` | `concrete_delivery_trip` |
| `manual_concrete_lifting` | `lintel_concrete_order_volume_m3` | lintel concrete order volume | `AUTO_CALCULATED` | `manual_concrete_lifting_m3` |
| `floor_2_masonry_work` | `floor_2_masonry_volume_m3` | 2nd floor wall volume | `AUTO_PROJECT` | `gas_block_masonry_work_m3` |
| `floor_2_gas_block_d400_material` | `ceil(floor_2_volume * waste_coeff / pallet_volume) * pallet_volume` | 2nd floor volume, waste, pallet | volume `AUTO_PROJECT`; coeff/pallet `DEFAULT` | `gas_block_d400_m3` |
| `floor_2_masonry_glue` | `ceil(floor_2_volume * adhesive_consumption * waste_coeff)` | 2nd floor volume, coeffs | volume `AUTO_PROJECT`; coeffs `DEFAULT` | `block_adhesive_bag` |
| `parapet_masonry_work`, `parapet_gas_block_d400_material` | parapet volume and pallet rounding | parapet spec volume | `AUTO_PROJECT` when flat roof has parapet | masonry/block prices |
| `vent_chimney_gas_block_cladding_work`, `vent_chimney_gas_block_d500_600x150x250_material` | `vent_spec_volume / thickness` for work area; block order by volume | vent/chimney spec volume, thickness | volume `AUTO_PROJECT`; thickness `DEFAULT` | cladding/block prices |
| `walls_consumables_tool_amortization` | provided amount in current calculator | raw amount | `MANUAL_REVIEW` pending formula | none |
| `construction_waste_removal` | `waste_removal_trucks` | trucks | `MANUAL_REVIEW` | `waste_removal_truck` |
| `walls_technical_supervision` | `1` fixed amount | amount | `MANUAL_REVIEW` | `technical_supervision_fixed` |

Production direction: prefer spec modes (`spec_area`, `spec_total_length`, `spec_volume`, `spec_length_items`, `floor_2_spec_volume`) over legacy reconstruction from one old project.

## 11. Next-Step Implications

For the next per-section contract work:

1. Start with `waterproofing` because it has the smallest matrix and cleanest calculator.
2. Create `sections/waterproofing/section_contract.yaml` from this matrix.
3. The contract must include only leaf inputs needed for review, not calculated line quantities.
4. After one contract works, repeat section by section.

Recommended contract order:

1. `waterproofing`
2. `schiedel_vent_channels`
3. `foundation_slab`
4. `floor_slab_2`
5. `floor_slab_1`
6. `flat_roof`
7. `load_bearing_walls_lintels`

## 12. Coverage Check

Representative calculator outputs checked:

- `waterproofing`: 8 estimate lines.
- `foundation_slab`: 30 estimate lines.
- `floor_slab_1`: 28 estimate lines.
- `floor_slab_2`: 26 estimate lines.
- `flat_roof`: 31 estimate lines.
- `schiedel_vent_channels`: 9 estimate lines.
- `load_bearing_walls_lintels`: 27 estimate lines.

Total representative estimate lines covered by explicit rows or line families: 159.

Known limitation: this is a draft matrix, not final per-section YAML. The per-section contract step must still validate every line code against the calculator result for that section.
