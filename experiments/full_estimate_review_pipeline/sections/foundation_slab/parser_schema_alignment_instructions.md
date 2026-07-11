# Parser/schema alignment instructions — foundation_slab

Purpose: keep the chat extraction files, review workbook contract, and calculator input shape aligned. The calculator field names are the ground truth; do not rename calculator fields to match an older parser output.

## Ground truth

- Section: `foundation_slab`
- Contract: `sections/foundation_slab/section_contract.yaml`
- Calculator: `experiments/foundation_slab_calculator/foundation_slab_calculator.py`
- Extraction files to keep aligned:
  - `experiments/chat_extraction_poc/data/calculator_targets_compact.json`
  - `experiments/chat_extraction_poc/data/target_aliases_ru.yaml`
  - `experiments/chat_extraction_poc/schemas/claude_extraction_output_schema.json`
  - `experiments/chat_extraction_poc/prompts/claude_estimate_extraction_prompt.md`

## Current status

This section is the reference example for the new rule:

> If parser/schema names disagree with the calculator, fix parser/schema/prompt to match the calculator.

For `foundation_rebar_items`, this is already done:

- contract/calculator row fields: `source_length_m`, `kg_per_meter`;
- parser target group fields: `source_length_m`, `kg_per_meter`, `weight_kg`;
- prompt says `foundation_rebar_items -> source_length_m, kg_per_meter`;
- schema says `source_length_m`, `kg_per_meter`.

## AUTO_PROJECT values expected from PDF/chat JSON

- `membrane_area_m2`
- `slab_side_formwork_area_m2`
- `eps50_under_slab_volume_m3`
- `concrete_project_volume_m3`
- `thermal_insert_50_length_m`
- `thermal_insert_100_length_m`
- `thermal_insert_50_material_spec_qty`
- `thermal_insert_100_material_spec_qty`
- `foundation_rebar_items`

## Rebar rule

For foundation slab rebar, the primary PDF unit is usually linear meters.

Use:

- `source_length_m` for length from specification;
- `kg_per_meter` for mass per meter / mass per item;
- `weight_kg` only if PDF explicitly gives kg;
- do not calculate total weight in GPT/Claude.

Do not copy this field naming to other sections by analogy. Other calculators must be checked separately.

## Important distinctions

- `slab_side_formwork_area_m2` is formwork area in m2, not EPS edge volume.
- `eps50_under_slab_volume_m3` is EPS under slab volume in m3; laying area is calculated later.
- `concrete_project_volume_m3` is only foundation slab concrete.
- `eps_100_edge_volume` may be found in PDF, but it is not a production input of the foundation slab calculator today. **Removed from `calculator_targets_compact.json`/`target_aliases_ru.yaml` 2026-07-11** — verified directly against `foundation_slab_calculator.py` that `eps100_required_volume_m3` is always computed geometrically (`thermal_insert_pieces * eps100_thickness_m * piece_height * piece_depth`), never taken as a direct spec volume, so this was dead parser weight, not a gap. Also removed `sand_volume` and `geotextile_area`, two more orphaned targets whose own notes said they duplicate `earthworks.sand_base_volume_m3`/`earthworks.geotextile_area_m2` — those real targets already exist under `earthworks`, nothing lost.

## Check before marking section ready

1. Compare every `review_parameters[*].calculator_input_path` with the calculator dataclass/constructor.
2. Compare every `target_code` and repeated-row column with `calculator_targets_compact.json`.
3. Compare repeated-row shape with `claude_extraction_output_schema.json`.
4. Check `target_aliases_ru.yaml` uses the same field names and does not ask GPT to calculate derived values.
5. Check prompt has a section-specific rule for any non-obvious mapping.
6. Run JSON/YAML validation after edits.
7. Confirm no project-specific values, page numbers, or USV-only facts were added to production config.

