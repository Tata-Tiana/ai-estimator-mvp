# Рефактор ЭППС 100 мм в гидроизоляции фундаментной плиты

Дата: 2026-06-09

## Контекст

После уточнения Елены участки без утепления больше не нужны для production-расчёта раздела "Гидроизоляция фундаментной плиты".

## Что было

В старом кейсе `non_insulated_edge_lengths_m` использовался для геометрической проверки:

```text
insulated_edge_length_m = slab_formwork_perimeter_m - sum(non_insulated_edge_lengths_m)
eps100_wall_geometry_check_area_m2 = insulated_edge_length_m * slab_edge_height_m
```

При этом сметная строка работы по ЭППС уже брала площадь из спецификации через объём:

```text
eps100_wall_insulation_area_m2 = eps100_wall_volume_m3 / eps100_wall_thickness_m
```

## Что стало production-стандартом

Основной источник для ЭППС 100 мм торец:

```text
eps100_wall_volume_m3
```

Площадь работ:

```text
eps100_wall_insulation_area_m2 = eps100_wall_volume_m3 / 0.1
```

Где `0.1 м` — толщина ЭППС 100 мм.

`non_insulated_edge_lengths_m` больше не требуется в production.

## Геометрическая проверка

Геометрическая проверка стала optional.

Она включается только если есть все данные:

- `slab_formwork_perimeter_m`;
- `slab_edge_height_m`;
- непустой `non_insulated_edge_lengths_m`.

Если данных нет:

```text
eps100_wall_geometry_check_enabled = false
```

Калькулятор не падает, а продолжает считать ЭППС по спецификации.

## Статус параметров

Production:

- `eps100_wall_volume_m3` — объём ЭППС 100 мм из спецификации;
- `eps100_wall_thickness_m = 0.1`;
- `eps100_wall_insulation_area_m2` — рассчитывается автоматически.

Legacy/debug:

- `non_insulated_edge_lengths_m`;
- `slab_formwork_perimeter_m`;
- `slab_edge_height_m`.

## Проверка

Production-кейс:

```text
experiments/waterproofing_calculator/cases/test_waterproofing_spec_area/
```

Проверяет:

```text
eps100_wall_volume_m3 = 1.75
eps100_wall_thickness_m = 0.1
eps100_wall_insulation_area_m2 = 17.5
eps100_wall_geometry_check_enabled = false
```

Старый legacy-кейс продолжает использовать `non_insulated_edge_lengths_m` для проверки:

```text
(81 - 8.2 - 2 - 5.3) * 0.3 = 19.65 м2
```

Старый `expected.json` не менялся.

## TODO

- Обновить `section_schema.py`.
- Убрать `non_insulated_edge_lengths_m` из `reviewed_parameters.xlsx` для production.
- Научить parser брать `eps100_wall_volume_m3` из спецификации.
- Показывать Елене `eps100_wall_volume_m3` и рассчитанную площадь работ по ЭППС как контроль.
