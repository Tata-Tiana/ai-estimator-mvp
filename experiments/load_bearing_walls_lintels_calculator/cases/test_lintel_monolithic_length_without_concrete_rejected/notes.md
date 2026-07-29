# Negative test: длина монолитной перемычки без бетона

Grounded in a real 2026-07-29 АРК case: ПБ1/ПБ2 (1-й этаж) give a combined
`floor_1_lintel_monolithic_total_length_m = 5.4` in the spec, but concrete is only given
per-lintel separately (ПБ1=0.21, ПБ2=0.16) with no combined total — extraction correctly
leaves `floor_1_lintel_monolithic_concrete_volume_m3` as missing/null rather than guessing
a sum. Before the 2026-07-29 fix, `calculate_monolithic_lintel_block` only guarded the
opposite direction (concrete without length) — this combination silently priced the
concreting work by length while defaulting concrete material to 0, losing real money with
no error. This case is the same base data as `test_lintel_monolithic_formwork_from_area`
with only `floor_1_lintel_monolithic_concrete_volume_m3` set to `null`.

Expected behavior: the calculator must raise:

```text
monolithic lintel concrete material requires concrete_volume_m3 when total_length_m is present
```
