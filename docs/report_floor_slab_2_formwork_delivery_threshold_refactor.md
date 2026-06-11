# Отчет: автоматизация доставки/вывоза опалубки плиты 2-го этажа

Дата: 2026-06-11

Раздел: `Ж/Б монолитная плита перекрытия 2-го этажа`

## Что изменено

Добавлен режим расчета:

```text
formwork_delivery_calc_method =
  area_threshold
  manual_override
```

Production default:

```text
formwork_delivery_calc_method = "area_threshold"
```

## Production-правило

Источник площади:

```text
main_formwork_area_m2
```

Правило:

```text
main_formwork_area_m2 <= 180 м2 -> 2 рейса: 1 привоз + 1 вывоз
main_formwork_area_m2 > 180 м2  -> 4 рейса: 2 привоза + 2 вывоза
```

Для ЮСВ:

```text
main_formwork_area_m2 = 81.9
formwork_delivery_trips = 2
```

## Строка сметы

Строка:

```text
formwork_delivery_manipulator
```

использует рассчитанное количество:

```text
quantity = formwork_delivery_trips
line_total = formwork_delivery_trips * formwork_delivery_unit_price
```

Примечание к строке обновлено:

```text
До 180 м2 включительно: 1 привоз + 1 вывоз = 2 рейса; более 180 м2: 2 привоза + 2 вывоза = 4 рейса.
```

## Статусы параметров

AUTO_CALCULATED:

- `formwork_delivery_trips`;
- `formwork_delivery_breakdown`;
- `formwork_delivery_status`.

AUTO_PROJECT:

- `main_formwork_area_m2`.

DEFAULT_VALUE / SYSTEM_SETTING:

- `formwork_delivery_threshold_m2 = 180`.

DEPRECATED / OPTIONAL_OVERRIDE:

- `manual_lines.formwork_delivery_trips_override`;
- ручной `formwork_delivery_trips` как обязательный input.

PRICE_DATABASE / FALLBACK_INPUT:

- `formwork_delivery_unit_price`.

## Legacy и override

Для исключений доступен режим:

```text
formwork_delivery_calc_method = "manual_override"
manual_lines.formwork_delivery_trips_override = ...
```

Если режим `area_threshold`, ручной override не используется, даже если случайно передан.

## Новые тесты

Добавлены кейсы:

```text
experiments/floor_slab_2_calculator/cases/test_floor_slab_2_formwork_delivery_threshold_180/
experiments/floor_slab_2_calculator/cases/test_floor_slab_2_formwork_delivery_threshold_above_180/
```

Проверки:

- `main_formwork_area_m2 = 180` -> `formwork_delivery_trips = 2`;
- `main_formwork_area_m2 = 180.01` -> `formwork_delivery_trips = 4`.

## TODO

- обновить `section_schema.py`;
- обновить `reviewed_parameters.xlsx`;
- убрать ручной `formwork_delivery_trips` из production-формы Елены;
- оставить `manual_lines.formwork_delivery_trips_override` только как исключение;
- научить parser/production flow передавать `main_formwork_area_m2` из спецификации.
