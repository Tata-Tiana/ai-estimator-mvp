# Pit items, sand items, trench depth_reference — real project case

Added 2026-07-26. Real project PDF (КР1, p.6/8, read directly): the pit-excavation spec gives ready
total volumes rather than area×depth geometry — "Площадь котлована 413,8м2", "Площадь приямков
подпятников 15,7м2", "Объем выемки грунта котлована 185,0м3", "Объем выемки грунта приямков
подпятников 27,5м3" — and sand backfill by category rather than the base/trench split the calculator
assumed — "Песок засыпки пазух стен и дна траншей 236,0м3", "Песок дна котлована подпятников 1,2м3".
Separately, the trench table on p.8 prints two depth rows per route ("Глубина" and "Глубина от дна
котлована") — the second is a different reference point that doesn't participate in any arithmetic
check today, but needs to be captured for context so a future check doesn't false-positive on it.

## pit_items[]

`calculate_excavator_shifts()` previously only computed `pit_area_m2 * pit_excavation_depth_m`. New
optional `pit_items` (`{context, volume_m3}` per row) sums to `machine_excavation_volume_m3` directly
when given, bypassing the geometry calc — same "stated project volume wins over recomputed geometry"
principle as `trench_routes[].volume_m3`. Here: Котлован 185,0 + Приямки подпятников 27,5 = 212,5;
`excavator_productivity_m3_per_shift` is already 80 by default (matches this project) →
ceil(212,5/80) = 3 shifts.

## sand_items[]

Previously `sand_base_volume_m3` (pit sand) and trench-derived sand were compacted separately then
summed. New optional `sand_items` sums raw quantities first (236,0 + 1,2 = 237,2), then applies the
*existing* `sand_compaction_coeff` (already 1,3 by default) and `sand_truck_step_m3` (already 20 by
default) exactly as before — no new math, only a new input source that replaces the base/trench split
when the PDF gives ready category totals that don't map onto it. Expected: raw 237,2 × 1,3 = 308,36 →
round up to nearest 20 → 320 m3. Material and work lines already shared one quantity
(`sand_order_volume_m3`) before this change — "работа равно материалу" was already true, confirmed
here, not newly introduced.

## trench_routes[].depth_reference

Purely a context string, carried through into the route's own result row and never used in any
calculation — confirmed here that the printed м3 column (16,4/23,0/2,4/18,3, total 60,1) matches
length×depth×width using the *regular* "Глубина" row, not "Глубина от дна котлована"; K2 and В1 have
small (~0.2-0.3%) rounding mismatches against that regular depth and produce warnings via the existing
`volume_m3` override machinery (unrelated to depth_reference), EO matches within tolerance.

All three additions are purely additive — every existing case (including
`test_excavator_shifts_standard`, `test_manual_excavation_standard_routes`) is untouched.
