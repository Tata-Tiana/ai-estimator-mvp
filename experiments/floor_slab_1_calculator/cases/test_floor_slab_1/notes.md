# Notes: test_floor_slab_1

Кейс относится к проекту `horoshevka_14`.

Раздел сметы:

```text
Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 1-го этажа на отм. +3.480 (180 мм) с балками
```

## Источники и статус

- Правила и числа взяты из текущего разбора раздела с Еленой.
- Дополнительная таблица Елены по балкам используется как источник размеров Б-1, Б-2, Б-3.
- `validated_with_elena = true`.
- `confidence = high`.

## Важные ручные/спорные места

- Ставка комплекта опалубки:
  - этот кейс использует legacy-режим `rates.formwork_rate_calc_method = legacy_supplier_quote_context`;
  - `rates.formwork_supplier_quote_total` и `rates.slab_2_formwork_area_for_rate_context_m2` оставлены только для сверки справочной средней ставки ЮСВ;
  - в production калькулятор плиты 1-го этажа использует прямую ставку `rates.formwork_rate_per_m2` и не зависит от площади плиты 2-го этажа.
- Доставка арматуры/металла:
  - этот кейс использует legacy-режим `rates.metal_delivery_calc_method = legacy_slab1_slab2_context`;
  - `rates.floor_slab_2_rebar_weight_for_delivery_context_kg` оставлен только для повторения старого контекста ЮСВ;
  - в production калькулятор плиты 1-го этажа отдаёт `section_rebar_delivery_weight_kg`, а количество машин считается на уровне `box_calculator`.
- Арматура плиты:
  - этот кейс использует legacy-режим `rebar_calc_method = legacy_weight_parts`;
  - арматура приходит весом в кг через `source_weight_kg` / `source_weight_parts_kg`;
  - калькулятор переводит вес в м.п. через `kg_per_meter`, добавляет запас и округляет до хлыстов;
  - в production арматура должна приходить из спецификации сразу в м.п. через `rebar_items[*].spec_length_m`.
- Утепление плиты:
  - этот кейс использует legacy-режим `insulation.insulation_calc_method = legacy_fixed_edge_length`;
  - переименовано 2026-07-26 (было `legacy_usv_geometry`) — формула никогда не читала геометрию проекта, всегда возвращала одну и ту же длину торца (84,8 м) вне зависимости от входных данных; переименование и явная константа убирают реальные размеры конкретного проекта из кода калькулятора, поведение побайтово не изменилось;
  - в production рабочие длины/площади и чистый объём ЭППС должны приходить из спецификации через `insulation.slab_outer_edge_eps_work_length_m`, `insulation.slab_edge_eps_material_area_m2`, `insulation.bottom_slab_eps_work_area_m2`, `insulation.total_eps_volume_from_spec_m3`.
- Площади опалубки:
  - этот кейс использует legacy-режим `formwork_areas_calc_method = legacy_calculated_from_geometry`;
  - основная площадь опалубки восстанавливается через объём бетона и толщину плиты;
  - площадь торца восстанавливается через периметр и высоту;
  - площадь опалубки балок восстанавливается из `beams.items`;
  - в production эти три площади должны приходить готовыми значениями из спецификации: `main_formwork_area_m2`, `edge_formwork_area_m2`, `beams_formwork_area_m2`.
- Доставка/вывоз опалубки:
  - этот кейс использует production-режим `rates.formwork_delivery_calc_method = area_threshold`;
  - до `180 м2` включительно: 1 привоз + 1 вывоз = 2 машины;
  - более `180 м2`: 2 привоза + 2 вывоза = 4 машины;
  - `manual_lines.formwork_delivery_trucks_override` оставлен только как optional override для исключений и в этом режиме не используется.
- Третья смена автокрана пока не выводится формулой и должна проходить только как `manual_review` / override.
- Бетононасос 32 м + гаситель — fixed/manual line, сейчас 1 смена.
- Доставка металла в этом экспериментальном калькуляторе считается для совпадения с Excel.
- В будущем `box_calculator` доставка металла должна считаться один раз по общему весу металла коробки, чтобы не задвоить доставку.
- Технический надзор — fixed `5000`.
- Логистика `1%` и расходные материалы/амортизация инструмента `3%` считаются от raw-базы до overheads.
- Номера строк Excel не используются как идентификаторы. Основной идентификатор — `code` + название строки.

## Raw/display

Excel часто отображает округлённое количество, но сумму считает от raw. Поэтому калькулятор хранит отдельно:

- `quantity_raw`;
- `quantity_display`;
- `material_total_raw`;
- `material_total`;
- `work_total_raw`;
- `work_total`;
- `line_total_raw`;
- `line_total`.
