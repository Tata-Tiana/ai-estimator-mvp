# Test communications pipe items

Тестовый кейс для production-стандарта расчёта длины коммуникаций из спецификации труб.

## Проверяемая формула

```text
communications_length_m = sum(pipe_length_m * quantity)
```

Если позиция содержит готовое `total_length_m`, используется оно.

## Проверочный расчёт

- Труба 1 м: `1 * 12 = 12 м`
- Труба 2 м: `2 * 5 = 10 м`
- Труба 3 м: `3 * 4 = 12 м`
- Труба гофрированная: `25 м`
- Итого: `59 м`

## Важно

- `communications_length_m` не вводится вручную в production-режиме.
- `communications_work.quantity = 59`.
- `communications_material.quantity = 59`.
- Прямой ввод `communications_length_m` остаётся только для legacy-кейсов.
