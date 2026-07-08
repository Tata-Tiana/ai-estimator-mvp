# Step 4 — Section Order

Status: completed

Goal: choose the implementation order for section contracts and downstream review/calculator work.

The order must reduce risk. Earthworks is already implemented and documented as the reference flow.
The next sections should go from compact and well-bounded calculators to the most complex calculators.

## 1. Selected Order

1. `earthworks` — already ready; use as reference behavior only.
2. `waterproofing` — small section, good first contract template.
3. `schiedel_vent_channels` — compact section with clear line sources.
4. `foundation_slab` — larger, but still mostly self-contained.
5. `floor_slab_2` — production modes are clearer and smaller than floor slab 1.
6. `floor_slab_1` — more complex because of beams, insulation, and legacy modes.
7. `flat_roof` — many supplier/manual rows and known Excel-match risks.
8. `load_bearing_walls_lintels` — broadest and most mode-heavy section.

## 2. Checks

- [x] Do not start from the most complex calculator.
- [x] Keep `earthworks` as reference behavior, not a source of project values.
- [x] Start first new contract from `waterproofing`.
- [x] Keep known contamination risks in mind before `flat_roof` and `load_bearing_walls_lintels`.
- [x] Preserve the universal production rule: every section must work from fresh chat/parser JSON.

## 3. Next Step

Step 5 creates:

- `sections/waterproofing/section_contract.yaml`
- `reports/step_05_waterproofing_contract.md`
