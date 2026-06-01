# Отчёт по input_builder

Дата: `2026-06-01`.

## Что сделано

Создан экспериментальный слой:

```text
experiments/input_builder/
```

Он закрывает следующий шаг после PDF parser pipeline:

```text
reviewed_parameters.xlsx
↓
input_builder
↓
generated input.json для калькуляторов
```

`input_builder` не читает PDF и не считает смету. Он только собирает промежуточные `input.json` для калькуляторов из проверочной таблицы Елены.

## Источник данных

Основной вход:

```text
experiments/pdf_parser_pipeline/output/mvp_usv_demo/reviewed_parameters.xlsx
```

Используется лист:

```text
parameters
```

Для каждой строки считается `effective_value`:

1. если заполнен `corrected_value` — используется он;
2. иначе если заполнен `final_value` — используется он;
3. иначе если заполнен `extracted_value` — используется он;
4. иначе параметр считается missing.

Расчёт `effective_value` выполняется в Python, без зависимости от Excel-формул.

## Режимы

### strict

Основной режим.

- required-параметры без значения блокируют раздел;
- старые template `input.json` значения не подставляются молча;
- если данные Еленой ещё не проверены/не заполнены, раздел получает статус `blocked_missing_required_params`.

Текущий результат strict-прогона:

```text
sections_enabled = 8
sections_generated = 0
sections_blocked = 8
missing_required_total = 287
manual_required_total = 69
```

Это ожидаемо, потому что текущий `reviewed_parameters.xlsx` ещё не заполнен Еленой.

### demo_with_template_fallback

Демонстрационный режим.

- missing-значения можно взять из template `input.json`;
- каждый fallback явно попадает в warnings;
- этот режим нужен только для проверки механики генерации input-файлов, не для реального расчёта.

Проверка demo-режима:

```text
sections_enabled = 8
sections_generated = 8
sections_blocked = 0
template fallback warnings = 287
```

После проверки финальные outputs были возвращены в strict-режим.

## Созданные файлы

```text
experiments/input_builder/input_builder.py
experiments/input_builder/run_input_builder.py
experiments/input_builder/section_input_registry.py
experiments/input_builder/README.md
experiments/input_builder/notes.md
```

Кейс:

```text
experiments/input_builder/cases/mvp_usv_demo/
```

Outputs:

```text
experiments/input_builder/cases/mvp_usv_demo/result.json
experiments/input_builder/cases/mvp_usv_demo/result.md
experiments/input_builder/cases/mvp_usv_demo/missing_parameters_report.md
experiments/input_builder/cases/mvp_usv_demo/generated_inputs/

experiments/input_builder/output/mvp_usv_demo/
```

## Команды

Strict:

```bash
../.venv/bin/python3 experiments/input_builder/run_input_builder.py experiments/input_builder/cases/mvp_usv_demo
```

Demo fallback:

```bash
../.venv/bin/python3 experiments/input_builder/run_input_builder.py experiments/input_builder/cases/mvp_usv_demo --mode demo_with_template_fallback
```

Compile:

```bash
../.venv/bin/python3 -m py_compile \
experiments/input_builder/input_builder.py \
experiments/input_builder/run_input_builder.py \
experiments/input_builder/section_input_registry.py
```

## Проверки

Выполнено:

```text
strict mode -> ok, 8 sections blocked by missing required parameters
demo_with_template_fallback -> ok, 8 generated inputs, fallback warnings present
py_compile -> ok
calculator files -> not changed
expected.json -> not changed
```

## Следующий шаг

Елена должна заполнить/проверить `reviewed_parameters.xlsx`:

- заполнить `corrected_value` для missing/manual;
- поставить `elena_status = reviewed / corrected / manual`;
- повторно запустить `input_builder`.

После этого можно запускать калькуляторы от generated inputs и переходить к `box_calculator`.
