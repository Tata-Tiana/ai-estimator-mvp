# Review card: Плита перекрытия 1-го этажа

## Что система нашла
| parameter_code | value | unit | source | page | status |
|---|---:|---|---|---:|---|
| floor_slab_1_concrete_volume | 40.53 | м3 | ЮСВ КР2.pdf | 21 | needs_human_review |
| floor_slab_1_eps100_volume | 7.77 | м3 | ЮСВ КР2.pdf | 21 | needs_human_review |
| floor_slab_1_rebar_a500_d10_weight | 3900 | кг | ЮСВ КР2.pdf | 21 | needs_human_review |
| floor_slab_1_rebar_a500_d12_weight | 42 | кг | ЮСВ КР2.pdf | 21 | needs_human_review |
| floor_slab_1_rebar_a500_d25_weight | 162 | кг | ЮСВ КР2.pdf | 21 | needs_human_review |
| floor_slab_1_rebar_a500_d16_weight | 52.04 | кг | ЮСВ КР2.pdf | 21 | needs_human_review |
| floor_slab_1_rebar_a240_d6_weight | 15 | кг | ЮСВ КР2.pdf | 21 | needs_human_review |
| floor_slab_1_rebar_a240_d8_weight | 17 | кг | ЮСВ КР2.pdf | 21 | needs_human_review |

## Что проверить Елене
- Проверить балки Б-1/Б-2/Б-3 и ручные геометрические параметры.

## Параметры для калькулятора
| parameter_code | calculator_input_key | status |
|---|---|---|
| floor_slab_1_concrete_volume | total_concrete_volume_from_spec_m3 | needs_human_review |
| floor_slab_1_eps100_volume | total_eps_volume_from_spec_m3 | needs_human_review |
| floor_slab_1_rebar_a500_d10_weight | rebar_items[3].source_weight_parts_kg | needs_human_review |
| floor_slab_1_rebar_a500_d12_weight | rebar_items[2].source_weight_kg | needs_human_review |
| floor_slab_1_rebar_a500_d25_weight | rebar_items[0].source_weight_kg | needs_human_review |
| floor_slab_1_rebar_a500_d16_weight | rebar_items[1].source_weight_parts_kg | needs_human_review |
| floor_slab_1_rebar_a240_d6_weight | rebar_items[5].source_weight_parts_kg | needs_human_review |
| floor_slab_1_rebar_a240_d8_weight | rebar_items[4].source_weight_kg | needs_human_review |
| floor_slab_1_geometry_total_concrete_volume_from_spec_m3 | geometry.total_concrete_volume_from_spec_m3 | missing |
| floor_slab_1_geometry_slab_thickness_m | geometry.slab_thickness_m | missing |
| floor_slab_1_geometry_slab_concrete_volume_m3_raw | geometry.slab_concrete_volume_m3_raw | missing |
| floor_slab_1_geometry_slab_concrete_volume_m3_display | geometry.slab_concrete_volume_m3_display | missing |
| floor_slab_1_geometry_slab_edge_perimeter_m | geometry.slab_edge_perimeter_m | missing |
| floor_slab_1_geometry_edge_formwork_height_m | geometry.edge_formwork_height_m | missing |
| floor_slab_1_beams_items_0_code | beams.items[0].code | manual_required |
| floor_slab_1_beams_items_0_name | beams.items[0].name | manual_required |
| floor_slab_1_beams_items_0_length_m | beams.items[0].length_m | missing |
| floor_slab_1_beams_items_0_width_m | beams.items[0].width_m | missing |
| floor_slab_1_beams_items_0_height_m | beams.items[0].height_m | missing |
| floor_slab_1_beams_items_1_code | beams.items[1].code | manual_required |
| floor_slab_1_beams_items_1_name | beams.items[1].name | manual_required |
| floor_slab_1_beams_items_1_length_m | beams.items[1].length_m | missing |
| floor_slab_1_beams_items_1_width_m | beams.items[1].width_m | missing |
| floor_slab_1_beams_items_1_height_m | beams.items[1].height_m | missing |
| floor_slab_1_beams_items_2_code | beams.items[2].code | manual_required |
| floor_slab_1_beams_items_2_name | beams.items[2].name | manual_required |
| floor_slab_1_beams_items_2_length_m | beams.items[2].length_m | missing |
| floor_slab_1_beams_items_2_width_m | beams.items[2].width_m | missing |
| floor_slab_1_beams_items_2_height_m | beams.items[2].height_m | missing |
| floor_slab_1_rates_formwork_rate_per_m2 | rates.formwork_rate_per_m2 | missing |
| floor_slab_1_rates_formwork_supplier_quote_total | rates.formwork_supplier_quote_total | manual_required |
| floor_slab_1_rates_slab_2_formwork_area_for_rate_context_m2 | rates.slab_2_formwork_area_for_rate_context_m2 | missing |
| floor_slab_1_rates_formwork_delivery_rate_per_trip | rates.formwork_delivery_rate_per_trip | missing |
| floor_slab_1_rates_crane_shift_rate | rates.crane_shift_rate | manual_required |
| floor_slab_1_rates_formwork_consumables_rate_per_m2 | rates.formwork_consumables_rate_per_m2 | missing |
| floor_slab_1_rates_plywood_sheet_working_area_m2 | rates.plywood_sheet_working_area_m2 | missing |
| floor_slab_1_rates_reserve_plywood_sheets | rates.reserve_plywood_sheets | manual_required |
| floor_slab_1_rates_non_multiple_places_coeff | rates.non_multiple_places_coeff | missing |
| floor_slab_1_rates_overhang_sheet_equivalent | rates.overhang_sheet_equivalent | manual_required |
| floor_slab_1_rates_plywood_unit_price | rates.plywood_unit_price | missing |
| floor_slab_1_rates_timber_thickness_m | rates.timber_thickness_m | missing |
| floor_slab_1_rates_additional_timber_coeff | rates.additional_timber_coeff | missing |
| floor_slab_1_rates_additional_timber_thickness_m | rates.additional_timber_thickness_m | missing |
| floor_slab_1_rates_timber_unit_price | rates.timber_unit_price | missing |
| floor_slab_1_rates_floor_slab_2_rebar_weight_for_delivery_context_kg | rates.floor_slab_2_rebar_weight_for_delivery_context_kg | missing |
| floor_slab_1_rates_max_rebar_delivery_weight_per_truck_kg | rates.max_rebar_delivery_weight_per_truck_kg | missing |
| floor_slab_1_rates_rebar_delivery_rate_per_truck | rates.rebar_delivery_rate_per_truck | missing |
| floor_slab_1_rates_slab_concreting_work_rate_per_m3 | rates.slab_concreting_work_rate_per_m3 | missing |
| floor_slab_1_rates_beam_concreting_work_rate_per_m3 | rates.beam_concreting_work_rate_per_m3 | missing |
| floor_slab_1_rates_concrete_waste_coeff | rates.concrete_waste_coeff | missing |
| floor_slab_1_rates_concrete_unit_price_per_m3 | rates.concrete_unit_price_per_m3 | missing |
| floor_slab_1_rates_mixer_capacity_m3 | rates.mixer_capacity_m3 | missing |
| floor_slab_1_rates_concrete_delivery_rate_per_trip | rates.concrete_delivery_rate_per_trip | missing |
| floor_slab_1_rates_concrete_pump_rate | rates.concrete_pump_rate | missing |
| floor_slab_1_rates_edge_beam_insulation_work_rate_per_m | rates.edge_beam_insulation_work_rate_per_m | missing |
| floor_slab_1_rates_bottom_slab_insulation_work_rate_per_m2 | rates.bottom_slab_insulation_work_rate_per_m2 | missing |
| floor_slab_1_rebar_items_0_code | rebar_items[0].code | missing |
| floor_slab_1_rebar_items_0_name | rebar_items[0].name | missing |
| floor_slab_1_rebar_items_0_steel_class | rebar_items[0].steel_class | missing |
| floor_slab_1_rebar_items_0_diameter_mm | rebar_items[0].diameter_mm | missing |
| floor_slab_1_rebar_items_0_kg_per_meter | rebar_items[0].kg_per_meter | missing |
| floor_slab_1_rebar_items_0_waste_coeff | rebar_items[0].waste_coeff | missing |
| floor_slab_1_rebar_items_0_rod_length_m | rebar_items[0].rod_length_m | missing |
| floor_slab_1_rebar_items_0_unit_price_per_m | rebar_items[0].unit_price_per_m | missing |
| floor_slab_1_rebar_items_1_code | rebar_items[1].code | missing |
| floor_slab_1_rebar_items_1_name | rebar_items[1].name | missing |
| floor_slab_1_rebar_items_1_steel_class | rebar_items[1].steel_class | missing |
| floor_slab_1_rebar_items_1_diameter_mm | rebar_items[1].diameter_mm | missing |
| floor_slab_1_rebar_items_1_source_weight_parts_kg_0 | rebar_items[1].source_weight_parts_kg[0] | missing |
| floor_slab_1_rebar_items_1_source_weight_parts_kg_1 | rebar_items[1].source_weight_parts_kg[1] | missing |
| floor_slab_1_rebar_items_1_kg_per_meter | rebar_items[1].kg_per_meter | missing |
| floor_slab_1_rebar_items_1_waste_coeff | rebar_items[1].waste_coeff | missing |
| floor_slab_1_rebar_items_1_rod_length_m | rebar_items[1].rod_length_m | missing |
| floor_slab_1_rebar_items_1_unit_price_per_m | rebar_items[1].unit_price_per_m | missing |
| floor_slab_1_rebar_items_2_code | rebar_items[2].code | missing |
| floor_slab_1_rebar_items_2_name | rebar_items[2].name | missing |
| floor_slab_1_rebar_items_2_steel_class | rebar_items[2].steel_class | missing |
| floor_slab_1_rebar_items_2_diameter_mm | rebar_items[2].diameter_mm | missing |
| floor_slab_1_rebar_items_2_kg_per_meter | rebar_items[2].kg_per_meter | missing |
| floor_slab_1_rebar_items_2_waste_coeff | rebar_items[2].waste_coeff | missing |
| floor_slab_1_rebar_items_2_rod_length_m | rebar_items[2].rod_length_m | missing |
| floor_slab_1_rebar_items_2_unit_price_per_m | rebar_items[2].unit_price_per_m | missing |
| floor_slab_1_rebar_items_3_code | rebar_items[3].code | missing |
| floor_slab_1_rebar_items_3_name | rebar_items[3].name | missing |
| floor_slab_1_rebar_items_3_steel_class | rebar_items[3].steel_class | missing |
| floor_slab_1_rebar_items_3_diameter_mm | rebar_items[3].diameter_mm | missing |
| floor_slab_1_rebar_items_3_source_weight_parts_kg_0 | rebar_items[3].source_weight_parts_kg[0] | missing |
| floor_slab_1_rebar_items_3_source_weight_parts_kg_1 | rebar_items[3].source_weight_parts_kg[1] | missing |
| floor_slab_1_rebar_items_3_source_weight_parts_kg_2 | rebar_items[3].source_weight_parts_kg[2] | missing |
| floor_slab_1_rebar_items_3_kg_per_meter | rebar_items[3].kg_per_meter | missing |
| floor_slab_1_rebar_items_3_waste_coeff | rebar_items[3].waste_coeff | missing |
| floor_slab_1_rebar_items_3_rod_length_m | rebar_items[3].rod_length_m | missing |
| floor_slab_1_rebar_items_3_unit_price_per_m | rebar_items[3].unit_price_per_m | missing |
| floor_slab_1_rebar_items_4_code | rebar_items[4].code | missing |
| floor_slab_1_rebar_items_4_name | rebar_items[4].name | missing |
| floor_slab_1_rebar_items_4_steel_class | rebar_items[4].steel_class | missing |
| floor_slab_1_rebar_items_4_diameter_mm | rebar_items[4].diameter_mm | missing |
| floor_slab_1_rebar_items_4_kg_per_meter | rebar_items[4].kg_per_meter | missing |
| floor_slab_1_rebar_items_4_waste_coeff | rebar_items[4].waste_coeff | missing |
| floor_slab_1_rebar_items_4_rod_length_m | rebar_items[4].rod_length_m | missing |
| floor_slab_1_rebar_items_4_unit_price_per_m | rebar_items[4].unit_price_per_m | missing |
| floor_slab_1_rebar_items_5_code | rebar_items[5].code | missing |
| floor_slab_1_rebar_items_5_name | rebar_items[5].name | missing |
| floor_slab_1_rebar_items_5_steel_class | rebar_items[5].steel_class | missing |
| floor_slab_1_rebar_items_5_diameter_mm | rebar_items[5].diameter_mm | missing |
| floor_slab_1_rebar_items_5_source_weight_parts_kg_0 | rebar_items[5].source_weight_parts_kg[0] | missing |
| floor_slab_1_rebar_items_5_source_weight_parts_kg_1 | rebar_items[5].source_weight_parts_kg[1] | missing |
| floor_slab_1_rebar_items_5_kg_per_meter | rebar_items[5].kg_per_meter | missing |
| floor_slab_1_rebar_items_5_waste_coeff | rebar_items[5].waste_coeff | missing |
| floor_slab_1_rebar_items_5_rod_length_m | rebar_items[5].rod_length_m | missing |
| floor_slab_1_rebar_items_5_unit_price_per_m | rebar_items[5].unit_price_per_m | missing |
| floor_slab_1_insulation_total_eps_volume_from_spec_m3 | insulation.total_eps_volume_from_spec_m3 | missing |
| floor_slab_1_insulation_eps_thickness_m | insulation.eps_thickness_m | missing |
| floor_slab_1_insulation_eps_waste_coeff | insulation.eps_waste_coeff | missing |
| floor_slab_1_insulation_eps_pack_volume_m3 | insulation.eps_pack_volume_m3 | missing |
| floor_slab_1_insulation_eps_unit_price_per_m3 | insulation.eps_unit_price_per_m3 | missing |
| floor_slab_1_insulation_foam_coverage_m2_per_can | insulation.foam_coverage_m2_per_can | missing |
| floor_slab_1_insulation_foam_unit_price_per_can | insulation.foam_unit_price_per_can | missing |
| floor_slab_1_overheads_logistics_and_supply_percent | overheads.logistics_and_supply_percent | manual_required |
| floor_slab_1_overheads_consumables_and_tool_percent | overheads.consumables_and_tool_percent | manual_required |
| floor_slab_1_manual_lines_formwork_delivery_trucks_override | manual_lines.formwork_delivery_trucks_override | manual_required |
| floor_slab_1_manual_lines_formwork_rebar_crane_shifts | manual_lines.formwork_rebar_crane_shifts | manual_required |
| floor_slab_1_manual_lines_concrete_pump_shifts | manual_lines.concrete_pump_shifts | manual_required |
| floor_slab_1_manual_lines_technical_supervision_amount | manual_lines.technical_supervision_amount | missing |

## Missing / manual_required
| parameter_code | label | status |
|---|---|---|
| floor_slab_1_geometry_total_concrete_volume_from_spec_m3 | total concrete volume from spec m3 | missing |
| floor_slab_1_geometry_slab_thickness_m | slab thickness m | missing |
| floor_slab_1_geometry_slab_concrete_volume_m3_raw | Объем бетона плиты, расчетное значение без округления | missing |
| floor_slab_1_geometry_slab_concrete_volume_m3_display | Объем бетона плиты, отображаемое значение | missing |
| floor_slab_1_geometry_slab_edge_perimeter_m | Периметр торца плиты | missing |
| floor_slab_1_geometry_edge_formwork_height_m | Высота торцевой опалубки | missing |
| floor_slab_1_beams_items_0_code | Балка Б-1: код позиции | manual_required |
| floor_slab_1_beams_items_0_name | Балка Б-1: наименование позиции | manual_required |
| floor_slab_1_beams_items_0_length_m | Балка Б-1: длина | missing |
| floor_slab_1_beams_items_0_width_m | Балка Б-1: ширина | missing |
| floor_slab_1_beams_items_0_height_m | Балка Б-1: высота | missing |
| floor_slab_1_beams_items_1_code | Балка Б-2: код позиции | manual_required |
| floor_slab_1_beams_items_1_name | Балка Б-2: наименование позиции | manual_required |
| floor_slab_1_beams_items_1_length_m | Балка Б-2: длина | missing |
| floor_slab_1_beams_items_1_width_m | Балка Б-2: ширина | missing |
| floor_slab_1_beams_items_1_height_m | Балка Б-2: высота | missing |
| floor_slab_1_beams_items_2_code | Балка Б-3: код позиции | manual_required |
| floor_slab_1_beams_items_2_name | Балка Б-3: наименование позиции | manual_required |
| floor_slab_1_beams_items_2_length_m | Балка Б-3: длина | missing |
| floor_slab_1_beams_items_2_width_m | Балка Б-3: ширина | missing |
| floor_slab_1_beams_items_2_height_m | Балка Б-3: высота | missing |
| floor_slab_1_rates_formwork_rate_per_m2 | formwork rate per m2 | missing |
| floor_slab_1_rates_formwork_supplier_quote_total | Сумма предложения поставщика по опалубке | manual_required |
| floor_slab_1_rates_slab_2_formwork_area_for_rate_context_m2 | Площадь опалубки плиты 2-го этажа для справочной ставки | missing |
| floor_slab_1_rates_formwork_delivery_rate_per_trip | formwork delivery rate per trip | missing |
| floor_slab_1_rates_crane_shift_rate | Стоимость смены автокрана | manual_required |
| floor_slab_1_rates_formwork_consumables_rate_per_m2 | formwork consumables rate per m2 | missing |
| floor_slab_1_rates_plywood_sheet_working_area_m2 | Рабочая площадь листа фанеры | missing |
| floor_slab_1_rates_reserve_plywood_sheets | Резерв фанеры | manual_required |
| floor_slab_1_rates_non_multiple_places_coeff | non multiple places coeff | missing |
| floor_slab_1_rates_overhang_sheet_equivalent | Эквивалент листов для свесов и доборов | manual_required |
| floor_slab_1_rates_plywood_unit_price | plywood unit price | missing |
| floor_slab_1_rates_timber_thickness_m | timber thickness m | missing |
| floor_slab_1_rates_additional_timber_coeff | additional timber coeff | missing |
| floor_slab_1_rates_additional_timber_thickness_m | additional timber thickness m | missing |
| floor_slab_1_rates_timber_unit_price | timber unit price | missing |
| floor_slab_1_rates_floor_slab_2_rebar_weight_for_delivery_context_kg | Вес арматуры плиты 2-го этажа для расчета доставки | missing |
| floor_slab_1_rates_max_rebar_delivery_weight_per_truck_kg | Максимальный вес арматуры на одну машину доставки | missing |
| floor_slab_1_rates_rebar_delivery_rate_per_truck | rebar delivery rate per truck | missing |
| floor_slab_1_rates_slab_concreting_work_rate_per_m3 | slab concreting work rate per m3 | missing |
| floor_slab_1_rates_beam_concreting_work_rate_per_m3 | beam concreting work rate per m3 | missing |
| floor_slab_1_rates_concrete_waste_coeff | concrete waste coeff | missing |
| floor_slab_1_rates_concrete_unit_price_per_m3 | concrete unit price per m3 | missing |
| floor_slab_1_rates_mixer_capacity_m3 | mixer capacity m3 | missing |
| floor_slab_1_rates_concrete_delivery_rate_per_trip | concrete delivery rate per trip | missing |
| floor_slab_1_rates_concrete_pump_rate | Стоимость смены бетононасоса | missing |
| floor_slab_1_rates_edge_beam_insulation_work_rate_per_m | edge beam insulation work rate per m | missing |
| floor_slab_1_rates_bottom_slab_insulation_work_rate_per_m2 | bottom slab insulation work rate per m2 | missing |
| floor_slab_1_rebar_items_0_code | Арматура 1: код позиции | missing |
| floor_slab_1_rebar_items_0_name | Арматура 1: наименование позиции | missing |
| floor_slab_1_rebar_items_0_steel_class | Арматура 1: класс стали | missing |
| floor_slab_1_rebar_items_0_diameter_mm | Арматура 1: диаметр | missing |
| floor_slab_1_rebar_items_0_kg_per_meter | Арматура 1: вес 1 погонного метра | missing |
| floor_slab_1_rebar_items_0_waste_coeff | Арматура 1: коэффициент запаса/отходов | missing |
| floor_slab_1_rebar_items_0_rod_length_m | Арматура 1: длина одного хлыста арматуры | missing |
| floor_slab_1_rebar_items_0_unit_price_per_m | Арматура 1: цена за погонный метр | missing |
| floor_slab_1_rebar_items_1_code | Арматура 2: код позиции | missing |
| floor_slab_1_rebar_items_1_name | Арматура 2: наименование позиции | missing |
| floor_slab_1_rebar_items_1_steel_class | Арматура 2: класс стали | missing |
| floor_slab_1_rebar_items_1_diameter_mm | Арматура 2: диаметр | missing |
| floor_slab_1_rebar_items_1_source_weight_parts_kg_0 | Арматура 2: вес по спецификации, часть 1 | missing |
| floor_slab_1_rebar_items_1_source_weight_parts_kg_1 | Арматура 2: вес по спецификации, часть 2 | missing |
| floor_slab_1_rebar_items_1_kg_per_meter | Арматура 2: вес 1 погонного метра | missing |
| floor_slab_1_rebar_items_1_waste_coeff | Арматура 2: коэффициент запаса/отходов | missing |
| floor_slab_1_rebar_items_1_rod_length_m | Арматура 2: длина одного хлыста арматуры | missing |
| floor_slab_1_rebar_items_1_unit_price_per_m | Арматура 2: цена за погонный метр | missing |
| floor_slab_1_rebar_items_2_code | Арматура 3: код позиции | missing |
| floor_slab_1_rebar_items_2_name | Арматура 3: наименование позиции | missing |
| floor_slab_1_rebar_items_2_steel_class | Арматура 3: класс стали | missing |
| floor_slab_1_rebar_items_2_diameter_mm | Арматура 3: диаметр | missing |
| floor_slab_1_rebar_items_2_kg_per_meter | Арматура 3: вес 1 погонного метра | missing |
| floor_slab_1_rebar_items_2_waste_coeff | Арматура 3: коэффициент запаса/отходов | missing |
| floor_slab_1_rebar_items_2_rod_length_m | Арматура 3: длина одного хлыста арматуры | missing |
| floor_slab_1_rebar_items_2_unit_price_per_m | Арматура 3: цена за погонный метр | missing |
| floor_slab_1_rebar_items_3_code | Арматура 4: код позиции | missing |
| floor_slab_1_rebar_items_3_name | Арматура 4: наименование позиции | missing |
| floor_slab_1_rebar_items_3_steel_class | Арматура 4: класс стали | missing |
| floor_slab_1_rebar_items_3_diameter_mm | Арматура 4: диаметр | missing |
| floor_slab_1_rebar_items_3_source_weight_parts_kg_0 | Арматура 4: вес по спецификации, часть 1 | missing |
| floor_slab_1_rebar_items_3_source_weight_parts_kg_1 | Арматура 4: вес по спецификации, часть 2 | missing |
| floor_slab_1_rebar_items_3_source_weight_parts_kg_2 | Арматура 4: вес по спецификации, часть 3 | missing |
| floor_slab_1_rebar_items_3_kg_per_meter | Арматура 4: вес 1 погонного метра | missing |
| floor_slab_1_rebar_items_3_waste_coeff | Арматура 4: коэффициент запаса/отходов | missing |
| floor_slab_1_rebar_items_3_rod_length_m | Арматура 4: длина одного хлыста арматуры | missing |
| floor_slab_1_rebar_items_3_unit_price_per_m | Арматура 4: цена за погонный метр | missing |
| floor_slab_1_rebar_items_4_code | Арматура 5: код позиции | missing |
| floor_slab_1_rebar_items_4_name | Арматура 5: наименование позиции | missing |
| floor_slab_1_rebar_items_4_steel_class | Арматура 5: класс стали | missing |
| floor_slab_1_rebar_items_4_diameter_mm | Арматура 5: диаметр | missing |
| floor_slab_1_rebar_items_4_kg_per_meter | Арматура 5: вес 1 погонного метра | missing |
| floor_slab_1_rebar_items_4_waste_coeff | Арматура 5: коэффициент запаса/отходов | missing |
| floor_slab_1_rebar_items_4_rod_length_m | Арматура 5: длина одного хлыста арматуры | missing |
| floor_slab_1_rebar_items_4_unit_price_per_m | Арматура 5: цена за погонный метр | missing |
| floor_slab_1_rebar_items_5_code | Арматура 6: код позиции | missing |
| floor_slab_1_rebar_items_5_name | Арматура 6: наименование позиции | missing |
| floor_slab_1_rebar_items_5_steel_class | Арматура 6: класс стали | missing |
| floor_slab_1_rebar_items_5_diameter_mm | Арматура 6: диаметр | missing |
| floor_slab_1_rebar_items_5_source_weight_parts_kg_0 | Арматура 6: вес по спецификации, часть 1 | missing |
| floor_slab_1_rebar_items_5_source_weight_parts_kg_1 | Арматура 6: вес по спецификации, часть 2 | missing |
| floor_slab_1_rebar_items_5_kg_per_meter | Арматура 6: вес 1 погонного метра | missing |
| floor_slab_1_rebar_items_5_waste_coeff | Арматура 6: коэффициент запаса/отходов | missing |
| floor_slab_1_rebar_items_5_rod_length_m | Арматура 6: длина одного хлыста арматуры | missing |
| floor_slab_1_rebar_items_5_unit_price_per_m | Арматура 6: цена за погонный метр | missing |
| floor_slab_1_insulation_total_eps_volume_from_spec_m3 | total eps volume from spec m3 | missing |
| floor_slab_1_insulation_eps_thickness_m | eps thickness m | missing |
| floor_slab_1_insulation_eps_waste_coeff | eps waste coeff | missing |
| floor_slab_1_insulation_eps_pack_volume_m3 | eps pack volume m3 | missing |
| floor_slab_1_insulation_eps_unit_price_per_m3 | eps unit price per m3 | missing |
| floor_slab_1_insulation_foam_coverage_m2_per_can | foam coverage m2 per can | missing |
| floor_slab_1_insulation_foam_unit_price_per_can | foam unit price per can | missing |
| floor_slab_1_overheads_logistics_and_supply_percent | Процент логистики и снабжения | manual_required |
| floor_slab_1_overheads_consumables_and_tool_percent | Процент расходных материалов и амортизации инструмента | manual_required |
| floor_slab_1_manual_lines_formwork_delivery_trucks_override | Ручное количество машин доставки опалубки | manual_required |
| floor_slab_1_manual_lines_formwork_rebar_crane_shifts | Количество смен крана для подачи опалубки и арматуры | manual_required |
| floor_slab_1_manual_lines_concrete_pump_shifts | Количество смен бетононасоса | manual_required |
| floor_slab_1_manual_lines_technical_supervision_amount | technical supervision amount | missing |
