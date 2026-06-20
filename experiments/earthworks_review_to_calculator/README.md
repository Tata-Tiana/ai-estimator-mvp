# Earthworks Review To Calculator

Изолированный адаптерный слой для раздела **Земляные работы**.

Назначение слоя:

```text
локальный review_workbook.xlsx
→ нормализованный JSON
→ отчёт для проверки
```

Этот слой:

- читает только локальный `review_workbook.xlsx`;
- не обращается к Google Sheet API;
- не меняет parser;
- не меняет калькулятор;
- не содержит формул расчёта;
- может запускать существующий `earthworks_calculator` как отдельный orchestration step;
- не пишет ничего обратно в `price_registry`.

Слой нужен как промежуточный мост между:

```text
experiments/earthworks_parser_google_stage1/
```

и

```text
experiments/earthworks_calculator/
```

## Что читает

- `01_Проверка проекта` — проектные параметры и возможные ручные исправления;
- `02_Цены себестоимости` — список реальных ценовых компонентов и технические price keys;
- `03_Детали объемов` — траншеи и коммуникации как структурированные данные.

## Что создаёт

В `outputs/`:

```text
review_values_normalized.json
review_reader_report.md
```

В `prices` reader сохраняет и видимые поля, и технические ключи:

- `calc_price_key`
- `price_registry_code`
- `fallback_key`
- `selected_price_source`
- `effective_price_source`

## Step 2: build calculator input

Следующий слой читает уже нормализованный review JSON и собирает вход для калькулятора,
не заходя ни в Google Sheet, ни в сам calculator runtime.

На этом шаге calculator input builder строит цены по `calc_price_key`.
Русские названия строк больше не являются source of truth для price mapping.

```bash
python experiments/earthworks_review_to_calculator/run_build_calculator_input.py \
  --normalized-json experiments/earthworks_review_to_calculator/outputs/review_values_normalized.json \
  --out experiments/earthworks_review_to_calculator/outputs/earthworks_calculation_input.json \
  --report experiments/earthworks_review_to_calculator/outputs/calculator_input_report.md

python experiments/earthworks_review_to_calculator/anti_cheat.py \
  --normalized-json experiments/earthworks_review_to_calculator/outputs/review_values_normalized.json \
  --calculator-input experiments/earthworks_review_to_calculator/outputs/earthworks_calculation_input.json
```

## Step 3: run existing earthworks calculator

Следующий слой запускает уже существующий `earthworks_calculator` на входе из review layer
и сохраняет результат локально в `outputs/calculation_result/`.

```bash
python experiments/earthworks_review_to_calculator/run_calculator_from_review_input.py \
  --calculator-input experiments/earthworks_review_to_calculator/outputs/earthworks_calculation_input.json \
  --out-dir experiments/earthworks_review_to_calculator/outputs/calculation_result

python experiments/earthworks_review_to_calculator/anti_cheat.py \
  --normalized-json experiments/earthworks_review_to_calculator/outputs/review_values_normalized.json \
  --calculator-input experiments/earthworks_review_to_calculator/outputs/earthworks_calculation_input.json \
  --calculation-result-dir experiments/earthworks_review_to_calculator/outputs/calculation_result
```

## Full local review flow

This is the recommended local command for the earthworks review-to-calculator flow.
It does not call Google API.
It does not modify Stage1.
It does not modify `earthworks_calculator`.
It only orchestrates existing local scripts.

```bash
python experiments/earthworks_review_to_calculator/run_full_review_flow.py \
  --workbook experiments/earthworks_parser_google_stage1/review_workbook.xlsx \
  --out-dir experiments/earthworks_review_to_calculator/outputs
```

## Diagnostic comparison

Comparison is not part of the production flow.
Baseline result path is always passed explicitly.
Review-layer does not import or read old fixture paths by default.

```bash
python experiments/earthworks_review_to_calculator/compare_calculation_results.py \
  --baseline-result <baseline_result.json> \
  --review-result experiments/earthworks_review_to_calculator/outputs/calculation_result/result.json \
  --out experiments/earthworks_review_to_calculator/outputs/calculation_comparison_report.md
```

## Input lineage report

This report explains where each calculator input field comes from.
It is a diagnostic transparency report.
It is not a production dependency.
Project quantities come from normalized review data.
Prices come from `calc_price_key` rows.
Generic method defaults come from `GENERIC_CALCULATOR_DEFAULTS`.

```bash
python experiments/earthworks_review_to_calculator/build_input_lineage_report.py \
  --normalized-json experiments/earthworks_review_to_calculator/outputs/review_values_normalized.json \
  --calculator-input experiments/earthworks_review_to_calculator/outputs/earthworks_calculation_input.json \
  --out experiments/earthworks_review_to_calculator/outputs/input_lineage_report.md \
  --out-json experiments/earthworks_review_to_calculator/outputs/input_lineage_report.json
```

## Formula-ready output for future Excel formulas

This is not Excel export yet.
It prepares estimate rows, symbolic formula models, layout-aware calc zones, and row-level helper cells.
The future Excel exporter will map symbolic references to real A1 cell references.

```bash
python experiments/earthworks_review_to_calculator/build_formula_ready_result.py \
  --calculator-input experiments/earthworks_review_to_calculator/outputs/earthworks_calculation_input.json \
  --calculation-result experiments/earthworks_review_to_calculator/outputs/calculation_result/result.json \
  --lineage-report experiments/earthworks_review_to_calculator/outputs/input_lineage_report.json \
  --out experiments/earthworks_review_to_calculator/outputs/formula_ready_result.json \
  --report experiments/earthworks_review_to_calculator/outputs/formula_ready_report.md
```

## Запуск

Из корня репозитория:

```bash
python experiments/earthworks_review_to_calculator/run_review_reader.py \
  --workbook experiments/earthworks_parser_google_stage1/review_workbook.xlsx \
  --out-dir experiments/earthworks_review_to_calculator/outputs

python experiments/earthworks_review_to_calculator/run_build_calculator_input.py \
  --normalized-json experiments/earthworks_review_to_calculator/outputs/review_values_normalized.json \
  --out experiments/earthworks_review_to_calculator/outputs/earthworks_calculation_input.json \
  --report experiments/earthworks_review_to_calculator/outputs/calculator_input_report.md

python experiments/earthworks_review_to_calculator/run_calculator_from_review_input.py \
  --calculator-input experiments/earthworks_review_to_calculator/outputs/earthworks_calculation_input.json \
  --out-dir experiments/earthworks_review_to_calculator/outputs/calculation_result

python experiments/earthworks_review_to_calculator/anti_cheat.py \
  --normalized-json experiments/earthworks_review_to_calculator/outputs/review_values_normalized.json \
  --calculator-input experiments/earthworks_review_to_calculator/outputs/earthworks_calculation_input.json \
  --calculation-result-dir experiments/earthworks_review_to_calculator/outputs/calculation_result \
  --lineage-report experiments/earthworks_review_to_calculator/outputs/input_lineage_report.json \
  --formula-ready-result experiments/earthworks_review_to_calculator/outputs/formula_ready_result.json
```

Если путь `review_workbook.xlsx` указывает на несуществующий файл, reader попробует найти свежий workbook stage1 в `data/jobs/*/google/review_workbook.xlsx`.

## Границы слоя

- это не общий `price_provider` для всего MVP;
- это не публикация данных в Google;
- это не замена stage1 review workbook;
- это не изменение production-калькулятора земляных работ;
- это не изменение формул калькулятора, только orchestration вокруг него.
