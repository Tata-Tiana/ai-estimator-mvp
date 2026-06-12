# USV Project Rehearsal

Отдельный эксперимент для проверки нового проекта ЮСВ после изменений проектировщика.

Это не финальная смета и не изменение калькуляторов. Эксперимент проверяет, насколько новые PDF закрывают production-параметры, которые нужны калькуляторам после разбора с Еленой.

## Что проверяем

- какие `AUTO_PROJECT` параметры реально появились в новых PDF;
- каких параметров не хватает;
- какие значения найдены с низкой уверенностью или конфликтом;
- какие данные остаются `SUPPLIER_INPUT`;
- можно ли после review собрать draft параметров для будущих `input.json`.

## Входные PDF

Исходные PDF копируются в:

```text
experiments/usv_project_rehearsal/data/input_pdfs/
```

Текущие имена:

```text
usv_2026_kr1.pdf
usv_2026_kr2.pdf
```

## Источник требований

Требования берутся из обновленного review-pack:

```text
output/elena_parameter_review_pack_updated.xlsx
```

Используется лист:

```text
К_обсуждению_с_Еленой
```

Production-relevant статусы:

- `AUTO_PROJECT`;
- `SUPPLIER_INPUT`;
- `MANUAL_REQUIRED`;
- `OPTIONAL_CONTROL`.

Не попадают в обязательные требования:

- `AUTO_CALCULATED`;
- `DEFAULT_VALUE`;
- `MATERIAL_CATALOG`;
- `PRICE_DATABASE`;
- `DEPRECATED / LEGACY_ONLY`;
- `DEPRECATED / OPTIONAL_OVERRIDE`.

## Как запустить

```bash
../.venv/bin/python3 experiments/usv_project_rehearsal/run_rehearsal.py
```

## Что создается

```text
data/raw_extraction/pages_text.json
data/raw_extraction/tables.json
data/extracted_candidates.json
data/mapped_parameters.json
data/review_pack.xlsx
data/final_project_parameters_draft.json
data/coverage_report.md
```

## Как читать review_pack.xlsx

Главный лист:

```text
01_Проверка_Елены
```

Он содержит только production-relevant строки:

- найденные `AUTO_PROJECT`;
- `missing`;
- `low_confidence`;
- `conflict`;
- `SUPPLIER_INPUT`;
- `MANUAL_REQUIRED`;
- видимые `OPTIONAL_CONTROL`.

Елена/команда заполняет:

- `elena_status`;
- `elena_value`, если значение нужно исправить;
- `elena_comment`.

`final_value` использует `elena_value`, если оно заполнено, иначе `value_from_pdf`.

## Почему это не финальный расчет

Этот эксперимент не создает финальные `input.json` для калькуляторов. Сначала нужно пройти review-pack, подтвердить low-confidence значения, закрыть missing и получить supplier input для кровельных раскладок.

После проверки `review_pack.xlsx` следующий этап:

```text
review_pack.xlsx -> final_project_parameters -> calculator input.json
```

## Ограничения

- PDF parser здесь эвристический, а не production OCR/semantic parser.
- Таблицы чертежей могут извлекаться шумно.
- Контрольные значения из задания добавлены как curated candidates с привязкой к PDF/page/context.
- Значения с неясной единицей измерения не скрываются: они идут как `low_confidence`.
