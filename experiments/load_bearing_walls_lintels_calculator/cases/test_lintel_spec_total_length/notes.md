# Test: перемычки общей длиной из спецификации

Этот кейс проверяет production-стандарт:

```text
lintel_length_calc_method = "spec_total_length"
lintel_total_length_m = 23.4
```

Старый список `lintel_lengths_m[*].length_m/count` в этом кейсе не используется.

Резка U-блока остаётся в штуках:

```text
u_block_quantity = lintel_total_length_m / gas_block_length_m
u_block_quantity = 23.4 / 0.6 = 39 шт
```
