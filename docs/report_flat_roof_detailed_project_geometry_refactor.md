# Отчет: production-геометрия плоской кровли из проектных составляющих

Дата: 2026-06-11

## Что изменилось

В калькулятор плоской кровли добавлен режим:

```text
roof_geometry_calc_method = "detailed_project_geometry"
```

Раньше калькулятор использовал готовые totals из input:

- `roof_area_total_m2`;
- `parapet_and_abutment_total_length_m`.

Теперь production-режим считает эти totals из проектных составляющих:

```text
roof_area_total_m2 =
roof_area_level_1_m2 + roof_area_level_2_m2

parapet_and_abutment_total_length_m =
parapet_length_level_1_m
+ parapet_length_level_2_m
+ vent_wall_abutment_level_1_m
+ vent_wall_abutment_level_2_m
```

Для ЮСВ:

```text
177.52 + 71.40 = 248.92 м2
96 + 35.4 + 4.68 + 2.54 = 138.62 м.п.
```

## Статусы параметров

`AUTO_PROJECT`:

- `roof_area_level_1_m2`;
- `roof_area_level_2_m2`;
- `parapet_length_level_1_m`;
- `parapet_length_level_2_m`;
- `vent_wall_abutment_level_1_m`;
- `vent_wall_abutment_level_2_m`.

`AUTO_CALCULATED`:

- `roof_area_total_m2`;
- `parapet_and_abutment_total_length_m`;
- `calculated_roof_area_total_m2`;
- `calculated_parapet_and_abutment_total_length_m`.

`CONTROL_OR_FALLBACK`:

- `input_roof_area_total_m2`;
- `input_parapet_and_abutment_total_length_m`;
- `roof_area_total_delta_m2`;
- `parapet_and_abutment_total_delta_m`.

`DEPRECATED / LEGACY_ONLY`:

- `roof_area_total_m2` как обязательный production input;
- `parapet_and_abutment_total_length_m` как обязательный production input.

## Совместимость

Legacy-режим `legacy_totals` сохранен и остается дефолтом, если `roof_geometry_calc_method` не передан. Старый locked-кейс `test_flat_roof_usv` продолжает брать totals напрямую из input.

В production-режиме, если totals переданы дополнительно, они используются только как контроль. При расхождении больше `0.01` калькулятор добавляет warning, но не заменяет расчетные totals из составляющих.

## Проверки

Добавлен кейс:

```text
experiments/flat_roof_calculator/cases/test_flat_roof_detailed_project_geometry
```

Он работает без входных:

- `roof_area_total_m2`;
- `parapet_and_abutment_total_length_m`.

Ожидаемые totals совпадают со старым ЮСВ-кейсом, поэтому суммы раздела не меняются.

## TODO

- обновить `section_schema.py`;
- обновить `reviewed_parameters.xlsx`;
- научить parser брать площади кровли по уровням из спецификации;
- научить parser брать длины парапетов и примыканий вентстен по уровням;
- оставить `project_spec_roof_area_m2 = 294` отдельным контрольным значением до ручного решения по источнику.
