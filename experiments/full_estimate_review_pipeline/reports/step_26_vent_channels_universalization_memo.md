# Step 26 — Vent Channels / Schiedel Universalization Memo

Date: 2026-07-20

Status: architecture memo only. No production config or calculator code changed in this step.

## Why This Memo Exists

We reviewed the vent-channel problem in detail after comparing:

- API extraction outputs for ARK/TRC;
- screenshots of TRC and USV vent-channel drawings/specifications;
- USV estimate workbook;
- TRC estimate workbook;
- current `schiedel_vent_channels` calculator behavior.

The conclusion is important for the whole extraction and estimate pipeline: the current section name
`schiedel_vent_channels` is too narrow and the current target names mix at least three different
concepts. This can make GPT/Claude confuse:

- bought Schiedel material pieces;
- physical vent shafts / ВК labels on drawings;
- total masonry length used for work quantity.

This memo records what must be changed later in chat extraction / full estimate architecture.

## Estimate Findings

These numbers are project examples from existing estimate workbooks. They are not defaults and must
not be copied into production config as universal quantities.

### USV Estimate

Workbook:

```text
/Users/tatanamedzidova/Desktop/Сметный расчет _ЮСВ_28.04.2026.xlsx
```

Use the sheet selected by the user as the current reference:

```text
АЛ 06.04 КР1,КР2 (ЕЧ)(ЮВ)КровТН
```

Relevant estimate rows found on this sheet:

- row 122: `Обкладка дымохода и вентканалов толщ. 150мм из из газобетонных блоков` — `11.466666666666667 м2`;
- row 212: `Монтаж примыкания к вентшахтам` — `3 шт`;
- row 231: section header `ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel`;
- row 232: `Кладка вентканалов Schiedel` — `15.82 мп`;
- row 233: `Вентиляционный канал 2х,36/25 см Schiedel` — `24 шт`;
- row 234: `Вентиляционный канал 3х,52/25 см Schiedel` — `8 шт`;
- row 235: `Доставка вентканалов` — `1 маш`.

Interpretation:

- USV uses Schiedel product pieces 2x and 3x in the estimate.
- The paid work row is driven by total masonry length `15.82 мп`, not by counting visible holes/shafts.
- Gas-block cladding of smoke/vent shafts is a separate walls/parapet-related estimate line, not the
  same thing as Schiedel product pieces.
- Roof abutments to vent shafts are a roof estimate line, not Schiedel material quantity.

### TRC Estimate

Workbook:

```text
/Users/tatanamedzidova/Desktop/ТРЦ_3_точный_расчет_коробка_для_ИИ.xlsx
```

Relevant estimate rows found on sheet `НС 29.06.26`:

- row 138: `Обкладка дымохода и вентканалов толщ. 150мм из из газобетонных блоков` — `4.4 м2`;
- row 265: section header `ВЕНТИЛЯЦИОННЫЕ КАНАЛЫ Schiedel (без учёта дымоходов)`;
- row 266: `Кладка вентканалов Schiedel` — `9.8 мп`;
- row 267: `Вентиляционный блок SCHIEDEL VENT, 1 хода, наружный размер 20/25 см, высота 33 см` — `21 шт`;
- row 268: `Вентиляционный блок SCHIEDEL VENT, 2 хода, наружный размер 36/25 см, высота 33 см` — `15 шт`;
- row 269: `Доставка вентканалов` — `1 маш`.

Interpretation:

- TRC uses Schiedel product pieces 1x and 2x in the estimate.
- There is no 3x material row in this TRC estimate fragment.
- The current calculator only has material rows for 2x and 3x, so it cannot represent TRC perfectly
  until a 1x product line is added or generalized.
- The paid work row is driven by total masonry length `9.8 мп`, not by the count of visible shaft
  labels.

### ARK Observation From API Runs

ARK pages contained vent-channel / shaft information without a branded Schiedel product. Opus 4.8
correctly noted that these are gas-block / non-Schiedel vent shafts and did not confidently fill
Schiedel product target codes.

Interpretation:

- ARK is not a `schiedel_prefab` case.
- It should not create Schiedel 2x/3x material rows just because the page contains vent shafts.
- It needs a more general `vent_channels` system type or it should route the gas-block cladding data
  to the load-bearing walls / parapet / vent-shaft cladding logic.

## The Core Modeling Problem

The word "vent channel" appears in several meanings:

1. **Bought Schiedel product pieces**

   Examples:

   - `Вентиляционный канал 2х,36/25 см Schiedel — 24 шт`;
   - `Вентиляционный блок SCHIEDEL VENT, 1 хода ... — 21 шт`;
   - `Вентиляционный блок SCHIEDEL VENT, 2 хода ... — 15 шт`;
   - `Вентиляционный канал 3х,52/25 см Schiedel — 8 шт`.

   These are material estimate lines: quantity in pieces multiplied by material unit price.

2. **Physical vent shafts / drawing labels**

   Examples:

   - `ВК-1`, `ВК-2`, `ВК-3`;
   - `ШВ-1`, `ШВ-2`;
   - one visible shaft or one drawing node.

   These are not automatically material quantities. A single visible shaft can require many bought
   Schiedel blocks.

3. **Total masonry length / height for work**

   Examples:

   - `Общая длина кладки 6,52 м/п`;
   - `Высота вентканалов общая 4,9п.м + 4,9п.м = 9,8п.м`;
   - estimate row `Кладка вентканалов Schiedel — 15.82 мп`.

   This is the primary paid quantity for masonry work.

The current names `schiedel_vent_channel_2x_count` and `vent_channel_2_count` are too easy to confuse.
The first is a material piece count. The second is only a legacy/control geometry count.

## What The Calculator Actually Needs

For the paid Schiedel estimate lines, the calculator needs:

- total masonry length for `Кладка вентканалов Schiedel`;
- product piece counts for each Schiedel product type that appears in the estimate;
- delivery trips;
- prices.

The calculator does **not** need the number of physical holes/shafts as a paid production input when
the PDF/specification already gives total masonry length and product quantities.

Physical shaft counts can be useful only as diagnostic/control data:

- to explain a drawing;
- to help a reviewer see why a total length might exist;
- to reconstruct a length only when no explicit total exists.

They should not be mixed into material count targets.

## Minimum Two System Types Already Exist

### Type 1 — `schiedel_prefab`

Use this when the project/estimate has branded Schiedel product pieces.

Possible product rows:

- 1x / one duct / `1 хода` / `1х,20/25`;
- 2x / two ducts / `2 хода` / `2х,36/25`;
- 3x / three ducts / `3 хода` / `3х,52/25`.

Expected estimate behavior:

- work: `Кладка вентканалов Schiedel`, quantity from total masonry length;
- materials: dynamic Schiedel product item rows, quantity from specification pieces;
- delivery: delivery trips;
- optional consumables/logistics lines according to catalog/calculator.

### Type 2 — `gas_block_vent_shaft` / non-Schiedel shafts

Use this when the project has vent shafts, gas-block cladding, or generic vent-channel rows but no
Schiedel product rows.

Expected behavior:

- do not fill Schiedel product count targets;
- keep raw/detail rows for review;
- route gas-block cladding volume/area to the relevant walls/parapet/vent-shaft cladding logic;
- calculate a separate vent-shaft mode only after a dedicated production contract exists.

### Type 3 — `unknown`

Use when the page contains vent-channel terms but the system type is unclear.

Expected behavior:

- do not calculate Schiedel materials automatically;
- keep candidates and `needs_review`;
- require manual review or a resolver decision.

## Required Architecture Change

Long-term target: replace the narrow section model with a general `vent_channels` contract and route
to calculators/adapters by system type.

Suggested normalized shape:

```yaml
vent_channels:
  vent_channel_system_type:
    allowed:
      - schiedel_prefab
      - gas_block_vent_shaft
      - unknown

  vent_channel_total_masonry_length_m:
    meaning: paid work quantity if explicit in PDF/specification/estimate

  schiedel_prefab_items:
    repeated: true
    fields:
      - product_type        # 1x, 2x, 3x, other
      - product_name
      - size
      - quantity_pcs
      - source_row

  vent_shaft_items:
    repeated: true
    purpose: diagnostic/control only
    fields:
      - shaft_mark          # ВК-1, ВК-2, ШВ-1...
      - height_m
      - count
      - notes

  vent_channel_gas_block_cladding:
    fields:
      - area_m2
      - volume_m3
      - block_size
      - density
```

Adapter behavior:

```text
if vent_channel_system_type == schiedel_prefab:
    send Schiedel masonry length + Schiedel product pieces to Schiedel calculator/adapter

if vent_channel_system_type == gas_block_vent_shaft:
    do not send Schiedel product pieces
    route gas-block cladding to walls/parapet/vent-shaft cladding logic

if vent_channel_system_type == unknown:
    keep review/manual; no automatic material estimate rows
```

## Immediate Changes Needed Later

These are not done in this memo. They should be scheduled as separate implementation steps.

1. Add a system-type target/rule:

   ```text
   vent_channel_system_type = schiedel_prefab | gas_block_vent_shaft | unknown
   ```

2. Rename or deprecate ambiguous targets:

   Current ambiguous fields:

   - `schiedel_vent_channel_2x_count`
   - `schiedel_vent_channel_3x_count`
   - `vent_channel_2_count`

   Clearer production names:

   - `schiedel_vent_channel_1x_material_count_pcs`
   - `schiedel_vent_channel_2x_material_count_pcs`
   - `schiedel_vent_channel_3x_material_count_pcs`
   - `vent_shaft_type_2_count` or similar, but mark as `CONTROL_ONLY` / `LEGACY_DIAGNOSTIC`.

3. Add support for Schiedel 1x.

   TRC estimate has:

   ```text
   Вентиляционный блок SCHIEDEL VENT, 1 хода, наружный размер 20/25 см, высота 33 см — 21 шт
   ```

   The current calculator cannot represent this as a material line because it only has 2x and 3x
   product rows.

4. Make Schiedel product rows dynamic.

   Instead of fixed 2x and 3x only, use repeated rows:

   ```yaml
   schiedel_prefab_items:
     - product_type: 1x
       quantity_pcs: ...
     - product_type: 2x
       quantity_pcs: ...
     - product_type: 3x
       quantity_pcs: ...
   ```

   The adapter can still output fixed legacy inputs for old calculator cases until the calculator is
   generalized.

5. Mark `vent_channel_1_height_m`, `vent_channel_2_height_m`, `vent_channel_2_count` as diagnostic
   only unless there is no explicit total masonry length.

6. Update chat extraction prompt/aliases:

   - Do not map a visible `ВК-1` / `ВК-2` / shaft count on a plan to Schiedel product piece counts.
   - Do not map `1 шт` from a drawing node to material quantity.
   - Schiedel material quantities must come from specification rows with `шт`.
   - Masonry work quantity should come from explicit total length/height such as `общая длина кладки`
     or `высота вентканалов общая`.
   - If the page has vent shafts but no word `Schiedel` or no Schiedel product names, do not fill
     Schiedel material targets; set system type to `gas_block_vent_shaft` or `unknown`.

7. Update full estimate catalogs:

   - allow Schiedel 1x estimate line;
   - keep Schiedel 2x and 3x estimate lines;
   - keep delivery line;
   - keep gas-block cladding as a separate line outside Schiedel product pieces;
   - keep roof vent-shaft abutment lines in flat roof, not in Schiedel material rows.

## Current Risk

If we leave the current naming as-is, a model can produce one of two wrong behaviors:

- take `1 шт` from a visible ВК/shaft mark and use it as a Schiedel material count;
- take product pieces like `15 шт` / `21 шт` and use them as physical shaft counts/control geometry.

Both are wrong. The first breaks material estimate rows. The second breaks diagnostic/control logic.

## Practical Rule For Review Workbooks

On review sheet `01_Проверка проекта`, paid calculator inputs should be only:

- explicit total masonry length for work;
- explicit product counts from specification;
- delivery/manual supplier inputs;
- prices.

Drawing shaft counts should go to details/control, not to paid estimate quantities, unless a future
calculator explicitly needs them and the contract says why.
