# Vent Chimney Spec Volume Thickness

Production-кейс для обкладки вентканалов без legacy-сегментов.

В production объём кладки вентканалов берётся из спецификации:
`vent_chimney_gas_block_spec_volume_m3 = 1.72`.

Площадь работ считается через постоянную толщину блока 150 мм:
`vent_chimney_cladding_area_m2 = 1.72 / 0.15 = 11.4666666667`.

Legacy-поля `vent_chimney_segment_lengths_m`, `vent_chimney_rows` и `block_height_m` в этом кейсе не передаются.
