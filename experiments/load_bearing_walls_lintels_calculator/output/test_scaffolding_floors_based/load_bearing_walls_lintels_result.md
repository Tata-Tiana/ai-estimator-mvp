# Расчёт несущих стен и перемычек: test_scaffolding_floors_based

Проект: `test_scaffolding_floors_based`

## Входные параметры
- `project_name`: `test_scaffolding_floors_based`
- `scaffolding_setup_work_unit_price`: `20000`
- `scaffolding_timber_unit_price`: `21500`
- `cutoff_waterproofing_material_unit_price`: `250`
- `cutoff_waterproofing_work_unit_price`: `100`
- `main_wall_gas_block_400_spec_volume_m3`: `78.95`
- `main_wall_gas_block_250_spec_volume_m3`: `30.4`
- `main_wall_masonry_work_unit_price`: `7000`
- `gas_block_waste_coeff`: `1.05`
- `gas_block_d400_pallet_volume_m3`: `2.15`
- `gas_block_d400_unit_price`: `6000`
- `gas_block_d500_250_pallet_volume_m3`: `1.8`
- `gas_block_d500_250_unit_price`: `5500`
- `adhesive_consumption_bag_per_m3`: `1.2`
- `adhesive_waste_coeff`: `1.05`
- `adhesive_unit_price`: `340`
- `sand_concrete_consumption_kg_per_m2_per_10mm`: `19`
- `sand_concrete_thickness_factor`: `2`
- `sand_concrete_bag_weight_kg`: `40`
- `sand_concrete_unit_price`: `375`
- `gas_block_length_m`: `0.6`
- `u_block_cutting_work_unit_price`: `400`
- `main_wall_external_length_m`: `79.9`
- `main_wall_internal_250_control_length_m`: `34.743`
- `main_wall_reinforcement_rows`: `5`
- `main_wall_400_reinforcement_threads`: `2`
- `main_wall_250_reinforcement_threads`: `1`
- `main_wall_reinforcement_overlap_coeff`: `1.1`
- `rebar_waste_coeff`: `1.05`
- `rebar_a500_d10_kg_per_m`: `0.617`
- `rebar_a500_d10_rod_length_m`: `11.7`
- `rebar_a500_d10_unit_price_per_m`: `32.72`
- `gas_block_delivery_truck_capacity_m3`: `32`
- `gas_block_delivery_unit_price`: `28000`
- `gas_block_unloading_manipulator_unit_price`: `15000`
- `crane_25t_unit_price`: `30000`
- `lintel_rebar_items`: `[{'code': 'lintel_rebar_a500_d12', 'name': 'Арматура класса А500 диаметром 12 мм', 'steel_class': 'A500', 'diameter_mm': 12, 'weight_kg': 103, 'kg_per_meter': 0.888, 'rod_length_m': 11.7, 'unit_price_per_m': 45.29}, {'code': 'lintel_rebar_a240_d6', 'name': 'Арматура класса А240 диаметром 6 мм', 'steel_class': 'A240', 'diameter_mm': 6, 'weight_kg': 20.4, 'kg_per_meter': 0.222, 'rod_length_m': 6, 'unit_price_per_m': 13.32}]`
- `lintel_concreting_work_unit_price`: `1000`
- `concrete_waste_coeff`: `1.05`
- `concrete_m300_unit_price`: `6400`
- `concrete_delivery_trips`: `1`
- `concrete_delivery_unit_price`: `7500`
- `manual_concrete_lifting_work_unit_price`: `5000`
- `lintel_monolithic_concreting_work_unit_price`: `20000`
- `lintel_formwork_plywood_unit_price`: `1450`
- `lintel_formwork_timber_unit_price`: `23500`
- `lintel_insulation_work_unit_price`: `650`
- `lintel_insulation_eps_unit_price`: `9020`
- `lintel_glue_foam_unit_price`: `450`
- `lintel_insulation_eps_waste_coeff`: `1.05`
- `lintel_insulation_eps_pack_volume_m3`: `0.2773`
- `lintel_glue_foam_coverage_m_per_can`: `10`
- `lintel_glue_foam_min_units`: `1`
- `parapet_masonry_work_unit_price`: `7000`
- `vent_chimney_cladding_work_unit_price`: `1200`
- `gas_block_d500_150_pallet_volume_m3`: `1.8`
- `gas_block_d500_150_unit_price`: `5600`
- `parapet_crane_shifts`: `1`
- `parapet_chasing_base_length_m`: `231.6`
- `second_light_chasing_base_length_m`: `153.16`
- `parapet_rebar_base_length_m`: `232`
- `second_light_rebar_base_length_m`: `153`
- `walls_consumables_tool_amortization_amount_raw`: `100521.7`
- `waste_removal_trucks`: `3`
- `waste_removal_truck_unit_price`: `10000`
- `waste_removal_work_unit_price`: `3500`
- `technical_supervision_amount`: `10000`
- `lintel_section_width_m`: `0.125`
- `lintel_section_height_m`: `0.125`
- `lintel_concrete_calc_method`: `legacy_length_section`
- `lintel_concrete_spec_volume_m3`: `None`
- `lintel_concrete_min_order_volume_m3`: `1`
- `scaffolding_calc_method`: `floors_based`
- `scaffolding_setup_quantity`: `None`
- `scaffolding_timber_quantity_m3`: `None`
- `floors_count`: `2`
- `scaffolding_setup_units_per_floor`: `1`
- `scaffolding_timber_m3_per_floor`: `1`
- `cutoff_waterproofing_calc_method`: `legacy_lengths_by_wall_thickness`
- `cutoff_waterproofing_load_bearing_walls_area_m2`: `None`
- `cutoff_waterproofing_wall_400_lengths_m`: `[17.8, 5.1, 6.6, 8.5, 3, 4.2, 11.3, 4.05, 0.9, 0.4, 4.4, 4.2, 1.2, 0.4, 1.75, 3.9]`
- `cutoff_waterproofing_wall_250_lengths_m`: `[2.7, 2.25, 1.9, 0.15, 1.7, 1.2, 8.4, 2.35, 2, 3.24, 2.75, 4.6, 1.95, 1.2, 1.65]`
- `wall_400_thickness_m`: `0.4`
- `wall_250_thickness_m`: `0.25`
- `lintel_length_calc_method`: `legacy_length_count_items`
- `lintel_total_length_m`: `None`
- `lintel_lengths_m`: `[{'length_m': 1.4, 'count': 6}, {'length_m': 2.3, 'count': 2}, {'length_m': 1.2, 'count': 3}, {'length_m': 2.3, 'count': 1}, {'length_m': 3.2, 'count': 1}, {'length_m': 1.3, 'count': 1}]`
- `floor_2_lintel_ublock_total_length_m`: `None`
- `floor_2_lintel_concrete_spec_volume_m3`: `None`
- `floor_2_concrete_delivery_trips`: `None`
- `floor_1_lintel_monolithic_concrete_volume_m3`: `None`
- `floor_1_lintel_monolithic_insulation_length_m`: `None`
- `floor_1_lintel_formwork_plywood_qty`: `None`
- `floor_1_lintel_formwork_timber_volume_m3`: `None`
- `floor_1_lintel_insulation_eps_spec_volume_m3`: `None`
- `floor_2_lintel_monolithic_concrete_volume_m3`: `None`
- `floor_2_lintel_monolithic_insulation_length_m`: `None`
- `floor_2_lintel_formwork_plywood_qty`: `None`
- `floor_2_lintel_formwork_timber_volume_m3`: `None`
- `floor_2_lintel_insulation_eps_spec_volume_m3`: `None`
- `main_wall_rebar_calc_method`: `legacy_wall_geometry`
- `main_wall_rebar_items`: `[]`
- `wall_block_items`: `[]`
- `lintel_rebar_calc_method`: `legacy_weight_items`
- `main_walls_crane_calc_method`: `legacy_manual_shifts`
- `main_walls_crane_shifts`: `2`
- `upper_floor_calc_method`: `legacy_second_light_addon`
- `floor_2_masonry_volume_m3`: `None`
- `second_light_masonry_enabled`: `True`
- `second_light_masonry_case_specific`: `True`
- `second_light_masonry_volume_m3`: `13.5`
- `parapet_calc_method`: `legacy_manual_toggle`
- `flat_roof_enabled`: `False`
- `parapet_enabled`: `True`
- `parapet_masonry_volume_m3`: `22.74`
- `parapet_gas_block_d500_250_spec_volume_m3`: `None`
- `vent_chimney_cladding_calc_method`: `legacy_manual_toggle`
- `vent_chimney_cladding_enabled`: `True`
- `vent_chimney_gas_block_spec_volume_m3`: `1.72`
- `vent_chimney_geometry_calc_method`: `legacy_segments_rows`
- `vent_chimney_block_thickness_m`: `0.15`
- `vent_chimney_segment_lengths_m`: `[{'length_m': 0.88, 'count': 2}, {'length_m': 0.55, 'count': 6}, {'length_m': 0.72, 'count': 2}, {'length_m': 0.36, 'count': 2}]`
- `vent_chimney_rows`: `5`
- `block_height_m`: `0.25`

## Формулы подмостей/лесов

Production-режим `floors_based`: подмости считаются от количества этажей.

* `scaffolding_setup_quantity = floors_count * scaffolding_setup_units_per_floor`
* `scaffolding_timber_quantity_m3 = floors_count * scaffolding_timber_m3_per_floor`

| Показатель | Значение |
| --- | ---: |
| `scaffolding_calc_method` | `floors_based` |
| `floors_count` | `2` |
| `setup_units_per_floor` | `1` |
| `timber_m3_per_floor` | `1` |
| `setup_quantity` | `2.0` |
| `timber_quantity_m3` | `2.0` |

## Формулы отсечной гидроизоляции

Legacy-режим `legacy_lengths_by_wall_thickness`: площадь считается по длинам стен 400/250 мм и толщине стены.

* `area = sum(lengths_400) * wall_400_thickness_m + sum(lengths_250) * wall_250_thickness_m`

| Показатель | Значение |
| --- | ---: |
| `cutoff_waterproofing_calc_method` | `legacy_lengths_by_wall_thickness` |
| `cutoff_waterproofing_source` | `legacy_lengths_by_wall_thickness` |
| `wall_400_length_m` | `77.7` |
| `wall_250_length_m` | `38.04` |
| `cutoff_waterproofing_area_m2` | `40.59` |

## Формулы перемычек

Legacy-режим `legacy_length_count_items`: общая длина перемычек считается по списку `length_m * count`.

* `lintel_total_length_m = sum(length_m * count)`
* `u_block_quantity = lintel_total_length_m / gas_block_length_m`

| Показатель | Значение |
| --- | ---: |
| `lintel_length_calc_method` | `legacy_length_count_items` |
| `lintel_length_source` | `legacy_length_count_items` |
| `lintel_total_length_m` | `23.4` |
| `gas_block_length_m` | `0.6` |
| `u_block_quantity` | `39.0` |
| `lintel_section_width_m` | `0.125` |
| `lintel_section_height_m` | `0.125` |
| `u_block_lintel_cutting.unit` | `шт` |


Бетон перемычек legacy: объём считается по длине перемычек и сечению U-блока.

* `lintel_raw_concrete_volume_m3 = lintel_total_length_m * lintel_section_width_m * lintel_section_height_m`
* `lintel_required_concrete_volume_m3 = lintel_raw_concrete_volume_m3 * concrete_waste_coeff`
* `lintel_concrete_order_volume_m3 = max(1, ceil(lintel_required_concrete_volume_m3))`

| Показатель | Значение |
| --- | ---: |
| `lintel_concrete_calc_method` | `legacy_length_section` |
| `lintel_concrete_source` | `legacy_length_section` |
| `lintel_section_width_m` | `0.125` |
| `lintel_section_height_m` | `0.125` |
| `lintel_raw_concrete_volume_m3` | `0.3656` |
| `lintel_required_concrete_volume_m3` | `0.3839` |
| `lintel_concrete_order_volume_m3` | `1.0` |

## Формулы арматуры

Арматура кладки legacy: считается через длины стен, ряды, нитки и коэффициент нахлёста.

| Показатель | Значение |
| --- | ---: |
| `main_wall_rebar_calc_method` | `legacy_wall_geometry` |
| `main_wall_rebar_source` | `legacy_wall_geometry` |
| `main_wall_chasing_quantity_m` | `1070.0` |


Арматура перемычек legacy: считается через вес `weight_kg` с переводом в м.п.

| Показатель | Значение |
| --- | ---: |
| `lintel_rebar_calc_method` | `legacy_weight_items` |
| `lintel_rebar_source` | `legacy_weight_items` |
| `lintel_rebar_frame_assembly_quantity_m` | `230.7` |

## Формулы крана несущих стен

Legacy-режим `legacy_manual_shifts`: используется прямое значение `main_walls_crane_shifts` из старого input.json.

| Показатель | Значение |
| --- | ---: |
| `main_walls_crane_calc_method` | `legacy_manual_shifts` |
| `gas_block_delivery_trucks` | `5` |
| `main_walls_crane_shifts` | `2.0` |

## Расчётные блоки
| Показатель | Значение |
| --- | ---: |
| `scaffolding.scaffolding_calc_method` | `floors_based` |
| `scaffolding.scaffolding_source` | `floors_based` |
| `scaffolding.floors_count` | `2` |
| `scaffolding.floors_count_source` | `floors_count` |
| `scaffolding.floors_count_input` | `2` |
| `scaffolding.setup_units_per_floor` | `1` |
| `scaffolding.timber_m3_per_floor` | `1` |
| `scaffolding.setup_quantity` | `2.0` |
| `scaffolding.timber_quantity_m3` | `2.0` |
| `cutoff_waterproofing.cutoff_waterproofing_calc_method` | `legacy_lengths_by_wall_thickness` |
| `cutoff_waterproofing.cutoff_waterproofing_source` | `legacy_lengths_by_wall_thickness` |
| `cutoff_waterproofing.cutoff_waterproofing_load_bearing_walls_area_m2` | `None` |
| `cutoff_waterproofing.wall_400_length_m` | `77.7` |
| `cutoff_waterproofing.wall_250_length_m` | `38.04` |
| `cutoff_waterproofing.cutoff_waterproofing_area_m2` | `40.59` |
| `main_walls.main_masonry_volume_m3` | `109.35` |
| `wall_block_items.used` | `False` |
| `wall_block_items.partitions_captured_volume_m3` | `0.0` |
| `main_gas_blocks.d400.spec_volume_m3` | `78.95` |
| `main_gas_blocks.d400.required_volume_m3` | `82.8975` |
| `main_gas_blocks.d400.raw_pallets` | `38.557` |
| `main_gas_blocks.d400.pallets` | `39` |
| `main_gas_blocks.d400.order_volume_m3` | `83.85` |
| `main_gas_blocks.d500_250.spec_volume_m3` | `30.4` |
| `main_gas_blocks.d500_250.required_volume_m3` | `31.92` |
| `main_gas_blocks.d500_250.raw_pallets` | `17.7333` |
| `main_gas_blocks.d500_250.pallets` | `18` |
| `main_gas_blocks.d500_250.order_volume_m3` | `32.4` |
| `adhesive_and_sand_concrete.main_adhesive_raw_bags` | `137.781` |
| `adhesive_and_sand_concrete.main_adhesive_bags` | `138` |
| `adhesive_and_sand_concrete.sand_concrete_raw_bags` | `38.5605` |
| `adhesive_and_sand_concrete.sand_concrete_bags` | `39` |
| `lintels.lintel_length_calc_method` | `legacy_length_count_items` |
| `lintels.lintel_length_source` | `legacy_length_count_items` |
| `lintels.lintel_total_length_m` | `23.4` |
| `lintels.gas_block_length_m` | `0.6` |
| `lintels.u_block_quantity` | `39.0` |
| `lintels.lintel_200mm_steps` | `117.0` |
| `lintels.lintel_concrete_calc_method` | `legacy_length_section` |
| `lintels.lintel_concrete_source` | `legacy_length_section` |
| `lintels.lintel_concrete_spec_volume_m3` | `None` |
| `lintels.lintel_section_width_m` | `0.125` |
| `lintels.lintel_section_height_m` | `0.125` |
| `lintels.lintel_raw_concrete_volume_m3` | `0.3656` |
| `lintels.lintel_required_concrete_volume_m3` | `0.3839` |
| `lintels.lintel_concrete_min_order_volume_m3` | `1.0` |
| `lintels.lintel_concrete_order_volume_m3` | `1.0` |
| `lintels.lintel_rebar_calc_method` | `legacy_weight_items` |
| `lintels.lintel_rebar_source` | `legacy_weight_items` |
| `lintels.rebar.lintel_rebar_a500_d12.weight_kg` | `103` |
| `lintels.rebar.lintel_rebar_a500_d12.raw_length_m` | `115.991` |
| `lintels.rebar.lintel_rebar_a500_d12.length_with_waste_m` | `121.7905` |
| `lintels.rebar.lintel_rebar_a500_d12.raw_rods` | `10.4094` |
| `lintels.rebar.lintel_rebar_a500_d12.rods` | `11` |
| `lintels.rebar.lintel_rebar_a500_d12.order_length_m` | `128.7` |
| `lintels.rebar.lintel_rebar_a240_d6.weight_kg` | `20.4` |
| `lintels.rebar.lintel_rebar_a240_d6.raw_length_m` | `91.8919` |
| `lintels.rebar.lintel_rebar_a240_d6.length_with_waste_m` | `96.4865` |
| `lintels.rebar.lintel_rebar_a240_d6.raw_rods` | `16.0811` |
| `lintels.rebar.lintel_rebar_a240_d6.rods` | `17` |
| `lintels.rebar.lintel_rebar_a240_d6.order_length_m` | `102.0` |
| `lintels.lintel_rebar_frame_assembly_quantity_m` | `230.7` |
| `lintels.lintel_rebar_order_length_m` | `230.7` |
| `lintels.lintel_rebar_delivery_weight_kg` | `136.9296` |
| `lintels.lintel_concrete_combined_order_volume_m3` | `1.0` |
| `lintels.ublock_enabled` | `True` |
| `lintels.concrete_enabled` | `True` |
| `floor_2_ublock_lintels.enabled` | `False` |
| `floor_2_ublock_lintels.ublock_total_length_m` | `0.0` |
| `floor_2_ublock_lintels.u_block_quantity` | `0.0` |
| `floor_2_ublock_lintels.concrete_spec_volume_m3` | `0.0` |
| `floor_2_lintel_concrete.enabled` | `False` |
| `floor_2_lintel_concrete.combined_required_volume_m3` | `0.0` |
| `floor_2_lintel_concrete.combined_order_volume_m3` | `0.0` |
| `floor_1_monolithic_lintels.enabled` | `False` |
| `floor_1_monolithic_lintels.monolithic_concrete_volume_m3` | `0.0` |
| `floor_1_monolithic_lintels.monolithic_insulation_length_m` | `0.0` |
| `floor_1_monolithic_lintels.formwork_plywood_qty` | `0.0` |
| `floor_1_monolithic_lintels.formwork_timber_volume_m3` | `0.0` |
| `floor_1_monolithic_lintels.insulation_eps_spec_volume_m3` | `0.0` |
| `floor_1_monolithic_lintels.insulation_eps_required_volume_m3` | `0.0` |
| `floor_1_monolithic_lintels.insulation_eps_raw_packs` | `0.0` |
| `floor_1_monolithic_lintels.insulation_eps_packs` | `0` |
| `floor_1_monolithic_lintels.insulation_eps_order_volume_m3` | `0.0` |
| `floor_1_monolithic_lintels.glue_foam_raw_units` | `0.0` |
| `floor_1_monolithic_lintels.glue_foam_units` | `0` |
| `floor_2_monolithic_lintels.enabled` | `False` |
| `floor_2_monolithic_lintels.monolithic_concrete_volume_m3` | `0.0` |
| `floor_2_monolithic_lintels.monolithic_insulation_length_m` | `0.0` |
| `floor_2_monolithic_lintels.formwork_plywood_qty` | `0.0` |
| `floor_2_monolithic_lintels.formwork_timber_volume_m3` | `0.0` |
| `floor_2_monolithic_lintels.insulation_eps_spec_volume_m3` | `0.0` |
| `floor_2_monolithic_lintels.insulation_eps_required_volume_m3` | `0.0` |
| `floor_2_monolithic_lintels.insulation_eps_raw_packs` | `0.0` |
| `floor_2_monolithic_lintels.insulation_eps_packs` | `0` |
| `floor_2_monolithic_lintels.insulation_eps_order_volume_m3` | `0.0` |
| `floor_2_monolithic_lintels.glue_foam_raw_units` | `0.0` |
| `floor_2_monolithic_lintels.glue_foam_units` | `0` |
| `main_wall_reinforcement.main_wall_rebar_calc_method` | `legacy_wall_geometry` |
| `main_wall_reinforcement.main_wall_rebar_source` | `legacy_wall_geometry` |
| `main_wall_reinforcement.main_wall_chasing_raw_length_m` | `1069.9865` |
| `main_wall_reinforcement.main_wall_chasing_quantity_m` | `1070.0` |
| `main_wall_reinforcement.main_wall_rebar_a500_d10.base_length_m` | `1070.0` |
| `main_wall_reinforcement.main_wall_rebar_a500_d10.raw_rods` | `96.0256` |
| `main_wall_reinforcement.main_wall_rebar_a500_d10.rods` | `97` |
| `main_wall_reinforcement.main_wall_rebar_a500_d10.order_length_m` | `1134.9` |
| `main_wall_reinforcement.main_wall_rebar_a500_d10.material_total_raw` | `37133.928` |
| `main_wall_reinforcement.main_wall_rebar_a500_d10.material_total` | `37134` |
| `main_wall_reinforcement.main_wall_rebar_control_weight_kg` | `700.2333` |
| `floor_2_load_bearing_walls.floors_count` | `2` |
| `floor_2_load_bearing_walls.upper_floor_calc_method` | `legacy_second_light_addon` |
| `floor_2_load_bearing_walls.enabled` | `True` |
| `floor_2_load_bearing_walls.floor_2_load_bearing_walls_enabled` | `True` |
| `floor_2_load_bearing_walls.floor_2_masonry_volume_m3` | `0.0` |
| `floor_2_load_bearing_walls.floor_2_d400.spec_volume_m3` | `0.0` |
| `floor_2_load_bearing_walls.floor_2_d400.required_volume_m3` | `0.0` |
| `floor_2_load_bearing_walls.floor_2_d400.raw_pallets` | `0.0` |
| `floor_2_load_bearing_walls.floor_2_d400.pallets` | `0` |
| `floor_2_load_bearing_walls.floor_2_d400.order_volume_m3` | `0.0` |
| `floor_2_load_bearing_walls.floor_2_adhesive_raw_bags` | `0.0` |
| `floor_2_load_bearing_walls.floor_2_adhesive_bags` | `0` |
| `deliveries_and_cranes.gas_block_delivery_total_volume_m3` | `158.55` |
| `deliveries_and_cranes.gas_block_delivery_raw_trucks` | `4.9547` |
| `deliveries_and_cranes.main_walls_crane_calc_method` | `legacy_manual_shifts` |
| `deliveries_and_cranes.main_walls_crane_source` | `legacy_manual_shifts` |
| `deliveries_and_cranes.gas_block_delivery_trucks` | `5` |
| `deliveries_and_cranes.main_walls_crane_threshold_trucks` | `None` |
| `deliveries_and_cranes.main_walls_crane_shifts` | `2.0` |
| `parapet.parapet_calc_method` | `legacy_manual_toggle` |
| `parapet.flat_roof_enabled` | `False` |
| `parapet.parapet_enabled_calculated` | `True` |
| `parapet.parapet_masonry_volume_m3` | `22.74` |
| `parapet.parapet_d400.spec_volume_m3` | `22.74` |
| `parapet.parapet_d400.required_volume_m3` | `23.877` |
| `parapet.parapet_d400.raw_pallets` | `11.1056` |
| `parapet.parapet_d400.pallets` | `12` |
| `parapet.parapet_d400.order_volume_m3` | `25.8` |
| `parapet.parapet_gas_block_d500_250_spec_volume_m3` | `0.0` |
| `parapet.parapet_d500_250.spec_volume_m3` | `0.0` |
| `parapet.parapet_d500_250.required_volume_m3` | `0.0` |
| `parapet.parapet_d500_250.raw_pallets` | `0.0` |
| `parapet.parapet_d500_250.pallets` | `0` |
| `parapet.parapet_d500_250.order_volume_m3` | `0.0` |
| `parapet.parapet_total_masonry_volume_m3` | `22.74` |
| `parapet.parapet_upper_level_total_volume_m3` | `36.24` |
| `parapet.parapet_and_upper_level_d400.spec_volume_m3` | `36.24` |
| `parapet.parapet_and_upper_level_d400.required_volume_m3` | `38.052` |
| `parapet.parapet_and_upper_level_d400.raw_pallets` | `17.6986` |
| `parapet.parapet_and_upper_level_d400.pallets` | `18` |
| `parapet.parapet_and_upper_level_d400.order_volume_m3` | `38.7` |
| `parapet.parapet_d400_delivery_control.order_volume_m3` | `23.65` |
| `parapet.parapet_d400_delivery_control.notes` | `Delivery split from combined parapet+second-light D400 order volume.` |
| `parapet.parapet_chasing_base_length_m` | `231.6` |
| `parapet.parapet_rebar_base_length_m` | `232` |
| `parapet.parapet_rebar_order_length_m` | `245.7` |
| `parapet.parapet_crane_shifts` | `1` |
| `vent_chimney_cladding.vent_chimney_cladding_calc_method` | `legacy_manual_toggle` |
| `vent_chimney_cladding.vent_chimney_geometry_calc_method` | `legacy_segments_rows` |
| `vent_chimney_cladding.flat_roof_enabled` | `False` |
| `vent_chimney_cladding.vent_chimney_cladding_enabled_calculated` | `True` |
| `vent_chimney_cladding.vent_chimney_gas_block_spec_volume_m3` | `1.72` |
| `vent_chimney_cladding.vent_chimney_block_thickness_m` | `0.15` |
| `vent_chimney_cladding.vent_chimney_cladding_area_m2` | `11.4666666667` |
| `vent_chimney_cladding.vent_chimney_display_area_m2` | `11.47` |
| `vent_chimney_cladding.vent_chimney_d500_150.spec_volume_m3` | `1.72` |
| `vent_chimney_cladding.vent_chimney_d500_150.required_volume_m3` | `1.806` |
| `vent_chimney_cladding.vent_chimney_d500_150.raw_pallets` | `1.0033` |
| `vent_chimney_cladding.vent_chimney_d500_150.pallets` | `2` |
| `vent_chimney_cladding.vent_chimney_d500_150.order_volume_m3` | `3.6` |
| `vent_chimney_cladding.vent_chimney_segment_lengths_m` | `[{'length_m': 0.88, 'count': 2}, {'length_m': 0.55, 'count': 6}, {'length_m': 0.72, 'count': 2}, {'length_m': 0.36, 'count': 2}]` |
| `vent_chimney_cladding.vent_chimney_rows` | `5` |
| `vent_chimney_cladding.block_height_m` | `0.25` |
| `vent_chimney_cladding.vent_chimney_total_length_m` | `7.22` |
| `vent_chimney_cladding.vent_chimney_height_m` | `1.25` |
| `vent_chimney_cladding.vent_chimney_geometry_volume_m3` | `1.3538` |
| `overheads.second_light_adhesive_raw_bags` | `17.01` |
| `overheads.second_light_adhesive_bags` | `18` |
| `overheads.parapet_vent_adhesive_raw_bags` | `30.8196` |
| `overheads.parapet_vent_adhesive_bags` | `31` |
| `overheads.parapet_upper_level_adhesive_bags` | `49` |
| `overheads.floor_2_adhesive_raw_bags` | `0.0` |
| `overheads.floor_2_adhesive_bags` | `0` |
| `overheads.parapet_rebar.base_length_m` | `232.0` |
| `overheads.parapet_rebar.raw_rods` | `20.8205` |
| `overheads.parapet_rebar.rods` | `21` |
| `overheads.parapet_rebar.order_length_m` | `245.7` |
| `overheads.parapet_rebar.material_total_raw` | `8039.304` |
| `overheads.parapet_rebar.material_total` | `8039` |
| `overheads.second_light_rebar.base_length_m` | `153.0` |
| `overheads.second_light_rebar.raw_rods` | `13.7308` |
| `overheads.second_light_rebar.rods` | `14` |
| `overheads.second_light_rebar.order_length_m` | `163.8` |
| `overheads.second_light_rebar.material_total_raw` | `5359.536` |
| `overheads.second_light_rebar.material_total` | `5360` |
| `overheads.parapet_and_second_light_rebar_order_length_m` | `409.5` |
| `overheads.walls_consumables_tool_amortization_amount_raw` | `100521.7` |
| `second_light_addon.upper_floor_calc_method` | `legacy_second_light_addon` |
| `second_light_addon.second_light_masonry_enabled` | `True` |
| `second_light_addon.second_light_masonry_case_specific` | `True` |
| `second_light_addon.second_light_masonry_volume_m3` | `13.5` |
| `second_light_addon.second_light_d400_delivery_control.spec_volume_m3` | `13.5` |
| `second_light_addon.second_light_d400_delivery_control.required_volume_m3` | `14.175` |
| `second_light_addon.second_light_d400_delivery_control.raw_pallets` | `6.593` |
| `second_light_addon.second_light_d400_delivery_control.pallets` | `7` |
| `second_light_addon.second_light_d400_delivery_control.order_volume_m3` | `15.05` |
| `second_light_addon.second_light_chasing_base_length_m` | `153.16` |
| `second_light_addon.second_light_chasing_case_specific` | `True` |
| `second_light_addon.second_light_rebar_base_length_m` | `153` |
| `second_light_addon.second_light_rebar_order_length_m` | `163.8` |
| `second_light_addon.second_light_rebar_case_specific` | `True` |

## Строки серой внутренней сметы
| code | name | quantity | display_quantity | unit | material_unit_price | material_total_raw | material_total | work_unit_price | work_total_raw | work_total | line_total_raw | line_total | case_specific |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `scaffolding_setup_dismantling` | Устройство лесов, подмостей для кладки, демонтаж лесов | `2.0` | `` | `компл` | `0.0` | `0.0` | `0` | `20000` | `40000.0` | `40000` | `40000.0` | `40000` | `False` |
| `scaffolding_timber_material` | Пиломатериал для устройства лесов | `2.0` | `` | `м3` | `21500` | `43000.0` | `43000` | `0.0` | `0.0` | `0` | `43000.0` | `43000` | `False` |
| `cutoff_waterproofing_under_first_row_blocks` | Гидроизоляция поверхности под первый ряд блоков | `40.59` | `` | `м2` | `250` | `10147.5` | `10148` | `100` | `4059.0` | `4059` | `14206.5` | `14207` | `False` |
| `main_load_bearing_wall_masonry_work` | Кладка внешних, внутренних стен из газобетонных блоков | `109.35` | `` | `м3` | `0.0` | `0.0` | `0` | `7000` | `765450.0` | `765450` | `765450.0` | `765450` | `False` |
| `main_gas_block_d400_600x400x250_material` | Газобетонный блок D400 600x400x250 мм | `83.85` | `` | `м3` | `6000` | `503100.0` | `503100` | `0.0` | `0.0` | `0` | `503100.0` | `503100` | `False` |
| `main_gas_block_d500_600x250x250_material` | Газобетонный блок D500 600x250x250 мм | `32.4` | `` | `м3` | `5500` | `178200.0` | `178200` | `0.0` | `0.0` | `0` | `178200.0` | `178200` | `False` |
| `main_gas_block_adhesive` | Монтажный клей для блоков 25 кг | `138.0` | `` | `мешок` | `340` | `46920.0` | `46920` | `0.0` | `0.0` | `0` | `46920.0` | `46920` | `False` |
| `sand_concrete_m300_first_row` | Пескобетон М300 40 кг | `39.0` | `` | `шт` | `375` | `14625.0` | `14625` | `0.0` | `0.0` | `0` | `14625.0` | `14625` | `False` |
| `main_wall_chasing_for_d10_reinforcement` | Штробление блоков под армирование Ø10 | `1070.0` | `` | `мп` | `0.0` | `0.0` | `0` | `0.0` | `0.0` | `0` | `0.0` | `0` | `False` |
| `main_wall_rebar_a500_d10` | Арматура A500 Ø10 для несущих стен | `1134.9` | `` | `мп` | `32.72` | `37133.928` | `37134` | `0.0` | `0.0` | `0` | `37133.928` | `37134` | `False` |
| `gas_blocks_and_mix_delivery` | Доставка блоков, смеси | `5.0` | `` | `маш` | `28000` | `140000.0` | `140000` | `0.0` | `0.0` | `0` | `140000.0` | `140000` | `False` |
| `gas_blocks_unloading_manipulator` | Разгрузка блоков, смеси манипулятором | `5.0` | `` | `маш` | `15000` | `75000.0` | `75000` | `0.0` | `0.0` | `0` | `75000.0` | `75000` | `False` |
| `main_walls_blocks_crane_moving_25t` | Перемещение блоков, смеси автокраном 25 т | `2.0` | `` | `смена` | `30000` | `60000.0` | `60000` | `0.0` | `0.0` | `0` | `60000.0` | `60000` | `False` |
| `lintel_rebar_frame_assembly` | Изготовление и монтаж каркаса армирования перемычек | `230.7` | `` | `мп` | `0.0` | `0.0` | `0` | `0.0` | `0.0` | `0` | `0.0` | `0` | `False` |
| `lintel_rebar_a500_d12` | Арматура класса А500 диаметром 12 мм | `128.7` | `` | `мп` | `45.29` | `5828.823` | `5829` | `0.0` | `0.0` | `0` | `5828.823` | `5829` | `False` |
| `lintel_rebar_a240_d6` | Арматура класса А240 диаметром 6 мм | `102.0` | `` | `мп` | `13.32` | `1358.64` | `1359` | `0.0` | `0.0` | `0` | `1358.64` | `1359` | `False` |
| `u_block_lintel_cutting` | Резка блока под перемычку (U-блок) | `39.0` | `` | `шт` | `0.0` | `0.0` | `0` | `400` | `15600.0` | `15600` | `15600.0` | `15600` | `False` |
| `lintel_concreting_work` | Бетонирование перемычек | `23.4` | `` | `мп` | `0.0` | `0.0` | `0` | `1000` | `23400.0` | `23400` | `23400.0` | `23400` | `False` |
| `lintel_concrete_b22_5_m300_material` | Бетон В22,5 М300 для перемычек | `1.0` | `` | `м3` | `6400` | `6400.0` | `6400` | `0.0` | `0.0` | `0` | `6400.0` | `6400` | `False` |
| `lintel_concrete_delivery` | Доставка бетона до объекта | `1.0` | `` | `рейс` | `7500` | `7500.0` | `7500` | `0.0` | `0.0` | `0` | `7500.0` | `7500` | `False` |
| `manual_concrete_lifting` | Перенос, подъём бетона вручную | `1.0` | `` | `м3` | `0.0` | `0.0` | `0` | `5000` | `5000.0` | `5000` | `5000.0` | `5000` | `False` |
| `parapet_and_upper_level_masonry_work` | Кладка парапета и верхнего уровня | `36.24` | `` | `м3` | `0.0` | `0.0` | `0` | `7000` | `253680.0` | `253680` | `253680.0` | `253680` | `True` |
| `parapet_and_upper_level_gas_block_d400_material` | Газобетонный блок D400 для парапета и верхнего уровня | `38.7` | `` | `м3` | `6000` | `232200.0` | `232200` | `0.0` | `0.0` | `0` | `232200.0` | `232200` | `True` |
| `vent_chimney_gas_block_cladding_work` | Обкладка дымохода и вентканалов 150 мм | `11.4667` | `11.47` | `м2` | `0.0` | `0.0` | `0` | `1200` | `13760.0` | `13760` | `13760.0` | `13760` | `False` |
| `vent_chimney_gas_block_d500_600x150x250_material` | Газобетонный блок D500 600x150x250 мм | `3.6` | `` | `м3` | `5600` | `20160.0` | `20160` | `0.0` | `0.0` | `0` | `20160.0` | `20160` | `False` |
| `parapet_upper_level_adhesive` | Монтажный клей для парапета и верхнего уровня | `49.0` | `` | `мешок` | `340` | `16660.0` | `16660` | `0.0` | `0.0` | `0` | `16660.0` | `16660` | `True` |
| `parapet_blocks_crane_moving` | Перемещение блоков, смеси автокраном для парапета | `1.0` | `` | `смена` | `30000` | `30000.0` | `30000` | `0.0` | `0.0` | `0` | `30000.0` | `30000` | `False` |
| `parapet_and_second_light_chasing_for_d10_reinforcement` | Штробление парапета и второго света | `384.76` | `` | `мп` | `0.0` | `0.0` | `0` | `0.0` | `0.0` | `0` | `0.0` | `0` | `True` |
| `parapet_and_second_light_rebar_a500_d10` | Арматура A500 Ø10 для парапета и второго света | `409.5` | `` | `мп` | `32.72` | `13398.84` | `13399` | `0.0` | `0.0` | `0` | `13398.84` | `13399` | `True` |
| `walls_consumables_tool_amortization` | Расходные материалы, амортизация инструмента | `1.0` | `` | `комплект` | `100522` | `100521.7` | `100522` | `0.0` | `0.0` | `0` | `100521.7` | `100522` | `False` |
| `construction_waste_removal` | Вывоз мусора с объекта | `3.0` | `` | `маш` | `10000` | `30000.0` | `30000` | `3500` | `10500.0` | `10500` | `40500.0` | `40500` | `False` |
| `walls_technical_supervision` | Технический надзор | `1.0` | `` | `-` | `0.0` | `0.0` | `0` | `10000` | `10000.0` | `10000` | `10000.0` | `10000` | `False` |

## Итоги raw/rounded
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total_raw` | `1572154.431` |
| `internal_materials_total` | `1572154` |
| `internal_works_total_raw` | `1141449.0` |
| `internal_works_total` | `1141449` |
| `internal_section_total_raw` | `2713603.431` |
| `internal_section_total` | `2713603` |
| `sum_of_displayed_line_material_totals` | `1572156` |
| `sum_of_displayed_line_work_totals` | `1141449` |
| `sum_of_displayed_line_totals` | `2713605` |

## Warnings
Предупреждений нет.

## Comparison
| Показатель | Ожидание | Получено | Разница | Статус |
| --- | ---: | ---: | ---: | --- |
| `calculation_blocks.scaffolding.scaffolding_calc_method` | `floors_based` | `floors_based` | `` | `ok` |
| `calculation_blocks.scaffolding.scaffolding_source` | `floors_based` | `floors_based` | `` | `ok` |
| `calculation_blocks.scaffolding.floors_count` | `2` | `2` | `0` | `ok` |
| `calculation_blocks.scaffolding.setup_units_per_floor` | `1` | `1` | `0` | `ok` |
| `calculation_blocks.scaffolding.timber_m3_per_floor` | `1` | `1` | `0` | `ok` |
| `calculation_blocks.scaffolding.setup_quantity` | `2` | `2.0` | `0.0` | `ok` |
| `calculation_blocks.scaffolding.timber_quantity_m3` | `2` | `2.0` | `0.0` | `ok` |
| `estimate_lines.scaffolding_setup_dismantling.quantity` | `2` | `2.0` | `0.0` | `ok` |
| `estimate_lines.scaffolding_setup_dismantling.work_total` | `40000` | `40000` | `0` | `ok` |
| `estimate_lines.scaffolding_setup_dismantling.line_total` | `40000` | `40000` | `0` | `ok` |
| `estimate_lines.scaffolding_timber_material.quantity` | `2` | `2.0` | `0.0` | `ok` |
| `estimate_lines.scaffolding_timber_material.material_total` | `43000` | `43000` | `0` | `ok` |
| `estimate_lines.scaffolding_timber_material.line_total` | `43000` | `43000` | `0` | `ok` |
