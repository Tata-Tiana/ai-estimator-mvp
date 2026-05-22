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
output/
  test_foundation_slab/
    foundation_slab_result.json
    foundation_slab_result.md
```

## Запуск

Из корня проекта:

```bash
../.venv/bin/python3 experiments/foundation_slab_calculator/run_foundation_slab_calc.py experiments/foundation_slab_calculator/cases/test_foundation_slab
```

Можно передать как папку кейса, так и прямой путь к `input.json`.

Проверка компиляции:

```bash
../.venv/bin/python3 -m py_compile experiments/foundation_slab_calculator/foundation_slab_calculator.py experiments/foundation_slab_calculator/run_foundation_slab_calc.py
```

## Блоки расчёта

- `membrane` - монтаж мембраны, рулоны Planter Standard, PLANTERBAND.
- `formwork` - площадь отбортовки, фанера, пиломатериал.
- `eps` - ЭППС 50 мм под плитой и ЭППС для термовкладыша.
- `thermal_insert` - штуки термовкладыша и контрольный объём.
- `rebar` - универсальный расчёт арматуры по весу, кг/м, запасу, длине прутка и округлению.
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
