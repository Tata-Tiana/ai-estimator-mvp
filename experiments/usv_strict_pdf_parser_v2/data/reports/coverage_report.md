# Coverage Report: USV Strict PDF Parser v2

## Статистика честности данных

- strict_parse_mode: true
- production values from PDF: 30
- production values from curated/expected: 0
- all found values have evidence: true

## Coverage по разделам

| section | targets | found_from_pdf | true_missing_in_project | low_confidence | mapping_gap | supplier_required | manual_required |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Земляные работы | 4 | 3 | 0 | 0 | 1 | 0 | 0 |
| Фундаментная плита | 8 | 8 | 0 | 0 | 0 | 0 | 0 |
| Гидроизоляция | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| Несущие стены и перемычки | 4 | 2 | 0 | 0 | 2 | 0 | 0 |
| Плита перекрытия 1-го этажа | 7 | 3 | 0 | 0 | 4 | 0 | 0 |
| Плита перекрытия 2-го этажа | 4 | 3 | 0 | 0 | 1 | 0 | 0 |
| Плоская кровля | 8 | 6 | 0 | 0 | 0 | 2 | 0 |
| Вентиляционные каналы Schiedel | 4 | 3 | 0 | 0 | 1 | 0 | 0 |

## Реально найдено в PDF

- Земляные работы :: `pit_area_m2` — Площадь котлована = 322.5 м2 (usv_2026_kr1.pdf p.8, cand_7af1030010ecdf13)
- Земляные работы :: `geotextile_laying_area_m2` — Площадь геотекстиля = 320.0 м2 (usv_2026_kr1.pdf p.8, cand_48d2b568e82d44fd)
- Земляные работы :: `sand_volume_m3` — Объем песка = 0.0 м3 (usv_2026_kr1.pdf p.8, cand_5ed7c5ea9db46dac)
- Фундаментная плита :: `concrete_volume_m3` — Бетон фундаментной плиты = 81.0 м3 (usv_2026_kr1.pdf p.10, cand_461df28e211f264e)
- Фундаментная плита :: `eps100_edge_volume_m3` — ЭППС 100 мм торец фундаментной плиты = 1.75 м3 (usv_2026_kr1.pdf p.10, cand_6ceea865ff7df50b)
- Фундаментная плита :: `eps50_bottom_volume_m3` — ЭППС 50 мм низ фундаментной плиты = 13.5 м3 (usv_2026_kr1.pdf p.10, cand_16ba6b5300fe087c)
- Фундаментная плита :: `slab_side_formwork_area_m2` — Площадь боковой опалубки фундаментной плиты = 23.58 м2 (usv_2026_kr1.pdf p.10, cand_9a1d93b3e955cfc6)
- Фундаментная плита :: `edge_insulation_area_m2` — Площадь утепления торцов фундаментной плиты = 17.5 м2 (usv_2026_kr1.pdf p.10, cand_aec14e56b33d1cfb)
- Фундаментная плита :: `thermal_insert_100_material_spec_qty` — ЭППС 100 мм термовставки = 0.4 м3 (usv_2026_kr1.pdf p.11, cand_e2dc17c7f84f6fc1)
- Фундаментная плита :: `thermal_insert_50_material_spec_qty` — ЭППС 50 мм термовставки = 0.2 м3 (usv_2026_kr1.pdf p.11, cand_cd213b03e0539a0b)
- Фундаментная плита :: `thermal_insert_length_m` — Длина термовставок = 22.0 м/п (usv_2026_kr1.pdf p.11, cand_fc9e99bfd6096004)
- Гидроизоляция :: `cutoff_waterproofing_load_bearing_walls_area_m2` — Отсечная гидроизоляция несущих стен = 39.555 м2 (usv_2026_kr2.pdf p.6, cand_f45d94f3c30dad44)
- Гидроизоляция :: `cutoff_waterproofing_partitions_area_m2` — Отсечная гидроизоляция перегородок = 5.04 м2 (usv_2026_kr2.pdf p.6, cand_44cb0560984e6720)
- Несущие стены и перемычки :: `lintel_total_length_m` — Длина перемычек в U-блоках = 21.5 м/п (usv_2026_kr2.pdf p.16, cand_bc0b01b9b3f69051)
- Несущие стены и перемычки :: `lintel_concrete_spec_volume_m3` — Бетон перемычек = 0.24 м3 (usv_2026_kr2.pdf p.16, cand_6cc10ce75c05a024)
- Плита перекрытия 1-го этажа :: `slab_concrete_volume_m3` — Бетон плиты +3.480 = 38.22 м3 (usv_2026_kr2.pdf p.22, cand_6e2e21024c8cabb4)
- Плита перекрытия 1-го этажа :: `beams_concrete_volume_m3` — Бетон балок +3.480 = 2.63 м3 (usv_2026_kr2.pdf p.22, cand_819f8a8d8b16a4ef)
- Плита перекрытия 1-го этажа :: `slab_edge_eps_material_area_m2` — Площадь утепления торца плиты = 26.6 м2 (usv_2026_kr2.pdf p.22, cand_e21b91a9d90b12da)
- Плита перекрытия 2-го этажа :: `slab_concrete_volume_m3` — Бетон плиты +4.680 = 16.5 м3 (usv_2026_kr2.pdf p.25, cand_04ca4cacc43f4a7e)
- Плита перекрытия 2-го этажа :: `main_formwork_area_m2` — Площадь опалубки плиты 2-го этажа = 212.35 м2 (usv_2026_kr2.pdf p.25, cand_2dd61f7523eb144f)
- Плита перекрытия 2-го этажа :: `edge_insulation_area_m2` — Площадь утепления торца плиты 2-го этажа = 7.4 м2 (usv_2026_kr2.pdf p.25, cand_b987426311c91bd2)
- Плоская кровля :: `roof_area_level_1_m2` — Площадь кровли уровня +3.480 = 212.35 м2 (usv_2026_kr2.pdf p.29, cand_d8c6f30e9fd4c9ac)
- Плоская кровля :: `roof_area_level_2_m2` — Площадь кровли уровня +4.680 = 82.0 м2 (usv_2026_kr2.pdf p.29, cand_770a10c0c43d6cb7)
- Плоская кровля :: `parapet_abutment_length_m` — Длина примыкания к парапетам = 103.35 м/п (usv_2026_kr2.pdf p.29, cand_64f2ad208b70db8a)
- Плоская кровля :: `wall_abutment_length_m` — Длина примыкания к стенам = 24.65 м/п (usv_2026_kr2.pdf p.29, cand_e430211ef0afd7eb)
- Плоская кровля :: `internal_roof_drains_count` — Внутренние воронки = 3.0 шт (usv_2026_kr2.pdf p.29, cand_9206cf52f62fd51e)
- Плоская кровля :: `parapet_roof_drains_count` — Парапетные воронки = 2.0 шт (usv_2026_kr2.pdf p.29, cand_5e77a9f37da8b76a)
- Вентиляционные каналы Schiedel :: `schiedel_vent_2_count` — Schiedel VENT 2 = 24.0 шт (usv_2026_kr2.pdf p.32, cand_d711621842ae0fe9)
- Вентиляционные каналы Schiedel :: `schiedel_vent_3_count` — Schiedel VENT 3 = 8.0 шт (usv_2026_kr2.pdf p.32, cand_f2ab4e234df3c938)
- Вентиляционные каналы Schiedel :: `schiedel_masonry_total_length_m` — Общая длина кладки вентканалов = 6.52 м/п (usv_2026_kr2.pdf p.32, cand_5ccced5a6ae6e071)

## Реально не найдено в проекте

- Нет.

## Проблемы mapping

- Земляные работы :: `trench_routes` — Таблица траншей = 0.0 м3 (usv_2026_kr1.pdf p.8, cand_5ed7c5ea9db46dac)
- Несущие стены и перемычки :: `vent_chimney_gas_block_spec_volume_m3` — Газоблок для обкладки вентканалов = 1.72 м3 (usv_2026_kr2.pdf p.32, cand_cb871e733dc6fb9c)
- Несущие стены и перемычки :: `floor_2_masonry_volume_m3` — Объем кладки несущих стен 2-го этажа = 39.555 м2 (usv_2026_kr2.pdf p.6, cand_f45d94f3c30dad44)
- Плита перекрытия 1-го этажа :: `main_formwork_area_m2` — Площадь опалубки под плиту 1-го этажа = 23.58 м2 (usv_2026_kr1.pdf p.10, cand_9a1d93b3e955cfc6)
- Плита перекрытия 1-го этажа :: `edge_formwork_area_m2` — Площадь торцевой опалубки плиты 1-го этажа = 23.58 м2 (usv_2026_kr1.pdf p.10, cand_9a1d93b3e955cfc6)
- Плита перекрытия 1-го этажа :: `beams_formwork_area_m2` — Площадь опалубки балок = 23.58 м2 (usv_2026_kr1.pdf p.10, cand_9a1d93b3e955cfc6)
- Плита перекрытия 1-го этажа :: `bottom_slab_eps_work_area_m2` — Площадь утепления низа плиты = 50.4 м3 (usv_2026_kr2.pdf p.22, cand_aadd38fe102a69d1)
- Плита перекрытия 2-го этажа :: `edge_formwork_area_m2` — Площадь торцевой опалубки плиты 2-го этажа = 7.4 м2 (usv_2026_kr2.pdf p.25, cand_b987426311c91bd2)
- Вентиляционные каналы Schiedel :: `vent_chimney_gas_block_spec_volume_m3` — Газоблок обкладки вентканалов = 16.81 м3 (usv_2026_kr2.pdf p.15, cand_34d7cb3ae1aee64a)

## Low Confidence

- Нет.

## Данные для Елены

- Нет.

## Данные для проектировщика

- Земляные работы :: `trench_routes` — Таблица траншей = 0.0 м3 (usv_2026_kr1.pdf p.8, cand_5ed7c5ea9db46dac)
- Несущие стены и перемычки :: `vent_chimney_gas_block_spec_volume_m3` — Газоблок для обкладки вентканалов = 1.72 м3 (usv_2026_kr2.pdf p.32, cand_cb871e733dc6fb9c)
- Несущие стены и перемычки :: `floor_2_masonry_volume_m3` — Объем кладки несущих стен 2-го этажа = 39.555 м2 (usv_2026_kr2.pdf p.6, cand_f45d94f3c30dad44)
- Плита перекрытия 1-го этажа :: `main_formwork_area_m2` — Площадь опалубки под плиту 1-го этажа = 23.58 м2 (usv_2026_kr1.pdf p.10, cand_9a1d93b3e955cfc6)
- Плита перекрытия 1-го этажа :: `edge_formwork_area_m2` — Площадь торцевой опалубки плиты 1-го этажа = 23.58 м2 (usv_2026_kr1.pdf p.10, cand_9a1d93b3e955cfc6)
- Плита перекрытия 1-го этажа :: `beams_formwork_area_m2` — Площадь опалубки балок = 23.58 м2 (usv_2026_kr1.pdf p.10, cand_9a1d93b3e955cfc6)
- Плита перекрытия 1-го этажа :: `bottom_slab_eps_work_area_m2` — Площадь утепления низа плиты = 50.4 м3 (usv_2026_kr2.pdf p.22, cand_aadd38fe102a69d1)
- Плита перекрытия 2-го этажа :: `edge_formwork_area_m2` — Площадь торцевой опалубки плиты 2-го этажа = 7.4 м2 (usv_2026_kr2.pdf p.25, cand_b987426311c91bd2)
- Вентиляционные каналы Schiedel :: `vent_chimney_gas_block_spec_volume_m3` — Газоблок обкладки вентканалов = 16.81 м3 (usv_2026_kr2.pdf p.15, cand_34d7cb3ae1aee64a)

## Данные для поставщика

- Плоская кровля :: `eps50_supplier_required_volume_m3` — ЭППС кровли по раскладке поставщика = 58.8 м3 (usv_2026_kr2.pdf p.29, cand_c14526b32c1e64a4)
- Плоская кровля :: `slope_plates_supplier_layout` — Разуклонка кровли = уточнить  (usv_2026_kr2.pdf p.29, cand_e67e041a8701a973)

## Normalized Structures

- normalized_rebar_items: 5
- normalized_beam_items: 79
- trench_routes: 0
- communication_pipe_items: 169
- normalized_roof_abutments: 6
- normalized_wall_block_volumes: 22

## Итог

- found_from_pdf: 30
- true_missing_in_project: 0
- mapping_gap: 9
- supplier_required: 2
- manual_required: 0
- low_confidence: 0

Переходить к generator input.json можно только после закрытия low_confidence, supplier_required и критичных missing/mapping_gap.
