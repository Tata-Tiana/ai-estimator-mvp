# Price registry mapping report v3

## Summary
- Source workbook: `output/price_registry_filled_v2.xlsx`
- Output workbook: `output/price_registry_filled_v3.xlsx`
- Registry rows: 131
- Required unique price_code from calculators: 81
- price_code filled after v3 manual mapping: 18
- Rows still empty in price_registry sheet: 113
- Manual obvious mappings applied: 15
- Manual mappings skipped because code is not required/already different: 1
- Rows to add: 63
- Rows to add with status needs_review: 59
- Rows to add with status requires_decision: 4
- Price differences on manually mapped rows: 14

## Manual Mappings Applied
| row | price_code | price_registry name | calculator line |
|---:|---|---|---|
| 95 | `schiedel_vent_channel_2x_36_25_item` | Вентиляционный канал двухходовой VENT 25/36, 0.33 пм | Вентиляционный канал 2х,36/25 см Schiedel |
| 96 | `schiedel_vent_channel_3x_52_25_item` | Вентиляционный канал трехходовой VENT 25/52, 0.33 пм | Вентиляционный канал 3х,52/25 см Schiedel |
| 100 | `rebar_a500_d25_m` | Арматура класса А500 диаметром 25 мм | Арматура класса А500 диаметром 25 мм |
| 102 | `rebar_a500_d16_m` | Арматура класса А500 диаметром 16 мм | Арматура класса А500 диаметром 16 мм |
| 103 | `rebar_a500_d12_m` | Арматура класса А500 диаметром 12мм | Арматура класса А500 диаметром 12 мм |
| 104 | `rebar_a500_d10_m` | Арматура класса А500 диаметром 10 мм | Арматура класса А500 диаметром 10 мм |
| 105 | `rebar_a240_d8_m` | Арматура класса А240 диаметром 8 мм | Арматура класса А240 диаметром 8 мм |
| 106 | `rebar_a240_d6_m` | Арматура класса А240 диаметром 6 мм | Арматура класса А240 диаметром 6 мм |
| 108 | `planter_standard_roll` | Planter Standard Технониколь 40м2-1рул | Planter Standard Технониколь |
| 109 | `planterband_item` | PLANTERBAND 10м х 10см-1шт | PLANTERBAND 10м х 10см |
| 112 | `eps_geo_50_m3` | Пеноплэкс ГЕО 50 мм-1м3 | Пеноплэкс ГЕО 50 мм |
| 113 | `eps_geo_100_m3` | Пеноплэкс ГЕО 100 мм-1м3 | Пеноплэкс ГЕО 100 мм |
| 114 | `eps_foam_glue_can` | Клей-пена для ЭППС-1шт | Клей-пена для ЭППС |
| 115 | `geotextile_dornit_300_m2` | Геотекстиль Дорнит 300 г.м2 (100м2) -1шт | Геотекстиль Дорнит 300 г.м2 (100м2) |
| 130 | `roof_pvc_aerator_75x375_item` | Аэратор кровельный PVC, А75х375 | Аэратор кровельный PVC, 75х375 (без пробивки отверстий) |

## Manual Mappings Skipped
| row | requested price_code | name | reason |
|---:|---|---|---|
| 101 | `rebar_a500_d20_m` | Арматура класса А500 диаметром 20мм | code_not_required |

## Requires Decision
| price_code | line | unit | current calculator price | reason |
|---|---|---|---:|---|
| `concrete_b22_5_m3` | Бетон марки В22,5 (М300) | м3 | 6400.000000 | В прайсе бетон разбит по зонам, в калькуляторах пока общий код. |
| `concrete_delivery_trip` | Доставка бетона до объекта | рейс | 7500.000000 | В прайсе доставка бетона по м3/зонам, в калькуляторах часть строк по рейсам. |
| `roof_geotextile_technonikol_prof_300_m2` | Геотекстиль ТЕХНОНИКОЛЬ ПРОФ Кровля 300, 2х50м | м2 | 111.76 | В прайсе найден близкий геотекстиль 150; для 300 нужна отдельная строка/решение. |
| `roof_pvc_membrane_logicroof_vrp_1_5mm_gray_roll` | Полимерная мембрана ПВХ Logicroof V-RP 1,5 мм мембрана серая, 2,10х20 | рул | 51431 | В калькуляторе закупка рулонами, в прайсе строка в м2. |

## Price Differences On Filled Rows
| price_code | registry name | registry price | calculator price |
|---|---|---:|---:|
| `schiedel_vent_channel_2x_36_25_item` | Вентиляционный канал двухходовой VENT 25/36, 0.33 пм | 512.4 | 504 |
| `schiedel_vent_channel_3x_52_25_item` | Вентиляционный канал трехходовой VENT 25/52, 0.33 пм | 732 | 720 |
| `rebar_a500_d25_m` | Арматура класса А500 диаметром 25 мм | 155.8 | 196.350000 |
| `rebar_a500_d16_m` | Арматура класса А500 диаметром 16 мм | 64.9 | 80.580000 |
| `rebar_a500_d12_m` | Арматура класса А500 диаметром 12мм | 36.85 | 45.290000 |
| `rebar_a500_d10_m` | Арматура класса А500 диаметром 10 мм | 27.16 | 32.720000 |
| `rebar_a240_d8_m` | Арматура класса А240 диаметром 8 мм | 18.5 | 24.000000 |
| `rebar_a240_d6_m` | Арматура класса А240 диаметром 6 мм | 10.25 | 13.320000 |
| `planter_standard_roll` | Planter Standard Технониколь 40м2-1рул | 4738 | 5166 |
| `planterband_item` | PLANTERBAND 10м х 10см-1шт | 750 | 790 |
| `eps_geo_50_m3` | Пеноплэкс ГЕО 50 мм-1м3 | 8800 | 9800 |
| `eps_geo_100_m3` | Пеноплэкс ГЕО 100 мм-1м3 | 8900 | 10000 |
| `eps_foam_glue_can` | Клей-пена для ЭППС-1шт | 450 | 490.000000 |
| `geotextile_dornit_300_m2` | Геотекстиль Дорнит 300 г.м2 (100м2) -1шт | 4562 | 109 |

## Rows To Add
All 63 rows are included in the workbook sheet `rows_to_add`.
| price_code | section | line | unit | price | status |
|---|---|---|---|---:|---|
| `axis_marking_shift` | Земляные работы | Вынос осей фундамента, котлована на участок | смена | 15000 | needs_review |
| `beam_concrete_placing_work_m3` | Ж/Б монолитная плита перекрытия 1-го этажа | Бетонирование балки бетоном марки В22,5 (М300) | м3 | 20000.000000 | needs_review |
| `bitumen_waterproofing_work_m2` | Гидроизоляция фундаментной плиты | Гидроизоляция фундаментной плиты битумной мастикой в 2 слоя | м2 | 350 | needs_review |
| `block_adhesive_bag` | Несущие стены и перемычки | Монтажный клей для блоков 25 кг | мешок | 340 | needs_review |
| `block_delivery_truck` | Несущие стены и перемычки | Доставка блоков, смеси | маш | 28000 | needs_review |
| `block_unloading_manipulator_truck` | Несущие стены и перемычки | Разгрузка блоков, смеси манипулятором | маш | 15000 | needs_review |
| `communications_installation_m` | Земляные работы | Закладка технологических входов коммуникаций до границы дома | мп | 350 | needs_review |
| `communications_material_m` | Земляные работы | Материалы для устройства входов коммуникаций | мп | 650 | needs_review |
| `concrete_b22_5_m3` | Ж/Б монолитная плита перекрытия 1-го этажа | Бетон марки В22,5 (М300) | м3 | 6400.000000 | requires_decision |
| `concrete_delivery_trip` | Ж/Б монолитная плита перекрытия 1-го этажа | Доставка бетона до объекта | рейс | 7500.000000 | requires_decision |
| `concrete_placing_work_m3` | Ж/Б монолитная плита перекрытия 1-го этажа | Бетонирование монолитной плиты перекрытия бетоном марки В22,5 (М300) | м3 | 12000.000000 | needs_review |
| `concrete_pump_32m_shift` | Ж/Б монолитная плита перекрытия 1-го этажа | Работа бетононасоса 32м + гаситель | смена | 38000.000000 | needs_review |
| `crane_shift` | Ж/Б монолитная плита перекрытия 1-го этажа | Подача опалубки, арматуры автокраном | смена | 30000.000000 | needs_review |
| `cutoff_waterproofing_under_blocks_m2` | Несущие стены и перемычки | Гидроизоляция поверхности под первый ряд блоков | м2 | 250 | needs_review |
| `edge_insulation_work_m` | Ж/Б монолитная плита перекрытия 1-го этажа | Устройство утепления по наружной стороне торцов плиты, балок | мп | 450.000000 | needs_review |
| `eps_bottom_slab_insulation_work_m2` | Ж/Б монолитная плита перекрытия 1-го этажа | Устройство утепления низа плиты | м2 | 900.000000 | needs_review |
| `eps_laying_work_m2` | Устройство фундаментной плиты | Укладка ЭППС 50мм под плитой | м2 | 250 | needs_review |
| `eps_penoplex_osnova_100_m3` | Ж/Б монолитная плита перекрытия 1-го этажа | Экструдированный пенополистирол Пеноплэкс Основа 100х585х1185 мм | м3 | 9020.000000 | needs_review |
| `eps_wall_insulation_work_m2` | Гидроизоляция фундаментной плиты | Утепление стен плиты ЭППС 100 мм | м2 | 500 | needs_review |
| `excavator_jcb_shift` | Земляные работы | Механизированная разработка грунта, Экскаватор JCB | смена | 22000 | needs_review |
| `formwork_consumables_m2` | Ж/Б монолитная плита перекрытия 1-го этажа | Расходные материалы для установки опалубки (смазка; звездочки ПВХ, трубки) | - | 9759.080000 | needs_review |
| `formwork_delivery_truck` | Ж/Б монолитная плита перекрытия 1-го этажа | Доставка, вывоз опалубки манипулятором | маш | 20000.000000 | needs_review |
| `formwork_dismantling_work_m2` | Устройство фундаментной плиты | Демонтаж опалубки после завершения бетонирования | м2 |  | needs_review |
| `formwork_rental_m2` | Ж/Б монолитная плита перекрытия 1-го этажа | Комплект опалубки (телескопические стойки, унивилки, треноги, водостойкая фанера, поперечные и продольные балки двутавровые) | м2 | 600.000000 | needs_review |
| `gas_block_cladding_work_m2` | Несущие стены и перемычки | Обкладка дымохода и вентканалов 150 мм | м2 | 1200 | needs_review |
| `gas_block_d400_m3` | Несущие стены и перемычки | Газобетонный блок D400 600x400x250 мм | м3 | 6000 | needs_review |
| `gas_block_d500_150_m3` | Несущие стены и перемычки | Газобетонный блок D500 600x150x250 мм | м3 | 5600 | needs_review |
| `gas_block_d500_m3` | Несущие стены и перемычки | Газобетонный блок D500 600x250x250 мм | м3 | 5500 | needs_review |
| `gas_block_masonry_work_m3` | Несущие стены и перемычки | Кладка внешних, внутренних стен из газобетонных блоков | м3 | 7000 | needs_review |
| `geotextile_laying_m2` | Земляные работы | Укладка геотекстиля | м2 | 35 | needs_review |
| `lintel_concreting_work_m` | Несущие стены и перемычки | Бетонирование перемычек | мп | 1000 | needs_review |
| `manual_concrete_lifting_m3` | Несущие стены и перемычки | Перенос, подъём бетона вручную | м3 | 5000 | needs_review |
| `manual_excavation_m3` | Земляные работы | Доработка грунта вручную | м3 | 1200 | needs_review |
| `metal_delivery_truck` | Ж/Б монолитная плита перекрытия 1-го этажа | Доставка арматуры, металла | маш | 22000.000000 | needs_review |
| `planter_membrane_installation_work_m2` | Устройство фундаментной плиты | Монтаж мембраны PLANTER стандарт | м2 | 100 | needs_review |
| `plywood_1520x1520_18mm_sheet` | Ж/Б монолитная плита перекрытия 1-го этажа | Фанера ФК 1,52 * 1,52 толщиной 18 мм для закрытия некратных мест и торцов | шт | 1450.000000 | needs_review |
| `roof_aluminum_edge_rail_m` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Рейка краевая алюминиевая 3м | мп | 98 | needs_review |
| `roof_aluminum_pressure_rail_m` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Рейка прижимная алюминиевая 3м | мп | 95 | needs_review |
| `roof_crane_lifting_shift` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Подъем материалов автокраном | смена | 30000 | needs_review |
| `roof_eps100_technonikol_carbon_eco_m3` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON ECO (100мм) | м3 | 7326.7 | needs_review |
| `roof_eps50_technonikol_carbon_eco_m3` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON ECO (50мм) | м3 | 6906.7 | needs_review |
| `roof_eps_slope_2_1_plate_a_m3` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты A) | м3 | 10896 | needs_review |
| `roof_eps_slope_2_1_plate_b_m3` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 2,1% (плиты B) | м3 | 10896 | needs_review |
| `roof_eps_slope_4_2_plate_j_m3` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты J) | м3 | 10896 | needs_review |
| `roof_eps_slope_4_2_plate_k_m3` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Утеплитель ЭППС ТЕХНОНИКОЛЬ CARBON PROF SLOPE уклон 4,2% (плиты K) | м3 | 10896 | needs_review |
| `roof_geotextile_technonikol_prof_150_m2` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Геотекстиль ТЕХНОНИКОЛЬ ПРОФ Кровля 150, 2х50м | м2 | 64.34 | needs_review |
| `roof_geotextile_technonikol_prof_300_m2` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Геотекстиль ТЕХНОНИКОЛЬ ПРОФ Кровля 300, 2х50м | м2 | 111.76 | requires_decision |
| `roof_internal_drain_pvc_110mm_m` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Устройство внутреннего водостока (ПВХ Ф110мм) (ориентировочно) | мп | 2500 | needs_review |
| `roof_internal_drain_with_heating_item` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Установка воронки кровельной (с обжимным мет. фланцем с обогревом 110х450мм) (без пробивки отверстий) | шт | 5000 | needs_review |
| `roof_parapet_drain_item` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Установка воронки парапетной (без пробивки отверстий) | шт | 5000 | needs_review |
| `roof_pvc_membrane_logicroof_vrp_1_5mm_gray_roll` | КРОВЕЛЬНОЕ ПОКРЫТИЕ ДОМА | Полимерная мембрана ПВХ Logicroof V-RP 1,5 мм мембрана серая, 2,10х20 | рул | 51431 | requires_decision |
| `sand_concrete_bag` | Несущие стены и перемычки | Пескобетон М300 40 кг | шт | 375 | needs_review |
| `sand_filling_work_m3` | Земляные работы | Отсыпка дна котлована, засыпка под плитой песком с трамбованием | м3 | 1200 | needs_review |
| `sand_m3` | Земляные работы | Песок строительный | м3 | 1000 | needs_review |
| `sand_manual_moving_m3` | Земляные работы | Перемещение песка вручную | м3 |  | needs_review |
| `scaffolding_setup_dismantling_work_set` | Несущие стены и перемычки | Устройство лесов, подмостей для кладки, демонтаж лесов | компл | 20000 | needs_review |
| `schiedel_delivery_truck` | ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel | Доставка вентканалов | маш | 15000 | needs_review |
| `technical_supervision_fixed` | Ж/Б монолитная плита перекрытия 1-го этажа | Технический надзор | - | 5000.000000 | needs_review |
| `thermal_insert_installation_work_m` | Устройство фундаментной плиты | Устройство и монтаж термовкладыша 150*400*250мм шаг 200мм | мп | 100 | needs_review |
| `timber_formwork_installation_work_m2` | Устройство фундаментной плиты | Монтаж опалубки из пиломатериалов для отбортовки плиты | м2 |  | needs_review |
| `timber_m3` | Ж/Б монолитная плита перекрытия 1-го этажа | Пиломатериал обрезной для устройства опалубки ГОСТ | м3 | 21499.997319 | needs_review |
| `u_block_lintel_cutting_item` | Несущие стены и перемычки | Резка блока под перемычку (U-блок) | шт | 400 | needs_review |
| `waste_removal_truck` | Несущие стены и перемычки | Вывоз мусора с объекта | маш | 10000 | needs_review |
