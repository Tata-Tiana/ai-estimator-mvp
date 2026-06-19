# Earthworks Parser Google Stage 1

Изолированная репетиция production-flow для раздела **Земляные работы**:

```text
PDF / parser artifacts
-> разбор проектных параметров
-> read-only snapshot Google price_registry
-> price resolution для earthworks
-> Google/Excel review sheet для Елены
```

## Что уже сделано в этом контуре

- собран изолированный review-flow именно для `earthworks`, без общего `price_provider` на весь MVP;
- реализован clean-run: можно удалить только generated jobs и заново прогнать подготовку;
- `prepare` строит свежий `review_workbook.xlsx` и публикует Google Sheet через OAuth;
- листы `01–04` остаются человекочитаемыми, а `05–06` используются как техническая диагностика;
- лист `05_Кандидаты parser` показывает короткие кандидаты без JSON-простыней;
- лист `06_Сырые данные parser` хранит summary, logical sheets, raw evidence и full JSON отдельно;
- anti-cheat проверяет, что workbook и builder не расходятся по утверждённой структуре.

## Важные правила

- `price_registry` читается только read-only.
- Недостающие цены калькулятора не публикуются обратно в общий прайс.
- Fallback из базового кейса ЮСВ используется только внутри текущей сметы/job и только для цен.
- Объемы/количества нельзя брать из legacy input/result.
- Ручная правка цены в review sheet действует только для текущей сметы.
- Лист `02_Цены себестоимости` показывает реальные price components одним списком, без искусственных строк с нулевой ценой.
- Этот stage1 не пишет ничего обратно в `price_registry` и не служит общим price-provider слоем для всего MVP.

## Структура

- `parser/` - адаптер проектных данных для earthworks.
- `pricing/` - локальный price contract, reader и resolver только для earthworks.
- `google/` - сборка review workbook/Google Sheet.
- `reports/` - отчеты и anti-cheat.
- `data/jobs/<job_id>/` - все outputs конкретного запуска.
- `data/jobs/<job_id>/google/review_workbook.xlsx` - свежий workbook для проверки.
- `data/jobs/<job_id>/google/google_sheet_metadata.json` - метаданные опубликованной таблицы.
- `data/jobs/<job_id>/reports/` - stage1 summary, parser report, anti-cheat.

Такая структура потом переносится в Telegram-бот: бот создает job, кладет PDF и запускает эти же шаги.

## Что пока не входит в stage1

- Telegram-бот и общий orchestration layer;
- запуск расчёта/сметы после проверки;
- запись найденных цен обратно в общий `price_registry`;
- общий `price_provider` для всех калькуляторов;
- любые изменения `parser core` вне этого review-flow;
- интеграция с другими разделами сметы за пределами `earthworks`.

## Запуск

```bash
cd experiments/earthworks_parser_google_stage1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run_stage1.py prepare --project-name "ЮСВ"
```

Если OAuth-настройки заполнены, будет создан Google Sheet. Если нет, будет создан локальный `review_workbook.xlsx` в папке job.

## Полное обнуление локальных прогонов

Перед повторным тестом можно удалить все созданные jobs:

```bash
python run_stage1.py clean
```

Команда удаляет только:

```text
data/jobs/*
```

И не трогает:

- `data/input_pdfs/`;
- `.env`, `credentials.json`, `token.json`;
- код эксперимента;
- v3 parser outputs;
- общий `price_registry`.

## Текущее состояние workbook

Актуальный workbook stage1 сейчас строится с такими листами:

```text
00_Конструктор сметы
01_Проверка проекта
02_Цены себестоимости
03_Детали объемов
04_Инструкция
05_Кандидаты parser
06_Сырые данные parser
```

Лист `07_Лог parser` не используется.

Удалить один конкретный job:

```bash
python run_stage1.py clean --job-id restore_check
```

## Прайс

Настройки `.env`:

```env
GOOGLE_OAUTH_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json
GOOGLE_DRIVE_FOLDER_ID=
GOOGLE_PRICE_REGISTRY_SPREADSHEET_ID=
GOOGLE_PRICE_REGISTRY_SHEET_NAME=price_registry
```

Секреты не коммитятся.
