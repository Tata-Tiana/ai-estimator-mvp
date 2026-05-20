# Отчёт по калькулятору гидроизоляции фундаментной плиты

Дата: 2026-05-15

## Кратко

В проекте `ai-estimator-mvp` сделан отдельный экспериментальный калькулятор блока "Гидроизоляция фундаментной плиты".

Калькулятор считает только серую внутреннюю себестоимость: материалы, работы и итог блока. Клиентская часть сметы, рентабельность, НР/СП/ТН и коммерческие коэффициенты не считаются.

Расчёт сделан отдельно от калькуляторов земляных работ и фундаментной плиты. Существующие калькуляторы не изменялись.

## Где находится

```text
experiments/waterproofing_calculator/
├── README.md
├── waterproofing_calculator.py
├── run_waterproofing_calc.py
├── cases/
│   └── test_waterproofing_foundation_slab/
│       ├── input.json
│       ├── expected.json
│       └── notes.md
└── output/
    └── test_waterproofing_foundation_slab/
        ├── waterproofing_result.json
        └── waterproofing_result.md
```

## Что считает калькулятор

Калькулятор считает 8 строк серой внутренней сметы:

1. Гидроизоляция фундаментной плиты битумной мастикой в 2 слоя.
2. Праймер битумный AquaMast, 18 л.
3. Мастика гидроизоляционная битумная для фундаментов AquaMast, 18 кг.
4. Утепление стен плиты ЭППС 100 мм.
5. Пеноплэкс ГЕО 100 мм.
6. Клей-пена для ЭППС.
7. Логистика и снабжение.
8. Расходные материалы, амортизация инструмента.

## Основные формулы

### Площадь гидроизоляции

Площадь считается по бортам плиты:

```text
waterproofing_area_m2 = slab_formwork_perimeter_m * slab_edge_height_m
```

В текущем кейсе:

```text
81 * 0.3 = 24.3 м2
```

### Работа по гидроизоляции

```text
24.3 * 350 = 8 505
```

### Праймер

```text
primer_required_liters = 24.3 * 0.3 = 7.29 л
primer_units = ceil(7.29 / 18) = 1 шт
```

Стоимость:

```text
1 * 2 770 = 2 770
```

### Мастика

```text
mastic_required_kg = 24.3 * 1 * 2 = 48.6 кг
mastic_units = ceil(48.6 / 18) = 3 шт
```

Стоимость:

```text
3 * 2 780 = 8 340
```

### Утепление стен плиты ЭППС 100 мм

Площадь берётся из спецификации:

```text
eps100_wall_insulation_area_m2 = 1.75 / 0.1 = 17.5 м2
```

Работа:

```text
17.5 * 500 = 8 750
```

Дополнительно выводится геометрическая проверка:

```text
(81 - 8.2 - 2 - 5.3) * 0.3 = 19.65 м2
```

Но в строку сметы берётся значение `17.5 м2` из спецификации.

### Пеноплэкс ГЕО 100 мм

```text
required_volume = 17.5 * 0.1 * 1.05 = 1.8375 м3
raw_packs = 1.8375 / 0.2776 = 6.6192
packs = 7
order_volume = 7 * 0.2776 = 1.9432 м3
```

Стоимость считается от точного объёма:

```text
1.9432 * 10 000 = 19 432
```

В смете отображается округлённое количество `1.94 м3`.

### Клей-пена

Подтверждённое правило:

```text
1 баллон на 10 м2, округление вверх, минимум 1 баллон
```

В текущем кейсе:

```text
ceil(17.5 / 10) = 2 баллона
2 * 490 = 980
```

### Логистика и расходники

База до логистики и расходников:

```text
8 505 + 2 770 + 8 340 + 8 750 + 19 432 + 980 = 48 777
```

Логистика:

```text
48 777 * 0.02 = 975.54 -> 976
```

Расходные материалы:

```text
48 777 * 0.03 = 1463.31 -> 1 463
```

## Итоги текущего кейса

Кейс:

```text
experiments/waterproofing_calculator/cases/test_waterproofing_foundation_slab/
```

Результат:

```text
waterproofing_base_subtotal = 48 777
internal_materials_total    = 33 961
internal_works_total        = 17 255
internal_section_total      = 51 216
```

## Сверка со сметой

Калькулятор был сверён со скрином раздела "Гидроизоляция, утепление бортов плит".

Проверка показала:

```text
54 ok
0 mismatch
```

Все видимые строки и итоговые суммы совпали:

```text
Материалы: 33 961
Работы:    17 255
Итого:     51 216
```

## Формат результата

После запуска создаются:

```text
experiments/waterproofing_calculator/output/test_waterproofing_foundation_slab/waterproofing_result.json
experiments/waterproofing_calculator/output/test_waterproofing_foundation_slab/waterproofing_result.md
```

В JSON сохраняются:

- входные параметры;
- расчётный блок `waterproofing`;
- строки серой внутренней сметы;
- итоги;
- expected;
- comparison;
- warnings.

## Команды запуска

Запуск расчёта:

```bash
../.venv/bin/python3 experiments/waterproofing_calculator/run_waterproofing_calc.py experiments/waterproofing_calculator/cases/test_waterproofing_foundation_slab
```

Проверка компиляции:

```bash
../.venv/bin/python3 -m py_compile experiments/waterproofing_calculator/waterproofing_calculator.py experiments/waterproofing_calculator/run_waterproofing_calc.py
```

## Текущий статус

Калькулятор гидроизоляции фундаментной плиты работает как отдельный экспериментальный модуль и повторяет проверенный фрагмент серой внутренней сметы без расхождений.

Он готов для добавления следующих кейсов: нужно создать новую папку в `cases/`, положить `input.json`, `expected.json`, `notes.md`, запустить runner и проверить comparison.
