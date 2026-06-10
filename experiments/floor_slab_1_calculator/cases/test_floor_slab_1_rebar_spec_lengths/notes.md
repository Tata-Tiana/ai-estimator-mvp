# Notes: test_floor_slab_1_rebar_spec_lengths

Production-кейс для арматуры плиты перекрытия 1-го этажа из спецификации в м.п.

Используется:

```text
rebar_calc_method = spec_length_items
rates.metal_delivery_calc_method = section_output_only
```

В `rebar_items` не передаются:

```text
source_weight_kg
source_weight_parts_kg
code
name
```

`code` и `name` формируются автоматически по классу стали и диаметру.

Проверяется:

- `spec_length_m` становится `base_length_m`;
- закупочная длина округляется до целых хлыстов;
- строки арматуры имеют unit `мп`;
- `section_rebar_delivery_weight_kg` считается только по текущему разделу.

Доставка металла по всей коробке должна считаться на уровне `box_calculator`.
