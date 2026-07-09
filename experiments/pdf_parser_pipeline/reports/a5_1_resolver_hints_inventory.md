# A5.1 — Resolver hints inventory

Источник истины: `docs/elena_parameter_review_pack_audit.md` (170 параметров с точной привязкой parameter_code, из 4 категорий: AUTO_PROJECT/SUPPLIER_INPUT/DEPRECATED_LEGACY_ONLY/DEPRECATED_OPTIONAL_OVERRIDE — остальные 4 категории июньского аудита (AUTO_CALCULATED/DEFAULT_VALUE/MATERIAL_CATALOG/OPTIONAL_CONTROL, 114 строк) в исходном markdown даны только агрегированными счётчиками, без parameter_code).
Fallback: `experiments/parameter_audit/output/mvp_usv_demo/parameter_audit_result.xlsx` (287 строк, скриптовая эвристика от 3 июня, ДО человеческой проверки — помечается как `script_suggested:*`, не как решение).

## 3.1 Общая статистика по разделам

| section_code | total_params | has_hints | auto_project_total | auto_project_with_hints | auto_project_without_hints |
|---|---|---|---|---|---|
| earthworks | 39 | 7 | 4 | 1 | 3 |
| flat_roof | 83 | 5 | 10 | 0 | 10 |
| floor_slab_1 | 136 | 5 | 22 | 0 | 22 |
| floor_slab_2 | 71 | 5 | 9 | 0 | 9 |
| foundation_slab | 102 | 16 | 17 | 4 | 13 |
| load_bearing_walls_lintels | 155 | 5 | 10 | 0 | 10 |
| schiedel_vent_channels | 16 | 1 | 3 | 0 | 3 |
| waterproofing | 27 | 1 | 0 | 0 | 0 |

## 3.2 AUTO_PROJECT без resolver_hints

Priority — рабочая сортировка (P0: required + top-level; P1: required+nested или не required; P2: control_only), не истина.

| section_code | parameter_code | display_name | unit | priority |
|---|---|---|---|---|
| earthworks | earthworks_trench_volume_m3 | trench volume m3 | м3 | P0 |
| earthworks | earthworks_communications_length_m | communications length m | м | P0 |
| earthworks | earthworks_geotextile_laying_area_m2 | geotextile laying area m2 | м2 | P0 |
| flat_roof | flat_roof_roof_area_level_1_m2 | Площадь кровли уровня 1 | м2 | P0 |
| flat_roof | flat_roof_roof_area_level_2_m2 | Площадь кровли уровня 2 | м2 | P0 |
| flat_roof | flat_roof_parapet_length_level_1_m | parapet length level 1 m | м | P0 |
| flat_roof | flat_roof_parapet_length_level_2_m | parapet length level 2 m | м | P0 |
| flat_roof | flat_roof_vent_wall_abutment_level_1_m | vent wall abutment level 1 m | м | P0 |
| flat_roof | flat_roof_vent_wall_abutment_level_2_m | vent wall abutment level 2 m | м | P0 |
| flat_roof | flat_roof_vent_shaft_abutment_count | Количество примыканий к вентшахтам | шт | P0 |
| flat_roof | flat_roof_roof_aerators_count | Количество кровельных аэраторов | шт | P0 |
| flat_roof | flat_roof_gas_block_wall_holes_count | Количество отверстий в стенах из газоблока | шт | P0 |
| flat_roof | flat_roof_internal_drain_height_per_drain_m | Высота внутреннего водостока на одну воронку | м | P0 |
| floor_slab_1 | floor_slab_1_beams_items_0_length_m | Балка Б-1: длина | м | P1 |
| floor_slab_1 | floor_slab_1_beams_items_0_width_m | Балка Б-1: ширина | м | P1 |
| floor_slab_1 | floor_slab_1_beams_items_0_height_m | Балка Б-1: высота | м | P1 |
| floor_slab_1 | floor_slab_1_beams_items_1_length_m | Балка Б-2: длина | м | P1 |
| floor_slab_1 | floor_slab_1_beams_items_1_width_m | Балка Б-2: ширина | м | P1 |
| floor_slab_1 | floor_slab_1_beams_items_1_height_m | Балка Б-2: высота | м | P1 |
| floor_slab_1 | floor_slab_1_beams_items_2_length_m | Балка Б-3: длина | м | P1 |
| floor_slab_1 | floor_slab_1_beams_items_2_width_m | Балка Б-3: ширина | м | P1 |
| floor_slab_1 | floor_slab_1_beams_items_2_height_m | Балка Б-3: высота | м | P1 |
| floor_slab_1 | floor_slab_1_rebar_items_0_steel_class | Арматура 1: класс стали | - | P1 |
| floor_slab_1 | floor_slab_1_rebar_items_0_diameter_mm | Арматура 1: диаметр | мм | P1 |
| floor_slab_1 | floor_slab_1_rebar_items_1_steel_class | Арматура 2: класс стали | - | P1 |
| floor_slab_1 | floor_slab_1_rebar_items_1_diameter_mm | Арматура 2: диаметр | мм | P1 |
| floor_slab_1 | floor_slab_1_rebar_items_2_steel_class | Арматура 3: класс стали | - | P1 |
| floor_slab_1 | floor_slab_1_rebar_items_2_diameter_mm | Арматура 3: диаметр | мм | P1 |
| floor_slab_1 | floor_slab_1_rebar_items_3_steel_class | Арматура 4: класс стали | - | P1 |
| floor_slab_1 | floor_slab_1_rebar_items_3_diameter_mm | Арматура 4: диаметр | мм | P1 |
| floor_slab_1 | floor_slab_1_rebar_items_4_steel_class | Арматура 5: класс стали | - | P1 |
| floor_slab_1 | floor_slab_1_rebar_items_4_diameter_mm | Арматура 5: диаметр | мм | P1 |
| floor_slab_1 | floor_slab_1_rebar_items_5_steel_class | Арматура 6: класс стали | - | P1 |
| floor_slab_1 | floor_slab_1_rebar_items_5_diameter_mm | Арматура 6: диаметр | мм | P1 |
| floor_slab_1 | floor_slab_1_insulation_total_eps_volume_from_spec_m3 | total eps volume from spec m3 | м3 | P1 |
| floor_slab_2 | floor_slab_2_slab_edge_perimeter_m | Периметр торца плиты | м | P0 |
| floor_slab_2 | floor_slab_2_main_formwork_area_m2 | Основная площадь опалубки | м2 | P0 |
| floor_slab_2 | floor_slab_2_edge_insulation_height_m | Высота утепления торца | м | P0 |
| floor_slab_2 | floor_slab_2_rebar_items_0_steel_class | Арматура 1: класс стали | - | P1 |
| floor_slab_2 | floor_slab_2_rebar_items_0_diameter_mm | Арматура 1: диаметр | мм | P1 |
| floor_slab_2 | floor_slab_2_rebar_items_1_steel_class | Арматура 2: класс стали | - | P1 |
| floor_slab_2 | floor_slab_2_rebar_items_1_diameter_mm | Арматура 2: диаметр | мм | P1 |
| floor_slab_2 | floor_slab_2_rebar_items_2_steel_class | Арматура 3: класс стали | - | P1 |
| floor_slab_2 | floor_slab_2_rebar_items_2_diameter_mm | Арматура 3: диаметр | мм | P1 |
| foundation_slab | foundation_slab_rebar_items_0_steel_class | Арматура 1: класс стали | - | P1 |
| foundation_slab | foundation_slab_rebar_items_0_diameter_mm | Арматура 1: диаметр | мм | P1 |
| foundation_slab | foundation_slab_rebar_items_0_weight_parts_kg_0 | Арматура 1: вес по спецификации | кг | P1 |
| foundation_slab | foundation_slab_rebar_items_1_steel_class | Арматура 2: класс стали | - | P1 |
| foundation_slab | foundation_slab_rebar_items_1_diameter_mm | Арматура 2: диаметр | мм | P1 |
| foundation_slab | foundation_slab_rebar_items_1_weight_parts_kg_0 | Арматура 2: вес по спецификации | кг | P1 |
| foundation_slab | foundation_slab_rebar_items_1_weight_parts_kg_1 | Арматура 2: вес по спецификации | кг | P1 |
| foundation_slab | foundation_slab_rebar_items_2_steel_class | Арматура 3: класс стали | - | P1 |
| foundation_slab | foundation_slab_rebar_items_2_diameter_mm | Арматура 3: диаметр | мм | P1 |
| foundation_slab | foundation_slab_rebar_items_2_weight_parts_kg_0 | Арматура 3: вес по спецификации | кг | P1 |
| foundation_slab | foundation_slab_rebar_items_3_steel_class | Арматура 4: класс стали | - | P1 |
| foundation_slab | foundation_slab_rebar_items_3_diameter_mm | Арматура 4: диаметр | мм | P1 |
| foundation_slab | foundation_slab_rebar_items_3_weight_parts_kg_0 | Арматура 4: вес по спецификации | кг | P1 |
| load_bearing_walls_lintels | load_bearing_walls_lintels_main_wall_external_length_m | main wall external length m | м | P0 |
| load_bearing_walls_lintels | load_bearing_walls_lintels_main_wall_reinforcement_rows | main wall reinforcement rows | - | P0 |
| load_bearing_walls_lintels | load_bearing_walls_lintels_main_wall_400_reinforcement_threads | main wall 400 reinforcement threads | - | P0 |
| load_bearing_walls_lintels | load_bearing_walls_lintels_main_wall_250_reinforcement_threads | main wall 250 reinforcement threads | - | P0 |
| load_bearing_walls_lintels | load_bearing_walls_lintels_parapet_masonry_volume_m3 | parapet masonry volume m3 | м3 | P0 |
| load_bearing_walls_lintels | load_bearing_walls_lintels_lintel_rebar_items_0_steel_class | Арматура перемычек 1: класс стали | - | P1 |
| load_bearing_walls_lintels | load_bearing_walls_lintels_lintel_rebar_items_0_diameter_mm | Арматура перемычек 1: диаметр | мм | P1 |
| load_bearing_walls_lintels | load_bearing_walls_lintels_lintel_rebar_items_1_steel_class | Арматура перемычек 2: класс стали | - | P1 |
| load_bearing_walls_lintels | load_bearing_walls_lintels_lintel_rebar_items_1_diameter_mm | Арматура перемычек 2: диаметр | мм | P1 |
| load_bearing_walls_lintels | gas_block_d500_150_volume | Газобетонный блок 600х150х250 | м3 | P2 |
| schiedel_vent_channels | schiedel_vent_channels_vent_channel_1_height_m | vent channel 1 height m | м | P0 |
| schiedel_vent_channels | schiedel_vent_channels_vent_channel_2_height_m | vent channel 2 height m | м | P0 |
| schiedel_vent_channels | schiedel_vent_channels_vent_channel_2_count | vent channel 2 count | шт | P0 |

Итого AUTO_PROJECT без hints: **70** (P0: 24, P1: 45, P2: 1)

## 3.3 Что не покрываем hints и почему

| audit_category | count |
|---|---|
| not_audited | 346 |
| script_suggested | 126 |
| DEPRECATED_LEGACY_ONLY | 73 |
| SUPPLIER_INPUT | 5 |
| DEPRECATED_OPTIONAL_OVERRIDE | 4 |

Итого не-AUTO_PROJECT: 554 (из них `not_audited`: 346 — вне 284 строк июньского human audit, статус не проверялся человеком).

## reclassification_candidates

Не-AUTO_PROJECT параметры с `schema_input_type=parsed` (уже существующий в схеме сигнал "задумывался как приходящий из PDF", независимо от июньского аудита), для которых черновой пробный hint (unit + 1 ключевое слово, никогда не сохранялся в section_schema.py) нашёл совпадение через настоящий `resolve()` на реальных кандидатах USV/TRC. Это сигнал для человека, не решение — статус НЕ меняется автоматически.

Найдено уникальных совпадений: **13** (затрагивают 95 параметров-кандидатов)

| project | value | unit | confidence | affected_parameters (section :: code [audit_category]) | raw_text |
|---|---|---|---|---|---|
| USV | 3.1 | m | 0.6 | ⚠ 31 параметров: load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_0 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_1 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_2 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_3 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_4 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_5 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_6 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_7 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_8 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_9 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_10 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_11 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_12 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_13 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_14 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_15 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_0 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_1 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_2 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_3 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_4 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_5 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_6 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_7 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_8 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_9 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_10 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_11 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_12 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_13 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_14 [DEPRECATED_LEGACY_ONLY] | Схема расположения отсечной гидроизоляции 5 900 400 5 100 400 Ж 0 0 0 0 4 4 0 0 0 0 0 0 6 3 9 2 9 2  |
| TRC | 3.1 | m | 0.6 | ⚠ 31 параметров: load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_0 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_1 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_2 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_3 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_4 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_5 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_6 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_7 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_8 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_9 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_10 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_11 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_12 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_13 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_14 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_400_lengths_m_15 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_0 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_1 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_2 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_3 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_4 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_5 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_6 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_7 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_8 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_9 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_10 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_11 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_12 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_13 [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_cutoff_waterproofing_wall_250_lengths_m_14 [DEPRECATED_LEGACY_ONLY] | Д Г 400 14400 400 В Б А 1 2 3 4 5 6 7 004 0048 004 400 15600 400 004 400 052 0064 004 0521 250 3400  |
| TRC | 11.4 | kg | 0.4 | ⚠ 7 параметров: floor_slab_1::floor_slab_1_rebar_items_1_source_weight_parts_kg_0 [DEPRECATED_LEGACY_ONLY]; floor_slab_1::floor_slab_1_rebar_items_1_source_weight_parts_kg_1 [DEPRECATED_LEGACY_ONLY]; floor_slab_1::floor_slab_1_rebar_items_3_source_weight_parts_kg_0 [DEPRECATED_LEGACY_ONLY]; floor_slab_1::floor_slab_1_rebar_items_3_source_weight_parts_kg_1 [DEPRECATED_LEGACY_ONLY]; floor_slab_1::floor_slab_1_rebar_items_3_source_weight_parts_kg_2 [DEPRECATED_LEGACY_ONLY]; floor_slab_1::floor_slab_1_rebar_items_5_source_weight_parts_kg_0 [DEPRECATED_LEGACY_ONLY]; floor_slab_1::floor_slab_1_rebar_items_5_source_weight_parts_kg_1 [DEPRECATED_LEGACY_ONLY] | 200 200 200 200 200 200 200 200 200 200 200 200 250 200 200 400 400 400 400 400 400 400 400 330 370  |
| USV | 0.0 | m | 0.85 | ⚠ 6 параметров: load_bearing_walls_lintels::load_bearing_walls_lintels_lintel_lengths_m_0_length_m [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_lintel_lengths_m_1_length_m [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_lintel_lengths_m_2_length_m [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_lintel_lengths_m_3_length_m [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_lintel_lengths_m_4_length_m [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_lintel_lengths_m_5_length_m [DEPRECATED_LEGACY_ONLY] | 1-1 План перемычек 1-го этажа 2 ЭППС 100 мм Стена наружняя 400 мм. Перемычка Пм-4 в U-блоке 250 3 00 |
| TRC | 0.2 | m | 0.85 | ⚠ 6 параметров: load_bearing_walls_lintels::load_bearing_walls_lintels_lintel_lengths_m_0_length_m [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_lintel_lengths_m_1_length_m [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_lintel_lengths_m_2_length_m [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_lintel_lengths_m_3_length_m [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_lintel_lengths_m_4_length_m [DEPRECATED_LEGACY_ONLY]; load_bearing_walls_lintels::load_bearing_walls_lintels_lintel_lengths_m_5_length_m [DEPRECATED_LEGACY_ONLY] | Схема фасада восях1-7 Ж/бперемычкавU- образномблоке Ж/бперемычкавU- +7,900 +7,900 образномблоке +7,4 |
| USV | 0.888 | m | 0.6 | ⚠ 3 параметров: waterproofing::waterproofing_non_insulated_edge_lengths_m_0 [DEPRECATED_LEGACY_ONLY]; waterproofing::waterproofing_non_insulated_edge_lengths_m_1 [DEPRECATED_LEGACY_ONLY]; waterproofing::waterproofing_non_insulated_edge_lengths_m_2 [DEPRECATED_LEGACY_ONLY] | Спецификация к плану фундаментной плиты Поз. Обозначение Н аименование К ол-во Масса ед. шт. Примеча |
| TRC | 3.0 | m | 0.8 | ⚠ 3 параметров: waterproofing::waterproofing_non_insulated_edge_lengths_m_0 [DEPRECATED_LEGACY_ONLY]; waterproofing::waterproofing_non_insulated_edge_lengths_m_1 [DEPRECATED_LEGACY_ONLY]; waterproofing::waterproofing_non_insulated_edge_lengths_m_2 [DEPRECATED_LEGACY_ONLY] | ВЕДОМОСТЬ ДЕТАЛЕЙ ФУНДАМЕНТА Кол- Поз Эскиз во 400 1. 2. 3. 4. 122 300 091 091 300 300 400 171 300 1 |
| USV | 0.617 | kg | 0.75 | ⚠ 2 параметров: floor_slab_2::floor_slab_2_rebar_a500_d10_weight_extra_1 [not_audited]; floor_slab_2::floor_slab_2_rebar_a500_d10_weight_extra_2 [not_audited] | План плиты перекрытия на отм. + 4. 680 Ж 0 0 6 3 Е Сечение по плите перекрытия 0 0 Верхнее фоновое а |
| TRC | 7.881 | kg | 0.8 | ⚠ 2 параметров: floor_slab_2::floor_slab_2_rebar_a500_d10_weight_extra_1 [not_audited]; floor_slab_2::floor_slab_2_rebar_a500_d10_weight_extra_2 [not_audited] | 100 300 +6,700 +6,450 +6,250 +6,250 В 052 054 Ø16 A500C 3шт. поз.1 Хомут Ø6А240 c шагом 200 Ø20 A500 |
| USV | 78.95 | m3 | 0.6 | load_bearing_walls_lintels::gas_block_d500_250_volume [not_audited] | Спецификация по газобетонным блокам Поз. Обозначение Н аименование К ол-во Масса ед. шт. Примечание  |
| TRC | 1.48 | m3 | 0.6 | load_bearing_walls_lintels::gas_block_d500_250_volume [not_audited] | Узел 1А арм-ние угла наружных стен толщиной 400 мм Штроба 25х25мм предварительно заполненная клеем Г |
| USV | 235.06 | m2 | 0.55 | flat_roof::flat_roof_roof_area_total_m2 [script_suggested:AUTO_CALCULATED] | Пояснительная записка ОБЩИЕ ДАННЫЕ: 1. Проектная документация марки КР разработанна в соответствии с |
| TRC | 150.495 | m2 | 0.67 | flat_roof::flat_roof_roof_area_total_m2 [script_suggested:AUTO_CALCULATED] | Условныеобозначения ОБЩИЕДАННЫЕ: №п/п Наименование Сечение Поверхность Примечание 1. Проектнаядокуме |

⚠ = одно и то же свидетельство совпало сразу с несколькими параметрами — обычно значит, что вероятное ключевое слово всё ещё недостаточно специфично для этой группы параметров (например, однотипные позиции списка с одинаковым названием). Проверять такие строки осторожнее, чем строки с одним параметром.
