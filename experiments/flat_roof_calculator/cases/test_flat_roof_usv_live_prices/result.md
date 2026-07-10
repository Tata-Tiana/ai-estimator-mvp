# Расчётный отчёт: КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА / плоская кровля

AI не используется для расчёта. Калькулятор считает только серую внутреннюю себестоимость по зафиксированным формулам.
Клиентская/белая зона и коммерческие коэффициенты вне текущего scope.

## Исходные параметры кровли

- project_name: `test_flat_roof_usv_live_prices`
- roof_geometry_calc_method: `legacy_totals`
- roof_area_total_m2: `248.92`
- project_spec_roof_area_m2: `294`
- parapet_and_abutment_total_length_m: `138.62`

## Геометрия кровли

| Параметр | Значение |
| --- | ---: |
| `roof_geometry_calc_method` | legacy_totals |
| `roof_area_level_1_m2` | 177.52 |
| `roof_area_level_2_m2` | 71.4 |
| `roof_area_total_m2` | 248.92 |
| `roof_area_total_source` | legacy_totals |
| `project_spec_roof_area_m2` | 294 |
| `parapet_length_level_1_m` | 96 |
| `parapet_length_level_2_m` | 35.4 |
| `vent_wall_abutment_level_1_m` | 4.68 |
| `vent_wall_abutment_level_2_m` | 2.54 |
| `parapet_and_abutment_total_length_m` | 138.62 |
| `parapet_and_abutment_total_length_source` | legacy_totals |
| `input_roof_area_total_m2` | 248.92 |
| `calculated_roof_area_total_m2` | None |
| `roof_area_total_delta_m2` | 0 |
| `input_parapet_and_abutment_total_length_m` | 138.62 |
| `calculated_parapet_and_abutment_total_length_m` | None |
| `parapet_and_abutment_total_delta_m` | 0 |

## Построчный расчёт

### 1. Подготовка основания под укладку пароизоляционного слоя, очистка поверхности

- Код: `roof_base_preparation_control`
- Тип строки: `zero_excel_structure_line`
- Ед. изм.: `м2`
- Количество raw: `248.92`
- Количество display: `248.92`
- Источник количества: `roof_area_total_m2`

Округление и итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `0` / `0`
- Итого raw/display: `0` / `0`
- Примечание: Строка сохранена для структуры Excel.
- Примечание: В текущем scope серая внутренняя себестоимость равна 0.

### 2. Пароизоляция основания плёнкой ПВХ

- Код: `vapor_barrier_installation`
- Тип строки: `work`
- Ед. изм.: `м2`
- Количество raw: `248.92`
- Количество display: `248.92`
- Источник количества: `roof_area_total_m2`

Формула:
- roof_area_total_m2: `248.92`
- rate_per_m2: `77`

Округление и итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `19166.84` / `19 167`
- Итого raw/display: `19166.84` / `19 167`

### 3. Пленка пароизоляция ТехноНИКОЛЬ 120 мкм, 150 м2/рул

- Код: `vapor_barrier_film_technonikol_120mk`
- Тип строки: `materials`
- Ед. изм.: `м2`
- Количество raw: `300`
- Количество display: `300`
- Источник количества: `roof_area_total_m2 * vapor_barrier_film_overlap_coeff rounded to rolls`
- price_code: `roof_vapor_barrier_film_technonikol_120mk_m2`

Формула:
- required_area_m2: `286.258`
- roll_area_m2: `150`
- rolls_ordered: `2`
- ordered_area_m2: `300`

Округление и итог:
- Материалы raw/display: `6936` / `6 936`
- Работы raw/display: `0` / `0`
- Итого raw/display: `6936` / `6 936`

### 4. Утепление кровельного покрытия ЭППС (1 слой -100мм, 2 слой -100мм, 3 слой - разуклонка)

- Код: `eps_roof_insulation_installation`
- Тип строки: `work`
- Ед. изм.: `м2`
- Количество raw: `248.92`
- Количество display: `248.92`
- Источник количества: `roof_area_total_m2`

Формула:
- roof_area_total_m2: `248.92`
- rate_per_m2: `770`
- rate_context: `likely eps_insulation_base_work_rate_per_m2 * roof_work_coeff`

Округление и итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `191668.4` / `191 668`
- Итого raw/display: `191668.4` / `191 668`
- Примечание: Для текущего проекта ставка 770 вероятно равна 700 * roof_work_coeff 1.10.

### 5. Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON ECO (100мм)

- Код: `eps100_technonikol_carbon_eco`
- Тип строки: `materials`
- Ед. изм.: `м3`
- Количество raw: `51.46688`
- Количество display: `51.47`
- Источник количества: `roof_area_total_m2 * eps_main_thickness_m * eps_insulation_waste_coeff rounded to packs`
- price_code: `roof_eps100_technonikol_carbon_eco_m3`

Формула:
- required_volume_m3: `51.27752`
- packs_ordered: `188`
- ordered_volume_m3: `51.46688`

Округление и итог:
- Материалы raw/display: `379716.9792832` / `379 717`
- Работы raw/display: `0` / `0`
- Итого raw/display: `379716.9792832` / `379 717`

### 6. Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON ECO (50мм)

- Код: `eps50_technonikol_carbon_eco`
- Тип строки: `materials`
- Ед. изм.: `м3`
- Количество raw: `4.1064`
- Количество display: `4.11`
- Источник количества: `supplier_required_volume_m3 rounded up to full packs`
- price_code: `roof_eps50_technonikol_carbon_eco_m3`

Формула:
- supplier_required_volume_m3: `3.92`
- pack_volume_m3: `0.27376`
- packs_ordered: `15`
- ordered_volume_m3: `4.1064`

Округление и итог:
- Материалы raw/display: `29382.688176` / `29 383`
- Работы raw/display: `0` / `0`
- Итого raw/display: `29382.688176` / `29 383`
- Примечание: supplier_required_volume_m3 берётся вручную от поставщика / Технониколь.

### 7. Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты A)

- Код: `eps_slope_2_1_plate_a`
- Тип строки: `materials`
- Ед. изм.: `м3`
- Количество raw: `3.7908`
- Количество display: `3.79`
- Источник количества: `supplier_required_volume_m3 rounded up to full packs`
- price_code: `roof_eps_slope_2_1_plate_a_m3`

Формула:
- supplier_required_volume_m3: `3.63`
- pack_volume_m3: `0.2916`
- packs_ordered: `13`
- ordered_volume_m3: `3.7908`

Округление и итог:
- Материалы raw/display: `37485.970236` / `37 486`
- Работы raw/display: `0` / `0`
- Итого raw/display: `37485.970236` / `37 486`
- Примечание: supplier_required_volume_m3 берётся вручную от поставщика / Технониколь.

### 8. Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты B)

- Код: `eps_slope_2_1_plate_b`
- Тип строки: `materials`
- Ед. изм.: `м3`
- Количество raw: `5.7456`
- Количество display: `5.75`
- Источник количества: `supplier_required_volume_m3 rounded up to full packs`
- price_code: `roof_eps_slope_2_1_plate_b_m3`

Формула:
- supplier_required_volume_m3: `5.61`
- pack_volume_m3: `0.2736`
- packs_ordered: `21`
- ordered_volume_m3: `5.7456`

Округление и итог:
- Материалы raw/display: `56816.342352` / `56 816`
- Работы raw/display: `0` / `0`
- Итого raw/display: `56816.342352` / `56 816`
- Примечание: supplier_required_volume_m3 берётся вручную от поставщика / Технониколь.

### 9. Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты J)

- Код: `eps_slope_4_2_plate_j`
- Тип строки: `materials`
- Ед. изм.: `м3`
- Количество raw: `1.458`
- Количество display: `1.46`
- Источник количества: `supplier_required_volume_m3 rounded up to full packs`
- price_code: `roof_eps_slope_4_2_plate_j_m3`

Формула:
- supplier_required_volume_m3: `1.43`
- pack_volume_m3: `0.2916`
- packs_ordered: `5`
- ordered_volume_m3: `1.458`

Округление и итог:
- Материалы raw/display: `14417.68086` / `14 418`
- Работы raw/display: `0` / `0`
- Итого raw/display: `14417.68086` / `14 418`
- Примечание: supplier_required_volume_m3 берётся вручную от поставщика / Технониколь.

### 10. Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты K)

- Код: `eps_slope_4_2_plate_k`
- Тип строки: `materials`
- Ед. изм.: `м3`
- Количество raw: `1.6416`
- Количество display: `1.64`
- Источник количества: `supplier_required_volume_m3 rounded up to full packs`
- price_code: `roof_eps_slope_4_2_plate_k_m3`

Формула:
- supplier_required_volume_m3: `1.5`
- pack_volume_m3: `0.2736`
- packs_ordered: `6`
- ordered_volume_m3: `1.6416`

Округление и итог:
- Материалы raw/display: `16233.240672` / `16 233`
- Работы raw/display: `0` / `0`
- Итого raw/display: `16233.240672` / `16 233`
- Примечание: supplier_required_volume_m3 берётся вручную от поставщика / Технониколь.

### 11. Геотекстиль ТЕХНОНИКОЛЬ ПРОФ Кровля 300, 2х50м

- Код: `geotextile_prof_300_flat`
- Тип строки: `materials`
- Ед. изм.: `м2`
- Количество raw: `300`
- Количество display: `300`
- Источник количества: `roof_area_total_m2 * geotextile_flat_coeff rounded to rolls`
- price_code: `roof_geotextile_technonikol_prof_300_m2`

Формула:
- required_area_m2: `273.812`
- roll_area_m2: `100`
- rolls_ordered: `3`
- ordered_area_m2: `300`

Округление и итог:
- Материалы raw/display: `33528` / `33 528`
- Работы raw/display: `0` / `0`
- Итого raw/display: `33528` / `33 528`

### 12. Геотекстиль ТЕХНОНИКОЛЬ ПРОФ Кровля 150, 2х50м

- Код: `geotextile_prof_150_parapet`
- Тип строки: `materials`
- Ед. изм.: `м2`
- Количество raw: `200`
- Количество display: `200`
- Источник количества: `parapet_and_abutment_total_length_m * geotextile_parapet_coeff rounded to rolls`
- price_code: `roof_geotextile_technonikol_prof_150_m2`

Формула:
- required_area_m2: `152.482`
- roll_area_m2: `100`
- rolls_ordered: `2`
- ordered_area_m2: `200`

Округление и итог:
- Материалы raw/display: `11512` / `11 512`
- Работы raw/display: `0` / `0`
- Итого raw/display: `11512` / `11 512`

### 13. Укладка ПВХ Мембраны

- Код: `pvc_membrane_flat_installation`
- Тип строки: `work`
- Ед. изм.: `м2`
- Количество raw: `248.92`
- Количество display: `248.92`
- Источник количества: `roof_area_total_m2`

Округление и итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `184200.8` / `184 201`
- Итого raw/display: `184200.8` / `184 201`

### 14. Монтаж примыкания кровли из ПВХ мембраны

- Код: `pvc_membrane_abutment_installation`
- Тип строки: `work`
- Ед. изм.: `мп`
- Количество raw: `138.62`
- Количество display: `138.62`
- Источник количества: `parapet_and_abutment_total_length_m`

Округление и итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `97034` / `97 034`
- Итого raw/display: `97034` / `97 034`

### 15. Монтаж примыкания к вентшахтам

- Код: `vent_shaft_abutment_installation`
- Тип строки: `work`
- Ед. изм.: `шт`
- Количество raw: `3`
- Количество display: `3`
- Источник количества: `vent_shaft_abutment_count`

Округление и итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `15000` / `15 000`
- Итого raw/display: `15000` / `15 000`

### 16. Рейка прижимная алюминиевая 3м

- Код: `aluminum_pressure_rail_3m`
- Тип строки: `materials`
- Ед. изм.: `мп`
- Количество raw: `141`
- Количество display: `141`
- Источник количества: `parapet_and_abutment_total_length_m rounded to rail pieces`
- price_code: `roof_aluminum_pressure_rail_m`

Формула:
- pieces_ordered: `47`
- ordered_length_m: `141`

Округление и итог:
- Материалы raw/display: `12690` / `12 690`
- Работы raw/display: `0` / `0`
- Итого raw/display: `12690` / `12 690`

### 17. Рейка краевая алюминиевая 3м

- Код: `aluminum_edge_rail_3m`
- Тип строки: `materials`
- Ед. изм.: `мп`
- Количество raw: `141`
- Количество display: `141`
- Источник количества: `parapet_and_abutment_total_length_m rounded to rail pieces`
- price_code: `roof_aluminum_edge_rail_m`

Формула:
- pieces_ordered: `47`
- ordered_length_m: `141`

Округление и итог:
- Материалы raw/display: `13395` / `13 395`
- Работы raw/display: `0` / `0`
- Итого raw/display: `13395` / `13 395`

### 18. Полимерная мембрана ПВХ Logicroof V-RP 1,5 мм мембрана серая, 2,10х20

- Код: `pvc_membrane_logicroof_vrp_1_5mm_gray`
- Тип строки: `materials`
- Ед. изм.: `рул`
- Количество raw: `11`
- Количество display: `11`
- Источник количества: `flat and abutment membrane areas rounded to rolls`
- price_code: `roof_pvc_membrane_logicroof_vrp_1_5mm_gray_roll`

Формула:
- flat_area_m2: `286.258`
- abutment_area_m2: `152.482`
- required_area_m2: `438.74`
- roll_area_m2: `42`
- rolls_ordered: `11`

Округление и итог:
- Материалы raw/display: `12616.01` / `12 616`
- Работы raw/display: `0` / `0`
- Итого raw/display: `12616.01` / `12 616`

### 19. Аэратор кровельный PVC, 75х375 (без пробивки отверстий)

- Код: `roof_pvc_aerator_75x375`
- Тип строки: `material_and_work`
- Ед. изм.: `шт`
- Количество raw: `3`
- Количество display: `3`
- Источник количества: `roof_aerators_count`
- price_code: `roof_pvc_aerator_75x375_item`

Округление и итог:
- Материалы raw/display: `1761` / `1 761`
- Работы raw/display: `8250` / `8 250`
- Итого raw/display: `10011` / `10 011`

### 20. Установка воронки парапетной (без пробивки отверстий)

- Код: `parapet_roof_drain_installation`
- Тип строки: `material_and_work`
- Ед. изм.: `шт`
- Количество raw: `2`
- Количество display: `2`
- Источник количества: `parapet_roof_drains_count`
- price_code: `roof_parapet_drain_item`

Округление и итог:
- Материалы raw/display: `10000` / `10 000`
- Работы raw/display: `11000` / `11 000`
- Итого raw/display: `21000` / `21 000`

### 21. Пробивка отверстий в стенах из газоблока толщ.400мм

- Код: `gas_block_wall_hole_drilling`
- Тип строки: `work`
- Ед. изм.: `шт`
- Количество raw: `2`
- Количество display: `2`
- Источник количества: `gas_block_wall_holes_count`

Округление и итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `6000` / `6 000`
- Итого raw/display: `6000` / `6 000`
- Примечание: Ручная строка; количество отверстий не всегда равно количеству парапетных воронок.

### 22. Установка воронки кровельной (с обжимным мет. фланцем с обогревом 110х450мм) (без пробивки отверстий)

- Код: `internal_roof_drain_with_heating`
- Тип строки: `material_and_work`
- Ед. изм.: `шт`
- Количество raw: `3`
- Количество display: `3`
- Источник количества: `internal_roof_drains_count`
- price_code: `roof_internal_drain_with_heating_item`

Округление и итог:
- Материалы raw/display: `15000` / `15 000`
- Работы raw/display: `16500` / `16 500`
- Итого raw/display: `31500` / `31 500`

### 23. Устройство внутреннего водостока (ПВХ Ф110мм) (ориентировочно)

- Код: `internal_drain_pvc_110mm`
- Тип строки: `material_and_work`
- Ед. изм.: `мп`
- Количество raw: `11.25`
- Количество display: `11.25`
- Источник количества: `internal_roof_drains_count * internal_drain_height_per_drain_m`
- price_code: `roof_internal_drain_pvc_110mm_m`

Округление и итог:
- Материалы raw/display: `28125` / `28 125`
- Работы raw/display: `33750` / `33 750`
- Итого raw/display: `61875` / `61 875`
- Примечание: internal_drain_height_per_drain_m = 3.75 is a project input, not a permanent constant.

### 24. Подъем материалов автокраном

- Код: `roof_crane_lifting`
- Тип строки: `fixed_manual_machinery`
- Ед. изм.: `смена`
- Количество raw: `1`
- Количество display: `1`
- Источник количества: `roof_crane_lifting_shifts`
- price_code: `roof_crane_lifting_shift`

Округление и итог:
- Материалы raw/display: `30000` / `30 000`
- Работы raw/display: `0` / `0`
- Итого raw/display: `30000` / `30 000`

### 25. Расходные материалы, амортизация инструмента

- Код: `roof_consumables_tool_depreciation`
- Тип строки: `manual_percentage_addon`
- Ед. изм.: `комплект`
- Количество raw: `1`
- Количество display: `1`
- Источник количества: `provided roof_consumables_total_raw`

Округление и итог:
- Материалы raw/display: `75297.06` / `75 297`
- Работы raw/display: `0` / `0`
- Итого raw/display: `75297.06` / `75 297`
- Примечание: temporarily uses provided raw total; base formula to be confirmed later.

### 26. Вывоз мусора с объекта

- Код: `roof_waste_removal`
- Тип строки: `material_and_work`
- Ед. изм.: `маш`
- Количество raw: `3`
- Количество display: `3`
- Источник количества: `roof_waste_removal_trucks`

Округление и итог:
- Материалы raw/display: `30000` / `30 000`
- Работы raw/display: `10500` / `10 500`
- Итого raw/display: `40500` / `40 500`

### 27. Логистика, и снабжение

- Код: `roof_logistics_and_supply`
- Тип строки: `manual_fixed_material`
- Ед. изм.: `-`
- Количество raw: `1`
- Количество display: `1`
- Источник количества: `provided roof_logistics_and_supply_total_raw`

Округление и итог:
- Материалы raw/display: `37648.53` / `37 649`
- Работы raw/display: `0` / `0`
- Итого raw/display: `37648.53` / `37 649`
- Примечание: Строка включена по уточнению: это серая внутренняя себестоимость текущего раздела.

### 28. Технический надзор

- Код: `technical_supervision`
- Тип строки: `manual_fixed_work`
- Ед. изм.: `-`
- Количество raw: `1`
- Количество display: `1`
- Источник количества: `provided technical_supervision_work_total`

Округление и итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `10000` / `10 000`
- Итого raw/display: `10000` / `10 000`
- Примечание: Строка включена по уточнению: это серая внутренняя работа текущего раздела.

### 29. Заготовительно-складские расходы

- Код: `procurement_storage`
- Тип строки: `manual_fixed_work`
- Ед. изм.: `-`
- Количество raw: `1`
- Количество display: `1`
- Источник количества: `provided procurement_storage_work_total`

Округление и итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `15000` / `15 000`
- Итого raw/display: `15000` / `15 000`
- Примечание: Строка включена по сверке с серой зоной: 15 000 входит во внутреннюю себестоимость.

### 30. Накладные и общехозяйственные расходы

- Код: `overhead_zero`
- Тип строки: `zero_excel_structure_line`
- Ед. изм.: `-`
- Количество raw: `1`
- Количество display: `1`
- Источник количества: `excel structure line`

Округление и итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `0` / `0`
- Итого raw/display: `0` / `0`
- Примечание: Строка сохранена для структуры Excel.
- Примечание: В текущем scope серая внутренняя себестоимость равна 0.

### 31. Сметная прибыль

- Код: `profit_zero`
- Тип строки: `zero_excel_structure_line`
- Ед. изм.: `-`
- Количество raw: `1`
- Количество display: `1`
- Источник количества: `excel structure line`

Округление и итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `0` / `0`
- Итого raw/display: `0` / `0`
- Примечание: Строка сохранена для структуры Excel.
- Примечание: В текущем scope серая внутренняя себестоимость равна 0.

## Warnings

- project_spec_roof_area_m2 is not used without human review; current calculation uses roof geometry totals.
- Slope insulation plate volumes are supplier/Technonikol manual inputs, not geometry-derived values.
- Temporary door line is case-specific and is not included in this universal base calculator.
- Roof consumables use provided raw total; base formula is to be confirmed later.
- Logistics and supply uses provided raw total from the reviewed gray estimate.
- Technical supervision uses provided gray work total from the reviewed estimate.
- Procurement/storage uses provided gray work total from the reviewed estimate.

## Источники цен

| Строка сметы | price_code | старая цена | использованная цена | источник | предупреждение |
| --- | --- | ---: | ---: | --- | --- |
| Подготовка основания под укладку пароизоляционного слоя, очистка поверхности | `` | `None` | `None` | `locked_case_prices` |  |
| Пароизоляция основания плёнкой ПВХ | `` | `77` | `77` | `locked_case_prices` |  |
| Пленка пароизоляция ТехноНИКОЛЬ 120 мкм, 150 м2/рул | `roof_vapor_barrier_film_technonikol_120mk_m2` | `35` | `23.12` | `price_registry` |  |
| Утепление кровельного покрытия ЭППС (1 слой -100мм, 2 слой -100мм, 3 слой - разуклонка) | `` | `770` | `770` | `locked_case_prices` |  |
| Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON ECO (100мм) | `roof_eps100_technonikol_carbon_eco_m3` | `7326.7` | `7377.89` | `price_registry` |  |
| Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON ECO (50мм) | `roof_eps50_technonikol_carbon_eco_m3` | `6906.7` | `7155.34` | `price_registry` |  |
| Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты A) | `roof_eps_slope_2_1_plate_a_m3` | `10896` | `9888.67` | `price_registry` |  |
| Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты B) | `roof_eps_slope_2_1_plate_b_m3` | `10896` | `9888.67` | `price_registry` |  |
| Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты J) | `roof_eps_slope_4_2_plate_j_m3` | `10896` | `9888.67` | `price_registry` |  |
| Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты K) | `roof_eps_slope_4_2_plate_k_m3` | `10896` | `9888.67` | `price_registry` |  |
| Геотекстиль ТЕХНОНИКОЛЬ ПРОФ Кровля 300, 2х50м | `roof_geotextile_technonikol_prof_300_m2` | `111.76` | `111.76` | `price_registry` |  |
| Геотекстиль ТЕХНОНИКОЛЬ ПРОФ Кровля 150, 2х50м | `roof_geotextile_technonikol_prof_150_m2` | `64.34` | `57.56` | `price_registry` |  |
| Укладка ПВХ Мембраны | `` | `740` | `740` | `locked_case_prices` |  |
| Монтаж примыкания кровли из ПВХ мембраны | `` | `700` | `700` | `locked_case_prices` |  |
| Монтаж примыкания к вентшахтам | `` | `5000` | `5000` | `locked_case_prices` |  |
| Рейка прижимная алюминиевая 3м | `roof_aluminum_pressure_rail_m` | `95` | `90` | `price_registry` |  |
| Рейка краевая алюминиевая 3м | `roof_aluminum_edge_rail_m` | `98` | `95` | `price_registry` |  |
| Полимерная мембрана ПВХ Logicroof V-RP 1,5 мм мембрана серая, 2,10х20 | `roof_pvc_membrane_logicroof_vrp_1_5mm_gray_roll` | `51431` | `1146.91` | `price_registry` |  |
| Аэратор кровельный PVC, 75х375 (без пробивки отверстий) | `roof_pvc_aerator_75x375_item` | `587` | `587` | `price_registry` |  |
| Установка воронки парапетной (без пробивки отверстий) | `roof_parapet_drain_item` | `5000` | `5000` | `price_registry` |  |
| Пробивка отверстий в стенах из газоблока толщ.400мм | `` | `3000` | `3000` | `locked_case_prices` |  |
| Установка воронки кровельной (с обжимным мет. фланцем с обогревом 110х450мм) (без пробивки отверстий) | `roof_internal_drain_with_heating_item` | `5000` | `5000` | `price_registry` |  |
| Устройство внутреннего водостока (ПВХ Ф110мм) (ориентировочно) | `roof_internal_drain_pvc_110mm_m` | `2500` | `2500` | `price_registry` |  |
| Подъем материалов автокраном | `roof_crane_lifting_shift` | `30000` | `30000` | `price_registry` |  |
| Расходные материалы, амортизация инструмента | `` | `None` | `None` | `locked_case_prices` |  |
| Вывоз мусора с объекта | `` | `10000` | `10000` | `locked_case_prices` |  |
| Логистика, и снабжение | `` | `37648.53` | `37648.53` | `locked_case_prices` |  |
| Технический надзор | `` | `10000` | `10000` | `locked_case_prices` |  |
| Заготовительно-складские расходы | `` | `15000` | `15000` | `locked_case_prices` |  |
| Накладные и общехозяйственные расходы | `` | `None` | `None` | `locked_case_prices` |  |
| Сметная прибыль | `` | `None` | `None` | `locked_case_prices` |  |

## Pricing summary

- mode: `price_registry_with_fallback`
- registry_path: `/Users/tatanamedzidova/Desktop/ai_estimator/ai_estimator_mvp/output/price_registry_filled_v3.xlsx`
- prices_from_price_registry: `17`
- prices_from_project_overrides: `0`
- prices_from_fallback_input: `0`
- warnings_count: `0`

## Итоги

- Материалы raw/display: `852561.5015792` / `852 562`
- Работы raw/display: `618070.04` / `618 070`
- Итого raw/display: `1470631.5415792` / `1 470 632`
- Сумма отображённых материалов по строкам: `852 562`
- Сумма отображённых работ по строкам: `618 070`
- Сумма отображённых итогов по строкам: `1 470 632`

## Проверка

- status: `ok`
- ok: `0`
- mismatch: `0`

| scope | code | field | expected | actual | status |
| --- | --- | --- | ---: | ---: | --- |
