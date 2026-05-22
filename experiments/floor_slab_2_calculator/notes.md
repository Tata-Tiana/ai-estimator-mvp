# Notes: Floor Slab 2

This calculator handles only internal gray cost for the section:

`Ж/Б МОНОЛИТНАЯ ПЛИТА ПЕРЕКРЫТИЯ 2-го этажа на отм. +4.680 (200мм)`

## Scope

- Client part is not calculated.
- White/client Excel area is a future export layer only.
- AI is not used.
- Excel cell addresses are not used in code, JSON, notes, or README.

## Current Case Rules

- This is a small slab / second-light area.
- No beams are calculated for floor slab 2.
- If a source line name mentions beams, the current calculation still covers only slab edges / slab perimeter.
- `concrete_placing_volume_m3 = 16.5` is a manual/project quantity for this case. It is not derived from `slab_area_m2 * slab_thickness_m`.
- `edge_insulation_height_m = 0.18` although the section title says 200 mm. Keep `0.18` for the current Excel match and expose it as a warning.
- Logistics 1% and consumables 3% are calculated from raw direct cost base before addons.
- Technical supervision, procurement/storage, overhead, and profit are zero structure lines in the current scope.

## Zero Structure Lines

The following lines are included for Excel structure only and do not change internal totals:

- Технический надзор
- Заготовительно-складские расходы
- Накладные и общехозяйственные расходы
- Сметная прибыль
