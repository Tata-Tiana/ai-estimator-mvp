# Расчётный отчёт: ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel

AI не используется для расчёта. Калькулятор считает только серую внутреннюю себестоимость.
Клиентская часть и коммерческие коэффициенты вне текущего scope.

## Исходные параметры раздела

- project_name: `test_schiedel_vent_channels_usv_live_prices`
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
- Материалы raw/display: `12297.6` / `12 298`
- Работы raw/display: `0` / `0`
- Итого raw/display: `12297.6` / `12 298`
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
- Материалы raw/display: `5856` / `5 856`
- Работы raw/display: `0` / `0`
- Итого raw/display: `5856` / `5 856`
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
- direct_cost_base_before_consumables: `114753.6`
- consumables_rate: `0.03`
- material_total_raw: `3442.608`

Итог:
- Материалы raw/display: `3442.608` / `3 443`
- Работы raw/display: `0` / `0`
- Итого raw/display: `3442.608` / `3 443`
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
- schiedel_masonry_work_m: price_code not found in price_registry, fallback input price used
- schiedel_delivery_truck: price_code not found in price_registry, fallback input price used

## Источники цен

| Строка сметы | price_code | старая цена | использованная цена | источник | предупреждение |
| --- | --- | ---: | ---: | --- | --- |
| Кладка вентканалов Schiedel | `schiedel_masonry_work_m` | `5000` | `5000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Вентиляционный канал 2х,36/25 см Schiedel | `schiedel_vent_channel_2x_36_25_item` | `504` | `512.4` | `price_registry` |  |
| Вентиляционный канал 3х,52/25 см Schiedel | `schiedel_vent_channel_3x_52_25_item` | `720` | `732` | `price_registry` |  |
| Доставка вентканалов | `schiedel_delivery_truck` | `15000` | `15000` | `fallback_input` | price_code not found in price_registry, fallback input price used |
| Расходные материалы, амортизация инструмента | `None` | `0` | `0` | `locked_case_prices` |  |
| Технический надзор | `None` | `0` | `0` | `locked_case_prices` |  |
| Заготовительно-складские расходы | `None` | `0` | `0` | `locked_case_prices` |  |
| Накладные и общехозяйственные расходы | `None` | `0` | `0` | `locked_case_prices` |  |
| Сметная прибыль | `None` | `0` | `0` | `locked_case_prices` |  |

## Pricing summary

| Показатель | Значение |
| --- | ---: |
| `mode` | `price_registry_with_fallback` |
| `registry_path` | `/Users/tatanamedzidova/Desktop/AI сметчик/ai_estimator_mvp/output/price_registry_filled_v3.xlsx` |
| `prices_from_price_registry` | `2` |
| `prices_from_project_overrides` | `0` |
| `prices_from_fallback_input` | `2` |
| `warnings_count` | `2` |

## Итоги

- Материалы: `36 596`
- Работы: `81 600`
- Всего: `118 196`
- internal_materials_total_raw: `36596.208`
- internal_works_total_raw: `81600`
- internal_section_total_raw: `118196.208`

## Проверка

- status: `ok`
- ok: `0`
- mismatch: `0`

| scope | code | field | expected | actual | status |
| --- | --- | --- | ---: | ---: | --- |
