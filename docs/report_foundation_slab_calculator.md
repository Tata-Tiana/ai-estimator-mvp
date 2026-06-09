# Отчёт по калькулятору фундаментной плиты

Дата: 2026-05-15

## Кратко

В проекте `ai-estimator-mvp` сделан экспериментальный детерминированный калькулятор раздела "Устройство фундаментной плиты дома, террасы, крыльца (250мм, 300мм)".

Калькулятор считает только серую внутреннюю себестоимость: материалы, работы и итог раздела. Клиентская часть сметы, рентабельность, НР/СП/ТН и коммерческие коэффициенты не считаются.

Расчёт сделан по той же архитектуре, что и калькулятор земляных работ: отдельный модуль расчёта, отдельный runner, кейс с `input.json`, `expected.json`, `notes.md`, результат в JSON и Markdown.

## Где находится

```text
experiments/foundation_slab_calculator/
├── README.md
├── foundation_slab_calculator.py
├── run_foundation_slab_calc.py
├── cases/
│   ├── test_foundation_slab/
│   │   ├── input.json
│   │   ├── expected.json
│   │   └── notes.md
│   └── test_foundation_slab_thermal_inserts_standard/
│       ├── input.json
│       ├── expected.json
│       └── notes.md
│   └── test_foundation_slab_formwork_spec_area/
│       ├── input.json
│       ├── expected.json
│       └── notes.md
│   └── test_foundation_slab_plywood_standard/
│       ├── input.json
│       ├── expected.json
│       └── notes.md
│   └── test_foundation_slab_rebar_spec_length/
│       ├── input.json
│       ├── expected.json
│       └── notes.md
└── output/
    └── test_foundation_slab/
        ├── foundation_slab_result.json
        └── foundation_slab_result.md
```

## Что считает калькулятор

Калькулятор считает 25 строк серой внутренней сметы и 3 нулевые строки структуры Excel:

- монтаж мембраны PLANTER;
- материал Planter Standard;
- PLANTERBAND;
- монтаж опалубки;
- фанеру;
- пиломатериал;
- укладку ЭППС 50 мм;
- legacy-термовкладыш или новые термовставки 50/100 мм;
- Пеноплэкс / ЭППС 50 мм;
- Пеноплэкс / ЭППС 100 мм;
- подачу арматуры краном;
- агрегирующую строку каркаса армирования;
- арматуру Ø16, Ø12, Ø10, Ø6;
- доставку арматуры и металла;
- работу по бетонированию;
- бетон В22,5 М300;
- доставку бетона;
- бетононасос;
- демонтаж опалубки;
- логистику и снабжение;
- расходные материалы и амортизацию инструмента;
- технический надзор.

После технадзора в результате сохраняются строки:

- "Заготовительно-складские расходы";
- "Накладные и общехозяйственные расходы";
- "Сметная прибыль".

Они помечены как `zero_excel_structure_line`, имеют нулевые суммы и не меняют внутреннюю серую себестоимость. Суммы клиентской части из Excel в расчёт не переносятся.

## Блоки расчёта

В результате расчёта есть структурированные блоки:

```text
calculation_blocks:
  confirmed_rules
  membrane
  formwork
  eps
  thermal_insert
  rebar
  concrete
  manual_lines
```

Это сделано, чтобы в JSON были видны не только итоговые строки сметы, но и промежуточные значения: рулоны, листы, пачки, прутки, объёмы, доставки, контрольные показатели.

## Подтверждённые правила

После комментариев Елены в калькулятор и notes добавлены подтверждённые правила:

- PLANTERBAND = количество рулонов мембраны * 4.
- В legacy-кейсе борта считались как внешний периметр фундаментной плиты * высота борта.
- В новом стандарте площадь опалубки бортов берётся готовым значением из спецификации.
- Пиломатериал = площадь опалубки * 0.05, без дополнительного коэффициента 1.5.
- Пеноплэкс = ЭППС.
- В legacy-кейсе ЭППС 50 мм + ЭППС 100 мм дают термовкладыш 150 мм.
- В новом стандарте Елены термовставки 50 мм и 100 мм считаются отдельно.
- В legacy-кейсе арматура считается из веса в кг, а в новом стандарте Елены - из м.п. по спецификации.
- Доставка металла ориентируется на 10 тонн на машину по общему весу листа "Коробка".
- Фанера в production-стандарте считается по листу 1.52 x 1.52 м с запасом 5% и округлением вверх.
- `working_area = 2.25 м2` оставлен только как legacy для старого кейса.

## Важные уточнения по формулам

### Мембрана

Монтаж мембраны считается как работа по м2.

Planter Standard считается как материал через рулоны:

```text
area_with_overlap = membrane_area_m2 * membrane_overlap_coeff
rolls = ceil(area_with_overlap / membrane_roll_area_m2)
```

PLANTERBAND считается от количества рулонов:

```text
planterband_quantity = membrane_rolls * 4
```

### Опалубка и пиломатериал

В legacy-кейсе площадь опалубки считалась по формуле:

```text
formwork_area_m2 = slab_formwork_perimeter_m * slab_edge_height_m
```

В новом production-стандарте площадь опалубки приходит готовым значением из спецификации:

```text
formwork_calc_method = "spec_area"
formwork_area_m2 = slab_side_formwork_area_m2
```

Периметр и высота борта больше не являются обязательными входами для расчёта опалубки в новом стандарте.

Пиломатериал:

```text
timber_volume_m3 = formwork_area_m2 * 0.05
```

`0.05` - это толщина доски 50 мм, а не коэффициент запаса.

### Фанера

Legacy-кейс использует метод:

```text
plywood_sheets = ceil(formwork_area_m2 / plywood_sheet_working_area_m2)
```

Этот режим нужен только для повторения исходной сметы:

```text
plywood_calc_method = "working_area"
plywood_sheet_working_area_m2 = 2.25
```

Production-стандарт:

```text
plywood_calc_method = "actual_area_with_waste"
plywood_sheet_area_m2 = 1.52 * 1.52
plywood_sheets = ceil(formwork_area_m2 * 1.05 / plywood_sheet_area_m2)
```

Размер листа `1.52 x 1.52 м` и запас `5%` являются системными настройками. Их не нужно показывать Елене как ручные поля.

Проверочный кейс:

```text
experiments/foundation_slab_calculator/cases/test_foundation_slab_plywood_standard/
```

В нём при `slab_side_formwork_area_m2 = 24.3`:

```text
plywood_sheet_area_m2 = 2.3104
plywood_raw_sheets = 11.0435
plywood_sheets = 12
```

### ЭППС / Пеноплэкс

Площадь укладки ЭППС 50 мм под плитой считается из объёма:

```text
eps50_laying_area_m2 = eps50_under_slab_volume_m3 / eps50_thickness_m
```

Материал ЭППС 50 мм считается с запасом 5% под плитой и добавлением 50-мм слоя термовкладыша.

Материал ЭППС 100 мм считается только для термовкладыша, без запаса 5%.

Оба материала округляются до целых пачек.

### Термовставки по новому стандарту Елены

Добавлен отдельный режим:

```text
thermal_insert_mode = "standard_50_100"
```

В нём старая логика термовкладыша 150 мм не используется. Калькулятор больше не делит длину на `0.6`, не считает количество элементов 400 x 150 x высота и не подмешивает материал термовставок в общие строки ЭППС 50/100.

Работы считаются по длине из спецификации:

```text
thermal_insert_50_work_total = thermal_insert_50_length_m * thermal_insert_50_work_unit_price
thermal_insert_100_work_total = thermal_insert_100_length_m * thermal_insert_100_work_unit_price
```

Материал считается по спецификации:

```text
thermal_insert_50_raw_qty = thermal_insert_50_material_spec_qty * thermal_insert_material_waste_coeff
thermal_insert_50_purchase_qty = round_up_to_multiple(thermal_insert_50_raw_qty, thermal_insert_50_pack_multiple_qty)

thermal_insert_100_raw_qty = thermal_insert_100_material_spec_qty * thermal_insert_material_waste_coeff
thermal_insert_100_purchase_qty = round_up_to_multiple(thermal_insert_100_raw_qty, thermal_insert_100_pack_multiple_qty)
```

В смете появляются отдельные строки:

- "Устройство и монтаж термовставок 50 мм";
- "Устройство и монтаж термовставок 100 мм";
- "Материал термовставок 50 мм";
- "Материал термовставок 100 мм".

Проверочный кейс нового стандарта:

```text
experiments/foundation_slab_calculator/cases/test_foundation_slab_thermal_inserts_standard/
```

### Арматура по новому стандарту Елены

Добавлен отдельный режим:

```text
rebar_calc_method = "spec_length_m"
```

В legacy-режиме старый кейс сохраняется без изменения эталона: вес из спецификации переводится в м.п. через `kg_per_meter`, затем добавляется запас, длина округляется до целых хлыстов и стоимость считается по м.п.

В новом production-стандарте проектная спецификация должна давать арматуру в м.п. по позиции/диаметру. Вес не вводится из проекта, а считается автоматически:

```text
source_length_m = source_length_m или sum(length_parts_m)
length_with_waste_m = source_length_m * rebar_waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
material_total = order_length_m * unit_price_per_m
design_weight_kg = source_length_m * kg_per_meter
delivery_weight_kg = order_length_m * kg_per_meter
```

`kg_per_meter`, `rod_length_m` и `unit_price_per_m` пока остаются в `input.json` тестового кейса. Для production они должны приходить из `price_registry` / каталога арматуры.

В `result.md` добавлен блок "Контроль армирования":

- вес арматуры по спецификации;
- вес арматуры с запасом/закупкой;
- объём бетона;
- плотность армирования по спецификации;
- плотность армирования с запасом.

Проверочный кейс нового стандарта:

```text
experiments/foundation_slab_calculator/cases/test_foundation_slab_rebar_spec_length/
```

Проверочный кейс новой площади опалубки из спецификации:

```text
experiments/foundation_slab_calculator/cases/test_foundation_slab_formwork_spec_area/
```

### Арматура

Арматура считается универсальной функцией:

```text
вес в кг
-> перевод в м.п.
-> запас 5%
-> округление до целых прутков
-> закупочные м.п.
-> стоимость
```

Для Ø16, Ø12, Ø10 длина прутка `11.7 м`.

Для Ø6 длина прутка `6 м`.

### Бетон

Работа по бетонированию считается от проектного объёма:

```text
81 м3
```

Материал бетон считается с запасом и округлением:

```text
81 * 1.05 = 85.05
round_up_to_0.5 = 85.5 м3
```

Доставка бетона:

```text
ceil(85.5 / 9) = 10 рейсов
```

## Результат по текущему кейсу

Кейс:

```text
experiments/foundation_slab_calculator/cases/test_foundation_slab/
```

Результат:

```text
internal_materials_total = 1 454 675
internal_works_total    = 1 083 650
internal_section_total  = 2 538 325
```

Проверка:

```text
229 ok
0 mismatch
```

Новый кейс термовставок 50/100 мм также проходит comparison без mismatch:

```text
41 ok
0 mismatch
```

Кейс новой площади опалубки из спецификации также проходит comparison без mismatch:

```text
25 ok
0 mismatch
```

При сверке со скрином Excel все видимые строки совпали построчно. Отличие итоговой суммы Excel на 1 рубль связано с округлением итогов и не влияет на корректность расчёта строк.

## Warning в текущем кейсе

В результате есть одно предупреждение:

```text
thermal_insert_piece_depth_for_eps_m отличается от slab_edge_height_m
```

Смысл: Елена уточнила, что обычно для термовкладыша нужно брать высоту плиты, например `0.3 м`, но в текущем кейсе значение `0.25 м` после округления до пачек не меняет закупку. Поэтому калькулятор не меняет значение автоматически, а показывает warning.

## Доставка металла

Строка доставки арматуры оставлена manual/fixed line, как в смете.

Дополнительно добавлена контрольная подсказка:

```text
suggested_box_metal_delivery_trucks = ceil(box_total_metal_weight_kg / 10000)
```

В текущем кейсе:

```text
box_total_metal_weight_kg = 8 263
suggested_box_metal_delivery_trucks = 1
actual_rebar_metal_delivery_trucks = 1
```

## Команды запуска

Запуск расчёта:

```bash
../.venv/bin/python3 experiments/foundation_slab_calculator/run_foundation_slab_calc.py experiments/foundation_slab_calculator/cases/test_foundation_slab
```

Проверка компиляции:

```bash
../.venv/bin/python3 -m py_compile experiments/foundation_slab_calculator/foundation_slab_calculator.py experiments/foundation_slab_calculator/run_foundation_slab_calc.py
```

## Текущий статус

Калькулятор фундаментной плиты работает как экспериментальный модуль и повторяет проверенный фрагмент серой внутренней сметы без расхождений по comparison.

Он готов для добавления следующих кейсов: нужно создать новую папку в `cases/`, положить `input.json`, `expected.json`, `notes.md`, запустить runner и проверить сравнение.
