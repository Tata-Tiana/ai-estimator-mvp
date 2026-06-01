# Расчёт гидроизоляции фундаментной плиты: test_waterproofing_foundation_slab_live_prices

Проект: `test_waterproofing_foundation_slab_live_prices`

## Входные параметры
- `project_name`: `test_waterproofing_foundation_slab_live_prices`
- `slab_formwork_perimeter_m`: `81`
- `slab_edge_height_m`: `0.3`
- `waterproofing_work_unit_price`: `350`
- `primer_consumption_l_per_m2`: `0.3`
- `primer_canister_volume_l`: `18`
- `primer_unit_price`: `2770`
- `mastic_consumption_kg_per_m2_per_layer`: `1`
- `mastic_layers`: `2`
- `mastic_bucket_weight_kg`: `18`
- `mastic_unit_price`: `2780`
- `eps100_wall_volume_m3`: `1.75`
- `eps100_wall_thickness_m`: `0.1`
- `eps100_wall_insulation_work_unit_price`: `500`
- `non_insulated_edge_lengths_m`: `[8.2, 2, 5.3]`
- `eps_waste_coeff`: `1.05`
- `eps100_pack_volume_m3`: `0.2776`
- `eps100_unit_price`: `10000`
- `glue_foam_coverage_m2_per_can`: `10`
- `glue_foam_min_units`: `1`
- `glue_foam_unit_price`: `490`
- `waterproofing_logistics_coeff`: `0.02`
- `waterproofing_consumables_coeff`: `0.03`
- `pricing`: `{'mode': 'price_registry_with_fallback', 'registry_path': 'output/price_registry_filled_v3.xlsx'}`

## Расчётные блоки
| Показатель | Значение |
| --- | ---: |
| `waterproofing_area_m2` | `24.3` |
| `primer_required_liters` | `7.29` |
| `primer_raw_units` | `0.405` |
| `primer_units` | `1` |
| `mastic_required_kg` | `48.6` |
| `mastic_raw_units` | `2.7` |
| `mastic_units` | `3` |
| `eps100_wall_insulation_area_m2` | `17.5` |
| `non_insulated_edge_lengths_total_m` | `15.5` |
| `insulated_edge_length_m` | `65.5` |
| `eps100_wall_geometry_check_area_m2` | `19.65` |
| `eps100_wall_required_volume_m3` | `1.8375` |
| `eps100_wall_raw_packs` | `6.6192` |
| `eps100_wall_packs` | `7` |
| `eps100_wall_order_volume_m3` | `1.9432` |
| `glue_foam_raw_units` | `1.75` |
| `glue_foam_units` | `2` |
| `waterproofing_base_subtotal` | `46799` |
| `logistics_amount_raw` | `935.98` |
| `consumables_amount_raw` | `1403.97` |

## Строки серой внутренней сметы
| code | name | quantity | display_quantity | unit | material_unit_price | material_total | work_unit_price | work_total | line_total |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `waterproofing_bitumen_mastic_work` | Гидроизоляция фундаментной плиты битумной мастикой в 2 слоя | `24.3` | `` | `м2` | `0.0` | `0` | `350.0` | `8505` | `8505` |
| `bitumen_primer_aquamast_18l` | Праймер битумный AquaMast, 18 л | `1.0` | `` | `шт` | `2865.0` | `2865` | `0.0` | `0` | `2865` |
| `bitumen_mastic_aquamast_18kg` | Мастика гидроизоляционная битумная для фундаментов AquaMast, 18 кг | `3.0` | `` | `шт` | `2828.21` | `8485` | `0.0` | `0` | `8485` |
| `eps100_wall_insulation_work` | Утепление стен плиты ЭППС 100 мм | `17.5` | `` | `м2` | `0.0` | `0` | `500.0` | `8750` | `8750` |
| `eps100_wall_penoplex_geo_material` | Пеноплэкс ГЕО 100 мм | `1.9432` | `1.94` | `м3` | `8900.0` | `17294` | `0.0` | `0` | `17294` |
| `eps_glue_foam` | Клей-пена для ЭППС | `2.0` | `` | `баллон` | `450.0` | `900` | `0.0` | `0` | `900` |
| `waterproofing_logistics_and_supply` | Логистика и снабжение | `1.0` | `` | `-` | `935.98` | `936` | `0.0` | `0` | `936` |
| `waterproofing_consumables_tool_amortization` | Расходные материалы, амортизация инструмента | `1.0` | `` | `комплект` | `1403.97` | `1404` | `0.0` | `0` | `1404` |

## Итоги серой внутренней себестоимости
| Показатель | Значение |
| --- | ---: |
| `waterproofing_base_subtotal` | `46799` |
| `internal_materials_total` | `31884` |
| `internal_works_total` | `17255` |
| `internal_section_total` | `49139` |

## Источники цен
| Строка сметы | price_code | старая цена | использованная цена | источник | предупреждение |
| --- | --- | ---: | ---: | --- | --- |
| Гидроизоляция фундаментной плиты битумной мастикой в 2 слоя | `bitumen_waterproofing_work_m2` | `350` | `350` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Праймер битумный AquaMast, 18 л | `bitumen_primer_aquamast_18l_item` | `2770` | `2865` | `price_registry` |  |
| Мастика гидроизоляционная битумная для фундаментов AquaMast, 18 кг | `bitumen_mastic_aquamast_18kg_item` | `2780` | `2828.21` | `price_registry` |  |
| Утепление стен плиты ЭППС 100 мм | `eps_wall_insulation_work_m2` | `500` | `500` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Пеноплэкс ГЕО 100 мм | `eps_geo_100_m3` | `10000` | `8900` | `price_registry` |  |
| Клей-пена для ЭППС | `eps_foam_glue_can` | `490` | `450` | `price_registry` |  |
| Логистика и снабжение | `None` | `935.98` | `935.98` | `locked_case_prices` |  |
| Расходные материалы, амортизация инструмента | `None` | `1403.97` | `1403.97` | `locked_case_prices` |  |

## Pricing summary
| Показатель | Значение |
| --- | ---: |
| `mode` | `price_registry_with_fallback` |
| `registry_path` | `/Users/tatanamedzidova/Desktop/AI сметчик/ai_estimator_mvp/output/price_registry_filled_v3.xlsx` |
| `prices_from_price_registry` | `4` |
| `prices_from_project_overrides` | `0` |
| `prices_from_fallback_input` | `2` |
| `warnings_count` | `2` |

## Warnings
- bitumen_waterproofing_work_m2: price_code not found in price_registry, fallback input price used
- eps_wall_insulation_work_m2: price_code not found in price_registry, fallback input price used

## Comparison
Expected values are not provided for this case.
