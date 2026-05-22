# Floor Slab 1 Calculator

Экспериментальный детерминированный калькулятор раздела:

```text
Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 1-го этажа на отм. +3.480 (180 мм) с балками
```

Калькулятор считает только серую внутреннюю себестоимость:

- материалы / механизмы;
- работы;
- итог раздела.

AI не используется. Клиентская часть сметы, рентабельность, НР/СП/ТН и коммерческие коэффициенты не считаются.

## Важные правила

- Номера строк Excel не используются как идентификаторы.
- Главный идентификатор строки — `code` + название строки.
- Деньги считаются через `Decimal` и `ROUND_HALF_UP`.
- Закупочные количества округляются через `ceil` там, где это требуется.
- Raw и displayed значения хранятся отдельно, потому что Excel может показывать округлённое количество, но считать сумму от raw.

## Структура

```text
experiments/floor_slab_1_calculator/
├── README.md
├── floor_slab_1_calculator.py
├── run_floor_slab_1_calc.py
├── cases/
│   └── test_floor_slab_1/
│       ├── input.json
│       ├── expected.json
│       └── notes.md
└── output/
    └── test_floor_slab_1/
        ├── floor_slab_1_result.json
        └── floor_slab_1_result.md
```

## Запуск

```bash
../.venv/bin/python3 experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py experiments/floor_slab_1_calculator/cases/test_floor_slab_1
```

## Компиляция

```bash
../.venv/bin/python3 -m py_compile experiments/floor_slab_1_calculator/floor_slab_1_calculator.py experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py
```

## Ожидаемые итоги

```text
internal_materials_total = 1175601
internal_works_total = 611926
internal_section_total = 1787527
```
