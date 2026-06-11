# Отчет: арматура плиты 2-го этажа через спецификацию и каталог

Дата: 2026-06-11

Раздел: `Ж/Б монолитная плита перекрытия 2-го этажа`

## Что изменено

Добавлен режим расчета арматуры:

```text
rebar_calc_method =
  legacy_weight_kg
  spec_length_items
```

Если параметр отсутствует, используется `legacy_weight_kg`, чтобы старый locked-кейс ЮСВ продолжал
работать без изменения expected.

## Было

В старом ЮСВ-режиме каждая позиция арматуры приходила в input с весом и всеми техническими
метаданными:

```text
code
name
source_weight_kg
kg_per_meter
rod_length_m
unit_price_per_m
```

Расчет:

```text
raw_length_m = source_weight_kg / kg_per_meter
length_with_waste_m = raw_length_m * waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
material_total_raw = order_length_m * unit_price_per_m
```

## Стало

В production-режиме `spec_length_items` из спецификации приходят проектные поля:

```text
steel_class
diameter_mm
spec_length_m
```

`code`, `name`, `kg_per_meter`, `rod_length_m` и `price_code` берутся из локального каталога по
паре `steel_class + diameter_mm`.

Production-расчет:

```text
base_length_m = spec_length_m
length_with_waste_m = spec_length_m * waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
order_weight_kg = order_length_m * kg_per_meter
material_total_raw = order_length_m * unit_price_per_m
```

## Каталог

Минимальный локальный каталог для текущего раздела:

- A500 D16: `kg_per_meter = 1.58`, `rod_length_m = 11.7`, `price_code = rebar_a500_d16_m`;
- A500 D12: `kg_per_meter = 0.888`, `rod_length_m = 11.7`, `price_code = rebar_a500_d12_m`;
- A500 D10: `kg_per_meter = 0.617`, `rod_length_m = 11.7`, `price_code = rebar_a500_d10_m`.

Если позиция не найдена в каталоге, калькулятор падает с ошибкой:

```text
Unsupported rebar catalog item: steel_class=..., diameter_mm=...
```

## Статусы параметров

AUTO_PROJECT:

- `rebar_items[*].steel_class`;
- `rebar_items[*].diameter_mm`;
- `rebar_items[*].spec_length_m`.

MATERIAL_CATALOG:

- `rebar_items[*].code`;
- `rebar_items[*].name`;
- `rebar_items[*].kg_per_meter`;
- `rebar_items[*].rod_length_m`;
- `rebar_items[*].price_code`.

PRICE_DATABASE / LIVE_PRICING / INPUT:

- `rebar_items[*].unit_price_per_m`.

AUTO_CALCULATED:

- `length_with_waste_m`;
- `raw_rods`;
- `rods`;
- `order_length_m`;
- `order_weight_kg`;
- `material_total_raw`;
- `total_rebar_order_length_m`;
- `total_rebar_order_weight_kg`.

DEPRECATED / LEGACY_ONLY:

- `rebar_items[*].source_weight_kg` как обязательный production-источник;
- `rebar_items[*].code` как input-поле;
- `rebar_items[*].name` как input-поле;
- `rebar_items[*].kg_per_meter` как input-поле;
- `rebar_items[*].rod_length_m` как input-поле.

## Новый тест

Создан кейс:

```text
experiments/floor_slab_2_calculator/cases/test_floor_slab_2_rebar_spec_lengths/
```

Он проверяет, что production input не передает `code`, `name`, `kg_per_meter`, `rod_length_m` и
`price_code`, а калькулятор подтягивает их из каталога.

Контрольные значения:

- D16: `spec_length_m = 90.126582`, `order_length_m = 105.3`, `order_weight_kg = 166.374`;
- D12: `spec_length_m = 24.774775`, `order_length_m = 35.1`, `order_weight_kg = 31.1688`;
- D10: `spec_length_m = 2551.166937`, `order_length_m = 2679.3`, `order_weight_kg = 1653.1281`;
- `total_rebar_order_length_m = 2819.7`;
- `total_rebar_order_weight_kg = 1850.6709`.

## TODO

- обновить `section_schema.py`;
- обновить `reviewed_parameters.xlsx`;
- научить parser брать арматуру плиты 2-го этажа из спецификации в м.п.;
- подключить общий material catalog вместо локального словаря;
- подключить полноценный price registry для `unit_price_per_m`;
- убрать `source_weight_kg`, `code`, `name`, `kg_per_meter`, `rod_length_m` из production-form.
