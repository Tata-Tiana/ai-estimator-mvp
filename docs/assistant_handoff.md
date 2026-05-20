# Assistant Handoff

Дата актуализации: `2026-05-15`.

Этот файл нужен, чтобы в новом чате быстро понять, что происходит в проекте `ai-estimator-mvp`, где лежит рабочий код и на какой точке остановились.

## Суть проекта

Проект — MVP AI-сметчика для частных домов.

Цепочка работы:

1. разобрать PDF-проект;
2. извлечь текст, таблицы и параметры;
3. при необходимости проанализировать созвон с инженером-сметчиком Еленой;
4. на основе подтверждённых правил сделать детерминированный калькулятор раздела сметы;
5. сверить строки, материалы, работы и итоги с серой внутренней сметой;
6. не считать клиентскую часть.

Главное правило: AI не считает смету. Расчёт должен быть обычным Python-кодом.

## Рабочая зона

Сейчас активная работа живёт в `experiments/`, не в `app/`.

`app/` пока каркас будущего стабильного MVP.

## Что уже сделано

### 1. PDF-парсер

Папка:

```text
experiments/pdf_tests/
```

Проверенный проект:

```text
experiments/pdf_tests/projects/horoshevka_14/
```

Входные PDF:

```text
kr1_below_floor.pdf
kr2_above_floor.pdf
```

Результаты:

- `full_text.txt`;
- `pages_text.json`;
- `blocks.json`;
- `tables.json`;
- `tables.xlsx`;
- `summary.json`.

Отчёт:

```text
docs/report_pdf_parser.md
```

### 2. Калькулятор земляных работ

Папка:

```text
experiments/earthworks_calculator/
```

Проверенные кейсы:

```text
usv_yusupovo_village -> ok (100/100)
horoshevka_14 -> ok (76/76)
```

Итоги:

```text
usv_yusupovo_village:
  internal_materials_total = 467797
  internal_works_total = 337223
  internal_section_total = 805020

horoshevka_14:
  internal_materials_total = 304992
  internal_works_total = 254372
  internal_section_total = 559364
```

Отчёт:

```text
docs/report_earthworks_calculator.md
```

### 3. Калькулятор фундаментной плиты

Папка:

```text
experiments/foundation_slab_calculator/
```

Кейс:

```text
test_foundation_slab -> ok (205/205)
```

Итоги:

```text
internal_materials_total = 1454675
internal_works_total = 1083650
internal_section_total = 2538325
```

Сверено со скрином Excel. Построчные суммы совпали. Отличие Excel на 1 рубль в итогах было признано несущественным и связано с округлением.

Важные правила:

- PLANTERBAND = рулоны мембраны * 4;
- опалубка по бортам = внешний периметр * высота плиты;
- при разной толщине плит можно брать максимальную толщину;
- пиломатериал = площадь опалубки * 0.05, без коэффициента 1.5;
- арматура считается универсально: кг -> м.п. -> 5% -> прутки -> закупочные м.п. -> стоимость;
- бетон: работа по проектному объёму, материал с 5% и округлением до 0.5 м3;
- доставка металла осталась manual/fixed, но добавлен suggested trucks по 10 тонн.

Отчёт:

```text
docs/report_foundation_slab_calculator.md
```

### 4. Калькулятор гидроизоляции фундаментной плиты

Папка:

```text
experiments/waterproofing_calculator/
```

Кейс:

```text
test_waterproofing_foundation_slab -> ok (54/54)
```

Итоги:

```text
waterproofing_base_subtotal = 48777
internal_materials_total = 33961
internal_works_total = 17255
internal_section_total = 51216
```

Сверено со скрином Excel по блоку "Гидроизоляция, утепление бортов плит". Все видимые строки и итоги совпали.

Отчёт:

```text
docs/report_waterproofing_calculator.md
```

## Как запускать проверки

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

Компиляция новых калькуляторов:

```bash
../.venv/bin/python3 -m py_compile experiments/foundation_slab_calculator/foundation_slab_calculator.py experiments/foundation_slab_calculator/run_foundation_slab_calc.py
../.venv/bin/python3 -m py_compile experiments/waterproofing_calculator/waterproofing_calculator.py experiments/waterproofing_calculator/run_waterproofing_calc.py
```

## Где лежат данные созвонов

Meeting analysis:

```text
experiments/meeting_analysis/
```

Фундаментная плита:

```text
experiments/meeting_analysis/input/2026-05-08_foundation_slab/
data/output/meeting_analysis/2026-05-08_1125_foundation_slab/
```

Земляные работы:

```text
experiments/meeting_analysis/input/2026-04-30_earthworks/
data/output/meeting_analysis/2026-04-30_1818_earthworks/
```

## Важные запреты

- Не считать клиентскую часть.
- Не добавлять рентабельность, НР/СП/ТН и коммерческие коэффициенты в экспериментальные калькуляторы.
- Не переписывать рабочие калькуляторы с нуля.
- Не подгонять mismatch молча.
- Если Excel отличается, сначала понять: строка, округление, отсутствующая строка или ручная корректировка.
- Любое отличие формульного расчёта от сметного количества фиксировать через `expected.json`, `notes.md`, warnings или explicit overrides.

## Git и контрольная точка

Последние коммиты:

```text
e39d52d Add project change log
4f376af Add meeting analysis and Unikma API notes
d8c75ff Initial MVP structure for PDF parsing and AI project card experiments
```

Большая работа по:

- проектным папкам PDF/AI;
- калькулятору земляных работ;
- калькулятору фундаментной плиты;
- калькулятору гидроизоляции;
- отчётам для руководства;
- обновлению README/docs

находится в рабочем дереве и ещё не зафиксирована отдельным git-коммитом.

Рекомендуемый следующий коммит после проверки пользователем:

```text
Add experimental estimate calculators and project handoff docs
```

## Следующий разумный шаг

1. Закоммитить текущую контрольную точку.
2. Продолжить следующий раздел сметы отдельным экспериментальным калькулятором.
3. Для каждого нового раздела повторять схему:
   `input.json` -> deterministic calculator -> `expected.json` -> result JSON/MD -> comparison -> report in docs.
