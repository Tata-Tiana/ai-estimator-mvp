# Отчёт: Live-Pricing Layer

Дата: `2026-06-01`

## Назначение

Live-pricing слой нужен, чтобы готовые детерминированные калькуляторы могли работать в двух режимах:

- эталонный режим для проверки старой сметы;
- live-режим для MVP, где цены подтягиваются из актуального `price_registry` с безопасным fallback.

Расчётные формулы калькуляторов при этом не меняются. AI не считает смету, клиентская/белая часть не считается.

## Режимы

### locked_case_prices

Это режим по умолчанию.

Если в `input.json` нет блока `pricing`, калькулятор работает как раньше:

- цены берутся из `input.json`;
- старые `expected.json` остаются эталоном;
- старые locked-кейсы проходят без mismatch;
- итоговые суммы старых кейсов не меняются.

### price_registry_with_fallback

Live-режим включается отдельным блоком:

```json
{
  "pricing": {
    "mode": "price_registry_with_fallback",
    "registry_path": "output/price_registry_filled_v3.xlsx"
  }
}
```

Приоритет источников цены:

```text
project_price_overrides
price_registry
input.json fallback
```

Если `price_code` найден в `price_registry`, используется цена из прайса.

Если `price_code` не найден, калькулятор берёт старую цену из `input.json` и пишет warning. Это позволяет не ломать MVP, пока прайс не полностью проверен Еленой.

## Что добавлено

- общий helper:
  - `experiments/pricing/live_pricing.py`;
- live-кейсы для всех готовых калькуляторов;
- `pricing_summary` во всех live `result.json`;
- блок `## Источники цен` во всех live `result.md`;
- общий отчёт:
  - `experiments/pricing/output/live_pricing_sections_report.md`.

Live `expected.json` не создавались: live-итоги могут отличаться от locked-итогов из-за актуальных цен.

## Поддерживаемые разделы

- `earthworks`;
- `foundation_slab`;
- `waterproofing`;
- `load_bearing_walls_lintels`;
- `floor_slab_1`;
- `floor_slab_2`;
- `flat_roof`;
- `schiedel_vent_channels`.

## Сводка Live-Pricing

| Раздел | Строк всего | Цен из price_registry | Цен из fallback | Warnings | Live total | Locked total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Земляные работы | 11 | 1 | 9 | 9 | 2586220 | 805020 |
| Фундаментная плита | 28 | 8 | 14 | 14 | 2449855 | 2538325 |
| Гидроизоляция | 8 | 4 | 2 | 2 | 49139 | 51216 |
| Несущие стены и перемычки | 32 | 4 | 24 | 24 | 2662117 | 2672103 |
| Плита перекрытия 1-го этажа | 29 | 7 | 16 | 16 | 1744464 | 1787527 |
| Плита перекрытия 2-го этажа | 26 | 4 | 12 | 12 | 700167 | 717051 |
| Плоская кровля | 31 | 2 | 15 | 15 | 2035314 | 2038872 |
| Schiedel вентканалы | 9 | 2 | 2 | 2 | 118196 | 117890 |

## Проверки Locked-Кейсов

Повторно проверены старые эталонные кейсы:

```text
earthworks:
  horoshevka_14 -> ok (76/76)
  usv_yusupovo_village -> ok (100/100)

foundation_slab -> ok
waterproofing -> ok
load_bearing_walls_lintels -> ok
floor_slab_1 -> ok (194/194)
floor_slab_2 -> ok (222/222)
flat_roof -> ok (460/460)
schiedel_vent_channels -> ok (138/138)
```

Старые `expected.json` не изменены.

## Следующий Шаг

На момент фиксации live-pricing следующим этапом планировался `box_calculator`.

После добавления рабочего PDF parser pipeline ближайший технический шаг изменён: сначала нужен `input_builder`, который соберёт `input.json` калькуляторов из проверенного `reviewed_parameters.xlsx`, и только потом `box_calculator`.

В этой контрольной точке `box_calculator`, Excel export и новые калькуляторы не создавались.
