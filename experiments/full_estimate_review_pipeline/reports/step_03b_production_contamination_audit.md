# Step 3b — Production Contamination Audit

Status: completed draft

Goal: protect the new full-estimate pipeline from old project-specific calculator behavior.

The production pipeline must accept a fresh chat/parser JSON for any project. Old calculator cases,
old result JSON files, old Excel snapshots, and old project runs are allowed only as audit evidence.
They must never provide production quantities, prices, display quantities, totals, filenames, or
hidden overrides.

## 1. What Was Checked

Checked the new full-estimate planning/docs area:

- `experiments/full_estimate_review_pipeline/HANDOFF.md`
- `experiments/full_estimate_review_pipeline/reports/step_00_architecture.md`
- `experiments/full_estimate_review_pipeline/reports/step_01_earthworks_reference.md`
- `experiments/full_estimate_review_pipeline/reports/step_02_section_contract_format.md`
- `experiments/full_estimate_review_pipeline/reports/step_03_all_sections_quantity_matrix.md`

Checked calculator source files for legacy project markers and old Excel-match behavior:

- `experiments/waterproofing_calculator/*.py`
- `experiments/foundation_slab_calculator/*.py`
- `experiments/floor_slab_1_calculator/*.py`
- `experiments/floor_slab_2_calculator/*.py`
- `experiments/flat_roof_calculator/*.py`
- `experiments/schiedel_vent_channels_calculator/*.py`
- `experiments/load_bearing_walls_lintels_calculator/*.py`

## 2. Full-Estimate Pipeline Result

The full-estimate planning/docs area has been updated so it no longer contains direct old project
name markers or old job path fragments.

The remaining old-project language in the full-estimate docs is intentional guardrail language:

- old runs are reference evidence only;
- old fixtures cannot provide production values;
- old expected totals cannot be used to force equality;
- contracts/adapters must run from reviewed JSON and formulas.

## 3. Calculator Risk Findings

The calculators still contain legacy behavior that must be treated carefully in future steps.

### Floor Slab 1

Risk:

- a legacy insulation mode remains in calculator source and runner output text;
- that mode is explicitly described as reproducing old geometry for old-estimate matching.

Production rule:

- future contracts must use the production specification mode for insulation quantities;
- do not make the legacy insulation mode the default for new chat/parser JSON.

### Flat Roof

Risk:

- calculator source contains material total override plumbing;
- several lines mention current Excel/raw-display mismatch behavior;
- some totals are forced to match an old workbook.

Production rule:

- future contracts must not copy these override totals;
- every overridden amount must either be converted into a real formula/source field or marked as `MANUAL_REVIEW` pending formula;
- no old workbook total may be used as a hidden production default.

### Load-Bearing Walls And Lintels

Risk:

- case-specific flags and legacy add-on logic remain in calculator source;
- some upper-level/parapet/second-light behavior is controlled by mode flags and manual/project-specific switches.

Production rule:

- future contracts must prefer explicit production modes and spec-volume/spec-length inputs;
- case-specific add-ons must be represented as `MANUAL_REVIEW` or disabled unless present in the new project JSON.

## 4. Step Checks Added

Updated the handoff and step reports so every future step must check:

- can this run from a fresh chat/parser JSON for a different project?
- are all leaf inputs classified as `AUTO_PROJECT`, `DETAIL_TABLE`, `DEFAULT`, `AUTO_CALCULATED`, `PRICE`, `SUPPLIER_INPUT`, or `MANUAL_REVIEW`?
- did we avoid copying fixture/result values as production quantities?
- did we keep confirmed numeric `DEFAULT` coefficients/catalog values that formulas require?
- did we check June Elena/manual review materials before deleting or nulling numeric constants?
- did we avoid hardcoded expected totals and display quantities?
- did we keep review workbook inputs separate from final estimate rows?

Important distinction:

- Removing old project quantities, totals, display values, and legacy overrides is required.
- Removing formula defaults just because they are numeric is a bug.

Future section contracts must audit numeric calculator fields against the June Elena/manual review
pack and calculator change reports. A number can stay in production if it is a method default,
business coefficient, catalog/package value, or formula coefficient. It must not be extracted from
PDF/chat JSON unless its source class is truly `AUTO_PROJECT` or `DETAIL_TABLE`.

## 5. Acceptance Checks

- [x] Full-estimate docs no longer contain direct old project name markers.
- [x] Handoff now states the universal production rule.
- [x] Handoff now states the numeric defaults rule for all future section contracts.
- [x] Steps 0, 1, 2, and 3 now include contamination guardrails.
- [x] Calculator source risks are listed for future contract work.
- [x] No calculator code was changed in this audit.

## 6. Next Action

Before Step 4 creates `sections/waterproofing/section_contract.yaml`, run this check on the files touched
by that step:

```text
old project marker search
old fixture/result value search
expected total / Excel-match phrase search
```

Any hit in production files blocks the step unless it is removed or reclassified as non-production
audit evidence in a report.
