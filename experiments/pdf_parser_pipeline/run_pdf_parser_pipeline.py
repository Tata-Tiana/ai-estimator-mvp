from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from review_sheet_builder import build_review_sheet
from section_review_card_builder import build_review_cards


REPO_ROOT = Path(__file__).resolve().parents[2]


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def render_result_md(result: dict) -> str:
    lines = [
        "# PDF parser pipeline result",
        "",
        "## Что создано",
        "- review cards по разделам",
        "- reviewed_parameters.xlsx",
        "",
        "## Обработанные источники",
        "| source_id | source_file | pages | parsed_dir |",
        "|---|---|---:|---|",
    ]
    for source in result["sources"]:
        lines.append(f"| {source.get('source_id','')} | {source.get('source_file','')} | {source.get('pages','')} | {source.get('parsed_dir','')} |")

    lines.extend([
        "",
        "## Разделы",
        "| section_code | section_name | required total | extracted found | manual required | missing | control only | review_card |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ])
    for section in result["sections"]:
        lines.append(
            f"| {section['section_code']} | {section['section_name']} | {section['required_total']} | "
            f"{section['extracted_found']} | {section['manual_required']} | {section['missing']} | "
            f"{section['control_only']} | {section['review_card_json']} |"
        )

    lines.extend([
        "",
        "## Что должна сделать Елена",
        "1. Открыть reviewed_parameters.xlsx.",
        "2. Проверить лист parameters.",
        "3. Исправить corrected_value, если extracted_value неверный.",
        "4. Заполнить manual_required/missing.",
        "5. Ответить на вопросы в review_questions.",
        "6. После проверки поставить elena_status: reviewed/corrected/manual/ignored.",
        "",
        "## Ограничения",
        "- parser/AI не считают смету;",
        "- расчет выполняют Python-калькуляторы;",
        "- значения без уверенного источника не придумываются;",
        "- часть параметров будет ручной.",
        "",
        "## Warnings",
    ])
    if result["warnings"]:
        for warning in result["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- Нет предупреждений.")
    lines.append("")
    return "\n".join(lines)


def copy_outputs(case_dir: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    review_cards_out = output_dir / "review_cards"
    review_cards_out.mkdir(exist_ok=True)
    for path in (case_dir / "review_cards").glob("*"):
        if path.is_file():
            shutil.copy2(path, review_cards_out / path.name)
    for name in ["reviewed_parameters.xlsx", "result.json", "result.md"]:
        shutil.copy2(case_dir / name, output_dir / name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build section review cards and reviewed_parameters.xlsx from parsed PDF artifacts.")
    parser.add_argument("case_dir", type=Path)
    args = parser.parse_args()

    case_dir = args.case_dir.resolve()
    case_dir.mkdir(parents=True, exist_ok=True)
    cards, warnings = build_review_cards(case_dir)
    result = build_review_sheet(case_dir)
    result["warnings"].extend(warnings)

    result_json = case_dir / "result.json"
    result_md = case_dir / "result.md"
    write_json(result_json, result)
    result_md.write_text(render_result_md(result), encoding="utf-8")

    output_dir = REPO_ROOT / "experiments/pdf_parser_pipeline/output" / case_dir.name
    copy_outputs(case_dir, output_dir)

    print(f"review_cards: {len(cards)}")
    print(f"reviewed_parameters.xlsx: {case_dir / 'reviewed_parameters.xlsx'}")
    print(f"result.json: {result_json}")
    print(f"missing_total: {result['missing_total']}")
    print(f"manual_required_total: {result['manual_required_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

