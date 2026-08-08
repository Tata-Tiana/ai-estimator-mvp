# Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 2-го этажа на отм. +4.680 (200мм)

## Inputs

- project_name: `test_floor_slab_2_rebar_spec_lengths`
- slab_area_m2: `None`
- slab_edge_perimeter_m: `36.2`
- concrete_placing_volume_m3: `16.5`

## Calculation Blocks

## Площадь опалубки и геометрия

Production-режим `spec_formwork_area`: площади опалубки берутся из спецификации.

- `main_formwork_area_m2` используется для строки `formwork_rental_set`.
- `edge_formwork_area_m2 + beams_formwork_area_m2` используется для торцевой опалубки, фанеры и пиломатериала.
- `slab_edge_perimeter_m` используется как проектная длина утепляемого торца.
- `slab_edge_perimeter_m * edge_formwork_height_m` остается только контрольной формулой.
- `slab_length_m`, `slab_width_m`, `slab_area_m2` являются optional geometry check.

- main_formwork_area_m2: `81.9`
- edge_formwork_area_m2: `7.24`
- beams_formwork_area_m2: `0.0`
- edge_and_beam_formwork_area_m2: `7.24`
- calculated_edge_formwork_area_m2: `7.24`
- edge_formwork_area_delta_m2: `0.0`
- slab_edge_perimeter_m: `36.2`
- calculated_slab_area_m2: `None`
- calculated_slab_edge_perimeter_m: `None`
- area_delta_m2: `None`
- formwork_area_delta_m2: `None`

## Доставка и вывоз опалубки

- Production-правило: до 180 м2 включительно — 2 рейса; более 180 м2 — 4 рейса.
- formwork_delivery_calc_method: `area_threshold`
- formwork_delivery_area_source_m2: `81.9`
- formwork_delivery_threshold_m2: `180.0`
- formwork_delivery_trips: `2.0`
- formwork_delivery_breakdown: `1 привоз + 1 вывоз`
- formwork_delivery_status: `calculated`

### geometry

- formwork_area_calc_method: `spec_formwork_area`
- formwork_area_source: `spec_formwork_area`
- edge_formwork_area_source: `spec_formwork_area`
- slab_edge_perimeter_source: `spec_edge_perimeter`
- slab_length_m: `None`
- slab_width_m: `None`
- slab_area_m2: `None`
- slab_edge_perimeter_m: `36.2`
- main_formwork_area_m2: `81.9`
- edge_formwork_area_m2: `7.24`
- beams_formwork_area_m2: `0.0`
- edge_and_beam_formwork_area_combined_m2: `None`
- edge_and_beam_formwork_area_m2: `7.24`
- calculated_edge_formwork_area_m2: `7.24`
- edge_formwork_area_delta_m2: `0.0`
- calculated_slab_area_m2: `None`
- calculated_slab_edge_perimeter_m: `None`
- input_slab_area_m2: `None`
- area_delta_m2: `None`
- formwork_area_delta_m2: `None`

### formwork

- formwork_area_calc_method: `spec_formwork_area`
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
- edge_formwork_area_source: `spec_formwork_area`
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

- rebar_calc_method: `spec_length_items`
- items: 3 items
- total_rebar_order_length_m: `2819.7`
- total_rebar_order_weight_kg: `1850.6709`
- total_rebar_weight_with_waste_kg: `1850.67`

### concrete

- concrete_placing_volume_m3: `16.5`
- slab_concrete_volume_m3: `16.5`
- beams_concrete_volume_m3: `0.0`
- concrete_volume_with_waste_raw_m3: `17.325`
- concrete_volume_with_waste_display_m3: `17.33`
- concrete_order_volume_m3: `17.5`
- delivery_trips_raw: `1.944444`
- delivery_trips: `2`
- reinforcement_density_kg_per_m3: `106.82`

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
| 11 | `rebar_a500_d16` | Арматура класса A500 диаметром 16 мм | мп | 105.3 | 105.3 | 8 485 | 0 | 8 485 |
| 12 | `rebar_a500_d12` | Арматура класса A500 диаметром 12 мм | мп | 35.1 | 35.1 | 1 590 | 0 | 1 590 |
| 13 | `rebar_a500_d10` | Арматура класса A500 диаметром 10 мм | мп | 2 679.3 | 2 679.3 | 87 667 | 0 | 87 667 |
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

### 11. Арматура класса A500 диаметром 16 мм

- Тип строки: `materials`
- Количество raw/display: `105.3` / `105.3`
- Материалы raw/display: `8485.074` / `8485`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `8485.074` / `8485`

### 12. Арматура класса A500 диаметром 12 мм

- Тип строки: `materials`
- Количество raw/display: `35.1` / `35.1`
- Материалы raw/display: `1589.679` / `1590`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `1589.679` / `1590`

### 13. Арматура класса A500 диаметром 10 мм

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
- ok: `93`
- mismatch: `0`

| scope | code | field | expected | actual | status |
| --- | --- | --- | ---: | ---: | --- |
| calculation_blocks | `geometry.formwork_area_calc_method` | `geometry.formwork_area_calc_method` | spec_formwork_area | spec_formwork_area | ok |
| calculation_blocks | `geometry.formwork_area_source` | `geometry.formwork_area_source` | spec_formwork_area | spec_formwork_area | ok |
| calculation_blocks | `geometry.slab_edge_perimeter_source` | `geometry.slab_edge_perimeter_source` | spec_edge_perimeter | spec_edge_perimeter | ok |
| calculation_blocks | `geometry.main_formwork_area_m2` | `geometry.main_formwork_area_m2` | 81.9 | 81.9 | ok |
| calculation_blocks | `geometry.edge_formwork_area_m2` | `geometry.edge_formwork_area_m2` | 7.24 | 7.24 | ok |
| calculation_blocks | `geometry.beams_formwork_area_m2` | `geometry.beams_formwork_area_m2` | 0 | 0.0 | ok |
| calculation_blocks | `geometry.edge_and_beam_formwork_area_m2` | `geometry.edge_and_beam_formwork_area_m2` | 7.24 | 7.24 | ok |
| calculation_blocks | `geometry.calculated_edge_formwork_area_m2` | `geometry.calculated_edge_formwork_area_m2` | 7.24 | 7.24 | ok |
| calculation_blocks | `geometry.edge_formwork_area_delta_m2` | `geometry.edge_formwork_area_delta_m2` | 0 | 0.0 | ok |
| calculation_blocks | `geometry.calculated_slab_area_m2` | `geometry.calculated_slab_area_m2` | None | None | ok |
| calculation_blocks | `geometry.calculated_slab_edge_perimeter_m` | `geometry.calculated_slab_edge_perimeter_m` | None | None | ok |
| calculation_blocks | `geometry.area_delta_m2` | `geometry.area_delta_m2` | None | None | ok |
| calculation_blocks | `geometry.formwork_area_delta_m2` | `geometry.formwork_area_delta_m2` | None | None | ok |
| calculation_blocks | `formwork.formwork_area_calc_method` | `formwork.formwork_area_calc_method` | spec_formwork_area | spec_formwork_area | ok |
| calculation_blocks | `formwork.main_formwork_area_m2` | `formwork.main_formwork_area_m2` | 81.9 | 81.9 | ok |
| calculation_blocks | `formwork.edge_formwork_area_m2` | `formwork.edge_formwork_area_m2` | 7.24 | 7.24 | ok |
| calculation_blocks | `formwork.beams_formwork_area_m2` | `formwork.beams_formwork_area_m2` | 0 | 0.0 | ok |
| calculation_blocks | `formwork.edge_and_beam_formwork_area_m2` | `formwork.edge_and_beam_formwork_area_m2` | 7.24 | 7.24 | ok |
| calculation_blocks | `formwork.calculated_edge_formwork_area_m2` | `formwork.calculated_edge_formwork_area_m2` | 7.24 | 7.24 | ok |
| calculation_blocks | `formwork.edge_formwork_area_delta_m2` | `formwork.edge_formwork_area_delta_m2` | 0 | 0.0 | ok |
| calculation_blocks | `formwork.edge_formwork_area_source` | `formwork.edge_formwork_area_source` | spec_formwork_area | spec_formwork_area | ok |
| calculation_blocks | `formwork.formwork_delivery_calc_method` | `formwork.formwork_delivery_calc_method` | area_threshold | area_threshold | ok |
| calculation_blocks | `formwork.formwork_delivery_area_source_m2` | `formwork.formwork_delivery_area_source_m2` | 81.9 | 81.9 | ok |
| calculation_blocks | `formwork.formwork_delivery_threshold_m2` | `formwork.formwork_delivery_threshold_m2` | 180 | 180.0 | ok |
| calculation_blocks | `formwork.formwork_delivery_trips` | `formwork.formwork_delivery_trips` | 2 | 2.0 | ok |
| calculation_blocks | `formwork.formwork_delivery_breakdown` | `formwork.formwork_delivery_breakdown` | 1 привоз + 1 вывоз | 1 привоз + 1 вывоз | ok |
| calculation_blocks | `formwork.formwork_delivery_status` | `formwork.formwork_delivery_status` | calculated | calculated | ok |
| calculation_blocks | `rebar.rebar_calc_method` | `rebar.rebar_calc_method` | spec_length_items | spec_length_items | ok |
| calculation_blocks | `rebar.items.0.code` | `rebar.items.0.code` | rebar_a500_d16 | rebar_a500_d16 | ok |
| calculation_blocks | `rebar.items.0.name` | `rebar.items.0.name` | Арматура класса A500 диаметром 16 мм | Арматура класса A500 диаметром 16 мм | ok |
| calculation_blocks | `rebar.items.0.steel_class` | `rebar.items.0.steel_class` | A500 | A500 | ok |
| calculation_blocks | `rebar.items.0.diameter_mm` | `rebar.items.0.diameter_mm` | 16 | 16 | ok |
| calculation_blocks | `rebar.items.0.spec_length_m` | `rebar.items.0.spec_length_m` | 90.126582 | 90.126582 | ok |
| calculation_blocks | `rebar.items.0.kg_per_meter` | `rebar.items.0.kg_per_meter` | 1.58 | 1.58 | ok |
| calculation_blocks | `rebar.items.0.rod_length_m` | `rebar.items.0.rod_length_m` | 11.7 | 11.7 | ok |
| calculation_blocks | `rebar.items.0.order_length_m` | `rebar.items.0.order_length_m` | 105.3 | 105.3 | ok |
| calculation_blocks | `rebar.items.0.order_weight_kg` | `rebar.items.0.order_weight_kg` | 166.374 | 166.374 | ok |
| calculation_blocks | `rebar.items.0.price_code` | `rebar.items.0.price_code` | rebar_a500_d16_m | rebar_a500_d16_m | ok |
| calculation_blocks | `rebar.items.0.material_total` | `rebar.items.0.material_total` | 8485 | 8485 | ok |
| calculation_blocks | `rebar.items.1.code` | `rebar.items.1.code` | rebar_a500_d12 | rebar_a500_d12 | ok |
| calculation_blocks | `rebar.items.1.name` | `rebar.items.1.name` | Арматура класса A500 диаметром 12 мм | Арматура класса A500 диаметром 12 мм | ok |
| calculation_blocks | `rebar.items.1.steel_class` | `rebar.items.1.steel_class` | A500 | A500 | ok |
| calculation_blocks | `rebar.items.1.diameter_mm` | `rebar.items.1.diameter_mm` | 12 | 12 | ok |
| calculation_blocks | `rebar.items.1.spec_length_m` | `rebar.items.1.spec_length_m` | 24.774775 | 24.774775 | ok |
| calculation_blocks | `rebar.items.1.kg_per_meter` | `rebar.items.1.kg_per_meter` | 0.888 | 0.888 | ok |
| calculation_blocks | `rebar.items.1.rod_length_m` | `rebar.items.1.rod_length_m` | 11.7 | 11.7 | ok |
| calculation_blocks | `rebar.items.1.order_length_m` | `rebar.items.1.order_length_m` | 35.1 | 35.1 | ok |
| calculation_blocks | `rebar.items.1.order_weight_kg` | `rebar.items.1.order_weight_kg` | 31.1688 | 31.1688 | ok |
| calculation_blocks | `rebar.items.1.price_code` | `rebar.items.1.price_code` | rebar_a500_d12_m | rebar_a500_d12_m | ok |
| calculation_blocks | `rebar.items.1.material_total` | `rebar.items.1.material_total` | 1590 | 1590 | ok |
| calculation_blocks | `rebar.items.2.code` | `rebar.items.2.code` | rebar_a500_d10 | rebar_a500_d10 | ok |
| calculation_blocks | `rebar.items.2.name` | `rebar.items.2.name` | Арматура класса A500 диаметром 10 мм | Арматура класса A500 диаметром 10 мм | ok |
| calculation_blocks | `rebar.items.2.steel_class` | `rebar.items.2.steel_class` | A500 | A500 | ok |
| calculation_blocks | `rebar.items.2.diameter_mm` | `rebar.items.2.diameter_mm` | 10 | 10 | ok |
| calculation_blocks | `rebar.items.2.spec_length_m` | `rebar.items.2.spec_length_m` | 2551.166937 | 2551.166937 | ok |
| calculation_blocks | `rebar.items.2.kg_per_meter` | `rebar.items.2.kg_per_meter` | 0.617 | 0.617 | ok |
| calculation_blocks | `rebar.items.2.rod_length_m` | `rebar.items.2.rod_length_m` | 11.7 | 11.7 | ok |
| calculation_blocks | `rebar.items.2.order_length_m` | `rebar.items.2.order_length_m` | 2679.3 | 2679.3 | ok |
| calculation_blocks | `rebar.items.2.order_weight_kg` | `rebar.items.2.order_weight_kg` | 1653.1281 | 1653.1281 | ok |
| calculation_blocks | `rebar.items.2.price_code` | `rebar.items.2.price_code` | rebar_a500_d10_m | rebar_a500_d10_m | ok |
| calculation_blocks | `rebar.items.2.material_total` | `rebar.items.2.material_total` | 87667 | 87667 | ok |
| calculation_blocks | `rebar.total_rebar_order_length_m` | `rebar.total_rebar_order_length_m` | 2819.7 | 2819.7 | ok |
| calculation_blocks | `rebar.total_rebar_order_weight_kg` | `rebar.total_rebar_order_weight_kg` | 1850.6709 | 1850.6709 | ok |
| estimate_lines | `formwork_rental_set` | `unit` | м2 | м2 | ok |
| estimate_lines | `formwork_rental_set` | `quantity_raw` | 81.9 | 81.9 | ok |
| estimate_lines | `formwork_rental_set` | `quantity_display` | 81.9 | 81.9 | ok |
| estimate_lines | `formwork_rental_set` | `material_unit_price` | 850 | 850.0 | ok |
| estimate_lines | `formwork_rental_set` | `material_total` | 69615 | 69615 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `quantity_raw` | 2 | 2.0 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `quantity_display` | 2 | 2.0 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `material_unit_price` | 20000 | 20000.0 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `material_total` | 40000 | 40000 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `line_total` | 40000 | 40000 | ok |
| estimate_lines | `edge_formwork_installation_control` | `quantity_raw` | 7.24 | 7.24 | ok |
| estimate_lines | `edge_formwork_installation_control` | `quantity_display` | 7.24 | 7.24 | ok |
| estimate_lines | `plywood_for_edges` | `quantity_raw` | 16 | 16.0 | ok |
| estimate_lines | `plywood_for_edges` | `quantity_display` | 16 | 16.0 | ok |
| estimate_lines | `timber_for_formwork` | `quantity_raw` | 0.362 | 0.362 | ok |
| estimate_lines | `timber_for_formwork` | `quantity_display` | 0.36 | 0.36 | ok |
| estimate_lines | `edge_insulation_work` | `unit` | мп | мп | ok |
| estimate_lines | `edge_insulation_work` | `quantity_raw` | 36.2 | 36.2 | ok |
| estimate_lines | `edge_insulation_work` | `quantity_display` | 36.2 | 36.2 | ok |
| estimate_lines | `rebar_frame_assembly_control` | `quantity_raw` | 2819.7 | 2819.7 | ok |
| estimate_lines | `rebar_frame_assembly_control` | `quantity_display` | 2819.7 | 2819.7 | ok |
| estimate_lines | `rebar_a500_d16` | `quantity_raw` | 105.3 | 105.3 | ok |
| estimate_lines | `rebar_a500_d16` | `quantity_display` | 105.3 | 105.3 | ok |
| estimate_lines | `rebar_a500_d16` | `material_total` | 8485 | 8485 | ok |
| estimate_lines | `rebar_a500_d12` | `quantity_raw` | 35.1 | 35.1 | ok |
| estimate_lines | `rebar_a500_d12` | `quantity_display` | 35.1 | 35.1 | ok |
| estimate_lines | `rebar_a500_d12` | `material_total` | 1590 | 1590 | ok |
| estimate_lines | `rebar_a500_d10` | `quantity_raw` | 2679.3 | 2679.3 | ok |
| estimate_lines | `rebar_a500_d10` | `quantity_display` | 2679.3 | 2679.3 | ok |
| estimate_lines | `rebar_a500_d10` | `material_total` | 87667 | 87667 | ok |
