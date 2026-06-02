# Notes

- This is a demo runner, not production.
- It uses generated inputs from `input_builder`.
- Current demo mode is `demo_with_template_fallback`.
- Missing parameters may have been copied from template `input.json` by input_builder.
- Existing calculators are launched as subprocesses.
- Existing calculator formulas are not changed.
- Existing `expected.json` files are not changed.
- Mismatches are allowed in this demo layer and are captured as warnings.
- Non-zero section exit codes do not stop the whole runner; stdout/stderr/exit code are preserved.
- This layer does not create `box_calculator`, Excel export, Telegram, or n8n flows.
