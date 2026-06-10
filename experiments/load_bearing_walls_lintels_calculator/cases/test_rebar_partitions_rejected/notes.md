# Negative test: арматура перегородок не входит в несущие стены

Этот кейс намеренно содержит:

```text
component = "partitions"
```

Ожидаемое поведение: калькулятор должен упасть с ошибкой:

```text
partitions rebar must be calculated in partitions calculator, not in load_bearing_walls_lintels_calculator
```
