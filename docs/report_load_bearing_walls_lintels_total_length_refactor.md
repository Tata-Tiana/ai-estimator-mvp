# Отчёт: перемычки общей длиной из спецификации

Дата: 2026-06-09

## Что было

В калькуляторе несущих стен и перемычек общая длина перемычек считалась из списка отдельных длин и количеств:

```text
lintel_total_length_m = sum(lintel_lengths_m[*].length_m * lintel_lengths_m[*].count)
```

Этот режим оставлен для старого ЮСВ-кейса.

## Что стало

Добавлен production-режим:

```text
lintel_length_calc_method = "spec_total_length"
lintel_total_length_m = готовая общая длина перемычек в U-блоке из спецификации
```

Дальше используются прежние формулы:

```text
u_block_quantity = lintel_total_length_m / gas_block_length_m
lintel_raw_concrete_volume_m3 = lintel_total_length_m * lintel_section_width_m * lintel_section_height_m
lintel_required_concrete_volume_m3 = lintel_raw_concrete_volume_m3 * concrete_waste_coeff
lintel_concrete_order_volume_m3 = max(lintel_concrete_min_order_volume_m3, ceil(lintel_required_concrete_volume_m3))
```

## Важно по U-блоку

Строка `u_block_lintel_cutting` остаётся в штуках:

```text
unit = "шт"
quantity = lintel_total_length_m / 0.6
```

Резка U-блока не переводится в м.п. и не округляется вверх, потому что старый калькулятор делал простое деление.

## Классификация параметров

| Параметр | Статус | Комментарий |
| --- | --- | --- |
| `lintel_total_length_m` | AUTO_PROJECT | Готовая общая длина перемычек в U-блоке из спецификации. |
| `lintel_lengths_m[*].length_m` | DEPRECATED / LEGACY_ONLY | Только для старого ЮСВ-кейса. |
| `lintel_lengths_m[*].count` | DEPRECATED / LEGACY_ONLY | Только для старого ЮСВ-кейса. |
| `gas_block_length_m` | DEFAULT_VALUE / SYSTEM_SETTING | Длина блока 0.6 м для расчёта количества резов. |

## Новый тест

Создан кейс:

```text
experiments/load_bearing_walls_lintels_calculator/cases/test_lintel_spec_total_length/
```

Проверка:

```text
lintel_total_length_m = 23.4
u_block_quantity = 23.4 / 0.6 = 39 шт
```

## TODO

- Обновить `section_schema.py`.
- Добавить `lintel_total_length_m` в `reviewed_parameters.xlsx`.
- Научить parser брать общую длину перемычек в U-блоке из спецификации.
- Убрать `lintel_lengths_m[*].length_m` и `lintel_lengths_m[*].count` из формы Елены для production.
- Показывать Елене `lintel_total_length_m` и рассчитанное `u_block_quantity` как контроль.
