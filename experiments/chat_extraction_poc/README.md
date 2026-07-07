# Claude Chat Extraction Pack (A6.1)

Экспериментально. Не production Telegram-flow, не API vision parser
(это отдельный эксперимент, см. `experiments/vision_pdf_parser_poc/`,
A6.0), не Google Sheet, не Excel-смета, не изменение текущих
parser/resolver/calculator файлов.

**Никакой API здесь не вызывается.** Извлечение делает человек
(Татьяна) вручную в обычном Claude-чате по Pro-подписке: загружает PDF
и файлы этого пакета, вставляет промпт, получает JSON, сохраняет его
руками. Всё, что есть в этой папке — только подготовка входных файлов
для этого чата и проверка результата после.

## Цель

Проверить, насколько хорошо интерактивная сессия в Claude-чате (с
человеком, способным сразу переспросить и свериться с PDF глазами)
извлекает данные для всех 8 калькуляторов сметы — в сравнении с
человеком-валидированным `input.json` по ЮСВ. Без подтасовок: эталон
не показывается модели во время извлечения (см. ниже).

## Структура

```
prompts/claude_estimate_extraction_prompt.md   - промпт для вставки в GPT/Claude чат
schemas/claude_extraction_output_schema.json   - форма ожидаемого JSON-ответа
data/calculator_targets_compact.json           - что искать, по 8 разделам (не все 629 параметров)
data/target_aliases_ru.yaml                    - русские алиасы строк PDF для маппинга target_code
data/section_guide.json                        - на каких листах что обычно бывает (без номеров страниц)
data/unit_normalization_guide.json             - таблица единиц измерения
README_FOR_CHAT_UPLOAD.md                      - инструкция для Татьяны, что грузить в чат и в каком порядке
build_claude_chat_pack.py                      - собирает dist/claude_chat_extraction_pack.zip
validate_claude_extraction.py                  - проверяет JSON, который вернул чат (источники, единицы, арифметика)
compare_with_validated_input.py                - сравнивает с human-validated input.json по ЮСВ
build_review_workbook_preview.py               - строит локальный preview workbook из GPT/Claude extraction_output.json
outputs/                                       - сюда Татьяна сохраняет ответ чата (gitignored, реальные данные)
reports/                                        - отчёты validate/compare (gitignored, реальные данные)
dist/                                           - собранный zip-пакет (gitignored)
```

## Как это использовать

1. Собрать пакет:
   ```
   .venv/bin/python3 experiments/chat_extraction_poc/build_claude_chat_pack.py
   ```
2. Дальше — по инструкции в `README_FOR_CHAT_UPLOAD.md` (загрузка в
   GPT/Claude-чат, сохранение ответа, запуск validate/compare).

## Preview Google Sheet structure from chat JSON

После получения `extraction_output.json` можно локально собрать preview
workbook без Telegram, Google API и калькуляторов:

```
.venv/bin/python experiments/chat_extraction_poc/build_review_workbook_preview.py path/to/extraction_output.json
```

По умолчанию результат пишется в:

```
experiments/chat_extraction_poc/outputs/review_workbook_preview.xlsx
```

Preview сохраняет структуру текущего earthworks review flow: листы
`00_Конструктор сметы`, `01_Проверка проекта`, `02_Цены себестоимости`,
`03_Детали объемов`, `04_Инструкция`, `05_Кандидаты parser`,
`06_Сырые данные parser`. Повторяющиеся данные, включая арматуру, остаются
на `03_Детали объемов`; отдельный лист арматуры не создаётся.

Лист `01_Проверка проекта` строится от 87 строк `AUTO_PROJECT high risk`
из `docs/elena_parameter_review_pack_audit.md` (июньское решение Елены).
`extraction_output.json` используется только как источник найденных
значений для этих строк; если GPT не нашел значение, строка остается
красной для ручного ввода/комментария.

## Честность сравнения

Во время извлечения (шаги 1–5 в `README_FOR_CHAT_UPLOAD.md`) чат не
должен видеть:
- `experiments/earthworks_calculator/cases/usv_yusupovo_village/input.json` (эталон);
- старый вывод парсера (`earthworks_parser.py` / `data/extracted/`);
- отчёты сравнения из прошлых экспериментов (A5.1a, A6.0).

Эти файлы используются только в `compare_with_validated_input.py`,
**после** того как результат извлечения уже получен и сохранён.

Главное правило A6.4: чат сначала сохраняет исходные строки таблиц в
`raw_table_rows`, затем маппит их на `target_code` через
`target_aliases_ru.yaml`. Сопоставление только по английскому имени
параметра запрещено.

## Откуда взят compact target list

`calculator_targets_compact.json` собран из
`experiments/pdf_parser_pipeline/section_schema.py` (`EXPLICIT_PARAMETERS`,
input_type `parsed`/`manual`) — это уже курированное подмножество,
проверенное в работе A4/A5 (не полные 629 auto-flattened параметров).
Поле `grounded: true` у цели значит, что именно этот параметр реально
проверялся на кандидатах USV/TRC (A4.2.7–A5.1a) и имеет resolver_hints
в парсере; `grounded: false` — параметр выведен из структуры
калькулятора (`input.json`/схема), но не проверялся независимо на
реальных PDF — к таким результатам стоит относиться с большим
скепсисом.
