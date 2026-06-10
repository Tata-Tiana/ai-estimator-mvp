# Отчёт: ставка опалубки плиты перекрытия 1-го этажа

Дата: 2026-06-10

Раздел:

```text
Ж/Б монолитная плита перекрытия 1-го этажа с балками
```

## Что было

В legacy-кейсе ЮСВ в `rates` хранился справочный контекст поставщика:

```text
rates.formwork_supplier_quote_total = 170710
rates.slab_2_formwork_area_for_rate_context_m2 = 81.9
```

Справочная средняя ставка считалась так:

```text
raw_average_rate =
    formwork_supplier_quote_total
    / (floor_slab_1_formwork_area_m2 + slab_2_formwork_area_for_rate_context_m2)
```

Этот контекст относится к предложению поставщика по комплекту опалубки на две плиты.

## Что изменено

Добавлен режим:

```text
rates.formwork_rate_calc_method
```

Варианты:

- `legacy_supplier_quote_context`;
- `direct_section_rate`.

Для production используется:

```text
rates.formwork_rate_calc_method = direct_section_rate
rates.formwork_rate_per_m2 = 600
```

Строка "Комплект опалубки" считает сумму от прямой ставки этой плиты:

```text
material_total =
    slab_formwork_area_m2 * rates.formwork_rate_per_m2
```

## Статусы параметров

`rates.slab_2_formwork_area_for_rate_context_m2`:

- status: `DEPRECATED / BOX_LEVEL_CONTEXT`;
- в production-калькуляторе плиты 1-го этажа не требуется;
- используется только в legacy/reference context ЮСВ.

`rates.formwork_supplier_quote_total`:

- status: `MANUAL_REQUIRED / BOX_LEVEL_QUOTE`;
- не является production-параметром плиты 1-го этажа;
- должен жить в будущем box-level quote context.

`rates.formwork_rate_per_m2`:

- status: `PRICE_DATABASE / MANUAL_OVERRIDE`;
- смысл: применяемая ставка аренды комплекта опалубки для этой плиты;
- используется строкой `formwork_set_rental_material`.

`raw_average_rate`:

- status: `AUTO_CALCULATED`;
- считается только в legacy/reference mode;
- не заменяет применяемую ставку production-строки.

## Новый test-case

Создан:

```text
experiments/floor_slab_1_calculator/cases/test_floor_slab_1_direct_formwork_rate/
```

Кейс проверяет:

- production-режим `direct_section_rate`;
- отсутствие `rates.formwork_supplier_quote_total`;
- отсутствие `rates.slab_2_formwork_area_for_rate_context_m2`;
- ставку `rates.formwork_rate_per_m2 = 600`;
- строку `formwork_set_rental_material`.

Проверочный расчёт:

```text
207.64 * 600 = 124584
```

## Legacy

Старый кейс:

```text
experiments/floor_slab_1_calculator/cases/test_floor_slab_1/
```

помечен:

```text
rates.formwork_rate_calc_method = legacy_supplier_quote_context
```

Старый `expected.json` не менялся.

## TODO

Не делалось в этой задаче:

- box-orchestrator;
- pdf_parser_pipeline;
- input_builder;
- price_registry;
- плита 2-го этажа;
- клиентская часть.

Следующий этап:

- создать box-level quote context;
- перенести туда `box_formwork_supplier_quote_total`;
- считать `box_formwork_quote_area_m2 = floor_slab_1_formwork_area_m2 + floor_slab_2_formwork_area_m2`;
- показывать `box_formwork_reference_rate` как контроль;
- убрать `rates.slab_2_formwork_area_for_rate_context_m2` из production-полей плиты 1-го этажа в review form.
