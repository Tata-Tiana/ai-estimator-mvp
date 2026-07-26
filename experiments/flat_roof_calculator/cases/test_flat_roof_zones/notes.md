# Roof zones — sum any number of zones by floor/type, including staircase roof

Added 2026-07-26 (Elena, via ТРЦ real-project review, part 13.1 of the roof findings). Real ТРЦ PDF
(КР2, p.21, read directly) splits roof area into 4 zones with no fit into the calculator's previous
`roof_area_level_1_m2`/`roof_area_level_2_m2` shape: 1эт(Тип1, Эксплуатируемая) 21,28 м2, 1эт(Тип2,
Неэксплуатируемая) 15,78 м2, 2эт(Тип2, Неэксплуатируемая) 75,975 м2, Кровля лестницы(Тип2,
Неэксплуатируемая) 18,04 м2 — plus matching per-zone parapet/wall-abutment lengths. The PDF happens to
also give a ready ИТОГО (131,075 м2 total, 91,135 м2 parapet total, 35,31 м2 wall-abutment total) which
this case uses as a cross-check input (`roof_area_total_m2`/`parapet_and_abutment_total_length_m`),
confirming the zones sum to exactly the same numbers (delta = 0 both ways).

Elena's rule: "Кровля лестницы идём в общую площадь кровли... для кровли правило суммировать все
найденные площади по этажам, по типам" — staircase roof is just another zone, no special-casing;
general principle is to sum whatever zones are found (this generalizes beyond just this one project,
which happens to also give a ready total — future projects without a ready total still need this).

This case: `roof_geometry_calc_method: "roof_zones"`, `roof_zones` = 4 items with `context`, `area_m2`,
`parapet_length_m`, and `wall_abutment_length_m` (staircase zone omits `wall_abutment_length_m` — the
PDF's wall-abutment row only lists 3 values, not 4, so the 4th zone genuinely has none, defaults to 0).
Confirms:
- `roof_area_total_m2` = 131.075 (sum of all 4 zone areas), matches the real PDF's own ИТОГО exactly;
- `parapet_and_abutment_total_length_m` = 126.445 (sum of all zone parapet+wall-abutment lengths, i.e.
  91.135 + 35.31), matches the real PDF's two ИТОГО rows summed;
- every downstream estimate line (vapor barrier, EPS, geotextile, PVC membrane, drains, etc.) derives
  correctly from these totals — full line-by-line regression captured in `expected.json`.

Additive: `roof_geometry_calc_method` gained a third option (`roof_zones`) alongside the existing
`legacy_totals` and `detailed_project_geometry` — neither existing method's behavior changed. Full
regression: 4/4 cases pass (both pre-existing cases untouched, 0 mismatches).

**Updated 2026-07-26 (13.2): membrane brand split by zone exploitability, also shipped.** Each zone now
also carries `operability` ("exploitable" for zone 1, "non_exploitable" for the other 3, matching the
PDF's own labels exactly). `calculate_roof_geometry()` sums exploitable vs non-exploitable area/length
separately (`exploitable_roof_area_m2`=21.28, `exploitable_parapet_and_abutment_length_m`=20.41,
non-exploitable = the remaining 109.795/106.035). The PVC membrane material now splits into two lines:
V-RP (`pvc_membrane_logicroof_vrp_1_5mm_gray`, sized from the non-exploitable area, 6 rolls) and V-GR
(`pvc_membrane_logicroof_vgr_1_5mm_gray`, sized from the exploitable area, 2 rolls, new
`pvc_membrane_vgr_roll_width_m`/`_roll_length_m`/`_unit_price_per_roll_display` rate fields — roll size
2.10×20 and price ≈53880 both grounded in the real delivered ТРЦ smeta's own V-GR line). Installation
work (`pvc_membrane_flat_installation`/`pvc_membrane_abutment_installation`) stays ONE combined line
regardless of brand — confirmed against the real smeta, which also bills membrane laying as a single
combined-area work line, not split by brand (same principle as combined masonry work despite split
D400/D500 material elsewhere in this pipeline).

Elena's rule: V-GR for a zone explicitly marked "эксплуатируемая"; V-RP for a zone with no operability
label at all, or explicitly "неэксплуатируемая". `operability` is optional per zone — omitting it
defaults to `"non_exploitable"`, so a project with no exploitable roof at all (every case before this
one) gets byte-identical behavior: `exploitable_roof_area_m2` stays 0, only the V-RP line appears, its
required area/rolls unchanged from before this fix.

Full regression: 4/4 cases pass, 0 mismatches (the two pre-existing legacy-mode cases needed only a
`quantity_source` text-string update, no numeric change, since their V-RP line now reads
"non-exploitable flat and abutment..." instead of "flat and abutment..." — still 100% of roof
area/length for them, just described precisely).
