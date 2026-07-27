# Negative test: коллизия auto-generated line_code в main_wall_rebar_items

Этот кейс намеренно содержит две строки `main_wall_rebar_items` с одинаковыми
`floor`/`component`/`steel_class`/`diameter_mm` и без явного `code` — симулирует реальный риск,
найденный 2026-07-26 (план, раздел 22) при разборе "подоконного армирования": если модель кладёт
подоконное армирование той же комбинацией floor+component+диаметр, что и основная комбинированная
строка, обе строки получают одинаковый авто-сгенерированный `line_code`, и вторая тихо перезаписывает
контрольные суммы первой в словаре `controls` (`main_wall_rebar_base_length_m`/`order_length_m`/
`delivery_weight_kg`) — сами ценовые строки (`rebar_lines`) при этом не теряются, деньги не портятся,
портятся только контрольные/отладочные числа.

До 2026-07-27 это было прикрыто только промптом (инструкция ставить уникальный `code` при коллизии,
`chat_extraction_poc/data`). Пользователь попросила защитить это и в коде — теперь
`calculate_main_wall_reinforcement()` (и по аналогии `calculate_lintel_rebar()`, тот же паттерн)
явно падает с `ValueError` при коллизии `line_code`, вместо тихой перезаписи.

Ожидаемое поведение: калькулятор должен упасть с ошибкой:

```text
main_wall_rebar_items: duplicate line_code 'load_bearing_walls_floor_1_rebar_a500_d10' (floor=1, component=load_bearing_walls, steel_class=A500, diameter_mm=10) — two rows resolve to the same auto-generated code and would silently overwrite each other's control totals. Set an explicit unique `code` on at least one of the colliding rows (e.g. a '_subwindow' suffix).
```
