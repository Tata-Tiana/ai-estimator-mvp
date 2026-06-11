# Отчет: перевод площадей опалубки плиты 1-го этажа на спецификацию

Дата: 2026-06-11

Раздел: `Ж/Б монолитная плита перекрытия 1-го этажа с балками`

## Что изменено

Добавлен режим источника площадей опалубки:

```text
formwork_areas_calc_method =
  legacy_calculated_from_geometry
  spec_formwork_areas
```

В production-режиме `spec_formwork_areas` калькулятор использует три готовые площади из
спецификации как главный источник расчета.

## Production-входы

AUTO_PROJECT:

- `main_formwork_area_m2` — площадь опалубки под плиту;
- `edge_formwork_area_m2` — площадь торцевой опалубки плиты;
- `beams_formwork_area_m2` — площадь опалубки на балки.

Production-формулы:

```text
slab_formwork_area_m2 = main_formwork_area_m2
edge_and_beam_formwork_area_m2 = edge_formwork_area_m2 + beams_formwork_area_m2
```

## Какие строки используют эти площади

`main_formwork_area_m2`:

- `slab_formwork_installation_control`;
- `formwork_set_rental_material`;
- `formwork_consumables`;
- `formwork_dismantling_zero_internal`;
- расчет доставки/вывоза опалубки по порогу площади.

`edge_formwork_area_m2 + beams_formwork_area_m2`:

- `edge_beam_formwork_installation_control`;
- расчет фанеры для торцов/балок;
- базовый объем пиломатериала для опалубки.

## Контрольные расчеты

Старые формулы сохранены только как control/fallback:

```text
calculated_main_formwork_area_m2 =
  (total_concrete_volume_from_spec_m3 - calculated_beams_concrete_volume_m3) / slab_thickness_m

calculated_edge_formwork_area_m2 =
  slab_edge_perimeter_m * edge_formwork_height_m

calculated_beams_formwork_area_m2 =
  sum(beam.length_m * (beam.width_m + 2 * beam.height_m) * beam.count)
```

AUTO_CALCULATED:

- `edge_and_beam_formwork_area_m2`;
- `calculated_main_formwork_area_m2`;
- `calculated_edge_formwork_area_m2`;
- `calculated_beams_formwork_area_m2`;
- `main_formwork_area_delta_m2`;
- `edge_formwork_area_delta_m2`;
- `beams_formwork_area_delta_m2`.

Если delta больше `0.01 м2`, калькулятор добавляет warning:

```text
Spec formwork area differs from calculated control area
```

Расчет при этом не падает, потому что контроль нужен только для качества данных.

## Legacy

DEPRECATED / LEGACY_ONLY:

- использование формулы через объем бетона как обязательного production-источника основной площади опалубки;
- использование `slab_edge_perimeter_m * edge_formwork_height_m` как обязательного production-источника площади торца;
- использование `beams.items` как обязательного production-источника площади опалубки балок.

Старый locked-кейс `test_floor_slab_1` использует:

```text
formwork_areas_calc_method = "legacy_calculated_from_geometry"
```

Его `expected.json` не менялся.

## Новый тест

Создан кейс:

```text
experiments/floor_slab_1_calculator/cases/test_floor_slab_1_spec_formwork_areas/
```

Проверяет:

- `main_formwork_area_m2 = 207.64`;
- `edge_formwork_area_m2 = 23.6`;
- `beams_formwork_area_m2 = 27.992`;
- `edge_and_beam_formwork_area_m2 = 51.592`;
- строка `formwork_set_rental_material` берет quantity `207.64`;
- фанера, пиломатериал и контроль торцов/балок используют `51.592`.

## TODO

- обновить `section_schema.py`;
- обновить `reviewed_parameters.xlsx`;
- научить parser брать три площади опалубки плиты 1-го этажа из спецификации;
- убрать обязательность расчетных geometry-полей как production-источников опалубки;
- оставить расчет через бетон/периметр/балки только как контроль качества данных.
