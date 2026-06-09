# Расчёт фундаментной плиты: foundation_slab

Проект: `test_foundation_slab_formwork_spec_area`

## Входные параметры
- `project_name`: `test_foundation_slab_formwork_spec_area`
- `membrane_area_m2`: `320`
- `membrane_installation_work_unit_price`: `100`
- `membrane_overlap_coeff`: `1.1`
- `membrane_roll_area_m2`: `40`
- `planter_standard_roll_unit_price`: `5166`
- `planterband_per_membrane_roll`: `4`
- `planterband_unit_price`: `790`
- `formwork_installation_work_unit_price`: `0`
- `plywood_sheet_working_area_m2`: `2.25`
- `plywood_unit_price`: `1450`
- `timber_thickness_m`: `0.05`
- `timber_unit_price`: `21500`
- `eps50_under_slab_volume_m3`: `13.5`
- `eps50_thickness_m`: `0.05`
- `eps50_laying_work_unit_price`: `250`
- `eps_waste_coeff`: `1.05`
- `eps50_pack_volume_m3`: `0.2776`
- `eps50_unit_price`: `9800`
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
- `box_metal_delivery_capacity_kg`: `10000`
- `formwork_calc_method`: `spec_area`
- `slab_side_formwork_area_m2`: `24.3`
- `thermal_insert_mode`: `standard_50_100`
- `thermal_insert_50_length_m`: `10`
- `thermal_insert_100_length_m`: `15`
- `thermal_insert_50_work_unit_price`: `100`
- `thermal_insert_100_work_unit_price`: `100`
- `thermal_insert_50_material_spec_qty`: `1.0`
- `thermal_insert_100_material_spec_qty`: `0.5`
- `thermal_insert_material_waste_coeff`: `1.05`
- `thermal_insert_50_pack_multiple_qty`: `0.2776`
- `thermal_insert_100_pack_multiple_qty`: `0.2776`
- `thermal_insert_50_material_unit_price`: `9800`
- `thermal_insert_100_material_unit_price`: `10000`

## Формулы
- Монтаж мембраны: `quantity = membrane_area_m2`.
- Planter Standard: `rolls = ceil(membrane_area_m2 * overlap / roll_area)`.
- PLANTERBAND: `quantity = membrane_rolls * planterband_per_membrane_roll`.
- Опалубка: `formwork_area = slab_side_formwork_area_m2`.
- Фанера: `working_area` считает `ceil(formwork_area / plywood_sheet_working_area_m2)`, `actual_area_with_waste` считает через фактическую площадь листа и запас.
- Пиломатериал: `timber_volume = formwork_area * timber_thickness_m`.
- ЭППС 50 под плитой, работа: `area = eps50_under_slab_volume_m3 / eps50_thickness_m`.
- Работы термовставок 50 мм: `quantity = thermal_insert_50_length_m`.
- Работы термовставок 100 мм: `quantity = thermal_insert_100_length_m`.
- Материал термовставок 50 мм: `purchase_qty = round_up_to_multiple(spec_qty * thermal_insert_material_waste_coeff, thermal_insert_50_pack_multiple_qty)`.
- Материал термовставок 100 мм: `purchase_qty = round_up_to_multiple(spec_qty * thermal_insert_material_waste_coeff, thermal_insert_100_pack_multiple_qty)`.
- Арматура: вес -> м.п. -> запас 5% -> прутки -> закупочные м.п. -> стоимость.
- Бетонирование: работа по проектному объёму, материал с запасом и округлением вверх.
- Итог раздела: `internal_section_total = internal_materials_total + internal_works_total`.

## Подтверждённые правила Елены
- PLANTERBAND = количество рулонов мембраны * 4.
- Пиломатериал = площадь опалубки * 0.05, без дополнительного запаса.
- Пеноплэкс = ЭППС.
- Доставка металла ориентируется на 10 тонн на машину по листу Коробка.
- Фанера зависит от раскроя; текущий кейс считает через рабочую площадь 2.25 м2.
- В новом стандарте площадь опалубки бортов фундаментной плиты берётся из спецификации.
- Периметр и высота борта не являются обязательными входами для расчёта опалубки в production-стандарте.
- Фанера, пиломатериал, монтаж и демонтаж опалубки считаются от готовой площади опалубки.
- Термовставки считаются отдельно по 50 мм и 100 мм.
- Работы по термовставкам считаются по длине в м.п. из спецификации.
- Материал термовставок берётся из спецификации, умножается на 1.05 и округляется до кратности пачки.
- Старая логика через элемент, шаг 600 мм и термовкладыш 150 мм не используется в новом стандарте.

## Промежуточные расчёты
| Показатель | Значение |
| --- | ---: |
| `confirmed_rules` | `['PLANTERBAND = количество рулонов мембраны * 4.', 'Пиломатериал = площадь опалубки * 0.05, без дополнительного запаса.', 'Пеноплэкс = ЭППС.', 'Доставка металла ориентируется на 10 тонн на машину по листу Коробка.', 'Фанера зависит от раскроя; текущий кейс считает через рабочую площадь 2.25 м2.', 'В новом стандарте площадь опалубки бортов фундаментной плиты берётся из спецификации.', 'Периметр и высота борта не являются обязательными входами для расчёта опалубки в production-стандарте.', 'Фанера, пиломатериал, монтаж и демонтаж опалубки считаются от готовой площади опалубки.', 'Термовставки считаются отдельно по 50 мм и 100 мм.', 'Работы по термовставкам считаются по длине в м.п. из спецификации.', 'Материал термовставок берётся из спецификации, умножается на 1.05 и округляется до кратности пачки.', 'Старая логика через элемент, шаг 600 мм и термовкладыш 150 мм не используется в новом стандарте.']` |
| `membrane.membrane_area_with_overlap_m2` | `352.0` |
| `membrane.membrane_raw_rolls` | `8.8` |
| `membrane.membrane_rolls` | `9` |
| `membrane.planterband_quantity` | `36` |
| `formwork.formwork_calc_method` | `spec_area` |
| `formwork.slab_side_formwork_area_m2` | `24.3` |
| `formwork.formwork_area_m2` | `24.3` |
| `formwork.plywood_calc_method` | `working_area` |
| `formwork.plywood_sheet_working_area_m2` | `2.25` |
| `formwork.plywood_raw_sheets` | `10.8` |
| `formwork.plywood_sheets` | `11` |
| `formwork.timber_raw_volume_m3` | `1.215` |
| `eps.mode` | `standard_50_100` |
| `eps.eps50_laying_area_m2` | `270.0` |
| `eps.eps50_under_slab_required_volume_m3` | `14.175` |
| `eps.eps50_thermal_insert_volume_m3` | `0` |
| `eps.eps50_required_volume_m3` | `14.175` |
| `eps.eps50_raw_packs` | `51.0627` |
| `eps.eps50_packs` | `52` |
| `eps.eps50_order_volume_m3` | `14.4352` |
| `eps.eps100_required_volume_m3` | `0` |
| `eps.eps100_raw_packs` | `0` |
| `eps.eps100_packs` | `0` |
| `eps.eps100_order_volume_m3` | `0` |
| `thermal_insert.mode` | `standard_50_100` |
| `thermal_insert.thermal_insert_50_length_m` | `10` |
| `thermal_insert.thermal_insert_100_length_m` | `15` |
| `thermal_insert.thermal_insert_50_material_spec_qty` | `1.0` |
| `thermal_insert.thermal_insert_100_material_spec_qty` | `0.5` |
| `thermal_insert.thermal_insert_material_waste_coeff` | `1.05` |
| `thermal_insert.thermal_insert_50_material_raw_qty` | `1.05` |
| `thermal_insert.thermal_insert_100_material_raw_qty` | `0.525` |
| `thermal_insert.thermal_insert_50_pack_multiple_qty` | `0.2776` |
| `thermal_insert.thermal_insert_100_pack_multiple_qty` | `0.2776` |
| `thermal_insert.thermal_insert_50_material_purchase_qty` | `1.1104` |
| `thermal_insert.thermal_insert_100_material_purchase_qty` | `0.5552` |
| `thermal_insert.warnings` | `[]` |
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
- planter_membrane_installation_work_m2: price_code not found in price_registry, fallback input price used
- timber_formwork_installation_work_m2: price_code not found in price_registry and fallback input price is missing
- plywood_1520x1520_18mm_sheet: price_code not found in price_registry, fallback input price used
- timber_m3: price_code not found in price_registry, fallback input price used
- eps_laying_work_m2: price_code not found in price_registry, fallback input price used
- thermal_insert_50_installation_work_m: price_code not found in price_registry, fallback input price used
- thermal_insert_100_installation_work_m: price_code not found in price_registry, fallback input price used
- thermal_insert_50_material_m3: price_code not found in price_registry, fallback input price used
- thermal_insert_100_material_m3: price_code not found in price_registry, fallback input price used
- crane_shift: price_code not found in price_registry, fallback input price used
- metal_delivery_truck: price_code not found in price_registry, fallback input price used
- concrete_placing_work_m3: price_code not found in price_registry, fallback input price used
- concrete_b22_5_m3: price_code not found in price_registry, fallback input price used
- concrete_delivery_trip: price_code not found in price_registry, fallback input price used
- concrete_pump_32m_shift: price_code not found in price_registry, fallback input price used
- formwork_dismantling_work_m2: price_code not found in price_registry and fallback input price is missing
- technical_supervision_fixed: price_code not found in price_registry, fallback input price used

## Строки серой внутренней сметы
| code | name | line_type | quantity | display_quantity | unit | material_unit_price | material_total | work_unit_price | work_total | line_total |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `planter_membrane_installation` | Монтаж мембраны PLANTER стандарт | `` | `320.0` | `` | `м2` | `0.0` | `0` | `100.0` | `32000` | `32000` |
| `planter_standard_material` | Planter Standard Технониколь | `` | `9.0` | `` | `рул` | `4738.0` | `42642` | `0.0` | `0` | `42642` |
| `planterband_material` | PLANTERBAND 10м х 10см | `` | `36.0` | `` | `шт` | `750.0` | `27000` | `0.0` | `0` | `27000` |
| `formwork_installation` | Монтаж опалубки из пиломатериалов для отбортовки плиты | `` | `24.3` | `` | `м2` | `0.0` | `0` | `0` | `0` | `0` |
| `formwork_plywood` | Фанера ФК 1,52 * 1,52 толщиной 18 мм | `` | `11.0` | `` | `шт` | `1450.0` | `15950` | `0.0` | `0` | `15950` |
| `formwork_timber` | Пиломатериал обрезной хвойных пород ГОСТ | `` | `1.215` | `1.2` | `м3` | `21500.0` | `26123` | `0.0` | `0` | `26123` |
| `eps50_laying_under_slab` | Укладка ЭППС 50мм под плитой | `` | `270.0` | `` | `м2` | `0.0` | `0` | `250.0` | `67500` | `67500` |
| `thermal_insert_50_installation` | Устройство и монтаж термовставок 50 мм | `` | `10.0` | `` | `мп` | `0.0` | `0` | `100.0` | `1000` | `1000` |
| `thermal_insert_100_installation` | Устройство и монтаж термовставок 100 мм | `` | `15.0` | `` | `мп` | `0.0` | `0` | `100.0` | `1500` | `1500` |
| `eps50_penoplex_geo_material` | Пеноплэкс ГЕО 50 мм под плитой | `` | `14.4352` | `14.44` | `м3` | `8800.0` | `127030` | `0.0` | `0` | `127030` |
| `thermal_insert_50_material` | Материал термовставок 50 мм | `` | `1.1104` | `1.11` | `м3` | `9800.0` | `10882` | `0.0` | `0` | `10882` |
| `thermal_insert_100_material` | Материал термовставок 100 мм | `` | `0.5552` | `0.56` | `м3` | `10000.0` | `5552` | `0.0` | `0` | `5552` |
| `rebar_crane_supply` | Подача арматуры автокраном | `` | `1.0` | `` | `смена` | `30000.0` | `30000` | `0.0` | `0` | `30000` |
| `rebar_frame_assembly` | Изготовление и монтаж каркаса армирования фундаментной плиты из арматуры | `` | `8615.4` | `` | `мп` | `0.0` | `0` | `0.0` | `0` | `0` |
| `rebar_a500_d16` | Арматура класса А500 диаметром 16 мм | `` | `222.3` | `` | `мп` | `64.9` | `14427` | `0.0` | `0` | `14427` |
| `rebar_a500_d12` | Арматура класса А500 диаметром 12 мм | `` | `6388.2` | `` | `мп` | `36.85` | `235405` | `0.0` | `0` | `235405` |
| `rebar_a500_d10` | Арматура класса А500 диаметром 10 мм | `` | `1836.9` | `` | `мп` | `27.16` | `49890` | `0.0` | `0` | `49890` |
| `rebar_a240_d6` | Арматура класса А240 диаметром 6 мм | `` | `168.0` | `` | `мп` | `10.25` | `1722` | `0.0` | `0` | `1722` |
| `rebar_metal_delivery` | Доставка арматуры, металла | `` | `1.0` | `` | `маш` | `22000.0` | `22000` | `0.0` | `0` | `22000` |
| `foundation_slab_concreting_work` | Бетонирование фундаментной плиты в опалубке бетоном В22,5 (М300) | `` | `81.0` | `` | `м3` | `0.0` | `0` | `12000.0` | `972000` | `972000` |
| `concrete_b22_5_m300_material` | Бетон марки В22,5 (М300) | `` | `85.5` | `` | `м3` | `6400.0` | `547200` | `0.0` | `0` | `547200` |
| `concrete_delivery` | Доставка бетона до объекта | `` | `10.0` | `` | `рейс` | `7500.0` | `75000` | `0.0` | `0` | `75000` |
| `concrete_pump_32m` | Работа бетононасоса 32м + гаситель | `` | `1.0` | `` | `смена` | `38000.0` | `38000` | `0.0` | `0` | `38000` |
| `formwork_dismantling` | Демонтаж опалубки после завершения бетонирования | `` | `24.3` | `` | `м2` | `0.0` | `0` | `0` | `0` | `0` |
| `logistics_and_supply` | Логистика и снабжение | `` | `1.0` | `` | `-` | `36291.7` | `36292` | `0.0` | `0` | `36292` |
| `consumables_tool_amortization` | Расходные материалы, амортизация инструмента | `` | `1.0` | `` | `комплект` | `72583` | `72583` | `0.0` | `0` | `72583` |
| `technical_supervision` | Технический надзор | `` | `1.0` | `` | `-` | `0.0` | `0` | `10000.0` | `10000` | `10000` |
| `procurement_warehouse_costs_excel_structure` | Заготовительно-складские расходы | `zero_excel_structure_line` | `1.0` | `` | `-` | `0.0` | `0` | `0.0` | `0` | `0` |
| `overhead_general_business_costs_excel_structure` | Накладные и общехозяйственные расходы | `zero_excel_structure_line` | `1.0` | `` | `-` | `0.0` | `0` | `0.0` | `0` | `0` |
| `estimated_profit_excel_structure` | Сметная прибыль | `zero_excel_structure_line` | `1.0` | `` | `-` | `0.0` | `0` | `0.0` | `0` | `0` |

## Итоги серой внутренней сметы
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total` | `1377698` |
| `internal_works_total` | `1084000` |
| `internal_section_total` | `2461698` |
| `internal_materials_total_raw` | `1377697.824` |
| `internal_works_total_raw` | `1084000` |
| `internal_section_total_raw` | `2461697.824` |

## Источники цен

| Строка сметы | price_code | старая цена | использованная цена | источник | предупреждение |
| --- | --- | ---: | ---: | --- | --- |
| Монтаж мембраны PLANTER стандарт | `planter_membrane_installation_work_m2` | `100` | `100` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Planter Standard Технониколь | `planter_standard_roll` | `5166` | `4738` | `price_registry` |  |
| PLANTERBAND 10м х 10см | `planterband_item` | `790` | `750` | `price_registry` |  |
| Монтаж опалубки из пиломатериалов для отбортовки плиты | `timber_formwork_installation_work_m2` | `None` | `None` | `fallback_input` | price_code not found in price_registry and fallback input price is missing |
| Фанера ФК 1,52 * 1,52 толщиной 18 мм | `plywood_1520x1520_18mm_sheet` | `1450` | `1450` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Пиломатериал обрезной хвойных пород ГОСТ | `timber_m3` | `21500` | `21500` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Укладка ЭППС 50мм под плитой | `eps_laying_work_m2` | `250` | `250` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Устройство и монтаж термовставок 50 мм | `thermal_insert_50_installation_work_m` | `100` | `100` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Устройство и монтаж термовставок 100 мм | `thermal_insert_100_installation_work_m` | `100` | `100` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Пеноплэкс ГЕО 50 мм под плитой | `eps_geo_50_m3` | `9800` | `8800` | `price_registry` |  |
| Материал термовставок 50 мм | `thermal_insert_50_material_m3` | `9800` | `9800` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Материал термовставок 100 мм | `thermal_insert_100_material_m3` | `10000` | `10000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Подача арматуры автокраном | `crane_shift` | `30000` | `30000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Изготовление и монтаж каркаса армирования фундаментной плиты из арматуры | `` | `None` | `None` | `locked_case_prices` |  |
| Арматура класса А500 диаметром 16 мм | `rebar_a500_d16_m` | `80.58` | `64.9` | `price_registry` |  |
| Арматура класса А500 диаметром 12 мм | `rebar_a500_d12_m` | `45.29` | `36.85` | `price_registry` |  |
| Арматура класса А500 диаметром 10 мм | `rebar_a500_d10_m` | `32.72` | `27.16` | `price_registry` |  |
| Арматура класса А240 диаметром 6 мм | `rebar_a240_d6_m` | `13.32` | `10.25` | `price_registry` |  |
| Доставка арматуры, металла | `metal_delivery_truck` | `22000` | `22000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Бетонирование фундаментной плиты в опалубке бетоном В22,5 (М300) | `concrete_placing_work_m3` | `12000` | `12000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Бетон марки В22,5 (М300) | `concrete_b22_5_m3` | `6400` | `6400` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Доставка бетона до объекта | `concrete_delivery_trip` | `7500` | `7500` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Работа бетононасоса 32м + гаситель | `concrete_pump_32m_shift` | `38000` | `38000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Демонтаж опалубки после завершения бетонирования | `formwork_dismantling_work_m2` | `None` | `None` | `fallback_input` | price_code not found in price_registry and fallback input price is missing |
| Логистика и снабжение | `` | `36291.7` | `36291.7` | `locked_case_prices` |  |
| Расходные материалы, амортизация инструмента | `` | `72583` | `72583` | `locked_case_prices` |  |
| Технический надзор | `technical_supervision_fixed` | `10000` | `10000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Заготовительно-складские расходы | `` | `None` | `None` | `locked_case_prices` |  |
| Накладные и общехозяйственные расходы | `` | `None` | `None` | `locked_case_prices` |  |
| Сметная прибыль | `` | `None` | `None` | `locked_case_prices` |  |

## Pricing summary
| Показатель | Значение |
| --- | ---: |
| `mode` | `price_registry_with_fallback` |
| `registry_path` | `/Users/tatanamedzidova/Desktop/AI сметчик/ai_estimator_mvp/output/price_registry_filled_v3.xlsx` |
| `prices_from_price_registry` | `7` |
| `prices_from_project_overrides` | `0` |
| `prices_from_fallback_input` | `17` |
| `warnings_count` | `17` |

## Проверка с расчётом Елены
| Показатель | Ожидание | Получено | Разница | Статус |
| --- | ---: | ---: | ---: | --- |
| `calculation_blocks.formwork.formwork_calc_method` | `spec_area` | `spec_area` | `` | `ok` |
| `calculation_blocks.formwork.slab_side_formwork_area_m2` | `24.3` | `24.3` | `0.0` | `ok` |
| `calculation_blocks.formwork.formwork_area_m2` | `24.3` | `24.3` | `0.0` | `ok` |
| `calculation_blocks.formwork.plywood_calc_method` | `working_area` | `working_area` | `` | `ok` |
| `calculation_blocks.formwork.plywood_sheet_working_area_m2` | `2.25` | `2.25` | `0.0` | `ok` |
| `calculation_blocks.formwork.plywood_sheets` | `11` | `11` | `0` | `ok` |
| `calculation_blocks.formwork.timber_raw_volume_m3` | `1.215` | `1.215` | `0.0` | `ok` |
| `estimate_lines.formwork_installation.unit` | `м2` | `м2` | `` | `ok` |
| `estimate_lines.formwork_installation.quantity` | `24.3` | `24.3` | `0.0` | `ok` |
| `estimate_lines.formwork_installation.line_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.formwork_plywood.unit` | `шт` | `шт` | `` | `ok` |
| `estimate_lines.formwork_plywood.quantity` | `11` | `11.0` | `0.0` | `ok` |
| `estimate_lines.formwork_plywood.material_total` | `15950` | `15950` | `0` | `ok` |
| `estimate_lines.formwork_plywood.line_total` | `15950` | `15950` | `0` | `ok` |
| `estimate_lines.formwork_timber.unit` | `м3` | `м3` | `` | `ok` |
| `estimate_lines.formwork_timber.quantity` | `1.215` | `1.215` | `0.0` | `ok` |
| `estimate_lines.formwork_timber.display_quantity` | `1.2` | `1.2` | `0.0` | `ok` |
| `estimate_lines.formwork_timber.material_total` | `26123` | `26123` | `0` | `ok` |
| `estimate_lines.formwork_timber.line_total` | `26123` | `26123` | `0` | `ok` |
| `estimate_lines.formwork_dismantling.unit` | `м2` | `м2` | `` | `ok` |
| `estimate_lines.formwork_dismantling.quantity` | `24.3` | `24.3` | `0.0` | `ok` |
| `estimate_lines.formwork_dismantling.line_total` | `0` | `0` | `0` | `ok` |
| `internal_totals.internal_materials_total` | `1465557` | `1377698` | `-87859` | `mismatch` |
| `internal_totals.internal_works_total` | `1084000` | `1084000` | `0` | `ok` |
| `internal_totals.internal_section_total` | `2549557` | `2461698` | `-87859` | `mismatch` |
