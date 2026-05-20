# Расчёт фундаментной плиты: test_foundation_slab

Проект: `test_foundation_slab`

## Входные параметры
- `project_name`: `test_foundation_slab`
- `membrane_area_m2`: `320`
- `membrane_installation_work_unit_price`: `100`
- `membrane_overlap_coeff`: `1.1`
- `membrane_roll_area_m2`: `40`
- `planter_standard_roll_unit_price`: `5166`
- `planterband_per_membrane_roll`: `4`
- `planterband_unit_price`: `790`
- `slab_formwork_perimeter_m`: `81`
- `slab_edge_height_m`: `0.3`
- `formwork_installation_work_unit_price`: `0`
- `plywood_sheet_working_area_m2`: `2.25`
- `plywood_unit_price`: `1450`
- `timber_thickness_m`: `0.05`
- `timber_unit_price`: `21500`
- `eps50_under_slab_volume_m3`: `13.5`
- `eps50_thickness_m`: `0.05`
- `eps50_laying_work_unit_price`: `250`
- `eps_waste_coeff`: `1.05`
- `thermal_insert_length_m`: `21.5`
- `thermal_insert_piece_length_m`: `0.6`
- `thermal_insert_piece_width_m`: `0.15`
- `thermal_insert_piece_height_m`: `0.4`
- `thermal_insert_piece_depth_for_work_m`: `0.3`
- `thermal_insert_piece_depth_for_eps_m`: `0.25`
- `thermal_insert_installation_work_unit_price`: `100`
- `eps50_pack_volume_m3`: `0.2776`
- `eps50_unit_price`: `9800`
- `eps100_thickness_m`: `0.1`
- `eps100_pack_volume_m3`: `0.2776`
- `eps100_unit_price`: `10000`
- `rebar_crane_shifts`: `1`
- `rebar_crane_unit_price`: `30000`
- `rebar_waste_coeff`: `1.05`
- `rebar_items`: `[{'code': 'rebar_a500_d16', 'name': 'Арматура класса А500 диаметром 16 мм', 'steel_class': 'A500', 'diameter_mm': 16, 'weight_parts_kg': [328], 'kg_per_meter': 1.58, 'rod_length_m': 11.7, 'unit_price_per_m': 80.58}, {'code': 'rebar_a500_d12', 'name': 'Арматура класса А500 диаметром 12 мм', 'steel_class': 'A500', 'diameter_mm': 12, 'weight_parts_kg': [122, 5276], 'kg_per_meter': 0.888, 'rod_length_m': 11.7, 'unit_price_per_m': 45.29}, {'code': 'rebar_a500_d10', 'name': 'Арматура класса А500 диаметром 10 мм', 'steel_class': 'A500', 'diameter_mm': 10, 'weight_parts_kg': [1078], 'kg_per_meter': 0.617, 'rod_length_m': 11.7, 'unit_price_per_m': 32.72}, {'code': 'rebar_a240_d6', 'name': 'Арматура класса А240 диаметром 6 мм', 'steel_class': 'A240', 'diameter_mm': 6, 'weight_parts_kg': [35], 'kg_per_meter': 0.222, 'rod_length_m': 6, 'unit_price_per_m': 13.32}]`
- `rebar_metal_delivery_trucks`: `1`
- `rebar_metal_delivery_unit_price`: `22000`
- `box_total_metal_weight_kg`: `8263`
- `concrete_project_volume_m3`: `81`
- `concreting_work_unit_price`: `12000`
- `concrete_waste_coeff`: `1.05`
- `concrete_round_step_m3`: `0.5`
- `concrete_unit_price`: `6400`
- `concrete_mixer_volume_m3`: `9`
- `concrete_delivery_unit_price`: `7500`
- `concrete_pump_shifts`: `1`
- `concrete_pump_unit_price`: `38000`
- `formwork_dismantling_work_unit_price`: `0`
- `logistics_and_supply_amount`: `36291.7`
- `consumables_tool_amortization_amount`: `72583`
- `technical_supervision_amount`: `10000`
- `plywood_calc_method`: `working_area`
- `plywood_sheet_width_m`: `1.52`
- `plywood_sheet_height_m`: `1.52`
- `plywood_waste_coeff`: `1.05`
- `slab_edge_height_strategy`: `max_thickness`
- `box_metal_delivery_capacity_kg`: `10000`

## Формулы
- Монтаж мембраны: `quantity = membrane_area_m2`.
- Planter Standard: `rolls = ceil(membrane_area_m2 * overlap / roll_area)`.
- PLANTERBAND: `quantity = membrane_rolls * planterband_per_membrane_roll`.
- Опалубка: `formwork_area = slab_formwork_perimeter_m * slab_edge_height_m`.
- Фанера: `working_area` считает `ceil(formwork_area / plywood_sheet_working_area_m2)`, `actual_area_with_waste` считает через фактическую площадь листа и запас.
- Пиломатериал: `timber_volume = formwork_area * timber_thickness_m`.
- ЭППС 50 под плитой, работа: `area = eps50_under_slab_volume_m3 / eps50_thickness_m`.
- Термовкладыш: `pieces = ceil(thermal_insert_length_m / thermal_insert_piece_length_m)`.
- Арматура: вес -> м.п. -> запас 5% -> прутки -> закупочные м.п. -> стоимость.
- Бетонирование: работа по проектному объёму, материал с запасом и округлением вверх.
- Итог раздела: `internal_section_total = internal_materials_total + internal_works_total`.

## Подтверждённые правила Елены
- PLANTERBAND = количество рулонов мембраны * 4.
- Борта = внешний периметр фундаментной плиты.
- При разных толщинах плит можно брать максимальную толщину.
- Пиломатериал = площадь опалубки * 0.05, без дополнительного запаса.
- Пеноплэкс = ЭППС.
- ЭППС 50 мм + ЭППС 100 мм = термовкладыш 150 мм.
- Доставка металла ориентируется на 10 тонн на машину по листу Коробка.
- Фанера зависит от раскроя; текущий кейс считает через рабочую площадь 2.25 м2.

## Промежуточные расчёты
| Показатель | Значение |
| --- | ---: |
| `confirmed_rules` | `['PLANTERBAND = количество рулонов мембраны * 4.', 'Борта = внешний периметр фундаментной плиты.', 'При разных толщинах плит можно брать максимальную толщину.', 'Пиломатериал = площадь опалубки * 0.05, без дополнительного запаса.', 'Пеноплэкс = ЭППС.', 'ЭППС 50 мм + ЭППС 100 мм = термовкладыш 150 мм.', 'Доставка металла ориентируется на 10 тонн на машину по листу Коробка.', 'Фанера зависит от раскроя; текущий кейс считает через рабочую площадь 2.25 м2.']` |
| `membrane.membrane_area_with_overlap_m2` | `352.0` |
| `membrane.membrane_raw_rolls` | `8.8` |
| `membrane.membrane_rolls` | `9` |
| `membrane.planterband_quantity` | `36` |
| `formwork.formwork_area_m2` | `24.3` |
| `formwork.slab_edge_height_strategy` | `max_thickness` |
| `formwork.plywood_calc_method` | `working_area` |
| `formwork.plywood_sheet_working_area_m2` | `2.25` |
| `formwork.plywood_raw_sheets` | `10.8` |
| `formwork.plywood_sheets` | `11` |
| `formwork.timber_raw_volume_m3` | `1.215` |
| `eps.eps50_laying_area_m2` | `270.0` |
| `eps.eps50_under_slab_required_volume_m3` | `14.175` |
| `eps.eps50_thermal_insert_volume_m3` | `0.18` |
| `eps.eps50_required_volume_m3` | `14.355` |
| `eps.eps50_raw_packs` | `51.7111` |
| `eps.eps50_packs` | `52` |
| `eps.eps50_order_volume_m3` | `14.4352` |
| `eps.eps100_required_volume_m3` | `0.36` |
| `eps.eps100_raw_packs` | `1.2968` |
| `eps.eps100_packs` | `2` |
| `eps.eps100_order_volume_m3` | `0.5552` |
| `thermal_insert.thermal_insert_raw_pieces` | `35.8333` |
| `thermal_insert.thermal_insert_pieces` | `36` |
| `thermal_insert.thermal_insert_control_volume_m3` | `0.648` |
| `thermal_insert.thermal_insert_piece_depth_for_eps_m` | `0.25` |
| `thermal_insert.slab_edge_height_m` | `0.3` |
| `thermal_insert.warnings` | `['thermal_insert_piece_depth_for_eps_m отличается от slab_edge_height_m; Елена уточнила, что обычно берём высоту плиты, но в текущем кейсе Excel использует/даёт значение, которое после округления не меняет закупку.']` |
| `rebar.items.rebar_a500_d16.name` | `Арматура класса А500 диаметром 16 мм` |
| `rebar.items.rebar_a500_d16.steel_class` | `A500` |
| `rebar.items.rebar_a500_d16.diameter_mm` | `16` |
| `rebar.items.rebar_a500_d16.weight_parts_kg` | `[328]` |
| `rebar.items.rebar_a500_d16.total_weight_kg` | `328.0` |
| `rebar.items.rebar_a500_d16.raw_length_m` | `207.5949` |
| `rebar.items.rebar_a500_d16.length_with_waste_m` | `217.9746` |
| `rebar.items.rebar_a500_d16.raw_rods` | `18.6303` |
| `rebar.items.rebar_a500_d16.rods` | `19` |
| `rebar.items.rebar_a500_d16.order_length_m` | `222.3` |
| `rebar.items.rebar_a500_d16.control_weight_kg` | `344.3999` |
| `rebar.items.rebar_a500_d12.name` | `Арматура класса А500 диаметром 12 мм` |
| `rebar.items.rebar_a500_d12.steel_class` | `A500` |
| `rebar.items.rebar_a500_d12.diameter_mm` | `12` |
| `rebar.items.rebar_a500_d12.weight_parts_kg` | `[122, 5276]` |
| `rebar.items.rebar_a500_d12.total_weight_kg` | `5398.0` |
| `rebar.items.rebar_a500_d12.raw_length_m` | `6078.8288` |
| `rebar.items.rebar_a500_d12.length_with_waste_m` | `6382.7702` |
| `rebar.items.rebar_a500_d12.raw_rods` | `545.5359` |
| `rebar.items.rebar_a500_d12.rods` | `546` |
| `rebar.items.rebar_a500_d12.order_length_m` | `6388.2` |
| `rebar.items.rebar_a500_d12.control_weight_kg` | `5667.8999` |
| `rebar.items.rebar_a500_d10.name` | `Арматура класса А500 диаметром 10 мм` |
| `rebar.items.rebar_a500_d10.steel_class` | `A500` |
| `rebar.items.rebar_a500_d10.diameter_mm` | `10` |
| `rebar.items.rebar_a500_d10.weight_parts_kg` | `[1078]` |
| `rebar.items.rebar_a500_d10.total_weight_kg` | `1078.0` |
| `rebar.items.rebar_a500_d10.raw_length_m` | `1747.1637` |
| `rebar.items.rebar_a500_d10.length_with_waste_m` | `1834.5219` |
| `rebar.items.rebar_a500_d10.raw_rods` | `156.7967` |
| `rebar.items.rebar_a500_d10.rods` | `157` |
| `rebar.items.rebar_a500_d10.order_length_m` | `1836.9` |
| `rebar.items.rebar_a500_d10.control_weight_kg` | `1131.9` |
| `rebar.items.rebar_a240_d6.name` | `Арматура класса А240 диаметром 6 мм` |
| `rebar.items.rebar_a240_d6.steel_class` | `A240` |
| `rebar.items.rebar_a240_d6.diameter_mm` | `6` |
| `rebar.items.rebar_a240_d6.weight_parts_kg` | `[35]` |
| `rebar.items.rebar_a240_d6.total_weight_kg` | `35.0` |
| `rebar.items.rebar_a240_d6.raw_length_m` | `157.6577` |
| `rebar.items.rebar_a240_d6.length_with_waste_m` | `165.5406` |
| `rebar.items.rebar_a240_d6.raw_rods` | `27.5901` |
| `rebar.items.rebar_a240_d6.rods` | `28` |
| `rebar.items.rebar_a240_d6.order_length_m` | `168.0` |
| `rebar.items.rebar_a240_d6.control_weight_kg` | `36.75` |
| `rebar.rebar_frame_assembly_quantity_m` | `8615.4` |
| `rebar.foundation_slab_rebar_control_weight_kg` | `7180.9498` |
| `rebar.box_total_metal_weight_kg` | `8263` |
| `rebar.box_metal_delivery_capacity_kg` | `10000` |
| `rebar.suggested_box_metal_delivery_trucks` | `1` |
| `rebar.actual_rebar_metal_delivery_trucks` | `1` |
| `rebar.warnings` | `[]` |
| `concrete.concrete_raw_order_volume_m3` | `85.05` |
| `concrete.concrete_order_volume_m3` | `85.5` |
| `concrete.concrete_delivery_raw_trips` | `9.5` |
| `concrete.concrete_delivery_trips` | `10` |
| `concrete.reinforcement_density_kg_per_m3` | `88.6537` |
| `concrete.reinforcement_density_kg_per_m3_rounded` | `89` |
| `manual_lines.rebar_crane_supply.quantity` | `1` |
| `manual_lines.rebar_crane_supply.unit_price` | `30000` |
| `manual_lines.rebar_crane_supply.line_type` | `fixed/manual` |
| `manual_lines.rebar_metal_delivery.quantity` | `1` |
| `manual_lines.rebar_metal_delivery.unit_price` | `22000` |
| `manual_lines.rebar_metal_delivery.line_type` | `fixed/manual` |
| `manual_lines.concrete_pump_32m.quantity` | `1` |
| `manual_lines.concrete_pump_32m.unit_price` | `38000` |
| `manual_lines.concrete_pump_32m.line_type` | `fixed/manual` |
| `manual_lines.logistics_and_supply.quantity` | `1` |
| `manual_lines.logistics_and_supply.unit_price` | `36291.7` |
| `manual_lines.logistics_and_supply.line_type` | `fixed/manual` |
| `manual_lines.consumables_tool_amortization.quantity` | `1` |
| `manual_lines.consumables_tool_amortization.unit_price` | `72583` |
| `manual_lines.consumables_tool_amortization.line_type` | `fixed/manual` |
| `manual_lines.technical_supervision.quantity` | `1` |
| `manual_lines.technical_supervision.unit_price` | `10000` |
| `manual_lines.technical_supervision.line_type` | `fixed/manual` |

## Предупреждения
- thermal_insert: thermal_insert_piece_depth_for_eps_m отличается от slab_edge_height_m; Елена уточнила, что обычно берём высоту плиты, но в текущем кейсе Excel использует/даёт значение, которое после округления не меняет закупку.

## Строки серой внутренней сметы
| code | name | quantity | display_quantity | unit | material_unit_price | material_total | work_unit_price | work_total | line_total |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `planter_membrane_installation` | Монтаж мембраны PLANTER стандарт | `320.0` | `` | `м2` | `0.0` | `0` | `100` | `32000` | `32000` |
| `planter_standard_material` | Planter Standard Технониколь | `9.0` | `` | `рул` | `5166` | `46494` | `0.0` | `0` | `46494` |
| `planterband_material` | PLANTERBAND 10м х 10см | `36.0` | `` | `шт` | `790` | `28440` | `0.0` | `0` | `28440` |
| `formwork_installation` | Монтаж опалубки из пиломатериалов для отбортовки плиты | `24.3` | `` | `м2` | `0.0` | `0` | `0` | `0` | `0` |
| `formwork_plywood` | Фанера ФК 1,52 * 1,52 толщиной 18 мм | `11.0` | `` | `шт` | `1450` | `15950` | `0.0` | `0` | `15950` |
| `formwork_timber` | Пиломатериал обрезной хвойных пород ГОСТ | `1.215` | `1.2` | `м3` | `21500` | `26123` | `0.0` | `0` | `26123` |
| `eps50_laying_under_slab` | Укладка ЭППС 50мм под плитой | `270.0` | `` | `м2` | `0.0` | `0` | `250` | `67500` | `67500` |
| `thermal_insert_installation` | Устройство и монтаж термовкладыша 150*400*250мм шаг 200мм | `21.5` | `` | `мп` | `0.0` | `0` | `100` | `2150` | `2150` |
| `eps50_penoplex_geo_material` | Пеноплэкс ГЕО 50 мм | `14.4352` | `14.44` | `м3` | `9800` | `141465` | `0.0` | `0` | `141465` |
| `eps100_penoplex_geo_material` | Пеноплэкс ГЕО 100 мм | `0.5552` | `0.56` | `м3` | `10000` | `5552` | `0.0` | `0` | `5552` |
| `rebar_crane_supply` | Подача арматуры автокраном | `1.0` | `` | `смена` | `30000` | `30000` | `0.0` | `0` | `30000` |
| `rebar_frame_assembly` | Изготовление и монтаж каркаса армирования фундаментной плиты из арматуры | `8615.4` | `` | `мп` | `0.0` | `0` | `0.0` | `0` | `0` |
| `rebar_a500_d16` | Арматура класса А500 диаметром 16 мм | `222.3` | `` | `мп` | `80.58` | `17913` | `0.0` | `0` | `17913` |
| `rebar_a500_d12` | Арматура класса А500 диаметром 12 мм | `6388.2` | `` | `мп` | `45.29` | `289322` | `0.0` | `0` | `289322` |
| `rebar_a500_d10` | Арматура класса А500 диаметром 10 мм | `1836.9` | `` | `мп` | `32.72` | `60103` | `0.0` | `0` | `60103` |
| `rebar_a240_d6` | Арматура класса А240 диаметром 6 мм | `168.0` | `` | `мп` | `13.32` | `2238` | `0.0` | `0` | `2238` |
| `rebar_metal_delivery` | Доставка арматуры, металла | `1.0` | `` | `маш` | `22000` | `22000` | `0.0` | `0` | `22000` |
| `foundation_slab_concreting_work` | Бетонирование фундаментной плиты в опалубке бетоном В22,5 (М300) | `81.0` | `` | `м3` | `0.0` | `0` | `12000` | `972000` | `972000` |
| `concrete_b22_5_m300_material` | Бетон марки В22,5 (М300) | `85.5` | `` | `м3` | `6400` | `547200` | `0.0` | `0` | `547200` |
| `concrete_delivery` | Доставка бетона до объекта | `10.0` | `` | `рейс` | `7500` | `75000` | `0.0` | `0` | `75000` |
| `concrete_pump_32m` | Работа бетононасоса 32м + гаситель | `1.0` | `` | `смена` | `38000` | `38000` | `0.0` | `0` | `38000` |
| `formwork_dismantling` | Демонтаж опалубки после завершения бетонирования | `24.3` | `` | `м2` | `0.0` | `0` | `0` | `0` | `0` |
| `logistics_and_supply` | Логистика и снабжение | `1.0` | `` | `-` | `36291.7` | `36292` | `0.0` | `0` | `36292` |
| `consumables_tool_amortization` | Расходные материалы, амортизация инструмента | `1.0` | `` | `комплект` | `72583` | `72583` | `0.0` | `0` | `72583` |
| `technical_supervision` | Технический надзор | `1.0` | `` | `-` | `0.0` | `0` | `10000` | `10000` | `10000` |

## Итоги серой внутренней сметы
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total` | `1454675` |
| `internal_works_total` | `1083650` |
| `internal_section_total` | `2538325` |

## Проверка с расчётом Елены
| Показатель | Ожидание | Получено | Разница | Статус |
| --- | ---: | ---: | ---: | --- |
| `calculation_blocks.membrane.membrane_rolls` | `9` | `9` | `0` | `ok` |
| `calculation_blocks.membrane.planterband_quantity` | `36` | `36` | `0` | `ok` |
| `calculation_blocks.formwork.formwork_area_m2` | `24.3` | `24.3` | `0.0` | `ok` |
| `calculation_blocks.formwork.plywood_calc_method` | `working_area` | `working_area` | `` | `ok` |
| `calculation_blocks.formwork.plywood_sheet_working_area_m2` | `2.25` | `2.25` | `0.0` | `ok` |
| `calculation_blocks.formwork.plywood_sheets` | `11` | `11` | `0` | `ok` |
| `calculation_blocks.formwork.timber_raw_volume_m3` | `1.215` | `1.215` | `0.0` | `ok` |
| `calculation_blocks.eps.eps50_laying_area_m2` | `270` | `270.0` | `0.0` | `ok` |
| `calculation_blocks.eps.eps50_order_volume_m3` | `14.4352` | `14.4352` | `0.0` | `ok` |
| `calculation_blocks.eps.eps100_order_volume_m3` | `0.5552` | `0.5552` | `0.0` | `ok` |
| `calculation_blocks.thermal_insert.thermal_insert_pieces` | `36` | `36` | `0` | `ok` |
| `calculation_blocks.rebar.items.rebar_a500_d16.order_length_m` | `222.3` | `222.3` | `0.0` | `ok` |
| `calculation_blocks.rebar.items.rebar_a500_d12.order_length_m` | `6388.2` | `6388.2` | `0.0` | `ok` |
| `calculation_blocks.rebar.items.rebar_a500_d10.order_length_m` | `1836.9` | `1836.9` | `0.0` | `ok` |
| `calculation_blocks.rebar.items.rebar_a240_d6.order_length_m` | `168` | `168.0` | `0.0` | `ok` |
| `calculation_blocks.rebar.rebar_frame_assembly_quantity_m` | `8615.4` | `8615.4` | `0.0` | `ok` |
| `calculation_blocks.rebar.foundation_slab_rebar_control_weight_kg` | `7180.9498` | `7180.9498` | `0.0` | `ok` |
| `calculation_blocks.rebar.box_total_metal_weight_kg` | `8263` | `8263` | `0` | `ok` |
| `calculation_blocks.rebar.box_metal_delivery_capacity_kg` | `10000` | `10000` | `0` | `ok` |
| `calculation_blocks.rebar.suggested_box_metal_delivery_trucks` | `1` | `1` | `0` | `ok` |
| `calculation_blocks.rebar.actual_rebar_metal_delivery_trucks` | `1` | `1` | `0` | `ok` |
| `calculation_blocks.concrete.concrete_order_volume_m3` | `85.5` | `85.5` | `0.0` | `ok` |
| `calculation_blocks.concrete.concrete_delivery_trips` | `10` | `10` | `0` | `ok` |
| `calculation_blocks.concrete.reinforcement_density_kg_per_m3_rounded` | `89` | `89` | `0` | `ok` |
| `estimate_lines.planter_membrane_installation.unit` | `м2` | `м2` | `` | `ok` |
| `estimate_lines.planter_membrane_installation.quantity` | `320` | `320.0` | `0.0` | `ok` |
| `estimate_lines.planter_membrane_installation.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.planter_membrane_installation.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.planter_membrane_installation.work_unit_price` | `100` | `100` | `0` | `ok` |
| `estimate_lines.planter_membrane_installation.work_total` | `32000` | `32000` | `0` | `ok` |
| `estimate_lines.planter_membrane_installation.line_total` | `32000` | `32000` | `0` | `ok` |
| `estimate_lines.planter_standard_material.unit` | `рул` | `рул` | `` | `ok` |
| `estimate_lines.planter_standard_material.quantity` | `9` | `9.0` | `0.0` | `ok` |
| `estimate_lines.planter_standard_material.material_unit_price` | `5166` | `5166` | `0` | `ok` |
| `estimate_lines.planter_standard_material.material_total` | `46494` | `46494` | `0` | `ok` |
| `estimate_lines.planter_standard_material.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.planter_standard_material.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.planter_standard_material.line_total` | `46494` | `46494` | `0` | `ok` |
| `estimate_lines.planterband_material.unit` | `шт` | `шт` | `` | `ok` |
| `estimate_lines.planterband_material.quantity` | `36` | `36.0` | `0.0` | `ok` |
| `estimate_lines.planterband_material.material_unit_price` | `790` | `790` | `0` | `ok` |
| `estimate_lines.planterband_material.material_total` | `28440` | `28440` | `0` | `ok` |
| `estimate_lines.planterband_material.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.planterband_material.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.planterband_material.line_total` | `28440` | `28440` | `0` | `ok` |
| `estimate_lines.formwork_installation.unit` | `м2` | `м2` | `` | `ok` |
| `estimate_lines.formwork_installation.quantity` | `24.3` | `24.3` | `0.0` | `ok` |
| `estimate_lines.formwork_installation.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.formwork_installation.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_installation.work_unit_price` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_installation.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_installation.line_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_plywood.unit` | `шт` | `шт` | `` | `ok` |
| `estimate_lines.formwork_plywood.quantity` | `11` | `11.0` | `0.0` | `ok` |
| `estimate_lines.formwork_plywood.material_unit_price` | `1450` | `1450` | `0` | `ok` |
| `estimate_lines.formwork_plywood.material_total` | `15950` | `15950` | `0` | `ok` |
| `estimate_lines.formwork_plywood.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.formwork_plywood.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_plywood.line_total` | `15950` | `15950` | `0` | `ok` |
| `estimate_lines.formwork_timber.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.formwork_timber.quantity` | `1.215` | `1.215` | `0.0` | `ok` |
| `estimate_lines.formwork_timber.display_quantity` | `1.2` | `1.2` | `0.0` | `ok` |
| `estimate_lines.formwork_timber.material_unit_price` | `21500` | `21500` | `0` | `ok` |
| `estimate_lines.formwork_timber.material_total` | `26123` | `26123` | `0` | `ok` |
| `estimate_lines.formwork_timber.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.formwork_timber.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_timber.line_total` | `26123` | `26123` | `0` | `ok` |
| `estimate_lines.eps50_laying_under_slab.unit` | `м2` | `м2` | `` | `ok` |
| `estimate_lines.eps50_laying_under_slab.quantity` | `270` | `270.0` | `0.0` | `ok` |
| `estimate_lines.eps50_laying_under_slab.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.eps50_laying_under_slab.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.eps50_laying_under_slab.work_unit_price` | `250` | `250` | `0` | `ok` |
| `estimate_lines.eps50_laying_under_slab.work_total` | `67500` | `67500` | `0` | `ok` |
| `estimate_lines.eps50_laying_under_slab.line_total` | `67500` | `67500` | `0` | `ok` |
| `estimate_lines.thermal_insert_installation.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.thermal_insert_installation.quantity` | `21.5` | `21.5` | `0.0` | `ok` |
| `estimate_lines.thermal_insert_installation.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.thermal_insert_installation.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.thermal_insert_installation.work_unit_price` | `100` | `100` | `0` | `ok` |
| `estimate_lines.thermal_insert_installation.work_total` | `2150` | `2150` | `0` | `ok` |
| `estimate_lines.thermal_insert_installation.line_total` | `2150` | `2150` | `0` | `ok` |
| `estimate_lines.eps50_penoplex_geo_material.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.eps50_penoplex_geo_material.quantity` | `14.4352` | `14.4352` | `0.0` | `ok` |
| `estimate_lines.eps50_penoplex_geo_material.display_quantity` | `14.44` | `14.44` | `0.0` | `ok` |
| `estimate_lines.eps50_penoplex_geo_material.material_unit_price` | `9800` | `9800` | `0` | `ok` |
| `estimate_lines.eps50_penoplex_geo_material.material_total` | `141465` | `141465` | `0` | `ok` |
| `estimate_lines.eps50_penoplex_geo_material.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.eps50_penoplex_geo_material.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.eps50_penoplex_geo_material.line_total` | `141465` | `141465` | `0` | `ok` |
| `estimate_lines.eps100_penoplex_geo_material.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.eps100_penoplex_geo_material.quantity` | `0.5552` | `0.5552` | `0.0` | `ok` |
| `estimate_lines.eps100_penoplex_geo_material.display_quantity` | `0.56` | `0.56` | `0.0` | `ok` |
| `estimate_lines.eps100_penoplex_geo_material.material_unit_price` | `10000` | `10000` | `0` | `ok` |
| `estimate_lines.eps100_penoplex_geo_material.material_total` | `5552` | `5552` | `0` | `ok` |
| `estimate_lines.eps100_penoplex_geo_material.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.eps100_penoplex_geo_material.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.eps100_penoplex_geo_material.line_total` | `5552` | `5552` | `0` | `ok` |
| `estimate_lines.rebar_crane_supply.unit` | `смена` | `смена` | `` | `ok` |
| `estimate_lines.rebar_crane_supply.quantity` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.rebar_crane_supply.material_unit_price` | `30000` | `30000` | `0` | `ok` |
| `estimate_lines.rebar_crane_supply.material_total` | `30000` | `30000` | `0` | `ok` |
| `estimate_lines.rebar_crane_supply.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.rebar_crane_supply.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_crane_supply.line_total` | `30000` | `30000` | `0` | `ok` |
| `estimate_lines.rebar_frame_assembly.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.rebar_frame_assembly.quantity` | `8615.4` | `8615.4` | `0.0` | `ok` |
| `estimate_lines.rebar_frame_assembly.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.rebar_frame_assembly.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_frame_assembly.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.rebar_frame_assembly.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_frame_assembly.line_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_a500_d16.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.rebar_a500_d16.quantity` | `222.3` | `222.3` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d16.material_unit_price` | `80.58` | `80.58` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d16.material_total` | `17913` | `17913` | `0` | `ok` |
| `estimate_lines.rebar_a500_d16.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d16.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_a500_d16.line_total` | `17913` | `17913` | `0` | `ok` |
| `estimate_lines.rebar_a500_d12.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.rebar_a500_d12.quantity` | `6388.2` | `6388.2` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d12.material_unit_price` | `45.29` | `45.29` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d12.material_total` | `289322` | `289322` | `0` | `ok` |
| `estimate_lines.rebar_a500_d12.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d12.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_a500_d12.line_total` | `289322` | `289322` | `0` | `ok` |
| `estimate_lines.rebar_a500_d10.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.rebar_a500_d10.quantity` | `1836.9` | `1836.9` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d10.material_unit_price` | `32.72` | `32.72` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d10.material_total` | `60103` | `60103` | `0` | `ok` |
| `estimate_lines.rebar_a500_d10.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a500_d10.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_a500_d10.line_total` | `60103` | `60103` | `0` | `ok` |
| `estimate_lines.rebar_a240_d6.unit` | `мп` | `мп` | `` | `ok` |
| `estimate_lines.rebar_a240_d6.quantity` | `168` | `168.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d6.material_unit_price` | `13.32` | `13.32` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d6.material_total` | `2238` | `2238` | `0` | `ok` |
| `estimate_lines.rebar_a240_d6.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.rebar_a240_d6.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_a240_d6.line_total` | `2238` | `2238` | `0` | `ok` |
| `estimate_lines.rebar_metal_delivery.unit` | `маш` | `маш` | `` | `ok` |
| `estimate_lines.rebar_metal_delivery.quantity` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.rebar_metal_delivery.material_unit_price` | `22000` | `22000` | `0` | `ok` |
| `estimate_lines.rebar_metal_delivery.material_total` | `22000` | `22000` | `0` | `ok` |
| `estimate_lines.rebar_metal_delivery.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.rebar_metal_delivery.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.rebar_metal_delivery.line_total` | `22000` | `22000` | `0` | `ok` |
| `estimate_lines.foundation_slab_concreting_work.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.foundation_slab_concreting_work.quantity` | `81` | `81.0` | `0.0` | `ok` |
| `estimate_lines.foundation_slab_concreting_work.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.foundation_slab_concreting_work.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.foundation_slab_concreting_work.work_unit_price` | `12000` | `12000` | `0` | `ok` |
| `estimate_lines.foundation_slab_concreting_work.work_total` | `972000` | `972000` | `0` | `ok` |
| `estimate_lines.foundation_slab_concreting_work.line_total` | `972000` | `972000` | `0` | `ok` |
| `estimate_lines.concrete_b22_5_m300_material.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.concrete_b22_5_m300_material.quantity` | `85.5` | `85.5` | `0.0` | `ok` |
| `estimate_lines.concrete_b22_5_m300_material.material_unit_price` | `6400` | `6400` | `0` | `ok` |
| `estimate_lines.concrete_b22_5_m300_material.material_total` | `547200` | `547200` | `0` | `ok` |
| `estimate_lines.concrete_b22_5_m300_material.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.concrete_b22_5_m300_material.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.concrete_b22_5_m300_material.line_total` | `547200` | `547200` | `0` | `ok` |
| `estimate_lines.concrete_delivery.unit` | `рейс` | `рейс` | `` | `ok` |
| `estimate_lines.concrete_delivery.quantity` | `10` | `10.0` | `0.0` | `ok` |
| `estimate_lines.concrete_delivery.material_unit_price` | `7500` | `7500` | `0` | `ok` |
| `estimate_lines.concrete_delivery.material_total` | `75000` | `75000` | `0` | `ok` |
| `estimate_lines.concrete_delivery.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.concrete_delivery.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.concrete_delivery.line_total` | `75000` | `75000` | `0` | `ok` |
| `estimate_lines.concrete_pump_32m.unit` | `смена` | `смена` | `` | `ok` |
| `estimate_lines.concrete_pump_32m.quantity` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.concrete_pump_32m.material_unit_price` | `38000` | `38000` | `0` | `ok` |
| `estimate_lines.concrete_pump_32m.material_total` | `38000` | `38000` | `0` | `ok` |
| `estimate_lines.concrete_pump_32m.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.concrete_pump_32m.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.concrete_pump_32m.line_total` | `38000` | `38000` | `0` | `ok` |
| `estimate_lines.formwork_dismantling.unit` | `м2` | `м2` | `` | `ok` |
| `estimate_lines.formwork_dismantling.quantity` | `24.3` | `24.3` | `0.0` | `ok` |
| `estimate_lines.formwork_dismantling.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.formwork_dismantling.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_dismantling.work_unit_price` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_dismantling.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_dismantling.line_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.logistics_and_supply.unit` | `-` | `-` | `` | `ok` |
| `estimate_lines.logistics_and_supply.quantity` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.logistics_and_supply.material_unit_price` | `36291.7` | `36291.7` | `0.0` | `ok` |
| `estimate_lines.logistics_and_supply.material_total` | `36292` | `36292` | `0` | `ok` |
| `estimate_lines.logistics_and_supply.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.logistics_and_supply.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.logistics_and_supply.line_total` | `36292` | `36292` | `0` | `ok` |
| `estimate_lines.consumables_tool_amortization.unit` | `комплект` | `комплект` | `` | `ok` |
| `estimate_lines.consumables_tool_amortization.quantity` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.consumables_tool_amortization.material_unit_price` | `72583` | `72583` | `0` | `ok` |
| `estimate_lines.consumables_tool_amortization.material_total` | `72583` | `72583` | `0` | `ok` |
| `estimate_lines.consumables_tool_amortization.work_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.consumables_tool_amortization.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.consumables_tool_amortization.line_total` | `72583` | `72583` | `0` | `ok` |
| `estimate_lines.technical_supervision.unit` | `-` | `-` | `` | `ok` |
| `estimate_lines.technical_supervision.quantity` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.technical_supervision.material_unit_price` | `0` | `0.0` | `0.0` | `ok` |
| `estimate_lines.technical_supervision.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.technical_supervision.work_unit_price` | `10000` | `10000` | `0` | `ok` |
| `estimate_lines.technical_supervision.work_total` | `10000` | `10000` | `0` | `ok` |
| `estimate_lines.technical_supervision.line_total` | `10000` | `10000` | `0` | `ok` |
| `internal_totals.internal_materials_total` | `1454675` | `1454675` | `0` | `ok` |
| `internal_totals.internal_works_total` | `1083650` | `1083650` | `0` | `ok` |
| `internal_totals.internal_section_total` | `2538325` | `2538325` | `0` | `ok` |
