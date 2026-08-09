# Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 2-го этажа на отм. +4.680 (200мм)

## Inputs

- project_name: `test_floor_slab_2_formwork_delivery_threshold_180`
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

- main_formwork_area_m2: `180.0`
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
- formwork_delivery_area_source_m2: `180.0`
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
- main_formwork_area_m2: `180.0`
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
- main_formwork_area_m2: `180.0`
- raw_supplier_rate: `850.0`
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
- formwork_delivery_area_source_m2: `180.0`
- formwork_delivery_threshold_m2: `180.0`
- formwork_delivery_trips: `2.0`
- formwork_delivery_breakdown: `1 привоз + 1 вывоз`
- formwork_delivery_status: `calculated`

### plywood_and_timber

- edge_and_beam_formwork_area_m2: `7.24`
- beams_bottom_formwork_area_m2: `0.0`
- edge_beam_formwork_area_for_materials_m2: `7.24`
- edge_plywood_sheets_raw: `3.147826`
- non_multiple_places_area_m2: `36.0`
- non_multiple_places_plywood_sheets_raw: `15.652174`
- base_plywood_sheets_raw: `18.8`
- order_plywood_sheets_raw: `23.8`
- plywood_sheets: `24`
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

- direct_cost_base_before_addons_raw: `789068.187`
- logistics_rate: `0.01`
- logistics_total_raw: `7890.68187`
- consumables_rate: `0.03`
- consumables_total_raw: `23672.04561`

## Estimate Lines

| # | code | name | unit | qty raw | qty display | material | work | total |
| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | `floor_slab_2_formwork_installation_control` | Монтаж опалубки под монолитное перекрытие 2-го этажа | м2 | 180 | 180 | 0 | 0 | 0 |
| 2 | `formwork_rental_set` | Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые) | м2 | 180 | 180 | 153 000 | 0 | 153 000 |
| 3 | `formwork_delivery_manipulator` | Доставка, вывоз опалубки манипулятором | маш | 2 | 2 | 40 000 | 0 | 40 000 |
| 4 | `crane_supply_formwork_rebar` | Подача опалубки, арматуры автокраном | смена | 2 | 2 | 60 000 | 0 | 60 000 |
| 5 | `rebar_metal_delivery` | Доставка арматуры, металла | маш | 0 | 0 | 0 | 0 | 0 |
| 6 | `formwork_consumables` | Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки) | - | 1 | 1 | 8 460 | 0 | 8 460 |
| 7 | `edge_formwork_installation_control` | Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты | м2 | 7.24 | 7.24 | 0 | 0 | 0 |
| 8 | `plywood_for_edges` | Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов | шт | 24 | 24 | 34 800 | 0 | 34 800 |
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
| 19 | `formwork_dismantling_control` | Демонтаж опалубки после завершения бетонирования | м2 | 180 | 180 | 0 | 0 | 0 |
| 20 | `edge_insulation_work` | Устройство утепления по наружной стороне торцов плиты, балок | мп | 36.2 | 36.2 | 0 | 16 290 | 16 290 |
| 21 | `bottom_slab_insulation_work` | Устройство утепления низа плиты | м2 | 0 | 0 | 0 | 0 | 0 |
| 22 | `eps100_penoplex_material` | Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм | м3 | 0.83 | 0.83 | 7 504 | 0 | 7 504 |
| 23 | `eps_foam_glue` | Клей-пена для ЭППС | баллон | 1 | 1 | 490 | 0 | 490 |
| 24 | `logistics_and_supply` | Логистика, и снабжение | - | 1 | 1 | 7 891 | 0 | 7 891 |
| 25 | `consumables_tool_depreciation` | Расходные материалы, амортизация инструмента | комплект | 1 | 1 | 23 672 | 0 | 23 672 |
| 26 | `technical_supervision` | Технический надзор | - | 1 | 1 | 0 | 0 | 0 |
| 27 | `procurement_storage_costs` | Заготовительно-складские расходы | - | 1 | 1 | 0 | 0 | 0 |
| 28 | `overhead_general_business_costs` | Накладные и общехозяйственные расходы | - | 1 | 1 | 0 | 0 | 0 |
| 29 | `estimated_profit` | Сметная прибыль | - | 1 | 1 | 0 | 0 | 0 |

## Post-Line Explanations

### 1. Монтаж опалубки под монолитное перекрытие 2-го этажа

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `180.0` / `180.0`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 2. Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые)

- Тип строки: `materials`
- Количество raw/display: `180.0` / `180.0`
- Материалы raw/display: `153000.0` / `153000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `153000.0` / `153000`

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
- Материалы raw/display: `8460.0` / `8460`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `8460.0` / `8460`

### 7. Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `7.24` / `7.24`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`
- Примечание: Production quantity uses edge_formwork_area_m2 + beams_formwork_area_m2 (or edge_and_beam_formwork_area_combined_m2) + beams_bottom_formwork_area_m2 from specification — same combined quantity as plywood/timber material.

### 8. Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов

- Тип строки: `materials`
- Количество raw/display: `24.0` / `24.0`
- Материалы raw/display: `34800.0` / `34800`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `34800.0` / `34800`

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
- Количество raw/display: `180.0` / `180.0`
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
- Материалы raw/display: `7890.68187` / `7891`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `7890.68187` / `7891`

### 25. Расходные материалы, амортизация инструмента

- Тип строки: `materials_overhead_percent`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `23672.04561` / `23672`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `23672.04561` / `23672`

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

- internal_materials_total_raw: `606340.91448`
- internal_materials_total: `606341`
- internal_works_total_raw: `214290.0`
- internal_works_total: `214290`
- internal_section_total_raw: `820630.91448`
- internal_section_total: `820631`
- sum_of_displayed_line_material_totals: `606342`
- sum_of_displayed_line_work_totals: `214290`
- sum_of_displayed_line_totals: `820632`

## Warnings

- edge_insulation_height_m = 0.18 m is confirmed by specification; 200 mm in the section title is considered a naming error.

## Comparison

- status: `ok`
- ok: `11`
- mismatch: `0`

| scope | code | field | expected | actual | status |
| --- | --- | --- | ---: | ---: | --- |
| calculation_blocks | `formwork.formwork_delivery_calc_method` | `formwork.formwork_delivery_calc_method` | area_threshold | area_threshold | ok |
| calculation_blocks | `formwork.formwork_delivery_area_source_m2` | `formwork.formwork_delivery_area_source_m2` | 180 | 180.0 | ok |
| calculation_blocks | `formwork.formwork_delivery_threshold_m2` | `formwork.formwork_delivery_threshold_m2` | 180 | 180.0 | ok |
| calculation_blocks | `formwork.formwork_delivery_trips` | `formwork.formwork_delivery_trips` | 2 | 2.0 | ok |
| calculation_blocks | `formwork.formwork_delivery_breakdown` | `formwork.formwork_delivery_breakdown` | 1 привоз + 1 вывоз | 1 привоз + 1 вывоз | ok |
| calculation_blocks | `formwork.formwork_delivery_status` | `formwork.formwork_delivery_status` | calculated | calculated | ok |
| estimate_lines | `formwork_delivery_manipulator` | `quantity_raw` | 2 | 2.0 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `quantity_display` | 2 | 2.0 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `material_unit_price` | 20000 | 20000.0 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `material_total` | 40000 | 40000 | ok |
| estimate_lines | `formwork_delivery_manipulator` | `line_total` | 40000 | 40000 | ok |
