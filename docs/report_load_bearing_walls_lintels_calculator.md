# Отчёт по калькулятору несущих стен и перемычек

Дата: 2026-05-18

## Кратко

В проекте `ai-estimator-mvp` сделан отдельный экспериментальный калькулятор раздела:

```text
ВНЕШНИЕ И ВНУТРЕННИЕ НЕСУЩИЕ СТЕНЫ, ПЕРЕМЫЧКИ
```

Калькулятор считает только серую внутреннюю себестоимость: материалы, работы и итог раздела. Клиентская часть сметы, рентабельность, НР/СП/ТН и коммерческие коэффициенты не считаются.

Расчёт сделан отдельным модулем и не затрагивает уже работающие калькуляторы земляных работ, фундаментной плиты и гидроизоляции.

## Где находится

```text
experiments/load_bearing_walls_lintels_calculator/
├── README.md
├── load_bearing_walls_lintels_calculator.py
├── run_load_bearing_walls_lintels_calc.py
├── cases/
│   └── test_load_bearing_walls_lintels/
│       ├── input.json
│       ├── expected.json
│       └── notes.md
└── output/
    └── test_load_bearing_walls_lintels/
        ├── load_bearing_walls_lintels_result.json
        └── load_bearing_walls_lintels_result.md
```

## Что считает калькулятор

Калькулятор считает строки серой внутренней сметы по разделу несущих стен:

- устройство лесов и подмостей;
- пиломатериал для лесов;
- гидроизоляцию под первый ряд блоков;
- кладку внешних и внутренних несущих стен;
- газобетонные блоки D400 400 мм;
- газобетонные блоки D500 250 мм;
- монтажный клей;
- пескобетон для первого ряда;
- резку блока под U-блоки перемычек;
- штробление под армирование;
- арматуру Ø10 для несущих стен;
- доставку и разгрузку блоков;
- перемещение блоков автокраном;
- армирование перемычек;
- бетон и работы по перемычкам;
- парапет;
- кладку второго света / над кухней как case-specific addon;
- обкладку дымохода и вентканалов;
- клей для парапета и верхнего уровня;
- расходные материалы;
- вывоз мусора;
- технический надзор.

## Важное по округлениям

В этом разделе Excel отображает строки округлёнными, но итог раздела считает от raw-значений.

Поэтому калькулятор хранит в каждой строке оба значения:

```text
material_total_raw
material_total
work_total_raw
work_total
line_total_raw
line_total
```

Итоги раздела тоже хранятся в двух вариантах:

```text
internal_materials_total_raw
internal_materials_total
internal_works_total_raw
internal_works_total
internal_section_total_raw
internal_section_total
```

Это нужно, чтобы повторить логику Excel, а не просто сумму видимых округлённых строк.

## Основные формулы

### Подмости и леса

Старый эталонный кейс использует legacy-режим:

```text
scaffolding_setup_quantity = прямое значение из input.json
scaffolding_timber_quantity_m3 = прямое значение из input.json
```

После уточнения Елены добавлен production-режим `floors_based`:

```text
scaffolding_setup_quantity = floors_count * scaffolding_setup_units_per_floor
scaffolding_timber_quantity_m3 = floors_count * scaffolding_timber_m3_per_floor
```

Production defaults:

```text
scaffolding_setup_units_per_floor = 1
scaffolding_timber_m3_per_floor = 1 м3
```

`floors_count` должен приходить из проекта. Прямые поля `scaffolding_setup_quantity` и `scaffolding_timber_quantity_m3` оставлены только для legacy/debug.

### Гидроизоляция под первый ряд

В расчёт входят стены 400 мм и 250 мм. Перегородки 150 мм сюда не включаются.

Старый legacy-режим:

```text
area = sum(lengths_400) * 0.4 + sum(lengths_250) * 0.25
```

В текущем кейсе:

```text
sum(lengths_400) = 77.7
77.7 * 0.4 = 31.08

sum(lengths_250) = 38.04
38.04 * 0.25 = 9.51

area = 40.59 м2
```

После уточнения Елены добавлен production-режим `spec_area`:

```text
cutoff_waterproofing_area_m2 = cutoff_waterproofing_load_bearing_walls_area_m2
```

`cutoff_waterproofing_load_bearing_walls_area_m2` берётся готовой площадью из спецификации и относится только к несущим стенам. Площадь отсечной гидроизоляции под перегородки должна быть отдельным параметром будущего раздела перегородок: `cutoff_waterproofing_partitions_area_m2`.

### Кладка несущих стен

Работа считается по проектному объёму кладки без запаса:

```text
78.95 + 30.4 = 109.35 м3
109.35 * 7000 = 765 450
```

### Газобетонные блоки

Материал считается по схеме:

```text
объём из спецификации * 1.05
-> деление на объём поддона
-> округление вверх до целых поддонов
-> обратно в м3
```

D400 400 мм:

```text
78.95 * 1.05 = 82.8975
82.8975 / 2.15 = 38.557
ceil = 39 поддонов
39 * 2.15 = 83.85 м3
83.85 * 6000 = 503 100
```

D500 250 мм:

```text
30.4 * 1.05 = 31.92
31.92 / 1.8 = 17.7333
ceil = 18 поддонов
18 * 1.8 = 32.4 м3
32.4 * 5500 = 178 200
```

### Клей и пескобетон

Клей для основной кладки:

```text
ceil(109.35 * 1.2 * 1.05) = 138 мешков
138 * 340 = 46 920
```

Пескобетон:

```text
ceil(40.59 * 19 * 2 / 40) = 39 мешков
39 * 375 = 14 625
```

### Перемычки

Старый legacy-режим считает суммарную длину перемычек по списку `length/count`:

```text
23.4 м
```

Резка U-блоков:

```text
23.4 / 0.6 = 39 шт
39 * 400 = 15 600
```

После уточнения Елены добавлен production-режим `spec_total_length`:

```text
lintel_total_length_m = готовая общая длина перемычек в U-блоке из спецификации
u_block_quantity = lintel_total_length_m / gas_block_length_m
```

Единица строки `u_block_lintel_cutting` остаётся `шт`. Резка U-блока не переводится в м.п.

Бетонирование перемычек:

```text
23.4 * 1000 = 23 400
```

Бетон перемычек:

```text
23.4 * 0.125 * 0.125 = 0.365625 м3
0.365625 * 1.05 = 0.38390625 м3
минимальный заказ = 1 м3
1 * 6400 = 6 400
```

Сечение бетонной части U-блока после уточнения Елены является системным default:

```text
lintel_section_width_m = 0.125
lintel_section_height_m = 0.125
```

В production эти параметры не спрашиваются у Елены. Они остаются в settings/defaults и используются в формуле:

```text
lintel_raw_concrete_volume_m3 = lintel_total_length_m * 0.125 * 0.125
```

TODO для следующих этапов:

- убрать `lintel_section_width_m` и `lintel_section_height_m` из `reviewed_parameters.xlsx` как production-поля;
- оставить эти значения только в settings/defaults;
- не показывать эти параметры Елене в review form.

Новый production-стандарт по объёму бетона перемычек:

```text
lintel_concrete_calc_method = spec_volume
lintel_concrete_spec_volume_m3 = готовый проектный объём бетона перемычек из спецификации
```

Для `spec_volume` калькулятор не применяет повторно `concrete_waste_coeff`:

```text
lintel_raw_concrete_volume_m3 = lintel_concrete_spec_volume_m3
lintel_required_concrete_volume_m3 = lintel_concrete_spec_volume_m3
lintel_concrete_order_volume_m3 = max(1, ceil(lintel_required_concrete_volume_m3))
```

Примеры закупочного округления:

| Проектный объём | Заказ |
| ---: | ---: |
| 0.38 м3 | 1 м3 |
| 1.00 м3 | 1 м3 |
| 1.10 м3 | 2 м3 |
| 2.00 м3 | 2 м3 |
| 2.05 м3 | 3 м3 |

Статусы параметров:

| parameter | status | source_of_truth | show_in_review_form |
| --- | --- | --- | --- |
| `lintel_concrete_spec_volume_m3` | AUTO_PROJECT | спецификация проекта / объём бетона перемычек | yes |
| `lintel_concrete_min_order_volume_m3` | DEFAULT_VALUE = 1 | закупочное правило | no |

TODO:

- обновить `section_schema.py`;
- добавить `lintel_concrete_spec_volume_m3` в `reviewed_parameters.xlsx`;
- убрать `lintel_concrete_min_order_volume_m3` из формы Елены как production-поле;
- научить parser брать объём бетона перемычек из спецификации.

### Арматура

Арматура считается детерминированно:

```text
масса или базовая длина
-> запас 5%
-> целые прутки
-> закупочная длина
-> стоимость
```

Для основной кладки Ø10:

```text
base_length = 1070 мп
raw_rods = 1070 * 1.05 / 11.7 = 96.0256
ceil = 97 прутков
order_length = 97 * 11.7 = 1134.9 мп
1134.9 * 32.72 = 37 133.928 -> 37 134
```

Для перемычек:

```text
Ø12: 128.7 мп -> 5 829
Ø6: 102 мп -> 1 359
```

После уточнения Елены добавлен production-режим `spec_length_items`.

Арматура несущих стен и перемычек в production должна приходить из спецификации в м.п.:

```text
spec_length_m
length_with_waste_m = spec_length_m * rebar_waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
delivery_weight_kg = order_length_m * kg_per_meter
```

Строки арматуры разделяются по этажам и конструкциям, например:

```text
load_bearing_walls_floor_1_rebar_a500_d10
lintels_floor_1_rebar_a500_d12
lintels_floor_1_rebar_a240_d6
```

Арматура перегородок не включается в этот калькулятор.

### Доставка и краны

Доставка блоков считается от закупочных объёмов после округления до поддонов:

```text
83.85 + 32.40 + 15.05 + 23.65 + 3.60 = 158.55 м3
158.55 / 32 = 4.9547
ceil = 5 машин
5 * 28 000 = 140 000
```

Разгрузка манипулятором:

```text
5 * 15 000 = 75 000
```

Перемещение блоков автокраном:

```text
2 смены * 30 000 = 60 000
```

### Парапет и второй свет

Парапет считается как постоянный блок.

Кладка над кухней / второй свет помечена как `case_specific`, потому что это особенность текущего проекта, а не универсальное правило для всех домов.

В текущем кейсе:

```text
second_light_volume = 13.5 м3
parapet_volume = 22.74 м3
total = 36.24 м3
36.24 * 7000 = 253 680
```

Материал D400 для парапета и второго света считается объединённо:

```text
36.24 * 1.05 = 38.052
38.052 / 2.15 = 17.6986
ceil = 18 поддонов
18 * 2.15 = 38.7 м3
38.7 * 6000 = 232 200
```

Для доставки этот объём разложен как в Excel:

```text
second_light = 15.05 м3
parapet = 23.65 м3
```

### Кран несущих стен

Legacy-режим старого ЮСВ-кейса использует прямое значение:

```text
main_walls_crane_calc_method = legacy_manual_shifts
main_walls_crane_shifts = 2
```

В production-режиме количество смен крана для несущих стен больше не является ручным параметром Елены. Оно считается от количества доставок блоков:

```text
main_walls_crane_calc_method = delivery_trucks_threshold

if gas_block_delivery_trucks <= 3:
    main_walls_crane_shifts = 1
else:
    main_walls_crane_shifts = 2
```

Источник `gas_block_delivery_trucks` - расчётный блок `deliveries_and_cranes`, где доставки блоков считаются от закупочного объёма газоблоков и вместимости машины. Строка `main_walls_blocks_crane_moving_25t` берёт quantity из рассчитанного `main_walls_crane_shifts`.

Проверочные кейсы:

- `test_main_walls_crane_from_delivery_trucks`: 3 доставки -> 1 смена крана.
- `test_main_walls_crane_from_delivery_trucks_four`: 4 доставки -> 2 смены крана.

### Вентканалы и дымоход

Работа:

```text
1.72 / 0.15 = 11.4666666667 м2
11.4666666667 * 1200 = 13 760
```

Материал D500 150 мм:

```text
1.72 * 1.05 = 1.806
1.806 / 1.8 = 1.0033
ceil = 2 поддона
2 * 1.8 = 3.6 м3
3.6 * 5600 = 20 160
```

## Case-specific строки

## Этажность и блок 2-го этажа

После уточнения Елены production-логика поддерживает только 1 или 2 этажа:

```text
floors_count = 1 или 2
```

3-этажные дома не входят в MVP scope и отклоняются validation.

Старый термин `second_light` оставлен только для legacy-кейса ЮСВ. В production используется блок:

```text
floor_2_load_bearing_walls
```

Если `floors_count = 1`, блок несущих стен 2-го этажа выключен. Если `floors_count = 2`, блок включён, а объём кладки берётся из спецификации:

```text
floor_2_masonry_volume_m3
```

Парапет в production включается автоматически:

```text
parapet_enabled_calculated =
flat_roof_enabled and parapet_masonry_volume_m3 > 0
```

Обкладка вентканалов в production включается автоматически:

```text
vent_chimney_cladding_enabled_calculated =
flat_roof_enabled and vent_chimney_gas_block_spec_volume_m3 > 0
```

Геометрия вентканалов в production больше не собирается по сегментам и рядам. Основной режим:

```text
vent_chimney_geometry_calc_method = spec_volume_thickness
vent_chimney_cladding_area_m2 =
    vent_chimney_gas_block_spec_volume_m3 / vent_chimney_block_thickness_m
```

Где:

- `vent_chimney_gas_block_spec_volume_m3` - `AUTO_PROJECT`, объём кладки вентканалов из спецификации;
- `vent_chimney_block_thickness_m = 0.15` - `DEFAULT_VALUE`, блок 150 мм;
- `vent_chimney_segment_lengths_m[*]` - `DEPRECATED / LEGACY_CHECK_ONLY`;
- `vent_chimney_rows` - `DEPRECATED / LEGACY_CHECK_ONLY`;
- `block_height_m = 0.25` - `DEFAULT_VALUE / LEGACY_CHECK_ONLY`.

Старый режим `legacy_segments_rows` оставлен для ЮСВ-сверки и контрольной геометрии:

```text
vent_total_length = sum(length_m * count)
vent_height = block_height_m * vent_chimney_rows
vent_geometry_volume_m3 =
    vent_total_length * vent_height * vent_chimney_block_thickness_m
```

Подробности: `docs/report_load_bearing_walls_floor_2_refactor.md`.

В результате явно помечены строки, связанные со вторым светом / кладкой над кухней:

- `parapet_and_upper_level_masonry_work`
- `parapet_and_upper_level_gas_block_d400_material`
- `parapet_upper_level_adhesive`
- `parapet_and_second_light_chasing_for_d10_reinforcement`
- `parapet_and_second_light_rebar_a500_d10`

Для них в JSON стоит:

```json
"is_case_specific": true
```

## Manual / fixed строки

Некоторые строки пока считаются как ручные или фиксированные, потому что универсальная формула требует отдельного подтверждения:

- количество смен кранов;
- количество машин вывоза мусора;
- расходные материалы и амортизация инструмента;
- технический надзор.

Расходные материалы в текущем кейсе:

```text
raw = 100 521.70
display = 100 522
```

Формула процента для этой строки пока не подтверждена.

## Итоги текущего кейса

Кейс:

```text
experiments/load_bearing_walls_lintels_calculator/cases/test_load_bearing_walls_lintels/
```

Результат по Excel-логике raw totals:

```text
internal_materials_total_raw = 1 550 654.431
internal_materials_total     = 1 550 654

internal_works_total_raw     = 1 121 449.000
internal_works_total         = 1 121 449

internal_section_total_raw   = 2 672 103.431
internal_section_total       = 2 672 103
```

Дополнительно калькулятор показывает сумму отображённых округлённых строк:

```text
sum_of_displayed_line_material_totals = 1 550 656
sum_of_displayed_line_work_totals     = 1 121 449
sum_of_displayed_line_totals          = 2 672 105
```

Это объясняет, почему простая сумма видимых округлённых строк отличается от Excel-итога на 2 рубля. Excel считает итог от raw-значений, и калькулятор повторяет именно эту логику.

## Сверка со сметой

Калькулятор был сверен со скринами раздела серой сметы.

На скрине итог по разделу:

```text
Материалы: 1 550 654
Работы:    1 121 449
Итого:     2 672 103
```

Калькулятор выдаёт те же значения.

Проверка `expected.json`:

```text
119 ok
0 mismatch
```

## Формат результата

После запуска создаются:

```text
experiments/load_bearing_walls_lintels_calculator/output/test_load_bearing_walls_lintels/load_bearing_walls_lintels_result.json
experiments/load_bearing_walls_lintels_calculator/output/test_load_bearing_walls_lintels/load_bearing_walls_lintels_result.md
```

В JSON сохраняются:

- входные параметры;
- расчётные блоки;
- строки серой внутренней сметы;
- raw и rounded totals;
- expected;
- comparison;
- warnings.

## Команды запуска

Запуск расчёта:

```bash
../.venv/bin/python3 experiments/load_bearing_walls_lintels_calculator/run_load_bearing_walls_lintels_calc.py experiments/load_bearing_walls_lintels_calculator/cases/test_load_bearing_walls_lintels
```

Проверка компиляции:

```bash
../.venv/bin/python3 -m py_compile experiments/load_bearing_walls_lintels_calculator/load_bearing_walls_lintels_calculator.py experiments/load_bearing_walls_lintels_calculator/run_load_bearing_walls_lintels_calc.py
```

## Текущий статус

Калькулятор несущих стен и перемычек работает как отдельный экспериментальный модуль и повторяет проверенный фрагмент серой внутренней сметы без расхождений.

Он готов для добавления следующих кейсов: нужно создать новую папку в `cases/`, положить `input.json`, `expected.json`, `notes.md`, запустить runner и проверить comparison.
