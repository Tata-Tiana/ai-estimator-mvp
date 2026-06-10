# Notes: test_floor_slab_1_insulation_spec_quantities

Production-кейс проверяет утепление плиты перекрытия 1-го этажа по готовым рабочим количествам и чистому объёму ЭППС из спецификации.

## Проверяемая методика

- `insulation.insulation_calc_method = spec_work_quantities`.
- Длина утепления наружного торца плиты приходит как `insulation.slab_outer_edge_eps_work_length_m`.
- Площадь материала наружного торца плиты приходит как `insulation.slab_edge_eps_material_area_m2`.
- Площадь утепления низа плиты приходит как `insulation.bottom_slab_eps_work_area_m2`.
- Чистый объём ЭППС приходит как `insulation.total_eps_volume_from_spec_m3`.
- Длина и площадь утепления балок считаются из `beams.items[*].length_m`, `height_m`, `count`.

## Контрольные числа

```text
beams_eps_work_length_m = 7 + 7.2 + 9 = 23.2
edge_beam_eps_work_length_m = 84.8 + 23.2 = 108.0

beams_eps_material_area_m2 = 7 * 0.25 + 7.2 * 0.68 + 9 * 0.43 = 10.516
edge_and_beam_eps_material_area_m2 = 15.264 + 10.516 = 25.78

edge_and_beam_eps_volume_m3 = 25.78 * 0.1 = 2.578
bottom_slab_eps_volume_m3 = 51.92 * 0.1 = 5.192
calculated_clean_eps_volume_m3 = 7.77

required_eps_volume_m3_raw = 7.77 * 1.05 = 8.1585
eps_packs_ordered = ceil(8.1585 / 0.2773) = 30
order_eps_volume_m3_raw = 30 * 0.2773 = 8.319
```

## Важно

Площадь материала торца плиты не выводится из длины и толщины ЭППС. Для production она приходит отдельным значением из спецификации, чтобы не зашивать геометрию ЮСВ в универсальный калькулятор.
