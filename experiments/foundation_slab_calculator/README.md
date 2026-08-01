# Foundation Slab Calculator Experiment

Экспериментальный детерминированный расчётный модуль для раздела "Устройство фундаментной плиты".

AI здесь не используется. AI может помогать только извлекать входные параметры, а расчёт остаётся обычным Python-кодом.

Калькулятор считает только серую внутреннюю себестоимость. Клиентская часть сметы, коэффициенты клиента, рентабельность, НР/СП/ТН здесь не считаются и не моделируются.

После строки "Технический надзор" калькулятор сохраняет три нулевые строки структуры Excel:

- "Заготовительно-складские расходы";
- "Накладные и общехозяйственные расходы";
- "Сметная прибыль".

Они имеют `line_type = zero_excel_structure_line`, нужны только для формы раздела и не влияют на `internal_totals`.

## Структура

```text
foundation_slab_calculator.py
run_foundation_slab_calc.py
cases/
  test_foundation_slab/
    input.json
    expected.json
    notes.md
  test_foundation_slab_thermal_inserts_standard/
    input.json
    expected.json
    notes.md
  test_foundation_slab_formwork_spec_area/
    input.json
    expected.json
    notes.md
  test_foundation_slab_plywood_standard/
    input.json
    expected.json
    notes.md
  test_foundation_slab_rebar_spec_length/
    input.json
    expected.json
    notes.md
output/
  test_foundation_slab/
    foundation_slab_result.json
    foundation_slab_result.md
  test_foundation_slab_thermal_inserts_standard/
    foundation_slab_result.json
    foundation_slab_result.md
  test_foundation_slab_formwork_spec_area/
    foundation_slab_result.json
    foundation_slab_result.md
  test_foundation_slab_plywood_standard/
    foundation_slab_result.json
    foundation_slab_result.md
  test_foundation_slab_rebar_spec_length/
    foundation_slab_result.json
    foundation_slab_result.md
```

## Запуск

Из корня проекта:

```bash
.venv/bin/python3 experiments/foundation_slab_calculator/run_foundation_slab_calc.py experiments/foundation_slab_calculator/cases/test_foundation_slab
```

Новый стандарт термовставок 50/100 мм:

```bash
.venv/bin/python3 experiments/foundation_slab_calculator/run_foundation_slab_calc.py experiments/foundation_slab_calculator/cases/test_foundation_slab_thermal_inserts_standard
```

Новый стандарт площади опалубки из спецификации:

```bash
.venv/bin/python3 experiments/foundation_slab_calculator/run_foundation_slab_calc.py experiments/foundation_slab_calculator/cases/test_foundation_slab_formwork_spec_area
```

Новый стандарт фанеры с листом 1.52 x 1.52 м и запасом 5%:

```bash
.venv/bin/python3 experiments/foundation_slab_calculator/run_foundation_slab_calc.py experiments/foundation_slab_calculator/cases/test_foundation_slab_plywood_standard
```

Новый стандарт арматуры из спецификации в м.п.:

```bash
.venv/bin/python3 experiments/foundation_slab_calculator/run_foundation_slab_calc.py experiments/foundation_slab_calculator/cases/test_foundation_slab_rebar_spec_length
```

Можно передать как папку кейса, так и прямой путь к `input.json`.

Проверка компиляции:

```bash
.venv/bin/python3 -m py_compile experiments/foundation_slab_calculator/foundation_slab_calculator.py experiments/foundation_slab_calculator/run_foundation_slab_calc.py
```

## Блоки расчёта

- `membrane` - монтаж мембраны, рулоны Planter Standard, PLANTERBAND.
- `formwork` - площадь отбортовки, фанера, пиломатериал.
- `eps` - ЭППС 50 мм под плитой; в legacy-кейсе также ЭППС для старого термовкладыша.
- `thermal_insert` - legacy-термовкладыш либо новый стандарт термовставок 50/100 мм.
- `rebar` - legacy-расчёт арматуры из веса или новый расчёт из м.п. спецификации, с запасом, округлением до хлыстов, стоимостью по м.п. и контролем веса.
- `concrete` - бетон, доставка бетона, контроль плотности армирования.
- `manual_lines` - фиксированные/manual строки: краны, доставки, насос, логистика, расходники, технадзор.

## Как добавлять следующий кейс

1. Создать папку в `cases/`.
2. Положить туда `input.json`.
3. Положить туда `expected.json` с эталонными значениями серой внутренней сметы.
4. Добавить `notes.md`: источник данных, что считается, что пока не считается, какие строки manual/fixed.
5. Запустить runner и проверить блок сравнения с эталоном.

## Формат результата

`foundation_slab_result.json` хранит расчёт отдельно от проверки:

```json
{
  "case_name": "test_foundation_slab",
  "inputs": {},
  "calculation_blocks": {
    "membrane": {},
    "formwork": {},
    "eps": {},
    "thermal_insert": {},
    "rebar": {},
    "concrete": {},
    "manual_lines": {}
  },
  "estimate_lines": [],
  "internal_totals": {},
  "expected": {},
  "comparison": []
}
```

Для строк, где сумма считается от точного количества, а в смете отображается округлённое, используются оба поля:

- `quantity` - точное количество для расчёта;
- `display_quantity` - округлённое значение для отображения.

## Опалубка бортов

Калькулятор поддерживает два режима:

- `formwork_calc_method = "legacy_perimeter_height"` - старый проверочный режим. Площадь считается как `slab_formwork_perimeter_m * slab_edge_height_m`.
- `formwork_calc_method = "spec_area"` - новый production-стандарт Елены. Площадь опалубки бортов берётся готовым значением из спецификации: `slab_side_formwork_area_m2`.

В новом стандарте `slab_formwork_perimeter_m`, `slab_edge_height_m` и `slab_edge_height_strategy` не обязательны для расчёта опалубки. От готовой площади считаются:

- монтаж опалубки;
- фанера;
- пиломатериал;
- демонтаж опалубки.

## Фанера

Production-стандарт:

```text
plywood_calc_method = "actual_area_with_waste"
plywood_sheet_width_m = 1.52
plywood_sheet_height_m = 1.52
plywood_waste_coeff = 1.05
```

Формула:

```text
plywood_sheet_area_m2 = 1.52 * 1.52
plywood_sheets = ceil(formwork_area_m2 * 1.05 / plywood_sheet_area_m2)
```

`plywood_calc_method`, размер листа и запас являются системными настройками. Их не нужно спрашивать у Елены по каждому проекту.

Legacy-режим:

```text
plywood_calc_method = "working_area"
plywood_sheet_working_area_m2 = 2.25
```

Он сохранён только для старого `test_foundation_slab`, чтобы не ломать сверку с исходной Excel-сметой.

## Термовставки

Калькулятор поддерживает четыре режима:

- `thermal_insert_mode = "legacy"` - старый проверенный кейс. Термовкладыш 150 мм считается через длину, размер элемента и количество элементов. Этот режим сохранён только для совместимости с `test_foundation_slab`.
- `thermal_insert_mode = "standard_50_100"` - стандарт Елены для термовставок 50 мм и/или 100 мм. Слои могут быть оба, только 100 мм, или одна общая длина установки для двух слоёв.
- `thermal_insert_mode = "items"` - произвольные типоразмеры термовставок построчно, когда проект не даёт классическое деление 50/100 мм.
- `thermal_insert_mode = "none"` - в проекте нет термовставок; строки работ и материалов термовставок не формируются.

В стандартном режиме:

- работы считаются по длине из спецификации: `length_m * work_unit_price`;
- если дана одна общая длина на два слоя, формируется одна строка работы по `thermal_insert_combined_length_m`;
- материал берётся из спецификации, умножается на `thermal_insert_material_waste_coeff`;
- закупочное количество округляется до кратности пачки через `round_up_to_multiple`;
- материалы термовставок 50 мм и 100 мм идут отдельными строками сметы только если соответствующий материал есть в проекте;
- старая логика `length / 0.6`, элемент 400 x 150 x высота и строка 150 мм не используются.

## Арматура

Калькулятор поддерживает два режима:

- `rebar_calc_method = "legacy_weight_to_length"` - старый проверочный режим. Спецификация даёт вес арматуры в кг, калькулятор переводит его в м.п. через `kg_per_meter`, добавляет запас, округляет до целых хлыстов и считает стоимость по м.п.
- `rebar_calc_method = "spec_length_m"` - новый production-стандарт Елены. Спецификация даёт длину арматуры в м.п.; вес не вводится из проекта, а рассчитывается через `kg_per_meter`.

В новом стандарте:

- `source_length_m` или сумма `length_parts_m` - проектная длина из спецификации;
- `length_with_waste_m = source_length_m * rebar_waste_coeff`;
- `rods = ceil(length_with_waste_m / rod_length_m)`;
- `order_length_m = rods * rod_length_m`;
- стоимость считается от `order_length_m * unit_price_per_m`;
- проектный вес считается как `source_length_m * kg_per_meter`;
- закупочный/доставочный вес считается как `order_length_m * kg_per_meter`;
- `rebar_frame_assembly` получает количество как сумму закупочных м.п. по всем позициям.

`kg_per_meter`, `rod_length_m` и `unit_price_per_m` сейчас остаются входами кейса. Для production они должны приходить из `price_registry` / material catalog. Финальная доставка металла должна агрегироваться на уровне `box_calculator`, потому что металл суммируется по всем разделам коробки дома.
