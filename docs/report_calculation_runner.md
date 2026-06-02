# Отчёт по calculation_runner

Дата: `2026-06-02`.

## Что сделано

Создан экспериментальный слой:

```text
experiments/calculation_runner/
```

Он закрывает demo-цепочку после `input_builder`:

```text
reviewed_parameters.xlsx
↓
input_builder demo_with_template_fallback
↓
generated input.json
↓
calculation_runner
↓
запуск существующих калькуляторов по 8 разделам
```

`calculation_runner` не меняет формулы, не меняет `expected.json`, не делает `box_calculator` и не экспортирует Excel-смету.

## Что делает runner

Для каждого включённого раздела:

1. Берёт generated `input.json` из `input_builder`.
2. Создаёт временную case-папку в:

```text
experiments/calculation_runner/cases/mvp_usv_demo_fallback/generated_cases/<section_code>/
```

3. Копирует туда template case существующего калькулятора.
4. Заменяет `input.json` на generated input.
5. Запускает существующий CLI калькулятора.
6. Сохраняет артефакты:
   - `stdout.txt`;
   - `stderr.txt`;
   - `exit_code.txt`;
   - `result.json`;
   - `result.md`.
7. Собирает общую сводку в `result.json` и `result.md`.

## Важное ограничение demo

Текущий прогон выполнен в режиме:

```text
demo_with_template_fallback
```

Это не production-расчёт и не финальная смета.

Недостающие параметры могли быть взяты из template `input.json`. Все такие подстановки фиксируются в warnings input_builder.

## Команды

Сначала создаются fallback inputs:

```bash
../.venv/bin/python3 experiments/input_builder/run_input_builder.py experiments/input_builder/cases/mvp_usv_demo_fallback
```

Затем запускаются расчёты:

```bash
../.venv/bin/python3 experiments/calculation_runner/run_calculation_runner.py experiments/calculation_runner/cases/mvp_usv_demo_fallback
```

## Текущий demo-run

Результат повторной проверки:

```text
sections_enabled = 8
sections_completed = 8
sections_failed = 0
sections_skipped = 0
total_materials = 8 185 731
total_works = 4 085 463
grand_total = 12 271 194
```

Сводка по разделам:

| Раздел | Статус | Материалы | Работы | Итого |
|---|---|---:|---:|---:|
| Земляные работы | completed_with_warnings | 2 248 997 | 337 223 | 2 586 220 |
| Фундаментная плита | completed_with_warnings | 1 366 205 | 1 083 650 | 2 449 855 |
| Гидроизоляция | completed_with_warnings | 31 884 | 17 255 | 49 139 |
| Несущие стены и перемычки | completed_with_warnings | 1 540 668 | 1 121 449 | 2 662 117 |
| Плита перекрытия 1-го этажа | completed_with_warnings | 1 132 538 | 611 926 | 1 744 464 |
| Плита перекрытия 2-го этажа | completed_with_warnings | 411 599 | 214 290 | 625 889 |
| Плоская кровля | completed_with_warnings | 1 417 244 | 618 070 | 2 035 314 |
| Вентиляционные каналы Schiedel | completed_with_warnings | 36 596 | 81 600 | 118 196 |

Все разделы завершились как `completed_with_warnings`, потому что demo использует live-pricing/fallback и часть калькуляторов возвращает mismatch относительно старых locked expected. Это ожидаемо для demo-run.

## Проверки

Выполнено:

```text
input_builder fallback -> ok
calculation_runner -> ok
8 sections completed
0 failed
0 skipped
py_compile -> ok
calculator files -> not changed
expected.json -> not changed
```

## Следующий шаг

Следующий слой:

```text
box_calculator
```

Он должен будет агрегировать результаты разделов в единую смету коробки дома.
