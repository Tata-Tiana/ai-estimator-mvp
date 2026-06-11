# test_floor_slab_2_spec_formwork_area

Production-кейс для площади опалубки плиты перекрытия 2-го этажа.

Проверяет режим `spec_formwork_area`:

- `main_formwork_area_m2` берется готовым значением из спецификации;
- `slab_edge_perimeter_m` берется как проектная длина утепляемого торца;
- `slab_length_m`, `slab_width_m`, `slab_area_m2` не обязательны и в этом кейсе не передаются;
- строка `formwork_rental_set` считает количество от `main_formwork_area_m2`.
