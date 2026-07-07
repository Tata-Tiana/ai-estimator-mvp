# Как использовать этот пакет в GPT/Claude-чате

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
