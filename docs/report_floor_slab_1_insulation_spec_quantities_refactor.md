# Paid report: refactor утепления плиты перекрытия 1-го этажа

Дата: 2026-06-10

## Раздел

`Ж/Б монолитная плита перекрытия 1-го этажа с балками`

## Что было

Утепление плиты 1-го этажа повторяло legacy-логику ЮСВ:

- часть рабочих количеств восстанавливалась из геометрии конкретного проекта;
- наружная длина утепления торца плиты была фактически привязана к старым размерам ЮСВ;
- площадь низа плиты выводилась через остаток объёма ЭППС;
- чистый объём ЭППС `total_eps_volume_from_spec_m3` уже был во входе, но не был единственным источником закупки материала в явном production-режиме.

Такую схему нельзя использовать как универсальный production-стандарт: она работает для сверки ЮСВ, но прячет проектную геометрию внутри калькулятора.

## Что изменено

Добавлен режим:

```text
insulation.insulation_calc_method
```

Варианты:

- `legacy_usv_geometry` - старый режим ЮСВ для locked-кейса;
- `spec_work_quantities` - production-режим по рабочим количествам и объёму из спецификации.

Старый `test_floor_slab_1` оставлен в legacy-режиме, `expected.json` не менялся.

## Production input

В production спецификация должна дать:

```text
insulation.slab_outer_edge_eps_work_length_m
insulation.slab_edge_eps_material_area_m2
insulation.bottom_slab_eps_work_area_m2
insulation.total_eps_volume_from_spec_m3
beams.items[*].length_m
beams.items[*].height_m
beams.items[*].count
```

`slab_outer_edge_eps_work_length_m` используется для строки работ в м.п.

`slab_edge_eps_material_area_m2` используется как площадь материала торца. Она не выводится из длины торца и толщины ЭППС, потому что для универсального production-расчёта это отдельная спецификационная величина.

`total_eps_volume_from_spec_m3` - чистый объём ЭППС из спецификации до запаса и до округления до упаковок.

## Формулы

Балки:

```text
beams_eps_work_length_m = sum(beam.length_m * beam.count)
beams_eps_material_area_m2 = sum(beam.length_m * beam.height_m * beam.count)
```

Работы:

```text
edge_beam_eps_work_length_m =
  slab_outer_edge_eps_work_length_m + beams_eps_work_length_m
```

Площадь материала для торцов и балок:

```text
edge_and_beam_eps_material_area_m2 =
  slab_edge_eps_material_area_m2 + beams_eps_material_area_m2
```

Контроль чистого объёма:

```text
edge_and_beam_eps_volume_m3 =
  edge_and_beam_eps_material_area_m2 * eps_thickness_m

bottom_slab_eps_volume_m3 =
  bottom_slab_eps_work_area_m2 * eps_thickness_m

calculated_clean_eps_volume_m3 =
  edge_and_beam_eps_volume_m3 + bottom_slab_eps_volume_m3

eps_volume_delta_m3 =
  calculated_clean_eps_volume_m3 - total_eps_volume_from_spec_m3
```

Если разница больше `0.01 м3`, калькулятор пишет warning. Закупка всё равно считается от `total_eps_volume_from_spec_m3`.

Закупка ЭППС:

```text
required_eps_volume_m3_raw =
  total_eps_volume_from_spec_m3 * eps_waste_coeff

eps_packs_ordered =
  ceil(required_eps_volume_m3_raw / eps_pack_volume_m3)

order_eps_volume_m3_raw =
  eps_packs_ordered * eps_pack_volume_m3
```

Клей-пена:

```text
foam_cans_ordered =
  ceil((edge_and_beam_eps_material_area_m2 + bottom_slab_eps_work_area_m2) / foam_coverage_m2_per_can)
```

## Статусы параметров

DEPRECATED / LEGACY_ONLY:

- hardcoded USV geometry для утепления;
- вычисление наружного торца через размеры конкретного проекта;
- восстановление production-количеств утепления через остаток объёма.

AUTO_PROJECT:

- `insulation.slab_outer_edge_eps_work_length_m`;
- `insulation.slab_edge_eps_material_area_m2`;
- `insulation.bottom_slab_eps_work_area_m2`;
- `insulation.total_eps_volume_from_spec_m3`;
- `beams.items[*].length_m`;
- `beams.items[*].height_m`;
- `beams.items[*].count`.

AUTO_CALCULATED:

- `beams_eps_work_length_m`;
- `beams_eps_material_area_m2`;
- `edge_beam_eps_work_length_m`;
- `edge_and_beam_eps_material_area_m2`;
- `calculated_clean_eps_volume_m3`;
- `eps_volume_delta_m3`;
- `eps_packs_ordered`;
- `order_eps_volume_m3_raw`;
- `foam_cans_ordered`.

DEFAULT_VALUE / MATERIAL_CATALOG:

- `eps_thickness_m = 0.1`;
- `eps_waste_coeff = 1.05`;
- `eps_pack_volume_m3 = 0.2773`.

PRICE_DATABASE:

- `eps_unit_price_per_m3`;
- `foam_unit_price_per_can`.

## Тесты

Создан production-кейс:

```text
experiments/floor_slab_1_calculator/cases/test_floor_slab_1_insulation_spec_quantities
```

Он проверяет:

- `insulation_calc_method = spec_work_quantities`;
- расчёт длины утепления балок из `beams.items`;
- расчёт площади утепления балок из `beams.items`;
- использование `slab_outer_edge_eps_work_length_m` для работ по торцам и балкам;
- использование `slab_edge_eps_material_area_m2` как отдельной площади материала торца;
- использование `bottom_slab_eps_work_area_m2` для работ низа плиты;
- закупку ЭППС от `total_eps_volume_from_spec_m3`;
- округление ЭППС до упаковок;
- расчёт клей-пены от площади материала.

## TODO

- Обновить `section_schema.py`.
- Обновить `reviewed_parameters.xlsx`.
- Научить parser брать блок утепления плиты из спецификации.
- Убрать legacy hardcoded USV geometry из production-flow.
- Позже связать `section_rebar_delivery_weight_kg` и другие section outputs с `box_calculator`.

В этой задаче не менялись `pdf_parser_pipeline`, `input_builder`, `price_registry`, `box_calculator`, плита 2-го этажа и клиентская часть.
