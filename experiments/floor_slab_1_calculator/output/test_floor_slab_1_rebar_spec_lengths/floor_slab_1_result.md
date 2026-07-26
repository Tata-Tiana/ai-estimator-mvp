# Расчёт монолитной плиты перекрытия 1-го этажа: test_floor_slab_1_rebar_spec_lengths

Проект: `test_floor_slab_1_rebar_spec_lengths`

## Итоги
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total` | `1168899` |
| `internal_works_total` | `611926` |
| `internal_section_total` | `1780825` |
| `base_subtotal_raw_before_overheads` | `1707526.834518` |
| `logistics_and_supply_total` | `17075` |
| `consumables_and_tool_depreciation_total` | `51226` |
| `technical_supervision_total` | `5000` |

## Comparison Summary
- status: `ok`
- ok: `54`
- mismatch: `0`

## Расчётные блоки
| Показатель | Значение |
| --- | ---: |
| `geometry.total_concrete_volume_from_spec_m3` | `40.53` |
| `geometry.slab_thickness_m` | `0.18` |
| `geometry.slab_concrete_volume_m3_raw` | `37.3752` |
| `geometry.slab_concrete_volume_m3_display` | `37.38` |
| `geometry.slab_formwork_area_m2` | `207.64` |
| `geometry.slab_control_geometry_area_m2` | `210.64` |
| `geometry.slab_edge_perimeter_m` | `118` |
| `geometry.edge_formwork_height_m` | `0.2` |
| `beams.items` | `[{"code": "beam_b1", "name": "Б-1", "length_m": 7.0, "width_m": 0.3, "height_m": 0.25, "count": 1.0, "concrete_volume_m3": 0.525, "formwork_area_m2": 5.6}, {"code": "beam_b2", "name": "Б-2", "length_m": 7.2, "width_m": 0.3, "height_m": 0.68, "count": 1.0, "concrete_volume_m3": 1.4688, "formwork_area_m2": 11.952}, {"code": "beam_b3", "name": "Б-3", "length_m": 9.0, "width_m": 0.3, "height_m": 0.43, "count": 1.0, "concrete_volume_m3": 1.161, "formwork_area_m2": 10.44}]` |
| `beams.total_length_m` | `23.2` |
| `beams.total_concrete_volume_m3` | `3.1548` |
| `beams.total_formwork_area_m2` | `27.992` |
| `beams.concrete_volume_source` | `calculated_from_beam_items` |
| `beams.calculated_concrete_volume_m3` | `3.1548` |
| `beams.concrete_volume_delta_m3` | `None` |
| `formwork.formwork_areas_calc_method` | `legacy_calculated_from_geometry` |
| `formwork.formwork_areas_source` | `legacy_calculated_from_geometry` |
| `formwork.main_formwork_area_m2` | `207.64` |
| `formwork.slab_formwork_area_m2` | `207.64` |
| `formwork.edge_formwork_area_m2` | `23.6` |
| `formwork.beams_formwork_area_m2` | `27.992` |
| `formwork.edge_and_beam_formwork_area_combined_m2` | `None` |
| `formwork.edge_and_beam_formwork_area_m2` | `51.592` |
| `formwork.calculated_main_formwork_area_m2` | `207.64` |
| `formwork.calculated_edge_formwork_area_m2` | `23.6` |
| `formwork.calculated_beams_formwork_area_m2` | `27.992` |
| `formwork.main_formwork_area_delta_m2` | `0.0` |
| `formwork.edge_formwork_area_delta_m2` | `0.0` |
| `formwork.beams_formwork_area_delta_m2` | `0.0` |
| `formwork.excel_rate_per_m2` | `600.0` |
| `formwork.formwork_delivery_calc_method` | `area_threshold` |
| `formwork.formwork_delivery_area_source_m2` | `207.64` |
| `formwork.formwork_delivery_threshold_m2` | `180.0` |
| `formwork.formwork_delivery_trucks` | `4.0` |
| `formwork.formwork_delivery_breakdown` | `2 привоза + 2 вывоза` |
| `formwork.formwork_delivery_status` | `calculated` |
| `formwork.formwork_delivery_note` | `До 180 м2 включительно: 1 привоз + 1 вывоз = 2 машины; более 180 м2: 2 привоза + 2 вывоза = 4 машины.` |
| `formwork_rate_context.formwork_rate_calc_method` | `direct_section_rate` |
| `formwork_rate_context.formwork_rate_per_m2` | `600.0` |
| `formwork_rate_context.box_level_quote_context_used` | `False` |
| `plywood_and_timber.beams_bottom_formwork_area_m2` | `0.0` |
| `plywood_and_timber.edge_beam_formwork_area_for_materials_m2` | `51.592` |
| `plywood_and_timber.edge_and_beam_plywood_sheets_raw` | `22.431304` |
| `plywood_and_timber.non_multiple_places_area_m2` | `41.528` |
| `plywood_and_timber.non_multiple_places_plywood_sheets_raw` | `18.055652` |
| `plywood_and_timber.base_plywood_sheets_raw` | `40.486957` |
| `plywood_and_timber.order_plywood_sheets_raw` | `50.486957` |
| `plywood_and_timber.order_plywood_sheets` | `51` |
| `plywood_and_timber.overhang_sheet_equivalent` | `24.193478` |
| `plywood_and_timber.base_timber_volume_m3` | `2.5796` |
| `plywood_and_timber.additional_timber_volume_m3` | `0.211246` |
| `plywood_and_timber.timber_volume_m3_raw` | `2.790846` |
| `rebar.rebar_calc_method` | `spec_length_items` |
| `rebar.items` | `[{"code": "rebar_a500_d25", "name": "Арматура класса A500 диаметром 25 мм", "steel_class": "A500", "diameter_mm": 25, "floor": 1, "component": "floor_slab_1", "spec_length_m": 46.8, "kg_per_meter": 3.85, "base_length_m": 46.8, "waste_coeff": 1.05, "length_with_waste_m": 49.14, "weight_with_waste_kg_display": 189.19, "rod_length_m": 11.7, "rods": 5, "rods_ordered": 5, "order_length_m": 58.5, "delivery_weight_kg": 225.225, "unit_price_per_m": 196.35, "material_total_raw": 11486.475, "material_total": 11486}, {"code": "rebar_a500_d16", "name": "Арматура класса A500 диаметром 16 мм", "steel_class": "A500", "diameter_mm": 16, "floor": 1, "component": "floor_slab_1", "spec_length_m": 81.9, "kg_per_meter": 1.58, "base_length_m": 81.9, "waste_coeff": 1.05, "length_with_waste_m": 85.995, "weight_with_waste_kg_display": 135.87, "rod_length_m": 11.7, "rods": 8, "rods_ordered": 8, "order_length_m": 93.6, "delivery_weight_kg": 147.888, "unit_price_per_m": 80.58, "material_total_raw": 7542.288, "material_total": 7542}, {"code": "rebar_a500_d12", "name": "Арматура класса A500 диаметром 12 мм", "steel_class": "A500", "diameter_mm": 12, "floor": 1, "component": "floor_slab_1", "spec_length_m": 58.5, "kg_per_meter": 0.888, "base_length_m": 58.5, "waste_coeff": 1.05, "length_with_waste_m": 61.425, "weight_with_waste_kg_display": 54.55, "rod_length_m": 11.7, "rods": 6, "rods_ordered": 6, "order_length_m": 70.2, "delivery_weight_kg": 62.3376, "unit_price_per_m": 45.29, "material_total_raw": 3179.358, "material_total": 3179}, {"code": "rebar_a500_d10", "name": "Арматура класса A500 диаметром 10 мм", "steel_class": "A500", "diameter_mm": 10, "floor": 1, "component": "floor_slab_1", "spec_length_m": 6879.6, "kg_per_meter": 0.617, "base_length_m": 6879.6, "waste_coeff": 1.05, "length_with_waste_m": 7223.58, "weight_with_waste_kg_display": 4456.95, "rod_length_m": 11.7, "rods": 618, "rods_ordered": 618, "order_length_m": 7230.6, "delivery_weight_kg": 4461.2802, "unit_price_per_m": 32.72, "material_total_raw": 236585.232, "material_total": 236585}, {"code": "rebar_a240_d8", "name": "Арматура класса A240 диаметром 8 мм", "steel_class": "A240", "diameter_mm": 8, "floor": 1, "component": "floor_slab_1", "spec_length_m": 48.0, "kg_per_meter": 0.395, "base_length_m": 48.0, "waste_coeff": 1.05, "length_with_waste_m": 50.4, "weight_with_waste_kg_display": 19.91, "rod_length_m": 6.0, "rods": 9, "rods_ordered": 9, "order_length_m": 54.0, "delivery_weight_kg": 21.33, "unit_price_per_m": 24.0, "material_total_raw": 1296.0, "material_total": 1296}, {"code": "rebar_a240_d6", "name": "Арматура класса A240 диаметром 6 мм", "steel_class": "A240", "diameter_mm": 6, "floor": 1, "component": "floor_slab_1", "spec_length_m": 180.0, "kg_per_meter": 0.222, "base_length_m": 180.0, "waste_coeff": 1.05, "length_with_waste_m": 189.0, "weight_with_waste_kg_display": 41.96, "rod_length_m": 6.0, "rods": 32, "rods_ordered": 32, "order_length_m": 192.0, "delivery_weight_kg": 42.624, "unit_price_per_m": 13.32, "material_total_raw": 2557.44, "material_total": 2557}]` |
| `rebar.item_controls_by_code.rebar_a500_d25.code` | `rebar_a500_d25` |
| `rebar.item_controls_by_code.rebar_a500_d25.name` | `Арматура класса A500 диаметром 25 мм` |
| `rebar.item_controls_by_code.rebar_a500_d25.steel_class` | `A500` |
| `rebar.item_controls_by_code.rebar_a500_d25.diameter_mm` | `25` |
| `rebar.item_controls_by_code.rebar_a500_d25.floor` | `1` |
| `rebar.item_controls_by_code.rebar_a500_d25.component` | `floor_slab_1` |
| `rebar.item_controls_by_code.rebar_a500_d25.spec_length_m` | `46.8` |
| `rebar.item_controls_by_code.rebar_a500_d25.base_length_m` | `46.8` |
| `rebar.item_controls_by_code.rebar_a500_d25.length_with_waste_m` | `49.14` |
| `rebar.item_controls_by_code.rebar_a500_d25.rods` | `5` |
| `rebar.item_controls_by_code.rebar_a500_d25.order_length_m` | `58.5` |
| `rebar.item_controls_by_code.rebar_a500_d25.delivery_weight_kg` | `225.225` |
| `rebar.item_controls_by_code.rebar_a500_d25.material_total_raw` | `11486.475` |
| `rebar.item_controls_by_code.rebar_a500_d16.code` | `rebar_a500_d16` |
| `rebar.item_controls_by_code.rebar_a500_d16.name` | `Арматура класса A500 диаметром 16 мм` |
| `rebar.item_controls_by_code.rebar_a500_d16.steel_class` | `A500` |
| `rebar.item_controls_by_code.rebar_a500_d16.diameter_mm` | `16` |
| `rebar.item_controls_by_code.rebar_a500_d16.floor` | `1` |
| `rebar.item_controls_by_code.rebar_a500_d16.component` | `floor_slab_1` |
| `rebar.item_controls_by_code.rebar_a500_d16.spec_length_m` | `81.9` |
| `rebar.item_controls_by_code.rebar_a500_d16.base_length_m` | `81.9` |
| `rebar.item_controls_by_code.rebar_a500_d16.length_with_waste_m` | `85.995` |
| `rebar.item_controls_by_code.rebar_a500_d16.rods` | `8` |
| `rebar.item_controls_by_code.rebar_a500_d16.order_length_m` | `93.6` |
| `rebar.item_controls_by_code.rebar_a500_d16.delivery_weight_kg` | `147.888` |
| `rebar.item_controls_by_code.rebar_a500_d16.material_total_raw` | `7542.288` |
| `rebar.item_controls_by_code.rebar_a500_d12.code` | `rebar_a500_d12` |
| `rebar.item_controls_by_code.rebar_a500_d12.name` | `Арматура класса A500 диаметром 12 мм` |
| `rebar.item_controls_by_code.rebar_a500_d12.steel_class` | `A500` |
| `rebar.item_controls_by_code.rebar_a500_d12.diameter_mm` | `12` |
| `rebar.item_controls_by_code.rebar_a500_d12.floor` | `1` |
| `rebar.item_controls_by_code.rebar_a500_d12.component` | `floor_slab_1` |
| `rebar.item_controls_by_code.rebar_a500_d12.spec_length_m` | `58.5` |
| `rebar.item_controls_by_code.rebar_a500_d12.base_length_m` | `58.5` |
| `rebar.item_controls_by_code.rebar_a500_d12.length_with_waste_m` | `61.425` |
| `rebar.item_controls_by_code.rebar_a500_d12.rods` | `6` |
| `rebar.item_controls_by_code.rebar_a500_d12.order_length_m` | `70.2` |
| `rebar.item_controls_by_code.rebar_a500_d12.delivery_weight_kg` | `62.3376` |
| `rebar.item_controls_by_code.rebar_a500_d12.material_total_raw` | `3179.358` |
| `rebar.item_controls_by_code.rebar_a500_d10.code` | `rebar_a500_d10` |
| `rebar.item_controls_by_code.rebar_a500_d10.name` | `Арматура класса A500 диаметром 10 мм` |
| `rebar.item_controls_by_code.rebar_a500_d10.steel_class` | `A500` |
| `rebar.item_controls_by_code.rebar_a500_d10.diameter_mm` | `10` |
| `rebar.item_controls_by_code.rebar_a500_d10.floor` | `1` |
| `rebar.item_controls_by_code.rebar_a500_d10.component` | `floor_slab_1` |
| `rebar.item_controls_by_code.rebar_a500_d10.spec_length_m` | `6879.6` |
| `rebar.item_controls_by_code.rebar_a500_d10.base_length_m` | `6879.6` |
| `rebar.item_controls_by_code.rebar_a500_d10.length_with_waste_m` | `7223.58` |
| `rebar.item_controls_by_code.rebar_a500_d10.rods` | `618` |
| `rebar.item_controls_by_code.rebar_a500_d10.order_length_m` | `7230.6` |
| `rebar.item_controls_by_code.rebar_a500_d10.delivery_weight_kg` | `4461.2802` |
| `rebar.item_controls_by_code.rebar_a500_d10.material_total_raw` | `236585.232` |
| `rebar.item_controls_by_code.rebar_a240_d8.code` | `rebar_a240_d8` |
| `rebar.item_controls_by_code.rebar_a240_d8.name` | `Арматура класса A240 диаметром 8 мм` |
| `rebar.item_controls_by_code.rebar_a240_d8.steel_class` | `A240` |
| `rebar.item_controls_by_code.rebar_a240_d8.diameter_mm` | `8` |
| `rebar.item_controls_by_code.rebar_a240_d8.floor` | `1` |
| `rebar.item_controls_by_code.rebar_a240_d8.component` | `floor_slab_1` |
| `rebar.item_controls_by_code.rebar_a240_d8.spec_length_m` | `48.0` |
| `rebar.item_controls_by_code.rebar_a240_d8.base_length_m` | `48.0` |
| `rebar.item_controls_by_code.rebar_a240_d8.length_with_waste_m` | `50.4` |
| `rebar.item_controls_by_code.rebar_a240_d8.rods` | `9` |
| `rebar.item_controls_by_code.rebar_a240_d8.order_length_m` | `54.0` |
| `rebar.item_controls_by_code.rebar_a240_d8.delivery_weight_kg` | `21.33` |
| `rebar.item_controls_by_code.rebar_a240_d8.material_total_raw` | `1296.0` |
| `rebar.item_controls_by_code.rebar_a240_d6.code` | `rebar_a240_d6` |
| `rebar.item_controls_by_code.rebar_a240_d6.name` | `Арматура класса A240 диаметром 6 мм` |
| `rebar.item_controls_by_code.rebar_a240_d6.steel_class` | `A240` |
| `rebar.item_controls_by_code.rebar_a240_d6.diameter_mm` | `6` |
| `rebar.item_controls_by_code.rebar_a240_d6.floor` | `1` |
| `rebar.item_controls_by_code.rebar_a240_d6.component` | `floor_slab_1` |
| `rebar.item_controls_by_code.rebar_a240_d6.spec_length_m` | `180.0` |
| `rebar.item_controls_by_code.rebar_a240_d6.base_length_m` | `180.0` |
| `rebar.item_controls_by_code.rebar_a240_d6.length_with_waste_m` | `189.0` |
| `rebar.item_controls_by_code.rebar_a240_d6.rods` | `32` |
| `rebar.item_controls_by_code.rebar_a240_d6.order_length_m` | `192.0` |
| `rebar.item_controls_by_code.rebar_a240_d6.delivery_weight_kg` | `42.624` |
| `rebar.item_controls_by_code.rebar_a240_d6.material_total_raw` | `2557.44` |
| `rebar.rebar_frame_assembly_quantity_m` | `7698.9` |
| `rebar.floor_slab_1_rebar_weight_with_waste_kg` | `4898.4` |
| `rebar.metal_delivery_calc_method` | `section_output_only` |
| `rebar.section_rebar_delivery_weight_kg` | `4960.6848` |
| `rebar.max_weight_per_truck_kg` | `10000.0` |
| `rebar.legacy_delivery_line_enabled` | `False` |
| `rebar.box_level_delivery_required` | `True` |
| `concrete.total_project_concrete_volume_m3` | `40.53` |
| `concrete.concrete_volume_with_waste_m3_raw` | `42.5565` |
| `concrete.concrete_volume_with_waste_m3_display` | `42.56` |
| `concrete.order_concrete_volume_m3` | `43` |
| `concrete.mixer_capacity_m3` | `9` |
| `concrete.concrete_delivery_trips` | `5` |
| `slab_zones.used` | `False` |
| `slab_zones.zone_count` | `0` |
| `insulation.insulation_calc_method` | `legacy_fixed_edge_length` |
| `insulation.edge_insulation_height_m` | `0.18` |
| `insulation.edge_insulation_height_source` | `specification` |
| `insulation.slab_outer_edge_length_m` | `84.8` |
| `insulation.slab_outer_edge_eps_work_length_m` | `84.8` |
| `insulation.insulated_beams_total_length_m` | `23.2` |
| `insulation.beams_eps_work_length_m` | `23.2` |
| `insulation.total_insulation_length_m` | `108.0` |
| `insulation.edge_beam_eps_work_length_m` | `108.0` |
| `insulation.slab_edge_insulation_area_m2` | `15.264` |
| `insulation.slab_edge_eps_material_area_m2` | `15.264` |
| `insulation.beams_insulation_area_m2` | `10.516` |
| `insulation.beams_eps_material_area_m2` | `10.516` |
| `insulation.edge_and_beam_insulation_area_m2` | `25.78` |
| `insulation.edge_and_beam_eps_material_area_m2` | `25.78` |
| `insulation.edge_and_beam_eps_volume_m3` | `2.578` |
| `insulation.bottom_slab_eps_volume_m3` | `5.192` |
| `insulation.bottom_slab_insulation_area_m2_raw` | `51.92` |
| `insulation.bottom_slab_eps_work_area_m2` | `51.92` |
| `insulation.total_insulation_area_m2` | `77.7` |
| `insulation.foam_base_area_m2` | `77.7` |
| `insulation.total_eps_volume_from_spec_m3` | `7.77` |
| `insulation.calculated_clean_eps_volume_m3` | `7.77` |
| `insulation.eps_volume_delta_m3` | `0.0` |
| `insulation.eps_thickness_m` | `0.1` |
| `insulation.eps_waste_coeff` | `1.05` |
| `insulation.required_eps_volume_m3_raw` | `8.1585` |
| `insulation.eps_pack_volume_m3` | `0.2773` |
| `insulation.eps_packs_raw` | `29.421204` |
| `insulation.eps_packs_ordered` | `30` |
| `insulation.order_eps_volume_m3_raw` | `8.319` |
| `insulation.foam_cans_raw` | `7.77` |
| `insulation.foam_cans_ordered` | `8` |
| `overheads.base_subtotal_raw_before_overheads` | `1707526.834518` |
| `overheads.logistics_and_supply_percent` | `0.01` |
| `overheads.logistics_and_supply_total_raw` | `17075.268345` |
| `overheads.logistics_and_supply_total` | `17075` |
| `overheads.consumables_and_tool_percent` | `0.03` |
| `overheads.consumables_and_tool_depreciation_total_raw` | `51225.805036` |
| `overheads.consumables_and_tool_depreciation_total` | `51226` |
| `manual_lines.concrete_pump_shifts` | `1` |
| `manual_lines.technical_supervision_amount` | `5000` |
| `control_metrics.control_geometry_area_m2` | `210.64` |
| `control_metrics.slab_area_used_in_estimate_m2` | `207.64` |
| `control_metrics.beam_concreting_control_total_by_length` | `46400` |
| `control_metrics.reinforcement_density_kg_per_m3` | `115.09` |

## Площади опалубки

Legacy-режим `legacy_calculated_from_geometry`: площади опалубки восстанавливаются из объёма бетона, толщины, периметра и геометрии балок.

| Показатель | Значение |
| --- | ---: |
| `formwork_areas_calc_method` | `legacy_calculated_from_geometry` |
| `formwork_areas_source` | `legacy_calculated_from_geometry` |
| `main_formwork_area_m2` | `207.64` |
| `slab_formwork_area_m2` | `207.64` |
| `edge_formwork_area_m2` | `23.6` |
| `beams_formwork_area_m2` | `27.992` |
| `edge_and_beam_formwork_area_m2` | `51.592` |
| `calculated_main_formwork_area_m2` | `207.64` |
| `calculated_edge_formwork_area_m2` | `23.6` |
| `calculated_beams_formwork_area_m2` | `27.992` |
| `main_formwork_area_delta_m2` | `0.0` |
| `edge_formwork_area_delta_m2` | `0.0` |
| `beams_formwork_area_delta_m2` | `0.0` |

## Ставка комплекта опалубки

Production-режим `direct_section_rate`: ставка опалубки взята напрямую для плиты перекрытия 1-го этажа.

Общая сумма предложения поставщика и площадь плиты 2-го этажа в этом калькуляторе не используются.

| Показатель | Значение |
| --- | ---: |
| `formwork_rate_calc_method` | `direct_section_rate` |
| `formwork_rate_per_m2` | `600.0` |
| `box_level_quote_context_used` | `False` |

## Арматура плиты перекрытия 1-го этажа

Production-режим `spec_length_items`: арматура берётся из спецификации в м.п. по классу стали и диаметру.

Формула: `length_with_waste_m = spec_length_m * waste_coeff`; `order_length_m = ceil(length_with_waste_m / rod_length_m) * rod_length_m`.

| Показатель | Значение |
| --- | ---: |
| `rebar_calc_method` | `spec_length_items` |
| `rebar_frame_assembly_quantity_m` | `7698.9` |
| `section_rebar_delivery_weight_kg` | `4960.6848` |

| code | floor | component | steel_class | diameter_mm | spec_length_m | base_length_m | length_with_waste_m | rods | order_length_m | kg_per_meter | delivery_weight_kg | price_code |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| rebar_a500_d25 | 1 | floor_slab_1 | A500 | 25 | 46.8 | 46.8 | 49.14 | 5 | 58.5 | 3.85 | 225.225 | rebar_a500_d25_m |
| rebar_a500_d16 | 1 | floor_slab_1 | A500 | 16 | 81.9 | 81.9 | 85.995 | 8 | 93.6 | 1.58 | 147.888 | rebar_a500_d16_m |
| rebar_a500_d12 | 1 | floor_slab_1 | A500 | 12 | 58.5 | 58.5 | 61.425 | 6 | 70.2 | 0.888 | 62.3376 | rebar_a500_d12_m |
| rebar_a500_d10 | 1 | floor_slab_1 | A500 | 10 | 6879.6 | 6879.6 | 7223.58 | 618 | 7230.6 | 0.617 | 4461.2802 | rebar_a500_d10_m |
| rebar_a240_d8 | 1 | floor_slab_1 | A240 | 8 | 48.0 | 48.0 | 50.4 | 9 | 54.0 | 0.395 | 21.33 | rebar_a240_d8_m |
| rebar_a240_d6 | 1 | floor_slab_1 | A240 | 6 | 180.0 | 180.0 | 189.0 | 32 | 192.0 | 0.222 | 42.624 | rebar_a240_d6_m |

## Доставка арматуры и металла

Production-режим `section_output_only`: калькулятор плиты 1-го этажа отдаёт только вес закупочной арматуры текущего раздела.

Количество машин доставки металла считается выше, на уровне `box_calculator`, по суммарному весу металла коробки.

| Показатель | Значение |
| --- | ---: |
| `metal_delivery_calc_method` | `section_output_only` |
| `section_rebar_delivery_weight_kg` | `4960.6848` |
| `max_weight_per_truck_kg` | `10000.0` |
| `legacy_delivery_line_enabled` | `False` |
| `box_level_delivery_required` | `True` |

## Утепление плиты

Legacy-режим `legacy_fixed_edge_length`: утепление рассчитано по фиксированной длине торца (не из реального проекта) для сохранения старых регресс-кейсов.

| Показатель | Значение |
| --- | ---: |
| `insulation_calc_method` | `legacy_fixed_edge_length` |
| `slab_outer_edge_eps_work_length_m` | `84.8` |
| `beams_eps_work_length_m` | `23.2` |
| `edge_beam_eps_work_length_m` | `108.0` |
| `slab_edge_eps_material_area_m2` | `15.264` |
| `beams_eps_material_area_m2` | `10.516` |
| `edge_and_beam_eps_material_area_m2` | `25.78` |
| `bottom_slab_eps_work_area_m2` | `51.92` |
| `total_eps_volume_from_spec_m3` | `7.77` |
| `calculated_clean_eps_volume_m3` | `7.77` |
| `eps_volume_delta_m3` | `0.0` |
| `eps_waste_coeff` | `1.05` |
| `required_eps_volume_m3_raw` | `8.1585` |
| `eps_pack_volume_m3` | `0.2773` |
| `eps_packs_raw` | `29.421204` |
| `eps_packs_ordered` | `30` |
| `order_eps_volume_m3_raw` | `8.319` |
| `foam_cans_ordered` | `8` |

## Строки серой внутренней сметы
| code | name | quantity_raw | quantity_display | unit | line_type | material_total_raw | material_total | work_total_raw | work_total | line_total_raw | line_total |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `slab_formwork_installation_control` | Монтаж опалубки под монолитное перекрытие 1-го этажа | `207.64` | `207.64` | `м2` | `zero_control_line` | `0.0` | `0` | `0.0` | `0` | `0.0` | `0` |
| `formwork_set_rental_material` | Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые) | `207.64` | `207.64` | `м2` | `materials` | `124584.0` | `124584` | `0.0` | `0` | `124584.0` | `124584` |
| `formwork_delivery_return_manipulator` | Доставка, вывоз опалубки манипулятором | `4.0` | `4.0` | `маш` | `logistics_machinery` | `80000.0` | `80000` | `0.0` | `0` | `80000.0` | `80000` |
| `formwork_rebar_crane_supply` | Подача опалубки, арматуры автокраном | `2.0` | `2.0` | `смена` | `machinery` | `60000.0` | `60000` | `0.0` | `0` | `60000.0` | `60000` |
| `formwork_consumables` | Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки) | `1.0` | `1.0` | `-` | `materials_consumables` | `9759.08` | `9759` | `0.0` | `0` | `9759.08` | `9759` |
| `edge_beam_formwork_installation_control` | Монтаж опалубки из доски 50 мм и фанеры для устройства балок, для отбортовки плиты | `51.592` | `51.59` | `м2` | `zero_control_line` | `0.0` | `0` | `0.0` | `0` | `0.0` | `0` |
| `plywood_fk_18mm_for_edges_and_non_multiple_places` | Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов | `51.0` | `51.0` | `шт` | `materials` | `73950.0` | `73950` | `0.0` | `0` | `73950.0` | `73950` |
| `formwork_timber_gost` | Пиломатериал обрезной для устройства опалубки ГОСТ | `2.790846` | `2.79` | `м3` | `materials` | `60003.181518` | `60003` | `0.0` | `0` | `60003.181518` | `60003` |
| `floor_slab_rebar_frame_assembly_control` | Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры (в том числе балок) | `7698.9` | `7698.9` | `мп` | `zero_control_line` | `0.0` | `0` | `0.0` | `0` | `0.0` | `0` |
| `rebar_a500_d25` | Арматура класса A500 диаметром 25 мм | `58.5` | `58.5` | `мп` | `materials` | `11486.475` | `11486` | `0.0` | `0` | `11486.475` | `11486` |
| `rebar_a500_d16` | Арматура класса A500 диаметром 16 мм | `93.6` | `93.6` | `мп` | `materials` | `7542.288` | `7542` | `0.0` | `0` | `7542.288` | `7542` |
| `rebar_a500_d12` | Арматура класса A500 диаметром 12 мм | `70.2` | `70.2` | `мп` | `materials` | `3179.358` | `3179` | `0.0` | `0` | `3179.358` | `3179` |
| `rebar_a500_d10` | Арматура класса A500 диаметром 10 мм | `7230.6` | `7230.6` | `мп` | `materials` | `236585.232` | `236585` | `0.0` | `0` | `236585.232` | `236585` |
| `rebar_a240_d8` | Арматура класса A240 диаметром 8 мм | `54.0` | `54.0` | `мп` | `materials` | `1296.0` | `1296` | `0.0` | `0` | `1296.0` | `1296` |
| `rebar_a240_d6` | Арматура класса A240 диаметром 6 мм | `192.0` | `192.0` | `мп` | `materials` | `2557.44` | `2557` | `0.0` | `0` | `2557.44` | `2557` |
| `floor_slab_concreting_work` | Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300) | `37.3752` | `37.38` | `м3` | `work` | `0.0` | `0` | `448502.4` | `448502` | `448502.4` | `448502` |
| `beam_concreting_work` | Бетонирование балки бетоном марки В22,5 (М300) | `3.1548` | `3.15` | `м3` | `work` | `0.0` | `0` | `63096.0` | `63096` | `63096.0` | `63096` |
| `concrete_b22_5_m300_material` | Бетон марки В22,5 (М300) | `43.0` | `43.0` | `м3` | `materials` | `275200.0` | `275200` | `0.0` | `0` | `275200.0` | `275200` |
| `concrete_delivery` | Доставка бетона до объекта | `5.0` | `5.0` | `рейс` | `logistics_machinery` | `37500.0` | `37500` | `0.0` | `0` | `37500.0` | `37500` |
| `concrete_pump_32m` | Работа бетононасоса 32м + гаситель | `1.0` | `1.0` | `смена` | `machinery_fixed` | `38000.0` | `38000` | `0.0` | `0` | `38000.0` | `38000` |
| `formwork_dismantling_zero_internal` | Демонтаж опалубки после завершения бетонирования | `207.64` | `207.6` | `м2` | `client_only_zero_internal_line` | `0.0` | `0` | `0.0` | `0` | `0.0` | `0` |
| `edge_beam_insulation_work` | Устройство утепления по наружной стороне торцов плиты, балок | `108.0` | `108.0` | `мп` | `work` | `0.0` | `0` | `48600.0` | `48600` | `48600.0` | `48600` |
| `bottom_slab_insulation_work` | Устройство утепления низа плиты | `51.92` | `51.9` | `м2` | `work` | `0.0` | `0` | `46728.0` | `46728` | `46728.0` | `46728` |
| `eps_penoplex_osnova_100mm` | Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм | `8.319` | `8.32` | `м3` | `materials` | `75037.38` | `75037` | `0.0` | `0` | `75037.38` | `75037` |
| `eps_glue_foam` | Клей-пена для ЭППС | `8.0` | `8.0` | `баллон` | `materials_consumables` | `3920.0` | `3920` | `0.0` | `0` | `3920.0` | `3920` |
| `logistics_and_supply` | Логистика, и снабжение | `1.0` | `1.0` | `-` | `materials_overhead_percent` | `17075.268345` | `17075` | `0.0` | `0` | `17075.268345` | `17075` |
| `consumables_tool_depreciation` | Расходные материалы, амортизация инструмента | `1.0` | `1.0` | `комплект` | `materials_overhead_percent` | `51225.805036` | `51226` | `0.0` | `0` | `51225.805036` | `51226` |
| `technical_supervision` | Технический надзор | `1.0` | `1.0` | `-` | `manual_fixed_work` | `0.0` | `0` | `5000.0` | `5000` | `5000.0` | `5000` |

## Warnings / Notes
- `formwork_delivery_return_manipulator`: До 180 м2 включительно: 1 привоз + 1 вывоз = 2 машины; более 180 м2: 2 привоза + 2 вывоза = 4 машины.
- `formwork_rebar_crane_supply`: 3-я смена пока только manual_review / override.
- `formwork_timber_gost`: Сумма считается от quantity_raw, не от отображаемого количества.
- `floor_slab_concreting_work`: Стоимость считается от raw 37.3752, не от display 37.38.
- `concrete_pump_32m`: Fixed/manual line; не вычислять от объёма бетона.
- `bottom_slab_insulation_work`: Стоимость считается от raw 51.92, не от display 51.9.
- `eps_penoplex_osnova_100mm`: Стоимость считается от закупочного raw-объёма 8.319, не от display 8.32.

## Comparison
| Показатель | Ожидание | Получено | Разница | Статус |
| --- | ---: | ---: | ---: | --- |
| `totals.internal_materials_total` | `1168899` | `1168899` | `0` | `ok` |
| `totals.internal_works_total` | `611926` | `611926` | `0` | `ok` |
| `totals.internal_section_total` | `1780825` | `1780825` | `0` | `ok` |
| `totals.base_subtotal_raw_before_overheads` | `1707526.834518` | `1707526.834518` | `0.0` | `ok` |
| `totals.logistics_and_supply_total` | `17075` | `17075` | `0` | `ok` |
| `totals.consumables_and_tool_depreciation_total` | `51226` | `51226` | `0` | `ok` |
| `totals.technical_supervision_total` | `5000` | `5000` | `0` | `ok` |
| `calculation_blocks.rebar.rebar_calc_method` | `spec_length_items` | `spec_length_items` | `` | `ok` |
| `calculation_blocks.rebar.rebar_frame_assembly_quantity_m` | `7698.9` | `7698.9` | `0.0` | `ok` |
| `calculation_blocks.rebar.floor_slab_1_rebar_weight_with_waste_kg` | `4898.4` | `4898.4` | `0.0` | `ok` |
| `calculation_blocks.rebar.metal_delivery_calc_method` | `section_output_only` | `section_output_only` | `` | `ok` |
| `calculation_blocks.rebar.section_rebar_delivery_weight_kg` | `4960.6848` | `4960.6848` | `0.0` | `ok` |
| `calculation_blocks.rebar.legacy_delivery_line_enabled` | `False` | `False` | `0` | `ok` |
| `calculation_blocks.rebar.box_level_delivery_required` | `True` | `True` | `0` | `ok` |
| `calculation_blocks.rebar.item_controls_by_code` | `{'rebar_a500_d25': {'code': 'rebar_a500_d25', 'name': 'Арматура класса A500 диаметром 25 мм', 'steel_class': 'A500', 'diameter_mm': 25, 'floor': 1, 'component': 'floor_slab_1', 'spec_length_m': 46.8, 'base_length_m': 46.8, 'length_with_waste_m': 49.14, 'rods': 5, 'order_length_m': 58.5, 'delivery_weight_kg': 225.225, 'material_total_raw': 11486.475}, 'rebar_a500_d16': {'code': 'rebar_a500_d16', 'name': 'Арматура класса A500 диаметром 16 мм', 'steel_class': 'A500', 'diameter_mm': 16, 'floor': 1, 'component': 'floor_slab_1', 'spec_length_m': 81.9, 'base_length_m': 81.9, 'length_with_waste_m': 85.995, 'rods': 8, 'order_length_m': 93.6, 'delivery_weight_kg': 147.888, 'material_total_raw': 7542.288}, 'rebar_a500_d12': {'code': 'rebar_a500_d12', 'name': 'Арматура класса A500 диаметром 12 мм', 'steel_class': 'A500', 'diameter_mm': 12, 'floor': 1, 'component': 'floor_slab_1', 'spec_length_m': 58.5, 'base_length_m': 58.5, 'length_with_waste_m': 61.425, 'rods': 6, 'order_length_m': 70.2, 'delivery_weight_kg': 62.3376, 'material_total_raw': 3179.358}, 'rebar_a500_d10': {'code': 'rebar_a500_d10', 'name': 'Арматура класса A500 диаметром 10 мм', 'steel_class': 'A500', 'diameter_mm': 10, 'floor': 1, 'component': 'floor_slab_1', 'spec_length_m': 6879.6, 'base_length_m': 6879.6, 'length_with_waste_m': 7223.58, 'rods': 618, 'order_length_m': 7230.6, 'delivery_weight_kg': 4461.2802, 'material_total_raw': 236585.232}, 'rebar_a240_d8': {'code': 'rebar_a240_d8', 'name': 'Арматура класса A240 диаметром 8 мм', 'steel_class': 'A240', 'diameter_mm': 8, 'floor': 1, 'component': 'floor_slab_1', 'spec_length_m': 48, 'base_length_m': 48, 'length_with_waste_m': 50.4, 'rods': 9, 'order_length_m': 54, 'delivery_weight_kg': 21.33, 'material_total_raw': 1296}, 'rebar_a240_d6': {'code': 'rebar_a240_d6', 'name': 'Арматура класса A240 диаметром 6 мм', 'steel_class': 'A240', 'diameter_mm': 6, 'floor': 1, 'component': 'floor_slab_1', 'spec_length_m': 180, 'base_length_m': 180, 'length_with_waste_m': 189, 'rods': 32, 'order_length_m': 192, 'delivery_weight_kg': 42.624, 'material_total_raw': 2557.44}}` | `{'rebar_a500_d25': {'code': 'rebar_a500_d25', 'name': 'Арматура класса A500 диаметром 25 мм', 'steel_class': 'A500', 'diameter_mm': 25, 'floor': 1, 'component': 'floor_slab_1', 'spec_length_m': 46.8, 'base_length_m': 46.8, 'length_with_waste_m': 49.14, 'rods': 5, 'order_length_m': 58.5, 'delivery_weight_kg': 225.225, 'material_total_raw': 11486.475}, 'rebar_a500_d16': {'code': 'rebar_a500_d16', 'name': 'Арматура класса A500 диаметром 16 мм', 'steel_class': 'A500', 'diameter_mm': 16, 'floor': 1, 'component': 'floor_slab_1', 'spec_length_m': 81.9, 'base_length_m': 81.9, 'length_with_waste_m': 85.995, 'rods': 8, 'order_length_m': 93.6, 'delivery_weight_kg': 147.888, 'material_total_raw': 7542.288}, 'rebar_a500_d12': {'code': 'rebar_a500_d12', 'name': 'Арматура класса A500 диаметром 12 мм', 'steel_class': 'A500', 'diameter_mm': 12, 'floor': 1, 'component': 'floor_slab_1', 'spec_length_m': 58.5, 'base_length_m': 58.5, 'length_with_waste_m': 61.425, 'rods': 6, 'order_length_m': 70.2, 'delivery_weight_kg': 62.3376, 'material_total_raw': 3179.358}, 'rebar_a500_d10': {'code': 'rebar_a500_d10', 'name': 'Арматура класса A500 диаметром 10 мм', 'steel_class': 'A500', 'diameter_mm': 10, 'floor': 1, 'component': 'floor_slab_1', 'spec_length_m': 6879.6, 'base_length_m': 6879.6, 'length_with_waste_m': 7223.58, 'rods': 618, 'order_length_m': 7230.6, 'delivery_weight_kg': 4461.2802, 'material_total_raw': 236585.232}, 'rebar_a240_d8': {'code': 'rebar_a240_d8', 'name': 'Арматура класса A240 диаметром 8 мм', 'steel_class': 'A240', 'diameter_mm': 8, 'floor': 1, 'component': 'floor_slab_1', 'spec_length_m': 48.0, 'base_length_m': 48.0, 'length_with_waste_m': 50.4, 'rods': 9, 'order_length_m': 54.0, 'delivery_weight_kg': 21.33, 'material_total_raw': 1296.0}, 'rebar_a240_d6': {'code': 'rebar_a240_d6', 'name': 'Арматура класса A240 диаметром 6 мм', 'steel_class': 'A240', 'diameter_mm': 6, 'floor': 1, 'component': 'floor_slab_1', 'spec_length_m': 180.0, 'base_length_m': 180.0, 'length_with_waste_m': 189.0, 'rods': 32, 'order_length_m': 192.0, 'delivery_weight_kg': 42.624, 'material_total_raw': 2557.44}}` | `` | `ok` |
| `estimate_lines.floor_slab_rebar_frame_assembly_control.quantity_raw` | `7698.9` | `7698.9` | `0.0` | `ok` |
| `estimate_lines.floor_slab_rebar_frame_assembly_control.quantity_display` | `7698.9` | `7698.9` | `0.0` | `ok` |
| `estimate_lines.floor_slab_rebar_frame_assembly_control.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.rebar_a500_d25.quantity_raw` | `58.5` | `58.5` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d25.quantity_display` | `58.5` | `58.5` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d25.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.rebar_a500_d25.price_code` | `rebar_a500_d25_m` | `rebar_a500_d25_m` | `` | `ok` |
| `estimate_lines.rebar_a500_d25.material_total_raw` | `11486.475` | `11486.475` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d25.material_total` | `11486` | `11486` | `0` | `ok` |
| `estimate_lines.rebar_a500_d16.quantity_raw` | `93.6` | `93.6` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d16.quantity_display` | `93.6` | `93.6` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d16.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.rebar_a500_d16.price_code` | `rebar_a500_d16_m` | `rebar_a500_d16_m` | `` | `ok` |
| `estimate_lines.rebar_a500_d16.material_total_raw` | `7542.288` | `7542.288` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d16.material_total` | `7542` | `7542` | `0` | `ok` |
| `estimate_lines.rebar_a500_d12.quantity_raw` | `70.2` | `70.2` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d12.quantity_display` | `70.2` | `70.2` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d12.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.rebar_a500_d12.price_code` | `rebar_a500_d12_m` | `rebar_a500_d12_m` | `` | `ok` |
| `estimate_lines.rebar_a500_d12.material_total_raw` | `3179.358` | `3179.358` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d12.material_total` | `3179` | `3179` | `0` | `ok` |
| `estimate_lines.rebar_a500_d10.quantity_raw` | `7230.6` | `7230.6` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d10.quantity_display` | `7230.6` | `7230.6` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d10.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.rebar_a500_d10.price_code` | `rebar_a500_d10_m` | `rebar_a500_d10_m` | `` | `ok` |
| `estimate_lines.rebar_a500_d10.material_total_raw` | `236585.232` | `236585.232` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d10.material_total` | `236585` | `236585` | `0` | `ok` |
| `estimate_lines.rebar_a240_d8.quantity_raw` | `54` | `54.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d8.quantity_display` | `54` | `54.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d8.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.rebar_a240_d8.price_code` | `rebar_a240_d8_m` | `rebar_a240_d8_m` | `` | `ok` |
| `estimate_lines.rebar_a240_d8.material_total_raw` | `1296` | `1296.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d8.material_total` | `1296` | `1296` | `0` | `ok` |
| `estimate_lines.rebar_a240_d6.quantity_raw` | `192` | `192.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d6.quantity_display` | `192` | `192.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d6.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.rebar_a240_d6.price_code` | `rebar_a240_d6_m` | `rebar_a240_d6_m` | `` | `ok` |
| `estimate_lines.rebar_a240_d6.material_total_raw` | `2557.44` | `2557.44` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d6.material_total` | `2557` | `2557` | `0` | `ok` |
