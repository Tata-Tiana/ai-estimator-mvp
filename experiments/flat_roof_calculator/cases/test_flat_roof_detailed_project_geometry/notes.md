# test_flat_roof_detailed_project_geometry

Production-кейс для геометрии плоской кровли.

В этом режиме `roof_geometry_calc_method = "detailed_project_geometry"`:

- `roof_area_total_m2` не передается как обязательный input;
- `parapet_and_abutment_total_length_m` не передается как обязательный input;
- общая площадь кровли считается как `roof_area_level_1_m2 + roof_area_level_2_m2`;
- общая длина примыканий считается как сумма парапетов и примыканий вентстен по двум уровням.

Старый locked-кейс `test_flat_roof_usv` остается в режиме `legacy_totals`.
