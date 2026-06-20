from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
import os
from pathlib import Path
from typing import Any

from normalization import display_number


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
DEFAULT_VENV_PYTHON = Path("/private/tmp/ai_estimator_venv/bin/python")


def _resolve_python() -> Path:
    env_python = os.environ.get("REVIEW_CALCULATOR_PYTHON")
    if env_python:
        return Path(env_python)
    if DEFAULT_VENV_PYTHON.exists():
        return DEFAULT_VENV_PYTHON
    return Path(sys.executable)


PYTHON = _resolve_python()

RUN_REVIEW_READER = BASE_DIR / "run_review_reader.py"
RUN_BUILD_CALCULATOR_INPUT = BASE_DIR / "run_build_calculator_input.py"
BUILD_INPUT_LINEAGE_REPORT = BASE_DIR / "build_input_lineage_report.py"
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
    "calculation_result_report.md",
    "hardcode_audit_report.md",
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


def _clean_generated_outputs(out_dir: Path) -> None:
    for name in GENERATED_FILES_TO_CLEAN:
        _safe_unlink(out_dir / name)
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


def _extract_generated_files(out_dir: Path) -> list[str]:
    candidates = [
        out_dir / "review_values_normalized.json",
        out_dir / "review_reader_report.md",
        out_dir / "earthworks_calculation_input.json",
        out_dir / "calculator_input_report.md",
        out_dir / "input_lineage_report.md",
        out_dir / "input_lineage_report.json",
        out_dir / "calculation_result" / "result.json",
        out_dir / "calculation_result" / "result.md",
        out_dir / "calculation_result" / "earthworks_result.json",
        out_dir / "calculation_result" / "earthworks_result.md",
        out_dir / "calculation_result_report.md",
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
        "lineage_summary": summary["lineage_summary"],
        "anti_cheat_status": summary["anti_cheat_status"],
        "calculator_run": summary["calculator_run"],
        "errors": summary["errors"],
    }


def _run_flow(workbook: Path, out_dir: Path, skip_clean: bool, skip_calculator: bool, skip_lineage: bool, keep_going: bool) -> dict[str, Any]:
    if not skip_clean:
        _clean_generated_outputs(out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    steps: list[dict[str, Any]] = []
    errors: list[str] = []

    normalized_json = out_dir / "review_values_normalized.json"
    calculator_input = out_dir / "earthworks_calculation_input.json"
    lineage_md = out_dir / "input_lineage_report.md"
    lineage_json = out_dir / "input_lineage_report.json"
    calculation_result_dir = out_dir / "calculation_result"
    calculation_result_report = out_dir / "calculation_result_report.md"
    full_report_md = out_dir / FULL_FLOW_REPORT_MD
    full_report_json = out_dir / FULL_FLOW_REPORT_JSON

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
        generated_files = _extract_generated_files(out_dir)
        summary = {
            "verdict": "failed",
            "anti_cheat_status": anti_cheat_status,
            "calculator_run": calculator_run,
            "lineage_status": "missing",
            "workbook": str(workbook),
            "out_dir": str(out_dir),
            "generated_files": generated_files,
            "key_totals": _extract_result_summary(result_data),
            "lineage_summary": _extract_lineage_summary(lineage_data),
            "steps": steps,
            "errors": errors,
        }
        _save_text(full_report_md, _render_markdown(summary))
        _save_json(full_report_json, _build_json_summary(summary))
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
            generated_files = _extract_generated_files(out_dir)
            summary = {
                "verdict": "failed",
                "anti_cheat_status": anti_cheat_status,
                "calculator_run": calculator_run,
                "lineage_status": "missing",
                "workbook": str(workbook),
                "out_dir": str(out_dir),
                "generated_files": generated_files,
                "key_totals": _extract_result_summary(result_data),
                "lineage_summary": _extract_lineage_summary(lineage_data),
                "steps": steps,
                "errors": errors,
            }
            _save_text(full_report_md, _render_markdown(summary))
            _save_json(full_report_json, _build_json_summary(summary))
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
            generated_files = _extract_generated_files(out_dir)
            summary = {
                "verdict": "failed",
                "anti_cheat_status": anti_cheat_status,
                "calculator_run": calculator_run,
                "lineage_status": lineage_status,
                "workbook": str(workbook),
                "out_dir": str(out_dir),
                "generated_files": generated_files,
                "key_totals": _extract_result_summary(result_data),
                "lineage_summary": _extract_lineage_summary(lineage_data),
                "steps": steps,
                "errors": errors,
            }
            _save_text(full_report_md, _render_markdown(summary))
            _save_json(full_report_json, _build_json_summary(summary))
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

    # Step 5: anti-cheat
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
    anti_cheat_step = _run_command("anti_cheat", anti_cheat_cmd, REPO_ROOT)
    record_step(anti_cheat_step)
    anti_cheat_status = anti_cheat_step["status"]

    result_data = _load_if_exists(calculation_result_dir / "result.json")
    lineage_data = _load_if_exists(lineage_json)
    generated_files = _extract_generated_files(out_dir)

    verdict = "clean"
    if errors:
        verdict = "failed"
    if anti_cheat_status != "ok":
        verdict = "failed"

    summary = {
        "verdict": verdict,
        "anti_cheat_status": "clean" if anti_cheat_status == "ok" else "failed",
        "calculator_run": calculator_run,
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
        "lineage_summary": _extract_lineage_summary(lineage_data),
        "steps": steps,
        "errors": errors,
    }

    _save_text(full_report_md, _render_markdown(summary))
    _save_json(full_report_json, _build_json_summary(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the full local earthworks review flow")
    parser.add_argument("--workbook", required=True, help="Path to local review_workbook.xlsx")
    parser.add_argument("--out-dir", required=True, help="Directory for generated outputs")
    parser.add_argument("--skip-clean", action="store_true", help="Skip cleaning generated outputs first")
    parser.add_argument("--skip-calculator", action="store_true", help="Skip running the calculator step")
    parser.add_argument("--skip-lineage", action="store_true", help="Skip building the input lineage report")
    parser.add_argument("--keep-going", action="store_true", help="Continue after a failed step when possible")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    workbook = Path(args.workbook)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = _run_flow(
        workbook=workbook,
        out_dir=out_dir,
        skip_clean=args.skip_clean,
        skip_calculator=args.skip_calculator,
        skip_lineage=args.skip_lineage,
        keep_going=args.keep_going,
    )

    return 0 if summary["verdict"] == "clean" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
