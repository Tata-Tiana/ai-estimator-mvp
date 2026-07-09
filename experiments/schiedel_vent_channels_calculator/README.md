# Schiedel Vent Channels Calculator

Экспериментальный детерминированный калькулятор раздела:

```text
ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel
```

## Как запустить

```bash
.venv/bin/python3 experiments/schiedel_vent_channels_calculator/run_case.py experiments/schiedel_vent_channels_calculator/cases/test_schiedel_vent_channels_usv
```

Live-режим с `price_registry` и fallback:

```bash
.venv/bin/python3 experiments/schiedel_vent_channels_calculator/run_case.py experiments/schiedel_vent_channels_calculator/cases/test_schiedel_vent_channels_usv_live_prices
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

У строк с ценой есть `price_code`:

- `schiedel_masonry_work_m`;
- `schiedel_vent_channel_2x_36_25_item`;
- `schiedel_vent_channel_3x_52_25_item`;
- `schiedel_delivery_truck`.

Режим `locked_case_prices` используется для проверки старой эталонной сметы: цены берутся из `input.json`, expected должен проходить без mismatch.

Режим `price_registry_with_fallback` используется для будущего MVP: цена ищется в `project_price_overrides`, затем в `price_registry`, затем берётся fallback из `input.json`. Live-суммы могут отличаться от старого expected из-за актуальных цен в прайсе.
