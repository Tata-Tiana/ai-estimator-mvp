Regression case added 2026-07-30. Same base geometry as `test_floor_slab_1_no_beams`, but
`manual_lines.rebar_metal_delivery_trucks = 2` — verifies that the `rebar_metal_delivery` estimate
line (dead in production before this change, since `metal_delivery_calc_method=section_output_only`
never populated it) now actually charges money when the box-calculator assigns this section a
non-zero truck count. See `rebar_crane_manual_and_box_delivery_final` memory / plan section 51.
