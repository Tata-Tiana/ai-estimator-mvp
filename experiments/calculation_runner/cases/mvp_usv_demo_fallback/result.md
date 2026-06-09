# Calculation runner result

## Что сделано

- Взяты generated `input.json` из input_builder.
- Созданы временные case folders.
- Запущены калькуляторы разделов.
- Собраны результаты по разделам.

## Важно

Этот прогон выполнен в `demo_with_template_fallback`.
Недостающие параметры могли быть взяты из template `input.json`.
Это не production-расчёт и не финальная смета.

## Сводка по разделам

| Раздел | Статус | Материалы | Работы | Итого | Exit code | Warnings | Result |
|---|---|---:|---:|---:|---:|---:|---|
| Земляные работы | completed_with_warnings | 2248997 | 337223 | 2586220 | 0 | 2 | experiments/calculation_runner/cases/mvp_usv_demo_fallback/calculations/earthworks/result.json |
| Фундаментная плита | completed_with_warnings | 1377698 | 1084000 | 2461698 | 0 | 19 | experiments/calculation_runner/cases/mvp_usv_demo_fallback/calculations/foundation_slab/result.json |
| Гидроизоляция | completed_with_warnings | 31884 | 17255 | 49139 | 0 | 4 | experiments/calculation_runner/cases/mvp_usv_demo_fallback/calculations/waterproofing/result.json |
| Несущие стены и перемычки | completed_with_warnings | 1540668 | 1121449 | 2662117 | 0 | 26 | experiments/calculation_runner/cases/mvp_usv_demo_fallback/calculations/load_bearing_walls_lintels/result.json |
| Плита перекрытия 1-го этажа | completed_with_warnings | 1132538 | 611926 | 1744464 | 0 | 18 | experiments/calculation_runner/cases/mvp_usv_demo_fallback/calculations/floor_slab_1/result.json |
| Плита перекрытия 2-го этажа | completed_with_warnings | 411599 | 214290 | 625889 | 1 | 17 | experiments/calculation_runner/cases/mvp_usv_demo_fallback/calculations/floor_slab_2/result.json |
| Плоская кровля | completed_with_warnings | 1417244 | 618070 | 2035314 | 1 | 26 | experiments/calculation_runner/cases/mvp_usv_demo_fallback/calculations/flat_roof/result.json |
| Вентиляционные каналы Schiedel | completed_with_warnings | 36596 | 81600 | 118196 | 1 | 8 | experiments/calculation_runner/cases/mvp_usv_demo_fallback/calculations/schiedel_vent_channels/result.json |

## Итоги

- Материалы всего: `8197224`
- Работы всего: `4085813`
- Итого: `12283037`

## Ошибки и предупреждения

- earthworks: pricing warnings: 9
- earthworks: comparison mismatches: 7
- foundation_slab: planter_membrane_installation_work_m2: price_code not found in price_registry, fallback input price used
- foundation_slab: timber_formwork_installation_work_m2: price_code not found in price_registry and fallback input price is missing
- foundation_slab: plywood_1520x1520_18mm_sheet: price_code not found in price_registry, fallback input price used
- foundation_slab: timber_m3: price_code not found in price_registry, fallback input price used
- foundation_slab: eps_laying_work_m2: price_code not found in price_registry, fallback input price used
- foundation_slab: thermal_insert_50_installation_work_m: price_code not found in price_registry, fallback input price used
- foundation_slab: thermal_insert_100_installation_work_m: price_code not found in price_registry, fallback input price used
- foundation_slab: thermal_insert_50_material_m3: price_code not found in price_registry, fallback input price used
- foundation_slab: thermal_insert_100_material_m3: price_code not found in price_registry, fallback input price used
- foundation_slab: crane_shift: price_code not found in price_registry, fallback input price used
- foundation_slab: metal_delivery_truck: price_code not found in price_registry, fallback input price used
- foundation_slab: concrete_placing_work_m3: price_code not found in price_registry, fallback input price used
- foundation_slab: concrete_b22_5_m3: price_code not found in price_registry, fallback input price used
- foundation_slab: concrete_delivery_trip: price_code not found in price_registry, fallback input price used
- foundation_slab: concrete_pump_32m_shift: price_code not found in price_registry, fallback input price used
- foundation_slab: formwork_dismantling_work_m2: price_code not found in price_registry and fallback input price is missing
- foundation_slab: technical_supervision_fixed: price_code not found in price_registry, fallback input price used
- foundation_slab: pricing warnings: 17
- foundation_slab: comparison mismatches: 2
- waterproofing: bitumen_waterproofing_work_m2: price_code not found in price_registry, fallback input price used
- waterproofing: eps_wall_insulation_work_m2: price_code not found in price_registry, fallback input price used
- waterproofing: pricing warnings: 2
- waterproofing: comparison mismatches: 18
- load_bearing_walls_lintels: scaffolding_setup_dismantling_work_set: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: timber_m3: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: cutoff_waterproofing_under_blocks_m2: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: gas_block_masonry_work_m3: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: gas_block_d400_m3: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: gas_block_d500_m3: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: block_adhesive_bag: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: sand_concrete_bag: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: u_block_lintel_cutting_item: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: block_delivery_truck: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: block_unloading_manipulator_truck: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: crane_shift: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: lintel_concreting_work_m: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: concrete_b22_5_m3: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: concrete_delivery_trip: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: manual_concrete_lifting_m3: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: gas_block_masonry_work_m3: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: gas_block_d400_m3: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: gas_block_cladding_work_m2: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: gas_block_d500_150_m3: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: block_adhesive_bag: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: crane_shift: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: waste_removal_truck: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: technical_supervision_fixed: price_code not found in price_registry, fallback input price used
- load_bearing_walls_lintels: pricing warnings: 24
- load_bearing_walls_lintels: comparison mismatches: 17
- floor_slab_1: formwork_rental_m2: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: formwork_delivery_truck: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: crane_shift: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: formwork_consumables_m2: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: plywood_1520x1520_18mm_sheet: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: timber_m3: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: metal_delivery_truck: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: concrete_placing_work_m3: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: beam_concrete_placing_work_m3: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: concrete_b22_5_m3: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: concrete_delivery_trip: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: concrete_pump_32m_shift: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: edge_insulation_work_m: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: eps_bottom_slab_insulation_work_m2: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: eps_penoplex_osnova_100_m3: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: technical_supervision_fixed: price_code not found in price_registry and fallback input price is missing
- floor_slab_1: pricing warnings: 16
- floor_slab_1: comparison mismatches: 21
- floor_slab_2: runner exited with code 1
- floor_slab_2: concrete_placing_volume_m3 is a manual/project quantity for this case; it is not derived from slab_area_m2 * slab thickness.
- floor_slab_2: edge_insulation_height_m is 0.18 m although the section title says 200 mm; 0.18 m is kept for the current Excel match.
- floor_slab_2: formwork_rental_m2: price_code not found in price_registry, fallback input price used
- floor_slab_2: formwork_delivery_truck: price_code not found in price_registry, fallback input price used
- floor_slab_2: crane_shift: price_code not found in price_registry, fallback input price used
- floor_slab_2: formwork_consumables_m2: price_code not found in price_registry and fallback input price is missing
- floor_slab_2: plywood_1520x1520_18mm_sheet: price_code not found in price_registry, fallback input price used
- floor_slab_2: timber_m3: price_code not found in price_registry, fallback input price used
- floor_slab_2: concrete_placing_work_m3: price_code not found in price_registry, fallback input price used
- floor_slab_2: concrete_b22_5_m3: price_code not found in price_registry, fallback input price used
- floor_slab_2: concrete_delivery_trip: price_code not found in price_registry, fallback input price used
- floor_slab_2: concrete_pump_32m_shift: price_code not found in price_registry, fallback input price used
- floor_slab_2: edge_insulation_work_m: price_code not found in price_registry, fallback input price used
- floor_slab_2: eps_penoplex_osnova_100_m3: price_code not found in price_registry, fallback input price used
- floor_slab_2: pricing warnings: 12
- floor_slab_2: comparison mismatches: 32
- flat_roof: runner exited with code 1
- flat_roof: project_spec_roof_area_m2 = 294 is not used without human review; current calculation uses roof_area_total_m2.
- flat_roof: Slope insulation plate volumes are supplier/Technonikol manual inputs, not geometry-derived values.
- flat_roof: Temporary door line is case-specific and is not included in this universal base calculator.
- flat_roof: Roof consumables use provided raw total; base formula is to be confirmed later.
- flat_roof: Logistics and supply uses provided raw total from the reviewed gray estimate.
- flat_roof: Technical supervision uses provided gray work total from the reviewed estimate.
- flat_roof: Procurement/storage uses provided gray work total from the reviewed estimate.
- flat_roof: Some material totals intentionally keep current Excel raw/display mismatches.
- flat_roof: roof_eps100_technonikol_carbon_eco_m3: price_code not found in price_registry, fallback input price used
- flat_roof: roof_eps50_technonikol_carbon_eco_m3: price_code not found in price_registry, fallback input price used
- flat_roof: roof_eps_slope_2_1_plate_a_m3: price_code not found in price_registry, fallback input price used
- flat_roof: roof_eps_slope_2_1_plate_b_m3: price_code not found in price_registry, fallback input price used
- flat_roof: roof_eps_slope_4_2_plate_j_m3: price_code not found in price_registry, fallback input price used
- flat_roof: roof_eps_slope_4_2_plate_k_m3: price_code not found in price_registry, fallback input price used
- flat_roof: roof_geotextile_technonikol_prof_300_m2: price_code not found in price_registry, fallback input price used
- flat_roof: roof_geotextile_technonikol_prof_150_m2: price_code not found in price_registry, fallback input price used
- flat_roof: roof_aluminum_pressure_rail_m: price_code not found in price_registry, fallback input price used
- flat_roof: roof_aluminum_edge_rail_m: price_code not found in price_registry, fallback input price used
- flat_roof: roof_pvc_membrane_logicroof_vrp_1_5mm_gray_roll: price_code not found in price_registry, fallback input price used
- flat_roof: roof_parapet_drain_item: price_code not found in price_registry, fallback input price used
- flat_roof: roof_internal_drain_with_heating_item: price_code not found in price_registry, fallback input price used
- flat_roof: roof_internal_drain_pvc_110mm_m: price_code not found in price_registry, fallback input price used
- flat_roof: roof_crane_lifting_shift: price_code not found in price_registry, fallback input price used
- flat_roof: pricing warnings: 15
- flat_roof: comparison mismatches: 18
- schiedel_vent_channels: runner exited with code 1
- schiedel_vent_channels: Количество материалов Schiedel 24 и 8 требует подтверждения у Елены/по спецификации.
- schiedel_vent_channels: Количество доставки является ручным параметром.
- schiedel_vent_channels: Клиентская часть не считается.
- schiedel_vent_channels: schiedel_masonry_work_m: price_code not found in price_registry, fallback input price used
- schiedel_vent_channels: schiedel_delivery_truck: price_code not found in price_registry, fallback input price used
- schiedel_vent_channels: pricing warnings: 2
- schiedel_vent_channels: comparison mismatches: 20

## Следующий шаг

`box_calculator` — агрегатор, который будет собирать разделы в единую смету коробки дома.
