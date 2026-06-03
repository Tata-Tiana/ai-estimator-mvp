# Notes

- This is an audit-only experiment.
- It classifies current `missing` and `manual_required` rows from the PDF parser pipeline.
- It must not modify calculators, formulas, `expected.json`, or `section_schema.py`.
- The audit separates project parameters from price, catalog/default, and derived fields.
- System coefficients, package sizes, raw/display fields, and prices should not stay in Elena's manual input table after a validated source is added.
- Project quantities, case-specific decisions, and unsafe defaults must not be hidden.
- `demo_with_template_fallback` is not production and must not be used as evidence that a parameter is safely defaultable.
- No Excel cell references are used as identifiers.

