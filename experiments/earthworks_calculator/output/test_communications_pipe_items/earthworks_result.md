# Расчёт земляных работ: test_communications_pipe_items

Проект: `test_communications_pipe_items`

## Входные параметры
- `project_name`: `test_communications_pipe_items`
- `pit_area_m2`: `0`
- `case_meta`: `{'validated_with_elena': False, 'confidence': 'formula_test'}`
- `assumptions`: `{}`
- `excavator_shifts_calc_method`: `legacy_manual_shifts`
- `excavator_productivity_m3_per_shift`: `80.0`
- `manual_excavation_calc_method`: `legacy_manual_override`
- `manual_refinement_depth_m`: `0.08`
- `trench_volume_m3`: `0`
- `trench_width_m`: `0.4`
- `sand_base_volume_m3`: `0`
- `sand_compaction_coeff`: `1.3`
- `sand_truck_step_m3`: `20.0`
- `geotextile_area_m2`: `0`
- `geotextile_overlap_coeff`: `1.1`
- `geotextile_roll_area_m2`: `100.0`
- `communications_length_calc_method`: `pipe_items`
- `communications_length_m`: `0.0`
- `communications_pipe_items`: `[{'code': 'pipe_1m', 'name': 'Труба 1 м', 'pipe_length_m': 1, 'quantity': 12, 'include_in_communications': True}, {'code': 'pipe_2m', 'name': 'Труба 2 м', 'pipe_length_m': 2, 'quantity': 5, 'include_in_communications': True}, {'code': 'pipe_3m', 'name': 'Труба 3 м', 'pipe_length_m': 3, 'quantity': 4, 'include_in_communications': True}, {'code': 'corrugated_pipe', 'name': 'Труба гофрированная', 'total_length_m': 25, 'include_in_communications': True}]`
- `axis_marking_shifts`: `0`
- `excavator_shifts`: `0`
- `geotextile_laying_area_m2`: `0`
- `geotextile_laying_overlap_coeff`: `1.0`
- `consumables_calc_method`: `legacy_fixed_amount`
- `consumables_rate`: `0.0`
- `consumables_amount`: `0`
- `enabled_lines`: `['communications_work', 'communications_material']`
- `quantity_overrides`: `{}`
- `line_name_overrides`: `{}`
- `internal_prices`: `{'communications_work_unit_price': 350, 'communications_material_unit_price': 650}`

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
| `excavator_shifts` | `0.0` |
| `manual_excavation_calc_method` | `legacy_manual_override` |
| `manual_pit_volume_m3` | `0.0` |
| `manual_refinement_depth_m` | `0.08` |
| `trench_width_m` | `0.4` |
| `trench_volume_source` | `legacy_direct_volume` |
| `trench_volume_total_m3` | `0.0` |
| `trench_volume_m3` | `0.0` |
| `manual_excavation_total_m3` | `0.0` |
| `sand_source` | `legacy` |
| `sand_items_raw_total_m3` | `0.0` |
| `compacted_sand_base_m3` | `0.0` |
| `compacted_sand_trenches_m3` | `0.0` |
| `sand_total_m3` | `0.0` |
| `sand_order_volume_m3` | `0` |
| `geotextile_with_overlap_m2` | `0.0` |
| `geotextile_rolls` | `0` |
| `communications_length_calc_method` | `pipe_items` |
| `communications_length_m` | `59.0` |



## Трубы технологических вводов

| code | name | pipe_length_m | quantity | total_length_m | include_in_communications |
| --- | --- | ---: | ---: | ---: | --- |
| `pipe_1m` | Труба 1 м | `1.0` | `12.0` | `12.0` | `True` |
| `pipe_2m` | Труба 2 м | `2.0` | `5.0` | `10.0` | `True` |
| `pipe_3m` | Труба 3 м | `3.0` | `4.0` | `12.0` | `True` |
| `corrugated_pipe` | Труба гофрированная | `None` | `None` | `25.0` | `True` |

## Строки серой внутренней сметы
| code | name | quantity | unit | material_unit_price | material_total | work_unit_price | work_total | line_total |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `communications_work` | Закладка технологических входов коммуникаций до границы дома | `59.0` | `мп` | `0.0` | `0` | `350` | `20650` | `20650` |
| `communications_material` | Материалы для устройства входов коммуникаций | `59.0` | `мп` | `650` | `38350` | `0.0` | `0` | `38350` |

## Итоги серой внутренней сметы
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total` | `38350` |
| `internal_works_total` | `20650` |
| `internal_section_total` | `59000` |

## Проверка с расчётом Елены
| Показатель | Ожидание | Получено | Разница | Статус |
| --- | ---: | ---: | ---: | --- |
| `volumes.communications_length_calc_method` | `pipe_items` | `pipe_items` | `` | `ok` |
| `volumes.communications_length_m` | `59` | `59.0` | `0.0` | `ok` |
| `estimate_lines.communications_work.name` | `Закладка технологических входов коммуникаций до границы дома` | `Закладка технологических входов коммуникаций до границы дома` | `` | `ok` |
| `estimate_lines.communications_work.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.communications_work.quantity` | `59` | `59.0` | `0.0` | `ok` |
| `estimate_lines.communications_work.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.communications_work.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.communications_work.work_unit_price` | `350` | `350` | `0` | `ok` |
| `estimate_lines.communications_work.work_total` | `20650` | `20650` | `0` | `ok` |
| `estimate_lines.communications_work.line_total` | `20650` | `20650` | `0` | `ok` |
| `estimate_lines.communications_material.name` | `Материалы для устройства входов коммуникаций` | `Материалы для устройства входов коммуникаций` | `` | `ok` |
| `estimate_lines.communications_material.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.communications_material.quantity` | `59` | `59.0` | `0.0` | `ok` |
| `estimate_lines.communications_material.material_unit_price` | `650` | `650` | `0` | `ok` |
| `estimate_lines.communications_material.material_total` | `38350` | `38350` | `0` | `ok` |
| `estimate_lines.communications_material.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.communications_material.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.communications_material.line_total` | `38350` | `38350` | `0` | `ok` |
| `internal_totals.internal_materials_total` | `38350` | `38350` | `0` | `ok` |
| `internal_totals.internal_works_total` | `20650` | `20650` | `0` | `ok` |
| `internal_totals.internal_section_total` | `59000` | `59000` | `0` | `ok` |
