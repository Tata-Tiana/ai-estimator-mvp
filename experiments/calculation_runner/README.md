# calculation_runner

`experiments/calculation_runner` is an experimental demo runner that launches existing section calculators from `input_builder` generated inputs.

It does not change calculator formulas, does not edit `expected.json`, does not build `box_calculator`, and does not export Excel estimates.

## Demo Flow

```text
pdf_parser_pipeline
-> reviewed_parameters.xlsx
-> input_builder demo_with_template_fallback
-> generated input.json
-> calculation_runner
-> section calculation results
```

The current demo case intentionally uses `demo_with_template_fallback`. Missing values may come from calculator template inputs, and every fallback is reported by `input_builder`. This is not a production estimate.

## Run

First generate fallback inputs:

```bash
../.venv/bin/python3 experiments/input_builder/run_input_builder.py experiments/input_builder/cases/mvp_usv_demo_fallback
```

Then run calculators:

```bash
../.venv/bin/python3 experiments/calculation_runner/run_calculation_runner.py experiments/calculation_runner/cases/mvp_usv_demo_fallback
```

## Outputs

```text
experiments/calculation_runner/cases/mvp_usv_demo_fallback/generated_cases/
experiments/calculation_runner/cases/mvp_usv_demo_fallback/calculations/
experiments/calculation_runner/cases/mvp_usv_demo_fallback/result.json
experiments/calculation_runner/cases/mvp_usv_demo_fallback/result.md

experiments/calculation_runner/output/mvp_usv_demo_fallback/
```

For each section:

- `stdout.txt`;
- `stderr.txt`;
- `exit_code.txt`;
- copied `result.json`;
- copied `result.md`, if produced.

## Next Step

The next layer is `box_calculator`, which will aggregate section results into one house-box estimate.
