# Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 2-го этажа на отм. +4.680 (200мм)

## Inputs

- project_name: `test_floor_slab_2`
- slab_area_m2: `81.9`
- slab_edge_perimeter_m: `36.2`
- concrete_placing_volume_m3: `16.5`

## Calculation Blocks

## Площадь опалубки и геометрия

Legacy-режим `legacy_dimensions`: площадь плиты, периметр и площадь опалубки считаются от габаритов.

- `slab_area_m2 = slab_length_m * slab_width_m`
- `slab_edge_perimeter_m = 2 * (slab_length_m + slab_width_m)`
- `main_formwork_area_m2 = slab_area_m2`

- main_formwork_area_m2: `81.9`
- edge_formwork_area_m2: `7.24`
- beams_formwork_area_m2: `0.0`
- edge_and_beam_formwork_area_m2: `7.24`
- calculated_edge_formwork_area_m2: `7.24`
- edge_formwork_area_delta_m2: `0.0`
- slab_edge_perimeter_m: `36.2`
- calculated_slab_area_m2: `81.9`
- calculated_slab_edge_perimeter_m: `36.2`
- area_delta_m2: `0.0`
- formwork_area_delta_m2: `0.0`

## Доставка и вывоз опалубки

- Production-правило: до 180 м2 включительно — 2 рейса; более 180 м2 — 4 рейса.
- formwork_delivery_calc_method: `area_threshold`
- formwork_delivery_area_source_m2: `81.9`
- formwork_delivery_threshold_m2: `180.0`
- formwork_delivery_trips: `2.0`
- formwork_delivery_breakdown: `1 привоз + 1 вывоз`
- formwork_delivery_status: `calculated`

### geometry

- formwork_area_calc_method: `legacy_dimensions`
- formwork_area_source: `legacy_dimensions`
- edge_formwork_area_source: `legacy_dimensions`
- slab_edge_perimeter_source: `legacy_dimensions`
- slab_length_m: `9.0`
- slab_width_m: `9.1`
- slab_area_m2: `81.9`
- slab_edge_perimeter_m: `36.2`
- main_formwork_area_m2: `81.9`
- edge_formwork_area_m2: `7.24`
- beams_formwork_area_m2: `0.0`
- edge_and_beam_formwork_area_combined_m2: `None`
- edge_and_beam_formwork_area_m2: `7.24`
- calculated_edge_formwork_area_m2: `7.24`
- edge_formwork_area_delta_m2: `0.0`
- calculated_slab_area_m2: `81.9`
- calculated_slab_edge_perimeter_m: `36.2`
- input_slab_area_m2: `81.9`
- area_delta_m2: `0.0`
- formwork_area_delta_m2: `0.0`

### formwork

- formwork_area_calc_method: `legacy_dimensions`
- main_formwork_area_m2: `81.9`
- raw_supplier_rate: `840.781441`
- used_rate_per_m2: `850.0`
- edge_formwork_area_m2: `7.24`
- beams_formwork_area_m2: `0.0`
- edge_and_beam_formwork_area_m2: `7.24`
- beams_bottom_formwork_area_m2: `0.0`
- edge_beam_formwork_area_for_materials_m2: `7.24`
- calculated_edge_formwork_area_m2: `7.24`
- edge_formwork_area_delta_m2: `0.0`
- edge_formwork_area_source: `legacy_dimensions`
- formwork_delivery_calc_method: `area_threshold`
- formwork_delivery_area_source_m2: `81.9`
- formwork_delivery_threshold_m2: `180.0`
- formwork_delivery_trips: `2.0`
- formwork_delivery_breakdown: `1 привоз + 1 вывоз`
- formwork_delivery_status: `calculated`

### plywood_and_timber

- edge_and_beam_formwork_area_m2: `7.24`
- beams_bottom_formwork_area_m2: `0.0`
- edge_beam_formwork_area_for_materials_m2: `7.24`
- edge_plywood_sheets_raw: `3.147826`
- non_multiple_places_area_m2: `16.38`
- non_multiple_places_plywood_sheets_raw: `7.121739`
- base_plywood_sheets_raw: `10.269565`
- order_plywood_sheets_raw: `15.269565`
- plywood_sheets: `16`
- timber_volume_m3_raw: `0.362`
- timber_volume_m3_display: `0.36`

### beams

- items: 0 items
- items_count: `0`
- items_total_length_m: `0.0`
- items_total_concrete_volume_m3: `0.0`
- items_total_formwork_area_m2: `0.0`
- items_total_eps_material_area_m2: `0.0`
- items_total_eps_work_length_m: `0.0`
- eps_work_length_source: `not_provided`
- eps_material_area_source: `not_provided`
- concrete_volume_source: `calculated_from_beam_items`
- calculated_concrete_volume_m3: `0.0`
- concrete_volume_delta_m3: `None`
- notes: `['All values are 0 when no beams.items are given. Beam concrete is subtracted from concrete_placing_volume_m3 for the slab work line and priced separately on the beam_concreting_work estimate line. beams_formwork_area_m2 and the insulation length/area both use this data when their own scalar inputs are absent.']`

### rebar

- rebar_calc_method: `legacy_weight_kg`
- items: 3 items
- total_rebar_order_length_m: `2819.7`
- total_rebar_order_weight_kg: `1850.6709`
- total_rebar_weight_with_waste_kg: `1825.39`

### concrete

- concrete_placing_volume_m3: `16.5`
- slab_concrete_volume_m3: `16.5`
- beams_concrete_volume_m3: `0.0`
- concrete_volume_with_waste_raw_m3: `17.325`
- concrete_volume_with_waste_display_m3: `17.33`
- concrete_order_volume_m3: `17.5`
- delivery_trips_raw: `1.944444`
- delivery_trips: `2`
- reinforcement_density_kg_per_m3: `105.36`

### insulation

- edge_insulation_height_m: `0.18`
- edge_insulation_height_source: `specification`
- edge_insulation_area_m2: `6.516`
- edge_and_beam_insulation_area_m2: `6.516`
- bottom_slab_eps_work_area_m2: `0.0`
- bottom_slab_eps_volume_m3: `0.0`
- total_insulation_length_m: `36.2`
- eps100_required_volume_without_waste_m3: `0.6516`
- eps100_required_volume_with_waste_m3: `0.68418`
- eps100_packs_raw: `2.467292`
- eps100_packs_ordered: `3`
- eps100_order_volume_m3: `0.8319`
- foam_cans_raw: `0.6516`
- foam_cans_display_control: `0.65`
- foam_cans_ordered: `1`

### addons

- direct_cost_base_before_addons_raw: `689472.487`
- logistics_rate: `0.01`
- logistics_total_raw: `6894.72487`
- consumables_rate: `0.03`
- consumables_total_raw: `20684.17461`

## Estimate Lines

| # | code | name | unit | qty raw | qty display | material | work | total |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | `floor_slab_2_formwork_installation_control` | Монтаж опалубки под монолитное перекрытие 2-го этажа | м2 | 81.9 | 81.9 | 0 | 0 | 0 |
| 2 | `formwork_rental_set` | Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые) | м2 | 81.9 | 81.9 | 69 615 | 0 | 69 615 |
| 3 | `formwork_delivery_manipulator` | Доставка, вывоз опалубки манипулятором | маш | 2 | 2 | 40 000 | 0 | 40 000 |
| 4 | `crane_supply_formwork_rebar` | Подача опалубки, арматуры автокраном | смена | 2 | 2 | 60 000 | 0 | 60 000 |
| 5 | `rebar_metal_delivery` | Доставка арматуры, металла | маш | 0 | 0 | 0 | 0 | 0 |
| 6 | `formwork_consumables` | Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки) | - | 1 | 1 | 3 849 | 0 | 3 849 |
| 7 | `edge_formwork_installation_control` | Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты | м2 | 7.24 | 7.24 | 0 | 0 | 0 |
| 8 | `plywood_for_edges` | Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов | шт | 16 | 16 | 23 200 | 0 | 23 200 |
| 9 | `timber_for_formwork` | Пиломатериал обрезной для устройства опалубки ГОСТ | м3 | 0.36 | 0.36 | 7 783 | 0 | 7 783 |
| 10 | `rebar_frame_assembly_control` | Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры | мп | 2 819.7 | 2 819.7 | 0 | 0 | 0 |
| 11 | `rebar_a500_d16` | Арматура класса А500 диаметром 16 мм | мп | 105.3 | 105.3 | 8 485 | 0 | 8 485 |
| 12 | `rebar_a500_d12` | Арматура класса А500 диаметром 12 мм | мп | 35.1 | 35.1 | 1 590 | 0 | 1 590 |
| 13 | `rebar_a500_d10` | Арматура класса А500 диаметром 10 мм | мп | 2 679.3 | 2 679.3 | 87 667 | 0 | 87 667 |
| 14 | `concrete_placing_work` | Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300) | м3 | 16.5 | 16.5 | 0 | 198 000 | 198 000 |
| 15 | `beam_concreting_work` | Бетонирование балки бетоном марки В22,5 (М300) | мп | 0 | 0 | 0 | 0 | 0 |
| 16 | `concrete_b22_5_m300_material` | Бетон марки В22,5 (М300) | м3 | 17.5 | 17.5 | 112 000 | 0 | 112 000 |
| 17 | `concrete_delivery` | Доставка бетона до объекта | рейс | 2 | 2 | 15 000 | 0 | 15 000 |
| 18 | `concrete_pump_32m` | Работа бетононасоса 32м + гаситель | смена | 1 | 1 | 38 000 | 0 | 38 000 |
| 19 | `formwork_dismantling_control` | Демонтаж опалубки после завершения бетонирования | м2 | 81.9 | 81.9 | 0 | 0 | 0 |
| 20 | `edge_insulation_work` | Устройство утепления по наружной стороне торцов плиты, балок | мп | 36.2 | 36.2 | 0 | 16 290 | 16 290 |
| 21 | `bottom_slab_insulation_work` | Устройство утепления низа плиты | м2 | 0 | 0 | 0 | 0 | 0 |
| 22 | `eps100_penoplex_material` | Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм | м3 | 0.83 | 0.83 | 7 504 | 0 | 7 504 |
| 23 | `eps_foam_glue` | Клей-пена для ЭППС | баллон | 1 | 1 | 490 | 0 | 490 |
| 24 | `logistics_and_supply` | Логистика, и снабжение | - | 1 | 1 | 6 895 | 0 | 6 895 |
| 25 | `consumables_tool_depreciation` | Расходные материалы, амортизация инструмента | комплект | 1 | 1 | 20 684 | 0 | 20 684 |
| 26 | `technical_supervision` | Технический надзор | - | 1 | 1 | 0 | 0 | 0 |
| 27 | `procurement_storage_costs` | Заготовительно-складские расходы | - | 1 | 1 | 0 | 0 | 0 |
| 28 | `overhead_general_business_costs` | Накладные и общехозяйственные расходы | - | 1 | 1 | 0 | 0 | 0 |
| 29 | `estimated_profit` | Сметная прибыль | - | 1 | 1 | 0 | 0 | 0 |

## Post-Line Explanations

### 1. Монтаж опалубки под монолитное перекрытие 2-го этажа

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `81.9` / `81.9`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 2. Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые)

- Тип строки: `materials`
- Количество raw/display: `81.9` / `81.9`
- Материалы raw/display: `69615.0` / `69615`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `69615.0` / `69615`

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

### 5. Доставка арматуры, металла

- Тип строки: `logistics_machinery`
- Количество raw/display: `0.0` / `0.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`
- Примечание: Количество машин — с уровня коробки (box-калькулятор, накопление 10 т по всем разделам с арматурой).

### 6. Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки)

- Тип строки: `materials_consumables`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `3849.3` / `3849`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `3849.3` / `3849`

### 7. Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `7.24` / `7.24`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`
- Примечание: Production quantity uses edge_formwork_area_m2 + beams_formwork_area_m2 (or edge_and_beam_formwork_area_combined_m2) + beams_bottom_formwork_area_m2 from specification — same combined quantity as plywood/timber material.

### 8. Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов

- Тип строки: `materials`
- Количество raw/display: `16.0` / `16.0`
- Материалы raw/display: `23200.0` / `23200`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `23200.0` / `23200`

### 9. Пиломатериал обрезной для устройства опалубки ГОСТ

- Тип строки: `materials`
- Количество raw/display: `0.362` / `0.36`
- Материалы raw/display: `7783.0` / `7783`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `7783.0` / `7783`
- Примечание: Money is calculated from raw quantity 0.362, not displayed quantity 0.36.

### 10. Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `2819.7` / `2819.7`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 11. Арматура класса А500 диаметром 16 мм

- Тип строки: `materials`
- Количество raw/display: `105.3` / `105.3`
- Материалы raw/display: `8485.074` / `8485`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `8485.074` / `8485`

### 12. Арматура класса А500 диаметром 12 мм

- Тип строки: `materials`
- Количество raw/display: `35.1` / `35.1`
- Материалы raw/display: `1589.679` / `1590`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `1589.679` / `1590`

### 13. Арматура класса А500 диаметром 10 мм

- Тип строки: `materials`
- Количество raw/display: `2679.3` / `2679.3`
- Материалы raw/display: `87666.696` / `87667`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `87666.696` / `87667`

### 14. Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300)

- Тип строки: `work`
- Количество raw/display: `16.5` / `16.5`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `198000.0` / `198000`
- Итого raw/display: `198000.0` / `198000`

### 15. Бетонирование балки бетоном марки В22,5 (М300)

- Тип строки: `work`
- Количество raw/display: `0.0` / `0.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`
- Примечание: С 2026-07-28 работа по бетонированию балок считается по длине балок, а не по объему бетона.
- Примечание: Quantity and total are 0 when no beams.items are given for this floor slab.

### 16. Бетон марки В22,5 (М300)

- Тип строки: `materials`
- Количество raw/display: `17.5` / `17.5`
- Материалы raw/display: `112000.0` / `112000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `112000.0` / `112000`

### 17. Доставка бетона до объекта

- Тип строки: `logistics_machinery`
- Количество raw/display: `2.0` / `2.0`
- Материалы raw/display: `15000.0` / `15000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `15000.0` / `15000`

### 18. Работа бетононасоса 32м + гаситель

- Тип строки: `machinery_fixed`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `38000.0` / `38000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `38000.0` / `38000`

### 19. Демонтаж опалубки после завершения бетонирования

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `81.9` / `81.9`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 20. Устройство утепления по наружной стороне торцов плиты, балок

- Тип строки: `work`
- Количество raw/display: `36.2` / `36.2`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `16290.0` / `16290`
- Итого raw/display: `16290.0` / `16290`
- Примечание: Quantity is slab_edge_perimeter_m plus beams_eps_work_length_m when the project explicitly gives insulated beam length; beam length is not inferred from beam_items.

### 21. Устройство утепления низа плиты

- Тип строки: `work`
- Количество raw/display: `0.0` / `0.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`
- Примечание: Optional production quantity from PDF: horizontal/bottom EPS insulation area of the slab itself. Defaults to 0 when the project has no such separate line.

### 22. Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм

- Тип строки: `materials`
- Количество raw/display: `0.8319` / `0.83`
- Материалы raw/display: `7503.738` / `7504`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `7503.738` / `7504`

### 23. Клей-пена для ЭППС

- Тип строки: `materials_consumables`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `490.0` / `490`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `490.0` / `490`

### 24. Логистика, и снабжение

- Тип строки: `materials_overhead_percent`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `6894.72487` / `6895`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `6894.72487` / `6895`

### 25. Расходные материалы, амортизация инструмента

- Тип строки: `materials_overhead_percent`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `20684.17461` / `20684`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `20684.17461` / `20684`

### 26. Технический надзор

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 27. Заготовительно-складские расходы

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 28. Накладные и общехозяйственные расходы

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 29. Сметная прибыль

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

## Totals

- internal_materials_total_raw: `502761.38648`
- internal_materials_total: `502761`
- internal_works_total_raw: `214290.0`
- internal_works_total: `214290`
- internal_section_total_raw: `717051.38648`
- internal_section_total: `717051`
- sum_of_displayed_line_material_totals: `502762`
- sum_of_displayed_line_work_totals: `214290`
- sum_of_displayed_line_totals: `717052`

## Warnings

- concrete_placing_volume_m3 is a manual/project quantity for this case; it is not derived from slab_area_m2 * slab thickness. If beams exist, this total is expected to already include beam concrete, same as floor_slab_1_calculator.
- edge_insulation_height_m = 0.18 m is confirmed by specification; 200 mm in the section title is considered a naming error.

## Comparison

- status: `ok`
- ok: `222`
- mismatch: `0`

| scope | code | field | expected | actual | status |
| --- | --- | --- | ---: | ---: | --- |
| totals | `internal_materials_total_raw` | `internal_materials_total_raw` | 502761.38648 | 502761.38648 | ok |
| totals | `internal_materials_total` | `internal_materials_total` | 502761 | 502761 | ok |
| totals | `internal_works_total_raw` | `internal_works_total_raw` | 214290 | 214290.0 | ok |
| totals | `internal_works_total` | `internal_works_total` | 214290 | 214290 | ok |
| totals | `internal_section_total_raw` | `internal_section_total_raw` | 717051.38648 | 717051.38648 | ok |
| totals | `internal_section_total` | `internal_section_total` | 717051 | 717051 | ok |
| totals | `sum_of_displayed_line_material_totals` | `sum_of_displayed_line_material_totals` | 502762 | 502762 | ok |
| totals | `sum_of_displayed_line_work_totals` | `sum_of_displayed_line_work_totals` | 214290 | 214290 | ok |
| totals | `sum_of_displayed_line_totals` | `sum_of_displayed_line_totals` | 717052 | 717052 | ok |
| estimate_lines | `floor_slab_2_formwork_installation_control` | `name` | Монтаж опалубки под монолитное перекрытие 2-го этажа | Монтаж опалубки под монолитное перекрытие 2-го этажа | ok |
| estimate_lines | `floor_slab_2_formwork_installation_control` | `unit` | м2 | м2 | ok |
| estimate_lines | `floor_slab_2_formwork_installation_control` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `floor_slab_2_formwork_installation_control` | `quantity_raw` | 81.9 | 81.9 | ok |
| estimate_lines | `floor_slab_2_formwork_installation_control` | `quantity_display` | 81.9 | 81.9 | ok |
| estimate_lines | `floor_slab_2_formwork_installation_control` | `material_total` | 0 | 0 | ok |
| estimate_lines | `floor_slab_2_formwork_installation_control` | `work_total` | 0 | 0 | ok |
| estimate_lines | `floor_slab_2_formwork_installation_control` | `line_total` | 0 | 0 | ok |
| estimate_lines | `formwork_rental_set` | `name` | Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые) | Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые) | ok |
| estimate_lines | `formwork_rental_set` | `unit` | м2 | м2 | ok |
| estimate_lines | `formwork_rental_set` | `line_type` | materials | materials | ok |
| estimate_lines | `formwork_rental_set` | `quantity_raw` | 81.9 | 81.9 | ok |
| estimate_lines | `formwork_rental_set` | `quantity_display` | 81.9 | 81.9 | ok |
| estimate_lines | `formwork_rental_set` | `material_unit_price` | 850 | 850.0 | ok |
| estimate_lines | `formwork_rental_set` | `material_total` | 69615 | 69615 | ok |
| estimate_lines | `formwork_rental_set` | `work_total` | 0 | 0 | ok |
| estimate_lines | `formwork_rental_set` | `line_total` | 69615 | 69615 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `name` | Доставка, вывоз опалубки манипулятором | Доставка, вывоз опалубки манипулятором | ok |
| estimate_lines | `formwork_delivery_manipulator` | `unit` | маш | маш | ok |
| estimate_lines | `formwork_delivery_manipulator` | `line_type` | logistics_machinery | logistics_machinery | ok |
| estimate_lines | `formwork_delivery_manipulator` | `quantity_raw` | 2 | 2.0 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `quantity_display` | 2 | 2.0 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `material_unit_price` | 20000 | 20000.0 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `material_total` | 40000 | 40000 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `line_total` | 40000 | 40000 | ok |
| estimate_lines | `crane_supply_formwork_rebar` | `name` | Подача опалубки, арматуры автокраном | Подача опалубки, арматуры автокраном | ok |
| estimate_lines | `crane_supply_formwork_rebar` | `unit` | смена | смена | ok |
| estimate_lines | `crane_supply_formwork_rebar` | `line_type` | machinery | machinery | ok |
| estimate_lines | `crane_supply_formwork_rebar` | `quantity_raw` | 2 | 2.0 | ok |
| estimate_lines | `crane_supply_formwork_rebar` | `quantity_display` | 2 | 2.0 | ok |
| estimate_lines | `crane_supply_formwork_rebar` | `material_unit_price` | 30000 | 30000.0 | ok |
| estimate_lines | `crane_supply_formwork_rebar` | `material_total` | 60000 | 60000 | ok |
| estimate_lines | `crane_supply_formwork_rebar` | `line_total` | 60000 | 60000 | ok |
| estimate_lines | `formwork_consumables` | `name` | Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки) | Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки) | ok |
| estimate_lines | `formwork_consumables` | `unit` | - | - | ok |
| estimate_lines | `formwork_consumables` | `line_type` | materials_consumables | materials_consumables | ok |
| estimate_lines | `formwork_consumables` | `quantity_raw` | 1 | 1.0 | ok |
| estimate_lines | `formwork_consumables` | `quantity_display` | 1 | 1.0 | ok |
| estimate_lines | `formwork_consumables` | `material_total_raw` | 3849.3 | 3849.3 | ok |
| estimate_lines | `formwork_consumables` | `material_total` | 3849 | 3849 | ok |
| estimate_lines | `formwork_consumables` | `line_total` | 3849 | 3849 | ok |
| estimate_lines | `edge_formwork_installation_control` | `name` | Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты | Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты | ok |
| estimate_lines | `edge_formwork_installation_control` | `unit` | м2 | м2 | ok |
| estimate_lines | `edge_formwork_installation_control` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `edge_formwork_installation_control` | `quantity_raw` | 7.24 | 7.24 | ok |
| estimate_lines | `edge_formwork_installation_control` | `quantity_display` | 7.24 | 7.24 | ok |
| estimate_lines | `edge_formwork_installation_control` | `material_total` | 0 | 0 | ok |
| estimate_lines | `edge_formwork_installation_control` | `work_total` | 0 | 0 | ok |
| estimate_lines | `edge_formwork_installation_control` | `line_total` | 0 | 0 | ok |
| estimate_lines | `plywood_for_edges` | `name` | Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов | Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов | ok |
| estimate_lines | `plywood_for_edges` | `unit` | шт | шт | ok |
| estimate_lines | `plywood_for_edges` | `line_type` | materials | materials | ok |
| estimate_lines | `plywood_for_edges` | `quantity_raw` | 16 | 16.0 | ok |
| estimate_lines | `plywood_for_edges` | `quantity_display` | 16 | 16.0 | ok |
| estimate_lines | `plywood_for_edges` | `material_unit_price` | 1450 | 1450.0 | ok |
| estimate_lines | `plywood_for_edges` | `material_total` | 23200 | 23200 | ok |
| estimate_lines | `plywood_for_edges` | `line_total` | 23200 | 23200 | ok |
| estimate_lines | `timber_for_formwork` | `name` | Пиломатериал обрезной для устройства опалубки ГОСТ | Пиломатериал обрезной для устройства опалубки ГОСТ | ok |
| estimate_lines | `timber_for_formwork` | `unit` | м3 | м3 | ok |
| estimate_lines | `timber_for_formwork` | `line_type` | materials | materials | ok |
| estimate_lines | `timber_for_formwork` | `quantity_raw` | 0.362 | 0.362 | ok |
| estimate_lines | `timber_for_formwork` | `quantity_display` | 0.36 | 0.36 | ok |
| estimate_lines | `timber_for_formwork` | `material_unit_price` | 21500 | 21500.0 | ok |
| estimate_lines | `timber_for_formwork` | `material_total` | 7783 | 7783 | ok |
| estimate_lines | `timber_for_formwork` | `line_total` | 7783 | 7783 | ok |
| estimate_lines | `rebar_frame_assembly_control` | `name` | Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры | Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры | ok |
| estimate_lines | `rebar_frame_assembly_control` | `unit` | мп | мп | ok |
| estimate_lines | `rebar_frame_assembly_control` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `rebar_frame_assembly_control` | `quantity_raw` | 2819.7 | 2819.7 | ok |
| estimate_lines | `rebar_frame_assembly_control` | `quantity_display` | 2819.7 | 2819.7 | ok |
| estimate_lines | `rebar_frame_assembly_control` | `material_total` | 0 | 0 | ok |
| estimate_lines | `rebar_frame_assembly_control` | `work_total` | 0 | 0 | ok |
| estimate_lines | `rebar_frame_assembly_control` | `line_total` | 0 | 0 | ok |
| estimate_lines | `rebar_a500_d16` | `name` | Арматура класса А500 диаметром 16 мм | Арматура класса А500 диаметром 16 мм | ok |
| estimate_lines | `rebar_a500_d16` | `unit` | мп | мп | ok |
| estimate_lines | `rebar_a500_d16` | `line_type` | materials | materials | ok |
| estimate_lines | `rebar_a500_d16` | `quantity_raw` | 105.3 | 105.3 | ok |
| estimate_lines | `rebar_a500_d16` | `quantity_display` | 105.3 | 105.3 | ok |
| estimate_lines | `rebar_a500_d16` | `material_unit_price` | 80.58 | 80.58 | ok |
| estimate_lines | `rebar_a500_d16` | `material_total_raw` | 8485.074 | 8485.074 | ok |
| estimate_lines | `rebar_a500_d16` | `material_total` | 8485 | 8485 | ok |
| estimate_lines | `rebar_a500_d16` | `line_total` | 8485 | 8485 | ok |
| estimate_lines | `rebar_a500_d12` | `name` | Арматура класса А500 диаметром 12 мм | Арматура класса А500 диаметром 12 мм | ok |
| estimate_lines | `rebar_a500_d12` | `unit` | мп | мп | ok |
| estimate_lines | `rebar_a500_d12` | `line_type` | materials | materials | ok |
| estimate_lines | `rebar_a500_d12` | `quantity_raw` | 35.1 | 35.1 | ok |
| estimate_lines | `rebar_a500_d12` | `quantity_display` | 35.1 | 35.1 | ok |
| estimate_lines | `rebar_a500_d12` | `material_unit_price` | 45.29 | 45.29 | ok |
| estimate_lines | `rebar_a500_d12` | `material_total_raw` | 1589.679 | 1589.679 | ok |
| estimate_lines | `rebar_a500_d12` | `material_total` | 1590 | 1590 | ok |
| estimate_lines | `rebar_a500_d12` | `line_total` | 1590 | 1590 | ok |
| estimate_lines | `rebar_a500_d10` | `name` | Арматура класса А500 диаметром 10 мм | Арматура класса А500 диаметром 10 мм | ok |
| estimate_lines | `rebar_a500_d10` | `unit` | мп | мп | ok |
| estimate_lines | `rebar_a500_d10` | `line_type` | materials | materials | ok |
| estimate_lines | `rebar_a500_d10` | `quantity_raw` | 2679.3 | 2679.3 | ok |
| estimate_lines | `rebar_a500_d10` | `quantity_display` | 2679.3 | 2679.3 | ok |
| estimate_lines | `rebar_a500_d10` | `material_unit_price` | 32.72 | 32.72 | ok |
| estimate_lines | `rebar_a500_d10` | `material_total_raw` | 87666.696 | 87666.696 | ok |
| estimate_lines | `rebar_a500_d10` | `material_total` | 87667 | 87667 | ok |
| estimate_lines | `rebar_a500_d10` | `line_total` | 87667 | 87667 | ok |
| estimate_lines | `concrete_placing_work` | `name` | Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300) | Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300) | ok |
| estimate_lines | `concrete_placing_work` | `unit` | м3 | м3 | ok |
| estimate_lines | `concrete_placing_work` | `line_type` | work | work | ok |
| estimate_lines | `concrete_placing_work` | `quantity_raw` | 16.5 | 16.5 | ok |
| estimate_lines | `concrete_placing_work` | `quantity_display` | 16.5 | 16.5 | ok |
| estimate_lines | `concrete_placing_work` | `work_unit_price` | 12000 | 12000.0 | ok |
| estimate_lines | `concrete_placing_work` | `work_total` | 198000 | 198000 | ok |
| estimate_lines | `concrete_placing_work` | `line_total` | 198000 | 198000 | ok |
| estimate_lines | `concrete_b22_5_m300_material` | `name` | Бетон марки В22,5 (М300) | Бетон марки В22,5 (М300) | ok |
| estimate_lines | `concrete_b22_5_m300_material` | `unit` | м3 | м3 | ok |
| estimate_lines | `concrete_b22_5_m300_material` | `line_type` | materials | materials | ok |
| estimate_lines | `concrete_b22_5_m300_material` | `quantity_raw` | 17.5 | 17.5 | ok |
| estimate_lines | `concrete_b22_5_m300_material` | `quantity_display` | 17.5 | 17.5 | ok |
| estimate_lines | `concrete_b22_5_m300_material` | `material_unit_price` | 6400 | 6400.0 | ok |
| estimate_lines | `concrete_b22_5_m300_material` | `material_total` | 112000 | 112000 | ok |
| estimate_lines | `concrete_b22_5_m300_material` | `line_total` | 112000 | 112000 | ok |
| estimate_lines | `concrete_delivery` | `name` | Доставка бетона до объекта | Доставка бетона до объекта | ok |
| estimate_lines | `concrete_delivery` | `unit` | рейс | рейс | ok |
| estimate_lines | `concrete_delivery` | `line_type` | logistics_machinery | logistics_machinery | ok |
| estimate_lines | `concrete_delivery` | `quantity_raw` | 2 | 2.0 | ok |
| estimate_lines | `concrete_delivery` | `quantity_display` | 2 | 2.0 | ok |
| estimate_lines | `concrete_delivery` | `material_unit_price` | 7500 | 7500.0 | ok |
| estimate_lines | `concrete_delivery` | `material_total` | 15000 | 15000 | ok |
| estimate_lines | `concrete_delivery` | `line_total` | 15000 | 15000 | ok |
| estimate_lines | `concrete_pump_32m` | `name` | Работа бетононасоса 32м + гаситель | Работа бетононасоса 32м + гаситель | ok |
| estimate_lines | `concrete_pump_32m` | `unit` | смена | смена | ok |
| estimate_lines | `concrete_pump_32m` | `line_type` | machinery_fixed | machinery_fixed | ok |
| estimate_lines | `concrete_pump_32m` | `quantity_raw` | 1 | 1.0 | ok |
| estimate_lines | `concrete_pump_32m` | `quantity_display` | 1 | 1.0 | ok |
| estimate_lines | `concrete_pump_32m` | `material_unit_price` | 38000 | 38000.0 | ok |
| estimate_lines | `concrete_pump_32m` | `material_total` | 38000 | 38000 | ok |
| estimate_lines | `concrete_pump_32m` | `line_total` | 38000 | 38000 | ok |
| estimate_lines | `formwork_dismantling_control` | `name` | Демонтаж опалубки после завершения бетонирования | Демонтаж опалубки после завершения бетонирования | ok |
| estimate_lines | `formwork_dismantling_control` | `unit` | м2 | м2 | ok |
| estimate_lines | `formwork_dismantling_control` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `formwork_dismantling_control` | `quantity_raw` | 81.9 | 81.9 | ok |
| estimate_lines | `formwork_dismantling_control` | `quantity_display` | 81.9 | 81.9 | ok |
| estimate_lines | `formwork_dismantling_control` | `material_total` | 0 | 0 | ok |
| estimate_lines | `formwork_dismantling_control` | `work_total` | 0 | 0 | ok |
| estimate_lines | `formwork_dismantling_control` | `line_total` | 0 | 0 | ok |
| estimate_lines | `edge_insulation_work` | `name` | Устройство утепления по наружной стороне торцов плиты, балок | Устройство утепления по наружной стороне торцов плиты, балок | ok |
| estimate_lines | `edge_insulation_work` | `unit` | мп | мп | ok |
| estimate_lines | `edge_insulation_work` | `line_type` | work | work | ok |
| estimate_lines | `edge_insulation_work` | `quantity_raw` | 36.2 | 36.2 | ok |
| estimate_lines | `edge_insulation_work` | `quantity_display` | 36.2 | 36.2 | ok |
| estimate_lines | `edge_insulation_work` | `work_unit_price` | 450 | 450.0 | ok |
| estimate_lines | `edge_insulation_work` | `work_total` | 16290 | 16290 | ok |
| estimate_lines | `edge_insulation_work` | `line_total` | 16290 | 16290 | ok |
| estimate_lines | `eps100_penoplex_material` | `name` | Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм | Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм | ok |
| estimate_lines | `eps100_penoplex_material` | `unit` | м3 | м3 | ok |
| estimate_lines | `eps100_penoplex_material` | `line_type` | materials | materials | ok |
| estimate_lines | `eps100_penoplex_material` | `quantity_raw` | 0.8319 | 0.8319 | ok |
| estimate_lines | `eps100_penoplex_material` | `quantity_display` | 0.83 | 0.83 | ok |
| estimate_lines | `eps100_penoplex_material` | `material_unit_price` | 9020 | 9020.0 | ok |
| estimate_lines | `eps100_penoplex_material` | `material_total_raw` | 7503.738 | 7503.738 | ok |
| estimate_lines | `eps100_penoplex_material` | `material_total` | 7504 | 7504 | ok |
| estimate_lines | `eps100_penoplex_material` | `line_total` | 7504 | 7504 | ok |
| estimate_lines | `eps_foam_glue` | `name` | Клей-пена для ЭППС | Клей-пена для ЭППС | ok |
| estimate_lines | `eps_foam_glue` | `unit` | баллон | баллон | ok |
| estimate_lines | `eps_foam_glue` | `line_type` | materials_consumables | materials_consumables | ok |
| estimate_lines | `eps_foam_glue` | `quantity_raw` | 1 | 1.0 | ok |
| estimate_lines | `eps_foam_glue` | `quantity_display` | 1 | 1.0 | ok |
| estimate_lines | `eps_foam_glue` | `material_unit_price` | 490 | 490.0 | ok |
| estimate_lines | `eps_foam_glue` | `material_total` | 490 | 490 | ok |
| estimate_lines | `eps_foam_glue` | `line_total` | 490 | 490 | ok |
| estimate_lines | `logistics_and_supply` | `name` | Логистика, и снабжение | Логистика, и снабжение | ok |
| estimate_lines | `logistics_and_supply` | `unit` | - | - | ok |
| estimate_lines | `logistics_and_supply` | `line_type` | materials_overhead_percent | materials_overhead_percent | ok |
| estimate_lines | `logistics_and_supply` | `quantity_raw` | 1 | 1.0 | ok |
| estimate_lines | `logistics_and_supply` | `quantity_display` | 1 | 1.0 | ok |
| estimate_lines | `logistics_and_supply` | `material_total_raw` | 6894.72487 | 6894.72487 | ok |
| estimate_lines | `logistics_and_supply` | `material_total` | 6895 | 6895 | ok |
| estimate_lines | `logistics_and_supply` | `line_total` | 6895 | 6895 | ok |
| estimate_lines | `consumables_tool_depreciation` | `name` | Расходные материалы, амортизация инструмента | Расходные материалы, амортизация инструмента | ok |
| estimate_lines | `consumables_tool_depreciation` | `unit` | комплект | комплект | ok |
| estimate_lines | `consumables_tool_depreciation` | `line_type` | materials_overhead_percent | materials_overhead_percent | ok |
| estimate_lines | `consumables_tool_depreciation` | `quantity_raw` | 1 | 1.0 | ok |
| estimate_lines | `consumables_tool_depreciation` | `quantity_display` | 1 | 1.0 | ok |
| estimate_lines | `consumables_tool_depreciation` | `material_total_raw` | 20684.17461 | 20684.17461 | ok |
| estimate_lines | `consumables_tool_depreciation` | `material_total` | 20684 | 20684 | ok |
| estimate_lines | `consumables_tool_depreciation` | `line_total` | 20684 | 20684 | ok |
| estimate_lines | `technical_supervision` | `name` | Технический надзор | Технический надзор | ok |
| estimate_lines | `technical_supervision` | `unit` | - | - | ok |
| estimate_lines | `technical_supervision` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `technical_supervision` | `quantity_raw` | 1 | 1.0 | ok |
| estimate_lines | `technical_supervision` | `quantity_display` | 1 | 1.0 | ok |
| estimate_lines | `technical_supervision` | `material_total` | 0 | 0 | ok |
| estimate_lines | `technical_supervision` | `work_total` | 0 | 0 | ok |
| estimate_lines | `technical_supervision` | `line_total` | 0 | 0 | ok |
| estimate_lines | `procurement_storage_costs` | `name` | Заготовительно-складские расходы | Заготовительно-складские расходы | ok |
| estimate_lines | `procurement_storage_costs` | `unit` | - | - | ok |
| estimate_lines | `procurement_storage_costs` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `procurement_storage_costs` | `quantity_raw` | 1 | 1.0 | ok |
| estimate_lines | `procurement_storage_costs` | `quantity_display` | 1 | 1.0 | ok |
| estimate_lines | `procurement_storage_costs` | `material_total` | 0 | 0 | ok |
| estimate_lines | `procurement_storage_costs` | `work_total` | 0 | 0 | ok |
| estimate_lines | `procurement_storage_costs` | `line_total` | 0 | 0 | ok |
| estimate_lines | `overhead_general_business_costs` | `name` | Накладные и общехозяйственные расходы | Накладные и общехозяйственные расходы | ok |
| estimate_lines | `overhead_general_business_costs` | `unit` | - | - | ok |
| estimate_lines | `overhead_general_business_costs` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `overhead_general_business_costs` | `quantity_raw` | 1 | 1.0 | ok |
| estimate_lines | `overhead_general_business_costs` | `quantity_display` | 1 | 1.0 | ok |
| estimate_lines | `overhead_general_business_costs` | `material_total` | 0 | 0 | ok |
| estimate_lines | `overhead_general_business_costs` | `work_total` | 0 | 0 | ok |
| estimate_lines | `overhead_general_business_costs` | `line_total` | 0 | 0 | ok |
| estimate_lines | `estimated_profit` | `name` | Сметная прибыль | Сметная прибыль | ok |
| estimate_lines | `estimated_profit` | `unit` | - | - | ok |
| estimate_lines | `estimated_profit` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `estimated_profit` | `quantity_raw` | 1 | 1.0 | ok |
| estimate_lines | `estimated_profit` | `quantity_display` | 1 | 1.0 | ok |
| estimate_lines | `estimated_profit` | `material_total` | 0 | 0 | ok |
| estimate_lines | `estimated_profit` | `work_total` | 0 | 0 | ok |
| estimate_lines | `estimated_profit` | `line_total` | 0 | 0 | ok |
