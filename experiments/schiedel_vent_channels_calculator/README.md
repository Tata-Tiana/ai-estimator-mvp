# Schiedel Vent Channels Calculator

Экспериментальный детерминированный калькулятор раздела:

```text
ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel
```

## Как запустить

```bash
.venv/bin/python3 experiments/schiedel_vent_channels_calculator/run_case.py experiments/schiedel_vent_channels_calculator/cases/test_schiedel_vent_channels_trc
```

Второй реальный кейс (другой набор типов каналов):

```bash
.venv/bin/python3 experiments/schiedel_vent_channels_calculator/run_case.py experiments/schiedel_vent_channels_calculator/cases/test_schiedel_vent_channels_ark
```

Если локальный Python запускается без venv:

```bash
python3 experiments/schiedel_vent_channels_calculator/run_case.py experiments/schiedel_vent_channels_calculator/cases/test_schiedel_vent_channels_trc
```

## Что входит в раздел

- кладка вентканалов Schiedel — одна работа (мп), не зависит от набора типов каналов;
- вентиляционные каналы Schiedel по типам: 1х, 2х (36/25см), 3х (52/25см), 4х, редкий CVENT —
  динамический список `schiedel_channel_items[]` (`product_type` + `quantity_pcs`), строка сметы
  появляется только для тех типов, что реально есть у проекта;
- доставка вентканалов;
- расходные материалы и амортизация инструмента;
- нулевые строки структуры Excel: технический надзор, заготовительно-складские расходы, накладные и общехозяйственные расходы, сметная прибыль.

## Что не считается

- клиентская/белая часть;
- коммерческие коэффициенты;
- суммы старой клиентской части по ТН, ЗСР, НР и СП;
- количество шахт/узлов на плане — оно не нужно вообще (Elena, 2026-07-26: "не надо считать шахты,
  это не важно"), важно только количество модулей по типам из спецификации.

## Ручные параметры

- `schiedel_channel_items` — по одной строке `{product_type, quantity_pcs}` на каждый тип канала,
  реально присутствующий у проекта (специфицированное количество модулей, а не количество шахт на
  плане). Если PDF не даёт готовое количество в штуках — это ручной ввод сметчицы.
- `schiedel_delivery_trips` — ручной параметр.

Бренд в этом разделе всегда Schiedel — даже если название не упоминается в проекте явно (подтверждено
на реальной смете, где Schiedel-блоки выставлены без единого упоминания бренда в PDF-чертежах).

## price_registry

У строк с ценой есть `price_code`:

- `schiedel_masonry_work_m`;
- `schiedel_vent_channel_2x_36_25_item`, `schiedel_vent_channel_3x_52_25_item` — существующие коды
  реестра цен;
- `schiedel_vent_channel_1x_item`, `schiedel_vent_channel_4x_item`, `schiedel_vent_channel_cvent_item` —
  новые коды (добавлены 2026-07-26, пока не в реестре цен — используют fallback из `input.json`);
- `schiedel_delivery_truck`.

Режим `locked_case_prices` используется для проверки эталонной сметы: цены берутся из `input.json`, expected должен проходить без mismatch.

Режим `price_registry_with_fallback` используется для будущего MVP: цена ищется в `project_price_overrides`, затем в `price_registry`, затем берётся fallback из `input.json`. Live-суммы могут отличаться от старого expected из-за актуальных цен в прайсе.
