# Test: арматура из спецификации в м.п.

Этот кейс проверяет production-стандарт для арматуры несущих стен и перемычек:

```text
main_wall_rebar_calc_method = "spec_length_items"
lintel_rebar_calc_method = "spec_length_items"
```

Арматура приходит из спецификации в м.п. и разделяется по:

- этажу;
- конструкции;
- классу стали;
- диаметру.

Закупочная длина считается по общему правилу:

```text
length_with_waste_m = spec_length_m * rebar_waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
```

Перегородки в этот калькулятор не входят.
