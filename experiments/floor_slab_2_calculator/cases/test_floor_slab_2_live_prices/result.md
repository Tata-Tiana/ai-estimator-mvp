# Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 2-го этажа на отм. +4.680 (200мм)

## Inputs

- project_name: `test_floor_slab_2_live_prices`
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
- items_total_concrete_volume_m3: `0.0`
- items_total_formwork_area_m2: `0.0`
- items_total_eps_material_area_m2: `0.0`
- items_total_eps_work_length_m: `0.0`
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
| 2 | `formwork_rental_set` | Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые) | м2 | 81.9 | 81.9 | 49 140 | 0 | 49 140 |
| 3 | `formwork_delivery_manipulator` | Доставка, вывоз опалубки манипулятором | маш | 2 | 2 | 40 000 | 0 | 40 000 |
| 4 | `crane_supply_formwork_rebar` | Подача опалубки, арматуры автокраном | смена | 2 | 2 | 60 000 | 0 | 60 000 |
| 5 | `formwork_consumables` | Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки) | - | 1 | 1 | 9 759 | 0 | 9 759 |
| 6 | `edge_formwork_installation_control` | Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты | м2 | 7.24 | 7.24 | 0 | 0 | 0 |
| 7 | `plywood_for_edges` | Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов | шт | 16 | 16 | 22 400 | 0 | 22 400 |
| 8 | `timber_for_formwork` | Пиломатериал обрезной для устройства опалубки ГОСТ | м3 | 0.36 | 0.36 | 7 783 | 0 | 7 783 |
| 9 | `rebar_frame_assembly_control` | Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры | мп | 2 819.7 | 2 819.7 | 0 | 0 | 0 |
| 10 | `rebar_a500_d16` | Арматура класса А500 диаметром 16 мм | мп | 105.3 | 105.3 | 6 834 | 0 | 6 834 |
| 11 | `rebar_a500_d12` | Арматура класса А500 диаметром 12 мм | мп | 35.1 | 35.1 | 1 293 | 0 | 1 293 |
| 12 | `rebar_a500_d10` | Арматура класса А500 диаметром 10 мм | мп | 2 679.3 | 2 679.3 | 72 770 | 0 | 72 770 |
| 13 | `concrete_placing_work` | Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300) | м3 | 16.5 | 16.5 | 0 | 198 000 | 198 000 |
| 14 | `beam_concreting_work` | Бетонирование балки бетоном марки В22,5 (М300) | м3 | 0 | 0 | 0 | 0 | 0 |
| 15 | `concrete_b22_5_m300_material` | Бетон марки В22,5 (М300) | м3 | 17.5 | 17.5 | 112 000 | 0 | 112 000 |
| 16 | `concrete_delivery` | Доставка бетона до объекта | рейс | 2 | 2 | 15 000 | 0 | 15 000 |
| 17 | `concrete_pump_32m` | Работа бетононасоса 32м + гаситель | смена | 1 | 1 | 38 000 | 0 | 38 000 |
| 18 | `formwork_dismantling_control` | Демонтаж опалубки после завершения бетонирования | м2 | 81.9 | 81.9 | 0 | 0 | 0 |
| 19 | `edge_insulation_work` | Устройство утепления по наружной стороне торцов плиты, балок | мп | 36.2 | 36.2 | 0 | 16 290 | 16 290 |
| 20 | `eps100_penoplex_material` | Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм | м3 | 0.83 | 0.83 | 7 504 | 0 | 7 504 |
| 21 | `eps_foam_glue` | Клей-пена для ЭППС | баллон | 1 | 1 | 450 | 0 | 450 |
| 22 | `logistics_and_supply` | Логистика, и снабжение | - | 1 | 1 | 6 895 | 0 | 6 895 |
| 23 | `consumables_tool_depreciation` | Расходные материалы, амортизация инструмента | комплект | 1 | 1 | 20 684 | 0 | 20 684 |
| 24 | `technical_supervision` | Технический надзор | - | 1 | 1 | 0 | 0 | 0 |
| 25 | `procurement_storage_costs` | Заготовительно-складские расходы | - | 1 | 1 | 0 | 0 | 0 |
| 26 | `overhead_general_business_costs` | Накладные и общехозяйственные расходы | - | 1 | 1 | 0 | 0 | 0 |
| 27 | `estimated_profit` | Сметная прибыль | - | 1 | 1 | 0 | 0 | 0 |

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
- Материалы raw/display: `49140.0` / `49140`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `49140.0` / `49140`

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
- Материалы raw/display: `9759.08` / `9759`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `9759.08` / `9759`

### 6. Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `7.24` / `7.24`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`
- Примечание: Production quantity uses edge_formwork_area_m2 + beams_formwork_area_m2 from specification.

### 7. Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов

- Тип строки: `materials`
- Количество raw/display: `16.0` / `16.0`
- Материалы raw/display: `22400.0` / `22400`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `22400.0` / `22400`

### 8. Пиломатериал обрезной для устройства опалубки ГОСТ

- Тип строки: `materials`
- Количество raw/display: `0.362` / `0.36`
- Материалы raw/display: `7782.999029478` / `7783`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `7782.999029478` / `7783`
- Примечание: Money is calculated from raw quantity 0.362, not displayed quantity 0.36.

### 9. Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `2819.7` / `2819.7`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 10. Арматура класса А500 диаметром 16 мм

- Тип строки: `materials`
- Количество raw/display: `105.3` / `105.3`
- Материалы raw/display: `6833.97` / `6834`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `6833.97` / `6834`

### 11. Арматура класса А500 диаметром 12 мм

- Тип строки: `materials`
- Количество raw/display: `35.1` / `35.1`
- Материалы raw/display: `1293.435` / `1293`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `1293.435` / `1293`

### 12. Арматура класса А500 диаметром 10 мм

- Тип строки: `materials`
- Количество raw/display: `2679.3` / `2679.3`
- Материалы raw/display: `72769.788` / `72770`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `72769.788` / `72770`

### 13. Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300)

- Тип строки: `work`
- Количество raw/display: `16.5` / `16.5`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `198000.0` / `198000`
- Итого raw/display: `198000.0` / `198000`

### 14. Бетонирование балки бетоном марки В22,5 (М300)

- Тип строки: `work`
- Количество raw/display: `0.0` / `0.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`
- Примечание: Quantity and total are 0 when no beams.items are given for this floor slab.

### 15. Бетон марки В22,5 (М300)

- Тип строки: `materials`
- Количество raw/display: `17.5` / `17.5`
- Материалы raw/display: `112000.0` / `112000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `112000.0` / `112000`

### 16. Доставка бетона до объекта

- Тип строки: `logistics_machinery`
- Количество raw/display: `2.0` / `2.0`
- Материалы raw/display: `15000.0` / `15000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `15000.0` / `15000`

### 17. Работа бетононасоса 32м + гаситель

- Тип строки: `machinery_fixed`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `38000.0` / `38000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `38000.0` / `38000`

### 18. Демонтаж опалубки после завершения бетонирования

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `81.9` / `81.9`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 19. Устройство утепления по наружной стороне торцов плиты, балок

- Тип строки: `work`
- Количество raw/display: `36.2` / `36.2`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `16290.0` / `16290`
- Итого raw/display: `16290.0` / `16290`
- Примечание: Quantity is slab_edge_perimeter_m plus the sum of beams.items length_m * count; equals slab_edge_perimeter_m alone when no beams.items are given.

### 20. Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм

- Тип строки: `materials`
- Количество raw/display: `0.8319` / `0.83`
- Материалы raw/display: `7503.738` / `7504`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `7503.738` / `7504`

### 21. Клей-пена для ЭППС

- Тип строки: `materials_consumables`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `450.0` / `450`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `450.0` / `450`

### 22. Логистика, и снабжение

- Тип строки: `materials_overhead_percent`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `6894.72487` / `6895`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `6894.72487` / `6895`

### 23. Расходные материалы, амортизация инструмента

- Тип строки: `materials_overhead_percent`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `20684.17461` / `20684`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `20684.17461` / `20684`

### 24. Технический надзор

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 25. Заготовительно-складские расходы

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 26. Накладные и общехозяйственные расходы

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 27. Сметная прибыль

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

## Totals

- internal_materials_total_raw: `470511.909509478`
- internal_materials_total: `470512`
- internal_works_total_raw: `214290`
- internal_works_total: `214290`
- internal_section_total_raw: `684801.909509478`
- internal_section_total: `684802`
- sum_of_displayed_line_material_totals: `470512`
- sum_of_displayed_line_work_totals: `214290`
- sum_of_displayed_line_totals: `684802`

## Warnings

- concrete_placing_volume_m3 is a manual/project quantity for this case; it is not derived from slab_area_m2 * slab thickness. If beams exist, this total is expected to already include beam concrete, same as floor_slab_1_calculator.
- edge_insulation_height_m = 0.18 m is confirmed by specification; 200 mm in the section title is considered a naming error.

## Источники цен

| Строка сметы | price_code | старая цена | использованная цена | источник | предупреждение |
| --- | --- | ---: | ---: | --- | --- |
| Монтаж опалубки под монолитное перекрытие 2-го этажа | `` | `None` | `None` | `locked_case_prices` |  |
| Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые) | `formwork_rental_m2` | `850` | `600` | `price_registry` |  |
| Доставка, вывоз опалубки манипулятором | `formwork_delivery_truck` | `20000` | `20000` | `price_registry` |  |
| Подача опалубки, арматуры автокраном | `crane_shift` | `30000` | `30000` | `price_registry` |  |
| Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки) | `formwork_consumables_m2` | `None` | `9759.08` | `price_registry` |  |
| Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты | `` | `None` | `None` | `locked_case_prices` |  |
| Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов | `plywood_1520x1520_18mm_sheet` | `1450` | `1400` | `price_registry` |  |
| Пиломатериал обрезной для устройства опалубки ГОСТ | `timber_m3` | `21500` | `21499.997319` | `price_registry` |  |
| Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры | `` | `None` | `None` | `locked_case_prices` |  |
| Арматура класса А500 диаметром 16 мм | `rebar_a500_d16_m` | `80.58` | `64.9` | `price_registry` |  |
| Арматура класса А500 диаметром 12 мм | `rebar_a500_d12_m` | `45.29` | `36.85` | `price_registry` |  |
| Арматура класса А500 диаметром 10 мм | `rebar_a500_d10_m` | `32.72` | `27.16` | `price_registry` |  |
| Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300) | `concrete_placing_work_m3` | `12000` | `12000` | `price_registry` |  |
| Бетонирование балки бетоном марки В22,5 (М300) | `beam_concrete_placing_work_m3` | `None` | `20000` | `price_registry` |  |
| Бетон марки В22,5 (М300) | `concrete_b22_5_m3` | `6400` | `6400` | `price_registry` |  |
| Доставка бетона до объекта | `concrete_delivery_trip` | `7500` | `7500` | `price_registry` |  |
| Работа бетононасоса 32м + гаситель | `concrete_pump_32m_shift` | `38000` | `38000` | `price_registry` |  |
| Демонтаж опалубки после завершения бетонирования | `` | `None` | `None` | `locked_case_prices` |  |
| Устройство утепления по наружной стороне торцов плиты, балок | `edge_insulation_work_m` | `450` | `450` | `price_registry` |  |
| Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм | `eps_penoplex_osnova_100_m3` | `9020` | `9020` | `price_registry` |  |
| Клей-пена для ЭППС | `eps_foam_glue_can` | `490` | `450` | `price_registry` |  |
| Логистика, и снабжение | `` | `None` | `None` | `locked_case_prices` |  |
| Расходные материалы, амортизация инструмента | `` | `None` | `None` | `locked_case_prices` |  |
| Технический надзор | `` | `None` | `None` | `locked_case_prices` |  |
| Заготовительно-складские расходы | `` | `None` | `None` | `locked_case_prices` |  |
| Накладные и общехозяйственные расходы | `` | `None` | `None` | `locked_case_prices` |  |
| Сметная прибыль | `` | `None` | `None` | `locked_case_prices` |  |

## Pricing summary

- mode: `price_registry_with_fallback`
- registry_path: `/Users/tatanamedzidova/Desktop/ai_estimator/ai_estimator_mvp/output/price_registry_filled_v3.xlsx`
- prices_from_price_registry: `17`
- prices_from_project_overrides: `0`
- prices_from_fallback_input: `0`
- warnings_count: `0`

## Comparison

- status: `ok`
- ok: `0`
- mismatch: `0`

| scope | code | field | expected | actual | status |
| --- | --- | --- | ---: | ---: | --- |
