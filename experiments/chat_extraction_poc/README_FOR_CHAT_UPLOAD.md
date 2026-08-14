# Как использовать этот пакет в GPT/Claude-чате

Пакет обновлён: 2026-08-13.

## Что сейчас в пакете

- `claude_estimate_extraction_prompt.md` — актуальные правила извлечения и служебной записки; последние
  уточнения добавлены 2026-08-13: раздел стен/перемычек `load_bearing_walls_lintels_p6` переведён на чистую зональную модель P6,
  без старых scalar-полей `main_wall_*`, `floor_1_lintel_*`, `floor_2_lintel_*`.
- `notes_report_correction_prompt.md` — второй промпт для работы над ошибками: после первого JSON
  запускается кодовый notes-report, затем этот report вместе с исходным JSON отдаётся в тот же чат,
  чтобы модель исправила только найденные программой проблемы.
- `service_note_technical_audit_prompt.md` и `elena_service_note_prompt.md` — дополнительные промпты
  для технического аудита записки и человеческой записки для Елены.
- `calculator_targets_compact.json` / `target_aliases_ru.yaml` — помимо одиночных (scalar) целей,
  содержат динамические группы построчных данных (`extract_groups`), которые нужно использовать вместо
  одиночного скаляра, когда PDF даёт данные несколькими строками без готового общего итога:
  `wall_zones`, `wall_block_items`, `wall_chasing_rebar_items`, `lintel_items`, `lintel_rebar_items`,
  `roof_zones`, `slab_zones`, `schiedel_channel_items`, `thermal_insert_items`,
  `pit_items`, `sand_items`, `foundation_wall_items`, `column_footing_items`,
  `foundation_rebar_items`,
  `floor_slab_zones`, `floor_slab_eps_items`, `floor_slab_beam_items`, `floor_slab_rebar_items`,
  `floor_slab_additional_items`,
  `beam_table_controls`, `communications_pipe_items`, `trench_routes`,
  `roof_raw_material_spec_rows`. У каждой группы в `notes` явно написано, как её использовать.
- Также добавлен скалярный `thermal_insert_combined_length_m` — используется ВМЕСТО раздельных
  `thermal_insert_50_length`/`thermal_insert_100_length`, только если PDF даёт одну общую длину
  термовставок на оба слоя ЭППС сразу (не копируй одно число в оба старых поля — это задвоение работы).
- **Стены и перемычки P6** (`load_bearing_walls_lintels_p6`): извлекаются только через repeated groups:
  `wall_zones`, `wall_block_items`, `wall_chasing_rebar_items`, `lintel_items`, `lintel_rebar_items`.
  Старые scalar-поля стен и перемычек больше не использовать. Арматура стен/парапета/перемычек
  извлекается построчно, но в таблице проверки будет справочной серой: Елена сверяет с PDF, не правит
  арматуру руками.
- **Плиты перекрытия/покрытия**: извлекаются через один
  production-раздел `floor_slabs`, где каждая физическая плита/зона идет отдельной строкой в
  `floor_slab_zones`, а ЭППС самой плиты, балки, арматура и дополнительные строки идут через группы
  `floor_slab_eps_items`, `floor_slab_beam_items`, `floor_slab_rebar_items`,
  `floor_slab_additional_items`. Утепление балок записывается только в строку балки, утепление
  монолитных перемычек — только в раздел стен/перемычек P6.

Если версия этого README старше, чем сегодняшняя правка промпта/target-файлов — сначала пересобери
пакет (`python3 build_claude_chat_pack.py`) и сверь список правил/групп выше с содержимым файлов
`data/`, прежде чем грузить пакет в чат.

## Шаги

1. Открой новый чат в GPT Plus или Claude (обычный чат по подписке, не API).
2. Загрузи PDF проекта (все файлы/чертежи, которые у тебя есть по этому проекту).
3. Загрузи файлы из этого архива:
   - `claude_estimate_extraction_prompt.md`
   - `claude_extraction_output_schema.json`
   - `calculator_targets_compact.json`
   - `target_aliases_ru.yaml`
   - `section_guide.json`
   - `unit_normalization_guide.json`
4. Вставь текст из `claude_estimate_extraction_prompt.md` как сообщение в чат.
5. Попроси чат сначала извлечь `raw_table_rows`, затем сопоставить строки
   с `target_code` по `target_aliases_ru.yaml`, и вернуть только JSON
   (без пояснений вокруг).
6. Скопируй ответ чата и сохрани его в файл:
   `experiments/chat_extraction_poc/outputs/claude_<project>_extraction.json`
   или `experiments/chat_extraction_poc/outputs/gpt_<project>_extraction.json`
   (например `gpt_usv_extraction.json`)
7. Запусти проверку:
   ```
   .venv/bin/python3 experiments/chat_extraction_poc/validate_claude_extraction.py \
     --input experiments/chat_extraction_poc/outputs/gpt_usv_extraction.json \
     --report experiments/chat_extraction_poc/reports/gpt_usv_validation_report.md
   ```
8. Собери технический отчёт по сомнениям/ошибкам JSON:
   ```
   .venv/bin/python3 experiments/full_estimate_review_pipeline/build_extraction_notes_report.py \
     --input experiments/chat_extraction_poc/outputs/gpt_usv_extraction.json \
     --output experiments/chat_extraction_poc/reports/code_notes_report_gpt_usv.md
   ```
9. Для работы над ошибками вернись в тот же чат, где PDF уже загружены, и приложи:
   - исходный extraction JSON;
   - `code_notes_report_*.md`;
   - текст из `notes_report_correction_prompt.md`.

   Попроси сохранить исправленный JSON отдельным файлом с суффиксом `_corrected`.
10. Запусти сравнение с проверенным эталоном (только после того, как результат уже получен и сохранён):
   ```
   .venv/bin/python3 experiments/chat_extraction_poc/compare_with_validated_input.py \
     --claude-json experiments/chat_extraction_poc/outputs/gpt_usv_extraction.json \
     --validated-input experiments/earthworks_calculator/cases/usv_yusupovo_village/input.json \
     --report experiments/chat_extraction_poc/reports/gpt_usv_compare_report.md
   ```

**Важно:** не показывай чату во время извлечения (шаги 1–5) файл
`experiments/earthworks_calculator/cases/usv_yusupovo_village/input.json`
и не давай никаких чисел из него в подсказках/уточнениях — иначе
сравнение на шаге 8 станет нечестным.

Если PDF большой и чат не справляется с ним целиком за одно
сообщение — можно идти по разделам сметы (по одному сообщению на
раздел из `calculator_targets_compact.json`), а в конце собрать все
разделы в один JSON-объект по схеме.
