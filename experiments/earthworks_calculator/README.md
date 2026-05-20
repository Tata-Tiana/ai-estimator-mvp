# Earthworks Calculator Experiment

Экспериментальный детерминированный расчётный модуль для раздела "Земляные работы".

AI здесь не используется. В будущем AI должен только подставлять входные параметры, а расчёт остаётся обычным Python-кодом.

## Структура

```text
earthworks_calculator.py
run_earthworks_calc.py
cases/
  usv_yusupovo_village/
    input.json
    expected.json
    notes.md
output/
  usv_yusupovo_village/
    earthworks_result.json
    earthworks_result.md
```

## Запуск

Из корня проекта:

```bash
../.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py
```

Запуск конкретного кейса:

```bash
../.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py experiments/earthworks_calculator/cases/usv_yusupovo_village
```

Запуск кейса Хорошевка 14:

```bash
../.venv/bin/python3 experiments/earthworks_calculator/run_earthworks_calc.py experiments/earthworks_calculator/cases/horoshevka_14
```

Запуск всех кейсов:

```bash
../.venv/bin/python3 experiments/earthworks_calculator/run_all_cases.py
```

Можно передать как папку кейса, так и прямой путь к `input.json`.

## Как добавлять следующие тесты

1. Создать папку в `cases/`.
2. Положить туда `input.json`.
3. Положить туда `expected.json` с эталонными значениями от Елены.
4. Добавить `notes.md`: источник данных, что считается, что пока не считается.
5. Запустить runner и проверить блок сравнения с эталоном.

## Формат результата

`earthworks_result.json` хранит расчёт отдельно от проверки:

```json
{
  "inputs": {},
  "volume_result": {},
  "estimate_lines": [],
  "internal_totals": {},
  "expected": {},
  "comparison": []
}
```

`expected.json` для кейса ЮСВ хранит:

- `volumes` — эталонные объёмы;
- `estimate_lines` — эталонные строки серой внутренней сметы по стабильному `code`;
- `internal_totals` — эталонные итоги внутренней себестоимости раздела.
