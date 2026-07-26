# Schiedel channels — 3x/4x product mix (different real project than the 1x/2x case)

Added 2026-07-26, alongside `test_schiedel_vent_channels_trc` (see that case's notes.md for the full
finding writeup and rule list — this case exists specifically to prove the dynamic `product_type` list
handles a completely different subset of types with zero code changes).

Real project smeta: masonry work 5.43 м.п.; materials "Вентиляционный блок SCHIEDEL VENT, 4 ход,
наружный размер 52/25 см... — 11 шт" and "3 ход, наружный размер 52/25 см... — 7 шт". Notably this
project's own PDF drawings never name the Schiedel brand explicitly (an earlier extraction pass assumed
this meant a brandless/generic system) — but the real delivered smeta bills these blocks as Schiedel
regardless, confirming Elena's rule that the brand defaults to Schiedel everywhere, PDF silence
included.

Confirms: exactly two material lines appear (`schiedel_vent_channel_3x`, `schiedel_vent_channel_4x`) —
1x/2x/cvent absent since unused, same mechanism as the 1x/2x case, just a different subset selected
purely by which `product_type` values appear in `schiedel_channel_items`.
