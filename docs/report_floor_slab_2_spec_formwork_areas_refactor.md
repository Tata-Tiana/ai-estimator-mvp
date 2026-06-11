# Отчет: три площади опалубки плиты 2-го этажа из спецификации

Дата: 2026-06-11

Раздел: `Ж/Б монолитная плита перекрытия 2-го этажа`

## Что изменено

Существующий production-режим:

```text
formwork_area_calc_method = "spec_formwork_area"
```

расширен до трех готовых площадей из спецификации:

```text
main_formwork_area_m2
edge_formwork_area_m2
beams_formwork_area_m2
```

Новый отдельный `formwork_areas_calc_method` не добавлялся.

## Production-логика

Главные источники:

- `main_formwork_area_m2` — площадь опалубки под плиту;
- `edge_formwork_area_m2` — площадь торцевой опалубки плиты;
- `beams_formwork_area_m2` — площадь опалубки на балки.

Для текущей плиты 2-го этажа балок нет:

```text
beams_formwork_area_m2 = 0
```

Расчетные значения:

```text
slab_formwork_area_m2 = main_formwork_area_m2
edge_and_beam_formwork_area_m2 = edge_formwork_area_m2 + beams_formwork_area_m2
```

`main_formwork_area_m2` используется для строки `formwork_rental_set`.
`edge_and_beam_formwork_area_m2` используется для:

- контрольной строки `edge_formwork_installation_control`;
- фанеры `plywood_for_edges`;
- пиломатериала `timber_for_formwork`.

## Что осталось контрольным

Старая формула:

```text
calculated_edge_formwork_area_m2 =
  slab_edge_perimeter_m * edge_formwork_height_m
```

оставлена как контроль качества данных, но не является production-источником.

Контрольная дельта:

```text
edge_formwork_area_delta_m2 =
  edge_formwork_area_m2 - calculated_edge_formwork_area_m2
```

Если разница больше `0.01 м2`, калькулятор добавляет warning, но не заменяет значение из спецификации.

## Утепление торца

`slab_edge_perimeter_m` сохраняется как production-параметр, но для другого смысла:

```text
edge_insulation_work.quantity = slab_edge_perimeter_m
```

То есть `slab_edge_perimeter_m` — это длина утепляемого торца в м.п., а не источник площади торцевой опалубки.

## Статусы параметров

AUTO_PROJECT:

- `main_formwork_area_m2`;
- `edge_formwork_area_m2`;
- `beams_formwork_area_m2`;
- `slab_edge_perimeter_m` для утепления торца.

AUTO_CALCULATED:

- `edge_and_beam_formwork_area_m2`;
- `calculated_edge_formwork_area_m2`;
- `edge_formwork_area_delta_m2`;
- `plywood_sheets`;
- `timber_volume_m3_raw`.

OPTIONAL_CONTROL / GEOMETRY_CHECK:

- `slab_length_m`;
- `slab_width_m`;
- `slab_area_m2`;
- `edge_formwork_height_m`.

DEPRECATED / LEGACY_ONLY:

- использование `slab_edge_perimeter_m * edge_formwork_height_m` как обязательного production-источника площади торцевой опалубки;
- использование `slab_length_m * slab_width_m` как обязательного production-источника площади опалубки под плиту.

CONTROL_OR_FALLBACK:

- `calculated_edge_formwork_area_m2`.

## Проверочный кейс

Обновлен кейс:

```text
experiments/floor_slab_2_calculator/cases/test_floor_slab_2_spec_formwork_area/
```

Он проверяет:

- `main_formwork_area_m2 = 81.9`;
- `edge_formwork_area_m2 = 7.24`;
- `beams_formwork_area_m2 = 0`;
- `edge_and_beam_formwork_area_m2 = 7.24`;
- `edge_formwork_installation_control.quantity_raw = 7.24`;
- `plywood_for_edges.quantity_raw = 16`;
- `timber_for_formwork.quantity_raw = 0.362`;
- `edge_insulation_work.quantity_raw = 36.2`.

## TODO

- обновить `section_schema.py`;
- обновить `reviewed_parameters.xlsx`;
- научить parser брать `main_formwork_area_m2` из спецификации;
- научить parser брать `edge_formwork_area_m2` из спецификации;
- научить parser брать `beams_formwork_area_m2` из спецификации;
- научить parser брать `slab_edge_perimeter_m` как длину утепляемого торца;
- позже убрать legacy-расчет площади торцевой опалубки из production-flow.
