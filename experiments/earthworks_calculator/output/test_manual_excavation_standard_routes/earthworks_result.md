# Расчёт земляных работ: test_manual_excavation_standard_routes

Проект: `test_manual_excavation_standard_routes`

## Входные параметры
- `project_name`: `test_manual_excavation_standard_routes`
- `pit_area_m2`: `330`
- `case_meta`: `{'validated_with_elena': False, 'confidence': 'formula_test'}`
- `assumptions`: `{}`
- `excavator_shifts_calc_method`: `legacy_manual_shifts`
- `excavator_productivity_m3_per_shift`: `80.0`
- `manual_excavation_calc_method`: `standard_routes`
- `manual_refinement_depth_m`: `0.08`
- `trench_width_m`: `0.4`
- `trench_routes`: `[{'route_code': 'K1', 'name': 'К1', 'length_m': 10, 'depth_m': 1.2}, {'route_code': 'K2', 'name': 'К2', 'length_m': 8, 'depth_m': 1.0}, {'route_code': 'VK', 'name': 'ВК', 'length_m': 12, 'depth_m': 1.4}, {'route_code': 'EO', 'name': 'ЭО', 'length_m': 5, 'depth_m': 0.7}]`
- `manual_trench_depth_k1_m`: `0.4`
- `manual_trench_depth_k2_m`: `0.6`
- `manual_trench_depth_water_m`: `1.6`
- `manual_trench_depth_eo_m`: `0.65`
- `manual_trench_depth_other_m`: `0.5`
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
- `geotextile_laying_overlap_coeff`: `1.0`
- `consumables_calc_method`: `legacy_fixed_amount`
- `consumables_rate`: `0.0`
- `consumables_amount`: `0`
- `enabled_lines`: `['manual_excavation']`
- `quantity_overrides`: `{}`
- `line_name_overrides`: `{}`
- `internal_prices`: `{'manual_excavation_work_unit_price': 1000}`

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
| `manual_excavation_calc_method` | `standard_routes` |
| `manual_pit_volume_m3` | `26.4` |
| `manual_refinement_depth_m` | `0.08` |
| `trench_width_m` | `0.4` |
| `trench_volume_source` | `routes_calculated` |
| `trench_volume_total_m3` | `16.12` |
| `trench_volume_m3` | `16.12` |
| `trench_manual_portion_m3` | `12.5` |
| `manual_trench_depth_k1_m` | `0.4` |
| `manual_trench_depth_k2_m` | `0.6` |
| `manual_trench_depth_water_m` | `1.6` |
| `manual_trench_depth_eo_m` | `0.65` |
| `manual_trench_depth_other_m` | `0.5` |
| `manual_excavation_total_m3` | `38.9` |
| `sand_source` | `legacy` |
| `sand_items_raw_total_m3` | `0.0` |
| `compacted_sand_base_m3` | `0.0` |
| `compacted_sand_trenches_m3` | `16.25` |
| `sand_total_m3` | `16.25` |
| `sand_order_volume_m3` | `20` |
| `geotextile_with_overlap_m2` | `0.0` |
| `geotextile_rolls` | `0` |
| `communications_length_calc_method` | `legacy_direct_length` |
| `communications_length_m` | `0.0` |

## Источник объёма траншей

Объём траншей рассчитан по трассам.

## Трассы траншей

| route_code | name | length_m | depth_m | width_m | volume_m3 |
| --- | --- | ---: | ---: | ---: | ---: |
| `K1` | К1 | `10.0` | `1.2` | `0.4` | `4.8` |
| `K2` | К2 | `8.0` | `1.0` | `0.4` | `3.2` |
| `VK` | ВК | `12.0` | `1.4` | `0.4` | `6.72` |
| `EO` | ЭО | `5.0` | `0.7` | `0.4` | `1.4` |


## Строки серой внутренней сметы
| code | name | quantity | unit | material_unit_price | material_total | work_unit_price | work_total | line_total |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `manual_excavation` | Разработка грунта вручную | `38.9` | `м3` | `0.0` | `0` | `1000` | `38900` | `38900` |

## Итоги серой внутренней сметы
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total` | `0` |
| `internal_works_total` | `38900` |
| `internal_section_total` | `38900` |

## Проверка с расчётом Елены
| Показатель | Ожидание | Получено | Разница | Статус |
| --- | ---: | ---: | ---: | --- |
| `volumes.manual_excavation_calc_method` | `standard_routes` | `standard_routes` | `` | `ok` |
| `volumes.manual_pit_volume_m3` | `26.4` | `26.4` | `0.0` | `ok` |
| `volumes.manual_refinement_depth_m` | `0.08` | `0.08` | `0.0` | `ok` |
| `volumes.trench_width_m` | `0.4` | `0.4` | `0.0` | `ok` |
| `volumes.trench_volume_total_m3` | `16.12` | `16.12` | `0.0` | `ok` |
| `volumes.trench_volume_m3` | `16.12` | `16.12` | `0.0` | `ok` |
| `volumes.manual_excavation_total_m3` | `38.9` | `38.9` | `0.0` | `ok` |
| `estimate_lines.manual_excavation.name` | `Разработка грунта вручную` | `Разработка грунта вручную` | `` | `ok` |
| `estimate_lines.manual_excavation.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.manual_excavation.quantity` | `38.9` | `38.9` | `0.0` | `ok` |
| `estimate_lines.manual_excavation.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.manual_excavation.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.manual_excavation.work_unit_price` | `1000` | `1000` | `0` | `ok` |
| `estimate_lines.manual_excavation.work_total` | `38900` | `38900` | `0` | `ok` |
| `estimate_lines.manual_excavation.line_total` | `38900` | `38900` | `0` | `ok` |
| `internal_totals.internal_materials_total` | `0` | `0` | `0` | `ok` |
| `internal_totals.internal_works_total` | `38900` | `38900` | `0` | `ok` |
| `internal_totals.internal_section_total` | `38900` | `38900` | `0` | `ok` |
