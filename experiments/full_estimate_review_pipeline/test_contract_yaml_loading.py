import tempfile
import unittest
from pathlib import Path

from build_review_workbook_from_contracts import load_yaml_contract


class ContractYamlLoadingTests(unittest.TestCase):
    def test_loads_contract_without_external_yaml_runtime(self) -> None:
        content = """\
section_code: foundation_slab
enabled: true
rows:
  - code: concrete
    quantity: 12.5
optional_note: null
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "contract.yaml"
            path.write_text(content, encoding="utf-8")

            contract = load_yaml_contract(path)

        self.assertEqual(contract["section_code"], "foundation_slab")
        self.assertTrue(contract["enabled"])
        self.assertEqual(contract["rows"][0]["quantity"], 12.5)
        self.assertIsNone(contract["optional_note"])

    def test_rejects_yaml_without_mapping_at_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "contract.yaml"
            path.write_text("- first\n- second\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "YAML mapping"):
                load_yaml_contract(path)


if __name__ == "__main__":
    unittest.main()
