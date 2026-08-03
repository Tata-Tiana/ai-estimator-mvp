# Service-memo coverage check

Extraction file: `experiments/chat_extraction_poc/outputs/trc/gpt_trc_extraction_2026-08-03.json`
Service memo: `experiments/chat_extraction_poc/outputs/trc/gpt_trc_service_memo_2026-08-03.txt`

Heuristic: literal substring search for each needs_review code inside the memo text. Not found = verify by hand, not a confirmed bug. Found = code is mentioned somewhere, doesn't guarantee the explanation is correct or complete.

Distinct needs_review codes: 21. Not found in memo: 10.

## Not found in service memo — verify by hand

- `beam_table_controls` (section(s): floor_slab_1, 1 row(s)) — sample source: "0,892+0,205+0,756+0,072+0,156+0,591+0,399+0,109 = 3,180 м3"
- `floor_slab_1_edge_eps_work_length` (section(s): floor_slab_1, 1 row(s)) — sample source: "Основная плита: 67,2 п.м; Плита кухни/гостиной: 10,6 п.м"
- `floor_slab_1_edge_formwork_area` (section(s): floor_slab_1, 1 row(s)) — sample source: "Вертикальные поверхности основной плиты и балок: 36,6 м2; Вертикальные поверхности плиты кухни/гостиной: 5,6 м2"
- `floor_slab_1_eps100_volume` (section(s): floor_slab_1, 1 row(s)) — sample source: "Вертикальные поверхности основной плиты: 1,478 м3; Под основной плитой: 1,549 м3; Плита кухни/гостиной: 0,263 м3"
- `floor_slab_1_slab_edge_perimeter` (section(s): floor_slab_1, 1 row(s)) — sample source: "Основная плита: 67,2 п.м; Плита кухни/гостиной: 10,6 п.м"
- `floor_slab_1_under_slab_formwork_area` (section(s): floor_slab_1, 1 row(s)) — sample source: "Основная плита: 97,11 м2; Плита кухни/гостиной: 25,05 м2"
- `floor_slab_2_beam_items` (section(s): floor_slab_2, 1 row(s)) — sample source: "БГ-1: длина 4,85п.м; ширина 0,3м; высота 0,25м; бетон 0,363м3; опалубка 2,575м2"
- `floor_slab_2_beams_eps_material_area` (section(s): floor_slab_2, 1 row(s)) — sample source: "ЭППС-100мм (Утепление вертикальных поверхностей плиты) — 0,942м3"
- `geotextile_laying_area_m2` (section(s): earthworks, 1 row(s)) — sample source: "Геотекстиль — 189,280 м2"
- `roof_raw_material_spec_rows` (section(s): flat_roof, 1 row(s)) — sample source: "Экстр. пенополистирол ТЕХНОНИКОЛЬ CARBON PROF SLOPE — 131,0,75м2"

## Found in service memo

- `beam_items` (section(s): floor_slab_1, 8 row(s))
- `eps_50_under_slab_volume` (section(s): foundation_slab, 1 row(s))
- `floor_slab_1_beams_concrete_volume` (section(s): floor_slab_1, 1 row(s))
- `floor_slab_1_beams_formwork_area` (section(s): floor_slab_1, 1 row(s))
- `floor_slab_2_beams_concrete_volume` (section(s): floor_slab_2, 1 row(s))
- `floor_slab_2_kind` (section(s): floor_slab_2, 1 row(s))
- `roof_vent_wall_abutment_level_2` (section(s): flat_roof, 1 row(s))
- `roof_zones` (section(s): flat_roof, 1 row(s))
- `trench_routes` (section(s): earthworks, 2 row(s))
- `vent_shaft_abutment_count` (section(s): flat_roof, 1 row(s))
- `waterproofing_area_m2` (section(s): waterproofing, 1 row(s))

