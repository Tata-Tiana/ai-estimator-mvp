# Test: Подмости/леса от количества этажей

Этот кейс проверяет новый production-стандарт:

```text
scaffolding_setup_quantity = floors_count * scaffolding_setup_units_per_floor
scaffolding_timber_quantity_m3 = floors_count * scaffolding_timber_m3_per_floor
```

При `floors_count = 2` и системных defaults `1` на этаж:

- устройство/демонтаж подмостей = `2 компл`;
- пиломатериал для подмостей = `2 м3`.

Прямые поля `scaffolding_setup_quantity` и `scaffolding_timber_quantity_m3` в этом кейсе не используются.
