# PDF parser pipeline

Экспериментальный слой MVP поверх существующего PDF parser.

Он строит цепочку:

PDF parser artifacts -> section review cards -> reviewed_parameters.xlsx -> будущий input_builder.

## Чем raw extraction отличается от review cards

`extracted_parameters_for_review.json` остается шумным диагностическим файлом. Он показывает, что parser нашел регулярками, но не является главным источником для расчета.

`review_cards` строятся по схемам разделов и содержат только параметры, которые нужны калькуляторам или важны для контроля.

## Почему Excel строится от schema калькуляторов

Если parser не нашел параметр, этот параметр все равно нужен калькулятору. Поэтому `reviewed_parameters.xlsx` строится от `section_schema.py`, а найденные PDF-значения только подставляются в `extracted_value`.

## Что делает Елена

1. Открывает `reviewed_parameters.xlsx`.
2. Проверяет `extracted_value`.
3. Исправляет значения в `corrected_value`.
4. Заполняет `manual_required` и `missing`.
5. Отвечает на вопросы в `review_questions`.

## Следующий этап

После проверки будет нужен `input_builder`, который соберет `input.json` для калькуляторов из проверенного Excel.

## Запуск

```bash
.venv/bin/python3 experiments/pdf_parser_pipeline/run_pdf_parser_pipeline.py experiments/pdf_parser_pipeline/cases/mvp_usv_demo
```

## Не входит в этот слой

- изменение калькуляторов;
- изменение `expected.json`;
- `box_calculator`;
- Excel-смета;
- Telegram/n8n;
- перенос кода в production app.

