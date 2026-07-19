# Negative test: floor_2 + D500 has no priced material path yet

`wall_block_items[]` deliberately only supports the (wall_role, block_density) combinations that
already have a real pricing path in this calculator: main_walls×D400, main_walls×D500,
floor_2×D400, parapet×D400, parapet×D500. floor_2×D500 is a known, separate gap (see
`floor_2_walls_incomplete_and_floors_count_risk` memory) — there is no D500 material/price line for
floor_2 masonry in this calculator today.

This case intentionally supplies a `floor_2`/`D500` row to prove the calculator fails loudly instead
of silently dropping that volume:

```text
wall_block_items combination wall_role='floor_2'/block_density='D500' has no priced material path yet (context='...')
```
