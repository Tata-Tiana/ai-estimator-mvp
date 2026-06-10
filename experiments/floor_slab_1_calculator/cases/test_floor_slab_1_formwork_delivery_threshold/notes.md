# Notes: test_floor_slab_1_formwork_delivery_threshold

Кейс проверяет production-правило доставки/вывоза опалубки по площади основной опалубки плиты.

## Проверяемая граница

Входные значения подобраны так, чтобы:

```text
slab_concrete_volume_m3 = 35.5548 - 3.1548 = 32.4
slab_formwork_area_m2 = 32.4 / 0.18 = 180
```

Ожидание:

```text
slab_formwork_area_m2 <= 180
formwork_delivery_trucks = 2
formwork_delivery_breakdown = 1 привоз + 1 вывоз
```

Существующие production/legacy кейсы с площадью `207.64 м2` дополнительно проверяют ветку `> 180`, где должно быть `4` машины.
