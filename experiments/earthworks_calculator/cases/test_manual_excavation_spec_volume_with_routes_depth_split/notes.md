# Spec-table trench_volume_m3 + named trench_routes given together

Added 2026-08-09. Real-project shape (TRC): sheet 01 has both a spec-table trench total
(`trench_volume_m3`, autosummed from the raw routes group and trusted over recomputed
geometry) AND the individual named routes (`trench_routes`) with their own lengths, used only
to split the manual (hand-dig) portion by network type.

Before this case existed, giving both together made the calculator silently drop
`trench_routes` entirely (`trench_volume_m3 is not None` short-circuited the whole
`standard_routes` branch), so `trench_manual_portion_m3` fell back to 100% of the trench total
instead of the real per-network formula - the exact bug found in the TRC pipeline run
2026-08-09 (`manual_excavation_total_m3` stuck at the old broken figure even after the
per-network coefficients were built and correctly filled in on sheet 01-1).

This case proves both halves now work independently: `trench_volume_total_m3` still comes from
the given `trench_volume_m3` (50, not the routes' geometry sum of 8.0 - spec wins, unchanged),
while `trench_manual_portion_m3` is computed from `trench_routes` (K1: 10m x 0.6m x 0.4m = 2.4,
K2: 8m x 1.0m x 0.4m = 3.2, total 5.6) rather than defaulting to the full 50.
`manual_excavation_total_m3` = manual_pit_volume_m3 (8.0) + trench_manual_portion_m3 (5.6) = 13.6.
