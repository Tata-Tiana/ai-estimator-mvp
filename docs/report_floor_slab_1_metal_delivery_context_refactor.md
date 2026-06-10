# Отчёт: вес арматуры плиты перекрытия 1-го этажа для доставки металла

Дата: 2026-06-10

Раздел:

```text
Ж/Б монолитная плита перекрытия 1-го этажа с балками
```

## Что было

В legacy-кейсе ЮСВ калькулятор плиты 1-го этажа использовал контекст веса арматуры плиты 2-го этажа:

```text
rates.floor_slab_2_rebar_weight_for_delivery_context_kg = 1825.39
```

Этот вес прибавлялся к весу арматуры плиты 1-го этажа, после чего внутри раздела считалась строка:

```text
rebar_metal_delivery
```

Такое поведение повторяет старую смету ЮСВ, но смешивает два раздела.

## Что изменено

Добавлен режим:

```text
rates.metal_delivery_calc_method
```

Варианты:

- `legacy_slab1_slab2_context`;
- `section_output_only`.

Для production используется:

```text
rates.metal_delivery_calc_method = section_output_only
```

В этом режиме калькулятор плиты 1-го этажа не требует:

```text
rates.floor_slab_2_rebar_weight_for_delivery_context_kg
```

и отдаёт только вес закупочной арматуры текущего раздела:

```text
section_rebar_delivery_weight_kg = sum(order_length_m * kg_per_meter)
```

## Статусы параметров

`rates.floor_slab_2_rebar_weight_for_delivery_context_kg`:

- status: `DEPRECATED / BOX_LEVEL_CONTEXT`;
- не требуется в production-калькуляторе плиты 1-го этажа;
- используется только в legacy/reference context ЮСВ.

`rates.max_rebar_delivery_weight_per_truck_kg`:

- status: `DEFAULT_VALUE / SYSTEM_SETTING`;
- значение: `10000`;
- используется как правило будущего box-level расчёта доставки металла.

`section_rebar_delivery_weight_kg`:

- status: `AUTO_CALCULATED`;
- смысл: вес закупочной арматуры текущего раздела;
- должен передаваться на уровень `box_calculator`.

## Production-логика доставки

В production строка `rebar_metal_delivery` внутри плиты 1-го этажа не создаётся.

Доставка металла должна считаться на уровне `box_calculator`:

```text
total_box_metal_weight_kg = sum(section_rebar_delivery_weight_kg)
trucks = ceil(total_box_metal_weight_kg / 10000)
```

Это исключает зависимость калькулятора плиты 1-го этажа от веса арматуры плиты 2-го этажа и предотвращает задвоение доставки в разделах.

## Test-case

Production-проверка сделана в кейсе:

```text
experiments/floor_slab_1_calculator/cases/test_floor_slab_1_direct_formwork_rate/
```

Кейс проверяет:

- `rates.metal_delivery_calc_method = section_output_only`;
- отсутствие `rates.floor_slab_2_rebar_weight_for_delivery_context_kg`;
- наличие `calculation_blocks.rebar.section_rebar_delivery_weight_kg`;
- отсутствие production-строки `rebar_metal_delivery`.

Legacy-кейс:

```text
experiments/floor_slab_1_calculator/cases/test_floor_slab_1/
```

помечен:

```text
rates.metal_delivery_calc_method = legacy_slab1_slab2_context
```

Старый `expected.json` не менялся.

## TODO

Не делалось в этой задаче:

- box-orchestrator;
- pdf_parser_pipeline;
- input_builder;
- price_registry;
- плита 2-го этажа.

Следующий этап:

- собрать `section_rebar_delivery_weight_kg` от всех разделов коробки;
- считать доставку металла один раз в `box_calculator`;
- исключать legacy-строки доставки металла из production totals при сборке общей сметы.
