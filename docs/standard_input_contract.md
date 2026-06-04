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
