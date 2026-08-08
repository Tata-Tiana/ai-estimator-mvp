# Как использовать этот пакет в GPT/Claude-чате

Пакет обновлён: 2026-08-08.

## Что сейчас в пакете

- `claude_estimate_extraction_prompt.md` — актуальные правила извлечения и служебной записки; последние
  уточнения добавлены 2026-08-02: линейные примыкания кровли к стенам/ВК/вентканалам не путать со
  штучными примыканиями к вентшахтам; по Schiedel готовую строку общей высоты/длины вентканалов
  маппить в рабочую длину кладки, а строки по типам в метрах не превращать в количество модулей;
  если PDF даёт компоненты без готового итога, модель сохраняет компоненты, а решение об автосумме
  принимает код review/calculator слоя.
- `calculator_targets_compact.json` / `target_aliases_ru.yaml` — помимо одиночных (scalar) целей,
  содержат динамические группы построчных данных (`extract_groups`), которые нужно использовать вместо
  одиночного скаляра, когда PDF даёт данные несколькими строками без готового общего итога:
  `wall_block_items`, `roof_zones`, `slab_zones`, `schiedel_channel_items`, `thermal_insert_items`,
  `pit_items`, `sand_items`, `foundation_wall_items`, `column_footing_items`,
  `lintel_groove_rebar_items`, `main_wall_rebar_items`, `lintel_rebar_items`, `foundation_rebar_items`,
  `floor_slab_1_rebar_items`, `floor_slab_2_rebar_items`, `floor_slab_2_beam_items`, `beam_items`,
  `beam_table_controls`, `communications_pipe_items`, `trench_routes`, `vent_chimney_cladding_segments`,
  `roof_raw_material_spec_rows`. У каждой группы в `notes` явно написано, когда её использовать вместо
  старого одиночного поля — не заполняй оба пути одновременно.
- Также добавлен скалярный `thermal_insert_combined_length_m` — используется ВМЕСТО раздельных
  `thermal_insert_50_length`/`thermal_insert_100_length`, только если PDF даёт одну общую длину
  термовставок на оба слоя ЭППС сразу (не копируй одно число в оба старых поля — это задвоение работы).
- **Добавлено 2026-08-07**: `wall_block_items` (и парные scalar-цели `main_wall_gas_block_400/250_spec_volume`)
  теперь явно разрешают смешанные источники по ролям в одном проекте — например main_walls может прийти
  готовой scalar-парой, а floor_2/parapet/partitions того же проекта одновременно через построчную группу
  `wall_block_items`, если именно их данные в PDF разбиты по зонам/уровням без готового итога. Раньше это
  было неочевидно и рискованно молча терять объём одной из ролей — калькулятор с 2026-08-07 резолвит
  каждую роль независимо. Не затаскивай роль в `wall_block_items` только потому, что другая роль туда
  уже попала — правило «одна готовая цифра → scalar, без дублирования» действует как раньше, просто
  теперь по ролям отдельно, а не по всему проекту разом.

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
8. Запусти сравнение с проверенным эталоном (только после того, как результат уже получен и сохранён):
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
