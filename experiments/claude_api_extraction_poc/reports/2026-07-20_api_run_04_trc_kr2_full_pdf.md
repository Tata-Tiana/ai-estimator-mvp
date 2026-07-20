# API run 04 — попытка полного прогона TRC KR2

Дата: 2026-07-20

## Цель

Проверить более близкий API-аналог ручного извлечения через чат:

- только проект TRC;
- только второй файл проекта / KR2;
- полный prompt pack, а не компактный section-pack;
- короткая заметка к запуску, что это надземная часть / вторая часть проекта;
- весь файл KR2 должен быть доступен модели, чтобы она могла использовать контекст между листами.

## Изменения в скриптах

Были добавлены две небольшие доработки API harness:

- `run_section_extraction.py`
  - добавлен `--source-pdf`, чтобы выбирать из manifest все подготовленные страницы одного PDF;
  - добавлен `--run-note`;
- `run_claude_api_extraction.py`
  - добавлен `--run-note`;
  - добавлен необязательный фильтр `--section-code`, при этом полный prompt pack все равно
    отправляется модели.

Эти изменения не меняют ручной prompt для chat extraction.

## Попытка 1: KR2 как 44 подготовленные PNG-страницы

Форма команды:

```text
run_section_extraction.py
--source-pdf КР2_ТРЦ_30,06,2026.pdf
--pack-mode full
--model claude-opus-4-8
```

Выбранный контент:

- 44 подготовленные страницы из `КР2_ТРЦ_30,06,2026.pdf`;
- полный API prompt pack;
- запрошенные разделы:
  - `load_bearing_walls_lintels`;
  - `floor_slab_1`;
  - `floor_slab_2`;
  - `flat_roof`;
  - `schiedel_vent_channels`.

Результат:

- запрос упал до начала извлечения;
- API вернул `413 request_too_large`;
- причина: 44 PNG-картинки + полный prompt + текст страниц превысили лимит размера запроса Anthropic.

Вывод:

Отправлять весь KR2 как отрендеренные PNG-страницы в одном запросе нельзя: запрос слишком большой.

## Попытка 2: KR2 как один PDF document block, без фильтра разделов

Форма команды:

```text
run_claude_api_extraction.py
--pdf /Users/tatanamedzidova/Desktop/КР2_ТРЦ_30,06,2026.pdf
--model claude-opus-4-8
--max-tokens 40000
```

Результат:

- API принял запрос;
- ответ сохранен в:
  - `experiments/claude_api_extraction_poc/outputs/trc/full_kr2_pdf_opus48_full_prompt/api_raw_response.json`
  - `experiments/claude_api_extraction_poc/outputs/trc/full_kr2_pdf_opus48_full_prompt/api_output_text.txt`
- parser не смог разобрать результат, потому что JSON был неполным;
- `stop_reason = max_tokens`;
- usage:
  - input tokens: `171695`;
  - output tokens: `40000`.

Важное наблюдение:

Так как full-PDF скрипт на тот момент еще не передавал список нужных section codes, модель начала
генерировать все восемь разделов prompt, включая пустые `earthworks` и `foundation_slab`. Это
потратило output tokens и практически гарантировало обрезание ответа.

## Попытка 3: KR2 как один PDF document block, с фильтром разделов KR2

Форма команды:

```text
run_claude_api_extraction.py
--pdf /Users/tatanamedzidova/Desktop/КР2_ТРЦ_30,06,2026.pdf
--section-code load_bearing_walls_lintels
--section-code floor_slab_1
--section-code floor_slab_2
--section-code flat_roof
--section-code schiedel_vent_channels
--model claude-opus-4-8
--max-tokens 40000
```

Результат:

- API принял запрос;
- ответ сохранен в:
  - `experiments/claude_api_extraction_poc/outputs/trc/full_kr2_pdf_opus48_full_prompt_v2/api_raw_response.json`
  - `experiments/claude_api_extraction_poc/outputs/trc/full_kr2_pdf_opus48_full_prompt_v2/api_output_text.txt`
- parser снова не смог разобрать результат, потому что JSON все еще неполный / malformed;
- `stop_reason = max_tokens`;
- usage:
  - input tokens: `171879`;
  - output tokens: `40000`.

Замечание по качеству частичного текста:

Модель действительно использовала широкий контекст между страницами и нашла реальные проблемы
проекта:

- заметила, что часть листов, похоже, имеет другой штамп проекта;
- нашла данные по стенам/блокам, плитам, опалубке, кровле и вентканалам;
- пометила много значений как `needs_review`, потому что текстовый слой PDF фрагментирован;
- увидела смешанные/неоднозначные значения, например опалубку торца плиты и опалубку балок.

Но это все равно не usable final `extraction_output.json`, потому что ответ уперся в output token
limit.

## Вывод

Идея full-KR2 / full-prompt правильная по направлению качества: она сохраняет контекст между
страницами. Но один монолитный JSON-ответ по всему KR2 слишком большой.

Рекомендованный следующий подход:

1. Оставить Opus 4.8.
2. Оставить полный prompt pack.
3. По возможности оставлять модели весь релевантный PDF-файл как контекст.
4. Не просить все разделы KR2 одним JSON-ответом.
5. Разбить KR2 на логические full-context задачи:
   - стены/перемычки;
   - плита 1 этажа;
   - плита 2 этажа;
   - плоская кровля;
   - вентканалы.
6. Альтернативно использовать группы разделов:
   - `flat_roof + schiedel_vent_channels`;
   - `floor_slab_1 + floor_slab_2`;
   - `load_bearing_walls_lintels`.

Это не то же самое, что слепая нарезка страниц: модель все еще может получать весь KR2 PDF/document,
но запрошенный output должен быть меньше и ограничен конкретным разделом, чтобы модель успела
закончить валидный JSON.

## Практический вывод

Для production API extraction нужен job plan:

```text
project file split (KR1/KR2)
→ full-file context
→ section-scoped extraction tasks
→ merge outputs
→ validate final JSON
```

Так мы сохраняем преимущество полного файла в контексте, но избегаем одного огромного ответа, который
не помещается в API output limit.
