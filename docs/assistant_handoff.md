# Assistant Handoff

Дата актуализации: `2026-06-22`.

Этот файл — главная точка входа для нового чата/агента. Если нужно быстро понять проект `ai-estimator-mvp`, начинать отсюда.

## Последняя расчётная контрольная точка

Текущая рабочая ветка:

```text
feature/foundation-slab-calculator-standards
```

Коммит расчётной базы:

```text
3682da0 Finalize foundation slab standards and metal delivery allocation
```

Смысл коммита:

- зафиксированы проектные папки PDF/AI;
- добавлены экспериментальные калькуляторы готовых разделов сметы;
- добавлен единый слой `price_code`;
- добавлен live-pricing режим для всех готовых калькуляторов;
- обновлена документация и handoff.

После этого коммита проект имел контрольную точку перед переходом к агрегированию коробки.

После этой контрольной точки добавлен новый рабочий PDF pipeline:

```text
experiments/pdf_parser_pipeline/
```

Он теперь считается основным путём подготовки параметров из PDF:

```text
PDF parser artifacts -> section review cards -> reviewed_parameters.xlsx -> будущий input_builder
```

Более ранний `experiments/review_sheet_builder/` был промежуточным экспериментом и удалён. В новых задачах по PDF-параметрам использовать `experiments/pdf_parser_pipeline/`.

После PDF pipeline добавлен следующий слой:

```text
experiments/input_builder/
```

Он читает проверочный Excel:

```text
experiments/pdf_parser_pipeline/output/mvp_usv_demo/reviewed_parameters.xlsx
```

и собирает generated `input.json` для калькуляторов.

Текущий status:

```text
strict mode:
  sections_enabled = 8
  sections_generated = 0
  sections_blocked = 8
  missing_required_total = 287
  manual_required_total = 69

demo_with_template_fallback:
  sections_generated = 8
  template fallback warnings = 287
```

Strict-результаты оставлены как основные. Demo fallback проверен только как smoke-test механики.

После fallback input_builder добавлен demo-runner расчётов:

```text
experiments/calculation_runner/
```

Он берёт:

```text
experiments/input_builder/output/mvp_usv_demo_fallback/generated_inputs/
```

и запускает существующие калькуляторы по 8 разделам.

Текущий demo-run:

```text
mode = demo_with_template_fallback
sections_enabled = 8
sections_completed = 8
sections_failed = 0
sections_skipped = 0
grand_total = 12 271 194
```

Это не production-расчёт и не финальная смета: часть missing-параметров была взята из template inputs в demo fallback режиме. Следующий слой — `box_calculator`.

### Earthworks Parser Google Stage 1

Отдельно от расчётной цепочки сейчас живёт изолированный review-flow для `earthworks`:

```text
experiments/earthworks_parser_google_stage1/
```

Он нужен не для расчёта, а для проверки PDF-параметров и цен перед расчётом.

Что уже сделано:

- `prepare` собирает свежий `review_workbook.xlsx` и публикует Google Sheet через OAuth;
- листы `01–04` остаются для Елены, лист `05` — короткая техническая диагностика candidates, лист `06` — raw/summary/full JSON;
- `clean` удаляет только generated jobs и не трогает исходные PDF, `.env`, `credentials.json` и `token.json`;
- `review_workbook_builder.py` и `anti_cheat.py` синхронизированы с утверждённой структурой;
- stage1 не пишет найденные цены обратно в общий `price_registry`;
- stage1 не заменяет `parser core`, `price resolver` или будущий Telegram-бот.

Что не входит в stage1:

- запуск расчёта сметы;
- общий `price_provider` на все разделы;
- публикация данных обратно в `price_registry`;
- интеграция с другими калькуляторами вне `earthworks`.

### Earthworks Review To Calculator

Полный сквозной контур от Google Sheet до подписанного Excel-файла сметы:

```text
experiments/earthworks_review_to_calculator/
```

8-шаговый full flow (`run_full_review_flow.py`):

```text
1. review_reader    — читает листы 01–03 review_workbook.xlsx
2. calculator_input — собирает earthworks_calculation_input.json
3. lineage_report   — строит input_lineage_report.md/json
4. calculator       — запускает earthworks_calculator
5. formula_ready    — собирает formula_ready_result.json
6. anti_cheat       — cross-check всех слоёв
7. excel_export     — генерирует earthworks_formula_review.xlsx с формулами
8. excel_validation — layout-aware валидация Excel (section_row / data_start_row)
```

Google Sheet интеграция (`build_from_google_sheet.py`):

- скачивает Google Sheet через Drive API → xlsx;
- восстанавливает скрытые колонки K:N в `02_Цены себестоимости` из локального `review_workbook.xlsx` (Google Sheets обрезает их при экспорте);
- запускает full flow;
- обновляет `job_state.json`.

Job ID команды:

- `job_locator.py` — точный резолвер `job_id → Path`;
- `build_job.py` — `--job-id`, создаёт timestamped out-dir;
- `show_job_status.py` — `--job-id` или `--stage1-job-dir`.

Ключевые команды:

```bash
# создать stage1 job с sharing
python experiments/earthworks_parser_google_stage1/run_stage1.py prepare \
  --sharing anyone_writer

# собрать смету по job_id
python experiments/earthworks_review_to_calculator/build_job.py \
  --job-id "юсв_earthworks_stage1_20260622_191437" \
  --section-number 2 \
  --estimate-date 21.06.2026

# статус
python experiments/earthworks_review_to_calculator/show_job_status.py \
  --job-id "юсв_earthworks_stage1_20260622_191437"
```

Проверенный demo job: `юсв_earthworks_stage1_20260622_191437`, sharing `anyone_writer`, `excel_validation = PASS`, `section_total = 848699`.

Что принципиально не меняется:

- `earthworks_calculator`;
- stage1 parser core;
- `price_registry`;
- back-write данных куда-либо.

После этого создан первый безопасный слой `box_calculator`:

```text
experiments/box_calculator/
```

На текущем этапе он реализует только распределение доставки арматуры/металла:

```text
recommended_metal_delivery_allocation
```

Правило:

```text
total_metal_delivery_trucks = ceil(total_box_metal_weight_kg / 10000)
```

Машины распределяются по разделам в порядке выполнения работ: первая машина назначается первому разделу с металлом, следующие — разделу, где накопленный вес пересёк очередную границу 10 тонн.

Проверочный кейс:

```text
experiments/box_calculator/cases/test_metal_delivery_allocation/
comparison = 12 ok / 0 mismatch
```

Важно: allocation пока не добавляется поверх section totals, потому что legacy-калькуляторы могут уже содержать строку доставки металла. Excel exporter позже должен заменить legacy delivery line на allocation line.

После calculation_runner добавлен аудит missing/manual параметров:

```text
experiments/parameter_audit/
```

Он классифицирует текущие 287 missing/manual параметров из `reviewed_parameters.xlsx`:

```text
AUTO_PROJECT = 140
AUTO_CALCULATED = 81
DEFAULT_VALUE = 26
PRICE_DATABASE = 7
MANUAL_REQUIRED = 33
```

Для созвона с Еленой создан review-pack:

```text
experiments/parameter_audit/output/mvp_usv_demo/elena_parameter_review_pack.xlsx
experiments/parameter_audit/output/mvp_usv_demo/elena_parameter_review_agenda.md
```

В pack по каждой строке есть пояснения:

- где используется в смете;
- формула калькулятора;
- пример формулы ЮСВ;
- что проверить Елене;
- зачем нужен параметр.

Важно: аудит пока ничего не внедряет. `section_schema.py`, калькуляторы и `expected.json` не менялись.

После audit/review-pack обновлён калькулятор фундаментной плиты под новые стандарты Елены:

```text
experiments/foundation_slab_calculator/
```

Новые режимы:

- `formwork_calc_method = "spec_area"` — площадь опалубки бортов берётся готовым значением `slab_side_formwork_area_m2` из спецификации;
- `formwork_calc_method = "legacy_perimeter_height"` — старый расчёт `perimeter * height` только для legacy-кейса;
- `plywood_calc_method = "actual_area_with_waste"` — production-фанера по листу `1.52 x 1.52 м`, запас 5%, округление вверх;
- `plywood_calc_method = "working_area"` — legacy-фанера через рабочую площадь `2.25 м2` только для старого кейса;
- `thermal_insert_mode = "standard_50_100"` — термовставки 50 мм и 100 мм считаются отдельными работами/материалами;
- `thermal_insert_mode = "legacy"` — старый термовкладыш 150 мм только для старого кейса.
- `rebar_calc_method = "spec_length_m"` — production-арматура приходит из спецификации в м.п.; вес считается через `kg_per_meter`;
- `rebar_calc_method = "legacy_weight_to_length"` — старый режим кг -> м.п. только для legacy-кейса.

Новые кейсы:

```text
experiments/foundation_slab_calculator/cases/test_foundation_slab_thermal_inserts_standard/
experiments/foundation_slab_calculator/cases/test_foundation_slab_formwork_spec_area/
experiments/foundation_slab_calculator/cases/test_foundation_slab_plywood_standard/
experiments/foundation_slab_calculator/cases/test_foundation_slab_rebar_spec_length/
```

Проверено:

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

Следующий слой тоже уже синхронизирован с этим стандартом:

- `experiments/pdf_parser_pipeline/section_schema.py` переведён на `slab_side_formwork_area_m2` и термовставки 50/100 мм;
- `reviewed_parameters.xlsx` и `elena_missing_parameters_by_section.*` пересобраны;
- `experiments/input_builder/section_input_registry.py` использует template `test_foundation_slab_formwork_spec_area`;
- demo fallback input фундаментной плиты больше не содержит legacy-полей старого термовкладыша.

Важно: другие калькуляторы и старый `expected.json` фундаментной плиты не менялись.

Также создан изолированный POC Excel-сметы с формулами по гидроизоляции:

```text
experiments/excel_formula_poc_waterproofing/
docs/report_excel_formula_poc_waterproofing.md
```

Смысл POC: проверить привычный Excel-вид сметчиц с живыми A1-формулами. Видимый лист `Смета`, белая зона копирует серую, правая область `P:V` — построчные helper-ячейки, цены остаются в `K/M`. Это не production exporter и не часть `box_calculator`.

После этого обновлён калькулятор земляных работ под новые стандарты Елены:

```text
experiments/earthworks_calculator/
```

Новые production-режимы:

- `excavator_shifts_calc_method = "standard_volume_productivity"` — смены JCB считаются как `ceil((pit_area_m2 * pit_excavation_depth_m) / 80)`;
- `manual_excavation_calc_method = "standard_routes"` — ручная разработка считается как `pit_area_m2 * 0.08 + trench_volume_total_m3`;
- `communications_length_calc_method = "pipe_items"` — длина коммуникаций считается из труб спецификации.

Правило траншей:

- если спецификация даёт готовый `trench_volume_m3`, он имеет приоритет;
- если готового объёма нет, траншеи считаются по трассам `length_m * depth_m * 0.4`;
- один и тот же `trench_volume_total_m3` используется для ручной разработки грунта и песка в траншеи.

Важно по глубинам:

- `pit_excavation_depth_m` — глубина механизированной выемки котлована;
- `manual_refinement_depth_m = 0.08` — ручная доработка дна котлована.

Новые кейсы:

```text
test_excavator_shifts_standard -> 17 ok / 0 mismatch
test_manual_excavation_standard_routes -> 18 ok / 0 mismatch
test_manual_excavation_spec_trench_volume -> 18 ok / 0 mismatch
test_communications_pipe_items -> 21 ok / 0 mismatch
```

Полный `run_all_cases.py` по земляным работам проходит без mismatch.

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

### 1.1. Рабочий PDF parser pipeline

Папка:

```text
experiments/pdf_parser_pipeline/
```

Кейс:

```text
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/
```

Что делает:

- читает готовые parser artifacts проекта ЮСВ;
- строит review cards по всем 8 готовым разделам;
- создаёт `reviewed_parameters.xlsx` для проверки Еленой;
- не меняет калькуляторы и `expected.json`;
- не считает смету.
- заменяет удалённый промежуточный `experiments/review_sheet_builder/`.

Созданные outputs:

```text
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/review_cards/
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/reviewed_parameters.xlsx
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/elena_missing_parameters_by_section.xlsx
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/elena_missing_parameters_by_section.md
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/result.json
experiments/pdf_parser_pipeline/cases/mvp_usv_demo/result.md
experiments/pdf_parser_pipeline/output/mvp_usv_demo/
```

Команда:

```bash
../.venv/bin/python3 experiments/pdf_parser_pipeline/run_pdf_parser_pipeline.py experiments/pdf_parser_pipeline/cases/mvp_usv_demo
```

Текущая проверка:

```text
review_cards = 8
missing_total = 287
manual_required_total = 69
py_compile -> ok
expected.json не изменялись
```

Файл `elena_missing_parameters_by_section.xlsx` показывает, какие параметры parser не нашёл:

- `summary` — сводка по разделам;
- `for_designers` — вопросы к проектировщикам/по проекту;
- `estimator_manual` — ручные сметные и технические параметры;
- `all_missing_raw` — полный список.

Labels для авто-параметров в `section_schema.py` переведены на русские человекочитаемые названия, чтобы в таблицах не было строк вида `code`, `name`, `diameter mm` без контекста.

Отчёт:

```text
docs/report_pdf_parser_pipeline.md
```

### 1.2. Input builder

Папка:

```text
experiments/input_builder/
```

Назначение:

- читает `reviewed_parameters.xlsx`;
- считает `effective_value` в Python;
- формирует `missing_parameters_report.md`;
- генерирует `input.json` для разделов, если хватает required-параметров;
- в strict-режиме блокирует разделы с missing required;
- в demo fallback режиме может временно брать значения из template inputs с warning.

Команда:

```bash
../.venv/bin/python3 experiments/input_builder/run_input_builder.py experiments/input_builder/cases/mvp_usv_demo
```

Отчёт:

```text
docs/report_input_builder.md
```

### 1.3. Calculation runner

Папка:

```text
experiments/calculation_runner/
```

Назначение:

- берёт generated inputs из `input_builder`;
- создаёт временные case folders;
- запускает существующие калькуляторы;
- сохраняет `stdout.txt`, `stderr.txt`, `exit_code.txt`, `result.json`, `result.md` по каждому разделу;
- собирает общий `result.json` и `result.md`;
- не меняет формулы и `expected.json`.

Команда:

```bash
../.venv/bin/python3 experiments/calculation_runner/run_calculation_runner.py experiments/calculation_runner/cases/mvp_usv_demo_fallback
```

Отчёт:

```text
docs/report_calculation_runner.md
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
- `2026-05-15_load_bearing_walls_lintels`;
- `2026-05-18_monolithic_floor_slab_1f_beams`;
- `2026-05-22_flat_roof`.

По созвонам хранятся входные материалы и локальные результаты анализа, но отдельные docs-отчёты по созвонам для работодателя не делаем. В docs фиксируем готовые расчётные артефакты и калькуляторы.

### 4. Калькулятор земляных работ

Папка:

```text
experiments/earthworks_calculator/
```

Проверенные кейсы:

```text
usv_yusupovo_village -> ok (100/100)
horoshevka_14 -> ok (76/76)
test_communications_pipe_items -> ok (21/21)
test_excavator_shifts_standard -> ok (17/17)
test_manual_excavation_spec_trench_volume -> ok (18/18)
test_manual_excavation_standard_routes -> ok (18/18)
usv_yusupovo_village_live_prices -> ok (0/0)
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
docs/report_earthworks_excavator_shifts_refactor.md
docs/report_earthworks_manual_excavation_refactor.md
docs/report_earthworks_communications_refactor.md
```

Production-стандарты:

- смены JCB считаются от объёма механизированной выемки: `ceil((pit_area_m2 * pit_excavation_depth_m) / 80)`;
- ручная разработка: `pit_area_m2 * 0.08 + trench_volume_total_m3`;
- `trench_volume_total_m3` берётся готовым `trench_volume_m3` из спецификации или считается по трассам `length_m * depth_m * 0.4`;
- `communications_length_m` считается из труб спецификации;
- legacy direct inputs оставлены только для старых кейсов.

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

### 8. Калькулятор плиты перекрытия 1-го этажа

Папка:

```text
experiments/floor_slab_1_calculator/
```

Кейс:

```text
test_floor_slab_1 -> ok (194/194)
```

Итоги:

```text
internal_materials_total = 1175601
internal_works_total = 611926
internal_section_total = 1787527
```

Считает серую внутреннюю себестоимость раздела "Ж/Б монолитная плита перекрытия 1-го этажа на отм. +3.480 (180 мм) с балками".

Важно:

- балки Б-1, Б-2, Б-3 считаются внутри раздела;
- raw/display значения хранятся отдельно;
- клиентская часть и Excel export для этого раздела пока не сделаны;
- доставка металла позже должна считаться один раз в общем `box_calculator`.

Отчёт:

```text
docs/report_floor_slab_1_calculator.md
```

### 9. Калькулятор плиты перекрытия 2-го этажа

Папка:

```text
experiments/floor_slab_2_calculator/
```

Кейс:

```text
test_floor_slab_2 -> ok (222/222)
```

Итоги:

```text
internal_materials_total_raw = 502761.38648
internal_materials_total = 502761
internal_works_total_raw = 214290
internal_works_total = 214290
internal_section_total_raw = 717051.38648
internal_section_total = 717051
sum_of_displayed_line_totals = 717052
```

Считает серую внутреннюю себестоимость раздела "Ж/Б монолитная плита перекрытия 2-го этажа на отм. +4.680 (200мм)".

Важно:

- балок нет, логика балок из 1-го этажа не переносилась;
- объём бетонирования `16.5 м3` — manual/project quantity;
- высота утепления торца `0.18 м` оставлена для совпадения с текущей сметой и вынесена в warning;
- клиентская часть и Excel export для этого раздела пока не сделаны;
- raw итог и сумма округлённых строк отличаются на 1 рубль, оба значения сохраняются.

Отчёт:

```text
docs/report_floor_slab_2_calculator.md
```

### 10. Калькулятор плоской кровли

Папка:

```text
experiments/flat_roof_calculator/
```

Кейс:

```text
test_flat_roof_usv -> ok (460/460)
```

Итоги:

```text
internal_materials_total = 1420802
internal_works_total = 618070
internal_section_total = 2038872
```

Считает серую внутреннюю себестоимость раздела "КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА / плоская кровля".

Важно:

- итог сходится с серой зоной Excel за минусом временной двери ДН-1;
- временная дверь не включена, потому что это case-specific строка;
- логистика и снабжение, технический надзор и заготовительно-складские расходы включены как manual fixed строки текущего scope;
- уклонные плиты берутся ручным объёмом от поставщика / Технониколь;
- клиентская часть и Excel export для этого раздела пока не сделаны.

Отчёт:

```text
docs/report_flat_roof_calculator.md
```

### 11. Калькулятор вентиляционных каналов Schiedel

Папка:

```text
experiments/schiedel_vent_channels_calculator/
```

Кейс:

```text
test_schiedel_vent_channels_usv -> ok (138/138)
```

Итоги:

```text
internal_materials_total = 36290
internal_works_total = 81600
internal_section_total = 117890
```

Считает серую внутреннюю себестоимость раздела "ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel".

Важно:

- кладка считается от raw `15.82 мп`, не от отображаемых `16 мп`;
- количества материалов `24` и `8` являются manual/specification input;
- контрольные правые числа сохранены справочно и не участвуют в quantity;
- 4 последние строки добавлены как нулевые строки структуры Excel;
- клиентская часть и Excel export для этого раздела пока не сделаны.

Отчёт:

```text
docs/report_schiedel_vent_channels_calculator.md
```

### 12. УНИКМА

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

### 13. Live-Pricing Layer

Папка:

```text
experiments/pricing/
```

Ключевой helper:

```text
experiments/pricing/live_pricing.py
```

Режимы:

- `locked_case_prices` — дефолтный режим, цены берутся из `input.json`, старые `expected.json` остаются эталоном;
- `price_registry_with_fallback` — live-режим для MVP, цена ищется в `project_price_overrides`, затем в `price_registry`, затем используется fallback из `input.json`.

Live-кейсы созданы для всех готовых калькуляторов:

- `earthworks`;
- `foundation_slab`;
- `waterproofing`;
- `load_bearing_walls_lintels`;
- `floor_slab_1`;
- `floor_slab_2`;
- `flat_roof`;
- `schiedel_vent_channels`.

Во всех live `result.json` есть `pricing_summary`, во всех live `result.md` есть блок `## Источники цен`.

Сводные отчёты:

```text
experiments/pricing/output/live_pricing_sections_report.md
docs/report_live_pricing_layer.md
```

Live `expected.json` не создавались.

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

Pricing-layer:

```bash
../.venv/bin/python3 experiments/pricing/validate_price_registry.py
../.venv/bin/python3 experiments/pricing/check_required_codes_against_registry.py
../.venv/bin/python3 experiments/pricing/test_price_reader_demo.py
```

PDF parser pipeline:

```bash
../.venv/bin/python3 experiments/pdf_parser_pipeline/run_pdf_parser_pipeline.py experiments/pdf_parser_pipeline/cases/mvp_usv_demo
```

Общий pytest:

```bash
../.venv/bin/python3 -m pytest
```

На момент фиксации `pytest` собирает `0` тестов; основные проверки сейчас идут через CLI калькуляторов.

## Что было проверено перед последней live-pricing контрольной точкой

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

floor_slab_1:
  ok (194/194)

floor_slab_2:
  ok (222/222)

flat_roof:
  ok (460/460)

schiedel_vent_channels:
  ok (138/138)

pricing:
  price_registry validation -> rows=131 filled=18 empty=113 duplicates=0
  required code coverage -> required=81 registry=18 rows_to_add=63 missing=0
  demo -> price_registry source and fallback warnings checked
  live_pricing_sections_report -> 8 sections

pdf_parser_pipeline:
  review_cards -> 8 sections
  reviewed_parameters.xlsx -> created
  missing_total -> 287
  manual_required_total -> 69

pytest:
  collected 0 items
```

## Price registry / pricing-layer

После Schiedel добавлен переходный слой цен:

```text
experiments/pricing/
output/price_registry_filled_v3.xlsx
output/price_registry_mapping_report_v3.md
```

Что важно:

- в готовые калькуляторы добавлено поле `price_code` для строк с ценой/ставкой;
- `material_price_code` и `work_rate_code` не вводились;
- формулы и `expected.json` не менялись;
- старый режим расчётов остаётся `locked_case_prices`;
- режим `price_registry_with_fallback` идёт через `project_price_overrides -> price_registry -> input fallback`;
- если цена не найдена в основном листе прайса, resolver возвращает fallback и warning;
- `price_registry_v3`: `81` required-код, `18` в основном листе, `63` в `rows_to_add`, `0` потерянных.

## Важные запреты

- Не считать клиентскую часть.
- Не добавлять рентабельность, НР/СП/ТН и коммерческие коэффициенты в экспериментальные калькуляторы.
- Не переписывать рабочие калькуляторы с нуля.
- Не подгонять mismatch молча.
- Если Excel отличается, сначала понять причину: строка, округление, отсутствующая строка или ручная корректировка.
- Любое отличие формульного расчёта от сметного количества фиксировать явно.

## Следующий разумный шаг

Следующий большой шаг — сделать `input_builder`, который будет читать проверенный `reviewed_parameters.xlsx` и собирать `input.json` для калькуляторов.

После `input_builder` разумно проектировать `box_calculator` как агрегатор готовых разделов.

Не начинать с Excel export, Telegram/n8n и новых калькуляторов, пока не зафиксирован путь `reviewed_parameters.xlsx -> input.json -> calculators`.

Для новых отдельных разделов по-прежнему использовать схему:

```text
input.json -> deterministic calculator -> expected.json -> result JSON/MD -> comparison -> report in docs
```

Перед новым большим этапом смотреть:

```text
docs/current_project_state.md
docs/project_notes.md
docs/change_log.md
```
