# Beam bottom (horizontal) formwork area feeds plywood/timber

Added 2026-07-26 (Elena, via ТРЦ real-project review). Real ТРЦ PDF (КР2, p.31/41) gives three
distinct formwork-area line items for floor_slab_1:
- horizontal under the slab (97,11 м2) — already handled as `main_formwork_area_m2`;
- horizontal under the beam (1,26 м2) — previously had no field at all, silently uncounted;
- vertical, slab edge + beam combined (36,60 м2) — already handled as
  `edge_and_beam_formwork_area_combined_m2` (shipped 2026-07-21).

Elena: "Площадь вертикальная опалубки указана общая (торец плиты и балок). Суммировать с нижней
площадью под балкой. 36.6 плюс 1,26 (горизонт площадь под балки) — это будет расчет фанеры и
пиломатериалов." — the two SHOULD be summed for plywood/timber; the slab's own horizontal area
(97,11) stays out of this sum (it already feeds `non_multiple_area` separately via a different
coefficient path).

This case reuses `test_floor_slab_1_edge_and_beam_formwork_combined`'s inputs, adding
`beams_bottom_formwork_area_m2=1.26`. Confirms:
- `edge_beam_formwork_area_for_materials_m2` = 51.592 + 1.26 = 52.852 (drives plywood/timber);
- `edge_and_beam_plywood_sheets_raw` increases from 22.431304 (old case, without the beam bottom
  area) to 22.97913;
- `base_timber_volume_m3` increases from 2.5796 to 2.6426;
- `edge_beam_formwork_installation_control`'s quantity = 52.852 (matches
  `edge_beam_formwork_area_for_materials_m2`), same as the material.

**Correction, 2026-07-26 (real project case, checked against the real costed smeta directly):** the
original version of this case had the installation-control line stay at 51.592 (unchanged), based on
a reading of Elena's quote as "beam bottom area affects material only, not the installation work
quantity." Checked a different real project's own smeta line for this exact work
("Монтаж опалубки из доски 50 мм и фанеры для отбортовки плиты и устройства балок") — its quantity
matches vertical-slab-edge + vertical-beam + beam-bottom summed together (not vertical-only), and the
same three-line naming/structure (this combined line, a separate slab-bottom line, and the matching
insulation pair) is identical across all three real projects reviewed this session. So the work
quantity must also include the beam bottom area, same as material — corrected here.

Additive: `beams_bottom_formwork_area_m2` defaults to 0 when absent — every other existing case is
byte-identical (confirmed via full regression, 11/11 other cases unaffected).
