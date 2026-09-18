from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

from experiments.flat_roof_calculator.calculator import calculate_flat_roof

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE.parent / "full_estimate_review_pipeline" / "review_to_calculator"))
from core.contract_loader import all_supplier_inputs, load_contract, price_keys  # noqa: E402
from sections.flat_roof.build_input import build_calculator_input, REQUIRED_SCALARS  # noqa: E402


class RoofSeparationLayerTests(unittest.TestCase):
    def inputs(self, area):
        data = json.loads((BASE / "cases/test_flat_roof_usv/input.json").read_text())
        data.update(
            roof_geometry_calc_method="roof_zones",
            roof_zones=[{"context": "Roof", "area_m2": area, "parapet_length_m": 0,
                         "wall_abutment_length_m": 0, "operability": "non_exploitable"}],
            roof_screed_items=[],
            roof_raw_material_spec_rows=[],
            roof_fiberglass_mat_roll_area_m2=400,
            roof_fiberglass_mat_unit_price_per_m2=60,
            roof_screed_installation_work_rate_per_m2=900,
            roof_screed_board_sheet_area_m2=3.84,
            roof_screed_layers_count=2,
            roof_screed_board_unit_price=2388,
        )
        return data

    def layer(self, data):
        result = calculate_flat_roof(data)
        layers = [row for row in result["estimate_lines"] if row["code"] in
                  ("geotextile_prof_300_flat", "fiberglass_mat_technonikol_100gr")]
        self.assertEqual(len(layers), 1)
        return layers[0], result

    def test_boundaries_before_overlap(self):
        for area, code, ordered in [
            (100, "geotextile_prof_300_flat", "200"),
            (248.92, "geotextile_prof_300_flat", "300"),
            (300, "geotextile_prof_300_flat", "400"),
            (300.01, "fiberglass_mat_technonikol_100gr", "400"),
            (364, "fiberglass_mat_technonikol_100gr", "400"),
            (400, "fiberglass_mat_technonikol_100gr", "400"),
            (430, "fiberglass_mat_technonikol_100gr", "400"),
            (430.01, "fiberglass_mat_technonikol_100gr", "800"),
            (800, "fiberglass_mat_technonikol_100gr", "1200"),
        ]:
            with self.subTest(area=area):
                row, _ = self.layer(self.inputs(area))
                self.assertEqual(row["code"], code)
                self.assertEqual(row["quantity_raw"], ordered)

    def test_zones_summed_before_selection_and_rounding(self):
        data = self.inputs(364)
        template = data["roof_zones"][0]
        data["roof_zones"] = [{**template, "area_m2": area} for area in [224.3, 54.8, 84.9]]
        row, _ = self.layer(data)
        self.assertEqual(row["code"], "fiberglass_mat_technonikol_100gr")
        self.assertEqual(row["quantity_raw"], "400")
        self.assertEqual(row["formula"]["required_area_m2"], "400.4")

    def test_small_zones_rounded_once(self):
        data = self.inputs(248.92)
        template = data["roof_zones"][0]
        data["roof_zones"] = [{**template, "area_m2": area} for area in [177.52, 71.4]]
        row, _ = self.layer(data)
        self.assertEqual(row["quantity_raw"], "300")
        self.assertEqual(row["formula"]["required_area_m2"], "273.812")

    def test_raw_spec_area_does_not_drive_main_layer(self):
        data = self.inputs(364)
        before, _ = self.layer(data)
        data["roof_raw_material_spec_rows"] = [
            {"name": "Стеклохолст", "quantity": 487.3, "unit": "м2"}]
        after, _ = self.layer(data)
        self.assertEqual(before, after)

    def test_geotextile_150_not_replaced(self):
        data = self.inputs(248.92)
        data["roof_zones"][0].update(parapet_length_m=131.4, wall_abutment_length_m=7.22)
        data["roof_raw_material_spec_rows"] = [
            {"name": "Геотекстиль ПРОФ 150", "quantity": 172.59, "unit": "м2"}]
        _, result = self.layer(data)
        rows = {row["code"]: row for row in result["estimate_lines"]}
        self.assertEqual(rows["geotextile_prof_150_parapet"]["quantity_raw"], "200")
        self.assertEqual(rows["geotextile_prof_300_flat"]["quantity_raw"], "300")

    def test_geotextile_150_always_uses_abutment_work_length(self):
        for area in [248.92, 364, 500]:
            with self.subTest(area=area):
                data = self.inputs(area)
                data["roof_zones"][0].update(parapet_length_m=133.8, wall_abutment_length_m=34.4)
                rows = {row["code"]: row for row in calculate_flat_roof(data)["estimate_lines"]}
                line = rows["geotextile_prof_150_parapet"]
                self.assertEqual(line["formula"]["required_area_m2"], "185.02")
                self.assertEqual(line["quantity_raw"], "200")
                self.assertEqual(line["formula"]["parapet_and_abutment_total_length_m"],
                                 rows["pvc_membrane_abutment_installation"]["quantity_raw"])

    def test_geotextile_150_spec_does_not_override_or_duplicate(self):
        data = self.inputs(364)
        data["roof_zones"][0].update(parapet_length_m=133.8, wall_abutment_length_m=34.4)
        before = calculate_flat_roof(data)
        data["roof_raw_material_spec_rows"] = [
            {"name": "Геотекстиль ПРОФ 150", "quantity": 900, "unit": "м2"}]
        self.assertEqual(before, calculate_flat_roof(data))

    def test_geotextile_150_rounds_summed_zones_once(self):
        data = self.inputs(364)
        zone = data["roof_zones"][0]
        data["roof_zones"] = [{**zone, "area_m2": 182, "parapet_length_m": 40} for _ in range(2)]
        rows = {row["code"]: row for row in calculate_flat_roof(data)["estimate_lines"]}
        self.assertEqual(rows["geotextile_prof_150_parapet"]["quantity_raw"], "100")

    def test_geotextile_150_under_screed_and_upstands_are_separate(self):
        data = self.inputs(364)
        data["roof_screed_items"] = [{"area_m2": 21.28}]
        data["roof_zones"][0].update(parapet_length_m=80, wall_abutment_length_m=20)
        rows = {row["code"]: row for row in calculate_flat_roof(data)["estimate_lines"]}
        self.assertEqual(rows["geotextile_prof_150_parapet"]["quantity_raw"], "200")
        self.assertEqual(rows["roof_screed_geotextile"]["quantity_raw"], "100")

    def test_no_geotextile_150_when_no_abutments(self):
        data = self.inputs(364)
        data["roof_raw_material_spec_rows"] = [
            {"name": "Геотекстиль", "quantity": 900, "unit": "м2"}]
        codes = {row["code"] for row in calculate_flat_roof(data)["estimate_lines"]}
        self.assertNotIn("geotextile_prof_150_parapet", codes)

    def test_screed_layers_remain_separate_without_double_counting(self):
        data = self.inputs(500)
        data["roof_screed_items"] = [{"area_m2": 100}]
        row, result = self.layer(data)
        self.assertEqual(row["formula"]["required_area_m2"], "440")
        self.assertEqual(row["quantity_raw"], "800")
        rows = {row["code"]: row for row in result["estimate_lines"]}
        self.assertEqual(rows["roof_screed_geotextile"]["quantity_raw"], "100")
        self.assertEqual(rows["roof_screed_fiberglass_mat"]["quantity_raw"], "400")
        self.assertEqual(rows["roof_screed_installation"]["quantity_raw"], "100")

    def test_all_screed_does_not_add_main_layer(self):
        data = self.inputs(100)
        data["roof_screed_items"] = [{"area_m2": 100}]
        codes = {row["code"] for row in calculate_flat_roof(data)["estimate_lines"]}
        self.assertNotIn("geotextile_prof_300_flat", codes)
        self.assertNotIn("fiberglass_mat_technonikol_100gr", codes)
        self.assertIn("roof_screed_fiberglass_mat", codes)

    def test_excess_screed_rejected(self):
        data = self.inputs(100)
        data["roof_screed_items"] = [{"area_m2": 101}]
        with self.assertRaisesRegex(ValueError, "exceeds total roof area"):
            calculate_flat_roof(data)

    def test_coverage_warning_only_for_actual_shortfall(self):
        for area, expected in [(364, False), (400, False), (400.01, True), (430, True), (431, False)]:
            with self.subTest(area=area):
                row, result = self.layer(self.inputs(area))
                self.assertEqual(any("less than the flat-roof area" in note
                                     for note in result["warnings"]), expected)
                self.assertEqual(bool(row["notes"]), expected)

    def normalized_review(self, area):
        contract = load_contract("flat_roof")
        keys = set(REQUIRED_SCALARS) | {row["key"] for row in all_supplier_inputs(contract)
                                     if row.get("required", True)}
        return {"project_name": "Roof test",
                "scalar_parameters": {key: {"value_number": 0} for key in keys},
                "production_items": {"roof_zones": self.inputs(area)["roof_zones"]},
                "resolved_prices": {row["key"]: 1 for row in price_keys(contract)}}

    def test_adapter_requires_fiberglass_price_without_screed(self):
        review = self.normalized_review(364)
        del review["resolved_prices"]["roof_fiberglass_mat_unit_price_per_m2"]
        with self.assertRaisesRegex(ValueError, "total roof area requires fiberglass"):
            build_calculator_input(review)

    def test_adapter_small_roof_does_not_require_fiberglass_price(self):
        review = self.normalized_review(248.92)
        del review["resolved_prices"]["roof_fiberglass_mat_unit_price_per_m2"]
        data = build_calculator_input(review)
        row, _ = self.layer(data)
        self.assertEqual(row["code"], "geotextile_prof_300_flat")
        self.assertEqual(data["roof_fiberglass_one_roll_max_area_m2"], 430)


if __name__ == "__main__":
    unittest.main()
