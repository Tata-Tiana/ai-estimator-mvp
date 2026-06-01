# Assistant Handoff

Дата актуализации: `2026-06-01`.

Этот файл — главная точка входа для нового чата/агента. Если нужно быстро понять проект `ai-estimator-mvp`, начинать отсюда.

## Последняя расчётная контрольная точка

Текущая рабочая ветка:

```text
feature/ai-project-card
```

Коммит расчётной базы:

```text
Add live pricing mode for all calculators
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

Отчёт:

```text
docs/report_pdf_parser_pipeline.md
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
