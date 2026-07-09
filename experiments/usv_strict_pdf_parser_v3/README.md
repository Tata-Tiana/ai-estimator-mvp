# USV Strict PDF Parser v3

Diagnostic parser-core for USV-like structural PDFs.

The goal is not to produce a final estimate. The goal is to prove that the parser can understand reusable project structure:

- logical sheets instead of physical page numbers;
- earthworks quantities and trench/communication structures;
- reinforcement rows without confusing pipes with rebar;
- beam tables as structured data;
- evidence for every extracted value.

No known USV values are used as data. Numeric values can only come from PDF text, PDF table cells, or PDF word extraction.

## Run

```bash
.venv/bin/python3 experiments/usv_strict_pdf_parser_v3/run_v3.py
```

## Outputs

```text
data/raw/pages_text.json
data/raw/tables.json
data/raw/drawing_index.json
data/raw/logical_pages.json
data/extracted/earthworks.json
data/extracted/rebar_items.json
data/extracted/beam_items.json
data/extracted/candidates.json
data/mapped/mapped_parameters.json
data/mapped/final_project_parameters_draft.json
data/reports/coverage_report.md
data/reports/parser_debug_report.md
data/reports/integrity_report.md
```

## Design

The parser is layered:

1. PDF extraction: text, tables, words.
2. Logical sheet classification.
3. Domain parsers that only run on allowed logical sheet types.
4. Candidate store with evidence IDs.
5. Mapping only within allowed logical sheet types.

Physical page numbers are evidence only.
