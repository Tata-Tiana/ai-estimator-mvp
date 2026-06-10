# Отчёт: кран несущих стен от доставок блоков

Дата: 2026-06-10

## Что было

В калькуляторе несущих стен и перемычек количество смен крана для строки `main_walls_blocks_crane_moving_25t` задавалось прямым входным параметром:

```text
main_walls_crane_shifts
```

Для старого ЮСВ-кейса это значение оставлено как legacy, чтобы не менять старый `expected.json`.

## Что стало

Добавлен режим:

```text
main_walls_crane_calc_method = delivery_trucks_threshold
```

Production-формула по правилу Елены:

```text
if gas_block_delivery_trucks <= 3:
    main_walls_crane_shifts = 1
else:
    main_walls_crane_shifts = 2
```

`gas_block_delivery_trucks` берётся из расчётного блока доставок блоков. Строка `main_walls_blocks_crane_moving_25t` теперь использует рассчитанное `main_walls_crane_shifts`.

## Статусы параметров

| parameter | status | comment |
| --- | --- | --- |
| `main_walls_crane_calc_method` | SYSTEM_SETTING | Выбирает legacy или production-расчёт. |
| `gas_block_delivery_trucks` | AUTO_CALCULATED | Считается от закупочного объёма газоблоков. |
| `main_walls_crane_shifts` | AUTO_CALCULATED в production | В форме Елены не должен быть manual_required. |
| `main_walls_crane_shifts` | LEGACY_ONLY в старом кейсе | Нужен для сверки старой сметы ЮСВ. |

## Проверочные кейсы

- `test_main_walls_crane_from_delivery_trucks`: 3 доставки блоков дают 1 смену крана.
- `test_main_walls_crane_from_delivery_trucks_four`: 4 доставки блоков дают 2 смены крана.

## TODO

- Обновить `section_schema.py`: убрать `main_walls_crane_shifts` из ручного ввода production.
- В `reviewed_parameters.xlsx` показывать Елене количество доставок блоков и рассчитанные смены крана как контроль.
- В будущем `input_builder` должен передавать `main_walls_crane_calc_method = delivery_trucks_threshold` для production-потока.
