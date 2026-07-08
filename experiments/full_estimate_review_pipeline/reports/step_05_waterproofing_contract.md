# Step 5 — Waterproofing Section Contract

Status: completed draft

Goal: create the first real `section_contract.yaml` for a compact new section.

Created:

- `sections/waterproofing/section_contract.yaml`

## 1. Calculator Lines

The waterproofing calculator produces 8 estimate lines:

| Code | Quantity source |
|---|---|
| `waterproofing_bitumen_mastic_work` | `waterproofing_area_m2` |
| `bitumen_primer_aquamast_18l` | calculated primer units |
| `bitumen_mastic_aquamast_18kg` | calculated mastic units |
| `eps100_wall_insulation_work` | `eps100_wall_volume_m3 / eps100_wall_thickness_m` |
| `eps100_wall_penoplex_geo_material` | calculated EPS order volume rounded to packs |
| `eps_glue_foam` | calculated foam cans |
| `waterproofing_logistics_and_supply` | calculated amount from base subtotal and logistics coefficient |
| `waterproofing_consumables_tool_amortization` | calculated amount from base subtotal and consumables coefficient |

## 2. Inputs Needed From Project

Only two project values are required in production:

| Key | Unit | Source |
|---|---|---|
| `waterproofing_area_m2` | `м2` | `AUTO_PROJECT` |
| `eps100_wall_volume_m3` | `м3` | `AUTO_PROJECT` |

The contract explicitly forbids using legacy perimeter/height fields as production inputs.

## 3. Prices

Price keys:

- `waterproofing_work_unit_price` -> `bitumen_waterproofing_work_m2`
- `primer_unit_price` -> `bitumen_primer_aquamast_18l_item`
- `mastic_unit_price` -> `bitumen_mastic_aquamast_18kg_item`
- `eps100_wall_insulation_work_unit_price` -> `eps_wall_insulation_work_m2`
- `eps100_unit_price` -> `eps_geo_100_m3`
- `glue_foam_unit_price` -> `eps_foam_glue_can`

Prices must come from price registry/project overrides/reviewed price rows, not from old cases.

## 4. Defaults

Defaults/modes are separated from project extraction:

- production mode: `waterproofing_area_calc_method = spec_area`;
- material thickness: `eps100_wall_thickness_m`;
- primer/mastic consumption and package defaults;
- EPS waste and pack defaults;
- glue foam coverage/minimum defaults;
- logistics and consumables coefficients.

Most numeric defaults are intentionally not copied into this contract. The future adapter must resolve them from a business default/catalog source and fail if they are missing.

## 5. Formulas

Important formulas:

```text
waterproofing_area_m2 = project/specification value
eps100_wall_insulation_area_m2 = eps100_wall_volume_m3 / eps100_wall_thickness_m
primer_units = ceil(waterproofing_area_m2 * primer_consumption_l_per_m2 / primer_canister_volume_l)
mastic_units = ceil(waterproofing_area_m2 * mastic_consumption_kg_per_m2_per_layer * mastic_layers / mastic_bucket_weight_kg)
eps100_wall_order_volume_m3 = ceil((eps100_wall_volume_m3 * eps_waste_coeff) / eps100_pack_volume_m3) * eps100_pack_volume_m3
glue_foam_units = max(glue_foam_min_units, ceil(eps100_wall_insulation_area_m2 / glue_foam_coverage_m2_per_can))
```

## 6. Checks

- [x] Contract has section metadata.
- [x] Contract has review parameters.
- [x] Contract has price keys.
- [x] Contract has defaults.
- [x] Contract has auto-calculated fields.
- [x] Contract has calculator input mapping.
- [x] Contract has estimate lines.
- [x] Contract keeps review workbook and final estimate workbook separate.
- [x] Contract contains no old project markers.
- [x] Contract contains no fixture totals or old expected values.

## 7. Next Step

Use this contract to prototype the review workbook for:

```text
earthworks + waterproofing
```
