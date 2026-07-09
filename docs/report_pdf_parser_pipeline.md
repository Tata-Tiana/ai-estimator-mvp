# Отчёт по PDF parser pipeline

Дата: `2026-06-01`.

## Что сделано

Создан рабочий экспериментальный слой:

```text
experiments/pdf_parser_pipeline/
```

Он закрывает MVP-цепочку:

```text
PDF parser artifacts
↓
section review cards
↓
reviewed_parameters.xlsx для Елены
↓
будущий input_builder
```

Этот слой теперь считается основным рабочим контуром для подготовки параметров из PDF. Более ранний `experiments/review_sheet_builder/` был промежуточной пробой и удалён, чтобы не держать два похожих контура.

## Зачем нужен pipeline

Калькуляторы не должны читать PDF напрямую. PDF parser извлекает текст и таблицы, но расчёт сметы выполняют детерминированные Python-калькуляторы.

Задача pipeline — подготовить таблицу проверки параметров:

- если параметр найден в PDF, он попадает в `extracted_value`;
- если параметр не найден, строка всё равно создаётся по schema и получает статус `missing` или `manual_required`;
- Елена проверяет значения, заполняет `corrected_value` и статусы;
- следующий слой `input_builder` позже сможет собрать `input.json` калькуляторов.

## Источники

Pipeline использует уже существующие артефакты проекта ЮСВ:

```text
experiments/pdf_tests/projects/usv_yusupovo_village/
```

Обрабатываются источники:

| source_id | source_file | Назначение |
|---|---|---|
| `kr1_foundation` | `ЮСВ КР1.pdf` | фундаментная часть |
| `kr2_above_zero` | `ЮСВ КР2.pdf` | конструкции выше нуля |
| `ar_architecture` | `ЮСВ АР.pdf` | архитектура |

По каждому источнику используются:

- `pages_text.json`;
- `tables.json`;
- `blocks.json`;
- `summary.json`;
- merged-файлы `project_manifest.json`, `extraction_report.md`, `extracted_parameters_for_review.json`, `project_full_text_by_sources.md`.

`page_images/` не дублируются в новом case, чтобы не раздувать экспериментальную папку. Они остаются в исходном parser-проекте.

## Созданные файлы

Кейс:

```text
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/
```

Основные результаты:

```text
review_cards/
reviewed_parameters.xlsx
result.json
result.md
```

Дубль для просмотра:

```text
experiments/pdf_parser_pipeline/output/mvp_usv_demo/
```

## Review cards

Создаются карточки по всем 8 готовым разделам:

- `earthworks`;
- `foundation_slab`;
- `waterproofing`;
- `load_bearing_walls_lintels`;
- `floor_slab_1`;
- `floor_slab_2`;
- `flat_roof`;
- `schiedel_vent_channels`.

Каждая карточка содержит:

- `parameter_code`;
- `calculator_input_key`;
- найденное значение или `null`;
- единицу измерения;
- источник `source_file`, `source_id`, `page`, `source_text`;
- `review_status`;
- `confidence`;
- вопросы для Елены.

## reviewed_parameters.xlsx

Excel строится от `section_schema.py`, а не от случайных regex-находок.

Листы:

- `parameters`;
- `missing_parameters`;
- `review_questions`;
- `sources`;
- `extraction_summary`;
- `raw_extraction_diagnostic`.

Главный лист `parameters` содержит:

- все параметры, нужные калькуляторам;
- найденные PDF-значения;
- пустую колонку `corrected_value` для Елены;
- `final_value`;
- статусы `needs_review`, `manual_required`, `missing`, `control_only`;
- признак `use_for_calculation`.

## Файл для Елены по missing-параметрам

Дополнительно создан отдельный отчёт:

```text
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/elena_missing_parameters_by_section.xlsx
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/elena_missing_parameters_by_section.md
experiments/pdf_parser_pipeline/output/mvp_usv_demo/elena_missing_parameters_by_section.xlsx
experiments/pdf_parser_pipeline/output/mvp_usv_demo/elena_missing_parameters_by_section.md
```

Он нужен, чтобы быстро понять, каких данных parser не нашёл по 8 разделам сметы.

Листы Excel:

- `summary` — краткая сводка по разделам;
- `for_designers` — параметры, которые лучше уточнять у проектировщиков или по проекту;
- `estimator_manual` — сметные, ценовые, технические и ручные параметры для Елены/сметчика;
- `all_missing_raw` — полный список missing/manual без фильтрации.

В `section_schema.py` улучшены русские labels для авто-параметров из `input.json`. Например:

- `rebar_items[0].code` -> `Арматура 1: код позиции`;
- `rebar_items[0].diameter_mm` -> `Арматура 1: диаметр`;
- `beams.items[0].name` -> `Балка Б-1: наименование позиции`;
- `gas_block_wall_holes_count` -> `Количество отверстий в стенах из газоблока`.

## Текущий результат прогона

Команда:

```bash
.venv/bin/python3 experiments/pdf_parser_pipeline/run_pdf_parser_pipeline.py experiments/pdf_parser_pipeline/cases/mvp_usv_demo
```

Итог:

```text
review_cards: 8
missing_total: 287
manual_required_total: 69
```

Сводка найденных параметров:

| Раздел | Найдено из PDF |
|---|---:|
| earthworks | 3 |
| foundation_slab | 15 |
| waterproofing | 2 |
| load_bearing_walls_lintels | 7 |
| floor_slab_1 | 8 |
| floor_slab_2 | 7 |
| flat_roof | 6 |
| schiedel_vent_channels | 4 |

Для всех найденных строк проверено наличие `source_text`.

## Проверки

Выполнено:

```bash
.venv/bin/python3 -m py_compile experiments/pdf_parser_pipeline/section_schema.py experiments/pdf_parser_pipeline/section_review_card_builder.py experiments/pdf_parser_pipeline/review_sheet_builder.py experiments/pdf_parser_pipeline/run_pdf_parser_pipeline.py
```

Также проверено:

- созданы 8 review cards;
- создан `reviewed_parameters.xlsx`;
- в Excel есть обязательные листы;
- найденные значения имеют источник;
- старые калькуляторы не менялись;
- `expected.json` не изменялись.

## Важные ограничения

- Parser/AI не считают смету.
- Значения без уверенного источника не придумываются.
- Цены, коэффициенты, доставки и ручные правила в основном остаются `price`, `default`, `calculation_constant` или `manual`.
- `raw_extraction_diagnostic` — только диагностический слой, не источник истины.
- Клиентская часть сметы не считается.

## Следующий шаг

Следующий логичный слой:

```text
input_builder
```

Он должен будет читать проверенный `reviewed_parameters.xlsx` и собирать `input.json` для готовых калькуляторов.
