# Adapter build plan — review_workbook.xlsx → calculator input, all 8 sections

Дата создания: 2026-07-12.

**Если контекст сессии прервался/сжался — читай этот файл первым, прежде чем начинать
раздел заново или гадать, что уже сделано.** Отмечай чекбоксы по мере готовности.

## 🔥 Актуальный план сборки сметы по АРК (добавлено 2026-07-30)

Этот раздел обновляет старые заметки ниже. Если ниже написано, что
`extraction_output.json -> review workbook` ещё не существует, это уже устарело: такой
шаг теперь есть в `populate_review_workbook_from_extraction.py`.

Текущий статус:

- `PDF/chat extraction -> extraction_output.json`: готово на стороне chat/API parser.
- `extraction_output.json -> review workbook`: готово.
  Скрипт: `experiments/full_estimate_review_pipeline/populate_review_workbook_from_extraction.py`.
- Лист `01_Проверка проекта`: заполняется из extraction JSON, включая scalar rows,
  production repeated rows и diagnostic repeated rows.
- Лист `01-1_Справочник`: заполняется из `output/manual_values_registry.xlsx`.
- Лист `02_Цены себестоимости`: заполняется из `output/price_registry_filled_v4.xlsx`.
- Лист `03_Детали объемов`: заполняется из `raw_table_rows` как evidence/control, не как
  источник калькулятора.
- `review workbook -> normalized_review`: core-reader готов
  (`review_to_calculator/core/workbook_reader.py`).
- `normalized_review prices -> resolved_prices`: core-resolver готов
  (`review_to_calculator/core/price_resolver.py`).
- `normalized_review -> calculator input`: НЕ ГОТОВО. Нет
  `review_to_calculator/sections/<section_code>/build_input.py`.
- `calculator results -> final estimate workbook`: НЕ ГОТОВО для all-section сметы.

Важное решение от 2026-08-03: универсальный `anti_cheat.py` в новый production-пайплайн пока не
делаем. Старый earthworks anti-cheat остается референсом, но не переносится как обязательный слой.
На текущем этапе нужен **audit gate** перед калькуляторами: явные blockers, проверки полноты листов
`01`/`01-1`/`02`, notes/confidence/needs_review, и громкое падение adapter при отсутствии обязательных
данных.

Ближайший план для АРК:

1. **Зафиксировать входы.**
   - Выбрать один canonical ARK extraction JSON. На 2026-07-30 самый свежий файл в Downloads:
     `/Users/tatanamedzidova/Downloads/gpt_arkadia_extraction(3).json`.
   - Скопировать его в repo/run folder, чтобы сборка не зависела от Downloads.
   - Не исправлять JSON вручную ради совпадения со сметой. Допустима только структурная
     нормализация под официальную schema, если файл невалиден.

2. **Пересобрать ARK review workbook.**
   - Использовать `populate_review_workbook_from_extraction.py`.
   - Обязательно брать свежие:
     `output/price_registry_filled_v4.xlsx` и `output/manual_values_registry.xlsx`.
   - Важно: `ark_review_workbook_with_prices_v5.xlsx` был создан раньше последней правки
     `price_registry_filled_v4.xlsx`, поэтому для реального прогона нужен новый workbook
     (`_v6` или следующий).

3. **Сделать audit gate перед калькуляторами.**
   - Проверить required rows sheet 01: found / needs_review / missing по каждому разделу.
   - Проверить required prices sheet 02: `price_registry`, `price_registry_empty`,
     `not_found`, `no_registry_code`.
   - Проверить sheet 01-1: какие manual/default-like values заполнены, какие остаются
     пустыми и должны быть заполнены Еленой.
   - Отдельно вывести blockers: поля, без которых adapter/calculator не должен стартовать.
   - Не называть этот слой `anti_cheat` и не пытаться сейчас воспроизвести старый earthworks
     `anti_cheat.py` для всех 8 разделов.

4. **Передать workbook Елене / получить исправленный workbook обратно.**
   - Елена правит листы `01`, `01-1`, `02`.
   - Sheet `03` остаётся справочным: смотреть можно, но adapter не читает его как источник.

5. **Написать adapters по одному разделу.**
   Target path:
   `experiments/full_estimate_review_pipeline/review_to_calculator/sections/<section_code>/build_input.py`.
   Каждый adapter должен:
   - брать только `normalized_review`, `resolved_prices`, contract defaults/manual values;
   - не читать sheet 03;
   - не брать значения из old cases/output/screenshot/old estimate;
   - fail loudly, если required value/price отсутствует;
   - явно выставлять production `*_calc_method`, чтобы calculator не упал в legacy.

6. **Порядок adapters для АРК.**
   - `earthworks` — есть старый earthworks-specific образец, но переносить только смысл, не
     старое чтение sheet 03.
   - `waterproofing` — маленький пилот для core.
   - `foundation_slab`.
   - `load_bearing_walls_lintels`.
   - `floor_slab_1`.
   - `floor_slab_2`.
   - `schiedel_vent_channels`.
   - `flat_roof`.

7. **Особые ARK риски, которые adapter/audit должен показать явно.**
   - Балки плит: бетон идёт по спецификации материалов, длина отдельно; ширина теперь не
     обязательна для работы, но нужна как diagnostic/context, если есть.
   - Утепление балок/перемычек не всегда на всю длину. Нельзя автоматически считать всю длину
     балки утепляемой, если PDF даёт отдельную длину утепления.
   - Монолитные перемычки: работа по длине, материал бетона по объёму.
   - Б4/Б4-1 в АРК может быть общей строкой по бетону/длине — не раскладывать по маркам без
     данных проектировщика.
   - Schiedel/вентканалы: различать брендированные покупные элементы Schiedel и generic
     газоблочные вентшахты. АРК может быть не Schiedel-case.
   - Flat roof: temporary door must not appear in calculator/final estimate; roof is flat roof,
     not a generic roof.

8. **Run calculators.**
   - Сначала запускать один раздел, не все 8 сразу.
   - Сохранять `normalized_review.json`, `calculator_input.json`, `calculator_result.json`,
     `adapter_report.md` в project run folder.
   - Calculator result source of final quantities is `estimate_lines`, not old Excel cells.

9. **Build final estimate workbook.**
   - Написать all-section exporter отдельно.
   - Источник строк: calculator `estimate_lines` + `catalogs/estimate_line_catalog.yaml` for
     ordering/layout metadata.
   - Review workbook and final estimate workbook remain separate artifacts.

10. **Compare against the real ARK estimate.**
    - Не подгонять код под ARK totals.
    - Отчёт должен классифицировать расхождения:
      parser missing, workbook/manual missing, price mismatch, calculator methodology mismatch,
      out-of-MVP/excluded row, real design/smeta ambiguity.

## ⚠️ Полный путь PDF → смета: что реально есть, а чего нет (добавлено 2026-07-13)

Этот файл называется «adapter build plan» и описывает только последний кусок пути —
чтение УЖЕ ЗАПОЛНЕННОЙ review-таблицы в вход калькулятора (Этап 0/1/2 ниже). Но перед
этим куском есть ещё два шага, и один из них **не существует нигде в репозитории**.
Полная цепочка:

1. **PDF → `extraction_output.json`** (ручной чат-экстракшн). Готово:
   `experiments/chat_extraction_poc/` — промпт, схема, `calculator_targets_compact.json`,
   `target_aliases_ru.yaml`. Пакет для загрузки в чат собирается
   `build_claude_chat_pack.py`.
2. **`extraction_output.json` → заполненная review-таблица (реальные значения на листах
   01/02/03).** ⚠️ **НЕ СУЩЕСТВУЕТ для текущей структуры.** Есть два независимых скрипта,
   не знающих друг о друге:
   - `build_review_workbook_from_contracts.py` (`full_estimate_review_pipeline/`) — строит
     ТЕКУЩУЮ, правильную структуру листов 01/03 (production_input блоки, row_data_json,
     колонки исправления — всё, что сделано вчера/сегодня), но **только пустой шаблон**
     из контрактов, без реальных данных.
   - `build_review_workbook_preview.py` (`chat_extraction_poc/`) — единственный скрипт,
     который реально берёт `extraction_output.json` и что-то заполняет, но построен по
     **июньскому списку из 87 строк** (`docs/elena_parameter_review_pack_audit.md`),
     `section_contract.yaml` вообще не читает, использует свой старый набор колонок,
     арматуру не разбивает на позиции (кладёт только на лист 03 общим блоком) — то есть
     это снимок структуры листа 01 ДО всего вчерашне-сегодняшнего редизайна. В его же
     README прямо сказано: «Preview... без Telegram, Google API и калькуляторов» — это
     диагностический POC-инструмент для проверки качества извлечения (сравнение с
     human-validated эталоном), не часть продакшн-конвейера.

   Нужно написать этот шаг заново — правдоподобно как расширение
   `build_review_workbook_from_contracts.py` (та же структура блоков и колонок, просто
   на вход дополнительно принимает `extraction_output.json` и заполняет «Найдено в
   проекте» / скрытый `row_data_json` вместо того, чтобы оставлять их пустыми), а не как
   правка `build_review_workbook_preview.py`.
3. **Локальный xlsx → реальная Google-таблица.** Функция публикации существует и
   универсальна: `experiments/earthworks_parser_google_stage1/google_sheets/
   google_sheet_publisher.py`, `publish_workbook_if_configured(workbook_path, title,
   sharing)`. Но она **нигде не вызывается** из `full_estimate_review_pipeline` — отдельно
   стоящий, никуда не подключённый кусок.
4. **Елена проверяет/правит в реальной Google-таблице.** Человеческий шаг, кода не
   требует, но требует понять, как заполненная/поправленная таблица потом попадает
   обратно в код (скачивание в xlsx? прямое чтение через Google Sheets API? — ещё не
   проверено, не предполагать одно из двух без проверки).
5. **Заполненная таблица → вход калькулятора.** Это Этап 0/1/2 ниже (`core/` +
   `sections/<code>/build_input.py`). `core/` готов и проверен — но только на копии
   шаблона, которую я заполняла вручную для теста, а не на таблице, реально прошедшей
   через шаги 2-4.

**Порядок работы: 2 → 3 → (4, человек) → 5.** Шаг 5 (Этап 1 ниже, `build_input.py`)
**отложен** — сначала нужно построить и своими глазами проверить шаг 2 (реальный JSON
корректно превращается в строки на листе 01), только потом возвращаться к
`sections/waterproofing/build_input.py`.

### Ещё два найденных пробела (2026-07-13, при проверке "а что с ценами и дефолтами")

- **Лист 02 (цены) страдает той же болезнью, что лист 01 страдал до вчера.**
  `build_prices_sheet()` всегда пишет «Цена из прайса»/«Цена fallback»/«Цена для
  расчёта» пустыми (`None, None, None`) — сама ячейка-подсказка в коде говорит
  «Заполнить цену из price registry/fallback/review», то есть автозаполнение
  задумывалось, но никогда не было написано. При этом реальный, рабочий регистр цен
  уже существует: `output/price_registry_filled_v3.xlsx` (лист `price_registry`, 78
  позиций с реальными ценами) + готовый код чтения с правильным приоритетом override
  проекта → registry → fallback (`experiments/pricing/price_reader.py`,
  `resolve_price()`, `experiments/pricing/live_pricing.py`). Сейчас этот механизм
  используется только тест-раннерами калькуляторов для сверки, к сборке review-таблицы
  не подключён вообще. Проверено покрытие: 103 из 129 `price_keys` по всем 8 разделам
  (80%) находятся в регистре напрямую; часть непокрытых — не пробел в данных, а
  структурная особенность (например `rebar_unit_price_by_item` резолвится по каждой
  позиции арматуры отдельно через шаблонный код `rebar_<class>_d<diameter>_m`, не одним
  плоским ключом). Нужно расширить `build_prices_sheet()`, чтобы она читала
  `price_registry_filled_v3.xlsx` и предзаполняла «Цена из прайса» по `registry_code`
  каждого `price_key` — тот же принцип, что и для листа 01 (шаг 2 выше), просто для цен.
- **Серьёзнее, чем просто "лист 02 пустой": бо́льшая часть того, что якобы "находится в
  регистре", на самом деле непроверенные заглушки, а не реальные цены поставщиков.**
  Пользователь описала ситуацию из памяти («прайс от Елены — там только материалы, цен
  на работы нет, решили брать дефолты из сметы ЮСВ, Елена поправит в таблице») — проверила
  файлы, подтвердилось буквально всё, с цифрами:
  - `price_registry_filled_v3.xlsx` содержит 6 листов: `price_registry` (итоговый) + 5
    листов сырых поставщицких данных по категориям — «Бетон + песок», «Пиломатериалы
    (Олег)», «Блокпаротермшидель (Алексей)», «Металл (Алексей)», «Утеплители/плёнки/
    мастика (Олег)». Среди пяти категорий **нет ни одной с работами** — только материалы.
  - Есть служебный лист `rows_to_add`: 63 строки с комментарием «Добавлено из
    калькулятора MVP, требуется проверка Елены» и статусом `needs_review` (59) /
    `requires_decision` (4) — это и есть цены на работы, вытащенные как временная
    заглушка из чисел старых тестовых кейсов калькуляторов (историческая смета ЮСВ).
  - Из 182 строк сырых данных только 81 вообще имеет `price_code` (без него
    `load_price_registry()` в `price_reader.py` строку молча пропускает) — остальные 101
    (в основном бетон по зонам/поставщикам без выбранного правила «какого поставщика
    использовать») не резолвятся в принципе. Из тех 81, что резолвятся, **63 (78%) — это
    заглушки из `rows_to_add`**, и только 18 — что-то ещё.
  - Значит цифра «103 из 129 price_keys находятся в регистре (80%)» из бюллета выше
    формально верна, но вводит в заблуждение: почти всё найденное — старые числа-заглушки
    из сметы ЮСВ, а не свежие подтверждённые цены поставщиков.

  **ИСПРАВЛЕНИЕ (2026-07-13, тем же днём позже):** первая версия этого пункта утверждала,
  что статус `needs_review`/`requires_decision` при переносе из `rows_to_add` в
  `price_registry` потерялся, и строки стали неотличимы от подтверждённых цен. Это
  оказалось неверно — я проверила только наличие кода, не текст самого комментария.
  Перепроверила построчно все 63: **51 строка** сохранила ровно исходный текст
  («Перенесено из rows_to_add, статус: needs_review. Добавлено из калькулятора MVP,
  требуется проверка Елены.»), ещё **12** (фанера, кровельный ЭППС ТехноНИКОЛЬ, геотекстиль
  и т.п.) имеют другой, но тоже явный текст («price_code проставлен автоматически по
  точному совпадению номенклатуры; проверьте цену/единицу»). То есть ни одна из 63 строк
  не осталась без предупреждения — правку `price_registry` делать не нужно.

  **Дополнительно проверила комментарии по всем 182 строкам листа `price_registry`
  целиком (не только эти 63), по просьбе пользователя.** Картина логичная и
  последовательная:
  | Категория | Кол-во |
  |---|---:|
  | Перенесено из `rows_to_add` (needs_review/requires_decision) | 51 |
  | Сырая позиция поставщика по зоне («Поставщик: ...») | 24 |
  | Автоматически сопоставлено по номенклатуре, «проверьте цену/единицу» | 14 |
  | Разное («Каталожная/поставщическая позиция, price_code не проставлен...» и т.п.) | 84 |
  | Пересчитано в другую единицу измерения | 1 |
  | Без комментария вообще | 8 |

  Из 8 строк без комментария — 6 это ровно те реальные, датированные (2026-07-11) цены
  на арматуру (`rebar_a500_d25_m`/`d16_m`/`d12_m`/`d10_m`, `rebar_a240_d8_m`/`d6_m`),
  найденные раньше как настоящие подтверждённые цены; комментарий там пуст не потому,
  что метка потерялась, а потому что эти строки уже не нуждаются в проверке. Ни одна
  строка не выглядит подтверждённой, будучи на деле заглушкой.

  **Единственное, что реально нужно на будущее:** когда будет писаться заполнение листа 02
  из этого файла, код должен скопировать текст из колонки «Комментарий» в колонку «Нужно
  внимание»/«Комментарий» листа 02, чтобы Елена его увидела — просто не забыть про это при
  реализации, отдельной правки данных сейчас не требуется.
- **`defaults:` — не пробел, осознанный дизайн, но маленький недочёт в `job_runner.py`
  нашёлся.** У записей `defaults:` в контракте нет `review_sheet`/`show_to_user` —
  они не предназначены попадать на лист 01/02 Елене на глаза, это чисто кодовые
  константы (коэффициент запаса, объём упаковки и т.п.), уже лежат прямо в контракте
  как `value:`. `core/contract_loader.py` уже умеет их отдавать. Но
  `core/job_runner.py`'s `run_section()` сейчас передаёт в `build_calculator_input()`
  только `normalized_review` — сам контракт не передаётся, значит каждому
  `build_input.py` придётся самому ещё раз грузить контракт, чтобы достать дефолты.
  Работает, но лишнее дублирование — стоит поправить `job_runner.py`, чтобы отдавал
  контракт вместе с `normalized_review`, до того как писать первый `build_input.py`.

## ⚠️ Критическое правило (добавлено 2026-07-12, читать в первую очередь)

**Вход калькулятора собирается только из данных листов `01_Проверка проекта` и
`02_Цены себестоимости`. Лист `03_Детали объемов` — только справочная информация для
Елены (визуальная сверка с PDF), в calculator input он НЕ читается.**

Это прямо противоположно тому, как было устроено в earthworks — там
`calculator_input_builder.py`'s `_build_trench_routes()`/`_build_communications_pipe_items()`
читали именно лист 03. Так больше не делаем. earthworks-код в этой части — только
антипример/история, не образец для переноса.

### Следствие: дизайн листа 01 под repeated_rows (ГОТОВО, 2026-07-12/13)

Первая версия этого плана (2026-07-12) предлагала рендерить на листе 01 «полноценный
блок с настоящими колонками из `columns` контракта» — то есть копию того, что теперь
живёт на листе 03. Пользователь это прямо отклонил: **на листе 01 никаких
таблиц/колонок под каждую позицию, только построчно, в тех же 13 колонках, что и везде**
(«в листе 01 никаких таблиц и колонок. это все как раз на листе 03, там именно как в
спецификации»). Финальный дизайн — компромисс, выработанный в диалоге:

- Не ВСЕ `repeated_rows`-группы получают построчный разбор на листе 01. Только те, где
  калькулятор в проде реально читает эту форму как вход (нет альтернативы-скаляра).
  Новое поле контракта `production_input: true/false` на каждой `repeated_rows`-группе
  (добавлено 2026-07-12, проверено по коду каждого калькулятора):
  - `true` (7 групп — идут построчно на лист 01): `foundation_rebar_items`,
    `floor_slab_1_rebar_items`, `floor_slab_2_rebar_items`, `main_wall_rebar_items`,
    `lintel_rebar_items`, `beam_items` (floor_slab_1 и floor_slab_2).
  - `false` (5 групп — остаются как одна скалярная строка, как раньше; построчная
    разбивка есть только на листе 03, необязательная сверка): `trench_routes`,
    `communications_pipe_items` (earthworks — калькулятор в проде берёт готовый скаляр),
    `roof_raw_material_spec_rows`, `beam_table_controls`, `schiedel_vent_chimney_cladding_segments`.
- Для 7 production-групп на листе 01 — блок (как на листе 03), но с ДРУГИМ набором
  колонок: не полная спецификация, а те же 13 стандартных колонок (A-M, включая скрытые
  `section_code`/`technical_key`/`source_class`/`target_code`) + несколько ВИДИМЫХ
  колонок «Исправить: <поле>» — по одной на каждое реально корректируемое числовое поле
  группы, а не общая «Исправить/ввести значение» на всех сразу (по прямому требованию:
  «нельзя приучать елену исправлять число в той же ячейке»). Плюс одна СКРЫТАЯ колонка
  `row_data_json` в самом конце — полный структурный набор значений строки (для
  адаптера, не для Елены — текст в «Найдено» она просто читает, не парсит).
  Новые поля контракта на каждой из 7 групп: `item_label_columns` (какие поля из
  `columns` формируют текст в «Что проверяем», например `[steel_class, diameter_mm]` →
  «A500 ⌀10») и `correction_columns` (какие поля получают свою колонку исправления,
  например `[spec_length_m, kg_per_meter]` → «Исправить: Длина по спецификации, мп» /
  «Исправить: Масса 1 м, кг/м»). Каталожные/адаптерные поля вроде `rod_length_m` и
  `unit_price_per_m` НЕ включены ни в `item_label_columns`, ни в `correction_columns` —
  это не PDF-данные, Елена их вообще не видит на листе 01, их подставляет адаптер/каталог
  позже.
- Максимум 4 колонки исправления (столько нужно балкам: длина/ширина/высота/кол-во;
  арматуре нужно 2 — длина/масса, остальные 2 слота у неё просто пустые в заголовке
  блока). Колонки фиксированы по номеру (N/O/P/Q) на весь лист, но текст заголовка
  каждый блок пишет свой (тот же приём, что и у блоков на листе 03) — значение "N" для
  одного блока значит «длина», для другого — «ширина».
- `build_project_sheet()` в `build_review_workbook_from_contracts.py` переписан
  (2026-07-12/13): скаляры (и 5 diagnostic-only repeated_rows групп) идут как раньше,
  одной строкой; 7 production-групп — через `append_block()`, как на листе 03, но с
  этим особым набором колонок и БЕЗ строк-примеров (шаблон контрактов не содержит
  реальных данных проекта — так же, как и блоки на листе 03). Проверено на
  пересобранном `step_12_all_sections_review_template.xlsx`: `project_item_blocks: 7`,
  `project_parameter_rows: 101` (было 108 — минус 7 групп, ушедших из плоского потока).
- Лист 03 не менялся — он и так уже был read-only зеркалом с полным набором колонок
  (сделано 2026-07-11), сейчас он даже более «полный» вид данных, чем лист 01 — это и
  задумано: лист 03 = «выглядит как в спецификации», лист 01 = «что реально
  проверяется/правится».

## Зачем этот файл

Пользователь попросил письменную инструкцию для будущей себя (Claude), потому что задача
большая и многосессионная — легко потерять нить на середине. Это не memory-заметка, а
рабочий план в репозитории, обновляемый по ходу дела.

## Контекст на момент написания (2026-07-12)

Что уже готово:
- Все 8 `section_contract.yaml` (earthworks, foundation_slab, waterproofing,
  load_bearing_walls_lintels, floor_slab_1, floor_slab_2, flat_roof,
  schiedel_vent_channels) полностью достроены и сверены с калькуляторами напрямую по
  исходнику. Все 8 калькуляторов проходят свои test suites с 0 mismatch.
- `experiments/full_estimate_review_pipeline/build_review_workbook_from_contracts.py`
  строит единую 6-листовую review-таблицу (`00_Конструктор сметы`, `01_Проверка
  проекта`, `02_Цены себестоимости`, `03_Детали объемов`, `04_Инструкция`,
  `05_Кандидаты parser`, `06_Сырые данные parser`) для всех 8 разделов сразу из
  контрактов. Лист 03 (2026-07-11/12) теперь рендерит реальные повторяющиеся группы
  (арматура/балки/т.д.) каждого раздела со своими настоящими колонками — 12 групп по
  всем 8 разделам (было 13, минус удалённый 2026-07-12 `lintel_items` — в реальных PDF
  ЮСВ/ТРЦ нет разбивки перемычек по маркам, только готовые агрегаты), а не только
  generic-заглушки.
- Публикация локального xlsx в реальный Google Sheet уже есть и уже общая, не
  earthworks-специфичная: `experiments/earthworks_parser_google_stage1/google_sheets/
  google_sheet_publisher.py`, функция `publish_workbook_if_configured(workbook_path,
  title, sharing)` — берёт любой xlsx-путь + заголовок, публикует через OAuth.

Чего нет вообще ни для одного раздела, кроме earthworks:
- Кода, который читает **заполненную** (проверенную Еленой) review-таблицу обратно в
  JSON и собирает из него вход конкретного калькулятора раздела.

Единственный существующий образец — `experiments/earthworks_review_to_calculator/`
(~12k строк). **Это не production-код для копирования** — пользователь явно сказал, что
эта папка сейчас не участвует в production-процессе. Это образец того, что реально
работало, и источник вдохновения по структуре.

### Что из earthworks-слоя реально переиспользуется, а что — только образец

Прочитано и разобрано (детали — в самом плане `/Users/tatanamedzidova/.claude/plans/
tingly-wiggling-mountain.md`, если он ещё существует; краткая выжимка ниже):

| Файл earthworks-слоя | Статус для остальных 7 разделов |
|---|---|
| `constants.py` | Не переносить как есть — все required params/prices/defaults уже есть в `section_contract.yaml`, читать оттуда, а не дублировать вручную. |
| `review_workbook_reader.py`, листы 01/02 | Почти общий код — заголовки `PROJECT_HEADERS`/`PRICE_HEADERS` одинаковы для всех разделов, можно обобщить один раз. |
| `review_workbook_reader.py`, лист 03 (`read_details_sheet`, `build_trench_item`, `build_communication_item`) | **Антипример, не образец.** В earthworks лист 03 читался как источник данных для калькулятора (`trench_routes`/`communications_pipe_items` уходили прямо в calculator input). Теперь так делать нельзя — см. правило выше. Репитед-роу данные (арматура/балки/т.п.) читаются с листа 01 (после Этапа -1), лист 03 в `core/workbook_reader.py` не читается вовсе. |
| `calculator_input_builder.py` → `build_calculator_input()` | **Не обобщается принципиально.** У каждого калькулятора свои имена полей и вложенность (пример: `floor_slab_1_calculator.py` — единственный с вложенной структурой `geometry/rates/insulation/beams/manual_lines`; `load_bearing_walls_lintels` — 9 разных `*_calc_method` с disjoint required-полями). Писать маленькую функцию на раздел, опираясь на `calculator_input_mapping` из соответствующего `section_contract.yaml` как на спецификацию. Дополнительно: earthworks-версия читала `trench_routes`/`communications_pipe_items` из sheet-03-данных — при переносе на новую архитектуру брать их из репитед-роу блоков листа 01, не с листа 03. |
| `run_full_review_flow.py` (8-шаговый CLI-оркестратор) | Параметризуется по `section_code`, структура шагов переиспользуется. |
| `anti_cheat.py` | **Не переносить сейчас в production.** Старый earthworks anti-cheat оставить как reference; вместо него на текущем этапе делать audit gate и loud-fail adapters. |
| `job_state.py`, `job_locator.py`, `build_job.py` | Вероятно обобщаются почти без изменений — не читала в деталях, проверить при реализации. |

## Целевая архитектура

```
experiments/full_estimate_review_pipeline/review_to_calculator/
  ADAPTER_BUILD_PLAN.md         # этот файл
  core/
    contract_loader.py          # читает section_contract.yaml: required params/prices/defaults
    workbook_reader.py          # читает листы 01/02 → normalized dict, общий для всех разделов (написан, 2026-07-13)
    price_resolver.py           # резолвит цены по calc_price_key, fail-loudly (написан, 2026-07-13)
    job_runner.py                # оркестрация: contract → workbook → prices → build_input → calculator (написан, 2026-07-13)
  sections/
    earthworks/build_input.py
    foundation_slab/build_input.py
    waterproofing/build_input.py
    load_bearing_walls_lintels/build_input.py
    floor_slab_1/build_input.py
    floor_slab_2/build_input.py
    flat_roof/build_input.py
    schiedel_vent_channels/build_input.py
  run_review_to_calculator.py   # CLI: --section <code> --workbook <path>
```

Не копировать `earthworks_review_to_calculator/` восемь раз — один общий движок в
`core/`, и только последний шаг (сборка входа конкретного калькулятора) — маленький
ручной файл на раздел в `sections/<code>/build_input.py`.

## Порядок работы (галочки — по мере готовности)

### Этап -1 — доделать лист 01 под repeated_rows (ЗАКРЫТО 2026-07-13)

- [x] Добавлено поле контракта `production_input: true/false` на все 12
      `repeated_rows`-групп по всем 8 разделам (7 true, 5 false) — проверено по коду
      каждого калькулятора, какая форма реально читается в проде, а не предполагалось.
- [x] Добавлены поля `item_label_columns`/`correction_columns` на 7 production-групп;
      каталожные/адаптерные поля (`rod_length_m`, `unit_price_per_m`) туда сознательно
      не включены.
- [x] `build_project_sheet()` переписан: скаляры + 5 diagnostic-only групп — одна строка
      как раньше; 7 production-групп — блок через `append_block()` со стандартными 13
      колонками + до 4 видимых колонок «Исправить: <поле>» + 1 скрытая `row_data_json`.
      Подробности дизайна и почему он именно такой — см. раздел «⚠️ Критическое правило»
      выше.
- [x] Лист 03 не менялся — уже был read-only зеркалом с 2026-07-11, дублирования
      источников истины нет (лист 01 = данные для адаптера, лист 03 = только для чтения
      человеком).
- [x] Перегенерирован `step_12_all_sections_review_template.xlsx`, проверено глазами
      (структура заголовков, видимые/скрытые колонки) на примере
      `floor_slab_1_rebar_items` и `beam_items`.

**Теперь `core/workbook_reader.py` для production repeated_rows групп будет читать: по
каждой строке блока — скрытые `technical_key`/`target_code` (какая это группа), скрытый
`row_data_json` (полный набор значений строки, основной источник), и видимые
«Исправить: ...» колонки (если Елена что-то вписала туда — это override поверх
`row_data_json`, для этого конкретного поля). Программе для реальных данных
конкретного проекта ещё предстоит: 1) заполнить эти блоки настоящими строками
(отдельный шаг — либо ручной ввод Еленой, либо будущий шаг чат-извлечения → заполнение
шаблона, ещё не спроектирован), 2) написать сам ридер (сделано — см. Этап 0 ниже).**

Оказалось проще, чем предполагалось: искать границы блоков не нужно вообще. Ридер просто
проходит все строки листа 01 подряд и смотрит на скрытую колонку `technical_key` — если
её значение совпадает с ключом одной из `production_repeated_row_params(contract)`, это
строка-позиция этой группы (независимо от того, в каком блоке физически находится).
Строка-заголовок блока сама по себе не совпадает ни с одним ключом группы (там в
`technical_key` буквально текст «technical_key», это же используется для отделения
заголовков от данных) и просто пропускается.

### Этап 0 — core/ (строится один раз) — ЗАКРЫТО 2026-07-13

Все 4 файла (`contract_loader.py`, `normalization.py`, `workbook_reader.py`,
`price_resolver.py`, `job_runner.py`) написаны и проверены сквозным прогоном на
тестовой книге. Дальше — Этап 1, пилот на waterproofing (нужен только
`sections/waterproofing/build_input.py`, всё остальное уже готово).

- [x] `core/contract_loader.py` — читает `section_contract.yaml`, отдаёт required
      review_parameters/supplier_inputs, price_keys, defaults,
      `production_repeated_row_params`. Проверено на всех 8 контрактах (0 ошибок,
      7 production repeated_rows групп нашлось суммарно — совпадает с ожиданием).
- [x] `core/normalization.py` — маленькие чистые хелперы (`cell_text`, `parse_number`,
      `is_blank`), без бизнес-логики; переписаны заново по образцу
      `earthworks_review_to_calculator/normalization.py` (сам файл не импортируется).
- [x] `core/workbook_reader.py`, чтение листа 01 (скаляры) и листа 02 — общая часть,
      написана по образцу `earthworks_review_to_calculator/review_workbook_reader.py`
      (`find_header_row`, `header_map`), но без хардкода `REQUIRED_PARAMETERS` — список
      ключей берётся из контракта. `read_scalar_parameters()` — override из
      «Исправить / ввести значение» побеждает «Найдено в проекте», если не пусто, тот же
      принцип для цен на листе 02 (`read_prices()`).
- [x] `core/workbook_reader.py`, чтение production repeated_rows блоков с листа 01
      (`read_production_item_rows()`) — читает `row_data_json` каждой строки как основной
      источник, поверх накладывает значения из видимых колонок «Исправить: ...» по
      порядку `correction_columns` контракта (N/O/P/Q — фиксированные позиции, но их
      значение per-group разное, поэтому сопоставление именно через список контракта, а
      не текст заголовка).
- [x] Проверено вручную: скопирован `step_12_all_sections_review_template.xlsx`, вписаны
      тестовые значения на листах 01/02 (в т.ч. override на скаляре, override на цене,
      override на одном числовом поле одной строки арматуры и на длине балки) —
      `read_review_workbook()` для waterproofing и floor_slab_1 вернул корректные,
      правильно приоритизированные значения по всем случаям.
- [x] **Лист 03 в `core/workbook_reader.py` НЕ читается вообще** — `read_review_workbook()`
      открывает только `01_Проверка проекта` и `02_Цены себестоимости`, лист 03 нигде в
      коде `core/` не упоминается.
- [x] **Найден и исправлен реальный баг (2026-07-13): `technical_key`/`calc_price_key` не
      уникальны глобально по листу, только в пределах раздела.** Пример: `beam_items`
      объявлен и у floor_slab_1, и у floor_slab_2; `eps100_unit_price` — сразу у
      waterproofing, floor_slab_2 и foundation_slab (это тот же класс коллизии
      `group_code`, что уже ловили в парсер-файлах раньше в этой сессии, просто теперь на
      уровне review-таблицы). Без фильтра по `section_code` ридер молча брал ПЕРВУЮ
      попавшуюся строку с нужным ключом — не обязательно строку своего раздела. Поймано
      руками: `resolve_prices()` для waterproofing вернул для `eps100_unit_price` цену,
      реально вписанную в строку foundation_slab. Все три функции чтения
      (`read_scalar_parameters`, `read_production_item_rows`, `read_prices`) теперь
      дополнительно фильтруют по `section_code == contract["section"]["code"]`, не только
      по ключу. Перепроверено: то же тестовое значение больше не протекает в чужой
      раздел, `floor_slab_2`'s пустой `beam_items` не подмешивается к `floor_slab_1`'s
      заполненному.

      **Решение, принятое 2026-07-13: чиним на уровне чтения (фильтр по section_code
      внутри core/workbook_reader.py), а не переименовываем ключи в контрактах.** Так
      сделано, потому что весь будущий код (job_runner.py, все 8 build_input.py) будет
      обращаться к листам 01/02 только через эти три функции, а не напрямую — значит
      защита уже встроена в архитектуру один раз, а не держится на том, что кто-то не
      забудет добавить фильтр в новом месте. Работает, проверено.

      **Можно сделать по-другому позже, если понадобится:** переименовать `price_keys`/
      `review_parameters` ключи так, чтобы они были уникальны глобально по всему проекту
      (например, `eps100_unit_price` → `waterproofing_eps100_unit_price`), как уже
      сделано для коллизии `vent_chimney_cladding_segments` в парсер-файлах (переименована
      в `schiedel_vent_chimney_cladding_segments`, 2026-07-10). Это устранило бы саму
      возможность коллизии, а не только защищало бы чтение, и сделало бы читаемее сырой
      JSON при отладке — но требует правки всех 8 `section_contract.yaml` разом. Не
      обязательно, не блокирует дальнейшую работу — просто вариант на будущее, если
      захочется.
- [x] `core/price_resolver.py` — не прямой перенос `_build_internal_prices()` (та работала
      со списком строк одного раздела и earthworks-специфичным полем
      `consumables_amount`), а более узкая функция: на входе — результат
      `read_prices()` + контракт, на выходе — `{calc_price_key: number}` только для того,
      что реально нужно; **падает с `PriceResolutionError`, если для обязательного
      `price_keys` нет `selected_price`** (никогда не возвращает частичный результат
      молча). Куда именно класть каждую цену в вход калькулятора (плоский `rates`,
      `calculator_input_path`, цена внутри строки арматуры) — решает
      `sections/<code>/build_input.py`, не этот модуль. Проверено на waterproofing:
      сначала правильно упал (4 из 6 цен не заполнены), после заполнения всех —
      вернул чистый словарь.
- [x] `core/job_runner.py` — не перенос `run_full_review_flow.py` (у того 8 subprocess-шагов
      с lineage/anti-cheat/excel-export отчётами, которых в новой архитектуре пока просто
      нет — ни одного `build_input.py` ещё не существует). Написан заново, узко:
      `run_section(section_code, workbook_path)` = contract_loader → workbook_reader →
      price_resolver → динамически импортированный `sections/<code>/build_input.py`
      (`build_calculator_input()`) → динамически импортированный калькулятор раздела
      (`calculate_<section_code>`). Падает с понятной ошибкой на первом отсутствующем
      звене, не позже.
      Найдено и решено по ходу (2026-07-13): 4 из 8 калькуляторов
      (earthworks/foundation_slab/waterproofing/load_bearing_walls_lintels) принимают
      типизированный dataclass `<Section>Input` с `from_dict()`, остальные 4 — простой
      `dict`. `_prepare_calculator_argument()` определяет это сама по типовой аннотации
      функции `calculate_<section_code>` (не хардкод по имени раздела) — проверено на
      всех 8. Два технических нюанса при динамической загрузке модулей калькуляторов:
      (1) все калькуляторы используют `from __future__ import annotations`, поэтому
      аннотации типов — строки в рантайме, нужен `inspect.signature(fn, eval_str=True)`,
      а не голый `.annotation`; (2) датаклассы, загруженные через
      `importlib.util.spec_from_file_location`, падают при обработке полей, если модуль
      не зарегistrирован в `sys.modules` до `exec_module()` — датакласс внутри резолвит
      свой `__module__` через `sys.modules[...]`. Оба нюанса пойманы прогоном на всех
      8 калькуляторах, не только предположены.
      Проверено сквозным прогоном `run_section()` на тестовой книге: waterproofing (цены
      заполнены) доходит ровно до отсутствующего `build_input.py`; floor_slab_1 (цены не
      заполнены) корректно падает раньше — на `resolve_prices()`. `run_full_review_flow.py`
      использован только как справка по общей форме потока, код не копировался.

### Этап 1 — пилот на одном разделе

**РАЗБЛОКИРОВАНО 2026-07-30.** Старый блокер от 2026-07-13 закрыт:
`populate_review_workbook_from_extraction.py` теперь строит review workbook из реального
`extraction_output.json`, заполняет sheet 01/01-1/02/03 и уже проверялся на ARK. Перед
первым `build_input.py` всё равно нужно сделать свежий ARK rebuild на последнем JSON и
последнем `price_registry_filled_v4.xlsx`, затем пройти audit gate из раздела
"Актуальный план сборки сметы по АРК" выше.

- [x] Раздел-пилот: **waterproofing** (самый маленький калькулятор, 8 строк сметы,
      плоский вход, 0 обязательных supplier_inputs, уже 0 mismatch на всех тестах).
      Цель — проверить весь core/ end-to-end на дешёвом случае, прежде чем писать
      остальные 7 `build_input.py`.
- [x] `sections/waterproofing/build_input.py` написан.
- [x] Прогнан против `experiments/waterproofing_calculator/cases/test_waterproofing_
      spec_area/expected.json` — 0 mismatch (`calculation_blocks` и `estimate_lines`
      оба сверены программно, не на глаз).

**ЭТАП 1 ЗАКРЫТ 2026-08-05.** Первый в проекте реально работающий путь
«заполненная таблица → вход калькулятора → результат» подтверждён сквозным прогоном
(`core.job_runner`-эквивалент вручную: `read_review_workbook` →
`resolve_prices` → `build_calculator_input` → `WaterproofingInput.from_dict` →
`calculate_waterproofing`). Три находки по ходу:

1. **Реальный (пока не сработавший) баг в `core/workbook_reader.py`, исправлен**:
   `CORRECTION_COLUMN_LETTERS`/`JSON_COLUMN_LETTER` были захардкожены под
   13-колоночный лист 01 (N-Q + R) от 2026-07-13 — с тех пор лист вырос до 14 колонок
   (добавился `target_code`), реальные позиции сейчас O-R + S. На waterproofing не
   сработал (у неё нет ни одной `repeated_rows`-группы), но сломал бы каждый
   следующий раздел с арматурой/балками молча (не тот столбец, не то поле). Исправлено
   и сверено напрямую с `build_review_workbook_from_contracts.py`'s
   `PROJECT_HEADERS`/`ITEM_BLOCK_HEADERS`, не подбором.
2. **`project_name` — добавлено чтение**: `core/workbook_reader.py` вообще не читал
   его никак. Добавлена `read_project_name(wb)` — берёт заголовок листа 01 (A1,
   `"Разбор проекта: <адрес>"`, пишется `populate_review_workbook_from_extraction.py`),
   срезает префикс. Общий код в `core/`, не костыль в одном `build_input.py`.
3. **Найден и ЗАКРЫТ реальный, уже задокументированный пробел в контракте** (не баг
   адаптера): `eps50_pack_volume_m3`'s `defaults.value` был буквально `None`, с
   пометкой «not yet resolved», тот же пробел был и у `foundation_slab`. Проверила в
   3 реальных сметах подряд (АРК для ИИ.xlsx строка 108, Сметный расчет ЮСВ строки
   55-56, ТРЦ_3_точный_расчет строки 74-75) — объём пачки Пеноплэкс ГЕО буквально
   `0,2776` м3 в каждом случае, одинаковый и для 50мм, и для 100мм слоя (тот же
   физический короб упаковки, просто разное количество листов внутри). Вписано в оба
   контракта (`waterproofing`, `foundation_slab`) 2026-08-05. Пилот перепрогнан целиком
   через `core.job_runner.run_section()` без единого ручного патча — 0 расхождений
   подтверждены заново.

**Освежённый конкретный план (2026-08-05), после чтения `WaterproofingInput`
(~26 полей, плоский dataclass с `from_dict()`), `section_contract.yaml`'s
`calculator_input_mapping` и `core/`'s реального API:**

1. Таблица соответствия полей `WaterproofingInput` → источник:
   - 4 поля из `review_parameters` (через `normalized_review["scalar_parameters"][key]
     ["value_number"]`): `waterproofing_area_m2` (required), `eps100_wall_volume_m3`
     (required), `eps100_wall_insulation_area_m2` (optional), `eps50_wall_volume_m3`
     (optional, null когда отсутствует — не 0, см. поле notes в контракте).
   - `waterproofing_area_calc_method` — фиксированно `"spec_area"` (contract fallback).
   - `project_name` — спецтрансформ `job_metadata_project_name`. **Открытый вопрос**:
     `core/workbook_reader.py`'s `read_review_workbook()` вообще не читает
     project_name — нет такого источника в `normalized_review`. Решить до/во время
     написания `build_input.py` (варианты: читать из листа `00_Конструктор сметы`,
     передавать отдельным параметром в `run_section()`, или как временную заглушку
     взять имя файла книги — выбрать самый дешёвый вариант, не изобретать новый слой
     контракта ради одного поля).
   - Остальные ~20 полей (цены, коэффициенты, объёмы упаковки) — механически из
     `contract_loader.defaults(contract)`/`default_by_key(contract)` и из
     `normalized_review["resolved_prices"]` по совпадению имени ключа с именем поля
     dataclass (проверено по `calculator_input_mapping`'s wildcard-запись
     `input_path: "*", from: {ref: "defaults + price_keys"}, transform:
     fill_remaining_calculator_fields` — так и назван transform в контракте, эта
     функция и есть его реализация).
2. Написать `sections/waterproofing/build_input.py`:
   `build_calculator_input(normalized_review: dict) -> dict`. Подгружает контракт сам
   (`core.contract_loader.load_contract("waterproofing")`), не полагается на то, что
   `normalized_review` несёт дефолты/цены-по-ключу — там только то, что реально
   прочитано с листов 01/02 плюс `resolved_prices`, добавленные `job_runner.py`.
3. Прогнать через `core.job_runner.run_section("waterproofing", <path>)` на копии
   пустого шаблона книги (`output/step_12_all_sections_review_template.xlsx` или
   свежесобранный аналог), куда вручную вписаны те же значения, что в
   `experiments/waterproofing_calculator/cases/test_waterproofing_spec_area/input.json`
   (готовый реальный тест-кейс калькулятора, `spec_area`-метод, 0 mismatch) — построчно
   на листы 01 (значения) и 02 (цены).
4. Сравнить `result` с `cases/test_waterproofing_spec_area/expected.json` — 0
   расхождений = адаптер верный. При необходимости повторить со вторым кейсом
   (`test_waterproofing_foundation_slab`, `legacy_perimeter_height` метод) для
   уверенности, что оба `waterproofing_area_calc_method` пути работают.
5. Отметить чекбоксы выше, задокументировать паттерн (явные review_parameters +
   механический defaults/price fallback по имени поля) как образец для следующих 7
   `build_input.py` — но не обобщать сам код раньше времени, только паттерн/подход.

### Этап 2 — раскатка на оставшиеся 7 (порядок — от простого к сложному)

- [x] `earthworks` — образец уже есть целиком, перенести под новый `core/`.
- [x] `schiedel_vent_channels`
- [x] `foundation_slab`
- [x] `floor_slab_2`
- [x] `floor_slab_1`
- [x] `flat_roof`
- [x] `load_bearing_walls_lintels` (самый сложный — 12 `*_calc_method` режимов, не 9)

#### `load_bearing_walls_lintels` (2026-08-06) — восьмой и последний адаптер Этапа 2

Единственная typed-dataclass секция после foundation_slab/waterproofing/earthworks (не
plain-dict), но БЕЗ вложенности вообще (в отличие от floor_slab_1) — все ~90 полей
верхнего уровня, включая цены (никакого `rates.`-префикса). Самая большая секция пайплайна:
12 `*_calc_method` полей (в памяти раньше значилось "9" — недосчёт, актуализировано).

Фиксированные production calc_method: `scaffolding_calc_method=floors_based`,
`cutoff_waterproofing_calc_method=spec_area`, `lintel_length_calc_method=spec_total_length`,
`lintel_concrete_calc_method=spec_volume`, `main_wall_rebar_calc_method=spec_length_items`,
`lintel_rebar_calc_method=spec_length_items`,
`main_walls_crane_calc_method=delivery_trucks_threshold` (полностью автоматический — смены
крана считаются из количества машин доставки блоков, `main_walls_crane_shifts` в этом режиме
вообще не читается и намеренно не выставляется),
`upper_floor_calc_method=floor_2_spec_volume`, `parapet_calc_method=flat_roof_spec_volume`,
`vent_chimney_cladding_calc_method=flat_roof_spec_volume`,
`vent_chimney_geometry_calc_method=spec_volume_thickness`,
`walls_consumables_calc_method=section_total_rate`. Ничего не выбирается динамически самим
адаптером — каждый режим фиксирован контрактом (в отличие от foundation_slab, единственной
секции с реальным динамическим выбором).

**`flat_roof_enabled`** — системный флаг (`AUTO_CALCULATED`, `required: true`,
`show_to_user: false`, Елена его никогда не видит) без единого места, где он реально
заполняется. Сам контракт прямо говорит, что делать: "true for flat-roof projects where
parapet or vent/chimney cladding rows are relevant" — адаптер выводит его из наличия
реальных (не null/не 0) значений в `parapet_masonry_volume_m3` /
`parapet_gas_block_d500_250_spec_volume_m3` / `vent_chimney_gas_block_spec_volume_m3` (эти
поля в принципе получают PDF-данные только на проектах с плоской кровлей).

**Два мёртвых, уже самоописанных пробела контракта** (правка не нужна — сами
`notes:` полей это подтверждают): `floor_1/2_lintel_formwork_plywood_qty` и
`floor_1/2_lintel_formwork_timber_volume_m3` имеют реальный `calculator_input_path`, но
указывают на поля датакласса, УДАЛЁННЫЕ из калькулятора 2026-07-25 (материал опалубки
перемычек теперь считается из площади, а не из готового кол-ва/объёма) — сами
`review_parameters`-записи просто не удалили следом (`show_to_user: false` уже стоит,
собственные notes прямо говорят "hidden... pending a separate re-wiring check"). Адаптер их
никогда не читает — передача любого из них вызвала бы `TypeError` при конструировании
датакласса (неожиданный keyword argument).

Арматура (`main_wall_rebar_items`/`lintel_rebar_items`): `floor`/`component` — настоящие
колонки из PDF (в отличие от foundation_slab, где `rod_length_m` был чистым дефолтом).
`component` тем не менее принудительно проставляется адаптером под каждую группу
(`"load_bearing_walls"`/`"lintels"` соответственно), так как это структурная константа
внутри каждой группы и `validate_spec_rebar_item()` жёстко падает при любом расхождении —
та же защитная логика, что и у floor_slab_1's forced component/floor, только на уровне
группы, а не всей секции. `floor` оставлен как есть из экстракции (реально варьируется:
1 или 2 этаж).

**Проверено end-to-end**: собран тестовый workbook (`floors_count=2` — включает floor_2 ветку;
и U-block, и монолитные перемычки на 1 этаже одновременно; парапет + обкладка вентканалов —
включает `flat_roof_enabled=True`; 4 позиции арматуры по 2 группам с намеренно НЕВЕРНЫМ
`component` в исходных данных — проверить принудительную коррекцию). Сверено с независимо
построенным вручную референсом (полностью с нуля, не переиспользование вывода адаптера) —
**0 расхождений** по всем 40 строкам сметы и `internal_totals`, единственные два отличия в
диффе — пустое поле `project_name` (не настраивала заголовок тестового workbook) и одно
забытое мной поле в референсе (`floor_2_concrete_delivery_trips`), которое не повлияло ни на
одну строку сметы в этом сценарии (нужно только когда есть U-block перемычки на 2 этаже,
которых в тесте не было).

**Этап 2 полностью завершён** — все 8 разделов имеют рабочий, проверенный `build_input.py`:
`waterproofing`, `earthworks`, `schiedel_vent_channels`, `foundation_slab`, `floor_slab_2`,
`floor_slab_1`, `flat_roof`, `load_bearing_walls_lintels`.

#### `flat_roof` (2026-08-05) — седьмой адаптер

Plain-dict вход, без вложенности (в отличие от floor_slab_1 — здесь абсолютно все поля
верхнего уровня). Фиксированные production calc_method:
`roof_geometry_calc_method=roof_zones`, `roof_consumables_calc_method=section_total_rate`,
`roof_logistics_and_supply_calc_method=section_total_rate`,
`technical_supervision_calc_method=section_work_rate`,
`procurement_storage_calc_method=section_material_rate`. Ничего не выбирается динамически.

**Два реальных пробела, оба найдены только при реальном прогоне калькулятора:**

1. Тот же класс бага, что и `slab_control_geometry_area_m2` у floor_slab_1, но сразу на 7
   полях: `roof_area_level_1/2_m2`, `project_spec_roof_area_m2`,
   `parapet_length_level_1/2_m`, `vent_wall_abutment_level_1/2_m` — контракт помечает их
   `required: false` (только фолбэк для старого режима `detailed_project_geometry`, "оставьте
   пустым при использовании roof_zones"), но код построения результата калькулятора читает
   все 7 безусловно для чисто диагностического блока `calculation_blocks.geometry` (не влияют
   на деньги — проверила каждое использование). По явному решению пользователя адаптер
   подставляет 0 для всех семи, когда их нет в проверенных данных.
2. **Настоящий баг `core/`, не специфичный для адаптера**: `template_price_keys()` ловил ЛЮБОЙ
   `"<"` в `registry_code` как признак шаблонной построчной цены (механизм арматуры). Но
   `slope_plate_unit_price_per_m3`'s `registry_code` — `"roof_eps_slope_<type>_m3"` — это не
   настоящий шаблон (на листе 02 всегда ровно одна строка, `<type>` — просто
   документационный плейсхолдер), а калькулятор читает 4 ОТДЕЛЬНЫХ поля верхнего уровня
   (`slope_plate_a/b/j/k_unit_price_per_m3`), собранных через f-string с одним и тем же
   значением (контракт это явно подтверждает: "all 4 are the same real product/price in every
   production test case"). Ложное срабатывание превращало `resolved_prices["slope_plate_..."]`
   в словарь `{registry_code: price}` вместо числа И (хуже) тихо пропускало проверку
   "обязательная цена не заполнена" для этого ключа, так как шаблонные ключи намеренно
   освобождены от этой проверки. Проверила все `section_contract.yaml` в пайплайне — это
   единственный ложный случай, всё остальное с `<...>` — настоящий арматурный
   `<class>`/`<diameter>` паттерн. Исправлено в `core/workbook_reader.py`: детекция теперь
   требует ОБА плейсхолдера `<class>` И `<diameter>` одновременно, а не голый `<`.
   Перепроверила: детекция корректна на всех 5 секций с рабочими адаптерами (4 находят
   `rebar_unit_price_by_item`, flat_roof теперь не находит ничего лишнего). Адаптер
   дублирует одну разрешённую цену `slope_plate_unit_price_per_m3` в 4 поля
   `slope_plate_{a,b,j,k}_unit_price_per_m3`.

Отдельно (без правки — уже решено ранее по памяти `roof_membrane_vgr_vrp_open_question`):
`pvc_membrane_vgr_*` поля (V-GR мембрана для эксплуатируемых зон) намеренно не подаются
адаптером — калькулятор трогает их только когда у зоны `operability: exploitable`, а
неэксплуатируемая-по-умолчанию логика уже подтверждена корректной и не критичной на
практике. Реальный проект с эксплуатируемой зоной потребует добавить эти 3 поля отдельно.

**Проверено end-to-end**: собран тестовый workbook (2 зоны кровли, все 9 обязательных
скаляров, все фолбэк-поля намеренно пустые — проверить подстановку 0, `roof_crane_lifting_
shifts`/`roof_waste_removal_trucks` на листе 01-1, все 26 цен на листе 02 кроме 2
необязательных legacy-полей). Сверено с независимо построенным вручную референсом — **0
расхождений** по всем строкам сметы, `totals` и всем 3 warnings.

**Далее**: `load_bearing_walls_lintels` (самый сложный, 9 `*_calc_method` режимов) — последний
раздел Этапа 2.

#### `floor_slab_1` (2026-08-05) — шестой адаптер, первый с namespaced-входом

Единственный калькулятор в этом пайплайне, чей вход разбит на под-словари: `geometry.*`,
`insulation.*`, `rates.*`, `overheads.*`, `manual_lines.*`, плюс `case_meta` (просто
эхо-проброс, калькулятор его не читает) и несколько по-настоящему плоских полей
(`main_formwork_area_m2`, `edge_formwork_area_m2`, `beams_*`, `slab_zones`, `rebar_items`,
`beams.items`, `formwork_areas_calc_method`, `rebar_calc_method`). Контракт сам уже кодирует
это через `calculator_input_path` с точками — адаптер читает эти пути ОБЩИМ механизмом
(`_set_nested()`), а не хардкодит для каждого из ~35 полей, в каком под-словаре оно лежит —
это единственный по-настоящему новый архитектурный приём этого адаптера, дальше он же
пригодится для более простой раскладки любых будущих секций.

Фиксированные production calc_method (всё `allow_override_later: false`):
`formwork_areas_calc_method=spec_formwork_areas`, `rebar_calc_method=spec_length_items`,
`insulation.insulation_calc_method=spec_work_quantities`,
`rates.formwork_rate_calc_method=direct_section_rate`,
`rates.formwork_delivery_calc_method=area_threshold`,
`rates.metal_delivery_calc_method=section_output_only`. Ничего не выбирается динамически.

**Два реальных пробела контракта, оба обнаружены только при попытке реально прогнать
калькулятор (не при чтении контракта), оба — с явной авторизацией пользователя:**

1. Контракт вообще не объявлял `rebar_waste_coeff` (в отличие от foundation_slab/floor_slab_2,
   у которых этот дефолт есть), а `calculate_rebar_item()` безусловно читает
   `item["waste_coeff"]` без fallback — гарантированный `KeyError` на любом реальном прогоне.
   Пользователь подтвердил природу поля (обычный коэффициент запаса материала, как
   `concrete_waste_coeff`/`eps_waste_coeff`, только для арматуры) и авторизовал добавление
   `rebar_waste_coeff=1.05` в `defaults:` (тот же путь `rebar_items[*].waste_coeff`, что и
   `rod_length_m` у foundation_slab — построчное значение, инжектится адаптером в каждую
   строку арматуры).
2. `calculate_rebar_item()` в режиме `spec_length_items` также безусловно требует
   `item["component"] == "floor_slab_1"` и `int(item["floor"]) == 1` — структурные константы
   этого раздела (не PDF-данные, всегда одинаковые для любой строки), но нигде не
   гарантированные извлечением. Вместо того чтобы доверять экстракции эти два
   валидационных поля, адаптер принудительно проставляет их в каждую строку арматуры,
   переопределяя то, что там было (тот же принцип, что и у `rod_length_m`-инъекции в
   foundation_slab).
3. `geometry.slab_control_geometry_area_m2` — требуется калькулятором безусловно
   (`geometry_in["slab_control_geometry_area_m2"]`, без `.get()`), но нигде не объявлено в
   контракте вообще. Проверила все места использования в калькуляторе — чисто
   диагностическое поле (эхо в `calculation_blocks.geometry`/`control_metrics`, ни разу не
   участвует в деньгах). Отдельного PDF-сигнала для этого контрольного числа нет, поэтому по
   явному решению пользователя адаптер просто зеркалит `main_formwork_area_m2` — то же самое
   производственное значение опалубки, используемое как собственный контроль.

**Проверено end-to-end**: собран тестовый workbook (2 позиции балок — одна с width_m и
вычисляемыми объёмом/опалубкой, другая с готовыми `concrete_volume_m3`/`formwork_area_m2` без
`width_m`; 3 позиции арматуры по 2 классам/диаметрам БЕЗ `component`/`floor` — специально,
проверить принудительную инъекцию; override balок по утеплению
(`beams_eps_work_length_m`/`beams_eps_material_area_m2`) и по нижней опалубке
(`beams_bottom_formwork_area_m2`); `formwork_rebar_crane_shifts`/`concrete_pump_shifts` на
листе 01-1; развёрнутые арматурные цены на листе 02). Сверено с независимо построенным вручную
референсом (не переиспользование старого фикстура калькулятора — там были другие
calc_method — и не повторный прогон вывода самого адаптера) — **0 расхождений** по всем
строкам сметы и `totals`, включая полное совпадение всех 3 контрольных warnings.

**Далее**: `flat_roof` → `load_bearing_walls_lintels` (самый сложный).

#### `floor_slab_2` (2026-08-05) — пятый адаптер

Plain-dict вход (без dataclass, как schiedel), второй пользователь шаблонного механизма
арматурных цен из `core/` (первый — foundation_slab). Ничего в этом разделе не выбирается
динамически — контракт вообще не декларирует альтернативные `*_calc_method` (legacy_dimensions,
edge_and_beam_formwork_area_combined_m2, legacy_weight_kg) как review_parameters, поэтому
адаптер всегда идёт по единственному production-пути: `formwork_area_calc_method=
spec_formwork_area`, `formwork_delivery_calc_method=area_threshold`,
`rebar_calc_method=spec_length_items`.

Два момента, специфичных именно для этого раздела:

1. `beam_items` маппится в `beams: {"items": [...]}`, а не в плоский ключ `beam_items` —
   `calculator_input_path` в контракте буквально `"beams.items"`, легко упустить по аналогии
   с остальными repeated_rows группами этого пайплайна, у которых путь всегда 1:1 с именем
   ключа.
2. `formwork_rental_supplier_quote_total` — реальный частный случай: помечено
   `AUTO_CALCULATED`, но нигде в кодовой базе фактически не заполняется (`show_to_user: false`,
   `allow_manual_override: false` — Елена его никогда не видит), при этом калькулятор требует
   его безусловно. Сам контракт прямо разрешает адаптеру синтезировать значение
   (`main_formwork_area_m2 * formwork_rental_used_rate_per_m2`), так как оно нужно только для
   internal-сравнения (`raw_supplier_rate`), не влияет ни на одну строку сметы. Сделано именно
   так — ratio получается ровно 1.0, то есть «аномалий нет».

`rod_length_m` в отличие от foundation_slab здесь — настоящая колонка спецификации (часть
`columns` группы `floor_slab_2_rebar_items`), не построчный дефолт: адаптер её не трогает,
передаёт как есть из строки; инжектится только `unit_price_per_m` (через шаблонный механизм
`core/`), `code` намеренно не выставляется — калькулятор сам выводит его из
`steel_class`+`diameter_mm`, как и предписывает заметка в контракте.

**Проверено end-to-end** на тестовом workbook (2 позиции балок с разным набором override —
одна с готовыми `concrete_volume_m3`/`formwork_area_m2` и `width_m`, другая без `width_m`;
3 позиции арматуры по 2 классам/диаметрам без `unit_price_per_m` — проверить инжекцию цены;
`crane_shifts`/`concrete_pump_shifts` на листе 01-1; развёрнутые арматурные цены на листе 02).
Сверено с независимо построенным вручную (не через `build_input.py`) референсом — **0
расхождений** по всем строкам сметы и `totals`.

Побочная находка при сборке тестового workbook (не баг продакшн-кода — только моего
тест-скрипта, production-скрипты этого пайплайна `insert_rows()` вообще не используют,
проверено): `openpyxl`'s `insert_rows()` сдвигает содержимое ячеек, но НЕ XML-декларацию
смёрженного диапазона. Если вставлять строки перед смёрженной строкой-заголовком группы, при
следующей загрузке файла Excel/openpyxl повторно применяет старую (несдвинутую) merge-область
к новому месту — молча стирая данные, которые там оказались. Обходится так: сначала
`unmerge_cells()` на старом диапазоне, потом `insert_rows()`, потом `merge_cells()` на новой
позиции — именно в этом порядке, в одной сессии до сохранения (порядок unmerge-после-insert
даёт `KeyError` из-за внутренней рассинхронизации openpyxl).

**Далее**: `floor_slab_1` → `flat_roof` → `load_bearing_walls_lintels` (самый сложный).

Для каждого раздела: написать `sections/<code>/build_input.py`, прогнать получившийся
вход через `calculate_<section>()`, сверить с `cases/*/expected.json` того же раздела.
Если совпадает — маппер верный.

#### `foundation_slab` (2026-08-05) — четвёртый адаптер, самый involved на сегодня

Первая секция с (а) динамически выбираемым режимом (`thermal_insert_mode` — "items"
если есть `thermal_insert_items` на листе 01, иначе фиксированный дефолт контракта
"standard_50_100" — единственный `*_calc_method` во всём пайплайне, который не
фиксирован жёстко) и (б) построчным ценообразованием арматуры через новый
"шаблонный" механизм `core/` (см. `core/workbook_reader.py`'s `template_price_keys()`/
`read_prices()`, `core/price_resolver.py`'s `resolve_prices()` — добавлено специально
под этот адаптер, пригодится ещё 3 будущим арматурным разделам: floor_slab_1,
floor_slab_2, load_bearing_walls_lintels).

**Три реальных бага найдены и исправлены при сборке (не гипотетические — все три
проявились бы на любом реальном проекте, не только на тестовом):**

1. Дженерик-цикл "остальное берём из `defaults` по имени поля" (тот же паттерн, что и
   в earthworks/schiedel) слепо копировал ВСЕ ключи `defaults:` как плоские поля
   верхнего уровня — включая `rod_length_m`, у которого `calculator_input_path:
   "rebar_items[*].rod_length_m"` (это дефолт хлыста, 11.7м, "каталожное значение, если
   строка не переопределяет") — по-настоящему построчное поле, а не поле
   `FoundationSlabInput`. Причём `rod_length_m` даже не входит в `columns` группы
   `foundation_rebar_items` — PDF-спецификация его никогда не даёт. Исправлено: цикл
   дефолтов теперь пропускает любой дефолт с `[` в `calculator_input_path` (не только
   `rod_length_m` — на будущее, если появится ещё один построчный дефолт); значение
   инжектится в каждую строку арматуры рядом с `unit_price_per_m`, с `item.setdefault()`
   (строка может переопределить).
2. `build_input.py` вообще не читал `supplier_inputs:` контракта (6 полей:
   `rebar_crane_shifts`, `rebar_metal_delivery_trucks`, `box_total_metal_weight_kg`,
   `concrete_pump_shifts`, `logistics_and_supply_amount`,
   `consumables_tool_amortization_amount`) — калькулятор требует их все (нет дефолта в
   dataclass ни у одного). Исправлено: явный цикл по `all_supplier_inputs(contract)`,
   читает из `scalars` (уже мержит лист 01 и 01-1 благодаря сентябрьскому — точнее
   августовскому — фиксу из schiedel-адаптера), `required: false` поля (два legacy
   fixed-amount поля) по умолчанию 0, если не заполнены.
3. (Не баг кода, ловушка тестирования.) Референс для сверки изначально строился на
   основе существующего калькуляторского тест-кейса
   (`test_foundation_slab_rebar_spec_length`), у которого 4 поля устарели относительно
   текущего контракта: `concrete_waste_coeff` (1.05 вместо текущих 1.02),
   `concrete_mixer_volume_m3` (9 вместо 7), `thermal_insert_50/100_pack_multiple_qty`
   (0.2776 вместо текущего `null` — ещё не заполненный каталожный дефолт),
   `logistics_and_supply_calc_method`/`consumables_tool_amortization_calc_method`
   (`legacy_fixed_amount` вместо текущего `section_total_rate`). После подмены этих 4
   групп полей на актуальные значения контракта — **0 расхождений** по всем 30 строкам
   сметы, `calculation_blocks`, `internal_totals`, warnings.

**Проверено end-to-end**: собран тестовый workbook (только `foundation_slab`),
заполнены 4 обязательных скаляра, 4 строки `foundation_rebar_items` (A500⌀16/12/10,
A240⌀6, БЕЗ `unit_price_per_m` — специально, проверить инжекцию цены), 2 supplier-поля
на листе 01-1, 8 обычных цен + 4 развёрнутых арматурных цены на листе 02 (проверена
корректность `insert_rows()` — сдвиг ранее заполненных строк тоже корректен). Прогнано
через `core.job_runner.run_section()`, сверено с независимо посчитанным референсом
(прямой вызов `calculate_foundation_slab()`) — 0 расхождений.

**Далее**: `floor_slab_2` → `floor_slab_1` → `flat_roof` →
`load_bearing_walls_lintels`.

**`earthworks` ЗАКРЫТ 2026-08-05.** Заметно сложнее waterproofing: 4 независимых
`*_calc_method` (все — фиксированные production-режимы из `defaults:`, не решаются
адаптером динамически: `excavator_shifts_calc_method=standard_volume_productivity`,
`manual_excavation_calc_method=standard_routes`,
`communications_length_calc_method=legacy_direct_length`,
`consumables_calc_method=section_total_rate`) и 2 реальные production repeated_rows
группы (`pit_items`, `sand_items` — построчно с листа 01; `trench_routes` и
`communications_pipe_items` НЕ читаются адаптером вообще, `production_input: false`
у первой и намеренно проигнорирована у второй согласно собственной заметке контракта
"Do not switch to pipe_items" — калькулятор в production-режиме читает уже
просуммированный scalar `trench_volume_m3`/`communications_length_m`, не построчные
данные напрямую).

Прогнано на двух сценариях через `core.job_runner.run_section()` целиком (не вручную
по кусочкам) — 0 расхождений оба раза:
1. `test_pit_items_sand_items_depth_reference` — сложный путь, с `pit_items`/
   `sand_items` (2+2 строки) и `trench_volume_m3` как заранее просуммированным
   scalar'ом (60,1 = сумма 4 маршрутов `trench_routes` того же кейса — именно так,
   как это уже делает слой построения review-таблицы, адаптер не пересчитывает сумму
   сам).
2. `test_excavator_shifts_standard` — простой путь, чистые scalar'ы, без построчных
   групп; кейс в оригинале использует `manual_excavation_calc_method:
   legacy_manual_override`, адаптер всё равно принудительно поставил
   `standard_routes` — с `trench_volume_m3=0` оба режима дают одинаковый (нулевой)
   результат, расхождений нет, но это узкое место стоит помнить при выборе
   следующих тестовых кейсов для других разделов.

Найден и ИСПРАВЛЕН (2026-08-05, с явного разрешения) реальный изъян в
`earthworks_calculator.py`: `validate()` требовал `pit_excavation_depth_m` не-`None`
всегда, когда `excavator_shifts_calc_method == "standard_volume_productivity"` — даже
если `pit_items` уже даёт объём напрямую и глубина физически не нужна для расчёта
(см. `calculate_excavator_shifts_context()`, ветка `if pit_items:` не трогает depth
вообще; глубина используется только (а) как fallback-формула площадь×глубина, когда
`pit_items` пуст, и (б) как справочное эхо в выводе `volumes.pit_excavation_depth_m`
независимо от того, каким путём считался объём). Реальный проект с `pit_items`, но
без отдельно данной глубины котлована, падал на этой проверке, хотя формуле глубина
не нужна.

Правка: `validate()` теперь требует `pit_excavation_depth_m` только когда
`self.pit_items` пуст — ровно тогда, когда она реально нужна формуле. Справочное эхо
в выводе не тронуто: при наличии глубины она по-прежнему попадает в результат, при
отсутствии — просто `null` вместо падения. Проверено: все 9 регресс-кейсов
`earthworks_calculator` по-прежнему проходят (`run_all_cases.py`, 0 изменений в
поведении), плюс отдельно проверен ранее падавший сценарий (`pit_items` есть, глубина
`None`) — теперь считает `machine_excavation_volume_m3 = 212.5` без ошибки, вместо
`ValueError`.

**`schiedel_vent_channels` ЗАКРЫТ 2026-08-05.** Плоский `dict`-вход (не typed dataclass,
без `from_dict()` — калькулятор принимает `dict[str, Any]` напрямую). Нашлись и были
исправлены (с явного разрешения) три реальных пробела по пути:

1. **`price_keys` был неполным**: контракт объявлял цены только для 2x/3x
   вентканалов, хотя калькулятор поддерживает 1x/2x/3x/4x/cvent + D400/D500
   газоблок кладки шахты. Реальные проекты уже используют «недостающие» типы:
   ТРЦ — 1x, АРК — 4x, отдельный тест — D400. Добавлены 5 недостающих
   `price_keys` (1x/4x обязательные — реально используются; cvent/D400/D500
   опциональные — редкие/условные).
2. **`schiedel_masonry_gas_block_items[]` не была объявлена в `review_parameters`
   вообще** — калькулятор её уже читал, память утверждала «SHIPPED», но по факту
   на листе 01 для неё не было ни одной строки, то есть Елена физически не могла
   её увидеть или поправить. Добавлена по образцу уже готовой
   `schiedel_channel_items`.
3. **Найден и исправлен системный баг в `core/workbook_reader.py`** (не
   специфичный для этого раздела — касается всех 8): обязательное поле
   `schiedel_delivery_trips` (`source_class: MANUAL_REVIEW`) физически лежит на
   листе **01-1** («Ручные строки, справочник» — другая структура колонок), а
   `read_scalar_parameters()` читал только лист 01. Это те же самые 12 полей
   логистики (краны/бетононасос/вывоз мусора), которые пользователь просила
   свести списком раньше в этой же сессии — без этой правки НИ ОДИН будущий
   адаптер не смог бы их прочитать. Добавлена `read_manual_values()`, читает
   лист 01-1 (приоритет: «Исправить для этого проекта» > «Типовое значение
   (справочник)»), результат сливается в тот же словарь, что и
   `read_scalar_parameters()`, — все уже написанные `build_input.py`
   (waterproofing, earthworks) продолжают работать без изменений.

Прогнано целиком через `core.job_runner.run_section()` на реальных числах ТРЦ
(`test_schiedel_vent_channels_trc`: кладка 9,8 мп, 21×1x + 15×2x каналов, 1
доставка) — 0 расхождений с `expected.json` (все 9 строк сметы + totals).
Отдельно перепроверены waterproofing и earthworks на регресс после правки
`core/` — 0 расхождений у обоих, правка чисто additive.

## Проверка на каждом шаге

- `contract_loader.py` — сверить на всех 8 контрактах, что required поля читаются без
  ошибок. Сделано 2026-07-13, 0 ошибок.
- `workbook_reader.py` — прогнать на реально сгенерированном
  `experiments/full_estimate_review_pipeline/output/step_12_all_sections_review_template.xlsx`
  с вручную вписанными тестовыми значениями на листах 01/02 (лист 03 не читается,
  проверять на нём нечего). Сделано 2026-07-13 на waterproofing (скаляры + цены) и
  floor_slab_1 (production repeated_rows блоки, включая override) — все случаи верны.
- Каждый `sections/<code>/build_input.py` — сравнение с уже существующими и проходящими
  `cases/*/expected.json` соответствующего калькулятора — это конечный критерий
  правильности.
