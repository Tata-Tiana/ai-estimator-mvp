# Negative test: редкая плотность без material_unit_price

Пара к `test_wall_block_items_rare_other_density` — то же самое floor_2 с `block_density: "D350"`,
но без `material_unit_price`. Проверяет, что калькулятор явно отказывается считать редкий блок,
если для него не дана цена, вместо того чтобы молча взять 0 или упасть на другом, менее понятном
шаге.

Ожидаемое поведение: калькулятор должен упасть с ошибкой:

```text
wall_block_items block_density='D350' is not one of ['D400', 'D500'] for wall_role='floor_2' (context='...') — supply an explicit material_unit_price on this row for a rare non-standard block, or use D400/D500.
```
