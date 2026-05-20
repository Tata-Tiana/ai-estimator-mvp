# Load Bearing Walls And Lintels Calculator Experiment

Экспериментальный детерминированный калькулятор раздела "Внешние и внутренние несущие стены, перемычки".

AI здесь не используется. Калькулятор считает только серую внутреннюю себестоимость: материалы, работы и итог раздела. Клиентская часть, рентабельность, НР/СП/ТН и коммерческие коэффициенты не считаются.

## Запуск

```bash
../.venv/bin/python3 experiments/load_bearing_walls_lintels_calculator/run_load_bearing_walls_lintels_calc.py experiments/load_bearing_walls_lintels_calculator/cases/test_load_bearing_walls_lintels
```

Проверка компиляции:

```bash
../.venv/bin/python3 -m py_compile experiments/load_bearing_walls_lintels_calculator/load_bearing_walls_lintels_calculator.py experiments/load_bearing_walls_lintels_calculator/run_load_bearing_walls_lintels_calc.py
```

## Структура

```text
load_bearing_walls_lintels_calculator.py
run_load_bearing_walls_lintels_calc.py
cases/
  test_load_bearing_walls_lintels/
    input.json
    expected.json
    notes.md
output/
  test_load_bearing_walls_lintels/
    load_bearing_walls_lintels_result.json
    load_bearing_walls_lintels_result.md
```

## Важные правила

- `second_light_masonry` - case_specific addon текущего проекта, не постоянное правило раздела.
- Расходные материалы пока manual/fixed amount, потому что формула не подтверждена.
- Краны, вывоз мусора и часть доставок задаются входными параметрами.
- Итоги раздела считаются по Excel-логике: суммируются raw-значения строк, затем округляется итог.
- Дополнительно выводится сумма отображённых округлённых строк, чтобы видеть разницу между raw totals и видимыми строками.

## Ожидаемый результат

```text
internal_materials_total_raw = 1550654.431
internal_materials_total = 1550654
internal_works_total_raw = 1121449
internal_works_total = 1121449
internal_section_total_raw = 2672103.431
internal_section_total = 2672103
```
