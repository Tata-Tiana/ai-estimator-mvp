# Рефакторинг арматуры фундаментной плиты

Дата: 2026-06-08

## Контекст

После созвона с Еленой уточнён новый стандарт входных данных по арматуре фундаментной плиты: в новых проектах спецификация должна давать арматуру в м.п., а не в кг.

Клиентская часть не считается. Формулы старого кейса не сломаны: `test_foundation_slab` остаётся legacy-кейсом для сверки с ранее зафиксированным Excel.

## Что было

Старая методика:

```text
source_weight_kg = sum(weight_parts_kg)
base_length_m = source_weight_kg / kg_per_meter
length_with_waste_m = base_length_m * rebar_waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
material_total = order_length_m * unit_price_per_m
```

То есть проектный вход был весом арматуры в кг.

## Что изменилось

Добавлен режим:

```text
rebar_calc_method = "spec_length_m"
```

В новом режиме основной проектный вход:

- `source_length_m` - длина арматуры по спецификации в м.п.;
- или `length_parts_m` - части длины, которые суммируются в `source_length_m`.

`weight_parts_kg` больше не требуется для нового standard-case.

## Новая формула

```text
source_length_m = source_length_m или sum(length_parts_m)
length_with_waste_m = source_length_m * rebar_waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
material_total = order_length_m * unit_price_per_m
design_weight_kg = source_length_m * kg_per_meter
delivery_weight_kg = order_length_m * kg_per_meter
```

Важно:

- запас сохраняется;
- округление до целых хлыстов сохраняется;
- стоимость считается по закупочной длине в м.п.;
- вес по спецификации считается от исходной длины без запаса;
- вес для доставки считается от закупочной длины.

## Новые поля

На уровне раздела:

- `rebar_calc_method`
- `rebar_waste_coeff`
- `box_metal_delivery_capacity_kg`

На уровне каждой позиции `rebar_items[]`:

- `source_length_m`
- `length_parts_m`
- `kg_per_meter`
- `rod_length_m`
- `unit_price_per_m`
- `steel_class`
- `diameter_mm`

## Контроль армирования

В `result.md` добавлен блок "Контроль армирования":

- вес арматуры по спецификации, кг;
- вес арматуры с запасом/закупкой, кг;
- объём бетона фундаментной плиты, м3;
- плотность армирования по спецификации, кг/м3;
- плотность армирования с запасом, кг/м3.

Эти показатели нужны для проверки разделов с большим объёмом армирования.

## Доставка металла

Строка доставки металла в калькуляторе фундаментной плиты остаётся `manual/fixed`.

В новом блоке арматуры добавлен контроль:

```text
suggested_foundation_rebar_delivery_trucks =
  ceil(foundation_slab_rebar_delivery_weight_kg / box_metal_delivery_capacity_kg)
```

Финальная доставка металла должна считаться на уровне `box_calculator`, где будет суммироваться металл по всем разделам коробки дома.

## Price registry / каталог

Для production в `price_registry` или material catalog по арматуре нужны не только цены, но и расчётные характеристики:

- `price_code`;
- `steel_class`, если используется для цены/кода;
- `diameter_mm`;
- `kg_per_meter`;
- `rod_length_m`;
- `unit_price_per_m`;
- `unit = м.п.`

Сейчас `kg_per_meter`, `rod_length_m` и `unit_price_per_m` берутся из `input.json` тестового кейса. Это временно.

TODO:

- расширить `price_registry`, чтобы он отдавал `kg_per_meter` и `rod_length_m`;
- научить live-pricing обновлять не только цену, но и характеристики арматуры из каталога.

## Новый test-case

Создан:

```text
experiments/foundation_slab_calculator/cases/test_foundation_slab_rebar_spec_length/
```

Кейс проверяет:

- арматуру из м.п.;
- отсутствие обязательного `weight_parts_kg`;
- запас;
- округление до хлыстов;
- стоимость по м.п.;
- проектный вес;
- закупочный/доставочный вес;
- контрольную плотность армирования.

## Legacy

Старый кейс:

```text
experiments/foundation_slab_calculator/cases/test_foundation_slab/
```

остаётся в режиме:

```text
rebar_calc_method = "legacy_weight_to_length"
```

Старый `expected.json` не менялся.

## Следующие шаги

Не сделано в этом этапе и должно быть отдельными задачами:

- обновить `section_schema.py`;
- заменить `rebar_items[].weight_parts_kg` на `rebar_items[].source_length_m` / `length_parts_m` в таблице параметров;
- обновить `reviewed_parameters.xlsx`;
- научить parser искать арматуру в м.п. в спецификации;
- расширить `price_registry` полями `kg_per_meter` и `rod_length_m`;
- на уровне `box_calculator` суммировать вес металла по всем разделам для доставки.
