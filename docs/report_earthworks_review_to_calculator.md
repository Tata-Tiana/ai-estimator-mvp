# Отчёт по Earthworks Review To Calculator

Дата: `2026-06-22`.

## Кратко

В проекте `ai-estimator-mvp` построен и проверен полный сквозной контур сборки сметы земляных работ:

```text
experiments/earthworks_review_to_calculator/
```

Он берёт проверенный `review_workbook.xlsx` от Елены и доходит до подписанного Excel-файла сметы с живыми формулами. В итоговой версии тот же файл можно скачать прямо из Google Sheet, которую Елена заполняла онлайн.

Главная идея:

```text
Google Sheet (Елена правит цены/параметры)
→ скачать как xlsx
→ восстановить технические скрытые колонки
→ собрать calculator_input
→ запустить earthworks_calculator
→ сгенерировать Excel-смету с формулами
→ провалидировать Excel
→ записать статус в job_state.json
```

Весь контур запускается одной командой по `job_id`. Никакие чужие файлы не меняются.

## Что уже сделано

### Восьмишаговый локальный full flow

Скрипт `run_full_review_flow.py` последовательно запускает все 8 шагов:

```text
1. review_reader      — читает листы 01–03 review_workbook.xlsx → review_values_normalized.json
2. calculator_input   — собирает earthworks_calculation_input.json
3. lineage_report     — строит input_lineage_report.md/json
4. calculator         — запускает earthworks_calculator → calculation_result/result.json
5. formula_ready      — собирает formula_ready_result.json
6. anti_cheat         — проверяет coherence всех слоёв
7. excel_export       — генерирует earthworks_formula_review.xlsx с формулами
8. excel_validation   — валидирует Excel по layout и значениям
```

Если любой шаг завершается с ошибкой, весь flow останавливается с exit code != 0.

### Слой чтения review workbook

`review_workbook_reader.py` читает три листа stage1:

- `01_Проверка проекта` — проектные параметры (`pit_area_m2`, `pit_excavation_depth_m`, `trench_routes` и т.д.);
- `02_Цены себестоимости` — ценовые компоненты с ключом `calc_price_key` как source of truth;
- `03_Детали объемов` — справочные детали траншей.

`calc_price_key` в листе `02` — это ключ, по которому `calculator_input_builder` сопоставляет строки с полями калькулятора. Не `price_code`, не `name` — именно этот технический ключ.

### Происхождение данных (lineage)

`build_input_lineage_report.py` строит `input_lineage_report.json`, где для каждого поля `calculator_input` зафиксировано:

- `source` — откуда пришло значение (`sheet_01`, `sheet_02`, `default`, `missing`);
- `sheet`, `row` и `raw_value` — точный источник.

Это позволяет понять, почему цена именно такая, а не другая, даже через несколько месяцев.

### Layout-aware Excel валидатор

`validate_estimate_excel_workbook.py` проверяет сгенерированный Excel:

- наличие нужного листа с правильным заголовком;
- структуру строки-заголовка секции (`section_row`);
- наличие строк данных от `data_start_row`;
- формульные ячейки в колонках количество/цена/итог;
- соответствие итогов между Excel и `formula_ready_result.json`;
- anti-hardcode check: если в Excel стоит голое число там, где должна быть формула, это FAIL.

Параметры `--section-row` и `--data-start-row` принимаются через CLI, нулевых хардкодированных строк нет.

Результат сохраняется в `excel_validation_report.md`. В `full_review_flow_report.json` пишется `excel_validation_status`.

Проверено layout-proof: запуск с `--section-row 20 --data-start-row 21` возвращает 60+ ошибок, доказывая, что не один номер строки не зашит в коде.

### Google Sheet интеграция (Шаг 4B)

`build_from_google_sheet.py` выполняет полный цикл:

1. Читает `google/google_sheet_metadata.json` из Stage1 job dir → берёт `spreadsheet_id`;
2. Скачивает Google Sheet через Drive API `files().export_media()` как xlsx;
3. Восстанавливает скрытые технические колонки K:N в листе `02_Цены себестоимости`;
4. Запускает `run_full_review_flow.py` в подпроцессе;
5. Обновляет `job_state.json`.

**Важная деталь:** Google Sheets при экспорте в xlsx обрезает скрытые колонки. В `02_Цены себестоимости` скрыты колонки K:N (`calc_price_key`, `price_registry_code`, `fallback_key`, `selected_price_source`) — именно они нужны review_reader'у. Функция `_restore_hidden_columns()` копирует значения из локального `review_workbook.xlsx` обратно в скачанный файл и переставляет флаги `hidden=True`.

### Sharing Google Sheet (Шаг 4C)

В Stage1 добавлен аргумент `--sharing`:

```bash
python experiments/earthworks_parser_google_stage1/run_stage1.py prepare \
  --sharing anyone_writer
```

Допустимые значения:

```text
owner_only     — только владелец (по умолчанию)
anyone_reader  — чтение для всех по ссылке
anyone_writer  — редактирование для всех по ссылке
```

Разрешения устанавливаются через `drive.permissions().create()`. Scope `drive.file` достаточен: OAuth-приложение может управлять правами файлов, которые оно же создало.

Информация о sharing сохраняется в `google_sheet_metadata.json` и в `job_state.json`.

### Job state (Шаг 5)

`job_state.py` обеспечивает паспорт заказа в `job_state.json`:

```json
{
  "schema_version": 1,
  "job_id": "юсв_earthworks_stage1_20260622_191437",
  "project_name": "ЮСВ",
  "section_code": "earthworks",
  "section_title": "Земляные работы",
  "stage1": { ... },
  "google_sheet": { "status": "published", "sharing": { ... }, "url": "..." },
  "last_build": {
    "status": "passed",
    "excel_validation": "PASS",
    "totals": { "materials": ..., "works": ..., "section_total": ... },
    "key_values": { "pit_area_m2": ..., "excavator_shifts": ... }
  }
}
```

Файл живёт в Stage1 job dir, пути хранятся относительно `REPO_ROOT`.

`show_job_status.py` выводит читаемый дашборд. `update_after_build()` читает `calculation_result/result.json` и `full_review_flow_report.json` — абсолютных числовых ожиданий в коде нет.

### Job ID команды (Шаг 6)

`job_locator.py` резолвит короткий job_id в полный Path:

```python
resolve_stage1_job_dir("юсв_earthworks_stage1_20260622_191437")
→ experiments/earthworks_parser_google_stage1/data/jobs/юсв_earthworks_stage1_20260622_191437/
```

Только точное совпадение. Fuzzy search нет.

`build_job.py` — тонкая обёртка над `build_from_google_sheet.py`:

- принимает `--job-id`;
- находит stage1_job_dir через job_locator;
- создаёт timestamped out-dir `outputs/jobs/<job_id>/build_YYYYMMDD_HHMMSS/`;
- вызывает `build_from_google_sheet.py` в подпроцессе;
- возвращает тот же exit code.

`show_job_status.py` теперь принимает либо `--stage1-job-dir`, либо `--job-id` (mutually exclusive).

## Структура скриптов

```text
experiments/earthworks_review_to_calculator/
├── run_full_review_flow.py           — 8-шаговый full flow
├── review_workbook_reader.py         — чтение листов 01–03 review_workbook.xlsx
├── normalization.py                  — нормализация значений из Excel
├── constants.py                      — общие константы
├── run_review_reader.py              — CLI для step 1
├── calculator_input_builder.py       — сборка earthworks_calculation_input.json
├── run_build_calculator_input.py     — CLI для step 2
├── build_input_lineage_report.py     — step 3: lineage report
├── run_calculator_from_review_input.py — step 4: запуск calculator
├── build_formula_ready_result.py     — step 5: formula_ready_result.json
├── anti_cheat.py                     — step 6: cross-check всех слоёв
├── export_formula_ready_to_excel.py  — step 7: Excel export с формулами
├── validate_estimate_excel_workbook.py — step 8: layout-aware Excel validation
├── compare_calculation_results.py    — diagnostic comparison (не в flow)
├── build_from_google_sheet.py        — скачивание GSheet + full flow
├── job_state.py                      — паспорт заказа
├── job_locator.py                    — resolver job_id → Path
├── build_job.py                      — build по job_id
└── show_job_status.py                — статус по job_id или stage1-job-dir
```

## Что проверяет anti_cheat

Anti-cheat проходит через все слои и проверяет:

- `review_values_normalized.json` не содержит неизвестных полей;
- `earthworks_calculation_input.json` ссылается только на поля, для которых есть lineage;
- `formula_ready_result.json` и `calculation_result/result.json` согласованы;
- для каждой строки в formula_ready есть ровно одна строка в calculator_input;
- итоги формульного Excel совпадают с `formula_ready_result.json`.

## Что не входит в этот контур

- Telegram-бот.
- n8n workflow.
- Supabase или любая база данных.
- Изменения `earthworks_calculator`.
- Изменения `earthworks_parser_google_stage1`.
- Изменения `price_registry`.
- Клиентская (белая) часть сметы.
- Добавление новых разделов.
- Back-write данных в `price_registry`.
- Поиск заказов по project_name или fuzzy search.

## Ключевые артефакты

Stage1 job dir (создаётся stage1):

```text
experiments/earthworks_parser_google_stage1/data/jobs/<job_id>/
├── google/google_sheet_metadata.json
├── google/review_workbook.xlsx
├── job_state.json
├── reports/
├── pricing/
└── extracted/
```

Build outputs (создаются build_job.py):

```text
experiments/earthworks_review_to_calculator/outputs/jobs/<job_id>/build_YYYYMMDD_HHMMSS/
├── downloaded_review_workbook.xlsx
├── review_values_normalized.json
├── review_reader_report.md
├── earthworks_calculation_input.json
├── calculator_input_report.md
├── input_lineage_report.md
├── input_lineage_report.json
├── calculation_result/result.json
├── calculation_result_report.md
├── formula_ready_result.json
├── formula_ready_report.md
├── earthworks_formula_review.xlsx
├── excel_formula_export_report.md
├── excel_validation_report.md
└── full_review_flow_report.json
```

## Результат demo job (ЮСВ)

Последний проверенный прогон по демо-заказу ЮСВ:

```text
job_id: юсв_earthworks_stage1_20260622_191437
Google Sheet: published, sharing: anyone_writer / applied / writer

full_flow_status: clean
excel_validation: PASS

materials:      472 797
works:          375 902
section_total:  848 699

pit_area_m2:      322.5
excavator_shifts: 2.0
```

## Команды

### Создать Stage1 job с sharing

```bash
python experiments/earthworks_parser_google_stage1/run_stage1.py prepare \
  --sharing anyone_writer
```

### Собрать смету по job_id

```bash
python experiments/earthworks_review_to_calculator/build_job.py \
  --job-id "юсв_earthworks_stage1_20260622_191437" \
  --section-number 2 \
  --estimate-date 21.06.2026
```

### Посмотреть статус

```bash
python experiments/earthworks_review_to_calculator/show_job_status.py \
  --job-id "юсв_earthworks_stage1_20260622_191437"
```

### Локальный full flow без Google

```bash
python experiments/earthworks_review_to_calculator/run_full_review_flow.py \
  --review-workbook "experiments/earthworks_parser_google_stage1/data/jobs/<job_id>/google/review_workbook.xlsx" \
  --out-dir "experiments/earthworks_review_to_calculator/outputs/local_test" \
  --section-number 2 \
  --estimate-date 21.06.2026
```

## Зачем это важно

Этот контур закрывает полную петлю для раздела земляных работ:

```text
PDF проекта
→ Stage1: parser + review workbook + Google Sheet
→ Елена проверяет / правит параметры онлайн
→ build_job.py: скачивает → full flow → Excel смета с формулами → PASS
→ job_state.json: паспорт заказа с totals и validation status
```

Расчётная логика не меняется — только способ передачи входных данных. Елена видит живую Google Sheet, а мы получаем подписанный Excel с формулами и зафиксированным статусом проверки.

## Следующий шаг

Контур для земляных работ завершён. Следующий разумный шаг — распространить ту же архитектуру review → full flow → Excel export → job_state на другие разделы, или перейти к `box_calculator` как агрегатору готовых разделов.
