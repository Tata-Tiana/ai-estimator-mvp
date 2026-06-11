# Отчет: перевод площади опалубки плиты 2-го этажа на спецификацию

Дата: 2026-06-10

Раздел: `Ж/Б монолитная плита перекрытия 2-го этажа`

## Что изменено

Добавлен режим расчета источника площади опалубки:

```text
formwork_area_calc_method =
  legacy_dimensions
  spec_formwork_area
```

В production-режиме `spec_formwork_area` главным источником количества для строки
`formwork_rental_set` становится `main_formwork_area_m2` из спецификации проекта.

## Было

В старой ЮСВ-логике геометрия была обязательной:

```text
slab_area_m2 = slab_length_m * slab_width_m
slab_edge_perimeter_m = 2 * (slab_length_m + slab_width_m)
main_formwork_area_m2 = slab_area_m2
```

Для эталонного кейса:

```text
9 * 9.1 = 81.9 м2
2 * (9 + 9.1) = 36.2 м.п.
81.9 * 850 = 69615
```

## Стало

Production-калькулятор не обязан знать длину и ширину плиты для расчета комплекта опалубки.
Он берет:

```text
main_formwork_area_m2
```

как готовую площадь опалубки из спецификации.

Для утепления торца плиты отдельно используется:

```text
slab_edge_perimeter_m
```

Это проектная длина утепляемого торца, а не обязательная формула прямоугольного периметра. Фактическая
утепляемая длина может отличаться от `2 * (slab_length_m + slab_width_m)`.

## Статусы параметров

AUTO_PROJECT:

- `main_formwork_area_m2`;
- `slab_edge_perimeter_m`.

OPTIONAL_CONTROL / GEOMETRY_CHECK:

- `slab_length_m`;
- `slab_width_m`;
- `slab_area_m2`.

AUTO_CALCULATED:

- `calculated_slab_area_m2`;
- `calculated_slab_edge_perimeter_m`;
- `area_delta_m2`;
- `formwork_area_delta_m2`.

DEPRECATED / LEGACY_ONLY:

- использование `slab_length_m * slab_width_m` как обязательного источника площади опалубки;
- использование `2 * (slab_length_m + slab_width_m)` как обязательного источника утепляемого периметра.

PRICE_DATABASE / MANUAL_RATE:

- `formwork_rental_used_rate_per_m2`.

## Legacy

Старый кейс `test_floor_slab_2` переведен в:

```text
formwork_area_calc_method = "legacy_dimensions"
```

Его `expected.json` не менялся.

## Новый тест

Создан кейс:

```text
experiments/floor_slab_2_calculator/cases/test_floor_slab_2_spec_formwork_area/
```

Он работает без `slab_length_m` и `slab_width_m` и проверяет:

- `main_formwork_area_m2 = 81.9`;
- `slab_edge_perimeter_m = 36.2`;
- `formwork_rental_set.quantity_raw = 81.9`;
- `formwork_rental_set.material_total = 69615`;
- `edge_insulation_work.quantity_raw = 36.2`.

## TODO

- обновить `section_schema.py`;
- обновить `reviewed_parameters.xlsx`;
- научить parser брать `main_formwork_area_m2` из спецификации;
- научить parser брать `slab_edge_perimeter_m` из спецификации;
- позже убрать `legacy_dimensions` из production-flow.
