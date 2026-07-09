# Step 14 — ЮСВ Source PDF Data-Quality Notes (Cross-Section)

## Scope and purpose

Unlike `step_13`, this is not a contract-vs-extraction structural check. These are observations
about the real project's **source PDF drawings themselves**, surfaced during the third (most
careful) chat-extraction pass, worth recording so they are not re-discovered from scratch on a
future pass. Per the Cross-Check Stage's hard rule, no literal project quantities are recorded
here — findings are described structurally/qualitatively only.

## 1. Earthworks: trench-route volumes do not match their own length×depth×width

For every one of the four trench routes in the earthworks trench table, the volume computed as
length × depth × width does not match the volume value printed in the same table row — the printed
volume is consistently larger than the computed one, by roughly the same factor across all four
routes. At the same time, the sum of the four printed per-route volumes matches the table's own
printed "Итого" (total) row exactly.

This means the discrepancy is internally consistent (not a random OCR misread) and is either: (a)
a real authoring choice in the source drawing — e.g. the printed volume already includes a
soil-loosening/slope-allowance coefficient not shown as a separate column, or (b) a genuine drafting
error that was carried through consistently. The extraction pass correctly did not try to "fix" the
printed volume to match the geometric computation, and flagged all four rows `needs_review`.

**Recommended action**: this is a question for whoever can read the original CAD drawing / ask the
project's engineer — not something the extraction pipeline or this repo's contracts can resolve.
If confirmed as a real coefficient (not an error), it may be worth documenting the coefficient
value in project-specific notes (kept outside this generic pipeline, per the no-leakage rule) so
future manual reviews of the same project know to expect it.

## 2. Explanatory note references a different project's address/cadastral number

КР1's explanatory note (early page, general provisions section) states an address and cadastral
number that does not match the address/cadastral number stamped on every other page of both КР1
and КР2 (title block stamp, consistent throughout). The mismatched address belongs to a different
municipal district and a different cadastral number pattern entirely.

This strongly suggests the explanatory note text was copied from a template or a different
project's document set and not fully re-edited for this project — a real authoring artifact in the
source PDF, unrelated to this pipeline.

**Recommended action**: flag to whoever manages the ЮСВ project documentation; not an extraction or
contract issue. No action needed in this repo.

## 3. Load-bearing walls: floor-count statement conflicts with the drawing set structure

КР2's general provisions text states the building is single-storey ("Этажность — 1 этаж"), but the
same document set contains a clearly separate specification table explicitly titled for
second-floor bearing walls (distinct from the first-floor bearing-wall table), with its own
distinct gas-block and rebar quantities.

This is a direct textual/structural contradiction within the source PDF: either the floor-count
statement is stale (leftover from an earlier single-storey design revision) or the "2nd floor"
table label is a labeling error. Either way, it should not be silently resolved by the extraction
pipeline — the third pass correctly kept both the text statement and the second table, flagged the
apparent contradiction, and did not attempt to decide which one is authoritative.

**Recommended action**: needs human confirmation against the actual building (or the architect)
before the `load_bearing_walls_lintels` section contract's Cross-Check Stage (a later step in the
Step 10 order) treats the second-floor bearing-wall table as real, distinct project data versus a
duplicate/mislabeled row.

## Why this report exists separately from step_13

These three findings are about the real project's source documents, not about
`section_contract.yaml` structure or `parser_mapping` correctness — they don't belong in a
per-section Cross-Check Stage report. They're recorded here, cross-section, so they aren't lost and
can inform the `load_bearing_walls_lintels` and `earthworks`-adjacent review work later.
