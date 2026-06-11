# test_floor_slab_2_formwork_delivery_threshold_above_180

Проверяет верхнюю сторону правила доставки/вывоза опалубки:

- `main_formwork_area_m2 = 180.01`;
- `formwork_delivery_calc_method = area_threshold`;
- ожидается `formwork_delivery_trips = 4`.

Ручной override не передается.
