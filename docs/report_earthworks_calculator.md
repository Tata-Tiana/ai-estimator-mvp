# Отчёт по калькулятору земляных работ

Дата: 2026-05-15

## Кратко

В проекте `ai-estimator-mvp` сделан экспериментальный детерминированный калькулятор раздела сметы "Земляные работы".

Калькулятор считает серую внутреннюю себестоимость раздела: материалы, работы и итог. Клиентская часть сметы, рентабельность, НР/СП/ТН и коммерческие коэффициенты в этом модуле не считаются.

Главный принцип: AI не считает смету. AI может помочь извлечь параметры из проекта, но расчёт выполняется обычным Python-кодом по явно зафиксированным формулам.

## Где находится

```text
experiments/earthworks_calculator/
├── earthworks_calculator.py
├── run_earthworks_calc.py
├── run_all_cases.py
├── cases/
│   ├── usv_yusupovo_village/
│   └── horoshevka_14/
└── output/
    ├── usv_yusupovo_village/
    └── horoshevka_14/
```

## Что считает калькулятор

Калькулятор считает объёмы и строки внутренней сметы для земляных работ:

- вынос осей;
- механизированная разработка грунта;
- ручная разработка / доработка грунта;
- укладка геотекстиля;
- геотекстиль как материал;
- песчаная подготовка;
- песок как материал;
- перемещение песка вручную;
- коммуникации;
- расходные материалы.

Набор строк может отличаться по кейсам: для этого предусмотрены `enabled_lines`, `quantity_overrides` и `line_name_overrides`.

## Основные формулы

В калькуляторе явно зафиксированы расчётные правила:

- ручная доработка котлована: `pit_area_m2 * manual_refinement_depth_m`;
- смены экскаватора legacy: готовое `excavator_shifts`;
- смены экскаватора production: `ceil((pit_area_m2 * pit_excavation_depth_m) / 80)`;
- объём траншей legacy: готовым значением или через `length * depth * width`;
- объём траншей production: если спецификация даёт готовый `trench_volume_m3`, используется он; если готового объёма нет, считается сумма `route_length_m * route_depth_m * 0.4` по трассам `К1/К2/ВК/ЭО`;
- коммуникации legacy: готовая длина `communications_length_m`;
- коммуникации production: сумма длин труб из спецификации;
- общая ручная разработка: ручная доработка котлована + траншеи;
- песок с трамбованием: объём * коэффициент уплотнения;
- песок в траншеи использует тот же `trench_volume_total_m3`, что и ручная разработка грунта;
- заказ песка: округление вверх до шага машины;
- геотекстиль с нахлёстом: площадь * коэффициент нахлёста;
- рулоны геотекстиля: округление вверх до целых рулонов;
- строка сметы: `quantity * unit_price`;
- итог раздела: материалы + работы.

## Формат входных данных

Каждый кейс хранится в отдельной папке:

```text
cases/<case_name>/
├── input.json
├── expected.json
└── notes.md
```

`input.json` содержит параметры проекта и ставки.

`expected.json` содержит эталонные значения для сравнения с расчётом.

`notes.md` фиксирует источник данных, допущения, overrides и открытые вопросы.

## Формат результата

После запуска создаются:

```text
output/<case_name>/earthworks_result.json
output/<case_name>/earthworks_result.md
```

В JSON сохраняются:

- входные данные;
- рассчитанные объёмы;
- строки серой внутренней сметы;
- итоги;
- expected;
- comparison по каждому проверяемому полю.

Markdown-отчёт нужен для быстрой проверки человеком.

## Проверенные кейсы

### usv_yusupovo_village

Статус: эталонный кейс, разобран с Еленой.

Результат:

```text
internal_materials_total = 467 797
internal_works_total    = 337 223
internal_section_total  = 805 020
```

Проверка:

```text
100 ok
0 mismatch
```

### horoshevka_14

Статус: повторение существующей сметы с явными overrides.

Результат:

```text
internal_materials_total = 304 992
internal_works_total    = 254 372
internal_section_total  = 559 364
```

Проверка:

```text
76 ok
0 mismatch
```

### test_manual_excavation_standard_routes

Статус: тест production-стандарта ручной разработки грунта.

Проверяет, что ручной override больше не нужен для нового стандарта:

```text
manual_pit_volume_m3 = 330 * 0.08 = 26.4
trench_volume_total_m3 = 16.12
manual_excavation_total_m3 = 42.52
```

Траншеи считаются по трассам:

```text
К1 = 10 * 1.2 * 0.4 = 4.8
К2 = 8 * 1.0 * 0.4 = 3.2
ВК = 12 * 1.4 * 0.4 = 6.72
ЭО = 5 * 0.7 * 0.4 = 1.4
```

### test_manual_excavation_spec_trench_volume

Статус: тест production-стандарта, где спецификация уже даёт готовый объём траншей.

Проверяет приоритет `trench_volume_m3` над расчётом по трассам:

```text
manual_pit_volume_m3 = 330 * 0.08 = 26.4
trench_volume_source = spec_volume
trench_volume_total_m3 = 18.29
manual_excavation_total_m3 = 44.69
compacted_sand_trenches_m3 = 18.29 * 1.3 = 23.777
```

Важно: этот же `trench_volume_total_m3` используется и для ручной разработки грунта, и для песка в траншеи.

### test_excavator_shifts_standard

Статус: тест production-стандарта расчёта смен экскаватора.

Проверяет, что строка `excavator_jcb` берёт рассчитанное количество смен:

```text
machine_excavation_volume_m3 = 330 * 0.6 = 198
excavator_productivity_m3_per_shift = 80
excavator_shifts = ceil(198 / 80) = 3
```

Стоимость строки:

```text
materials = 3 * 26000 = 78000
works = 3 * 3500 = 10500
line_total = 88500
```

Важно: `pit_excavation_depth_m` — глубина механизированной выемки, а `manual_refinement_depth_m = 0.08` — ручная доработка дна котлована.

### test_communications_pipe_items

Статус: тест production-стандарта расчёта длины коммуникаций.

Проверяет, что `communications_length_m` считается из спецификации труб:

```text
pipe_1m = 1 * 12 = 12
pipe_2m = 2 * 5 = 10
pipe_3m = 3 * 4 = 12
corrugated_pipe = 25
communications_length_m = 59
```

Рассчитанная длина используется в двух строках:

- `communications_work`;
- `communications_material`.

## Почему это важно

Калькулятор земляных работ стал первым рабочим примером архитектуры расчётов:

1. Входные параметры отделены от формул.
2. Формулы вынесены в детерминированный код.
3. Эталонные значения хранятся отдельно.
4. Сравнение показывает, где расчёт совпал, а где есть расхождение.
5. Любое отличие от формульного расчёта не прячется в коде, а фиксируется в `overrides` и `notes.md`.

## Команды запуска

Запуск одного кейса:

```bash
../.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py experiments/earthworks_calculator/cases/usv_yusupovo_village
```

Запуск Хорошевки:

```bash
../.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py experiments/earthworks_calculator/cases/horoshevka_14
```

Запуск всех кейсов:

```bash
../.venv/bin/python3 experiments/earthworks_calculator/run_all_cases.py
```

## Текущий статус

Калькулятор земляных работ работает и повторяет проверенные эталонные расчёты по двум кейсам без расхождений.

Он остаётся в `experiments/`, потому что проект развивается по принципу: сначала экспериментальный калькулятор, затем проверка на нескольких кейсах, затем возможный перенос стабильной логики в `app/estimator/`.
