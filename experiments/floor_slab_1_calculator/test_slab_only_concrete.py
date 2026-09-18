from __future__ import annotations

import json
import unittest
from pathlib import Path

from floor_slab_calculator import calculate_floor_slabs


BASE_DIR = Path(__file__).resolve().parent


class SlabOnlyConcreteTests(unittest.TestCase):
    def make_input(self, slab_volume=57.8, beam_volume=6.17):
        data = json.loads((BASE_DIR / "cases/test_floor_slab_1/input.json").read_text())
        data["formwork_areas_calc_method"] = "spec_formwork_areas"
        data["geometry"]["slab_thickness_m"] = 0.18
        data["slab_zones"] = [{
            "context": "slab_1",
            "concrete_volume_m3": slab_volume,
            "edge_perimeter_m": 100,
            "under_slab_formwork_area_m2": 275.2,
            "edge_and_beam_formwork_area_m2": 72.28,
        }]
        data["beams_concrete_volume_m3"] = beam_volume
        return data

    def assert_slab(self, result, volume, area):
        blocks = result["calculation_blocks"]
        self.assertEqual(blocks["geometry"]["slab_concrete_volume_m3_raw"], volume)
        self.assertAlmostEqual(blocks["formwork"]["main_formwork_area_m2"], area, places=5)
        lines = {line["code"]: line for line in result["estimate_lines"]}
        self.assertEqual(lines["floor_slab_concreting_work"]["quantity_raw"], volume)

    def test_ark_pm1_slab_only_and_order(self):
        result = calculate_floor_slabs(self.make_input())
        self.assert_slab(result, 57.8, 57.8 / 0.18)
        concrete = result["calculation_blocks"]["concrete"]
        self.assertEqual(concrete["concrete_volume_with_waste_m3_raw"], 67.1685)
        self.assertEqual(concrete["order_concrete_volume_m3"], 68)

    def test_ark_pm2_slab_only_and_order(self):
        result = calculate_floor_slabs(self.make_input(17.5, 0.77))
        self.assert_slab(result, 17.5, 17.5 / 0.18)
        concrete = result["calculation_blocks"]["concrete"]
        self.assertEqual(concrete["concrete_volume_with_waste_m3_raw"], 19.1835)
        self.assertEqual(concrete["order_concrete_volume_m3"], 20)

    def test_beam_items_without_total_override(self):
        data = self.make_input()
        del data["beams_concrete_volume_m3"]
        data["beams"]["items"] = [{
            "code": "beam_b1", "name": "B1", "length_m": 10,
            "width_m": 0.3, "height_m": 0.25, "concrete_volume_m3": 6.17,
        }]
        result = calculate_floor_slabs(data)
        self.assert_slab(result, 57.8, 57.8 / 0.18)
        self.assertEqual(result["calculation_blocks"]["concrete"]["order_concrete_volume_m3"], 68)

    def test_multiple_zones_sum_slab_only(self):
        data = self.make_input(10, 3)
        second = dict(data["slab_zones"][0], context="slab_2", concrete_volume_m3=20)
        data["slab_zones"].append(second)
        result = calculate_floor_slabs(data)
        self.assert_slab(result, 30, 30 / 0.18)
        self.assertEqual(result["calculation_blocks"]["concrete"]["order_concrete_volume_m3"], 35)

    def test_no_beams(self):
        data = self.make_input(18, 0)
        data["beams"]["items"] = []
        result = calculate_floor_slabs(data)
        self.assert_slab(result, 18, 100)
        self.assertEqual(result["calculation_blocks"]["concrete"]["order_concrete_volume_m3"], 19)

    def test_additional_concrete_does_not_reduce_slab(self):
        data = self.make_input(18, 2)
        data["additional_concrete_items"] = [{
            "name": "beam_without_length", "zone_context": "slab_1", "concrete_volume_m3": 2,
        }]
        result = calculate_floor_slabs(data)
        self.assert_slab(result, 18, 100)
        # The additional item and beam override describe the same volume in this existing path.
        self.assertEqual(result["calculation_blocks"]["concrete"]["order_concrete_volume_m3"], 21)

    def test_legacy_combined_scalar_still_isolates_slab(self):
        data = self.make_input(18, 2)
        del data["slab_zones"]
        data["formwork_areas_calc_method"] = "legacy_calculated_from_geometry"
        data["geometry"]["total_concrete_volume_from_spec_m3"] = 20
        result = calculate_floor_slabs(data)
        self.assert_slab(result, 18, 100)
        self.assertEqual(result["calculation_blocks"]["concrete"]["order_concrete_volume_m3"], 21)

    def assert_dismantling_sum(self, result, expected):
        lines = {line["code"]: line for line in result["estimate_lines"]}
        dismantling = lines["formwork_dismantling_zero_internal"]
        installed = (
            lines["slab_formwork_installation_control"]["quantity_raw"]
            + lines["edge_beam_formwork_installation_control"]["quantity_raw"]
        )
        self.assertAlmostEqual(dismantling["quantity_raw"], installed, places=5)
        self.assertAlmostEqual(dismantling["quantity_raw"], expected, places=5)
        self.assertEqual(dismantling["line_total"], 0)

    def test_ark_pm1_dismantling_sum(self):
        self.assert_dismantling_sum(calculate_floor_slabs(self.make_input()), 393.391111)

    def test_ark_pm2_dismantling_sum(self):
        data = self.make_input(17.5, 0.77)
        data["slab_zones"][0]["edge_and_beam_formwork_area_m2"] = 15.2
        self.assert_dismantling_sum(calculate_floor_slabs(data), 112.422222)

    def test_dismantling_includes_beam_bottom_once(self):
        data = self.make_input(18, 2)
        data["beams_bottom_formwork_area_m2"] = 5
        self.assert_dismantling_sum(calculate_floor_slabs(data), 177.28)

    def test_dismantling_without_edge_or_beam_formwork(self):
        data = self.make_input(18, 0)
        data["beams"]["items"] = []
        data["slab_zones"][0]["edge_and_beam_formwork_area_m2"] = 0
        self.assert_dismantling_sum(calculate_floor_slabs(data), 100)

    def test_dismantling_with_separate_edge_and_beam_areas(self):
        data = self.make_input(18, 2)
        del data["slab_zones"]
        data["geometry"]["total_concrete_volume_from_spec_m3"] = 20
        data["main_formwork_area_m2"] = 100
        data["edge_formwork_area_m2"] = 12
        data["beams_formwork_area_m2"] = 8
        self.assert_dismantling_sum(calculate_floor_slabs(data), 120)


if __name__ == "__main__":
    unittest.main()
