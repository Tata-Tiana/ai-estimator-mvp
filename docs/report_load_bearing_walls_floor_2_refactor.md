# Отчёт: блок несущих стен 2-го этажа вместо legacy second_light

Дата: 2026-06-10

## Что было

В старом ЮСВ-кейсе использовались поля:

- `second_light_masonry_enabled`;
- `second_light_masonry_case_specific`;
- `second_light_masonry_volume_m3`.

Фактически этот блок использовался как кладка верхнего уровня / 2-го этажа, но название `second_light` было case-specific и не подходит для production.

## Что стало

Production поддерживает только:

- `floors_count = 1`;
- `floors_count = 2`.

`floors_count = 3` запрещён validation:

```text
floors_count must be 1 or 2. Three-storey houses are out of MVP scope.
```

Для production добавлен режим:

```text
upper_floor_calc_method = floor_2_spec_volume
```

Логика:

```text
if floors_count == 1:
    floor_2_load_bearing_walls_enabled = false

if floors_count == 2:
    floor_2_load_bearing_walls_enabled = true
```

Объём кладки 2-го этажа берётся из спецификации:

```text
floor_2_masonry_volume_m3
```

## Парапет

Старое поле `parapet_enabled` оставлено для legacy.

Production-режим:

```text
parapet_calc_method = flat_roof_spec_volume
parapet_enabled_calculated = flat_roof_enabled and parapet_masonry_volume_m3 > 0
```

`parapet_masonry_volume_m3` является проектным параметром из спецификации кровли.

## Вентканалы

Старое поле `vent_chimney_cladding_enabled` оставлено для legacy.

Production-режим:

```text
vent_chimney_cladding_calc_method = flat_roof_spec_volume
vent_chimney_cladding_enabled_calculated = flat_roof_enabled and vent_chimney_gas_block_spec_volume_m3 > 0
```

`vent_chimney_gas_block_spec_volume_m3` является проектным параметром из спецификации вентканалов.

## Статусы параметров

| parameter | status | source_of_truth | comment |
| --- | --- | --- | --- |
| `floors_count` | AUTO_PROJECT | проект / спецификация | Только 1 или 2. |
| `floor_2_masonry_volume_m3` | AUTO_PROJECT | спецификация кладки 2-го этажа | Используется только при `floors_count = 2`. |
| `second_light_*` | DEPRECATED / LEGACY_ONLY | старый ЮСВ-кейс | В production не использовать. |
| `parapet_enabled` | DEPRECATED / LEGACY_ONLY | старый ЮСВ-кейс | В production считается автоматически. |
| `parapet_masonry_volume_m3` | AUTO_PROJECT | спецификация кровли / парапет | Включает production-парапет. |
| `vent_chimney_cladding_enabled` | DEPRECATED / LEGACY_ONLY | старый ЮСВ-кейс | В production считается автоматически. |
| `vent_chimney_gas_block_spec_volume_m3` | AUTO_PROJECT | спецификация вентканалов | Включает production-обкладку вентканалов. |

## Проверочные кейсы

- `test_floor_1_without_floor_2`: 1 этаж, блок 2-го этажа выключен.
- `test_floor_2_load_bearing_walls_spec_volume`: 2 этажа, блок 2-го этажа включён от `floor_2_masonry_volume_m3`.
- `test_flat_roof_parapet_vent_channels`: flat roof включает парапет и обкладку вентканалов от проектных объёмов.
- `test_floors_count_three_rejected`: validation запрещает 3 этажа.

## TODO

- Обновить `section_schema.py`.
- Обновить `reviewed_parameters.xlsx`.
- Научить parser брать `floor_2_masonry_volume_m3` из спецификации кладки 2-го этажа.
- Научить parser брать `parapet_masonry_volume_m3` из спецификации кровли.
- Научить parser брать `vent_chimney_gas_block_spec_volume_m3` из спецификации вентканалов.
- На этапе `box_calculator` сделать общий переключатель разделов: foundation, walls_floor_1, walls_floor_2, slabs, roof, vents.
