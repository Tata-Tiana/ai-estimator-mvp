# Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 2-го этажа на отм. +4.680 (200мм)

## Inputs

- project_name: `test_floor_slab_2_beams_bottom_formwork_area`
- slab_area_m2: `None`
- slab_edge_perimeter_m: `41.8`
- concrete_placing_volume_m3: `17.5`

## Calculation Blocks

## Площадь опалубки и геометрия

Production-режим `spec_formwork_area`: площади опалубки берутся из спецификации.

- `main_formwork_area_m2` используется для строки `formwork_rental_set`.
- `edge_formwork_area_m2 + beams_formwork_area_m2` используется для торцевой опалубки, фанеры и пиломатериала.
- `slab_edge_perimeter_m` используется как проектная длина утепляемого торца.
- `slab_edge_perimeter_m * edge_formwork_height_m` остается только контрольной формулой.
- `slab_length_m`, `slab_width_m`, `slab_area_m2` являются optional geometry check.

- main_formwork_area_m2: `94.0`
- edge_formwork_area_m2: `None`
- beams_formwork_area_m2: `None`
- edge_and_beam_formwork_area_m2: `12.92`
- calculated_edge_formwork_area_m2: `None`
- edge_formwork_area_delta_m2: `None`
- slab_edge_perimeter_m: `41.8`
- calculated_slab_area_m2: `None`
- calculated_slab_edge_perimeter_m: `None`
- area_delta_m2: `None`
- formwork_area_delta_m2: `None`

## Доставка и вывоз опалубки

- Production-правило: до 180 м2 включительно — 2 рейса; более 180 м2 — 4 рейса.
- formwork_delivery_calc_method: `area_threshold`
- formwork_delivery_area_source_m2: `94.0`
- formwork_delivery_threshold_m2: `180.0`
- formwork_delivery_trips: `2.0`
- formwork_delivery_breakdown: `1 привоз + 1 вывоз`
- formwork_delivery_status: `calculated`

### geometry

- formwork_area_calc_method: `spec_formwork_area`
- formwork_area_source: `spec_formwork_area`
- edge_formwork_area_source: `spec_formwork_area_combined_edge_and_beam`
- slab_edge_perimeter_source: `spec_edge_perimeter`
- slab_length_m: `None`
- slab_width_m: `None`
- slab_area_m2: `None`
- slab_edge_perimeter_m: `41.8`
- main_formwork_area_m2: `94.0`
- edge_formwork_area_m2: `None`
- beams_formwork_area_m2: `None`
- edge_and_beam_formwork_area_combined_m2: `12.92`
- edge_and_beam_formwork_area_m2: `12.92`
- calculated_edge_formwork_area_m2: `None`
- edge_formwork_area_delta_m2: `None`
- calculated_slab_area_m2: `None`
- calculated_slab_edge_perimeter_m: `None`
- input_slab_area_m2: `None`
- area_delta_m2: `None`
- formwork_area_delta_m2: `None`

### formwork

- formwork_area_calc_method: `spec_formwork_area`
- main_formwork_area_m2: `94.0`
- raw_supplier_rate: `850.0`
- used_rate_per_m2: `850.0`
- edge_formwork_area_m2: `None`
- beams_formwork_area_m2: `None`
- edge_and_beam_formwork_area_m2: `12.92`
- beams_bottom_formwork_area_m2: `3.1`
- edge_beam_formwork_area_for_materials_m2: `16.02`
- calculated_edge_formwork_area_m2: `None`
- edge_formwork_area_delta_m2: `None`
- edge_formwork_area_source: `spec_formwork_area_combined_edge_and_beam`
- formwork_delivery_calc_method: `area_threshold`
- formwork_delivery_area_source_m2: `94.0`
- formwork_delivery_threshold_m2: `180.0`
- formwork_delivery_trips: `2.0`
- formwork_delivery_breakdown: `1 привоз + 1 вывоз`
- formwork_delivery_status: `calculated`

### plywood_and_timber

- edge_and_beam_formwork_area_m2: `12.92`
- beams_bottom_formwork_area_m2: `3.1`
- edge_beam_formwork_area_for_materials_m2: `16.02`
- edge_plywood_sheets_raw: `6.965217`
- non_multiple_places_area_m2: `18.8`
- non_multiple_places_plywood_sheets_raw: `8.173913`
- base_plywood_sheets_raw: `15.13913`
- order_plywood_sheets_raw: `20.13913`
- plywood_sheets: `21`
- timber_volume_m3_raw: `0.801`
- timber_volume_m3_display: `0.8`

### beams

- items: 0 items
- items_count: `0`
- items_total_concrete_volume_m3: `0.0`
- items_total_formwork_area_m2: `0.0`
- items_total_eps_material_area_m2: `0.0`
- items_total_eps_work_length_m: `0.0`
- concrete_volume_source: `calculated_from_beam_items`
- calculated_concrete_volume_m3: `0.0`
- concrete_volume_delta_m3: `None`
- notes: `['All values are 0 when no beams.items are given. Beam concrete is subtracted from concrete_placing_volume_m3 for the slab work line and priced separately on the beam_concreting_work estimate line. beams_formwork_area_m2 and the insulation length/area both use this data when their own scalar inputs are absent.']`

### rebar

- rebar_calc_method: `legacy_weight_kg`
- items: 2 items
- total_rebar_order_length_m: `1263.6`
- total_rebar_order_weight_kg: `847.2438`
- total_rebar_weight_with_waste_kg: `840.0`

### concrete

- concrete_placing_volume_m3: `17.5`
- slab_concrete_volume_m3: `17.5`
- beams_concrete_volume_m3: `0.0`
- concrete_volume_with_waste_raw_m3: `18.375`
- concrete_volume_with_waste_display_m3: `18.38`
- concrete_order_volume_m3: `18.5`
- delivery_trips_raw: `2.055556`
- delivery_trips: `3`
- reinforcement_density_kg_per_m3: `45.71`

### insulation

- edge_insulation_height_m: `0.18`
- edge_insulation_height_source: `specification`
- edge_insulation_area_m2: `7.524`
- edge_and_beam_insulation_area_m2: `7.524`
- total_insulation_length_m: `41.8`
- eps100_required_volume_without_waste_m3: `0.7524`
- eps100_required_volume_with_waste_m3: `0.79002`
- eps100_packs_raw: `2.848972`
- eps100_packs_ordered: `3`
- eps100_order_volume_m3: `0.8319`
- foam_cans_raw: `0.7524`
- foam_cans_display_control: `0.75`
- foam_cans_ordered: `1`

### addons

- direct_cost_base_before_addons_raw: `692398.002`
- logistics_rate: `0.01`
- logistics_total_raw: `6923.98002`
- consumables_rate: `0.03`
- consumables_total_raw: `20771.94006`

## Estimate Lines

| # | code | name | unit | qty raw | qty display | material | work | total |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | `floor_slab_2_formwork_installation_control` | Монтаж опалубки под монолитное перекрытие 2-го этажа | м2 | 94 | 94 | 0 | 0 | 0 |
| 2 | `formwork_rental_set` | Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые) | м2 | 94 | 94 | 79 900 | 0 | 79 900 |
| 3 | `formwork_delivery_manipulator` | Доставка, вывоз опалубки манипулятором | маш | 2 | 2 | 40 000 | 0 | 40 000 |
| 4 | `crane_supply_formwork_rebar` | Подача опалубки, арматуры автокраном | смена | 2 | 2 | 60 000 | 0 | 60 000 |
| 5 | `formwork_consumables` | Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки) | - | 1 | 1 | 4 418 | 0 | 4 418 |
| 6 | `edge_formwork_installation_control` | Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты | м2 | 16.02 | 16.02 | 0 | 0 | 0 |
| 7 | `plywood_for_edges` | Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов | шт | 21 | 21 | 30 450 | 0 | 30 450 |
| 8 | `timber_for_formwork` | Пиломатериал обрезной для устройства опалубки ГОСТ | м3 | 0.8 | 0.8 | 17 222 | 0 | 17 222 |
| 9 | `rebar_frame_assembly_control` | Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры | мп | 1 263.6 | 1 263.6 | 0 | 0 | 0 |
| 10 | `rebar_a500_d16` | Арматура класса А500 диаметром 16 мм | мп | 70.2 | 70.2 | 5 657 | 0 | 5 657 |
| 11 | `rebar_a500_d10` | Арматура класса А500 диаметром 10 мм | мп | 1 193.4 | 1 193.4 | 39 048 | 0 | 39 048 |
| 12 | `concrete_placing_work` | Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300) | м3 | 17.5 | 17.5 | 0 | 210 000 | 210 000 |
| 13 | `beam_concreting_work` | Бетонирование балки бетоном марки В22,5 (М300) | м3 | 0 | 0 | 0 | 0 | 0 |
| 14 | `concrete_b22_5_m300_material` | Бетон марки В22,5 (М300) | м3 | 18.5 | 18.5 | 118 400 | 0 | 118 400 |
| 15 | `concrete_delivery` | Доставка бетона до объекта | рейс | 3 | 3 | 22 500 | 0 | 22 500 |
| 16 | `concrete_pump_32m` | Работа бетононасоса 32м + гаситель | смена | 1 | 1 | 38 000 | 0 | 38 000 |
| 17 | `formwork_dismantling_control` | Демонтаж опалубки после завершения бетонирования | м2 | 94 | 94 | 0 | 0 | 0 |
| 18 | `edge_insulation_work` | Устройство утепления по наружной стороне торцов плиты, балок | мп | 41.8 | 41.8 | 0 | 18 810 | 18 810 |
| 19 | `eps100_penoplex_material` | Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм | м3 | 0.83 | 0.83 | 7 504 | 0 | 7 504 |
| 20 | `eps_foam_glue` | Клей-пена для ЭППС | баллон | 1 | 1 | 490 | 0 | 490 |
| 21 | `logistics_and_supply` | Логистика, и снабжение | - | 1 | 1 | 6 924 | 0 | 6 924 |
| 22 | `consumables_tool_depreciation` | Расходные материалы, амортизация инструмента | комплект | 1 | 1 | 20 772 | 0 | 20 772 |
| 23 | `technical_supervision` | Технический надзор | - | 1 | 1 | 0 | 0 | 0 |
| 24 | `procurement_storage_costs` | Заготовительно-складские расходы | - | 1 | 1 | 0 | 0 | 0 |
| 25 | `overhead_general_business_costs` | Накладные и общехозяйственные расходы | - | 1 | 1 | 0 | 0 | 0 |
| 26 | `estimated_profit` | Сметная прибыль | - | 1 | 1 | 0 | 0 | 0 |

## Post-Line Explanations

### 1. Монтаж опалубки под монолитное перекрытие 2-го этажа

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `94.0` / `94.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 2. Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые)

- Тип строки: `materials`
- Количество raw/display: `94.0` / `94.0`
- Материалы raw/display: `79900.0` / `79900`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `79900.0` / `79900`

### 3. Доставка, вывоз опалубки манипулятором

- Тип строки: `logistics_machinery`
- Количество raw/display: `2.0` / `2.0`
- Материалы raw/display: `40000.0` / `40000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `40000.0` / `40000`
- Примечание: До 180 м2 включительно: 1 привоз + 1 вывоз = 2 рейса; более 180 м2: 2 привоза + 2 вывоза = 4 рейса.

### 4. Подача опалубки, арматуры автокраном

- Тип строки: `machinery`
- Количество raw/display: `2.0` / `2.0`
- Материалы raw/display: `60000.0` / `60000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `60000.0` / `60000`

### 5. Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки)

- Тип строки: `materials_consumables`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `4418.0` / `4418`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `4418.0` / `4418`

### 6. Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `16.02` / `16.02`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`
- Примечание: Production quantity uses edge_formwork_area_m2 + beams_formwork_area_m2 (or edge_and_beam_formwork_area_combined_m2) + beams_bottom_formwork_area_m2 from specification — same combined quantity as plywood/timber material.

### 7. Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов

- Тип строки: `materials`
- Количество raw/display: `21.0` / `21.0`
- Материалы raw/display: `30450.0` / `30450`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `30450.0` / `30450`

### 8. Пиломатериал обрезной для устройства опалубки ГОСТ

- Тип строки: `materials`
- Количество raw/display: `0.801` / `0.8`
- Материалы raw/display: `17221.5` / `17222`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `17221.5` / `17222`
- Примечание: Money is calculated from raw quantity 0.362, not displayed quantity 0.36.

### 9. Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `1263.6` / `1263.6`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 10. Арматура класса А500 диаметром 16 мм

- Тип строки: `materials`
- Количество raw/display: `70.2` / `70.2`
- Материалы raw/display: `5656.716` / `5657`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `5656.716` / `5657`

### 11. Арматура класса А500 диаметром 10 мм

- Тип строки: `materials`
- Количество raw/display: `1193.4` / `1193.4`
- Материалы raw/display: `39048.048` / `39048`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `39048.048` / `39048`

### 12. Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300)

- Тип строки: `work`
- Количество raw/display: `17.5` / `17.5`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `210000.0` / `210000`
- Итого raw/display: `210000.0` / `210000`

### 13. Бетонирование балки бетоном марки В22,5 (М300)

- Тип строки: `work`
- Количество raw/display: `0.0` / `0.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`
- Примечание: Quantity and total are 0 when no beams.items are given for this floor slab.

### 14. Бетон марки В22,5 (М300)

- Тип строки: `materials`
- Количество raw/display: `18.5` / `18.5`
- Материалы raw/display: `118400.0` / `118400`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `118400.0` / `118400`

### 15. Доставка бетона до объекта

- Тип строки: `logistics_machinery`
- Количество raw/display: `3.0` / `3.0`
- Материалы raw/display: `22500.0` / `22500`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `22500.0` / `22500`

### 16. Работа бетононасоса 32м + гаситель

- Тип строки: `machinery_fixed`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `38000.0` / `38000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `38000.0` / `38000`

### 17. Демонтаж опалубки после завершения бетонирования

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `94.0` / `94.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 18. Устройство утепления по наружной стороне торцов плиты, балок

- Тип строки: `work`
- Количество raw/display: `41.8` / `41.8`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `18810.0` / `18810`
- Итого raw/display: `18810.0` / `18810`
- Примечание: Quantity is slab_edge_perimeter_m plus the sum of beams.items length_m * count; equals slab_edge_perimeter_m alone when no beams.items are given.

### 19. Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм

- Тип строки: `materials`
- Количество raw/display: `0.8319` / `0.83`
- Материалы raw/display: `7503.738` / `7504`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `7503.738` / `7504`

### 20. Клей-пена для ЭППС

- Тип строки: `materials_consumables`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `490.0` / `490`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `490.0` / `490`

### 21. Логистика, и снабжение

- Тип строки: `materials_overhead_percent`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `6923.98002` / `6924`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `6923.98002` / `6924`

### 22. Расходные материалы, амортизация инструмента

- Тип строки: `materials_overhead_percent`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `20771.94006` / `20772`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `20771.94006` / `20772`

### 23. Технический надзор

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 24. Заготовительно-складские расходы

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 25. Накладные и общехозяйственные расходы

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 26. Сметная прибыль

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

## Totals

- internal_materials_total_raw: `491283.92208`
- internal_materials_total: `491284`
- internal_works_total_raw: `228810.0`
- internal_works_total: `228810`
- internal_section_total_raw: `720093.92208`
- internal_section_total: `720094`
- sum_of_displayed_line_material_totals: `491285`
- sum_of_displayed_line_work_totals: `228810`
- sum_of_displayed_line_totals: `720095`

## Warnings

- concrete_placing_volume_m3 is a manual/project quantity for this case; it is not derived from slab_area_m2 * slab thickness. If beams exist, this total is expected to already include beam concrete, same as floor_slab_1_calculator.
- edge_insulation_height_m = 0.18 m is confirmed by specification; 200 mm in the section title is considered a naming error.

## Comparison

- status: `ok`
- ok: `20`
- mismatch: `0`

| scope | code | field | expected | actual | status |
| --- | --- | --- | ---: | ---: | --- |
| calculation_blocks | `formwork.formwork_area_calc_method` | `formwork.formwork_area_calc_method` | spec_formwork_area | spec_formwork_area | ok |
| calculation_blocks | `formwork.main_formwork_area_m2` | `formwork.main_formwork_area_m2` | 94.0 | 94.0 | ok |
| calculation_blocks | `formwork.edge_formwork_area_m2` | `formwork.edge_formwork_area_m2` | None | None | ok |
| calculation_blocks | `formwork.beams_formwork_area_m2` | `formwork.beams_formwork_area_m2` | None | None | ok |
| calculation_blocks | `formwork.edge_and_beam_formwork_area_m2` | `formwork.edge_and_beam_formwork_area_m2` | 12.92 | 12.92 | ok |
| calculation_blocks | `formwork.beams_bottom_formwork_area_m2` | `formwork.beams_bottom_formwork_area_m2` | 3.1 | 3.1 | ok |
| calculation_blocks | `formwork.edge_beam_formwork_area_for_materials_m2` | `formwork.edge_beam_formwork_area_for_materials_m2` | 16.02 | 16.02 | ok |
| calculation_blocks | `formwork.edge_formwork_area_source` | `formwork.edge_formwork_area_source` | spec_formwork_area_combined_edge_and_beam | spec_formwork_area_combined_edge_and_beam | ok |
| calculation_blocks | `plywood_and_timber.edge_and_beam_formwork_area_m2` | `plywood_and_timber.edge_and_beam_formwork_area_m2` | 12.92 | 12.92 | ok |
| calculation_blocks | `plywood_and_timber.beams_bottom_formwork_area_m2` | `plywood_and_timber.beams_bottom_formwork_area_m2` | 3.1 | 3.1 | ok |
| calculation_blocks | `plywood_and_timber.edge_beam_formwork_area_for_materials_m2` | `plywood_and_timber.edge_beam_formwork_area_for_materials_m2` | 16.02 | 16.02 | ok |
| calculation_blocks | `plywood_and_timber.edge_plywood_sheets_raw` | `plywood_and_timber.edge_plywood_sheets_raw` | 6.965217 | 6.965217 | ok |
| calculation_blocks | `plywood_and_timber.base_plywood_sheets_raw` | `plywood_and_timber.base_plywood_sheets_raw` | 15.13913 | 15.13913 | ok |
| calculation_blocks | `plywood_and_timber.order_plywood_sheets_raw` | `plywood_and_timber.order_plywood_sheets_raw` | 20.13913 | 20.13913 | ok |
| calculation_blocks | `plywood_and_timber.plywood_sheets` | `plywood_and_timber.plywood_sheets` | 21 | 21 | ok |
| calculation_blocks | `plywood_and_timber.timber_volume_m3_raw` | `plywood_and_timber.timber_volume_m3_raw` | 0.801 | 0.801 | ok |
| calculation_blocks | `plywood_and_timber.timber_volume_m3_display` | `plywood_and_timber.timber_volume_m3_display` | 0.8 | 0.8 | ok |
| estimate_lines | `edge_formwork_installation_control` | `unit` | м2 | м2 | ok |
| estimate_lines | `edge_formwork_installation_control` | `quantity_raw` | 16.02 | 16.02 | ok |
| estimate_lines | `edge_formwork_installation_control` | `quantity_display` | 16.02 | 16.02 | ok |
