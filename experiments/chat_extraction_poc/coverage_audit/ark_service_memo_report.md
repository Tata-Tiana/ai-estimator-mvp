# Service-memo coverage check

Extraction file: `gpt_arkadia_extraction(2).json`
Service memo: `gpt_arkadia_service_note(2).txt`

Heuristic: literal substring search for each needs_review code inside the memo text. Not found = verify by hand, not a confirmed bug. Found = code is mentioned somewhere, doesn't guarantee the explanation is correct or complete.

Distinct needs_review codes: 12. Not found in memo: 3.

## Not found in service memo — verify by hand

- `floor_slab_2_slab_area` (section(s): floor_slab_2, 1 row(s)) — sample source: "Нижняя опалубка плиты ПМ2 — 94,0м2"
- `geotextile_area_m2` (section(s): earthworks, 1 row(s)) — sample source: "ГОСТ 32491-2013 Геотекстиль 520,0м2"
- `geotextile_laying_area_m2` (section(s): earthworks, 1 row(s)) — sample source: "ГОСТ 32491-2013 Геотекстиль 520,0м2"

## Found in service memo

- `beam_items` (section(s): floor_slab_1, 1 row(s))
- `floor_1_lintel_monolithic_concrete_volume` (section(s): load_bearing_walls_lintels, 1 row(s))
- `floor_slab_1_concrete_volume` (section(s): floor_slab_1, 1 row(s))
- `membrane_area_m2` (section(s): foundation_slab, 1 row(s))
- `pit_excavation_depth_m` (section(s): earthworks, 1 row(s))
- `roof_internal_drains_count` (section(s): flat_roof, 1 row(s))
- `roof_raw_material_spec_rows` (section(s): flat_roof, 1 row(s))
- `roof_zones` (section(s): flat_roof, 3 row(s))
- `waterproofing_area_m2` (section(s): waterproofing, 1 row(s))

