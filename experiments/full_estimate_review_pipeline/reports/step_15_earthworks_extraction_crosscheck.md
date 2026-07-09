# Step 15 — Earthworks: Contract vs Real Extraction Cross-Check

## Scope

Cost-basis ("себестоимость") only, per the Cross-Check Stage in `HANDOFF.md`. Checks
`sections/earthworks/section_contract.yaml` against `experiments/earthworks_calculator/earthworks_calculator.py`
(ground truth for what the calculator actually reads) and against the chat-extraction pipeline's own
target/schema files (`experiments/chat_extraction_poc/data/calculator_targets_compact.json`,
`schemas/claude_extraction_output_schema.json`). No literal project quantities are recorded in this
file, per the hard rule in the Cross-Check Stage section of `HANDOFF.md`.

Unlike `step_13` (foundation_slab), the bulk of this report's findings are structural — they compare
contract field names against calculator field names and against parser target/group field names, all
of which are non-project-specific. The "found/missing in a real project's extraction JSON" verdict
(the part that needs the live chat turn with real numbers) is a separate, smaller follow-up once the
earthworks section of a real extraction pass is pasted into the chat.

## Why this section is different from the other 7

`sections/earthworks/section_contract.yaml` already existed before the Cross-Check Stage was defined
(Step 1/4/6 in `HANDOFF.md`), built from the pre-existing, separately maintained earthworks
review-to-calculator flow (`experiments/earthworks_review_to_calculator/`,
`experiments/earthworks_parser_google_stage1/`). That flow works today, but it does **not** go
through the generic `build_review_workbook_from_contracts.py` adapter that the other 7 sections are
meant to use — it has its own hand-written reader/adapter/builder scripts, hardcoded per earthworks,
that never read `section_contract.yaml` at runtime. `calculator_input_mapping.transform:
earthworks_review_to_calculator_adapter` in the contract names this as "reference behavior," not a
real, generic transform.

The user has asked to redo earthworks so it goes through the same `section_contract.yaml`-driven path
as the other sections, instead of keeping the separate hardcoded pipeline. This is a genuine plan
change, not something `HANDOFF.md` already specifies — recorded as a new step in `HANDOFF.md` (see
below) alongside this cross-check.

## What was checked

Every `review_parameters` scalar and repeated-row group in the contract, matched against:
1. `EarthworksInput` dataclass fields and the actual per-row keys read inside
   `calculate_trench_routes` / `calculate_communications_length` in `earthworks_calculator.py`.
2. The parser's own `targets` / `extract_groups` field lists for `earthworks` in
   `calculator_targets_compact.json` and `group_value_shapes` in the extraction output schema.

## Confirmed matches (no action needed)

- Scalar `calculator_input_path`s (`pit_area_m2`, `pit_excavation_depth_m`, `sand_base_volume_m3`,
  `trench_volume_m3`, `geotextile_area_m2`, `geotextile_laying_area_m2`, `communications_length_m`)
  all match `EarthworksInput`'s real dataclass field names exactly — no calculator-side renames
  needed anywhere in this contract, unlike foundation_slab's rebar case.
- `communications_length_m`'s design (scalar is the real calculator input, `communications_pipe_items`
  is a cross-check-only breakdown, `status_if_missing: manual_required`) is internally consistent with
  how the parser is actually configured: the parser has no direct target_code for a communications
  total length at all — only the itemized `communications_pipe_items` group, with an explicit
  instruction not to output one summed number from the drawing text. This is the same
  no-silent-aggregation principle documented in `step_13`'s finding 3, applied correctly here by
  design, not by accident.
- `auto_calculated.manual_excavation_quantity_for_estimate_m3` correctly stays `AUTO_CALCULATED` and
  is not expected as a direct parser target — the parser's own target list marks the equivalent code
  `manual_excavation_quantity_for_estimate` as `"grounded": false`, i.e. explicitly not meant to be
  read from the PDF. Contract and parser agree here.

## Findings / corrections needed

### 1. Every scalar `parser_mapping.target_code` in this contract uses a different name than the parser's real target_code

Same category of bug as `step_13` finding 1 (`membrane_area_m2` vs `planter_membrane_area`), but here
it affects **all 6** extractable scalars in the section, not just one:

| Contract `target_codes` | Parser's real `code` |
|---|---|
| `pit_area_m2` | `pit_area` |
| `pit_excavation_depth_m` | `pit_excavation_depth` |
| `sand_base_volume_m3` | `sand_volume` |
| `trench_volume_m3` | `trench_volume_total` |
| `geotextile_area_m2` | `geotextile_area` |
| `geotextile_laying_area_m2` | `geotextile_laying_area` |

None of these six would be recognized by name if a future adapter trusted `parser_mapping.target_codes`
literally — every one of them would look "not found" even when the parser found it correctly under its
own real code.

**Suggested fix**: update each `parser_mapping.target_codes` above to the parser's real code (add
alongside or replace the existing value).

### 2. `trench_routes`: calculator needs `route_code`, which exists in neither the contract's columns nor the parser's fields

`calculate_trench_routes` (and the input `validate()` step gating it) requires
`route.get("route_code")` truthy for every row when `manual_excavation_calc_method == "standard_routes"`
— the contract's own current production default (`defaults.manual_excavation_calc_method`). Neither
the contract's `trench_routes.columns` (`name`, `length_m`, `depth_m`, `width_m`, `volume_m3`) nor the
parser's `trench_routes` group fields (`route_name`, `length_m`, `depth_m`, `width_m`, `volume_m3`)
contain a `route_code` field at all — only a display `name`/`route_name`.

Feeding real parser output through this contract as-is, in `standard_routes` mode, without
`trench_volume_m3` given directly, would raise `trench_routes[i].route_code is required` for every
row — a hard block, not a soft warning.

**Suggested fix**: either (a) add a `route_code` column to the contract and a matching parser target
field (e.g. derived deterministically from route name/order — К1, К2, ... — since the PDF drawings do
label routes this way per the source data already reviewed), or (b) change the calculator to accept
`name` as a fallback identifier when `route_code` is absent. (b) is a calculator code change and out of
this contract-only stage's scope; (a) is the contract/parser-side fix.

### 3. `trench_routes.width_m` and `.volume_m3` are declared required but never read by the calculator

`calculate_trench_routes` only reads `route["length_m"]` and `route["depth_m"]` per row; width comes
from the single global `trench_width_m` default (currently `0.4`, shared across every route), and
`volume_m3` is always recomputed by the calculator itself (`length * depth * width`), never taken from
the row. The contract marks both `width_m` and `volume_m3` as `required: true` columns, which is
misleading — the parser can find them, but nothing consumes them as calculator input; they only matter
for the read-only `03_Детали объемов` mirror sheet.

**Suggested fix**: downgrade `width_m`/`volume_m3` from `required: true` to `required: false` /
diagnostic-only in the contract's `columns`, with a note that they exist for the mirror sheet and
manual sanity-checking only, not as calculator input. Don't block review completion on them.

### 4. Real risk: if `trench_volume_m3` isn't captured directly, the calculator's routes fallback will not match the real PDF total

This connects directly to `step_14`'s earthworks finding (per-route printed volume does not equal
`length × depth × width`, consistently, across all routes, even though the sum of printed volumes
matches the table's own "Итого" row). The parser's own target list already anticipates this: the
`trench_volume_total` target is explicitly instructed to be left null "if no ready Итого row exists,"
with the note "объём посчитается из trench_routes" — i.e. the design assumes falling back to
per-route geometry is an acceptable substitute.

Per `step_14`, that assumption does not hold for this real project's PDF: the geometric recomputation
from length/depth/width would produce a smaller total than the real stated volume, by whatever
unexplained factor is causing the discrepancy. If a future project's PDF has the same convention and
`trench_volume_total` is missed by the parser (no explicit Итого row, or the row isn't recognized),
the calculator would silently compute a materially wrong (understated) trench volume with no error or
warning — this is a real correctness risk, not a naming/schema mismatch.

**Suggested fix**: no contract schema change fixes this by itself. Two options for the user to weigh:
(a) always require `trench_volume_m3` as a hard `required: true` scalar in review (never allow the
routes-only fallback silently), pushing Elena to manually confirm the total instead of trusting a
recomputation; or (b) keep the fallback but flag it loudly (`needs_review`/warning) whenever
`trench_volume_m3` is missing and only per-route data is available, so it's caught before the estimate
is finalized, not after.

### 5. `communications_pipe_items`: three separate field-name/requirement mismatches

Comparing contract `columns` vs parser `fields` vs what `calculate_communications_length` actually
reads per item:

| | Contract column | Parser field | Calculator reads |
|---|---|---|---|
| length per piece | `pipe_length_m` | `piece_length_m` | `item["pipe_length_m"]` (only if `total_length_m` absent) |
| count | `quantity` | `quantity_pcs` | `item["quantity"]` (only if `total_length_m` absent) |
| identifier | *(none — `name` is `row_key_field`)* | *(none)* | `item["code"]` — **required**, accessed as `item["code"]`, not `.get`, so a missing key raises a raw `KeyError`, not a graceful validation error |
| `total_length_m` | `required: true` | *(not a parser field — parser is explicitly told not to compute/output a summed length)* | optional; if present, used directly instead of `pipe_length_m * quantity` |

The `code` gap is the most serious of these three: it's a hard Python `KeyError` today, not even a
`ValueError` with a clear message like the `route_code` case gets. The `pipe_length_m`/`piece_length_m`
and `quantity`/`quantity_pcs` naming differences are the same class of mismatch as `step_13`'s rebar
column finding.

**Suggested fix**: 
(a) rename parser fields `piece_length_m` → `pipe_length_m` and `quantity_pcs` → `quantity` in
`calculator_targets_compact.json` and the extraction schema, matching the calculator (same direction
as the `step_13` foundation-rebar fix — align the parser to the calculator, not the other way round);
(b) add a `code` field to both the contract's `columns` and the parser's `communications_pipe_items`
fields — needs a real identifier convention (could reuse the pipe's name/GOST label if stable per row);
(c) contract's `total_length_m: required: true` should become `required: false`, since the parser is
deliberately never going to populate it directly — the calculator already handles its absence
correctly by computing from `pipe_length_m * quantity`.

## Confirmed NOT in real extraction scope (expected — correctly out of scope for this stage)

`excavator_shifts_calc_method`, `manual_excavation_calc_method`, `communications_length_calc_method`,
`excavator_productivity_m3_per_shift`, `manual_refinement_depth_m`, `trench_width_m`,
`sand_compaction_coeff`, `sand_truck_step_m3`, `geotextile_overlap_coeff`, `geotextile_roll_area_m2`,
`axis_marking_shifts` — all `DEFAULT` source_class, correctly not parser targets. None currently has a
`value: null` risk like foundation_slab's pack-multiples did (all have real numeric defaults already
filled in the contract).

## Verdict

- Calculator input field names for all 7 top-level `review_parameters` are already correct (no
  calculator-side rename needed anywhere in this contract) — better shape than foundation_slab's rebar
  case going in.
- 6 scalar `parser_mapping.target_codes` need correction (finding 1) — safe, mechanical, same pattern
  as `step_13` finding 1.
- `trench_routes` has a real blocking gap (finding 2: missing `route_code`) and a real correctness risk
  under a specific fallback condition (finding 4), both worth the user's attention before this section
  is trusted in production with the `standard_routes` default.
- `trench_routes.width_m`/`volume_m3` `required: true` is misleading (finding 3) — cosmetic/UX fix, not
  blocking.
- `communications_pipe_items` has a hard-crash-risk gap (finding 5: missing `code`, raw `KeyError`) plus
  two straightforward naming mismatches.
- No real per-project extraction JSON was reviewed for this section in this pass — findings above are
  fully structural (contract vs calculator vs parser config), not "found/not found in a real project."
  A follow-up found/missing verdict needs the earthworks section of a real extraction pass pasted into
  the chat (not written to any file, per the hard rule).

## Next steps (not yet applied — awaiting go-ahead)

1. Apply finding 1: fix all 6 scalar `parser_mapping.target_codes` in
   `sections/earthworks/section_contract.yaml`.
2. Decide and apply finding 2 (`route_code`): add a contract/parser column, or accept `name` as
   fallback (calculator-code change, separate from this contract-only stage).
3. Apply finding 3: downgrade `width_m`/`volume_m3` to non-required in `trench_routes.columns`.
4. User decision on finding 4 (routes-fallback correctness risk): hard-require `trench_volume_m3`, or
   flag-loudly-on-fallback.
5. Apply finding 5's naming fixes (`pipe_length_m`/`quantity`) and decide on a `code` convention for
   `communications_pipe_items`.
6. Optional: paste the earthworks section of a real extraction pass into the chat to add the
   found/missing verdict on top of these structural findings.
7. Separately: `HANDOFF.md` now has a new step recording the plan to move earthworks off its own
   hardcoded pipeline onto the generic contract-driven adapter (see next section) — that migration is
   independent of this cross-check and should happen after these contract fixes, not before.
