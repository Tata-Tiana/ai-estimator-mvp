# test_floor_slab_2_rebar_spec_lengths

Production-кейс для арматуры плиты перекрытия 2-го этажа.

Проверяет режим `rebar_calc_method = "spec_length_items"`:

- из input приходят только `steel_class`, `diameter_mm`, `spec_length_m` и `unit_price_per_m`;
- `code`, `name`, `kg_per_meter`, `rod_length_m`, `price_code` подтягиваются из локального каталога;
- закупочная длина округляется до целых хлыстов;
- `total_rebar_order_weight_kg` считается по закупочной длине текущего раздела.

Опалубка оставлена в production-режиме `spec_formwork_area`, чтобы кейс был близок к реальному production-flow.
