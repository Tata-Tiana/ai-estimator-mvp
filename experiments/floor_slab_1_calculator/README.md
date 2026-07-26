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
│   ├── test_floor_slab_1/
│   │   ├── input.json
│   │   ├── expected.json
│   │   └── notes.md
│   ├── test_floor_slab_1_direct_formwork_rate/
│   │   ├── input.json
│   │   ├── expected.json
│   │   └── notes.md
│   ├── test_floor_slab_1_rebar_spec_lengths/
│   │   ├── input.json
│   │   ├── expected.json
│   │   └── notes.md
│   ├── test_floor_slab_1_insulation_spec_quantities/
│   │   ├── input.json
│   │   ├── expected.json
│   │   └── notes.md
│   └── test_floor_slab_1_spec_formwork_areas/
│       ├── input.json
│       ├── expected.json
│       └── notes.md
└── output/
    └── test_floor_slab_1/
        ├── floor_slab_1_result.json
        └── floor_slab_1_result.md
```

## Production-стандарт площадей опалубки

В production спецификация должна давать три готовые площади:

```text
main_formwork_area_m2
edge_formwork_area_m2
beams_formwork_area_m2
```

Смысл:

- `main_formwork_area_m2` - площадь опалубки под плиту; используется для строки `formwork_set_rental_material`;
- `edge_formwork_area_m2` - площадь торцевой опалубки плиты;
- `beams_formwork_area_m2` - площадь опалубки балок.

Режимы:

- `formwork_areas_calc_method = legacy_calculated_from_geometry` - legacy ЮСВ, где площади восстанавливаются через бетон, толщину, периметр и `beams.items`;
- `formwork_areas_calc_method = spec_formwork_areas` - production, где три площади берутся из спецификации.

Production-формулы:

```text
slab_formwork_area_m2 = main_formwork_area_m2
edge_and_beam_formwork_area_m2 = edge_formwork_area_m2 + beams_formwork_area_m2
```

Старые расчетные формулы остаются как контроль:

```text
calculated_main_formwork_area_m2 =
  (total_concrete_volume_from_spec_m3 - calculated_beams_concrete_volume_m3) / slab_thickness_m

calculated_edge_formwork_area_m2 =
  slab_edge_perimeter_m * edge_formwork_height_m

calculated_beams_formwork_area_m2 =
  sum(beam.length_m * (beam.width_m + 2 * beam.height_m) * beam.count)
```

Если контрольные значения отличаются от spec-площадей больше чем на `0.01 м2`, калькулятор добавляет warning, но не заменяет production-значения.

## Production-стандарт ставки опалубки

В production калькулятор плиты перекрытия 1-го этажа не зависит от площади плиты перекрытия 2-го этажа.

Режимы:

- `rates.formwork_rate_calc_method = legacy_supplier_quote_context` - legacy ЮСВ, где хранится справочный box-level контекст поставщика;
- `rates.formwork_rate_calc_method = direct_section_rate` - production, где используется готовая ставка для этой плиты.

Production использует:

```text
rates.formwork_rate_per_m2
```

Это применяемая ставка аренды комплекта опалубки для плиты перекрытия 1-го этажа.

В production не требуются:

```text
rates.formwork_supplier_quote_total
rates.slab_2_formwork_area_for_rate_context_m2
```

Эти поля относятся к будущему box-level quote context и не должны быть обязательными параметрами калькулятора плиты 1-го этажа.

## Production-стандарт доставки/вывоза опалубки

Количество машин доставки/вывоза опалубки в production считается от площади основной опалубки плиты:

```text
slab_formwork_area_m2 <= 180 -> 2 машины
slab_formwork_area_m2 > 180  -> 4 машины
```

Режимы:

- `rates.formwork_delivery_calc_method = area_threshold` - production default;
- `rates.formwork_delivery_calc_method = manual_override` - ручное исключение.

В режиме `area_threshold` поле `manual_lines.formwork_delivery_trucks_override` не требуется и не используется, даже если случайно осталось во входе старого кейса.

В режиме `manual_override` поле `manual_lines.formwork_delivery_trucks_override` обязательно.

В `calculation_blocks.formwork` выводятся:

```text
formwork_delivery_calc_method
formwork_delivery_area_source_m2
formwork_delivery_threshold_m2
formwork_delivery_trucks
formwork_delivery_breakdown
formwork_delivery_status
```

## Production-стандарт веса металла

В production калькулятор плиты перекрытия 1-го этажа не зависит от веса арматуры плиты перекрытия 2-го этажа.

Режимы:

- `rates.metal_delivery_calc_method = legacy_slab1_slab2_context` - legacy ЮСВ, где строка доставки металла считалась с контекстом веса арматуры 1-й и 2-й плит;
- `rates.metal_delivery_calc_method = section_output_only` - production, где калькулятор отдаёт только вес закупочной арматуры текущего раздела.

Production-выход:

```text
calculation_blocks.rebar.section_rebar_delivery_weight_kg
```

В production не требуется:

```text
rates.floor_slab_2_rebar_weight_for_delivery_context_kg
```

Доставка металла должна считаться на уровне `box_calculator` по суммарному весу металла коробки:

```text
total_box_metal_weight_kg = sum(section_rebar_delivery_weight_kg)
trucks = ceil(total_box_metal_weight_kg / 10000)
```

## Production-стандарт арматуры

В production арматура плиты перекрытия 1-го этажа приходит из спецификации в м.п., а не в кг.

Режимы:

- `rebar_calc_method = legacy_weight_parts` - legacy ЮСВ, где арматура задана весом через `source_weight_kg` / `source_weight_parts_kg`;
- `rebar_calc_method = spec_length_items` - production, где каждая позиция содержит `spec_length_m`.

Production item:

```json
{
  "floor": 1,
  "component": "floor_slab_1",
  "steel_class": "A500",
  "diameter_mm": 10,
  "spec_length_m": 6879.6,
  "kg_per_meter": 0.617,
  "rod_length_m": 11.7,
  "unit_price_per_m": 32.72
}
```

`code` и `name` не являются ручными production-полями: они формируются автоматически по классу стали и диаметру.

Формула закупки:

```text
length_with_waste_m = spec_length_m * waste_coeff
rods = ceil(length_with_waste_m / rod_length_m)
order_length_m = rods * rod_length_m
material_total = order_length_m * unit_price_per_m
section_rebar_delivery_weight_kg = sum(order_length_m * kg_per_meter)
```

`source_weight_parts_kg` оставлен только для legacy-кейса ЮСВ.

## Production-стандарт утепления плиты

В production утепление плиты перекрытия 1-го этажа не восстанавливается через фиксированную геометрию. Рабочие количества и чистый объём ЭППС приходят из спецификации.

Режимы:

- `insulation.insulation_calc_method = legacy_fixed_edge_length` - legacy-режим для старых регресс-кейсов, где длина торца плиты — фиксированная константа (84,8 м), не читается из проекта;
- `insulation.insulation_calc_method = spec_work_quantities` - production, где рабочие длины/площади и объём ЭППС берутся из спецификации.

Production input:

```text
insulation.slab_outer_edge_eps_work_length_m
insulation.edge_insulation_height_m
insulation.slab_edge_eps_material_area_m2
insulation.bottom_slab_eps_work_area_m2
insulation.total_eps_volume_from_spec_m3
beams.items[*].length_m
beams.items[*].height_m
beams.items[*].count
```

Калькулятор сам считает:

```text
beams_eps_work_length_m = sum(beam.length_m * beam.count)
beams_eps_material_area_m2 = sum(beam.length_m * beam.height_m * beam.count)
edge_beam_eps_work_length_m = slab_outer_edge_eps_work_length_m + beams_eps_work_length_m
edge_and_beam_eps_material_area_m2 = slab_edge_eps_material_area_m2 + beams_eps_material_area_m2
required_eps_volume_m3_raw = total_eps_volume_from_spec_m3 * eps_waste_coeff
eps_packs_ordered = ceil(required_eps_volume_m3_raw / eps_pack_volume_m3)
order_eps_volume_m3_raw = eps_packs_ordered * eps_pack_volume_m3
foam_cans_ordered = ceil((edge_and_beam_eps_material_area_m2 + bottom_slab_eps_work_area_m2) / foam_coverage_m2_per_can)
```

`insulation.edge_insulation_height_m` — высота утепления торца плиты. Для ЮСВ подтвержденное значение `0.18 м`: это фактические 180 мм, а не 200 мм из ошибочного названия раздела. Если поле не пришло, калькулятор использует fallback `geometry.slab_thickness_m` и добавляет warning.

`slab_edge_eps_material_area_m2` не выводится из длины торца и толщины ЭППС. Это отдельный production-параметр из спецификации, потому что рабочая длина торца в м.п. и площадь материала торца в м2 имеют разный смысл.

## Запуск

```bash
.venv/bin/python3 experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py experiments/floor_slab_1_calculator/cases/test_floor_slab_1
```

Production-кейс прямой ставки:

```bash
.venv/bin/python3 experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py experiments/floor_slab_1_calculator/cases/test_floor_slab_1_direct_formwork_rate
```

Production-кейс арматуры из м.п.:

```bash
.venv/bin/python3 experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py experiments/floor_slab_1_calculator/cases/test_floor_slab_1_rebar_spec_lengths
```

Production-кейс порога доставки опалубки:

```bash
.venv/bin/python3 experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py experiments/floor_slab_1_calculator/cases/test_floor_slab_1_formwork_delivery_threshold
```

Production-кейс утепления по спецификации:

```bash
.venv/bin/python3 experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py experiments/floor_slab_1_calculator/cases/test_floor_slab_1_insulation_spec_quantities
```

## Компиляция

```bash
.venv/bin/python3 -m py_compile experiments/floor_slab_1_calculator/floor_slab_1_calculator.py experiments/floor_slab_1_calculator/run_floor_slab_1_calc.py
```

## Ожидаемые итоги

```text
internal_materials_total = 1175601
internal_works_total = 611926
internal_section_total = 1787527
```
