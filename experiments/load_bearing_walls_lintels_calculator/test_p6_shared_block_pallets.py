from dataclasses import fields
from decimal import Decimal
import unittest

from load_bearing_walls_lintels_p6_calculator import (
    P6Defaults,
    P6BlockItem,
    P6LoadBearingWallsLintelsInput,
    P6Rates,
    calculate_load_bearing_walls_lintels_p6,
    _block_pallet_volume,
)


def block(item_id, volume, density="D400", size="600x400x250", **overrides):
    return dict(item_id=item_id, volume_m3=volume, block_density=density, block_size=size, **overrides)


def zone(zone_id, blocks, kind="main_walls"):
    return dict(zone_id=zone_id, display_name=zone_id, zone_kind=kind, block_items=blocks)


def calculate(zones, **defaults):
    rates = P6Rates(**{entry.name: 100 for entry in fields(P6Rates)})
    data = P6LoadBearingWallsLintelsInput.from_dict(
        dict(project_name="Shared block order", wall_zones=zones, rates=rates, defaults=P6Defaults(**defaults))
    )
    result = calculate_load_bearing_walls_lintels_p6(data)
    return result, {row["code"]: row for row in result["estimate_lines"]}


class SharedBlockPalletsTest(unittest.TestCase):
    def test_ark_order_and_logistics(self):
        result, rows = calculate(
            [
                zone("main_walls", [block("outer", 75.2), block("inner", 35.6, "D500", "600x250x250")]),
                zone("superstructure", [block("upper", 13)], "second_light"),
                zone("pm1", [block("p1", 14.8)], "parapet"),
                zone("pm2", [block("p2", 8.2)], "parapet"),
                zone("vent", [block("cladding", 1.6, "D500", "150x250x650")], "vent_chimney_cladding"),
            ]
        )
        self.assertEqual([rows[code]["quantity"] for code in ["main_walls_block_outer", "superstructure_block_upper", "parapet_block_p1"]], [79.92, 12.96, 25.92])
        pool = result["calculation_blocks"]["block_purchase_pools"]["D400:250x400x600"]
        self.assertEqual(pool["pallets"], 55)
        self.assertEqual(pool["order_volume_m3"], 118.8)
        self.assertEqual([rows[code]["quantity"] for code in ["main_walls_masonry_work", "superstructure_masonry_work", "parapet_masonry_work"]], [110.8, 13, 23])
        self.assertEqual([rows[code]["quantity"] for code in ["main_walls_blocks_delivery", "upper_parapet_vent_blocks_delivery"]], [4, 2])
        self.assertEqual([rows[code]["quantity"] for code in ["main_walls_blocks_unloading_manipulator", "upper_parapet_vent_blocks_unloading_manipulator"]], [4, 2])
        self.assertEqual([rows[code]["quantity"] for code in ["main_walls_blocks_crane_moving", "upper_parapet_vent_blocks_crane_moving", "parapet_blocks_crane_moving"]], [2, 1, 1])

    def test_two_one_and_half_pallet_stages_buy_three_pallets(self):
        result, rows = calculate(
            [zone("first", [block("a", 3)]), zone("second", [block("b", 3)])],
            gas_block_waste_coeff=1, gas_block_d400_pallet_volume_m3=2,
        )
        self.assertEqual(rows["first_block_a"]["quantity"], 4)
        self.assertEqual(rows["second_block_b"]["quantity"], 2)
        self.assertEqual(result["calculation_blocks"]["block_purchase_pools"]["D400:250x400x600"]["pallets"], 3)

    def test_stock_only_stage_keeps_material_work_adhesive_and_crane_rows(self):
        result, rows = calculate(
            [zone("first", [block("a", 0.1)]), zone("second", [block("b", 0.1)], "second_light")]
        )
        self.assertEqual(rows["second_block_b"]["quantity"], 0)
        self.assertEqual(rows["second_masonry_work"]["quantity"], 0.1)
        self.assertEqual(rows["second_block_adhesive"]["quantity"], 1)
        self.assertEqual(rows["upper_parapet_vent_blocks_delivery"]["quantity"], 0)
        self.assertEqual(rows["upper_parapet_vent_blocks_unloading_manipulator"]["quantity"], 0)
        self.assertEqual(rows["upper_parapet_vent_blocks_crane_moving"]["quantity"], 1)
        controls = result["calculation_blocks"]["zones"]["second"]["block_items"]["b"]
        self.assertEqual(controls["pallets"], 0)
        self.assertGreater(controls["available_before_m3"], controls["required_volume_m3"])

    def test_incompatible_materials_do_not_share_stock(self):
        result, rows = calculate(
            [
                zone("first", [block("d400", 0.1)]),
                zone("second", [block("d500", 0.1, "D500", "600x250x250")]),
                zone("vent", [block("thin", 0.1, "D500", "600x150x250")], "vent_chimney_cladding"),
            ]
        )
        self.assertEqual(len(result["calculation_blocks"]["block_purchase_pools"]), 3)
        self.assertEqual(rows["second_block_d500"]["quantity"], 1.8)
        self.assertEqual(rows["vent_block_thin"]["quantity"], 1.8)

    def test_crane_workload_counts_stock_lift_not_only_new_purchase(self):
        result, rows = calculate(
            [zone("first", [block("a", 1)]), zone("second", [block("b", 33)], "second_light")],
            gas_block_waste_coeff=1, gas_block_d400_pallet_volume_m3=100, crane_trucks_per_shift=1,
        )
        self.assertEqual(rows["second_block_b"]["quantity"], 0)
        self.assertEqual(rows["upper_parapet_vent_blocks_crane_moving"]["quantity"], 2)
        batch = result["calculation_blocks"]["crane_batches"]["upper_parapet_vent"]
        self.assertEqual(batch["block_order_volume_m3"], 0)
        self.assertEqual(batch["block_lift_volume_m3"], 33)

    def test_negative_waste_coefficient_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "waste coefficient must be positive"):
            calculate([zone("first", [block("a", 1)])], gas_block_waste_coeff=-1)

    def test_group_raw_volumes_before_rounding_and_keep_item_controls(self):
        result, rows = calculate([zone("first", [block("a", 0.1), block("b", 0.2)])])
        self.assertIn("first_block_a", rows)
        self.assertNotIn("first_block_b", rows)
        self.assertEqual(rows["first_block_a"]["quantity"], 2.16)
        controls = result["calculation_blocks"]["zones"]["first"]["block_items"]
        self.assertEqual(controls["a"]["spec_volume_m3"], 0.1)
        self.assertEqual(controls["b"]["spec_volume_m3"], 0.2)

    def test_same_dimensions_in_different_order_share_stock(self):
        result, rows = calculate(
            [zone("first", [block("a", 0.1)]), zone("second", [block("b", 0.1, size="250х600х400 (стены)")])]
        )
        self.assertEqual(len(result["calculation_blocks"]["block_purchase_pools"]), 1)
        self.assertEqual(rows["second_block_b"]["quantity"], 0)

    def test_different_piece_lengths_do_not_share_stock(self):
        result, rows = calculate(
            [zone("first", [block("a", 0.1, "D500", "600x150x250")]), zone("second", [block("b", 0.1, "D500", "650x150x250")])]
        )
        self.assertEqual(len(result["calculation_blocks"]["block_purchase_pools"]), 2)
        self.assertEqual(rows["second_block_b"]["quantity"], 1.8)

    def test_conflicting_pallet_overrides_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "pallet volume differs between zones"):
            calculate([zone("first", [block("a", 1)]), zone("second", [block("b", 1, pallet_volume_m3=2.15)])])

    def test_conflicting_price_overrides_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "price or pallet volume differs between zones"):
            calculate([zone("first", [block("a", 1)]), zone("second", [block("b", 1, material_unit_price=200)])])

    def test_conflicting_prices_within_zone_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "differs within zone"):
            calculate([zone("first", [block("a", 1), block("b", 1, material_unit_price=200)])])

    def test_zero_volume_stage_does_not_buy_extra_pallet(self):
        _, rows = calculate([zone("first", [block("a", 1)]), zone("second", [block("b", 0)])])
        self.assertEqual(rows["second_block_b"]["quantity"], 0)
        self.assertNotIn("second_blocks_delivery", rows)

    def test_stage_order_changes_allocation_but_not_total_purchase(self):
        stages = [zone("first", [block("a", 75.2)]), zone("second", [block("b", 13)]), zone("third", [block("c", 23)])]
        for zones in [stages, list(reversed(stages))]:
            result, rows = calculate(zones)
            purchased = sum(Decimal(str(row["quantity"])) for code, row in rows.items() if "_block_" in code and row["unit"] == "м3")
            self.assertEqual(purchased, Decimal("118.8"))
            self.assertEqual(result["calculation_blocks"]["block_purchase_pools"]["D400:250x400x600"]["pallets"], 55)

    def test_400mm_d400_and_d500_use_216_pallet(self):
        for density in ["D400", "D500", "Д400", "Д500"]:
            for size in ["600x400x250", "250х600х400 (h)", "600×400×250", "650x400x250"]:
                with self.subTest(density=density, size=size):
                    item = P6BlockItem.from_dict(block("a", 1, density, size))
                    self.assertEqual(_block_pallet_volume(item, P6Defaults()), 2.16)

    def test_other_thicknesses_use_18_pallet_regardless_of_density(self):
        for density in ["D300", "D400", "D500", "D600"]:
            for thickness in [100, 150, 200, 250, 300]:
                with self.subTest(density=density, thickness=thickness):
                    item = P6BlockItem.from_dict(block("a", 1, density, f"600x{thickness}x250"))
                    self.assertEqual(_block_pallet_volume(item, P6Defaults()), 1.8)

    def test_unlisted_family_needs_price_but_not_pallet_override(self):
        _, rows = calculate([zone("first", [block("a", 1, "D400", "600x200x250", material_unit_price=123)])])
        self.assertEqual(rows["first_block_a"]["quantity"], 1.8)
        with self.assertRaisesRegex(ValueError, "without explicit material_unit_price"):
            calculate([zone("first", [block("a", 1, "D500", "600x400x250")])])

    def test_equal_pallet_capacity_does_not_mix_densities(self):
        result, rows = calculate([
            zone("first", [block("a", 0.1)]),
            zone("second", [block("b", 0.1, "D500", material_unit_price=100)]),
        ])
        self.assertEqual(len(result["calculation_blocks"]["block_purchase_pools"]), 2)
        self.assertEqual(rows["second_block_b"]["quantity"], 2.16)

    def test_explicit_pallet_override_still_wins(self):
        _, rows = calculate([zone("first", [block("a", 1, pallet_volume_m3=3)])])
        self.assertEqual(rows["first_block_a"]["quantity"], 3)

    def test_invalid_dimensions_do_not_silently_get_standard_pallet(self):
        item = P6BlockItem.from_dict(block("a", 1, size="unknown", material_unit_price=100))
        with self.assertRaisesRegex(ValueError, "Invalid block dimensions"):
            _block_pallet_volume(item, P6Defaults())


if __name__ == "__main__":
    unittest.main()
