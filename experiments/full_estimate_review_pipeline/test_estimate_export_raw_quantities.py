from __future__ import annotations

import unittest

from openpyxl import Workbook

from export_calculator_results_to_estimate_workbook import (
    _cost_parts,
    _quantity,
    _setup_printing,
    _write_data_row,
)


class RawQuantityExportTests(unittest.TestCase):
    def test_raw_quantity_has_priority(self):
        self.assertEqual(_quantity({"quantity_raw": 7.4871, "quantity_display": 7.49}), 7.4871)
        self.assertEqual(_quantity({"quantity_raw": 0, "quantity": 1, "quantity_display": 2}), 0)

    def test_legacy_and_display_only_quantities_supported(self):
        self.assertEqual(_quantity({"quantity": 3}), 3)
        self.assertEqual(_quantity({"quantity_raw": None, "quantity_display": 4}), 4)

    def test_flattened_line_price_uses_raw_cost_not_display_rounding(self):
        parts = _cost_parts({"quantity_raw": 7.4871, "quantity_display": 7.49,
                             "material_total_raw": 67533.642, "material_total": 67534})
        self.assertAlmostEqual(parts[1], 9020)
        self.assertEqual(parts[2], 67534)

    def test_explicit_registry_price_preserved(self):
        parts = _cost_parts({"quantity_raw": 62.41728, "quantity_display": 62.42,
                             "internal_cost": {"material_unit_price": 7377.89,
                                               "material_total_raw": 460508.1623392,
                                               "material_total": 460508}})
        self.assertEqual(parts[0], 62.41728)
        self.assertEqual(parts[1], 7377.89)

    def test_excel_uses_raw_quantity_and_rounds_money(self):
        sheet = Workbook().active
        _write_data_row(sheet, 12, {"name": "EPS", "unit": "m3", "quantity_raw": 7.4871,
                                    "quantity_display": 7.49, "material_total_raw": 67533.642,
                                    "material_total": 67534})
        self.assertEqual(sheet["J12"].value, 7.4871)
        self.assertAlmostEqual(sheet["K12"].value, 9020)
        self.assertEqual(sheet["L12"].value, "=ROUND(J12*K12,0)")
        self.assertEqual(sheet["N12"].value, "=ROUND(J12*M12,0)")
        self.assertEqual(sheet["J12"].number_format, "0.00")

    def test_printing_excludes_grey_calculation_zone(self):
        sheet = Workbook().active
        _setup_printing(sheet, 42)

        self.assertEqual(str(sheet.print_area), "'Sheet'!$A$1:$I$42")
        self.assertEqual(sheet.print_title_rows, "$9:$10")
        self.assertEqual(sheet.page_setup.orientation, "landscape")
        self.assertEqual(sheet.page_setup.fitToWidth, 1)


if __name__ == "__main__":
    unittest.main()
