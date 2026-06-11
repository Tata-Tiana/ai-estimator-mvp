# Отчёт по внесению изменений в калькулятор плиты перекрытия 2-го этажа

Дата: 2026-06-11

Проект: `ai-estimator-mvp`

Раздел сметы: `Ж/Б монолитная плита перекрытия 2-го этажа`

Папка калькулятора:

```text
experiments/floor_slab_2_calculator/
```

## Цель работ

Калькулятор плиты перекрытия 2-го этажа был доработан под production-правила, уточнённые с Еленой. Главная цель — убрать обязательную зависимость от прямоугольной геометрии, ручных организационных параметров и лишних input-полей арматуры, оставив старый locked-кейс ЮСВ как legacy для сверки с исходной Excel-сметой.

Работы выполнены как дополнительная оплачиваемая доработка существующего калькулятора.

## Общий принцип изменений

- старый кейс `test_floor_slab_2` сохранён как legacy/locked;
- старый `expected.json` не менялся;
- production-кейсы вынесены отдельно;
- новые production-режимы используют данные из спецификации проекта, локальный material catalog или системные defaults;
- box-level задачи только задокументированы и не реализовывались в этом разделе.

## Что изменено

### 1. Геометрия и площадь опалубки из спецификации

Что было:

- площадь плиты считалась как `slab_length_m * slab_width_m`;
- периметр считался как `2 * (slab_length_m + slab_width_m)`;
- площадь комплекта опалубки приравнивалась к площади плиты.

Что стало:

Добавлен и расширен режим:

```text
formwork_area_calc_method
```

Варианты:

- `legacy_dimensions` — старый ЮСВ-режим;
- `spec_formwork_area` — production.

Production использует готовые значения из спецификации:

```text
main_formwork_area_m2
edge_formwork_area_m2
beams_formwork_area_m2
slab_edge_perimeter_m
```

Формулы:

```text
slab_formwork_area_m2 = main_formwork_area_m2
edge_and_beam_formwork_area_m2 =
    edge_formwork_area_m2 + beams_formwork_area_m2
```

Для текущей плиты 2-го этажа балок нет:

```text
beams_formwork_area_m2 = 0
```

Строка "Комплект опалубки" использует `main_formwork_area_m2`. Торцевая опалубка, фанера и пиломатериал используют `edge_formwork_area_m2 + beams_formwork_area_m2`.

Старые формулы через длину, ширину, периметр и высоту оставлены только как geometry/control check:

```text
calculated_slab_area_m2
calculated_slab_edge_perimeter_m
calculated_edge_formwork_area_m2
edge_formwork_area_delta_m2
```

### 2. Доставка/вывоз опалубки

Что было:

- `formwork_delivery_trips` считался ручным организационным параметром.

Что стало:

Добавлен режим:

```text
formwork_delivery_calc_method
```

Варианты:

- `area_threshold` — production default;
- `manual_override` — исключение.

Production-формула:

```text
if main_formwork_area_m2 <= 180:
    formwork_delivery_trips = 2
else:
    formwork_delivery_trips = 4
```

Расшифровка:

- до `180 м2` включительно: 1 привоз + 1 вывоз = 2 рейса;
- более `180 м2`: 2 привоза + 2 вывоза = 4 рейса.

Ручной `formwork_delivery_trips` больше не является обязательным production-параметром и используется только как optional override.

### 3. Арматура через спецификацию и каталог

Что было:

Арматура считалась от веса:

```text
raw_length_m = source_weight_kg / kg_per_meter
length_with_waste_m = raw_length_m * waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
```

В input по каждой позиции передавались технические поля:

```text
code
name
kg_per_meter
rod_length_m
price_code
```

Что стало:

Добавлен режим:

```text
rebar_calc_method
```

Варианты:

- `legacy_weight_kg` — старый ЮСВ-режим;
- `spec_length_items` — production.

Production item:

```text
steel_class
diameter_mm
spec_length_m
unit_price_per_m
```

`code`, `name`, `kg_per_meter`, `rod_length_m`, `price_code` берутся из локального каталога по паре `steel_class + diameter_mm`.

Production-формула:

```text
base_length_m = spec_length_m
length_with_waste_m = spec_length_m * waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
order_weight_kg = order_length_m * kg_per_meter
material_total = order_length_m * unit_price_per_m
```

В calculation blocks добавлены:

```text
total_rebar_order_length_m
total_rebar_order_weight_kg
```

### 4. Высота утепления торца

Что было:

В расчетах использовалось:

```text
edge_insulation_height_m = 0.18
```

Ранее это сопровождалось warning, потому что в названии раздела фигурировало 200 мм.

Что уточнила Елена:

Правильная высота утепления торца — 180 мм. Ошибка была только в названии раздела.

Что стало:

`edge_insulation_height_m` закреплен как production-параметр из спецификации:

```text
edge_insulation_height_m = 0.18
edge_insulation_height_source = specification
```

Расчет не изменился:

```text
edge_insulation_area_m2 =
    slab_edge_perimeter_m * edge_insulation_height_m

eps100_required_volume_without_waste_m3 =
    edge_insulation_area_m2 * eps100_thickness_m
```

Для ЮСВ:

```text
36.2 * 0.18 = 6.516 м2
6.516 * 0.1 = 0.6516 м3
```

Работа по утеплению торца остается в м.п.:

```text
edge_insulation_work.quantity = slab_edge_perimeter_m = 36.2
```

Старый warning заменен на пояснение, что `0.18 м` подтверждено спецификацией, а `200 мм` в названии раздела считается ошибкой названия.

## Новые кейсы

Добавлены production-кейсы:

```text
test_floor_slab_2_spec_formwork_area
test_floor_slab_2_formwork_delivery_threshold_180
test_floor_slab_2_formwork_delivery_threshold_above_180
test_floor_slab_2_rebar_spec_lengths
```

Что они проверяют:

- площадь комплекта опалубки из `main_formwork_area_m2`;
- торцевую опалубку, фанеру и пиломатериал от `edge_formwork_area_m2 + beams_formwork_area_m2`;
- доставку/вывоз опалубки по порогу `180 м2`;
- арматуру от `spec_length_m` с каталогом по классу стали и диаметру;
- высоту утепления торца `edge_insulation_height_m = 0.18`;
- неизменность старого locked-кейса ЮСВ.

## Документация

Обновлены:

```text
experiments/floor_slab_2_calculator/README.md
docs/report_floor_slab_2_calculator.md
docs/report_floor_slab_2_spec_formwork_area_refactor.md
```

Созданы технические отчёты:

```text
docs/report_floor_slab_2_spec_formwork_areas_refactor.md
docs/report_floor_slab_2_formwork_delivery_threshold_refactor.md
docs/report_floor_slab_2_rebar_spec_lengths_refactor.md
docs/report_floor_slab_2_edge_insulation_height_refactor.md
```

## Что не входило в работы

В рамках этой доработки не менялись:

- `pdf_parser_pipeline`;
- `input_builder`;
- `price_registry`;
- `box_calculator`;
- плита перекрытия 1-го этажа;
- другие разделы;
- клиентская часть;
- Excel-структура.

## Результат

Калькулятор плиты 2-го этажа переведён на production-источники из спецификации по опалубке, доставке, арматуре и утеплению торца. Старый locked-кейс ЮСВ сохранён и продолжает проходить без изменения старого `expected.json`.
