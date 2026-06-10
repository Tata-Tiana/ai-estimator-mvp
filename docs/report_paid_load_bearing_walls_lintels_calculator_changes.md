# Отчёт по доработке калькулятора несущих стен и перемычек

Дата: 2026-06-10

Раздел: `experiments/load_bearing_walls_lintels_calculator`

## Цель работ

Калькулятор раздела "Внешние и внутренние несущие стены, перемычки" был переведён с набора ручных и case-specific параметров ЮСВ на production-стандарты, согласованные с Еленой.

Главный принцип доработки:

- старый ЮСВ-кейс сохранён как legacy для сверки со старой Excel-сметой;
- новые production-режимы используют готовые проектные параметры из спецификации;
- параметры, которые являются системными правилами или defaults, не должны спрашиваться у Елены в каждом проекте;
- перегородки не смешиваются с несущими стенами.

## Что изменено в калькуляторе

### Подмости и леса

Было:

- `scaffolding_setup_quantity` задавался напрямую;
- `scaffolding_timber_quantity_m3` задавался напрямую.

Стало:

- добавлен режим `scaffolding_calc_method`;
- legacy: `legacy_direct_quantity`;
- production: `floors_based`;
- формулы:

```text
scaffolding_setup_quantity = floors_count * scaffolding_setup_units_per_floor
scaffolding_timber_quantity_m3 = floors_count * scaffolding_timber_m3_per_floor
```

Production defaults:

- `scaffolding_setup_units_per_floor = 1`;
- `scaffolding_timber_m3_per_floor = 1`.

### Отсечная гидроизоляция под несущие стены

Было:

```text
cutoff_waterproofing_area_m2 =
    sum(cutoff_waterproofing_wall_400_lengths_m) * wall_400_thickness_m
  + sum(cutoff_waterproofing_wall_250_lengths_m) * wall_250_thickness_m
```

Стало:

- добавлен режим `cutoff_waterproofing_calc_method`;
- legacy: `legacy_lengths_by_wall_thickness`;
- production: `spec_area`;
- production-параметр:

```text
cutoff_waterproofing_load_bearing_walls_area_m2
```

Площадь перегородок в этот калькулятор не включается.

### Перемычки: общая длина

Было:

```text
lintel_total_length_m = sum(length_m * count)
```

Стало:

- добавлен режим `lintel_length_calc_method`;
- legacy: `legacy_length_count_items`;
- production: `spec_total_length`;
- production-параметр:

```text
lintel_total_length_m
```

Резка U-блока сохранена в штуках:

```text
u_block_quantity = lintel_total_length_m / gas_block_length_m
```

Единица строки `u_block_lintel_cutting` не менялась.

### Перемычки: сечение U-блока

Закреплены системные defaults:

```text
lintel_section_width_m = 0.125
lintel_section_height_m = 0.125
```

В production эти поля не являются ручными параметрами Елены.

### Перемычки: бетон

Было:

```text
lintel_raw_concrete_volume_m3 =
    lintel_total_length_m * lintel_section_width_m * lintel_section_height_m
lintel_required_concrete_volume_m3 =
    lintel_raw_concrete_volume_m3 * concrete_waste_coeff
```

Стало:

- добавлен режим `lintel_concrete_calc_method`;
- legacy: `legacy_length_section`;
- production: `spec_volume`;
- production-параметр:

```text
lintel_concrete_spec_volume_m3
```

Закупочный объём:

```text
lintel_concrete_order_volume_m3 =
    max(1, ceil(lintel_concrete_spec_volume_m3))
```

`lintel_concrete_min_order_volume_m3 = 1` закреплён как default закупочного правила.

### Арматура несущих стен и перемычек

Было:

- арматура кладки считалась через геометрию стен, ряды, нитки и коэффициент нахлёста;
- арматура перемычек считалась через `weight_kg` с переводом в метры.

Стало:

- добавлен режим `main_wall_rebar_calc_method`;
- добавлен режим `lintel_rebar_calc_method`;
- legacy:
  - `legacy_wall_geometry`;
  - `legacy_weight_items`;
- production:
  - `spec_length_items`.

Production-модель арматуры:

```text
floor
component
steel_class
diameter_mm
spec_length_m
kg_per_meter
rod_length_m
unit_price_per_m
```

Закупка:

```text
length_with_waste_m = spec_length_m * rebar_waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
material_total = order_length_m * unit_price_per_m
delivery_weight_kg = order_length_m * kg_per_meter
```

Строки арматуры в production разделяются по этажу, конструкции, классу стали и диаметру.

Перегородки защищены validation:

```text
partitions rebar must be calculated in partitions calculator, not in load_bearing_walls_lintels_calculator
```

### Смены крана для несущих стен

Было:

- `main_walls_crane_shifts` задавался вручную.

Стало:

- добавлен режим `main_walls_crane_calc_method`;
- legacy: `legacy_manual_shifts`;
- production: `delivery_trucks_threshold`;
- источник: рассчитанное количество доставок блоков `gas_block_delivery_trucks`.

Формула:

```text
if gas_block_delivery_trucks <= 3:
    main_walls_crane_shifts = 1
else:
    main_walls_crane_shifts = 2
```

### Этажность и блок 2-го этажа

Было:

- старые поля `second_light_*`;
- в ЮСВ поле second_light фактически использовалось как кладка 2-го этажа.

Стало:

- добавлен `floors_count`;
- допустимые значения только `1` или `2`;
- `floors_count = 3` запрещён:

```text
floors_count must be 1 or 2. Three-storey houses are out of MVP scope.
```

- добавлен режим `upper_floor_calc_method`;
- legacy: `legacy_second_light_addon`;
- production: `floor_2_spec_volume`;
- production-блок:

```text
floor_2_load_bearing_walls
```

Если `floors_count = 1`, блок второго этажа выключен.
Если `floors_count = 2`, блок включён, а объём кладки берётся из:

```text
floor_2_masonry_volume_m3
```

Термин `second_light` в production-отчёте не используется.

### Парапет

Было:

- `parapet_enabled` был ручным toggle.

Стало:

- добавлен режим `parapet_calc_method`;
- legacy: `legacy_manual_toggle`;
- production: `flat_roof_spec_volume`;
- production включение:

```text
parapet_enabled_calculated =
    flat_roof_enabled and parapet_masonry_volume_m3 > 0
```

`parapet_masonry_volume_m3` относится к спецификации кровли.

### Обкладка вентканалов

Было:

- production-площадь уже фактически считалась от объёма и толщины;
- но legacy-поля сегментов и рядов оставались обязательными:
  - `vent_chimney_segment_lengths_m`;
  - `vent_chimney_rows`;
  - `block_height_m`.

Стало:

- добавлен режим `vent_chimney_geometry_calc_method`;
- legacy: `legacy_segments_rows`;
- production: `spec_volume_thickness`;
- production-параметр:

```text
vent_chimney_gas_block_spec_volume_m3
```

- default:

```text
vent_chimney_block_thickness_m = 0.15
block_height_m = 0.25
```

Production-формула:

```text
vent_chimney_cladding_area_m2 =
    vent_chimney_gas_block_spec_volume_m3 / 0.15
```

Legacy geometry оставлена только как контроль:

```text
vent_total_length = sum(length_m * count)
vent_height = block_height_m * vent_chimney_rows
vent_geometry_volume_m3 =
    vent_total_length * vent_height * vent_chimney_block_thickness_m
```

## Новые test-cases

Созданы отдельные кейсы для production-режимов и validation:

- `test_scaffolding_floors_based`;
- `test_cutoff_waterproofing_spec_area`;
- `test_lintel_spec_total_length`;
- `test_lintel_concrete_spec_volume`;
- `test_lintel_concrete_spec_volume_min_order`;
- `test_main_walls_crane_from_delivery_trucks`;
- `test_main_walls_crane_from_delivery_trucks_four`;
- `test_floor_1_without_floor_2`;
- `test_floor_2_load_bearing_walls_spec_volume`;
- `test_flat_roof_parapet_vent_channels`;
- `test_vent_chimney_spec_volume_thickness`;
- `test_rebar_spec_length_by_floor_component`;
- `test_floors_count_three_rejected`;
- `test_rebar_partitions_rejected`.

Старый кейс `test_load_bearing_walls_lintels` оставлен как legacy для сверки ЮСВ.
Live-кейс `test_load_bearing_walls_lintels_live_prices` оставлен совместимым с legacy-полями.

## Документация

Обновлены:

- `experiments/load_bearing_walls_lintels_calculator/README.md`;
- `docs/report_load_bearing_walls_lintels_calculator.md`;
- `experiments/load_bearing_walls_lintels_calculator/cases/test_load_bearing_walls_lintels/notes.md`.

Созданы отдельные отчёты:

- `docs/report_load_bearing_walls_scaffolding_refactor.md`;
- `docs/report_load_bearing_walls_cutoff_waterproofing_refactor.md`;
- `docs/report_load_bearing_walls_lintels_total_length_refactor.md`;
- `docs/report_load_bearing_walls_rebar_spec_length_refactor.md`;
- `docs/report_load_bearing_walls_crane_refactor.md`;
- `docs/report_load_bearing_walls_floor_2_refactor.md`;
- `docs/report_partitions_cutoff_waterproofing_refactor.md`;
- `docs/report_partitions_rebar_spec_length_refactor.md`.

## Проверки

Запущены позитивные кейсы раздела:

- `test_load_bearing_walls_lintels`;
- `test_load_bearing_walls_lintels_live_prices`;
- `test_scaffolding_floors_based`;
- `test_cutoff_waterproofing_spec_area`;
- `test_lintel_spec_total_length`;
- `test_lintel_concrete_spec_volume`;
- `test_lintel_concrete_spec_volume_min_order`;
- `test_main_walls_crane_from_delivery_trucks`;
- `test_main_walls_crane_from_delivery_trucks_four`;
- `test_floor_1_without_floor_2`;
- `test_floor_2_load_bearing_walls_spec_volume`;
- `test_flat_roof_parapet_vent_channels`;
- `test_vent_chimney_spec_volume_thickness`;
- `test_rebar_spec_length_by_floor_component`.

Запущены negative-проверки:

- `test_floors_count_three_rejected` падает с ожидаемой ошибкой про 1 или 2 этажа;
- `test_rebar_partitions_rejected` падает с ожидаемой ошибкой про отдельный калькулятор перегородок.

Дополнительно выполнено:

```bash
../.venv/bin/python3 -m py_compile \
experiments/load_bearing_walls_lintels_calculator/load_bearing_walls_lintels_calculator.py \
experiments/load_bearing_walls_lintels_calculator/run_load_bearing_walls_lintels_calc.py
```

Проверка mismatch:

```bash
rg -n '"status": "mismatch"' experiments/load_bearing_walls_lintels_calculator/output
```

Результат: mismatch не найден.

Старый `expected.json` ЮСВ не изменён.

## Что осталось на следующие этапы

Не делалось в рамках этой пачки:

- `pdf_parser_pipeline`;
- `input_builder`;
- `price_registry`;
- полноценный калькулятор перегородок;
- общий box-orchestrator;
- поддержка 3+ этажей;
- универсальный `floors[]` engine.

Следующие TODO:

- обновить `section_schema.py`;
- обновить `reviewed_parameters.xlsx`;
- научить parser брать production-поля из спецификации:
  - площади отсечной гидроизоляции;
  - общую длину перемычек;
  - объём бетона перемычек;
  - арматуру в м.п. по этажам и конструкциям;
  - количество этажей;
  - объём кладки 2-го этажа;
  - объём парапета;
  - объём кладки вентканалов;
- вынести перегородки в отдельный калькулятор/раздел и не смешивать их с несущими стенами.
