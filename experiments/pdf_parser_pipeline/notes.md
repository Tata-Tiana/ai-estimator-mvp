# Notes

- `extracted_parameters_for_review.json` — шумный диагностический слой.
- Основной слой для Елены — `reviewed_parameters.xlsx`.
- В `reviewed_parameters.xlsx` должны быть все параметры, нужные калькуляторам.
- Найденные parser/review_card значения подставляются автоматически.
- Ненайденные параметры остаются пустыми и отмечаются `missing` или `manual_required`.
- Нельзя использовать Excel cell references как идентификаторы логики.
- В этой задаче не делаются `input_builder`, `box_calculator`, Excel export, Telegram/n8n.
- Значения без уверенного source_file/source_id/page/source_text не считаются найденными.

