# API run 04: TRC KR2 full-PDF attempt

Date: 2026-07-20

## Goal

Test a closer API equivalent of the manual chat extraction:

- only TRC;
- only the second project file / KR2;
- full prompt pack, not compact section-pack;
- short run note explaining that this is the above-floor / second part of the project;
- keep the whole KR2 file available so the model can use cross-page context.

## Script Changes

Two small API harness changes were added:

- `run_section_extraction.py`
  - added `--source-pdf` to select all prepared pages belonging to one PDF from manifest;
  - added `--run-note`;
- `run_claude_api_extraction.py`
  - added `--run-note`;
  - added optional `--section-code` filter while still sending the full prompt pack.

These changes do not alter the manual chat prompt.

## Attempt 1: KR2 as 44 prepared PNG pages

Command shape:

```text
run_section_extraction.py
--source-pdf КР2_ТРЦ_30,06,2026.pdf
--pack-mode full
--model claude-opus-4-8
```

Selected content:

- 44 prepared pages from `КР2_ТРЦ_30,06,2026.pdf`;
- full API prompt pack;
- requested sections:
  - `load_bearing_walls_lintels`;
  - `floor_slab_1`;
  - `floor_slab_2`;
  - `flat_roof`;
  - `schiedel_vent_channels`.

Result:

- failed before extraction;
- API returned `413 request_too_large`;
- reason: 44 PNG images + full prompt + page text exceeded Anthropic request size.

Conclusion:

Sending the entire KR2 as rendered PNG pages is not viable in one request.

## Attempt 2: KR2 as one PDF document block, no section filter

Command shape:

```text
run_claude_api_extraction.py
--pdf /Users/tatanamedzidova/Desktop/КР2_ТРЦ_30,06,2026.pdf
--model claude-opus-4-8
--max-tokens 40000
```

Result:

- API accepted the request;
- output was saved to:
  - `experiments/claude_api_extraction_poc/outputs/trc/full_kr2_pdf_opus48_full_prompt/api_raw_response.json`
  - `experiments/claude_api_extraction_poc/outputs/trc/full_kr2_pdf_opus48_full_prompt/api_output_text.txt`
- parser failed because the JSON was incomplete;
- `stop_reason = max_tokens`;
- usage:
  - input tokens: `171695`;
  - output tokens: `40000`.

Important observation:

Because this full-PDF script did not pass requested section codes yet, the model started generating
all eight prompt sections, including empty `earthworks` and `foundation_slab`. That wasted output
tokens and made truncation inevitable.

## Attempt 3: KR2 as one PDF document block, with KR2 section filter

Command shape:

```text
run_claude_api_extraction.py
--pdf /Users/tatanamedzidova/Desktop/КР2_ТРЦ_30,06,2026.pdf
--section-code load_bearing_walls_lintels
--section-code floor_slab_1
--section-code floor_slab_2
--section-code flat_roof
--section-code schiedel_vent_channels
--model claude-opus-4-8
--max-tokens 40000
```

Result:

- API accepted the request;
- output was saved to:
  - `experiments/claude_api_extraction_poc/outputs/trc/full_kr2_pdf_opus48_full_prompt_v2/api_raw_response.json`
  - `experiments/claude_api_extraction_poc/outputs/trc/full_kr2_pdf_opus48_full_prompt_v2/api_output_text.txt`
- parser failed because the JSON was still incomplete / malformed;
- `stop_reason = max_tokens`;
- usage:
  - input tokens: `171879`;
  - output tokens: `40000`.

Quality note from the partial text:

The model did use broad cross-page context and found real project issues:

- it noticed that some sheets appear to have a different project stamp;
- it found wall/block, slab, formwork, roof, and vent-channel related data;
- it flagged many values as `needs_review` because the PDF text layer is fragmented;
- it identified mixed/ambiguous values such as slab edge formwork vs beam formwork.

But the response is not a usable final `extraction_output.json` because it hit the output token limit.

## Conclusion

The full-KR2 / full-prompt idea is directionally right for quality because it preserves cross-page
context. But one monolithic JSON answer for the whole KR2 is too large.

Recommended next approach:

1. Keep Opus 4.8.
2. Keep the full prompt pack.
3. Keep the whole relevant PDF file available when possible.
4. Do not ask for all KR2 sections in one JSON response.
5. Split KR2 into logical full-context runs:
   - walls/lintels;
   - floor slab 1;
   - floor slab 2;
   - flat roof;
   - vent channels.
6. Alternatively use section groups:
   - `flat_roof + schiedel_vent_channels`;
   - `floor_slab_1 + floor_slab_2`;
   - `load_bearing_walls_lintels`.

This is not the same as blind page slicing: the model can still receive the full KR2 PDF/document,
but the requested output must be smaller and section-scoped so it can finish valid JSON.

## Practical Takeaway

For production API extraction, we need a job plan:

```text
project file split (KR1/KR2)
→ full-file context
→ section-scoped extraction tasks
→ merge outputs
→ validate final JSON
```

This preserves the benefit of seeing the whole file while avoiding a single huge response that cannot
fit in the API output limit.
