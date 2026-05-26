# Schiedel Vent Channels Calculator

Экспериментальный детерминированный калькулятор раздела:

```text
ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel
```

## Как запустить

```bash
../.venv/bin/python3 experiments/schiedel_vent_channels_calculator/run_case.py experiments/schiedel_vent_channels_calculator/cases/test_schiedel_vent_channels_usv
```

Если локальный Python запускается без venv:

```bash
python3 experiments/schiedel_vent_channels_calculator/run_case.py experiments/schiedel_vent_channels_calculator/cases/test_schiedel_vent_channels_usv
```

## Что входит в раздел

- кладка вентканалов Schiedel;
- вентиляционный канал 2х, 36/25 см;
- вентиляционный канал 3х, 52/25 см;
- доставка вентканалов;
- расходные материалы и амортизация инструмента;
- нулевые строки структуры Excel: технический надзор, заготовительно-складские расходы, накладные и общехозяйственные расходы, сметная прибыль.

## Что не считается

- клиентская/белая часть;
- коммерческие коэффициенты;
- суммы старой клиентской части по ТН, ЗСР, НР и СП;
- автоматический вывод количества блоков Schiedel из правых контрольных чисел.

## Ручные параметры

- `schiedel_vent_channel_2x_count = 24`;
- `schiedel_vent_channel_3x_count = 8`;
- `schiedel_delivery_trips = 1`.

Количество `24` и `8` берётся как manual/specification input, потому что контрольные правые значения пока не являются надёжной формулой закупочного количества.

## price_registry

У материальных строк есть `price_code`. Сейчас цены берутся из `input.json`.
Позже `price_code` можно связать с Google Sheets `price_registry`, не меняя расчётные формулы.
