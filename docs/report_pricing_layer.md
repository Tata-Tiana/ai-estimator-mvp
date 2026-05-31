# Отчёт по слою цен MVP

## Что сделано

В проект добавлен отдельный безопасный слой работы с ценами:

```text
experiments/pricing/
```

Он не меняет формулы существующих калькуляторов и не подключается к ним автоматически. Старые расчёты продолжают работать в режиме зафиксированных цен кейса.

## Зачем это нужно

Раньше цены жили прямо в `input.json` и параметрах калькуляторов. Для MVP нужен переходный слой, который позволит позже брать цены из единого прайса, но не сломает уже сверенные с Еленой расчёты.

Слой цен поддерживает безопасный fallback:

```text
project_price_overrides
↓
price_registry
↓
input.json fallback
```

Если цена не найдена в прайсе, используется старая цена из входных данных и возвращается warning.

## Price registry

Подготовлена версия:

```text
output/price_registry_filled_v3.xlsx
```

В ней есть:

- лист `price_registry`;
- лист `rows_to_add`.

Состояние покрытия:

```text
required unique price_code: 81
found in price_registry: 18
found in rows_to_add: 63
missing completely: 0
```

Это означает, что для MVP все требуемые коды либо уже есть в основном прайсе, либо явно вынесены в лист добавления с ценой из калькулятора и статусом проверки.

## Что добавлено в код

```text
experiments/pricing/price_reader.py
experiments/pricing/validate_price_registry.py
experiments/pricing/check_required_codes_against_registry.py
experiments/pricing/test_price_reader_demo.py
experiments/pricing/README.md
```

### `price_reader.py`

Содержит:

- `load_price_registry(path)`;
- `load_project_price_overrides(path)`;
- `resolve_price(price_code, fallback_price, registry, overrides=None)`.

### `validate_price_registry.py`

Проверяет:

- наличие листа `price_registry`;
- обязательные колонки;
- количество строк;
- заполненные и пустые `price_code`;
- дубли;
- пустые и нечисловые цены.

Отчёт:

```text
experiments/pricing/output/price_registry_validation_report.md
```

### `check_required_codes_against_registry.py`

Сравнивает required-коды калькуляторов с `price_registry` и `rows_to_add`.

Отчёт:

```text
experiments/pricing/output/required_codes_coverage_report.md
```

### `test_price_reader_demo.py`

Показывает работу resolver:

- код из `price_registry`;
- код из `rows_to_add`, который сейчас уходит в fallback;
- неизвестный код;
- код доставки бетона с fallback.

## Price code в калькуляторах

В старые калькуляторы добавлено единое поле `price_code` в строках сметы, где есть цена или ставка. Отдельные `material_price_code` и `work_rate_code` не вводились.

Обновлены:

- `earthworks_calculator`;
- `foundation_slab_calculator`;
- `waterproofing_calculator`;
- `load_bearing_walls_lintels_calculator`;
- `floor_slab_1_calculator`;
- `floor_slab_2_calculator`.

Существующие `price_code` в калькуляторах плоской кровли и Schiedel не переименовывались.

## Проверки

Проверены все текущие калькуляторы:

```text
earthworks:
  horoshevka_14 -> ok (76/76)
  usv_yusupovo_village -> ok (100/100)

foundation_slab:
  internal_section_total = 2538325

waterproofing:
  internal_section_total = 51216

load_bearing_walls_lintels:
  internal_section_total = 2672103

floor_slab_1:
  ok (194/194), internal_section_total = 1787527

floor_slab_2:
  ok (222/222), internal_section_total = 717051

flat_roof:
  ok (460/460), internal_section_total = 2038872

schiedel_vent_channels:
  ok (138/138), internal_section_total = 117890
```

Проверки pricing-layer:

```text
price_registry validation: rows=131 filled=18 empty=113 duplicates=0
required code coverage: required=81 registry=18 rows_to_add=63 missing=0 fallback=63
```

## Что пока не сделано

- Калькуляторы пока не переключены на режим `price_registry_with_fallback`.
- Цены из `rows_to_add` требуют проверки Елены.
- Спорные единицы измерения не подставлены автоматически:
  - бетон по зонам против общего кода;
  - доставка бетона рейсами против зон/м3;
  - ПВХ мембрана рулонами против м2;
  - геотекстиль 300 при наличии близкой строки 150.

## Главное ограничение

Клиентская часть сметы не считается. Этот слой касается только источника цен для внутренней серой себестоимости.
