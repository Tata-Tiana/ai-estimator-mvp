# API run 03: Opus 4.8 + section-pack

Дата: 2026-07-20

## Цель

Проверить, помогает ли более сильная модель `claude-opus-4-8`, если отправлять ей не полный chat-pack, а компактный section-pack только по нужным разделам.

Важно: это не подгонка под ARK или TRC. ARK и TRC использованы только как тестовые проекты. Inventory/pre-processing слой в этом прогоне специально не использовался, чтобы отдельно проверить модель + section-pack.

## Что изменено в инструменте

В `experiments/claude_api_extraction_poc/run_section_extraction.py` добавлен режим:

```bash
--pack-mode section
```

Старый режим `--pack-mode full` остался значением по умолчанию.

Новый section-pack передаёт в модель:

- универсальные правила секционного извлечения;
- schema output JSON;
- `calculator_targets_compact.json`, отфильтрованный только по requested section codes;
- `target_aliases_ru.yaml`, отфильтрованный только по requested section codes;
- `section_guide.json`, отфильтрованный только по requested section codes;
- полный `unit_normalization_guide.json`.

## Запуски

### ARK

Команда:

```bash
.venv/bin/python experiments/claude_api_extraction_poc/run_section_extraction.py \
  --manifest experiments/claude_api_extraction_poc/outputs/ark/prepared/manifest.json \
  --section-code flat_roof \
  --section-code schiedel_vent_channels \
  --page-ref 'АРК КР2 для ИИ.pdf:23' \
  --page-ref 'АРК КР2 для ИИ.pdf:24' \
  --page-ref 'АРК КР2 для ИИ.pdf:25' \
  --out-dir experiments/claude_api_extraction_poc/outputs/ark/sections/flat_roof_schiedel_opus48_section_pack \
  --pack-mode section \
  --model claude-opus-4-8
```

Результаты:

- output: `experiments/claude_api_extraction_poc/outputs/ark/sections/flat_roof_schiedel_opus48_section_pack/extraction_output.json`
- memo: `experiments/claude_api_extraction_poc/outputs/ark/sections/flat_roof_schiedel_opus48_section_pack/service_memo.txt`
- validation: sections 2, raw_table_rows 27, found_items 12, missing_items 7, needs_review_items 11, warnings 0
- usage: input 32958, output 18839, stop_reason end_turn

Ключевое наблюдение:

Opus 4.8 корректно заметил, что на ARK стр. 25 вентканалы выполнены из газобетона, а не Schiedel. Поэтому продуктовые Schiedel target codes не заполнены как будто они найдены. Это лучше предыдущей опасной логики, где модель могла натянуть неподходящий раздел на похожую страницу.

По кровле модель нашла уровни и воронки, но часть суммарных значений оставила `needs_review`, потому что на выбранных страницах есть несколько типов кровли и нет одной общей итоговой строки по объекту.

### TRC

Команда:

```bash
.venv/bin/python experiments/claude_api_extraction_poc/run_section_extraction.py \
  --manifest experiments/claude_api_extraction_poc/outputs/trc/prepared/manifest.json \
  --section-code schiedel_vent_channels \
  --page-ref 'КР2_ТРЦ_30,06,2026.pdf:39' \
  --page-ref 'КР2_ТРЦ_30,06,2026.pdf:40' \
  --out-dir experiments/claude_api_extraction_poc/outputs/trc/sections/schiedel_opus48_section_pack \
  --pack-mode section \
  --model claude-opus-4-8
```

Результаты:

- output: `experiments/claude_api_extraction_poc/outputs/trc/sections/schiedel_opus48_section_pack/extraction_output.json`
- memo: `experiments/claude_api_extraction_poc/outputs/trc/sections/schiedel_opus48_section_pack/service_memo.txt`
- validation: sections 1, raw_table_rows 3, found_items 5, missing_items 1, needs_review_items 4, warnings 0
- usage: input 20204, output 5577, stop_reason end_turn

Ключевое наблюдение:

Opus 4.8 извлёк явную итоговую строку `4,9п.м+4,9п.м=9,8п.м` как `schiedel_masonry_total_length_m = 9.8`.

Старый риск по количествам 15/21 стал заметно лучше: модель не записала `21` в 2x как уверенную истину. Она выбрала `15` для `schiedel_vent_channel_2x_count`, но пометила `needs_review`, потому что в PDF количества визуально расположены неоднозначно.

## Вывод

Opus 4.8 + section-pack выглядит сильнее предыдущих Sonnet-прогонов без inventory:

- вход стал компактнее;
- модель лучше соблюдает requested section codes;
- меньше натягивает неподходящие таблицы на target codes;
- лучше пишет служебную записку о спорных местах;
- спорные значения чаще остаются `needs_review`, а не превращаются в уверенные ошибки.

Но это не отменяет post-processing/adapter слой:

- для multi-value scalar всё равно нужны правила агрегации;
- для страниц с несколькими типами кровли нужна явная методика, когда суммировать, а когда оставлять candidates;
- для Schiedel/TRC нужен отдельный production target для 1x-каналов или понятное правило, что 1x остаётся только raw/detail.

Стоимость в этом отчёте не рассчитана: API response содержит token usage, но не возвращает итоговую цену.
