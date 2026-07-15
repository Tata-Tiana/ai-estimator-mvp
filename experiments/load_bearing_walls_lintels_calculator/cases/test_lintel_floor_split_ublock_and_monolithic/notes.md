# Lintels split per floor, U-block + monolithic

Added 2026-07-15 after finding, on a real ТРЦ project smeta, that a full two-floor
house's lintels are not a single project-wide total: floor 1 and floor 2 each have their
own U-block lintel length, their own monolithic lintel concrete volume, and floor 2 can
have a different rebar diameter (Ø16) than floor 1. See
`docs/report_load_bearing_walls_floor_2_refactor.md` for the discovery and Elena's
confirmation (2026-07-15) that:
- monolithic and U-block lintels can coexist, or either type alone — at least 50% of
  projects have monolithic lintels;
- U-block lintels need no formwork; monolithic lintels need plywood + timber board only
  (no separate formwork-installation work line in the cost structure);
- monolithic lintels are always insulated (Пеноплэкс Основа + glue-foam), so insulation
  shares the same enable gate as the monolithic block, not a separate condition;
- concrete material purchase is combined per floor across both lintel types (same truck),
  but the work lines stay split by construction method.

This case exercises the full matrix: floor 1 has both U-block (22.62 м.п.) and
monolithic (0.35 м3) lintels; floor 2 has both too (20.5 м.п. U-block, 0.41 м3
monolithic, matching the real ТРЦ numbers). Verifies 23 new/changed line codes appear
with correct quantities, and that the combined concrete purchase per floor correctly
sums U-block + monolithic need before applying the 1 m3 minimum order.

Numbers hand-verified against the calculation formulas before being captured into
`expected.json` (see conversation this was built in — spot-checked u_block_quantity,
combined concrete order volumes, EPS pack rounding, and glue-foam minimum-unit logic).
