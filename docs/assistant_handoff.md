# Assistant Handoff

Дата актуализации: `2026-05-20`.

Этот файл — главная точка входа для нового чата/агента. Если нужно быстро понять проект `ai-estimator-mvp`, начинать отсюда.

## Последняя расчётная контрольная точка

Текущая рабочая ветка:

```text
feature/ai-project-card
```

Коммит расчётной базы:

```text
20c9d05 Add experimental estimate calculators and project handoff docs
```

Смысл коммита:

- зафиксированы проектные папки PDF/AI;
- добавлены экспериментальные калькуляторы разделов сметы;
- добавлены отчёты для руководства;
- обновлена документация и handoff.

После этого коммита проект имеет чистую расчётную контрольную точку, от которой можно продолжать следующий раздел сметы.

## Суть проекта

Проект — MVP AI-сметчика для частных домов.

Рабочая цепочка:

1. разобрать PDF-проект дома;
2. извлечь текст, таблицы и технические параметры;
3. при необходимости проанализировать созвон с инженером-сметчиком Еленой;
4. на основе подтверждённых правил сделать детерминированный калькулятор раздела сметы;
5. сверить строки, материалы, работы и итоги с серой внутренней сметой;
6. зафиксировать расхождения через `expected.json`, `notes.md`, warnings или explicit overrides;
7. не считать клиентскую часть.

Главное правило: AI не считает смету. AI помогает достать входные параметры, а расчёт делается обычным Python-кодом.

## Где что лежит

- `app/` — каркас будущего стабильного MVP.
- `experiments/` — активная рабочая зона.
- `docs/` — карта проекта, handoff, changelog и отчёты.
- `data/` — legacy/локальные данные, результаты старых прогонов и справочные выгрузки.
- `tests/` — заготовки будущих тестов стабильного слоя.

Сейчас реальные рабочие расчёты живут в `experiments/`, не в `app/`.

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

Парсер извлекает:

- полный текст;
- текст по страницам;
- текстовые блоки с координатами;
- таблицы в JSON и Excel;
- `summary.json`.

Отчёт:

```text
docs/report_pdf_parser.md
```

### 2. AI-карточка проекта

Папка:

```text
experiments/ai_tests/
```

Проверенный проект:

```text
experiments/ai_tests/projects/horoshevka_14/
```

Назначение:

- собрать общий текст из PDF-артефактов;
- отправить его в OpenAI;
- получить техническую карточку проекта;
- сохранить missing data, warnings и табличные артефакты.

### 3. Meeting Analysis

Папка:

```text
experiments/meeting_analysis/
```

Назначение:

- анализировать транскрипты созвонов с Еленой;
- извлекать формулы, расчётную логику, открытые вопросы и требования к проектам.

Важные темы:

- `2026-04-30_earthworks`;
- `2026-05-08_foundation_slab`.

### 4. Калькулятор земляных работ

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

### 5. Калькулятор фундаментной плиты

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

Считает серую внутреннюю себестоимость раздела "Устройство фундаментной плиты дома, террасы, крыльца (250мм, 300мм)".

Отчёт:

```text
docs/report_foundation_slab_calculator.md
```

### 6. Калькулятор гидроизоляции фундаментной плиты

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

Считает блок "Гидроизоляция, утепление бортов плит".

Отчёт:

```text
docs/report_waterproofing_calculator.md
```

### 7. Калькулятор несущих стен и перемычек

Папка:

```text
experiments/load_bearing_walls_lintels_calculator/
```

Кейс:

```text
test_load_bearing_walls_lintels -> ok
```

Итоги:

```text
internal_materials_total_raw = 1550654.431
internal_materials_total = 1550654
internal_works_total_raw = 1121449.0
internal_works_total = 1121449
internal_section_total_raw = 2672103.431
internal_section_total = 2672103
```

Важно: в этом разделе Excel отображает строки округлёнными, но итог считает от raw-значений. Поэтому результат хранит и raw, и display totals.

Отчёт:

```text
docs/report_load_bearing_walls_lintels_calculator.md
```

### 8. УНИКМА

Папка:

```text
experiments/unikma_api_tests/
```

Что уже проверено:

- `GetStores`;
- `GetNomenclatures` с нормализацией `ArrayRef`;
- постраничная загрузка по `Limit=100`;
- `GetPriceFile`;
- черновой material matching по кровельным позициям.

Вывод: УНИКМА полезна как слой товаров, цен, складов и остатков, но не заменяет расчётную логику сметы.

## Проверочные команды

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

Несущие стены и перемычки:

```bash
../.venv/bin/python3 experiments/load_bearing_walls_lintels_calculator/run_load_bearing_walls_lintels_calc.py experiments/load_bearing_walls_lintels_calculator/cases/test_load_bearing_walls_lintels
```

Общий pytest:

```bash
../.venv/bin/python3 -m pytest
```

На момент фиксации `pytest` собирает `0` тестов; основные проверки сейчас идут через CLI калькуляторов.

## Что было проверено перед коммитом `20c9d05`

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

pytest:
  collected 0 items
```

## Важные запреты

- Не считать клиентскую часть.
- Не добавлять рентабельность, НР/СП/ТН и коммерческие коэффициенты в экспериментальные калькуляторы.
- Не переписывать рабочие калькуляторы с нуля.
- Не подгонять mismatch молча.
- Если Excel отличается, сначала понять причину: строка, округление, отсутствующая строка или ручная корректировка.
- Любое отличие формульного расчёта от сметного количества фиксировать явно.

## Следующий разумный шаг

Продолжать следующий раздел сметы отдельным экспериментальным калькулятором по той же схеме:

```text
input.json -> deterministic calculator -> expected.json -> result JSON/MD -> comparison -> report in docs
```

Перед новым большим этапом смотреть:

```text
docs/current_project_state.md
docs/project_notes.md
docs/change_log.md
```
