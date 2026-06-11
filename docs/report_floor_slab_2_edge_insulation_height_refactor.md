# Отчет: высота утепления торца плиты 2-го этажа

Дата: 2026-06-11

Раздел: `Ж/Б монолитная плита перекрытия 2-го этажа`

## Что изменено

`edge_insulation_height_m` закреплен как production-параметр из спецификации:

```text
edge_insulation_height_m = 0.18
edge_insulation_height_source = "specification"
```

Старый warning о расхождении с названием раздела заменен на пояснение: `0.18 м` подтверждено
спецификацией, а `200 мм` в названии раздела считается ошибкой названия.

## Расчет

Расчет утепления торца не изменился:

```text
edge_insulation_area_m2 =
  slab_edge_perimeter_m * edge_insulation_height_m
```

Для ЮСВ:

```text
36.2 * 0.18 = 6.516 м2
```

Работа остается в погонных метрах:

```text
edge_insulation_work.quantity = slab_edge_perimeter_m = 36.2 м.п.
```

Материал ЭППС считается в м3:

```text
eps100_required_volume_without_waste_m3 =
  edge_insulation_area_m2 * eps100_thickness_m

6.516 * 0.1 = 0.6516 м3
```

Дальше сохраняется текущая логика:

- запас `eps_waste_coeff`;
- округление до упаковок через `eps100_pack_volume_m3`;
- расчет `foam_cans_ordered`.

## Статусы параметров

AUTO_PROJECT:

- `edge_insulation_height_m`;
- `slab_edge_perimeter_m`.

AUTO_CALCULATED:

- `edge_insulation_area_m2`;
- `eps100_required_volume_without_waste_m3`;
- `eps100_required_volume_with_waste_m3`;
- `eps100_packs_ordered`;
- `eps100_order_volume_m3`;
- `foam_cans_ordered`.

DEFAULT_VALUE / MATERIAL_SETTING:

- `eps100_thickness_m`;
- `eps_waste_coeff`;
- `eps100_pack_volume_m3`;
- `foam_coverage_area_per_can_m2`;
- `foam_min_cans`.

## Проверки

Проверяются неизменные ключевые значения:

- `edge_insulation_height_m = 0.18`;
- `edge_insulation_area_m2 = 6.516`;
- `eps100_required_volume_without_waste_m3 = 0.6516`;
- `edge_insulation_work.quantity = 36.2`.

## TODO

- обновить `section_schema.py`;
- обновить `reviewed_parameters.xlsx`;
- научить parser брать `edge_insulation_height_m` из спецификации;
- в review form показывать высоту торца как контрольный production-параметр.
