# Trench routes — given volume_m3 takes priority over length*depth*width

Added 2026-07-26. Real project finding: a project's own trench-plan table (План котлована) prints a
ready м3 column per route (К1/К2/Вода/Эл.кабель) that disagrees with `length_m * depth_m * width_m`
computed from the same table's other columns — none of the four rows match, and the mismatch is not a
consistent scale factor, so it can't be a units error.

Elena's decision: the printed/given volume always wins ("готовая сумма траншей/коммуникаций в
приоритете"); the calculator should only flag the mismatch as a warning, not block or try to
reconcile it, because she reviews every trench/communications row by hand anyway (see
`feedback_communications_precision_not_needed` memory).

This case grounds that fix: each route in `trench_routes` carries an explicit `volume_m3` that
diverges from its own `length_m * depth_m` geometry (times the shared `trench_width_m = 0.4`).
`calculate_trench_routes()` now uses the given `volume_m3` per route when present, still reports the
geometry-derived value as `calculated_volume_m3` for transparency, and appends one warning string per
mismatching route to `volume_result.trench_routes_warnings` / top-level `warnings`
(tolerance 0.01 m3).

Expected total: 12.2 + 3.48 + 8.5 + 8.2 = 32.38 m3 (matches the real project's own printed trench
total), not the geometry sum (which would be roughly 6.15 + 1.74 + 7.06 + 5.79 ≈ 20.7 m3).

`pit_area_m2` is set to 0 here specifically so `manual_pit_volume_m3` is 0 and the trench-only
behavior can be checked in isolation without also depending on pit geometry.
