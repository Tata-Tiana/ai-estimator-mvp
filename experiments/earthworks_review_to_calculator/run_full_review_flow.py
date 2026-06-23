from __future__ import annotations

import argparse
import datetime
import json
import shlex
import shutil
import subprocess
import sys
import os
from pathlib import Path
from typing import Any

from normalization import display_number
from export_formula_ready_to_excel import (
    build_workbook as _excel_build_workbook,
    build_report as _excel_build_report,
    DEFAULT_LOGO_PATH as _EXCEL_DEFAULT_LOGO_PATH,
    SHEET_NAME as _EXCEL_SHEET_NAME,
)
from validate_estimate_excel_workbook import validate as _excel_validate


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]


def _resolve_python() -> Path:
    env_python = os.environ.get("REVIEW_CALCULATOR_PYTHON")
    if env_python:
        return Path(env_python)
    return Path(sys.executable)


PYTHON = _resolve_python()

RUN_REVIEW_READER = BASE_DIR / "run_review_reader.py"
RUN_BUILD_CALCULATOR_INPUT = BASE_DIR / "run_build_calculator_input.py"
BUILD_INPUT_LINEAGE_REPORT = BASE_DIR / "build_input_lineage_report.py"
BUILD_FORMULA_READY_RESULT = BASE_DIR / "build_formula_ready_result.py"
RUN_CALCULATOR_FROM_REVIEW_INPUT = BASE_DIR / "run_calculator_from_review_input.py"
ANTI_CHEAT = BASE_DIR / "anti_cheat.py"

FULL_FLOW_REPORT_MD = "full_review_flow_report.md"
FULL_FLOW_REPORT_JSON = "full_review_flow_report.json"

GENERATED_FILES_TO_CLEAN = (
    "review_values_normalized.json",
    "review_reader_report.md",
    "earthworks_calculation_input.json",
    "calculator_input_report.md",
    "input_lineage_report.md",
    "input_lineage_report.json",
    "formula_ready_result.json",
    "formula_ready_report.md",
    "calculation_result_report.md",
    "hardcode_audit_report.md",
    "earthworks_formula_review.xlsx",
    "excel_formula_export_report.md",
    "excel_validation_report.md",
    "full_review_flow_report.md",
    "full_review_flow_report.json",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _save_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _format_display(value: Any) -> str:
    if value is None:
        return "missing"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, float)):
        return display_number(value)
    return str(value)


def _safe_unlink(path: Path) -> None:
    if path.exists() or path.is_symlink():
        path.unlink()


def _safe_rmtree(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


def _clean_generated_outputs(out_dir: Path, excel_filename: str = "earthworks_formula_review.xlsx") -> None:
    for name in GENERATED_FILES_TO_CLEAN:
        _safe_unlink(out_dir / name)
    if excel_filename != "earthworks_formula_review.xlsx":
        _safe_unlink(out_dir / excel_filename)
    _safe_rmtree(out_dir / "calculation_result")
    for pycache in BASE_DIR.rglob("__pycache__"):
        _safe_rmtree(pycache)


def _command_display(command: list[str]) -> str:
    parts = [str(part) for part in command]
    if parts and parts[0] == str(PYTHON):
        parts = ["python", *parts[1:]]
    return shlex.join(parts)


def _run_command(step_name: str, command: list[str], cwd: Path) -> dict[str, Any]:
    display_command = _command_display(command)
    print(f"[{step_name}] $ {display_command}")
    completed = subprocess.run(command, cwd=str(cwd), capture_output=True, text=True)
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.stderr:
        print(completed.stderr, end="" if completed.stderr.endswith("\n") else "\n", file=sys.stderr)
    status = "ok" if completed.returncode == 0 else "failed"
    print(f"[{step_name}] {status}")
    return {
        "name": step_name,
        "command": command,
        "command_display": display_command,
        "status": status,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _build_step_summary(step: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": step["name"],
        "status": step["status"],
        "returncode": step["returncode"],
        "command_display": step["command_display"],
    }


def _load_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _load_json(path)


def _extract_result_summary(result_data: dict[str, Any] | None) -> dict[str, Any]:
    if not result_data:
        return {
            "internal_materials_total": None,
            "internal_works_total": None,
            "internal_section_total": None,
            "communications_length_m": None,
            "sand_order_volume_m3": None,
            "excavator_shifts": None,
        }

    internal_totals = result_data.get("internal_totals", {}) or {}
    volume_result = result_data.get("volume_result", {}) or {}
    return {
        "internal_materials_total": internal_totals.get("internal_materials_total"),
        "internal_works_total": internal_totals.get("internal_works_total"),
        "internal_section_total": internal_totals.get("internal_section_total"),
        "communications_length_m": volume_result.get("communications_length_m"),
        "sand_order_volume_m3": volume_result.get("sand_order_volume_m3"),
        "excavator_shifts": volume_result.get("excavator_shifts"),
    }


def _extract_lineage_summary(lineage_data: dict[str, Any] | None) -> dict[str, Any]:
    if not lineage_data:
        return {
            "verdict": "missing",
            "untraced_fields": None,
            "hardcoded_project_values_detected_in_source": None,
        }
    return {
        "verdict": lineage_data.get("verdict", "missing"),
        "untraced_fields": len(lineage_data.get("untraced_fields", []) or []),
        "hardcoded_project_values_detected_in_source": lineage_data.get(
            "hardcoded_project_values_detected_in_source"
        ),
    }


def _extract_formula_ready_summary(formula_ready_data: dict[str, Any] | None) -> dict[str, Any]:
    if not formula_ready_data:
        return {
            "verdict": "missing",
            "excel_export_ready": None,
            "rows": None,
            "rows_with_formula_model": None,
            "rows_with_control_fields": None,
            "layout_model_present": None,
            "warnings": None,
            "errors": None,
            "row_count_note": None,
        }
    return {
        "verdict": "clean" if formula_ready_data.get("excel_export_ready") else "failed",
        "excel_export_ready": formula_ready_data.get("excel_export_ready"),
        "rows": len(formula_ready_data.get("rows", []) or []),
        "rows_with_formula_model": formula_ready_data.get("rows_with_formula_model"),
        "rows_with_control_fields": formula_ready_data.get("rows_with_control_fields"),
        "layout_model_present": bool(formula_ready_data.get("layout_model")),
        "warnings": len(formula_ready_data.get("warnings", []) or []),
        "errors": len(formula_ready_data.get("errors", []) or []),
        "row_count_note": formula_ready_data.get("row_count_note"),
    }


def _extract_generated_files(out_dir: Path, excel_filename: str = "earthworks_formula_review.xlsx") -> list[str]:
    candidates = [
        out_dir / "review_values_normalized.json",
        out_dir / "review_reader_report.md",
        out_dir / "earthworks_calculation_input.json",
        out_dir / "calculator_input_report.md",
        out_dir / "input_lineage_report.md",
        out_dir / "input_lineage_report.json",
        out_dir / "formula_ready_result.json",
        out_dir / "formula_ready_report.md",
        out_dir / "calculation_result" / "result.json",
        out_dir / "calculation_result" / "result.md",
        out_dir / "calculation_result" / "earthworks_result.json",
        out_dir / "calculation_result" / "earthworks_result.md",
        out_dir / "calculation_result_report.md",
        out_dir / excel_filename,
        out_dir / "excel_formula_export_report.md",
        out_dir / "excel_validation_report.md",
        out_dir / "full_review_flow_report.md",
        out_dir / "full_review_flow_report.json",
    ]
    return [str(path.relative_to(out_dir)) for path in candidates if path.exists()]


def _render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Earthworks full review flow report",
        "",
        "## Verdict",
        f"- full_flow_status: {summary['verdict']}",
        f"- anti_cheat: {summary['anti_cheat_status']}",
        f"- calculator_run: {'yes' if summary['calculator_run'] else 'no'}",
        f"- lineage_report: {summary['lineage_status']}",
        "",
        "## Inputs",
        f"- workbook: {summary['workbook']}",
        f"- out_dir: {summary['out_dir']}",
        "",
        "## Generated files",
    ]
    if summary["generated_files"]:
        lines.extend(f"- {item}" for item in summary["generated_files"])
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Key result summary",
            f"- internal_materials_total: {_format_display(summary['key_totals']['internal_materials_total'])}",
            f"- internal_works_total: {_format_display(summary['key_totals']['internal_works_total'])}",
            f"- internal_section_total: {_format_display(summary['key_totals']['internal_section_total'])}",
            f"- communications_length_m: {_format_display(summary['key_totals']['communications_length_m'])}",
            f"- sand_order_volume_m3: {_format_display(summary['key_totals']['sand_order_volume_m3'])}",
            f"- excavator_shifts: {_format_display(summary['key_totals']['excavator_shifts'])}",
            "",
            "## Formula-ready output",
            f"- formula_ready_result: {summary['formula_ready_summary']['verdict']}",
            f"- excel_export_ready: {'yes' if summary['formula_ready_summary']['excel_export_ready'] else 'no'}",
            f"- rows: {_format_display(summary['formula_ready_summary']['rows'])}",
            f"- layout_model: {'yes' if summary['formula_ready_summary']['layout_model_present'] else 'no'}",
            f"- row_count_note: {_format_display(summary['formula_ready_summary']['row_count_note'])}",
            f"- errors: {_format_display(summary['formula_ready_summary']['errors'])}",
            f"- excel_export: {summary.get('excel_export_status', 'missing')}",
            f"- excel_validation: {summary.get('excel_validation_status', 'missing')}",
            "",
            "## Data lineage summary",
            f"- untraced_fields: {_format_display(summary['lineage_summary']['untraced_fields'])}",
            "- quantities source: normalized review data",
            "- prices source: calc_price_key",
            "- defaults source: GENERIC_CALCULATOR_DEFAULTS",
            "",
            "## Step results",
        ]
    )
    for step in summary["steps"]:
        lines.append(
            f"- {step['name']}: {step['status']} (returncode={_format_display(step['returncode'])})"
        )

    lines.extend(
        [
            "",
            "## Commands executed",
        ]
    )
    for step in summary["steps"]:
        lines.append(f"- `{step['command_display']}`")

    if summary["errors"]:
        lines.extend(
            [
                "",
                "## Errors",
            ]
        )
        lines.extend(f"- {error}" for error in summary["errors"])

    return "\n".join(lines) + "\n"


def _build_json_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "verdict": summary["verdict"],
        "workbook": summary["workbook"],
        "out_dir": summary["out_dir"],
        "steps": [_build_step_summary(step) for step in summary["steps"]],
        "generated_files": summary["generated_files"],
        "key_totals": summary["key_totals"],
        "formula_ready_status": summary["formula_ready_status"],
        "excel_export_status": summary.get("excel_export_status", "missing"),
        "excel_validation_status": summary.get("excel_validation_status", "missing"),
        "formula_ready_summary": summary["formula_ready_summary"],
        "lineage_summary": summary["lineage_summary"],
        "anti_cheat_status": summary["anti_cheat_status"],
        "calculator_run": summary["calculator_run"],
        "errors": summary["errors"],
    }


def _write_full_flow_report(summary: dict[str, Any], md_path: Path, json_path: Path, out_dir: Path) -> dict[str, Any]:
    current_summary = dict(summary)
    _save_text(md_path, _render_markdown(current_summary))
    _save_json(json_path, _build_json_summary(current_summary))
    final_generated_files = _extract_generated_files(out_dir, excel_filename)
    if final_generated_files != current_summary.get("generated_files", []):
        current_summary["generated_files"] = final_generated_files
        _save_text(md_path, _render_markdown(current_summary))
        _save_json(json_path, _build_json_summary(current_summary))
    return current_summary


def _run_excel_export(
    formula_ready_json: Path,
    out_dir: Path,
    section_number: int | str | None,
    estimate_date: str | None,
    excel_filename: str = "earthworks_formula_review.xlsx",
) -> dict[str, Any]:
    xlsx_path = out_dir / excel_filename
    report_path = out_dir / "excel_formula_export_report.md"
    step_name = "excel_export"

    skipped = {
        "name": step_name,
        "command": [],
        "command_display": "skipped: formula_ready_result.json missing",
        "status": "skipped",
        "returncode": None,
        "stdout": "",
        "stderr": "",
    }

    if not formula_ready_json.exists():
        return skipped

    step: dict[str, Any] = {
        "name": step_name,
        "command": [],
        "command_display": f"build_workbook({formula_ready_json.name}) → {xlsx_path.name}",
        "status": "failed",
        "returncode": 1,
        "stdout": "",
        "stderr": "",
    }

    try:
        data = _load_json(formula_ready_json)

        if not data.get("excel_export_ready"):
            step["stderr"] = "formula_ready_result.json not marked excel_export_ready=true"
            print(f"[{step_name}] failed")
            return step

        raw_address = (
            (data.get("meta") or {}).get("project_address")
            or (data.get("project_meta") or {}).get("project_address")
        )
        if not raw_address:
            norm_path = out_dir / "review_values_normalized.json"
            if norm_path.exists():
                try:
                    norm = _load_json(norm_path)
                    raw_address = (norm.get("project_address") or {}).get("effective_value") or ""
                except Exception:
                    pass
        address = raw_address or "Адрес объекта: —"
        address_missing = not raw_address

        sn = section_number if section_number is not None else 2

        ed = (
            estimate_date
            or (data.get("meta") or {}).get("estimate_date")
            or (data.get("project_meta") or {}).get("estimate_date")
        )
        sheet_title = str(ed) if ed else datetime.date.today().strftime("%d.%m.%Y")

        print(f"[{step_name}] $ build_workbook(section={sn}, sheet={sheet_title!r})")

        wb, row_stats, warnings, total_formula_count = _excel_build_workbook(
            data, _EXCEL_DEFAULT_LOGO_PATH, address, sn, sheet_title=sheet_title,
        )

        if address_missing:
            warnings.append("project address missing in formula_ready_result — showing fallback")

        wb.save(str(xlsx_path))

        section_title = data.get("section_title", _EXCEL_SHEET_NAME)
        report_text = _excel_build_report(
            out_path=xlsx_path,
            formula_ready_path=formula_ready_json,
            row_stats=row_stats,
            warnings=warnings,
            total_formula_count=total_formula_count,
            section_title=section_title,
            helper_data_audit=data.get("helper_data_audit"),
            sheet_title=sheet_title,
        )
        report_path.write_text(report_text, encoding="utf-8")

        rows_count = len(row_stats)
        stdout = (
            f"excel: {xlsx_path}\n"
            f"report: {report_path}\n"
            f"rows_exported: {rows_count}\n"
            f"formulas_created: {total_formula_count}\n"
        )
        print(stdout, end="")
        step["status"] = "ok"
        step["returncode"] = 0
        step["stdout"] = stdout
        print(f"[{step_name}] ok")
    except Exception as exc:
        step["stderr"] = f"error: {exc}"
        print(f"[{step_name}] error: {exc}", file=sys.stderr)
        print(f"[{step_name}] failed")

    return step


def _run_flow(workbook: Path, out_dir: Path, skip_clean: bool, skip_calculator: bool, skip_lineage: bool, keep_going: bool, section_number: int | str | None = None, estimate_date: str | None = None, section_row: int = 11, data_start_row: int = 12, excel_filename: str = "earthworks_formula_review.xlsx") -> dict[str, Any]:
    if not skip_clean:
        _clean_generated_outputs(out_dir, excel_filename)

    out_dir.mkdir(parents=True, exist_ok=True)

    steps: list[dict[str, Any]] = []
    errors: list[str] = []

    normalized_json = out_dir / "review_values_normalized.json"
    calculator_input = out_dir / "earthworks_calculation_input.json"
    lineage_md = out_dir / "input_lineage_report.md"
    lineage_json = out_dir / "input_lineage_report.json"
    formula_ready_json = out_dir / "formula_ready_result.json"
    formula_ready_md = out_dir / "formula_ready_report.md"
    calculation_result_dir = out_dir / "calculation_result"
    calculation_result_report = out_dir / "calculation_result_report.md"
    full_report_md = out_dir / FULL_FLOW_REPORT_MD
    full_report_json = out_dir / FULL_FLOW_REPORT_JSON
    formula_ready_status = "missing"
    formula_ready_summary = _extract_formula_ready_summary(None)

    def record_step(step: dict[str, Any]) -> None:
        steps.append(step)
        if step["status"] == "failed":
            errors.append(
                f"{step['name']} failed with returncode {step['returncode']}"
            )

    # Step 1: review reader
    review_cmd = [
        PYTHON,
        str(RUN_REVIEW_READER),
        "--workbook",
        str(workbook),
        "--out-dir",
        str(out_dir),
    ]
    review_step = _run_command("review_reader", review_cmd, REPO_ROOT)
    record_step(review_step)
    review_ok = review_step["status"] == "ok" and normalized_json.exists()
    if not review_ok and not keep_going:
        result_data = None
        lineage_data = None
        calculator_run = False
        anti_cheat_status = "skipped"
        generated_files = _extract_generated_files(out_dir, excel_filename)
        summary = {
            "verdict": "failed",
            "anti_cheat_status": anti_cheat_status,
            "calculator_run": calculator_run,
            "formula_ready_status": formula_ready_status,
            "lineage_status": "missing",
            "workbook": str(workbook),
            "out_dir": str(out_dir),
            "generated_files": generated_files,
            "key_totals": _extract_result_summary(result_data),
            "formula_ready_summary": formula_ready_summary,
            "lineage_summary": _extract_lineage_summary(lineage_data),
            "steps": steps,
            "errors": errors,
        }
        summary = _write_full_flow_report(summary, full_report_md, full_report_json, out_dir)
        return summary

    # Step 2: calculator input
    calc_input_status = "skipped"
    if normalized_json.exists():
        calc_cmd = [
            PYTHON,
            str(RUN_BUILD_CALCULATOR_INPUT),
            "--normalized-json",
            str(normalized_json),
            "--out",
            str(calculator_input),
            "--report",
            str(out_dir / "calculator_input_report.md"),
        ]
        calc_step = _run_command("calculator_input", calc_cmd, REPO_ROOT)
        record_step(calc_step)
        calc_input_status = calc_step["status"]
        if calc_step["status"] == "failed" and not keep_going:
            result_data = None
            lineage_data = None
            calculator_run = False
            anti_cheat_status = "skipped"
            generated_files = _extract_generated_files(out_dir, excel_filename)
            summary = {
                "verdict": "failed",
                "anti_cheat_status": anti_cheat_status,
                "calculator_run": calculator_run,
                "formula_ready_status": formula_ready_status,
                "lineage_status": "missing",
                "workbook": str(workbook),
                "out_dir": str(out_dir),
                "generated_files": generated_files,
                "key_totals": _extract_result_summary(result_data),
                "formula_ready_summary": formula_ready_summary,
                "lineage_summary": _extract_lineage_summary(lineage_data),
                "steps": steps,
                "errors": errors,
            }
            summary = _write_full_flow_report(summary, full_report_md, full_report_json, out_dir)
            return summary
    else:
        errors.append("normalized review json is missing; calculator input step skipped")
        steps.append(
            {
                "name": "calculator_input",
                "command": [],
                "command_display": "skipped: normalized review json missing",
                "status": "skipped",
                "returncode": None,
                "stdout": "",
                "stderr": "",
            }
        )

    # Step 3: lineage report
    lineage_status = "missing"
    if not skip_lineage and normalized_json.exists() and calculator_input.exists():
        lineage_cmd = [
            PYTHON,
            str(BUILD_INPUT_LINEAGE_REPORT),
            "--normalized-json",
            str(normalized_json),
            "--calculator-input",
            str(calculator_input),
            "--out",
            str(lineage_md),
            "--out-json",
            str(lineage_json),
        ]
        lineage_step = _run_command("lineage_report", lineage_cmd, REPO_ROOT)
        record_step(lineage_step)
        lineage_status = lineage_step["status"]
    elif skip_lineage:
        steps.append(
            {
                "name": "lineage_report",
                "command": [],
                "command_display": "skipped: --skip-lineage",
                "status": "skipped",
                "returncode": None,
                "stdout": "",
                "stderr": "",
            }
        )
        lineage_status = "missing"
    else:
        steps.append(
            {
                "name": "lineage_report",
                "command": [],
                "command_display": "skipped: prerequisites missing",
                "status": "skipped",
                "returncode": None,
                "stdout": "",
                "stderr": "",
            }
        )

    # Step 4: calculator
    calculator_run = False
    if not skip_calculator and calculator_input.exists():
        calculator_cmd = [
            PYTHON,
            str(RUN_CALCULATOR_FROM_REVIEW_INPUT),
            "--calculator-input",
            str(calculator_input),
            "--out-dir",
            str(calculation_result_dir),
        ]
        calculator_step = _run_command("calculator", calculator_cmd, REPO_ROOT)
        record_step(calculator_step)
        calculator_run = calculator_step["status"] == "ok"
        if calculator_step["status"] == "failed" and not keep_going:
            result_data = _load_if_exists(calculation_result_dir / "result.json")
            lineage_data = _load_if_exists(lineage_json)
            anti_cheat_status = "skipped"
            generated_files = _extract_generated_files(out_dir, excel_filename)
            summary = {
                "verdict": "failed",
                "anti_cheat_status": anti_cheat_status,
                "calculator_run": calculator_run,
                "formula_ready_status": formula_ready_status,
                "lineage_status": lineage_status,
                "workbook": str(workbook),
                "out_dir": str(out_dir),
                "generated_files": generated_files,
                "key_totals": _extract_result_summary(result_data),
                "formula_ready_summary": formula_ready_summary,
                "lineage_summary": _extract_lineage_summary(lineage_data),
                "steps": steps,
                "errors": errors,
            }
            summary = _write_full_flow_report(summary, full_report_md, full_report_json, out_dir)
            return summary
    elif skip_calculator:
        steps.append(
            {
                "name": "calculator",
                "command": [],
                "command_display": "skipped: --skip-calculator",
                "status": "skipped",
                "returncode": None,
                "stdout": "",
                "stderr": "",
            }
        )
    else:
        steps.append(
            {
                "name": "calculator",
                "command": [],
                "command_display": "skipped: calculator input missing",
                "status": "skipped",
                "returncode": None,
                "stdout": "",
                "stderr": "",
            }
        )

    # Step 5: formula-ready output
    formula_ready_path = calculation_result_dir / "result.json"
    if (
        not skip_calculator
        and not skip_lineage
        and calculator_input.exists()
        and lineage_json.exists()
        and formula_ready_path.exists()
    ):
        formula_cmd = [
            PYTHON,
            str(BUILD_FORMULA_READY_RESULT),
            "--calculator-input",
            str(calculator_input),
            "--calculation-result",
            str(formula_ready_path),
            "--lineage-report",
            str(lineage_json),
            "--out",
            str(formula_ready_json),
            "--report",
            str(formula_ready_md),
        ]
        formula_step = _run_command("formula_ready", formula_cmd, REPO_ROOT)
        record_step(formula_step)
        formula_ready_status = formula_step["status"]
        formula_ready_data = _load_if_exists(formula_ready_json)
        if formula_ready_data is not None:
            formula_ready_summary = _extract_formula_ready_summary(formula_ready_data)
        if formula_step["status"] == "failed" and not keep_going:
            result_data = _load_if_exists(calculation_result_dir / "result.json")
            lineage_data = _load_if_exists(lineage_json)
            anti_cheat_status = "skipped"
            generated_files = _extract_generated_files(out_dir, excel_filename)
            summary = {
                "verdict": "failed",
                "anti_cheat_status": anti_cheat_status,
                "calculator_run": calculator_run,
                "formula_ready_status": formula_ready_status,
                "lineage_status": lineage_status,
                "workbook": str(workbook),
                "out_dir": str(out_dir),
                "generated_files": generated_files,
                "key_totals": _extract_result_summary(result_data),
                "formula_ready_summary": formula_ready_summary,
                "lineage_summary": _extract_lineage_summary(lineage_data),
                "steps": steps,
                "errors": errors,
            }
            summary = _write_full_flow_report(summary, full_report_md, full_report_json, out_dir)
            return summary
    elif skip_calculator or skip_lineage:
        steps.append(
            {
                "name": "formula_ready",
                "command": [],
                "command_display": "skipped: calculator or lineage skipped",
                "status": "skipped",
                "returncode": None,
                "stdout": "",
                "stderr": "",
            }
        )
        formula_ready_status = "skipped"
    else:
        steps.append(
            {
                "name": "formula_ready",
                "command": [],
                "command_display": "skipped: prerequisites missing",
                "status": "skipped",
                "returncode": None,
                "stdout": "",
                "stderr": "",
            }
        )
        formula_ready_status = "missing"

    # Step 6: anti-cheat
    anti_cheat_cmd = [
        PYTHON,
        str(ANTI_CHEAT),
        "--normalized-json",
        str(normalized_json),
    ]
    if calculator_input.exists():
        anti_cheat_cmd.extend(["--calculator-input", str(calculator_input)])
    if calculation_result_dir.exists():
        anti_cheat_cmd.extend(["--calculation-result-dir", str(calculation_result_dir)])
    if lineage_json.exists():
        anti_cheat_cmd.extend(["--lineage-report", str(lineage_json)])
    if formula_ready_json.exists():
        anti_cheat_cmd.extend(["--formula-ready-result", str(formula_ready_json)])
    anti_cheat_step = _run_command("anti_cheat", anti_cheat_cmd, REPO_ROOT)
    record_step(anti_cheat_step)
    anti_cheat_status = anti_cheat_step["status"]

    # Step 7: Excel export
    excel_step = _run_excel_export(formula_ready_json, out_dir, section_number, estimate_date, excel_filename)
    record_step(excel_step)
    excel_export_status = excel_step["status"]

    # Step 8: Excel validation
    excel_path = out_dir / excel_filename
    validation_report_path = out_dir / "excel_validation_report.md"
    excel_validation_status = "skipped"

    if excel_export_status == "ok" and excel_path.exists() and formula_ready_json.exists():
        val_step_name = "excel_validation"
        print(f"[{val_step_name}] $ validate({excel_path.name}, section_row={section_row}, data_start_row={data_start_row})")
        try:
            _calc_result_path = calculation_result_dir / "result.json"
            val_report = _excel_validate(
                wb_path=excel_path,
                formula_ready_path=formula_ready_json,
                calc_result_path=_calc_result_path if _calc_result_path.exists() else None,
                section_row=section_row,
                data_start_row=data_start_row,
                expected_sheet_title=estimate_date,
                section_code_arg="earthworks",
                section_number_arg=str(section_number) if section_number is not None else "2",
                section_title_arg="Земляные работы",
            )
            _save_text(validation_report_path, val_report.render_markdown())
            is_pass = val_report.is_pass()
            val_status = "ok" if is_pass else "failed"
            print(f"[{val_step_name}] {val_status}")
            val_step: dict[str, Any] = {
                "name": val_step_name,
                "command": [],
                "command_display": f"validate({excel_path.name}, section_row={section_row}, data_start_row={data_start_row})",
                "status": val_status,
                "returncode": 0 if is_pass else 1,
                "stdout": f"report: {validation_report_path}\n",
                "stderr": "",
            }
        except Exception as exc:
            val_status = "failed"
            print(f"[{val_step_name}] error: {exc}", file=sys.stderr)
            print(f"[{val_step_name}] failed")
            val_step = {
                "name": val_step_name,
                "command": [],
                "command_display": f"validate({excel_path.name})",
                "status": "failed",
                "returncode": 1,
                "stdout": "",
                "stderr": f"error: {exc}",
            }
        record_step(val_step)
        excel_validation_status = val_status
    else:
        steps.append({
            "name": "excel_validation",
            "command": [],
            "command_display": "skipped: excel export not ok or prerequisites missing",
            "status": "skipped",
            "returncode": None,
            "stdout": "",
            "stderr": "",
        })

    result_data = _load_if_exists(calculation_result_dir / "result.json")
    lineage_data = _load_if_exists(lineage_json)
    if formula_ready_json.exists():
        formula_ready_data = _load_if_exists(formula_ready_json)
        formula_ready_summary = _extract_formula_ready_summary(formula_ready_data)
    generated_files = _extract_generated_files(out_dir, excel_filename)

    verdict = "clean"
    if errors:
        verdict = "failed"
    if anti_cheat_status != "ok":
        verdict = "failed"
    if formula_ready_status not in {"ok", "skipped"}:
        verdict = "failed"
    if excel_export_status not in {"ok", "skipped"}:
        verdict = "failed"
    if excel_validation_status not in {"ok", "skipped"}:
        verdict = "failed"

    summary = {
        "verdict": verdict,
        "anti_cheat_status": "clean" if anti_cheat_status == "ok" else "failed",
        "calculator_run": calculator_run,
        "formula_ready_status": formula_ready_status,
        "excel_export_status": excel_export_status,
        "excel_validation_status": excel_validation_status,
        "lineage_status": (
            "clean"
            if lineage_status == "ok" and lineage_json.exists()
            else "missing"
            if skip_lineage or not lineage_json.exists()
            else "failed"
        ),
        "workbook": str(workbook),
        "out_dir": str(out_dir),
        "generated_files": generated_files,
        "key_totals": _extract_result_summary(result_data),
        "formula_ready_summary": formula_ready_summary,
        "lineage_summary": _extract_lineage_summary(lineage_data),
        "steps": steps,
        "errors": errors,
    }

    summary = _write_full_flow_report(summary, full_report_md, full_report_json, out_dir)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the full local earthworks review flow")
    parser.add_argument("--review-workbook", required=True, help="Path to local review_workbook.xlsx")
    parser.add_argument("--out-dir", required=True, help="Directory for generated outputs")
    parser.add_argument("--section-number", type=int, default=2, help="Section number in the estimate (default: 2)")
    parser.add_argument("--estimate-date", default=None, help="Estimate date DD.MM.YYYY for Excel tab name (default: today)")
    parser.add_argument("--section-row", type=int, default=11, help="Row number of the section header in the Excel layout (default: 11)")
    parser.add_argument("--data-start-row", type=int, default=12, help="First data row in the Excel layout (default: 12)")
    parser.add_argument("--skip-clean", action="store_true", help="Skip cleaning generated outputs first")
    parser.add_argument("--skip-calculator", action="store_true", help="Skip running the calculator step")
    parser.add_argument("--skip-lineage", action="store_true", help="Skip building the input lineage report")
    parser.add_argument("--keep-going", action="store_true", help="Continue after a failed step when possible")
    parser.add_argument("--excel-filename", default="earthworks_formula_review.xlsx", help="Output Excel filename (default: earthworks_formula_review.xlsx)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workbook = Path(args.review_workbook).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = _run_flow(
        workbook=workbook,
        out_dir=out_dir,
        skip_clean=args.skip_clean,
        skip_calculator=args.skip_calculator,
        skip_lineage=args.skip_lineage,
        keep_going=args.keep_going,
        section_number=args.section_number,
        estimate_date=args.estimate_date,
        section_row=args.section_row,
        data_start_row=args.data_start_row,
        excel_filename=args.excel_filename,
    )

    return 0 if summary["verdict"] == "clean" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
