# Missing parameters report

## Project

- project_name: ЮСВ demo
- reviewed_parameters_path: experiments/pdf_parser_pipeline/output/mvp_usv_demo/reviewed_parameters.xlsx
- builder_mode: demo_with_template_fallback

## Blocked sections

| section_code | section_name | missing required count | manual_required count | can_generate_input |
|---|---|---:|---:|---|
| earthworks | Земляные работы | 0 | 0 | yes |
| foundation_slab | Фундаментная плита | 0 | 0 | yes |
| waterproofing | Гидроизоляция | 0 | 0 | yes |
| load_bearing_walls_lintels | Несущие стены и перемычки | 0 | 0 | yes |
| floor_slab_1 | Плита перекрытия 1-го этажа | 0 | 0 | yes |
| floor_slab_2 | Плита перекрытия 2-го этажа | 0 | 0 | yes |
| flat_roof | Плоская кровля | 0 | 0 | yes |
| schiedel_vent_channels | Вентиляционные каналы Schiedel | 0 | 0 | yes |

## Missing parameters

| section_code | parameter_code | calculator_input_key | label | input_type | unit | elena_status | reason |
|---|---|---|---|---|---|---|---|

## Needs review warnings

| section_code | parameter_code | label | effective_value | source_file | page | warning |
|---|---|---|---|---|---|---|
| earthworks | sand_volume | Песок | 96.6 | ЮСВ КР1.pdf | 8 | needs_review value used; Elena has not confirmed this parameter |
| earthworks | geotextile_area | Геотекстиль | 320 | ЮСВ КР1.pdf | 8 | needs_review value used; Elena has not confirmed this parameter |
| foundation_slab | concrete_project_volume | Проектный объем бетона фундаментной плиты | 81 | ЮСВ КР1.pdf | 9 | needs_review value used; Elena has not confirmed this parameter |
| foundation_slab | eps_50_under_slab_volume | ЭППС 50 мм, низ плиты | 13.5 | ЮСВ КР1.pdf | 9 | needs_review value used; Elena has not confirmed this parameter |
| foundation_slab | rebar_a500c_d12_main_grid_weight | Арматура A500C d12, сетка фундаментной плиты | 5276 | ЮСВ КР1.pdf | 9 | needs_review value used; Elena has not confirmed this parameter |
| foundation_slab | rebar_a500c_d12_thermal_insert_weight | Арматура A500C d12, сетка термовставок | 122 | ЮСВ КР1.pdf | 10 | needs_review value used; Elena has not confirmed this parameter |
| foundation_slab | rebar_a500c_d10_weight | Арматура A500C d10 | 1078 | ЮСВ КР1.pdf | 9 | needs_review value used; Elena has not confirmed this parameter |
| foundation_slab | rebar_a500c_d16_thermal_insert_weight | Арматура A500C d16 для термовставок | 328 | ЮСВ КР1.pdf | 10 | needs_review value used; Elena has not confirmed this parameter |
| foundation_slab | rebar_a240_d6_thermal_insert_weight | Арматура A240 d6 для термовставок | 35 | ЮСВ КР1.pdf | 10 | needs_review value used; Elena has not confirmed this parameter |
| foundation_slab | sand_volume | Песок | 96.6 | ЮСВ КР1.pdf | 8 | needs_review value used; Elena has not confirmed this parameter |
| foundation_slab | geotextile_area | Геотекстиль | 320 | ЮСВ КР1.pdf | 8 | needs_review value used; Elena has not confirmed this parameter |
| foundation_slab | planter_membrane_area | Профилированная мембрана PLANTER | 320 | ЮСВ КР1.pdf | 8 | needs_review value used; Elena has not confirmed this parameter |
| waterproofing | eps_100_edge_volume | ЭППС 100 мм, торец/вертикальное утепление | 1.75 | ЮСВ КР1.pdf | 9 | needs_review value used; Elena has not confirmed this parameter |
| load_bearing_walls_lintels | gas_block_d400_volume | Газобетонный блок 600х400х250 | 78.95 | ЮСВ КР2.pdf | 13 | needs_review value used; Elena has not confirmed this parameter |
| load_bearing_walls_lintels | gas_block_d500_250_volume | Газобетонный блок 600х250х250 | 30.4 | ЮСВ КР2.pdf | 13 | needs_review value used; Elena has not confirmed this parameter |
| load_bearing_walls_lintels | masonry_rebar_a500_d10_weight | Арматура ф10 А500С для кладки | 880 | ЮСВ КР2.pdf | 13 | needs_review value used; Elena has not confirmed this parameter |
| load_bearing_walls_lintels | lintel_concrete_volume | Бетон перемычек | 0.24 | ЮСВ КР2.pdf | 15 | needs_review value used; Elena has not confirmed this parameter |
| load_bearing_walls_lintels | lintel_rebar_a500_d12_weight | Арматура ф12 А500С для перемычек | 103 | ЮСВ КР2.pdf | 15 | needs_review value used; Elena has not confirmed this parameter |
| load_bearing_walls_lintels | lintel_rebar_a240_d6_weight | Арматура ф6 А240 для перемычек | 20.4 | ЮСВ КР2.pdf | 15 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_1 | floor_slab_1_concrete_volume | Бетон плиты перекрытия +3.480 | 40.53 | ЮСВ КР2.pdf | 21 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_1 | floor_slab_1_eps100_volume | ЭППС 100 мм торец и низ плиты | 7.77 | ЮСВ КР2.pdf | 21 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_1 | floor_slab_1_rebar_a500_d10_weight | Арматура ф10 А500С | 3900 | ЮСВ КР2.pdf | 21 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_1 | floor_slab_1_rebar_a500_d12_weight | Арматура ф12 А500С | 42 | ЮСВ КР2.pdf | 21 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_1 | floor_slab_1_rebar_a500_d25_weight | Арматура ф25 А500С | 162 | ЮСВ КР2.pdf | 21 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_1 | floor_slab_1_rebar_a500_d16_weight | Арматура ф16 А500С | 52.04 | ЮСВ КР2.pdf | 21 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_1 | floor_slab_1_rebar_a240_d6_weight | Арматура ф6 А240 | 15 | ЮСВ КР2.pdf | 21 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_1 | floor_slab_1_rebar_a240_d8_weight | Арматура ф8 А240 | 17 | ЮСВ КР2.pdf | 21 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_2 | floor_slab_2_concrete_volume | Бетон плиты перекрытия +3.680/+4.680 | 16.5 | ЮСВ КР2.pdf | 24 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_2 | floor_slab_2_rebar_a500_d10_weight_main | Арматура ф10 А500С, основная | 1500 | ЮСВ КР2.pdf | 24 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_2 | floor_slab_2_rebar_a500_d10_weight_extra_1 | Арматура ф10 А500С, доп. лист 25 | 42.57 | ЮСВ КР2.pdf | 25 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_2 | floor_slab_2_rebar_a500_d10_weight_extra_2 | Арматура ф10 А500С, доп. лист 26 | 35.1 | ЮСВ КР2.pdf | 26 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_2 | floor_slab_2_rebar_a500_d12_weight | Арматура ф12 А500С | 22 | ЮСВ КР2.pdf | 24 | needs_review value used; Elena has not confirmed this parameter |
| floor_slab_2 | floor_slab_2_rebar_a500_d16_weight | Арматура ф16 А500С | 142.4 | ЮСВ КР2.pdf | 26 | needs_review value used; Elena has not confirmed this parameter |
| flat_roof | roof_internal_drains_count | Воронки внутреннего водостока | 3 | ЮСВ КР2.pdf | 28 | needs_review value used; Elena has not confirmed this parameter |
| flat_roof | roof_parapet_drains_count | Парапетные воронки | 2 | ЮСВ КР2.pdf | 28 | needs_review value used; Elena has not confirmed this parameter |
| schiedel_vent_channels | schiedel_vent_channel_2x_count | Вентиляционный канал Schiedel VENT 2 | 24 | ЮСВ КР2.pdf | 31 | needs_review value used; Elena has not confirmed this parameter |
| schiedel_vent_channels | schiedel_vent_channel_3x_count | Вентиляционный канал Schiedel VENT 3 | 8 | ЮСВ КР2.pdf | 31 | needs_review value used; Elena has not confirmed this parameter |
