# Review card: Фундаментная плита

## Что система нашла
| parameter_code | value | unit | source | page | status |
|---|---:|---|---|---:|---|
| foundation_type | Ж/б плита фундамента | - | ЮСВ КР1.pdf | 6 | control_only |
| foundation_slab_thickness | 300 | мм | ЮСВ КР1.pdf | 6 | control_only |
| concrete_project_volume | 81 | м3 | ЮСВ КР1.pdf | 9 | needs_human_review |
| eps_50_under_slab_volume | 13.5 | м3 | ЮСВ КР1.pdf | 9 | needs_human_review |
| eps_100_edge_volume | 1.75 | м3 | ЮСВ КР1.pdf | 9 | needs_human_review |
| eps_150_thermal_insert_volume | 0.74 | м3 | ЮСВ КР1.pdf | 10 | needs_human_review |
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
- Подтвердить трактовку ЭППС 150 мм термовставок.
- Подтвердить, использовать ли PLANTER 320 м2 из спецификации или геометрическую площадь как контроль.

## Параметры для калькулятора
| parameter_code | calculator_input_key | status |
|---|---|---|
| concrete_project_volume | concrete_project_volume_m3 | needs_human_review |
| eps_50_under_slab_volume | eps50_under_slab_volume_m3 | needs_human_review |
| eps_100_edge_volume | eps100_edge_volume_m3 | needs_human_review |
| eps_150_thermal_insert_volume | thermal_insert_eps150_volume_m3 | needs_human_review |
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
| foundation_slab_slab_formwork_perimeter_m | slab_formwork_perimeter_m | missing |
| foundation_slab_slab_edge_height_m | slab_edge_height_m | missing |
| foundation_slab_formwork_installation_work_unit_price | formwork_installation_work_unit_price | missing |
| foundation_slab_plywood_sheet_working_area_m2 | plywood_sheet_working_area_m2 | missing |
| foundation_slab_plywood_unit_price | plywood_unit_price | missing |
| foundation_slab_timber_thickness_m | timber_thickness_m | missing |
| foundation_slab_timber_unit_price | timber_unit_price | missing |
| foundation_slab_eps50_thickness_m | eps50_thickness_m | missing |
| foundation_slab_eps50_laying_work_unit_price | eps50_laying_work_unit_price | missing |
| foundation_slab_eps_waste_coeff | eps_waste_coeff | missing |
| foundation_slab_thermal_insert_length_m | thermal_insert_length_m | missing |
| foundation_slab_thermal_insert_piece_length_m | thermal_insert_piece_length_m | missing |
| foundation_slab_thermal_insert_piece_width_m | thermal_insert_piece_width_m | missing |
| foundation_slab_thermal_insert_piece_height_m | thermal_insert_piece_height_m | missing |
| foundation_slab_thermal_insert_piece_depth_for_work_m | thermal_insert_piece_depth_for_work_m | manual_required |
| foundation_slab_thermal_insert_piece_depth_for_eps_m | thermal_insert_piece_depth_for_eps_m | manual_required |
| foundation_slab_thermal_insert_installation_work_unit_price | thermal_insert_installation_work_unit_price | missing |
| foundation_slab_eps50_pack_volume_m3 | eps50_pack_volume_m3 | missing |
| foundation_slab_eps50_unit_price | eps50_unit_price | missing |
| foundation_slab_eps100_thickness_m | eps100_thickness_m | missing |
| foundation_slab_eps100_pack_volume_m3 | eps100_pack_volume_m3 | missing |
| foundation_slab_eps100_unit_price | eps100_unit_price | missing |
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
| foundation_slab_slab_edge_height_strategy | slab_edge_height_strategy | manual_required |
| foundation_slab_box_metal_delivery_capacity_kg | box_metal_delivery_capacity_kg | missing |

## Missing / manual_required
| parameter_code | label | status |
|---|---|---|
| foundation_slab_membrane_installation_work_unit_price | membrane installation work unit price | missing |
| foundation_slab_membrane_overlap_coeff | membrane overlap coeff | missing |
| foundation_slab_membrane_roll_area_m2 | membrane roll area m2 | missing |
| foundation_slab_planter_standard_roll_unit_price | planter standard roll unit price | missing |
| foundation_slab_planterband_per_membrane_roll | planterband per membrane roll | missing |
| foundation_slab_planterband_unit_price | planterband unit price | missing |
| foundation_slab_slab_formwork_perimeter_m | slab formwork perimeter m | missing |
| foundation_slab_slab_edge_height_m | slab edge height m | missing |
| foundation_slab_formwork_installation_work_unit_price | formwork installation work unit price | missing |
| foundation_slab_plywood_sheet_working_area_m2 | plywood sheet working area m2 | missing |
| foundation_slab_plywood_unit_price | plywood unit price | missing |
| foundation_slab_timber_thickness_m | timber thickness m | missing |
| foundation_slab_timber_unit_price | timber unit price | missing |
| foundation_slab_eps50_thickness_m | eps50 thickness m | missing |
| foundation_slab_eps50_laying_work_unit_price | eps50 laying work unit price | missing |
| foundation_slab_eps_waste_coeff | eps waste coeff | missing |
| foundation_slab_thermal_insert_length_m | thermal insert length m | missing |
| foundation_slab_thermal_insert_piece_length_m | thermal insert piece length m | missing |
| foundation_slab_thermal_insert_piece_width_m | thermal insert piece width m | missing |
| foundation_slab_thermal_insert_piece_height_m | thermal insert piece height m | missing |
| foundation_slab_thermal_insert_piece_depth_for_work_m | thermal insert piece depth for work m | manual_required |
| foundation_slab_thermal_insert_piece_depth_for_eps_m | thermal insert piece depth for eps m | manual_required |
| foundation_slab_thermal_insert_installation_work_unit_price | thermal insert installation work unit price | missing |
| foundation_slab_eps50_pack_volume_m3 | eps50 pack volume m3 | missing |
| foundation_slab_eps50_unit_price | eps50 unit price | missing |
| foundation_slab_eps100_thickness_m | eps100 thickness m | missing |
| foundation_slab_eps100_pack_volume_m3 | eps100 pack volume m3 | missing |
| foundation_slab_eps100_unit_price | eps100 unit price | missing |
| foundation_slab_rebar_crane_shifts | rebar crane shifts | manual_required |
| foundation_slab_rebar_crane_unit_price | rebar crane unit price | missing |
| foundation_slab_rebar_waste_coeff | rebar waste coeff | missing |
| foundation_slab_rebar_items_0_code | code | missing |
| foundation_slab_rebar_items_0_name | name | missing |
| foundation_slab_rebar_items_0_steel_class | steel class | missing |
| foundation_slab_rebar_items_0_diameter_mm | diameter mm | missing |
| foundation_slab_rebar_items_0_weight_parts_kg_0 | weight parts kg | missing |
| foundation_slab_rebar_items_0_kg_per_meter | kg per meter | missing |
| foundation_slab_rebar_items_0_rod_length_m | rod length m | missing |
| foundation_slab_rebar_items_0_unit_price_per_m | unit price per m | missing |
| foundation_slab_rebar_items_1_code | code | missing |
| foundation_slab_rebar_items_1_name | name | missing |
| foundation_slab_rebar_items_1_steel_class | steel class | missing |
| foundation_slab_rebar_items_1_diameter_mm | diameter mm | missing |
| foundation_slab_rebar_items_1_weight_parts_kg_0 | weight parts kg | missing |
| foundation_slab_rebar_items_1_weight_parts_kg_1 | weight parts kg | missing |
| foundation_slab_rebar_items_1_kg_per_meter | kg per meter | missing |
| foundation_slab_rebar_items_1_rod_length_m | rod length m | missing |
| foundation_slab_rebar_items_1_unit_price_per_m | unit price per m | missing |
| foundation_slab_rebar_items_2_code | code | missing |
| foundation_slab_rebar_items_2_name | name | missing |
| foundation_slab_rebar_items_2_steel_class | steel class | missing |
| foundation_slab_rebar_items_2_diameter_mm | diameter mm | missing |
| foundation_slab_rebar_items_2_weight_parts_kg_0 | weight parts kg | missing |
| foundation_slab_rebar_items_2_kg_per_meter | kg per meter | missing |
| foundation_slab_rebar_items_2_rod_length_m | rod length m | missing |
| foundation_slab_rebar_items_2_unit_price_per_m | unit price per m | missing |
| foundation_slab_rebar_items_3_code | code | missing |
| foundation_slab_rebar_items_3_name | name | missing |
| foundation_slab_rebar_items_3_steel_class | steel class | missing |
| foundation_slab_rebar_items_3_diameter_mm | diameter mm | missing |
| foundation_slab_rebar_items_3_weight_parts_kg_0 | weight parts kg | missing |
| foundation_slab_rebar_items_3_kg_per_meter | kg per meter | missing |
| foundation_slab_rebar_items_3_rod_length_m | rod length m | missing |
| foundation_slab_rebar_items_3_unit_price_per_m | unit price per m | missing |
| foundation_slab_rebar_metal_delivery_trucks | rebar metal delivery trucks | missing |
| foundation_slab_rebar_metal_delivery_unit_price | rebar metal delivery unit price | missing |
| foundation_slab_box_total_metal_weight_kg | box total metal weight kg | missing |
| foundation_slab_concreting_work_unit_price | concreting work unit price | missing |
| foundation_slab_concrete_waste_coeff | concrete waste coeff | missing |
| foundation_slab_concrete_round_step_m3 | concrete round step m3 | missing |
| foundation_slab_concrete_unit_price | concrete unit price | missing |
| foundation_slab_concrete_mixer_volume_m3 | concrete mixer volume m3 | missing |
| foundation_slab_concrete_delivery_unit_price | concrete delivery unit price | missing |
| foundation_slab_concrete_pump_shifts | concrete pump shifts | manual_required |
| foundation_slab_concrete_pump_unit_price | concrete pump unit price | missing |
| foundation_slab_formwork_dismantling_work_unit_price | formwork dismantling work unit price | missing |
| foundation_slab_logistics_and_supply_amount | logistics and supply amount | missing |
| foundation_slab_consumables_tool_amortization_amount | consumables tool amortization amount | missing |
| foundation_slab_technical_supervision_amount | technical supervision amount | missing |
| foundation_slab_plywood_calc_method | plywood calc method | manual_required |
| foundation_slab_plywood_sheet_width_m | plywood sheet width m | missing |
| foundation_slab_plywood_sheet_height_m | plywood sheet height m | missing |
| foundation_slab_plywood_waste_coeff | plywood waste coeff | missing |
| foundation_slab_slab_edge_height_strategy | slab edge height strategy | manual_required |
| foundation_slab_box_metal_delivery_capacity_kg | box metal delivery capacity kg | missing |
