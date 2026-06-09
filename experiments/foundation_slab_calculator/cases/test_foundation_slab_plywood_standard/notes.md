# Test case: plywood production standard

Этот кейс проверяет новый production-стандарт Елены по фанере для опалубки фундаментной плиты.

## Что проверяется

- Площадь опалубки приходит готовым значением из спецификации: `slab_side_formwork_area_m2`.
- Фанера считается от площади опалубки.
- Размер листа фанеры: `1.52 x 1.52 м`.
- Запас на фанеру фундаментной плиты: `5%`.
- Количество листов округляется вверх до целого.

Формула:

```text
plywood_sheet_area_m2 = 1.52 * 1.52
plywood_sheets = ceil(slab_side_formwork_area_m2 * 1.05 / plywood_sheet_area_m2)
```

Контроль для текущего кейса:

```text
slab_side_formwork_area_m2 = 24.3
plywood_sheet_area_m2 = 2.3104
plywood_raw_sheets = 24.3 * 1.05 / 2.3104 = 11.0435
plywood_sheets = 12
```

## Важно

`plywood_calc_method`, размер листа и запас являются системными настройками, а не ручными полями Елены.

Legacy-метод `working_area = 2.25 м2` сохранён только для старого `test_foundation_slab`.

No Excel cell references.
