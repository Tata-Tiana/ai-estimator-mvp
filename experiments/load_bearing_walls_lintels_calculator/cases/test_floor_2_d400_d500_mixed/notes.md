# Floor 2 mixed D400 + D500 — closes the known floor_2 D500 gap

Added 2026-07-24 (Elena, via ТРЦ real-project review). Replaces the old negative test
`test_wall_block_items_unsupported_combination_rejected`, which proved `("floor_2", "D500")` was
rejected — that gap is now closed.

Same principle as floor 1 and parapet: external walls are D400 600x400x250, internal load-bearing
walls are D500 600x250x250, on any floor. Floor 1 already priced both; floor 2 only priced D400 until
this fix — real ТРЦ data (КР2_ТРЦ, p.8, read directly from the PDF) shows floor 2 genuinely has both:
"КС_Блок 400х600х250(D-400) 2эт — 50,71 м³" and "КС_Блок 250х600х250(D-500) 2эт — 10,95 м³". The real
delivered ТРЦ smeta ("НС 29.06.26", row 114) confirms the masonry work line combines both densities
into one quantity — 61,66 м3, exactly 50.71 + 10.95 — while material purchase stays split by density
(row 115 D400, row 116 D500) because the two blocks have different prices.

This case: `wall_block_items` with two `floor_2` rows (D400=50.71, D500=10.95). Confirms:
- `floor_2_total_masonry_volume_m3` (61.66) — used for the single masonry work line, matches the real
  ТРЦ smeta combined quantity exactly;
- `floor_2_gas_block_d400_material` and `floor_2_gas_block_d500_material` — split material lines, each
  independently gated (D500 line only appears if its portion is > 0), same convention as parapet's
  D400/D500 split (see `test_parapet_d400_d500_mixed`);
- glue quantity is now based on the combined D400+D500 volume, not D400 alone.

`WALL_BLOCK_ITEM_PRICED_KEYS` now includes `("floor_2", "D500")`. The legacy scalar path
(`floor_2_masonry_volume_m3`, no `wall_block_items`) is unaffected — it has no D500 concept and stays
byte-identical, since real floor_2 D500 data can only reach the calculator through `wall_block_items`.
