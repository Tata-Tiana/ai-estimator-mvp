# Отчёт по обновлению термовставок фундаментной плиты

Дата: 2026-06-03

## Кратко

В `foundation_slab_calculator` добавлен новый стандарт Елены для термовставок фундаментной плиты. Старый расчёт сохранён как legacy-режим, чтобы не ломать проверенный кейс `test_foundation_slab`.

## Что было раньше

В старом кейсе термовставка считалась как термовкладыш 150 мм:

```text
pieces = ceil(thermal_insert_length_m / thermal_insert_piece_length_m)
```

Материал ЭППС 50 мм и ЭППС 100 мм добавлялся через количество элементов и размеры элемента. Эта логика оставлена только для legacy-кейса.

## Что изменила Елена

Новый стандарт:

- термовставки 50 мм и 100 мм считаются отдельно;
- работы считаются по длине в м.п. из спецификации;
- материал берётся из спецификации отдельно по 50 мм и 100 мм;
- закупочное количество материала = количество из спецификации * 1.05;
- закупочное количество округляется до кратности пачки;
- старая логика 150 мм, элемент 400 x 150 x высота и деление длины на 0.6 не используются.

## Новые поля input.json

```text
thermal_insert_mode = "standard_50_100"
thermal_insert_50_length_m
thermal_insert_100_length_m
thermal_insert_50_work_unit_price
thermal_insert_100_work_unit_price
thermal_insert_50_material_spec_qty
thermal_insert_100_material_spec_qty
thermal_insert_material_waste_coeff
thermal_insert_50_pack_multiple_qty
thermal_insert_100_pack_multiple_qty
thermal_insert_50_material_unit_price
thermal_insert_100_material_unit_price
```

Единица материала в текущем тестовом кейсе оставлена `м3`, как в существующих строках ЭППС.

## Формулы

Работы:

```text
thermal_insert_50_work_total = thermal_insert_50_length_m * thermal_insert_50_work_unit_price
thermal_insert_100_work_total = thermal_insert_100_length_m * thermal_insert_100_work_unit_price
```

Материалы:

```text
thermal_insert_50_raw_qty = thermal_insert_50_material_spec_qty * thermal_insert_material_waste_coeff
thermal_insert_50_purchase_qty = round_up_to_multiple(thermal_insert_50_raw_qty, thermal_insert_50_pack_multiple_qty)

thermal_insert_100_raw_qty = thermal_insert_100_material_spec_qty * thermal_insert_material_waste_coeff
thermal_insert_100_purchase_qty = round_up_to_multiple(thermal_insert_100_raw_qty, thermal_insert_100_pack_multiple_qty)
```

Если кратность пачки отсутствует или равна 0, калькулятор не округляет закупку молча и добавляет warning.

## Новые строки сметы

- `thermal_insert_50_installation`: "Устройство и монтаж термовставок 50 мм".
- `thermal_insert_100_installation`: "Устройство и монтаж термовставок 100 мм".
- `thermal_insert_50_material`: "Материал термовставок 50 мм".
- `thermal_insert_100_material`: "Материал термовставок 100 мм".

## Legacy-поля

Следующие поля остаются только для старого режима `thermal_insert_mode = "legacy"`:

- `thermal_insert_length_m`;
- `thermal_insert_piece_length_m`;
- `thermal_insert_piece_width_m`;
- `thermal_insert_piece_height_m`;
- `thermal_insert_piece_depth_for_work_m`;
- `thermal_insert_piece_depth_for_eps_m`;
- `thermal_insert_installation_work_unit_price`;
- `eps100_thickness_m`;
- `eps100_pack_volume_m3`;
- `eps100_unit_price`.

## Проверки

Старый legacy-кейс:

```text
internal_materials_total = 1 454 675
internal_works_total = 1 083 650
internal_section_total = 2 538 325
comparison: 229 ok / 0 mismatch
```

Новый standard-кейс:

```text
internal_materials_total = 1 465 557
internal_works_total = 1 084 000
internal_section_total = 2 549 557
comparison: 41 ok / 0 mismatch
```

`expected.json` старого кейса не изменялся.
