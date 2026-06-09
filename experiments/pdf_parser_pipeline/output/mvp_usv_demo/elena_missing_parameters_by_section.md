# Что parser не нашел по 8 разделам сметы

Файл для Елены: список параметров, которые не удалось уверенно извлечь из PDF.

Главный блок ниже — вопросы к проектировщикам/проекту. Отдельно вынесены параметры, которые скорее заполняет Елена или сметчик, а не проектировщик.

## Сводка

| Раздел | К проектировщикам/по проекту | Ручные сметные/технические | Всего missing/manual |
|---|---:|---:|---:|
| Земляные работы (`earthworks`) | 3 | 10 | 13 |
| Фундаментная плита (`foundation_slab`) | 5 | 32 | 37 |
| Гидроизоляция (`waterproofing`) | 5 | 5 | 10 |
| Несущие стены и перемычки (`load_bearing_walls_lintels`) | 53 | 36 | 89 |
| Плита перекрытия 1-го этажа (`floor_slab_1`) | 13 | 53 | 66 |
| Плита перекрытия 2-го этажа (`floor_slab_2`) | 7 | 22 | 29 |
| Плоская кровля (`flat_roof`) | 14 | 19 | 33 |
| Вентиляционные каналы Schiedel (`schiedel_vent_channels`) | 3 | 3 | 6 |

## Вопросы к проектировщикам / по проекту

### Земляные работы

| Что нужно уточнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Длина коммуникаций | м | `communications_length_m` | missing |
| Площадь котлована | м2 | `pit_area_m2` | missing |
| Объем траншей | м3 | `trench_volume_m3` | missing |

### Фундаментная плита

| Что нужно уточнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Площадь опалубки бортов фундаментной плиты по спецификации | м2 | `slab_side_formwork_area_m2` | missing |
| Длина термовставок 100 мм по спецификации | мп | `thermal_insert_100_length_m` | missing |
| Материал термовставок 100 мм по спецификации | м3 | `thermal_insert_100_material_spec_qty` | missing |
| Длина термовставок 50 мм по спецификации | мп | `thermal_insert_50_length_m` | missing |
| Материал термовставок 50 мм по спецификации | м3 | `thermal_insert_50_material_spec_qty` | missing |

### Гидроизоляция

| Что нужно уточнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Длины участков без утепления | м | `non_insulated_edge_lengths_m[0]` | missing |
| Длины участков без утепления | м | `non_insulated_edge_lengths_m[1]` | missing |
| Длины участков без утепления | м | `non_insulated_edge_lengths_m[2]` | missing |
| Высота борта плиты | м | `slab_edge_height_m` | missing |
| Периметр бортов/опалубки плиты | м | `slab_formwork_perimeter_m` | missing |

### Несущие стены и перемычки

| Что нужно уточнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[0]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[1]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[10]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[11]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[12]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[13]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[14]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[2]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[3]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[4]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[5]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[6]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[7]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[8]` | missing |
| Длины отсечной гидроизоляции стен 250 мм | м | `cutoff_waterproofing_wall_250_lengths_m[9]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[0]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[1]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[10]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[11]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[12]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[13]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[14]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[15]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[2]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[3]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[4]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[5]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[6]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[7]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[8]` | missing |
| Длины отсечной гидроизоляции стен 400 мм | м | `cutoff_waterproofing_wall_400_lengths_m[9]` | missing |
| Перемычка 1: длина | м | `lintel_lengths_m[0].length_m` | missing |
| Перемычка 2: длина | м | `lintel_lengths_m[1].length_m` | missing |
| Перемычка 3: длина | м | `lintel_lengths_m[2].length_m` | missing |
| Перемычка 4: длина | м | `lintel_lengths_m[3].length_m` | missing |
| Перемычка 5: длина | м | `lintel_lengths_m[4].length_m` | missing |
| Перемычка 6: длина | м | `lintel_lengths_m[5].length_m` | missing |
| Высота сечения перемычки | м | `lintel_section_height_m` | missing |
| Ширина сечения перемычки | м | `lintel_section_width_m` | missing |
| Количество ниток армирования стены 250 мм | - | `main_wall_250_reinforcement_threads` | missing |
| Количество ниток армирования стены 400 мм | - | `main_wall_400_reinforcement_threads` | missing |
| Длина наружных стен | м | `main_wall_external_length_m` | missing |
| Количество рядов армирования кладки | - | `main_wall_reinforcement_rows` | missing |
| Базовая длина штробления парапета | м | `parapet_chasing_base_length_m` | missing |
| Объем кладки парапета | м3 | `parapet_masonry_volume_m3` | missing |
| Базовая длина арматуры парапета | м | `parapet_rebar_base_length_m` | missing |
| Базовая длина штробления второго света | м | `second_light_chasing_base_length_m` | missing |
| Объем кладки второго света | м3 | `second_light_masonry_volume_m3` | missing |
| Базовая длина арматуры второго света | м | `second_light_rebar_base_length_m` | missing |
| Сегмент обкладки вентканалов 1: длина | м | `vent_chimney_segment_lengths_m[0].length_m` | missing |
| Сегмент обкладки вентканалов 2: длина | м | `vent_chimney_segment_lengths_m[1].length_m` | missing |
| Сегмент обкладки вентканалов 3: длина | м | `vent_chimney_segment_lengths_m[2].length_m` | missing |
| Сегмент обкладки вентканалов 4: длина | м | `vent_chimney_segment_lengths_m[3].length_m` | missing |

### Плита перекрытия 1-го этажа

| Что нужно уточнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Балка Б-1: высота | м | `beams.items[0].height_m` | missing |
| Балка Б-1: длина | м | `beams.items[0].length_m` | missing |
| Балка Б-1: ширина | м | `beams.items[0].width_m` | missing |
| Балка Б-2: высота | м | `beams.items[1].height_m` | missing |
| Балка Б-2: длина | м | `beams.items[1].length_m` | missing |
| Балка Б-2: ширина | м | `beams.items[1].width_m` | missing |
| Балка Б-3: высота | м | `beams.items[2].height_m` | missing |
| Балка Б-3: длина | м | `beams.items[2].length_m` | missing |
| Балка Б-3: ширина | м | `beams.items[2].width_m` | missing |
| Высота торцевой опалубки | м | `geometry.edge_formwork_height_m` | missing |
| Периметр торца плиты | м | `geometry.slab_edge_perimeter_m` | missing |
| Объем бетона по спецификации | м3 | `geometry.total_concrete_volume_from_spec_m3` | missing |
| Объем ЭППС по спецификации | м3 | `insulation.total_eps_volume_from_spec_m3` | missing |

### Плита перекрытия 2-го этажа

| Что нужно уточнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Высота торцевой опалубки | м | `edge_formwork_height_m` | missing |
| Высота утепления торца | м | `edge_insulation_height_m` | missing |
| Основная площадь опалубки | м2 | `main_formwork_area_m2` | missing |
| Площадь плиты | м2 | `slab_area_m2` | missing |
| Периметр торца плиты | м | `slab_edge_perimeter_m` | missing |
| Длина плиты | м | `slab_length_m` | missing |
| Ширина плиты | м | `slab_width_m` | missing |

### Плоская кровля

| Что нужно уточнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Объем ЭППС 50 мм по раскладке поставщика | м3 | `eps50_supplier_required_volume_m3` | missing |
| Высота внутреннего водостока на одну воронку | м | `internal_drain_height_per_drain_m` | missing |
| Суммарная длина парапетов и примыканий | м | `parapet_and_abutment_total_length_m` | missing |
| Длина парапета уровня 1 | м | `parapet_length_level_1_m` | missing |
| Длина парапета уровня 2 | м | `parapet_length_level_2_m` | missing |
| Площадь кровли уровня 1 | м2 | `roof_area_level_1_m2` | missing |
| Площадь кровли уровня 2 | м2 | `roof_area_level_2_m2` | missing |
| Общая площадь кровли | м2 | `roof_area_total_m2` | missing |
| Объем уклонных плит A по раскладке поставщика | м3 | `slope_plate_a_supplier_required_volume_m3` | missing |
| Объем уклонных плит B по раскладке поставщика | м3 | `slope_plate_b_supplier_required_volume_m3` | missing |
| Объем уклонных плит J по раскладке поставщика | м3 | `slope_plate_j_supplier_required_volume_m3` | missing |
| Объем уклонных плит K по раскладке поставщика | м3 | `slope_plate_k_supplier_required_volume_m3` | missing |
| Длина примыканий к вентшахтам/стенам уровня 1 | м | `vent_wall_abutment_level_1_m` | missing |
| Длина примыканий к вентшахтам/стенам уровня 2 | м | `vent_wall_abutment_level_2_m` | missing |

### Вентиляционные каналы Schiedel

| Что нужно уточнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Общая длина кладки вентканалов Schiedel | м | `schiedel_masonry_total_length_m` | missing |
| Высота вентканала 1 | м | `vent_channel_1_height_m` | missing |
| Высота вентканала 2 | м | `vent_channel_2_height_m` | missing |

## Ручные сметные / технические параметры не для проектировщиков

### Земляные работы

| Что заполнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Ручное количество геотекстиля | bool | `assumptions.geotextile_override` | manual_required |
| Ручной объем доработки котлована | bool | `assumptions.manual_excavation_override` | manual_required |
| Ручной объем песка | bool | `assumptions.sand_override` | manual_required |
| Количество смен для разбивки осей | смена | `axis_marking_shifts` | manual_required |
| Количество смен экскаватора | смена | `excavator_shifts` | manual_required |
| Площадь укладки геотекстиля | м2 | `geotextile_laying_area_m2` | missing |
| Площадь одного рулона геотекстиля | м2 | `geotextile_roll_area_m2` | missing |
| Объем ручной доработки котлована для сметы | м3 | `manual_excavation_quantity_for_estimate_m3` | manual_required |
| Глубина ручной доработки | м | `manual_refinement_depth_m` | manual_required |
| Шаг заказа песка машиной | м3 | `sand_truck_step_m3` | missing |

### Фундаментная плита

| Что заполнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Общий вес металла коробки для доставки | кг | `box_total_metal_weight_kg` | missing |
| Объем одного автобетоносмесителя | м3 | `concrete_mixer_volume_m3` | missing |
| Количество смен бетононасоса | смена | `concrete_pump_shifts` | manual_required |
| Площадь одного рулона мембраны | м2 | `membrane_roll_area_m2` | missing |
| Количество PLANTERBAND на один рулон мембраны | - | `planterband_per_membrane_roll` | missing |
| Метод расчета фанеры | - | `plywood_calc_method` | manual_required |
| Высота листа фанеры | м | `plywood_sheet_height_m` | missing |
| Ширина листа фанеры | м | `plywood_sheet_width_m` | missing |
| Рабочая площадь листа фанеры | м2 | `plywood_sheet_working_area_m2` | missing |
| Количество смен крана для подачи арматуры | смена | `rebar_crane_shifts` | manual_required |
| Арматура 1: код позиции | - | `rebar_items[0].code` | missing |
| Арматура 1: диаметр | мм | `rebar_items[0].diameter_mm` | missing |
| Арматура 1: наименование позиции | - | `rebar_items[0].name` | missing |
| Арматура 1: класс стали | - | `rebar_items[0].steel_class` | missing |
| Арматура 1: вес по спецификации | кг | `rebar_items[0].weight_parts_kg[0]` | missing |
| Арматура 2: код позиции | - | `rebar_items[1].code` | missing |
| Арматура 2: диаметр | мм | `rebar_items[1].diameter_mm` | missing |
| Арматура 2: наименование позиции | - | `rebar_items[1].name` | missing |
| Арматура 2: класс стали | - | `rebar_items[1].steel_class` | missing |
| Арматура 2: вес по спецификации | кг | `rebar_items[1].weight_parts_kg[0]` | missing |
| Арматура 2: вес по спецификации | кг | `rebar_items[1].weight_parts_kg[1]` | missing |
| Арматура 3: код позиции | - | `rebar_items[2].code` | missing |
| Арматура 3: диаметр | мм | `rebar_items[2].diameter_mm` | missing |
| Арматура 3: наименование позиции | - | `rebar_items[2].name` | missing |
| Арматура 3: класс стали | - | `rebar_items[2].steel_class` | missing |
| Арматура 3: вес по спецификации | кг | `rebar_items[2].weight_parts_kg[0]` | missing |
| Арматура 4: код позиции | - | `rebar_items[3].code` | missing |
| Арматура 4: диаметр | мм | `rebar_items[3].diameter_mm` | missing |
| Арматура 4: наименование позиции | - | `rebar_items[3].name` | missing |
| Арматура 4: класс стали | - | `rebar_items[3].steel_class` | missing |
| Арматура 4: вес по спецификации | кг | `rebar_items[3].weight_parts_kg[0]` | missing |
| Количество машин доставки арматуры/металла | - | `rebar_metal_delivery_trucks` | missing |

### Гидроизоляция

| Что заполнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Минимальное количество клей-пены | - | `glue_foam_min_units` | manual_required |
| Вес одного ведра битумной мастики | кг | `mastic_bucket_weight_kg` | missing |
| Количество слоев битумной мастики | - | `mastic_layers` | manual_required |
| Объем одной канистры праймера | - | `primer_canister_volume_l` | missing |
| Расход праймера на 1 м2 | м2 | `primer_consumption_l_per_m2` | manual_required |

### Несущие стены и перемычки

| Что заполнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Расход клея для блоков на 1 м3 кладки | м3 | `adhesive_consumption_bag_per_m3` | manual_required |
| Высота блока | м | `block_height_m` | missing |
| Количество рейсов доставки бетона | рейс | `concrete_delivery_trips` | manual_required |
| Объем газобетона D400 в одном поддоне | м3 | `gas_block_d400_pallet_volume_m3` | missing |
| Объем газобетона D500 150 мм в одном поддоне | м3 | `gas_block_d500_150_pallet_volume_m3` | missing |
| Объем газобетона D500 250 мм в одном поддоне | м3 | `gas_block_d500_250_pallet_volume_m3` | missing |
| Длина газобетонного блока | м | `gas_block_length_m` | missing |
| Минимальный заказ бетона для перемычек | м3 | `lintel_concrete_min_order_volume_m3` | missing |
| Перемычка 1: количество | - | `lintel_lengths_m[0].count` | manual_required |
| Перемычка 2: количество | - | `lintel_lengths_m[1].count` | manual_required |
| Перемычка 3: количество | - | `lintel_lengths_m[2].count` | manual_required |
| Перемычка 4: количество | - | `lintel_lengths_m[3].count` | manual_required |
| Перемычка 5: количество | - | `lintel_lengths_m[4].count` | manual_required |
| Перемычка 6: количество | - | `lintel_lengths_m[5].count` | manual_required |
| Арматура перемычек 1: код позиции | - | `lintel_rebar_items[0].code` | missing |
| Арматура перемычек 1: диаметр | мм | `lintel_rebar_items[0].diameter_mm` | missing |
| Арматура перемычек 1: наименование позиции | - | `lintel_rebar_items[0].name` | missing |
| Арматура перемычек 1: класс стали | - | `lintel_rebar_items[0].steel_class` | missing |
| Арматура перемычек 2: код позиции | - | `lintel_rebar_items[1].code` | missing |
| Арматура перемычек 2: диаметр | мм | `lintel_rebar_items[1].diameter_mm` | missing |
| Арматура перемычек 2: наименование позиции | - | `lintel_rebar_items[1].name` | missing |
| Арматура перемычек 2: класс стали | - | `lintel_rebar_items[1].steel_class` | missing |
| Количество смен крана для несущих стен | смена | `main_walls_crane_shifts` | manual_required |
| Количество смен крана для парапета | смена | `parapet_crane_shifts` | manual_required |
| Учитывать парапет в расчете | bool | `parapet_enabled` | manual_required |
| Вес одного мешка пескобетона | кг | `sand_concrete_bag_weight_kg` | missing |
| Количество для устройства лесов/подмостей | - | `scaffolding_setup_quantity` | manual_required |
| Объем пиломатериала для подмостей | м3 | `scaffolding_timber_quantity_m3` | manual_required |
| Кладка второго света: учитывать проектную особенность | bool | `second_light_masonry_case_specific` | manual_required |
| Учитывать кладку второго света | bool | `second_light_masonry_enabled` | manual_required |
| Учитывать обкладку вентканалов | bool | `vent_chimney_cladding_enabled` | manual_required |
| Количество рядов обкладки вентканалов | - | `vent_chimney_rows` | manual_required |
| Сегмент обкладки вентканалов 1: количество | - | `vent_chimney_segment_lengths_m[0].count` | manual_required |
| Сегмент обкладки вентканалов 2: количество | - | `vent_chimney_segment_lengths_m[1].count` | manual_required |
| Сегмент обкладки вентканалов 3: количество | - | `vent_chimney_segment_lengths_m[2].count` | manual_required |
| Сегмент обкладки вентканалов 4: количество | - | `vent_chimney_segment_lengths_m[3].count` | manual_required |

### Плита перекрытия 1-го этажа

| Что заполнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Балка Б-1: код позиции | - | `beams.items[0].code` | manual_required |
| Балка Б-1: наименование позиции | - | `beams.items[0].name` | manual_required |
| Балка Б-2: код позиции | - | `beams.items[1].code` | manual_required |
| Балка Б-2: наименование позиции | - | `beams.items[1].name` | manual_required |
| Балка Б-3: код позиции | - | `beams.items[2].code` | manual_required |
| Балка Б-3: наименование позиции | - | `beams.items[2].name` | manual_required |
| Объем бетона плиты, отображаемое значение | - | `geometry.slab_concrete_volume_m3_display` | missing |
| Объем бетона плиты, расчетное значение без округления | - | `geometry.slab_concrete_volume_m3_raw` | missing |
| Количество смен бетононасоса | смена | `manual_lines.concrete_pump_shifts` | manual_required |
| Ручное количество машин доставки опалубки | - | `manual_lines.formwork_delivery_trucks_override` | manual_required |
| Количество смен крана для подачи опалубки и арматуры | смена | `manual_lines.formwork_rebar_crane_shifts` | manual_required |
| Процент расходных материалов и амортизации инструмента | - | `overheads.consumables_and_tool_percent` | manual_required |
| Процент логистики и снабжения | - | `overheads.logistics_and_supply_percent` | manual_required |
| Стоимость смены бетононасоса | руб. | `rates.concrete_pump_rate` | missing |
| Стоимость смены автокрана | руб. | `rates.crane_shift_rate` | manual_required |
| Вес арматуры плиты 2-го этажа для расчета доставки | кг | `rates.floor_slab_2_rebar_weight_for_delivery_context_kg` | missing |
| Сумма предложения поставщика по опалубке | - | `rates.formwork_supplier_quote_total` | manual_required |
| Максимальный вес арматуры на одну машину доставки | кг | `rates.max_rebar_delivery_weight_per_truck_kg` | missing |
| Эквивалент листов для свесов и доборов | - | `rates.overhang_sheet_equivalent` | manual_required |
| Рабочая площадь листа фанеры | м2 | `rates.plywood_sheet_working_area_m2` | missing |
| Резерв фанеры | - | `rates.reserve_plywood_sheets` | manual_required |
| Площадь опалубки плиты 2-го этажа для справочной ставки | м2 | `rates.slab_2_formwork_area_for_rate_context_m2` | missing |
| Арматура 1: код позиции | - | `rebar_items[0].code` | missing |
| Арматура 1: диаметр | мм | `rebar_items[0].diameter_mm` | missing |
| Арматура 1: наименование позиции | - | `rebar_items[0].name` | missing |
| Арматура 1: класс стали | - | `rebar_items[0].steel_class` | missing |
| Арматура 2: код позиции | - | `rebar_items[1].code` | missing |
| Арматура 2: диаметр | мм | `rebar_items[1].diameter_mm` | missing |
| Арматура 2: наименование позиции | - | `rebar_items[1].name` | missing |
| Арматура 2: вес по спецификации, часть 1 | кг | `rebar_items[1].source_weight_parts_kg[0]` | missing |
| Арматура 2: вес по спецификации, часть 2 | кг | `rebar_items[1].source_weight_parts_kg[1]` | missing |
| Арматура 2: класс стали | - | `rebar_items[1].steel_class` | missing |
| Арматура 3: код позиции | - | `rebar_items[2].code` | missing |
| Арматура 3: диаметр | мм | `rebar_items[2].diameter_mm` | missing |
| Арматура 3: наименование позиции | - | `rebar_items[2].name` | missing |
| Арматура 3: класс стали | - | `rebar_items[2].steel_class` | missing |
| Арматура 4: код позиции | - | `rebar_items[3].code` | missing |
| Арматура 4: диаметр | мм | `rebar_items[3].diameter_mm` | missing |
| Арматура 4: наименование позиции | - | `rebar_items[3].name` | missing |
| Арматура 4: вес по спецификации, часть 1 | кг | `rebar_items[3].source_weight_parts_kg[0]` | missing |
| Арматура 4: вес по спецификации, часть 2 | кг | `rebar_items[3].source_weight_parts_kg[1]` | missing |
| Арматура 4: вес по спецификации, часть 3 | кг | `rebar_items[3].source_weight_parts_kg[2]` | missing |
| Арматура 4: класс стали | - | `rebar_items[3].steel_class` | missing |
| Арматура 5: код позиции | - | `rebar_items[4].code` | missing |
| Арматура 5: диаметр | мм | `rebar_items[4].diameter_mm` | missing |
| Арматура 5: наименование позиции | - | `rebar_items[4].name` | missing |
| Арматура 5: класс стали | - | `rebar_items[4].steel_class` | missing |
| Арматура 6: код позиции | - | `rebar_items[5].code` | missing |
| Арматура 6: диаметр | мм | `rebar_items[5].diameter_mm` | missing |
| Арматура 6: наименование позиции | - | `rebar_items[5].name` | missing |
| Арматура 6: вес по спецификации, часть 1 | кг | `rebar_items[5].source_weight_parts_kg[0]` | missing |
| Арматура 6: вес по спецификации, часть 2 | кг | `rebar_items[5].source_weight_parts_kg[1]` | missing |
| Арматура 6: класс стали | - | `rebar_items[5].steel_class` | missing |

### Плита перекрытия 2-го этажа

| Что заполнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Объем одного автобетоносмесителя | м3 | `concrete_mixer_volume_m3` | missing |
| Количество смен бетононасоса | смена | `concrete_pump_shifts` | manual_required |
| Процент расходных материалов | руб. | `consumables_rate` | manual_required |
| Количество смен автокрана | смена | `crane_shifts` | manual_required |
| Минимальное количество баллонов клей-пены | - | `foam_min_cans` | manual_required |
| Количество рейсов доставки/вывоза опалубки | рейс | `formwork_delivery_trips` | manual_required |
| Сумма предложения поставщика по аренде опалубки | - | `formwork_rental_supplier_quote_total` | manual_required |
| Процент логистики | руб. | `logistics_rate` | manual_required |
| Резерв фанеры | - | `plywood_reserve_sheets` | manual_required |
| Рабочая площадь листа фанеры | м2 | `plywood_sheet_working_area_m2` | missing |
| Арматура 1: код позиции | - | `rebar_items[0].code` | missing |
| Арматура 1: диаметр | мм | `rebar_items[0].diameter_mm` | missing |
| Арматура 1: наименование позиции | - | `rebar_items[0].name` | missing |
| Арматура 1: класс стали | - | `rebar_items[0].steel_class` | missing |
| Арматура 2: код позиции | - | `rebar_items[1].code` | missing |
| Арматура 2: диаметр | мм | `rebar_items[1].diameter_mm` | missing |
| Арматура 2: наименование позиции | - | `rebar_items[1].name` | missing |
| Арматура 2: класс стали | - | `rebar_items[1].steel_class` | missing |
| Арматура 3: код позиции | - | `rebar_items[2].code` | missing |
| Арматура 3: диаметр | мм | `rebar_items[2].diameter_mm` | missing |
| Арматура 3: наименование позиции | - | `rebar_items[2].name` | missing |
| Арматура 3: класс стали | - | `rebar_items[2].steel_class` | missing |

### Плоская кровля

| Что заполнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Ставка пробивки отверстия в стене из газоблока | руб. | `gas_block_wall_hole_drilling_rate` | missing |
| Количество отверстий в стенах из газоблока | шт | `gas_block_wall_holes_count` | manual_required |
| Площадь рулона геотекстиля для плоской части кровли | м2 | `geotextile_flat_roll_area_m2` | missing |
| Площадь рулона геотекстиля для парапетов | м2 | `geotextile_parapet_roll_area_m2` | missing |
| Ставка установки внутренней кровельной воронки | руб. | `internal_roof_drain_installation_rate` | missing |
| Ставка установки парапетной кровельной воронки | руб. | `parapet_roof_drain_installation_rate` | missing |
| Заготовительно-складские расходы | - | `procurement_storage_work_total` | manual_required |
| Ожидаемая сумма материала ПВХ мембраны | - | `pvc_membrane_expected_material_total` | missing |
| Длина рулона ПВХ мембраны | м | `pvc_membrane_roll_length_m` | missing |
| Ширина рулона ПВХ мембраны | м | `pvc_membrane_roll_width_m` | missing |
| Длина одной алюминиевой рейки | м | `rail_piece_length_m` | missing |
| Ставка установки кровельного аэратора | руб. | `roof_aerator_installation_rate` | missing |
| Количество кровельных аэраторов | шт | `roof_aerators_count` | manual_required |
| Сумма расходных материалов по кровле | - | `roof_consumables_total` | missing |
| Количество смен автокрана для подъема кровельных материалов | смена | `roof_crane_lifting_shifts` | manual_required |
| Сумма логистики и снабжения по кровле | - | `roof_logistics_and_supply_total` | missing |
| Сумма технического надзора | - | `technical_supervision_work_total` | manual_required |
| Площадь рулона пароизоляционной пленки | м2 | `vapor_barrier_film_roll_area_m2` | missing |
| Количество примыканий к вентшахтам | шт | `vent_shaft_abutment_count` | manual_required |

### Вентиляционные каналы Schiedel

| Что заполнить | Ед. | calculator_input_key | Статус |
|---|---|---|---|
| Процент расходных материалов | руб. | `consumables_rate` | manual_required |
| Количество доставок вентканалов Schiedel | рейс | `schiedel_delivery_trips` | manual_required |
| Количество вентканалов типа 2 | шт | `vent_channel_2_count` | manual_required |

## Примечание

- Parser/AI не считают смету.
- Найденные значения всё равно требуют проверки Еленой.
- Этот файл показывает только незаполненные параметры из текущего `reviewed_parameters.xlsx`.
- Полный raw-список есть в Excel-версии на листе `all_missing_raw`.
