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
- не запускает расчёт сметы;
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
- `02_Цены себестоимости` — список реальных ценовых компонентов;
- `03_Детали объемов` — траншеи и коммуникации как структурированные данные.

## Что создаёт

В `outputs/`:

```text
review_values_normalized.json
review_reader_report.md
```

## Step 2: build calculator input

Следующий слой читает уже нормализованный review JSON и собирает вход для калькулятора,
не заходя ни в Google Sheet, ни в сам calculator runtime.

```bash
python experiments/earthworks_review_to_calculator/run_build_calculator_input.py \
  --normalized-json experiments/earthworks_review_to_calculator/outputs/review_values_normalized.json \
  --out experiments/earthworks_review_to_calculator/outputs/earthworks_calculation_input.json \
  --report experiments/earthworks_review_to_calculator/outputs/calculator_input_report.md

python experiments/earthworks_review_to_calculator/anti_cheat.py \
  --normalized-json experiments/earthworks_review_to_calculator/outputs/review_values_normalized.json \
  --calculator-input experiments/earthworks_review_to_calculator/outputs/earthworks_calculation_input.json
```

## Запуск

Из корня репозитория:

```bash
python experiments/earthworks_review_to_calculator/run_review_reader.py \
  --workbook experiments/earthworks_parser_google_stage1/review_workbook.xlsx \
  --out-dir experiments/earthworks_review_to_calculator/outputs

python experiments/earthworks_review_to_calculator/anti_cheat.py \
  --normalized-json experiments/earthworks_review_to_calculator/outputs/review_values_normalized.json
```

Если путь `review_workbook.xlsx` указывает на несуществующий файл, reader попробует найти свежий workbook stage1 в `data/jobs/*/google/review_workbook.xlsx`.

## Границы слоя

- это не общий `price_provider` для всего MVP;
- это не публикация данных в Google;
- это не замена stage1 review workbook;
- это не запуск калькулятора;
- это не изменение production-калькулятора земляных работ.
