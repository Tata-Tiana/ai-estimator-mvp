# Отчёт: арматура несущих стен и перемычек из спецификации в м.п.

Дата: 2026-06-10

## Что было

В старом ЮСВ-кейсе:

- арматура кладки несущих стен считалась через геометрию стен, ряды армирования, нитки и коэффициент нахлёста;
- арматура перемычек считалась через `weight_kg` с переводом в м.п. через `kg_per_meter`.

Эти режимы сохранены как legacy:

```text
main_wall_rebar_calc_method = "legacy_wall_geometry"
lintel_rebar_calc_method = "legacy_weight_items"
```

## Что стало

Добавлен production-режим:

```text
main_wall_rebar_calc_method = "spec_length_items"
lintel_rebar_calc_method = "spec_length_items"
```

Арматура приходит из спецификации в м.п. и разделяется по:

- этажу;
- конструкции;
- классу стали;
- диаметру.

Формула закупки:

```text
length_with_waste_m = spec_length_m * rebar_waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
material_total = order_length_m * unit_price_per_m
delivery_weight_kg = order_length_m * kg_per_meter
```

## Классификация параметров

| Параметр | Статус | Комментарий |
| --- | --- | --- |
| `spec_length_m` | AUTO_PROJECT | Длина арматуры из спецификации, м.п. |
| `floor` | AUTO_PROJECT | Этаж из спецификации. |
| `component` | AUTO_PROJECT | `load_bearing_walls` или `lintels`. |
| `steel_class` | AUTO_PROJECT | Класс стали из спецификации. |
| `diameter_mm` | AUTO_PROJECT | Диаметр из спецификации. |
| `kg_per_meter` | MATERIAL_CATALOG | Вес 1 м.п. для контроля доставки. |
| `rod_length_m` | MATERIAL_CATALOG | Длина хлыста. |
| `unit_price_per_m` | PRICE_DATABASE / fallback input | Цена за м.п. |
| `code/name` | AUTO_CALCULATED | Генерируются из component/floor/steel/diameter. |
| `main_wall_external_length_m` | DEPRECATED / LEGACY_ONLY | Не нужен для production-арматуры. |
| `main_wall_reinforcement_rows` | DEPRECATED / LEGACY_ONLY | Не нужен для production-арматуры. |
| `main_wall_400_reinforcement_threads` | DEPRECATED / LEGACY_ONLY | Не нужен для production-арматуры. |
| `main_wall_250_reinforcement_threads` | DEPRECATED / LEGACY_ONLY | Не нужен для production-арматуры. |
| `lintel_rebar_items[*].weight_kg` | DEPRECATED / LEGACY_ONLY | Не нужен для production-арматуры перемычек. |

## Новый тест

Создан кейс:

```text
experiments/load_bearing_walls_lintels_calculator/cases/test_rebar_spec_length_by_floor_component/
```

Проверяет:

- арматуру несущих стен из `spec_length_m`;
- арматуру перемычек из `spec_length_m`;
- разделение line codes по этажу и конструкции;
- price_code `rebar_a500_d10_m`, `rebar_a500_d12_m`, `rebar_a240_d6_m`;
- контрольный вес доставки.

## Перегородки

`component = partitions` запрещён в `load_bearing_walls_lintels_calculator`.

Ошибка:

```text
partitions rebar must be calculated in partitions calculator, not in load_bearing_walls_lintels_calculator
```

## TODO

- Обновить `section_schema.py`.
- Добавить `main_wall_rebar_items` в `reviewed_parameters.xlsx`.
- Добавить `lintel_rebar_items[*].spec_length_m` в `reviewed_parameters.xlsx`.
- Добавить `partition_rebar_items` в будущий раздел перегородок.
- Научить parser брать арматуру из спецификации в м.п.
- Научить parser разделять арматуру по этажам и конструкциям.
- Подключить полноценный каталог арматуры для `kg_per_meter` и `rod_length_m`.
- Убрать legacy-поля геометрии армирования стен из формы Елены для production.
- Убрать `lintel_rebar_items[*].weight_kg` из формы Елены для production.
