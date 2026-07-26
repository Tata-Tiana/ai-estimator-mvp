# Monolithic lintel formwork — derive plywood/timber from area (no direct spec value)

Added 2026-07-25 (Elena, via ТРЦ real-project review). ТРЦ КР2, p.11-12: monolithic lintel formwork is
given as horizontal + vertical area per floor (1-й этаж: 0,5 м2 + 1,4 м2; 2-й этаж: 0,45 м2 + 3,25 м2),
but the calculator's target fields expected a ready plywood sheet count and timber volume — neither
exists in the PDF.

Elena's rule: "Есть перемычки монолитные, они с опалубкой. У нас так же есть площадь опалубки, делим на
лист площадь листа фанеры 2,3. Пиломатериалы берем площадь опалубки и умножаем на толщину доски 0,05. И
получаем кубы. По аналогии с балками." — same method already used for beam/slab formwork elsewhere in
this pipeline (`foundation_slab_calculator.py`/`floor_slab_1_calculator.py`): sheets = ceil(total area /
sheet area), timber volume = total area × board thickness.

This case: `floor_1_lintel_formwork_horizontal_area_m2=0.5`, `floor_1_lintel_formwork_vertical_area_m2=1.4`
(total 1.9 m2) and `floor_2_lintel_formwork_horizontal_area_m2=0.45`,
`floor_2_lintel_formwork_vertical_area_m2=3.25` (total 3.7 m2), using the defaults
`lintel_formwork_plywood_sheet_area_m2=2.3` and `lintel_formwork_board_thickness_m=0.05`. Confirms:
- floor 1: 1.9 / 2.3 = 0.826 → ceil → 1 sheet; 1.9 × 0.05 = 0.095 m3 timber;
- floor 2: 3.7 / 2.3 = 1.609 → ceil → 2 sheets; 3.7 × 0.05 = 0.185 m3 timber.

**Updated same day (2026-07-25):** the direct-value fields (`floor_N_lintel_formwork_plywood_qty`/
`floor_N_lintel_formwork_timber_volume_m3`) were REMOVED entirely, not kept as an alternative path.
Checked real PDFs across АРК/ТРЦ and confirmed lintel formwork is never given as a ready sheet
count/m3 in any real project — area-from-PDF is the only real path, so
`calculate_monolithic_lintel_block()` now always derives plywood/timber from
`formwork_horizontal_area_m2`/`formwork_vertical_area_m2`, no direct-quantity alternative and no
mutual-exclusion check needed anymore. See [[lintel_monolithic_formwork_from_area_shipped]] and
`test_lintel_floor_split_ublock_and_monolithic` (updated the same day to use area inputs instead of the
removed direct fields).

Note: the insulation-length part of the same original finding (2,8/3,25 п.м taken as candidates from
"Общая длина ж/б перемычек" rows, since no dedicated insulation-length row exists) is a SEPARATE,
still-open question — Elena did not address it in this message, only the formwork plywood/timber part.
Do not conflate the two; see `ARK_TRC_USV_WALL_ROOF_LINTEL_FINDINGS_PLAN.md` section 11.7.
