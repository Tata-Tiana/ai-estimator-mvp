# Flat Roof Calculator

Экспериментальный детерминированный калькулятор раздела:

```text
КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА / плоская кровля
```

## Как запустить

```bash
../.venv/bin/python3 experiments/flat_roof_calculator/run_case.py experiments/flat_roof_calculator/cases/test_flat_roof_usv
```

Если локальный Python запускается без venv:

```bash
python3 experiments/flat_roof_calculator/run_case.py experiments/flat_roof_calculator/cases/test_flat_roof_usv
```

## Что создаётся

```text
experiments/flat_roof_calculator/cases/test_flat_roof_usv/result.json
experiments/flat_roof_calculator/cases/test_flat_roof_usv/result.md
```

## Что считается

- только серая внутренняя себестоимость;
- материалы/механизмы;
- работы;
- итог раздела по реализованным строкам;
- raw и display значения отдельно;
- закупочные количества с округлением вверх там, где требуется.

## Что не считается

- клиентская/белая часть;
- коммерческие коэффициенты;
- налоги;
- временная дверь как индивидуальная case-specific строка;
- уклонные плиты по геометрии кровли.

## Ручные параметры

- в legacy-режиме готовые totals кровли требуют проверки человеком;
- объёмы ЭППС 50 мм и SLOPE плит берутся как `supplier_required_volume_m3`;
- расходные материалы временно берутся как предоставленный raw total;
- логистика и снабжение временно берётся как предоставленный raw total;
- технический надзор берётся как предоставленный fixed work total;
- заготовительно-складские расходы берутся как предоставленный fixed work total;
- `roof_work_coeff` является параметром проекта и может меняться.

## Production roof geometry

Для production используется режим:

```text
roof_geometry_calc_method = "detailed_project_geometry"
```

Из проекта/спецификации приходят составляющие:

- `roof_area_level_1_m2`;
- `roof_area_level_2_m2`;
- `parapet_length_level_1_m`;
- `parapet_length_level_2_m`;
- `vent_wall_abutment_level_1_m`;
- `vent_wall_abutment_level_2_m`.

Калькулятор сам считает:

```text
roof_area_total_m2 =
roof_area_level_1_m2 + roof_area_level_2_m2

parapet_and_abutment_total_length_m =
parapet_length_level_1_m
+ parapet_length_level_2_m
+ vent_wall_abutment_level_1_m
+ vent_wall_abutment_level_2_m
```

Статусы параметров:

- `roof_area_level_1_m2`, `roof_area_level_2_m2`, `parapet_length_level_1_m`, `parapet_length_level_2_m`, `vent_wall_abutment_level_1_m`, `vent_wall_abutment_level_2_m` — `AUTO_PROJECT`;
- `roof_area_total_m2`, `parapet_and_abutment_total_length_m`, `calculated_roof_area_total_m2`, `calculated_parapet_and_abutment_total_length_m` — `AUTO_CALCULATED`;
- `input_roof_area_total_m2`, `input_parapet_and_abutment_total_length_m` — `CONTROL_OR_FALLBACK`;
- `roof_area_total_m2` и `parapet_and_abutment_total_length_m` как обязательные production input — `DEPRECATED / LEGACY_ONLY`.

`project_spec_roof_area_m2 = 294` остается отдельным контрольным значением и не используется автоматически без проверки человека.

## price_registry

У материальных строк есть `price_code`. Сейчас цены берутся из `input.json`.
Позже `price_code` можно связать с Google Sheets `price_registry`, не меняя смысловые формулы.

## Почему SLOPE плиты не считаются автоматически

Уклонные плиты зависят от схемы водоразделов, воронок, уклонов и раскладки производителя.
Для текущего MVP объёмы от поставщика фиксируются как ручной вход, чтобы не имитировать точность, которой пока нет.
