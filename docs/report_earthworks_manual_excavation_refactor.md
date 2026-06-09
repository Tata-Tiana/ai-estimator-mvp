# Рефактор ручной разработки грунта в земляных работах

Дата: 2026-06-09

## Что было

В старой логике раздела "Земляные работы" строка "Разработка грунта вручную" могла брать ручное количество:

```text
manual_excavation_quantity_for_estimate_m3
```

Это было нужно, чтобы повторить старую смету ЮСВ с количеством `44.695 м3`.

Также калькулятор мог считать траншею готовым объёмом `trench_volume_m3` или общей формулой:

```text
trench_length_m * trench_depth_m * trench_width_m
```

## Что стало production-стандартом

Добавлен режим:

```text
manual_excavation_calc_method = standard_routes
```

В нём ручная разработка считается автоматически:

```text
manual_pit_volume_m3 = pit_area_m2 * 0.08
trench_volume_total_m3 =
  trench_volume_m3 из спецификации
  или sum(route_length_m * route_depth_m * 0.4)
manual_excavation_total_m3 = manual_pit_volume_m3 + trench_volume_total_m3
```

Строка "Разработка грунта вручную" берёт `manual_excavation_total_m3`.

## Приоритет объёма траншей

После уточнения Елены `trench_volume_m3` не считается только legacy-параметром.

В production-режиме `standard_routes` действует приоритет:

1. Если спецификация проекта уже даёт готовый объём траншей, используем `trench_volume_m3`.
2. Если готового объёма нет, считаем по трассам:

```text
trench_route_volume_m3 = route_length_m * route_depth_m * 0.4
trench_volume_total_m3 = sum(trench_route_volume_m3)
```

Один и тот же `trench_volume_total_m3` используется:

- в ручной разработке грунта;
- в песке в траншеи:

```text
compacted_sand_trenches_m3 = trench_volume_total_m3 * sand_compaction_coeff
```

## Какие данные нужны из проекта

Project-параметры:

- `pit_area_m2` — площадь котлована;
- `trench_volume_m3` — готовый объём траншей, если он есть в спецификации;
- `trench_routes[].route_code` — код трассы, например `K1`, `K2`, `VK`, `EO`, если готового объёма нет;
- `trench_routes[].length_m` — длина трассы, если готового объёма нет;
- `trench_routes[].depth_m` — глубина трассы, если готового объёма нет.

Системные настройки:

- `manual_refinement_depth_m = 0.08`;
- `trench_width_m = 0.4`.

Эти системные настройки не нужно спрашивать у Елены в каждом проекте.

## Legacy

Старые параметры оставлены только для legacy-кейсов:

- `assumptions.manual_excavation_override`;
- `manual_excavation_quantity_for_estimate_m3`;
- расчёт траншей через общий `trench_length_m * trench_depth_m * trench_width_m`.

`trench_volume_m3` как готовый объём траншей теперь допустим и в production-режиме, если он пришёл из спецификации проекта.

Кейс `usv_yusupovo_village` явно использует:

```text
manual_excavation_calc_method = legacy_manual_override
```

Старый `expected.json` не менялся.

## Новый тест

Создан кейс:

```text
experiments/earthworks_calculator/cases/test_manual_excavation_standard_routes/
```

Он проверяет:

- `manual_pit_volume_m3 = 26.4`;
- `trench_volume_total_m3 = 16.12`;
- `manual_excavation_total_m3 = 42.52`;
- `estimate_lines.manual_excavation.quantity = 42.52`.

Создан кейс:

```text
experiments/earthworks_calculator/cases/test_manual_excavation_spec_trench_volume/
```

Он проверяет вариант, когда спецификация уже даёт готовый объём траншей:

- `trench_volume_source = spec_volume`;
- `trench_volume_total_m3 = 18.29`;
- `manual_excavation_total_m3 = 44.69`;
- `compacted_sand_trenches_m3 = 23.777`.

## TODO

- Обновить `section_schema.py`.
- В `reviewed_parameters.xlsx` показывать `trench_volume_m3`, если найден готовый объём траншей; иначе показывать `trench_routes`.
- Научить parser сначала искать готовый объём траншей в спецификации.
- Если готового объёма нет, научить parser искать длины и глубины `К1/К2/ВК/ЭО` в спецификации/чертежах.
- Убрать `assumptions.manual_excavation_override` из формы Елены для production-потока.
- Показывать Елене выбранный источник объёма траншей и итоговый объём как контроль.
