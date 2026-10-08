import copy
import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CALCULATOR_DIR = REPO_ROOT / "experiments" / "foundation_slab_calculator"
if str(CALCULATOR_DIR) not in sys.path:
    sys.path.insert(0, str(CALCULATOR_DIR))

from foundation_slab_calculator import (  # noqa: E402
    FoundationSlabInput,
    calculate_foundation_slab,
)


BASE_INPUT_PATH = (
    CALCULATOR_DIR
    / "cases"
    / "test_foundation_slab_formwork_spec_area"
    / "input.json"
)


def base_input() -> dict:
    return json.loads(BASE_INPUT_PATH.read_text(encoding="utf-8"))


def two_complete_zones() -> list[dict]:
    return [
        {
            "zone_id": "house",
            "display_name": "Плита дома",
            "element_type": "slab_body",
            "level": "0.000",
            "thickness_m": 0.3,
            "concrete_grade": "B22.5",
            "concrete_volume_m3": 60,
            "membrane_area_m2": 240,
            "side_formwork_area_m2": 18,
            "horizontal_insulation_material": "ЭППС",
            "horizontal_insulation_thickness_mm": 50,
            "horizontal_insulation_area_m2": 200,
            "horizontal_insulation_volume_m3": 10,
            "include_in_estimate": True,
        },
        {
            "zone_id": "terrace",
            "display_name": "Плита террасы",
            "element_type": "slab_body",
            "level": "-0.150",
            "thickness_m": 0.25,
            "concrete_grade": "B22.5",
            "concrete_volume_m3": 21,
            "membrane_area_m2": 80,
            "side_formwork_area_m2": 6.3,
            "horizontal_insulation_material": "ЭППС",
            "horizontal_insulation_thickness_mm": 50,
            "horizontal_insulation_area_m2": 70,
            "horizontal_insulation_volume_m3": 3.5,
            "include_in_estimate": True,
        },
    ]


class FoundationSlabExtendedZonesTests(unittest.TestCase):
    def test_complete_zones_drive_all_supported_quantities(self) -> None:
        raw = base_input()
        raw.update(
            {
                "membrane_area_m2": None,
                "slab_side_formwork_area_m2": None,
                "eps50_under_slab_volume_m3": None,
                "concrete_project_volume_m3": None,
                "slab_zones": two_complete_zones(),
            }
        )

        data = FoundationSlabInput.from_dict(raw)
        result = calculate_foundation_slab(data)

        self.assertEqual(data.concrete_project_volume_m3, 81)
        self.assertEqual(data.membrane_area_m2, 320)
        self.assertEqual(data.slab_side_formwork_area_m2, 24.3)
        self.assertEqual(data.eps50_under_slab_volume_m3, 13.5)
        self.assertEqual(result["calculation_blocks"]["slab_zones"]["zone_count"], 2)
        self.assertEqual(
            result["calculation_blocks"]["slab_zones"]["quantity_resolution"]
            ["concrete_project_volume_m3"]["source"],
            "slab_zones",
        )

    def test_partial_zone_breakdown_uses_explicit_section_total(self) -> None:
        raw = base_input()
        zones = two_complete_zones()
        zones[1]["membrane_area_m2"] = None
        raw["slab_zones"] = zones

        data = FoundationSlabInput.from_dict(raw)

        self.assertEqual(data.membrane_area_m2, 320)
        self.assertEqual(
            data.zone_quantity_resolution["membrane_area_m2"]["source"],
            "section_total_with_partial_zone_breakdown",
        )

    def test_partial_zone_breakdown_without_total_is_rejected(self) -> None:
        raw = base_input()
        zones = two_complete_zones()
        zones[1]["membrane_area_m2"] = None
        raw.update({"slab_zones": zones, "membrane_area_m2": None})

        with self.assertRaisesRegex(ValueError, "filled for only 1 of 2"):
            FoundationSlabInput.from_dict(raw)

    def test_conflicting_complete_total_is_rejected(self) -> None:
        raw = base_input()
        raw["slab_zones"] = two_complete_zones()
        raw["concrete_project_volume_m3"] = 90

        with self.assertRaisesRegex(ValueError, "conflicts with the complete slab_zones sum"):
            FoundationSlabInput.from_dict(raw)

    def test_excluded_zone_does_not_enter_totals(self) -> None:
        raw = base_input()
        zones = two_complete_zones()
        zones[1]["include_in_estimate"] = False
        raw.update(
            {
                "membrane_area_m2": None,
                "slab_side_formwork_area_m2": None,
                "eps50_under_slab_volume_m3": None,
                "concrete_project_volume_m3": None,
                "slab_zones": zones,
            }
        )

        data = FoundationSlabInput.from_dict(raw)
        result = calculate_foundation_slab(data)

        self.assertEqual(data.concrete_project_volume_m3, 60)
        self.assertEqual(data.membrane_area_m2, 240)
        self.assertEqual(result["calculation_blocks"]["slab_zones"]["zone_count"], 1)
        self.assertEqual(result["calculation_blocks"]["slab_zones"]["excluded_zone_count"], 1)

    def test_rib_cannot_enter_foundation_slab_zones(self) -> None:
        raw = base_input()
        zones = two_complete_zones()
        zones[0]["element_type"] = "rib_down"
        raw["slab_zones"] = zones

        with self.assertRaisesRegex(ValueError, "belong to grillage"):
            FoundationSlabInput.from_dict(raw)

    def test_rebar_zone_and_component_are_validated(self) -> None:
        raw = base_input()
        raw["slab_zones"] = two_complete_zones()
        raw["rebar_items"] = copy.deepcopy(raw["rebar_items"])
        raw["rebar_items"][0].update(
            {"zone_id": "house", "component": "thermal_insert_reinforcement"}
        )
        FoundationSlabInput.from_dict(raw)

        raw["rebar_items"][0]["zone_id"] = "unknown"
        with self.assertRaisesRegex(ValueError, "does not match an included"):
            FoundationSlabInput.from_dict(raw)

    def test_area_and_thickness_can_supply_zone_insulation_volume(self) -> None:
        raw = base_input()
        zones = two_complete_zones()
        zones[0]["horizontal_insulation_volume_m3"] = None
        zones[1]["horizontal_insulation_volume_m3"] = None
        raw.update({"slab_zones": zones, "eps50_under_slab_volume_m3": None})

        data = FoundationSlabInput.from_dict(raw)

        self.assertEqual(data.eps50_under_slab_volume_m3, 13.5)
        self.assertEqual(
            data.zone_quantity_resolution["eps50_under_slab_volume_m3"]["source"],
            "slab_zones",
        )

    def test_unsupported_concrete_grade_is_not_priced_as_b22_5(self) -> None:
        raw = base_input()
        zones = two_complete_zones()
        for zone in zones:
            zone["concrete_grade"] = "B25"
        raw["slab_zones"] = zones

        with self.assertRaisesRegex(ValueError, "supports only B22.5/M300"):
            FoundationSlabInput.from_dict(raw)


if __name__ == "__main__":
    unittest.main()
