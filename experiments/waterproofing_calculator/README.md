# Waterproofing Calculator Experiment

Экспериментальный детерминированный расчётный модуль для блока "Гидроизоляция фундаментной плиты".

AI здесь не используется. Калькулятор считает только серую внутреннюю себестоимость: материалы, работы и итог блока. Клиентская часть, рентабельность, НР/СП/ТН и коммерческие коэффициенты не считаются.

## Структура

```text
waterproofing_calculator.py
run_waterproofing_calc.py
cases/
  test_waterproofing_foundation_slab/
    input.json
    expected.json
    notes.md
  test_waterproofing_foundation_slab_live_prices/
    input.json
    notes.md
    result.json
    result.md
output/
  test_waterproofing_foundation_slab/
    waterproofing_result.json
    waterproofing_result.md
  test_waterproofing_foundation_slab_live_prices/
    waterproofing_result.json
    waterproofing_result.md
```

## Запуск

Из корня проекта:

```bash
../.venv/bin/python3 experiments/waterproofing_calculator/run_waterproofing_calc.py experiments/waterproofing_calculator/cases/test_waterproofing_foundation_slab
```

Live-режим с `price_registry` и fallback:

```bash
../.venv/bin/python3 experiments/waterproofing_calculator/run_waterproofing_calc.py experiments/waterproofing_calculator/cases/test_waterproofing_foundation_slab_live_prices
```

Проверка компиляции:

```bash
../.venv/bin/python3 -m py_compile experiments/waterproofing_calculator/waterproofing_calculator.py experiments/waterproofing_calculator/run_waterproofing_calc.py
```

## Входные параметры

Калькулятору нужны:

- периметр и высота борта фундаментной плиты;
- ставка работы по гидроизоляции;
- расход и цена праймера;
- расход, слои и цена мастики;
- объём/толщина ЭППС 100 мм по спецификации;
- неутепляемые участки для геометрической проверки;
- объём пачки и цена ЭППС;
- правило расхода клей-пены;
- коэффициенты логистики и расходников.

## Режимы цен

По умолчанию используется режим:

```json
{
  "pricing": {
    "mode": "locked_case_prices"
  }
}
```

Если блока `pricing` нет, поведение такое же: цены берутся из `input.json`, старый эталонный кейс сравнивается с `expected.json`.

Live-режим:

```json
{
  "pricing": {
    "mode": "price_registry_with_fallback",
    "registry_path": "output/price_registry_filled_v3.xlsx"
  }
}
```

В этом режиме цены для строк с `price_code` ищутся по приоритету:

```text
project_price_overrides
price_registry
input.json fallback
```

Суммы live-режима могут отличаться от старого `expected.json`, потому что часть цен берётся из актуального прайса. Поэтому live-кейс не сравнивается со старым expected по суммам.

## Ожидаемый результат тестового кейса

```text
waterproofing_base_subtotal = 48 777
internal_materials_total    = 33 961
internal_works_total        = 17 255
internal_section_total      = 51 216
```

## Формат результата

`waterproofing_result.json` хранит расчёт отдельно от проверки:

```json
{
  "case_name": "test_waterproofing_foundation_slab",
  "inputs": {},
  "calculation_blocks": {
    "waterproofing": {}
  },
  "estimate_lines": [],
  "internal_totals": {},
  "expected": {},
  "comparison": [],
  "warnings": []
}
```

`waterproofing_result.md` содержит человекочитаемый отчёт: входные параметры, расчётный блок, строки серой сметы, итоги и comparison.

В live-режиме дополнительно выводятся `pricing_summary` и таблица источников цен.
