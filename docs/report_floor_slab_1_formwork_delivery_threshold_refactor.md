# Paid report: refactor доставки/вывоза опалубки плиты перекрытия 1-го этажа

Дата: 2026-06-10

## Раздел

`Ж/Б монолитная плита перекрытия 1-го этажа с балками`

## Что было

В калькуляторе было ручное поле:

```text
manual_lines.formwork_delivery_trucks_override
```

Старое правило было неполным:

- `<=150 м2`: 1 привоз + 1 вывоз;
- `>180 м2`: 2 привоза + 2 вывоза;
- `150-180 м2`: manual review.

Из-за этого production-кейс мог требовать ручное количество машин в диапазоне, где после уточнения Елены уже есть однозначное правило.

## Что изменено

Добавлен режим:

```text
rates.formwork_delivery_calc_method
```

Варианты:

- `area_threshold` - production default;
- `manual_override` - ручное исключение.

Production-формула:

```text
if slab_formwork_area_m2 <= 180:
    formwork_delivery_trucks = 2
    formwork_delivery_breakdown = "1 привоз + 1 вывоз"
else:
    formwork_delivery_trucks = 4
    formwork_delivery_breakdown = "2 привоза + 2 вывоза"
```

Для ЮСВ:

```text
slab_formwork_area_m2 = 207.64
formwork_delivery_trucks = 4
```

Старый locked-кейс остаётся валидным по количеству и суммам.

## Статусы параметров

DEPRECATED / OPTIONAL_OVERRIDE:

- `manual_lines.formwork_delivery_trucks_override`.

AUTO_CALCULATED:

- `calculation_blocks.formwork.formwork_delivery_trucks`;
- `calculation_blocks.formwork.formwork_delivery_breakdown`;
- `calculation_blocks.formwork.formwork_delivery_status`.

AUTO_PROJECT / AUTO_CALCULATED SOURCE:

- `slab_formwork_area_m2` - та же площадь, которая используется для комплекта опалубки.

DEFAULT_VALUE / SYSTEM_SETTING:

- `formwork_delivery_threshold_m2 = 180`.

PRICE_DATABASE:

- `rates.formwork_delivery_rate_per_trip`.

## Result output

В `calculation_blocks.formwork` добавлены:

```text
formwork_delivery_calc_method
formwork_delivery_area_source_m2
formwork_delivery_threshold_m2
formwork_delivery_trucks
formwork_delivery_breakdown
formwork_delivery_status
```

Строка `formwork_delivery_return_manipulator` берёт:

```text
quantity = formwork_delivery_trucks
material_total = formwork_delivery_trucks * rates.formwork_delivery_rate_per_trip
```

## Тесты

Добавлен кейс:

```text
experiments/floor_slab_1_calculator/cases/test_floor_slab_1_formwork_delivery_threshold
```

Он проверяет границу:

```text
slab_formwork_area_m2 = 180
formwork_delivery_trucks = 2
```

Ветка `>180 м2` проверяется существующими кейсами с площадью `207.64 м2`, где результат остаётся `4` машины.

## TODO

- Обновить `section_schema.py`.
- Обновить `reviewed_parameters.xlsx`.
- Убрать `manual_lines.formwork_delivery_trucks_override` из production review form.
- Оставить override только в настройках исключений / debug flow.

В этой задаче не менялись `pdf_parser_pipeline`, `input_builder`, `price_registry`, `box_calculator`, другие разделы и клиентская часть.
