# Отчёт по калькулятору вентиляционных каналов Schiedel

Дата: 2026-05-26

## Кратко

В проекте `ai-estimator-mvp` сделан отдельный экспериментальный детерминированный калькулятор раздела:

`ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel`

Калькулятор считает только серую внутреннюю себестоимость: материалы/механизмы, работы и итог раздела. Клиентская часть, белая зона Excel, коммерческие коэффициенты и налоги вне текущего scope.

AI в расчёте не используется. Формулы, ручные количества, округления и ожидаемые значения зафиксированы явно в `input.json`, `expected.json` и коде калькулятора.

## Где находится

```text
experiments/schiedel_vent_channels_calculator/
├── calculator.py
├── run_case.py
├── README.md
├── notes.md
└── cases/
    └── test_schiedel_vent_channels_usv/
        ├── input.json
        ├── expected.json
        ├── result.json
        └── result.md
```

## Что считает калькулятор

Калькулятор считает 9 строк серой внутренней сметы:

- кладку вентканалов Schiedel;
- вентиляционный канал 2х, 36/25 см;
- вентиляционный канал 3х, 52/25 см;
- доставку вентканалов;
- расходные материалы и амортизацию инструмента;
- нулевые строки структуры: технический надзор, заготовительно-складские расходы, накладные и общехозяйственные расходы, сметная прибыль.

## Что не входит

- клиентская/белая зона Excel;
- коммерческие коэффициенты;
- суммы старой клиентской части по ТН, ЗСР, НР и СП;
- автоматический вывод количества блоков Schiedel из правых контрольных чисел.

## Блоки расчёта

В `result.json` сохраняются структурированные блоки:

```text
calculation_blocks:
  masonry
  materials
  delivery
  consumables
  control_metrics
```

Построчные формулы и raw/display значения сохраняются в `estimate_lines`.

## Ключевые формулы

### Кладка вентканалов

Количество берётся из входного параметра:

```text
schiedel_masonry_total_length_m = 15.82
```

Контроль:

```text
15.82 = 6.2 + 4.81 * 2
```

Стоимость:

```text
15.82 * 5000 = 79100
```

Важно: старая левая часть может показывать `16 мп`, но серая сумма считается от raw `15.82 мп`.

### Материалы Schiedel

Вентиляционный канал 2х:

```text
quantity = 24 шт
material_total = 24 * 504 = 12096
```

Вентиляционный канал 3х:

```text
quantity = 8 шт
material_total = 8 * 720 = 5760
```

Важно: количества `24` и `8` не выводятся автоматически из правых контрольных чисел. Пока это manual/specification input от спецификации Schiedel или таблицы Елены.

Справочные контрольные значения сохранены в отчёте и `calculation_blocks.control_metrics`, но не участвуют в расчёте quantity:

```text
2х control_blocks_raw = 65.51515152
2х secondary_control_value = 28
3х control_blocks_raw = 14.57575758
3х secondary_control_value = 6
```

### Доставка

```text
material_total = 1 * 15000 = 15000
work_total = 1 * 2500 = 2500
line_total = 17500
```

Количество доставок `1` является ручным параметром.

### Расходные материалы

База прямых затрат до расходников:

```text
79100 + 12096 + 5760 + 17500 = 114456
```

Расходники:

```text
114456 * 0.03 = 3433.68 -> 3434
```

### Нулевые строки структуры

В estimate_lines обязательно добавлены:

```text
Технический надзор
Заготовительно-складские расходы
Накладные и общехозяйственные расходы
Сметная прибыль
```

Они нужны для структуры Excel, но не меняют internal totals. Суммы `1053`, `536`, `14746`, `18959` из старой части не используются.

## Raw vs Display

Калькулятор хранит:

- `quantity_raw`;
- `quantity_display`;
- `material_total_raw`;
- `material_total`;
- `work_total_raw`;
- `work_total`;
- `line_total_raw`;
- `line_total`.

Деньги считаются через `Decimal` и `ROUND_HALF_UP`.

## Текущие итоги

```text
test_schiedel_vent_channels_usv -> ok (138/138)
internal_materials_total_raw = 36289.68
internal_materials_total = 36290
internal_works_total_raw = 81600
internal_works_total = 81600
internal_section_total_raw = 117889.68
internal_section_total = 117890
sum_of_displayed_line_totals = 117890
```

Проверка:

```bash
../.venv/bin/python3 experiments/schiedel_vent_channels_calculator/run_case.py experiments/schiedel_vent_channels_calculator/cases/test_schiedel_vent_channels_usv
```

Результат:

```text
status: ok
ok: 138
mismatch: 0
```

## Важные ограничения

- AI не используется в расчёте.
- Не используются ссылки на Excel-ячейки как идентификаторы.
- Основные идентификаторы строк — смысловой `code` и название строки.
- Цены сейчас берутся из `input.json`.
- У материальных строк добавлен `price_code` для будущей связки с Google Sheets `price_registry`.
- Клиентская часть не считается.
- Количества `24` и `8` требуют подтверждения у Елены или по спецификации.
