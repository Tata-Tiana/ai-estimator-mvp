# Отчёт по калькулятору плиты перекрытия 1-го этажа

Дата: 2026-05-22

## Кратко

В проекте `ai-estimator-mvp` сделан отдельный экспериментальный детерминированный калькулятор раздела:

`Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 1-го этажа на отм. +3.480 (180 мм) с балками`

Калькулятор считает только серую внутреннюю себестоимость: материалы/механизмы, работы и итог раздела. Клиентская часть, белая зона Excel, коммерческие коэффициенты, налоги, НР/СП и прибыль вне текущего scope.

AI в расчёте не используется. Формулы, ручные количества, округления и ожидаемые значения зафиксированы явно в `input.json`, `expected.json` и коде калькулятора.

## Где находится

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

## Что считает калькулятор

Калькулятор считает 29 строк серой внутренней сметы:

- контрольную строку монтажа основной опалубки;
- комплект опалубки;
- доставку/вывоз опалубки манипулятором;
- подачу опалубки и арматуры автокраном;
- расходные материалы для опалубки;
- контрольную строку опалубки балок и отбортовки плиты;
- фанеру;
- пиломатериал;
- контрольную строку каркаса армирования;
- арматуру А500 Ø25, Ø16, Ø12, Ø10;
- арматуру А240 Ø8, Ø6;
- доставку арматуры/металла;
- бетонирование плиты;
- бетонирование балок;
- бетон В22,5 М300;
- доставку бетона;
- бетононасос;
- демонтаж опалубки как нулевую внутреннюю строку;
- утепление торцов плиты и балок;
- утепление низа плиты;
- ЭППС 100 мм;
- клей-пену;
- логистику 1%;
- расходные материалы и амортизацию инструмента 3%;
- технический надзор fixed `5000`.

## Блоки расчёта

В `result.json` сохраняются структурированные блоки:

```text
calculation_blocks:
  geometry
  beams
  formwork
  plywood_and_timber
  rebar
  concrete
  insulation
  overheads
  manual_lines
  control_metrics
```

Это нужно, чтобы были видны не только итоговые строки, но и промежуточные значения: геометрия плиты, объём и опалубка балок, листы фанеры, объём пиломатериала, закупочные длины арматуры, заказ бетона, утепление, база для логистики и расходников.

## Ключевые формулы

### Балки

В текущем кейсе учитываются балки Б-1, Б-2 и Б-3.

```text
beam_concrete_volume_m3 = length_m * width_m * height_m
beam_formwork_area_m2 = length_m * (width_m + 2 * height_m)
```

Итоги по балкам:

```text
total_length_m = 23.2
total_concrete_volume_m3 = 3.1548
total_formwork_area_m2 = 27.992
```

### Основная площадь плиты

Основная площадь плиты выводится из общего проектного объёма бетона и объёма балок:

```text
slab_concrete_volume_m3_raw = total_concrete_volume_from_spec_m3 - beams_total_concrete_volume_m3
slab_formwork_area_m2 = slab_concrete_volume_m3_raw / slab_thickness_m
```

Текущий кейс:

```text
40.53 - 3.1548 = 37.3752 м3
37.3752 / 0.18 = 207.64 м2
```

Контрольная геометрия `210.64 м2` хранится только как контрольный показатель. В смете используется `207.64 м2`.

### Комплект опалубки

Для совпадения с текущей сметой используется ставка `600 руб/м2`.

```text
material_total = 207.64 * 600 = 124584
```

Поставщик давал общий контекст на плиты 1-го и 2-го этажей; raw average rate хранится справочно, но не заменяет ставку текущей строки.

### Доставка опалубки и кран

Доставка/вывоз опалубки:

```text
4 машины * 20000 = 80000
```

Текущее правило:

- `<=150 м2`: ориентировочно 1 привоз + 1 вывоз;
- `>180 м2`: 2 привоз + 2 вывоз;
- `150-180 м2`: manual review.

Кран:

```text
2 смены * 30000 = 60000
```

Третья смена крана пока только через manual review / override.

### Фанера и пиломатериал

Площадь для опалубки балок и отбортовки:

```text
edge_formwork_area_m2 = slab_edge_perimeter_m * edge_formwork_height_m
edge_and_beam_formwork_area_m2 = edge_formwork_area_m2 + beams_formwork_area_m2
```

Текущий кейс:

```text
118 * 0.2 = 23.6 м2
23.6 + 27.992 = 51.592 м2
```

Фанера:

```text
edge_and_beam_plywood_sheets_raw = 51.592 / 2.3
non_multiple_places_area_m2 = 207.64 * 0.2
order_plywood_sheets = ceil(edge + non_multiple + reserve)
```

Текущий результат:

```text
order_plywood_sheets = 51
material_total = 51 * 1450 = 73950
```

Пиломатериал:

```text
timber_volume_m3_raw = 2.790845652
material_total = ROUND_HALF_UP(2.790845652 * 21500) = 60003
```

Важно: сумма считается от raw `2.790845652`, а не от display `2.79`.

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
Ø25 А500: 46.8 м.п. -> 9189
Ø16 А500: 81.9 м.п. -> 6600
Ø12 А500: 58.5 м.п. -> 2649
Ø10 А500: 6879.6 м.п. -> 225101
Ø8 А240: 48 м.п. -> 1152
Ø6 А240: 180 м.п. -> 2398
```

Контрольная строка каркаса:

```text
46.8 + 81.9 + 58.5 + 6879.6 + 48 + 180 = 7294.8 м.п.
```

### Бетон

Бетонирование плиты:

```text
37.3752 * 12000 = 448502.4 -> 448502
```

Бетонирование балок:

```text
3.1548 * 20000 = 63096
```

Материал бетон:

```text
total_project_concrete_volume_m3 = 37.3752 + 3.1548 = 40.53
concrete_volume_with_waste_m3_raw = 40.53 * 1.05 = 42.5565
order_concrete_volume_m3 = ceil(42.5565) = 43
material_total = 43 * 6400 = 275200
```

Доставка бетона:

```text
ceil(42.5565 / 9) = 5 рейсов
5 * 7500 = 37500
```

Бетононасос:

```text
1 смена * 38000 = 38000
```

Бетононасос не вычисляется от объёма бетона, это fixed/manual line.

### Утепление

Утепление торцов плиты и балок:

```text
slab_outer_edge_length_m = 84.8
insulated_beams_total_length_m = 23.2
total_insulation_length_m = 108
work_total = 108 * 450 = 48600
```

Утепление низа плиты:

```text
bottom_slab_eps_volume_m3 = 7.77 - 2.578 = 5.192
bottom_slab_insulation_area_m2_raw = 5.192 / 0.1 = 51.92
work_total = 51.92 * 900 = 46728
```

ЭППС:

```text
base_eps_volume_m3 = 77.7 * 0.1 = 7.77
required_eps_volume_m3_raw = 7.77 * 1.05 = 8.1585
packs_ordered = ceil(8.1585 / 0.2773) = 30
order_eps_volume_m3_raw = 30 * 0.2773 = 8.319
material_total = ROUND_HALF_UP(8.319 * 9020) = 75037
```

### Overheads текущего scope

Логистика и расходники считаются от raw-базы до overheads:

```text
base_subtotal_raw_before_overheads = 1713968.300518
logistics = 1% = 17139.68300518 -> 17140
consumables = 3% = 51419.04901554 -> 51419
```

Технический надзор:

```text
fixed = 5000
```

## Raw vs Display

Калькулятор хранит raw и displayed значения отдельно:

- `quantity_raw`;
- `quantity_display`;
- `material_total_raw`;
- `material_total`;
- `work_total_raw`;
- `work_total`;
- `line_total_raw`;
- `line_total`.

Это важно для строк пиломатериала, бетонирования, утепления и ЭППС: Excel может показывать округлённое количество, но сумма считается от raw.

## Результат по текущему кейсу

Кейс:

```text
experiments/floor_slab_1_calculator/cases/test_floor_slab_1/
```

Итоги:

```text
internal_materials_total = 1175601
internal_works_total = 611926
internal_section_total = 1787527
base_subtotal_raw_before_overheads = 1713968.300518
logistics_and_supply_total = 17140
consumables_and_tool_depreciation_total = 51419
technical_supervision_total = 5000
```

Проверка:

```text
194 ok
0 mismatch
```

## Warnings и ручные места

- Доставка/вывоз опалубки имеет пороговое правило и manual review в диапазоне `150-180 м2`.
- Третья смена автокрана пока только через manual review / override.
- Бетононасос — fixed/manual line.
- Доставка металла в этом экспериментальном калькуляторе считается для совпадения с текущей сметой. В будущем `box_calculator` должен считать доставку металла один раз по общему весу металла коробки.
- Технический надзор — fixed `5000`.

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
../.venv/bin/python3 experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py experiments/floor_slab_1_calculator/cases/test_floor_slab_1
```

Компиляция:

```bash
../.venv/bin/python3 -m py_compile experiments/floor_slab_1_calculator/floor_slab_1_calculator.py experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py
```
