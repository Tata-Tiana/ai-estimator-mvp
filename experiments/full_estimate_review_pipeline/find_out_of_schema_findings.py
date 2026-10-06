"""Finds real values the extraction parser found in a project's PDFs that don't map to
any known field in the 8 section_contract.yaml files.

The extraction prompt (chat_extraction_poc/prompts/claude_estimate_extraction_prompt.md,
line 31) already tells the model to capture such values and mark them in `notes` /
`target_code` as outside calculator_targets_compact.json — but nothing collects them into
one place. populate_review_workbook_from_extraction.py only iterates contract fields
looking for a match in the extraction, so anything found in the PDF with no matching
contract field never appears on sheet 01 at all and Elena never sees it unless she reads
the raw JSON or the PDF herself.

This script does the reverse pass: for each section, scan extraction found[] items and
report any whose effective code isn't a known target_code/key/parser_mapping alias in
that section's contract. Output is a short markdown list meant to sit alongside (or be
appended to) the служебная записка, not a replacement for it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_review_workbook_from_contracts import (  # noqa: E402
    default_contract_paths,
    load_yaml_contract,
    section_code,
    section_name,
)


def known_codes_for_contract(contract: dict[str, Any]) -> set[str]:
    codes: set[str] = set()
    params = (contract.get("review_parameters") or []) + (contract.get("supplier_inputs") or [])
    for param in params:
        if param.get("target_code"):
            codes.add(param["target_code"])
        if param.get("key"):
            codes.add(param["key"])
        parser_mapping = param.get("parser_mapping") or {}
        for alias_code in parser_mapping.get("target_codes") or []:
            codes.add(alias_code)
    return codes


def format_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def find_out_of_schema_items(
    extraction: dict[str, Any], contracts: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    by_section: dict[str, list[dict[str, Any]]] = {}
    for contract in contracts:
        sec_code = section_code(contract)
        known_codes = known_codes_for_contract(contract)
        section_data = (extraction.get("sections") or {}).get(sec_code) or {}
        items = []
        for item in section_data.get("found") or []:
            code = item.get("group_code") or item.get("target_code")
            if code and code not in known_codes:
                items.append(item)
        if items:
            by_section[sec_code] = items
    return by_section


def render_markdown(
    project_name: str,
    by_section: dict[str, list[dict[str, Any]]],
    contracts_by_code: dict[str, dict[str, Any]],
) -> str:
    lines = ["# Найдено в PDF, но не входит в текущую схему калькулятора", ""]
    lines.append(f"Проект: {project_name}")
    lines.append("")
    if not by_section:
        lines.append("Таких находок нет — всё найденное укладывается в текущую схему.")
        lines.append("")
        return "\n".join(lines)

    lines.append(
        "Эти значения реально есть в проекте (найдены парсером в PDF), но ни в одном "
        "калькуляторе для них сейчас нет поля — они не попадут в смету автоматически. "
        "Нужно решить для каждой позиции: добавить поле в схему, или обработать вручную."
    )
    lines.append("")

    for sec_code, items in by_section.items():
        contract = contracts_by_code[sec_code]
        lines.append(f"## {section_name(contract)} (`{sec_code}`)")
        lines.append("")
        for item in items:
            value_str = format_value(item.get("value"))
            unit = item.get("unit") or ""
            source = item.get("source_pdf") or "?"
            page = item.get("page_number")
            page_str = f"стр.{page}" if page is not None else "стр.?"
            table_context = item.get("table_context") or ""
            notes = item.get("notes") or ""
            label = item.get("raw_text") or item.get("item_name") or value_str
            line = f"- {label} — {value_str} {unit} ({source}, {page_str}"
            if table_context:
                line += f', "{table_context}"'
            line += ")"
            if notes:
                line += f" — {notes}"
            lines.append(line)
        lines.append("")

    return "\n".join(lines)


def run(extraction_path: Path, output_path: Path | None) -> str:
    extraction = json.loads(extraction_path.read_text(encoding="utf-8"))
    contracts = [load_yaml_contract(path) for path in default_contract_paths()]
    contracts_by_code = {section_code(c): c for c in contracts}

    by_section = find_out_of_schema_items(extraction, contracts)
    markdown = render_markdown(
        extraction.get("project_name") or "?", by_section, contracts_by_code
    )

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")

    return markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("extraction_json", help="Path to an extraction_output.json")
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to write the markdown report; prints to stdout if omitted.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output) if args.output else None
    markdown = run(Path(args.extraction_json), output_path)
    if not output_path:
        print(markdown)


if __name__ == "__main__":
    main()
