# Утепление монолитной перемычки = 0 не должно заказывать минимум клей-пены

Same base data as `test_lintel_monolithic_formwork_from_area`, but floor 2's monolithic
lintel has `floor_2_lintel_monolithic_insulation_length_m: 0` and
`floor_2_lintel_insulation_eps_spec_volume_m3: 0` (concrete/length stay real — the
monolithic lintel itself exists and is billed, it just isn't insulated at all, matching
Elena's 2026-07-29 rule that monolithic lintels are not always insulated).

Before the fix, `foam_units` shared the lintel's own `enabled` (true here, from
concrete/length) instead of its own `insulation_length_m > 0` check — so a lintel with
zero insulation would still order the minimum glue-foam can (`glue_foam_units: 1`)
despite there being nothing to glue. After the fix, floor 2's
`insulation_enabled: false` and `glue_foam_units: 0`; floor 1 (still genuinely insulated,
unchanged from the base case) keeps `insulation_enabled: true` and its normal
`glue_foam_units: 1`.
