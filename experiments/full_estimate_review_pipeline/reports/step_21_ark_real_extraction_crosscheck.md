# Step 21 — АРК: Real Chat-Extraction Crosscheck Against UNIVERSALIZATION_PLAN

## Scope

Cost-basis only. This is the Cross-Check Stage (HANDOFF.md) applied for the first time to a
project other than ЮСВ: a real chat-extraction pass (`claude_estimate_extraction_prompt.md` flow)
was run against this project's КР1+КР2, producing a real `extraction_output.json` and a real
служебная записка. Per the Hard Rule in that stage, **no literal project quantity is recorded in
this file** — only found/not-found/found-but-wrong-shape verdicts, source_class notes, and
parser_mapping/contract-shape findings. Numbers were discussed in chat with the user and are not
reproduced here.

## Why this document exists

`reports/step_20_ark_third_project_stress_test.md` and `UNIVERSALIZATION_PLAN.md` were built by
reading this project's PDFs by hand and cross-checking a few tables against user screenshots — both
files explicitly flagged themselves as needing verification against a real chat-extraction pass
before being trusted. That pass has now been run. This report records what it confirmed, what it
found that step_20 didn't anticipate, and where it disagrees with step_20.

## Confirmed exactly as predicted in step_20 / UNIVERSALIZATION_PLAN

- **Scalar-target collisions are real, not theoretical.** Every place UNIVERSALIZATION_PLAN
  predicted a flat `target_code` would receive more than one physically-distinct value, the real
  extraction produced exactly that: two `found` items under the same target_code, both flagged
  `needs_review`, with a note that no combined total exists in the source. Confirmed in:
  foundation concrete volume, foundation membrane area, monolithic lintel concrete, floor-cover-slab
  beam concrete (both slabs), floor-cover-slab beam formwork area (both slabs), and — most sharply —
  the roof area/abutment fields, where a single level with two roof *types* produced **three**
  colliding values under one target_code (two types at one elevation, one type at the other). This
  is the strongest evidence yet for the `roof_levels[].roof_types[]` shape specifically, not just
  `roof_levels[]`.
- **`floors_count` has no source value at all** for this project — not ambiguous-with-candidates
  like ЮСВ/ТРЦ, genuinely absent, because the project's own general notes never state a floor count
  the way ЮСВ/ТРЦ did. This is stronger confirmation than step_20 had: it's not just that gating on
  `floors_count` is fragile, it's that the field cannot be populated for this project shape at all.
  Reinforces the P1 item to gate wall/lintel cost lines on component presence, not floor count.
- **Masonry rebar sometimes covers two block widths in one reported row** (P3 item) — confirmed
  exactly: the main-wall rebar for this project's two load-bearing block widths is one combined row,
  not two.
- **Vent channels are brand-agnostic and vent-channel height is only available as an ambiguous
  candidate pair, not a clean per-channel-type value** — confirmed, matching the P2 item's existing
  fallback-to-0 design (no change needed there).
- **The extraction correctly avoided double-counting a genuinely duplicated table on one sheet**
  (a communications spec table printed twice with identical rows) — this is the extraction prompt's
  duplicate-detection rule working as intended on a case step_20 never saw; worth noting as a
  positive signal, not a gap.

## New findings this crosscheck surfaced (not in step_20)

- **Partition (perevegorodka) masonry volume and its rebar have no capture path at all** — not
  diagnostic-only like the earlier ТРЦ *waterproofing* finding, but literally no matching
  target_code and no `outside_target_*` fallback code either, unlike the equivalent ЮСВ case. Real,
  non-trivial quantities from this project's PDF are currently unreachable except by reading raw
  table rows by hand. This upgrades the existing P2 "should `cutoff_waterproofing_partitions_area_m2`
  become active" question from open-ended to: partitions need a real capture path across concrete,
  rebar, *and* waterproofing, not just the waterproofing line.
  **Confirmed cross-project, 2026-07-18**: a direct read of ТРЦ's own КР2 (not just the ARK PDF) shows
  the identical gap already exists there — a wall-block material spec table gives partition masonry
  volume as its own distinct rows (by floor), and a separate rebar spec table gives partition rebar
  as its own distinct rows (by floor) — neither has a matching target_code today, same as ARK. This
  is not an ARK-specific edge case; it has been present, unnoticed, in the first non-ЮСВ project ever
  crosschecked. Also worth a standing caution for any future work on wall-block volumes: this
  spec table's own printed grand total sums load-bearing walls, parapets, partitions, *and*
  vent-channel cladding together in one figure — it must never be used as a shortcut for "total main
  wall volume."
- **Lintel formwork fields model the wrong level of the data.** The contract's
  `floor_1_lintel_formwork_plywood_qty` / `floor_1_lintel_formwork_timber_volume` expect purchase-
  ready quantities (sheet count, material volume); what this project's PDF actually gives is raw
  formwork area (vertical/horizontal, m²) — the same shape floor_slab_1/2's own formwork fields
  already use. This is not a missing-data gap, it's a field-shape mismatch: the targets should
  become area-based (mirroring the slab formwork pattern) rather than staying as derived-quantity
  placeholders that no real PDF can ever fill directly.
- **Correction after reading the actual calculator code (2026-07-19): `floor_slab_1_beams_concrete_volume`
  is not redundant — it's a deliberate cross-check, already correctly implemented, and should stay
  `AUTO_PROJECT`.** `floor_slab_1_calculator.py` already sums `beam_items[]` unconditionally; if the
  scalar override is present it's compared against that sum and the calculator raises if they differ
  by more than 0.01 m³, otherwise the sum alone is used. This is real, working discrepancy-catching
  (the same category as the roof membrane-brand and vent-channel-length mismatches found elsewhere),
  confirmed by the field's own contract notes to have been designed specifically because both ЮСВ and
  ТРЦ print a genuine combined "Итого" row across all beam marks. Moving it to `AUTO_CALCULATED` would
  remove that protection for exactly the projects where it currently works.
  **The real problem is narrower**: on this project's floor_slab_1, the beam spec table has no
  combined total, only one row per beam mark — and the extraction's alias list for this target
  (generic phrases like "бетон балок") apparently matches individual per-mark rows too, when the
  field was only ever meant to capture a genuine cross-mark grand total. The fix belongs in the
  extraction prompt/alias rule, not the contract or calculator: this target should only ever be
  populated from a row explicitly labeled as a combined total across all marks (e.g. an "Итого" row),
  never from an individual mark's own value — those already have a correct home in `beam_items[]`
  with no separate target needed.
- **Correction after reading the earthworks calculator code (2026-07-19): the main pit is fine, only
  secondary pits (приямки) are a real gap.** The main pit's excavation volume is not a missing
  target — it's `AUTO_CALCULATED` downstream from the two `AUTO_PROJECT` fields that already exist
  (`pit_area_m2` × `pit_excavation_depth_m`), and that calculation is already wired into the
  excavator-shift costing. Secondary pits (приямки — local recesses in the pit floor, e.g. for sumps
  or drainage points) are the genuine gap: no area, no depth, no volume target exists for them at
  all, not even a diagnostic one. Real project data for both their area and their excavation volume
  exists on this project's PDF and has nowhere to go. Fix: extend the plan's existing `pit_items[]`
  idea (repeated group, area/volume + free-text context) to cover this — the main pit can become the
  first item in that same list without disturbing its current area×depth calculation.
- **Confirmed cross-sheet material-brand inconsistency on the flat roof, not caught by the
  extraction or the project's own служебная записка.** The materials spec table for both roof
  "types" at one elevation names the same membrane brand, while the roof buildup diagram elsewhere
  on the same sheet correctly differentiates the two types on every other attribute (insulation
  thickness, area) but names a *different* membrane brand for one of them. Visually confirmed by the
  user against the actual PDF; most likely explanation is that the second type's spec table was
  copy-built from the first type's and the membrane-name cell was never updated — i.e. a source-PDF
  typo, not an extraction error. The more important structural finding is *why* the real extraction
  didn't catch it: its contradiction-detection worked correctly for duplicate/conflicting rows
  *within one table* (see the earthworks duplicate-table case above) but did not cross-reference a
  spec-table cell against a same-sheet buildup diagram describing the same physical layer. This is a
  gap in the extraction methodology's scope, not just a one-off PDF typo — worth deciding whether the
  extraction prompt should cross-check named-material cells against any same-sheet buildup/layer
  diagram before accepting them as `found` with high confidence, at least for roof membrane brand.

## Where this crosscheck disagrees with step_20

None outright — everything step_20 predicted either was confirmed or turned out to be an
underestimate of the same underlying issue (see "New findings" above). No case was found where
step_20 predicted a problem that the real extraction shows isn't actually one.

## Служебная записка review

The project's own служебная записка (produced alongside the real extraction) is accurate and
matches the JSON's `needs_review` items closely: sand backfill covering multiple purposes, a
duplicated communications table (correctly not double-counted), foundation plate concrete/membrane
given per-zone with no printed total, the waterproofing-area-equals-formwork-area convention,
upper-wall masonry not explicitly labeled as a second floor/level, floor-cover-slab concrete given
per-component with no printed total, roof area discrepancies between plan labels and spec tables,
and a vent-channel length/height arithmetic mismatch — all match structural findings in this report.

Two suggested additions for future notes of this kind:
1. Make the `floors_count` absence more actionable — state explicitly that Elena's decision on it
   determines whether the upper-wall/parapet cost lines enter the estimate at all (the same framing
   already used for ТРЦ's floors_count risk), not just note the labeling ambiguity.
2. Add the roof membrane-brand cross-sheet inconsistency confirmed above — this one the extraction
   missed entirely (not even a `needs_review` candidate pair), unlike the other items on this list.

## Where this feeds next

Update `UNIVERSALIZATION_PLAN.md`: several P1/P2 items can now be marked "confirmed by real
extraction" rather than "predicted from manual PDF read." Two new checklist items are needed
(lintel formwork field shape; partitions rebar/concrete capture, not just waterproofing — confirmed
cross-project on ТРЦ too, 2026-07-18). The beam-concrete question originally framed as an open
`AUTO_CALCULATED` design decision was resolved after reading `floor_slab_1_calculator.py`
(2026-07-19): the field and its sum/cross-check logic are already correct and should not change;
the actual fix is a tighter extraction-prompt rule so this target is never populated from a
per-mark row, only from an explicit combined-total row.
