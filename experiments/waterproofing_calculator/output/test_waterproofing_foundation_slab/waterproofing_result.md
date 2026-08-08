# Расчёт гидроизоляции фундаментной плиты: test_waterproofing_foundation_slab

Проект: `test_waterproofing_foundation_slab`

## Входные параметры
- `project_name`: `test_waterproofing_foundation_slab`
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
- `eps_waste_coeff`: `1.05`
- `eps100_pack_volume_m3`: `0.2776`
- `eps100_unit_price`: `10000`
- `eps50_wall_thickness_m`: `0.05`
- `eps50_wall_insulation_work_unit_price`: `500`
- `eps50_pack_volume_m3`: `0.6`
- `eps50_unit_price`: `8800`
- `glue_foam_coverage_m2_per_can`: `10`
- `glue_foam_min_units`: `1`
- `glue_foam_unit_price`: `490`
- `waterproofing_logistics_coeff`: `0.02`
- `waterproofing_consumables_coeff`: `0.03`
- `waterproofing_area_calc_method`: `legacy_perimeter_height`
- `slab_formwork_perimeter_m`: `81`
- `slab_edge_height_m`: `0.3`
- `non_insulated_edge_lengths_m`: `[8.2, 2, 5.3]`

## Формулы
- Площадь гидроизоляции legacy: `waterproofing_area_m2 = slab_formwork_perimeter_m * slab_edge_height_m`.
- Использованный метод площади: `legacy_perimeter_height`.
- Источник площади: `legacy_perimeter_height`.
- Площадь, которая ушла в работы, праймер и мастику: `24.3` м2.
- Праймер: `primer_required_liters = waterproofing_area_m2 * primer_consumption_l_per_m2`; `primer_units = ceil(primer_required_liters / primer_canister_volume_l)`.
- Мастика: `mastic_required_kg = waterproofing_area_m2 * mastic_consumption_kg_per_m2_per_layer * mastic_layers`; `mastic_units = ceil(mastic_required_kg / mastic_bucket_weight_kg)`.
- Основная площадь работ по ЭППС 100 мм торец/борт плиты: если в проекте есть явная площадь `eps100_wall_insulation_area_m2`, используется она; иначе fallback `eps100_wall_volume_m3 / eps100_wall_thickness_m`.
- Геометрическая проверка по участкам без утепления включается только если заданы `slab_formwork_perimeter_m`, `slab_edge_height_m` и `non_insulated_edge_lengths_m`.
- Если геометрическая проверка выключена, площадь ЭППС берётся из спецификации через `объём / толщину`.
- Геометрическая проверка включена: `True`.

## Расчётные блоки
| Показатель | Значение |
| --- | ---: |
| `waterproofing_area_calc_method` | `legacy_perimeter_height` |
| `waterproofing_area_source` | `legacy_perimeter_height` |
| `legacy_slab_formwork_perimeter_m` | `81` |
| `legacy_slab_edge_height_m` | `0.3` |
| `waterproofing_area_m2` | `24.3` |
| `primer_required_liters` | `7.29` |
| `primer_raw_units` | `0.405` |
| `primer_units` | `1` |
| `mastic_required_kg` | `48.6` |
| `mastic_raw_units` | `2.7` |
| `mastic_units` | `3` |
| `eps100_wall_insulation_area_m2` | `17.5` |
| `eps100_wall_insulation_area_source` | `volume_div_thickness` |
| `eps100_wall_geometry_check_enabled` | `True` |
| `non_insulated_edge_lengths_total_m` | `15.5` |
| `insulated_edge_length_m` | `65.5` |
| `eps100_wall_geometry_check_area_m2` | `19.65` |
| `eps100_wall_required_volume_m3` | `1.8375` |
| `eps100_wall_raw_packs` | `6.6192` |
| `eps100_wall_packs` | `7` |
| `eps100_wall_order_volume_m3` | `1.9432` |
| `eps50_wall_enabled` | `False` |
| `eps50_wall_insulation_area_m2` | `0.0` |
| `eps50_wall_required_volume_m3` | `0.0` |
| `eps50_wall_raw_packs` | `0.0` |
| `eps50_wall_packs` | `0` |
| `eps50_wall_order_volume_m3` | `0.0` |
| `combined_wall_insulation_area_m2` | `17.5` |
| `glue_foam_raw_units` | `1.75` |
| `glue_foam_units` | `2` |
| `waterproofing_base_subtotal` | `48777` |
| `logistics_amount_raw` | `975.54` |
| `consumables_amount_raw` | `1463.31` |

## Строки серой внутренней сметы
| code | name | quantity | display_quantity | unit | material_unit_price | material_total | work_unit_price | work_total | line_total |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `waterproofing_bitumen_mastic_work` | Гидроизоляция фундаментной плиты битумной мастикой в 2 слоя | `24.3` | `` | `м2` | `0.0` | `0` | `350` | `8505` | `8505` |
| `bitumen_primer_aquamast_18l` | Праймер битумный AquaMast, 18 л | `1.0` | `` | `шт` | `2770` | `2770` | `0.0` | `0` | `2770` |
| `bitumen_mastic_aquamast_18kg` | Мастика гидроизоляционная битумная для фундаментов AquaMast, 18 кг | `3.0` | `` | `шт` | `2780` | `8340` | `0.0` | `0` | `8340` |
| `eps100_wall_insulation_work` | Утепление торца/борта фундаментной плиты ЭППС 100 мм | `17.5` | `` | `м2` | `0.0` | `0` | `500` | `8750` | `8750` |
| `eps100_wall_penoplex_geo_material` | Пеноплэкс ГЕО 100 мм | `1.9432` | `1.94` | `м3` | `10000` | `19432` | `0.0` | `0` | `19432` |
| `eps_glue_foam` | Клей-пена для ЭППС | `2.0` | `` | `баллон` | `490` | `980` | `0.0` | `0` | `980` |
| `waterproofing_logistics_and_supply` | Логистика и снабжение | `1.0` | `` | `-` | `975.54` | `976` | `0.0` | `0` | `976` |
| `waterproofing_consumables_tool_amortization` | Расходные материалы, амортизация инструмента | `1.0` | `` | `комплект` | `1463.31` | `1463` | `0.0` | `0` | `1463` |

## Итоги серой внутренней себестоимости
| Показатель | Значение |
| --- | ---: |
| `waterproofing_base_subtotal` | `48777` |
| `internal_materials_total` | `33961` |
| `internal_works_total` | `17255` |
| `internal_section_total` | `51216` |

## Comparison
| Показатель | Ожидание | Получено | Разница | Статус |
| --- | ---: | ---: | ---: | --- |
| `calculation_blocks.waterproofing.waterproofing_area_m2` | `24.3` | `24.3` | `0.0` | `ok` |
| `calculation_blocks.waterproofing.primer_required_liters` | `7.29` | `7.29` | `0.0` | `ok` |
| `calculation_blocks.waterproofing.primer_raw_units` | `0.405` | `0.405` | `0.0` | `ok` |
| `calculation_blocks.waterproofing.primer_units` | `1` | `1` | `0` | `ok` |
| `calculation_blocks.waterproofing.mastic_required_kg` | `48.6` | `48.6` | `0.0` | `ok` |
| `calculation_blocks.waterproofing.mastic_raw_units` | `2.7` | `2.7` | `0.0` | `ok` |
| `calculation_blocks.waterproofing.mastic_units` | `3` | `3` | `0` | `ok` |
| `calculation_blocks.waterproofing.eps100_wall_insulation_area_m2` | `17.5` | `17.5` | `0.0` | `ok` |
| `calculation_blocks.waterproofing.eps100_wall_geometry_check_area_m2` | `19.65` | `19.65` | `0.0` | `ok` |
| `calculation_blocks.waterproofing.eps100_wall_required_volume_m3` | `1.8375` | `1.8375` | `0.0` | `ok` |
| `calculation_blocks.waterproofing.eps100_wall_packs` | `7` | `7` | `0` | `ok` |
| `calculation_blocks.waterproofing.eps100_wall_order_volume_m3` | `1.9432` | `1.9432` | `0.0` | `ok` |
| `calculation_blocks.waterproofing.glue_foam_raw_units` | `1.75` | `1.75` | `0.0` | `ok` |
| `calculation_blocks.waterproofing.glue_foam_units` | `2` | `2` | `0` | `ok` |
| `calculation_blocks.waterproofing.waterproofing_base_subtotal` | `48777` | `48777` | `0` | `ok` |
| `calculation_blocks.waterproofing.logistics_amount_raw` | `975.54` | `975.54` | `0.0` | `ok` |
| `calculation_blocks.waterproofing.consumables_amount_raw` | `1463.31` | `1463.31` | `0.0` | `ok` |
| `estimate_lines.waterproofing_bitumen_mastic_work.quantity` | `24.3` | `24.3` | `0.0` | `ok` |
| `estimate_lines.waterproofing_bitumen_mastic_work.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.waterproofing_bitumen_mastic_work.work_total` | `8505` | `8505` | `0` | `ok` |
| `estimate_lines.waterproofing_bitumen_mastic_work.line_total` | `8505` | `8505` | `0` | `ok` |
| `estimate_lines.bitumen_primer_aquamast_18l.quantity` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.bitumen_primer_aquamast_18l.material_total` | `2770` | `2770` | `0` | `ok` |
| `estimate_lines.bitumen_primer_aquamast_18l.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.bitumen_primer_aquamast_18l.line_total` | `2770` | `2770` | `0` | `ok` |
| `estimate_lines.bitumen_mastic_aquamast_18kg.quantity` | `3` | `3.0` | `0.0` | `ok` |
| `estimate_lines.bitumen_mastic_aquamast_18kg.material_total` | `8340` | `8340` | `0` | `ok` |
| `estimate_lines.bitumen_mastic_aquamast_18kg.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.bitumen_mastic_aquamast_18kg.line_total` | `8340` | `8340` | `0` | `ok` |
| `estimate_lines.eps100_wall_insulation_work.quantity` | `17.5` | `17.5` | `0.0` | `ok` |
| `estimate_lines.eps100_wall_insulation_work.material_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.eps100_wall_insulation_work.work_total` | `8750` | `8750` | `0` | `ok` |
| `estimate_lines.eps100_wall_insulation_work.line_total` | `8750` | `8750` | `0` | `ok` |
| `estimate_lines.eps100_wall_penoplex_geo_material.quantity` | `1.9432` | `1.9432` | `0.0` | `ok` |
| `estimate_lines.eps100_wall_penoplex_geo_material.display_quantity` | `1.94` | `1.94` | `0.0` | `ok` |
| `estimate_lines.eps100_wall_penoplex_geo_material.material_total` | `19432` | `19432` | `0` | `ok` |
| `estimate_lines.eps100_wall_penoplex_geo_material.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.eps100_wall_penoplex_geo_material.line_total` | `19432` | `19432` | `0` | `ok` |
| `estimate_lines.eps_glue_foam.quantity` | `2` | `2.0` | `0.0` | `ok` |
| `estimate_lines.eps_glue_foam.material_total` | `980` | `980` | `0` | `ok` |
| `estimate_lines.eps_glue_foam.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.eps_glue_foam.line_total` | `980` | `980` | `0` | `ok` |
| `estimate_lines.waterproofing_logistics_and_supply.quantity` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.waterproofing_logistics_and_supply.material_total` | `976` | `976` | `0` | `ok` |
| `estimate_lines.waterproofing_logistics_and_supply.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.waterproofing_logistics_and_supply.line_total` | `976` | `976` | `0` | `ok` |
| `estimate_lines.waterproofing_consumables_tool_amortization.quantity` | `1` | `1.0` | `0.0` | `ok` |
| `estimate_lines.waterproofing_consumables_tool_amortization.material_total` | `1463` | `1463` | `0` | `ok` |
| `estimate_lines.waterproofing_consumables_tool_amortization.work_total` | `0` | `0` | `0` | `ok` |
| `estimate_lines.waterproofing_consumables_tool_amortization.line_total` | `1463` | `1463` | `0` | `ok` |
| `internal_totals.waterproofing_base_subtotal` | `48777` | `48777` | `0` | `ok` |
| `internal_totals.internal_materials_total` | `33961` | `33961` | `0` | `ok` |
| `internal_totals.internal_works_total` | `17255` | `17255` | `0` | `ok` |
| `internal_totals.internal_section_total` | `51216` | `51216` | `0` | `ok` |
