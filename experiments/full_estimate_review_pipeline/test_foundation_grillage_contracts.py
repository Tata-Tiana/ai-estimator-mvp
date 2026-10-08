import json
import sys
import unittest
from pathlib import Path


PIPELINE_DIR = Path(__file__).resolve().parent
REVIEW_TO_CALCULATOR_DIR = PIPELINE_DIR / "review_to_calculator"
if str(REVIEW_TO_CALCULATOR_DIR) not in sys.path:
    sys.path.insert(0, str(REVIEW_TO_CALCULATOR_DIR))
if str(PIPELINE_DIR) not in sys.path:
    sys.path.insert(0, str(PIPELINE_DIR))

from core.contract_loader import load_contract, review_parameter_by_key  # noqa: E402
from foundation_grillage_ownership import (  # noqa: E402
    assert_no_ownership_errors,
    audit_foundation_grillage_ownership,
)
from sections.foundation_slab.build_input import build_calculator_input  # noqa: E402
from sections.grillage.build_input import (  # noqa: E402
    build_calculator_input as build_grillage_calculator_input,
)


FIXTURES_DIR = PIPELINE_DIR / "tests" / "fixtures" / "foundation_grillage_ownership"


class FoundationGrillageContractTests(unittest.TestCase):
    def test_contracts_define_complementary_ownership(self) -> None:
        slab = load_contract("foundation_slab")
        grillage = load_contract("grillage")

        slab_types = set(slab["section"]["ownership"]["element_types"])
        grillage_types = set(grillage["section"]["ownership"]["element_types"])

        self.assertEqual(slab_types, {"slab_body"})
        self.assertFalse(slab_types & grillage_types)
        self.assertIn("rib_up", grillage_types)
        self.assertIn("rib_down", grillage_types)
        self.assertIn("foundation_wall", grillage_types)
        self.assertIn("column_footing", grillage_types)

    def test_foundation_slab_contract_has_zone_and_rebar_ownership_fields(self) -> None:
        params = review_parameter_by_key(load_contract("foundation_slab"))
        zone_columns = {column["key"] for column in params["slab_zones"]["columns"]}
        rebar_columns = {
            column["key"] for column in params["foundation_rebar_items"]["columns"]
        }

        self.assertTrue(
            {
                "zone_id",
                "display_name",
                "element_type",
                "level",
                "thickness_m",
                "concrete_volume_m3",
                "membrane_area_m2",
                "side_formwork_area_m2",
                "horizontal_insulation_volume_m3",
                "include_in_estimate",
            }.issubset(zone_columns)
        )
        self.assertTrue({"zone_id", "component"}.issubset(rebar_columns))

    def test_grillage_contract_points_to_local_calculator_without_registration(self) -> None:
        grillage = load_contract("grillage")

        self.assertEqual(grillage["section"]["status"], "local_calculator")
        self.assertEqual(
            grillage["section"]["calculator_module"],
            "experiments/grillage_calculator/grillage_calculator.py",
        )
        self.assertTrue(grillage["estimate_lines"])

    def test_grillage_adapter_builds_explicit_elements_and_priced_rebar(self) -> None:
        contract = load_contract("grillage")
        resolved_prices = {
            entry["key"]: 1
            for entry in contract["price_keys"]
            if entry["key"] != "rebar_unit_price_by_item"
        }
        resolved_prices["rebar_unit_price_by_item"] = {"rebar_a500_d12_m": 42}
        manual_values = {
            "concrete_pump_shifts": 0,
            "manual_concrete_transfer_volume_m3": 0,
            "inventory_formwork_rental_unit_price": 900,
            "rebar_metal_delivery_trucks": 1,
            "technical_supervision_amount": 5000,
        }
        normalized_review = {
            "project_name": "synthetic_grillage_adapter",
            "scalar_parameters": {
                key: {"value_number": value} for key, value in manual_values.items()
            },
            "production_items": {
                "grillage_elements": [
                    {
                        "element_id": "rib",
                        "display_name": "Ребро вверх",
                        "element_type": "rib_up",
                        "concrete_volume_m3": 5,
                        "inventory_formwork_area_m2": 10,
                    }
                ],
                "grillage_rebar_items": [
                    {
                        "element_id": "rib",
                        "code": "rib_d12",
                        "name": "Арматура ребра",
                        "steel_class": "A500C",
                        "diameter_mm": 12,
                        "source_length_m": 100,
                    }
                ],
            },
            "resolved_prices": resolved_prices,
        }

        calculator_input = build_grillage_calculator_input(normalized_review)

        self.assertEqual(calculator_input["grillage_elements"][0]["element_type"], "rib_up")
        self.assertEqual(calculator_input["rebar_items"][0]["element_id"], "rib")
        self.assertEqual(calculator_input["rebar_items"][0]["unit_price_per_m"], 42)
        self.assertEqual(calculator_input["rebar_items"][0]["kg_per_meter"], 0.888)
        self.assertEqual(calculator_input["concrete_pump_shifts"], 0)

        normalized_review["production_items"]["grillage_elements"][0][
            "inventory_formwork_area_m2"
        ] = 0
        del normalized_review["scalar_parameters"]["concrete_pump_shifts"]
        del normalized_review["scalar_parameters"]["inventory_formwork_rental_unit_price"]
        calculator_input = build_grillage_calculator_input(normalized_review)
        self.assertEqual(calculator_input["concrete_pump_shifts"], 1)
        self.assertEqual(calculator_input["inventory_formwork_rental_unit_price"], 0)

    def test_grillage_adapter_requires_supplier_rate_for_inventory_formwork(self) -> None:
        contract = load_contract("grillage")
        resolved_prices = {
            entry["key"]: 1
            for entry in contract["price_keys"]
            if entry["key"] != "rebar_unit_price_by_item"
        }
        resolved_prices["rebar_unit_price_by_item"] = {"rebar_a500_d12_m": 42}
        normalized_review = {
            "project_name": "inventory_formwork_requires_rate",
            "scalar_parameters": {},
            "production_items": {
                "grillage_elements": [
                    {
                        "element_id": "wall",
                        "element_type": "foundation_wall",
                        "concrete_volume_m3": 1,
                        "inventory_formwork_area_m2": 10,
                    }
                ],
                "grillage_rebar_items": [
                    {
                        "element_id": "wall",
                        "steel_class": "A500C",
                        "diameter_mm": 12,
                        "source_length_m": 10,
                    }
                ],
            },
            "resolved_prices": resolved_prices,
        }

        with self.assertRaisesRegex(ValueError, "supplier rate is required"):
            build_grillage_calculator_input(normalized_review)

    def test_adapter_passes_extended_zone_and_rebar_ownership_fields(self) -> None:
        contract = load_contract("foundation_slab")
        required_prices = {
            entry["key"]: 1
            for entry in contract["price_keys"]
            if entry.get("required", True) and entry["key"] != "rebar_unit_price_by_item"
        }
        required_prices["rebar_unit_price_by_item"] = {"rebar_a500_d12_m": 1}
        required_prices["thermal_insert_100_work_unit_price"] = 1
        required_prices["thermal_insert_100_material_unit_price"] = 1

        scalar_values = {
            "membrane_area_m2": 10,
            "slab_side_formwork_area_m2": 2,
            "eps50_under_slab_volume_m3": 1,
            "concrete_project_volume_m3": 10,
            "thermal_insert_100_length_m": 1,
            "thermal_insert_100_material_spec_qty": 1,
            "rebar_crane_shifts": 0,
            "rebar_metal_delivery_trucks": 0,
            "box_total_metal_weight_kg": 0,
            "concrete_pump_shifts": 0,
            "logistics_and_supply_amount": 0,
            "consumables_tool_amortization_amount": 0,
            "concrete_mixer_volume_m3": 7,
        }
        normalized_review = {
            "project_name": "synthetic_foundation_contract",
            "scalar_parameters": {
                key: {"value_number": value} for key, value in scalar_values.items()
            },
            "production_items": {
                "slab_zones": [
                    {
                        "zone_id": "main",
                        "display_name": "Основная плита",
                        "element_type": "slab_body",
                        "level": "0.000",
                        "thickness_m": 0.2,
                        "concrete_volume_m3": 10,
                        "membrane_area_m2": 10,
                    }
                ],
                "foundation_rebar_items": [
                    {
                        "code": "slab_rebar",
                        "zone_id": "main",
                        "component": "slab_body",
                        "name": "Арматура плиты",
                        "steel_class": "A500",
                        "diameter_mm": 12,
                        "source_length_m": 12,
                        "kg_per_meter": 0.888,
                    }
                ],
            },
            "resolved_prices": required_prices,
        }

        calculator_input = build_calculator_input(normalized_review)

        self.assertEqual(calculator_input["slab_zones"][0]["zone_id"], "main")
        self.assertEqual(
            calculator_input["slab_zones"][0]["display_name"],
            "Основная плита",
        )
        self.assertEqual(calculator_input["slab_zones"][0]["membrane_area_m2"], 10)
        self.assertEqual(calculator_input["rebar_items"][0]["zone_id"], "main")
        self.assertEqual(calculator_input["rebar_items"][0]["component"], "slab_body")

    def test_valid_synthetic_cases_have_no_ownership_issues(self) -> None:
        cases = json.loads((FIXTURES_DIR / "valid_cases.json").read_text(encoding="utf-8"))

        for case in cases:
            with self.subTest(case=case["name"]):
                self.assertEqual(audit_foundation_grillage_ownership(case), [])
                self.assertEqual(assert_no_ownership_errors(case), [])

    def test_invalid_synthetic_cases_report_expected_issue(self) -> None:
        cases = json.loads((FIXTURES_DIR / "invalid_cases.json").read_text(encoding="utf-8"))

        for case in cases:
            with self.subTest(case=case["name"]):
                issues = audit_foundation_grillage_ownership(case)
                matches = [
                    issue
                    for issue in issues
                    if issue.code == case["expected_code"]
                    and issue.severity == case["expected_severity"]
                ]
                self.assertTrue(matches, [issue.to_dict() for issue in issues])

                if case["expected_severity"] == "error":
                    with self.assertRaises(ValueError):
                        assert_no_ownership_errors(case)
                else:
                    self.assertEqual(assert_no_ownership_errors(case), issues)


if __name__ == "__main__":
    unittest.main()
