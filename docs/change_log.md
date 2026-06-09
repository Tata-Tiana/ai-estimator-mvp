# Change Log

Этот файл — человеческая карта изменений проекта.

Git хранит точную техническую историю коммитов, а этот файл объясняет простыми словами:

- что изменилось;
- зачем это было сделано;
- какие решения были приняты;
- к какой контрольной точке можно вернуться.

Правило:

- после значимого этапа добавлять запись в этот файл;
- указывать дату, ветку, коммит и смысл изменений;
- не дублировать весь `git diff`, а фиксировать проектный смысл.

## Как смотреть техническую историю

Короткий список коммитов:

```bash
git log --oneline --decorate
```

Подробности конкретного коммита:

```bash
git show <commit_hash>
```

Текущее состояние рабочей папки:

```bash
git status
```

Важно:

- коммит — это контрольная точка проекта;
- к коммиту можно вернуться, посмотреть его, создать от него новую ветку или откатить изменения;
- для обычной работы безопаснее не делать резкий откат, а создавать новую ветку от нужной точки.

## Контрольные точки

### 2026-06-09 — Финализированы production-стандарты калькулятора фундаментной плиты

- Ветка: `feature/foundation-slab-calculator-standards`
- Коммит: будет создан текущей фиксацией

Что закреплено:

- `formwork_calc_method = "spec_area"` — площадь опалубки приходит готовым значением `slab_side_formwork_area_m2` из спецификации;
- `thermal_insert_mode = "standard_50_100"` — термовставки 50 мм и 100 мм считаются отдельно;
- `plywood_calc_method = "actual_area_with_waste"` — фанера считается по листу `1.52 x 1.52 м`, с запасом 5%, с округлением вверх;
- `rebar_calc_method = "spec_length_m"` — арматура приходит из спецификации в м.п., вес считается через `kg_per_meter`;
- legacy-режимы сохранены для старого `test_foundation_slab` и переходных проверок;
- старый `expected.json` фундаментной плиты не менялся молча.

Новые/актуальные кейсы:

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
docs/report_foundation_slab_calculator.md
docs/report_foundation_slab_formwork_refactor.md
docs/report_thermal_inserts_refactor.md
docs/report_rebar_spec_length_refactor.md
```

### 2026-06-09 — Добавлен allocator доставки металла на уровне box_calculator

- Ветка: `feature/foundation-slab-calculator-standards`
- Коммит: будет создан текущей фиксацией

Что добавлено:

- создан новый слой `experiments/box_calculator/`;
- добавлен `metal_delivery_allocator.py`;
- доставка арматуры/металла считается по общему весу коробки кратно 10 тоннам;
- первая машина назначается первому разделу с металлом, следующие — разделу, где накопленный вес пересёк очередную границу 10 тонн;
- создан тест `test_metal_delivery_allocation`;
- result.md показывает общий вес металла, количество машин и распределение по разделам;
- allocation выводится как `recommended_metal_delivery_allocation`, не прибавляется поверх старых totals;
- добавлен warning против задвоения legacy delivery lines.

Проверки:

```text
box_calculator test_metal_delivery_allocation -> 12 ok / 0 mismatch
py_compile box_calculator -> ok
```

Важно:

- старые калькуляторы и старые `expected.json` не менялись;
- `rebar_metal_delivery_trucks` задокументирован как legacy/manual для старых кейсов и `AUTO_CALCULATED_BY_BOX` для production-потока;
- Excel exporter позже должен заменять legacy delivery line на allocation line.

### 2026-06-08 — Добавлен изолированный POC Excel-сметы с формулами по гидроизоляции

- Ветка: `poc/waterproofing-excel-formulas`
- Коммит: будет создан текущей фиксацией

Что добавлено:

- создан изолированный эксперимент `experiments/excel_formula_poc_waterproofing/`;
- POC работает только от frozen fixtures внутри своей папки;
- генерируется `waterproofing_formula_demo.xlsx` по разделу "Гидроизоляция, утепление бортов плит";
- видимый лист один — `Смета`;
- белая зона `A:I` технически копирует серую зону `J:O`;
- правая область `P:V` сделана как построчные helper-ячейки, а не отдельная панель;
- цены остаются в колонках сметной таблицы `K` и `M`;
- клиентская часть не считается;
- создан отчёт `docs/report_excel_formula_poc_waterproofing.md`.

Проверки:

```text
py_compile -> ok
Excel generated -> ok
Expected totals: materials = 33961, works = 17255, section_total = 51216
```

Важно:

- POC не внедрён в `box_calculator`;
- рабочие калькуляторы, `pricing`, `input_builder`, `pdf_parser_pipeline`, `calculation_runner` и demo app не менялись ради этого POC;
- следующий возможный шаг — отдельно проектировать production Excel exporter после решения по `box_calculator`.

### 2026-06-08 — Синхронизирован PDF/input contract фундаментной плиты с новым стандартом

- Ветка: `feature/ai-project-card` / текущая рабочая ветка
- Коммит: будет создан текущей фиксацией

Что изменено:

- `experiments/pdf_parser_pipeline/section_schema.py` переведён на production-поля фундаментной плиты:
  - `slab_side_formwork_area_m2`;
  - `thermal_insert_50_length_m`;
  - `thermal_insert_100_length_m`;
  - `thermal_insert_50_material_spec_qty`;
  - `thermal_insert_100_material_spec_qty`;
- legacy-поля старого расчёта опалубки и термовкладыша больше не попадают в production-ввод фундаментной плиты;
- review card фундаментной плиты и `reviewed_parameters.xlsx` пересобраны;
- `elena_missing_parameters_by_section.*` пересобран и теперь показывает Елене новые проектные вопросы по опалубке и термовставкам 50/100 мм;
- `experiments/input_builder/section_input_registry.py` теперь берёт template фундаментной плиты из `test_foundation_slab_formwork_spec_area`;
- demo fallback input фундаментной плиты собирается с `formwork_calc_method = "spec_area"` и `thermal_insert_mode = "standard_50_100"`;
- `calculation_runner` проверен на demo fallback: 8 разделов completed, 0 failed.

Проверки:

```text
pdf_parser_pipeline -> review_cards: 8, missing_total: 283, manual_required_total: 66
input_builder strict -> 8 blocked sections, как ожидается до проверки Еленой
input_builder demo_with_template_fallback -> 8 generated sections
calculation_runner demo_with_template_fallback -> 8 completed, 0 failed
py_compile -> ok
```

Важно:

- калькуляторы и старые `expected.json` не менялись;
- старый legacy-кейс фундаментной плиты сохранён;
- `slab_formwork_perimeter_m` всё ещё может встречаться в разделе гидроизоляции, потому что гидроизоляция пока считает площадь по своему старому правилу.

### 2026-06-04 — Обновлены стандарты фундаментной плиты: опалубка и термовставки

- Ветка: `feature/ai-project-card`
- Коммит: будет создан текущей фиксацией

Что изменено:

- в `foundation_slab_calculator` добавлен режим опалубки `formwork_calc_method`;
- production-режим `spec_area` считает площадь опалубки от готового значения `slab_side_formwork_area_m2` из спецификации;
- legacy-режим `legacy_perimeter_height` оставлен для старого кейса и формулы `perimeter * height`;
- добавлен режим термовставок `thermal_insert_mode = "standard_50_100"`;
- термовставки 50 мм и 100 мм теперь считаются отдельными строками работ и материалов;
- старая логика термовкладыша 150 мм через элемент и деление длины на 0.6 оставлена только как legacy;
- создан `docs/standard_input_contract.md`;
- созданы отчёты:
  - `docs/report_thermal_inserts_refactor.md`;
  - `docs/report_foundation_slab_formwork_refactor.md`;
- добавлены кейсы:
  - `test_foundation_slab_thermal_inserts_standard`;
  - `test_foundation_slab_formwork_spec_area`.

Проверки:

```text
test_foundation_slab -> 229 ok / 0 mismatch
test_foundation_slab_thermal_inserts_standard -> 41 ok / 0 mismatch
test_foundation_slab_formwork_spec_area -> 25 ok / 0 mismatch
py_compile -> ok
```

Важно:

- старый `expected.json` не изменён;
- другие калькуляторы не менялись;
- `pdf_parser_pipeline` и `input_builder` не менялись;
- следующий шаг на тот момент был обновить schema/reviewed parameters под новый input contract; он выполнен записью от 2026-06-08.

### 2026-06-03 — Добавлен аудит параметров и review-pack для Елены

- Ветка: `feature/ai-project-card`
- Коммит: будет создан текущей фиксацией

Что добавлено:

- создан новый эксперимент `experiments/parameter_audit/`;
- добавлен аудит текущих missing/manual параметров из `reviewed_parameters.xlsx`;
- создан `parameter_audit_result.xlsx` с листами:
  - `all_parameters_audit`;
  - `by_section_summary`;
  - `to_default_values`;
  - `to_price_database`;
  - `to_auto_calculated`;
  - `to_auto_project`;
  - `still_manual_required`;
  - `schema_changes`;
- создан `parameter_audit_report.md`;
- создан review-pack для созвона с Еленой:
  - `elena_parameter_review_pack.xlsx`;
  - `elena_parameter_review_agenda.md`;
- в review-pack по каждой строке добавлены пояснения:
  - где параметр используется в смете;
  - формула калькулятора;
  - пример формулы ЮСВ;
  - что проверить Елене;
  - зачем нужен параметр.

Результат аудита:

```text
parameters_audited = 287
AUTO_PROJECT = 140
AUTO_CALCULATED = 81
DEFAULT_VALUE = 26
PRICE_DATABASE = 7
MANUAL_REQUIRED = 33
```

Важно:

- аудит пока не внедрён в `pdf_parser_pipeline`;
- `section_schema.py` не менялся;
- калькуляторы не менялись;
- `expected.json` не менялись;
- параметры не скрывались из `reviewed_parameters.xlsx`;
- следующий шаг — обсудить review-pack с Еленой и только потом внедрять defaults/material catalog/derived parameters.

### 2026-06-02 — Добавлен calculation_runner для demo-запуска всех разделов

- Ветка: `feature/ai-project-card`
- Коммит: будет создан текущей фиксацией

Что добавлено:

- создан demo fallback case для `input_builder`:
  - `experiments/input_builder/cases/mvp_usv_demo_fallback/`;
  - `experiments/input_builder/output/mvp_usv_demo_fallback/`;
- создан новый слой `experiments/calculation_runner/`;
- runner берёт generated `input.json` из `input_builder`;
- создаёт временные case folders;
- запускает существующие калькуляторы по 8 разделам;
- сохраняет по каждому разделу:
  - `stdout.txt`;
  - `stderr.txt`;
  - `exit_code.txt`;
  - `result.json`;
  - `result.md`;
- создан docs-отчёт `docs/report_calculation_runner.md`.

Проверки:

```text
input_builder fallback -> ok
warnings = 324
template fallback warnings = 287
calculation_runner -> ok
sections_enabled = 8
sections_completed = 8
sections_failed = 0
sections_skipped = 0
grand_total = 12 271 194
py_compile -> ok
calculator files -> not changed
expected.json -> not changed
```

Важно:

- это demo-run в режиме `demo_with_template_fallback`;
- это не production-расчёт и не финальная смета;
- следующий шаг: `box_calculator`.

### 2026-06-01 — Добавлен input_builder для сборки input.json из reviewed_parameters.xlsx

- Ветка: `feature/ai-project-card`
- Коммит: `703b170 Add input builder experiment`

Что добавлено:

- создан новый слой `experiments/input_builder/`;
- добавлен registry по 8 готовым разделам;
- реализовано чтение `reviewed_parameters.xlsx`;
- реализован расчёт `effective_value` в Python:
  - `corrected_value`;
  - затем `final_value`;
  - затем `extracted_value`;
  - иначе missing;
- добавлены режимы:
  - `strict`;
  - `demo_with_template_fallback`;
- создан `missing_parameters_report.md`;
- создан docs-отчёт `docs/report_input_builder.md`.

Проверки:

```text
strict mode -> 8 sections blocked, missing_required_total = 287, manual_required_total = 69
demo_with_template_fallback -> 8 generated inputs, 287 template fallback warnings
py_compile -> ok
calculator files -> not changed
expected.json -> not changed
```

Следующий шаг:

- заполнить `reviewed_parameters.xlsx` после проверки Еленой;
- повторно запустить `input_builder`;
- затем переходить к запуску калькуляторов от generated inputs и к `box_calculator`.

### 2026-06-01 — Улучшены русские labels и файл missing-параметров для Елены

- Ветка: `feature/ai-project-card`
- Коммит: `03084cf Improve PDF parameter review labels`

Что изменено:

- в `experiments/pdf_parser_pipeline/section_schema.py` улучшены человекочитаемые русские названия параметров;
- авто-параметры из `input.json` теперь получают контекст: арматура, балки, перемычки, кровля, Schiedel и т.п.;
- добавлен генератор `build_elena_missing_parameters_report.py`;
- создан файл для Елены:
  - `experiments/pdf_parser_pipeline/cases/mvp_usv_demo/elena_missing_parameters_by_section.xlsx`;
  - `experiments/pdf_parser_pipeline/cases/mvp_usv_demo/elena_missing_parameters_by_section.md`;
  - дубль в `experiments/pdf_parser_pipeline/output/mvp_usv_demo/`;
- файл показывает, какие параметры parser не нашёл, с разделением на вопросы к проектировщикам и ручные сметные/технические параметры.

Проверки:

```text
pdf_parser_pipeline -> ok
review_cards = 8
missing_total = 287
manual_required_total = 69
py_compile -> ok
голые labels code/name/diameter mm/source weight parts kg -> не найдены
```

Калькуляторы и `expected.json` не изменялись.

### 2026-06-01 — Удалён устаревший review_sheet_builder после перехода на pdf_parser_pipeline

- Ветка: `feature/ai-project-card`
- Коммит: см. коммит `Remove deprecated review sheet builder`

Что изменено:

- старый `experiments/review_sheet_builder/` удалён, чтобы не путаться в двух похожих контурах;
- рабочий путь подготовки параметров из PDF теперь только `experiments/pdf_parser_pipeline/`;
- `reviewed_parameters.xlsx` создаётся через `pdf_parser_pipeline`;
- следующий шаг: `input_builder`.

Проверки перед удалением:

```text
pdf_parser_pipeline -> ok
review_cards = 8
reviewed_parameters.xlsx создан
missing_total = 287
manual_required_total = 69
py_compile -> ok
```

Калькуляторы и `expected.json` не изменялись.

### 2026-06-01 — Добавлен рабочий PDF parser pipeline для review cards

- Ветка: `feature/ai-project-card`
- Коммит: см. коммит `Add PDF parser pipeline`

Что добавлено:

- создан новый рабочий слой `experiments/pdf_parser_pipeline/`;
- добавлена schema по всем 8 готовым разделам сметы;
- создаются section review cards для:
  - earthworks;
  - foundation_slab;
  - waterproofing;
  - load_bearing_walls_lintels;
  - floor_slab_1;
  - floor_slab_2;
  - flat_roof;
  - schiedel_vent_channels;
- создаётся общий `reviewed_parameters.xlsx` для проверки Еленой;
- добавлен docs-отчёт `docs/report_pdf_parser_pipeline.md`.

Ключевые решения:

- рабочим контуром теперь считается `experiments/pdf_parser_pipeline/`;
- более ранний `experiments/review_sheet_builder/` был промежуточным экспериментом и удалён следующей контрольной точкой;
- таблица для Елены строится от schema параметров калькуляторов, а не только от найденных parser values;
- если параметр не найден в PDF, он всё равно попадает в Excel как `missing` или `manual_required`;
- значения без `source_file/source_id/page/source_text` не считаются найденными.

Проверки:

```text
review_cards: 8
reviewed_parameters.xlsx создан
missing_total = 287
manual_required_total = 69
py_compile -> ok
expected.json -> не изменялись
```

Следующий шаг:

- сделать `input_builder`, который будет собирать `input.json` калькуляторов из проверенного `reviewed_parameters.xlsx`.

### 2026-06-01 — Добавлен live-pricing режим для всех готовых калькуляторов

- Ветка: `feature/ai-project-card`
- Коммит: см. коммит `Add live pricing mode for all calculators`

Что добавлено:

- добавлен общий helper `experiments/pricing/live_pricing.py`;
- созданы live-кейсы для всех готовых разделов:
  - earthworks;
  - foundation_slab;
  - waterproofing;
  - load_bearing_walls_lintels;
  - floor_slab_1;
  - floor_slab_2;
  - flat_roof;
  - schiedel_vent_channels;
- во всех live `result.json` есть `pricing_summary`;
- во всех live `result.md` есть блок `Источники цен`;
- создан общий отчёт `experiments/pricing/output/live_pricing_sections_report.md`;
- создан docs-отчёт `docs/report_live_pricing_layer.md`.

Ключевые решения:

- `locked_case_prices` остаётся дефолтным эталонным режимом;
- `price_registry_with_fallback` используется только в отдельных live-кейсах;
- если `price_code` найден в `price_registry`, берётся цена из прайса;
- если `price_code` не найден, берётся fallback из `input.json` и сохраняется warning;
- старые `expected.json` не изменены;
- live `expected.json` не создавались.

Проверки:

```text
earthworks:
  horoshevka_14 -> ok (76/76)
  usv_yusupovo_village -> ok (100/100)

foundation_slab -> ok
waterproofing -> ok
load_bearing_walls_lintels -> ok
floor_slab_1 -> ok (194/194)
floor_slab_2 -> ok (222/222)
flat_roof -> ok (460/460)
schiedel_vent_channels -> ok (138/138)
```

Следующий шаг:

- `box_calculator`.

### 2026-05-31 — Добавлены единые price_code и pricing-layer MVP

- Ветка: `feature/ai-project-card`
- Коммит: см. последний коммит после этой записи

Что добавлено:

- в готовые старые калькуляторы добавлено единое поле `price_code` для строк с ценой/ставкой;
- отдельные `material_price_code` и `work_rate_code` не вводились;
- формулы калькуляторов и `expected.json` не менялись;
- создана версия прайса:
  - `output/price_registry_filled_v3.xlsx`;
  - `output/price_registry_mapping_report_v3.md`;
- создан отдельный слой цен:
  - `experiments/pricing/price_reader.py`;
  - `experiments/pricing/validate_price_registry.py`;
  - `experiments/pricing/check_required_codes_against_registry.py`;
  - `experiments/pricing/test_price_reader_demo.py`;
  - `experiments/pricing/README.md`.

Ключевые решения:

- старый режим расчёта остаётся `locked_case_prices`;
- новый режим `price_registry_with_fallback` пока существует как отдельный слой и не подключён к калькуляторам автоматически;
- приоритет будущего режима:

```text
project_price_overrides
↓
price_registry
↓
input.json fallback
```

Проверки:

```text
earthworks:
  horoshevka_14 -> ok (76/76)
  usv_yusupovo_village -> ok (100/100)

floor_slab_1 -> ok (194/194)
floor_slab_2 -> ok (222/222)
flat_roof -> ok (460/460)
schiedel_vent_channels -> ok (138/138)

price_registry validation:
  rows=131 filled=18 empty=113 duplicates=0

required code coverage:
  required=81 registry=18 rows_to_add=63 missing=0
```

Состояние `price_registry_v3`:

- `18` required-кодов уже есть в основном листе `price_registry`;
- `63` required-кода вынесены в лист `rows_to_add`;
- полностью потерянных required-кодов нет;
- спорные единицы измерения оставлены на ручное решение.

### 2026-05-26 — Добавлен калькулятор вентиляционных каналов Schiedel

- Ветка: `feature/ai-project-card`
- Коммит: `86795ea`

Что добавлено:

- создан отдельный экспериментальный калькулятор:
  - `experiments/schiedel_vent_channels_calculator/`;
- добавлен тестовый кейс:
  - `cases/test_schiedel_vent_channels_usv/input.json`;
  - `cases/test_schiedel_vent_channels_usv/expected.json`;
  - `cases/test_schiedel_vent_channels_usv/result.json`;
  - `cases/test_schiedel_vent_channels_usv/result.md`;
- добавлены:
  - `README.md`;
  - `notes.md`;
  - `docs/report_schiedel_vent_channels_calculator.md`.

Проверка:

```text
test_schiedel_vent_channels_usv -> ok (138/138)
internal_materials_total = 36290
internal_works_total = 81600
internal_section_total = 117890
```

Ключевые решения:

- калькулятор считает только серую внутреннюю себестоимость;
- кладка считается от raw `15.82 мп`, не от отображаемых `16 мп`;
- количества материалов Schiedel `24` и `8` являются ручными/specification inputs;
- контрольные правые числа сохранены справочно и не участвуют в quantity;
- 4 последние строки добавлены как нулевые строки структуры Excel;
- клиентская/белая часть и Excel export для этого раздела пока не делаются.

### 2026-05-26 — Добавлен калькулятор плоской кровли

- Ветка: `feature/ai-project-card`
- Коммит: `454c132`

Что добавлено:

- создан отдельный экспериментальный калькулятор:
  - `experiments/flat_roof_calculator/`;
- добавлен тестовый кейс:
  - `cases/test_flat_roof_usv/input.json`;
  - `cases/test_flat_roof_usv/expected.json`;
  - `cases/test_flat_roof_usv/result.json`;
  - `cases/test_flat_roof_usv/result.md`;
- добавлены:
  - `README.md`;
  - `notes.md`;
  - `docs/report_flat_roof_calculator.md`.

Проверка:

```text
test_flat_roof_usv -> ok (460/460)
internal_materials_total = 1420802
internal_works_total = 618070
internal_section_total = 2038872
```

Ключевые решения:

- калькулятор считает только серую внутреннюю себестоимость;
- итог сходится с серой зоной Excel за минусом временной двери ДН-1;
- временная дверь не включена, потому что это case-specific строка;
- логистика и снабжение, технический надзор и заготовительно-складские расходы включены как manual fixed строки текущего scope;
- уклонные плиты берутся ручным объёмом от поставщика / Технониколь;
- клиентская/белая часть и Excel export для этого раздела пока не делаются.

### 2026-05-22 — Добавлен docs-отчёт по калькулятору плиты перекрытия 1-го этажа

- Ветка: `feature/ai-project-card`
- Коммит: `1d549a3`

Что добавлено:

- создан отчёт:
  - `docs/report_floor_slab_1_calculator.md`;
- обновлены ссылки и статус в:
  - `README.md`;
  - `docs/assistant_handoff.md`;
  - `docs/current_project_state.md`;
  - `docs/change_log.md`.

Проверка калькулятора:

```text
test_floor_slab_1 -> ok (194/194)
internal_materials_total = 1175601
internal_works_total = 611926
internal_section_total = 1787527
```

Ключевые решения, зафиксированные в отчёте:

- калькулятор считает только серую внутреннюю себестоимость;
- балки Б-1, Б-2, Б-3 входят в расчёт 1-го этажа;
- raw/display значения хранятся отдельно;
- клиентская/белая часть и Excel export для этого раздела пока не сделаны;
- доставка металла позже должна считаться один раз в общем `box_calculator`.

### 2026-05-21 — Добавлен калькулятор плиты перекрытия 2-го этажа

- Ветка: `feature/ai-project-card`
- Коммит: `0a9ea77`

Что добавлено:

- создан отдельный экспериментальный калькулятор:
  - `experiments/floor_slab_2_calculator/`;
- добавлен тестовый кейс:
  - `cases/test_floor_slab_2/input.json`;
  - `cases/test_floor_slab_2/expected.json`;
  - `cases/test_floor_slab_2/result.json`;
  - `cases/test_floor_slab_2/result.md`;
- добавлены:
  - `README.md`;
  - `notes.md`;
  - `docs/report_floor_slab_2_calculator.md`.

Проверка:

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

Ключевые решения:

- калькулятор считает только серую внутреннюю себестоимость;
- клиентская/белая часть и Excel export для этого раздела пока не делаются;
- балок в плите 2-го этажа нет;
- объём бетонирования `16.5 м3` оставлен как manual/project quantity;
- высота утепления торца `0.18 м` оставлена для совпадения с текущей сметой и вынесена в warning;
- raw totals и сумма отображаемых округлённых строк сохраняются отдельно, потому что отличаются на 1 рубль.

### 2026-05-20 — Зафиксирована контрольная точка экспериментальных калькуляторов и документации

- Ветка: `feature/ai-project-card`
- Коммит: `20c9d05`
- Сообщение: `Add experimental estimate calculators and project handoff docs`

Что зафиксировано:

- проектные папки PDF/AI экспериментов;
- калькулятор земляных работ;
- калькулятор фундаментной плиты;
- калькулятор гидроизоляции фундаментной плиты;
- калькулятор несущих стен и перемычек;
- отчёты для руководства;
- README, handoff, current state, project notes и changelog.

Проверки перед коммитом:

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

Значение контрольной точки:

- это актуальная база для продолжения следующего раздела сметы;
- новый чат должен начинать с `docs/assistant_handoff.md`;
- подробная карта проекта находится в `docs/current_project_state.md`;
- рабочие правила и статусы кейсов находятся в `docs/project_notes.md`.

### 2026-05-15 — Калькуляторы фундаментной плиты, гидроизоляции и handoff-документация

- Ветка: текущая рабочая ветка
- Коммит: вошло в `20c9d05` от 2026-05-20

Что добавлено:

- создан `README.md` проекта с краткой картой текущего состояния;
- создан handoff для нового чата/агента:
  - `docs/assistant_handoff.md`;
- добавлены отчёты для руководства:
  - `docs/report_pdf_parser.md`;
  - `docs/report_earthworks_calculator.md`;
  - `docs/report_foundation_slab_calculator.md`;
  - `docs/report_waterproofing_calculator.md`;
- создан экспериментальный калькулятор фундаментной плиты:
  - `experiments/foundation_slab_calculator/`;
- создан экспериментальный калькулятор гидроизоляции фундаментной плиты:
  - `experiments/waterproofing_calculator/`.

Фундаментная плита:

```text
test_foundation_slab -> ok (205/205)
internal_materials_total = 1454675
internal_works_total = 1083650
internal_section_total = 2538325
```

Ключевые правила:

- PLANTERBAND = рулоны мембраны * 4;
- пиломатериал = площадь опалубки * 0.05, без коэффициента 1.5;
- фанера по текущему кейсу считается через рабочую площадь 2.25 м2, альтернативный метод через фактический лист и запас добавлен опционально;
- арматура считается по схеме вес -> м.п. -> запас -> прутки -> закупочные м.п.;
- доставка металла остаётся manual/fixed, но добавлен suggested trucks по правилу 10 тонн;
- клиентская часть не считается.

Гидроизоляция фундаментной плиты:

```text
test_waterproofing_foundation_slab -> ok (54/54)
waterproofing_base_subtotal = 48777
internal_materials_total = 33961
internal_works_total = 17255
internal_section_total = 51216
```

Ключевые правила:

- площадь гидроизоляции = внешний периметр плиты * высота борта;
- праймер и мастика округляются вверх до целых упаковок;
- площадь утепления ЭППС 100 мм берётся из спецификации, геометрия выводится как контроль;
- Пеноплэкс округляется до пачек;
- клей-пена = 1 баллон на 10 м2, минимум 1;
- логистика = 2% от базы;
- расходники = 3% от базы.

Что проверено:

- фундаментная плита сверена со скрином Excel; построчные суммы совпали, отличие Excel на 1 рубль в итогах признано округлением;
- гидроизоляция сверена со скрином Excel; все видимые строки и итоги совпали;
- existing `earthworks_calculator` не переписывался;
- existing `foundation_slab_calculator` не ломался при добавлении safe improvements;
- новые калькуляторы работают без AI и без клиентской части.

Важно:

- эта работа позже вошла в общий коммит `20c9d05`;
- перед продолжением следующего крупного раздела важно обновлять handoff/current state/changelog.

### 2026-05-06 — Проектные папки PDF/AI и калькулятор земляных работ

- Ветка: `feature/ai-project-card`
- Коммит: вошло в `20c9d05` от 2026-05-20

Что добавлено и изменено:

- PDF-эксперименты переведены на проектную структуру:
  - `experiments/pdf_tests/projects/<project_name>/input/`
  - `experiments/pdf_tests/projects/<project_name>/output/`
- Для Хорошевки 14 создана понятная структура:
  - `kr1_below_floor` — ниже пола, фундаментная часть;
  - `kr2_above_floor` — выше пола, стены/кровля/надземная часть.
- AI-эксперименты переведены на проектную структуру:
  - `experiments/ai_tests/projects/<project_name>/input/`
  - `experiments/ai_tests/projects/<project_name>/output/`
- AI-карточка Хорошевки 14 перенесена в:
  - `experiments/ai_tests/projects/horoshevka_14/`
- Создан экспериментальный калькулятор земляных работ:
  - `experiments/earthworks_calculator/`
- В калькуляторе заведены два кейса:
  - `usv_yusupovo_village`;
  - `horoshevka_14`.
- Добавлен индекс кейсов:
  - `experiments/earthworks_calculator/cases/index.md`.
- Добавлен агрегированный запуск:
  - `experiments/earthworks_calculator/run_all_cases.py`.

Что проверено:

```text
horoshevka_14 -> ok (76/76)
usv_yusupovo_village -> ok (100/100)
```

Итоги серой внутренней части земляных работ:

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

Ключевые решения:

- новые PDF/AI эксперименты группировать по домам внутри `experiments/.../projects/`;
- расчётные кейсы хранить как `input.json`, `expected.json`, `notes.md`;
- для каждого кейса фиксировать `case_meta` и `assumptions`;
- сметные расхождения с формульным расчётом задавать явно через `quantity_overrides`, а не прятать в коде;
- пока считать только внутреннюю себестоимость раздела, без клиентских коэффициентов, рентабельности, НР/СП/ТН.

### 2026-05-05 — Meeting Analysis и первый реальный тест УНИКМА

- Ветка: `feature/ai-project-card`
- Коммит: `4f376af`
- Сообщение: `Add meeting analysis and Unikma API notes`

Что добавлено:

- экспериментальный CLI `experiments/meeting_analysis/` для анализа транскриптов созвонов с инженером-сметчиком;
- промпты для:
  - краткого резюме созвона;
  - логики расчётов;
  - формул;
  - открытых вопросов и требований к проектировщикам;
- поддержка точечных примеров в `examples/`:
  - скрины сметы;
  - PDF-листы;
  - текстовые/CSV-примеры;
- документация по входным и выходным файлам meeting analysis;
- тестовый список кровельных позиций из скринов сметы:
  - `experiments/unikma_api_tests/samples/roofing_from_screenshot.txt`;
- подробный отчёт по первому реальному тесту API УНИКМА:
  - `docs/api_unikma_notes.md`;
- обновлённая живая карта проекта:
  - `docs/current_project_state.md`.

Что проверено:

- `GetStores` работает;
- `GetNomenclatures` работает, но возвращает объект с `ArrayRef`;
- большой `Limit=5000` для номенклатуры дал HTTP 200, но невалидный JSON;
- рабочий способ загрузки номенклатуры — постранично по `Limit=100`;
- `GetPriceFile` успешно скачал Excel-прайс;
- прайс на `65 551` строку оказался полезнее для первичного поиска цен;
- проведён черновой матчинг `22` кровельных строк со сметного скрина;
- черновая сумма только по найденным товарным позициям: `1 020 210 руб.`

Ключевые технические изменения:

- API-ключ УНИКМА теперь маскируется в логах;
- клиент УНИКМА нормализует `ArrayRef` в обычный список;
- `run.py` умеет читать локальные JSON как в формате списка, так и в формате объекта с `ArrayRef`;
- `.gitignore` защищает реальные транскрипты, скрины, результаты прогонов, прайсы и API-выгрузки от случайного коммита.

Главный вывод:

- УНИКМА API полезен как источник товаров, цен, складов и остатков;
- он не заменяет расчетную логику сметы;
- для MVP нужен отдельный слой `material matching`, который:
  - отличает материалы от работ и услуг;
  - ищет кандидатов в прайсе;
  - проверяет бренд, размеры, толщины, упаковки и единицы;
  - помечает спорные позиции на ручную проверку.

### 2026-04-30 — Базовая структура MVP

- Ветка: `main`
- Коммит: `d8c75ff`
- Сообщение: `Initial MVP structure for PDF parsing and AI project card experiments`

Что было зафиксировано:

- базовая структура проекта;
- разделение `app/`, `experiments/`, `data/`, `docs/`, `tests/`;
- экспериментальный контур PDF-парсинга;
- экспериментальный контур AI-карточки проекта;
- заготовка интеграции с УНИКМА;
- подготовка под будущую логику расчёта сметы;
- первичная схема git/GitHub.

Значение контрольной точки:

- это стабильная базовая версия проекта;
- от неё можно начинать новые крупные ветки, если нужно отделить будущие эксперименты от текущего направления.
