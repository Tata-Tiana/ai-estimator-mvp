# test_schiedel_channel_linear_meters

Covers the case where a project's spec gives Schiedel vent-channel rows in running meters
instead of a ready piece count.

Elena, 2026-09-10: Schiedel VENT modules are always 33 cm tall (every channel type, no
exception including CVENT), so `pieces = ceil(linear_length_m / 0.33)`, rounded up per spec row.

Input uses the real ARK figures (`3x` = 2.0 м.пог, `4x` = 3.4 м.пог). Expected piece counts
(7 and 11) match ARK's real delivered smeta exactly - the same numbers ARK's own
`test_schiedel_vent_channels_ark` case supplies directly via `quantity_pcs`. Only the
`quantity_source` text differs (it records the conversion). All money totals are identical to
the ARK case since the rates and resulting piece counts are the same.
