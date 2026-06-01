# Input builder result

## Что сделано

- Прочитан `reviewed_parameters.xlsx`.
- Собраны `input.json` для разделов, где хватает обязательных данных.
- Сформирован `missing_parameters_report.md`.

## Сводка по разделам

| Раздел | Статус | Параметров использовано | Missing | Manual required | Needs review | Generated input |
|---|---|---:|---:|---:|---:|---|
| Земляные работы | blocked_missing_required_params | 16 | 13 | 7 | 2 |  |
| Фундаментная плита | blocked_missing_required_params | 54 | 41 | 6 | 10 |  |
| Гидроизоляция | blocked_missing_required_params | 14 | 10 | 3 | 1 |  |
| Несущие стены и перемычки | blocked_missing_required_params | 51 | 89 | 21 | 6 |  |
| Плита перекрытия 1-го этажа | blocked_missing_required_params | 58 | 66 | 15 | 8 |  |
| Плита перекрытия 2-го этажа | blocked_missing_required_params | 38 | 29 | 8 | 6 |  |
| Плоская кровля | blocked_missing_required_params | 45 | 33 | 6 | 2 |  |
| Вентиляционные каналы Schiedel | blocked_missing_required_params | 7 | 6 | 3 | 2 |  |

## Что делать Елене

Если раздел `blocked_missing_required_params`:

- открыть `reviewed_parameters.xlsx`;
- заполнить `corrected_value`;
- поставить `elena_status = manual / reviewed / corrected`;
- повторно запустить `input_builder`.

## Warnings

- earthworks:sand_volume: needs_review value used; Elena has not confirmed this parameter
- earthworks:geotextile_area: needs_review value used; Elena has not confirmed this parameter
- foundation_slab:concrete_project_volume: needs_review value used; Elena has not confirmed this parameter
- foundation_slab:eps_50_under_slab_volume: needs_review value used; Elena has not confirmed this parameter
- foundation_slab:rebar_a500c_d12_main_grid_weight: needs_review value used; Elena has not confirmed this parameter
- foundation_slab:rebar_a500c_d12_thermal_insert_weight: needs_review value used; Elena has not confirmed this parameter
- foundation_slab:rebar_a500c_d10_weight: needs_review value used; Elena has not confirmed this parameter
- foundation_slab:rebar_a500c_d16_thermal_insert_weight: needs_review value used; Elena has not confirmed this parameter
- foundation_slab:rebar_a240_d6_thermal_insert_weight: needs_review value used; Elena has not confirmed this parameter
- foundation_slab:sand_volume: needs_review value used; Elena has not confirmed this parameter
- foundation_slab:geotextile_area: needs_review value used; Elena has not confirmed this parameter
- foundation_slab:planter_membrane_area: needs_review value used; Elena has not confirmed this parameter
- waterproofing:eps_100_edge_volume: needs_review value used; Elena has not confirmed this parameter
- load_bearing_walls_lintels:gas_block_d400_volume: needs_review value used; Elena has not confirmed this parameter
- load_bearing_walls_lintels:gas_block_d500_250_volume: needs_review value used; Elena has not confirmed this parameter
- load_bearing_walls_lintels:masonry_rebar_a500_d10_weight: needs_review value used; Elena has not confirmed this parameter
- load_bearing_walls_lintels:lintel_concrete_volume: needs_review value used; Elena has not confirmed this parameter
- load_bearing_walls_lintels:lintel_rebar_a500_d12_weight: needs_review value used; Elena has not confirmed this parameter
- load_bearing_walls_lintels:lintel_rebar_a240_d6_weight: needs_review value used; Elena has not confirmed this parameter
- floor_slab_1:floor_slab_1_concrete_volume: needs_review value used; Elena has not confirmed this parameter
- floor_slab_1:floor_slab_1_eps100_volume: needs_review value used; Elena has not confirmed this parameter
- floor_slab_1:floor_slab_1_rebar_a500_d10_weight: needs_review value used; Elena has not confirmed this parameter
- floor_slab_1:floor_slab_1_rebar_a500_d12_weight: needs_review value used; Elena has not confirmed this parameter
- floor_slab_1:floor_slab_1_rebar_a500_d25_weight: needs_review value used; Elena has not confirmed this parameter
- floor_slab_1:floor_slab_1_rebar_a500_d16_weight: needs_review value used; Elena has not confirmed this parameter
- floor_slab_1:floor_slab_1_rebar_a240_d6_weight: needs_review value used; Elena has not confirmed this parameter
- floor_slab_1:floor_slab_1_rebar_a240_d8_weight: needs_review value used; Elena has not confirmed this parameter
- floor_slab_2:floor_slab_2_concrete_volume: needs_review value used; Elena has not confirmed this parameter
- floor_slab_2:floor_slab_2_rebar_a500_d10_weight_main: needs_review value used; Elena has not confirmed this parameter
- floor_slab_2:floor_slab_2_rebar_a500_d10_weight_extra_1: needs_review value used; Elena has not confirmed this parameter
- floor_slab_2:floor_slab_2_rebar_a500_d10_weight_extra_2: needs_review value used; Elena has not confirmed this parameter
- floor_slab_2:floor_slab_2_rebar_a500_d12_weight: needs_review value used; Elena has not confirmed this parameter
- floor_slab_2:floor_slab_2_rebar_a500_d16_weight: needs_review value used; Elena has not confirmed this parameter
- flat_roof:roof_internal_drains_count: needs_review value used; Elena has not confirmed this parameter
- flat_roof:roof_parapet_drains_count: needs_review value used; Elena has not confirmed this parameter
- schiedel_vent_channels:schiedel_vent_channel_2x_count: needs_review value used; Elena has not confirmed this parameter
- schiedel_vent_channels:schiedel_vent_channel_3x_count: needs_review value used; Elena has not confirmed this parameter
