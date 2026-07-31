Regression case added 2026-07-30. Same base geometry as `test_floor_slab_2_spec_formwork_area`, but
`rebar_metal_delivery_trucks = 1` — verifies the new `rebar_metal_delivery` estimate line (this
section had none before) actually charges money when the box-calculator assigns it a non-zero truck
count. See `rebar_crane_manual_and_box_delivery_final` memory / plan section 51.
