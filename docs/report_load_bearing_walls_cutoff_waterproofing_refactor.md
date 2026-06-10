# Отчёт: отсечная гидроизоляция несущих стен готовой площадью

Дата: 2026-06-09

## Что было

В калькуляторе несущих стен отсечная гидроизоляция считалась по отдельным длинам стен 400 мм и 250 мм:

```text
cutoff_waterproofing_area_m2 =
sum(cutoff_waterproofing_wall_400_lengths_m) * wall_400_thickness_m
+ sum(cutoff_waterproofing_wall_250_lengths_m) * wall_250_thickness_m
```

Для старого ЮСВ-кейса это даёт `40.59 м2`.

## Что стало

Добавлен production-режим:

```text
cutoff_waterproofing_calc_method = "spec_area"
cutoff_waterproofing_area_m2 = cutoff_waterproofing_load_bearing_walls_area_m2
```

`cutoff_waterproofing_load_bearing_walls_area_m2` - готовая площадь отсечной гидроизоляции под несущие стены из спецификации проекта.

## Разделение несущих стен и перегородок

Площадь перегородок не включается в `load_bearing_walls_lintels_calculator`.

Для будущего раздела перегородок должен использоваться отдельный параметр:

```text
cutoff_waterproofing_partitions_area_m2
```

## Классификация параметров

| Параметр | Статус | Комментарий |
| --- | --- | --- |
| `cutoff_waterproofing_load_bearing_walls_area_m2` | AUTO_PROJECT | Готовая площадь из спецификации под несущие стены. |
| `cutoff_waterproofing_wall_400_lengths_m` | DEPRECATED / LEGACY_ONLY | Нужен только для старого ЮСВ-кейса. |
| `cutoff_waterproofing_wall_250_lengths_m` | DEPRECATED / LEGACY_ONLY | Нужен только для старого ЮСВ-кейса. |
| `wall_400_thickness_m` | DEPRECATED / LEGACY_ONLY | Для production-отсечки не нужен. |
| `wall_250_thickness_m` | DEPRECATED / LEGACY_ONLY | Для production-отсечки не нужен. |

## Новый тест

Создан кейс:

```text
experiments/load_bearing_walls_lintels_calculator/cases/test_cutoff_waterproofing_spec_area/
```

Проверка:

```text
cutoff_waterproofing_load_bearing_walls_area_m2 = 40.59
estimate_lines.cutoff_waterproofing_under_first_row_blocks.quantity = 40.59
```

## Legacy

Старый кейс `test_load_bearing_walls_lintels` оставлен в режиме:

```text
cutoff_waterproofing_calc_method = "legacy_lengths_by_wall_thickness"
```

Старый `expected.json` не изменяется.

## TODO

- Обновить `section_schema.py`.
- Добавить `cutoff_waterproofing_load_bearing_walls_area_m2` в `reviewed_parameters.xlsx` для раздела несущих стен.
- Добавить `cutoff_waterproofing_partitions_area_m2` в `reviewed_parameters.xlsx` для будущего раздела перегородок.
- Научить parser брать обе площади из спецификации.
- Убрать массивы `cutoff_waterproofing_wall_400_lengths_m` и `cutoff_waterproofing_wall_250_lengths_m` из формы Елены для production.
- Показывать Елене две готовые площади как контроль.
- Создать отдельный калькулятор перегородок и не включать перегородки в `load_bearing_walls_lintels_calculator`.
