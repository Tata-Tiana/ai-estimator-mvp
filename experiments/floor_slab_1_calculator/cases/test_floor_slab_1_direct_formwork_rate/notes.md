# Notes: test_floor_slab_1_direct_formwork_rate

Production-кейс для ставки аренды комплекта опалубки без box-level контекста поставщика.

Этот же кейс проверяет production-режим доставки металла: калькулятор плиты 1-го этажа отдаёт только вес закупочной арматуры текущего раздела и не зависит от веса арматуры плиты 2-го этажа.

В этом кейсе используются:

```text
rates.formwork_rate_calc_method = direct_section_rate
rates.formwork_rate_per_m2 = 600
rates.metal_delivery_calc_method = section_output_only
```

В production input не передаются:

```text
rates.formwork_supplier_quote_total
rates.slab_2_formwork_area_for_rate_context_m2
rates.floor_slab_2_rebar_weight_for_delivery_context_kg
```

Строка `formwork_set_rental_material` считает материал от прямой ставки:

```text
material_total = slab_formwork_area_m2 * formwork_rate_per_m2
               = 207.64 * 600
               = 124584
```

Строка `rebar_metal_delivery` в production не создаётся. Вместо неё в `calculation_blocks.rebar` выводится:

```text
section_rebar_delivery_weight_kg = 4665.1632
```

Количество машин доставки металла должно считаться на уровне `box_calculator` по суммарному весу металла коробки.
