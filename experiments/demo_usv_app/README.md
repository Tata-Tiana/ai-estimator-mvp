# USV Browser Demo

Локальная Streamlit-панель для созвона по проекту `ai-estimator-mvp`.

Это demo, не production. Терминал нужен только для запуска Streamlit; клиенту показывается страница в браузере. Telegram-бот и CLI-интерфейс здесь не используются.

## Запуск

Из корня проекта:

```bash
streamlit run experiments/demo_usv_app/app.py
```

Если Streamlit установлен только в проектном venv:

```bash
.venv/bin/streamlit run experiments/demo_usv_app/app.py
```

После запуска открыть:

```text
http://localhost:8501
```

## Что Показывает Demo

- Красивую шапку `Brick House` с адресом объекта ЮСВ.
- Процесс `PDF -> найденные параметры -> расчёт фундаментной плиты -> Excel-смета`.
- Clean-карточку параметров из `foundation_slab_review_card.json`.
- Смету фундаментной плиты в стиле таблицы Елены.
- Белую зону и серую зону.
- Скачивание:
  - `usv_foundation_slab_demo.xlsx`;
  - `usv_foundation_slab_demo_report.md`;
  - `usv_foundation_slab_result.json`.

## Важные Ограничения

- AI не считает смету.
- Расчёт берётся из существующего `foundation_slab_calculator` / готового `foundation_slab_result.json`.
- Клиентская часть не считается.
- Белая зона сейчас является технической копией серой зоны.
- Серая зона содержит реальные значения внутренней себестоимости из Python-калькулятора.
- Коэффициенты клиента, налоги, НР, СП, ТН сверху не применяются.
- Логика не использует ссылки на Excel-ячейки.

## Файлы

```text
experiments/demo_usv_app/
├── app.py
├── excel_export.py
├── report_export.py
├── README.md
└── output/
```

`output/` содержит локально сгенерированные файлы demo и не предназначен для production-хранения.
