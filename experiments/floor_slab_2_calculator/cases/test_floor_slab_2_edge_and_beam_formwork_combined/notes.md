# Combined edge+beam vertical formwork, ported from floor_slab_1

Added 2026-07-26. `edge_and_beam_formwork_area_combined_m2` did not exist in `floor_slab_2_calculator`
at all before this — floor_slab_2 lagged behind floor_slab_1 (shipped there 2026-07-21), even though a
real project's floor-2 slab can give the same merged-edge-and-beam figure that floor_slab_1's real
project case did. Confirmed this gap is universal, not project-specific: multiple real project smetas
reviewed this session use the identical work-line name ("Монтаж опалубки из доски 50 мм и фанеры для
устройства балок и отбортовки плиты") and the same two-line structure (this combined line + a separate
slab-bottom-only line) at BOTH floor 1 and floor 2, for every project checked.

Ported the mutually-exclusive override (same validation as floor_slab_1: providing
`edge_and_beam_formwork_area_combined_m2` together with `edge_formwork_area_m2`/`beams_formwork_area_m2`
raises). Grounded in a real project's floor-2 slab numbers: edge (7,52 м2) + beam (5,4 м2) vertical
formwork given as one combined figure (12,92 м2), no beam-bottom formwork in this case (0).

Confirms:
- `edge_formwork_area_m2`/`beams_formwork_area_m2` become `null` when combined is used (mirrors
  floor_slab_1's convention);
- `edge_and_beam_formwork_area_m2` = 12,92 (the combined value, used as-is);
- plywood/timber and the `edge_formwork_installation_control` work line both correctly use 12,92.

Additive: `edge_and_beam_formwork_area_combined_m2` defaults to unset (falls back to the existing split
fields) — all 7 pre-existing cases pass unchanged.
