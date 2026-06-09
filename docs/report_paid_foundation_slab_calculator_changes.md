# Отчёт по внесению изменений в калькулятор фундаментной плиты

Дата: 2026-06-09

Проект: `ai-estimator-mvp`

Раздел сметы: "Устройство фундаментной плиты дома, террасы, крыльца"

Папка калькулятора:

```text
experiments/foundation_slab_calculator/
```

Коммиты с изменениями:

```text
cee460f Update foundation slab standards
3682da0 Finalize foundation slab standards and metal delivery allocation
```

## Цель работ

После уточнений с Еленой калькулятор фундаментной плиты был доработан под новые production-правила. Основная цель — заменить старые расчётные допущения и ручные вводы на данные из спецификации проекта и утверждённые формулы.

Работы выполнены как дополнительная доработка существующего калькулятора. Старый эталонный кейс `test_foundation_slab` сохранён как legacy и продолжает проходить без изменения старого `expected.json`.

## Что изменено

### 1. Площадь опалубки бортов фундаментной плиты

Затронутые строки сметы:

```text
Монтаж опалубки из пиломатериалов для отбортовки плиты
Фанера ламинированная 18 мм
Пиломатериал
Демонтаж опалубки
```

Что было:

```text
formwork_area_m2 = slab_formwork_perimeter_m * slab_edge_height_m
```

Что стало:

Добавлен production-режим:

```text
formwork_calc_method = spec_area
```

Формула:

```text
formwork_area_m2 = slab_side_formwork_area_m2
```

Где `slab_side_formwork_area_m2` — готовая площадь опалубки бортов из спецификации проекта.

Старые параметры `slab_formwork_perimeter_m` и `slab_edge_height_m` оставлены только для legacy-режима.

### 2. Фанера для опалубки

Что было:

Старый кейс использовал рабочую площадь листа:

```text
plywood_sheets = ceil(formwork_area_m2 / 2.25)
```

Что стало:

Закреплён production-стандарт:

```text
plywood_calc_method = actual_area_with_waste
plywood_sheet_area_m2 = 1.52 * 1.52
plywood_sheets = ceil(formwork_area_m2 * 1.05 / plywood_sheet_area_m2)
```

Правила:

- лист фанеры — `1.52 x 1.52 м`;
- запас на фанеру — `5%`;
- количество листов округляется вверх;
- размер листа и запас являются системными настройками, не ручными полями Елены.

### 3. Термовставки 50 мм и 100 мм

Затронутые строки сметы:

```text
Устройство и монтаж термовставок 50 мм
Устройство и монтаж термовставок 100 мм
Материал термовставок 50 мм
Материал термовставок 100 мм
```

Что было:

Старый расчёт термовставок был через термовкладыш 150 мм и деление длины на элементы:

```text
pieces = ceil(thermal_insert_length_m / thermal_insert_piece_length_m)
```

Что стало:

Добавлен production-режим:

```text
thermal_insert_mode = standard_50_100
```

Работы считаются отдельно по длине:

```text
thermal_insert_50_work_total = thermal_insert_50_length_m * thermal_insert_50_work_unit_price
thermal_insert_100_work_total = thermal_insert_100_length_m * thermal_insert_100_work_unit_price
```

Материал считается отдельно по спецификации:

```text
thermal_insert_50_raw_qty = thermal_insert_50_material_spec_qty * 1.05
thermal_insert_50_purchase_qty = round_up_to_multiple(thermal_insert_50_raw_qty, thermal_insert_50_pack_multiple_qty)

thermal_insert_100_raw_qty = thermal_insert_100_material_spec_qty * 1.05
thermal_insert_100_purchase_qty = round_up_to_multiple(thermal_insert_100_raw_qty, thermal_insert_100_pack_multiple_qty)
```

Старая логика 150 мм, элемент `400 x 150 x высота` и деление на `0.6` оставлены только для legacy-кейса.

### 4. Арматура фундаментной плиты

Затронутые строки сметы:

```text
Арматура А500 Ø16
Арматура А500 Ø12
Арматура А500 Ø10
Арматура А240 Ø6
Устройство армокаркаса
```

Что было:

Спецификация задавала арматуру весом в кг, а калькулятор переводил вес в длину:

```text
source_weight_kg = sum(weight_parts_kg)
base_length_m = source_weight_kg / kg_per_meter
length_with_waste_m = base_length_m * rebar_waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
```

Что стало:

Добавлен production-режим:

```text
rebar_calc_method = spec_length_m
```

Новый проектный вход — длина арматуры в м.п. по спецификации:

```text
source_length_m = source_length_m или sum(length_parts_m)
length_with_waste_m = source_length_m * rebar_waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
material_total = order_length_m * unit_price_per_m
```

Вес теперь рассчитывается автоматически:

```text
design_weight_kg = source_length_m * kg_per_meter
delivery_weight_kg = order_length_m * kg_per_meter
```

Добавлен контроль армирования:

- вес по спецификации;
- вес с запасом/закупкой;
- плотность армирования по спецификации;
- плотность армирования с запасом.

### 5. Доставка арматуры и металла

Для фундаментной плиты зафиксировано, что доставка металла не должна окончательно считаться как ручной параметр отдельного раздела.

Создан отдельный слой:

```text
experiments/box_calculator/
```

Он распределяет доставку металла по общему весу коробки дома:

```text
total_metal_delivery_trucks = ceil(total_box_metal_weight_kg / 10000)
```

Важно: в старых section totals legacy-строка доставки может сохраняться для сверки, поэтому allocation выводится как recommended-блок и не добавляется поверх старых totals.

## Legacy сохранён

Старые режимы оставлены для сверки со старой сметой:

- `formwork_calc_method = legacy_perimeter_height`;
- `plywood_calc_method = working_area`;
- `thermal_insert_mode = legacy`;
- `rebar_calc_method = legacy_weight_to_length`.

Старый кейс:

```text
experiments/foundation_slab_calculator/cases/test_foundation_slab/
```

остаётся legacy-кейсом.

Старый `expected.json` не менялся.

## Добавленные тестовые кейсы

Добавлены отдельные проверочные кейсы:

```text
experiments/foundation_slab_calculator/cases/test_foundation_slab_thermal_inserts_standard/
experiments/foundation_slab_calculator/cases/test_foundation_slab_formwork_spec_area/
experiments/foundation_slab_calculator/cases/test_foundation_slab_plywood_standard/
experiments/foundation_slab_calculator/cases/test_foundation_slab_rebar_spec_length/
experiments/box_calculator/cases/test_metal_delivery_allocation/
```

Что проверяют:

- `test_foundation_slab_thermal_inserts_standard` — отдельные термовставки 50/100 мм;
- `test_foundation_slab_formwork_spec_area` — площадь опалубки из спецификации;
- `test_foundation_slab_plywood_standard` — фанера 1.52 x 1.52 м с запасом 5%;
- `test_foundation_slab_rebar_spec_length` — арматура из м.п. спецификации;
- `test_metal_delivery_allocation` — доставка металла по общему весу коробки.

## Проверки

Перед коммитом были выполнены проверки:

```text
test_foundation_slab -> 229 ok / 0 mismatch
test_foundation_slab_thermal_inserts_standard -> 41 ok / 0 mismatch
test_foundation_slab_formwork_spec_area -> 25 ok / 0 mismatch
test_foundation_slab_plywood_standard -> 18 ok / 0 mismatch
test_foundation_slab_rebar_spec_length -> 55 ok / 0 mismatch
box_calculator test_metal_delivery_allocation -> 12 ok / 0 mismatch
py_compile -> ok
```

## Обновлённые документы

Обновлены:

```text
docs/report_foundation_slab_calculator.md
docs/standard_input_contract.md
docs/current_project_state.md
docs/assistant_handoff.md
docs/project_notes.md
docs/change_log.md
experiments/foundation_slab_calculator/README.md
```

Созданы отдельные технические отчёты:

```text
docs/report_foundation_slab_formwork_refactor.md
docs/report_thermal_inserts_refactor.md
docs/report_rebar_spec_length_refactor.md
docs/report_metal_delivery_allocation.md
```

## Итог

Калькулятор фундаментной плиты доработан под новые production-правила Елены.

Ручной ввод и старые расчётные допущения сокращены:

- площадь опалубки берётся из спецификации;
- фанера считается по фактическому размеру листа с запасом 5%;
- термовставки 50/100 мм считаются отдельно;
- арматура приходит из спецификации в м.п.;
- вес арматуры считается автоматически;
- доставка металла вынесена на уровень коробки дома.

Старый эталонный кейс сохранён и проходит без расхождений.
