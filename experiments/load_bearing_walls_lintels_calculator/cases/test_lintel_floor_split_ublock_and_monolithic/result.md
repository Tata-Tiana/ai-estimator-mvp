# Расчёт несущих стен и перемычек: test_lintel_floor_split_ublock_and_monolithic

Проект: `test_lintel_floor_split_ublock_and_monolithic`

## Входные параметры
- `project_name`: `test_lintel_floor_split_ublock_and_monolithic`
- `scaffolding_setup_work_unit_price`: `20000`
- `scaffolding_timber_unit_price`: `23500`
- `cutoff_waterproofing_material_unit_price`: `250`
- `cutoff_waterproofing_work_unit_price`: `100`
- `main_wall_gas_block_400_spec_volume_m3`: `58.05`
- `main_wall_gas_block_250_spec_volume_m3`: `28.8`
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
- `parapet_crane_shifts`: `0`
- `parapet_chasing_base_length_m`: `0`
- `parapet_rebar_base_length_m`: `0`
- `walls_consumables_tool_amortization_amount_raw`: `100521.7`
- `waste_removal_trucks`: `3`
- `waste_removal_truck_unit_price`: `10000`
- `waste_removal_work_unit_price`: `3500`
- `technical_supervision_amount`: `10000`
- `lintel_section_width_m`: `0.125`
- `lintel_section_height_m`: `0.125`
- `lintel_concrete_calc_method`: `spec_volume`
- `lintel_concrete_spec_volume_m3`: `0.24`
- `lintel_concrete_min_order_volume_m3`: `1`
- `scaffolding_calc_method`: `legacy_direct_quantity`
- `scaffolding_setup_quantity`: `2`
- `scaffolding_timber_quantity_m3`: `2`
- `floors_count`: `2`
- `scaffolding_setup_units_per_floor`: `1.0`
- `scaffolding_timber_m3_per_floor`: `1.0`
- `cutoff_waterproofing_calc_method`: `spec_area`
- `cutoff_waterproofing_load_bearing_walls_area_m2`: `28.41`
- `cutoff_waterproofing_wall_400_lengths_m`: `None`
- `cutoff_waterproofing_wall_250_lengths_m`: `None`
- `wall_400_thickness_m`: `None`
- `wall_250_thickness_m`: `None`
- `lintel_length_calc_method`: `spec_total_length`
- `lintel_total_length_m`: `22.62`
- `lintel_lengths_m`: `[]`
- `floor_2_lintel_ublock_total_length_m`: `20.5`
- `floor_2_lintel_concrete_spec_volume_m3`: `0.3`
- `floor_2_concrete_delivery_trips`: `1`
- `floor_1_lintel_monolithic_concrete_volume_m3`: `0.35`
- `floor_1_lintel_monolithic_insulation_length_m`: `1.5`
- `floor_1_lintel_formwork_plywood_qty`: `1`
- `floor_1_lintel_formwork_timber_volume_m3`: `0.2`
- `floor_1_lintel_insulation_eps_spec_volume_m3`: `0.3`
- `floor_2_lintel_monolithic_concrete_volume_m3`: `0.41`
- `floor_2_lintel_monolithic_insulation_length_m`: `1.2`
- `floor_2_lintel_formwork_plywood_qty`: `2`
- `floor_2_lintel_formwork_timber_volume_m3`: `0.2`
- `floor_2_lintel_insulation_eps_spec_volume_m3`: `0.25`
- `main_wall_rebar_calc_method`: `legacy_wall_geometry`
- `main_wall_rebar_items`: `[]`
- `lintel_rebar_calc_method`: `legacy_weight_items`
- `main_walls_crane_calc_method`: `legacy_manual_shifts`
- `main_walls_crane_shifts`: `2`
- `upper_floor_calc_method`: `floor_2_spec_volume`
- `floor_2_masonry_volume_m3`: `61.66`
- `parapet_calc_method`: `flat_roof_spec_volume`
- `flat_roof_enabled`: `False`
- `parapet_masonry_volume_m3`: `None`
- `vent_chimney_cladding_calc_method`: `flat_roof_spec_volume`
- `vent_chimney_gas_block_spec_volume_m3`: `None`
- `vent_chimney_geometry_calc_method`: `legacy_segments_rows`
- `vent_chimney_block_thickness_m`: `0.15`
- `vent_chimney_segment_lengths_m`: `[]`
- `vent_chimney_rows`: `1`
- `block_height_m`: `0.25`

## Формулы подмостей/лесов

Legacy-режим `legacy_direct_quantity`: используются прямые значения `scaffolding_setup_quantity` и `scaffolding_timber_quantity_m3` из старого input.json.

| Показатель | Значение |
| --- | ---: |
| `scaffolding_calc_method` | `legacy_direct_quantity` |
| `setup_quantity` | `2.0` |
| `timber_quantity_m3` | `2.0` |

## Формулы отсечной гидроизоляции

Production-режим `spec_area`: площадь отсечной гидроизоляции под несущие стены берётся готовым значением из спецификации.

Площадь перегородок сюда не включается; для перегородок нужен отдельный параметр `cutoff_waterproofing_partitions_area_m2`.

| Показатель | Значение |
| --- | ---: |
| `cutoff_waterproofing_calc_method` | `spec_area` |
| `cutoff_waterproofing_source` | `spec_area` |
| `cutoff_waterproofing_load_bearing_walls_area_m2` | `28.41` |
| `cutoff_waterproofing_area_m2` | `28.41` |

## Формулы перемычек

Production-режим `spec_total_length`: общая длина перемычек в U-блоке берётся готовым значением из спецификации.

* `u_block_quantity = lintel_total_length_m / gas_block_length_m`
* строка `u_block_lintel_cutting` остаётся в штуках (`шт`), не в м.п.

| Показатель | Значение |
| --- | ---: |
| `lintel_length_calc_method` | `spec_total_length` |
| `lintel_length_source` | `spec_total_length` |
| `lintel_total_length_m` | `22.62` |
| `gas_block_length_m` | `0.6` |
| `u_block_quantity` | `37.7` |
| `lintel_section_width_m` | `0.125` |
| `lintel_section_height_m` | `0.125` |
| `u_block_lintel_cutting.unit` | `шт` |


Бетон перемычек standard: проектный объём берётся из спецификации, без повторного коэффициента запаса.

* `lintel_required_concrete_volume_m3 = lintel_concrete_spec_volume_m3`
* `lintel_concrete_order_volume_m3 = max(1, ceil(lintel_required_concrete_volume_m3))`

| Показатель | Значение |
| --- | ---: |
| `lintel_concrete_calc_method` | `spec_volume` |
| `lintel_concrete_source` | `spec_volume` |
| `lintel_concrete_spec_volume_m3` | `0.24` |
| `lintel_required_concrete_volume_m3` | `0.24` |
| `lintel_concrete_min_order_volume_m3` | `1.0` |
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
| `scaffolding.scaffolding_calc_method` | `legacy_direct_quantity` |
| `scaffolding.scaffolding_source` | `legacy_direct_quantity` |
| `scaffolding.floors_count` | `2` |
| `scaffolding.setup_units_per_floor` | `1.0` |
| `scaffolding.timber_m3_per_floor` | `1.0` |
| `scaffolding.setup_quantity` | `2.0` |
| `scaffolding.timber_quantity_m3` | `2.0` |
| `cutoff_waterproofing.cutoff_waterproofing_calc_method` | `spec_area` |
| `cutoff_waterproofing.cutoff_waterproofing_source` | `spec_area` |
| `cutoff_waterproofing.cutoff_waterproofing_load_bearing_walls_area_m2` | `28.41` |
| `cutoff_waterproofing.wall_400_length_m` | `None` |
| `cutoff_waterproofing.wall_250_length_m` | `None` |
| `cutoff_waterproofing.cutoff_waterproofing_area_m2` | `28.41` |
| `main_walls.main_masonry_volume_m3` | `86.85` |
| `main_gas_blocks.d400.spec_volume_m3` | `58.05` |
| `main_gas_blocks.d400.required_volume_m3` | `60.9525` |
| `main_gas_blocks.d400.raw_pallets` | `28.35` |
| `main_gas_blocks.d400.pallets` | `29` |
| `main_gas_blocks.d400.order_volume_m3` | `62.35` |
| `main_gas_blocks.d500_250.spec_volume_m3` | `28.8` |
| `main_gas_blocks.d500_250.required_volume_m3` | `30.24` |
| `main_gas_blocks.d500_250.raw_pallets` | `16.8` |
| `main_gas_blocks.d500_250.pallets` | `17` |
| `main_gas_blocks.d500_250.order_volume_m3` | `30.6` |
| `adhesive_and_sand_concrete.main_adhesive_raw_bags` | `109.431` |
| `adhesive_and_sand_concrete.main_adhesive_bags` | `110` |
| `adhesive_and_sand_concrete.sand_concrete_raw_bags` | `26.9895` |
| `adhesive_and_sand_concrete.sand_concrete_bags` | `27` |
| `lintels.lintel_length_calc_method` | `spec_total_length` |
| `lintels.lintel_length_source` | `spec_total_length` |
| `lintels.lintel_total_length_m` | `22.62` |
| `lintels.gas_block_length_m` | `0.6` |
| `lintels.u_block_quantity` | `37.7` |
| `lintels.lintel_200mm_steps` | `113.1` |
| `lintels.lintel_concrete_calc_method` | `spec_volume` |
| `lintels.lintel_concrete_source` | `spec_volume` |
| `lintels.lintel_concrete_spec_volume_m3` | `0.24` |
| `lintels.lintel_section_width_m` | `0.125` |
| `lintels.lintel_section_height_m` | `0.125` |
| `lintels.lintel_raw_concrete_volume_m3` | `0.24` |
| `lintels.lintel_required_concrete_volume_m3` | `0.24` |
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
| `floor_2_ublock_lintels.enabled` | `True` |
| `floor_2_ublock_lintels.ublock_total_length_m` | `20.5` |
| `floor_2_ublock_lintels.u_block_quantity` | `34.1667` |
| `floor_2_ublock_lintels.concrete_spec_volume_m3` | `0.3` |
| `floor_2_lintel_concrete.enabled` | `True` |
| `floor_2_lintel_concrete.combined_required_volume_m3` | `0.71` |
| `floor_2_lintel_concrete.combined_order_volume_m3` | `1.0` |
| `floor_1_monolithic_lintels.enabled` | `True` |
| `floor_1_monolithic_lintels.monolithic_concrete_volume_m3` | `0.35` |
| `floor_1_monolithic_lintels.monolithic_insulation_length_m` | `1.5` |
| `floor_1_monolithic_lintels.formwork_plywood_qty` | `1.0` |
| `floor_1_monolithic_lintels.formwork_timber_volume_m3` | `0.2` |
| `floor_1_monolithic_lintels.insulation_eps_spec_volume_m3` | `0.3` |
| `floor_1_monolithic_lintels.insulation_eps_required_volume_m3` | `0.315` |
| `floor_1_monolithic_lintels.insulation_eps_raw_packs` | `1.136` |
| `floor_1_monolithic_lintels.insulation_eps_packs` | `2` |
| `floor_1_monolithic_lintels.insulation_eps_order_volume_m3` | `0.5546` |
| `floor_1_monolithic_lintels.glue_foam_raw_units` | `0.15` |
| `floor_1_monolithic_lintels.glue_foam_units` | `1` |
| `floor_2_monolithic_lintels.enabled` | `True` |
| `floor_2_monolithic_lintels.monolithic_concrete_volume_m3` | `0.41` |
| `floor_2_monolithic_lintels.monolithic_insulation_length_m` | `1.2` |
| `floor_2_monolithic_lintels.formwork_plywood_qty` | `2.0` |
| `floor_2_monolithic_lintels.formwork_timber_volume_m3` | `0.2` |
| `floor_2_monolithic_lintels.insulation_eps_spec_volume_m3` | `0.25` |
| `floor_2_monolithic_lintels.insulation_eps_required_volume_m3` | `0.2625` |
| `floor_2_monolithic_lintels.insulation_eps_raw_packs` | `0.9466` |
| `floor_2_monolithic_lintels.insulation_eps_packs` | `1` |
| `floor_2_monolithic_lintels.insulation_eps_order_volume_m3` | `0.2773` |
| `floor_2_monolithic_lintels.glue_foam_raw_units` | `0.12` |
| `floor_2_monolithic_lintels.glue_foam_units` | `1` |
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
| `floor_2_load_bearing_walls.upper_floor_calc_method` | `floor_2_spec_volume` |
| `floor_2_load_bearing_walls.enabled` | `True` |
| `floor_2_load_bearing_walls.floor_2_load_bearing_walls_enabled` | `True` |
| `floor_2_load_bearing_walls.floor_2_masonry_volume_m3` | `61.66` |
| `floor_2_load_bearing_walls.floor_2_d400.spec_volume_m3` | `61.66` |
| `floor_2_load_bearing_walls.floor_2_d400.required_volume_m3` | `64.743` |
| `floor_2_load_bearing_walls.floor_2_d400.raw_pallets` | `30.113` |
| `floor_2_load_bearing_walls.floor_2_d400.pallets` | `31` |
| `floor_2_load_bearing_walls.floor_2_d400.order_volume_m3` | `66.65` |
| `floor_2_load_bearing_walls.floor_2_adhesive_raw_bags` | `77.6916` |
| `floor_2_load_bearing_walls.floor_2_adhesive_bags` | `78` |
| `deliveries_and_cranes.gas_block_delivery_total_volume_m3` | `159.6` |
| `deliveries_and_cranes.gas_block_delivery_raw_trucks` | `4.9875` |
| `deliveries_and_cranes.main_walls_crane_calc_method` | `legacy_manual_shifts` |
| `deliveries_and_cranes.main_walls_crane_source` | `legacy_manual_shifts` |
| `deliveries_and_cranes.gas_block_delivery_trucks` | `5` |
| `deliveries_and_cranes.main_walls_crane_threshold_trucks` | `None` |
| `deliveries_and_cranes.main_walls_crane_shifts` | `2.0` |
| `parapet.parapet_calc_method` | `flat_roof_spec_volume` |
| `parapet.flat_roof_enabled` | `False` |
| `parapet.parapet_enabled_calculated` | `False` |
| `parapet.parapet_masonry_volume_m3` | `0.0` |
| `parapet.parapet_d400.spec_volume_m3` | `0.0` |
| `parapet.parapet_d400.required_volume_m3` | `0.0` |
| `parapet.parapet_d400.raw_pallets` | `0.0` |
| `parapet.parapet_d400.pallets` | `0` |
| `parapet.parapet_d400.order_volume_m3` | `0.0` |
| `parapet.parapet_upper_level_total_volume_m3` | `0.0` |
| `parapet.parapet_and_upper_level_d400.spec_volume_m3` | `0.0` |
| `parapet.parapet_and_upper_level_d400.required_volume_m3` | `0.0` |
| `parapet.parapet_and_upper_level_d400.raw_pallets` | `0.0` |
| `parapet.parapet_and_upper_level_d400.pallets` | `0` |
| `parapet.parapet_and_upper_level_d400.order_volume_m3` | `0.0` |
| `parapet.parapet_d400_delivery_control.order_volume_m3` | `0.0` |
| `parapet.parapet_d400_delivery_control.notes` | `Production parapet order volume calculated separately.` |
| `parapet.parapet_chasing_base_length_m` | `0` |
| `parapet.parapet_rebar_base_length_m` | `0` |
| `parapet.parapet_rebar_order_length_m` | `0.0` |
| `parapet.parapet_crane_shifts` | `0` |
| `vent_chimney_cladding.vent_chimney_cladding_calc_method` | `flat_roof_spec_volume` |
| `vent_chimney_cladding.vent_chimney_geometry_calc_method` | `legacy_segments_rows` |
| `vent_chimney_cladding.flat_roof_enabled` | `False` |
| `vent_chimney_cladding.vent_chimney_cladding_enabled_calculated` | `False` |
| `vent_chimney_cladding.vent_chimney_gas_block_spec_volume_m3` | `0.0` |
| `vent_chimney_cladding.vent_chimney_block_thickness_m` | `0.15` |
| `vent_chimney_cladding.vent_chimney_cladding_area_m2` | `0.0` |
| `vent_chimney_cladding.vent_chimney_display_area_m2` | `0.0` |
| `vent_chimney_cladding.vent_chimney_d500_150.spec_volume_m3` | `0.0` |
| `vent_chimney_cladding.vent_chimney_d500_150.required_volume_m3` | `0.0` |
| `vent_chimney_cladding.vent_chimney_d500_150.raw_pallets` | `0.0` |
| `vent_chimney_cladding.vent_chimney_d500_150.pallets` | `0` |
| `vent_chimney_cladding.vent_chimney_d500_150.order_volume_m3` | `0.0` |
| `vent_chimney_cladding.vent_chimney_segment_lengths_m` | `[]` |
| `vent_chimney_cladding.vent_chimney_rows` | `1` |
| `vent_chimney_cladding.block_height_m` | `0.25` |
| `vent_chimney_cladding.vent_chimney_total_length_m` | `0.0` |
| `vent_chimney_cladding.vent_chimney_height_m` | `0.25` |
| `vent_chimney_cladding.vent_chimney_geometry_volume_m3` | `0.0` |
| `overheads.parapet_vent_adhesive_raw_bags` | `0.0` |
| `overheads.parapet_vent_adhesive_bags` | `0` |
| `overheads.parapet_upper_level_adhesive_bags` | `0` |
| `overheads.floor_2_adhesive_raw_bags` | `77.6916` |
| `overheads.floor_2_adhesive_bags` | `78` |
| `overheads.parapet_rebar.base_length_m` | `0.0` |
| `overheads.parapet_rebar.raw_rods` | `0.0` |
| `overheads.parapet_rebar.rods` | `0` |
| `overheads.parapet_rebar.order_length_m` | `0.0` |
| `overheads.parapet_rebar.material_total_raw` | `0.0` |
| `overheads.parapet_rebar.material_total` | `0` |
| `overheads.walls_consumables_tool_amortization_amount_raw` | `100521.7` |

## Строки серой внутренней сметы
| code | name | quantity | display_quantity | unit | material_unit_price | material_total_raw | material_total | work_unit_price | work_total_raw | work_total | line_total_raw | line_total | case_specific |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `scaffolding_setup_dismantling` | Устройство лесов, подмостей для кладки, демонтаж лесов | `2.0` | `` | `компл` | `0.0` | `0.0` | `0` | `20000` | `40000.0` | `40000` | `40000.0` | `40000` | `False` |
| `scaffolding_timber_material` | Пиломатериал для устройства лесов | `2.0` | `` | `м3` | `23500` | `47000.0` | `47000` | `0.0` | `0.0` | `0` | `47000.0` | `47000` | `False` |
| `cutoff_waterproofing_under_first_row_blocks` | Гидроизоляция поверхности под первый ряд блоков | `28.41` | `` | `м2` | `250` | `7102.5` | `7103` | `100` | `2841.0` | `2841` | `9943.5` | `9944` | `False` |
| `main_load_bearing_wall_masonry_work` | Кладка внешних, внутренних стен из газобетонных блоков | `86.85` | `` | `м3` | `0.0` | `0.0` | `0` | `7000` | `607950.0` | `607950` | `607950.0` | `607950` | `False` |
| `main_gas_block_d400_600x400x250_material` | Газобетонный блок D400 600x400x250 мм | `62.35` | `` | `м3` | `6000` | `374100.0` | `374100` | `0.0` | `0.0` | `0` | `374100.0` | `374100` | `False` |
| `main_gas_block_d500_600x250x250_material` | Газобетонный блок D500 600x250x250 мм | `30.6` | `` | `м3` | `5500` | `168300.0` | `168300` | `0.0` | `0.0` | `0` | `168300.0` | `168300` | `False` |
| `main_gas_block_adhesive` | Монтажный клей для блоков 25 кг | `110.0` | `` | `мешок` | `340` | `37400.0` | `37400` | `0.0` | `0.0` | `0` | `37400.0` | `37400` | `False` |
| `sand_concrete_m300_first_row` | Пескобетон М300 40 кг | `27.0` | `` | `шт` | `375` | `10125.0` | `10125` | `0.0` | `0.0` | `0` | `10125.0` | `10125` | `False` |
| `main_wall_chasing_for_d10_reinforcement` | Штробление блоков под армирование Ø10 | `1070.0` | `` | `мп` | `0.0` | `0.0` | `0` | `0.0` | `0.0` | `0` | `0.0` | `0` | `False` |
| `main_wall_rebar_a500_d10` | Арматура A500 Ø10 для несущих стен | `1134.9` | `` | `мп` | `32.72` | `37133.928` | `37134` | `0.0` | `0.0` | `0` | `37133.928` | `37134` | `False` |
| `gas_blocks_and_mix_delivery` | Доставка блоков, смеси | `5.0` | `` | `маш` | `28000` | `140000.0` | `140000` | `0.0` | `0.0` | `0` | `140000.0` | `140000` | `False` |
| `gas_blocks_unloading_manipulator` | Разгрузка блоков, смеси манипулятором | `5.0` | `` | `маш` | `15000` | `75000.0` | `75000` | `0.0` | `0.0` | `0` | `75000.0` | `75000` | `False` |
| `main_walls_blocks_crane_moving_25t` | Перемещение блоков, смеси автокраном 25 т | `2.0` | `` | `смена` | `30000` | `60000.0` | `60000` | `0.0` | `0.0` | `0` | `60000.0` | `60000` | `False` |
| `lintel_rebar_frame_assembly` | Изготовление и монтаж каркаса армирования перемычек | `230.7` | `` | `мп` | `0.0` | `0.0` | `0` | `0.0` | `0.0` | `0` | `0.0` | `0` | `False` |
| `lintel_rebar_a500_d12` | Арматура класса А500 диаметром 12 мм | `128.7` | `` | `мп` | `45.29` | `5828.823` | `5829` | `0.0` | `0.0` | `0` | `5828.823` | `5829` | `False` |
| `lintel_rebar_a240_d6` | Арматура класса А240 диаметром 6 мм | `102.0` | `` | `мп` | `13.32` | `1358.64` | `1359` | `0.0` | `0.0` | `0` | `1358.64` | `1359` | `False` |
| `u_block_lintel_cutting` | Резка блока под перемычку (U-блок) | `37.7` | `` | `шт` | `0.0` | `0.0` | `0` | `400` | `15080.0` | `15080` | `15080.0` | `15080` | `False` |
| `lintel_concreting_work` | Бетонирование перемычек | `22.62` | `` | `мп` | `0.0` | `0.0` | `0` | `1000` | `22620.0` | `22620` | `22620.0` | `22620` | `False` |
| `lintel_concrete_b22_5_m300_material` | Бетон В22,5 М300 для перемычек | `1.0` | `` | `м3` | `6400` | `6400.0` | `6400` | `0.0` | `0.0` | `0` | `6400.0` | `6400` | `False` |
| `lintel_concrete_delivery` | Доставка бетона до объекта | `1.0` | `` | `рейс` | `7500` | `7500.0` | `7500` | `0.0` | `0.0` | `0` | `7500.0` | `7500` | `False` |
| `manual_concrete_lifting` | Перенос, подъём бетона вручную | `1.0` | `` | `м3` | `0.0` | `0.0` | `0` | `5000` | `5000.0` | `5000` | `5000.0` | `5000` | `False` |
| `floor_2_u_block_lintel_cutting` | Резка блока под перемычку (U-блок), 2-й этаж | `34.1667` | `` | `шт` | `0.0` | `0.0` | `0` | `400` | `13666.68` | `13667` | `13666.68` | `13667` | `False` |
| `floor_2_lintel_concreting_work` | Бетонирование перемычек в U-блоке, 2-й этаж | `20.5` | `` | `мп` | `0.0` | `0.0` | `0` | `1000` | `20500.0` | `20500` | `20500.0` | `20500` | `False` |
| `floor_2_lintel_concrete_b22_5_m300_material` | Бетон В22,5 М300 для перемычек, 2-й этаж | `1.0` | `` | `м3` | `6400` | `6400.0` | `6400` | `0.0` | `0.0` | `0` | `6400.0` | `6400` | `False` |
| `floor_2_lintel_concrete_delivery` | Доставка бетона до объекта, 2-й этаж | `1.0` | `` | `рейс` | `7500` | `7500.0` | `7500` | `0.0` | `0.0` | `0` | `7500.0` | `7500` | `False` |
| `floor_2_manual_concrete_lifting` | Перенос, подъём бетона вручную, 2-й этаж | `1.0` | `` | `м3` | `0.0` | `0.0` | `0` | `5000` | `5000.0` | `5000` | `5000.0` | `5000` | `False` |
| `floor_1_lintel_monolithic_concreting_work` | Бетонирование монолитных перемычек, 1-й этаж | `0.35` | `` | `м3` | `0.0` | `0.0` | `0` | `20000` | `7000.0` | `7000` | `7000.0` | `7000` | `False` |
| `floor_1_lintel_formwork_plywood_material` | Фанера для опалубки монолитных перемычек, 1-й этаж | `1.0` | `` | `шт` | `1450` | `1450.0` | `1450` | `0.0` | `0.0` | `0` | `1450.0` | `1450` | `False` |
| `floor_1_lintel_formwork_timber_material` | Пиломатериал обрезной для опалубки монолитных перемычек, 1-й этаж | `0.2` | `` | `м3` | `23500` | `4700.0` | `4700` | `0.0` | `0.0` | `0` | `4700.0` | `4700` | `False` |
| `floor_1_lintel_edge_insulation_work` | Устройство утепления по наружной стороне монолитной перемычки, 1-й этаж | `1.5` | `` | `мп` | `0.0` | `0.0` | `0` | `650` | `975.0` | `975` | `975.0` | `975` | `False` |
| `floor_1_lintel_edge_insulation_eps_material` | Экструдированный пенополистирол Пеноплэкс Основа, 1-й этаж | `0.5546` | `0.55` | `м3` | `9020` | `5002.492` | `5002` | `0.0` | `0.0` | `0` | `5002.492` | `5002` | `False` |
| `floor_1_lintel_edge_insulation_glue_foam` | Клей-пена для ЭППС, 1-й этаж | `1.0` | `` | `баллон` | `450` | `450.0` | `450` | `0.0` | `0.0` | `0` | `450.0` | `450` | `False` |
| `floor_2_lintel_monolithic_concreting_work` | Бетонирование монолитных перемычек, 2-й этаж | `0.41` | `` | `м3` | `0.0` | `0.0` | `0` | `20000` | `8200.0` | `8200` | `8200.0` | `8200` | `False` |
| `floor_2_lintel_formwork_plywood_material` | Фанера для опалубки монолитных перемычек, 2-й этаж | `2.0` | `` | `шт` | `1450` | `2900.0` | `2900` | `0.0` | `0.0` | `0` | `2900.0` | `2900` | `False` |
| `floor_2_lintel_formwork_timber_material` | Пиломатериал обрезной для опалубки монолитных перемычек, 2-й этаж | `0.2` | `` | `м3` | `23500` | `4700.0` | `4700` | `0.0` | `0.0` | `0` | `4700.0` | `4700` | `False` |
| `floor_2_lintel_edge_insulation_work` | Устройство утепления по наружной стороне монолитной перемычки, 2-й этаж | `1.2` | `` | `мп` | `0.0` | `0.0` | `0` | `650` | `780.0` | `780` | `780.0` | `780` | `False` |
| `floor_2_lintel_edge_insulation_eps_material` | Экструдированный пенополистирол Пеноплэкс Основа, 2-й этаж | `0.2773` | `0.28` | `м3` | `9020` | `2501.246` | `2501` | `0.0` | `0.0` | `0` | `2501.246` | `2501` | `False` |
| `floor_2_lintel_edge_insulation_glue_foam` | Клей-пена для ЭППС, 2-й этаж | `1.0` | `` | `баллон` | `450` | `450.0` | `450` | `0.0` | `0.0` | `0` | `450.0` | `450` | `False` |
| `floor_2_masonry_work` | Кладка несущих стен 2-го этажа из газобетонных блоков | `61.66` | `` | `м3` | `0.0` | `0.0` | `0` | `7000` | `431620.0` | `431620` | `431620.0` | `431620` | `False` |
| `floor_2_gas_block_d400_material` | Газобетонный блок D400 для несущих стен 2-го этажа | `66.65` | `` | `м3` | `6000` | `399900.0` | `399900` | `0.0` | `0.0` | `0` | `399900.0` | `399900` | `False` |
| `floor_2_masonry_glue` | Монтажный клей для блоков 2-го этажа | `78.0` | `` | `мешок` | `340` | `26520.0` | `26520` | `0.0` | `0.0` | `0` | `26520.0` | `26520` | `False` |
| `walls_consumables_tool_amortization` | Расходные материалы, амортизация инструмента | `1.0` | `` | `комплект` | `100522` | `100521.7` | `100522` | `0.0` | `0.0` | `0` | `100521.7` | `100522` | `False` |
| `construction_waste_removal` | Вывоз мусора с объекта | `3.0` | `` | `маш` | `10000` | `30000.0` | `30000` | `3500` | `10500.0` | `10500` | `40500.0` | `40500` | `False` |
| `walls_technical_supervision` | Технический надзор | `1.0` | `` | `-` | `0.0` | `0.0` | `0` | `10000` | `10000.0` | `10000` | `10000.0` | `10000` | `False` |

## Итоги raw/rounded
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total_raw` | `1570244.329` |
| `internal_materials_total` | `1570244` |
| `internal_works_total_raw` | `1201732.68` |
| `internal_works_total` | `1201733` |
| `internal_section_total_raw` | `2771977.009` |
| `internal_section_total` | `2771977` |
| `sum_of_displayed_line_material_totals` | `1570245` |
| `sum_of_displayed_line_work_totals` | `1201733` |
| `sum_of_displayed_line_totals` | `2771978` |

## Warnings
Предупреждений нет.

## Comparison
Expected values are not provided for this case.
