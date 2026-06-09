# Standard Input Contract

Дата: 2026-06-04

Этот файл фиксирует новые стандарты входных данных, которые постепенно переводятся из legacy-кейсов в production-контур MVP.

## Фундаментная плита

### Опалубка бортов

Production-стандарт:

```text
formwork_calc_method = "spec_area"
slab_side_formwork_area_m2 = готовая площадь опалубки из спецификации, м2
```

Расчёт:

```text
formwork_area_m2 = slab_side_formwork_area_m2
```

От этой площади считаются:

- монтаж опалубки;
- фанера;
- пиломатериал;
- демонтаж опалубки.

Legacy-параметры:

- `slab_formwork_perimeter_m`;
- `slab_edge_height_m`;
- `slab_edge_height_strategy`.

Они остаются только для старого кейса `test_foundation_slab` и не должны быть обязательными для новых проектов.

### Фанера для опалубки

Production-стандарт:

```text
plywood_calc_method = "actual_area_with_waste"
plywood_sheet_width_m = 1.52
plywood_sheet_height_m = 1.52
plywood_waste_coeff = 1.05
```

Расчёт:

```text
plywood_sheet_area_m2 = 1.52 * 1.52
plywood_sheets = ceil(slab_side_formwork_area_m2 * 1.05 / plywood_sheet_area_m2)
```

Статус:

```text
plywood_calc_method = SYSTEM_SETTING
plywood_sheet_width_m = DEFAULT_VALUE / SYSTEM_SETTING
plywood_sheet_height_m = DEFAULT_VALUE / SYSTEM_SETTING
plywood_waste_coeff = DEFAULT_VALUE / SYSTEM_SETTING
show_in_review_form = false
```

Эти параметры не спрашивать у Елены по каждому проекту.

Legacy:

```text
plywood_calc_method = "working_area"
plywood_sheet_working_area_m2 = 2.25
```

Остаётся только для старого `test_foundation_slab`.

### Термовставки

Production-стандарт:

```text
thermal_insert_mode = "standard_50_100"
```

Работы:

```text
thermal_insert_50_length_m * thermal_insert_50_work_unit_price
thermal_insert_100_length_m * thermal_insert_100_work_unit_price
```

Материалы:

```text
round_up_to_multiple(thermal_insert_50_material_spec_qty * thermal_insert_material_waste_coeff, thermal_insert_50_pack_multiple_qty)
round_up_to_multiple(thermal_insert_100_material_spec_qty * thermal_insert_material_waste_coeff, thermal_insert_100_pack_multiple_qty)
```

Legacy-логика термовкладыша 150 мм через элемент и деление длины на 0.6 остаётся только для старого теста.

### Арматура

Production-стандарт:

```text
rebar_calc_method = "spec_length_m"
```

Проектная спецификация даёт арматуру в м.п., а не в кг.

Расчёт:

```text
source_length_m = source_length_m или sum(length_parts_m)
length_with_waste_m = source_length_m * rebar_waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
material_total = order_length_m * unit_price_per_m
design_weight_kg = source_length_m * kg_per_meter
delivery_weight_kg = order_length_m * kg_per_meter
```

Статус:

```text
source_length_m / length_parts_m = AUTO_PROJECT
kg_per_meter = PRICE_DATABASE / MATERIAL_CATALOG
rod_length_m = MATERIAL_CATALOG
unit_price_per_m = PRICE_DATABASE
```

Legacy:

```text
rebar_calc_method = "legacy_weight_to_length"
weight_parts_kg -> kg_per_meter -> length -> waste -> rods -> order_length_m
```

Остаётся только для старых проверочных кейсов.

### Доставка арматуры / металла

Production-стандарт:

```text
rebar_metal_delivery_trucks = AUTO_CALCULATED_BY_BOX
```

`rebar_metal_delivery_trucks` больше не должен быть ручным input-параметром раздела фундаментной плиты в production-потоке.

Статус:

```text
old status: manual/input в foundation_slab
new status: AUTO_CALCULATED_BY_BOX
show_in_review_form: false
can_override: yes, только на уровне box_calculator / project logistics settings
```

Комментарий:

```text
Не вводится в разделе фундаментной плиты.
Рассчитывается по общему весу металла коробки и распределяется по разделам.
```

Legacy-поле остаётся в старых кейсах для сверки с зафиксированной сметой.
