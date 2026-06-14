from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from source_paths import CALC_RESULT_JSON_PATH, CALC_RESULT_MD_PATH, REPO_ROOT


sys.path.insert(0, str(REPO_ROOT / "experiments" / "earthworks_calculator"))
from earthworks_calculator import EarthworksInput, calculate_earthworks  # noqa: E402


def run_calculation(
    payload: dict[str, Any],
    json_path=CALC_RESULT_JSON_PATH,
    md_path=CALC_RESULT_MD_PATH,
) -> dict[str, Any]:
    data = EarthworksInput.from_dict(payload["input"])
    result = calculate_earthworks(data)
    result["price_sources"] = payload.get("price_sources", {})
    result["price_warnings"] = payload.get("price_warnings", [])
    result["poc_assumptions"] = payload.get("assumptions", [])
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown_result(result), encoding="utf-8")
    return result


def markdown_result(result: dict[str, Any]) -> str:
    lines = ["# Earthworks Mini-MVP POC Result", "", "## Estimate Lines", ""]
    lines.append("| code | name | unit | qty | material | work | total |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: |")
    for line in result["estimate_lines"]:
        lines.append(
            f"| `{line['code']}` | {line['name']} | {line['unit']} | {line['quantity']} | "
            f"{line['material_total']} | {line['work_total']} | {line['line_total']} |"
        )
    totals = result["internal_totals"]
    lines.extend(
        [
            "",
            "## Totals",
            "",
            f"- Материалы: {totals.get('internal_materials_total')}",
            f"- Работы: {totals.get('internal_works_total')}",
            f"- Итого раздел: {totals.get('internal_section_total')}",
            "",
        ]
    )
    return "\n".join(lines)
