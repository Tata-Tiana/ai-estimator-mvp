# Thermal inserts — arbitrary size via thermal_insert_items[] (not a 50/100 split)

Added 2026-07-26. Real АРК КР1 case (p.15, read directly): a single thermal-insert type Т1,
ЭППС 100x400x160(h), total installation length 14,2 м.пог, spec material quantity 0,09 м3 — no 50mm/100mm
split at all, unlike the ТРЦ/ЮСВ projects `standard_50_100` was built for (see
`test_foundation_slab_thermal_inserts_combined_length`/`test_foundation_slab_thermal_inserts_standard`).

`thermal_insert_mode = "standard_50_100"` can't represent this: it hardcodes exactly two fixed
thicknesses. New `thermal_insert_mode = "items"` generalizes to any number of arbitrary sizes via
`thermal_insert_items[]` (`eps_size` free string + `length_m` + `material_spec_qty_m3` +
`pack_multiple_qty` + `material_unit_price` per item):

- material stays per-item (spec qty * waste coeff, rounded up to that item's own pack multiple) —
  same math as the existing 50/100 fields, just not hardcoded to two names;
- installation work is one combined line by the sum of all items' lengths — same convention already
  established for `thermal_insert_combined_length_m` (Elena, 2026-07-25: "брать работу общей суммой"),
  generalized from exactly 2 sizes to N.

Rebar for the thermal insert itself needed zero changes — `rebar_items[]` was already a fully generic
diameter/class list, not tied to any specific construction, so ARK's ф12+ф6 composition (vs ЮСВ's
ф16/12/6) just becomes different rows in the same list.

This case: one item, `eps_size="100x400x160"`, `length_m=14.2`, `material_spec_qty_m3=0.09`,
`pack_multiple_qty=0.2776` (reusing the existing EPS-pack-size convention from the sibling test cases,
not a real ARK packaging number — this is a formula/regression test, not an Elena-validated production
case), `material_unit_price=9800`. Expected: `material_raw_qty_m3 = 0.09*1.05 = 0.0945`, rounded up to
the 0.2776 pack multiple → `0.2776` (one pack) — same purchase-quantity math the sibling combined-length
case already exercises, just reached through the new per-item path. Combined installation length =
14.2 (only one item here; the field still sums correctly regardless of item count).

`standard_50_100`/`legacy` modes and all their existing test cases are untouched — this is a purely
additive third mode, selected only via `thermal_insert_mode = "items"`.
