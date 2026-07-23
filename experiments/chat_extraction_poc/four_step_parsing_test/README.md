# 4-step parsing test

Изолированный тестовый пакет для chat extraction без смешивания с основным
`experiments/chat_extraction_poc`.

Цель: разделить чтение PDF и маппинг в сметные `target_code`.

## Сценарий

```text
Чат 1а: PDF КР1 + prompts/step1_read_pdf_tables_prompt.md
        -> outputs/step1_below.json

Чат 1б: PDF КР2 + prompts/step1_read_pdf_tables_prompt.md
        -> outputs/step1_above.json

Чат 2:  step1_below.json + step1_above.json
        + data/calculator_targets_compact.json
        + data/target_aliases_ru.yaml
        + data/section_guide.json
        + data/unit_normalization_guide.json
        + schemas/claude_extraction_output_schema.json
        + prompts/step2_map_tables_to_extraction_prompt.md
        -> outputs/step2_extraction.json

Чат 3:  outputs/step2_extraction.json
        + prompts/step3_service_note_prompt.md
        -> outputs/step3_note.md
```

PDF загружается только на шаге 1. На шаге 2 модель видит только уже выписанные
таблицы и справочники. На шаге 3 модель видит только финальный extraction JSON.

## Что скопировано из основного pack

- `data/calculator_targets_compact.json`
- `data/target_aliases_ru.yaml`
- `data/section_guide.json`
- `data/unit_normalization_guide.json`
- `schemas/claude_extraction_output_schema.json`
- `validators/validate_claude_extraction.py`

## Локальные отличия тестового pack

`target_aliases_ru.yaml` и `section_guide.json` изменены только внутри этой папки:

- отсечная гидроизоляция удалена из маршрутизации раздела `waterproofing`;
- для `waterproofing_area_m2` добавлен негативный контекст `отсечн`, `под стены`,
  `под кладк`, `первый ряд`;
- отсечная гидроизоляция перенесена в поиск раздела `load_bearing_walls_lintels`;
- для `cutoff_waterproofing_load_bearing_walls_area` добавлены подсказки по листам
  отсечной гидроизоляции.

## Проверки

Проверить step1-файл:

```bash
.venv/bin/python experiments/chat_extraction_poc/four_step_parsing_test/validators/validate_step1_tables.py \
  --input experiments/chat_extraction_poc/four_step_parsing_test/outputs/step1_below.json \
  --report experiments/chat_extraction_poc/four_step_parsing_test/reports/step1_below_validation.md
```

Проверить финальный step2 extraction:

```bash
.venv/bin/python experiments/chat_extraction_poc/four_step_parsing_test/validators/validate_claude_extraction.py \
  --input experiments/chat_extraction_poc/four_step_parsing_test/outputs/step2_extraction.json \
  --report experiments/chat_extraction_poc/four_step_parsing_test/reports/step2_validation.md
```

## Важное правило про штампы

Адрес проекта определяется по титульному листу / загруженному комплекту. Ошибки в
штампах отдельных листов считаются ошибками оформления/копирования. Модель должна
отметить это в предупреждениях, но не отбрасывать данные и не снижать уверенность
только из-за штампа.
