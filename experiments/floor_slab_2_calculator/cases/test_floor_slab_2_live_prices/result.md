# Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 2-го этажа на отм. +4.680 (200мм)

## Inputs

- project_name: `test_floor_slab_2_live_prices`
- slab_area_m2: `81.9`
- slab_edge_perimeter_m: `36.2`
- concrete_placing_volume_m3: `16.5`

## Calculation Blocks

### geometry

- slab_length_m: `9.0`
- slab_width_m: `9.1`
- slab_area_m2: `81.9`
- slab_edge_perimeter_m: `36.2`

### formwork

- main_formwork_area_m2: `81.9`
- raw_supplier_rate: `840.781441`
- used_rate_per_m2: `850.0`
- edge_formwork_area_m2: `7.24`

### plywood_and_timber

- edge_plywood_sheets_raw: `3.147826`
- non_multiple_places_area_m2: `16.38`
- non_multiple_places_plywood_sheets_raw: `7.121739`
- base_plywood_sheets_raw: `10.269565`
- order_plywood_sheets_raw: `15.269565`
- plywood_sheets: `16`
- timber_volume_m3_raw: `0.362`
- timber_volume_m3_display: `0.36`

### rebar

- items: 3 items
- total_rebar_order_length_m: `2819.7`
- total_rebar_weight_with_waste_kg: `1825.39`

### concrete

- concrete_placing_volume_m3: `16.5`
- concrete_volume_with_waste_raw_m3: `17.325`
- concrete_volume_with_waste_display_m3: `17.33`
- concrete_order_volume_m3: `17.5`
- delivery_trips_raw: `1.944444`
- delivery_trips: `2`
- reinforcement_density_kg_per_m3: `105.36`

### insulation

- edge_insulation_area_m2: `6.516`
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
| 5 | `formwork_consumables` | Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки) | - | 1 | 1 | 3 849 | 0 | 3 849 |
| 6 | `edge_formwork_installation_control` | Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты | м2 | 7.24 | 7.24 | 0 | 0 | 0 |
| 7 | `plywood_for_edges` | Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов | шт | 16 | 16 | 23 200 | 0 | 23 200 |
| 8 | `timber_for_formwork` | Пиломатериал обрезной для устройства опалубки ГОСТ | м3 | 0.36 | 0.36 | 7 783 | 0 | 7 783 |
| 9 | `rebar_frame_assembly_control` | Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры | мп | 2 819.7 | 2 819.7 | 0 | 0 | 0 |
| 10 | `rebar_a500_d16` | Арматура класса А500 диаметром 16 мм | мп | 105.3 | 105.3 | 6 834 | 0 | 6 834 |
| 11 | `rebar_a500_d12` | Арматура класса А500 диаметром 12 мм | мп | 35.1 | 35.1 | 1 293 | 0 | 1 293 |
| 12 | `rebar_a500_d10` | Арматура класса А500 диаметром 10 мм | мп | 2 679.3 | 2 679.3 | 72 770 | 0 | 72 770 |
| 13 | `concrete_placing_work` | Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300) | м3 | 16.5 | 16.5 | 0 | 198 000 | 198 000 |
| 14 | `concrete_b22_5_m300_material` | Бетон марки В22,5 (М300) | м3 | 17.5 | 17.5 | 112 000 | 0 | 112 000 |
| 15 | `concrete_delivery` | Доставка бетона до объекта | рейс | 2 | 2 | 15 000 | 0 | 15 000 |
| 16 | `concrete_pump_32m` | Работа бетононасоса 32м + гаситель | смена | 1 | 1 | 38 000 | 0 | 38 000 |
| 17 | `formwork_dismantling_control` | Демонтаж опалубки после завершения бетонирования | м2 | 81.9 | 81.9 | 0 | 0 | 0 |
| 18 | `edge_insulation_work` | Устройство утепления по наружной стороне торцов плиты, балок | мп | 36.2 | 36.2 | 0 | 16 290 | 16 290 |
| 19 | `eps100_penoplex_material` | Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм | м3 | 0.83 | 0.83 | 7 504 | 0 | 7 504 |
| 20 | `eps_foam_glue` | Клей-пена для ЭППС | баллон | 1 | 1 | 450 | 0 | 450 |
| 21 | `logistics_and_supply` | Логистика, и снабжение | - | 1 | 1 | 6 895 | 0 | 6 895 |
| 22 | `consumables_tool_depreciation` | Расходные материалы, амортизация инструмента | комплект | 1 | 1 | 20 684 | 0 | 20 684 |
| 23 | `technical_supervision` | Технический надзор | - | 1 | 1 | 0 | 0 | 0 |
| 24 | `procurement_storage_costs` | Заготовительно-складские расходы | - | 1 | 1 | 0 | 0 | 0 |
| 25 | `overhead_general_business_costs` | Накладные и общехозяйственные расходы | - | 1 | 1 | 0 | 0 | 0 |
| 26 | `estimated_profit` | Сметная прибыль | - | 1 | 1 | 0 | 0 | 0 |

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

### 4. Подача опалубки, арматуры автокраном

- Тип строки: `machinery`
- Количество raw/display: `2.0` / `2.0`
- Материалы raw/display: `60000.0` / `60000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `60000.0` / `60000`

### 5. Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки)

- Тип строки: `materials_consumables`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `3849.3` / `3849`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `3849.3` / `3849`

### 6. Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `7.24` / `7.24`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`
- Примечание: For floor slab 2 this control line is used for slab edge formwork only; no beams are calculated.

### 7. Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов

- Тип строки: `materials`
- Количество raw/display: `16.0` / `16.0`
- Материалы raw/display: `23200.0` / `23200`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `23200.0` / `23200`

### 8. Пиломатериал обрезной для устройства опалубки ГОСТ

- Тип строки: `materials`
- Количество raw/display: `0.362` / `0.36`
- Материалы raw/display: `7783.0` / `7783`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `7783.0` / `7783`
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

### 14. Бетон марки В22,5 (М300)

- Тип строки: `materials`
- Количество raw/display: `17.5` / `17.5`
- Материалы raw/display: `112000.0` / `112000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `112000.0` / `112000`

### 15. Доставка бетона до объекта

- Тип строки: `logistics_machinery`
- Количество raw/display: `2.0` / `2.0`
- Материалы raw/display: `15000.0` / `15000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `15000.0` / `15000`

### 16. Работа бетононасоса 32м + гаситель

- Тип строки: `machinery_fixed`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `38000.0` / `38000`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `38000.0` / `38000`

### 17. Демонтаж опалубки после завершения бетонирования

- Тип строки: `zero_excel_structure_line`
- Количество raw/display: `81.9` / `81.9`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `0.0` / `0`

### 18. Устройство утепления по наружной стороне торцов плиты, балок

- Тип строки: `work`
- Количество raw/display: `36.2` / `36.2`
- Материалы raw/display: `0.0` / `0`
- Работы raw/display: `16290.0` / `16290`
- Итого raw/display: `16290.0` / `16290`
- Примечание: Line name keeps the source wording; for floor slab 2 the calculation covers slab edges only, without beams.

### 19. Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм

- Тип строки: `materials`
- Количество raw/display: `0.8319` / `0.83`
- Материалы raw/display: `7503.738` / `7504`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `7503.738` / `7504`

### 20. Клей-пена для ЭППС

- Тип строки: `materials_consumables`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `450.0` / `450`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `450.0` / `450`

### 21. Логистика, и снабжение

- Тип строки: `materials_overhead_percent`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `6894.72487` / `6895`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `6894.72487` / `6895`

### 22. Расходные материалы, амортизация инструмента

- Тип строки: `materials_overhead_percent`
- Количество raw/display: `1.0` / `1.0`
- Материалы raw/display: `20684.17461` / `20684`
- Работы raw/display: `0.0` / `0`
- Итого raw/display: `20684.17461` / `20684`

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

- internal_materials_total_raw: `485877.13048`
- internal_materials_total: `485877`
- internal_works_total_raw: `214290`
- internal_works_total: `214290`
- internal_section_total_raw: `700167.13048`
- internal_section_total: `700167`
- sum_of_displayed_line_material_totals: `485877`
- sum_of_displayed_line_work_totals: `214290`
- sum_of_displayed_line_totals: `700167`

## Warnings

- concrete_placing_volume_m3 is a manual/project quantity for this case; it is not derived from slab_area_m2 * slab thickness.
- edge_insulation_height_m is 0.18 m although the section title says 200 mm; 0.18 m is kept for the current Excel match.
- formwork_rental_m2: price_code not found in price_registry, fallback input price used
- formwork_delivery_truck: price_code not found in price_registry, fallback input price used
- crane_shift: price_code not found in price_registry, fallback input price used
- formwork_consumables_m2: price_code not found in price_registry and fallback input price is missing
- plywood_1520x1520_18mm_sheet: price_code not found in price_registry, fallback input price used
- timber_m3: price_code not found in price_registry, fallback input price used
- concrete_placing_work_m3: price_code not found in price_registry, fallback input price used
- concrete_b22_5_m3: price_code not found in price_registry, fallback input price used
- concrete_delivery_trip: price_code not found in price_registry, fallback input price used
- concrete_pump_32m_shift: price_code not found in price_registry, fallback input price used
- edge_insulation_work_m: price_code not found in price_registry, fallback input price used
- eps_penoplex_osnova_100_m3: price_code not found in price_registry, fallback input price used

## Источники цен

| Строка сметы | price_code | старая цена | использованная цена | источник | предупреждение |
| --- | --- | ---: | ---: | --- | --- |
| Монтаж опалубки под монолитное перекрытие 2-го этажа | `` | `None` | `None` | `locked_case_prices` |  |
| Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые) | `formwork_rental_m2` | `850` | `850` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Доставка, вывоз опалубки манипулятором | `formwork_delivery_truck` | `20000` | `20000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Подача опалубки, арматуры автокраном | `crane_shift` | `30000` | `30000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки) | `formwork_consumables_m2` | `None` | `None` | `fallback_input` | price_code not found in price_registry and fallback input price is missing |
| Монтаж опалубки из доски 50 мм и фанеры для устройства балок и отбортовки плиты | `` | `None` | `None` | `locked_case_prices` |  |
| Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов | `plywood_1520x1520_18mm_sheet` | `1450` | `1450` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Пиломатериал обрезной для устройства опалубки ГОСТ | `timber_m3` | `21500` | `21500` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры | `` | `None` | `None` | `locked_case_prices` |  |
| Арматура класса А500 диаметром 16 мм | `rebar_a500_d16_m` | `80.58` | `64.9` | `price_registry` |  |
| Арматура класса А500 диаметром 12 мм | `rebar_a500_d12_m` | `45.29` | `36.85` | `price_registry` |  |
| Арматура класса А500 диаметром 10 мм | `rebar_a500_d10_m` | `32.72` | `27.16` | `price_registry` |  |
| Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300) | `concrete_placing_work_m3` | `12000` | `12000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Бетон марки В22,5 (М300) | `concrete_b22_5_m3` | `6400` | `6400` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Доставка бетона до объекта | `concrete_delivery_trip` | `7500` | `7500` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Работа бетононасоса 32м + гаситель | `concrete_pump_32m_shift` | `38000` | `38000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Демонтаж опалубки после завершения бетонирования | `` | `None` | `None` | `locked_case_prices` |  |
| Устройство утепления по наружной стороне торцов плиты, балок | `edge_insulation_work_m` | `450` | `450` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм | `eps_penoplex_osnova_100_m3` | `9020` | `9020` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Клей-пена для ЭППС | `eps_foam_glue_can` | `490` | `450` | `price_registry` |  |
| Логистика, и снабжение | `` | `None` | `None` | `locked_case_prices` |  |
| Расходные материалы, амортизация инструмента | `` | `None` | `None` | `locked_case_prices` |  |
| Технический надзор | `` | `None` | `None` | `locked_case_prices` |  |
| Заготовительно-складские расходы | `` | `None` | `None` | `locked_case_prices` |  |
| Накладные и общехозяйственные расходы | `` | `None` | `None` | `locked_case_prices` |  |
| Сметная прибыль | `` | `None` | `None` | `locked_case_prices` |  |

## Pricing summary

- mode: `price_registry_with_fallback`
- registry_path: `/Users/tatanamedzidova/Desktop/AI сметчик/ai_estimator_mvp/output/price_registry_filled_v3.xlsx`
- prices_from_price_registry: `4`
- prices_from_project_overrides: `0`
- prices_from_fallback_input: `12`
- warnings_count: `12`

## Comparison

- status: `ok`
- ok: `0`
- mismatch: `0`

| scope | code | field | expected | actual | status |
| --- | --- | --- | ---: | ---: | --- |
