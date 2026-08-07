# Расчёт земляных работ: usv_yusupovo_village

Проект: `usv_yusupovo_village`

## Входные параметры
- `project_name`: `usv_yusupovo_village`
- `pit_area_m2`: `330`
- `case_meta`: `{'validated_with_elena': True, 'confidence': 'high'}`
- `assumptions`: `{'manual_excavation_override': True, 'sand_override': False, 'geotextile_override': False}`
- `excavator_shifts_calc_method`: `legacy_manual_shifts`
- `excavator_productivity_m3_per_shift`: `80.0`
- `manual_excavation_calc_method`: `legacy_manual_override`
- `manual_refinement_depth_m`: `0.08`
- `trench_volume_m3`: `18.29`
- `trench_width_m`: `0.4`
- `sand_base_volume_m3`: `96.6`
- `sand_compaction_coeff`: `1.3`
- `sand_truck_step_m3`: `20`
- `geotextile_area_m2`: `330`
- `geotextile_overlap_coeff`: `1.1`
- `geotextile_roll_area_m2`: `100`
- `communications_length_calc_method`: `legacy_direct_length`
- `communications_length_m`: `115`
- `axis_marking_shifts`: `1`
- `excavator_shifts`: `3`
- `geotextile_laying_area_m2`: `340`
- `geotextile_laying_overlap_coeff`: `1.0`
- `manual_excavation_quantity_for_estimate_m3`: `44.695`
- `consumables_calc_method`: `legacy_fixed_amount`
- `consumables_rate`: `0.0`
- `consumables_amount`: `23447.18`
- `quantity_overrides`: `{}`
- `line_name_overrides`: `{}`
- `internal_prices`: `{'axis_marking_work_unit_price': 20000, 'excavator_material_unit_price': 26000, 'excavator_work_unit_price': 3500, 'manual_excavation_work_unit_price': 1400, 'geotextile_laying_work_unit_price': 35, 'geotextile_material_unit_price': 109, 'sand_filling_work_unit_price': 1200, 'sand_material_unit_price': 1550, 'sand_manual_moving_work_unit_price': 0, 'communications_work_unit_price': 350, 'communications_material_unit_price': 650}`

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
| `manual_pit_volume_m3` | `26.4` |
| `manual_refinement_depth_m` | `0.08` |
| `trench_width_m` | `0.4` |
| `trench_volume_source` | `legacy_direct_volume` |
| `trench_volume_total_m3` | `18.29` |
| `trench_volume_m3` | `18.29` |
| `manual_excavation_total_m3` | `44.69` |
| `sand_source` | `legacy` |
| `sand_items_raw_total_m3` | `0.0` |
| `compacted_sand_base_m3` | `125.58` |
| `compacted_sand_trenches_m3` | `23.777` |
| `sand_total_m3` | `149.357` |
| `sand_order_volume_m3` | `160` |
| `geotextile_with_overlap_m2` | `363.0` |
| `geotextile_rolls` | `4` |
| `communications_length_calc_method` | `legacy_direct_length` |
| `communications_length_m` | `115.0` |




## Строки серой внутренней сметы
| code | name | quantity | unit | material_unit_price | material_total | work_unit_price | work_total | line_total |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `axis_marking` | Вынос осей фундамента, котлована на участок | `1.0` | `смена` | `0.0` | `0` | `20000` | `20000` | `20000` |
| `excavator_jcb` | Механизированная разработка грунта, Экскаватор JCB | `3.0` | `смена` | `26000` | `78000` | `3500` | `10500` | `88500` |
| `manual_excavation` | Разработка грунта вручную | `44.695` | `м3` | `0.0` | `0` | `1400` | `62573` | `62573` |
| `geotextile_laying` | Укладка геотекстиля | `340.0` | `м2` | `0.0` | `0` | `35` | `11900` | `11900` |
| `geotextile_material` | Геотекстиль Дорнит 300 г.м2 (100м2) | `400.0` | `м2` | `109` | `43600` | `0.0` | `0` | `43600` |
| `sand_filling` | Отсыпка дна котлована, засыпка под плитой песком с трамбованием | `160.0` | `м3` | `0.0` | `0` | `1200` | `192000` | `192000` |
| `sand_material` | Песок строительный | `160.0` | `м3` | `1550` | `248000` | `0.0` | `0` | `248000` |
| `sand_manual_moving` | Перемещение песка вручную | `160.0` | `м3` | `0.0` | `0` | `0` | `0` | `0` |
| `communications_work` | Закладка технологических входов коммуникаций до границы дома | `115.0` | `мп` | `0.0` | `0` | `350` | `40250` | `40250` |
| `communications_material` | Материалы для устройства входов коммуникаций | `115.0` | `мп` | `650` | `74750` | `0.0` | `0` | `74750` |
| `consumables` | Расходные материалы, амортизация инструмента | `1.0` | `комплект` | `23447.18` | `23447` | `0.0` | `0` | `23447` |

## Итоги серой внутренней сметы
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total` | `467797` |
| `internal_works_total` | `337223` |
| `internal_section_total` | `805020` |

## Проверка с расчётом Елены
| Показатель | Ожидание | Получено | Разница | Статус |
| --- | ---: | ---: | ---: | --- |
| `volumes.manual_pit_volume_m3` | `26.4` | `26.4` | `0.0` | `ok` |
| `volumes.trench_volume_m3` | `18.29` | `18.29` | `0.0` | `ok` |
| `volumes.manual_excavation_total_m3` | `44.69` | `44.69` | `0.0` | `ok` |
| `volumes.compacted_sand_base_m3` | `125.58` | `125.58` | `0.0` | `ok` |
| `volumes.compacted_sand_trenches_m3` | `23.777` | `23.777` | `0.0` | `ok` |
| `volumes.sand_total_m3` | `149.357` | `149.357` | `0.0` | `ok` |
| `volumes.sand_order_volume_m3` | `160` | `160` | `0` | `ok` |
| `volumes.geotextile_with_overlap_m2` | `363.0` | `363.0` | `0.0` | `ok` |
| `volumes.geotextile_rolls` | `4` | `4` | `0` | `ok` |
| `estimate_lines.axis_marking.name` | `Вынос осей фундамента, котлована на участок` | `Вынос осей фундамента, котлована на участок` | `` | `ok` |
| `estimate_lines.axis_marking.unit` | `смена` | `смена` | `` | `ok` |
| `estimate_lines.axis_marking.quantity` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.axis_marking.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.axis_marking.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.axis_marking.work_unit_price` | `20000` | `20000` | `0` | `ok` |
| `estimate_lines.axis_marking.work_total` | `20000` | `20000` | `0` | `ok` |
| `estimate_lines.axis_marking.line_total` | `20000` | `20000` | `0` | `ok` |
| `estimate_lines.excavator_jcb.name` | `Механизированная разработка грунта, Экскаватор JCB` | `Механизированная разработка грунта, Экскаватор JCB` | `` | `ok` |
| `estimate_lines.excavator_jcb.unit` | `смена` | `смена` | `` | `ok` |
| `estimate_lines.excavator_jcb.quantity` | `3` | `3.0` | `0.0` | `ok` |
| `estimate_lines.excavator_jcb.material_unit_price` | `26000` | `26000` | `0` | `ok` |
| `estimate_lines.excavator_jcb.material_total` | `78000` | `78000` | `0` | `ok` |
| `estimate_lines.excavator_jcb.work_unit_price` | `3500` | `3500` | `0` | `ok` |
| `estimate_lines.excavator_jcb.work_total` | `10500` | `10500` | `0` | `ok` |
| `estimate_lines.excavator_jcb.line_total` | `88500` | `88500` | `0` | `ok` |
| `estimate_lines.manual_excavation.name` | `Разработка грунта вручную` | `Разработка грунта вручную` | `` | `ok` |
| `estimate_lines.manual_excavation.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.manual_excavation.quantity` | `44.695` | `44.695` | `0.0` | `ok` |
| `estimate_lines.manual_excavation.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.manual_excavation.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.manual_excavation.work_unit_price` | `1400` | `1400` | `0` | `ok` |
| `estimate_lines.manual_excavation.work_total` | `62573` | `62573` | `0` | `ok` |
| `estimate_lines.manual_excavation.line_total` | `62573` | `62573` | `0` | `ok` |
| `estimate_lines.geotextile_laying.name` | `Укладка геотекстиля` | `Укладка геотекстиля` | `` | `ok` |
| `estimate_lines.geotextile_laying.unit` | `м2` | `м2` | `` | `ok` |
| `estimate_lines.geotextile_laying.quantity` | `340` | `340.0` | `0.0` | `ok` |
| `estimate_lines.geotextile_laying.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.geotextile_laying.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.geotextile_laying.work_unit_price` | `35` | `35` | `0` | `ok` |
| `estimate_lines.geotextile_laying.work_total` | `11900` | `11900` | `0` | `ok` |
| `estimate_lines.geotextile_laying.line_total` | `11900` | `11900` | `0` | `ok` |
| `estimate_lines.geotextile_material.name` | `Геотекстиль Дорнит 300 г.м2 (100м2)` | `Геотекстиль Дорнит 300 г.м2 (100м2)` | `` | `ok` |
| `estimate_lines.geotextile_material.unit` | `м2` | `м2` | `` | `ok` |
| `estimate_lines.geotextile_material.quantity` | `400` | `400.0` | `0.0` | `ok` |
| `estimate_lines.geotextile_material.material_unit_price` | `109` | `109` | `0` | `ok` |
| `estimate_lines.geotextile_material.material_total` | `43600` | `43600` | `0` | `ok` |
| `estimate_lines.geotextile_material.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.geotextile_material.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.geotextile_material.line_total` | `43600` | `43600` | `0` | `ok` |
| `estimate_lines.sand_filling.name` | `Отсыпка дна котлована, засыпка под плитой песком с трамбованием` | `Отсыпка дна котлована, засыпка под плитой песком с трамбованием` | `` | `ok` |
| `estimate_lines.sand_filling.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.sand_filling.quantity` | `160` | `160.0` | `0.0` | `ok` |
| `estimate_lines.sand_filling.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.sand_filling.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.sand_filling.work_unit_price` | `1200` | `1200` | `0` | `ok` |
| `estimate_lines.sand_filling.work_total` | `192000` | `192000` | `0` | `ok` |
| `estimate_lines.sand_filling.line_total` | `192000` | `192000` | `0` | `ok` |
| `estimate_lines.sand_material.name` | `Песок строительный` | `Песок строительный` | `` | `ok` |
| `estimate_lines.sand_material.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.sand_material.quantity` | `160` | `160.0` | `0.0` | `ok` |
| `estimate_lines.sand_material.material_unit_price` | `1550` | `1550` | `0` | `ok` |
| `estimate_lines.sand_material.material_total` | `248000` | `248000` | `0` | `ok` |
| `estimate_lines.sand_material.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.sand_material.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.sand_material.line_total` | `248000` | `248000` | `0` | `ok` |
| `estimate_lines.sand_manual_moving.name` | `Перемещение песка вручную` | `Перемещение песка вручную` | `` | `ok` |
| `estimate_lines.sand_manual_moving.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.sand_manual_moving.quantity` | `160` | `160.0` | `0.0` | `ok` |
| `estimate_lines.sand_manual_moving.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.sand_manual_moving.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.sand_manual_moving.work_unit_price` | `0` | `0` | `0` | `ok` |
| `estimate_lines.sand_manual_moving.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.sand_manual_moving.line_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.communications_work.name` | `Закладка технологических входов коммуникаций до границы дома` | `Закладка технологических входов коммуникаций до границы дома` | `` | `ok` |
| `estimate_lines.communications_work.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.communications_work.quantity` | `115` | `115.0` | `0.0` | `ok` |
| `estimate_lines.communications_work.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.communications_work.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.communications_work.work_unit_price` | `350` | `350` | `0` | `ok` |
| `estimate_lines.communications_work.work_total` | `40250` | `40250` | `0` | `ok` |
| `estimate_lines.communications_work.line_total` | `40250` | `40250` | `0` | `ok` |
| `estimate_lines.communications_material.name` | `Материалы для устройства входов коммуникаций` | `Материалы для устройства входов коммуникаций` | `` | `ok` |
| `estimate_lines.communications_material.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.communications_material.quantity` | `115` | `115.0` | `0.0` | `ok` |
| `estimate_lines.communications_material.material_unit_price` | `650` | `650` | `0` | `ok` |
| `estimate_lines.communications_material.material_total` | `74750` | `74750` | `0` | `ok` |
| `estimate_lines.communications_material.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.communications_material.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.communications_material.line_total` | `74750` | `74750` | `0` | `ok` |
| `estimate_lines.consumables.name` | `Расходные материалы, амортизация инструмента` | `Расходные материалы, амортизация инструмента` | `` | `ok` |
| `estimate_lines.consumables.unit` | `комплект` | `комплект` | `` | `ok` |
| `estimate_lines.consumables.quantity` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.consumables.material_unit_price` | `23447.18` | `23447.18` | `0.0` | `ok` |
| `estimate_lines.consumables.material_total` | `23447` | `23447` | `0` | `ok` |
| `estimate_lines.consumables.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.consumables.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.consumables.line_total` | `23447` | `23447` | `0` | `ok` |
| `internal_totals.internal_materials_total` | `467797` | `467797` | `0` | `ok` |
| `internal_totals.internal_works_total` | `337223` | `337223` | `0` | `ok` |
| `internal_totals.internal_section_total` | `805020` | `805020` | `0` | `ok` |
