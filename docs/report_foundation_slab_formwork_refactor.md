# Отчёт по обновлению площади опалубки фундаментной плиты

Дата: 2026-06-04

## Кратко

В `foundation_slab_calculator` добавлен новый стандарт Елены для площади опалубки бортов фундаментной плиты: площадь должна приходить готовым значением из спецификации.

Старый расчёт сохранён как legacy-режим, чтобы не ломать проверенный кейс `test_foundation_slab`.

## Что было раньше

Площадь опалубки считалась из периметра и высоты борта:

```text
formwork_area_m2 = slab_formwork_perimeter_m * slab_edge_height_m
```

Эта логика теперь считается legacy и нужна только для старого теста и сверки с ранее проверенным Excel.

## Почему меняем

После созвона с Еленой уточнён новый стандарт входных данных: в будущих проектах спецификация должна давать готовую площадь опалубки бортов фундаментной плиты в м2.

Это убирает лишний ручной ввод для Елены и снижает риск ошибки при выборе периметра/высоты борта.

## Что стало

Добавлен режим:

```text
formwork_calc_method = "spec_area"
```

В этом режиме:

```text
formwork_area_m2 = slab_side_formwork_area_m2
```

Старые параметры не требуются для нового standard-case:

- `slab_formwork_perimeter_m`;
- `slab_edge_height_m`;
- `slab_edge_height_strategy`.

## Какие строки сметы зависят от новой площади

От `slab_side_formwork_area_m2` считаются:

- `formwork_installation`: монтаж опалубки;
- `formwork_plywood`: фанера;
- `formwork_timber`: пиломатериал;
- `formwork_dismantling`: демонтаж опалубки.

Формулы фанеры и пиломатериала не менялись:

```text
plywood_sheets = ceil(formwork_area_m2 / plywood_sheet_working_area_m2)
timber_raw_volume_m3 = formwork_area_m2 * timber_thickness_m
```

## Новый кейс

Создан кейс:

```text
experiments/foundation_slab_calculator/cases/test_foundation_slab_formwork_spec_area/
```

В нём:

```text
slab_side_formwork_area_m2 = 24.3
```

Проверяемые значения:

```text
formwork_area_m2 = 24.3
plywood_sheets = 11
timber_raw_volume_m3 = 1.215
formwork_installation.quantity = 24.3
formwork_dismantling.quantity = 24.3
```

## Проверки

Новый кейс:

```text
comparison: 25 ok / 0 mismatch
```

Старый legacy-кейс:

```text
comparison: 229 ok / 0 mismatch
internal_section_total = 2 538 325
```

`expected.json` старого кейса не изменялся.

## TODO для следующего шага

В этой задаче `pdf_parser_pipeline` не менялся. После подтверждения стандарта нужно отдельной задачей:

- обновить `experiments/pdf_parser_pipeline/section_schema.py`;
- добавить `slab_side_formwork_area_m2` как `AUTO_PROJECT`;
- пометить `slab_formwork_perimeter_m` и `slab_edge_height_m` как legacy/deprecated для расчёта опалубки;
- пересоздать `reviewed_parameters.xlsx`, чтобы Елена видела готовую площадь опалубки, а не периметр и высоту.
