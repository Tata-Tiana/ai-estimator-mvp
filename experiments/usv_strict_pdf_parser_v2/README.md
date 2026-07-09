# USV Strict PDF Parser v2

Новый чистый эксперимент для проверки проекта ЮСВ после изменений проектировщика.

Первый эксперимент `experiments/usv_project_rehearsal/` признан неудачным:

- заранее известные значения были смешаны с реальными extracted candidates;
- mapping давал ложные missing и местами ложные found.

Этот эксперимент работает только в strict mode.

## Strict Rules

Production values могут появляться только из:

- текста PDF;
- таблиц PDF;
- строк спецификаций, разобранных из PDF.

Запрещено подставлять числа из старой сметы, прошлых обсуждений или заранее известных контрольных примеров. Если parser не нашел значение, оно остается missing, mapping gap или low confidence. Руками число не подставляется.

Этот эксперимент не запускает калькуляторы и не делает финальную смету. Его задача - честно показать:

- что реально извлечено из PDF;
- что проектировщик действительно внес;
- чего не хватает в проекте;
- что является проблемой parser/mapping;
- что требует проверки Елены или поставщика.

## Run

```bash
.venv/bin/python3 experiments/usv_strict_pdf_parser_v2/run_strict_parser.py
```

## Outputs

```text
data/raw/pages_text.json
data/raw/tables.json
data/raw/table_rows.json
data/extracted/spec_rows.json
data/extracted/candidates.json
data/mapped/mapped_parameters.json
data/mapped/normalized_parameters.json
data/mapped/final_project_parameters_draft.json
data/reports/coverage_report.md
data/reports/parser_quality_report.md
data/reports/integrity_report.md
data/review/review_pack.xlsx
```

## Review Pack

Главный лист:

```text
01_Проверка_Елены
```

На нем нет значений, добавленных из памяти. Каждая найденная строка содержит PDF, страницу, фрагмент и `candidate_id`.

## Next Step

После проверки `review_pack.xlsx` можно решать, что делать дальше:

- дорабатывать parser/mapping;
- просить проектировщика уточнить спецификации;
- получать supplier input;
- собирать будущий `input.json` для калькуляторов.
