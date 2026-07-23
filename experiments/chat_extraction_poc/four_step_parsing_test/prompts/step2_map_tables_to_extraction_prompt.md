# Шаг 2 — разложить сырые таблицы по сметным target_code

Используй этот промпт в новом чате без PDF.

Загрузи:

1. `step1_below.json`;
2. `step1_above.json`;
3. `data/calculator_targets_compact.json`;
4. `data/target_aliases_ru.yaml`;
5. `data/section_guide.json`;
6. `data/unit_normalization_guide.json`;
7. `schemas/claude_extraction_output_schema.json`.

PDF на этом шаге не загружается. Все числа, страницы, листы, таблицы и цитаты
нужно брать только из `step1_below.json` и `step1_above.json`.

## Главный принцип

Каждый `found` item обязан ссылаться на одну или несколько строк шага 1 через
`source_row_ids`.

Если нет подходящей строки в step1-файлах, значит значения нет. Не вспоминай PDF
и не придумывай значение.

## Порядок работы

1. Прочитай `extraction_warnings` из обоих step1-файлов и перенеси важные
   предупреждения в top-level `extraction_warnings` итогового JSON.
2. Для каждой строки `raw_table_rows` проверь:
   - русский текст строки;
   - `table_title`;
   - `page_title`;
   - `legend_ref`;
   - единицу;
   - контекст соседних ячеек.
3. Сопоставляй строки с `target_code` только через `target_aliases_ru.yaml`,
   `calculator_targets_compact.json` и `section_guide.json`.
4. Сначала сохрани в разделе `raw_table_rows` только те строки, которые:
   - стали `found`;
   - стали candidate/needs_review;
   - объясняют `missing`;
   - важны как out-of-scope для сметы.
5. Потом заполни `found`, `missing`, `needs_review` по схеме.

## Отсечная гидроизоляция

Отсечная гидроизоляция под первый ряд блоков/стен относится к разделу
`load_bearing_walls_lintels`, target:

```text
cutoff_waterproofing_load_bearing_walls_area
```

Не маппь отсечную гидроизоляцию в:

```text
waterproofing.waterproofing_area_m2
```

Обычная `waterproofing_area_m2` — это площадь гидроизоляции фундаментной плиты
битумной мастикой. По методике Елены, если отдельной строки гидроизоляции в PDF
нет, она может быть равна площади опалубки бортов фундаментной плиты. Но это не
то же самое, что отсечная гидроизоляция под кладку стен.

Если строка отсечной гидроизоляции различается только штриховкой/маркером, а
`legend_ref` отсутствует, не принимай ее уверенно. Оставь соответствующий target
в `missing` или `needs_review` и объясни, что не хватает связи с легендой.

## Правило про штампы

Если в step1 есть предупреждения, что штамп листа отличается от титульного, не
считай это причиной для `needs_review` само по себе. Это ошибка оформления PDF.
Используй данные по содержанию строки и таблицы.

`needs_review` ставь только при реальной сметной неоднозначности: непонятная
единица, несколько кандидатов, противоречащие числа, нет legend_ref для
графического маркера, нет явного итога, неясный раздел по содержанию.

## Формат `found`

У каждого found item должны быть:

- `target_code`;
- `value`;
- `unit`;
- `normalized_unit`;
- `source_pdf`;
- `page_number`;
- `page_title`;
- `raw_text`;
- `confidence`;
- `needs_review`;
- `notes`;
- `source_row_ids`.

Если значение собрано из нескольких строк, перечисли все `source_row_ids` и не
скрывай арифметику в `notes`.

## Запреты

- Не бери значения не из step1-файлов.
- Не выбирай `target_code` по английскому имени.
- Не суммируй компоненты в scalar, если нет явного итога.
- Не маппь строки с несовпадающей единицей уверенно.
- Не теряй строку `1х` Schiedel, даже если в targets пока нет отдельного кода:
  сохрани ее в `raw_table_rows` / notes как unmapped product row.

Верни только JSON по `claude_extraction_output_schema.json`.
