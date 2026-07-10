# Parser/schema alignment instructions — floor_slab_2

Purpose: keep the chat extraction files, review workbook contract, and calculator input shape aligned. The calculator field names are the ground truth; do not rename calculator fields to match an older parser output.

## Ground truth

- Section: `floor_slab_2`
- Contract: `sections/floor_slab_2/section_contract.yaml`
- Calculator: `experiments/floor_slab_2_calculator/calculator.py`
- Extraction files to keep aligned:
  - `experiments/chat_extraction_poc/data/calculator_targets_compact.json`
  - `experiments/chat_extraction_poc/data/target_aliases_ru.yaml`
  - `experiments/chat_extraction_poc/schemas/claude_extraction_output_schema.json`
  - `experiments/chat_extraction_poc/prompts/claude_estimate_extraction_prompt.md`

## Current status

Contract exists, but this section still needs the same parser/schema cross-check pass that foundation slab already received.

Known risk: this contract currently expects `floor_slab_2_rebar_items` rows with `spec_length_m`. Active parser/schema files must be checked and aligned to the calculator, not to old generic names.

**Calculator change applied 2026-07-10** (explicitly requested, out of the usual "never touch calculator code" rule for this stage — recorded here on purpose): `experiments/floor_slab_2_calculator/calculator.py` previously hardcoded the assumption "floor slab 2 has no beams" — `beams_formwork_area_m2` silently defaulted to 0 with that exact warning text if not supplied, and there was no way to feed beam geometry at all. Per Elena, a beam may or may not exist on either floor slab independently — it is not tied to which floor. Added an optional `beams: {"items": [...]}` input (same row shape as `floor_slab_1_calculator.py`: `code`, `name`, `length_m`, `width_m`, `height_m`, `count`), applied to all three places beams actually affect the floor_slab_1 calculation (audited by reading `floor_slab_1_calculator.py` in full first, to make sure nothing was missed):

1. **Formwork**: `beams_formwork_area_m2` is derived from the sum of item `formwork_area_m2` when the scalar input is absent; if both are given, the scalar wins with a delta warning past 0.01 m2 — same priority as `floor_slab_1_calculator.py`.
2. **EPS100 edge insulation**: each beam's `length_m * height_m * count` now adds to the insulation material area (`edge_and_beam_insulation_area_m2`, drives EPS pack count and foam-glue can count), and each beam's `length_m * count` adds to `total_insulation_length_m`, which is now the real quantity on the `edge_insulation_work` estimate line (previously always `slab_edge_perimeter_m` alone, silently ignoring beams).
3. **Concrete**: `slab_concrete_volume_m3 = concrete_placing_volume_m3 - beams_items_concrete_volume_m3` is now the quantity on `concrete_placing_work` (slab-only work); a new `beam_concreting_work` estimate line prices the beam concrete separately, using a new optional `beam_concreting_work_unit_price` input that is only read when `beams.items` is non-empty (so it is never required on projects without beams).

Backward compatible in every case: no `beams` input at all → every one of the above stays numerically identical to before (0 contribution everywhere, `beam_concreting_work` line present with quantity/total 0, no new required input is read). All 6 existing test cases in `cases/` still pass with 0 mismatches after this change; also manually verified with a synthetic beam that formwork/insulation/concrete all move together consistently.

Rebar is deliberately untouched — floor_slab_1's beam rebar positions are not a separate group, they go into the same flat rebar list differentiated only by diameter/class, and floor_slab_2 already works the same way.

Separately noted, not fixed in this pass: `calculate_rebar_item`'s `spec_length_items` production path hardcodes a 3-entry `REBAR_CATALOG` (A500 ⌀16/12/10 only) and the estimate-line builder unconditionally expects exactly those three codes (`rebar_by_code["rebar_a500_d16"]`, etc.) — a project with a different rebar diameter/class on this slab would crash. This is a real, separate risk from the beams gap; needs its own decision before being touched.

## AUTO_PROJECT values expected from PDF/chat JSON

- `main_formwork_area_m2`
- `edge_formwork_area_m2`
- `beams_formwork_area_m2`
- `slab_edge_perimeter_m`
- `edge_insulation_height_m`
- `concrete_placing_volume_m3`
- `slab_area_m2`
- `floor_slab_2_rebar_items`

## Repeated-row shape

`floor_slab_2_rebar_items`:

- `steel_class`
- `diameter_mm`
- `spec_length_m`

## Critical extraction rules

- Keep slab formwork, edge formwork, and beam formwork as separate rows.
- Keep slab perimeter and edge insulation height separate; the calculator uses both for edge EPS.
- Keep concrete volume for this slab separate from foundation slab, floor slab 1, beams, walls, and lintels.
- Rebar rows must stay row-by-row; do not calculate total weight in GPT/Claude unless PDF explicitly gives it and the calculator expects it.

## Check before marking section ready

1. Read the calculator input shape directly, especially rebar item fields.
2. Confirm whether parser/schema should use `spec_length_m` for `floor_slab_2_rebar_items`.
3. Compare all scalar target codes with contract and calculator.
4. Confirm prompt distinguishes EPS edge volume/area from formwork area.
5. Run JSON/YAML validation after edits.
6. Confirm no project-specific values, page numbers, or USV-only facts were added to production config.

