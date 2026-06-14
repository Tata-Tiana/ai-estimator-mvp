from __future__ import annotations

import argparse
import sys

from earthworks_calculation_runner import run_calculation
from earthworks_input_builder import build_input_from_review, validate_review
from earthworks_pdf_adapter import extract_parameters
from excel_exporter import export_excel
from integrity_checks import run_integrity_checks
from parameter_review_builder import build_hints_workbook, build_review_workbook
from report_builder import build_blocked_report, build_calculate_report, build_prepare_report, build_validation_report
from source_paths import (
    CALC_RESULT_JSON_PATH,
    CALC_RESULT_MD_PATH,
    CALCULATE_BLOCKED_REPORT_PATH,
    CALCULATE_REPORT_PATH,
    FINAL_EXCEL_PATH,
    INTEGRITY_REPORT_PATH,
    PREPARE_REPORT_PATH,
    POC_INPUT_PATH,
    REVIEW_FINAL_EXCEL_PATH,
    REVIEW_HINTS_PATH,
    REVIEW_INPUT_PATH,
    REVIEW_RESULT_JSON_PATH,
    REVIEW_RESULT_MD_PATH,
    REVIEW_TABLE_PATH,
    VALIDATION_REPORT_PATH,
)


def cleanup_generated_calculation_outputs() -> None:
    for path in [
        POC_INPUT_PATH,
        REVIEW_INPUT_PATH,
        CALC_RESULT_JSON_PATH,
        CALC_RESULT_MD_PATH,
        REVIEW_RESULT_JSON_PATH,
        REVIEW_RESULT_MD_PATH,
        FINAL_EXCEL_PATH,
        REVIEW_FINAL_EXCEL_PATH,
        CALCULATE_BLOCKED_REPORT_PATH,
        CALCULATE_REPORT_PATH,
        INTEGRITY_REPORT_PATH,
    ]:
        if path.exists():
            path.unlink()


def cmd_prepare() -> int:
    cleanup_generated_calculation_outputs()
    extracted = extract_parameters()
    rows = build_review_workbook(extracted)
    build_hints_workbook()
    build_prepare_report(extracted, rows)
    print("Prepare completed.")
    print(f"- review: {REVIEW_TABLE_PATH}")
    print(f"- hints: {REVIEW_HINTS_PATH}")
    print(f"- report: {PREPARE_REPORT_PATH}")
    print("Расчет не запускался. Откройте review Excel, проверьте значения и заполните ручные поля.")
    return 0


def cmd_validate() -> int:
    errors, warnings, rows = validate_review()
    build_validation_report(errors, warnings, rows)
    print(f"Validation report: {VALIDATION_REPORT_PATH}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Validation passed. Можно запускать calculate.")
    return 0


def cmd_calculate() -> int:
    errors, warnings, rows = validate_review()
    build_validation_report(errors, warnings, rows)
    if errors:
        build_blocked_report(errors, warnings)
        print("Расчет заблокирован.")
        print("Не заполнены / не проверены обязательные поля:")
        for error in errors:
            print(f"- {error}")
        print(f"Blocked report: {CALCULATE_BLOCKED_REPORT_PATH}")
        return 2

    payload = build_input_from_review()
    result = run_calculation(payload, REVIEW_RESULT_JSON_PATH, REVIEW_RESULT_MD_PATH)
    extracted = extract_parameters()
    export_excel(extracted, payload, result, REVIEW_FINAL_EXCEL_PATH)
    build_calculate_report(payload, result)
    run_integrity_checks(extracted, payload, result)
    print("Calculate completed.")
    print(f"- input: {REVIEW_INPUT_PATH}")
    print(f"- result_json: {REVIEW_RESULT_JSON_PATH}")
    print(f"- result_md: {REVIEW_RESULT_MD_PATH}")
    print(f"- excel: {REVIEW_FINAL_EXCEL_PATH}")
    print(f"- report: {CALCULATE_REPORT_PATH}")
    print(f"- integrity: {INTEGRITY_REPORT_PATH}")
    print(f"- section_total: {result['internal_totals']['internal_section_total']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Earthworks mini-MVP CLI rehearsal")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("prepare", help="Create review table and hints, then stop")
    subparsers.add_parser("validate", help="Validate reviewed table without calculation")
    subparsers.add_parser("calculate", help="Validate reviewed table and calculate if gate passes")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "prepare":
        return cmd_prepare()
    if args.command == "validate":
        return cmd_validate()
    if args.command == "calculate":
        return cmd_calculate()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
