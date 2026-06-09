# Box calculator result

Проект: `test_metal_delivery_allocation`

## Доставка арматуры и металла

- Общий вес металла коробки: `19763.0` кг
- Грузоподъёмность машины: `10000.0` кг
- Количество машин: `2`
- Цена за машину: `22000.0`
- Итоговая стоимость доставки: `44000.0`

| Раздел | Вес металла, кг | Накопленный вес, кг | Машин доставки | Сумма доставки |
| --- | ---: | ---: | ---: | ---: |
| Фундаментная плита | 8263 | 8263 | 1 | 22000 |
| Несущие стены и перемычки | 2500 | 10763 | 1 | 22000 |
| Плита перекрытия 1-го этажа | 6000 | 16763 | 0 | 0 |
| Плита перекрытия 2-го этажа | 3000 | 19763 | 0 | 0 |

## Totals policy

- Allocation показан отдельно как recommended block.
- Section totals не пересчитываются.
- Доставка металла не добавляется поверх legacy totals.

## Warnings

- recommended_metal_delivery_allocation показан отдельно от итогов разделов; legacy section totals могут уже содержать доставку металла. Не добавлять allocation сверху, пока Excel exporter не поддерживает замену legacy-строки.

## Проверка

| Показатель | Ожидание | Получено | Разница | Статус |
| --- | ---: | ---: | ---: | --- |
| `recommended_metal_delivery_allocation.total_box_metal_weight_kg` | `19763` | `19763.0` | `0.0` | `ok` |
| `recommended_metal_delivery_allocation.total_trucks` | `2` | `2` | `0` | `ok` |
| `recommended_metal_delivery_allocation.total_delivery_cost` | `44000` | `44000.0` | `0.0` | `ok` |
| `recommended_metal_delivery_allocation.sections.0.section_code` | `foundation_slab` | `foundation_slab` | `` | `ok` |
| `recommended_metal_delivery_allocation.sections.0.allocated_trucks` | `1` | `1` | `0` | `ok` |
| `recommended_metal_delivery_allocation.sections.1.section_code` | `load_bearing_walls_lintels` | `load_bearing_walls_lintels` | `` | `ok` |
| `recommended_metal_delivery_allocation.sections.1.allocated_trucks` | `1` | `1` | `0` | `ok` |
| `recommended_metal_delivery_allocation.sections.2.section_code` | `floor_slab_1` | `floor_slab_1` | `` | `ok` |
| `recommended_metal_delivery_allocation.sections.2.allocated_trucks` | `0` | `0` | `0` | `ok` |
| `recommended_metal_delivery_allocation.sections.3.section_code` | `floor_slab_2` | `floor_slab_2` | `` | `ok` |
| `recommended_metal_delivery_allocation.sections.3.allocated_trucks` | `0` | `0` | `0` | `ok` |
| `totals_policy.metal_delivery_added_to_grand_total` | `False` | `False` | `0` | `ok` |
