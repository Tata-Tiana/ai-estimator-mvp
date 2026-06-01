# Расчёт несущих стен и перемычек: test_load_bearing_walls_lintels_live_prices

Проект: `test_load_bearing_walls_lintels_live_prices`

## Входные параметры
- `project_name`: `test_load_bearing_walls_lintels_live_prices`
- `scaffolding_setup_quantity`: `1`
- `scaffolding_setup_work_unit_price`: `20000`
- `scaffolding_timber_quantity_m3`: `1`
- `scaffolding_timber_unit_price`: `21500`
- `cutoff_waterproofing_wall_400_lengths_m`: `[17.8, 5.1, 6.6, 8.5, 3, 4.2, 11.3, 4.05, 0.9, 0.4, 4.4, 4.2, 1.2, 0.4, 1.75, 3.9]`
- `cutoff_waterproofing_wall_250_lengths_m`: `[2.7, 2.25, 1.9, 0.15, 1.7, 1.2, 8.4, 2.35, 2, 3.24, 2.75, 4.6, 1.95, 1.2, 1.65]`
- `wall_400_thickness_m`: `0.4`
- `wall_250_thickness_m`: `0.25`
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
- `lintel_lengths_m`: `[{'length_m': 1.4, 'count': 6}, {'length_m': 2.3, 'count': 2}, {'length_m': 1.2, 'count': 3}, {'length_m': 2.3, 'count': 1}, {'length_m': 3.2, 'count': 1}, {'length_m': 1.3, 'count': 1}]`
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
- `main_walls_crane_shifts`: `2`
- `crane_25t_unit_price`: `30000`
- `lintel_rebar_items`: `[{'code': 'lintel_rebar_a500_d12', 'name': 'Арматура класса А500 диаметром 12 мм', 'steel_class': 'A500', 'diameter_mm': 12, 'weight_kg': 103, 'kg_per_meter': 0.888, 'rod_length_m': 11.7, 'unit_price_per_m': 45.29}, {'code': 'lintel_rebar_a240_d6', 'name': 'Арматура класса А240 диаметром 6 мм', 'steel_class': 'A240', 'diameter_mm': 6, 'weight_kg': 20.4, 'kg_per_meter': 0.222, 'rod_length_m': 6, 'unit_price_per_m': 13.32}]`
- `lintel_concreting_work_unit_price`: `1000`
- `lintel_section_width_m`: `0.125`
- `lintel_section_height_m`: `0.125`
- `concrete_waste_coeff`: `1.05`
- `lintel_concrete_min_order_volume_m3`: `1`
- `concrete_m300_unit_price`: `6400`
- `concrete_delivery_trips`: `1`
- `concrete_delivery_unit_price`: `7500`
- `manual_concrete_lifting_work_unit_price`: `5000`
- `parapet_enabled`: `True`
- `parapet_masonry_volume_m3`: `22.74`
- `parapet_masonry_work_unit_price`: `7000`
- `second_light_masonry_enabled`: `True`
- `second_light_masonry_case_specific`: `True`
- `second_light_masonry_volume_m3`: `13.5`
- `vent_chimney_cladding_enabled`: `True`
- `vent_chimney_gas_block_spec_volume_m3`: `1.72`
- `vent_chimney_block_thickness_m`: `0.15`
- `vent_chimney_cladding_work_unit_price`: `1200`
- `gas_block_d500_150_pallet_volume_m3`: `1.8`
- `gas_block_d500_150_unit_price`: `5600`
- `vent_chimney_segment_lengths_m`: `[{'length_m': 0.88, 'count': 2}, {'length_m': 0.55, 'count': 6}, {'length_m': 0.72, 'count': 2}, {'length_m': 0.36, 'count': 2}]`
- `vent_chimney_rows`: `5`
- `block_height_m`: `0.25`
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

## Расчётные блоки
| Показатель | Значение |
| --- | ---: |
| `scaffolding.setup_quantity` | `1` |
| `scaffolding.timber_quantity_m3` | `1` |
| `cutoff_waterproofing.wall_400_length_m` | `77.7` |
| `cutoff_waterproofing.wall_250_length_m` | `38.04` |
| `cutoff_waterproofing.cutoff_waterproofing_area_m2` | `40.59` |
| `main_walls.main_masonry_volume_m3` | `109.35` |
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
| `lintels.lintel_total_length_m` | `23.4` |
| `lintels.u_block_quantity` | `39.0` |
| `lintels.lintel_200mm_steps` | `117.0` |
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
| `lintels.lintel_raw_concrete_volume_m3` | `0.3656` |
| `lintels.lintel_required_concrete_volume_m3` | `0.3839` |
| `lintels.lintel_concrete_order_volume_m3` | `1.0` |
| `main_wall_reinforcement.main_wall_chasing_raw_length_m` | `1069.9865` |
| `main_wall_reinforcement.main_wall_chasing_quantity_m` | `1070.0` |
| `main_wall_reinforcement.main_wall_rebar_a500_d10.base_length_m` | `1070.0` |
| `main_wall_reinforcement.main_wall_rebar_a500_d10.raw_rods` | `96.0256` |
| `main_wall_reinforcement.main_wall_rebar_a500_d10.rods` | `97` |
| `main_wall_reinforcement.main_wall_rebar_a500_d10.order_length_m` | `1134.9` |
| `main_wall_reinforcement.main_wall_rebar_a500_d10.material_total_raw` | `37133.928` |
| `main_wall_reinforcement.main_wall_rebar_a500_d10.material_total` | `37134` |
| `main_wall_reinforcement.main_wall_rebar_control_weight_kg` | `700.2333` |
| `deliveries_and_cranes.gas_block_delivery_total_volume_m3` | `158.55` |
| `deliveries_and_cranes.gas_block_delivery_raw_trucks` | `4.9547` |
| `deliveries_and_cranes.gas_block_delivery_trucks` | `5` |
| `deliveries_and_cranes.main_walls_crane_shifts` | `2` |
| `parapet.parapet_masonry_volume_m3` | `22.74` |
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
| `vent_chimney_cladding.vent_chimney_cladding_area_m2` | `11.4666666667` |
| `vent_chimney_cladding.vent_chimney_display_area_m2` | `11.47` |
| `vent_chimney_cladding.vent_chimney_d500_150.spec_volume_m3` | `1.72` |
| `vent_chimney_cladding.vent_chimney_d500_150.required_volume_m3` | `1.806` |
| `vent_chimney_cladding.vent_chimney_d500_150.raw_pallets` | `1.0033` |
| `vent_chimney_cladding.vent_chimney_d500_150.pallets` | `2` |
| `vent_chimney_cladding.vent_chimney_d500_150.order_volume_m3` | `3.6` |
| `vent_chimney_cladding.vent_chimney_total_length_m` | `7.22` |
| `vent_chimney_cladding.vent_chimney_height_m` | `1.25` |
| `vent_chimney_cladding.vent_chimney_geometry_volume_m3` | `1.3538` |
| `overheads.second_light_adhesive_raw_bags` | `17.01` |
| `overheads.second_light_adhesive_bags` | `18` |
| `overheads.parapet_vent_adhesive_raw_bags` | `30.8196` |
| `overheads.parapet_vent_adhesive_bags` | `31` |
| `overheads.parapet_upper_level_adhesive_bags` | `49` |
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

## Строки серой внутренней сметы
| code | name | quantity | display_quantity | unit | material_unit_price | material_total_raw | material_total | work_unit_price | work_total_raw | work_total | line_total_raw | line_total | case_specific |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `scaffolding_setup_dismantling` | Устройство лесов, подмостей для кладки, демонтаж лесов | `1.0` | `` | `компл` | `0.0` | `0.0` | `0` | `20000.0` | `20000.0` | `20000` | `20000.0` | `20000` | `False` |
| `scaffolding_timber_material` | Пиломатериал для устройства лесов | `1.0` | `` | `м3` | `21500.0` | `21500.0` | `21500` | `0.0` | `0.0` | `0` | `21500.0` | `21500` | `False` |
| `cutoff_waterproofing_under_first_row_blocks` | Гидроизоляция поверхности под первый ряд блоков | `40.59` | `` | `м2` | `250.0` | `10147.5` | `10148` | `100` | `4059.0` | `4059` | `14206.5` | `14207` | `False` |
| `main_load_bearing_wall_masonry_work` | Кладка внешних, внутренних стен из газобетонных блоков | `109.35` | `` | `м3` | `0.0` | `0.0` | `0` | `7000.0` | `765450.0` | `765450` | `765450.0` | `765450` | `False` |
| `main_gas_block_d400_600x400x250_material` | Газобетонный блок D400 600x400x250 мм | `83.85` | `` | `м3` | `6000.0` | `503100.0` | `503100` | `0.0` | `0.0` | `0` | `503100.0` | `503100` | `False` |
| `main_gas_block_d500_600x250x250_material` | Газобетонный блок D500 600x250x250 мм | `32.4` | `` | `м3` | `5500.0` | `178200.0` | `178200` | `0.0` | `0.0` | `0` | `178200.0` | `178200` | `False` |
| `main_gas_block_adhesive` | Монтажный клей для блоков 25 кг | `138.0` | `` | `мешок` | `340.0` | `46920.0` | `46920` | `0.0` | `0.0` | `0` | `46920.0` | `46920` | `False` |
| `sand_concrete_m300_first_row` | Пескобетон М300 40 кг | `39.0` | `` | `шт` | `375.0` | `14625.0` | `14625` | `0.0` | `0.0` | `0` | `14625.0` | `14625` | `False` |
| `u_block_lintel_cutting` | Резка блока под перемычку (U-блок) | `39.0` | `` | `шт` | `0.0` | `0.0` | `0` | `400.0` | `15600.0` | `15600` | `15600.0` | `15600` | `False` |
| `main_wall_chasing_for_d10_reinforcement` | Штробление блоков под армирование Ø10 | `1070.0` | `` | `мп` | `0.0` | `0.0` | `0` | `0.0` | `0.0` | `0` | `0.0` | `0` | `False` |
| `main_wall_rebar_a500_d10` | Арматура A500 Ø10 для несущих стен | `1134.9` | `` | `мп` | `27.16` | `30823.884` | `30824` | `0.0` | `0.0` | `0` | `30823.884` | `30824` | `False` |
| `gas_blocks_and_mix_delivery` | Доставка блоков, смеси | `5.0` | `` | `маш` | `28000.0` | `140000.0` | `140000` | `0.0` | `0.0` | `0` | `140000.0` | `140000` | `False` |
| `gas_blocks_unloading_manipulator` | Разгрузка блоков, смеси манипулятором | `5.0` | `` | `маш` | `15000.0` | `75000.0` | `75000` | `0.0` | `0.0` | `0` | `75000.0` | `75000` | `False` |
| `main_walls_blocks_crane_moving_25t` | Перемещение блоков, смеси автокраном 25 т | `2.0` | `` | `смена` | `30000.0` | `60000.0` | `60000` | `0.0` | `0.0` | `0` | `60000.0` | `60000` | `False` |
| `lintel_rebar_frame_assembly` | Изготовление и монтаж каркаса армирования перемычек | `230.7` | `` | `мп` | `0.0` | `0.0` | `0` | `0.0` | `0.0` | `0` | `0.0` | `0` | `False` |
| `lintel_rebar_a500_d12` | Арматура класса А500 диаметром 12 мм | `128.7` | `` | `мп` | `36.85` | `4742.595` | `4743` | `0.0` | `0.0` | `0` | `4742.595` | `4743` | `False` |
| `lintel_rebar_a240_d6` | Арматура класса А240 диаметром 6 мм | `102.0` | `` | `мп` | `10.25` | `1045.5` | `1046` | `0.0` | `0.0` | `0` | `1045.5` | `1046` | `False` |
| `lintel_concreting_work` | Бетонирование перемычек | `23.4` | `` | `мп` | `0.0` | `0.0` | `0` | `1000.0` | `23400.0` | `23400` | `23400.0` | `23400` | `False` |
| `lintel_concrete_b22_5_m300_material` | Бетон В22,5 М300 для перемычек | `1.0` | `` | `м3` | `6400.0` | `6400.0` | `6400` | `0.0` | `0.0` | `0` | `6400.0` | `6400` | `False` |
| `lintel_concrete_delivery` | Доставка бетона до объекта | `1.0` | `` | `рейс` | `7500.0` | `7500.0` | `7500` | `0.0` | `0.0` | `0` | `7500.0` | `7500` | `False` |
| `manual_concrete_lifting` | Перенос, подъём бетона вручную | `1.0` | `` | `м3` | `0.0` | `0.0` | `0` | `5000.0` | `5000.0` | `5000` | `5000.0` | `5000` | `False` |
| `parapet_and_upper_level_masonry_work` | Кладка парапета и верхнего уровня | `36.24` | `` | `м3` | `0.0` | `0.0` | `0` | `7000.0` | `253680.0` | `253680` | `253680.0` | `253680` | `True` |
| `parapet_and_upper_level_gas_block_d400_material` | Газобетонный блок D400 для парапета и верхнего уровня | `38.7` | `` | `м3` | `6000.0` | `232200.0` | `232200` | `0.0` | `0.0` | `0` | `232200.0` | `232200` | `True` |
| `vent_chimney_gas_block_cladding_work` | Обкладка дымохода и вентканалов 150 мм | `11.4667` | `11.47` | `м2` | `0.0` | `0.0` | `0` | `1200.0` | `13760.04` | `13760` | `13760.04` | `13760` | `False` |
| `vent_chimney_gas_block_d500_600x150x250_material` | Газобетонный блок D500 600x150x250 мм | `3.6` | `` | `м3` | `5600.0` | `20160.0` | `20160` | `0.0` | `0.0` | `0` | `20160.0` | `20160` | `False` |
| `parapet_upper_level_adhesive` | Монтажный клей для парапета и верхнего уровня | `49.0` | `` | `мешок` | `340.0` | `16660.0` | `16660` | `0.0` | `0.0` | `0` | `16660.0` | `16660` | `True` |
| `parapet_blocks_crane_moving` | Перемещение блоков, смеси автокраном для парапета | `1.0` | `` | `смена` | `30000.0` | `30000.0` | `30000` | `0.0` | `0.0` | `0` | `30000.0` | `30000` | `False` |
| `parapet_and_second_light_chasing_for_d10_reinforcement` | Штробление парапета и второго света | `384.76` | `` | `мп` | `0.0` | `0.0` | `0` | `0.0` | `0.0` | `0` | `0.0` | `0` | `True` |
| `parapet_and_second_light_rebar_a500_d10` | Арматура A500 Ø10 для парапета и второго света | `409.5` | `` | `мп` | `27.16` | `11122.02` | `11122` | `0.0` | `0.0` | `0` | `11122.02` | `11122` | `True` |
| `walls_consumables_tool_amortization` | Расходные материалы, амортизация инструмента | `1.0` | `` | `комплект` | `100522` | `100521.7` | `100522` | `0.0` | `0.0` | `0` | `100521.7` | `100522` | `False` |
| `construction_waste_removal` | Вывоз мусора с объекта | `3.0` | `` | `маш` | `10000.0` | `30000.0` | `30000` | `3500` | `10500.0` | `10500` | `40500.0` | `40500` | `False` |
| `walls_technical_supervision` | Технический надзор | `1.0` | `` | `-` | `0.0` | `0.0` | `0` | `10000.0` | `10000.0` | `10000` | `10000.0` | `10000` | `False` |

## Итоги raw/rounded
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total_raw` | `1540668.199` |
| `internal_materials_total` | `1540668` |
| `internal_works_total_raw` | `1121449.04` |
| `internal_works_total` | `1121449` |
| `internal_section_total_raw` | `2662117.239` |
| `internal_section_total` | `2662117` |
| `sum_of_displayed_line_material_totals` | `1540670` |
| `sum_of_displayed_line_work_totals` | `1121449` |
| `sum_of_displayed_line_totals` | `2662119` |

## Источники цен

| Строка сметы | price_code | старая цена | использованная цена | источник | предупреждение |
| --- | --- | ---: | ---: | --- | --- |
| Устройство лесов, подмостей для кладки, демонтаж лесов | `scaffolding_setup_dismantling_work_set` | `20000` | `20000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Пиломатериал для устройства лесов | `timber_m3` | `21500` | `21500` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Гидроизоляция поверхности под первый ряд блоков | `cutoff_waterproofing_under_blocks_m2` | `250` | `250` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Кладка внешних, внутренних стен из газобетонных блоков | `gas_block_masonry_work_m3` | `7000` | `7000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Газобетонный блок D400 600x400x250 мм | `gas_block_d400_m3` | `6000` | `6000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Газобетонный блок D500 600x250x250 мм | `gas_block_d500_m3` | `5500` | `5500` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Монтажный клей для блоков 25 кг | `block_adhesive_bag` | `340` | `340` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Пескобетон М300 40 кг | `sand_concrete_bag` | `375` | `375` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Резка блока под перемычку (U-блок) | `u_block_lintel_cutting_item` | `400` | `400` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Штробление блоков под армирование Ø10 | `` | `None` | `None` | `locked_case_prices` |  |
| Арматура A500 Ø10 для несущих стен | `rebar_a500_d10_m` | `32.72` | `27.16` | `price_registry` |  |
| Доставка блоков, смеси | `block_delivery_truck` | `28000` | `28000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Разгрузка блоков, смеси манипулятором | `block_unloading_manipulator_truck` | `15000` | `15000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Перемещение блоков, смеси автокраном 25 т | `crane_shift` | `30000` | `30000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Изготовление и монтаж каркаса армирования перемычек | `` | `None` | `None` | `locked_case_prices` |  |
| Арматура класса А500 диаметром 12 мм | `rebar_a500_d12_m` | `45.29` | `36.85` | `price_registry` |  |
| Арматура класса А240 диаметром 6 мм | `rebar_a240_d6_m` | `13.32` | `10.25` | `price_registry` |  |
| Бетонирование перемычек | `lintel_concreting_work_m` | `1000` | `1000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Бетон В22,5 М300 для перемычек | `concrete_b22_5_m3` | `6400` | `6400` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Доставка бетона до объекта | `concrete_delivery_trip` | `7500` | `7500` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Перенос, подъём бетона вручную | `manual_concrete_lifting_m3` | `5000` | `5000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Кладка парапета и верхнего уровня | `gas_block_masonry_work_m3` | `7000` | `7000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Газобетонный блок D400 для парапета и верхнего уровня | `gas_block_d400_m3` | `6000` | `6000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Обкладка дымохода и вентканалов 150 мм | `gas_block_cladding_work_m2` | `1200` | `1200` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Газобетонный блок D500 600x150x250 мм | `gas_block_d500_150_m3` | `5600` | `5600` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Монтажный клей для парапета и верхнего уровня | `block_adhesive_bag` | `340` | `340` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Перемещение блоков, смеси автокраном для парапета | `crane_shift` | `30000` | `30000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Штробление парапета и второго света | `` | `None` | `None` | `locked_case_prices` |  |
| Арматура A500 Ø10 для парапета и второго света | `rebar_a500_d10_m` | `32.72` | `27.16` | `price_registry` |  |
| Расходные материалы, амортизация инструмента | `` | `100522` | `100522` | `locked_case_prices` |  |
| Вывоз мусора с объекта | `waste_removal_truck` | `10000` | `10000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Технический надзор | `technical_supervision_fixed` | `10000` | `10000` | `fallback_input` | price_code not found in price_registry, fallback input price used |

## Pricing summary
| Показатель | Значение |
| --- | ---: |
| `mode` | `price_registry_with_fallback` |
| `registry_path` | `/Users/tatanamedzidova/Desktop/AI сметчик/ai_estimator_mvp/output/price_registry_filled_v3.xlsx` |
| `prices_from_price_registry` | `4` |
| `prices_from_project_overrides` | `0` |
| `prices_from_fallback_input` | `24` |
| `warnings_count` | `24` |

## Warnings
- scaffolding_setup_dismantling_work_set: price_code not found in price_registry, fallback input price used
- timber_m3: price_code not found in price_registry, fallback input price used
- cutoff_waterproofing_under_blocks_m2: price_code not found in price_registry, fallback input price used
- gas_block_masonry_work_m3: price_code not found in price_registry, fallback input price used
- gas_block_d400_m3: price_code not found in price_registry, fallback input price used
- gas_block_d500_m3: price_code not found in price_registry, fallback input price used
- block_adhesive_bag: price_code not found in price_registry, fallback input price used
- sand_concrete_bag: price_code not found in price_registry, fallback input price used
- u_block_lintel_cutting_item: price_code not found in price_registry, fallback input price used
- block_delivery_truck: price_code not found in price_registry, fallback input price used
- block_unloading_manipulator_truck: price_code not found in price_registry, fallback input price used
- crane_shift: price_code not found in price_registry, fallback input price used
- lintel_concreting_work_m: price_code not found in price_registry, fallback input price used
- concrete_b22_5_m3: price_code not found in price_registry, fallback input price used
- concrete_delivery_trip: price_code not found in price_registry, fallback input price used
- manual_concrete_lifting_m3: price_code not found in price_registry, fallback input price used
- gas_block_masonry_work_m3: price_code not found in price_registry, fallback input price used
- gas_block_d400_m3: price_code not found in price_registry, fallback input price used
- gas_block_cladding_work_m2: price_code not found in price_registry, fallback input price used
- gas_block_d500_150_m3: price_code not found in price_registry, fallback input price used
- block_adhesive_bag: price_code not found in price_registry, fallback input price used
- crane_shift: price_code not found in price_registry, fallback input price used
- waste_removal_truck: price_code not found in price_registry, fallback input price used
- technical_supervision_fixed: price_code not found in price_registry, fallback input price used

## Comparison
Expected values are not provided for this case.
