# Notes

- Source of truth after human review is `reviewed_parameters.xlsx`.
- `extracted_value` is what parser/review cards found in PDF.
- `corrected_value` is what Elena corrected or entered.
- `effective_value` is calculated in Python:
  - `corrected_value`;
  - else `final_value`;
  - else `extracted_value`;
  - else missing.
- Calculators do not read Excel directly.
- `input_builder` creates intermediate `input.json` files for calculators.
- `strict` mode blocks sections with missing required parameters.
- `demo_with_template_fallback` is only a demonstration mode and must write warnings for every template fallback.
- No Excel cell references are used.
- This layer does not calculate estimates, does not export Excel estimates, and does not create Telegram/n8n flows.
