# Full Estimate Review Pipeline — Handoff And Checklist

Use this file when a new chat starts.

If the user says "прочитай инструкцию и продолжай", read this file first, then read the current step report in `reports/`.

## Current Goal

Build a Google review workbook for all 8 estimate sections, then make it flow into calculators and final estimate export the same way the earthworks flow already does.

This is a universal production pipeline. It must accept a new chat/parser JSON for any project and produce review/calculator/final-estimate artifacts from that JSON. Old calculator fixtures and old project runs are reference behavior only; they are not allowed to provide production quantities, prices, display quantities, totals, or hidden overrides.

The important distinction:

- Review workbook = human-checkable inputs, prices, details, parser evidence.
- Final estimate workbook = estimate rows, formulas, helper cells, totals.

Do not confuse `AUTO_PROJECT` rows with final estimate rows.

## Explicit Decision — No Universal Production Anti-Cheat For Now

As of 2026-08-03, do not build or wire a universal `anti_cheat.py` gate into the new all-section
production pipeline.

There is an older earthworks-specific anti-cheat in `experiments/earthworks_review_to_calculator/`.
It is useful as historical reference, but it must not be copied wholesale into the new 8-section
pipeline. The current production direction is:

- keep the Google review workbook human-readable and auditable;
- use validation, coverage reports, notes reports, and explicit blockers;
- fail adapters/calculators loudly when required reviewed values or prices are missing;
- postpone a separate universal anti-cheat layer until the review workbook -> adapters -> final
  estimate flow is stable.

## Production Gate Idea — Human Review Status And Final Estimate Sanity Audit

Added 2026-08-07 after the TRC final-estimate dry run exposed a silent zero in the walls section.

This is not the postponed universal "anti-cheat" layer above. This is a narrower production gate around
the existing workflow, needed before the Telegram bot can safely return a final estimate.

The intended bot workflow is:

```text
corrected chat/parser JSON
-> bot builds Google review workbook
-> estimator checks/fixes Google workbook
-> bot downloads filled workbook
-> normalized review JSON
-> pre-calculation readiness check
-> calculators
-> draft final estimate workbook
-> post-calculation sanity audit
-> final estimate is released only if there are no red blockers
```

Important distinction:

- Calculator input validity means "the Python dataclasses/calculators can run".
- Estimate readiness means "the reviewed business data is confirmed enough to release a final estimate".

These are not the same. A calculator can accept a yellow `needs_review` value because the value is a
valid number, but the pipeline may still decide that the final estimate cannot be released until a human
confirms that value.

### Pre-calculation readiness check

Run after the filled Google workbook is downloaded and normalized, before calculators.

Purpose:

- block required red rows (`missing`, required manual inputs, required prices) before calculators see them;
- distinguish yellow rows that may be calculated with a warning from yellow rows that must be explicitly
  accepted/confirmed before final release;
- treat an estimator-entered corrected value or explicit confirmation as acceptance of a `needs_review`
  value;
- produce a human-readable report saying what Elena/estimator can fix in the Google workbook.

Examples Elena/estimator can fix:

- price not found on sheet 02 -> enter/fix price;
- project value missing -> enter reviewed value on sheet 01;
- suspicious value found -> confirm, correct, or set zero if the work is absent;
- optional work absent -> enter 0 or leave empty according to the section contract.

Examples Elena/estimator should not fix manually:

- data exists in the review workbook/JSON, but a calculated estimate line becomes zero;
- a repeated-row group disables a scalar value for another role;
- calculator output contradicts its own input source.

Those are code bugs and must be sent to the developer backlog.

### Post-calculation sanity audit

Run after calculators and before sending the final estimate workbook.

Purpose:

- catch silent zeros and source-selection bugs that are invisible to schema validation;
- compare critical input values with critical estimate lines;
- stop release when the estimate lost money-bearing quantities.

Required first checks:

- if main wall D400/D500 volumes exist in review data but the 1st-floor masonry estimate lines are zero,
  block release as a red technical error;
- if concrete/rebar/formwork/EPS/roof material values exist in review data but the corresponding mandatory
  estimate line is zero, block release unless the section contract marks that line optional/diagnostic;
- if a repeated group is present, verify that it only overrides the scalar for the same role/component,
  not unrelated roles/components;
- if a calculator used fallback/default/auto-sum logic for a money-bearing line, surface that in the audit
  as yellow unless the rule is explicitly documented as safe.

Audit outcome levels:

- Green: no blockers; send final estimate.
- Yellow: send estimate plus warnings, or require explicit confirmation depending on the section rule.
- Red: do not send a "final" estimate; send a clear report and either ask the estimator to fix the workbook
  or mark it as a developer bug.

TRC wall-block lesson:

The bug was not in extraction: the main-wall D400/D500 values existed. The calculator treated "any
`wall_block_items` rows exist" as "all wall roles must come from `wall_block_items`", so main-wall scalar
volumes were silently ignored when only floor_2/parapet/partitions had repeated rows. Future code must use
per-role source selection: `main_walls` repeated rows override only main-wall scalars; `floor_2` rows
override only floor_2 scalars; `parapet` rows override only parapet scalars. Mixed scalar + repeated-row
input is a normal production state, not an error.

## Canonical Pipeline

The target pipeline is:

```text
chat extraction / parser output
-> Google review workbook
-> normalized review JSON
-> calculator input JSON
-> calculator result JSON
-> formula_ready rows
-> final estimate workbook
```

The earthworks section already proves this pattern.

**`output/manual_values_registry.xlsx` prerequisite (added 2026-08-08):** this file (sheet 01-1's
typical-value source) is no longer hand-edited locally — Elena edits it directly in a Google Sheet
(https://docs.google.com/spreadsheets/d/16d4Nm_1EeQ1ssB4t9nsJVVpU4et63wFa/). Before building any
review workbook, run:

```
.venv/bin/python3 experiments/full_estimate_review_pipeline/download_manual_values_registry.py
```

This overwrites `output/manual_values_registry.xlsx` with the current Google Sheet content (downloads
via `curl`, not urllib — this venv's Python has no working local CA bundle; validates sheet name/header
before overwriting, so a bad download never corrupts the local copy). **Do not hand-edit
`output/manual_values_registry.xlsx` locally anymore — edits will be silently lost on the next
download.** If a new manual-input field needs a typical value, add the row via
`regenerate_manual_values_registry.py` as before (it adds blank rows for newly-manual contract fields),
then copy that row into the Google Sheet by hand so it survives the next download.

## Current Active Step — TRC JSON To Review Workbook Plan (updated 2026-08-02)

The current planning baseline is:

```text
reports/step_28_trc_json_to_review_workbook_plan.md
```

Read it before changing prompt/schema/validator/workbook logic.

Context:

- Fresh TRC one-prompt chat extraction has been saved under
  `experiments/chat_extraction_poc/outputs/trc/`.
- Human audit is saved as
  `experiments/chat_extraction_poc/reports/trc_json_and_memo_human_audit_2026-08-02.md`.
- Validation, coverage audit, and service memo coverage reports have been generated.
- The four-step parsing experiment is closed; do not edit or restart it unless the user explicitly
  reopens that experiment. Current production/chat path is the one-prompt `chat_extraction_poc`
  upload pack.

Main conclusion:

- The prompt is now good enough to expose many real project ambiguities.
- The next bottleneck is code/schema/workbook handling of real project structures:
  repeated slab zones, candidates, safe autosums, complex units, visible notes, confidence, and
  complete `needs_review` reporting.

Immediate next actions, in order:

Done before the next active step:

- TRC baseline reports committed.
- Service-note coverage rule added to the one-prompt chat extraction prompt.
- Automatic extraction notes report generated and summarized.
- Sheet `01_Проверка проекта` verified on
  `experiments/full_estimate_review_pipeline/output/trc_review_workbook_2026-08-02_v1.xlsx`:
  empty `Сверка` is absent, `Уверенность` is visible.
- `normalized_unit: mixed` is now allowed only for `raw_table_rows` and repeated group rows. TRC
  validation dropped from 52 warnings to 11; the remaining warnings are all rebar `weight_kg`.
- Rebar validation now distinguishes printed total kg (`... п.м; ... кг`) from kg-per-meter
  source data. TRC validation is now 0 warnings.
- Candidate/autosum handling on sheet 01 is explicit: only listed safe targets autosum; unresolved
  candidates render their components in `Фрагмент проекта` with "Автосумма не применена".
- Sheet 01 now appends parser `notes` to `Фрагмент проекта` when a JSON item has both `raw_text`
  and `notes`. Do not regress this to `raw_text` only: visible review would hide exactly the doubts
  Elena needs to see.
- Prompt/code boundary fixed on 2026-08-02: chat extraction preserves PDF facts and components;
  review/calculator code decides safe autosums, blocking, and workbook display. Do not move
  project-specific production decisions into the prompt.
- Floor slab zones decision fixed on 2026-08-02: keep `floor_slab_1/slab_zones` live; do not add
  `floor_slab_2_slab_zones` until a real project needs it and the calculator/contract/schema are
  changed together. Do not add generic insulation zones now; beam/lintel/slab insulation must come
  from explicit project lines or remain `needs_review`/manual.
- 2026-08-04 update: beam concrete scalar rows may be closed by repeated beam rows in the review
  workbook. `floor_slab_1_beams_concrete_volume` can be shown as a sum of
  `beam_items.concrete_volume_m3`; `floor_slab_2_beams_concrete_volume` can be shown as a sum of
  `floor_slab_2_beam_items.concrete_volume_m3`. This rule is only for beam concrete volumes, not
  beam insulation lengths/areas.
- 2026-08-04 update (see step 28.17): `build_extraction_notes_report.py:semantic_diagnostics()` got
  5 more checks — duplicate/missing `code` in `*_rebar_items` groups, a generalized forbidden-source
  mapping table (`FORBIDDEN_SOURCE_TERMS`), thermal-insert scalar-vs-`thermal_insert_items`
  conflict, `roof_zones[].operability` enum, and partition rebar wrongly tagged
  `component=load_bearing_walls`. This is not a new subsystem — same narrow-binary-rule pattern as
  the existing `wall_role`/beam-concrete-scalar checks. Do not add a "field is absent" style check
  here; that already failed once as the original ungraded `coverage_audit.py` (see `da35e2a`) — every
  new rule here must check a concrete violation of an already-documented rule, tested against ARK
  before shipping so it stays silent where the data is already correct.
- 2026-08-04 update (see step 28.18): first full run of the step 28.12 loop end-to-end — fresh
  extraction -> `build_extraction_notes_report.py` -> correction prompt
  (`prompts/notes_report_correction_prompt.md`) run in the same chat with PDFs loaded ->
  `extraction_output_corrected.json` -> heavy audit prompt
  (`prompts/service_note_technical_audit_prompt.md`) on the corrected file. All 27 `semantic_error`
  findings from the code pass were genuinely fixed (verified by JSON diff, not just the report
  counter); the heavy audit itself confirmed the code layer was clean and surfaced one new bug class
  code can't see: a `candidates[]` entry carrying a `target_code` that doesn't match the item it's
  attached to. Added 6th check `candidate_target_code_mismatch_diagnostics`, same narrow-binary-rule
  pattern, 0 false positives on ARK/TRC 08-02/03/04, fires on the known bug in both the pre- and
  post-correction TRC files (that bug is outside the code-report/correction-prompt scope; only the
  heavy audit catches it). Synthesis in
  `reports/trc_json_and_memo_human_audit_2026-08-04.md`. Practical ordering confirmed: run the cheap
  code-report correction pass *before* the heavy audit prompt, not after — the heavy audit explicitly
  self-reported it wasn't re-flagging anything the code pass already fixed.
- 2026-08-05 real money bug found and fixed in `sections/load_bearing_walls_lintels/section_contract.yaml`:
  `floor_1/2_lintel_formwork_horizontal_area_m2`/`vertical_area_m2` are real calculator dataclass
  fields (since the 2026-07-25 formwork-from-area fix) and real extraction target_codes (same date,
  `calculator_targets_compact.json`) — TRC's own JSON has real values (0.5/1.4 m2 floor 1, 0.45/3.25
  m2 floor 2) — but had ZERO `review_parameters` entries wiring extraction to the calculator input.
  Real project area was silently never reaching the calculator; formwork_plywood_qty/timber_volume_m3
  computed from a missing area defaulted toward zero — plywood/timber cost silently dropped from the
  estimate with no needs_review/missing flag anywhere (this specific field pair isn't in
  SECTION_PRESENCE_PAIRS, so the "confirmed_required" escalation never caught it either). Added the 4
  missing review_parameters entries + 2 new `defaults` entries (`lintel_formwork_plywood_sheet_area_m2`,
  `lintel_formwork_board_thickness_m` — already-hardcoded calculator constants, now traceable in the
  contract) + corrected the `formula`/`leaf_inputs` on all 4 formwork material estimate_lines, which
  had been silently pointing at the *other* stale bug (the direct plywood-qty/timber-volume fields
  removed from the calculator 2026-07-25 but left in the contract, hidden from sheet 01 the same day
  as this fix). Verified: workbook build shows all 4 new area rows as real "Найдено" values from the
  TRC JSON, found-count +4. Same investigation also fixed a real display bug: `lintel_groove_rebar_items`
  had `value_kind: rows` (the only occurrence of that string in the whole codebase; every other
  repeated-row group uses `value_kind: repeated_rows`), so it fell through to the generic scalar
  review path and rendered as a dead "Проверьте" row instead of a real per-item diagnostic table.
- 2026-08-05 `floor_slab_1/slab_zones[]` extended with per-zone formwork (Elena's own idea, mirroring
  how foundation already does zones): 3 new optional columns `edge_perimeter_m`,
  `under_slab_formwork_area_m2`, `edge_and_beam_formwork_area_m2` in
  `sections/floor_slab_1/section_contract.yaml`. Real ТРЦ case this fixes: the flat scalar formwork
  fields can only represent ONE project-wide situation (either a clean edge/beam split, or one merged
  edge+beam number) at a time — but this project needs BOTH simultaneously across its two zones: the
  main zone's vertical formwork is one unsplittable merged number (torец плиты + балки), while the
  kitchen/dining zone gives its own pure edge-only number with no beams. `calculate_floor_slab_1()` in
  `floor_slab_1_calculator.py` now validates all-or-nothing per zone (any zone giving any of the three
  fields means every zone must give all three, or `ValueError`), sums each field across zones, and
  routes the sums into `calculate_formwork_areas_context()` (now taking two new optional kwargs
  `zone_main_formwork_area`/`zone_edge_and_beam_formwork_area`) ahead of the flat scalars — same
  precedence pattern as the existing concrete-volume zone override. Also fixed two latent bugs found
  while wiring this: `edge_formwork_height_m` had no fallback to `slab_thickness_m` despite the
  contract already documenting that behavior (would hard-`KeyError` on a real project omitting the
  line); and the diagnostic `calculation_blocks.geometry` echo block read the raw un-overridden
  `geometry_in["slab_edge_perimeter_m"]`/`["edge_formwork_height_m"]` instead of the locally resolved
  values, which would misreport the actual perimeter/height used once zones are in play. Verified
  additive: re-ran all 15 pre-existing `floor_slab_1_calculator` regression cases against both the
  pre-session baseline (`git show HEAD:...`) and the edited file — byte-identical pass/fail counts on
  every case, including the 3 pre-existing mismatches in `test_slab_zones_equivalence` and the 23 in
  `test_floor_slab_1_insulation_spec_quantities` (confirmed pre-existing, unrelated to this change, not
  something introduced this session). Added a 16th case,
  `cases/test_slab_zones_formwork_equivalence`, using the real TRC zone numbers (main zone: perimeter
  67.2, under-slab area 97.11, combined edge+beam 36.6; kitchen zone: perimeter 10.6, under-slab area
  25.05, pure edge 5.6, no beams) — passes clean, confirms zone sums (122.16 m2 main, 42.2 m2
  edge+beam, 77.8 m perimeter) and the height fallback all land correctly. Extraction-side JSON not yet
  patched with these per-zone values and the TRC review workbook not yet rebuilt with this change —
  both still pending, only requested if/when the user confirms.
- 2026-08-05 (same investigation, different layer): `floor_slab_1_alternative_scalar()` in
  `populate_review_workbook_from_extraction.py` got 4 fixes at the review-workbook layer (separate
  from the calculator/contract zone work above — pre-approved as "mechanical, no questions" before the
  zone architecture was even proposed). Signature extended to take `found`/`found_by_target` like the
  other section alternative-scalar functions: (1) `floor_slab_1_slab_edge_perimeter` and (2)
  `floor_slab_1_under_slab_formwork_area` now auto-sum same-target_code candidates via the existing
  `candidate_sum_scalar` pattern (new `AUTO_SUM_CANDIDATE_TARGETS["floor_slab_1"]` entry) — real TRC
  case: PDF gives these per zone (main slab + kitchen/dining) with no combined total, same shape as
  the already-shipped `cutoff_waterproofing_load_bearing_walls_area` sum; (3)
  `floor_slab_1_beams_formwork_area` now falls back to summing `beam_items[].formwork_area_m2` when
  the scalar is missing/unreliable — the contract already documented this as calculator behavior, the
  workbook display just never implemented it; (4) `floor_slab_1_edge_formwork_height` now shows
  "Найдено (=толщина плиты)" using `found_by_target["floor_slab_1_slab_thickness"]` instead of a blank
  "Проверьте" row when no separate height line exists — matches the field's own long-documented
  auto_calculated fallback, control-calc only, never money-relevant. Verified on the real TRC JSON
  (`extraction_output_corrected.json`, workbook rebuilt as `trc_review_workbook_2026-08-05_v5.xlsx`):
  perimeter → 77.8 мп, under-slab area → 122.16 м2, beams formwork → 34.339 м2 (live sum from the real
  beam_items rows), edge height → 0.2 м. Extraction JSON itself was explicitly NOT touched this round —
  user will redo the chat extraction pass from scratch, so JSON patching is off the table for now.
- 2026-08-05 follow-up, two more fixes after user reviewed the rebuilt workbook row-by-row (screenshot
  walkthrough of the remaining empty floor_slab_1 EPS/formwork rows):
  1. **Extraction prompt updated for the new zone-formwork columns** (this was the important one —
     without it, redoing the chat extraction pass would reproduce the exact same broken state, since
     GPT never learned the new `slab_zones` formwork columns or the
     `floor_slab_1_edge_and_beam_formwork_area_combined` scalar even existed).
     `chat_extraction_poc/data/calculator_targets_compact.json`: `slab_zones` group's `fields` extended
     with `edge_perimeter_m`/`under_slab_formwork_area_m2`/`edge_and_beam_formwork_area_m2` plus a
     detailed notes block (all-or-nothing rule, when to use merged-vs-pure-edge in
     `edge_and_beam_formwork_area_m2`); added the missing `floor_slab_1_edge_and_beam_formwork_area_combined`
     scalar target (was referenced only in a comment before, never an actual target GPT could fill —
     confirmed absent from `found`/`needs_review`/`missing` in the real TRC JSON, not even attempted);
     updated notes on `floor_slab_1_slab_edge_perimeter`/`floor_slab_1_under_slab_formwork_area`/
     `floor_slab_1_edge_formwork_area` to point at `slab_zones` when the PDF gives per-zone data, and
     to explicitly warn against summing a merged slab+beam candidate (e.g. 36.6 м2) into the
     slab-edge-only scalar (real bug pattern seen this session: candidates 36.6+5.6 sitting unresolved
     in `floor_slab_1_edge_formwork_area` precisely because 36.6 already includes beam area — summing
     would double-count). Same 5 changes mirrored in `chat_extraction_poc/data/target_aliases_ru.yaml`
     (`slab_zones` entry extended, 3 scalar entries' notes updated, new
     `floor_slab_1_edge_and_beam_formwork_area_combined` alias entry added). Both files validated
     (JSON/YAML parse clean).
  2. **`floor_slab_1_eps100_volume` auto-sum shipped** (the one genuinely safe leftover item from the
     row-by-row review) — new `AUTO_SUM_CANDIDATE_TARGETS["floor_slab_1"]` entry + branch in
     `floor_slab_1_alternative_scalar()`, same `candidate_sum_scalar` pattern as the perimeter/area
     fixes above. Real TRC case: PDF gives EPS-100 volume as 3 non-overlapping components (edge
     1.478 + under-slab 1.549 + kitchen zone 0.263 m3) with no combined total — these are genuinely
     additive (unlike the edge-formwork-area case above, which is NOT safe to sum because one
     candidate already includes the other's content). Verified on real TRC JSON: autosum → 3.29 m3.
     Rebuilt workbook as `trc_review_workbook_2026-08-05_v6.xlsx`.
  Two other items flagged in the same review were deliberately left alone: the
  `floor_slab_1_edge_eps_work_length` needs_review row has candidates carrying the WRONG target_code
  (`floor_slab_1_slab_edge_perimeter` instead of its own) — this is exactly what the 6th diagnostic
  check (`candidate_target_code_mismatch_diagnostics`, see step 28.18) already catches; no code fix
  needed, it'll surface automatically next time this JSON goes through
  `build_extraction_notes_report.py`. And the 4 genuinely-missing EPS/beam-insulation rows
  (`floor_slab_1_beams_eps_work_length`, `floor_slab_1_beams_eps_material_area`,
  `floor_slab_1_edge_eps_material_area`, `floor_slab_1_bottom_eps_work_area`) have zero candidates in
  the JSON at all — not a bug, just data genuinely not present on the pages the model read; needs a
  manual PDF check, not a code change.
- 2026-08-05 manual PDF check done (`КР2_ТРЦ_30,07,2026.pdf` on Desktop, стр. 26-38/41-44) — confirmed
  the 4 "missing" floor_slab_1 fields above AND their floor_slab_2 counterparts
  (`floor_slab_2_beams_bottom_formwork_area`, `floor_slab_2_beams_eps_material_area`,
  `floor_slab_2_bottom_eps_work_area`, `floor_slab_2_slab_area`) are genuine PDF-level gaps, not parser
  misses: the material-spec tables (стр. 31, 36) only give EPS insulation as a VOLUME total in m3 per
  location ("Утепление вертикальных поверхностей плиты" / "...под плитой"), never a separate m2 area
  figure for the same locations, and never a beam-specific EPS row at all. Floor 2 additionally has no
  separate horizontal-under-beam formwork line at all (floor 1 does, at 1.26 м2) — a real structural
  difference between the two floors in this project, not missing extraction. No code change from this;
  recorded as confirmed-not-a-bug. Same PDF check surfaced an unrelated real finding: pages 38+44 show a
  third, fully-specified staircase landing slab (elevation +7.150) with its own real concrete/EPS/
  formwork numbers, currently uncaptured in any section — see `[[future_estimate_sections_roadmap]]`
  memory (updated with the confirmed numbers). Per user: "просто фиксируем" — recorded only, no schema
  work started.
- 2026-08-05 flat_roof: reverted the 2026-08-03 decision that moved 7 fields
  (`slope_plate_a/b/j/k_supplier_required_volume_m3`, `eps50_supplier_required_volume_m3`,
  `roof_aerators_count`, `internal_drain_height_per_drain_m`) from `SUPPLIER_INPUT` to `AUTO_PROJECT`
  on the assumption they're PDF specification values. Direct check of all 3 real projects' KR2 PDFs
  (ARK/TRC/USV) found none print a letter-split SLOPE volume or aerator count as extractable text —
  the SLOPE line is always one undivided figure or "Уточнить у монтажной организации". Confirmed
  against Elena's own real delivered estimates (`АРК для ИИ.xlsx` rows 294-311, `Сметный расчет
  _ЮСВ_28.04.2026.xlsx` rows 200-220): all 7 values are hand-typed fixed numbers, never formulas
  from roof area/PDF geometry — ЮСВ's own row label spells it out ("требуется расчет уклонов у
  расчетной организации"), and the internal drain height row is explicitly labelled "(ориентировочно)"
  with a flat rule-of-thumb `3.75*3`. Moved all 7 back to `sections/flat_roof/section_contract.yaml`'s
  `supplier_inputs`, removed them from `checks.required_review_parameters`, and deleted their entries
  entirely from `chat_extraction_poc/data/calculator_targets_compact.json` and `target_aliases_ru.yaml`
  — per user instruction, these are not extraction targets at all now ("не нужно искать эти все данные
  по кровле и портить статистику... это болванка для заполнения"), same pattern as
  `formwork_rental_supplier_quote_total`. Ran `regenerate_manual_values_registry.py`: added 7 new
  blank rows to `output/manual_values_registry.xlsx` (dropped 0, kept 13 existing). Rebuilt TRC
  workbook (`trc_review_workbook_2026-08-05_v8.xlsx`): flat_roof's `missing` count dropped from 22 to
  15 — these 7 no longer count against found/missing statistics at all.
- 2026-08-05 flat_roof follow-up: fixed the other roof gap from the same review — `roof_area_level_1/2`,
  `roof_parapet_length_level_1/2`, `roof_vent_wall_abutment_level_1/2` (6 fields, all documented
  "Fallback only" in the contract since `roof_zones[]` became primary geometry) were dangling as
  "Не найдено" instead of showing they're correctly superseded. New `ROOF_ZONES_FALLBACK_ONLY_TARGETS`
  set + branch in `flat_roof_alternative_scalar()` (signature extended to take `found_groups`, matching
  the other section alternative-scalar functions): when `roof_zones[]` is present, these 6 show "Не
  требуется (есть roof_zones)" with the zone rows quoted in the fragment, same pattern as
  `wall_block_items[]` superseding its 5 scalar fields. Rebuilt workbook
  (`trc_review_workbook_2026-08-05_v9.xlsx`): flat_roof `missing` dropped 15→9, `found` 175→181.
- 2026-08-05 flat_roof follow-up #2: user asked to keep the 7 fields from the SLOPE/EPS50/aerators
  revert (above) visible on sheet 01 after all, just not searched by extraction and not in
  `manual_values_registry.xlsx` — that registry is explicitly for project-independent universal
  defaults (its own docstring), while these are real per-project numbers from a supplier's КП
  (commercial proposal), a different kind of data entirely. Sheet 01 vs sheet 01-1 placement in
  `scalar_review_rows_for_contract()` is governed purely by `source_class` — anything in
  `MANUAL_VALUE_SOURCE_CLASSES = {MANUAL_REVIEW, SUPPLIER_INPUT}` goes to 01-1 regardless of which
  YAML section (`review_parameters`/`supplier_inputs`) declares it. Moved all 7 fields back into
  `review_parameters` with `source_class: AUTO_PROJECT`, `target_code: ""`, and an explicit
  `parser_mapping: {target_codes: [], ...}` (empty on purpose, with a note explaining there's no live
  PDF signal) so they render on sheet 01 but are never attempted by extraction; `action_ru` changed to
  "Заполните на основании КП от поставщика...". Re-ran `regenerate_manual_values_registry.py`:
  dropped exactly the 7 stale rows, added 0. Rebuilt workbook (`trc_review_workbook_2026-08-05_v10.xlsx`)
  — all 7 now show status "Проверьте" with the КП action text directly in the roof section of sheet 01.
- 2026-08-05 round-trip loop run #2 on TRC (rebuilt prompt pack from this session's work): fresh
  extraction (`gpt_trc_extraction(5).json`) → `build_extraction_notes_report.py` found 8
  `semantic_error` (3 thermal_insert double-counted with thermal_insert_items, 4 `wall_block_items`
  invalid `wall_role` values `partition`/`main`, 1 roof_zones vent-channel abutment flagged outside
  the zone) → correction prompt run in the same chat → `gpt_trc_extraction_corrected_05_08.json`.
  Re-ran the report on the corrected file: 7 of 8 genuinely fixed, but the roof_zones finding came
  back as **2** hits instead of 0. Investigated: this was a **false positive in the diagnostic check
  itself**, not a data problem — `is_roof_vent_abutment_item()` matched on raw_text containing
  "вентканал" without excluding items already tied to `roof_zones` (its own found/needs_review row,
  or a `raw_table_rows` component row whose `mapped_target_codes` already says it feeds
  `roof_zones`). The corrected data was actually 100% correct — `wall_abutment_length_m: 14.92`
  already equals the printed 9.5+5.42 components, both kept as diagnostic `raw_table_rows` for audit.
  Fixed `is_roof_vent_abutment_item()` in `build_extraction_notes_report.py` to exclude items with
  `group_code`/`target_code == "roof_zones"` or `"roof_zones" in mapped_target_codes`. Re-ran: 0
  `semantic_error` remaining. Lesson: the round-trip loop caught a bug in the *checker*, not just the
  *data* — worth remembering that a diagnostic re-firing after a claimed fix isn't automatically proof
  the fix failed; check the diagnostic's own logic first when the "still broken" data looks correct.

Next:

1. Run the next real chat extraction test with the rebuilt one-prompt pack.
2. Rebuild the review workbook from the new JSON and compare visible sheet 01/02 against the
   diagnostic notes report.
3. After the current TRC review is finished, test a correction loop:
   `extraction JSON -> build_extraction_notes_report.py -> same chat with PDFs already loaded ->
   corrected JSON -> repeated notes/validation report -> Google review workbook`.
   This is still the one-prompt chat extraction pipeline, not the closed `four_step_parsing_test`.
4. Only after the review workbook is stable, start adapter work section by section.

Guardrail:

Do not solve TRC by hardcoding TRC values or by using old project estimates as hidden sources.
TRC, ARK, and USV are test projects; production logic must stay universal.

## ARK Estimate Assembly Status (updated 2026-07-30)

If the user asks "что нужно, чтобы собрать смету по АРК", do not start from the old
2026-07-13 adapter note as if the review workbook builder were still missing. That note is
historical. Current state:

- `extraction_output.json -> review workbook` exists now:
  `populate_review_workbook_from_extraction.py`.
- It fills sheets `00`, `01`, `01-1`, `02`, `03`, `04`, `05`, `06`.
- Sheet `02` is filled from `output/price_registry_filled_v4.xlsx`.
- Sheet `01-1` is filled from `output/manual_values_registry.xlsx`.
- Current ARK workbook outputs already exist under
  `experiments/full_estimate_review_pipeline/output/ark_review_workbook_with_prices_v*.xlsx`.
- Important freshness check: on 2026-07-30 `output/price_registry_filled_v4.xlsx` was edited
  after `ark_review_workbook_with_prices_v5.xlsx`, so the next real ARK review workbook must be
  rebuilt before giving it to Elena or reading it into calculators.

What is still missing for a real ARK final estimate:

- choose/copy the canonical latest ARK extraction JSON into the repo run folder;
- rebuild the ARK review workbook from that JSON and the latest price/manual registries;
- audit required missing values and required blank prices before calculator run;
- write `review_to_calculator/sections/<section_code>/build_input.py` adapters;
- run each section calculator from the reviewed workbook;
- build a shared final estimate workbook from calculator `estimate_lines`.

Do not let sheet `03_Детали объемов` become a hidden data source during this work. Sheet 03 is
only evidence/control for Elena. Calculator inputs must come from sheet 01, sheet 01-1, sheet 02,
contract defaults, and explicit supplier/manual values.

## Missing Classification Gate (updated 2026-07-31)

Do not treat every parser `missing` target as a calculator blocker. The review workbook and notes
report now classify common all-project patterns before the adapter stage:

- `missing_confirmed_required` / "Не найдено — ОБЯЗАТЕЛЬНО" means a sibling field proves the
  construction exists, so the value must be filled before calculator input is built. Real example:
  monolithic lintel length exists, but combined concrete volume is missing because PDF gave only
  component rows.
- `not_required_alt` / "Не требуется (...)" means a legacy scalar is covered by production repeated
  rows such as `wall_block_items`, `pit_items`, `sand_items`, `communications_pipe_items`,
  `slab_zones`, or `thermal_insert_items`.
- `conditional_absent_ok` means the target is only needed when that construction exists in this
  project, for example floor-2 lintels or gas-block vent/chimney cladding.
- `diagnostic_only` means the parser can capture the row for future work, but the current smeta
  calculator must not require it.

The adapter must still fail loudly on `missing_confirmed_required` and real `missing` blockers. It
must not read sheet 03 to "fix" those values; the reviewed source remains sheet 01 / sheet 01-1 /
sheet 02 / defaults.

2026-08-02 update: `slab_zones` is live for `foundation_slab` and `floor_slab_1` only. The
`floor_slab_1` contract/calculator already consume it, and the review workbook can now show its sum
as `floor_slab_1_concrete_volume` when PDF has no printed total. Do not add `floor_slab_2_slab_zones`
until the floor_slab_2 calculator/adapter explicitly supports that repeated group.

2026-08-02 update: `experiments/chat_extraction_poc/coverage_audit/coverage_audit.py` classifies
never-mentioned targets/groups by severity. Current severities are `optional_absent`,
`legacy_ignored`, and `blocker_or_schema_gap`; default is the blocking/schema-gap class unless the
code is explicitly listed as optional/diagnostic. This prevents optional detail groups from looking
like production blockers in human reports.

2026-08-02 update: review workbook builders hide diagnostic/noisy sheets by default:
`03_Детали объемов`, `05_Кандидаты parser`, `06_Сырые данные parser`. They are still present in the
XLSX for developers, but not visible to Elena on first open. Applies to both the empty template
builder and extraction-populated workbook builder.

## Sheet 01/02/03 Rule (fixed 2026-07-09, read this before touching any section_contract.yaml)

**There is no `DETAIL_TABLE` source class and no separate "detail table" data source.**
It existed in this pipeline's schema/contracts from Step 2 onward and was removed on
2026-07-09 from the template and all 8 section contracts after the user caught it: it had
calculator adapters silently reading project quantities from sheet 03 instead of from the
reviewed sheet 01 row (confirmed as a real, live bug for earthworks
`communications_length_m`, not just a naming issue — see the fix in
`sections/earthworks/section_contract.yaml`). If you see `DETAIL_TABLE` anywhere (a stale
report, a half-finished branch, model memory from before this fix), it is wrong; do not
recreate it.

The rule, in one paragraph: **every piece of project data extracted from the PDF/chat JSON —
scalar or repeated-row group (rebar by diameter, trench routes, pipe items, beam items,
lintel items, ...) — is a row on sheet `01_Проверка проекта`, one row per value or per
repeated item.** All prices are rows on sheet `02_Цены себестоимости`. **The calculator input
adapter reads only from sheet 01 and sheet 02** (plus contract `defaults`/`supplier_inputs`,
which are not project data). Sheet `03_Детали объемов` is a **read-only reference mirror**:
the workbook builder may copy the same repeated-row groups onto it, formatted like the PDF
spec table, purely so Elena can eyeball it without opening the PDF — but it is generated FROM
sheet 01, Elena does not edit it as the primary correction surface, and the adapter must never
read it back as an independent input.

In `section_contract.yaml` terms:

- A repeated-row group is a `review_parameters` entry with `value_kind: repeated_rows` and a
  `columns:` list (not a separate `detail_tables:` block).
- `source_class` stays `AUTO_PROJECT` for repeated-row groups exactly like for scalars — it is
  still project data from the PDF, just shaped as multiple rows instead of one cell.
- Set `mirror_to_details_sheet: true` on entries that should also render on sheet 03 for
  convenience, with a `mirror_notes` field explaining that sheet 03 is a copy, not a source.
- `calculator_input_mapping` / `auto_calculated` / `estimate_lines` leaf inputs reference
  `review_parameters.<key>`, never `detail_tables.<key>`.

Known follow-up (not yet done as of 2026-07-09): `build_review_workbook_from_contracts.py`
still reads `contract.get("detail_tables")` in several places to populate sheet 03
(`build_review_workbook_from_contracts.py:311,507,573,600,615,627,689`). Now that no contract
has a `detail_tables` key, sheet 03 will render empty for what used to be detail tables until
the builder is updated to read `review_parameters` entries with `mirror_to_details_sheet: true`
instead. Fix the builder before assuming sheet 03 output is complete.

## Universal Production Rule

Every step must protect against project-specific contamination.

Allowed:

- source field names;
- formulas;
- source classes;
- unit normalization rules;
- calculator code paths;
- representative line counts used only for coverage checks;
- default/catalog values explicitly marked as defaults.

### Numeric Defaults Rule

Do not delete numeric defaults just because they are numbers.

For every numeric constant or coefficient in a calculator, first check the June Elena/manual review
materials and section reports (`elena_parameter_review_pack`, paid calculator change reports,
calculator README/report files). Then classify it:

- `AUTO_PROJECT`: project quantity from parser/chat JSON or reviewed workbook — scalar or
  repeated-row group, always a sheet-01 row (see the Sheet 01/02/03 Rule above; there is no
  separate detail-table class);
- `PRICE`: price registry/project price/reviewed price row;
- `DEFAULT`: formula default, method constant, business coefficient, or catalog/package value;
- `AUTO_CALCULATED`: derived by adapter/calculator/formula-ready;
- `SUPPLIER_INPUT`: external supplier layout/quote input;
- `MANUAL_REVIEW`: real human decision that is not a default and not in the project JSON.

Production contracts must keep confirmed `DEFAULT` numeric values when formulas require them.
Otherwise the calculator input adapter will produce incomplete inputs and formulas will fail.

Only remove or null a number when it is project-specific, fixture-only, an old expected total,
a display quantity copied from an old workbook, or a legacy override. If unsure, leave it out of
project extraction but document the uncertainty as `MANUAL_REVIEW` or `DEFAULT` pending confirmation;
do not silently drop a formula coefficient.

Forbidden in production contracts, adapters, review workbook builders, normalized JSON, and formula-ready builders:

- project-specific volumes, areas, lengths, counts, prices, totals, display quantities, page numbers, or filenames;
- copying values from old fixtures, old result JSON, old Excel snapshots, screenshots, or old parser outputs;
- hardcoded "expected total" or "Excel match" values;
- treating legacy reconstruction modes as production defaults when a specification/project value should be read from JSON;
- using any old project name as logic, filter, path convention, or data source.

Before committing any future step, run a text search for old project names and known fixture-only phrases in the files touched by that step. If a match remains, it must be either removed or explicitly documented as non-production reference evidence.

## Universalization Workstream (started 2026-07-18)

Customer explicitly asked to validate calculators/parser against several more real projects and make
the whole box-shell estimate system adaptive to different architectural/structural variations, not
tuned to one house. ЮСВ shaped the original 8 contracts; ТРЦ (2026-07-13..15) forced real optional
structure into `load_bearing_walls_lintels`/`waterproofing`; a third project (АРК) surfaced five more
rigid spots plus one correction to a rule derived from ТРЦ (D400/D500-by-block-width is a default, not
a hard constant).

Read, in this order, before touching any section_contract.yaml for this workstream:

- `reports/step_20_ark_third_project_stress_test.md` — structural findings, per section, with an
  explicit out-of-scope list (canopies, above-grade columns, windows, blind-area apron — all
  confirmed excluded 2026-07-18).
- `UNIVERSALIZATION_PLAN.md` (this directory) — the P1/P2/P3 prioritized checklist those findings
  drive. Update its checkboxes as items land; do not start a P2 item before its P1 prerequisites in
  the same section are done.
- `reports/step_21_ark_real_extraction_crosscheck.md` — the real chat-extraction pass against АРК
  (2026-07-18), crosschecked against step_20/the plan. Confirms every prediction in the plan (several
  turned out worse than the manual-PDF read suggested); adds two new P1/P2 items (both resolved by
  2026-07-19 after reading the actual calculator code — see the file for corrections).
- `reports/step_22_trc_real_extraction_audit.md` — a real chat-extraction pass against ТРЦ (2026-07-19,
  files supplied by the user), auditing whether ТРЦ is fully ready for the pipeline and how much of
  its remaining gaps the ARK-derived plan already covers. Most do; three plan items needed expanding
  (`slab_zones[]` scope, a new "source more aggregated than contract" rule, Schiedel shaft-count vs
  module-count). One finding — several КР2 pages carry a different project's title block — is a
  standing precondition requiring architect confirmation, not a code fix.

No contract edit from this workstream has shipped yet as of 2026-07-19 — real chat-extraction passes
against both АРК (step_21) and ТРЦ (step_22) are now done; next is P1 implementation with explicit
authorization before any calculator.py edit.

Since then (2026-07-20/21), the P1 calculator.py items have shipped (`wall_block_items[]`,
`slab_zones[]` for foundation_slab/floor_slab_1, `edge_and_beam_formwork_area_combined_m2` for
floor_slab_1) — see `UNIVERSALIZATION_PLAN.md` checkboxes and memory (`p1_wall_block_items_shipped`,
`p1_slab_zones_shipped`, `p1_floor_slab_1_combined_formwork_shipped`).

## Section-Within-Section & Capture Status (started 2026-07-22)

Read `SECTION_WITHIN_SECTION_AND_CAPTURE_STATUS_PLAN.md` (this directory) before touching
`populate_review_workbook_from_extraction.py`, `build_review_workbook_from_contracts.py`, any
`section_contract.yaml`, or the extraction prompt. Covers a verified, non-hypothetical problem: data
that's already captured in schema (`wall_block_items`, `foundation_wall_items`, `column_footing_items`
— partitions/columns/foundation walls) does not actually reach Elena on sheet 01 today (three
compounding bugs), and separately, a real extraction run mistagged partition rebar in a way that would
let it slip past the calculator's own guardrail and get silently priced as load-bearing-wall rebar.
Also defines the `capture_status` model (active/in_development/outside_schema, field-level granularity)
and a `future_section:*` tag for the Elena-approved roadmap of sections that don't exist yet (see
memory `future_estimate_sections_roadmap`). Nothing implemented yet as of 2026-07-22 — plan only.

## Wall/Lintel/Slab/Roof/Vent-Channel Findings — ARK/TRC/USV (started 2026-07-23)

Read `ARK_TRC_USV_WALL_ROOF_LINTEL_FINDINGS_PLAN.md` (this directory) before touching
`wall_block_items` roles, `slab_zones`, thermal insert fields, `lintel_groove_rebar_items`,
`floor_slab_1`/`floor_slab_2` formwork/insulation fields, `flat_roof`, or the D400/D500 vent-channel
rule. Living document, user-driven deep-dive comparing real ARK/TRC/USV project data category by
category (foundation walls, slab zones, thermal inserts, earthworks, partition waterproofing, lintel
subtypes, roof types/membrane brands, vent channels). Flags one direct conflict with the already-
finalized D400/D500 rule (needs Elena, not a unilateral reversal) and one unresolved open question
(Д1 embedded steel in ПМ1 — include with slab per section-within-section precedent, pending user
confirmation). Also the beam-subtraction-from-slab-concrete bug from `floor_slab_1_calculator.py`
(confirmed via real delivered smeta files for all three projects) lives in
`SECTION_WITHIN_SECTION_AND_CAPTURE_STATUS_PLAN.md`, not here — don't duplicate it.

## Reference Earthworks Flow

Start with:

- `experiments/full_estimate_review_pipeline/reports/step_01_earthworks_reference.md`

Earthworks reference files:

- review workbook: project-specific reference workbook, exact path documented only in the step report if needed for audit.
- review reader: `experiments/earthworks_review_to_calculator/review_workbook_reader.py`
- calculator input adapter: `experiments/earthworks_review_to_calculator/calculator_input_builder.py`
- calculator: `experiments/earthworks_calculator/earthworks_calculator.py`
- formula-ready builder: `experiments/earthworks_review_to_calculator/build_formula_ready_result.py`
- Excel export: `experiments/earthworks_review_to_calculator/export_formula_ready_to_excel.py`

Earthworks baseline counts:

- normalized parameters: 7
- price rows: 12
- detail groups: `trench_routes`, `communications_pipe_items`
- calculator estimate lines: 11
- formula-ready rows: 11
- helper cells: 27

Lesson: earthworks review input is small; the calculator/formula-ready layer expands it into estimate rows.

## Step Checklist

### Step 0 — Pipeline Architecture

- [x] Document the canonical pipeline:
  - chat extraction / parser output;
  - review Google workbook;
  - normalized review JSON;
  - calculator inputs;
  - calculator results;
  - formula_ready rows;
  - final estimate workbook.
- [x] State that review workbook and final estimate workbook are different entities.
- [x] State that review workbook checks inputs and final estimate workbook shows estimate rows.
- [x] State that the pipeline is universal and cannot depend on old project values.
- [x] Commit step 0 separately.

Step report:

- `reports/step_00_architecture.md`

### Step 1 — Earthworks Reference

- [x] Identify earthworks reference files.
- [x] Measure baseline counts.
- [x] List review parameters, price keys, detail groups, estimate lines.
- [x] Define guardrails for the next sections.
- [x] Mark the earthworks run as reference behavior, not production data.
- [x] Commit step 1 separately.

Step report:

- `reports/step_01_earthworks_reference.md`

### Step 2 — Common Section Contract Format

- [x] Design `section_contract.yaml` schema.
- [x] Include required blocks:
  - section metadata;
  - review parameters;
  - detail tables;
  - price keys;
  - defaults;
  - auto-calculated fields;
  - supplier inputs;
  - calculator input mapping;
  - estimate lines;
  - formula-ready/helper fields;
  - validation checks.
- [x] Create a report describing the schema and acceptance checks.
- [x] Do not yet implement every section.
- [x] Include project-specific contamination checks in the contract rules.
- [x] Commit step 2 separately.

Suggested report:

- `reports/step_02_section_contract_format.md`

Template:

- `templates/section_contract.template.yaml`

### Step 3 — All New Sections Quantity Matrix

- [x] Read calculators for 7 new sections.
- [x] Build "estimate line -> quantity formula -> leaf inputs -> source class" matrix.
- [x] Identify what must come from project, what is default/price/supplier/manual, and what is calculated.
- [x] Do not write new calculator code.
- [x] Flag old fixture/result values as audit evidence only, not production inputs.
- [x] Commit step 3 separately.

Step report:

- `reports/step_03_all_sections_quantity_matrix.md`

### Step 4 — Section Order

- [x] Choose low-risk section order.
- [x] Start with `earthworks` as reference behavior.
- [x] Use `waterproofing` as the first new contract.
- [x] Keep the hardest sections for later.
- [x] Commit step 4 separately.

Selected order:

1. `earthworks`
2. `waterproofing`
3. `schiedel_vent_channels`
4. `foundation_slab`
5. `floor_slab_2`
6. `floor_slab_1`
7. `flat_roof`
8. `load_bearing_walls_lintels`

Step report:

- `reports/step_04_section_order.md`

### Step 5 — WaterProofing Contract

- [x] Read `experiments/waterproofing_calculator/`.
- [x] Read `reports/step_03_all_sections_quantity_matrix.md`.
- [x] Create draft contract for `waterproofing`.
- [x] Run contract checks manually in the report.
- [x] Commit step 5 separately.

Suggested files:

- `sections/waterproofing/section_contract.yaml`
- `reports/step_05_waterproofing_contract.md`

### Step 6 — Earthworks + Waterproofing Review Workbook Prototype

- [x] Reuse earthworks reference behavior without rewriting it blindly.
- [x] Build a review workbook from section contracts for `earthworks + waterproofing`.
- [x] Keep review workbook separate from final estimate workbook.
- [x] Verify sheet counts and key rows.
- [x] Commit step 6 separately.

Builder:

- `build_review_workbook_from_contracts.py`

Local workbook:

- `output/step_06_earthworks_waterproofing_review.xlsx`

Step 6 builds the local `.xlsx` review workbook from contracts. Publishing that workbook to a real Google Sheet is the next separate checkpoint, and downloading it back after Elena edits is the checkpoint after that. The downloaded workbook is the source of truth for normalized review JSON and calculator inputs. Hidden technical columns must survive, but the main check is that visible user corrections are read from the downloaded Google Sheet and used by calculators.

Do not merge these checks:

1. local workbook builder check;
2. Google publish check;
3. downloaded edited workbook -> normalized JSON -> calculator input check.

Step report:

- `reports/step_06_earthworks_waterproofing_review_workbook.md`

### Step 7 — Multi-Section Normalized Review JSON

- [ ] Read prototype workbook.
- [ ] Produce normalized JSON shaped by section:

```json
{
  "sections": {
    "earthworks": {},
    "waterproofing": {}
  }
}
```

- [ ] Prove that manual overrides are preserved.
- [ ] Commit step 7 separately.

### Step 8 — Waterproofing Review-To-Calculator Adapter

- [ ] Convert normalized waterproofing review data into calculator input.
- [ ] Add defaults and prices deterministically.
- [ ] Run existing waterproofing calculator.
- [ ] Commit step 8 separately.

### Step 9 — Waterproofing Formula-Ready

- [ ] Convert waterproofing calculator result into formula-ready rows.
- [ ] Each estimate line must have quantity, prices, formula model or explicit reason.
- [ ] Formula-ready row count must match calculator estimate line count.
- [ ] Commit step 9 separately.

### Step 10 — Repeat Section By Section

Recommended order:

- [ ] `schiedel_vent_channels`
- [ ] `foundation_slab`
- [ ] `floor_slab_2`
- [ ] `floor_slab_1`
- [ ] `flat_roof`
- [ ] `load_bearing_walls_lintels`

Each section gets its own contract, adapter, formula-ready report, and commit.

## Cross-Check Stage — Section Contract vs Real Extraction JSON (No Value Leakage)

Use this stage when the user says "проверяем контракт по [раздел] на реальных данных" or
"сверяем со сметой [проект]", or when resuming a chat that stopped mid cross-check.

### Why this stage exists

`sections/*/section_contract.yaml` files (through `foundation_slab`, `flat_roof`,
`load_bearing_walls_lintels`, `floor_slab_1`, `floor_slab_2`, `schiedel_vent_channels`,
`waterproofing`, `earthworks` — see `reports/step_05..step_12`) were drafted from calculator
source, calculator docs, `docs/elena_parameter_review_pack_audit.md`, and
`experiments/chat_extraction_poc/data/{calculator_targets_compact.json,target_aliases_ru.yaml}`.
They were never checked against a real per-project chat/parser extraction JSON. This stage closes
that gap, one finished real-project estimate at a time, without repeating the earthworks mistake
(project-specific numbers silently becoming pipeline expectations — see the Universal Production
Rule above and `reports/step_03b_production_contamination_audit.md`).

Scope: cost-basis ("себестоимость", the internal/grey estimate) only. The client-facing
white/markup part of the estimate is out of scope for this stage entirely.

### What the user provides

A finished, hand-built real-project estimate for one section (screenshot or pasted rows: label +
unit, sometimes a value) for a project this pipeline has real chat-extraction JSON for (currently
ЮСВ, `experiments/chat_extraction_poc/`). The estimate was built by hand by an estimator and is
**not** an automated pipeline output — it is only used here as a source of real row labels/units to
cross-check contract coverage, never as a target value.

### What the assistant does per row

1. Find the matching field in the section's calculator (`experiments/<section>_calculator/*.py`)
   and in `sections/<section>/section_contract.yaml`. If nothing matches, say so explicitly — that
   is a real finding, not a search failure.
2. Classify/confirm its `source_class` per the enum already used in section contracts:
   `AUTO_PROJECT`, `DEFAULT`, `AUTO_CALCULATED`, `PRICE`, `SUPPLIER_INPUT`, `MANUAL_REVIEW`.
   A repeated-row group (rebar by diameter, trench routes, pipe items, ...) is still
   `AUTO_PROJECT` — see the Sheet 01/02/03 Rule above, there is no separate detail-table class.
   Add a `ZERO_STRUCTURE_LINE` case for rows that exist only as an empty Excel-structure
   placeholder filled in by hand after export (confirmed pattern in
   `foundation_slab_calculator.py`, `floor_slab_2_calculator.py`, `flat_roof_calculator.py` for
   "Технический надзор" / "Заготовительно-складские расходы" / "Накладные и общехозяйственные
   расходы" / "Сметная прибыль" — earthworks has none of these four rows at all, not even as a
   placeholder).
3. If `source_class` is `AUTO_PROJECT` (scalar or repeated-row group), check whether a matching
   `target_code` / `group_code` actually exists in the real project's chat-extraction JSON
   (`experiments/chat_extraction_poc/outputs/*.json` when present). Report found / not found /
   found-but-wrong-shape. This is the check that matters: can the parser realistically supply this
   field on a real project, not just in the contract's own `parser_mapping.aliases_ru` guess.

### Hard rule: no project values in any written file

The output of this stage is **only**:

- confirmed/corrected `source_class`;
- confirmed/corrected `parser_mapping` (target codes, aliases, expected unit);
- found/not-found verdict against the real extraction JSON;
- missing calculator/contract coverage (row exists in the real estimate, nothing matches it in the
  contract or the calculator).

A literal number from the user's real project (81, 320, 18.29, etc.) may appear **only inside the
chat turn itself**, to let the assistant locate the right field. It must never be written into
`section_contract.yaml`, a `reports/*.md` file, or any other file in this repo — not even in a
scratch file "to delete later". If the assistant needs working notes across several rows in one
session, keep them in the chat, not in a file. Do not create a temporary/scratch file for this at
all; there is nothing in it that survives the session except the structural findings above, and
those go straight into the real report/contract.

### Naming Alignment Rule (fixed 2026-07-09 — read this before "fixing" any target_code mismatch)

When a cross-check finds that the contract's `parser_mapping.target_codes` (or a repeated-row group's
`columns` keys) don't match what the parser actually emits, **do not build a translation/bridge inside
the contract.** Rename the parser-side files instead
(`experiments/chat_extraction_poc/data/target_aliases_ru.yaml`,
`data/calculator_targets_compact.json`, `schemas/claude_extraction_output_schema.json`, and the prompt
if it names the field explicitly) so the parser's `target_code`/field names become **identical** to
the calculator's real dataclass field names for that section. After the fix, within one section:
`section_contract.yaml`'s `calculator_input_path` == its `parser_mapping.target_codes` == what the
parser actually outputs — no separate "bridge" name anywhere.

**Never rename a calculator's own field names to fix this.** Calculators are tested, working
financial-calculation code; renaming their fields is a real code change with real risk, not a
config/schema edit. If the calculator's name is awkward or inconsistent with another section, that's
a separate, deliberate future cleanup (see the naming-divergence note below), not something to fix as
a side effect of a cross-check.

This replaces the earlier, inconsistent approach (see `step_13`'s `membrane_area_m2` finding, fixed
by editing the contract, versus its `foundation_rebar_items` finding, fixed by editing the parser) —
going forward, always fix the parser side, for every section, no exceptions decided case by case.

**Fact, not a bug, to keep in mind while doing this**: different section calculators were built
independently and do **not** use one shared name for the same physical material/process across
sections — e.g. rebar's "length from spec" field is `source_length_m` in `foundation_slab_calculator.py`
but `spec_length_m` in `floor_slab_1_calculator.py`, `floor_slab_2_calculator.py`, and
`load_bearing_walls_lintels_calculator.py`. This means the parser's canonical field name for "rebar
length from spec" legitimately differs per section-specific extraction group
(`foundation_rebar_items` vs `floor_slab_1_rebar_items` etc.) — don't assume one group's fix applies to
another by analogy; verify each calculator's real field names independently. A shared naming
dictionary/catalog across all calculators (one name per physical concept, everywhere) would be a good
future cleanup, but is out of scope for now — it means touching tested calculator code across every
section, not a config-only change like the fixes in this stage.

### Where findings land

- Structural corrections to an existing section: edit `sections/<section>/section_contract.yaml`
  directly (only `source_class`, `parser_mapping`, `notes` fields — never add a `default_value` or
  `example` populated with a real project number). Per the Naming Alignment Rule above, most naming
  fixes actually land in the parser-side files, not the contract.
- A running log of the cross-check itself (what was checked, what didn't match, what's missing
  entirely from the contract or calculator): `reports/step_13_<section>_extraction_crosscheck.md`
  (bump the number per section if more than one cross-check report is open at once).

### Order

Start with `foundation_slab` (has a contract already — step 8 — but zero real-JSON cross-check).
Then repeat per section in the Step 10 order once foundation_slab is done. `earthworks` and
`waterproofing` are also in scope for this stage even though they aren't in the Step 10 list (they
were built earlier, in steps 1/5/6, before this stage existed) — see `reports/step_15_*` for
earthworks and `reports/step_16_waterproofing_extraction_crosscheck.md` for waterproofing. Do the
cross-check itself before the Step 11 migration below; the migration should build on a contract
that's already been checked against parser/calculator names, not the other way round.

## Step 11 — Earthworks Migration Off Its Own Hardcoded Pipeline

- [ ] Read `experiments/earthworks_review_to_calculator/*.py` and
      `experiments/earthworks_parser_google_stage1/google_sheets/review_workbook_builder.py` in full;
      confirm exactly which pieces are earthworks-hardcoded (`PARAM_META`, `SUMMARY_RULES`, and
      similar dicts) versus reusable logic.
- [ ] Finish Step 15's earthworks Cross-Check first (`reports/step_15_earthworks_extraction_crosscheck.md`)
      so the contract itself is correct before anything is built on top of it.
- [ ] Build (or extend `build_review_workbook_from_contracts.py` with) a real extraction-JSON ingestion
      path — this does not exist yet for any section (see the "no extraction-JSON input" gap noted for
      `build_review_workbook_from_contracts.py`'s `parse_args`/`build_project_sheet`), earthworks
      migration depends on it same as every other section eventually will.
- [ ] Replace `calculator_input_mapping.transform: earthworks_review_to_calculator_adapter` in
      `sections/earthworks/section_contract.yaml` with the same generic
      `review_parameters + defaults + price_keys -> calculator input` mapping style used by the other
      7 contracts, once the generic adapter can actually produce it correctly (regression check
      against the existing hardcoded flow's known-good output before retiring it).
- [ ] Only after the generic path is proven equivalent: retire/archive the earthworks-specific scripts,
      update `section.status` in the contract away from `reference_ready`, and update the "Reference
      Earthworks Flow" section above (it currently documents the old flow as canonical).
- [ ] Commit step 11 separately.

Not started. Recorded 2026-07-09 per explicit user decision to stop treating earthworks as a permanent
special case and bring it onto the same contract-driven path as the other 7 sections.

## Guardrails For Every Step

Before marking a step complete, run these checks mentally and, where possible, with scripts.

### 1. Workbook Role Check

Question: Am I building a review workbook or a final estimate workbook?

Fail if a review row is treated as a final estimate line without passing through calculator/formula-ready.

### 2. Source Class Check

For each leaf input and numeric coefficient, confirm its source class against the June Elena/manual
review materials before removing it from the contract.

Ask:

- Is this value extracted from the new project JSON?
- Is this value a price?
- Is this value a formula default/catalog package/business coefficient that formulas need?
- Is this value calculated downstream?
- Is this value a real manual/supplier decision?
- Is this value only an old project fixture or expected-total artifact?

Fail if a required formula coefficient is dropped just because it is numeric.

Every leaf input must be one of:

- `AUTO_PROJECT` (scalar or repeated-row group — see the Sheet 01/02/03 Rule; there is no
  separate `DETAIL_TABLE` class)
- `DEFAULT`
- `AUTO_CALCULATED`
- `PRICE`
- `SUPPLIER_INPUT`
- `MANUAL_REVIEW`

Fail if the source is "kind of from somewhere".

### 3. End-To-Start Trace Check

For every estimate line:

```text
estimate line -> quantity formula -> leaf inputs -> source class
```

Fail if quantity formula or leaf inputs are missing.

### 4. Adapter Check

There must be a deterministic path:

```text
review workbook -> normalized JSON -> calculator input
```

Fail if the calculator input is manually copied from old fixture JSON.

### 5. Calculator Check

The existing calculator for the section must run from generated input.

Fail if the section bypasses the calculator.

### 6. Formula-Ready Check

Every calculator estimate line must appear in formula-ready.

Fail if:

- calculator result has N lines;
- formula-ready has a different count;
- and the difference is not explicitly explained.

### 7. Price Check

Every price used by a calculator line must have a `calc_price_key` or explicit zero/fixed reason.

Fail if price mapping depends only on a Russian row label.

### 8. Project-Specific Contamination Check

Question: can this step run from a fresh chat/parser JSON for a different project?

Fail if touched production files contain:

- old project names or old job path fragments;
- fixture-only values copied as quantities, totals, display quantities, or prices;
- hardcoded expected totals used to force old Excel equality;
- old parser/page/table evidence treated as a universal rule.

Allowed only in reports: old project references used to explain why a legacy calculator mode is risky. They must never become contract defaults or adapter output.

### 9. Dirty Worktree Check

Before commits:

```bash
git status --short
```

Only stage files from the current step. Do not use `git add .` in this repo unless the user explicitly asks and the diff was reviewed.

## Commit Policy

Commit each accepted step separately.

Suggested commit messages:

- `docs(full-estimate): record earthworks reference contract`
- `docs(full-estimate): define section contract format`
- `docs(full-estimate): map section quantity sources`
- `feat(full-estimate): add waterproofing section contract`
- `feat(full-estimate): build earthworks waterproofing review workbook`

Before committing:

1. Run `git status --short`.
2. Stage only current-step files.
3. Run `git diff --cached --stat`.
4. Commit.
5. Tell the user the commit hash and what was included.

## Current State

Completed (checklist above under-reports this — verified against files on disk):

- Steps 0–3b as listed in the checklist.
- Draft `section_contract.yaml` now exists for all 8 sections: `earthworks`, `waterproofing`,
  `schiedel_vent_channels`, `foundation_slab`, `load_bearing_walls_lintels`, `floor_slab_1`,
  `floor_slab_2`, `flat_roof` — see `reports/step_05..step_12`.
- Local review-workbook prototypes were built and re-built incrementally through step 12
  (`output/step_06_*.xlsx` .. `output/step_12_all_sections_review_template.xlsx`), each adding one
  more section's contract into the combined workbook.
- The formal Step Checklist above (steps 6–10 checkboxes) was not kept in sync with this work —
  treat the checkboxes as stale and the `reports/` + `sections/` file list as the source of truth
  for what's actually done.
- Cross-check reports now exist for `foundation_slab`, `earthworks`, and `waterproofing`
  (`reports/step_13_*`, `reports/step_15_*`, `reports/step_16_*`). Treat each report's scope
  carefully: some checks are against real extraction JSON, some are structural parser/contract/
  calculator-name checks. The remaining sections still need the same pass.

2026-08-05 update: Этап 1 of `review_to_calculator/ADAPTER_BUILD_PLAN.md` is now DONE — the
first-ever working review-workbook-to-calculator-result path exists, for `waterproofing`:
`sections/waterproofing/build_input.py` written, run end to end (`workbook_reader.py` →
`price_resolver.py` → `build_calculator_input()` → `WaterproofingInput.from_dict()` →
`calculate_waterproofing()`), 0 mismatch against `cases/test_waterproofing_spec_area/
expected.json` (calculation_blocks AND estimate_lines both compared programmatically). Also
fixed a real latent column-position bug in `core/workbook_reader.py` (stale N-Q+R from a
13-column sheet 01, current layout is O-R+S — didn't affect waterproofing since it has no
repeated_rows groups, but would have silently broken every section with rebar/beams) and added
`read_project_name()` (sheet 01's own title, previously not read by `core/` at all). See
`ADAPTER_BUILD_PLAN.md`'s Этап 1 section for the full writeup. Also closed the one open
contract gap found along the way: `eps50_pack_volume_m3` default was `None` in both
`waterproofing` and `foundation_slab` — checked 3 real delivered estimates (АРК для ИИ.xlsx,
Сметный расчет ЮСВ, ТРЦ_3_точный_расчет), Пеноплэкс ГЕО pack volume is identically 0.2776 m3
for both 50mm and 100mm layers in every case (same physical package, different board count).
Filled into both contracts; pilot re-verified end to end via `core.job_runner.run_section()`
with zero manual patches — still 0 mismatch.

2026-08-05 update #2: `earthworks` adapter (`sections/earthworks/build_input.py`) also done —
second section, more involved than waterproofing (4 fixed `*_calc_method` production defaults,
2 real production repeated_rows groups `pit_items`/`sand_items`). Verified on 2 scenarios via
`core.job_runner.run_section()`, 0 mismatch both times: one exercising `pit_items`/`sand_items`
with `trench_volume_m3` as a pre-summed scalar (60.1 = sum of the same case's 4 `trench_routes`,
matching how the review-workbook layer already surfaces this — the adapter never reads
`trench_routes` directly, it's `production_input: false`), one pure-scalar path with no repeated
rows at all. Found AND FIXED (explicit user authorization) a real pre-existing calculator quirk:
`earthworks_calculator.py`'s `validate()` used to always require `pit_excavation_depth_m`
non-None in `standard_volume_productivity` mode even when `pit_items` already gives volume
directly and the actual formula never touches depth in that branch. Now only required when
`pit_items` is empty. All 9 `earthworks_calculator` regression cases still pass unchanged; new
manual check confirms the previously-failing scenario (pit_items given, depth None) now computes
cleanly. See `ADAPTER_BUILD_PLAN.md`'s Этап 2 section for full writeup.

2026-08-05 update #3: `schiedel_vent_channels` adapter also done (third section; plain-dict
calculator input, no dataclass). Three real gaps found and fixed along the way: (1) contract's
`price_keys` only covered 2x/3x channel types, missing 1x/4x/cvent + D400/D500 masonry gas
block prices even though real projects already use them (TRC uses 1x, ARK uses 4x) — added the
5 missing entries; (2) `schiedel_masonry_gas_block_items[]` was never declared in
`review_parameters` at all despite the calculator already reading it and a prior memory note
claiming it shipped — added, mirroring `schiedel_channel_items`; (3) a real cross-section bug in
`core/workbook_reader.py`: fields with `source_class: MANUAL_REVIEW`/`SUPPLIER_INPUT` (like
`schiedel_delivery_trips`) render on sheet 01-1, not sheet 01, but nothing ever read sheet 01-1
— this affects every section with required manual/supplier fields (crane shifts, concrete pump,
waste removal trucks - the same 12-field list surfaced earlier this session), not just this one.
Added `read_manual_values()`, merged into the same dict `read_scalar_parameters()` returns so
every existing `build_input.py` keeps working unchanged. Verified end to end on real TRC numbers
(`test_schiedel_vent_channels_trc`) — 0 mismatch; re-verified waterproofing and earthworks still
0 mismatch after the core/ fix.

2026-08-05 update #4: `foundation_slab` adapter also done (fourth section, most involved so
far). First adapter with a *dynamically* chosen mode: `thermal_insert_mode` is "items" when
`thermal_insert_items` has real rows on sheet 01, else the contract's fixed
"standard_50_100" default — every other `*_calc_method` in this pipeline so far has been a
single fixed default. Also the first use of `core/`'s new per-item "template" price
mechanism (`template_price_keys()`/`read_prices()` in `core/workbook_reader.py`,
`resolve_prices()` in `core/price_resolver.py`, added specifically to unblock this adapter):
sheet 02 expands the contract's single `rebar_unit_price_by_item` key into one real row per
steel_class/diameter_mm actually in the project, and `resolve_prices()` now returns
`{price_registry_code: price}` for such keys instead of a single float. Needed by 3 more
future sections with rebar items: floor_slab_1, floor_slab_2, load_bearing_walls_lintels.
Two real adapter bugs found and fixed while verifying: (1) the generic "everything else from
`defaults` by key name" fallback loop was blindly copying `rod_length_m` (a per-item catalog
default, `calculator_input_path: "rebar_items[*].rod_length_m"`, not even a
`foundation_rebar_items` column — PDFs never give it) as a flat top-level field, crashing
`FoundationSlabInput.__init__()`; fixed by skipping any default with `[` in its
`calculator_input_path` in the generic loop, injecting it per-item instead (with
`item.setdefault()` so a row can still override); (2) `build_input.py` never read
`supplier_inputs:` at all (6 fields: crane/pump shifts, delivery trucks, box metal weight,
2 legacy fixed-amount fields) — `FoundationSlabInput` has no dataclass default for any of
them, so this would have crashed on every real run. Fixed by reading `all_supplier_inputs(contract)`
explicitly from `scalars` (already merges sheet 01 + 01-1 since the schiedel-adapter core/
fix), defaulting `required: false` legacy fields to 0. Verified via
`core.job_runner.run_section()` against an independently-built reference (direct
`calculate_foundation_slab()` call) — 0 mismatch across all 30 estimate lines,
`calculation_blocks`, `internal_totals`, warnings, once the reference's own stale
fixture-vs-current-contract-default drift (`concrete_waste_coeff`, `concrete_mixer_volume_m3`,
`thermal_insert_50/100_pack_multiple_qty`, `logistics_and_supply_calc_method`,
`consumables_tool_amortization_calc_method`) was corrected to match. See
`ADAPTER_BUILD_PLAN.md`'s Этап 2 section for the full writeup.

2026-08-05 update #5: `floor_slab_2` adapter also done (fifth section). Plain-dict calculator
input (no dataclass, like schiedel), second user of foundation_slab's per-item template
rebar-pricing mechanism. Nothing dynamically chosen here — the contract doesn't even declare
the alternative calc_method modes (legacy_dimensions, edge_and_beam_formwork_area_combined_m2,
legacy_weight_kg) as review_parameters, so the adapter only ever exercises the single
production path. Two section-specific things worth remembering: (1) `beam_items` maps to
`beams: {"items": [...]}`, not a flat `beam_items` key — this section's own
`calculator_input_path` is literally `"beams.items"`, easy to miss by analogy with every other
repeated_rows group in this pipeline, which map 1:1 to their own top-level key; (2)
`formwork_rental_supplier_quote_total` is AUTO_CALCULATED but never actually populated
anywhere in the codebase (Elena never sees it - `show_to_user: false`), yet the calculator
requires it unconditionally; the contract's own notes explicitly authorize synthesizing it as
`main_formwork_area_m2 * formwork_rental_used_rate_per_m2` since it only feeds a
self-comparison ratio, never a real estimate line. Verified via `core.job_runner.run_section()`
against an independently hand-built reference (not a reused fixture, and not a re-run of the
adapter's own output) — 0 mismatch. Also surfaced a pure test-construction gotcha (not a
product bug - the real pipeline scripts never call `insert_rows()` at all, confirmed by
`grep`): `openpyxl`'s `insert_rows()` shifts cell content but not merged-range XML
declarations, so inserting rows before a merged group-title row silently loses data in that
row's cells on the next file load unless you unmerge before inserting and re-merge after, in
one session, before saving. See `ADAPTER_BUILD_PLAN.md`'s Этап 2 section for the full writeup.

2026-08-05 update #6: `floor_slab_1` adapter also done (sixth section) — the first calculator
in this pipeline whose input is namespaced into sub-dicts (`geometry.*`, `insulation.*`,
`rates.*`, `overheads.*`, `manual_lines.*`) rather than a flat dict. The contract's own
`calculator_input_path` already encodes these dotted paths, so the adapter reads them
generically via a new `_set_nested()` helper instead of hand-coding which sub-dict each of
~35 fields belongs to — a reusable pattern for any future namespaced section. Two real
contract gaps found only by actually running the calculator (not by reading the contract):
(1) no `rebar_waste_coeff` default existed at all (unlike every other rebar-bearing section),
yet `calculate_rebar_item()` reads `item["waste_coeff"]` unconditionally — added the missing
default (1.05, matching foundation_slab/floor_slab_2) with explicit authorization, injected
per-item like foundation_slab's `rod_length_m`; (2) `calculate_rebar_item()`'s
`spec_length_items` branch also hard-requires `item["component"] == "floor_slab_1"` and
`item["floor"] == 1` — structural constants, not real PDF data — so the adapter force-sets
them on every row rather than trust extraction; (3) `geometry.slab_control_geometry_area_m2`
is required unconditionally but was never declared anywhere in the contract — confirmed by
reading every usage that it's purely a diagnostic echo, never touches money, and per explicit
user decision the adapter mirrors `main_formwork_area_m2` into it (no separate PDF signal
exists for a distinct control area). Verified via `core.job_runner.run_section()` against an
independently hand-built reference — 0 mismatch, including exact match on all 3 warnings
produced by the deliberately-imperfect test data. See `ADAPTER_BUILD_PLAN.md`'s Этап 2 section
for the full writeup.

2026-08-05 update #7: `flat_roof` adapter also done (seventh section) — plain-dict, no
namespacing at all (unlike floor_slab_1, every field is top-level). Fixed production
calc_methods: `roof_geometry_calc_method=roof_zones` (plus 4 `section_*_rate` overhead
methods), nothing dynamic. Two real gaps found only by running the calculator: (1) the same
class of bug as floor_slab_1's `slab_control_geometry_area_m2` but on 7 fields at once -
`roof_area_level_1/2_m2`, `project_spec_roof_area_m2`, `parapet_length_level_1/2_m`,
`vent_wall_abutment_level_1/2_m` are all `required: false` (fallback-only for the legacy
`detailed_project_geometry` mode) yet the calculator's result-building code reads all 7
unconditionally for a diagnostic report block; per user decision the adapter defaults all 7
to 0 when absent; (2) a real `core/` bug, not adapter-specific:
`template_price_keys()` in `core/workbook_reader.py` flagged ANY `"<"` in a price's
`registry_code` as the rebar per-item template pattern, which wrongly caught flat_roof's
`slope_plate_unit_price_per_m3` (`registry_code: "roof_eps_slope_<type>_m3"` - a
documentation-style placeholder, not a real expansion; sheet 02 only ever has one row for it,
the calculator reads 4 separate top-level fields
`slope_plate_a/b/j/k_unit_price_per_m3` built via f-string, all sharing one reviewed price per
the contract's own note). The false positive made `resolve_prices()` return a
`{registry_code: price}` dict instead of a float AND silently skip the "required price
missing" check (template keys are deliberately exempt from it). Grepped every
`section_contract.yaml` in the pipeline - this was the only false positive, every other `<...>`
is the genuine rebar `<class>`/`<diameter>` pattern. Fixed by narrowing the detection to
require both `<class>` and `<diameter>` together; re-verified detection is still correct
across all sections with `<...>` in any registry_code (4 rebar-bearing sections still detect
`rebar_unit_price_by_item`, flat_roof detects nothing). Verified via
`core.job_runner.run_section()` against an independently hand-built reference - 0 mismatch.
See `ADAPTER_BUILD_PLAN.md`'s Этап 2 section for the full writeup.

2026-08-06 update #8: `load_bearing_walls_lintels` adapter done - the eighth and last section
of Этап 2, and the hardest: a typed dataclass (like foundation_slab/waterproofing/earthworks,
not plain-dict) with 12 `*_calc_method` fields (memory previously said "9" - an undercount,
now corrected), but fully flat, no namespacing at all (unlike floor_slab_1 - not even a
`rates.` prefix on prices). All 12 calc_methods are fixed contract defaults, nothing chosen
dynamically. One real design decision worth remembering: `flat_roof_enabled` is an
AUTO_CALCULATED system flag Elena never sees and nothing ever populates; the contract's own
note says to derive it from whether parapet/vent-chimney project data is present, so the
adapter sets it `True` when any of `parapet_masonry_volume_m3`/
`parapet_gas_block_d500_250_spec_volume_m3`/`vent_chimney_gas_block_spec_volume_m3` has a
real value. Found two already-self-documented dead contract entries needing no fix
(`floor_1/2_lintel_formwork_plywood_qty`/`timber_volume_m3` point at dataclass fields removed
from the calculator 2026-07-25; their own notes already say "hidden... pending re-wiring
check" - adapter simply never reads them, since passing them would raise TypeError on
construction). `main_wall_rebar_items`/`lintel_rebar_items` carry real `floor`/`component`
extraction columns (unlike foundation_slab's `rod_length_m` default), but `component` is
still force-set per group (structural constant within each group,
`validate_spec_rebar_item()` hard-fails on mismatch) - same defensive pattern as floor_slab_1,
applied per-group instead of per-section. Verified via `core.job_runner.run_section()` on a
test workbook exercising floor_2 masonry, both U-block and monolithic lintels on floor 1,
parapet + vent-chimney cladding (triggering `flat_roof_enabled=True`), and deliberately-wrong
`component` values in the rebar rows (to prove the forced correction works) - compared against
an independently hand-built reference (built completely from scratch, not reusing the
adapter's own output) - 0 real mismatches across all 40 estimate lines and `internal_totals`.
See `ADAPTER_BUILD_PLAN.md`'s Этап 2 section for the full writeup.

**Этап 2 is now fully complete** - all 8 sections have a working, verified `build_input.py`:
`waterproofing`, `earthworks`, `schiedel_vent_channels`, `foundation_slab`, `floor_slab_2`,
`floor_slab_1`, `flat_roof`, `load_bearing_walls_lintels`.

Next:

- Continue Cross-Check Stage for the remaining sections, per the no-value-leakage rule.
- Этап 2 is done. The next major piece of the canonical pipeline (chat extraction → review
  workbook → normalized review JSON → calculator input → calculator result → formula-ready
  rows → final estimate workbook) is Step 9: the shared final-estimate-workbook exporter that
  combines all 8 sections' `estimate_lines` into one actual smeta. Still not built at all.
  Building this is the natural next step now that every section can be turned into a
  calculator result on its own.

Do not start coding all remaining sections' adapters at once — one at a time, verified
against that section's own `cases/*/expected.json` (or an independently-built reference, when
no clean fixture matches production defaults) before moving to the next, same as the
waterproofing pilot.

## Current Note 2026-08-04: flat roof vent-channel abutments

For flat roof production geometry, `roof_zones[]` is the live source when present. Linear roof
abutments to walls, VK, vent channels, and vent shafts in linear meters belong in
`roof_zones[].wall_abutment_length_m` for the matching roof zone.

Do not keep `roof_vent_wall_abutment_level_1/2` as a parallel live value when `roof_zones[]` exists;
those fields are fallback only. Do not map linear meters to `vent_shaft_abutment_count`, which is a
hidden optional per-piece special-case field. Do not move roof abutment lengths to Schiedel; Schiedel
is for vent-channel masonry/items, not PVC roof abutment work.

`build_extraction_notes_report.py` now raises a semantic diagnostic if a JSON has `roof_zones[]` and
also leaves a linear VK/vent-channel abutment outside the zone rows.

## OPEN 2026-08-07: earthworks manual excavation depth rule — waiting on Elena, do not implement yet

Comparing our built TRC final estimate against her real TRC smeta line-by-line found
`calculate_manual_excavation_total()` in `earthworks_calculator.py` overstates manual excavation
(94.782 m3 built vs 34 m3 real) because it has NO machine/manual split for trenches at all - the
full volume of every `trench_routes[]` item is always treated as 100% hand-dug. Pulled real Excel
formulas from TRC/ARK/USV smeta files: all three actually split trench volume by network group,
each group getting its OWN "manual depth" coefficient (shallower than the trench's real total
depth) - the excavator handles most of the depth, hand-digging only finishes the remainder below
the already-excavated pit floor. Confirmed against the real TRC project PDF (`КР-1_ТРЦ
_01,07,2026.pdf`, page 7 "План котлована") that pit depth (0.5m) and per-network design depths
(К1=0.4m, К2=0.5m, ЭО=0.9m, В1=1.9m) are real project values, matching our own extracted numbers
exactly - but the machine/manual SPLIT coefficient itself isn't drawn on any project page in any
of the 3 reference projects, and differs between TRC (0.6/1.0/1.6/0.7m by group) and USV
(0.2/0.2/1.6/0.6m by group). Question sent to Elena 2026-08-07 (see
`open_question_manual_excavation_depth_rule` memory) asking how she decides the split. **Do not
redesign `calculate_manual_excavation_total`/`calculate_excavator_shifts` or add a `manual_depth_m`
field to `trench_routes[]` until she answers** - her answer determines whether this is a simple
formula (real depth − pit depth) or a judgment call needing a manual per-project input instead.

Separately found (and this part IS a fixable bug, unblocked): TRC's extraction has two near-duplicate
routes both labeled "К2, К3" - checked the real project PDF and found К3 is actually a completely
different network (Дренажная гофротруба ф110 с перфорацией, perimeter drainage), visually matching
the longer of the two routes (74.56m, follows almost the whole building perimeter on the drawing).
Elena confirmed this is a designer's labeling slip, not something that belongs in earthworks trench
calculations at all. User will exclude it (set the correction column for that row's `volume_m3` to 0
on sheet 01) on the next parser/workbook rebuild.

## Current Note 2026-08-06: `gas_block_wall_hole_drilling` removed from `flat_roof`

While building a real estimate from the TRC project's Google Sheets review workbook (goal:
zero unresolved/"red" prices on sheet 02), `gas_block_wall_hole_drilling_rate` turned up with
no price anywhere in Elena's registry and no matching line in any of the 3 real reference
smetas (TRC/ARK/USV). Elena's own 2026-07-30 note on this field already called it a rare
special-case ("not a standard work item except exceptional projects"), so instead of sourcing
or faking a price for a feature with zero real-world usage, the user asked to remove it
outright.

Removed 3 entries from `sections/flat_roof/section_contract.yaml`: the
`gas_block_wall_holes_count` supplier_input, the `gas_block_wall_hole_drilling_rate` price_key,
and the `gas_block_wall_hole_drilling` estimate_line (`enabled_by_default: false`, so this
never appeared in standard production output anyway - the removal only closes the special
case, it changes nothing for normal projects). `flat_roof_calculator.py` was deliberately left
untouched - its `if gas_block_wall_holes_count > 0: ...` branch is now dead code, but rewriting
tested calculator logic just to delete an unreachable branch was judged riskier than leaving
it. The adapter (`review_to_calculator/sections/flat_roof/build_input.py`) needed no code
change - the field already flowed through the generic "skip optional supplier_inputs" path -
only its explanatory comment was updated. Full writeup in `ADAPTER_BUILD_PLAN.md` right before
the `flat_roof` (2026-08-05) section.

If a future project genuinely has gas-block walls needing hole-drilling, all 3 contract
entries will need to be re-added, and a real price sourced from whatever price list is current
at that time.
