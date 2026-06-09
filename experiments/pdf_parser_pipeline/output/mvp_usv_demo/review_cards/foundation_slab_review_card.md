# Review card: Фундаментная плита

## Что система нашла
| parameter_code | value | unit | source | page | status |
|---|---:|---|---|---:|---|
| foundation_type | Ж/б плита фундамента | - | ЮСВ КР1.pdf | 6 | control_only |
| foundation_slab_thickness | 300 | мм | ЮСВ КР1.pdf | 6 | control_only |
| concrete_project_volume | 81 | м3 | ЮСВ КР1.pdf | 9 | needs_human_review |
| eps_50_under_slab_volume | 13.5 | м3 | ЮСВ КР1.pdf | 9 | needs_human_review |
| eps_100_edge_volume | 1.75 | м3 | ЮСВ КР1.pdf | 9 | needs_human_review |
| rebar_a500c_d12_main_grid_weight | 5276 | кг | ЮСВ КР1.pdf | 9 | needs_human_review |
| rebar_a500c_d12_thermal_insert_weight | 122 | кг | ЮСВ КР1.pdf | 10 | needs_human_review |
| rebar_a500c_d10_weight | 1078 | кг | ЮСВ КР1.pdf | 9 | needs_human_review |
| rebar_a500c_d16_thermal_insert_weight | 328 | кг | ЮСВ КР1.pdf | 10 | needs_human_review |
| rebar_a240_d6_thermal_insert_weight | 35 | кг | ЮСВ КР1.pdf | 10 | needs_human_review |
| sand_volume | 96.6 | м3 | ЮСВ КР1.pdf | 8 | needs_human_review |
| geotextile_area | 320 | м2 | ЮСВ КР1.pdf | 8 | needs_human_review |
| planter_membrane_area | 320 | м2 | ЮСВ КР1.pdf | 8 | needs_human_review |
| foundation_section_levels | 0,000 -0,500 -0,200 | отм. | ЮСВ КР1.pdf | 6 | control_only |

## Что проверить Елене
- Подтвердить, что бетон 81 м3 относится к нужному объему для калькулятора фундаментной плиты.
- Подтвердить готовую площадь опалубки бортов фундаментной плиты по спецификации.
- Подтвердить длины и материал термовставок 50 мм и 100 мм по спецификации.
- Подтвердить, использовать ли PLANTER 320 м2 из спецификации или геометрическую площадь как контроль.

## Параметры для калькулятора
| parameter_code | calculator_input_key | status |
|---|---|---|
| concrete_project_volume | concrete_project_volume_m3 | needs_human_review |
| eps_50_under_slab_volume | eps50_under_slab_volume_m3 | needs_human_review |
| eps_100_edge_volume | eps100_edge_volume_m3 | needs_human_review |
| formwork_calc_method | formwork_calc_method | missing |
| slab_side_formwork_area | slab_side_formwork_area_m2 | missing |
| thermal_insert_mode | thermal_insert_mode | missing |
| thermal_insert_50_length | thermal_insert_50_length_m | missing |
| thermal_insert_100_length | thermal_insert_100_length_m | missing |
| thermal_insert_50_material_spec_qty | thermal_insert_50_material_spec_qty | missing |
| thermal_insert_100_material_spec_qty | thermal_insert_100_material_spec_qty | missing |
| thermal_insert_material_waste_coeff | thermal_insert_material_waste_coeff | missing |
| thermal_insert_50_pack_multiple_qty | thermal_insert_50_pack_multiple_qty | missing |
| thermal_insert_100_pack_multiple_qty | thermal_insert_100_pack_multiple_qty | missing |
| thermal_insert_50_work_unit_price | thermal_insert_50_work_unit_price | missing |
| thermal_insert_100_work_unit_price | thermal_insert_100_work_unit_price | missing |
| thermal_insert_50_material_unit_price | thermal_insert_50_material_unit_price | missing |
| thermal_insert_100_material_unit_price | thermal_insert_100_material_unit_price | missing |
| rebar_a500c_d12_main_grid_weight | rebar_items[1].weight_parts_kg | needs_human_review |
| rebar_a500c_d12_thermal_insert_weight | rebar_items[1].weight_parts_kg | needs_human_review |
| rebar_a500c_d10_weight | rebar_items[2].weight_parts_kg | needs_human_review |
| rebar_a500c_d16_thermal_insert_weight | rebar_items[0].weight_parts_kg | needs_human_review |
| rebar_a240_d6_thermal_insert_weight | rebar_items[3].weight_parts_kg | needs_human_review |
| sand_volume | earthworks.sand_base_volume_m3 | needs_human_review |
| geotextile_area | earthworks.geotextile_area_m2 | needs_human_review |
| planter_membrane_area | membrane_area_m2 | needs_human_review |
| foundation_slab_membrane_installation_work_unit_price | membrane_installation_work_unit_price | missing |
| foundation_slab_membrane_overlap_coeff | membrane_overlap_coeff | missing |
| foundation_slab_membrane_roll_area_m2 | membrane_roll_area_m2 | missing |
| foundation_slab_planter_standard_roll_unit_price | planter_standard_roll_unit_price | missing |
| foundation_slab_planterband_per_membrane_roll | planterband_per_membrane_roll | missing |
| foundation_slab_planterband_unit_price | planterband_unit_price | missing |
| foundation_slab_formwork_installation_work_unit_price | formwork_installation_work_unit_price | missing |
| foundation_slab_plywood_sheet_working_area_m2 | plywood_sheet_working_area_m2 | missing |
| foundation_slab_plywood_unit_price | plywood_unit_price | missing |
| foundation_slab_timber_thickness_m | timber_thickness_m | missing |
| foundation_slab_timber_unit_price | timber_unit_price | missing |
| foundation_slab_eps50_thickness_m | eps50_thickness_m | missing |
| foundation_slab_eps50_laying_work_unit_price | eps50_laying_work_unit_price | missing |
| foundation_slab_eps_waste_coeff | eps_waste_coeff | missing |
| foundation_slab_eps50_pack_volume_m3 | eps50_pack_volume_m3 | missing |
| foundation_slab_eps50_unit_price | eps50_unit_price | missing |
| foundation_slab_rebar_crane_shifts | rebar_crane_shifts | manual_required |
| foundation_slab_rebar_crane_unit_price | rebar_crane_unit_price | missing |
| foundation_slab_rebar_waste_coeff | rebar_waste_coeff | missing |
| foundation_slab_rebar_items_0_code | rebar_items[0].code | missing |
| foundation_slab_rebar_items_0_name | rebar_items[0].name | missing |
| foundation_slab_rebar_items_0_steel_class | rebar_items[0].steel_class | missing |
| foundation_slab_rebar_items_0_diameter_mm | rebar_items[0].diameter_mm | missing |
| foundation_slab_rebar_items_0_weight_parts_kg_0 | rebar_items[0].weight_parts_kg[0] | missing |
| foundation_slab_rebar_items_0_kg_per_meter | rebar_items[0].kg_per_meter | missing |
| foundation_slab_rebar_items_0_rod_length_m | rebar_items[0].rod_length_m | missing |
| foundation_slab_rebar_items_0_unit_price_per_m | rebar_items[0].unit_price_per_m | missing |
| foundation_slab_rebar_items_1_code | rebar_items[1].code | missing |
| foundation_slab_rebar_items_1_name | rebar_items[1].name | missing |
| foundation_slab_rebar_items_1_steel_class | rebar_items[1].steel_class | missing |
| foundation_slab_rebar_items_1_diameter_mm | rebar_items[1].diameter_mm | missing |
| foundation_slab_rebar_items_1_weight_parts_kg_0 | rebar_items[1].weight_parts_kg[0] | missing |
| foundation_slab_rebar_items_1_weight_parts_kg_1 | rebar_items[1].weight_parts_kg[1] | missing |
| foundation_slab_rebar_items_1_kg_per_meter | rebar_items[1].kg_per_meter | missing |
| foundation_slab_rebar_items_1_rod_length_m | rebar_items[1].rod_length_m | missing |
| foundation_slab_rebar_items_1_unit_price_per_m | rebar_items[1].unit_price_per_m | missing |
| foundation_slab_rebar_items_2_code | rebar_items[2].code | missing |
| foundation_slab_rebar_items_2_name | rebar_items[2].name | missing |
| foundation_slab_rebar_items_2_steel_class | rebar_items[2].steel_class | missing |
| foundation_slab_rebar_items_2_diameter_mm | rebar_items[2].diameter_mm | missing |
| foundation_slab_rebar_items_2_weight_parts_kg_0 | rebar_items[2].weight_parts_kg[0] | missing |
| foundation_slab_rebar_items_2_kg_per_meter | rebar_items[2].kg_per_meter | missing |
| foundation_slab_rebar_items_2_rod_length_m | rebar_items[2].rod_length_m | missing |
| foundation_slab_rebar_items_2_unit_price_per_m | rebar_items[2].unit_price_per_m | missing |
| foundation_slab_rebar_items_3_code | rebar_items[3].code | missing |
| foundation_slab_rebar_items_3_name | rebar_items[3].name | missing |
| foundation_slab_rebar_items_3_steel_class | rebar_items[3].steel_class | missing |
| foundation_slab_rebar_items_3_diameter_mm | rebar_items[3].diameter_mm | missing |
| foundation_slab_rebar_items_3_weight_parts_kg_0 | rebar_items[3].weight_parts_kg[0] | missing |
| foundation_slab_rebar_items_3_kg_per_meter | rebar_items[3].kg_per_meter | missing |
| foundation_slab_rebar_items_3_rod_length_m | rebar_items[3].rod_length_m | missing |
| foundation_slab_rebar_items_3_unit_price_per_m | rebar_items[3].unit_price_per_m | missing |
| foundation_slab_rebar_metal_delivery_trucks | rebar_metal_delivery_trucks | missing |
| foundation_slab_rebar_metal_delivery_unit_price | rebar_metal_delivery_unit_price | missing |
| foundation_slab_box_total_metal_weight_kg | box_total_metal_weight_kg | missing |
| foundation_slab_concreting_work_unit_price | concreting_work_unit_price | missing |
| foundation_slab_concrete_waste_coeff | concrete_waste_coeff | missing |
| foundation_slab_concrete_round_step_m3 | concrete_round_step_m3 | missing |
| foundation_slab_concrete_unit_price | concrete_unit_price | missing |
| foundation_slab_concrete_mixer_volume_m3 | concrete_mixer_volume_m3 | missing |
| foundation_slab_concrete_delivery_unit_price | concrete_delivery_unit_price | missing |
| foundation_slab_concrete_pump_shifts | concrete_pump_shifts | manual_required |
| foundation_slab_concrete_pump_unit_price | concrete_pump_unit_price | missing |
| foundation_slab_formwork_dismantling_work_unit_price | formwork_dismantling_work_unit_price | missing |
| foundation_slab_logistics_and_supply_amount | logistics_and_supply_amount | missing |
| foundation_slab_consumables_tool_amortization_amount | consumables_tool_amortization_amount | missing |
| foundation_slab_technical_supervision_amount | technical_supervision_amount | missing |
| foundation_slab_plywood_calc_method | plywood_calc_method | manual_required |
| foundation_slab_plywood_sheet_width_m | plywood_sheet_width_m | missing |
| foundation_slab_plywood_sheet_height_m | plywood_sheet_height_m | missing |
| foundation_slab_plywood_waste_coeff | plywood_waste_coeff | missing |
| foundation_slab_box_metal_delivery_capacity_kg | box_metal_delivery_capacity_kg | missing |

## Missing / manual_required
| parameter_code | label | status |
|---|---|---|
| formwork_calc_method | Метод расчёта опалубки бортов | missing |
| slab_side_formwork_area | Площадь опалубки бортов фундаментной плиты по спецификации | missing |
| thermal_insert_mode | Метод расчёта термовставок | missing |
| thermal_insert_50_length | Длина термовставок 50 мм по спецификации | missing |
| thermal_insert_100_length | Длина термовставок 100 мм по спецификации | missing |
| thermal_insert_50_material_spec_qty | Материал термовставок 50 мм по спецификации | missing |
| thermal_insert_100_material_spec_qty | Материал термовставок 100 мм по спецификации | missing |
| thermal_insert_material_waste_coeff | Коэффициент запаса материала термовставок | missing |
| thermal_insert_50_pack_multiple_qty | Кратность упаковки материала термовставок 50 мм | missing |
| thermal_insert_100_pack_multiple_qty | Кратность упаковки материала термовставок 100 мм | missing |
| thermal_insert_50_work_unit_price | Ставка работы по термовставкам 50 мм | missing |
| thermal_insert_100_work_unit_price | Ставка работы по термовставкам 100 мм | missing |
| thermal_insert_50_material_unit_price | Цена материала термовставок 50 мм | missing |
| thermal_insert_100_material_unit_price | Цена материала термовставок 100 мм | missing |
| foundation_slab_membrane_installation_work_unit_price | membrane installation work unit price | missing |
| foundation_slab_membrane_overlap_coeff | membrane overlap coeff | missing |
| foundation_slab_membrane_roll_area_m2 | Площадь одного рулона мембраны | missing |
| foundation_slab_planter_standard_roll_unit_price | planter standard roll unit price | missing |
| foundation_slab_planterband_per_membrane_roll | Количество PLANTERBAND на один рулон мембраны | missing |
| foundation_slab_planterband_unit_price | planterband unit price | missing |
| foundation_slab_formwork_installation_work_unit_price | formwork installation work unit price | missing |
| foundation_slab_plywood_sheet_working_area_m2 | Рабочая площадь листа фанеры | missing |
| foundation_slab_plywood_unit_price | plywood unit price | missing |
| foundation_slab_timber_thickness_m | timber thickness m | missing |
| foundation_slab_timber_unit_price | timber unit price | missing |
| foundation_slab_eps50_thickness_m | eps50 thickness m | missing |
| foundation_slab_eps50_laying_work_unit_price | eps50 laying work unit price | missing |
| foundation_slab_eps_waste_coeff | eps waste coeff | missing |
| foundation_slab_eps50_pack_volume_m3 | eps50 pack volume m3 | missing |
| foundation_slab_eps50_unit_price | eps50 unit price | missing |
| foundation_slab_rebar_crane_shifts | Количество смен крана для подачи арматуры | manual_required |
| foundation_slab_rebar_crane_unit_price | rebar crane unit price | missing |
| foundation_slab_rebar_waste_coeff | rebar waste coeff | missing |
| foundation_slab_rebar_items_0_code | Арматура 1: код позиции | missing |
| foundation_slab_rebar_items_0_name | Арматура 1: наименование позиции | missing |
| foundation_slab_rebar_items_0_steel_class | Арматура 1: класс стали | missing |
| foundation_slab_rebar_items_0_diameter_mm | Арматура 1: диаметр | missing |
| foundation_slab_rebar_items_0_weight_parts_kg_0 | Арматура 1: вес по спецификации | missing |
| foundation_slab_rebar_items_0_kg_per_meter | Арматура 1: вес 1 погонного метра | missing |
| foundation_slab_rebar_items_0_rod_length_m | Арматура 1: длина одного хлыста арматуры | missing |
| foundation_slab_rebar_items_0_unit_price_per_m | Арматура 1: цена за погонный метр | missing |
| foundation_slab_rebar_items_1_code | Арматура 2: код позиции | missing |
| foundation_slab_rebar_items_1_name | Арматура 2: наименование позиции | missing |
| foundation_slab_rebar_items_1_steel_class | Арматура 2: класс стали | missing |
| foundation_slab_rebar_items_1_diameter_mm | Арматура 2: диаметр | missing |
| foundation_slab_rebar_items_1_weight_parts_kg_0 | Арматура 2: вес по спецификации | missing |
| foundation_slab_rebar_items_1_weight_parts_kg_1 | Арматура 2: вес по спецификации | missing |
| foundation_slab_rebar_items_1_kg_per_meter | Арматура 2: вес 1 погонного метра | missing |
| foundation_slab_rebar_items_1_rod_length_m | Арматура 2: длина одного хлыста арматуры | missing |
| foundation_slab_rebar_items_1_unit_price_per_m | Арматура 2: цена за погонный метр | missing |
| foundation_slab_rebar_items_2_code | Арматура 3: код позиции | missing |
| foundation_slab_rebar_items_2_name | Арматура 3: наименование позиции | missing |
| foundation_slab_rebar_items_2_steel_class | Арматура 3: класс стали | missing |
| foundation_slab_rebar_items_2_diameter_mm | Арматура 3: диаметр | missing |
| foundation_slab_rebar_items_2_weight_parts_kg_0 | Арматура 3: вес по спецификации | missing |
| foundation_slab_rebar_items_2_kg_per_meter | Арматура 3: вес 1 погонного метра | missing |
| foundation_slab_rebar_items_2_rod_length_m | Арматура 3: длина одного хлыста арматуры | missing |
| foundation_slab_rebar_items_2_unit_price_per_m | Арматура 3: цена за погонный метр | missing |
| foundation_slab_rebar_items_3_code | Арматура 4: код позиции | missing |
| foundation_slab_rebar_items_3_name | Арматура 4: наименование позиции | missing |
| foundation_slab_rebar_items_3_steel_class | Арматура 4: класс стали | missing |
| foundation_slab_rebar_items_3_diameter_mm | Арматура 4: диаметр | missing |
| foundation_slab_rebar_items_3_weight_parts_kg_0 | Арматура 4: вес по спецификации | missing |
| foundation_slab_rebar_items_3_kg_per_meter | Арматура 4: вес 1 погонного метра | missing |
| foundation_slab_rebar_items_3_rod_length_m | Арматура 4: длина одного хлыста арматуры | missing |
| foundation_slab_rebar_items_3_unit_price_per_m | Арматура 4: цена за погонный метр | missing |
| foundation_slab_rebar_metal_delivery_trucks | Количество машин доставки арматуры/металла | missing |
| foundation_slab_rebar_metal_delivery_unit_price | rebar metal delivery unit price | missing |
| foundation_slab_box_total_metal_weight_kg | Общий вес металла коробки для доставки | missing |
| foundation_slab_concreting_work_unit_price | concreting work unit price | missing |
| foundation_slab_concrete_waste_coeff | concrete waste coeff | missing |
| foundation_slab_concrete_round_step_m3 | concrete round step m3 | missing |
| foundation_slab_concrete_unit_price | concrete unit price | missing |
| foundation_slab_concrete_mixer_volume_m3 | Объем одного автобетоносмесителя | missing |
| foundation_slab_concrete_delivery_unit_price | concrete delivery unit price | missing |
| foundation_slab_concrete_pump_shifts | Количество смен бетононасоса | manual_required |
| foundation_slab_concrete_pump_unit_price | concrete pump unit price | missing |
| foundation_slab_formwork_dismantling_work_unit_price | formwork dismantling work unit price | missing |
| foundation_slab_logistics_and_supply_amount | logistics and supply amount | missing |
| foundation_slab_consumables_tool_amortization_amount | consumables tool amortization amount | missing |
| foundation_slab_technical_supervision_amount | technical supervision amount | missing |
| foundation_slab_plywood_calc_method | Метод расчета фанеры | manual_required |
| foundation_slab_plywood_sheet_width_m | Ширина листа фанеры | missing |
| foundation_slab_plywood_sheet_height_m | Высота листа фанеры | missing |
| foundation_slab_plywood_waste_coeff | plywood waste coeff | missing |
| foundation_slab_box_metal_delivery_capacity_kg | box metal delivery capacity kg | missing |
