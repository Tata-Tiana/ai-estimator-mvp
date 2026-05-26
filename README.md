# ai-estimator-mvp

MVP AI-сметчика для частных домов.

Идея проекта: из PDF-проекта дома извлекать проверяемые технические параметры, а затем считать разделы сметы детерминированным Python-кодом. AI в этой архитектуре не считает смету: он может помогать читать документы, транскрипты и вытаскивать входные параметры. Сами формулы, цены, округления, ручные строки и итоги фиксируются явно в коде и в `expected.json`.

## Главное правило

- `app/` — будущий стабильный код MVP.
- `experiments/` — рабочая зона экспериментов.
- Каждый новый раздел сметы сначала делается отдельным калькулятором в `experiments/`, проверяется на кейсах, сравнивается с эталонной серой сметой и только потом может переноситься в `app/estimator/`.
- Клиентская часть сметы пока не считается: нет рентабельности, НР/СП/ТН и коммерческих коэффициентов.

## Где быстро понять состояние проекта

Начинать новый чат/сессию лучше с этих файлов:

```text
docs/assistant_handoff.md
docs/current_project_state.md
docs/project_notes.md
docs/change_log.md
```

Отчёты для руководства лежат здесь:

```text
docs/report_pdf_parser.md
docs/report_earthworks_calculator.md
docs/report_foundation_slab_calculator.md
docs/report_floor_slab_1_calculator.md
docs/report_floor_slab_2_calculator.md
docs/report_flat_roof_calculator.md
docs/report_schiedel_vent_channels_calculator.md
docs/report_waterproofing_calculator.md
docs/report_load_bearing_walls_lintels_calculator.md
```

## Последняя расчётная контрольная точка

```text
branch: feature/ai-project-card
commit: 454c132 Add flat roof calculator
date: 2026-05-26
```

Это актуальная зафиксированная расчётная база проекта: проектные папки PDF/AI, экспериментальные калькуляторы, отчёты и handoff-документация сохранены в git.

## Что сейчас работает

### PDF-парсер

Папка:

```text
experiments/pdf_tests/
```

Проверенный проект:

```text
experiments/pdf_tests/projects/horoshevka_14/
```

Парсер извлекает:

- полный текст;
- текст по страницам;
- текстовые блоки с координатами;
- таблицы в JSON и Excel;
- `summary.json`.

### Калькулятор земляных работ

Папка:

```text
experiments/earthworks_calculator/
```

Проверенные кейсы:

```text
usv_yusupovo_village -> ok (100/100), итог 805020
horoshevka_14 -> ok (76/76), итог 559364
```

### Калькулятор фундаментной плиты

Папка:

```text
experiments/foundation_slab_calculator/
```

Проверенный кейс:

```text
test_foundation_slab -> ok (205/205), итог 2538325
```

Считает серую внутреннюю себестоимость раздела "Устройство фундаментной плиты дома, террасы, крыльца (250мм, 300мм)".

### Калькулятор плиты перекрытия 1-го этажа

Папка:

```text
experiments/floor_slab_1_calculator/
```

Проверенный кейс:

```text
test_floor_slab_1 -> ok (194/194), итог 1787527
```

Считает серую внутреннюю себестоимость раздела "Ж/Б монолитная плита перекрытия 1-го этажа на отм. +3.480 (180 мм) с балками".

Важно:

- балки Б-1, Б-2, Б-3 считаются внутри раздела;
- клиентская/белая часть не считается;
- Excel export для этого раздела пока не сделан;
- raw/display значения хранятся отдельно для строк, где Excel показывает округлённое количество.

### Калькулятор плиты перекрытия 2-го этажа

Папка:

```text
experiments/floor_slab_2_calculator/
```

Проверенный кейс:

```text
test_floor_slab_2 -> ok (222/222), итог 717051
```

Считает серую внутреннюю себестоимость раздела "Ж/Б монолитная плита перекрытия 2-го этажа на отм. +4.680 (200мм)".

Важно:

- балок в расчёте нет;
- объём бетонирования `16.5 м3` пока manual/project quantity;
- клиентская/белая часть не считается;
- Excel export для этого раздела пока не сделан;
- raw итог `717051.38648`, итог после ROUND_HALF_UP `717051`, сумма округлённых строк `717052`.

### Калькулятор плоской кровли

Папка:

```text
experiments/flat_roof_calculator/
```

Проверенный кейс:

```text
test_flat_roof_usv -> ok (460/460), итог 2038872
```

Считает серую внутреннюю себестоимость раздела "КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА / плоская кровля".

Важно:

- итог сходится с серой зоной Excel за минусом временной двери ДН-1;
- временная дверь не входит в универсальный калькулятор;
- логистика, технадзор и заготовительно-складские расходы включены как manual fixed строки текущего scope;
- клиентская/белая часть не считается;
- уклонные плиты берутся ручным объёмом от поставщика / Технониколь.

### Калькулятор гидроизоляции фундаментной плиты

### Калькулятор вентиляционных каналов Schiedel

Папка:

```text
experiments/schiedel_vent_channels_calculator/
```

Проверенный кейс:

```text
test_schiedel_vent_channels_usv -> ok (138/138), итог 117890
```

Считает серую внутреннюю себестоимость раздела "ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel".

Важно:

- кладка считается от raw `15.82 мп`, не от отображаемых `16 мп`;
- количества материалов `24` и `8` являются manual/specification input;
- 4 последние строки добавлены как нулевые строки структуры Excel;
- клиентская/белая часть не считается.

### Калькулятор гидроизоляции фундаментной плиты

Папка:

```text
experiments/waterproofing_calculator/
```

Проверенный кейс:

```text
test_waterproofing_foundation_slab -> ok (54/54), итог 51216
```

Считает блок "Гидроизоляция, утепление бортов плит".

### Калькулятор несущих стен и перемычек

Папка:

```text
experiments/load_bearing_walls_lintels_calculator/
```

Проверенный кейс:

```text
test_load_bearing_walls_lintels -> ok, итог 2672103
```

Считает серую внутреннюю себестоимость раздела "Внешние и внутренние несущие стены, перемычки".

Важно: в этом разделе Excel показывает округлённые строки, но итог считает от raw-значений. Поэтому результат хранит raw totals и display totals.

## Команды проверки

Земляные работы:

```bash
../.venv/bin/python3 experiments/earthworks_calculator/run_all_cases.py
```

Фундаментная плита:

```bash
../.venv/bin/python3 experiments/foundation_slab_calculator/run_foundation_slab_calc.py experiments/foundation_slab_calculator/cases/test_foundation_slab
```

Плита перекрытия 1-го этажа:

```bash
../.venv/bin/python3 experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py experiments/floor_slab_1_calculator/cases/test_floor_slab_1
```

Плита перекрытия 2-го этажа:

```bash
../.venv/bin/python3 experiments/floor_slab_2_calculator/run_case.py experiments/floor_slab_2_calculator/cases/test_floor_slab_2
```

Плоская кровля:

```bash
../.venv/bin/python3 experiments/flat_roof_calculator/run_case.py experiments/flat_roof_calculator/cases/test_flat_roof_usv
```

Вентиляционные каналы Schiedel:

```bash
../.venv/bin/python3 experiments/schiedel_vent_channels_calculator/run_case.py experiments/schiedel_vent_channels_calculator/cases/test_schiedel_vent_channels_usv
```

Гидроизоляция:

```bash
../.venv/bin/python3 experiments/waterproofing_calculator/run_waterproofing_calc.py experiments/waterproofing_calculator/cases/test_waterproofing_foundation_slab
```

Несущие стены и перемычки:

```bash
../.venv/bin/python3 experiments/load_bearing_walls_lintels_calculator/run_load_bearing_walls_lintels_calc.py experiments/load_bearing_walls_lintels_calculator/cases/test_load_bearing_walls_lintels
```

## Текущий git-статус по смыслу

Текущая расчётная контрольная точка зафиксирована коммитом `454c132`.

Перед этим были проверены:

```text
earthworks:
  horoshevka_14 -> ok (76/76)
  usv_yusupovo_village -> ok (100/100)

foundation_slab:
  internal_section_total = 2538325

waterproofing:
  internal_section_total = 51216

load_bearing_walls_lintels:
  internal_section_total = 2672103
```

`pytest` на текущий момент собирает `0` тестов; рабочие проверки идут через CLI калькуляторов.
