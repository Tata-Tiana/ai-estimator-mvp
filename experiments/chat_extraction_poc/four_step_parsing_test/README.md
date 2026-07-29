# 4-step parsing test

**СТАТУС: ЗАКРЫТ 2026-07-28. Больше не править.**

Этот эксперимент оставлен как архив проверки идеи "PDF только на шаге 1,
маппинг отдельно". В текущем рабочем процессе он не является источником правды и
не должен обновляться при следующих правках prompt/aliases/targets. Актуальные
файлы для chat extraction живут в `experiments/chat_extraction_poc/data`,
`experiments/chat_extraction_poc/prompts` и в собираемом zip-пакете.

Изолированный тестовый пакет для chat extraction без смешивания с основным
`experiments/chat_extraction_poc`.

Цель: разделить чтение PDF и маппинг в сметные `target_code`.

Пакет пересобран: 2026-07-27.

Основа: актуальные файлы из `experiments/chat_extraction_poc` после обновления
большого chat prompt и target-файлов.

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

## Как нарезан актуальный большой prompt

- `step1_read_pdf_tables_prompt.md` — только чтение PDF: страницы, штампы,
  таблицы, спецификации, легенды, штриховки/цвета, визуальная проверка картинки,
  без target-кодов и без сметного маппинга.
- `step2_map_tables_to_extraction_prompt.md` — маппинг уже выписанных
  `step1_*.json` в extraction JSON по актуальным `calculator_targets_compact.json`,
  `target_aliases_ru.yaml`, `section_guide.json`, `unit_normalization_guide.json`
  и схеме. PDF на этом шаге не загружается.
- `step3_service_note_prompt.md` — служебная записка для сметчицы только по
  готовому `step2_extraction.json`.

## Важные правила, которые сохранены в 4 шагах

- сначала raw tables, потом маппинг;
- `legend_ref` для штриховок, цветов и графических маркеров;
- ошибки штампов/адресов на листах считаются ошибками оформления, а не причиной
  выбрасывать страницу;
- приоритет таблицы спецификации над чертежом/узлом/пояснительной запиской;
- толщина плиты по сечению, а не по пояснительной записке;
- если текстовый слой PDF выглядит как каша, сначала смотреть страницу визуально;
- repeated groups использовать вместо scalar-поля, когда PDF даёт компоненты без
  явного итога;
- отсечную гидроизоляцию не маппить в `waterproofing_area_m2`;
- Schiedel считать по строкам модулей/товаров из спецификации, а не по количеству
  шахт на плане;
- кровлю с несколькими зонами вести через `roof_zones`, а не втискивать в две
  level-строки.

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
