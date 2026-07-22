# Step 22 — ТРЦ: Real Extraction Audit and Overlap With the ARK-Derived Plan

## Scope

Cost-basis only. No literal project quantities are recorded in this file — only found/missing/
needs_review verdicts, source_class notes, and contract-shape findings. This audit was run against a
real chat-extraction pass already performed for ТРЦ (`extraction_output.json` + a служебная записка,
both supplied by the user), the two ТРЦ source PDFs, the current section contracts, and the relevant
calculator source code — not just a manual PDF read.

## Why this document exists

ТРЦ was the second project used to grow the original ЮСВ-shaped contracts (2026-07-13..15: floor-2
U-block lintels, monolithic lintels, optional D500 parapet). The user's concern (2026-07-19): ТРЦ may
still not be fully ready to pass cleanly through parser → review workbook → calculator, and some of
its remaining gaps may or may not already be covered by the P1/P2/P3 plan built from the third project
(АРК, `UNIVERSALIZATION_PLAN.md`). This audit answers that directly: which ТРЦ findings are already
covered by that plan, which require expanding it, and which are not a schema problem at all.

## Finding #0 — a source-document trust issue, not a schema issue

The extraction's own top-level warnings flag that several pages of ТРЦ's КР2 carry a title block for a
*different* project than the rest of the set. This affects the flat roof section in full, the floor-
cover slab 2 section in full, and part of floor-cover slab 1's kitchen/dining-area rebar. Every
affected value is already correctly marked `needs_review`, so nothing is silently lost — but no
contract or calculator change resolves this. It requires the architect/design bureau to confirm which
pages genuinely belong to this house before those three areas can be trusted for costing. This should
be treated as the standing precondition for finishing ТРЦ, ahead of any code work.

## Findings already covered by the ARK-derived plan

Confirmed present in ТРЦ's real extraction, in the same shape already documented in
`UNIVERSALIZATION_PLAN.md` and `step_21`:

- Partition (perevegorodka) masonry volume and its rebar: no matching target_code, not even a
  diagnostic one — same as found on АРК. Double confirmation, no new plan item needed, just execute
  the existing P1 `wall_block_items[]` item.
- Main wall block volumes, parapet masonry volume, and cutoff waterproofing area under load-bearing
  walls: all present as PDF components with no printed combined total, colliding on their respective
  scalar target_codes — the exact shape `wall_block_items[]` is designed to fix.
- Lintel formwork fields (`floor_1_lintel_formwork_plywood_qty`/`_timber_volume` and floor_2
  equivalents): entirely missing from the real extraction, because — confirmed by the служебная
  записка — the PDF gives only raw formwork area (split vertical/horizontal), never a ready plywood-
  sheet count or timber volume. Matches the field-shape mismatch already added to the plan from АРК.
- Flat roof: four distinct zones (two types at one level, one type at another level, plus a separate
  stair-roof zone) colliding against a two-level target model — the exact case `roof_levels[].roof_types[]`
  is designed for.
- `trench_volume_m3` appearing in `missing`: confirmed **not a gap** after reading
  `earthworks_calculator.py` — the calculator already falls back to summing `trench_routes[]` when the
  scalar is absent, the same pattern already corrected for beam concrete volume. No action needed.

## Findings that require expanding the plan's scope

1. **`slab_zones[]` needs to cover `floor_slab_1`, not only `foundation_slab`.** ТРЦ's first-floor
   slab is split into two physically separate pours (a main slab and a kitchen/dining-area slab) with
   independent concrete volume, edge perimeter, formwork area, and insulation — no combined total for
   any of them. This is structurally identical to the foundation zone-splitting problem the plan
   already solves for `foundation_slab`, but the plan currently doesn't scope that fix to
   `floor_slab_1`. Needs an explicit plan item (and, later, likely `floor_slab_2` too, once a project
   exercises that case).
2. **A new, opposite failure mode: source data more aggregated than the contract wants.** On ТРЦ,
   floor_slab_1's edge/torets formwork area is printed as a single number that mixes the slab's own
   edge and the beams' edge together — the source cannot be cleanly split into the two separate
   figures the contract's formwork fields expect. Every other finding so far has been "PDF gives more
   granularity than the contract has room for"; this is the reverse. No current plan item addresses
   it. Needs an explicit rule: accept the merged figure with a flag that clean separation isn't
   possible, rather than attempting to force a split the source doesn't support.
3. **Schiedel's `_2x_count`/`_3x_count` fields conflate two different meanings of "count."** ТРЦ's real
   extraction shows a spec-table quantity that is almost certainly a material/module count, mapped
   into a field whose name implies a shaft count, while the actual number of physical shafts shown on
   the plan is different and lower. The plan's existing `channel_items[]` item (brand-agnostic,
   free-form type label) does not by itself separate "how many physical shafts" from "how many
   material modules were ordered for them" — these need to become two distinct fields inside that
   redesign, not one.

## Findings that are one-off data-verification items, not code changes

- Two different tables in ТРЦ's КР1 give different length/volume figures under the same trench route
  label. Already correctly flagged `needs_review` by the extraction with both values preserved
  separately (not summed). Resolving which is correct (or whether they're genuinely two distinct
  segments) is a question for the architect, not a parser or contract fix, and isn't expected to
  recur systematically across other projects.
- A thermal-insulation thickness callout on one foundation detail sheet conflicts with a general
  insulation-scheme label elsewhere on the same sheet (50mm vs 100mm) — same category as the roof
  membrane-brand inconsistency found on АРК (step_21): a same-sheet cross-reference contradiction that
  the extraction's current contradiction-detection doesn't catch across different visual elements on
  one page. Reinforces (does not duplicate) the open P3 item already recorded for that class of issue.

## Resolution, 2026-07-21 — Finding #0 downgraded from blocker to logged warning

User decision: the foreign title block (Ananьино) on several КР2 pages is a copy-paste artifact from
reusing a template project's sheet, the same category as the kadastr-number and отметка 0,000
discrepancies caught by rule 24 in `step_25`. It is **not** a signal that the underlying quantities on
those pages belong to a different building. Verbatim: "это ошибки при копировании, только указать в
служебной записке и дальше игнорить, ни на что не должно влиять."

This reverses this document's original framing ("the standing precondition before ТРЦ's roof and
floor_slab_2 can be trusted at all") — flat_roof, floor_slab_2, and the floor_slab_1 kitchen/dining
rebar affected by this stamp are no longer waiting on architect confirmation. Extraction should keep
flagging the mismatch (`needs_review` + note, same as today) purely as an audit trail — Elena/the
architect can still be told, but the pipeline does not wait for their answer before trusting the
numbers. No contract/calculator change needed; this only changes downstream handling of an
already-caught finding, not detection.

## Where this feeds next

`UNIVERSALIZATION_PLAN.md` updated: `slab_zones[]` scope note expanded to include `floor_slab_1`; a
new item added for the "source more aggregated than contract" case; the Schiedel `channel_items[]`
item's description tightened to separate shaft count from module/material count. Finding #0 (title
block mismatch) is recorded as a standing precondition, not a checklist item, since no code change
resolves it.
