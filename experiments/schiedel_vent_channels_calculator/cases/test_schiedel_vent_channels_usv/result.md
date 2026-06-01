# Расчётный отчёт: ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel

AI не используется для расчёта. Калькулятор считает только серую внутреннюю себестоимость.
Клиентская часть и коммерческие коэффициенты вне текущего scope.

## Исходные параметры раздела

- project_name: `test_schiedel_vent_channels_usv`
- schiedel_masonry_total_length_m: `15.82`
- schiedel_vent_channel_2x_count: `24`
- schiedel_vent_channel_3x_count: `8`
- schiedel_delivery_trips: `1`

## Важные правила

- Кладка считается от raw `15.82 мп`, не от отображаемых `16 мп`.
- Количества `24 шт` и `8 шт` по материалам Schiedel являются ручными/спецификационными значениями.
- Контрольные правые числа сохранены как справочные и не используются для quantity.
- Расходные материалы считаются как `3%` от прямой базы `114456`.
- Последние 4 строки являются нулевыми строками структуры Excel.

## Построчный расчёт

### 1. Кладка вентканалов Schiedel

- Код: `schiedel_masonry_work`
- Тип строки: `work`
- Ед. изм.: `мп`
- Количество raw/display: `15.82` / `15.82`
- Источник количества: `schiedel_masonry_total_length_m`
- price_code: `schiedel_masonry_work_m`

Формула и контроль:
- control_length_m: `15.82`
- control_formula: `vent_channel_1_height_m + vent_channel_2_height_m * vent_channel_2_count`
- work_total: `schiedel_masonry_total_length_m * schiedel_masonry_work_rate_per_m`

Итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `79100` / `79 100`
- Итого raw/display: `79100` / `79 100`
- Примечание: Серая сумма считается от raw 15.82 мп.
- Примечание: Не считать от старого отображаемого количества 16 мп.

### 2. Вентиляционный канал 2х,36/25 см Schiedel

- Код: `schiedel_vent_channel_2x_36_25`
- Тип строки: `materials`
- Ед. изм.: `шт`
- Количество raw/display: `24` / `24`
- Источник количества: `manual_from_schiedel_specification_or_elena_table`
- price_code: `schiedel_vent_channel_2x_36_25_item`

Формула и контроль:
- quantity: `manual/specification input`
- material_total: `schiedel_vent_channel_2x_count * schiedel_vent_channel_2x_unit_price`
- control_blocks_raw: `65.51515152`
- secondary_control_value: `28`

Итог:
- Материалы raw/display: `12096` / `12 096`
- Работы raw/display: `0` / `0`
- Итого raw/display: `12096` / `12 096`
- Примечание: Количество 24 не выводится автоматически из контрольных правых значений.
- Примечание: Контрольные числа сохранены справочно и не участвуют в quantity.

### 3. Вентиляционный канал 3х,52/25 см Schiedel

- Код: `schiedel_vent_channel_3x_52_25`
- Тип строки: `materials`
- Ед. изм.: `шт`
- Количество raw/display: `8` / `8`
- Источник количества: `manual_from_schiedel_specification_or_elena_table`
- price_code: `schiedel_vent_channel_3x_52_25_item`

Формула и контроль:
- quantity: `manual/specification input`
- material_total: `schiedel_vent_channel_3x_count * schiedel_vent_channel_3x_unit_price`
- control_blocks_raw: `14.57575758`
- secondary_control_value: `6`

Итог:
- Материалы raw/display: `5760` / `5 760`
- Работы raw/display: `0` / `0`
- Итого raw/display: `5760` / `5 760`
- Примечание: Количество 8 не выводится автоматически из контрольных правых значений.
- Примечание: Контрольные числа сохранены справочно и не участвуют в quantity.

### 4. Доставка вентканалов

- Код: `schiedel_delivery`
- Тип строки: `material_and_work`
- Ед. изм.: `маш`
- Количество raw/display: `1` / `1`
- Источник количества: `manual_input`
- price_code: `schiedel_delivery_truck`

Формула и контроль:
- material_total: `schiedel_delivery_trips * schiedel_delivery_truck_price`
- work_total: `schiedel_delivery_trips * schiedel_delivery_work_price`

Итог:
- Материалы raw/display: `15000` / `15 000`
- Работы raw/display: `2500` / `2 500`
- Итого raw/display: `17500` / `17 500`

### 5. Расходные материалы, амортизация инструмента

- Код: `schiedel_consumables_tool_depreciation`
- Тип строки: `percentage_addon`
- Ед. изм.: `комплект`
- Количество raw/display: `1` / `1`
- Источник количества: `direct_cost_base_before_consumables * consumables_rate`

Формула и контроль:
- direct_cost_base_before_consumables: `114456`
- consumables_rate: `0.03`
- material_total_raw: `3433.68`

Итог:
- Материалы raw/display: `3433.68` / `3 434`
- Работы raw/display: `0` / `0`
- Итого raw/display: `3433.68` / `3 434`
- Примечание: Расходные материалы считаются как 3% от прямой базы 114456.

### 6. Технический надзор

- Код: `technical_supervision_zero`
- Тип строки: `zero_excel_structure_line`
- Ед. изм.: `-`
- Количество raw/display: `1` / `1`
- Источник количества: `excel_structure_line`

Итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `0` / `0`
- Итого raw/display: `0` / `0`
- Примечание: Строка сохранена для структуры Excel.
- Примечание: В текущем scope серая внутренняя себестоимость равна 0.

### 7. Заготовительно-складские расходы

- Код: `procurement_storage_zero`
- Тип строки: `zero_excel_structure_line`
- Ед. изм.: `-`
- Количество raw/display: `1` / `1`
- Источник количества: `excel_structure_line`

Итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `0` / `0`
- Итого raw/display: `0` / `0`
- Примечание: Строка сохранена для структуры Excel.
- Примечание: В текущем scope серая внутренняя себестоимость равна 0.

### 8. Накладные и общехозяйственные расходы

- Код: `overhead_zero`
- Тип строки: `zero_excel_structure_line`
- Ед. изм.: `-`
- Количество raw/display: `1` / `1`
- Источник количества: `excel_structure_line`

Итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `0` / `0`
- Итого raw/display: `0` / `0`
- Примечание: Строка сохранена для структуры Excel.
- Примечание: В текущем scope серая внутренняя себестоимость равна 0.

### 9. Сметная прибыль

- Код: `profit_zero`
- Тип строки: `zero_excel_structure_line`
- Ед. изм.: `-`
- Количество raw/display: `1` / `1`
- Источник количества: `excel_structure_line`

Итог:
- Материалы raw/display: `0` / `0`
- Работы raw/display: `0` / `0`
- Итого raw/display: `0` / `0`
- Примечание: Строка сохранена для структуры Excel.
- Примечание: В текущем scope серая внутренняя себестоимость равна 0.

## Warnings

- Количество материалов Schiedel 24 и 8 требует подтверждения у Елены/по спецификации.
- Количество доставки является ручным параметром.
- Клиентская часть не считается.

## Итоги

- Материалы: `36 290`
- Работы: `81 600`
- Всего: `117 890`
- internal_materials_total_raw: `36289.68`
- internal_works_total_raw: `81600`
- internal_section_total_raw: `117889.68`

## Проверка

- status: `ok`
- ok: `138`
- mismatch: `0`

| scope | code | field | expected | actual | status |
| --- | --- | --- | ---: | ---: | --- |
| totals | `internal_materials_total_raw` | `internal_materials_total_raw` | 36289.68 | 36289.68 | ok |
| totals | `internal_materials_total` | `internal_materials_total` | 36290 | 36290 | ok |
| totals | `internal_works_total_raw` | `internal_works_total_raw` | 81600 | 81600 | ok |
| totals | `internal_works_total` | `internal_works_total` | 81600 | 81600 | ok |
| totals | `internal_section_total_raw` | `internal_section_total_raw` | 117889.68 | 117889.68 | ok |
| totals | `internal_section_total` | `internal_section_total` | 117890 | 117890 | ok |
| totals | `sum_of_displayed_line_material_totals` | `sum_of_displayed_line_material_totals` | 36290 | 36290 | ok |
| totals | `sum_of_displayed_line_work_totals` | `sum_of_displayed_line_work_totals` | 81600 | 81600 | ok |
| totals | `sum_of_displayed_line_totals` | `sum_of_displayed_line_totals` | 117890 | 117890 | ok |
| estimate_lines | `schiedel_masonry_work` | `name` | Кладка вентканалов Schiedel | Кладка вентканалов Schiedel | ok |
| estimate_lines | `schiedel_masonry_work` | `unit` | мп | мп | ok |
| estimate_lines | `schiedel_masonry_work` | `line_type` | work | work | ok |
| estimate_lines | `schiedel_masonry_work` | `quantity_raw` | 15.82 | 15.82 | ok |
| estimate_lines | `schiedel_masonry_work` | `quantity_display` | 15.82 | 15.82 | ok |
| estimate_lines | `schiedel_masonry_work` | `quantity_source` | schiedel_masonry_total_length_m | schiedel_masonry_total_length_m | ok |
| estimate_lines | `schiedel_masonry_work` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `schiedel_masonry_work` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `schiedel_masonry_work` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `schiedel_masonry_work` | `internal_cost.work_unit_price` | 5000 | 5000 | ok |
| estimate_lines | `schiedel_masonry_work` | `internal_cost.work_total_raw` | 79100 | 79100 | ok |
| estimate_lines | `schiedel_masonry_work` | `internal_cost.work_total` | 79100 | 79100 | ok |
| estimate_lines | `schiedel_masonry_work` | `internal_cost.line_total_raw` | 79100 | 79100 | ok |
| estimate_lines | `schiedel_masonry_work` | `internal_cost.line_total` | 79100 | 79100 | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `name` | Вентиляционный канал 2х,36/25 см Schiedel | Вентиляционный канал 2х,36/25 см Schiedel | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `unit` | шт | шт | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `line_type` | materials | materials | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `quantity_raw` | 24 | 24 | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `quantity_display` | 24 | 24 | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `quantity_source` | manual_from_schiedel_specification_or_elena_table | manual_from_schiedel_specification_or_elena_table | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `price_code` | schiedel_vent_channel_2x_36_25_item | schiedel_vent_channel_2x_36_25_item | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `internal_cost.material_unit_price` | 504 | 504 | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `internal_cost.material_total_raw` | 12096 | 12096 | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `internal_cost.material_total` | 12096 | 12096 | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `internal_cost.line_total_raw` | 12096 | 12096 | ok |
| estimate_lines | `schiedel_vent_channel_2x_36_25` | `internal_cost.line_total` | 12096 | 12096 | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `name` | Вентиляционный канал 3х,52/25 см Schiedel | Вентиляционный канал 3х,52/25 см Schiedel | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `unit` | шт | шт | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `line_type` | materials | materials | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `quantity_raw` | 8 | 8 | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `quantity_display` | 8 | 8 | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `quantity_source` | manual_from_schiedel_specification_or_elena_table | manual_from_schiedel_specification_or_elena_table | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `price_code` | schiedel_vent_channel_3x_52_25_item | schiedel_vent_channel_3x_52_25_item | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `internal_cost.material_unit_price` | 720 | 720 | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `internal_cost.material_total_raw` | 5760 | 5760 | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `internal_cost.material_total` | 5760 | 5760 | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `internal_cost.line_total_raw` | 5760 | 5760 | ok |
| estimate_lines | `schiedel_vent_channel_3x_52_25` | `internal_cost.line_total` | 5760 | 5760 | ok |
| estimate_lines | `schiedel_delivery` | `name` | Доставка вентканалов | Доставка вентканалов | ok |
| estimate_lines | `schiedel_delivery` | `unit` | маш | маш | ok |
| estimate_lines | `schiedel_delivery` | `line_type` | material_and_work | material_and_work | ok |
| estimate_lines | `schiedel_delivery` | `quantity_raw` | 1 | 1 | ok |
| estimate_lines | `schiedel_delivery` | `quantity_display` | 1 | 1 | ok |
| estimate_lines | `schiedel_delivery` | `quantity_source` | manual_input | manual_input | ok |
| estimate_lines | `schiedel_delivery` | `price_code` | schiedel_delivery_truck | schiedel_delivery_truck | ok |
| estimate_lines | `schiedel_delivery` | `internal_cost.material_unit_price` | 15000 | 15000 | ok |
| estimate_lines | `schiedel_delivery` | `internal_cost.material_total_raw` | 15000 | 15000 | ok |
| estimate_lines | `schiedel_delivery` | `internal_cost.material_total` | 15000 | 15000 | ok |
| estimate_lines | `schiedel_delivery` | `internal_cost.work_unit_price` | 2500 | 2500 | ok |
| estimate_lines | `schiedel_delivery` | `internal_cost.work_total_raw` | 2500 | 2500 | ok |
| estimate_lines | `schiedel_delivery` | `internal_cost.work_total` | 2500 | 2500 | ok |
| estimate_lines | `schiedel_delivery` | `internal_cost.line_total_raw` | 17500 | 17500 | ok |
| estimate_lines | `schiedel_delivery` | `internal_cost.line_total` | 17500 | 17500 | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `name` | Расходные материалы, амортизация инструмента | Расходные материалы, амортизация инструмента | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `unit` | комплект | комплект | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `line_type` | percentage_addon | percentage_addon | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `quantity_raw` | 1 | 1 | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `quantity_display` | 1 | 1 | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `quantity_source` | direct_cost_base_before_consumables * consumables_rate | direct_cost_base_before_consumables * consumables_rate | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `internal_cost.material_total_raw` | 3433.68 | 3433.68 | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `internal_cost.material_total` | 3434 | 3434 | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `internal_cost.line_total_raw` | 3433.68 | 3433.68 | ok |
| estimate_lines | `schiedel_consumables_tool_depreciation` | `internal_cost.line_total` | 3434 | 3434 | ok |
| estimate_lines | `technical_supervision_zero` | `name` | Технический надзор | Технический надзор | ok |
| estimate_lines | `technical_supervision_zero` | `unit` | - | - | ok |
| estimate_lines | `technical_supervision_zero` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `technical_supervision_zero` | `quantity_raw` | 1 | 1 | ok |
| estimate_lines | `technical_supervision_zero` | `quantity_display` | 1 | 1 | ok |
| estimate_lines | `technical_supervision_zero` | `quantity_source` | excel_structure_line | excel_structure_line | ok |
| estimate_lines | `technical_supervision_zero` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `technical_supervision_zero` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `technical_supervision_zero` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `technical_supervision_zero` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `technical_supervision_zero` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `technical_supervision_zero` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `technical_supervision_zero` | `internal_cost.line_total_raw` | 0 | 0 | ok |
| estimate_lines | `technical_supervision_zero` | `internal_cost.line_total` | 0 | 0 | ok |
| estimate_lines | `procurement_storage_zero` | `name` | Заготовительно-складские расходы | Заготовительно-складские расходы | ok |
| estimate_lines | `procurement_storage_zero` | `unit` | - | - | ok |
| estimate_lines | `procurement_storage_zero` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `procurement_storage_zero` | `quantity_raw` | 1 | 1 | ok |
| estimate_lines | `procurement_storage_zero` | `quantity_display` | 1 | 1 | ok |
| estimate_lines | `procurement_storage_zero` | `quantity_source` | excel_structure_line | excel_structure_line | ok |
| estimate_lines | `procurement_storage_zero` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `procurement_storage_zero` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `procurement_storage_zero` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `procurement_storage_zero` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `procurement_storage_zero` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `procurement_storage_zero` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `procurement_storage_zero` | `internal_cost.line_total_raw` | 0 | 0 | ok |
| estimate_lines | `procurement_storage_zero` | `internal_cost.line_total` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `name` | Накладные и общехозяйственные расходы | Накладные и общехозяйственные расходы | ok |
| estimate_lines | `overhead_zero` | `unit` | - | - | ok |
| estimate_lines | `overhead_zero` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `overhead_zero` | `quantity_raw` | 1 | 1 | ok |
| estimate_lines | `overhead_zero` | `quantity_display` | 1 | 1 | ok |
| estimate_lines | `overhead_zero` | `quantity_source` | excel_structure_line | excel_structure_line | ok |
| estimate_lines | `overhead_zero` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.line_total_raw` | 0 | 0 | ok |
| estimate_lines | `overhead_zero` | `internal_cost.line_total` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `name` | Сметная прибыль | Сметная прибыль | ok |
| estimate_lines | `profit_zero` | `unit` | - | - | ok |
| estimate_lines | `profit_zero` | `line_type` | zero_excel_structure_line | zero_excel_structure_line | ok |
| estimate_lines | `profit_zero` | `quantity_raw` | 1 | 1 | ok |
| estimate_lines | `profit_zero` | `quantity_display` | 1 | 1 | ok |
| estimate_lines | `profit_zero` | `quantity_source` | excel_structure_line | excel_structure_line | ok |
| estimate_lines | `profit_zero` | `internal_cost.material_unit_price` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.material_total_raw` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.material_total` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.work_unit_price` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.work_total_raw` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.work_total` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.line_total_raw` | 0 | 0 | ok |
| estimate_lines | `profit_zero` | `internal_cost.line_total` | 0 | 0 | ok |
