# test_floor_slab_2

## Legacy geometry

Этот кейс использует старую ЮСВ-логику:

- площадь плиты считается как `slab_length_m * slab_width_m`;
- периметр считается как `2 * (slab_length_m + slab_width_m)`;
- площадь опалубки берется равной площади плиты.

В production-режиме площадь опалубки приходит напрямую из спецификации:
`main_formwork_area_m2`.

## Доставка/вывоз опалубки

В production количество рейсов считается от площади опалубки:

- `main_formwork_area_m2 <= 180` -> 2 рейса;
- `main_formwork_area_m2 > 180` -> 4 рейса.

Старое прямое поле `formwork_delivery_trips` может оставаться в legacy input для совместимости,
но при `formwork_delivery_calc_method = "area_threshold"` источником расчета является площадь.

Старый `expected.json` не менять.
