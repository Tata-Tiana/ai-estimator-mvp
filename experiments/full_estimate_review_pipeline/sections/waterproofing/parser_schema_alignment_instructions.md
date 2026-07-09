# Parser/schema alignment instructions — waterproofing

Purpose: keep the chat extraction files, review workbook contract, and calculator input shape aligned. The calculator field names are the ground truth; do not rename calculator fields to match an older parser output.

## Ground truth

- Section: `waterproofing`
- Contract: `sections/waterproofing/section_contract.yaml`
- Calculator: `experiments/waterproofing_calculator/waterproofing_calculator.py`
- Extraction files to keep aligned:
  - `experiments/chat_extraction_poc/data/calculator_targets_compact.json`
  - `experiments/chat_extraction_poc/data/target_aliases_ru.yaml`
  - `experiments/chat_extraction_poc/schemas/claude_extraction_output_schema.json`
  - `experiments/chat_extraction_poc/prompts/claude_estimate_extraction_prompt.md`

## Current status

Parser-side targets were aligned to production calculator inputs:

- `waterproofing_area_m2`
- `eps100_wall_volume_m3`

The older name `waterproofing_eps_100_edge_volume` must not be used as the production target code.

Contract/parser target names currently match. One calculator-level risk remains outside parser/schema:
`waterproofing_calculator.py` still contains a hardcoded `display_quantity=1.94` for the EPS100
material estimate line. The real calculated quantity is still produced by the calculator, but a final
estimate/export adapter must not copy or trust old display overrides as production quantities.

## AUTO_PROJECT values expected from PDF/chat JSON

- `waterproofing_area_m2`
- `eps100_wall_volume_m3`

## Critical extraction rules

- If PDF has a direct waterproofing area, use it.
- If PDF has no direct waterproofing area, Elena's production rule allows:
  `waterproofing.waterproofing_area_m2 = foundation_slab.slab_side_formwork_area`.
- When this reuse happens, keep the same source/raw text/page and mark `needs_review: true`.
- `eps100_wall_volume_m3` is volume in m3. The calculator converts it to work area by dividing by EPS thickness.

## Important distinctions

- `waterproofing_area_m2` is mastics/waterproofing area in m2.
- `eps100_wall_volume_m3` is EPS 100 mm wall/edge insulation volume in m3.
- Do not mix either of these with foundation slab formwork material lines, roof waterproofing, or floor slab EPS.

## Check before marking section ready

1. Confirm parser targets use `waterproofing_area_m2` and `eps100_wall_volume_m3`.
2. Confirm prompt includes the allowed reuse rule from foundation slab side formwork area.
3. Confirm schema can carry both scalar values.
4. Confirm no legacy perimeter/height reconstruction is used as a production PDF extraction path.
5. Confirm final estimate/export does not use `display_quantity` as the production quantity for EPS100 material.
6. Run JSON/YAML validation after edits.
7. Confirm no project-specific values, page numbers, or USV-only facts were added to production config.
