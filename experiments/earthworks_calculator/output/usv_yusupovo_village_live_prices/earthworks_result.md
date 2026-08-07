# Расчёт земляных работ: usv_yusupovo_village_live_prices

Проект: `usv_yusupovo_village_live_prices`

## Входные параметры
- `project_name`: `usv_yusupovo_village_live_prices`
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
| `axis_marking` | Вынос осей фундамента, котлована на участок | `1.0` | `смена` | `0.0` | `0` | `15000.0` | `15000` | `15000` |
| `excavator_jcb` | Механизированная разработка грунта, Экскаватор JCB | `3.0` | `смена` | `22000.0` | `66000` | `3500` | `10500` | `66000` |
| `manual_excavation` | Разработка грунта вручную | `44.695` | `м3` | `0.0` | `0` | `1200.0` | `53634` | `53634` |
| `geotextile_laying` | Укладка геотекстиля | `340.0` | `м2` | `0.0` | `0` | `35.0` | `11900` | `11900` |
| `geotextile_material` | Геотекстиль Дорнит 300 г.м2 (100м2) | `400.0` | `м2` | `109.0` | `43600` | `0.0` | `0` | `43600` |
| `sand_filling` | Отсыпка дна котлована, засыпка под плитой песком с трамбованием | `160.0` | `м3` | `0.0` | `0` | `1200.0` | `192000` | `192000` |
| `sand_material` | Песок строительный | `160.0` | `м3` | `1000.0` | `160000` | `0.0` | `0` | `160000` |
| `sand_manual_moving` | Перемещение песка вручную | `160.0` | `м3` | `0.0` | `0` | `0` | `0` | `0` |
| `communications_work` | Закладка технологических входов коммуникаций до границы дома | `115.0` | `мп` | `0.0` | `0` | `350.0` | `40250` | `40250` |
| `communications_material` | Материалы для устройства входов коммуникаций | `115.0` | `мп` | `650.0` | `74750` | `0.0` | `0` | `74750` |
| `consumables` | Расходные материалы, амортизация инструмента | `1.0` | `комплект` | `23447.18` | `23447` | `0.0` | `0` | `23447` |

## Итоги серой внутренней сметы
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total` | `367797` |
| `internal_works_total` | `323284` |
| `internal_section_total` | `691081` |
| `internal_materials_total_raw` | `367797` |
| `internal_works_total_raw` | `323284` |
| `internal_section_total_raw` | `691081` |

## Источники цен

| Строка сметы | price_code | старая цена | использованная цена | источник | предупреждение |
| --- | --- | ---: | ---: | --- | --- |
| Вынос осей фундамента, котлована на участок | `axis_marking_shift` | `20000` | `15000` | `price_registry` |  |
| Механизированная разработка грунта, Экскаватор JCB | `excavator_jcb_shift` | `26000` | `22000` | `price_registry` |  |
| Разработка грунта вручную | `manual_excavation_m3` | `1400` | `1200` | `price_registry` |  |
| Укладка геотекстиля | `geotextile_laying_m2` | `35` | `35` | `price_registry` |  |
| Геотекстиль Дорнит 300 г.м2 (100м2) | `geotextile_dornit_300_m2` | `109` | `109` | `price_registry` |  |
| Отсыпка дна котлована, засыпка под плитой песком с трамбованием | `sand_filling_work_m3` | `1200` | `1200` | `price_registry` |  |
| Песок строительный | `sand_m3` | `1550` | `1000` | `price_registry` |  |
| Перемещение песка вручную | `sand_manual_moving_m3` | `None` | `None` | `fallback_input` | price_code not found in price_registry and fallback input price is missing |
| Закладка технологических входов коммуникаций до границы дома | `communications_installation_m` | `350` | `350` | `price_registry` |  |
| Материалы для устройства входов коммуникаций | `communications_material_m` | `650` | `650` | `price_registry` |  |
| Расходные материалы, амортизация инструмента | `` | `23447.18` | `23447.18` | `locked_case_prices` |  |

## Pricing summary
| Показатель | Значение |
| --- | ---: |
| `mode` | `price_registry_with_fallback` |
| `registry_path` | `/Users/tatanamedzidova/Desktop/ai_estimator/ai_estimator_mvp/output/price_registry_filled_v3.xlsx` |
| `prices_from_price_registry` | `9` |
| `prices_from_project_overrides` | `0` |
| `prices_from_fallback_input` | `1` |
| `warnings_count` | `1` |

## Проверка с расчётом Елены
Expected values are not provided for this case.
