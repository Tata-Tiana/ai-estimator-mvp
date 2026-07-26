# Schiedel channels — dynamic product-type list, module count not shaft count

Added 2026-07-26 (Elena, via ТРЦ real-project review). Full rewrite of the calculator, replacing the
old prototype entirely (previous single test case, `test_schiedel_vent_channels_usv`, was deleted — it
was built on numbers that don't match either project's real delivered smeta and used a design Elena has
now explicitly rejected).

Real ТРЦ PDF (КР2, p.39-40, read directly): plan shows two shaft nodes В-1/В-2. Spec table:
"Вентиляционный канал 1х,20/25 см Schiedel — 21 шт", "2х,36/25 см Schiedel — 15 шт",
"высота вентканалов общая 4,9+4,9=9,8 п.м". The old calculator only understood 2x/3x and separately
tracked shaft height/count (`vent_channel_1_height_m`/`vent_channel_2_height_m`/`vent_channel_2_count`)
for an unused diagnostic cross-check — neither matches this project (1x doesn't exist in the old schema
at all) nor Elena's actual rule.

Elena's rules, all confirmed against real PDF/smeta data:
1. "Не надо считать шахты, это не важно" — shaft count/height tracking removed entirely, no
   replacement, no diagnostic either.
2. "Нужно считать количество модулей разных вентиляционных каналов... в прайсе это всегда модули" —
   the only quantity that matters is module/product count per type, via `schiedel_channel_items[]`
   (list of `{product_type, quantity_pcs}`), replacing the hardcoded `schiedel_vent_channel_2x_count`/
   `_3x_count` scalar pair. Product types: 1x, 2x, 3x, 4x, and the rare cvent.
3. "Всегда используется Шидель, даже если в проекте не указано название, во всех проектах" — checked
   the real delivered АРК smeta directly: it bills Schiedel-branded blocks ("SCHIEDEL VENT, 4 ход...",
   "3 ход...") even though this project's earlier extraction assumed no-brand — this reverses the old
   `vent_channels_universalization` memory's "ARK is brandless" claim. No separate no-brand system type
   needed; brand is always Schiedel.
4. "И работа по погонным метрам и всё" — masonry work stays the one payable quantity, driven solely by
   `schiedel_masonry_total_length_m`, unaffected by which/how many product types exist.
5. "Если вентканалы не указаны в штуках... ставить ручной ввод, сметчица сама посчитает" — no special
   calculator handling needed for this; `schiedel_channel_items[]` simply gets filled in manually by the
   reviewer when the PDF doesn't give a ready piece count, same as any other manually-entered field in
   this pipeline.

This case: real ТРЦ quantities (1x=21, 2x=15, masonry=9.8 м.п.). Confirms:
- exactly two material lines appear (`schiedel_vent_channel_1x`, `schiedel_vent_channel_2x`) — 3x/4x/
  cvent are silently absent since their bucketed quantity is 0, no code branching needed per type;
- masonry work line unaffected by the product-type mix;
- `2x`/`3x` keep their pre-existing price codes (`schiedel_vent_channel_2x_36_25_item`/`_3x_52_25_item`,
  already real entries in the price registry); `1x`/`4x`/`cvent` get new codes
  (`schiedel_vent_channel_1x_item` etc.) since no registry entry existed for them before.

Also cleaned up (data hygiene): removed hardcoded real-project numbers that were baked directly into
the old calculator's code (control values "24", "8", "65.51515152", "28", "14.57575758", "6" and warning
text referencing them) — calculator.py must never contain real project data, only test cases may. See
`test_schiedel_vent_channels_ark` for the 3x/4x-only case (a different real project's product mix,
proving the dynamic list handles any subset of the five types without code changes).
