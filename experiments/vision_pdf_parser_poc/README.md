# Vision PDF Parser POC (A6.0)

Experimental only. Does not touch production Telegram-flow, the earthworks
Google Sheet, `earthworks_v3_adapter.py`, `section_schema.py`,
`resolver_hints`, calculators, or the Excel exporter.

## Goal

Test whether an OpenAI vision model can read structured tables out of a
construction-project PDF (page images, not extracted text) at least as
reliably as the current text-based parser — specifically on the
route/communications tables that the current text parser only handles via
project-specific hardcoded logic (see `earthworks_parser.py`).

The PDF used (ЮСВ) is treated as "just a project" — the prompt asks for
generic construction data useful to an 8-section box estimate, not
"find К1/К2/Вода/Эл.кабель". No project-specific values, page numbers, or
table shapes are hardcoded into the prompt or the code.

## Pipeline

```text
PDF (both usv_2026_kr1.pdf + usv_2026_kr2.pdf, all pages)
  -> render_pdf_pages.py       {pdf_stem}_page_NNN.png + manifest.json
  -> openai_vision_extract.py  one vision call per page -> raw JSON per page
  -> validate_vision_extraction.py   sum/unit sanity checks -> ok/needs_review/conflict
  -> compare_vision_with_reference.py  vision vs validated input.json vs old parser raw output
  -> reports/usv_vision_poc_report.md
```

## Run

```bash
.venv/bin/python3 experiments/vision_pdf_parser_poc/render_pdf_pages.py \
  --pdf-path experiments/usv_strict_pdf_parser_v3/data/input_pdfs/usv_2026_kr1.pdf \
  --out-dir experiments/vision_pdf_parser_poc/output/usv/pages
.venv/bin/python3 experiments/vision_pdf_parser_poc/render_pdf_pages.py \
  --pdf-path experiments/usv_strict_pdf_parser_v3/data/input_pdfs/usv_2026_kr2.pdf \
  --out-dir experiments/vision_pdf_parser_poc/output/usv/pages

.venv/bin/python3 experiments/vision_pdf_parser_poc/openai_vision_extract.py \
  --pages-dir experiments/vision_pdf_parser_poc/output/usv/pages \
  --out-json experiments/vision_pdf_parser_poc/output/usv/vision_extracted_raw.json

.venv/bin/python3 experiments/vision_pdf_parser_poc/validate_vision_extraction.py \
  --vision-json experiments/vision_pdf_parser_poc/output/usv/vision_extracted_raw.json \
  --out-json experiments/vision_pdf_parser_poc/output/usv/vision_validated.json

.venv/bin/python3 experiments/vision_pdf_parser_poc/compare_vision_with_reference.py \
  --vision-json experiments/vision_pdf_parser_poc/output/usv/vision_validated.json \
  --validated-input experiments/earthworks_calculator/cases/usv_yusupovo_village/input.json \
  --parser-earthworks-json experiments/usv_strict_pdf_parser_v3/data/extracted/earthworks.json \
  --out-report experiments/vision_pdf_parser_poc/reports/usv_vision_poc_report.md
```

## Model

Set `OPENAI_VISION_MODEL` in `.env` to override (default: `gpt-4o`). Uses
the existing `OPENAI_API_KEY` from `.env` — never printed/logged.

## Output data

`experiments/vision_pdf_parser_poc/output/` contains real ЮСВ project
content (page renders, extracted raw text/values) — gitignored, kept local
only, same as `data_mkp1/`.
