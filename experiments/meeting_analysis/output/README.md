# Meeting Analysis Output

Основной результат анализа сохраняется в:

```text
data/output/meeting_analysis/{datetime}_{topic}/
```

Внутри создаются:

- `meeting_summary.md` — краткое содержание созвона, разделы сметы, бизнес-правила и решения;
- `calculation_logic.md` — логика расчёта по разделам сметы;
- `formulas.md` — формулы, коэффициенты, округления и вопросы к Елене;
- `parameters_table.xlsx` — таблица параметров для будущей базы расчётной логики;
- `open_questions.md` — вопросы, которые нужно уточнить;
- `project_requirements.md` — требования к проектировщикам и составу проектных данных;
- `raw_ai_response.json` — сырой ответ AI;
- `combined_transcript.txt` — объединённый текст транскриптов;
- `sources.json` — список входных файлов, примеров, режима и модели.
