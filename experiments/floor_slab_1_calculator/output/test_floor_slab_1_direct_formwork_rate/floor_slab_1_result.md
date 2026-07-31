# Расчёт монолитной плиты перекрытия 1-го этажа: test_floor_slab_1_direct_formwork_rate

Проект: `test_floor_slab_1_direct_formwork_rate`

## Итоги
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total` | `1151589` |
| `internal_works_total` | `583630` |
| `internal_section_total` | `1735219` |
| `base_subtotal_raw_before_overheads` | `1663672.300518` |
| `logistics_and_supply_total` | `16637` |
| `consumables_and_tool_depreciation_total` | `49910` |
| `technical_supervision_total` | `5000` |

## Comparison Summary
- status: `ok`
- ok: `193`
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
| `rebar.rebar_calc_method` | `legacy_weight_parts` |
| `rebar.items` | `[{"code": "rebar_a500_d25", "name": "Арматура класса А500 диаметром 25 мм", "steel_class": "A500", "diameter_mm": 25, "source_weight_kg": 162.0, "kg_per_meter": 3.85, "base_length_m": 42.077922, "waste_coeff": 1.05, "length_with_waste_m": 44.181818, "weight_with_waste_kg_display": 170.1, "rod_length_m": 11.7, "rods": 4, "rods_ordered": 4, "order_length_m": 46.8, "delivery_weight_kg": 180.18, "unit_price_per_m": 196.35, "material_total_raw": 9189.18, "material_total": 9189}, {"code": "rebar_a500_d16", "name": "Арматура класса А500 диаметром 16 мм", "steel_class": "A500", "diameter_mm": 16, "source_weight_kg": 112.04, "kg_per_meter": 1.58, "base_length_m": 70.911392, "waste_coeff": 1.05, "length_with_waste_m": 74.456962, "weight_with_waste_kg_display": 117.64, "rod_length_m": 11.7, "rods": 7, "rods_ordered": 7, "order_length_m": 81.9, "delivery_weight_kg": 129.402, "unit_price_per_m": 80.58, "material_total_raw": 6599.502, "material_total": 6600}, {"code": "rebar_a500_d12", "name": "Арматура класса А500 диаметром 12 мм", "steel_class": "A500", "diameter_mm": 12, "source_weight_kg": 42.0, "kg_per_meter": 0.888, "base_length_m": 47.297297, "waste_coeff": 1.05, "length_with_waste_m": 49.662162, "weight_with_waste_kg_display": 44.1, "rod_length_m": 11.7, "rods": 5, "rods_ordered": 5, "order_length_m": 58.5, "delivery_weight_kg": 51.948, "unit_price_per_m": 45.29, "material_total_raw": 2649.465, "material_total": 2649}, {"code": "rebar_a500_d10", "name": "Арматура класса А500 диаметром 10 мм", "steel_class": "A500", "diameter_mm": 10, "source_weight_kg": 4038.6, "kg_per_meter": 0.617, "base_length_m": 6545.54295, "waste_coeff": 1.05, "length_with_waste_m": 6872.820097, "weight_with_waste_kg_display": 4240.53, "rod_length_m": 11.7, "rods": 588, "rods_ordered": 588, "order_length_m": 6879.6, "delivery_weight_kg": 4244.7132, "unit_price_per_m": 32.72, "material_total_raw": 225100.512, "material_total": 225101}, {"code": "rebar_a240_d8", "name": "Арматура класса А240 диаметром 8 мм", "steel_class": "A240", "diameter_mm": 8, "source_weight_kg": 17.0, "kg_per_meter": 0.395, "base_length_m": 43.037975, "waste_coeff": 1.05, "length_with_waste_m": 45.189873, "weight_with_waste_kg_display": 17.85, "rod_length_m": 6.0, "rods": 8, "rods_ordered": 8, "order_length_m": 48.0, "delivery_weight_kg": 18.96, "unit_price_per_m": 24.0, "material_total_raw": 1152.0, "material_total": 1152}, {"code": "rebar_a240_d6", "name": "Арматура класса А240 диаметром 6 мм", "steel_class": "A240", "diameter_mm": 6, "source_weight_kg": 38.0, "kg_per_meter": 0.222, "base_length_m": 171.171171, "waste_coeff": 1.05, "length_with_waste_m": 179.72973, "weight_with_waste_kg_display": 39.9, "rod_length_m": 6.0, "rods": 30, "rods_ordered": 30, "order_length_m": 180.0, "delivery_weight_kg": 39.96, "unit_price_per_m": 13.32, "material_total_raw": 2397.6, "material_total": 2398}]` |
| `rebar.item_controls_by_code.rebar_a500_d25.code` | `rebar_a500_d25` |
| `rebar.item_controls_by_code.rebar_a500_d25.name` | `Арматура класса А500 диаметром 25 мм` |
| `rebar.item_controls_by_code.rebar_a500_d25.steel_class` | `A500` |
| `rebar.item_controls_by_code.rebar_a500_d25.diameter_mm` | `25` |
| `rebar.item_controls_by_code.rebar_a500_d25.floor` | `None` |
| `rebar.item_controls_by_code.rebar_a500_d25.component` | `None` |
| `rebar.item_controls_by_code.rebar_a500_d25.spec_length_m` | `None` |
| `rebar.item_controls_by_code.rebar_a500_d25.base_length_m` | `42.077922` |
| `rebar.item_controls_by_code.rebar_a500_d25.length_with_waste_m` | `44.181818` |
| `rebar.item_controls_by_code.rebar_a500_d25.rods` | `4` |
| `rebar.item_controls_by_code.rebar_a500_d25.order_length_m` | `46.8` |
| `rebar.item_controls_by_code.rebar_a500_d25.delivery_weight_kg` | `180.18` |
| `rebar.item_controls_by_code.rebar_a500_d25.material_total_raw` | `9189.18` |
| `rebar.item_controls_by_code.rebar_a500_d16.code` | `rebar_a500_d16` |
| `rebar.item_controls_by_code.rebar_a500_d16.name` | `Арматура класса А500 диаметром 16 мм` |
| `rebar.item_controls_by_code.rebar_a500_d16.steel_class` | `A500` |
| `rebar.item_controls_by_code.rebar_a500_d16.diameter_mm` | `16` |
| `rebar.item_controls_by_code.rebar_a500_d16.floor` | `None` |
| `rebar.item_controls_by_code.rebar_a500_d16.component` | `None` |
| `rebar.item_controls_by_code.rebar_a500_d16.spec_length_m` | `None` |
| `rebar.item_controls_by_code.rebar_a500_d16.base_length_m` | `70.911392` |
| `rebar.item_controls_by_code.rebar_a500_d16.length_with_waste_m` | `74.456962` |
| `rebar.item_controls_by_code.rebar_a500_d16.rods` | `7` |
| `rebar.item_controls_by_code.rebar_a500_d16.order_length_m` | `81.9` |
| `rebar.item_controls_by_code.rebar_a500_d16.delivery_weight_kg` | `129.402` |
| `rebar.item_controls_by_code.rebar_a500_d16.material_total_raw` | `6599.502` |
| `rebar.item_controls_by_code.rebar_a500_d12.code` | `rebar_a500_d12` |
| `rebar.item_controls_by_code.rebar_a500_d12.name` | `Арматура класса А500 диаметром 12 мм` |
| `rebar.item_controls_by_code.rebar_a500_d12.steel_class` | `A500` |
| `rebar.item_controls_by_code.rebar_a500_d12.diameter_mm` | `12` |
| `rebar.item_controls_by_code.rebar_a500_d12.floor` | `None` |
| `rebar.item_controls_by_code.rebar_a500_d12.component` | `None` |
| `rebar.item_controls_by_code.rebar_a500_d12.spec_length_m` | `None` |
| `rebar.item_controls_by_code.rebar_a500_d12.base_length_m` | `47.297297` |
| `rebar.item_controls_by_code.rebar_a500_d12.length_with_waste_m` | `49.662162` |
| `rebar.item_controls_by_code.rebar_a500_d12.rods` | `5` |
| `rebar.item_controls_by_code.rebar_a500_d12.order_length_m` | `58.5` |
| `rebar.item_controls_by_code.rebar_a500_d12.delivery_weight_kg` | `51.948` |
| `rebar.item_controls_by_code.rebar_a500_d12.material_total_raw` | `2649.465` |
| `rebar.item_controls_by_code.rebar_a500_d10.code` | `rebar_a500_d10` |
| `rebar.item_controls_by_code.rebar_a500_d10.name` | `Арматура класса А500 диаметром 10 мм` |
| `rebar.item_controls_by_code.rebar_a500_d10.steel_class` | `A500` |
| `rebar.item_controls_by_code.rebar_a500_d10.diameter_mm` | `10` |
| `rebar.item_controls_by_code.rebar_a500_d10.floor` | `None` |
| `rebar.item_controls_by_code.rebar_a500_d10.component` | `None` |
| `rebar.item_controls_by_code.rebar_a500_d10.spec_length_m` | `None` |
| `rebar.item_controls_by_code.rebar_a500_d10.base_length_m` | `6545.54295` |
| `rebar.item_controls_by_code.rebar_a500_d10.length_with_waste_m` | `6872.820097` |
| `rebar.item_controls_by_code.rebar_a500_d10.rods` | `588` |
| `rebar.item_controls_by_code.rebar_a500_d10.order_length_m` | `6879.6` |
| `rebar.item_controls_by_code.rebar_a500_d10.delivery_weight_kg` | `4244.7132` |
| `rebar.item_controls_by_code.rebar_a500_d10.material_total_raw` | `225100.512` |
| `rebar.item_controls_by_code.rebar_a240_d8.code` | `rebar_a240_d8` |
| `rebar.item_controls_by_code.rebar_a240_d8.name` | `Арматура класса А240 диаметром 8 мм` |
| `rebar.item_controls_by_code.rebar_a240_d8.steel_class` | `A240` |
| `rebar.item_controls_by_code.rebar_a240_d8.diameter_mm` | `8` |
| `rebar.item_controls_by_code.rebar_a240_d8.floor` | `None` |
| `rebar.item_controls_by_code.rebar_a240_d8.component` | `None` |
| `rebar.item_controls_by_code.rebar_a240_d8.spec_length_m` | `None` |
| `rebar.item_controls_by_code.rebar_a240_d8.base_length_m` | `43.037975` |
| `rebar.item_controls_by_code.rebar_a240_d8.length_with_waste_m` | `45.189873` |
| `rebar.item_controls_by_code.rebar_a240_d8.rods` | `8` |
| `rebar.item_controls_by_code.rebar_a240_d8.order_length_m` | `48.0` |
| `rebar.item_controls_by_code.rebar_a240_d8.delivery_weight_kg` | `18.96` |
| `rebar.item_controls_by_code.rebar_a240_d8.material_total_raw` | `1152.0` |
| `rebar.item_controls_by_code.rebar_a240_d6.code` | `rebar_a240_d6` |
| `rebar.item_controls_by_code.rebar_a240_d6.name` | `Арматура класса А240 диаметром 6 мм` |
| `rebar.item_controls_by_code.rebar_a240_d6.steel_class` | `A240` |
| `rebar.item_controls_by_code.rebar_a240_d6.diameter_mm` | `6` |
| `rebar.item_controls_by_code.rebar_a240_d6.floor` | `None` |
| `rebar.item_controls_by_code.rebar_a240_d6.component` | `None` |
| `rebar.item_controls_by_code.rebar_a240_d6.spec_length_m` | `None` |
| `rebar.item_controls_by_code.rebar_a240_d6.base_length_m` | `171.171171` |
| `rebar.item_controls_by_code.rebar_a240_d6.length_with_waste_m` | `179.72973` |
| `rebar.item_controls_by_code.rebar_a240_d6.rods` | `30` |
| `rebar.item_controls_by_code.rebar_a240_d6.order_length_m` | `180.0` |
| `rebar.item_controls_by_code.rebar_a240_d6.delivery_weight_kg` | `39.96` |
| `rebar.item_controls_by_code.rebar_a240_d6.material_total_raw` | `2397.6` |
| `rebar.rebar_frame_assembly_quantity_m` | `7294.8` |
| `rebar.floor_slab_1_rebar_weight_with_waste_kg` | `4630.1` |
| `rebar.metal_delivery_calc_method` | `section_output_only` |
| `rebar.section_rebar_delivery_weight_kg` | `4665.1632` |
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
| `insulation.beams_eps_work_length_source` | `calculated_all_beams` |
| `insulation.calculated_all_beams_eps_work_length_m` | `23.2` |
| `insulation.total_insulation_length_m` | `108.0` |
| `insulation.edge_beam_eps_work_length_m` | `108.0` |
| `insulation.slab_edge_insulation_area_m2` | `15.264` |
| `insulation.slab_edge_eps_material_area_m2` | `15.264` |
| `insulation.beams_insulation_area_m2` | `10.516` |
| `insulation.beams_eps_material_area_m2` | `10.516` |
| `insulation.beams_eps_material_area_source` | `calculated_all_beams` |
| `insulation.calculated_all_beams_eps_material_area_m2` | `10.516` |
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
| `overheads.base_subtotal_raw_before_overheads` | `1663672.300518` |
| `overheads.logistics_and_supply_percent` | `0.01` |
| `overheads.logistics_and_supply_total_raw` | `16636.723005` |
| `overheads.logistics_and_supply_total` | `16637` |
| `overheads.consumables_and_tool_percent` | `0.03` |
| `overheads.consumables_and_tool_depreciation_total_raw` | `49910.169016` |
| `overheads.consumables_and_tool_depreciation_total` | `49910` |
| `manual_lines.concrete_pump_shifts` | `1` |
| `manual_lines.technical_supervision_amount` | `5000` |
| `control_metrics.control_geometry_area_m2` | `210.64` |
| `control_metrics.slab_area_used_in_estimate_m2` | `207.64` |
| `control_metrics.beam_concreting_control_total_by_length` | `34800` |
| `control_metrics.reinforcement_density_kg_per_m3` | `108.79` |

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

Legacy-режим `legacy_weight_parts`: арматура берётся весом в кг и переводится в м.п. через `kg_per_meter`.

| Показатель | Значение |
| --- | ---: |
| `rebar_calc_method` | `legacy_weight_parts` |
| `rebar_frame_assembly_quantity_m` | `7294.8` |
| `section_rebar_delivery_weight_kg` | `4665.1632` |

| code | floor | component | steel_class | diameter_mm | spec_length_m | base_length_m | length_with_waste_m | rods | order_length_m | kg_per_meter | delivery_weight_kg | price_code |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| rebar_a500_d25 | None | None | A500 | 25 | None | 42.077922 | 44.181818 | 4 | 46.8 | 3.85 | 180.18 | rebar_a500_d25_m |
| rebar_a500_d16 | None | None | A500 | 16 | None | 70.911392 | 74.456962 | 7 | 81.9 | 1.58 | 129.402 | rebar_a500_d16_m |
| rebar_a500_d12 | None | None | A500 | 12 | None | 47.297297 | 49.662162 | 5 | 58.5 | 0.888 | 51.948 | rebar_a500_d12_m |
| rebar_a500_d10 | None | None | A500 | 10 | None | 6545.54295 | 6872.820097 | 588 | 6879.6 | 0.617 | 4244.7132 | rebar_a500_d10_m |
| rebar_a240_d8 | None | None | A240 | 8 | None | 43.037975 | 45.189873 | 8 | 48.0 | 0.395 | 18.96 | rebar_a240_d8_m |
| rebar_a240_d6 | None | None | A240 | 6 | None | 171.171171 | 179.72973 | 30 | 180.0 | 0.222 | 39.96 | rebar_a240_d6_m |

## Доставка арматуры и металла

Production-режим `section_output_only`: калькулятор плиты 1-го этажа отдаёт только вес закупочной арматуры текущего раздела.

Количество машин доставки металла считается выше, на уровне `box_calculator`, по суммарному весу металла коробки.

| Показатель | Значение |
| --- | ---: |
| `metal_delivery_calc_method` | `section_output_only` |
| `section_rebar_delivery_weight_kg` | `4665.1632` |
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
| `floor_slab_rebar_frame_assembly_control` | Изготовление и монтаж каркаса армирования монолитного перекрытия из арматуры (в том числе балок) | `7294.8` | `7294.8` | `мп` | `zero_control_line` | `0.0` | `0` | `0.0` | `0` | `0.0` | `0` |
| `rebar_a500_d25` | Арматура класса А500 диаметром 25 мм | `46.8` | `46.8` | `мп` | `materials` | `9189.18` | `9189` | `0.0` | `0` | `9189.18` | `9189` |
| `rebar_a500_d16` | Арматура класса А500 диаметром 16 мм | `81.9` | `81.9` | `мп` | `materials` | `6599.502` | `6600` | `0.0` | `0` | `6599.502` | `6600` |
| `rebar_a500_d12` | Арматура класса А500 диаметром 12 мм | `58.5` | `58.5` | `мп` | `materials` | `2649.465` | `2649` | `0.0` | `0` | `2649.465` | `2649` |
| `rebar_a500_d10` | Арматура класса А500 диаметром 10 мм | `6879.6` | `6879.6` | `мп` | `materials` | `225100.512` | `225101` | `0.0` | `0` | `225100.512` | `225101` |
| `rebar_a240_d8` | Арматура класса А240 диаметром 8 мм | `48.0` | `48.0` | `мп` | `materials` | `1152.0` | `1152` | `0.0` | `0` | `1152.0` | `1152` |
| `rebar_a240_d6` | Арматура класса А240 диаметром 6 мм | `180.0` | `180.0` | `мп` | `materials` | `2397.6` | `2398` | `0.0` | `0` | `2397.6` | `2398` |
| `rebar_metal_delivery` | Доставка арматуры, металла | `0.0` | `0.0` | `маш` | `logistics_machinery` | `0.0` | `0` | `0.0` | `0` | `0.0` | `0` |
| `floor_slab_concreting_work` | Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300) | `37.3752` | `37.38` | `м3` | `work` | `0.0` | `0` | `448502.4` | `448502` | `448502.4` | `448502` |
| `beam_concreting_work` | Бетонирование балки бетоном марки В22,5 (М300) | `23.2` | `23.2` | `мп` | `work` | `0.0` | `0` | `34800.0` | `34800` | `34800.0` | `34800` |
| `concrete_b22_5_m300_material` | Бетон марки В22,5 (М300) | `43.0` | `43.0` | `м3` | `materials` | `275200.0` | `275200` | `0.0` | `0` | `275200.0` | `275200` |
| `concrete_delivery` | Доставка бетона до объекта | `5.0` | `5.0` | `рейс` | `logistics_machinery` | `37500.0` | `37500` | `0.0` | `0` | `37500.0` | `37500` |
| `concrete_pump_32m` | Работа бетононасоса 32м + гаситель | `1.0` | `1.0` | `смена` | `machinery_fixed` | `38000.0` | `38000` | `0.0` | `0` | `38000.0` | `38000` |
| `formwork_dismantling_zero_internal` | Демонтаж опалубки после завершения бетонирования | `207.64` | `207.6` | `м2` | `client_only_zero_internal_line` | `0.0` | `0` | `0.0` | `0` | `0.0` | `0` |
| `edge_beam_insulation_work` | Устройство утепления по наружной стороне торцов плиты, балок | `108.0` | `108.0` | `мп` | `work` | `0.0` | `0` | `48600.0` | `48600` | `48600.0` | `48600` |
| `bottom_slab_insulation_work` | Устройство утепления низа плиты | `51.92` | `51.9` | `м2` | `work` | `0.0` | `0` | `46728.0` | `46728` | `46728.0` | `46728` |
| `eps_penoplex_osnova_100mm` | Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм | `8.319` | `8.32` | `м3` | `materials` | `75037.38` | `75037` | `0.0` | `0` | `75037.38` | `75037` |
| `eps_glue_foam` | Клей-пена для ЭППС | `8.0` | `8.0` | `баллон` | `materials_consumables` | `3920.0` | `3920` | `0.0` | `0` | `3920.0` | `3920` |
| `logistics_and_supply` | Логистика, и снабжение | `1.0` | `1.0` | `-` | `materials_overhead_percent` | `16636.723005` | `16637` | `0.0` | `0` | `16636.723005` | `16637` |
| `consumables_tool_depreciation` | Расходные материалы, амортизация инструмента | `1.0` | `1.0` | `комплект` | `materials_overhead_percent` | `49910.169016` | `49910` | `0.0` | `0` | `49910.169016` | `49910` |
| `technical_supervision` | Технический надзор | `1.0` | `1.0` | `-` | `manual_fixed_work` | `0.0` | `0` | `5000.0` | `5000` | `5000.0` | `5000` |

## Warnings / Notes
- insulation.beams_eps_work_length_m is not provided; fallback assumes all beams are insulated. Elena confirmed beams may be insulated only partially, so review this length.
- insulation.beams_eps_material_area_m2 is not provided; fallback assumes all beam side faces are insulated. Elena confirmed beams may be insulated only partially, so review this area.
- `formwork_delivery_return_manipulator`: До 180 м2 включительно: 1 привоз + 1 вывоз = 2 машины; более 180 м2: 2 привоза + 2 вывоза = 4 машины.
- `formwork_rebar_crane_supply`: 3-я смена пока только manual_review / override.
- `formwork_timber_gost`: Сумма считается от quantity_raw, не от отображаемого количества.
- `rebar_metal_delivery`: Количество машин — с уровня коробки (box-калькулятор, накопление 10 т по всем разделам с арматурой).
- `floor_slab_concreting_work`: Стоимость считается от raw 37.3752, не от display 37.38.
- `beam_concreting_work`: С 2026-07-28 работа по бетонированию балок считается по длине балок, а не по объему бетона.
- `concrete_pump_32m`: Fixed/manual line; не вычислять от объёма бетона.
- `bottom_slab_insulation_work`: Стоимость считается от raw 51.92, не от display 51.9.
- `eps_penoplex_osnova_100mm`: Стоимость считается от закупочного raw-объёма 8.319, не от display 8.32.

## Comparison
| Показатель | Ожидание | Получено | Разница | Статус |
| --- | ---: | ---: | ---: | --- |
| `totals.internal_materials_total` | `1151589` | `1151589` | `0` | `ok` |
| `totals.internal_works_total` | `583630` | `583630` | `0` | `ok` |
| `totals.internal_section_total` | `1735219` | `1735219` | `0` | `ok` |
| `totals.base_subtotal_raw_before_overheads` | `1663672.300518` | `1663672.300518` | `0.0` | `ok` |
| `totals.logistics_and_supply_total` | `16637` | `16637` | `0` | `ok` |
| `totals.consumables_and_tool_depreciation_total` | `49910` | `49910` | `0` | `ok` |
| `totals.technical_supervision_total` | `5000` | `5000` | `0` | `ok` |
| `calculation_blocks.geometry.slab_concrete_volume_m3_raw` | `37.3752` | `37.3752` | `0.0` | `ok` |
| `calculation_blocks.geometry.slab_concrete_volume_m3_display` | `37.38` | `37.38` | `0.0` | `ok` |
| `calculation_blocks.geometry.slab_formwork_area_m2` | `207.64` | `207.64` | `0.0` | `ok` |
| `calculation_blocks.beams.total_length_m` | `23.2` | `23.2` | `0.0` | `ok` |
| `calculation_blocks.beams.total_concrete_volume_m3` | `3.1548` | `3.1548` | `0.0` | `ok` |
| `calculation_blocks.beams.total_formwork_area_m2` | `27.992` | `27.992` | `0.0` | `ok` |
| `calculation_blocks.formwork.edge_formwork_area_m2` | `23.6` | `23.6` | `0.0` | `ok` |
| `calculation_blocks.formwork.edge_and_beam_formwork_area_m2` | `51.592` | `51.592` | `0.0` | `ok` |
| `calculation_blocks.formwork.formwork_delivery_trucks` | `4` | `4.0` | `0.0` | `ok` |
| `calculation_blocks.formwork_rate_context.formwork_rate_calc_method` | `direct_section_rate` | `direct_section_rate` | `` | `ok` |
| `calculation_blocks.formwork_rate_context.formwork_rate_per_m2` | `600` | `600.0` | `0.0` | `ok` |
| `calculation_blocks.formwork_rate_context.box_level_quote_context_used` | `False` | `False` | `0` | `ok` |
| `calculation_blocks.plywood_and_timber.order_plywood_sheets` | `51` | `51` | `0` | `ok` |
| `calculation_blocks.plywood_and_timber.timber_volume_m3_raw` | `2.790846` | `2.790846` | `0.0` | `ok` |
| `calculation_blocks.rebar.rebar_frame_assembly_quantity_m` | `7294.8` | `7294.8` | `0.0` | `ok` |
| `calculation_blocks.rebar.floor_slab_1_rebar_weight_with_waste_kg` | `4630.1` | `4630.1` | `0.0` | `ok` |
| `calculation_blocks.rebar.metal_delivery_calc_method` | `section_output_only` | `section_output_only` | `` | `ok` |
| `calculation_blocks.rebar.section_rebar_delivery_weight_kg` | `4665.1632` | `4665.1632` | `0.0` | `ok` |
| `calculation_blocks.rebar.legacy_delivery_line_enabled` | `False` | `False` | `0` | `ok` |
| `calculation_blocks.rebar.box_level_delivery_required` | `True` | `True` | `0` | `ok` |
| `calculation_blocks.concrete.concrete_volume_with_waste_m3_raw` | `42.5565` | `42.5565` | `0.0` | `ok` |
| `calculation_blocks.concrete.concrete_volume_with_waste_m3_display` | `42.56` | `42.56` | `0.0` | `ok` |
| `calculation_blocks.concrete.order_concrete_volume_m3` | `43` | `43` | `0` | `ok` |
| `calculation_blocks.concrete.concrete_delivery_trips` | `5` | `5` | `0` | `ok` |
| `calculation_blocks.insulation.total_insulation_length_m` | `108` | `108.0` | `0.0` | `ok` |
| `calculation_blocks.insulation.edge_and_beam_insulation_area_m2` | `25.78` | `25.78` | `0.0` | `ok` |
| `calculation_blocks.insulation.bottom_slab_insulation_area_m2_raw` | `51.92` | `51.92` | `0.0` | `ok` |
| `calculation_blocks.insulation.total_insulation_area_m2` | `77.7` | `77.7` | `0.0` | `ok` |
| `calculation_blocks.insulation.eps_packs_ordered` | `30` | `30` | `0` | `ok` |
| `calculation_blocks.insulation.order_eps_volume_m3_raw` | `8.319` | `8.319` | `0.0` | `ok` |
| `calculation_blocks.insulation.foam_cans_ordered` | `8` | `8` | `0` | `ok` |
| `calculation_blocks.overheads.base_subtotal_raw_before_overheads` | `1663672.300518` | `1663672.300518` | `0.0` | `ok` |
| `calculation_blocks.overheads.logistics_and_supply_total` | `16637` | `16637` | `0` | `ok` |
| `calculation_blocks.overheads.consumables_and_tool_depreciation_total` | `49910` | `49910` | `0` | `ok` |
| `estimate_lines.slab_formwork_installation_control.quantity_raw` | `207.64` | `207.64` | `0.0` | `ok` |
| `estimate_lines.slab_formwork_installation_control.quantity_display` | `207.64` | `207.64` | `0.0` | `ok` |
| `estimate_lines.slab_formwork_installation_control.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.slab_formwork_installation_control.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.slab_formwork_installation_control.line_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_set_rental_material.quantity_raw` | `207.64` | `207.64` | `0.0` | `ok` |
| `estimate_lines.formwork_set_rental_material.quantity_display` | `207.64` | `207.64` | `0.0` | `ok` |
| `estimate_lines.formwork_set_rental_material.material_total_raw` | `124584` | `124584.0` | `0.0` | `ok` |
| `estimate_lines.formwork_set_rental_material.material_total` | `124584` | `124584` | `0` | `ok` |
| `estimate_lines.formwork_set_rental_material.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_set_rental_material.line_total` | `124584` | `124584` | `0` | `ok` |
| `estimate_lines.formwork_delivery_return_manipulator.quantity_raw` | `4` | `4.0` | `0.0` | `ok` |
| `estimate_lines.formwork_delivery_return_manipulator.quantity_display` | `4` | `4.0` | `0.0` | `ok` |
| `estimate_lines.formwork_delivery_return_manipulator.material_total` | `80000` | `80000` | `0` | `ok` |
| `estimate_lines.formwork_delivery_return_manipulator.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_delivery_return_manipulator.line_total` | `80000` | `80000` | `0` | `ok` |
| `estimate_lines.formwork_rebar_crane_supply.quantity_raw` | `2` | `2.0` | `0.0` | `ok` |
| `estimate_lines.formwork_rebar_crane_supply.quantity_display` | `2` | `2.0` | `0.0` | `ok` |
| `estimate_lines.formwork_rebar_crane_supply.material_total` | `60000` | `60000` | `0` | `ok` |
| `estimate_lines.formwork_rebar_crane_supply.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_rebar_crane_supply.line_total` | `60000` | `60000` | `0` | `ok` |
| `estimate_lines.formwork_consumables.quantity_raw` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.formwork_consumables.quantity_display` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.formwork_consumables.material_total_raw` | `9759.08` | `9759.08` | `0.0` | `ok` |
| `estimate_lines.formwork_consumables.material_total` | `9759` | `9759` | `0` | `ok` |
| `estimate_lines.formwork_consumables.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_consumables.line_total` | `9759` | `9759` | `0` | `ok` |
| `estimate_lines.edge_beam_formwork_installation_control.quantity_raw` | `51.592` | `51.592` | `0.0` | `ok` |
| `estimate_lines.edge_beam_formwork_installation_control.quantity_display` | `51.59` | `51.59` | `0.0` | `ok` |
| `estimate_lines.edge_beam_formwork_installation_control.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.edge_beam_formwork_installation_control.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.edge_beam_formwork_installation_control.line_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.plywood_fk_18mm_for_edges_and_non_multiple_places.quantity_raw` | `51` | `51.0` | `0.0` | `ok` |
| `estimate_lines.plywood_fk_18mm_for_edges_and_non_multiple_places.quantity_display` | `51` | `51.0` | `0.0` | `ok` |
| `estimate_lines.plywood_fk_18mm_for_edges_and_non_multiple_places.material_total` | `73950` | `73950` | `0` | `ok` |
| `estimate_lines.plywood_fk_18mm_for_edges_and_non_multiple_places.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.plywood_fk_18mm_for_edges_and_non_multiple_places.line_total` | `73950` | `73950` | `0` | `ok` |
| `estimate_lines.formwork_timber_gost.quantity_raw` | `2.790846` | `2.790846` | `0.0` | `ok` |
| `estimate_lines.formwork_timber_gost.quantity_display` | `2.79` | `2.79` | `0.0` | `ok` |
| `estimate_lines.formwork_timber_gost.material_total_raw` | `60003.181518` | `60003.181518` | `0.0` | `ok` |
| `estimate_lines.formwork_timber_gost.material_total` | `60003` | `60003` | `0` | `ok` |
| `estimate_lines.formwork_timber_gost.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_timber_gost.line_total` | `60003` | `60003` | `0` | `ok` |
| `estimate_lines.floor_slab_rebar_frame_assembly_control.quantity_raw` | `7294.8` | `7294.8` | `0.0` | `ok` |
| `estimate_lines.floor_slab_rebar_frame_assembly_control.quantity_display` | `7294.8` | `7294.8` | `0.0` | `ok` |
| `estimate_lines.floor_slab_rebar_frame_assembly_control.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.floor_slab_rebar_frame_assembly_control.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.floor_slab_rebar_frame_assembly_control.line_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_a500_d25.quantity_raw` | `46.8` | `46.8` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d25.quantity_display` | `46.8` | `46.8` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d25.material_total_raw` | `9189.18` | `9189.18` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d25.material_total` | `9189` | `9189` | `0` | `ok` |
| `estimate_lines.rebar_a500_d25.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_a500_d25.line_total` | `9189` | `9189` | `0` | `ok` |
| `estimate_lines.rebar_a500_d16.quantity_raw` | `81.9` | `81.9` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d16.quantity_display` | `81.9` | `81.9` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d16.material_total_raw` | `6599.502` | `6599.502` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d16.material_total` | `6600` | `6600` | `0` | `ok` |
| `estimate_lines.rebar_a500_d16.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_a500_d16.line_total` | `6600` | `6600` | `0` | `ok` |
| `estimate_lines.rebar_a500_d12.quantity_raw` | `58.5` | `58.5` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d12.quantity_display` | `58.5` | `58.5` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d12.material_total_raw` | `2649.465` | `2649.465` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d12.material_total` | `2649` | `2649` | `0` | `ok` |
| `estimate_lines.rebar_a500_d12.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_a500_d12.line_total` | `2649` | `2649` | `0` | `ok` |
| `estimate_lines.rebar_a500_d10.quantity_raw` | `6879.6` | `6879.6` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d10.quantity_display` | `6879.6` | `6879.6` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d10.material_total_raw` | `225100.512` | `225100.512` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d10.material_total` | `225101` | `225101` | `0` | `ok` |
| `estimate_lines.rebar_a500_d10.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_a500_d10.line_total` | `225101` | `225101` | `0` | `ok` |
| `estimate_lines.rebar_a240_d8.quantity_raw` | `48` | `48.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d8.quantity_display` | `48` | `48.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d8.material_total` | `1152` | `1152` | `0` | `ok` |
| `estimate_lines.rebar_a240_d8.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_a240_d8.line_total` | `1152` | `1152` | `0` | `ok` |
| `estimate_lines.rebar_a240_d6.quantity_raw` | `180` | `180.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d6.quantity_display` | `180` | `180.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d6.material_total_raw` | `2397.6` | `2397.6` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d6.material_total` | `2398` | `2398` | `0` | `ok` |
| `estimate_lines.rebar_a240_d6.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_a240_d6.line_total` | `2398` | `2398` | `0` | `ok` |
| `estimate_lines.floor_slab_concreting_work.quantity_raw` | `37.3752` | `37.3752` | `0.0` | `ok` |
| `estimate_lines.floor_slab_concreting_work.quantity_display` | `37.38` | `37.38` | `0.0` | `ok` |
| `estimate_lines.floor_slab_concreting_work.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.floor_slab_concreting_work.work_total_raw` | `448502.4` | `448502.4` | `0.0` | `ok` |
| `estimate_lines.floor_slab_concreting_work.work_total` | `448502` | `448502` | `0` | `ok` |
| `estimate_lines.floor_slab_concreting_work.line_total` | `448502` | `448502` | `0` | `ok` |
| `estimate_lines.beam_concreting_work.quantity_raw` | `23.2` | `23.2` | `0.0` | `ok` |
| `estimate_lines.beam_concreting_work.quantity_display` | `23.2` | `23.2` | `0.0` | `ok` |
| `estimate_lines.beam_concreting_work.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.beam_concreting_work.work_total` | `34800` | `34800` | `0` | `ok` |
| `estimate_lines.beam_concreting_work.line_total` | `34800` | `34800` | `0` | `ok` |
| `estimate_lines.concrete_b22_5_m300_material.quantity_raw` | `43` | `43.0` | `0.0` | `ok` |
| `estimate_lines.concrete_b22_5_m300_material.quantity_display` | `43` | `43.0` | `0.0` | `ok` |
| `estimate_lines.concrete_b22_5_m300_material.material_total` | `275200` | `275200` | `0` | `ok` |
| `estimate_lines.concrete_b22_5_m300_material.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.concrete_b22_5_m300_material.line_total` | `275200` | `275200` | `0` | `ok` |
| `estimate_lines.concrete_delivery.quantity_raw` | `5` | `5.0` | `0.0` | `ok` |
| `estimate_lines.concrete_delivery.quantity_display` | `5` | `5.0` | `0.0` | `ok` |
| `estimate_lines.concrete_delivery.material_total` | `37500` | `37500` | `0` | `ok` |
| `estimate_lines.concrete_delivery.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.concrete_delivery.line_total` | `37500` | `37500` | `0` | `ok` |
| `estimate_lines.concrete_pump_32m.quantity_raw` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.concrete_pump_32m.quantity_display` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.concrete_pump_32m.material_total` | `38000` | `38000` | `0` | `ok` |
| `estimate_lines.concrete_pump_32m.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.concrete_pump_32m.line_total` | `38000` | `38000` | `0` | `ok` |
| `estimate_lines.formwork_dismantling_zero_internal.quantity_raw` | `207.64` | `207.64` | `0.0` | `ok` |
| `estimate_lines.formwork_dismantling_zero_internal.quantity_display` | `207.6` | `207.6` | `0.0` | `ok` |
| `estimate_lines.formwork_dismantling_zero_internal.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_dismantling_zero_internal.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_dismantling_zero_internal.line_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.edge_beam_insulation_work.quantity_raw` | `108` | `108.0` | `0.0` | `ok` |
| `estimate_lines.edge_beam_insulation_work.quantity_display` | `108` | `108.0` | `0.0` | `ok` |
| `estimate_lines.edge_beam_insulation_work.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.edge_beam_insulation_work.work_total` | `48600` | `48600` | `0` | `ok` |
| `estimate_lines.edge_beam_insulation_work.line_total` | `48600` | `48600` | `0` | `ok` |
| `estimate_lines.bottom_slab_insulation_work.quantity_raw` | `51.92` | `51.92` | `0.0` | `ok` |
| `estimate_lines.bottom_slab_insulation_work.quantity_display` | `51.9` | `51.9` | `0.0` | `ok` |
| `estimate_lines.bottom_slab_insulation_work.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.bottom_slab_insulation_work.work_total` | `46728` | `46728` | `0` | `ok` |
| `estimate_lines.bottom_slab_insulation_work.line_total` | `46728` | `46728` | `0` | `ok` |
| `estimate_lines.eps_penoplex_osnova_100mm.quantity_raw` | `8.319` | `8.319` | `0.0` | `ok` |
| `estimate_lines.eps_penoplex_osnova_100mm.quantity_display` | `8.32` | `8.32` | `0.0` | `ok` |
| `estimate_lines.eps_penoplex_osnova_100mm.material_total_raw` | `75037.38` | `75037.38` | `0.0` | `ok` |
| `estimate_lines.eps_penoplex_osnova_100mm.material_total` | `75037` | `75037` | `0` | `ok` |
| `estimate_lines.eps_penoplex_osnova_100mm.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.eps_penoplex_osnova_100mm.line_total` | `75037` | `75037` | `0` | `ok` |
| `estimate_lines.eps_glue_foam.quantity_raw` | `8` | `8.0` | `0.0` | `ok` |
| `estimate_lines.eps_glue_foam.quantity_display` | `8` | `8.0` | `0.0` | `ok` |
| `estimate_lines.eps_glue_foam.material_total` | `3920` | `3920` | `0` | `ok` |
| `estimate_lines.eps_glue_foam.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.eps_glue_foam.line_total` | `3920` | `3920` | `0` | `ok` |
| `estimate_lines.logistics_and_supply.quantity_raw` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.logistics_and_supply.quantity_display` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.logistics_and_supply.material_total_raw` | `16636.723005` | `16636.723005` | `0.0` | `ok` |
| `estimate_lines.logistics_and_supply.material_total` | `16637` | `16637` | `0` | `ok` |
| `estimate_lines.logistics_and_supply.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.logistics_and_supply.line_total` | `16637` | `16637` | `0` | `ok` |
| `estimate_lines.consumables_tool_depreciation.quantity_raw` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.consumables_tool_depreciation.quantity_display` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.consumables_tool_depreciation.material_total_raw` | `49910.169016` | `49910.169016` | `0.0` | `ok` |
| `estimate_lines.consumables_tool_depreciation.material_total` | `49910` | `49910` | `0` | `ok` |
| `estimate_lines.consumables_tool_depreciation.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.consumables_tool_depreciation.line_total` | `49910` | `49910` | `0` | `ok` |
| `estimate_lines.technical_supervision.quantity_raw` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.technical_supervision.quantity_display` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.technical_supervision.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.technical_supervision.work_total` | `5000` | `5000` | `0` | `ok` |
| `estimate_lines.technical_supervision.line_total` | `5000` | `5000` | `0` | `ok` |
