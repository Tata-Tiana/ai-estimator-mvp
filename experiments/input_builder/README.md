# input_builder

`experiments/input_builder` is an experimental MVP bridge between Elena-reviewed PDF parameters and deterministic calculator `input.json` files.

It does not read PDF directly and does not calculate estimates.

Pipeline:

```text
pdf_parser_pipeline -> reviewed_parameters.xlsx -> input_builder -> generated input.json -> calculators
```

## Source

Default demo source:

```text
experiments/pdf_parser_pipeline/output/mvp_usv_demo/reviewed_parameters.xlsx
```

The builder reads the `parameters` sheet and uses:

- `corrected_value` first;
- then `final_value`;
- then `extracted_value`;
- otherwise the parameter is treated as missing.

The effective value is calculated in Python. The builder does not rely on Excel formulas.

## Modes

`strict`

- default mode;
- required parameters without values block the section;
- old template `input.json` values are not silently used.

`demo_with_template_fallback`

- missing values may be copied from the calculator template input;
- every copied value gets a warning;
- this mode is only for demonstrating the mechanics, not for real calculations.

## Run

```bash
.venv/bin/python3 experiments/input_builder/run_input_builder.py experiments/input_builder/cases/mvp_usv_demo
```

Demo fallback smoke run:

```bash
.venv/bin/python3 experiments/input_builder/run_input_builder.py experiments/input_builder/cases/mvp_usv_demo --mode demo_with_template_fallback
```

## Outputs

Case outputs:

```text
experiments/input_builder/cases/mvp_usv_demo/generated_inputs/
experiments/input_builder/cases/mvp_usv_demo/missing_parameters_report.md
experiments/input_builder/cases/mvp_usv_demo/result.json
experiments/input_builder/cases/mvp_usv_demo/result.md
```

Copied outputs:

```text
experiments/input_builder/output/mvp_usv_demo/
```

## Next Step

After Elena fills `corrected_value` and statuses in `reviewed_parameters.xlsx`, this builder can create section inputs for calculator runs. The next larger layer after this is `box_calculator`.
