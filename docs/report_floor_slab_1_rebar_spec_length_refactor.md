# Отчёт: арматура плиты перекрытия 1-го этажа из спецификации в м.п.

Дата: 2026-06-10

Раздел:

```text
Ж/Б монолитная плита перекрытия 1-го этажа с балками
```

## Что было

В legacy-кейсе ЮСВ арматура плиты 1-го этажа задавалась весом:

```text
source_weight_kg
source_weight_parts_kg
```

Калькулятор переводил вес в длину:

```text
base_length_m = source_weight_kg / kg_per_meter
length_with_waste_m = base_length_m * waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
material_total = order_length_m * unit_price_per_m
```

Эта логика оставлена только для старого кейса.

## Что изменено

Добавлен режим:

```text
rebar_calc_method
```

Варианты:

- `legacy_weight_parts`;
- `spec_length_items`.

Production-режим:

```text
rebar_calc_method = spec_length_items
```

В этом режиме каждая позиция арматуры содержит:

```text
floor = 1
component = floor_slab_1
steel_class
diameter_mm
spec_length_m
kg_per_meter
rod_length_m
unit_price_per_m
```

`code` и `name` не спрашиваются у Елены и формируются автоматически.

## Production-формула

```text
base_length_m = spec_length_m
length_with_waste_m = spec_length_m * waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
delivery_weight_kg = order_length_m * kg_per_meter
material_total = order_length_m * unit_price_per_m
```

Вес текущего раздела для будущей box-level доставки:

```text
section_rebar_delivery_weight_kg = sum(order_length_m * kg_per_meter)
```

## Статусы параметров

`rebar_items[*].source_weight_parts_kg`:

- status: `DEPRECATED / LEGACY_ONLY`;
- используется только для повторения старой сметы ЮСВ.

`rebar_items[*].spec_length_m`:

- status: `AUTO_PROJECT`;
- source_of_truth: спецификация проекта / ведомость арматуры плиты 1-го этажа;
- unit: `м.п.`

`rebar_items[*].steel_class`, `rebar_items[*].diameter_mm`:

- status: `AUTO_PROJECT`;
- source_of_truth: спецификация арматуры.

`rebar_items[*].code`, `rebar_items[*].name`:

- status: `AUTO_CALCULATED`;
- формируются по классу стали и диаметру.

`kg_per_meter`, `rod_length_m`:

- status: `MATERIAL_CATALOG`;
- сейчас могут приходить из input тестового кейса как snapshot.

`unit_price_per_m`:

- status: `PRICE_DATABASE`;
- сейчас может приходить из input тестового кейса как fallback/snapshot.

`base_length_m`, `length_with_waste_m`, `rods`, `order_length_m`, `delivery_weight_kg`, `section_rebar_delivery_weight_kg`:

- status: `AUTO_CALCULATED`.

## Test-case

Создан:

```text
experiments/floor_slab_1_calculator/cases/test_floor_slab_1_rebar_spec_lengths/
```

Кейс проверяет:

- production-режим `spec_length_items`;
- отсутствие `source_weight_parts_kg`;
- `spec_length_m` как источник `base_length_m`;
- округление закупки до целых хлыстов;
- строки арматуры в `мп`;
- расчёт `section_rebar_delivery_weight_kg` только по текущему разделу.

## Legacy

Старый кейс:

```text
experiments/floor_slab_1_calculator/cases/test_floor_slab_1/
```

помечен:

```text
rebar_calc_method = legacy_weight_parts
```

Старый `expected.json` не менялся.

## TODO

Не делалось в этой задаче:

- pdf_parser_pipeline;
- input_builder;
- price_registry;
- box-orchestrator;
- плита 2-го этажа;
- другие разделы.

Следующие этапы:

- обновить `section_schema.py`;
- обновить `reviewed_parameters.xlsx`;
- научить parser брать арматуру плиты 1-го этажа из спецификации в м.п.;
- убрать `source_weight_parts_kg` из production-формы Елены;
- подключить полноценный catalog/price registry для `kg_per_meter`, `rod_length_m`, `unit_price_per_m`;
- передавать `section_rebar_delivery_weight_kg` в будущий `box_calculator`;
- считать доставку металла по всей коробке:

```text
total_box_metal_weight_kg = sum(section_rebar_delivery_weight_kg)
trucks = ceil(total_box_metal_weight_kg / 10000)
```
