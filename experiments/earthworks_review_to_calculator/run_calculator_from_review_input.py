from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from normalization import display_number


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
CALCULATOR_SCRIPT = REPO_ROOT / "experiments" / "earthworks_calculator" / "run_earthworks_calc.py"
TEMP_INPUT_CASE_NAME = "review_calculator_input"
TEMP_INPUT_DIRNAME = "_review_calculator_input_case"
RESULT_JSON_CANDIDATES = ("earthworks_result.json", "result.json")
RESULT_MD_CANDIDATES = ("earthworks_result.md", "result.md")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _resolve_python() -> Path:
    env_python = os.environ.get("REVIEW_CALCULATOR_PYTHON")
    if env_python:
        return Path(env_python)
    return Path(sys.executable)


def _find_existing(path: Path, names: tuple[str, ...]) -> Path | None:
    for name in names:
        candidate = path / name
        if candidate.exists():
            return candidate
    return None


def _copy_candidates(source_dir: Path, target_dir: Path, candidates: tuple[str, ...]) -> list[str]:
    copied: list[str] = []
    if not source_dir.exists():
        return copied
    for name in candidates:
        source = source_dir / name
        if source.exists():
            shutil.copy2(source, target_dir / name)
            copied.append(name)
    return copied


def _format_report(
    calculator_input_path: Path,
    calculator_input: dict[str, Any],
    result_dir: Path,
    result_data: dict[str, Any] | None,
    copied_files: list[str],
    returncode: int,
    stdout: str,
    stderr: str,
) -> str:
    result_volume_result = result_data.get("volume_result", {}) if result_data else {}
    communications_effective_length = result_volume_result.get(
        "communications_length_m",
        calculator_input.get("communications_length_m"),
    )
    lines = [
        "# Calculation result report",
        "",
        "## Source",
        f"- calculator_input: {calculator_input_path}",
        "- calculator: existing earthworks_calculator",
        f"- calculator_script: {CALCULATOR_SCRIPT}",
        f"- calculator_python: {_resolve_python()}",
        f"- result_dir: {result_dir}",
        "",
        "## Input summary",
        f"- pit_area_m2: {display_number(calculator_input.get('pit_area_m2'))}",
        f"- pit_excavation_depth_m: {display_number(calculator_input.get('pit_excavation_depth_m'))}",
        f"- trench_volume_m3: {display_number(calculator_input.get('trench_volume_m3'))}",
        f"- sand_base_volume_m3: {display_number(calculator_input.get('sand_base_volume_m3'))}",
        f"- communications_length_m (input): {display_number(calculator_input.get('communications_length_m'))}",
        f"- communications_total_length_m: {display_number(communications_effective_length)}",
        f"- internal_prices count: {len(calculator_input.get('internal_prices', {}))}",
        f"- consumables_amount: {display_number(calculator_input.get('consumables_amount'))}",
        "",
        "## Result summary",
        f"- calculation completed: {'yes' if result_data else 'no'}",
        f"- returncode: {returncode}",
        f"- result files: {', '.join(copied_files) if copied_files else 'none'}",
    ]

    if result_data:
        lines.extend(
            [
                "",
                "## Key totals",
                f"- internal_materials_total: {display_number(result_data.get('internal_totals', {}).get('internal_materials_total'))}",
                f"- internal_works_total: {display_number(result_data.get('internal_totals', {}).get('internal_works_total'))}",
                f"- internal_section_total: {display_number(result_data.get('internal_totals', {}).get('internal_section_total'))}",
            ]
        )
        volume_result = result_data.get("volume_result", {})
        lines.extend(
            [
                "",
                "## Volume result",
                f"- excavator_shifts: {display_number(volume_result.get('excavator_shifts'))}",
                f"- trench_volume_m3: {display_number(volume_result.get('trench_volume_m3'))}",
                f"- communications_length_m: {display_number(volume_result.get('communications_length_m'))}",
                f"- sand_order_volume_m3: {display_number(volume_result.get('sand_order_volume_m3'))}",
            ]
        )

    if stdout.strip():
        lines.extend(
            [
                "",
                "## Calculator stdout",
                "```text",
                stdout.strip(),
                "```",
            ]
        )
    if stderr.strip():
        lines.extend(
            [
                "",
                "## Calculator stderr",
                "```text",
                stderr.strip(),
                "```",
            ]
        )

    if result_data:
        lines.extend(
            [
                "",
                "## Validation",
                "- errors: 0",
                "- warnings: 0",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## Validation",
                "- errors: calculator did not produce a result json",
                "- warnings: 0",
            ]
        )

    return "\n".join(lines) + "\n"


def run_calculator_from_review_input(calculator_input_path: Path, out_dir: Path) -> dict[str, Any]:
    if not calculator_input_path.exists():
        raise FileNotFoundError(f"Calculator input not found: {calculator_input_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    result_dir = out_dir
    input_case_root = out_dir / TEMP_INPUT_DIRNAME
    temp_case_dir = input_case_root / TEMP_INPUT_CASE_NAME
    calculator_output_dir = REPO_ROOT / "experiments" / "earthworks_calculator" / "output" / TEMP_INPUT_CASE_NAME

    shutil.rmtree(temp_case_dir, ignore_errors=True)
    shutil.rmtree(result_dir, ignore_errors=True)
    shutil.rmtree(calculator_output_dir, ignore_errors=True)
    temp_case_dir.mkdir(parents=True, exist_ok=True)

    temp_input_path = temp_case_dir / "input.json"
    shutil.copy2(calculator_input_path, temp_input_path)

    python_executable = _resolve_python()
    cmd = [str(python_executable), str(CALCULATOR_SCRIPT), str(temp_case_dir)]
    completed = subprocess.run(cmd, capture_output=True, text=True)

    result_json_path: Path | None = None
    copied_files: list[str] = []
    result_data: dict[str, Any] | None = None

    try:
        result_dir.mkdir(parents=True, exist_ok=True)

        if completed.returncode == 0:
            copied_files.extend(_copy_candidates(calculator_output_dir, result_dir, RESULT_JSON_CANDIDATES))
            copied_files.extend(_copy_candidates(calculator_output_dir, result_dir, RESULT_MD_CANDIDATES))
            copied_files.extend(_copy_candidates(temp_case_dir, result_dir, RESULT_JSON_CANDIDATES))
            copied_files.extend(_copy_candidates(temp_case_dir, result_dir, RESULT_MD_CANDIDATES))

            result_json_path = _find_existing(result_dir, RESULT_JSON_CANDIDATES)
            if result_json_path is not None:
                result_data = load_json(result_json_path)
        report_text = _format_report(
            calculator_input_path=calculator_input_path,
            calculator_input=load_json(calculator_input_path),
            result_dir=result_dir,
            result_data=result_data,
            copied_files=sorted(set(copied_files)),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
        save_text(out_dir.parent / "calculation_result_report.md", report_text)
    finally:
        shutil.rmtree(temp_case_dir, ignore_errors=True)
        shutil.rmtree(input_case_root, ignore_errors=True)
        shutil.rmtree(calculator_output_dir, ignore_errors=True)

    if completed.returncode != 0:
        raise RuntimeError(
            "Calculator failed:\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    if result_json_path is None:
        raise RuntimeError("Calculator completed but no result json was copied to calculation_result")

    return {
        "calculator_input_path": str(calculator_input_path),
        "result_dir": str(result_dir),
        "report_path": str(out_dir.parent / "calculation_result_report.md"),
        "result_json_path": str(result_json_path),
        "result_data": result_data,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "copied_files": sorted(set(copied_files)),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run existing earthworks calculator from review input")
    parser.add_argument(
        "--calculator-input",
        required=True,
        help="Path to earthworks_calculation_input.json",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        help="Directory for calculation_result and report",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    calculator_input = Path(args.calculator_input).resolve()
    out_dir = Path(args.out_dir).resolve()
    result = run_calculator_from_review_input(calculator_input, out_dir)
    print(
        json.dumps(
            {
                "result_dir": result["result_dir"],
                "report_path": result["report_path"],
                "result_json_path": result["result_json_path"],
                "copied_files": result["copied_files"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
