# Хорошевка 14

Экспериментальный AI-анализ проектной документации.

Входом для карточки являются результаты PDF-парсинга:

- `experiments/pdf_tests/projects/horoshevka_14/output/kr1_below_floor/full_text.txt`
- `experiments/pdf_tests/projects/horoshevka_14/output/kr2_above_floor/full_text.txt`

## Структура

```text
projects/horoshevka_14/
├── input/
│   └── sources.json
├── output/
│   ├── full_text_combined.txt
│   ├── sources.json
│   ├── project_card_full.json
│   ├── project_card_full.md
│   ├── materials_extracted.xlsx
│   ├── estimate_scope_mapping.xlsx
│   ├── missing_data.txt
│   └── warnings.txt
└── notes.md
```

## Источник текущей миграции

Старый результат AI-карточки:

```text
data/output/ai_project_cards/2026-04-29_2056/
```

Сейчас он скопирован в:

```text
experiments/ai_tests/projects/horoshevka_14/output/
```
