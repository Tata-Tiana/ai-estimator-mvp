# Output

Здесь сохраняются результаты запуска `run_earthworks_calc.py` по каждому кейсу.

Формат:

```text
output/
└── <case_name>/
    ├── earthworks_result.json
    └── earthworks_result.md
```

Файлы:

- `earthworks_result.json` — машинно-читаемый результат: `inputs`, `volume_result`, `estimate_lines`, `internal_totals`, эталон и сравнение с `expected.json`.
- `earthworks_result.md` — читаемый отчёт с входными параметрами, формулами, результатами и проверкой с расчётом Елены.
