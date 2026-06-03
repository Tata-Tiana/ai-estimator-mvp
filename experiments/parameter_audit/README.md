# Parameter Audit

`parameter_audit` is a diagnostic experiment for the MVP review pipeline.

It reads the current `reviewed_parameters.xlsx` from `experiments/pdf_parser_pipeline/output/mvp_usv_demo/` and classifies rows that are currently `missing` or `manual_required`.

The goal is to show which rows should remain visible to Elena and which rows should later move to:

- PDF/project extraction (`AUTO_PROJECT`)
- derived calculations (`AUTO_CALCULATED`)
- defaults/material catalog (`DEFAULT_VALUE`)
- price registry (`PRICE_DATABASE`)
- true manual estimator input (`MANUAL_REQUIRED`)

This experiment does not change calculators, formulas, `expected.json`, or `section_schema.py`.

## Run

```bash
../.venv/bin/python3 experiments/parameter_audit/run_parameter_audit.py experiments/parameter_audit/cases/mvp_usv_demo
```

Outputs are written to both the case folder and:

```text
experiments/parameter_audit/output/mvp_usv_demo/
```

## Outputs

- `parameter_audit_result.xlsx`
- `parameter_audit_report.md`
- `result.json`

## Important

`DEFAULT_VALUE` in the audit is only a recommendation. It does not mean that a value from an old template estimate is automatically safe for new projects. Every default needs a source of truth, applicability rules, override behavior, and risk level.

