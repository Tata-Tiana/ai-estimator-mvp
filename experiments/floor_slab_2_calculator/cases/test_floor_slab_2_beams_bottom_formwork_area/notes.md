# Beam bottom (horizontal) formwork area, ported from floor_slab_1 — feeds material AND work

Added 2026-07-26. `beams_bottom_formwork_area_m2` did not exist in `floor_slab_2_calculator` at all
before this. Ported from floor_slab_1 (shipped there 2026-07-26, same day) — real project's floor-2
slab gives the beam's own horizontal/bottom formwork as its own separate line (3,1 м2), distinct from
the combined vertical slab+beam area (12,92 м2, see `test_floor_slab_2_edge_and_beam_formwork_combined`)
and from the slab's own horizontal area (`main_formwork_area_m2`).

Unlike floor_slab_1's original 2026-07-26 shipment (which only fed this into plywood/timber material,
leaving the installation-work control line unfixed until corrected later the same day — see that
calculator's own notes), this port goes straight to the corrected behavior: both plywood/timber
material AND `edge_formwork_installation_control`'s quantity include the beam-bottom area from the
start, matching real project smetas checked this session where the installation work-line quantity
already equals vertical-slab-edge + vertical-beam + beam-bottom (not vertical-only).

This case reuses `test_floor_slab_2_edge_and_beam_formwork_combined`'s inputs, adding
`beams_bottom_formwork_area_m2=3.1`. Confirms:
- `edge_beam_formwork_area_for_materials_m2` = 12,92 + 3,1 = 16,02 (drives plywood/timber AND the
  installation-control work quantity, both correctly at 16,02);
- `edge_plywood_sheets_raw` increases from 5,617391 (combined-only case) to 6,965217;
- `timber_volume_m3_raw` increases from 0,646 to 0,801.

Additive: `beams_bottom_formwork_area_m2` defaults to 0 when absent — all pre-existing cases
(including the combined-formwork case above) are byte-identical (confirmed via full regression).
