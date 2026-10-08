import copy
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CALCULATOR_DIR = REPO_ROOT / "experiments" / "grillage_calculator"
if str(CALCULATOR_DIR) not in sys.path:
    sys.path.insert(0, str(CALCULATOR_DIR))

from grillage_calculator import GrillageInput, calculate_grillage  # noqa: E402


def calculator_input() -> dict:
    return {
        "project_name": "synthetic_grillage",
        "grillage_elements": [
            {
                "element_id": "walls",
                "display_name": "Фундаментные стены",
                "element_type": "foundation_wall",
                "concrete_grade": "B22.5",
                "concrete_volume_m3": 20,
                "membrane_area_m2": 80,
                "inventory_formwork_area_m2": 120,
                "timber_formwork_area_m2": 0,
                "horizontal_insulation_material": "ЭППС",
                "horizontal_insulation_thickness_mm": 50,
                "horizontal_insulation_area_m2": 20,
                "horizontal_insulation_volume_m3": 1,
            },
            {
                "element_id": "pads",
                "display_name": "Подпятники",
                "element_type": "pad",
                "concrete_grade": "B22.5",
                "concrete_volume_m3": 2,
                "membrane_area_m2": 4,
                "inventory_formwork_area_m2": 0,
                "timber_formwork_area_m2": 8,
            },
        ],
        "rebar_items": [
            {
                "element_id": "walls",
                "code": "walls_d12",
                "name": "Арматура стен D12",
                "steel_class": "A500C",
                "diameter_mm": 12,
                "source_length_m": 100,
                "kg_per_meter": 0.888,
                "rod_length_m": 11.7,
                "unit_price_per_m": 42,
            },
            {
                "element_id": "pads",
                "code": "pads_d12",
                "name": "Арматура подпятников D12",
                "steel_class": "A500C",
                "diameter_mm": 12,
                "source_length_m": 20,
                "kg_per_meter": 0.888,
                "rod_length_m": 11.7,
                "unit_price_per_m": 42,
            },
        ],
        "membrane_installation_work_unit_price": 100,
        "membrane_overlap_coeff": 1.1,
        "membrane_roll_area_m2": 40,
        "planter_standard_roll_unit_price": 5000,
        "planterband_per_membrane_roll": 4,
        "planterband_unit_price": 800,
        "inventory_formwork_installation_work_unit_price": 0,
        "inventory_formwork_rental_unit_price": 900,
        "formwork_transport_unit_price": 29000,
        "inventory_formwork_consumables_unit_price": 47,
        "crane_unit_price": 28000,
        "timber_formwork_installation_work_unit_price": 0,
        "plywood_unit_price": 1450,
        "timber_unit_price": 21500,
        "formwork_dismantling_work_unit_price": 0,
        "formwork_cleaning_work_unit_price": 0,
        "rebar_frame_assembly_work_unit_price": 0,
        "rebar_waste_coeff": 1.05,
        "rebar_metal_delivery_trucks": 1,
        "rebar_metal_delivery_unit_price": 22000,
        "concreting_work_unit_price": 14000,
        "concrete_waste_coeff": 1.05,
        "concrete_round_step_m3": 0.5,
        "concrete_unit_price": 6000,
        "concrete_mixer_volume_m3": 7,
        "concrete_delivery_unit_price": 5250,
        "concrete_pump_shifts": 1,
        "concrete_pump_unit_price": 38000,
        "manual_concrete_transfer_volume_m3": 0,
        "manual_concrete_transfer_work_unit_price": 5000,
        "eps_laying_work_unit_price": 250,
        "eps_waste_coeff": 1.05,
        "eps_pack_volume_m3": 0.2776,
        "eps_unit_price": 9800,
        "technical_supervision_amount": 5000,
    }


class GrillageCalculatorTests(unittest.TestCase):
    def test_calculates_explicit_elements_without_geometry_inference(self) -> None:
        result = calculate_grillage(GrillageInput.from_dict(calculator_input()))
        quantities = result["calculation_blocks"]["quantities"]
        formwork = result["calculation_blocks"]["formwork"]

        self.assertEqual(quantities["concrete_project_volume_m3"], 22)
        self.assertEqual(quantities["membrane_area_m2"], 84)
        self.assertEqual(quantities["inventory_formwork_area_m2"], 120)
        self.assertEqual(quantities["timber_formwork_area_m2"], 8)
        self.assertEqual(quantities["dismantling_area_m2"], 128)
        self.assertEqual(formwork["transport_trips"], 2)
        self.assertEqual(formwork["crane_shifts"], 1)
        self.assertEqual(formwork["plywood_sheets"], 4)
        self.assertEqual(formwork["timber_order_volume_m3"], 0.4)

    def test_rebar_is_pooled_before_whole_rod_rounding(self) -> None:
        result = calculate_grillage(GrillageInput.from_dict(calculator_input()))
        rebar = result["calculation_blocks"]["rebar"]

        self.assertEqual(len(rebar["pools"]), 1)
        self.assertEqual(rebar["pools"][0]["source_length_m"], 120)
        self.assertEqual(rebar["pools"][0]["rods"], 11)
        self.assertEqual(rebar["pools"][0]["order_length_m"], 128.7)
        self.assertEqual(rebar["order_length_m"], 128.7)

    def test_concrete_rounding_delivery_and_manual_transfer(self) -> None:
        raw = calculator_input()
        raw["concrete_pump_shifts"] = 0
        raw["manual_concrete_transfer_volume_m3"] = 2
        result = calculate_grillage(GrillageInput.from_dict(raw))

        concrete = result["calculation_blocks"]["concrete"]
        lines = {line["code"]: line for line in result["estimate_lines"]}
        self.assertEqual(concrete["required_volume_m3"], 23.1)
        self.assertEqual(concrete["order_volume_m3"], 23.5)
        self.assertEqual(concrete["delivery_trips"], 4)
        self.assertEqual(lines["concrete_pump"]["quantity"], 0)
        self.assertEqual(lines["manual_concrete_transfer"]["quantity"], 2)
        self.assertEqual(lines["concrete_material"]["quantity"], 23.5)

    def test_shared_planter_area_controls_one_purchase(self) -> None:
        raw = calculator_input()
        raw["planter_purchase_area_m2"] = 200
        result = calculate_grillage(GrillageInput.from_dict(raw))

        planter = result["calculation_blocks"]["planter_purchase"]
        lines = {line["code"]: line for line in result["estimate_lines"]}
        self.assertEqual(planter["basis"], "shared_foundation_purchase")
        self.assertEqual(planter["rolls"], 6)
        self.assertEqual(lines["planter_membrane_installation"]["quantity"], 84)
        self.assertEqual(lines["planter_standard_material"]["quantity"], 6)
        self.assertEqual(result["warnings"], [])

    def test_inventory_formwork_thresholds_are_inclusive(self) -> None:
        raw = calculator_input()
        raw["grillage_elements"][0]["inventory_formwork_area_m2"] = 150
        result = calculate_grillage(GrillageInput.from_dict(raw))
        self.assertEqual(result["calculation_blocks"]["formwork"]["crane_shifts"], 1)

        raw["grillage_elements"][0]["inventory_formwork_area_m2"] = 200
        result = calculate_grillage(GrillageInput.from_dict(raw))
        self.assertEqual(result["calculation_blocks"]["formwork"]["transport_trips"], 2)

        raw["grillage_elements"][0]["inventory_formwork_area_m2"] = 201
        result = calculate_grillage(GrillageInput.from_dict(raw))
        self.assertEqual(result["calculation_blocks"]["formwork"]["transport_trips"], 4)
        self.assertEqual(result["calculation_blocks"]["formwork"]["crane_shifts"], 2)

    def test_ribs_belong_to_grillage_and_slab_body_does_not(self) -> None:
        raw = calculator_input()
        raw["grillage_elements"][0]["element_type"] = "rib_up"
        GrillageInput.from_dict(raw)

        raw = copy.deepcopy(raw)
        raw["grillage_elements"][0]["element_type"] = "slab_body"
        with self.assertRaisesRegex(ValueError, "does not belong to grillage"):
            GrillageInput.from_dict(raw)

    def test_timber_formwork_uses_only_explicit_project_area(self) -> None:
        raw = calculator_input()
        raw["grillage_elements"][0]["inventory_formwork_area_m2"] = 300
        raw["grillage_elements"][0]["timber_formwork_area_m2"] = 0
        raw["grillage_elements"][1]["timber_formwork_area_m2"] = 0
        result = calculate_grillage(GrillageInput.from_dict(raw))

        self.assertEqual(result["calculation_blocks"]["formwork"]["plywood_sheets"], 0)
        self.assertEqual(result["calculation_blocks"]["formwork"]["timber_order_volume_m3"], 0)

    def test_concrete_grade_metadata_does_not_block_quantity_calculation(self) -> None:
        raw = calculator_input()
        raw["grillage_elements"][0]["concrete_grade"] = "B25"

        result = calculate_grillage(GrillageInput.from_dict(raw))

        self.assertEqual(result["calculation_blocks"]["quantities"]["concrete_project_volume_m3"], 22)
        self.assertEqual(
            result["calculation_blocks"]["elements"]["included"][0]["concrete_grade"],
            "B25",
        )


if __name__ == "__main__":
    unittest.main()
