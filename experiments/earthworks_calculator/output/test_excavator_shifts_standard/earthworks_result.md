# Расчёт земляных работ: test_excavator_shifts_standard

Проект: `test_excavator_shifts_standard`

## Входные параметры
- `project_name`: `test_excavator_shifts_standard`
- `pit_area_m2`: `330`
- `case_meta`: `{'validated_with_elena': False, 'confidence': 'formula_test'}`
- `assumptions`: `{}`
- `excavator_shifts_calc_method`: `standard_volume_productivity`
- `pit_excavation_depth_m`: `0.6`
- `excavator_productivity_m3_per_shift`: `80`
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
- `communications_length_calc_method`: `legacy_direct_length`
- `communications_length_m`: `0`
- `axis_marking_shifts`: `0`
- `excavator_shifts`: `0`
- `geotextile_laying_area_m2`: `0`
- `consumables_amount`: `0`
- `enabled_lines`: `['excavator_jcb']`
- `quantity_overrides`: `{}`
- `line_name_overrides`: `{}`
- `internal_prices`: `{'excavator_material_unit_price': 26000, 'excavator_work_unit_price': 3500}`

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
| `excavator_shifts_calc_method` | `standard_volume_productivity` |
| `excavator_shifts_source` | `standard_volume_productivity` |
| `pit_excavation_depth_m` | `0.6` |
| `machine_excavation_volume_m3` | `198.0` |
| `excavator_productivity_m3_per_shift` | `80` |
| `excavator_shifts` | `3.0` |
| `manual_excavation_calc_method` | `legacy_manual_override` |
| `manual_pit_volume_m3` | `26.4` |
| `manual_refinement_depth_m` | `0.08` |
| `trench_width_m` | `0.4` |
| `trench_volume_source` | `legacy_direct_volume` |
| `trench_volume_total_m3` | `0.0` |
| `trench_volume_m3` | `0.0` |
| `manual_excavation_total_m3` | `26.4` |
| `sand_source` | `legacy` |
| `sand_items_raw_total_m3` | `0.0` |
| `compacted_sand_base_m3` | `0.0` |
| `compacted_sand_trenches_m3` | `0.0` |
| `sand_total_m3` | `0.0` |
| `sand_order_volume_m3` | `0` |
| `geotextile_with_overlap_m2` | `0.0` |
| `geotextile_rolls` | `0` |
| `communications_length_calc_method` | `legacy_direct_length` |
| `communications_length_m` | `0.0` |




## Строки серой внутренней сметы
| code | name | quantity | unit | material_unit_price | material_total | work_unit_price | work_total | line_total |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `excavator_jcb` | Механизированная разработка грунта, Экскаватор JCB | `3.0` | `смена` | `26000` | `78000` | `3500` | `10500` | `88500` |

## Итоги серой внутренней сметы
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total` | `78000` |
| `internal_works_total` | `10500` |
| `internal_section_total` | `88500` |

## Проверка с расчётом Елены
| Показатель | Ожидание | Получено | Разница | Статус |
| --- | ---: | ---: | ---: | --- |
| `volumes.excavator_shifts_calc_method` | `standard_volume_productivity` | `standard_volume_productivity` | `` | `ok` |
| `volumes.excavator_shifts_source` | `standard_volume_productivity` | `standard_volume_productivity` | `` | `ok` |
| `volumes.pit_excavation_depth_m` | `0.6` | `0.6` | `0.0` | `ok` |
| `volumes.machine_excavation_volume_m3` | `198` | `198.0` | `0.0` | `ok` |
| `volumes.excavator_productivity_m3_per_shift` | `80` | `80` | `0` | `ok` |
| `volumes.excavator_shifts` | `3` | `3.0` | `0.0` | `ok` |
| `estimate_lines.excavator_jcb.name` | `Механизированная разработка грунта, Экскаватор JCB` | `Механизированная разработка грунта, Экскаватор JCB` | `` | `ok` |
| `estimate_lines.excavator_jcb.unit` | `смена` | `смена` | `` | `ok` |
| `estimate_lines.excavator_jcb.quantity` | `3` | `3.0` | `0.0` | `ok` |
| `estimate_lines.excavator_jcb.material_unit_price` | `26000` | `26000` | `0` | `ok` |
| `estimate_lines.excavator_jcb.material_total` | `78000` | `78000` | `0` | `ok` |
| `estimate_lines.excavator_jcb.work_unit_price` | `3500` | `3500` | `0` | `ok` |
| `estimate_lines.excavator_jcb.work_total` | `10500` | `10500` | `0` | `ok` |
| `estimate_lines.excavator_jcb.line_total` | `88500` | `88500` | `0` | `ok` |
| `internal_totals.internal_materials_total` | `78000` | `78000` | `0` | `ok` |
| `internal_totals.internal_works_total` | `10500` | `10500` | `0` | `ok` |
| `internal_totals.internal_section_total` | `88500` | `88500` | `0` | `ok` |
