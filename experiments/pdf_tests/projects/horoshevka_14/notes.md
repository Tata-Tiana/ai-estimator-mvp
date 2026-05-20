# Хорошевка 14

Экспериментальный проект для PDF-парсинга.

Дом состоит из двух PDF-файлов, как принято у проектировщиков:

- `kr1_below_floor.pdf` — КР1, ниже пола: фундамент, котлован, коммуникации, плита, сваи.
- `kr2_above_floor.pdf` — КР2, выше пола: стены, перегородки, перекрытие/покрытие, кровля, вентканалы, навес.

## Структура

```text
projects/horoshevka_14/
├── input/
│   ├── kr1_below_floor.pdf
│   └── kr2_above_floor.pdf
├── output/
│   ├── kr1_below_floor/
│   │   ├── full_text.txt
│   │   ├── pages_text.json
│   │   ├── blocks.json
│   │   ├── tables.json
│   │   ├── tables.xlsx
│   │   └── summary.json
│   └── kr2_above_floor/
│       └── ...
└── notes.md
```

## Источник текущей миграции

Старые входные PDF:

- `data/input/pdf/f_44269e741d40fbd8.pdf` -> `input/kr1_below_floor.pdf`
- `data/input/pdf/f_26869e741d485093.pdf` -> `input/kr2_above_floor.pdf`

Старые результаты парсинга:

- `data/output/pdf_experiments/f_44269e741d40fbd8_2026-04-29_2020/` -> `output/kr1_below_floor/`
- `data/output/pdf_experiments/f_26869e741d485093_2026-04-29_2019/` -> `output/kr2_above_floor/`

## Связанный AI-анализ

AI-карточка этого же дома лежит здесь:

```text
experiments/ai_tests/projects/horoshevka_14/
```
