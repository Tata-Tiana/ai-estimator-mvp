# Расчётный отчёт: КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА / плоская кровля

AI не используется для расчёта. Калькулятор считает только серую внутреннюю себестоимость по зафиксированным формулам.
Клиентская/белая зона и коммерческие коэффициенты вне текущего scope.

## Исходные параметры кровли

- project_name: `test_flat_roof_usv`
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
- Материалы raw/display: `10500` / `10 500`
- Работы raw/display: `0` / `0`
- Итого raw/display: `10500` / `10 500`

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
- Материалы raw/display: `377082.389696` / `377 082`
- Работы raw/display: `0` / `0`
- Итого raw/display: `377082.389696` / `377 082`

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
- Материалы raw/display: `28361.67288` / `28 362`
- Работы raw/display: `0` / `0`
- Итого raw/display: `28361.67288` / `28 362`
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
- Материалы raw/display: `41304.5568` / `41 305`
- Работы raw/display: `0` / `0`
- Итого raw/display: `41304.5568` / `41 305`
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
- Материалы raw/display: `62604.0576` / `62 604`
- Работы raw/display: `0` / `0`
- Итого raw/display: `62604.0576` / `62 604`
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
- Материалы raw/display: `15886.368` / `15 886`
- Работы raw/display: `0` / `0`
- Итого raw/display: `15886.368` / `15 886`
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
- Материалы raw/display: `17886.8736` / `17 887`
- Работы raw/display: `0` / `0`
- Итого raw/display: `17886.8736` / `17 887`
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
- Материалы raw/display: `12868` / `12 868`
- Работы raw/display: `0` / `0`
- Итого raw/display: `12868` / `12 868`

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
- Материалы raw/display: `13395` / `13 395`
- Работы raw/display: `0` / `0`
- Итого raw/display: `13395` / `13 395`

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
- Материалы raw/display: `13818` / `13 818`
- Работы raw/display: `0` / `0`
- Итого raw/display: `13818` / `13 818`

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
- Материалы raw/display: `565741` / `565 741`
- Работы raw/display: `0` / `0`
- Итого raw/display: `565741` / `565 741`

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
- Roof consumables use provided raw total; base formula is to be confirmed later.
- Logistics and supply uses provided raw total from the reviewed gray estimate.
- Technical supervision uses provided gray work total from the reviewed estimate.
- Procurement/storage uses provided gray work total from the reviewed estimate.

## Итоги

- Материалы raw/display: `1420807.508576` / `1 420 808`
- Работы raw/display: `618070.04` / `618 070`
- Итого raw/display: `2038878` / `2 038 878`
- Сумма отображённых материалов по строкам: `1 420 808`
- Сумма отображённых работ по строкам: `618 070`
- Сумма отображённых итогов по строкам: `2 038 878`

## Проверка

- status: `ok`
- ok: `460`
- mismatch: `0`

| scope | code | field | expected | actual | status |
| --- | --- | --- | ---: | ---: | --- |
| totals | `internal_materials_total_raw` | `internal_materials_total_raw` | 1420807.508576 | 1420807.508576 | ok |
| totals | `internal_materials_total` | `internal_materials_total` | 1420808 | 1420808 | ok |
| totals | `internal_works_total_raw` | `internal_works_total_raw` | 618070.04 | 618070.04 | ok |
| totals | `internal_works_total` | `internal_works_total` | 618070 | 618070 | ok |
| totals | `internal_section_total_raw` | `internal_section_total_raw` | 2038878 | 2038878 | ok |
| totals | `internal_section_total` | `internal_section_total` | 2038878 | 2038878 | ok |
| totals | `sum_of_displayed_line_material_totals` | `sum_of_displayed_line_material_totals` | 1420808 | 1420808 | ok |
| totals | `sum_of_displayed_line_work_totals` | `sum_of_displayed_line_work_totals` | 618070 | 618070 | ok |
| totals | `sum_of_displayed_line_totals` | `sum_of_displayed_line_totals` | 2038878 | 2038878 | ok |
| estimate_lines | `roof_base_preparation_control` | `name` | Подготовка основания под укладку пароизоляционного слоя, очистка поверхности | Подготовка основания под укладку пароизоляционного слоя, очистка поверхности | ok |
| estimate_lines | `roof_base_preparation_control` | `unit` | м2 | м2 | ok |
| estimate_lines | `roof_base_preparation_control` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `roof_base_preparation_control` | `quantity_raw` | 248.92 | 248.92 | ok |
| estimate_lines | `roof_base_preparation_control` | `quantity_display` | 248.92 | 248.92 | ok |
| estimate_lines | `roof_base_preparation_control` | `quantity_source` | roof_area_total_m2 | roof_area_total_m2 | ok |
| estimate_lines | `roof_base_preparation_control` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `roof_base_preparation_control` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `roof_base_preparation_control` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `roof_base_preparation_control` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `roof_base_preparation_control` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `roof_base_preparation_control` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `roof_base_preparation_control` | `internal_cost.line_total_raw` | 0 | 0 | ok |
| estimate_lines | `roof_base_preparation_control` | `internal_cost.line_total` | 0 | 0 | ok |
| estimate_lines | `vapor_barrier_installation` | `name` | Пароизоляция основания плёнкой ПВХ | Пароизоляция основания плёнкой ПВХ | ok |
| estimate_lines | `vapor_barrier_installation` | `unit` | м2 | м2 | ok |
| estimate_lines | `vapor_barrier_installation` | `line_type` | work | work | ok |
| estimate_lines | `vapor_barrier_installation` | `quantity_raw` | 248.92 | 248.92 | ok |
| estimate_lines | `vapor_barrier_installation` | `quantity_display` | 248.92 | 248.92 | ok |
| estimate_lines | `vapor_barrier_installation` | `quantity_source` | roof_area_total_m2 | roof_area_total_m2 | ok |
| estimate_lines | `vapor_barrier_installation` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `vapor_barrier_installation` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `vapor_barrier_installation` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `vapor_barrier_installation` | `internal_cost.work_unit_price` | 77 | 77 | ok |
| estimate_lines | `vapor_barrier_installation` | `internal_cost.work_total_raw` | 19166.84 | 19166.84 | ok |
| estimate_lines | `vapor_barrier_installation` | `internal_cost.work_total` | 19167 | 19167 | ok |
| estimate_lines | `vapor_barrier_installation` | `internal_cost.line_total_raw` | 19166.84 | 19166.84 | ok |
| estimate_lines | `vapor_barrier_installation` | `internal_cost.line_total` | 19167 | 19167 | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `name` | Пленка пароизоляция ТехноНИКОЛЬ 120 мкм, 150 м2/рул | Пленка пароизоляция ТехноНИКОЛЬ 120 мкм, 150 м2/рул | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `unit` | м2 | м2 | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `line_type` | materials | materials | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `quantity_raw` | 300 | 300 | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `quantity_display` | 300 | 300 | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `quantity_source` | roof_area_total_m2 * vapor_barrier_film_overlap_coeff rounded to rolls | roof_area_total_m2 * vapor_barrier_film_overlap_coeff rounded to rolls | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `price_code` | roof_vapor_barrier_film_technonikol_120mk_m2 | roof_vapor_barrier_film_technonikol_120mk_m2 | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `internal_cost.material_unit_price` | 35 | 35 | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `internal_cost.material_total_raw` | 10500 | 10500 | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `internal_cost.material_total` | 10500 | 10500 | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `internal_cost.line_total_raw` | 10500 | 10500 | ok |
| estimate_lines | `vapor_barrier_film_technonikol_120mk` | `internal_cost.line_total` | 10500 | 10500 | ok |
| estimate_lines | `eps_roof_insulation_installation` | `name` | Утепление кровельного покрытия ЭППС (1 слой -100мм, 2 слой -100мм, 3 слой - разуклонка) | Утепление кровельного покрытия ЭППС (1 слой -100мм, 2 слой -100мм, 3 слой - разуклонка) | ok |
| estimate_lines | `eps_roof_insulation_installation` | `unit` | м2 | м2 | ok |
| estimate_lines | `eps_roof_insulation_installation` | `line_type` | work | work | ok |
| estimate_lines | `eps_roof_insulation_installation` | `quantity_raw` | 248.92 | 248.92 | ok |
| estimate_lines | `eps_roof_insulation_installation` | `quantity_display` | 248.92 | 248.92 | ok |
| estimate_lines | `eps_roof_insulation_installation` | `quantity_source` | roof_area_total_m2 | roof_area_total_m2 | ok |
| estimate_lines | `eps_roof_insulation_installation` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `eps_roof_insulation_installation` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `eps_roof_insulation_installation` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `eps_roof_insulation_installation` | `internal_cost.work_unit_price` | 770 | 770 | ok |
| estimate_lines | `eps_roof_insulation_installation` | `internal_cost.work_total_raw` | 191668.4 | 191668.4 | ok |
| estimate_lines | `eps_roof_insulation_installation` | `internal_cost.work_total` | 191668 | 191668 | ok |
| estimate_lines | `eps_roof_insulation_installation` | `internal_cost.line_total_raw` | 191668.4 | 191668.4 | ok |
| estimate_lines | `eps_roof_insulation_installation` | `internal_cost.line_total` | 191668 | 191668 | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `name` | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON ECO (100мм) | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON ECO (100мм) | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `unit` | м3 | м3 | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `line_type` | materials | materials | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `quantity_raw` | 51.46688 | 51.46688 | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `quantity_display` | 51.47 | 51.47 | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `quantity_source` | roof_area_total_m2 * eps_main_thickness_m * eps_insulation_waste_coeff rounded to packs | roof_area_total_m2 * eps_main_thickness_m * eps_insulation_waste_coeff rounded to packs | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `price_code` | roof_eps100_technonikol_carbon_eco_m3 | roof_eps100_technonikol_carbon_eco_m3 | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `internal_cost.material_unit_price` | 7326.7 | 7326.7 | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `internal_cost.material_total_raw` | 377082.389696 | 377082.389696 | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `internal_cost.material_total` | 377082 | 377082 | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `internal_cost.line_total_raw` | 377082.389696 | 377082.389696 | ok |
| estimate_lines | `eps100_technonikol_carbon_eco` | `internal_cost.line_total` | 377082 | 377082 | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `name` | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON ECO (50мм) | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON ECO (50мм) | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `unit` | м3 | м3 | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `line_type` | materials | materials | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `quantity_raw` | 4.1064 | 4.1064 | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `quantity_display` | 4.11 | 4.11 | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `quantity_source` | supplier_required_volume_m3 rounded up to full packs | supplier_required_volume_m3 rounded up to full packs | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `price_code` | roof_eps50_technonikol_carbon_eco_m3 | roof_eps50_technonikol_carbon_eco_m3 | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `internal_cost.material_unit_price` | 6906.7 | 6906.7 | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `internal_cost.material_total_raw` | 28361.67288 | 28361.67288 | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `internal_cost.material_total` | 28362 | 28362 | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `internal_cost.line_total_raw` | 28361.67288 | 28361.67288 | ok |
| estimate_lines | `eps50_technonikol_carbon_eco` | `internal_cost.line_total` | 28362 | 28362 | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `name` | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты A) | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты A) | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `unit` | м3 | м3 | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `line_type` | materials | materials | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `quantity_raw` | 3.7908 | 3.7908 | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `quantity_display` | 3.79 | 3.79 | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `quantity_source` | supplier_required_volume_m3 rounded up to full packs | supplier_required_volume_m3 rounded up to full packs | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `price_code` | roof_eps_slope_2_1_plate_a_m3 | roof_eps_slope_2_1_plate_a_m3 | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `internal_cost.material_unit_price` | 10896 | 10896 | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `internal_cost.material_total_raw` | 41304.5568 | 41304.5568 | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `internal_cost.material_total` | 41305 | 41305 | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `internal_cost.line_total_raw` | 41304.5568 | 41304.5568 | ok |
| estimate_lines | `eps_slope_2_1_plate_a` | `internal_cost.line_total` | 41305 | 41305 | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `name` | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты B) | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты B) | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `unit` | м3 | м3 | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `line_type` | materials | materials | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `quantity_raw` | 5.7456 | 5.7456 | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `quantity_display` | 5.75 | 5.75 | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `quantity_source` | supplier_required_volume_m3 rounded up to full packs | supplier_required_volume_m3 rounded up to full packs | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `price_code` | roof_eps_slope_2_1_plate_b_m3 | roof_eps_slope_2_1_plate_b_m3 | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `internal_cost.material_unit_price` | 10896 | 10896 | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `internal_cost.material_total_raw` | 62604.0576 | 62604.0576 | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `internal_cost.material_total` | 62604 | 62604 | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `internal_cost.line_total_raw` | 62604.0576 | 62604.0576 | ok |
| estimate_lines | `eps_slope_2_1_plate_b` | `internal_cost.line_total` | 62604 | 62604 | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `name` | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты J) | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты J) | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `unit` | м3 | м3 | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `line_type` | materials | materials | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `quantity_raw` | 1.458 | 1.458 | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `quantity_display` | 1.46 | 1.46 | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `quantity_source` | supplier_required_volume_m3 rounded up to full packs | supplier_required_volume_m3 rounded up to full packs | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `price_code` | roof_eps_slope_4_2_plate_j_m3 | roof_eps_slope_4_2_plate_j_m3 | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `internal_cost.material_unit_price` | 10896 | 10896 | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `internal_cost.material_total_raw` | 15886.368 | 15886.368 | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `internal_cost.material_total` | 15886 | 15886 | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `internal_cost.line_total_raw` | 15886.368 | 15886.368 | ok |
| estimate_lines | `eps_slope_4_2_plate_j` | `internal_cost.line_total` | 15886 | 15886 | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `name` | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты K) | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты K) | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `unit` | м3 | м3 | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `line_type` | materials | materials | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `quantity_raw` | 1.6416 | 1.6416 | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `quantity_display` | 1.64 | 1.64 | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `quantity_source` | supplier_required_volume_m3 rounded up to full packs | supplier_required_volume_m3 rounded up to full packs | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `price_code` | roof_eps_slope_4_2_plate_k_m3 | roof_eps_slope_4_2_plate_k_m3 | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `internal_cost.material_unit_price` | 10896 | 10896 | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `internal_cost.material_total_raw` | 17886.8736 | 17886.8736 | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `internal_cost.material_total` | 17887 | 17887 | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `internal_cost.line_total_raw` | 17886.8736 | 17886.8736 | ok |
| estimate_lines | `eps_slope_4_2_plate_k` | `internal_cost.line_total` | 17887 | 17887 | ok |
| estimate_lines | `geotextile_prof_300_flat` | `name` | Геотекстиль ТЕХНОНИКОЛЬ ПРОФ Кровля 300, 2х50м | Геотекстиль ТЕХНОНИКОЛЬ ПРОФ Кровля 300, 2х50м | ok |
| estimate_lines | `geotextile_prof_300_flat` | `unit` | м2 | м2 | ok |
| estimate_lines | `geotextile_prof_300_flat` | `line_type` | materials | materials | ok |
| estimate_lines | `geotextile_prof_300_flat` | `quantity_raw` | 300 | 300 | ok |
| estimate_lines | `geotextile_prof_300_flat` | `quantity_display` | 300 | 300 | ok |
| estimate_lines | `geotextile_prof_300_flat` | `quantity_source` | roof_area_total_m2 * geotextile_flat_coeff rounded to rolls | roof_area_total_m2 * geotextile_flat_coeff rounded to rolls | ok |
| estimate_lines | `geotextile_prof_300_flat` | `price_code` | roof_geotextile_technonikol_prof_300_m2 | roof_geotextile_technonikol_prof_300_m2 | ok |
| estimate_lines | `geotextile_prof_300_flat` | `internal_cost.material_unit_price` | 111.76 | 111.76 | ok |
| estimate_lines | `geotextile_prof_300_flat` | `internal_cost.material_total_raw` | 33528 | 33528 | ok |
| estimate_lines | `geotextile_prof_300_flat` | `internal_cost.material_total` | 33528 | 33528 | ok |
| estimate_lines | `geotextile_prof_300_flat` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `geotextile_prof_300_flat` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `geotextile_prof_300_flat` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `geotextile_prof_300_flat` | `internal_cost.line_total_raw` | 33528 | 33528 | ok |
| estimate_lines | `geotextile_prof_300_flat` | `internal_cost.line_total` | 33528 | 33528 | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `name` | Геотекстиль ТЕХНОНИКОЛЬ ПРОФ Кровля 150, 2х50м | Геотекстиль ТЕХНОНИКОЛЬ ПРОФ Кровля 150, 2х50м | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `unit` | м2 | м2 | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `line_type` | materials | materials | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `quantity_raw` | 200 | 200 | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `quantity_display` | 200 | 200 | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `quantity_source` | parapet_and_abutment_total_length_m * geotextile_parapet_coeff rounded to rolls | parapet_and_abutment_total_length_m * geotextile_parapet_coeff rounded to rolls | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `price_code` | roof_geotextile_technonikol_prof_150_m2 | roof_geotextile_technonikol_prof_150_m2 | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `internal_cost.material_unit_price` | 64.34 | 64.34 | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `internal_cost.material_total_raw` | 12868 | 12868 | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `internal_cost.material_total` | 12868 | 12868 | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `internal_cost.line_total_raw` | 12868 | 12868 | ok |
| estimate_lines | `geotextile_prof_150_parapet` | `internal_cost.line_total` | 12868 | 12868 | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `name` | Укладка ПВХ Мембраны | Укладка ПВХ Мембраны | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `unit` | м2 | м2 | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `line_type` | work | work | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `quantity_raw` | 248.92 | 248.92 | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `quantity_display` | 248.92 | 248.92 | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `quantity_source` | roof_area_total_m2 | roof_area_total_m2 | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `internal_cost.work_unit_price` | 740 | 740 | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `internal_cost.work_total_raw` | 184200.8 | 184200.8 | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `internal_cost.work_total` | 184201 | 184201 | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `internal_cost.line_total_raw` | 184200.8 | 184200.8 | ok |
| estimate_lines | `pvc_membrane_flat_installation` | `internal_cost.line_total` | 184201 | 184201 | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `name` | Монтаж примыкания кровли из ПВХ мембраны | Монтаж примыкания кровли из ПВХ мембраны | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `unit` | мп | мп | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `line_type` | work | work | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `quantity_raw` | 138.62 | 138.62 | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `quantity_display` | 138.62 | 138.62 | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `quantity_source` | parapet_and_abutment_total_length_m | parapet_and_abutment_total_length_m | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `internal_cost.work_unit_price` | 700 | 700 | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `internal_cost.work_total_raw` | 97034 | 97034 | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `internal_cost.work_total` | 97034 | 97034 | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `internal_cost.line_total_raw` | 97034 | 97034 | ok |
| estimate_lines | `pvc_membrane_abutment_installation` | `internal_cost.line_total` | 97034 | 97034 | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `name` | Монтаж примыкания к вентшахтам | Монтаж примыкания к вентшахтам | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `unit` | шт | шт | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `line_type` | work | work | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `quantity_raw` | 3 | 3 | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `quantity_display` | 3 | 3 | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `quantity_source` | vent_shaft_abutment_count | vent_shaft_abutment_count | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `internal_cost.work_unit_price` | 5000 | 5000 | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `internal_cost.work_total_raw` | 15000 | 15000 | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `internal_cost.work_total` | 15000 | 15000 | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `internal_cost.line_total_raw` | 15000 | 15000 | ok |
| estimate_lines | `vent_shaft_abutment_installation` | `internal_cost.line_total` | 15000 | 15000 | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `name` | Рейка прижимная алюминиевая 3м | Рейка прижимная алюминиевая 3м | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `unit` | мп | мп | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `line_type` | materials | materials | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `quantity_raw` | 141 | 141 | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `quantity_display` | 141 | 141 | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `quantity_source` | parapet_and_abutment_total_length_m rounded to rail pieces | parapet_and_abutment_total_length_m rounded to rail pieces | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `price_code` | roof_aluminum_pressure_rail_m | roof_aluminum_pressure_rail_m | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `internal_cost.material_unit_price` | 95 | 95 | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `internal_cost.material_total_raw` | 13395 | 13395 | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `internal_cost.material_total` | 13395 | 13395 | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `internal_cost.line_total_raw` | 13395 | 13395 | ok |
| estimate_lines | `aluminum_pressure_rail_3m` | `internal_cost.line_total` | 13395 | 13395 | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `name` | Рейка краевая алюминиевая 3м | Рейка краевая алюминиевая 3м | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `unit` | мп | мп | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `line_type` | materials | materials | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `quantity_raw` | 141 | 141 | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `quantity_display` | 141 | 141 | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `quantity_source` | parapet_and_abutment_total_length_m rounded to rail pieces | parapet_and_abutment_total_length_m rounded to rail pieces | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `price_code` | roof_aluminum_edge_rail_m | roof_aluminum_edge_rail_m | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `internal_cost.material_unit_price` | 98 | 98 | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `internal_cost.material_total_raw` | 13818 | 13818 | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `internal_cost.material_total` | 13818 | 13818 | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `internal_cost.line_total_raw` | 13818 | 13818 | ok |
| estimate_lines | `aluminum_edge_rail_3m` | `internal_cost.line_total` | 13818 | 13818 | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `name` | Полимерная мембрана ПВХ Logicroof V-RP 1,5 мм мембрана серая, 2,10х20 | Полимерная мембрана ПВХ Logicroof V-RP 1,5 мм мембрана серая, 2,10х20 | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `unit` | рул | рул | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `line_type` | materials | materials | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `quantity_raw` | 11 | 11 | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `quantity_display` | 11 | 11 | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `quantity_source` | flat and abutment membrane areas rounded to rolls | flat and abutment membrane areas rounded to rolls | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `price_code` | roof_pvc_membrane_logicroof_vrp_1_5mm_gray_roll | roof_pvc_membrane_logicroof_vrp_1_5mm_gray_roll | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `internal_cost.material_unit_price` | 51431 | 51431 | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `internal_cost.material_total_raw` | 565741 | 565741 | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `internal_cost.material_total` | 565741 | 565741 | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `internal_cost.line_total_raw` | 565741 | 565741 | ok |
| estimate_lines | `pvc_membrane_logicroof_vrp_1_5mm_gray` | `internal_cost.line_total` | 565741 | 565741 | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `name` | Аэратор кровельный PVC, 75х375 (без пробивки отверстий) | Аэратор кровельный PVC, 75х375 (без пробивки отверстий) | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `unit` | шт | шт | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `line_type` | material_and_work | material_and_work | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `quantity_raw` | 3 | 3 | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `quantity_display` | 3 | 3 | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `quantity_source` | roof_aerators_count | roof_aerators_count | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `price_code` | roof_pvc_aerator_75x375_item | roof_pvc_aerator_75x375_item | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `internal_cost.material_unit_price` | 587 | 587 | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `internal_cost.material_total_raw` | 1761 | 1761 | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `internal_cost.material_total` | 1761 | 1761 | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `internal_cost.work_unit_price` | 2750 | 2750 | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `internal_cost.work_total_raw` | 8250 | 8250 | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `internal_cost.work_total` | 8250 | 8250 | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `internal_cost.line_total_raw` | 10011 | 10011 | ok |
| estimate_lines | `roof_pvc_aerator_75x375` | `internal_cost.line_total` | 10011 | 10011 | ok |
| estimate_lines | `parapet_roof_drain_installation` | `name` | Установка воронки парапетной (без пробивки отверстий) | Установка воронки парапетной (без пробивки отверстий) | ok |
| estimate_lines | `parapet_roof_drain_installation` | `unit` | шт | шт | ok |
| estimate_lines | `parapet_roof_drain_installation` | `line_type` | material_and_work | material_and_work | ok |
| estimate_lines | `parapet_roof_drain_installation` | `quantity_raw` | 2 | 2 | ok |
| estimate_lines | `parapet_roof_drain_installation` | `quantity_display` | 2 | 2 | ok |
| estimate_lines | `parapet_roof_drain_installation` | `quantity_source` | parapet_roof_drains_count | parapet_roof_drains_count | ok |
| estimate_lines | `parapet_roof_drain_installation` | `price_code` | roof_parapet_drain_item | roof_parapet_drain_item | ok |
| estimate_lines | `parapet_roof_drain_installation` | `internal_cost.material_unit_price` | 5000 | 5000 | ok |
| estimate_lines | `parapet_roof_drain_installation` | `internal_cost.material_total_raw` | 10000 | 10000 | ok |
| estimate_lines | `parapet_roof_drain_installation` | `internal_cost.material_total` | 10000 | 10000 | ok |
| estimate_lines | `parapet_roof_drain_installation` | `internal_cost.work_unit_price` | 5500 | 5500 | ok |
| estimate_lines | `parapet_roof_drain_installation` | `internal_cost.work_total_raw` | 11000 | 11000 | ok |
| estimate_lines | `parapet_roof_drain_installation` | `internal_cost.work_total` | 11000 | 11000 | ok |
| estimate_lines | `parapet_roof_drain_installation` | `internal_cost.line_total_raw` | 21000 | 21000 | ok |
| estimate_lines | `parapet_roof_drain_installation` | `internal_cost.line_total` | 21000 | 21000 | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `name` | Пробивка отверстий в стенах из газоблока толщ.400мм | Пробивка отверстий в стенах из газоблока толщ.400мм | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `unit` | шт | шт | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `line_type` | work | work | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `quantity_raw` | 2 | 2 | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `quantity_display` | 2 | 2 | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `quantity_source` | gas_block_wall_holes_count | gas_block_wall_holes_count | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `internal_cost.work_unit_price` | 3000 | 3000 | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `internal_cost.work_total_raw` | 6000 | 6000 | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `internal_cost.work_total` | 6000 | 6000 | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `internal_cost.line_total_raw` | 6000 | 6000 | ok |
| estimate_lines | `gas_block_wall_hole_drilling` | `internal_cost.line_total` | 6000 | 6000 | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `name` | Установка воронки кровельной (с обжимным мет. фланцем с обогревом 110х450мм) (без пробивки отверстий) | Установка воронки кровельной (с обжимным мет. фланцем с обогревом 110х450мм) (без пробивки отверстий) | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `unit` | шт | шт | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `line_type` | material_and_work | material_and_work | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `quantity_raw` | 3 | 3 | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `quantity_display` | 3 | 3 | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `quantity_source` | internal_roof_drains_count | internal_roof_drains_count | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `price_code` | roof_internal_drain_with_heating_item | roof_internal_drain_with_heating_item | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `internal_cost.material_unit_price` | 5000 | 5000 | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `internal_cost.material_total_raw` | 15000 | 15000 | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `internal_cost.material_total` | 15000 | 15000 | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `internal_cost.work_unit_price` | 5500 | 5500 | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `internal_cost.work_total_raw` | 16500 | 16500 | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `internal_cost.work_total` | 16500 | 16500 | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `internal_cost.line_total_raw` | 31500 | 31500 | ok |
| estimate_lines | `internal_roof_drain_with_heating` | `internal_cost.line_total` | 31500 | 31500 | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `name` | Устройство внутреннего водостока (ПВХ Ф110мм) (ориентировочно) | Устройство внутреннего водостока (ПВХ Ф110мм) (ориентировочно) | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `unit` | мп | мп | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `line_type` | material_and_work | material_and_work | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `quantity_raw` | 11.25 | 11.25 | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `quantity_display` | 11.25 | 11.25 | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `quantity_source` | internal_roof_drains_count * internal_drain_height_per_drain_m | internal_roof_drains_count * internal_drain_height_per_drain_m | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `price_code` | roof_internal_drain_pvc_110mm_m | roof_internal_drain_pvc_110mm_m | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `internal_cost.material_unit_price` | 2500 | 2500 | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `internal_cost.material_total_raw` | 28125 | 28125 | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `internal_cost.material_total` | 28125 | 28125 | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `internal_cost.work_unit_price` | 3000 | 3000 | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `internal_cost.work_total_raw` | 33750 | 33750 | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `internal_cost.work_total` | 33750 | 33750 | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `internal_cost.line_total_raw` | 61875 | 61875 | ok |
| estimate_lines | `internal_drain_pvc_110mm` | `internal_cost.line_total` | 61875 | 61875 | ok |
| estimate_lines | `roof_crane_lifting` | `name` | Подъем материалов автокраном | Подъем материалов автокраном | ok |
| estimate_lines | `roof_crane_lifting` | `unit` | смена | смена | ok |
| estimate_lines | `roof_crane_lifting` | `line_type` | fixed_manual_machinery | fixed_manual_machinery | ok |
| estimate_lines | `roof_crane_lifting` | `quantity_raw` | 1 | 1 | ok |
| estimate_lines | `roof_crane_lifting` | `quantity_display` | 1 | 1 | ok |
| estimate_lines | `roof_crane_lifting` | `quantity_source` | roof_crane_lifting_shifts | roof_crane_lifting_shifts | ok |
| estimate_lines | `roof_crane_lifting` | `price_code` | roof_crane_lifting_shift | roof_crane_lifting_shift | ok |
| estimate_lines | `roof_crane_lifting` | `internal_cost.material_unit_price` | 30000 | 30000 | ok |
| estimate_lines | `roof_crane_lifting` | `internal_cost.material_total_raw` | 30000 | 30000 | ok |
| estimate_lines | `roof_crane_lifting` | `internal_cost.material_total` | 30000 | 30000 | ok |
| estimate_lines | `roof_crane_lifting` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `roof_crane_lifting` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `roof_crane_lifting` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `roof_crane_lifting` | `internal_cost.line_total_raw` | 30000 | 30000 | ok |
| estimate_lines | `roof_crane_lifting` | `internal_cost.line_total` | 30000 | 30000 | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `name` | Расходные материалы, амортизация инструмента | Расходные материалы, амортизация инструмента | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `unit` | комплект | комплект | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `line_type` | manual_percentage_addon | manual_percentage_addon | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `quantity_raw` | 1 | 1 | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `quantity_display` | 1 | 1 | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `quantity_source` | provided roof_consumables_total_raw | provided roof_consumables_total_raw | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `internal_cost.material_total_raw` | 75297.06 | 75297.06 | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `internal_cost.material_total` | 75297 | 75297 | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `internal_cost.line_total_raw` | 75297.06 | 75297.06 | ok |
| estimate_lines | `roof_consumables_tool_depreciation` | `internal_cost.line_total` | 75297 | 75297 | ok |
| estimate_lines | `roof_waste_removal` | `name` | Вывоз мусора с объекта | Вывоз мусора с объекта | ok |
| estimate_lines | `roof_waste_removal` | `unit` | маш | маш | ok |
| estimate_lines | `roof_waste_removal` | `line_type` | material_and_work | material_and_work | ok |
| estimate_lines | `roof_waste_removal` | `quantity_raw` | 3 | 3 | ok |
| estimate_lines | `roof_waste_removal` | `quantity_display` | 3 | 3 | ok |
| estimate_lines | `roof_waste_removal` | `quantity_source` | roof_waste_removal_trucks | roof_waste_removal_trucks | ok |
| estimate_lines | `roof_waste_removal` | `internal_cost.material_unit_price` | 10000 | 10000 | ok |
| estimate_lines | `roof_waste_removal` | `internal_cost.material_total_raw` | 30000 | 30000 | ok |
| estimate_lines | `roof_waste_removal` | `internal_cost.material_total` | 30000 | 30000 | ok |
| estimate_lines | `roof_waste_removal` | `internal_cost.work_unit_price` | 3500 | 3500 | ok |
| estimate_lines | `roof_waste_removal` | `internal_cost.work_total_raw` | 10500 | 10500 | ok |
| estimate_lines | `roof_waste_removal` | `internal_cost.work_total` | 10500 | 10500 | ok |
| estimate_lines | `roof_waste_removal` | `internal_cost.line_total_raw` | 40500 | 40500 | ok |
| estimate_lines | `roof_waste_removal` | `internal_cost.line_total` | 40500 | 40500 | ok |
| estimate_lines | `roof_logistics_and_supply` | `name` | Логистика, и снабжение | Логистика, и снабжение | ok |
| estimate_lines | `roof_logistics_and_supply` | `unit` | - | - | ok |
| estimate_lines | `roof_logistics_and_supply` | `line_type` | manual_fixed_material | manual_fixed_material | ok |
| estimate_lines | `roof_logistics_and_supply` | `quantity_raw` | 1 | 1 | ok |
| estimate_lines | `roof_logistics_and_supply` | `quantity_display` | 1 | 1 | ok |
| estimate_lines | `roof_logistics_and_supply` | `quantity_source` | provided roof_logistics_and_supply_total_raw | provided roof_logistics_and_supply_total_raw | ok |
| estimate_lines | `roof_logistics_and_supply` | `internal_cost.material_unit_price` | 37648.53 | 37648.53 | ok |
| estimate_lines | `roof_logistics_and_supply` | `internal_cost.material_total_raw` | 37648.53 | 37648.53 | ok |
| estimate_lines | `roof_logistics_and_supply` | `internal_cost.material_total` | 37649 | 37649 | ok |
| estimate_lines | `roof_logistics_and_supply` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `roof_logistics_and_supply` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `roof_logistics_and_supply` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `roof_logistics_and_supply` | `internal_cost.line_total_raw` | 37648.53 | 37648.53 | ok |
| estimate_lines | `roof_logistics_and_supply` | `internal_cost.line_total` | 37649 | 37649 | ok |
| estimate_lines | `technical_supervision` | `name` | Технический надзор | Технический надзор | ok |
| estimate_lines | `technical_supervision` | `unit` | - | - | ok |
| estimate_lines | `technical_supervision` | `line_type` | manual_fixed_work | manual_fixed_work | ok |
| estimate_lines | `technical_supervision` | `quantity_raw` | 1 | 1 | ok |
| estimate_lines | `technical_supervision` | `quantity_display` | 1 | 1 | ok |
| estimate_lines | `technical_supervision` | `quantity_source` | provided technical_supervision_work_total | provided technical_supervision_work_total | ok |
| estimate_lines | `technical_supervision` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `technical_supervision` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `technical_supervision` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `technical_supervision` | `internal_cost.work_unit_price` | 10000 | 10000 | ok |
| estimate_lines | `technical_supervision` | `internal_cost.work_total_raw` | 10000 | 10000 | ok |
| estimate_lines | `technical_supervision` | `internal_cost.work_total` | 10000 | 10000 | ok |
| estimate_lines | `technical_supervision` | `internal_cost.line_total_raw` | 10000 | 10000 | ok |
| estimate_lines | `technical_supervision` | `internal_cost.line_total` | 10000 | 10000 | ok |
| estimate_lines | `procurement_storage` | `name` | Заготовительно-складские расходы | Заготовительно-складские расходы | ok |
| estimate_lines | `procurement_storage` | `unit` | - | - | ok |
| estimate_lines | `procurement_storage` | `line_type` | manual_fixed_work | manual_fixed_work | ok |
| estimate_lines | `procurement_storage` | `quantity_raw` | 1 | 1 | ok |
| estimate_lines | `procurement_storage` | `quantity_display` | 1 | 1 | ok |
| estimate_lines | `procurement_storage` | `quantity_source` | provided procurement_storage_work_total | provided procurement_storage_work_total | ok |
| estimate_lines | `procurement_storage` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `procurement_storage` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `procurement_storage` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `procurement_storage` | `internal_cost.work_unit_price` | 15000 | 15000 | ok |
| estimate_lines | `procurement_storage` | `internal_cost.work_total_raw` | 15000 | 15000 | ok |
| estimate_lines | `procurement_storage` | `internal_cost.work_total` | 15000 | 15000 | ok |
| estimate_lines | `procurement_storage` | `internal_cost.line_total_raw` | 15000 | 15000 | ok |
| estimate_lines | `procurement_storage` | `internal_cost.line_total` | 15000 | 15000 | ok |
| estimate_lines | `overhead_zero` | `name` | Накладные и общехозяйственные расходы | Накладные и общехозяйственные расходы | ok |
| estimate_lines | `overhead_zero` | `unit` | - | - | ok |
| estimate_lines | `overhead_zero` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `overhead_zero` | `quantity_raw` | 1 | 1 | ok |
| estimate_lines | `overhead_zero` | `quantity_display` | 1 | 1 | ok |
| estimate_lines | `overhead_zero` | `quantity_source` | excel structure line | excel structure line | ok |
| estimate_lines | `overhead_zero` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.line_total_raw` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.line_total` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `name` | Сметная прибыль | Сметная прибыль | ok |
| estimate_lines | `profit_zero` | `unit` | - | - | ok |
| estimate_lines | `profit_zero` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `profit_zero` | `quantity_raw` | 1 | 1 | ok |
| estimate_lines | `profit_zero` | `quantity_display` | 1 | 1 | ok |
| estimate_lines | `profit_zero` | `quantity_source` | excel structure line | excel structure line | ok |
| estimate_lines | `profit_zero` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.line_total_raw` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.line_total` | 0 | 0 | ok |
