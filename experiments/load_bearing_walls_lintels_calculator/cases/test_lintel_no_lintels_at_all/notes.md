# No lintels at all, on any floor

Added 2026-07-15. Confirms the user's explicit requirement: "перемычки могут быть или
нет, поэтому ни в один этаж этот блок не зашивается жёстко" — including floor 1, which
before this change had `lintel_total_length_m`/`lintel_concrete_spec_volume_m3` as
`required: true` and would raise a `ValueError` if absent.

`lintel_total_length_m` and `lintel_concrete_spec_volume_m3` are both `null`; no
`floor_2_*` or `floor_1_lintel_monolithic_*` fields are set either. Confirms:
- the calculator no longer raises (previously this input would have failed validation);
- every lintel-specific estimate line (U-block cutting, concreting work, concrete
  material/delivery/lifting, and all `floor_2_*`/`floor_1_lintel_monolithic_*`/
  `floor_2_lintel_monolithic_*` lines) is absent from `estimate_lines`;
- `lintel_rebar_frame_assembly` (a pre-existing zero/aggregating structural row, not new)
  is the only lintel-related line still present, at quantity 0 — unchanged prior
  behavior, not a regression.
