# Отчёт по внесению изменений в калькулятор гидроизоляции

Дата: 2026-06-09

Проект: `ai-estimator-mvp`

Раздел сметы: "Гидроизоляция фундаментной плиты"

Папка калькулятора:

```text
experiments/waterproofing_calculator/
```

## Цель работ

После уточнений с Еленой калькулятор гидроизоляции был доработан под новый production-стандарт: ключевые площади должны приходить из спецификации проекта, а не рассчитываться через старую геометрию периметра и высоты борта.

Работы выполнены как дополнительная доработка существующего калькулятора. Старый эталонный кейс сохранён как legacy и продолжает проходить без изменения старого `expected.json`.

## Что изменено

### 1. Площадь гидроизоляции

Затронутые строки сметы:

```text
Гидроизоляция фундаментной плиты битумной мастикой в 2 слоя
Праймер битумный AquaMast, 18 л
Мастика гидроизоляционная битумная для фундаментов AquaMast, 18 кг
```

Что было:

```text
waterproofing_area_m2 = slab_formwork_perimeter_m * slab_edge_height_m
```

В старом кейсе:

```text
81 * 0.3 = 24.3 м2
```

Что стало:

Добавлен production-режим:

```text
waterproofing_area_calc_method = spec_area
```

Формула:

```text
waterproofing_area_m2 = готовая площадь из спецификации проекта
```

По методике Елены эта площадь равна площади опалубки фундаментной плиты.

Старые параметры:

```text
slab_formwork_perimeter_m
slab_edge_height_m
```

оставлены только для legacy-режима и больше не обязательны для production-гидроизоляции.

### 2. Праймер и мастика

Формулы остались прежними, но теперь используют готовую площадь `waterproofing_area_m2`:

```text
primer_required_liters = waterproofing_area_m2 * primer_consumption_l_per_m2
primer_units = ceil(primer_required_liters / primer_canister_volume_l)

mastic_required_kg = waterproofing_area_m2 * mastic_consumption_kg_per_m2_per_layer * mastic_layers
mastic_units = ceil(mastic_required_kg / mastic_bucket_weight_kg)
```

Для тестовой площади `24.3 м2`:

```text
primer_required_liters = 7.29
primer_units = 1
mastic_required_kg = 48.6
mastic_units = 3
```

### 3. ЭППС 100 мм торец

Затронутые строки сметы:

```text
Утепление стен плиты ЭППС 100 мм
Пеноплэкс ГЕО 100 мм
Клей-пена для ЭППС
```

Уточнено, что участки без утепления больше не нужны для production-расчёта.

Основная production-формула:

```text
eps100_wall_insulation_area_m2 = eps100_wall_volume_m3 / eps100_wall_thickness_m
```

Где:

```text
eps100_wall_thickness_m = 0.1
```

Для тестового кейса:

```text
1.75 / 0.1 = 17.5 м2
```

### 4. Геометрическая проверка по участкам без утепления

Что было:

```text
insulated_edge_length_m = slab_formwork_perimeter_m - sum(non_insulated_edge_lengths_m)
eps100_wall_geometry_check_area_m2 = insulated_edge_length_m * slab_edge_height_m
```

Что стало:

`non_insulated_edge_lengths_m` больше не обязателен и не нужен для production.

Геометрическая проверка стала optional и включается только если есть все данные:

- `slab_formwork_perimeter_m`;
- `slab_edge_height_m`;
- непустой `non_insulated_edge_lengths_m`.

В result добавлен флаг:

```text
eps100_wall_geometry_check_enabled
```

Для production-кейса:

```text
eps100_wall_geometry_check_enabled = false
```

Для старого legacy-кейса проверка остаётся:

```text
(81 - 8.2 - 2 - 5.3) * 0.3 = 19.65 м2
```

## Legacy сохранён

Старый кейс:

```text
experiments/waterproofing_calculator/cases/test_waterproofing_foundation_slab/
```

использует:

```text
waterproofing_area_calc_method = legacy_perimeter_height
```

В нём оставлены:

- `slab_formwork_perimeter_m = 81`;
- `slab_edge_height_m = 0.3`;
- `non_insulated_edge_lengths_m = [8.2, 2, 5.3]`.

Старый `expected.json` не менялся.

## Добавленные тестовые кейсы

Добавлен production-кейс:

```text
experiments/waterproofing_calculator/cases/test_waterproofing_spec_area/
```

Что проверяет:

- площадь гидроизоляции берётся из `waterproofing_area_m2`;
- старые `slab_formwork_perimeter_m` и `slab_edge_height_m` не требуются;
- `non_insulated_edge_lengths_m` не требуется;
- ЭППС 100 мм торец считается от объёма спецификации;
- геометрическая проверка выключается, если данных нет.

## Проверки

Выполнены проверки:

```text
test_waterproofing_foundation_slab -> ok
test_waterproofing_spec_area -> ok
test_waterproofing_foundation_slab_live_prices -> ok
py_compile -> ok
```

Для production-кейса проверены значения:

```text
waterproofing_area_calc_method = spec_area
waterproofing_area_m2 = 24.3
primer_required_liters = 7.29
primer_units = 1
mastic_required_kg = 48.6
mastic_units = 3
eps100_wall_insulation_area_m2 = 17.5
eps100_wall_geometry_check_enabled = false
internal_section_total = 51216
```

## Обновлённые документы

Обновлены:

```text
docs/report_waterproofing_calculator.md
experiments/waterproofing_calculator/README.md
experiments/waterproofing_calculator/cases/test_waterproofing_foundation_slab/notes.md
```

Созданы отдельные технические отчёты:

```text
docs/report_waterproofing_spec_area_refactor.md
docs/report_waterproofing_eps100_refactor.md
```

## Итог

Калькулятор гидроизоляции доработан под новый production-стандарт Елены.

Ручной ввод и старые геометрические зависимости сокращены:

- площадь гидроизоляции берётся готовым значением из спецификации;
- периметр и высота борта больше не нужны для production-площади гидроизоляции;
- участки без утепления больше не нужны для production-расчёта ЭППС;
- площадь работ по ЭППС считается от объёма ЭППС из спецификации;
- старая геометрическая проверка сохранена только для legacy/debug.

Старый эталонный кейс сохранён и проходит без расхождений.
