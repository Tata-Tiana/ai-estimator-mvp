# Отчёт по внесению изменений в калькулятор земляных работ

Дата: 2026-06-09

Проект: `ai-estimator-mvp`

Раздел сметы: "Земляные работы"

Папка калькулятора:

```text
experiments/earthworks_calculator/
```

Коммит с изменениями:

```text
d9e1c3a Update earthworks production standards
```

## Цель работ

После уточнений с Еленой калькулятор земляных работ был доработан под новые production-правила, чтобы часть параметров больше не вводилась вручную, а считалась по спецификации проекта и утверждённым формулам.

Работы выполнены как дополнительная доработка существующего калькулятора, без изменения старых эталонных `expected.json`.

## Что изменено

### 1. Смены экскаватора JCB

Затронута строка сметы:

```text
Механизированная разработка грунта, Экскаватор JCB
```

Что было:

```text
excavator_shifts
```

Количество смен задавалось готовым числом.

Что стало:

Добавлен production-режим:

```text
excavator_shifts_calc_method = standard_volume_productivity
```

Формула:

```text
machine_excavation_volume_m3 = pit_area_m2 * pit_excavation_depth_m
excavator_shifts = ceil(machine_excavation_volume_m3 / 80)
```

Где:

- `pit_area_m2` — площадь котлована из проекта;
- `pit_excavation_depth_m` — глубина механизированной выемки котлована из проекта;
- `80 м3/смена` — системная производительность экскаватора по методике Елены.

Важно: `pit_excavation_depth_m` не равен `manual_refinement_depth_m`. `manual_refinement_depth_m = 0.08` используется только для ручной доработки дна котлована.

### 2. Ручная разработка грунта

Затронута строка сметы:

```text
Разработка грунта вручную
```

Что было:

Старый кейс мог использовать ручной override:

```text
manual_excavation_quantity_for_estimate_m3
```

Что стало:

Добавлен production-режим:

```text
manual_excavation_calc_method = standard_routes
```

Формула:

```text
manual_pit_volume_m3 = pit_area_m2 * 0.08
manual_excavation_total_m3 = manual_pit_volume_m3 + trench_volume_total_m3
```

Приоритет для `trench_volume_total_m3`:

1. Если в спецификации проекта есть готовый `trench_volume_m3`, используется он.
2. Если готового объёма нет, объём траншей считается по трассам:

```text
trench_volume_total_m3 = sum(route_length_m * route_depth_m * 0.4)
```

Где `0.4 м` — системная ширина траншеи.

### 3. Песок в траншеи

Уточнено правило, чтобы ручная разработка и песок использовали один и тот же выбранный объём траншей:

```text
compacted_sand_trenches_m3 = trench_volume_total_m3 * sand_compaction_coeff
```

Это исключает ситуацию, когда ручная разработка считается от одного объёма траншей, а песок — от другого.

### 4. Длина коммуникаций

Затронуты строки сметы:

```text
Закладка технологических входов коммуникаций до границы дома
Материалы для устройства входов коммуникаций
```

Что было:

```text
communications_length_m
```

Длина коммуникаций задавалась готовым числом.

Что стало:

Добавлен production-режим:

```text
communications_length_calc_method = pipe_items
```

Длина считается из спецификации труб:

```text
communications_length_m = sum(pipe_length_m * quantity)
```

Если позиция спецификации уже содержит готовую длину, используется:

```text
total_length_m
```

Рассчитанная `communications_length_m` используется и для работ, и для материалов коммуникаций.

## Legacy сохранён

Старые режимы оставлены для сверки со старыми сметами:

- `excavator_shifts_calc_method = legacy_manual_shifts`;
- `manual_excavation_calc_method = legacy_manual_override`;
- `communications_length_calc_method = legacy_direct_length`.

Кейс ЮСВ явно помечен как legacy по этим местам, чтобы старый эталон не изменился молча.

Старые `expected.json` не менялись.

## Добавленные тестовые кейсы

Добавлены отдельные проверочные кейсы:

```text
experiments/earthworks_calculator/cases/test_excavator_shifts_standard/
experiments/earthworks_calculator/cases/test_manual_excavation_standard_routes/
experiments/earthworks_calculator/cases/test_manual_excavation_spec_trench_volume/
experiments/earthworks_calculator/cases/test_communications_pipe_items/
```

Что проверяют:

- `test_excavator_shifts_standard` — смены JCB считаются от объёма выемки;
- `test_manual_excavation_standard_routes` — траншеи считаются по трассам;
- `test_manual_excavation_spec_trench_volume` — готовый объём траншей из спецификации имеет приоритет;
- `test_communications_pipe_items` — длина коммуникаций считается из труб спецификации.

## Проверки

Перед коммитом выполнены проверки:

```text
horoshevka_14 -> ok (76/76)
test_communications_pipe_items -> ok (21/21)
test_excavator_shifts_standard -> ok (17/17)
test_manual_excavation_spec_trench_volume -> ok (18/18)
test_manual_excavation_standard_routes -> ok (18/18)
usv_yusupovo_village -> ok (100/100)
usv_yusupovo_village_live_prices -> ok (0/0)
```

Также выполнена проверка компиляции:

```text
py_compile -> ok
```

## Обновлённые документы

Обновлены:

```text
docs/report_earthworks_calculator.md
docs/current_project_state.md
docs/assistant_handoff.md
docs/project_notes.md
docs/change_log.md
experiments/earthworks_calculator/README.md
```

Созданы отдельные технические отчёты:

```text
docs/report_earthworks_excavator_shifts_refactor.md
docs/report_earthworks_manual_excavation_refactor.md
docs/report_earthworks_communications_refactor.md
```

## Итог

Калькулятор земляных работ доработан под новые production-правила Елены.

Ручной ввод сокращён там, где теперь есть утверждённые формулы:

- смены экскаватора считаются автоматически;
- ручная разработка считается автоматически;
- объём траншей берётся из спецификации или считается по трассам;
- песок в траншеи использует тот же объём траншей;
- длина коммуникаций считается из труб спецификации.

Старые эталонные кейсы сохранены и проходят без расхождений.
