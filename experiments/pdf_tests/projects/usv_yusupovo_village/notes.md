# USV Yusupovo Village PDF Demo

Проектная папка для demo-контура PDF-парсинга проекта `usv_yusupovo_village`.

## Структура

```text
experiments/pdf_tests/projects/usv_yusupovo_village/
├── input/
├── output/
└── notes.md
```

## Как использовать

PDF проекта нужно положить в:

```text
experiments/pdf_tests/projects/usv_yusupovo_village/input/
```

После прогона парсера результаты сохраняются в:

```text
experiments/pdf_tests/projects/usv_yusupovo_village/output/<pdf_part_name>/
```

Ожидаемые артефакты полного прогона:

- `full_text.txt`
- `pages_text.json`
- `blocks.json`
- `tables.json`
- `tables.xlsx`
- `summary.json`

## Статус

Папка подготовлена для demo-контура. Если в `input/` нет PDF, парсер не запускается.
