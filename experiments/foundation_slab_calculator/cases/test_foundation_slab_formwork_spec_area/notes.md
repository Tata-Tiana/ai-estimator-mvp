# Test Foundation Slab Formwork Spec Area Notes

Этот кейс проверяет новый стандарт Елены для площади опалубки бортов фундаментной плиты.

## Новый стандарт

Площадь опалубки приходит готовым значением из спецификации:

```text
formwork_area_m2 = slab_side_formwork_area_m2
```

В этом кейсе:

```text
slab_side_formwork_area_m2 = 24.3
```

## Что не используется

В новом standard-case не используются как рабочие входы:

- `slab_formwork_perimeter_m`;
- `slab_edge_height_m`;
- `slab_edge_height_strategy`.

Старая формула `formwork_area_m2 = slab_formwork_perimeter_m * slab_edge_height_m` остаётся только в legacy-кейсе `test_foundation_slab`.

## Что проверяется

- `formwork_installation.quantity = 24.3`;
- `formwork_dismantling.quantity = 24.3`;
- `plywood_sheets = ceil(24.3 / 2.25) = 11`;
- `timber_raw_volume_m3 = 24.3 * 0.05 = 1.215`.

## Важно

Этот кейс использует также новый стандарт термовставок 50/100 мм, чтобы не требовать legacy-поля опалубки и высоты борта.
