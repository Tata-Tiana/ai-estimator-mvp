# Current Project State

Этот файл — живая карта проекта `ai-estimator-mvp`. Он фиксирует текущую архитектуру, рабочие папки, что уже сделано и куда двигаться дальше.

Дата актуализации: `2026-07-05`.

## 0. Последняя расчётная контрольная точка

Текущая рабочая ветка:

```text
feature/foundation-slab-calculator-standards
```

Коммит расчётной базы:

```text
3682da0 Finalize foundation slab standards and metal delivery allocation
```

Это актуальная зафиксированная расчётная контрольная точка проекта перед текущими правками земляных работ. В неё вошли:

- проектная структура PDF/AI экспериментов;
- калькулятор земляных работ;
- калькулятор фундаментной плиты;
- калькулятор гидроизоляции фундаментной плиты;
- калькулятор несущих стен и перемычек;
- калькулятор плиты перекрытия 1-го этажа;
- калькулятор плиты перекрытия 2-го этажа;
- калькулятор плоской кровли;
- калькулятор вентиляционных каналов Schiedel;
- единый `price_code` для готовых калькуляторов;
- `price_registry_filled_v3.xlsx`;
- live-pricing режим для всех готовых калькуляторов;
- README, handoff, changelog и проектная документация.

Перед фиксацией проверены CLI-прогоны всех текущих экспериментальных калькуляторов. `pytest` собирает `0` тестов, поэтому рабочая проверка сейчас идёт через команды калькуляторов.

## 0.1. Live-Pricing Контрольная Точка

Реализован безопасный слой live-pricing:

```text
experiments/pricing/live_pricing.py
```

Поддерживаются режимы:

- `locked_case_prices` — дефолтный режим, цены берутся из `input.json`, старые `expected.json` остаются эталоном;
- `price_registry_with_fallback` — live-режим, цена берётся из `project_price_overrides`, затем из `price_registry`, затем fallback из `input.json` с warning.

Live-кейсы созданы для всех готовых разделов:

- earthworks;
- foundation_slab;
- waterproofing;
- load_bearing_walls_lintels;
- floor_slab_1;
- floor_slab_2;
- flat_roof;
- schiedel_vent_channels.

Сводный отчёт:

```text
experiments/pricing/output/live_pricing_sections_report.md
docs/report_live_pricing_layer.md
```

Live `expected.json` не создавались, потому что live-итоги могут отличаться от locked-итогов из-за актуальных цен.

## 0.2. Текущий PDF Pipeline После Последнего Коммита

После live-pricing контрольной точки добавлен новый рабочий слой подготовки параметров из PDF:

```text
experiments/pdf_parser_pipeline/
```

Он считается основным рабочим контуром для цепочки:

```text
PDF parser artifacts -> section review cards -> reviewed_parameters.xlsx -> будущий input_builder
```

Слой создаёт review cards по всем 8 готовым разделам и общий Excel для проверки Еленой:

```text
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/reviewed_parameters.xlsx
experiments/pdf_parser_pipeline/output/mvp_usv_demo/reviewed_parameters.xlsx
```

Более ранний `experiments/review_sheet_builder/` был промежуточным экспериментом и удалён, чтобы не держать два похожих контура. Рабочим путём считать `experiments/pdf_parser_pipeline/`.

Отчёт:

```text
docs/report_pdf_parser_pipeline.md
```

Дополнительно создан отдельный файл для Елены по незаполненным параметрам:

```text
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/elena_missing_parameters_by_section.xlsx
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/elena_missing_parameters_by_section.md
experiments/pdf_parser_pipeline/output/mvp_usv_demo/elena_missing_parameters_by_section.xlsx
experiments/pdf_parser_pipeline/output/mvp_usv_demo/elena_missing_parameters_by_section.md
```

Он строится из `reviewed_parameters.xlsx` и показывает, какие данные parser не нашёл. Внутри есть листы:

- `summary` — сводка по разделам;
- `for_designers` — проектные вопросы для проектировщиков;
- `estimator_manual` — сметные/технические параметры для ручного заполнения Еленой;
- `all_missing_raw` — полный raw-список missing/manual.

Labels в `section_schema.py` переведены на понятные русские названия, чтобы в таблицах не было голых технических строк вроде `code`, `name`, `diameter mm`.

## 0.3. Текущий input_builder

После PDF pipeline добавлен следующий экспериментальный слой:

```text
experiments/input_builder/
```

Он читает:

```text
experiments/pdf_parser_pipeline/output/mvp_usv_demo/reviewed_parameters.xlsx
```

и собирает промежуточные `input.json` для калькуляторов.

Важное:

- `input_builder` не читает PDF;
- `input_builder` не считает смету;
- калькуляторы не читают Excel напрямую;
- source of truth после проверки — `reviewed_parameters.xlsx`;
- `effective_value` считается в Python из `corrected_value`, `final_value`, `extracted_value`.

Режимы:

- `strict` — основной режим, required-параметры без значения блокируют раздел;
- `demo_with_template_fallback` — демонстрационный режим, недостающие значения берутся из template `input.json` только с явными warnings.

Текущий strict-прогон:

```text
sections_enabled = 8
sections_generated = 0
sections_blocked = 8
missing_required_total = 287
manual_required_total = 69
```

Это ожидаемо: Елена ещё не заполнила missing/manual параметры.

Отчёт:

```text
docs/report_input_builder.md
```

## 0.4. Текущий calculation_runner

После fallback-кейса `input_builder` добавлен demo-runner расчётов:

```text
experiments/calculation_runner/
```

Он берёт generated inputs:

```text
experiments/input_builder/output/mvp_usv_demo_fallback/generated_inputs/
```

и запускает существующие калькуляторы по 8 разделам.

Важное:

- режим текущего прогона — `demo_with_template_fallback`;
- это не production-расчёт и не финальная смета;
- недостающие параметры могли быть взяты из template `input.json`;
- старые калькуляторы и `expected.json` не менялись;
- по каждому разделу сохраняются `stdout.txt`, `stderr.txt`, `exit_code.txt`, `result.json`, `result.md`.

Текущий demo-run:

```text
sections_enabled = 8
sections_completed = 8
sections_failed = 0
sections_skipped = 0
total_materials = 8 185 731
total_works = 4 085 463
grand_total = 12 271 194
```

Отчёт:

```text
docs/report_calculation_runner.md
```

Следующий слой:

```text
box_calculator
```

## 0.5. Parameter Audit И Review-Pack Для Елены

После `calculation_runner` добавлен отдельный аудит missing/manual параметров:

```text
experiments/parameter_audit/
```

## 0.6. Новые стандарты фундаментной плиты

После созвонов с Еленой обновлён `foundation_slab_calculator`:

```text
experiments/foundation_slab_calculator/
```

Добавлены production-стандарты входных данных:

1. Опалубка бортов фундаментной плиты:

```text
formwork_calc_method = "spec_area"
slab_side_formwork_area_m2 = готовая площадь опалубки из спецификации
```

Старый расчёт `slab_formwork_perimeter_m * slab_edge_height_m` оставлен только как `legacy_perimeter_height` для старого проверочного кейса.

2. Термовставки:

```text
thermal_insert_mode = "standard_50_100"
```

Термовставки 50 мм и 100 мм считаются отдельно: работы по длине из спецификации, материалы по спецификации с запасом и округлением до кратности пачки. Старая логика термовкладыша 150 мм через элемент и деление длины на 0.6 оставлена только для legacy-кейса.

3. Фанера для опалубки:

```text
plywood_calc_method = "actual_area_with_waste"
plywood_sheet_width_m = 1.52
plywood_sheet_height_m = 1.52
plywood_waste_coeff = 1.05
```

Фанера считается от готовой площади опалубки, по листу `1.52 x 1.52 м`, с запасом 5% и округлением вверх до целого листа. Старый `working_area = 2.25 м2` оставлен только как legacy для старого кейса.

4. Арматура:

```text
rebar_calc_method = "spec_length_m"
```

В новом стандарте спецификация даёт арматуру в м.п., а вес считается автоматически через `kg_per_meter` для доставки и контроля плотности армирования. Старый режим `legacy_weight_to_length` оставлен для старого кейса.

Новые кейсы:

```text
experiments/foundation_slab_calculator/cases/test_foundation_slab_thermal_inserts_standard/
experiments/foundation_slab_calculator/cases/test_foundation_slab_formwork_spec_area/
experiments/foundation_slab_calculator/cases/test_foundation_slab_plywood_standard/
experiments/foundation_slab_calculator/cases/test_foundation_slab_rebar_spec_length/
```

Проверки:

```text
test_foundation_slab -> 229 ok / 0 mismatch
test_foundation_slab_thermal_inserts_standard -> 41 ok / 0 mismatch
test_foundation_slab_formwork_spec_area -> 25 ok / 0 mismatch
test_foundation_slab_plywood_standard -> 18 ok / 0 mismatch
test_foundation_slab_rebar_spec_length -> 55 ok / 0 mismatch
py_compile -> ok
```

Документы:

```text
docs/standard_input_contract.md
docs/report_thermal_inserts_refactor.md
docs/report_foundation_slab_formwork_refactor.md
docs/report_rebar_spec_length_refactor.md
```

После этого отдельным шагом обновлены `pdf_parser_pipeline` и `input_builder`:

- `section_schema.py` теперь показывает Елене `slab_side_formwork_area_m2` как актуальный проектный параметр опалубки;
- добавлены проектные параметры термовставок 50 мм и 100 мм;
- legacy-поля `slab_formwork_perimeter_m`, `slab_edge_height_m`, `thermal_insert_length_m`, `thermal_insert_piece_*` больше не являются production-вводом фундаментной плиты;
- `input_builder` берёт template фундаментной плиты из `test_foundation_slab_formwork_spec_area`;
- demo fallback input для фундаментной плиты собирается с `formwork_calc_method = "spec_area"` и `thermal_insert_mode = "standard_50_100"`.

Он читает текущий файл:

```text
experiments/pdf_parser_pipeline/output/mvp_usv_demo/reviewed_parameters.xlsx
```

и классифицирует 287 missing/manual параметров по источнику:

```text
AUTO_PROJECT = 140
AUTO_CALCULATED = 81
DEFAULT_VALUE = 26
PRICE_DATABASE = 7
MANUAL_REQUIRED = 33
```

Аудит ничего не внедряет автоматически:

- `section_schema.py` не меняется;
- калькуляторы не меняются;
- `expected.json` не меняются;
- параметры не скрываются из `reviewed_parameters.xlsx`.

Для созвона с Еленой подготовлен review-pack:

```text
experiments/parameter_audit/output/mvp_usv_demo/elena_parameter_review_pack.xlsx
experiments/parameter_audit/output/mvp_usv_demo/elena_parameter_review_agenda.md
```

В Excel по каждой строке добавлены пояснения:

- где параметр используется в смете;
- формула калькулятора;
- пример формулы на ЮСВ;
- что проверить Елене;
- зачем параметр нужен.

Назначение этапа — согласовать, что действительно остаётся ручным вводом, а что должно уйти в проектное извлечение, `price_registry`, defaults/material catalog или derived-parameters слой.

## 0.7. POC Excel-Сметы С Формулами По Гидроизоляции

Создан изолированный POC:

```text
experiments/excel_formula_poc_waterproofing/
```

Он генерирует Excel-файл:

```text
experiments/excel_formula_poc_waterproofing/output/waterproofing_formula_demo.xlsx
```

Назначение: проверить идею Excel-сметы в привычном виде сметчиц, но с живыми обычными A1-формулами.

Ключевое решение:

- видимый лист один — `Смета`;
- `A:I` — белая зона, технически копирует серую;
- `J:O` — серая внутренняя сметная зона;
- `P:V` — построчные helper-ячейки справа, без отдельной панели и без прайса;
- цены остаются в колонках `K` и `M`;
- клиентская часть не считается;
- POC работает только от frozen fixtures внутри своей папки.

Отчёт:

```text
docs/report_excel_formula_poc_waterproofing.md
```

Важно: это не production exporter и не часть `box_calculator`.

## 0.8. Земляные Работы: Production-Стандарты После Созвона С Еленой

После уточнений Елены обновлён калькулятор земляных работ:

```text
experiments/earthworks_calculator/
```

Добавлены production-режимы:

- `excavator_shifts_calc_method = "standard_volume_productivity"` — смены экскаватора считаются от объёма механизированной выемки;
- `manual_excavation_calc_method = "standard_routes"` — ручная разработка считается от ручной доработки котлована и выбранного объёма траншей;
- `communications_length_calc_method = "pipe_items"` — длина коммуникаций считается из труб спецификации.

Ключевые формулы:

```text
machine_excavation_volume_m3 = pit_area_m2 * pit_excavation_depth_m
excavator_shifts = ceil(machine_excavation_volume_m3 / 80)

manual_pit_volume_m3 = pit_area_m2 * 0.08
trench_volume_total_m3 = trench_volume_m3 из спецификации
  или sum(route_length_m * route_depth_m * 0.4)
manual_excavation_total_m3 = manual_pit_volume_m3 + trench_volume_total_m3

compacted_sand_trenches_m3 = trench_volume_total_m3 * sand_compaction_coeff

communications_length_m = sum(pipe_length_m * quantity)
  или sum(total_length_m)
```

Важно:

- `pit_excavation_depth_m` — глубина механизированной выемки котлована из проекта;
- `manual_refinement_depth_m = 0.08` — системная ручная доработка дна котлована;
- `trench_width_m = 0.4` — системная ширина траншеи;
- `excavator_productivity_m3_per_shift = 80` — системная производительность JCB по методике Елены;
- готовый `trench_volume_m3` из спецификации имеет приоритет над расчётом по трассам;
- один и тот же `trench_volume_total_m3` используется для ручной разработки и песка в траншеи;
- старые прямые значения `excavator_shifts`, `manual_excavation_quantity_for_estimate_m3`, `communications_length_m` сохранены только для legacy-кейсов.

Новые тестовые кейсы:

```text
test_excavator_shifts_standard -> 17 ok / 0 mismatch
test_manual_excavation_standard_routes -> 18 ok / 0 mismatch
test_manual_excavation_spec_trench_volume -> 18 ok / 0 mismatch
test_communications_pipe_items -> 21 ok / 0 mismatch
```

Полная проверка:

```text
horoshevka_14 -> ok (76/76)
test_communications_pipe_items -> ok (21/21)
test_excavator_shifts_standard -> ok (17/17)
test_manual_excavation_spec_trench_volume -> ok (18/18)
test_manual_excavation_standard_routes -> ok (18/18)
usv_yusupovo_village -> ok (100/100)
usv_yusupovo_village_live_prices -> ok (0/0)
py_compile -> ok
```

Документы:

```text
docs/report_earthworks_calculator.md
docs/report_earthworks_excavator_shifts_refactor.md
docs/report_earthworks_manual_excavation_refactor.md
docs/report_earthworks_communications_refactor.md
```

## 0.9. Earthworks Parser Google Stage 1

После стабилизации земляных расчётов добавлен отдельный изолированный контур проверки PDF-параметров через Google Sheet:

```text
experiments/earthworks_parser_google_stage1/
```

Назначение этого слоя:

- прочитать PDF проекта;
- собрать `review_workbook.xlsx` для Елены;
- опубликовать Google Sheet через OAuth;
- хранить технические листы `05_Кандидаты parser` и `06_Сырые данные parser` отдельно от человекочитаемых листов;
- выполнять clean-run без удаления секретов и исходных PDF;
- проверять, что builder и workbook совпадают по утверждённой структуре.

Что уже сделано внутри stage1:

- листы `01–04` зафиксированы для рабочего review-flow;
- лист `05_Кандидаты parser` сделан читаемым, без JSON-простыней;
- лист `06_Сырые данные parser` хранит summary, logical sheets, raw evidence и full JSON в разных блоках;
- `review_workbook_builder.py` и `anti_cheat.py` синхронизированы с workbook;
- clean-run и публикация Google Sheet проверены на реальном job;
- stage1 не пишет ничего обратно в общий `price_registry` и не запускает расчёт сметы.

Что специально не входит в этот контур:

- Telegram-бот и общий orchestration layer;
- общий `price_provider` для всех калькуляторов;
- back-write цен в `price_registry`;
- расчёт сметы после review;
- изменение `parser core` вне этого review-flow.

## 0.10. Earthworks Review To Calculator

Полный сквозной контур сборки сметы земляных работ от Google Sheet до подписанного Excel:

```text
experiments/earthworks_review_to_calculator/
```

### Что уже сделано

**8-шаговый full flow** (`run_full_review_flow.py`):

```text
1. review_reader      — читает листы 01–03 review_workbook.xlsx → review_values_normalized.json
2. calculator_input   — собирает earthworks_calculation_input.json
3. lineage_report     — строит input_lineage_report.md/json
4. calculator         — запускает earthworks_calculator → calculation_result/result.json
5. formula_ready      — собирает formula_ready_result.json
6. anti_cheat         — cross-check всех слоёв
7. excel_export       — генерирует earthworks_formula_review.xlsx с живыми формулами
8. excel_validation   — layout-aware валидация Excel (section_row / data_start_row)
```

**Google Sheet интеграция** (`build_from_google_sheet.py`):

- скачивает Google Sheet через Drive API → xlsx;
- восстанавливает скрытые колонки K:N в `02_Цены себестоимости` из локальной копии (Google Sheets обрезает их при экспорте);
- запускает full flow;
- обновляет `job_state.json`.

**Sharing Google Sheet** (Stage1 `--sharing`):

- `owner_only`, `anyone_reader`, `anyone_writer`;
- устанавливается через `drive.permissions().create()`.

**Job state** (`job_state.py`, `job_state.json` в Stage1 job dir):

- паспорт заказа: `job_id`, `project_name`, `google_sheet`, `last_build`;
- `last_build` содержит `excel_validation`, `totals`, `key_values`, `final_excel`;
- пути хранятся относительно `REPO_ROOT`.

**Job ID команды** (Шаг 6):

- `job_locator.py` — точный резолвер `job_id → Path`;
- `build_job.py` — обёртка с `--job-id`, создаёт timestamped out-dir `outputs/jobs/<job_id>/build_YYYYMMDD_HHMMSS/`;
- `show_job_status.py` — принимает `--job-id` или `--stage1-job-dir`.

### Проверенный demo job

```text
job_id: юсв_earthworks_stage1_20260622_191437
sharing: anyone_writer / applied / writer
full_flow_status: clean
excel_validation: PASS
section_total: 848 699
```

### Что специально не входит

- Google API изменения вне download/sharing;
- изменения `earthworks_calculator`;
- изменения Stage1 parser core;
- back-write в `price_registry`;
- web-server.

> Обновление: Telegram-бот из списка "не входит" выше был реализован после этой контрольной точки — см. 0.11.

### Команды

```bash
# создать Stage1 job с sharing
python experiments/earthworks_parser_google_stage1/run_stage1.py prepare \
  --sharing anyone_writer

# собрать смету по job_id
python experiments/earthworks_review_to_calculator/build_job.py \
  --job-id "юсв_earthworks_stage1_20260622_191437" \
  --section-number 2 \
  --estimate-date 21.06.2026

# посмотреть статус
python experiments/earthworks_review_to_calculator/show_job_status.py \
  --job-id "юсв_earthworks_stage1_20260622_191437"
```

Отчёт:

```text
docs/report_earthworks_review_to_calculator.md
```

## 0.11. Telegram-бот для сборки сметы земляных работ

После контрольной точки 0.10 добавлен production-контур приёма проекта от пользователя через Telegram:

```text
experiments/earthworks_review_to_calculator/telegram_bot.py   (~2170 строк)
```

Бот оборачивает уже существующий full review flow (0.10) интерфейсом для конечного пользователя (не только для разработчика с CLI):

- пользователь присылает PDF-файлы боту; после `QUIET_SECONDS` (5с) тишины или явной команды `/done` бот запускает `create_job_from_pdf.py` и весь 8-шаговый flow;
- батчинг PDF с защитой от гонки состояний (несколько файлов подряд не запускают parser дважды);
- восстановление сессии после падения/перезапуска бота (`telegram_sessions/`, backups в `backups/telegram_sessions/`);
- пользователь может пересобрать (`recreate_review_sheet.py`) или перезапустить парсинг (`rerun_parser.py`) для своих же job'ов без участия разработчика;
- админ-доступ: экспорт лога всех job'ов в Excel (`admin_exports/`), команда очистки тестовых job'ов;
- извлечение адреса проекта и уникальное имя Excel-файла по `job_id` (чтобы разные проекты не перетирали друг друга);
- anti_cheat сделан non-blocking для продакшн-потока (раньше мог полностью останавливать сборку) и принимает альтернативные названия чертежей схем коммуникаций;
- fallback на ручную длину и извлечение диаметра из названия трубы, когда pipe specs отсутствуют.

Хранилища бота:

```text
experiments/earthworks_review_to_calculator/data/telegram_uploads/
experiments/earthworks_review_to_calculator/data/telegram_logs/
experiments/earthworks_review_to_calculator/data/telegram_sessions/
experiments/earthworks_review_to_calculator/data/telegram_user_jobs/
experiments/earthworks_review_to_calculator/data/admin_exports/
```

(`telegram_uploads/` и `telegram_logs/` игнорируются git — см. `.gitignore`.)

Запуск бота требует `TELEGRAM_BOT_TOKEN` в `.env` (см. `.env.example`) и пакет `pyTelegramBotAPI`.

## 0.12. PDF Parser v3 — Evidence Layer + Generic Candidate Extractor + Parameter Resolver (серия A4)

Параллельно с Telegram-ботом ведётся отдельная экспериментальная ветка внутри диагностического парсера:

```text
experiments/usv_strict_pdf_parser_v3/     — evidence_layer.py, generic_candidate_extractor.py, text_normalization.py
experiments/pdf_parser_pipeline/parameter_resolver/   — resolver_engine.py, context_scorer.py, validation.py
```

**Важно:** это отдельный, ещё не подключённый к продакшену контур. Действующий Telegram-flow (0.11) читает старый `V3_CANDIDATES_PATH` через `earthworks_v3_adapter.py` и не использует `evidence.json` / `generic_candidates.json` / resolver. Цель серии A4 — постепенно заменить project-specific regex-парсинг обобщённым слоем evidence → typed candidates → resolver, который работает на любом похожем на USV проекте, а не только на известных значениях.

Пайплайн:

1. `evidence_layer.py` строит `evidence.json` из текста страниц, названий листов, строк таблиц и drawing index; таблицы — первичный источник, поэтому CAD PDF с пустым текстом страницы всё равно даёт evidence.
2. `generic_candidate_extractor.py` классифицирует evidence в типизированные кандидаты (`route_summary`, `pipe_item`, `pipe_piece_qty`, `label_value_quantity`, `material_quantity`, `table_quantity_row`, `unknown_relevant_quantity`, `elevation_marker`, `diameter_spec`) — только по стандартной русской инженерной лексике, без project-specific имён файлов/номеров страниц/захардкоженных значений.
3. `resolver_engine.py` (в `pdf_parser_pipeline/`) резолвит кандидатов в значение параметра по `resolver_hints` из `section_schema.py`: scoring по контексту, section-aware bonus/penalty (+0.10 та же секция, −0.15 чужая секция), конфликт при расхождении значений >10%, `collect_all` для агрегации списков.

Хронология (коммиты `afa7395` → `4b62d69` → `0a03893` → `63b7f3c`):

- **A4 + A4.2.2** — resolver слой (`resolve()`/`resolve_all()`) + пропагация `section_code` от страницы через evidence до кандидата; same-section scoring bonus; `section_code` заполненность выросла с 0% до 84% (127/151 кандидатов).
- **A4.2.5** — типы `elevation_marker` (координатные отметки, напр. `+3,250`) и `diameter_spec` (голый диаметр без полезной величины, напр. `Ø110 мм` без п.м/шт) выделены как отдельные типы кандидатов, а не игнорировались/не путались с длиной.
- **A4.2.5.1** (текущая точка, `63b7f3c`) — **eligibility guard**: `resolver_engine._AUXILIARY_TYPES = {'elevation_marker', 'diameter_spec'}` — эти типы теперь отфильтровываются до любого scoring, то есть отметки и голые диаметры труб физически не могут быть выбраны resolver'ом как значение параметра сметы (раньше был риск, что `+3,250` или `Ø110 мм` "выигрывали" как длина/глубина).

Статистика после guard (239 тестов зелёных: 206 + 33 новых):

```text
              candidates   resolver_eligible   auxiliary
USV                  168          125 (74%)     43 (37 elevation_marker + 6 diameter_spec)
TRC                  511          304 (60%)     207 (192 elevation_marker + 15 diameter_spec)
```

97 unknown-кандидатов по TRC разобраны: 58 — elevation_marker с координатных рамок чертежей (не приоритет), 3 pipe_item + 3 pipe_piece_qty — реальные дренажные трубы (ГОСТ + Ø110 + шт) на неклассифицированных страницах, кандидат на следующий шаг.

**Ближайший следующий шаг (не начат):** A4.2.8 — аудит unknown-кандидатов / обучение classifier row-level сигналам вида "ГОСТ + Ø110 + труба + шт/м.п + дренаж/ливневая канализация" → earthworks/communications, через generic-сигналы, а не конкретные значения.

**Обновление (2026-07-05 — 2026-07-06):** после `63b7f3c` добавлен третий smoke-проект MKP1 (первый АР+КР документ, не только КР — см. `docs/report_mkp1_smoke_test.md`) и два generic-бага исправлены отдельными коммитами: **A4.2.2** (`1192286`, table-level section classification / `table_override` — было реализовано и протестировано раньше, но не закоммичено, найдено и довнесено при подготовке следующего коммита), **A4.2.7** (`6596f76`, dimensions-filter gap + route-label/АР-код коллизия) и **A4.2.7.1** (`a25ca6b`, марка бетона В22/В25 vs route label В1/В2). Независимая проверка от 2026-07-06 подтвердила: A4.2.7.1 закрыт корректно, без нужды в доп. правках экстрактора.

**Финальное именование (2026-07-06, больше не переименовывать):** **A4.2.8** = row-level strong signals / unknown classification improvement — статус **backlog / deferred**, сейчас не делаем. **A4.2.9** = parser freeze / final parser handoff — статус **делается сейчас**. Подробности, обоснование и границы (Google Sheet/Telegram-flow не трогаем, требование к будущему A5 явно показывать unknown как needs_review) — см. `docs/report_mkp1_smoke_test.md`.

## 1. Цель проекта

`ai-estimator-mvp` — MVP AI-сметчика для частных домов.

Рабочая идея:

1. взять PDF-проект дома;
2. извлечь текст, таблицы и инженерные параметры;
3. собрать техническую карточку проекта;
4. на основе карточки и недостающих ручных вводов считать разделы сметы;
5. позже подключать УНИКМА для номенклатуры, цен, складов и остатков.

Важное разделение:

- AI помогает извлечь и структурировать входные параметры;
- расчёт сметы должен быть детерминированным Python-кодом;
- цены, коэффициенты, правила округления и строки сметы фиксируются явно.

## 2. Главный принцип структуры

Проект разделён на два слоя:

- `app/` — будущий стабильный код MVP;
- `experiments/` — исследовательские контуры и проверка гипотез.

Правило:

- всё экспериментальное сначала живёт в `experiments/`;
- после стабилизации переносится в `app/`;
- для серии домов результаты группируются по проектам, а не размазываются по `data/output`.

## 3. Верхний уровень

Ключевые файлы и папки:

- `app/` — каркас будущего приложения.
- `experiments/` — текущая активная рабочая зона.
- `docs/` — документация и карта проекта.
- `tests/` — заготовка будущих тестов стабильного приложения.
- `data/` — legacy/локальные входы и выходы первых экспериментов, плюс справочные выгрузки.
- `requirements.txt` — зависимости.
- `.env` — локальные ключи, не коммитится.
- `.gitignore` — защищает ключи, локальные PDF, результаты прогонов и тяжёлые артефакты.

## 4. Папка `app/`

`app/` пока остаётся каркасом будущего MVP.

Структура:

- `app/config.py` — общая конфигурация.
- `app/pdf/` — будущая стабильная логика PDF-извлечения.
- `app/ai/` — будущая стабильная AI-логика.
- `app/estimator/` — будущая стабильная логика расчёта сметы.
- `app/integrations/` — интеграции, включая будущий клиент УНИКМА.
- `app/reports/` — будущие отчёты.
- `app/storage/` — будущие хранилища промежуточных данных.

Сейчас реальные рабочие проверки идут в `experiments/`.

## 5. Папка `data/`

`data/` использовалась как первая общая зона входов и выходов.

Текущий статус:

- `data/input/pdf/` — старые исходные PDF Хорошевки 14.
- `data/output/pdf_experiments/` — старые результаты PDF-парсинга.
- `data/output/ai_project_cards/` — старый результат AI-карточки.
- `data/output/meeting_analysis/` — результаты анализа встреч.
- `data/output/unikma_tests/` — результаты тестов матчинга УНИКМА.
- `data/reference/unikma/` — справочные выгрузки УНИКМА.

Важно:

- для новых PDF/AI экспериментов основной путь теперь не `data/output`, а проектные папки внутри `experiments/`;
- старые файлы в `data/` не удалены, чтобы не потерять историю и не сломать ссылки в логах;
- `data/input/`, `data/output/` и тяжёлые выгрузки остаются локальными и не коммитятся.

## 6. Эксперименты

### 6.1. PDF-парсинг: `experiments/pdf_tests/`

Назначение:

- извлекать текст через PyMuPDF;
- извлекать блоки с координатами;
- извлекать таблицы через pdfplumber;
- сохранять результаты по каждому дому и каждой части PDF.

Ключевые файлы:

- `pdf_parser.py`
- `run_pdf_parser.py`
- `logger.py`
- `projects/README.md`

Новая рабочая структура:

```text
experiments/pdf_tests/projects/<project_name>/
├── input/
│   ├── kr1_below_floor.pdf
│   └── kr2_above_floor.pdf
├── output/
│   ├── kr1_below_floor/
│   │   ├── full_text.txt
│   │   ├── pages_text.json
│   │   ├── blocks.json
│   │   ├── tables.json
│   │   ├── tables.xlsx
│   │   └── summary.json
│   └── kr2_above_floor/
│       └── ...
└── notes.md
```

Актуальный проект:

- `experiments/pdf_tests/projects/horoshevka_14/`

Для Хорошевки 14:

- `kr1_below_floor.pdf` — КР1, ниже пола: фундамент, котлован, коммуникации, плита, сваи.
- `kr2_above_floor.pdf` — КР2, выше пола: стены, перекрытие/покрытие, кровля, вентканалы, навес.

Запуск:

```bash
.venv/bin/python3 experiments/pdf_tests/run_pdf_parser.py
```

Скрипт спрашивает:

- имя проекта, например `horoshevka_14`;
- имя части PDF, например `kr1_below_floor`;
- путь к PDF.

### 6.1.1. Рабочий PDF parser pipeline: `experiments/pdf_parser_pipeline/`

Назначение:

- брать готовые parser artifacts из `experiments/pdf_tests/projects/usv_yusupovo_village/`;
- строить section review cards по всем готовым разделам сметы;
- собирать общий `reviewed_parameters.xlsx` для проверки Еленой;
- готовить данные для будущего `input_builder`.

Рабочий кейс:

```text
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/
```

Создаёт:

```text
review_cards/
reviewed_parameters.xlsx
result.json
result.md
```

Output-дубль:

```text
experiments/pdf_parser_pipeline/output/mvp_usv_demo/
```

Разделы:

- `earthworks`;
- `foundation_slab`;
- `waterproofing`;
- `load_bearing_walls_lintels`;
- `floor_slab_1`;
- `floor_slab_2`;
- `flat_roof`;
- `schiedel_vent_channels`.

Запуск:

```bash
.venv/bin/python3 experiments/pdf_parser_pipeline/run_pdf_parser_pipeline.py experiments/pdf_parser_pipeline/cases/mvp_usv_demo
```

Текущий результат:

```text
review_cards = 8
missing_total = 287
manual_required_total = 69
```

Важное:

- `reviewed_parameters.xlsx` строится от `section_schema.py`, то есть от параметров, нужных калькуляторам;
- `extracted_parameters_for_review.json` остаётся диагностическим шумным слоем;
- если PDF не дал параметр, строка всё равно есть в Excel как `missing` или `manual_required`;
- найденные значения должны иметь `source_file`, `source_id`, `page`, `source_text`;
- parser/AI не считают смету.

Отчёт:

```text
docs/report_pdf_parser_pipeline.md
```

### 6.2. AI-карточка проекта: `experiments/ai_tests/`

Назначение:

- брать один или несколько `full_text.txt`;
- собирать общий текст;
- отправлять текст в OpenAI;
- получать техническую карточку проекта;
- сохранять карточку и вспомогательные Excel/Markdown артефакты.

Ключевые файлы:

- `run_project_card.py`
- `project_card_ai.py`
- `combine_project_texts.py`
- `prompts/project_card_prompt.txt`
- `projects/README.md`

Новая рабочая структура:

```text
experiments/ai_tests/projects/<project_name>/
├── input/
│   └── sources.json
├── output/
│   ├── full_text_combined.txt
│   ├── sources.json
│   ├── project_card_full.json
│   ├── project_card_full.md
│   ├── materials_extracted.xlsx
│   ├── estimate_scope_mapping.xlsx
│   ├── missing_data.txt
│   └── warnings.txt
└── notes.md
```

Актуальный проект:

- `experiments/ai_tests/projects/horoshevka_14/`

Источники карточки Хорошевки:

- `experiments/pdf_tests/projects/horoshevka_14/output/kr1_below_floor/full_text.txt`
- `experiments/pdf_tests/projects/horoshevka_14/output/kr2_above_floor/full_text.txt`

Запуск:

```bash
.venv/bin/python3 experiments/ai_tests/run_project_card.py
```

Скрипт теперь спрашивает имя проекта и сохраняет результат в `experiments/ai_tests/projects/<project_name>/output/`.

### 6.3. Калькулятор земляных работ: `experiments/earthworks_calculator/`

Назначение:

- проверять детерминированный расчёт раздела "Земляные работы";
- повторять серую внутреннюю часть сметы: материалы, работы, итоги;
- хранить отдельные кейсы по домам;
- сравнивать расчёт с эталонными значениями.

AI здесь не используется.

Структура:

```text
experiments/earthworks_calculator/
├── earthworks_calculator.py
├── run_earthworks_calc.py
├── run_all_cases.py
├── cases/
│   ├── index.md
│   ├── usv_yusupovo_village/
│   │   ├── input.json
│   │   ├── expected.json
│   │   └── notes.md
│   └── horoshevka_14/
│       ├── input.json
│       ├── expected.json
│       └── notes.md
└── output/
    ├── usv_yusupovo_village/
    └── horoshevka_14/
```

Что считает сейчас:

- смены экскаватора от объёма механизированной выемки в production-режиме;
- ручную доработку котлована;
- объём траншей: готовый объём из спецификации или расчёт по трассам;
- общую ручную разработку;
- песок под котлован и траншеи с коэффициентом уплотнения;
- заказ песка с округлением вверх к шагу машины;
- геотекстиль с нахлёстом и рулонами;
- длину технологических вводов коммуникаций по трубам спецификации в production-режиме;
- серые внутренние строки материалов и работ;
- внутренние итоги `internal_materials_total`, `internal_works_total`, `internal_section_total`.

Поддержка кейсов:

- `case_meta` — статус проверки и confidence.
- `assumptions` — грязные допущения и overrides.
- `enabled_lines` — какие строки серой сметы входят в конкретный кейс.
- `quantity_overrides` — явное повторение сметных количеств, когда они отличаются от формульного объёмного расчёта.
- `line_name_overrides` — отличия формулировок строк между сметами.

Кейсы:

- `usv_yusupovo_village`
  - разобран с Еленой;
  - `validated_with_elena = true`;
  - `confidence = high`;
  - включает коммуникации;
  - включает отдельную укладку геотекстиля;
  - итог: `805020`.

- `horoshevka_14`
  - не разбирался с Еленой дословно;
  - повторяет имеющуюся смету;
  - `validated_with_elena = false`;
  - `confidence = medium`;
  - нет коммуникаций в серой итоговой части;
  - работа геотекстиля сидит внутри строки материала;
  - используются overrides по ручной разработке, песку и геотекстилю;
  - итог: `559364`.

- `test_excavator_shifts_standard`
  - проверяет расчёт смен JCB по формуле `ceil((pit_area_m2 * pit_excavation_depth_m) / 80)`.

- `test_manual_excavation_standard_routes`
  - проверяет расчёт ручной разработки по трассам траншей.

- `test_manual_excavation_spec_trench_volume`
  - проверяет приоритет готового `trench_volume_m3` из спецификации.

- `test_communications_pipe_items`
  - проверяет расчёт `communications_length_m` из труб спецификации.

Запуск одного кейса:

```bash
.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py experiments/earthworks_calculator/cases/horoshevka_14
```

Запуск всех кейсов:

```bash
.venv/bin/python3 experiments/earthworks_calculator/run_all_cases.py
```

Текущий результат:

```text
horoshevka_14 -> ok (76/76)
test_communications_pipe_items -> ok (21/21)
test_excavator_shifts_standard -> ok (17/17)
test_manual_excavation_spec_trench_volume -> ok (18/18)
test_manual_excavation_standard_routes -> ok (18/18)
usv_yusupovo_village -> ok (100/100)
usv_yusupovo_village_live_prices -> ok (0/0)
```

### 6.4. Meeting Analysis: `experiments/meeting_analysis/`

Назначение:

- анализировать транскрипты созвонов с инженером-сметчиком;
- извлекать логику расчётов, формулы, открытые вопросы и требования к проектам.

Актуальные прогоны:

- тема: `earthworks`;
  - результаты: `data/output/meeting_analysis/2026-04-30_1818_earthworks/`;
  - эти материалы стали источником правил для первого калькулятора земляных работ.
- тема: `foundation_slab`;
  - входы: `experiments/meeting_analysis/input/2026-05-08_foundation_slab/`;
  - результаты: `data/output/meeting_analysis/2026-05-08_1125_foundation_slab/`;
  - материалы использовались для расчёта раздела фундаментной плиты и последующих уточнений с Еленой.
- тема: `load_bearing_walls_lintels`;
  - входы: `experiments/meeting_analysis/input/2026-05-15_load_bearing_walls_lintels/`;
  - результаты: `data/output/meeting_analysis/2026-05-15_1635_load_bearing_walls_lintels/`;
  - материалы использовались для расчёта несущих стен и перемычек.
- тема: `monolithic_floor_slab_1f_beams`;
  - входы: `experiments/meeting_analysis/input/2026-05-18_monolithic_floor_slab_1f_beams/`;
  - результаты: `data/output/meeting_analysis/2026-05-18_1839_monolithic_floor_slab_1f_beams/`;
  - материалы использовались для расчёта плиты перекрытия 1-го этажа.
- тема: `flat_roof`;
  - входы: `experiments/meeting_analysis/input/2026-05-22_flat_roof/`;
  - результаты: `data/output/meeting_analysis/2026-05-22_1103_flat_roof/`;
  - материалы использовались для расчёта плоской кровли.
- тема: `grillage_foundation`;
  - входы: `experiments/meeting_analysis/input/2026-05-26_grillage_foundation/`;
  - это raw input для будущего раздела "Устройство ростверкового фундамента";
  - отдельный docs-отчёт по созвону не делаем.

### 6.5. Калькулятор фундаментной плиты: `experiments/foundation_slab_calculator/`

Назначение:

- считать серую внутреннюю себестоимость раздела "Устройство фундаментной плиты дома, террасы, крыльца (250мм, 300мм)";
- хранить входные параметры, expected, notes и результат отдельным кейсом;
- сравнивать расчёт с эталонной серой сметой по стабильным `code`;
- не считать клиентскую часть.

Кейс:

- `test_foundation_slab`.

Текущий результат:

```text
test_foundation_slab -> ok (205/205)
internal_materials_total = 1454675
internal_works_total = 1083650
internal_section_total = 2538325
```

Что считается:

- мембрана PLANTER и PLANTERBAND;
- опалубка, фанера, пиломатериал;
- ЭППС/Пеноплэкс под плитой и в термовкладыше;
- арматура по универсальной схеме вес -> м.п. -> запас -> прутки -> закупочные м.п.;
- бетон, доставка бетона, бетононасос;
- fixed/manual строки: кран, доставка металла, логистика, расходники, технадзор.

Отчёт для руководства:

- `docs/report_foundation_slab_calculator.md`.

### 6.6. Калькулятор гидроизоляции фундаментной плиты: `experiments/waterproofing_calculator/`

Назначение:

- считать серую внутреннюю себестоимость блока "Гидроизоляция, утепление бортов плит";
- хранить расчёт отдельно от калькулятора фундаментной плиты;
- сверять строки и итоги со скрином серой сметы;
- не считать клиентскую часть.

Кейс:

- `test_waterproofing_foundation_slab`.

Текущий результат:

```text
test_waterproofing_foundation_slab -> ok (54/54)
waterproofing_base_subtotal = 48777
internal_materials_total = 33961
internal_works_total = 17255
internal_section_total = 51216
```

Что считается:

- гидроизоляция битумной мастикой в 2 слоя как работа;
- праймер AquaMast;
- мастика AquaMast;
- утепление стен плиты ЭППС 100 мм;
- Пеноплэкс ГЕО 100 мм с округлением до пачек;
- клей-пена по правилу 1 баллон на 10 м2, минимум 1;
- логистика 2% от базы;
- расходники 3% от базы.

Отчёт для руководства:

- `docs/report_waterproofing_calculator.md`.

### 6.7. Калькулятор несущих стен и перемычек: `experiments/load_bearing_walls_lintels_calculator/`

Назначение:

- считать серую внутреннюю себестоимость раздела "Внешние и внутренние несущие стены, перемычки";
- хранить расчёт отдельным экспериментальным калькулятором;
- сверять строки, raw-итоги и отображаемые итоги с серой внутренней сметой;
- не считать клиентскую часть.

Кейс:

- `test_load_bearing_walls_lintels`.

Текущий результат:

```text
test_load_bearing_walls_lintels -> ok
internal_materials_total_raw = 1550654.431
internal_materials_total = 1550654
internal_works_total_raw = 1121449.0
internal_works_total = 1121449
internal_section_total_raw = 2672103.431
internal_section_total = 2672103
```

Что считается:

- устройство лесов и подмостей;
- пиломатериал для лесов;
- гидроизоляция под первый ряд блоков;
- кладка внешних и внутренних несущих стен;
- газобетонные блоки D400 400 мм и D500 250 мм;
- монтажный клей и пескобетон;
- U-блоки/резка под перемычки;
- штробление и арматура Ø10 для несущих стен;
- доставка и разгрузка блоков;
- перемещение блоков автокраном;
- армирование и бетонирование перемычек;
- бетон и доставка бетона;
- парапет;
- кладка второго света / над кухней как case-specific addon;
- обкладка дымохода и вентканалов;
- клей, расходники, вывоз мусора и технадзор.

Важное по округлениям:

- Excel отображает строки округлёнными;
- итог раздела считается от raw-значений;
- поэтому в результате хранятся `*_raw` и отображаемые totals.

Отчёт для руководства:

- `docs/report_load_bearing_walls_lintels_calculator.md`.

### 6.8. Калькулятор плиты перекрытия 1-го этажа: `experiments/floor_slab_1_calculator/`

Назначение:

- считать серую внутреннюю себестоимость раздела "Ж/Б монолитная плита перекрытия 1-го этажа на отм. +3.480 (180 мм) с балками";
- хранить raw и display значения отдельно;
- сверять строки и итоги с `expected.json`;
- не считать клиентскую часть.

Кейс:

- `test_floor_slab_1`.

Текущий результат:

```text
test_floor_slab_1 -> ok (194/194)
internal_materials_total = 1175601
internal_works_total = 611926
internal_section_total = 1787527
```

Что считается:

- основная опалубка плиты;
- балки Б-1, Б-2, Б-3;
- опалубка балок и отбортовки;
- фанера и пиломатериал;
- арматура Ø25, Ø16, Ø12, Ø10, Ø8, Ø6;
- доставка арматуры/металла;
- бетонирование плиты и балок;
- бетон, доставка бетона, бетононасос;
- утепление торцов плиты/балок и низа плиты;
- ЭППС, клей-пена;
- логистика 1%, расходники 3%, технадзор fixed.

Важное:

- клиентская/белая зона для этого раздела пока не считается;
- Excel export для этого раздела пока не сделан;
- доставка металла позже должна считаться один раз в общем `box_calculator`;
- часть строк отображает округлённые количества, но суммы считаются от raw.

Отчёт для руководства:

- `docs/report_floor_slab_1_calculator.md`.

### 6.9. Калькулятор плиты перекрытия 2-го этажа: `experiments/floor_slab_2_calculator/`

Назначение:

- считать серую внутреннюю себестоимость раздела "Ж/Б монолитная плита перекрытия 2-го этажа на отм. +4.680 (200мм)";
- хранить raw и display значения отдельно;
- сверять строки, raw-итоги и отображаемые итоги с `expected.json`;
- не считать клиентскую часть.

Кейс:

- `test_floor_slab_2`.

Текущий результат:

```text
test_floor_slab_2 -> ok (222/222)
internal_materials_total_raw = 502761.38648
internal_materials_total = 502761
internal_works_total_raw = 214290
internal_works_total = 214290
internal_section_total_raw = 717051.38648
internal_section_total = 717051
sum_of_displayed_line_totals = 717052
```

Что считается:

- опалубка плиты перекрытия 2-го этажа;
- доставка опалубки и подача краном;
- расходники опалубки;
- фанера и пиломатериал для торцов;
- арматура Ø16, Ø12, Ø10;
- бетонирование плиты;
- бетон, доставка бетона, бетононасос;
- демонтаж опалубки;
- утепление торцов плиты;
- ЭППС 100 мм и клей-пена;
- логистика 1% и расходники 3%;
- нулевые строки структуры: технадзор, заготовительно-складские, накладные, сметная прибыль.

Важное:

- балок в расчёте нет;
- объём бетонирования `16.5 м3` пока manual/project quantity;
- высота утепления торца `0.18 м` оставлена для совпадения с текущей сметой;
- Excel export и клиентская/белая зона для этого раздела пока не сделаны.

Отчёт для руководства:

- `docs/report_floor_slab_2_calculator.md`.

### 6.10. Калькулятор плоской кровли: `experiments/flat_roof_calculator/`

Назначение:

- считать серую внутреннюю себестоимость раздела "КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА / плоская кровля";
- хранить raw и display значения отдельно;
- сверять строки и итоги с `expected.json`;
- не считать клиентскую часть.

Кейс:

- `test_flat_roof_usv`.

Текущий результат:

```text
test_flat_roof_usv -> ok (460/460)
internal_materials_total_raw = 1420802
internal_materials_total = 1420802
internal_works_total_raw = 618070
internal_works_total = 618070
internal_section_total_raw = 2038872
internal_section_total = 2038872
sum_of_displayed_line_totals = 2038872
```

Что считается:

- пароизоляция;
- ЭППС 100 мм, 50 мм и SLOPE плиты;
- геотекстиль;
- ПВХ мембрана и примыкания;
- рейки;
- аэраторы, воронки, отверстия, внутренний водосток;
- кран, расходники, вывоз мусора;
- логистика и снабжение, технадзор, заготовительно-складские расходы;
- нулевые строки структуры: накладные и общехозяйственные расходы, сметная прибыль.

Важное:

- итог сходится с серой зоной Excel за минусом временной двери ДН-1;
- временная дверь не включена в универсальный калькулятор;
- уклонные плиты берутся ручным объёмом от поставщика / Технониколь;
- базы логистики, расходников и заготовительно-складских расходов пока не автоматизированы;
- Excel export и клиентская/белая зона для этого раздела пока не сделаны.

Отчёт для руководства:

- `docs/report_flat_roof_calculator.md`.

### 6.11. Калькулятор вентиляционных каналов Schiedel: `experiments/schiedel_vent_channels_calculator/`

Назначение:

- считать серую внутреннюю себестоимость раздела "ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel";
- хранить raw и display значения отдельно;
- сверять строки и итоги с `expected.json`;
- не считать клиентскую часть.

Кейс:

- `test_schiedel_vent_channels_usv`.

Текущий результат:

```text
test_schiedel_vent_channels_usv -> ok (138/138)
internal_materials_total_raw = 36289.68
internal_materials_total = 36290
internal_works_total_raw = 81600
internal_works_total = 81600
internal_section_total_raw = 117889.68
internal_section_total = 117890
sum_of_displayed_line_totals = 117890
```

Что считается:

- кладка вентканалов Schiedel;
- вентиляционный канал 2х;
- вентиляционный канал 3х;
- доставка вентканалов;
- расходные материалы 3%;
- нулевые строки структуры: технадзор, заготовительно-складские, накладные, сметная прибыль.

Важное:

- кладка считается от raw `15.82 мп`;
- количества `24` и `8` по Schiedel являются ручными/specification inputs;
- контрольные правые числа не участвуют в расчёте quantity;
- Excel export и клиентская/белая зона для этого раздела пока не сделаны.

Отчёт для руководства:

- `docs/report_schiedel_vent_channels_calculator.md`.

### 6.12. УНИКМА: `experiments/unikma_api_tests/`

Назначение:

- тестировать API УНИКМА;
- скачивать прайс;
- смотреть склады/остатки;
- проверять черновой матчинг материалов.

Что уже проверено:

- `GetStores` работает;
- `GetNomenclatures` работает, но возвращает объект с `ArrayRef`;
- большой `Limit=5000` дал невалидный JSON;
- рабочая схема — постранично по `Limit=100`;
- `GetPriceFile` скачал Excel-прайс на `65 551` строку;
- первый кровельный фрагмент сметы был сопоставлен с прайсом.

Главный вывод:

- УНИКМА закрывает слой товаров, цен, складов и остатков;
- УНИКМА не заменяет расчётную логику сметы.

### 6.13. Price registry и pricing-layer: `experiments/pricing/`

Назначение:

- подготовить единый источник цен для MVP;
- не ломать старые сверенные калькуляторы;
- дать безопасный fallback на цены из `input.json`.

Подготовленные файлы:

```text
output/required_price_codes_v2.json
output/required_price_codes_v2.csv
output/price_registry_filled_v2.xlsx
output/price_registry_mapping_report_v2.md
output/price_registry_missing_codes_v2.csv
output/price_registry_ambiguous_matches_v2.csv
output/price_registry_unused_rows_v2.csv
output/price_registry_filled_v3.xlsx
output/price_registry_mapping_report_v3.md
```

Что сделано:

- в старые калькуляторы добавлено единое поле `price_code` для строк с ценой или ставкой;
- `material_price_code` и `work_rate_code` не добавлялись;
- формулы и expected не менялись;
- текущий режим расчётов остаётся `locked_case_prices`;
- новый слой цен живёт отдельно и пока не подключён к калькуляторам.

Папка pricing-layer:

```text
experiments/pricing/
├── price_reader.py
├── validate_price_registry.py
├── check_required_codes_against_registry.py
├── test_price_reader_demo.py
├── README.md
└── output/
```

Режимы:

- `locked_case_prices` — цены берутся из входов кейса, старое поведение;
- `price_registry_with_fallback` — будущий режим с приоритетом:

```text
project_price_overrides
↓
price_registry
↓
input.json fallback
```

Состояние покрытия `price_registry_v3`:

```text
required unique price_code = 81
found in price_registry = 18
found in rows_to_add = 63
missing completely = 0
fallback needed = 63
```

Отчёты:

```text
experiments/pricing/output/price_registry_validation_report.md
experiments/pricing/output/required_codes_coverage_report.md
```

Важные решения:

- исходный прайс не перезаписывается;
- спорные единицы измерения вынесены в report как `requires_decision`;
- если `price_code` не найден в `price_registry`, resolver возвращает fallback-цену и warning;
- клиентская часть сметы не считается.

## 7. Документация

Файлы:

- `docs/current_project_state.md` — живая карта проекта.
- `docs/assistant_handoff.md` — краткий handoff для нового чата/агента.
- `docs/change_log.md` — человеческая история контрольных точек.
- `docs/api_unikma_notes.md` — заметки по API УНИКМА.
- `docs/git_github_workflow.md` — рабочие правила git/GitHub.
- `docs/mvp_scope.md` — границы MVP.
- `docs/project_notes.md` — короткие проектные заметки и договорённости.
- `docs/report_pdf_parser.md` — отчёт по PDF-парсеру.
- `docs/report_pdf_parser_pipeline.md` — отчёт по рабочему pipeline PDF -> review cards -> reviewed_parameters.xlsx.
- `docs/report_earthworks_calculator.md` — отчёт по калькулятору земляных работ.
- `docs/report_foundation_slab_calculator.md` — отчёт по калькулятору фундаментной плиты.
- `docs/report_floor_slab_1_calculator.md` — отчёт по калькулятору плиты перекрытия 1-го этажа.
- `docs/report_floor_slab_2_calculator.md` — отчёт по калькулятору плиты перекрытия 2-го этажа.
- `docs/report_flat_roof_calculator.md` — отчёт по калькулятору плоской кровли.
- `docs/report_schiedel_vent_channels_calculator.md` — отчёт по калькулятору вентиляционных каналов Schiedel.
- `docs/report_waterproofing_calculator.md` — отчёт по калькулятору гидроизоляции.
- `docs/report_load_bearing_walls_lintels_calculator.md` — отчёт по калькулятору несущих стен и перемычек.

## 8. Текущее состояние

Сейчас проект умеет:

- парсить PDF проекта;
- строить section review cards и `reviewed_parameters.xlsx` для Елены через `experiments/pdf_parser_pipeline/`;
- хранить PDF/AI эксперименты по папкам домов;
- собирать AI-карточку проекта;
- анализировать встречи с инженером;
- тестировать УНИКМА;
- считать раздел сметы "Земляные работы" на двух кейсах;
- считать раздел "Устройство фундаментной плиты" на тестовом кейсе;
- считать блок "Гидроизоляция, утепление бортов плит" на тестовом кейсе.
- считать раздел "Внешние и внутренние несущие стены, перемычки" на тестовом кейсе.
- считать раздел "Ж/Б монолитная плита перекрытия 1-го этажа" на тестовом кейсе.
- считать раздел "Ж/Б монолитная плита перекрытия 2-го этажа" на тестовом кейсе.
- считать раздел "КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА / плоская кровля" на тестовом кейсе.
- считать раздел "ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel" на тестовом кейсе.
- хранить единый `price_code` в строках готовых калькуляторов.
- проверять покрытие `price_code` через `experiments/pricing/`.
- распределять доставку арматуры/металла на уровне `experiments/box_calculator/` как recommended allocation без прибавления поверх legacy totals.
- принимать PDF проекта от пользователя через Telegram-бота и вести пользователя по всему review flow земляных работ (`experiments/earthworks_review_to_calculator/telegram_bot.py`) — см. 0.11.
- в отдельном экспериментальном контуре (не подключён к продакшену) извлекать типизированные кандидаты значений из PDF (evidence → generic candidates → resolver) и резолвить их в значения параметров с section-aware scoring — см. 0.12.

При этом:

- PDF/AI результаты всё ещё экспериментальные;
- рабочий слой подготовки параметров из PDF — `experiments/pdf_parser_pipeline/`;
- устаревший `experiments/review_sheet_builder/` удалён;
- расчётные калькуляторы пока живут в `experiments/`, не в `app/`;
- клиентская цена, рентабельность, НР/СП/ТН пока не считаются;
- УНИКМА пока не подключён к расчётному модулю.
- `price_registry_with_fallback` пока не подключён к калькуляторам как основной режим.
- `box_calculator` пока реализует только первый безопасный блок: `recommended_metal_delivery_allocation`.

## 9. Что считать стабильной базой

Стабильной базой можно считать:

- структуру проекта;
- разделение `app/` и `experiments/`;
- новую проектную организацию PDF и AI экспериментов;
- детерминированный калькулятор земляных работ;
- детерминированный калькулятор фундаментной плиты;
- детерминированный калькулятор гидроизоляции фундаментной плиты;
- детерминированный калькулятор несущих стен и перемычек;
- детерминированный калькулятор плиты перекрытия 1-го этажа;
- детерминированный калькулятор плиты перекрытия 2-го этажа;
- детерминированный калькулятор плоской кровли;
- детерминированный калькулятор вентиляционных каналов Schiedel;
- единый `price_code` в готовых калькуляторах;
- `price_registry_v3` и отдельный pricing-layer с fallback;
- рабочий pipeline `PDF parser artifacts -> review cards -> reviewed_parameters.xlsx`;
- первый слой `box_calculator` для распределения доставки металла по общему весу коробки;
- формат кейсов `input.json`, `expected.json`, `notes.md`;
- агрегированный запуск `run_all_cases.py`;
- production Telegram-бот приёма PDF и сборки сметы земляных работ (0.11) — реально используется пользователем, не демо.

## 10. Что остаётся экспериментом

Экспериментально:

- качество AI-карточки;
- полнота `materials_extracted`;
- правила переноса проверенных PDF-параметров в расчётные inputs;
- будущий `input_builder` из `reviewed_parameters.xlsx`;
- дальнейшее развитие `box_calculator` в полноценный агрегатор всех разделов;
- расчёт следующих разделов сметы;
- матчинг материалов с УНИКМА;
- перенос расчётной логики в `app/`;
- evidence → generic candidate → resolver слой (серия A4, 0.12) — диагностический, ещё не заменил project-specific extraction в продакшн-flow.

## 11. Ближайшие разумные шаги

1. Довести `box_calculator` от metal delivery allocation до полноценного агрегатора разделов.
2. Научить разделы отдавать `section_metal_weight_kg` / `section_rebar_delivery_weight_kg` единообразно.
3. Обновить Excel exporter так, чтобы он заменял legacy delivery line на allocation line и не задваивал доставку.
4. Добавить ещё несколько кейсов для уже сделанных калькуляторов, чтобы отделить универсальные правила от повторения конкретной сметы.
5. Постепенно превратить удачные экспериментальные структуры в стабильные модули `app/`.
6. Позже подключить УНИКМА к материалам, но не смешивать это с расчётной логикой.
7. После каждого крупного этапа обновлять `docs/assistant_handoff.md`, `docs/current_project_state.md` и `docs/change_log.md`.
8. A4.2.9 (делаем сейчас) — parser freeze / final parser handoff: зафиксировать финальные метрики после A4.2.7/A4.2.7.1, записать known limitations, объявить parser layer достаточным для перехода к A4.3. Без новых extraction rules, без чистки unknown до нуля.
9. A4.3 (следующий шаг после A4.2.9) — source-category audit: по каждому параметру всех 8 разделов `section_schema.py` определить категорию источника — `PDF_PROJECT` (должен быть напрямую в проектной документации), `PDF_DERIVED` (вычисляется из PDF-данных), `MANUAL_REVIEW` (требует ручного ввода/подтверждения), `CALCULATED` (считается калькулятором, не ищется в PDF), `PRICE` (из прайса), `DEFAULT_STANDARD` (нормативная константа), `CONTROL_ONLY` (только для проверки, не для расчёта), `INTERNAL_SERVICE` (служебный параметр калькулятора). Результат — CSV/MD/JSON аудит с колонками: `section_code`, `parameter_code`/`input_key`, `display_name`, `unit`, текущий input_type (если есть), `has_resolver_hints`, `proposed_source_category`, `resolver_required` (yes/no), `review_table_required` (yes/no), `reason`, `confidence`, `notes`. A4.3 не меняет calculator logic и не расширяет resolver_hints массово — сначала только аудит и карта источников.
10. A4.2.8 (backlog, отложено) — аудит unknown-кандидатов TRC/USV/MKP1 в resolver-слое, обучение classifier row-level сигналам (ГОСТ + Ø + труба + шт/м.п + дренаж/ливневая канализация → earthworks/communications). Добавляет новые правила. Не блокер для A4.3/A5 — вернуться точечно, если выяснится, что unknown реально мешает.
11. A5 (после A4.3) — all-sections review table. Обязана явно показывать resolved unknown-section кандидатов как строки `needs_review`, а не молча их скрывать. Отдельный новый экспорт — не замена существующей Google-таблицы земляных работ.
12. Решить, когда и как evidence/candidate/resolver слой (0.12) заменит или дополнит текущий `earthworks_v3_adapter.py`, который продакшн Telegram-flow (0.11) использует сейчас — пока не трогать ни старый Google Sheet, ни `earthworks_v3_adapter.py`, ни действующий production Telegram-flow.

## 12. Практическое правило

Для каждого нового дома:

1. PDF складывать в `experiments/pdf_tests/projects/<project_name>/input/`.
2. Parser artifacts хранить в `experiments/pdf_tests/projects/<project_name>/parsed/` и `merged/`.
3. Review cards и `reviewed_parameters.xlsx` собирать через `experiments/pdf_parser_pipeline/`.
4. AI-карточку, если нужна, хранить в `experiments/ai_tests/projects/<project_name>/`.
5. Расчётные кейсы хранить в соответствующем калькуляторе: `experiments/<calculator>/cases/<project_name>/`.
6. Все ручные допущения фиксировать в `notes.md`, `case_meta` и `assumptions`.
