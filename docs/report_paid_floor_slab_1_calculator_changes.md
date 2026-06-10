# Отчёт по внесению изменений в калькулятор плиты перекрытия 1-го этажа

Дата: 2026-06-10

Проект: `ai-estimator-mvp`

Раздел сметы: `Ж/Б монолитная плита перекрытия 1-го этажа с балками`

Папка калькулятора:

```text
experiments/floor_slab_1_calculator/
```

## Цель работ

Калькулятор плиты перекрытия 1-го этажа был доработан под production-правила, уточнённые с Еленой. Главная цель — убрать зависимости от параметров плиты 2-го этажа, старых ручных override и case-specific геометрии ЮСВ, оставив старый locked-кейс как legacy для сверки с исходной Excel-сметой.

Работы выполнены как дополнительная оплачиваемая доработка существующего калькулятора.

## Общий принцип изменений

- старый кейс `test_floor_slab_1` сохранён как legacy/locked;
- старый `expected.json` не менялся;
- production-кейсы вынесены отдельно;
- новые production-режимы используют данные из спецификации проекта или системные defaults;
- box-level задачи только задокументированы и не реализовывались в этом разделе.

## Что изменено

### 1. Ставка комплекта опалубки

Что было:

- в ЮСВ поставщик дал общее предложение по опалубке на две плиты;
- ставка могла рассматриваться через контекст площади плиты 1-го и 2-го этажа;
- в калькуляторе плиты 1-го этажа присутствовали box-level поля:

```text
rates.formwork_supplier_quote_total
rates.slab_2_formwork_area_for_rate_context_m2
```

Что стало:

Добавлен режим:

```text
rates.formwork_rate_calc_method
```

Варианты:

- `legacy_supplier_quote_context` — legacy ЮСВ;
- `direct_section_rate` — production.

Production использует прямую ставку текущего раздела:

```text
rates.formwork_rate_per_m2
```

Поля `formwork_supplier_quote_total` и `slab_2_formwork_area_for_rate_context_m2` больше не обязательны для production-кейса плиты 1-го этажа. Они оставлены только как legacy/reference context.

### 2. Доставка/вывоз опалубки

Что было:

- количество машин могло зависеть от ручного поля:

```text
manual_lines.formwork_delivery_trucks_override
```

- старое правило имело неопределённый диапазон `150-180 м2`.

Что стало:

Добавлен режим:

```text
rates.formwork_delivery_calc_method
```

Варианты:

- `area_threshold` — production default;
- `manual_override` — исключение.

Production-формула:

```text
if slab_formwork_area_m2 <= 180:
    formwork_delivery_trucks = 2
else:
    formwork_delivery_trucks = 4
```

Расшифровка:

- до `180 м2` включительно: 1 привоз + 1 вывоз = 2 машины;
- более `180 м2`: 2 привоза + 2 вывоза = 4 машины.

`manual_lines.formwork_delivery_trucks_override` больше не обязателен в production и используется только в режиме `manual_override`.

### 3. Доставка арматуры и металла

Что было:

Калькулятор плиты 1-го этажа использовал вес арматуры плиты 2-го этажа для контекста доставки металла:

```text
rates.floor_slab_2_rebar_weight_for_delivery_context_kg
```

Что стало:

Добавлен режим:

```text
rates.metal_delivery_calc_method
```

Варианты:

- `legacy_slab1_slab2_context` — legacy ЮСВ;
- `section_output_only` — production.

Production-калькулятор отдаёт только вес закупочной арматуры текущего раздела:

```text
section_rebar_delivery_weight_kg =
    sum(order_length_m * kg_per_meter)
```

Количество машин доставки металла по всей коробке должно считаться выше, на уровне `box_calculator`:

```text
total_box_metal_weight_kg = sum(section_rebar_delivery_weight_kg)
trucks = ceil(total_box_metal_weight_kg / 10000)
```

### 4. Арматура плиты 1-го этажа

Что было:

Арматура приходила весом в кг:

```text
source_weight_kg = sum(source_weight_parts_kg)
base_length_m = source_weight_kg / kg_per_meter
length_with_waste_m = base_length_m * waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
```

Что стало:

Добавлен режим:

```text
rebar_calc_method
```

Варианты:

- `legacy_weight_parts` — старый ЮСВ-режим;
- `spec_length_items` — production.

Production item:

```text
floor = 1
component = floor_slab_1
steel_class
diameter_mm
spec_length_m
kg_per_meter
rod_length_m
unit_price_per_m
```

Формула:

```text
base_length_m = spec_length_m
length_with_waste_m = spec_length_m * waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
delivery_weight_kg = order_length_m * kg_per_meter
material_total = order_length_m * unit_price_per_m
```

`source_weight_parts_kg` оставлен только для legacy-кейса.

### 5. Утепление плиты

Что было:

Утепление частично восстанавливалось через legacy-геометрию ЮСВ:

- длина утепления наружного торца;
- площадь торца;
- площадь низа через остаток объёма.

Что стало:

Добавлен режим:

```text
insulation.insulation_calc_method
```

Варианты:

- `legacy_usv_geometry` — старый ЮСВ-режим;
- `spec_work_quantities` — production.

Production-источники из спецификации:

```text
insulation.slab_outer_edge_eps_work_length_m
insulation.slab_edge_eps_material_area_m2
insulation.bottom_slab_eps_work_area_m2
insulation.total_eps_volume_from_spec_m3
beams.items[*].length_m
beams.items[*].height_m
beams.items[*].count
```

Калькулятор считает:

```text
beams_eps_work_length_m = sum(length_m * count)
beams_eps_material_area_m2 = sum(length_m * height_m * count)
edge_beam_eps_work_length_m =
    slab_outer_edge_eps_work_length_m + beams_eps_work_length_m
edge_and_beam_eps_material_area_m2 =
    slab_edge_eps_material_area_m2 + beams_eps_material_area_m2
```

ЭППС закупается от чистого объёма из спецификации:

```text
required_eps_volume_m3_raw =
    total_eps_volume_from_spec_m3 * eps_waste_coeff
eps_packs_ordered =
    ceil(required_eps_volume_m3_raw / eps_pack_volume_m3)
order_eps_volume_m3_raw =
    eps_packs_ordered * eps_pack_volume_m3
```

Важно: `slab_edge_eps_material_area_m2` не выводится из длины торца и толщины ЭППС. Это отдельная площадь материала из спецификации.

## Новые кейсы

Добавлены production-кейсы:

```text
test_floor_slab_1_direct_formwork_rate
test_floor_slab_1_formwork_delivery_threshold
test_floor_slab_1_rebar_spec_lengths
test_floor_slab_1_insulation_spec_quantities
```

Что они проверяют:

- прямую ставку опалубки без контекста плиты 2-го этажа;
- порог доставки опалубки `180 м2`;
- арматуру из спецификации в м.п.;
- section-only вес металла для будущего box-level delivery;
- утепление по рабочим количествам и объёму ЭППС из спецификации.

## Документация

Обновлены:

```text
experiments/floor_slab_1_calculator/README.md
docs/report_floor_slab_1_calculator.md
```

Созданы технические отчёты:

```text
docs/report_floor_slab_1_formwork_rate_context_refactor.md
docs/report_floor_slab_1_formwork_delivery_threshold_refactor.md
docs/report_floor_slab_1_metal_delivery_context_refactor.md
docs/report_floor_slab_1_rebar_spec_length_refactor.md
docs/report_floor_slab_1_insulation_spec_quantities_refactor.md
```

## Что не входило в работы

В рамках этой доработки не менялись:

- `pdf_parser_pipeline`;
- `input_builder`;
- `price_registry`;
- `box_calculator`;
- плита перекрытия 2-го этажа;
- другие разделы;
- клиентская часть;
- Excel-структура.

## Результат

Калькулятор плиты 1-го этажа переведён на набор production-режимов, где данные берутся из спецификации текущего раздела, а cross-section/box-level зависимости вынесены в TODO для будущего `box_calculator`.

Старый locked-кейс ЮСВ сохранён и продолжает проходить без изменения старого `expected.json`.
