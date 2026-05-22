# Отчёт по калькулятору плиты перекрытия 2-го этажа

Дата: 2026-05-21

## Кратко

В проекте `ai-estimator-mvp` сделан отдельный экспериментальный детерминированный калькулятор раздела:

`Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 2-го этажа на отм. +4.680 (200мм)`

Калькулятор считает только серую внутреннюю себестоимость: материалы/механизмы, работы и итог раздела. Клиентская часть, белая зона Excel, коммерческие коэффициенты, налоги, НР/СП/ТН и прибыль вне текущего scope.

AI в расчёте не используется. Формулы, ручные количества, округления и ожидаемые значения зафиксированы явно в `input.json`, `expected.json` и коде калькулятора.

## Где находится

```text
experiments/floor_slab_2_calculator/
├── calculator.py
├── run_case.py
├── README.md
├── notes.md
└── cases/
    └── test_floor_slab_2/
        ├── input.json
        ├── expected.json
        ├── result.json
        └── result.md
```

## Что считает калькулятор

Калькулятор считает 26 строк серой внутренней сметы:

- контрольную строку монтажа основной опалубки;
- комплект опалубки;
- доставку/вывоз опалубки манипулятором;
- подачу опалубки и арматуры автокраном;
- расходные материалы для опалубки;
- контрольную строку опалубки торцов плиты;
- фанеру;
- пиломатериал;
- контрольную строку каркаса армирования;
- арматуру А500 Ø16, Ø12, Ø10;
- работу по бетонированию плиты;
- бетон В22,5 М300;
- доставку бетона;
- бетононасос;
- демонтаж опалубки;
- утепление торцов плиты;
- ЭППС 100 мм;
- клей-пену;
- логистику 1%;
- расходные материалы и амортизацию инструмента 3%;
- нулевые строки структуры Excel: технический надзор, заготовительно-складские расходы, накладные и общехозяйственные расходы, сметная прибыль.

## Важные отличия от плиты 1-го этажа

- Балок в расчёте нет.
- Строка с названием про балки сохранена только как исходное название строки; фактически для 2-го этажа считается только плита/торцы.
- Не добавлена строка "Бетонирование балки...".
- Логика балок из калькулятора 1-го этажа не переносилась.
- Объём бетонирования `16.5 м3` берётся как manual/project quantity и не выводится из площади и толщины.

## Блоки расчёта

В `result.json` сохраняются структурированные блоки:

```text
calculation_blocks:
  geometry
  formwork
  plywood_and_timber
  rebar
  concrete
  insulation
  addons
```

Это нужно, чтобы были видны не только итоговые строки, но и промежуточные значения: площадь, периметр, листы фанеры, объём пиломатериала, закупочные длины арматуры, заказ бетона, пачки ЭППС, база для логистики и расходников.

## Ключевые формулы

### Геометрия

```text
slab_area_m2 = slab_length_m * slab_width_m
slab_edge_perimeter_m = slab_length_m * 2 + slab_width_m * 2
```

Текущий кейс:

```text
9 * 9.1 = 81.9 м2
9 * 2 + 9.1 * 2 = 36.2 м
```

### Комплект опалубки

```text
raw_supplier_rate = formwork_rental_supplier_quote_total / main_formwork_area_m2
material_total = main_formwork_area_m2 * formwork_rental_used_rate_per_m2
```

Для совпадения с текущей сметой используется ставка `850 руб/м2`.

### Фанера

```text
edge_plywood_sheets_raw = edge_formwork_area_m2 / plywood_sheet_working_area_m2
non_multiple_places_area_m2 = main_formwork_area_m2 * non_multiple_places_coeff
non_multiple_places_plywood_sheets_raw = non_multiple_places_area_m2 / plywood_sheet_working_area_m2
plywood_sheets = ceil(edge + non_multiple + reserve)
```

Текущий кейс:

```text
plywood_sheets = 16
material_total = 16 * 1450 = 23200
```

### Пиломатериал

```text
timber_volume_m3_raw = edge_formwork_area_m2 * timber_thickness_m
material_total = timber_volume_m3_raw * timber_unit_price
```

Важно: сумма считается от raw `0.362 м3`, а не от display `0.36 м3`.

### Арматура

Универсальная формула по каждому диаметру:

```text
source_weight_kg / kg_per_meter
-> length_with_waste_m = raw_length_m * 1.05
-> rods = ceil(length_with_waste_m / rod_length_m)
-> order_length_m = rods * rod_length_m
-> material_total = ROUND_HALF_UP(order_length_m * unit_price_per_m)
```

Текущий кейс:

```text
Ø16: 105.3 м.п. -> 8485
Ø12: 35.1 м.п. -> 1590
Ø10: 2679.3 м.п. -> 87667
```

Контрольный вес арматуры с запасом:

```text
total_rebar_weight_with_waste_kg = 1825.39
```

### Бетон

Работа по бетонированию:

```text
concrete_placing_volume_m3 = 16.5
work_total = 16.5 * 12000 = 198000
```

Это ручное/проектное количество текущего кейса. Калькулятор не выводит его из площади плиты и толщины.

Материал:

```text
concrete_volume_with_waste_raw_m3 = 16.5 * 1.05 = 17.325
concrete_order_volume_m3 = round_up_to_step(17.325, 0.5) = 17.5
material_total = 17.5 * 6400 = 112000
```

Доставка:

```text
delivery_trips = ceil(17.5 / 9) = 2
```

### Утепление торцов и ЭППС

Работа:

```text
quantity = slab_edge_perimeter_m = 36.2
work_total = 36.2 * 450 = 16290
```

Материал ЭППС 100 мм:

```text
edge_insulation_area_m2 = 36.2 * 0.18 = 6.516
required_volume_with_waste = 6.516 * 0.1 * 1.05 = 0.68418
packs = ceil(0.68418 / 0.2773) = 3
order_volume = 3 * 0.2773 = 0.8319
material_total = ROUND_HALF_UP(0.8319 * 9020) = 7504
```

Важно: высота утепления `0.18 м` сохранена для совпадения с текущей сметой, хотя название раздела говорит о плите 200 мм. Это вынесено в warning.

### Addons

Логистика и расходники считаются от raw-базы прямых затрат до addons:

```text
direct_cost_base_before_addons_raw = 689472.487
logistics = 1% = 6894.72487 -> 6895
consumables = 3% = 20684.17461 -> 20684
```

## Raw vs Display

Калькулятор хранит оба варианта:

- raw totals — расчёт от точных raw-значений;
- displayed line totals — сумма округлённых строк.

В текущем кейсе они отличаются на 1 рубль:

```text
internal_section_total_raw = 717051.38648
internal_section_total = 717051
sum_of_displayed_line_totals = 717052
```

Это ожидаемое отличие округлений, его не нужно "чинить" изменением формул строк.

## Результат по текущему кейсу

Кейс:

```text
experiments/floor_slab_2_calculator/cases/test_floor_slab_2/
```

Итоги:

```text
internal_materials_total_raw = 502761.38648
internal_materials_total = 502761
internal_works_total_raw = 214290
internal_works_total = 214290
internal_section_total_raw = 717051.38648
internal_section_total = 717051
sum_of_displayed_line_material_totals = 502762
sum_of_displayed_line_work_totals = 214290
sum_of_displayed_line_totals = 717052
```

Проверка:

```text
222 ok
0 mismatch
```

## Warnings текущего кейса

- `concrete_placing_volume_m3 = 16.5` — ручное/проектное количество; не выводится из площади и толщины.
- `edge_insulation_height_m = 0.18` — оставлено для совпадения с текущей сметой, хотя название раздела говорит о 200 мм.

## Что пока не сделано

- Нет клиентской/белой части сметы.
- Нет Excel export для этого раздела.
- Нет интеграции в общий `box_calculator`.
- Нет объединённой доставки металла по всей коробке дома.
- Нет автоматического извлечения входов из PDF для этого конкретного раздела.
- Нет переноса в стабильный слой `app/estimator/`.

## Команды

Запуск:

```bash
../.venv/bin/python3 experiments/floor_slab_2_calculator/run_case.py experiments/floor_slab_2_calculator/cases/test_floor_slab_2
```

Компиляция:

```bash
../.venv/bin/python3 -m py_compile experiments/floor_slab_2_calculator/calculator.py experiments/floor_slab_2_calculator/run_case.py
```
