# Step 20 — АРК Third Reference Project: Structural Stress Test

## Scope

Cost-basis ("себестоимость") only. Structural findings from reading a third real project's PDFs
directly (КР1 "Конструкции ниже отм.+0,000" and КР2 "Конструкции выше отм.+0,000"), cross-referenced
against all 8 `section_contract.yaml` files and the calculators they map to. This project is at
concept stage ("Стадия П" / "Эскизный проект"), not working-drawing stage like ЮСВ/ТРЦ — quantities
may still change before РД, so treat this as a structural/architecture signal, not a source of
production numbers.

Per the Hard Rule in this pipeline's Cross-Check Stage (HANDOFF.md), **no literal project quantity
from this project is recorded in this file** — only field names, source classes, and contexts. The
underlying numbers were discussed in chat with the user on 2026-07-18 and can be re-derived from a
real chat-extraction pass if needed for a future `build_input.py` pilot.

## Why this document exists

ЮСВ alone shaped all 8 section contracts. ТРЦ (see `reports/step_17_load_bearing_walls_lintels_extraction_crosscheck.md`
and the 2026-07-13..15 commits — `bb6dca2`, `c6f6bf1`, `9ade87a`, `f865204`, `b9d7156`) forced
`load_bearing_walls_lintels` and `waterproofing` to grow real optional structure: per-floor lintels,
a monolithic lintel type, an optional D500 parapet, an optional EPS-50 waterproofing layer. This
third project shows the same rigidity in five more places, and one case where a rule we derived from
ТРЦ turns out not to be universal. See `UNIVERSALIZATION_PLAN.md` (same directory's parent) for the
prioritized checklist this report feeds into.

## Method

Read both PDFs' full text directly (not through the production chat-extraction flow), then verified
the highest-risk table alignments against screenshots the user provided directly. No automated
extraction pass has been run against this project yet — see "Verification needed" below before
acting on any of this.

## Findings by section

### earthworks

- The pit excavation is not a single area/volume pair: this project's site plan has a main pit plus
  separate small pits ("приямки") under column footings, each with its own area and excavation
  volume on the same sheet.
- Sand backfill appears in at least 3 distinct contexts on one sheet: general wall-pazuha-and-trench
  backfill (reported as one combined line), and a separate small line for the footing-pit sand base.
  Not one flat `sand_base_volume_m3`.
- Trench route codes are K1/K2/V1/EO (electrical routes) here, not ЮСВ's K1/K2/Вода/Эл.кабель —
  confirms `route_code` must stay a free string, matching the conclusion already reached after ТРЦ.
- Trench depth on this project's utility scheme is dimensioned from the pit bottom, not from site
  zero — a different depth datum than ЮСВ/ТРЦ used. Not a contract change today; a note for whoever
  eventually builds an automated length×width×depth arithmetic cross-check, so it doesn't assume one
  universal datum.

### foundation_slab → needs to become a foundation *system*, not a single slab

- This project's foundation is walls topped by a cap plate (the drawing set has a dedicated "cover
  plates over foundation walls" sheet), not a slab poured directly on a sand base like ЮСВ/ТРЦ.
- Two separate cap plates at different elevations, each with its own concrete volume, own vertical
  formwork, own membrane area, and own edge-waterproofing scope — and the two plates' coating-
  waterproofing scope genuinely differs from each other (one is edge-only, the other is edge+top-
  surface). This is a real per-plate design choice in the source drawings, not extraction noise.
- Foundation walls carry their own concrete and vertical formwork, plus **two** separate
  waterproofing systems layered together: a membrane (same brand the slab already uses) and a
  coating/smeared waterproofing (a different, named brand). ЮСВ/ТРЦ's foundation only ever needed the
  membrane.
- A small footing/pedestal element under a column is part of the below-+0.000 drawing set (own
  concrete, formwork, waterproofing, own rebar). **User decision, 2026-07-18: keep this inside the
  foundation section** — it belongs to the foundation drawings. The column itself above +0.000 stays
  out of scope (see "Explicitly out of scope" below).
- The thermal insert on this project is a single size (unlike ЮСВ's 50mm/100mm split), with its own
  rebar cage (two diameters) — same structural need as ЮСВ's thermal-insert rebar, just needs the
  section to accept an arbitrary EPS size instead of two hardcoded 50/100mm fields.

**Contract change:** `foundation_slab.concrete_project_volume_m3` (scalar) → `slab_zones[]` (repeated
group, each zone carrying its own concrete/formwork/membrane-area/edge-waterproofing-scope). Add
`foundation_wall_items[]` and `column_footing_items[]` (repeated, concrete+formwork+two waterproofing
types). Thermal insert stays a repeated group but drops the hardcoded 50/100mm split for a free
`eps_size` string per item.

### waterproofing

- Cutoff waterproofing under partitions is a priced line on this project, the same way it was
  present-but-treated-as-out-of-scope on ТРЦ. Open question, not purely technical: should
  `cutoff_waterproofing_partitions_area_m2` become an active production target across all projects
  instead of staying diagnostic-only?

### load_bearing_walls_lintels → the largest architectural change in this report

- Wall-block volumes for this project's above-ground-floor masonry split into three distinct
  contexts that don't map onto ТРЦ's "floor 2" model at all: a "second light" wall zone (masonry
  between two roof-plate levels, roughly one storey tall) and **two separate parapet zones**, one at
  each roof-plate level. ЮСВ/ТРЦ only ever needed one wall-below-parapet + one parapet-above pattern.
- Masonry rebar is sometimes reported as **one combined line covering two different block widths
  together**, not split per context — the calculator-input model needs to tolerate a `context` that
  names more than one physical wall type in a single reported row, rather than assuming a strict 1:1
  context-to-row mapping.
- A small, previously-unseen rebar context appears: reinforcement under window sills. Recommendation:
  leave out of MVP production targets (negligible cost), but make sure it still surfaces as an
  `outside_target` finding rather than being silently dropped.
- Partition thickness is reported inconsistently *within the same project*: general notes state one
  nominal thickness; the actual masonry block spec and the lintel-type label both use a different
  (larger) thickness. Same category of discrepancy as the ТРЦ 625mm/600mm gas-block case — a
  needs_review note for Elena, not something the parser should silently resolve.
- **A third lintel construction type**, beyond the existing U-block and monolithic-poured types:
  reinforcement set directly into a groove cut into the block itself and glued in place — no concrete
  pour, no formwork, no EPS edge insulation. Needs its own `lintel_groups[].type`, because none of
  the existing types' cost lines (concrete, formwork) apply — only a rebar-and-glue cost does.
- **The "D400 is always 600×400×250, everything else is D500" rule** (established after ТРЦ, recorded
  in memory as `lintel_floor_split_and_monolithic.md`) **has a confirmed counter-example**: a narrow
  block used specifically for vent-channel masonry is explicitly labeled a different density than the
  rule would predict. The rule needs to be downgraded from a hard constant to a default used only
  when the PDF doesn't state density explicitly — extraction must always prefer an explicit density
  label over the width-based heuristic. Memory file needs a correction.

**Contract change:** replace the current fixed fields (main-wall D400/D500 volumes, parapet volume,
optional D500-parapet volume, floor-2 masonry volume, and their rebar counterparts) with one repeated
`wall_block_items[]` — each item carrying a free-text `context`, `block_size`, `block_density` (read
from the PDF label, never inferred), `volume_m3`. This is a real calculator.py change (today's
masonry lines are keyed to fixed field names), so flag for explicit user authorization before editing
`load_bearing_walls_lintels_calculator.py`, same as the 2026-07-10 exceptions for other calculators.
The existing `floor_2_masonry_volume_m3 when floors_count = 2` gating pattern (found 2026-07-16) needs
to become "does an item with this context exist" instead of a floor-count boolean gate — `floors_count`
stops being a control variable for whether wall-masonry lines are priced at all.
Extend the existing U-block/monolithic lintel split (2026-07-15) with a third `groove_reinforced`
type that has no concrete/formwork/EPS fields, only rebar.

### floor_slab_1 / floor_slab_2 → roof-cover plates on this project, not living-floor slabs

- Both of this project's "slab" levels are structurally flat-roof cover plates by the project's own
  general notes (explicitly labeled as flat, non-operable roof construction at both elevations), not
  living floors like ЮСВ/ТРЦ's floor_slab_1/2. They still occupy the same *position* in the pipeline
  (concrete → beams → formwork → edge insulation, before `flat_roof`'s own membrane/insulation layers
  run on top) — no pipeline reordering needed, only the internal field list needs to grow.
- Formwork and edge insulation split into **4 formwork lines** per plate (vertical formwork of the
  plate itself, vertical formwork of the beams embedded in the plate, horizontal/bottom formwork of
  the plate, horizontal/bottom formwork of the beams), where `floor_slab_1`/`floor_slab_2` currently
  support a smaller set. Edge insulation likewise separates plate-perimeter insulation from beam-side
  insulation, and can (rarely) mix two different EPS thicknesses on the same plate's perimeter — a
  short secondary run alongside the main run.
- Beam rebar on this project reaches **Ø20**, a diameter that hasn't appeared in ЮСВ or ТРЦ's
  floor-slab beams before. This is a price-registry gap risk, not a contract change: confirm an
  `rebar_a500_d20_m`-equivalent key exists before piloting this project, or `price_resolver.py` will
  correctly, loudly fail on it.

**Contract change:** extend `floor_slab_1`/`floor_slab_2` (or their eventual shared `slab_items[]`
replacement, see `review_to_calculator/ADAPTER_BUILD_PLAN.md`) with the 4-way formwork split above,
and allow the edge-insulation perimeter to carry more than one EPS thickness per plate.

### flat_roof

- Two roof "types" can coexist at the same elevation, and they differ by **membrane brand**, not just
  insulation thickness — confirmed: one type uses one LOGICROOF membrane variant with the thicker
  main-insulation layer, the other type uses a different LOGICROOF variant with a thinner
  main-insulation layer. This is orthogonal to the level-vs-level ambiguity ТРЦ already surfaced
  (`roof_area_level_1`/`level_2` needing candidates) — here it's two fully separate materials lists
  at the *same* level.
- Drains are not one generic type: at least two distinct product types appear (an "internal drain"
  type at one roof elevation, a "parapet drain" type at another), with different installation logic
  implied by the product name itself.
- Each roof level/type reports abutment lengths (to parapets, to walls, to vent channels) as its own
  separate line, not one combined total per building — finer than what ТРЦ gave us (ТРЦ only had one
  combined abutment total per type, with no per-level split at all).

**Contract change:** `flat_roof`'s scalar roof-area/abutment fields need to become
`roof_levels[].roof_types[]`, each type carrying its own membrane brand, its own insulation-layer
list, and its own abutment lengths (parapet/wall/vent-channel tracked separately). Add a `drain_type`
field (internal vs parapet, extend as needed) to drain items.

### schiedel_vent_channels → confirmed brand-agnostic model needed

- This project's vent shafts are not a branded Schiedel product at all — generic masonry shafts built
  from gas block, in two channel-count variants, with no product-brand column anywhere on the source
  sheet. Already suspected after ТРЦ (which was still Schiedel-branded, just different VENT numbers);
  this project confirms the section needs a brand-agnostic model, not just more VENT-number variants.
- Only one combined total-height figure is given for all shafts together, rather than per-shaft or
  per-type — coarser than ЮСВ/ТРЦ's data. Confirms the existing fallback-to-0 design for
  `vent_channel_1_height_m`/`vent_channel_2_height_m` (2026-07-13, since these only ever feed a
  diagnostic control formula, never the paid masonry quantity) was the right call — no change needed
  there.

**Contract change:** rename the section's model away from `schiedel_vent_channel_2x_count`/`_3x_count`
toward a repeated `channel_items[]` with a free `type_label` and an optional `brand` field (null when
not a branded product). Update section docs to stop assuming Schiedel is the only vendor.

## Explicitly out of scope for this pass (confirmed with user 2026-07-18)

- Canopies (steel + wood + glazing structure, including its own embedded-steel-plate connections into
  the roof-cover plate) — not priced, not modeled.
- The above-grade RC column itself — not priced. (Its footing/pedestal below +0.000 stays in scope,
  see foundation_slab findings above — user decision 2026-07-18.)
- Steel embeds set into the roof-cover plate purely to support the excluded canopy — not priced (user
  decision 2026-07-18), even though physically part of the plate's own material spec sheet.
- Windows/doors, blind-area apron ("отмостка" — user decision 2026-07-18: not now), underfloor-heating
  pipe layer, facade finishing — out of scope, not part of the shell estimate.
- Window-sill masonry reinforcement (negligible cost) — recommended out of MVP production targets, but
  should still surface as an `outside_target` finding rather than being silently dropped.

## Verification needed before any contract edits ship

Everything above is a structural read of concept-stage ("Стадия П") PDF text, cross-checked against
user-provided screenshots for the highest-risk tables only. A full chat-extraction pass (the normal
`claude_estimate_extraction_prompt.md` flow) has not been run against this project yet. Before editing
any `section_contract.yaml` based on this report, run that extraction pass and confirm
target_code/group_code coverage the same way `step_13`/`step_15`/`step_16`/`step_17` did for ЮСВ,
rather than hand-deriving field names from this report alone.

## Where this feeds next

See `UNIVERSALIZATION_PLAN.md` (parent directory) for the prioritized (P1/P2/P3) checklist of contract
and calculator edits this report drives.
