# Thermal inserts — combined installation length (no per-thickness split)

Added 2026-07-25 (Elena, via ТРЦ real-project review). Real ТРЦ PDF (КР-1_ТРЦ, p.20, read directly)
gives one combined installation length for the whole thermal-insert run — "Длина термовставок = 7,15
п.м" — with material split by thickness: "ЭППС 100мм (Термовставки) - 0,108м3",
"ЭППС 50мм (Термовставки) - 0,054м3". There is no separate length per thickness anywhere on the sheet.

Before this fix, `standard_50_100` mode unconditionally built two separate installation work lines
(`thermal_insert_50_installation` + `thermal_insert_100_installation`), each using its own length. If
the single 7,15 value were fed into both (as chat extraction had been doing, flagged `needs_review`),
the calculator would have charged the installation work twice — once per thickness — a real
double-billing risk, not just a data-quality nitpick.

Elena's decision: "Брать работу общей суммой" — one work line, one combined length, one price.
Material stays split by thickness exactly as before (no change there).

This case: `thermal_insert_combined_length_m=7.15` + `thermal_insert_combined_work_unit_price=100`,
with `thermal_insert_50_length_m`/`thermal_insert_100_length_m` both omitted. Confirms:
- exactly one work line (`thermal_insert_combined_installation`), quantity 7.15, no double-counting;
- material lines (`thermal_insert_50_material`, `thermal_insert_100_material`) unaffected, computed
  from the existing per-thickness spec quantities as before;
- validation rejects supplying both combined and split lengths at once (mutually exclusive).

Legacy split-length inputs (`test_foundation_slab_thermal_inserts_standard`) are untouched — this is a
purely additive alternative, selected only when `thermal_insert_combined_length_m` is provided.
