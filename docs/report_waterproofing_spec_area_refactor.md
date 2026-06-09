# Рефактор площади гидроизоляции фундаментной плиты

Дата: 2026-06-09

## Контекст

После созвона с Еленой уточнён production-стандарт для раздела "Гидроизоляция фундаментной плиты".

В новых проектах площадь гидроизоляции должна приходить готовым значением из спецификации проекта.

По методике Елены:

```text
waterproofing_area_m2 = площадь опалубки фундаментной плиты
```

## Что было

Старая формула:

```text
waterproofing_area_m2 = slab_formwork_perimeter_m * slab_edge_height_m
```

В эталонном кейсе ЮСВ:

```text
81 * 0.3 = 24.3 м2
```

Эта логика оставлена только как legacy для старого кейса.

## Что стало

Добавлен режим:

```text
waterproofing_area_calc_method = spec_area
```

В этом режиме:

```text
waterproofing_area_m2 = готовая площадь из спецификации проекта
```

`waterproofing_area_m2` используется для:

- работы по гидроизоляции битумной мастикой;
- расчёта праймера;
- расчёта мастики.

## ЭППС 100 мм торец

После дополнительного уточнения Елены участки без утепления не нужны для production-расчёта.

Основная площадь работ по ЭППС 100 мм торец считается от объёма ЭППС из спецификации:

```text
eps100_wall_insulation_area_m2 = eps100_wall_volume_m3 / eps100_wall_thickness_m
```

В текущем стандарте:

```text
eps100_wall_thickness_m = 0.1
```

`non_insulated_edge_lengths_m` оставлен только как legacy/geometric check.

## Статус параметров

Production-параметр:

- `waterproofing_area_m2` — `AUTO_PROJECT`, берётся из спецификации проекта.

Legacy-only параметры для расчёта площади гидроизоляции:

- `slab_formwork_perimeter_m`;
- `slab_edge_height_m`.

Они остаются для старого кейса и возможной геометрической проверки/debug, но не должны быть ручными входами Елены для production-гидроизоляции.

Legacy-check параметр для ЭППС:

- `non_insulated_edge_lengths_m` — `DEPRECATED / LEGACY_CHECK_ONLY`.

## Новый test-case

Создан:

```text
experiments/waterproofing_calculator/cases/test_waterproofing_spec_area/
```

Проверяет:

```text
waterproofing_area_calc_method = spec_area
waterproofing_area_m2 = 24.3
primer_required_liters = 7.29
primer_units = 1
mastic_required_kg = 48.6
mastic_units = 3
eps100_wall_insulation_area_m2 = 17.5
eps100_wall_geometry_check_enabled = false
```

## Legacy

Старый кейс:

```text
experiments/waterproofing_calculator/cases/test_waterproofing_foundation_slab/
```

использует:

```text
waterproofing_area_calc_method = legacy_perimeter_height
```

Старый `expected.json` не менялся.

## TODO

- Обновить `section_schema.py`.
- Добавить `waterproofing_area_m2` в `reviewed_parameters.xlsx`.
- Научить parser искать площадь опалубки фундаментной плиты в спецификации.
- Убрать `slab_formwork_perimeter_m` и `slab_edge_height_m` из формы Елены для production-гидроизоляции.
- Показывать Елене `waterproofing_area_m2` как контрольный параметр.
- Убрать `non_insulated_edge_lengths_m` из `reviewed_parameters.xlsx` для production.
- Научить parser брать `eps100_wall_volume_m3` из спецификации.
- Показывать Елене `eps100_wall_volume_m3` и рассчитанную площадь работ по ЭППС как контроль.
