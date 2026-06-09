# PDF parser pipeline result

## Что создано
- review cards по разделам
- reviewed_parameters.xlsx

## Обработанные источники
| source_id | source_file | pages | parsed_dir |
|---|---|---:|---|
| kr1_foundation | ЮСВ КР1.pdf | 12 | parsed/kr1_foundation |
| kr2_above_zero | ЮСВ КР2.pdf | 31 | parsed/kr2_above_zero |
| ar_architecture | ЮСВ АР.pdf | 21 | parsed/ar_architecture |

## Разделы
| section_code | section_name | required total | extracted found | manual required | missing | control only | review_card |
|---|---|---:|---:|---:|---:|---:|---|
| earthworks | Земляные работы | 29 | 3 | 7 | 6 | 3 | /Users/tatanamedzidova/Desktop/AI сметчик/ai_estimator_mvp/experiments/pdf_parser_pipeline/cases/mvp_usv_demo/review_cards/earthworks_review_card.json |
| foundation_slab | Фундаментная плита | 96 | 14 | 3 | 34 | 5 | /Users/tatanamedzidova/Desktop/AI сметчик/ai_estimator_mvp/experiments/pdf_parser_pipeline/cases/mvp_usv_demo/review_cards/foundation_slab_review_card.json |
| waterproofing | Гидроизоляция | 24 | 2 | 3 | 7 | 2 | /Users/tatanamedzidova/Desktop/AI сметчик/ai_estimator_mvp/experiments/pdf_parser_pipeline/cases/mvp_usv_demo/review_cards/waterproofing_review_card.json |
| load_bearing_walls_lintels | Несущие стены и перемычки | 140 | 7 | 21 | 68 | 2 | /Users/tatanamedzidova/Desktop/AI сметчик/ai_estimator_mvp/experiments/pdf_parser_pipeline/cases/mvp_usv_demo/review_cards/load_bearing_walls_lintels_review_card.json |
| floor_slab_1 | Плита перекрытия 1-го этажа | 124 | 8 | 15 | 51 | 5 | /Users/tatanamedzidova/Desktop/AI сметчик/ai_estimator_mvp/experiments/pdf_parser_pipeline/cases/mvp_usv_demo/review_cards/floor_slab_1_review_card.json |
| floor_slab_2 | Плита перекрытия 2-го этажа | 67 | 7 | 8 | 21 | 1 | /Users/tatanamedzidova/Desktop/AI сметчик/ai_estimator_mvp/experiments/pdf_parser_pipeline/cases/mvp_usv_demo/review_cards/floor_slab_2_review_card.json |
| flat_roof | Плоская кровля | 78 | 6 | 6 | 27 | 2 | /Users/tatanamedzidova/Desktop/AI сметчик/ai_estimator_mvp/experiments/pdf_parser_pipeline/cases/mvp_usv_demo/review_cards/flat_roof_review_card.json |
| schiedel_vent_channels | Вентиляционные каналы Schiedel | 13 | 4 | 3 | 3 | 2 | /Users/tatanamedzidova/Desktop/AI сметчик/ai_estimator_mvp/experiments/pdf_parser_pipeline/cases/mvp_usv_demo/review_cards/schiedel_vent_channels_review_card.json |

## Что должна сделать Елена
1. Открыть reviewed_parameters.xlsx.
2. Проверить лист parameters.
3. Исправить corrected_value, если extracted_value неверный.
4. Заполнить manual_required/missing.
5. Ответить на вопросы в review_questions.
6. После проверки поставить elena_status: reviewed/corrected/manual/ignored.

## Ограничения
- parser/AI не считают смету;
- расчет выполняют Python-калькуляторы;
- значения без уверенного источника не придумываются;
- часть параметров будет ручной.

## Warnings
- Нет предупреждений.
