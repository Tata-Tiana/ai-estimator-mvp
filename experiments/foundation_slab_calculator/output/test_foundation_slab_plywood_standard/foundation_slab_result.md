# Расчёт фундаментной плиты: test_foundation_slab_plywood_standard

Проект: `test_foundation_slab_plywood_standard`

## Входные параметры
- `project_name`: `test_foundation_slab_plywood_standard`
- `membrane_area_m2`: `320`
- `membrane_installation_work_unit_price`: `100`
- `membrane_overlap_coeff`: `1.1`
- `membrane_roll_area_m2`: `40`
- `planter_standard_roll_unit_price`: `5166`
- `planterband_per_membrane_roll`: `4`
- `planterband_unit_price`: `790`
- `formwork_installation_work_unit_price`: `0`
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
- `rebar_items`: `[{'code': 'rebar_a500_d16', 'name': 'Арматура класса А500 диаметром 16 мм', 'steel_class': 'A500', 'diameter_mm': 16, 'kg_per_meter': 1.58, 'rod_length_m': 11.7, 'unit_price_per_m': 80.58, 'weight_parts_kg': [328], 'source_length_m': None, 'length_parts_m': []}, {'code': 'rebar_a500_d12', 'name': 'Арматура класса А500 диаметром 12 мм', 'steel_class': 'A500', 'diameter_mm': 12, 'kg_per_meter': 0.888, 'rod_length_m': 11.7, 'unit_price_per_m': 45.29, 'weight_parts_kg': [122, 5276], 'source_length_m': None, 'length_parts_m': []}, {'code': 'rebar_a500_d10', 'name': 'Арматура класса А500 диаметром 10 мм', 'steel_class': 'A500', 'diameter_mm': 10, 'kg_per_meter': 0.617, 'rod_length_m': 11.7, 'unit_price_per_m': 32.72, 'weight_parts_kg': [1078], 'source_length_m': None, 'length_parts_m': []}, {'code': 'rebar_a240_d6', 'name': 'Арматура класса А240 диаметром 6 мм', 'steel_class': 'A240', 'diameter_mm': 6, 'kg_per_meter': 0.222, 'rod_length_m': 6, 'unit_price_per_m': 13.32, 'weight_parts_kg': [35], 'source_length_m': None, 'length_parts_m': []}]`
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
- `plywood_calc_method`: `actual_area_with_waste`
- `plywood_sheet_width_m`: `1.52`
- `plywood_sheet_height_m`: `1.52`
- `plywood_waste_coeff`: `1.05`
- `box_metal_delivery_capacity_kg`: `10000`
- `rebar_calc_method`: `legacy_weight_to_length`
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
- `thermal_insert_items`: `[]`
- `slab_zones`: `[]`

## Формулы
- Монтаж мембраны: `quantity = membrane_area_m2`.
- Planter Standard: `rolls = ceil(membrane_area_m2 * overlap / roll_area)`.
- PLANTERBAND: `quantity = membrane_rolls * planterband_per_membrane_roll`.
- Опалубка: `formwork_area = slab_side_formwork_area_m2`.
- Фанера standard: `plywood_sheets = ceil(formwork_area * 1.05 / (1.52 * 1.52))`.
- Пиломатериал: `timber_volume = formwork_area * timber_thickness_m`.
- ЭППС 50 под плитой, работа: `area = eps50_under_slab_volume_m3 / eps50_thickness_m`.
- Работы термовставок 50 мм: `quantity = thermal_insert_50_length_m`.
- Работы термовставок 100 мм: `quantity = thermal_insert_100_length_m`.
- Материал термовставок 50 мм: `purchase_qty = round_up_to_multiple(spec_qty * thermal_insert_material_waste_coeff, thermal_insert_50_pack_multiple_qty)`.
- Материал термовставок 100 мм: `purchase_qty = round_up_to_multiple(spec_qty * thermal_insert_material_waste_coeff, thermal_insert_100_pack_multiple_qty)`.
- Арматура legacy: вес -> м.п. -> запас 5% -> прутки -> закупочные м.п. -> стоимость.
- Бетонирование: работа по проектному объёму, материал с запасом и округлением вверх.
- Итог раздела: `internal_section_total = internal_materials_total + internal_works_total`.

## Подтверждённые правила Елены
- PLANTERBAND = количество рулонов мембраны * 4.
- Пиломатериал = площадь опалубки * 0.05, без дополнительного запаса.
- Пеноплэкс = ЭППС.
- Доставка металла ориентируется на 10 тонн на машину по листу Коробка.
- Фанера в production-стандарте считается по листу 1.52 x 1.52 м.
- Запас на фанеру фундаментной плиты = 5%.
- Количество листов фанеры округляется вверх до целого.
- plywood_calc_method, размер листа и запас являются системными настройками, а не ручными полями Елены.
- В новом стандарте площадь опалубки бортов фундаментной плиты берётся из спецификации.
- Периметр и высота борта не являются обязательными входами для расчёта опалубки в production-стандарте.
- Фанера, пиломатериал, монтаж и демонтаж опалубки считаются от готовой площади опалубки.
- Термовставки считаются отдельно по 50 мм и 100 мм.
- Работы по термовставкам считаются по длине в м.п. из спецификации.
- Материал термовставок берётся из спецификации, умножается на 1.05 и округляется до кратности пачки.
- Старая логика через элемент, шаг 600 мм и термовкладыш 150 мм не используется в новом стандарте.
- Legacy-арматура: вес из спецификации переводится в м.п. через kg_per_meter, затем запас, хлысты и стоимость по м.п.

## Промежуточные расчёты
| Показатель | Значение |
| --- | ---: |
| `confirmed_rules` | `['PLANTERBAND = количество рулонов мембраны * 4.', 'Пиломатериал = площадь опалубки * 0.05, без дополнительного запаса.', 'Пеноплэкс = ЭППС.', 'Доставка металла ориентируется на 10 тонн на машину по листу Коробка.', 'Фанера в production-стандарте считается по листу 1.52 x 1.52 м.', 'Запас на фанеру фундаментной плиты = 5%.', 'Количество листов фанеры округляется вверх до целого.', 'plywood_calc_method, размер листа и запас являются системными настройками, а не ручными полями Елены.', 'В новом стандарте площадь опалубки бортов фундаментной плиты берётся из спецификации.', 'Периметр и высота борта не являются обязательными входами для расчёта опалубки в production-стандарте.', 'Фанера, пиломатериал, монтаж и демонтаж опалубки считаются от готовой площади опалубки.', 'Термовставки считаются отдельно по 50 мм и 100 мм.', 'Работы по термовставкам считаются по длине в м.п. из спецификации.', 'Материал термовставок берётся из спецификации, умножается на 1.05 и округляется до кратности пачки.', 'Старая логика через элемент, шаг 600 мм и термовкладыш 150 мм не используется в новом стандарте.', 'Legacy-арматура: вес из спецификации переводится в м.п. через kg_per_meter, затем запас, хлысты и стоимость по м.п.']` |
| `membrane.membrane_area_with_overlap_m2` | `352.0` |
| `membrane.membrane_raw_rolls` | `8.8` |
| `membrane.membrane_rolls` | `9` |
| `membrane.planterband_quantity` | `36` |
| `formwork.formwork_calc_method` | `spec_area` |
| `formwork.slab_side_formwork_area_m2` | `24.3` |
| `formwork.formwork_area_m2` | `24.3` |
| `formwork.plywood_calc_method` | `actual_area_with_waste` |
| `formwork.plywood_sheet_width_m` | `1.52` |
| `formwork.plywood_sheet_height_m` | `1.52` |
| `formwork.plywood_sheet_area_m2` | `2.3104` |
| `formwork.plywood_waste_coeff` | `1.05` |
| `formwork.plywood_raw_sheets` | `11.0435` |
| `formwork.plywood_sheets` | `12` |
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
| `thermal_insert.thermal_insert_combined_length_m` | `None` |
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
| `rebar.rebar_calc_method` | `legacy_weight_to_length` |
| `rebar.items.rebar_a500_d16.name` | `Арматура класса А500 диаметром 16 мм` |
| `rebar.items.rebar_a500_d16.steel_class` | `A500` |
| `rebar.items.rebar_a500_d16.diameter_mm` | `16` |
| `rebar.items.rebar_a500_d16.calculation_method` | `legacy_weight_to_length` |
| `rebar.items.rebar_a500_d16.total_weight_kg` | `328.0` |
| `rebar.items.rebar_a500_d16.raw_length_m` | `207.5949` |
| `rebar.items.rebar_a500_d16.source_length_m` | `207.5949` |
| `rebar.items.rebar_a500_d16.length_with_waste_m` | `217.9746` |
| `rebar.items.rebar_a500_d16.raw_rods` | `18.6303` |
| `rebar.items.rebar_a500_d16.rods` | `19` |
| `rebar.items.rebar_a500_d16.order_length_m` | `222.3` |
| `rebar.items.rebar_a500_d16.kg_per_meter` | `1.58` |
| `rebar.items.rebar_a500_d16.rod_length_m` | `11.7` |
| `rebar.items.rebar_a500_d16.unit_price_per_m` | `80.58` |
| `rebar.items.rebar_a500_d16.design_weight_kg` | `328.0` |
| `rebar.items.rebar_a500_d16.delivery_weight_kg` | `351.234` |
| `rebar.items.rebar_a500_d16.control_weight_kg` | `344.3999` |
| `rebar.items.rebar_a500_d16.weight_parts_kg` | `[328]` |
| `rebar.items.rebar_a500_d12.name` | `Арматура класса А500 диаметром 12 мм` |
| `rebar.items.rebar_a500_d12.steel_class` | `A500` |
| `rebar.items.rebar_a500_d12.diameter_mm` | `12` |
| `rebar.items.rebar_a500_d12.calculation_method` | `legacy_weight_to_length` |
| `rebar.items.rebar_a500_d12.total_weight_kg` | `5398.0` |
| `rebar.items.rebar_a500_d12.raw_length_m` | `6078.8288` |
| `rebar.items.rebar_a500_d12.source_length_m` | `6078.8288` |
| `rebar.items.rebar_a500_d12.length_with_waste_m` | `6382.7702` |
| `rebar.items.rebar_a500_d12.raw_rods` | `545.5359` |
| `rebar.items.rebar_a500_d12.rods` | `546` |
| `rebar.items.rebar_a500_d12.order_length_m` | `6388.2` |
| `rebar.items.rebar_a500_d12.kg_per_meter` | `0.888` |
| `rebar.items.rebar_a500_d12.rod_length_m` | `11.7` |
| `rebar.items.rebar_a500_d12.unit_price_per_m` | `45.29` |
| `rebar.items.rebar_a500_d12.design_weight_kg` | `5398.0` |
| `rebar.items.rebar_a500_d12.delivery_weight_kg` | `5672.7216` |
| `rebar.items.rebar_a500_d12.control_weight_kg` | `5667.8999` |
| `rebar.items.rebar_a500_d12.weight_parts_kg` | `[122, 5276]` |
| `rebar.items.rebar_a500_d10.name` | `Арматура класса А500 диаметром 10 мм` |
| `rebar.items.rebar_a500_d10.steel_class` | `A500` |
| `rebar.items.rebar_a500_d10.diameter_mm` | `10` |
| `rebar.items.rebar_a500_d10.calculation_method` | `legacy_weight_to_length` |
| `rebar.items.rebar_a500_d10.total_weight_kg` | `1078.0` |
| `rebar.items.rebar_a500_d10.raw_length_m` | `1747.1637` |
| `rebar.items.rebar_a500_d10.source_length_m` | `1747.1637` |
| `rebar.items.rebar_a500_d10.length_with_waste_m` | `1834.5219` |
| `rebar.items.rebar_a500_d10.raw_rods` | `156.7967` |
| `rebar.items.rebar_a500_d10.rods` | `157` |
| `rebar.items.rebar_a500_d10.order_length_m` | `1836.9` |
| `rebar.items.rebar_a500_d10.kg_per_meter` | `0.617` |
| `rebar.items.rebar_a500_d10.rod_length_m` | `11.7` |
| `rebar.items.rebar_a500_d10.unit_price_per_m` | `32.72` |
| `rebar.items.rebar_a500_d10.design_weight_kg` | `1078.0` |
| `rebar.items.rebar_a500_d10.delivery_weight_kg` | `1133.3673` |
| `rebar.items.rebar_a500_d10.control_weight_kg` | `1131.9` |
| `rebar.items.rebar_a500_d10.weight_parts_kg` | `[1078]` |
| `rebar.items.rebar_a240_d6.name` | `Арматура класса А240 диаметром 6 мм` |
| `rebar.items.rebar_a240_d6.steel_class` | `A240` |
| `rebar.items.rebar_a240_d6.diameter_mm` | `6` |
| `rebar.items.rebar_a240_d6.calculation_method` | `legacy_weight_to_length` |
| `rebar.items.rebar_a240_d6.total_weight_kg` | `35.0` |
| `rebar.items.rebar_a240_d6.raw_length_m` | `157.6577` |
| `rebar.items.rebar_a240_d6.source_length_m` | `157.6577` |
| `rebar.items.rebar_a240_d6.length_with_waste_m` | `165.5406` |
| `rebar.items.rebar_a240_d6.raw_rods` | `27.5901` |
| `rebar.items.rebar_a240_d6.rods` | `28` |
| `rebar.items.rebar_a240_d6.order_length_m` | `168.0` |
| `rebar.items.rebar_a240_d6.kg_per_meter` | `0.222` |
| `rebar.items.rebar_a240_d6.rod_length_m` | `6` |
| `rebar.items.rebar_a240_d6.unit_price_per_m` | `13.32` |
| `rebar.items.rebar_a240_d6.design_weight_kg` | `35.0` |
| `rebar.items.rebar_a240_d6.delivery_weight_kg` | `37.296` |
| `rebar.items.rebar_a240_d6.control_weight_kg` | `36.75` |
| `rebar.items.rebar_a240_d6.weight_parts_kg` | `[35]` |
| `rebar.rebar_frame_assembly_quantity_m` | `8615.4` |
| `rebar.foundation_slab_rebar_control_weight_kg` | `7180.9498` |
| `rebar.foundation_slab_rebar_design_weight_kg` | `6839.0` |
| `rebar.foundation_slab_rebar_delivery_weight_kg` | `7194.6189` |
| `rebar.concrete_project_volume_m3` | `81` |
| `rebar.reinforcement_density_design_kg_per_m3` | `84.4321` |
| `rebar.reinforcement_density_delivery_kg_per_m3` | `88.8225` |
| `rebar.box_total_metal_weight_kg` | `8263` |
| `rebar.box_metal_delivery_capacity_kg` | `10000` |
| `rebar.suggested_foundation_rebar_delivery_trucks` | `1` |
| `rebar.suggested_box_metal_delivery_trucks` | `1` |
| `rebar.actual_rebar_metal_delivery_trucks` | `1` |
| `rebar.warnings` | `[]` |
| `concrete.concrete_raw_order_volume_m3` | `85.05` |
| `concrete.concrete_order_volume_m3` | `85.5` |
| `concrete.concrete_delivery_raw_trips` | `9.5` |
| `concrete.concrete_delivery_trips` | `10` |
| `concrete.reinforcement_density_kg_per_m3` | `88.6537` |
| `concrete.reinforcement_density_kg_per_m3_rounded` | `89` |
| `concrete.reinforcement_density_design_kg_per_m3` | `84.4321` |
| `concrete.reinforcement_density_delivery_kg_per_m3` | `88.8225` |
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
| `slab_zones.used` | `False` |
| `slab_zones.zone_count` | `0` |
| `slab_zones.concrete_project_volume_m3` | `81` |

## Контроль армирования
| Показатель | Значение |
| --- | ---: |
| `Метод расчёта арматуры` | `legacy_weight_to_length` |
| `Вес арматуры по спецификации, кг` | `6839.0` |
| `Вес арматуры с запасом/закупкой, кг` | `7194.6189` |
| `Объём бетона фундаментной плиты, м3` | `81` |
| `Плотность по спецификации, кг/м3` | `84.4321` |
| `Плотность с запасом/закупкой, кг/м3` | `88.8225` |
| `Legacy/control плотность, кг/м3` | `88.6537` |

Контрольная плотность армирования нужна для проверки разделов с большим объёмом армирования.

## Предупреждения
Предупреждений нет.

## Строки серой внутренней сметы
| code | name | line_type | quantity | display_quantity | unit | material_unit_price | material_total | work_unit_price | work_total | line_total |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `planter_membrane_installation` | Монтаж мембраны PLANTER стандарт | `` | `320.0` | `` | `м2` | `0.0` | `0` | `100` | `32000` | `32000` |
| `planter_standard_material` | Planter Standard Технониколь | `` | `9.0` | `` | `рул` | `5166` | `46494` | `0.0` | `0` | `46494` |
| `planterband_material` | PLANTERBAND 10м х 10см | `` | `36.0` | `` | `шт` | `790` | `28440` | `0.0` | `0` | `28440` |
| `formwork_installation` | Монтаж опалубки из пиломатериалов для отбортовки плиты | `` | `24.3` | `` | `м2` | `0.0` | `0` | `0` | `0` | `0` |
| `formwork_plywood` | Фанера ФК 1,52 * 1,52 толщиной 18 мм | `` | `12.0` | `` | `шт` | `1450` | `17400` | `0.0` | `0` | `17400` |
| `formwork_timber` | Пиломатериал обрезной хвойных пород ГОСТ | `` | `1.215` | `1.22` | `м3` | `21500` | `26123` | `0.0` | `0` | `26123` |
| `eps50_laying_under_slab` | Укладка ЭППС 50мм под плитой | `` | `270.0` | `` | `м2` | `0.0` | `0` | `250` | `67500` | `67500` |
| `thermal_insert_50_installation` | Устройство и монтаж термовставок 50 мм | `` | `10.0` | `` | `мп` | `0.0` | `0` | `100` | `1000` | `1000` |
| `thermal_insert_100_installation` | Устройство и монтаж термовставок 100 мм | `` | `15.0` | `` | `мп` | `0.0` | `0` | `100` | `1500` | `1500` |
| `eps50_penoplex_geo_material` | Пеноплэкс ГЕО 50 мм под плитой | `` | `14.4352` | `14.44` | `м3` | `9800` | `141465` | `0.0` | `0` | `141465` |
| `thermal_insert_50_material` | Материал термовставок 50 мм | `` | `1.1104` | `1.11` | `м3` | `9800` | `10882` | `0.0` | `0` | `10882` |
| `thermal_insert_100_material` | Материал термовставок 100 мм | `` | `0.5552` | `0.56` | `м3` | `10000` | `5552` | `0.0` | `0` | `5552` |
| `rebar_crane_supply` | Подача арматуры автокраном | `` | `1.0` | `` | `смена` | `30000` | `30000` | `0.0` | `0` | `30000` |
| `rebar_frame_assembly` | Изготовление и монтаж каркаса армирования фундаментной плиты из арматуры | `` | `8615.4` | `` | `мп` | `0.0` | `0` | `0.0` | `0` | `0` |
| `rebar_a500_d16` | Арматура класса А500 диаметром 16 мм | `` | `222.3` | `` | `мп` | `80.58` | `17913` | `0.0` | `0` | `17913` |
| `rebar_a500_d12` | Арматура класса А500 диаметром 12 мм | `` | `6388.2` | `` | `мп` | `45.29` | `289322` | `0.0` | `0` | `289322` |
| `rebar_a500_d10` | Арматура класса А500 диаметром 10 мм | `` | `1836.9` | `` | `мп` | `32.72` | `60103` | `0.0` | `0` | `60103` |
| `rebar_a240_d6` | Арматура класса А240 диаметром 6 мм | `` | `168.0` | `` | `мп` | `13.32` | `2238` | `0.0` | `0` | `2238` |
| `rebar_metal_delivery` | Доставка арматуры, металла | `` | `1.0` | `` | `маш` | `22000` | `22000` | `0.0` | `0` | `22000` |
| `foundation_slab_concreting_work` | Бетонирование фундаментной плиты в опалубке бетоном В22,5 (М300) | `` | `81.0` | `` | `м3` | `0.0` | `0` | `12000` | `972000` | `972000` |
| `concrete_b22_5_m300_material` | Бетон марки В22,5 (М300) | `` | `85.5` | `` | `м3` | `6400` | `547200` | `0.0` | `0` | `547200` |
| `concrete_delivery` | Доставка бетона до объекта | `` | `10.0` | `` | `рейс` | `7500` | `75000` | `0.0` | `0` | `75000` |
| `concrete_pump_32m` | Работа бетононасоса 32м + гаситель | `` | `1.0` | `` | `смена` | `38000` | `38000` | `0.0` | `0` | `38000` |
| `formwork_dismantling` | Демонтаж опалубки после завершения бетонирования | `` | `24.3` | `` | `м2` | `0.0` | `0` | `0` | `0` | `0` |
| `logistics_and_supply` | Логистика и снабжение | `` | `1.0` | `` | `-` | `36291.7` | `36292` | `0.0` | `0` | `36292` |
| `consumables_tool_amortization` | Расходные материалы, амортизация инструмента | `` | `1.0` | `` | `комплект` | `72583` | `72583` | `0.0` | `0` | `72583` |
| `technical_supervision` | Технический надзор | `` | `1.0` | `` | `-` | `0.0` | `0` | `10000` | `10000` | `10000` |
| `procurement_warehouse_costs_excel_structure` | Заготовительно-складские расходы | `zero_excel_structure_line` | `1.0` | `` | `-` | `0.0` | `0` | `0.0` | `0` | `0` |
| `overhead_general_business_costs_excel_structure` | Накладные и общехозяйственные расходы | `zero_excel_structure_line` | `1.0` | `` | `-` | `0.0` | `0` | `0.0` | `0` | `0` |
| `estimated_profit_excel_structure` | Сметная прибыль | `zero_excel_structure_line` | `1.0` | `` | `-` | `0.0` | `0` | `0.0` | `0` | `0` |

## Итоги серой внутренней сметы
| Показатель | Значение |
| --- | ---: |
| `internal_materials_total` | `1467007` |
| `internal_works_total` | `1084000` |
| `internal_section_total` | `2551007` |

## Проверка с расчётом Елены
| Показатель | Ожидание | Получено | Разница | Статус |
| --- | ---: | ---: | ---: | --- |
| `calculation_blocks.formwork.formwork_calc_method` | `spec_area` | `spec_area` | `` | `ok` |
| `calculation_blocks.formwork.slab_side_formwork_area_m2` | `24.3` | `24.3` | `0.0` | `ok` |
| `calculation_blocks.formwork.formwork_area_m2` | `24.3` | `24.3` | `0.0` | `ok` |
| `calculation_blocks.formwork.plywood_calc_method` | `actual_area_with_waste` | `actual_area_with_waste` | `` | `ok` |
| `calculation_blocks.formwork.plywood_sheet_width_m` | `1.52` | `1.52` | `0.0` | `ok` |
| `calculation_blocks.formwork.plywood_sheet_height_m` | `1.52` | `1.52` | `0.0` | `ok` |
| `calculation_blocks.formwork.plywood_sheet_area_m2` | `2.3104` | `2.3104` | `0.0` | `ok` |
| `calculation_blocks.formwork.plywood_waste_coeff` | `1.05` | `1.05` | `0.0` | `ok` |
| `calculation_blocks.formwork.plywood_raw_sheets` | `11.0435` | `11.0435` | `0.0` | `ok` |
| `calculation_blocks.formwork.plywood_sheets` | `12` | `12` | `0` | `ok` |
| `calculation_blocks.formwork.timber_raw_volume_m3` | `1.215` | `1.215` | `0.0` | `ok` |
| `estimate_lines.formwork_plywood.unit` | `шт` | `шт` | `` | `ok` |
| `estimate_lines.formwork_plywood.quantity` | `12` | `12.0` | `0.0` | `ok` |
| `estimate_lines.formwork_plywood.material_total` | `17400` | `17400` | `0` | `ok` |
| `estimate_lines.formwork_plywood.line_total` | `17400` | `17400` | `0` | `ok` |
| `internal_totals.internal_materials_total` | `1467007` | `1467007` | `0` | `ok` |
| `internal_totals.internal_works_total` | `1084000` | `1084000` | `0` | `ok` |
| `internal_totals.internal_section_total` | `2551007` | `2551007` | `0` | `ok` |
