# test_floor_slab_1_spec_formwork_areas

Production-кейс для опалубочных площадей плиты перекрытия 1-го этажа.

Проверяет режим `spec_formwork_areas`, где спецификация дает три готовые площади:

- `main_formwork_area_m2` — площадь опалубки под плиту;
- `edge_formwork_area_m2` — площадь торцевой опалубки плиты;
- `beams_formwork_area_m2` — площадь опалубки балок.

Старые расчетные формулы через бетон, толщину, периметр и `beams.items` остаются только контрольными
и не являются source of truth для production-опалубки.
