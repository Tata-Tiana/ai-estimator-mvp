# Расчёт земляных работ: horoshevka_14

Проект: `horoshevka_14`

## Входные параметры
- `project_name`: `horoshevka_14`
- `pit_area_m2`: `262`
- `case_meta`: `{'validated_with_elena': False, 'confidence': 'medium'}`
- `assumptions`: `{'manual_excavation_override': True, 'sand_override': True, 'geotextile_override': True}`
- `excavator_shifts_calc_method`: `legacy_manual_shifts`
- `excavator_productivity_m3_per_shift`: `80.0`
- `manual_excavation_calc_method`: `legacy_manual_override`
- `manual_refinement_depth_m`: `0.08`
- `trench_volume_m3`: `11.43`
- `trench_width_m`: `0.4`
- `manual_trench_depth_k1_m`: `0.4`
- `manual_trench_depth_k2_m`: `0.6`
- `manual_trench_depth_water_m`: `1.6`
- `manual_trench_depth_eo_m`: `0.65`
- `manual_trench_depth_other_m`: `0.5`
- `sand_base_volume_m3`: `165.7`
- `sand_compaction_coeff`: `1.3`
- `sand_truck_step_m3`: `10`
- `geotextile_area_m2`: `257.4`
- `geotextile_overlap_coeff`: `1.0`
- `geotextile_roll_area_m2`: `100`
- `communications_length_calc_method`: `legacy_direct_length`
- `communications_length_m`: `0`
- `axis_marking_shifts`: `1`
- `excavator_shifts`: `3`
- `geotextile_laying_area_m2`: `0`
- `geotextile_laying_overlap_coeff`: `1.0`
- `manual_excavation_quantity_for_estimate_m3`: `32.393`
- `consumables_calc_method`: `legacy_fixed_amount`
- `consumables_rate`: `0.0`
- `consumables_amount`: `16292.16`
- `enabled_lines`: `['axis_marking', 'excavator_jcb', 'manual_excavation', 'geotextile_material', 'sand_filling', 'sand_material', 'sand_manual_moving', 'consumables']`
- `quantity_overrides`: `{'sand_order_volume_m3': 190, 'geotextile_material_quantity_m2': 300}`
- `line_name_overrides`: `{'manual_excavation': 'Доработка грунта вручную', 'sand_filling': 'Отсыпка дна под плиту и под ростверк песком с трамбованием'}`
- `internal_prices`: `{'axis_marking_work_unit_price': 15000, 'excavator_material_unit_price': 22000, 'excavator_work_unit_price': 0, 'manual_excavation_work_unit_price': 1200, 'geotextile_laying_work_unit_price': 0, 'geotextile_material_unit_price': 109, 'geotextile_material_work_unit_price': 35, 'sand_filling_work_unit_price': 1000, 'sand_material_unit_price': 1000, 'sand_manual_moving_work_unit_price': 0, 'communications_work_unit_price': 0, 'communications_material_unit_price': 0}`

## Формулы
- Смены экскаватора legacy: используется готовое `excavator_shifts`.
- Смены экскаватора standard: `machine_excavation_volume = pit_area_m2 * pit_excavation_depth_m`; `excavator_shifts = ceil(machine_excavation_volume / excavator_productivity_m3_per_shift)`.
- `pit_excavation_depth_m` — глубина механизированной выемки; `manual_refinement_depth_m` — ручная доработка дна котлована.
- Ручная разработка legacy: строка может брать `manual_excavation_quantity_for_estimate_m3`, если включён `legacy_manual_override`.
- Ручная разработка standard: `manual_excavation_total = pit_area_m2 * 0.08 + trench_volume_total_m3`.
- Доработка котлована: `manual_pit_volume = pit_area_m2 * manual_refinement_depth_m`.
- Объём траншей legacy: `trench_volume = trench_length_m * trench_depth_m * trench_width_m` или готовый `trench_volume_m3`.
- Объём траншей standard: если есть готовый `trench_volume_m3` из спецификации, берём его; иначе считаем сумму `length_m * depth_m * trench_width_m` по `trench_routes`.
- Коммуникации legacy: используется готовое `communications_length_m`.
- Коммуникации standard: `communications_length_m = sum(pipe_length_m * quantity)` или сумма готовых `total_length_m` по трубам из спецификации.
- Песок под котлован: `compacted_sand_base = sand_base_volume_m3 * sand_compaction_coeff`
- Песок в траншеи: `compacted_sand_trenches = trench_volume_total_m3 * sand_compaction_coeff`
- Общий песок: `sand_total = compacted_sand_base + compacted_sand_trenches`
- Песок к заказу: `sand_order_volume = ceil(sand_total / sand_truck_step_m3) * sand_truck_step_m3`
- Геотекстиль: `geotextile_with_overlap = geotextile_area_m2 * geotextile_overlap_coeff`
- Рулоны геотекстиля: `geotextile_rolls = ceil(geotextile_with_overlap / geotextile_roll_area_m2)`
- Строка серой сметы: `material_total = quantity * material_unit_price`, `work_total = quantity * work_unit_price`
- Итог раздела: `internal_section_total = internal_materials_total + internal_works_total`

## Объёмы
| Показатель | Значение |
| --- | ---: |
| `excavator_shifts_calc_method` | `legacy_manual_shifts` |
| `excavator_shifts_source` | `legacy_manual_shifts` |
| `pit_excavation_depth_m` | `None` |
| `machine_excavation_volume_m3` | `None` |
| `excavator_productivity_m3_per_shift` | `80.0` |
| `excavator_shifts` | `3.0` |
| `manual_excavation_calc_method` | `legacy_manual_override` |
| `manual_pit_volume_m3` | `20.96` |
| `manual_refinement_depth_m` | `0.08` |
| `trench_width_m` | `0.4` |
| `trench_volume_source` | `legacy_direct_volume` |
| `trench_volume_total_m3` | `11.43` |
| `trench_volume_m3` | `11.43` |
| `trench_manual_portion_m3` | `11.43` |
| `manual_trench_depth_k1_m` | `0.4` |
| `manual_trench_depth_k2_m` | `0.6` |
| `manual_trench_depth_water_m` | `1.6` |
| `manual_trench_depth_eo_m` | `0.65` |
| `manual_trench_depth_other_m` | `0.5` |
| `manual_excavation_total_m3` | `32.39` |
| `sand_source` | `legacy` |
| `sand_items_raw_total_m3` | `0.0` |
| `compacted_sand_base_m3` | `215.41` |
| `compacted_sand_trenches_m3` | `14.859` |
| `sand_total_m3` | `230.269` |
| `sand_order_volume_m3` | `240` |
| `geotextile_with_overlap_m2` | `257.4` |
| `geotextile_rolls` | `3` |
| `communications_length_calc_method` | `legacy_direct_length` |
| `communications_length_m` | `0.0` |




## Строки серой внутренней сметы
| code | name | quantity | unit | material_unit_price | material_total | work_unit_price | work_total | line_total |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `axis_marking` | Вынос осей фундамента, котлована на участок | `1.0` | `смена` | `0.0` | `0` | `15000` | `15000` | `15000` |
| `excavator_jcb` | Механизированная разработка грунта, Экскаватор JCB | `3.0` | `смена` | `22000` | `66000` | `0` | `0` | `66000` |
| `manual_excavation` | Доработка грунта вручную | `32.393` | `м3` | `0.0` | `0` | `1200` | `38872` | `38872` |
| `geotextile_material` | Геотекстиль Дорнит 300 г.м2 (100м2) | `300.0` | `м2` | `109` | `32700` | `35` | `10500` | `43200` |
| `sand_filling` | Отсыпка дна под плиту и под ростверк песком с трамбованием | `190.0` | `м3` | `0.0` | `0` | `1000` | `190000` | `190000` |
| `sand_material` | Песок строительный | `190.0` | `м3` | `1000` | `190000` | `0.0` | `0` | `190000` |
| `sand_manual_moving` | Перемещение песка вручную | `190.0` | `м3` | `0.0` | `0` | `0` | `0` | `0` |
| `consumables` | Расходные материалы, амортизация инструмента | `1.0` | `комплект` | `16292.16` | `16292` | `0.0` | `0` | `16292` |

## Итоги серой внутренней сметы
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total` | `304992` |
| `internal_works_total` | `254372` |
| `internal_section_total` | `559364` |

## Проверка с расчётом Елены
| Показатель | Ожидание | Получено | Разница | Статус |
| --- | ---: | ---: | ---: | --- |
| `volumes.manual_pit_volume_m3` | `20.96` | `20.96` | `0.0` | `ok` |
| `volumes.trench_volume_m3` | `11.43` | `11.43` | `0.0` | `ok` |
| `volumes.manual_excavation_total_m3` | `32.39` | `32.39` | `0.0` | `ok` |
| `volumes.compacted_sand_base_m3` | `215.41` | `215.41` | `0.0` | `ok` |
| `volumes.compacted_sand_trenches_m3` | `14.859` | `14.859` | `0.0` | `ok` |
| `volumes.sand_total_m3` | `230.269` | `230.269` | `0.0` | `ok` |
| `volumes.sand_order_volume_m3` | `240` | `240` | `0` | `ok` |
| `volumes.geotextile_with_overlap_m2` | `257.4` | `257.4` | `0.0` | `ok` |
| `volumes.geotextile_rolls` | `3` | `3` | `0` | `ok` |
| `estimate_lines.axis_marking.name` | `Вынос осей фундамента, котлована на участок` | `Вынос осей фундамента, котлована на участок` | `` | `ok` |
| `estimate_lines.axis_marking.unit` | `смена` | `смена` | `` | `ok` |
| `estimate_lines.axis_marking.quantity` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.axis_marking.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.axis_marking.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.axis_marking.work_unit_price` | `15000` | `15000` | `0` | `ok` |
| `estimate_lines.axis_marking.work_total` | `15000` | `15000` | `0` | `ok` |
| `estimate_lines.axis_marking.line_total` | `15000` | `15000` | `0` | `ok` |
| `estimate_lines.excavator_jcb.name` | `Механизированная разработка грунта, Экскаватор JCB` | `Механизированная разработка грунта, Экскаватор JCB` | `` | `ok` |
| `estimate_lines.excavator_jcb.unit` | `смена` | `смена` | `` | `ok` |
| `estimate_lines.excavator_jcb.quantity` | `3` | `3.0` | `0.0` | `ok` |
| `estimate_lines.excavator_jcb.material_unit_price` | `22000` | `22000` | `0` | `ok` |
| `estimate_lines.excavator_jcb.material_total` | `66000` | `66000` | `0` | `ok` |
| `estimate_lines.excavator_jcb.work_unit_price` | `0` | `0` | `0` | `ok` |
| `estimate_lines.excavator_jcb.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.excavator_jcb.line_total` | `66000` | `66000` | `0` | `ok` |
| `estimate_lines.manual_excavation.name` | `Доработка грунта вручную` | `Доработка грунта вручную` | `` | `ok` |
| `estimate_lines.manual_excavation.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.manual_excavation.quantity` | `32.393` | `32.393` | `0.0` | `ok` |
| `estimate_lines.manual_excavation.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.manual_excavation.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.manual_excavation.work_unit_price` | `1200` | `1200` | `0` | `ok` |
| `estimate_lines.manual_excavation.work_total` | `38872` | `38872` | `0` | `ok` |
| `estimate_lines.manual_excavation.line_total` | `38872` | `38872` | `0` | `ok` |
| `estimate_lines.geotextile_material.name` | `Геотекстиль Дорнит 300 г.м2 (100м2)` | `Геотекстиль Дорнит 300 г.м2 (100м2)` | `` | `ok` |
| `estimate_lines.geotextile_material.unit` | `м2` | `м2` | `` | `ok` |
| `estimate_lines.geotextile_material.quantity` | `300` | `300.0` | `0.0` | `ok` |
| `estimate_lines.geotextile_material.material_unit_price` | `109` | `109` | `0` | `ok` |
| `estimate_lines.geotextile_material.material_total` | `32700` | `32700` | `0` | `ok` |
| `estimate_lines.geotextile_material.work_unit_price` | `35` | `35` | `0` | `ok` |
| `estimate_lines.geotextile_material.work_total` | `10500` | `10500` | `0` | `ok` |
| `estimate_lines.geotextile_material.line_total` | `43200` | `43200` | `0` | `ok` |
| `estimate_lines.sand_filling.name` | `Отсыпка дна под плиту и под ростверк песком с трамбованием` | `Отсыпка дна под плиту и под ростверк песком с трамбованием` | `` | `ok` |
| `estimate_lines.sand_filling.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.sand_filling.quantity` | `190` | `190.0` | `0.0` | `ok` |
| `estimate_lines.sand_filling.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.sand_filling.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.sand_filling.work_unit_price` | `1000` | `1000` | `0` | `ok` |
| `estimate_lines.sand_filling.work_total` | `190000` | `190000` | `0` | `ok` |
| `estimate_lines.sand_filling.line_total` | `190000` | `190000` | `0` | `ok` |
| `estimate_lines.sand_material.name` | `Песок строительный` | `Песок строительный` | `` | `ok` |
| `estimate_lines.sand_material.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.sand_material.quantity` | `190` | `190.0` | `0.0` | `ok` |
| `estimate_lines.sand_material.material_unit_price` | `1000` | `1000` | `0` | `ok` |
| `estimate_lines.sand_material.material_total` | `190000` | `190000` | `0` | `ok` |
| `estimate_lines.sand_material.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.sand_material.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.sand_material.line_total` | `190000` | `190000` | `0` | `ok` |
| `estimate_lines.sand_manual_moving.name` | `Перемещение песка вручную` | `Перемещение песка вручную` | `` | `ok` |
| `estimate_lines.sand_manual_moving.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.sand_manual_moving.quantity` | `190` | `190.0` | `0.0` | `ok` |
| `estimate_lines.sand_manual_moving.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.sand_manual_moving.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.sand_manual_moving.work_unit_price` | `0` | `0` | `0` | `ok` |
| `estimate_lines.sand_manual_moving.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.sand_manual_moving.line_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.consumables.name` | `Расходные материалы, амортизация инструмента` | `Расходные материалы, амортизация инструмента` | `` | `ok` |
| `estimate_lines.consumables.unit` | `комплект` | `комплект` | `` | `ok` |
| `estimate_lines.consumables.quantity` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.consumables.material_unit_price` | `16292.16` | `16292.16` | `0.0` | `ok` |
| `estimate_lines.consumables.material_total` | `16292` | `16292` | `0` | `ok` |
| `estimate_lines.consumables.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.consumables.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.consumables.line_total` | `16292` | `16292` | `0` | `ok` |
| `internal_totals.internal_materials_total` | `304992` | `304992` | `0` | `ok` |
| `internal_totals.internal_works_total` | `254372` | `254372` | `0` | `ok` |
| `internal_totals.internal_section_total` | `559364` | `559364` | `0` | `ok` |
