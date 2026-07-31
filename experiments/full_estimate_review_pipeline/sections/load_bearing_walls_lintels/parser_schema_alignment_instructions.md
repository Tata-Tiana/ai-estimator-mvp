# Parser/schema alignment instructions — load_bearing_walls_lintels

Purpose: keep the chat extraction files, review workbook contract, and calculator input shape aligned. The calculator field names are the ground truth; do not rename calculator fields to match an older parser output.

## Ground truth

- Section: `load_bearing_walls_lintels`
- Contract: `sections/load_bearing_walls_lintels/section_contract.yaml`
- Calculator: `experiments/load_bearing_walls_lintels_calculator/load_bearing_walls_lintels_calculator.py`
- Extraction files to keep aligned:
  - `experiments/chat_extraction_poc/data/calculator_targets_compact.json`
  - `experiments/chat_extraction_poc/data/target_aliases_ru.yaml`
  - `experiments/chat_extraction_poc/schemas/claude_extraction_output_schema.json`
  - `experiments/chat_extraction_poc/prompts/claude_estimate_extraction_prompt.md`

## Current status

Parser-side extraction files have received the first production alignment pass in
`reports/step_17_load_bearing_walls_lintels_extraction_crosscheck.md`.

The active chat extraction targets now use production target codes for the main project quantities
and production repeated-row shapes for wall/lintel rebar. Legacy wall-geometry rebar targets are not
active production extraction targets.

Known remaining risk: the calculator still has required non-PDF constants/defaults that the adapter
must fill from a defaults/catalog layer before a real calculator run. Do not ask GPT/Claude to invent
those constants from the PDF.

## AUTO_PROJECT values expected from PDF/chat JSON

- `floors_count`
- `cutoff_waterproofing_load_bearing_walls_area_m2`
- `main_wall_gas_block_400_spec_volume_m3`
- `main_wall_gas_block_250_spec_volume_m3`
- `lintel_total_length_m`
- `lintel_concrete_spec_volume_m3`
- `floor_1_lintel_monolithic_concrete_volume_m3`
- `floor_1_lintel_monolithic_total_length_m`
- `floor_1_lintel_monolithic_insulation_length_m`
- `floor_1_lintel_formwork_horizontal_area_m2`
- `floor_1_lintel_formwork_vertical_area_m2`
- `floor_1_lintel_insulation_eps_spec_volume_m3`
- `floor_2_masonry_volume_m3`
- `floor_2_lintel_ublock_total_length_m`
- `floor_2_lintel_concrete_spec_volume_m3`
- `floor_2_lintel_monolithic_concrete_volume_m3`
- `floor_2_lintel_monolithic_total_length_m`
- `floor_2_lintel_monolithic_insulation_length_m`
- `floor_2_lintel_formwork_horizontal_area_m2`
- `floor_2_lintel_formwork_vertical_area_m2`
- `floor_2_lintel_insulation_eps_spec_volume_m3`
- `parapet_masonry_volume_m3`
- `vent_chimney_gas_block_spec_volume_m3`
- `main_wall_rebar_items`
- `lintel_rebar_items`
- `parapet_chasing_base_length_m`
- `parapet_rebar_base_length_m`

## Repeated-row shapes

`main_wall_rebar_items`:

- `floor`
- `component`
- `steel_class`
- `diameter_mm`
- `spec_length_m`
- `kg_per_meter`

`lintel_rebar_items`:

- `floor`
- `component`
- `steel_class`
- `diameter_mm`
- `spec_length_m`
- `kg_per_meter`

## Critical extraction rules

- Keep wall gas block 400 mm and 250 mm volumes separate.
- Keep lintel total length separate from lintel concrete volume.
- Keep lintel concrete separate from slab, beam, foundation, and wall concrete.
- For monolithic lintels, keep concrete volume separate from total lintel length: concrete material/purchase uses m3, concreting work uses total length in м.п. from 2026-07-28.
- Do not substitute monolithic lintel insulation length for total monolithic lintel length; insulation may cover only part of the lintels.
- Keep vent chimney gas block volume separate from Schiedel vent channel kit quantities.
- Rebar rows must stay row-by-row; do not calculate total weight in GPT/Claude unless PDF explicitly gives it and the calculator expects it.
- Keep parapet reinforcement separate from `main_wall_rebar_items` and `lintel_rebar_items`.
  Parapet A500 Ø10 rows feed `parapet_chasing_base_length_m` and `parapet_rebar_base_length_m`
  as base linear lengths. They are not main-wall masonry rebar and not lintel rebar.

## Check before marking section ready

1. Read the calculator input shape directly, especially `main_wall_rebar_items` and `lintel_rebar_items`.
2. Confirm parser/schema field names match the calculator, not older generic `length_m/mass_per_m_kg` names.
3. Compare all scalar target codes with contract and calculator.
4. Confirm prompt/aliases separate walls, lintels, parapets, and vent chimney blocks.
5. Run JSON/YAML validation after edits.
6. Confirm no project-specific values, page numbers, or USV-only facts were added to production config.

## Adapter/defaults still required

The following calculator inputs are not PDF extraction targets. They must come from DEFAULT,
catalog, price registry, supplier input, or business settings before the adapter can build a valid
calculator input:

- `gas_block_d400_pallet_volume_m3`
- `gas_block_d500_250_pallet_volume_m3`
- `adhesive_consumption_bag_per_m3`
- `sand_concrete_consumption_kg_per_m2_per_10mm`
- `sand_concrete_thickness_factor`
- `gas_block_delivery_truck_capacity_m3`
- `gas_block_d500_150_pallet_volume_m3`
- `second_light_chasing_base_length_m`
- `second_light_rebar_base_length_m`

**All of the above declared in the contract 2026-07-10** — see the dated entry in
`step_17_load_bearing_walls_lintels_extraction_crosscheck.md` for the full `defaults`/`price_keys`
build-out (plus 9 more required calculator fields that this list had missed: `rebar_a500_d10_kg_per_m`,
`rebar_a500_d10_rod_length_m`, `rebar_a500_d10_unit_price_per_m`, and 6 dead-in-production legacy
wall-geometry fields). Only the contract-level declaration exists; the actual
`build_load_bearing_walls_lintels_input` adapter function is still not implemented anywhere in the repo.

**Checklist item 2 done 2026-07-10**: `calculator_targets_compact.json`, the extraction schema, and
`target_aliases_ru.yaml` still used the old flat rebar shape for `main_wall_rebar_items`/
`lintel_rebar_items` in one respect — both were missing `rod_length_m` as a field, even though the
contract's own `columns` list already required it (added in the same pass that added the
adapter/defaults list above, since the calculator reads `item.rod_length_m` with no fallback in
`spec_length_items` mode). Fixed in all three files, plus the extraction prompt, with guidance that
`rod_length_m` is usually a catalog/standard value by diameter (e.g. 11.7 m for A500 Ø10) rather than
something PDFs state per row — only extract it from the PDF if an explicit rod-length table exists,
otherwise leave it null for an adapter/catalog fallback. The identical gap was found and fixed at the
same time on `floor_slab_1_rebar_items` and `floor_slab_2_rebar_items` (the latter also had fully
stale field names left over from that section's rebar-catalog removal) — see those sections' own
alignment files.

## `lintel_items` removed 2026-07-12

The diagnostic mark-by-mark breakdown (`mark`/`length_m`/`count`/`total_length_m`, always
`required: false`, `calculator_input_path: ""` — never fed the calculator) was removed from the
contract, and from `calculator_targets_compact.json`, `target_aliases_ru.yaml`, the extraction schema,
the extraction prompt, `defaults_catalog.yaml`'s notes, and `build_review_workbook_from_contracts.py`'s
generic detail-sheet templates. Reason: it assumed a "Марка Пм-1/Пм-2..." table that does not exist in
real project PDFs. Checked directly (page text + tables) against `ЮСВ КР2 (11).pdf` (page 16, "План
перемычек 1-го этажа" / "Спецификация перемычек 1-го этажа") and `КР2_ТРЦ_30,06,2026.pdf` (pages 11-12,
"План перемычек 1/2 этажа", "СПЕЦИФИКАЦИЯ МАТЕРИАЛОВ НА УСТРОЙСТВО ПЕРЕМЫЧЕК"): both projects give a
per-floor lintel *materials* spec table (Поз/Обозначение/Наименование/Кол-во/Масса/Примечание — concrete
volume by lintel type, rebar length+mass by diameter, formwork area) with the totals already given as
explicit summary lines (e.g. "Общая длина перемычек в U-блоке", "Длина перемычек в U-блоках"), not a
row-per-mark schedule. `lintel_total_length_m`, `lintel_concrete_spec_volume_m3`, and
`lintel_rebar_items` already capture exactly this real structure and remain correct as-is.
