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
docs/report_waterproofing_calculator.md
```

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

## Команды проверки

Земляные работы:

```bash
../.venv/bin/python3 experiments/earthworks_calculator/run_all_cases.py
```

Фундаментная плита:

```bash
../.venv/bin/python3 experiments/foundation_slab_calculator/run_foundation_slab_calc.py experiments/foundation_slab_calculator/cases/test_foundation_slab
```

Гидроизоляция:

```bash
../.venv/bin/python3 experiments/waterproofing_calculator/run_waterproofing_calc.py experiments/waterproofing_calculator/cases/test_waterproofing_foundation_slab
```

## Текущий git-статус по смыслу

Последние коммиты в истории пока фиксируют базовую структуру, meeting analysis, УНИКМА и changelog. Большая работа по проектным папкам, калькуляторам, отчётам и документации находится в рабочем дереве и требует отдельного коммита, когда пользователь решит зафиксировать текущую контрольную точку.
