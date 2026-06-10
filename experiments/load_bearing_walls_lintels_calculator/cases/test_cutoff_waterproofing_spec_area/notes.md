# Test: отсечная гидроизоляция готовой площадью из спецификации

Этот кейс проверяет production-стандарт для раздела несущих стен:

```text
cutoff_waterproofing_calc_method = "spec_area"
cutoff_waterproofing_area_m2 = cutoff_waterproofing_load_bearing_walls_area_m2
```

Площадь под перегородки в этот раздел не включается. Для неё должен быть отдельный параметр будущего раздела перегородок:

```text
cutoff_waterproofing_partitions_area_m2
```

Старые массивы длин стен 400/250 мм и толщины стен в этом кейсе не используются.
