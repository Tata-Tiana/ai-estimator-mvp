# Earthworks Calculator Experiment

Экспериментальный детерминированный расчётный модуль для раздела "Земляные работы".

AI здесь не используется. В будущем AI должен только подставлять входные параметры, а расчёт остаётся обычным Python-кодом.

## Структура

```text
earthworks_calculator.py
run_earthworks_calc.py
cases/
  usv_yusupovo_village/
    input.json
    expected.json
    notes.md
output/
  usv_yusupovo_village/
    earthworks_result.json
    earthworks_result.md
```

## Запуск

Из корня проекта:

```bash
.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py
```

Запуск конкретного кейса:

```bash
.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py experiments/earthworks_calculator/cases/usv_yusupovo_village
```

Запуск кейса Хорошевка 14:

```bash
.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py experiments/earthworks_calculator/cases/horoshevka_14
```

Запуск теста production-стандарта ручной разработки по трассам:

```bash
.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py experiments/earthworks_calculator/cases/test_manual_excavation_standard_routes
```

Запуск теста production-стандарта ручной разработки с готовым объёмом траншей из спецификации:

```bash
.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py experiments/earthworks_calculator/cases/test_manual_excavation_spec_trench_volume
```

Запуск теста production-стандарта коммуникаций по трубам:

```bash
.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py experiments/earthworks_calculator/cases/test_communications_pipe_items
```

Запуск теста production-стандарта смен экскаватора по объёму выемки:

```bash
.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py experiments/earthworks_calculator/cases/test_excavator_shifts_standard
```

Запуск всех кейсов:

```bash
.venv/bin/python3 experiments/earthworks_calculator/run_all_cases.py
```

Можно передать как папку кейса, так и прямой путь к `input.json`.

## Как добавлять следующие тесты

1. Создать папку в `cases/`.
2. Положить туда `input.json`.
3. Положить туда `expected.json` с эталонными значениями от Елены.
4. Добавить `notes.md`: источник данных, что считается, что пока не считается.
5. Запустить runner и проверить блок сравнения с эталоном.

## Формат результата

`earthworks_result.json` хранит расчёт отдельно от проверки:

```json
{
  "inputs": {},
  "volume_result": {},
  "estimate_lines": [],
  "internal_totals": {},
  "expected": {},
  "comparison": []
}
```

`expected.json` для кейса ЮСВ хранит:

- `volumes` — эталонные объёмы;
- `estimate_lines` — эталонные строки серой внутренней сметы по стабильному `code`;
- `internal_totals` — эталонные итоги внутренней себестоимости раздела.

## Смены экскаватора

Калькулятор поддерживает два режима:

- `legacy_manual_shifts` — старый режим для повторения существующих смет. Строка "Механизированная разработка грунта, Экскаватор JCB" берёт готовое `excavator_shifts`.
- `standard_volume_productivity` — новый production-стандарт. Смены считаются от объёма механизированной выемки:

```text
machine_excavation_volume_m3 = pit_area_m2 * pit_excavation_depth_m
excavator_shifts = ceil(machine_excavation_volume_m3 / 80)
```

В production-стандарте:

- `pit_area_m2` — проектная площадь котлована;
- `pit_excavation_depth_m` — проектная глубина механизированной выемки котлована;
- `excavator_productivity_m3_per_shift = 80` — системная настройка по методике Елены;
- `excavator_shifts` не используется как ручной ввод.

Важно: `pit_excavation_depth_m` не равен `manual_refinement_depth_m`. `manual_refinement_depth_m = 0.08` относится только к ручной доработке дна котлована.

## Ручная разработка грунта

Калькулятор поддерживает два режима:

- `legacy_manual_override` — старый режим для повторения существующих смет. Если задано `manual_excavation_quantity_for_estimate_m3`, строка "Разработка грунта вручную" берёт это количество.
- `standard_routes` — новый production-стандарт. Ручная разработка считается формулой:

```text
manual_excavation_total_m3 = pit_area_m2 * 0.08 + trench_volume_total_m3
```

В production-стандарте:

- `manual_refinement_depth_m = 0.08` — системная настройка ручной доработки котлована;
- `trench_width_m = 0.4` — системная ширина траншеи;
- `trench_volume_m3` — готовый объём траншей из спецификации, если он есть;
- `trench_routes[].length_m` и `trench_routes[].depth_m` — проектные данные из спецификации/чертежа, если готового объёма траншей нет;
- `manual_excavation_quantity_for_estimate_m3` не используется.

Приоритет для `trench_volume_total_m3`:

1. если спецификация даёт готовый `trench_volume_m3`, используется он;
2. если готового объёма нет, траншеи считаются по трассам: `sum(route_length_m * route_depth_m * 0.4)`.

Один и тот же `trench_volume_total_m3` используется в ручной разработке грунта и в песке в траншеи:

```text
compacted_sand_trenches_m3 = trench_volume_total_m3 * sand_compaction_coeff
```

## Коммуникации

Калькулятор поддерживает два режима расчёта длины технологических вводов:

- `legacy_direct_length` — старый режим: используется готовое `communications_length_m`;
- `pipe_items` — новый production-стандарт: длина считается из спецификации труб.

Для `pipe_items` используется список:

```json
"communications_pipe_items": [
  {
    "code": "pipe_1m",
    "name": "Труба 1 м",
    "pipe_length_m": 1,
    "quantity": 12,
    "include_in_communications": true
  }
]
```

Если в спецификации позиция уже дана готовой длиной, можно передать `total_length_m`.

Рассчитанное `communications_length_m` используется в строках:

- `communications_work`;
- `communications_material`.
