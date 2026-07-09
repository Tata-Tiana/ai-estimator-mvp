# Earthworks Mini-MVP CLI POC

Изолированная репетиция MVP-процесса для раздела **Земляные работы**.

Цепочка:

```text
PDF / strict parser v3 output
→ prepare review table
→ Elena reviews/fixes/fills manual values
→ validate gate
→ calculate from reviewed table
→ static Excel
```

Это не финальная смета и не изменение production pipeline. Эксперимент не меняет существующие калькуляторы, locked cases, parser pipeline, input builder или runners.

## Сценарий

```bash
# 1. Подготовить таблицу проверки
.venv/bin/python3 experiments/earthworks_mini_mvp_poc/run_mini_mvp.py prepare

# 2. Открыть data/review/earthworks_parameter_review.xlsx
#    Проверить значения, заполнить ручные поля, поставить статусы

# 3. Проверить готовность к расчету
.venv/bin/python3 experiments/earthworks_mini_mvp_poc/run_mini_mvp.py validate

# 4. Выполнить расчет
.venv/bin/python3 experiments/earthworks_mini_mvp_poc/run_mini_mvp.py calculate
```

`prepare` не считает.

`calculate` не считает, если обязательные поля не проверены или ручные поля пустые.

Запуск без аргументов выводит help и не запускает расчет.

## Gate

В review table есть POC smoke-test:

```text
manual_required_smoke_test
```

Он не передается в `EarthworksInput` и не влияет на сумму. Он нужен только для проверки, что расчет блокируется без ручного ввода.

Также `pit_excavation_depth_m` должен быть проверен или исправлен, потому что parser интерпретирует диапазон глубины котлована.

## Источники

Read-only:

- `experiments/usv_strict_pdf_parser_v3/data/extracted/earthworks.json`
- `experiments/usv_strict_pdf_parser_v3/data/extracted/candidates.json`
- `experiments/usv_strict_pdf_parser_v3/data/raw/logical_pages.json`
- `experiments/usv_strict_pdf_parser_v3/data/raw/tables.json`
- `output/price_registry_filled_v3.xlsx`
- `experiments/earthworks_calculator/cases/usv_yusupovo_village_live_prices/input.json` только как fallback для цен

Количество и объемы не берутся из legacy input.

## Outputs After Prepare

```text
data/extracted/earthworks_extracted_parameters.json
data/review/earthworks_parameter_review.xlsx
data/review/earthworks_review_hints.xlsx
data/reports/prepare_report.md
```

## Outputs After Blocked Calculate

```text
data/reports/calculate_blocked_report.md
```

## Outputs After Successful Calculate

```text
data/mapped/earthworks_input_from_review.json
data/calculated/earthworks_result_from_review.json
data/calculated/earthworks_result_from_review.md
data/excel/earthworks_final_from_review.xlsx
data/reports/calculate_report.md
data/reports/integrity_report.md
```

## Excel

Финальный Excel статический, без формул. Листы:

- `01_Проверка`
- `02_Траншеи`
- `03_Коммуникации`
- `04_Расчет`
- `05_Итоги`
- `06_Источники`
- `07_Лог`

Русские названия параметров берутся из локального `parameter_dictionary.py`.

## Operator Logs

`data/reports/operator_log.json` содержит человекочитаемые сообщения, которые имитируют будущие уведомления бота:

- сколько параметров найдено;
- сколько ожидают проверки;
- почему расчет заблокирован;
- что создано после успешного расчета.
