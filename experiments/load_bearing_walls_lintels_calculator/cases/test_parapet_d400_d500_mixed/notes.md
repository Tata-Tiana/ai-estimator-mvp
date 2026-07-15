# Parapet mixed D400 + D500

Added 2026-07-15. Elena clarified (2026-07-15) that parapet is usually D400
600x400x250 (80-90% of projects) but can rarely be entirely D500 600x250x250, or
mixed (part D400, part D500), depending on building architecture. D500 250mm-width
is the same SKU already used as the second material for main walls
(main_wall_gas_block_250_spec_volume_m3) — not a new block type.

This case: parapet_masonry_volume_m3=15.0 (D400 portion),
parapet_gas_block_d500_250_spec_volume_m3=6.74 (D500 portion). Confirms:
- masonry work line (кладка) combines both densities into one quantity (21.74 m3) —
  it's one physical laying operation regardless of block density;
- material lines stay split by density, each independently gated (only appears if
  its own portion is > 0) — verified separately in this session that a pure-D500
  scenario (D400 portion = 0) correctly omits the D400 material line while keeping
  the masonry work and D500 material lines.

Also corrects an earlier wrong finding from this session: a narrow 600x150x250 block
seen in a real ТРЦ smeta's "Парапет" section was NOT a second parapet block type —
Elena clarified it was vent-channel cladding material grouped under the same smeta
section only because vent channels sit on the roof near the parapet. That material
already has its own correct field (vent_chimney_gas_block_spec_volume_m3, D500
600x150x250) — no code change was needed there.
