# Service-memo coverage check

Extraction file: `experiments/chat_extraction_poc/coverage_audit/gpt_arkadia_extraction(2).json`
Service memo: `experiments/chat_extraction_poc/coverage_audit/gpt_arkadia_service_note(2).txt`

Heuristic: literal substring search for each needs_review code inside the memo text. Not found = verify by hand, not a confirmed bug. Found = code is mentioned somewhere, doesn't guarantee the explanation is correct or complete.

Distinct needs_review codes: 16. Not found in memo: 7.

## Not found in service memo — verify by hand

- `beam_items` (section(s): floor_slab_1, 1 row(s)) — sample source: "Б4/Б4-1: длина 24,1 м; бетон B-22,5 5,3 м3"
- `communications_pipe_items` (section(s): earthworks, 5 row(s)) — sample source: "ГОСТ32412-2013 Труба 3м, Ø110 (рыжая) 8 шт"
- `floor_1_lintel_insulation_eps_volume` (section(s): load_bearing_walls_lintels, 1 row(s)) — sample source: "ПБ1 ГОСТ 32310-2012 ЭППС 100мм 0,07 м3"
- `floor_slab_1_edge_eps_work_length` (section(s): floor_slab_1, 1 row(s)) — sample source: "Периметр плиты ПМ1 покрытия стен 1этажа под устройство утепления из ЭППС 100мм (н=180мм) - 73,2м.пог"
- `floors_count` (section(s): load_bearing_walls_lintels, 1 row(s)) — sample source: "Конструкции стен 1-го этажа; выше — стены второго света/надстройки и парапеты, отдельного 2-го этажа нет."
- `geotextile_laying_area_m2` (section(s): earthworks, 1 row(s)) — sample source: "ГОСТ 32491-2013 Геотекстиль 520,0м2"
- `waterproofing_area_m2` (section(s): waterproofing, 1 row(s)) — sample source: "Общая площадь вертикальной опалубки плит фундамента ФП1, ФП2 - 46,5м2"

## Found in service memo

- `floor_1_lintel_insulation_length` (section(s): load_bearing_walls_lintels, 1 row(s))
- `floor_1_lintel_monolithic_concrete_volume` (section(s): load_bearing_walls_lintels, 1 row(s))
- `lintel_groove_rebar_items` (section(s): load_bearing_walls_lintels, 1 row(s))
- `membrane_area_m2` (section(s): foundation_slab, 1 row(s))
- `pit_excavation_depth_m` (section(s): earthworks, 1 row(s))
- `roof_internal_drains_count` (section(s): flat_roof, 1 row(s))
- `roof_raw_material_spec_rows` (section(s): flat_roof, 1 row(s))
- `roof_zones` (section(s): flat_roof, 2 row(s))
- `wall_block_items` (section(s): load_bearing_walls_lintels, 1 row(s))

