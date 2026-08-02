# Service-memo coverage check

Extraction file: `experiments/chat_extraction_poc/outputs/trc/gpt_trc_extraction_2026-08-02.json`
Service memo: `experiments/chat_extraction_poc/outputs/trc/gpt_trc_service_note_2026-08-02.txt`

Heuristic: literal substring search for each needs_review code inside the memo text. Not found = verify by hand, not a confirmed bug. Found = code is mentioned somewhere, doesn't guarantee the explanation is correct or complete.

Distinct needs_review codes: 21. Not found in memo: 12.

## Not found in service memo — verify by hand

- `beam_items` (section(s): floor_slab_1, 8 row(s)) — sample source: "Б1.1: Длина 5.1; Ширина 0.25; Высота 0.7; Бетон 0.892 м3; Опалубка 8.415 м2"
- `beam_table_controls` (section(s): floor_slab_1, 2 row(s)) — sample source: "Сумма бетона по строкам таблицы балок: 3,18 м3"
- `floor_slab_1_concrete_volume` (section(s): floor_slab_1, 1 row(s)) — sample source: "Несколько отдельных значений по плитам; явного общего итога нет"
- `floor_slab_1_edge_eps_work_length` (section(s): floor_slab_1, 1 row(s)) — sample source: "Несколько отдельных значений по плитам; явного общего итога нет"
- `floor_slab_1_edge_formwork_area` (section(s): floor_slab_1, 1 row(s)) — sample source: "Несколько отдельных значений по плитам; явного общего итога нет"
- `floor_slab_1_eps100_volume` (section(s): floor_slab_1, 1 row(s)) — sample source: "Несколько отдельных значений по плитам; явного общего итога нет"
- `floor_slab_1_kind` (section(s): floor_slab_1, 1 row(s)) — sample source: "В проекте выделены основная плита и отдельная плита на отм. +3,750"
- `floor_slab_1_rebar_items` (section(s): floor_slab_1, 5 row(s)) — sample source: "А240 ф-6 хомуты l=1020; 54 шт; 55,08 п.м; 12,22 кг"
- `floor_slab_1_slab_edge_perimeter` (section(s): floor_slab_1, 1 row(s)) — sample source: "Несколько отдельных значений по плитам; явного общего итога нет"
- `floor_slab_1_under_slab_formwork_area` (section(s): floor_slab_1, 1 row(s)) — sample source: "Несколько отдельных значений по плитам; явного общего итога нет"
- `floor_slab_2_beam_items` (section(s): floor_slab_2, 1 row(s)) — sample source: "БГ-1: Длина 4,85; Ширина 0,3; Высота 0,25; Бетон 0,363 м3; Опалубка 2,575 м2"
- `geotextile_laying_area_m2` (section(s): earthworks, 1 row(s)) — sample source: "Геотекстиль — 189,280 м2"

## Found in service memo

- `eps_50_under_slab_volume` (section(s): foundation_slab, 1 row(s))
- `floor_slab_1_beams_concrete_volume` (section(s): floor_slab_1, 1 row(s))
- `floor_slab_2_beams_concrete_volume` (section(s): floor_slab_2, 1 row(s))
- `floor_slab_2_kind` (section(s): floor_slab_2, 1 row(s))
- `roof_raw_material_spec_rows` (section(s): flat_roof, 1 row(s))
- `roof_zones` (section(s): flat_roof, 1 row(s))
- `slab_zones` (section(s): foundation_slab, 2 row(s))
- `trench_routes` (section(s): earthworks, 2 row(s))
- `waterproofing_area_m2` (section(s): waterproofing, 1 row(s))

