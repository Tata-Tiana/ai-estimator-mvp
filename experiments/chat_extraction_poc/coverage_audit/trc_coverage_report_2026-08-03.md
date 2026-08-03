# Coverage audit — chat-extraction completeness

Extraction file: `experiments/chat_extraction_poc/outputs/trc/gpt_trc_extraction_2026-08-03.json`

Sections checked: 8. Total expected targets/groups: 115. Never mentioned anywhere: 8.
Never-mentioned severity: blocker_or_schema_gap=1, legacy_ignored=1, optional_absent=6.

## earthworks — optional_only

- Expected: 11 | found: 7 | missing: 2 | needs_review: 2 | **never mentioned: 2**

Never mentioned anywhere (not found/missing/needs_review), classified:
  - `pit_items` — optional_absent: Optional detail group: only needed when the project gives pit/foundation excavation as separate item rows.
  - `sand_items` — optional_absent: Optional detail group: only needed when the project gives sand volumes as separate item rows.

## flat_roof — ok

- Expected: 15 | found: 7 | missing: 8 | needs_review: 4 | **never mentioned: 0**

## floor_slab_1 — ok

- Expected: 20 | found: 14 | missing: 6 | needs_review: 9 | **never mentioned: 0**

## floor_slab_2 — ok

- Expected: 15 | found: 10 | missing: 5 | needs_review: 4 | **never mentioned: 0**

## foundation_slab — gaps_found

- Expected: 14 | found: 8 | missing: 3 | needs_review: 1 | **never mentioned: 3**

Never mentioned anywhere (not found/missing/needs_review), classified:
  - `column_footing_items` — optional_absent: Optional future/detail group: only needed when the project has column footings below zero.
  - `foundation_wall_items` — optional_absent: Optional future/detail group: only needed when the project has foundation/rostverк walls below zero.
  - `thermal_insert_items` — blocker_or_schema_gap: Expected by calculator_targets_compact.json but not mentioned in found/missing/needs_review.

## load_bearing_walls_lintels — optional_only

- Expected: 33 | found: 21 | missing: 10 | needs_review: 0 | **never mentioned: 2**

Never mentioned anywhere (not found/missing/needs_review), classified:
  - `lintel_groove_rebar_items` — legacy_ignored: Diagnostic/future group: captures groove lintel rebar for later logic; current calculator does not require it.
  - `vent_chimney_cladding_segments` — optional_absent: Optional detail group: only needed when the project has gas-block cladding around vent/chimney shafts.

## schiedel_vent_channels — optional_only

- Expected: 3 | found: 2 | missing: 0 | needs_review: 0 | **never mentioned: 1**

Never mentioned anywhere (not found/missing/needs_review), classified:
  - `schiedel_masonry_gas_block_items` — optional_absent: Optional detail group: only needed when the Schiedel/vent section has separate gas-block masonry rows.

## waterproofing — ok

- Expected: 4 | found: 4 | missing: 0 | needs_review: 1 | **never mentioned: 0**

