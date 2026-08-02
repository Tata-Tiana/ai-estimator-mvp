# Coverage audit — chat-extraction completeness

Extraction file: `experiments/chat_extraction_poc/outputs/trc/gpt_trc_extraction_2026-08-02.json`

Sections checked: 8. Total expected targets/groups: 115. Never mentioned anywhere: 8.
Never-mentioned severity: legacy_ignored=1, optional_absent=7.

## earthworks — optional_only

- Expected: 11 | found: 7 | missing: 2 | needs_review: 2 | **never mentioned: 2**

Never mentioned anywhere (not found/missing/needs_review), classified:
  - `pit_items` — optional_absent: Optional detail group: only needed when the project gives pit/foundation excavation as separate item rows.
  - `sand_items` — optional_absent: Optional detail group: only needed when the project gives sand volumes as separate item rows.

## flat_roof — ok

- Expected: 15 | found: 5 | missing: 10 | needs_review: 2 | **never mentioned: 0**

## floor_slab_1 — optional_only

- Expected: 20 | found: 13 | missing: 6 | needs_review: 11 | **never mentioned: 1**

Never mentioned anywhere (not found/missing/needs_review), classified:
  - `slab_zones` — optional_absent: Optional alternative input: only needed when the project gives floor-slab concrete by zones with no ready total.

## floor_slab_2 — ok

- Expected: 15 | found: 9 | missing: 6 | needs_review: 3 | **never mentioned: 0**

## foundation_slab — optional_only

- Expected: 14 | found: 9 | missing: 3 | needs_review: 2 | **never mentioned: 2**

Never mentioned anywhere (not found/missing/needs_review), classified:
  - `column_footing_items` — optional_absent: Optional future/detail group: only needed when the project has column footings below zero.
  - `foundation_wall_items` — optional_absent: Optional future/detail group: only needed when the project has foundation/rostverк walls below zero.

## load_bearing_walls_lintels — optional_only

- Expected: 33 | found: 17 | missing: 14 | needs_review: 0 | **never mentioned: 2**

Never mentioned anywhere (not found/missing/needs_review), classified:
  - `lintel_groove_rebar_items` — legacy_ignored: Diagnostic/future group: captures groove lintel rebar for later logic; current calculator does not require it.
  - `vent_chimney_cladding_segments` — optional_absent: Optional detail group: only needed when the project has gas-block cladding around vent/chimney shafts.

## schiedel_vent_channels — optional_only

- Expected: 3 | found: 2 | missing: 0 | needs_review: 0 | **never mentioned: 1**

Never mentioned anywhere (not found/missing/needs_review), classified:
  - `schiedel_masonry_gas_block_items` — optional_absent: Optional detail group: only needed when the Schiedel/vent section has separate gas-block masonry rows.

## waterproofing — ok

- Expected: 4 | found: 4 | missing: 0 | needs_review: 1 | **never mentioned: 0**

