# Claude API Extraction POC

Отдельный экспериментальный контур для проверки Claude API extraction.

Не production. Не трогает калькуляторы, Google workbook, adapters, Telegram flow и ручной
`experiments/chat_extraction_poc`.

ARK, TRC и USV здесь только тестовые проекты. Правила должны оставаться универсальными.

## Идея

Итоговые пользовательские файлы те же, что у ручного chat parsing:

- `extraction_output.json`;
- `service_memo.txt`.

Но внутри API-процесс можно делать кусками:

1. подготовить страницы PDF как текст + PNG;
2. прогнать одну или несколько секций по выбранным страницам;
3. склеить секционные JSON в один итоговый JSON;
4. проверить итог validator-ом.

Так мы не зависим от того, умеет ли конкретный чат “сам” читать PDF. Мы явно даем модели и текстовый
слой, и картинку страницы.

## Pack

Локальная копия правил лежит здесь:

- `pack/prompts/api_estimate_extraction_prompt.md`;
- `pack/schemas/claude_extraction_output_schema.json`;
- `pack/data/calculator_targets_compact.json`;
- `pack/data/target_aliases_ru.yaml`;
- `pack/data/unit_normalization_guide.json`;
- `pack/data/section_guide.json`.

API-prompt можно менять смело внутри этого эксперимента. Ручной chat-prompt от этого не меняется.

## Шаг 1. Подготовить страницы

```bash
.venv/bin/python experiments/claude_api_extraction_poc/prepare_project_pages.py \
  --project-code ark \
  --pdf "/Users/tatanamedzidova/Desktop/АРК КР1 для ИИ.pdf" \
  --pdf "/Users/tatanamedzidova/Desktop/АРК КР2 для ИИ.pdf" \
  --out-dir experiments/claude_api_extraction_poc/outputs/ark/prepared
```

Результат:

- `manifest.json` — список страниц, путей к тексту и PNG;
- `project_full_text.md` — весь текстовый слой;
- `pages_text/...` — текст по страницам;
- `pages_images/...` — картинки страниц.

## Шаг 2. Секционный dry-run

Dry-run проверяет сборку запроса без вызова API и без записи base64 картинок в summary:

```bash
.venv/bin/python experiments/claude_api_extraction_poc/run_section_extraction.py \
  --manifest experiments/claude_api_extraction_poc/outputs/ark/prepared/manifest.json \
  --section-code flat_roof \
  --section-code schiedel_vent_channels \
  --page-ref "АРК КР2 для ИИ.pdf:23" \
  --page-ref "АРК КР2 для ИИ.pdf:24" \
  --page-ref "АРК КР2 для ИИ.pdf:25" \
  --out-dir experiments/claude_api_extraction_poc/outputs/ark/sections/flat_roof_schiedel \
  --dry-run
```

## Шаг 3. Реальный секционный запуск

Нужен `ANTHROPIC_API_KEY` в `.env` или окружении.

```bash
.venv/bin/python experiments/claude_api_extraction_poc/run_section_extraction.py \
  --manifest experiments/claude_api_extraction_poc/outputs/ark/prepared/manifest.json \
  --section-code flat_roof \
  --section-code schiedel_vent_channels \
  --page-ref "АРК КР2 для ИИ.pdf:23" \
  --page-ref "АРК КР2 для ИИ.pdf:24" \
  --page-ref "АРК КР2 для ИИ.pdf:25" \
  --out-dir experiments/claude_api_extraction_poc/outputs/ark/sections/flat_roof_schiedel
```

## Шаг 4. Склеить секции

```bash
.venv/bin/python experiments/claude_api_extraction_poc/merge_section_outputs.py \
  --section-output experiments/claude_api_extraction_poc/outputs/ark/sections/flat_roof_schiedel \
  --out-dir experiments/claude_api_extraction_poc/outputs/ark/final
```

## Full-PDF Smoke Test

Оставлен старый монолитный режим: PDF передаются в Claude API как `document` blocks.
Это полезно только как сравнение с секционным режимом.

Dry-run:

```bash
.venv/bin/python experiments/claude_api_extraction_poc/run_claude_api_extraction.py \
  --pdf "/Users/tatanamedzidova/Desktop/АРК КР1 для ИИ.pdf" \
  --pdf "/Users/tatanamedzidova/Desktop/АРК КР2 для ИИ.pdf" \
  --out-dir experiments/claude_api_extraction_poc/outputs/api_ark_test \
  --dry-run
```

Real run:

```bash
.venv/bin/python experiments/claude_api_extraction_poc/run_claude_api_extraction.py \
  --pdf "/Users/tatanamedzidova/Desktop/АРК КР1 для ИИ.pdf" \
  --pdf "/Users/tatanamedzidova/Desktop/АРК КР2 для ИИ.pdf" \
  --out-dir experiments/claude_api_extraction_poc/outputs/api_ark_test
```

## Notes

Outputs contain real project data and should stay local. They are covered by the repo's generic
`experiments/**/outputs/**` gitignore rule.
