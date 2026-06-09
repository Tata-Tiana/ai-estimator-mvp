# Рефактор смен экскаватора в земляных работах

Дата: 2026-06-09

## Что было

В старой логике строка "Механизированная разработка грунта, Экскаватор JCB" брала готовое количество смен:

```text
excavator_shifts
```

Это значение использовалось как количество строки сметы:

```text
material_total = excavator_shifts * excavator_material_unit_price
work_total = excavator_shifts * excavator_work_unit_price
```

## Что стало production-стандартом

Добавлен режим:

```text
excavator_shifts_calc_method = standard_volume_productivity
```

В нём количество смен считается от объёма механизированной выемки:

```text
machine_excavation_volume_m3 = pit_area_m2 * pit_excavation_depth_m
excavator_shifts = ceil(machine_excavation_volume_m3 / excavator_productivity_m3_per_shift)
```

По методике Елены:

```text
excavator_productivity_m3_per_shift = 80
```

## Важное разделение глубин

`pit_excavation_depth_m` — глубина механизированной выемки котлована экскаватором.

`manual_refinement_depth_m = 0.08` — ручная доработка дна котлована.

Эти параметры нельзя смешивать.

## Источники параметров

Project-параметры:

- `pit_area_m2` — площадь котлована из спецификации/чертежа;
- `pit_excavation_depth_m` — глубина механизированной выемки из спецификации/чертежа.

Системные настройки:

- `excavator_productivity_m3_per_shift = 80`.

Legacy/debug:

- `excavator_shifts` — прямое количество смен для старых кейсов и сверки со старой сметой.

## Новый тест

Создан кейс:

```text
experiments/earthworks_calculator/cases/test_excavator_shifts_standard/
```

Проверочный расчёт:

```text
machine_excavation_volume_m3 = 330 * 0.6 = 198
excavator_shifts = ceil(198 / 80) = 3
materials = 3 * 26000 = 78000
works = 3 * 3500 = 10500
line_total = 88500
```

## Legacy

Кейс `usv_yusupovo_village` явно использует:

```text
excavator_shifts_calc_method = legacy_manual_shifts
```

Старый `expected.json` не менялся.

## TODO

- Обновить `section_schema.py`.
- Добавить `pit_excavation_depth_m` в `reviewed_parameters.xlsx`.
- Научить parser искать глубину механизированной выемки котлована в спецификации/чертежах.
- Убрать `excavator_shifts` из формы Елены как ручной ввод для production-потока.
- Показывать Елене расчёт смен экскаватора как контроль.
