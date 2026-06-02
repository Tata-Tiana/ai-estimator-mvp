"""Run existing calculators from input_builder generated inputs."""

from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from runner_registry import RUNNER_REGISTRY, enabled_sections


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")


def clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def resolve_repo_path(path: str | Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else REPO_ROOT / path


def copy_case(template_case_dir: Path, case_dir: Path, generated_input: Path) -> None:
    if case_dir.exists():
        shutil.rmtree(case_dir)
    shutil.copytree(template_case_dir, case_dir)
    template_data = load_json(template_case_dir / "input.json")
    generated_data = load_json(generated_input)
    allowed_keys = set(template_data) | {"pricing"}
    runtime_input = {
        key: value
        for key, value in generated_data.items()
        if key in allowed_keys
    }
    write_json(case_dir / "input.json", runtime_input)


def format_candidate(candidate: str, case_dir: Path, case_name: str) -> Path:
    value = candidate.format(case_dir=str(case_dir), case_name=case_name)
    return resolve_repo_path(value)


def first_existing(candidates: list[str], case_dir: Path, case_name: str) -> Path | None:
    for candidate in candidates:
        path = format_candidate(candidate, case_dir, case_name)
        if path.exists():
            return path
    return None


def cleanup_external_calculator_outputs(registry: dict[str, Any], case_dir: Path) -> None:
    candidate_paths = [
        *registry.get("output_result_candidates", []),
        *registry.get("output_report_candidates", []),
    ]
    for candidate in candidate_paths:
        path = format_candidate(candidate, case_dir, case_dir.name)
        parent = path.parent
        if (
            parent.exists()
            and parent.name == case_dir.name
            and parent.parent.name == "output"
            and "calculator" in parent.parent.parent.name
        ):
            shutil.rmtree(parent)


def as_int(value: Any) -> int:
    if value is None or value == "":
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value))
    try:
        return int(Decimal(str(value)))
    except (InvalidOperation, ValueError):
        return 0


def extract_totals(result: dict[str, Any]) -> tuple[int, int, int]:
    totals = result.get("totals") or result.get("internal_totals") or {}
    materials = as_int(totals.get("internal_materials_total"))
    works = as_int(totals.get("internal_works_total"))
    section_total = as_int(totals.get("internal_section_total"))
    return materials, works, section_total


def extract_warnings(result: dict[str, Any]) -> list[Any]:
    warnings = result.get("warnings") or []
    pricing_summary = result.get("pricing_summary") or {}
    if pricing_summary.get("warnings_count"):
        warnings = list(warnings) + [f"pricing warnings: {pricing_summary['warnings_count']}"]
    comparison = result.get("comparison") or []
    if isinstance(comparison, dict):
        comparison = comparison.get("items") or comparison.get("checks") or []
    if not isinstance(comparison, list):
        comparison = []
    mismatches = [
        item
        for item in comparison
        if isinstance(item, dict) and item.get("status") not in {None, "ok"}
    ]
    if mismatches:
        warnings = list(warnings) + [f"comparison mismatches: {len(mismatches)}"]
    return warnings


def run_section(
    section_code: str,
    config: dict[str, Any],
    case_root: Path,
    calculations_root: Path,
) -> dict[str, Any]:
    registry = RUNNER_REGISTRY[section_code]
    generated_inputs_dir = resolve_repo_path(config["generated_inputs_dir"])
    generated_input = generated_inputs_dir / registry["generated_input_filename"]
    section_calc_dir = calculations_root / section_code
    section_calc_dir.mkdir(parents=True, exist_ok=True)

    base_result = {
        "section_code": section_code,
        "section_name": registry["section_name"],
        "enabled": True,
        "status": "skipped_missing_generated_input",
        "exit_code": None,
        "generated_input_path": str(generated_input.relative_to(REPO_ROOT)) if generated_input.exists() else str(generated_input),
        "case_dir": "",
        "result_json": "",
        "result_md": "",
        "internal_materials_total": 0,
        "internal_works_total": 0,
        "internal_section_total": 0,
        "warnings_count": 0,
        "warnings": [],
    }

    if not generated_input.exists():
        base_result["warnings"] = [f"generated input not found: {generated_input}"]
        base_result["warnings_count"] = 1
        return base_result

    case_dir = case_root / section_code
    copy_case(resolve_repo_path(registry["template_case_dir"]), case_dir, generated_input)
    base_result["case_dir"] = str(case_dir.relative_to(REPO_ROOT))

    command_text = registry["runner_command"].format(case_dir=shlex.quote(str(case_dir)))
    completed = subprocess.run(
        shlex.split(command_text),
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    (section_calc_dir / "stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (section_calc_dir / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
    (section_calc_dir / "exit_code.txt").write_text(str(completed.returncode), encoding="utf-8")
    base_result["exit_code"] = completed.returncode

    result_json_path = first_existing(registry["output_result_candidates"], case_dir, case_dir.name)
    result_md_path = first_existing(registry["output_report_candidates"], case_dir, case_dir.name)

    warnings: list[Any] = []
    if completed.returncode != 0:
        warnings.append(f"runner exited with code {completed.returncode}")

    result_found = False
    if result_json_path and result_json_path.exists():
        result_found = True
        target_json = section_calc_dir / "result.json"
        shutil.copy2(result_json_path, target_json)
        base_result["result_json"] = str(target_json.relative_to(REPO_ROOT))
        result_data = load_json(result_json_path)
        materials, works, section_total = extract_totals(result_data)
        warnings.extend(extract_warnings(result_data))
        base_result["internal_materials_total"] = materials
        base_result["internal_works_total"] = works
        base_result["internal_section_total"] = section_total
    else:
        warnings.append("result.json was not found")

    if result_md_path and result_md_path.exists():
        target_md = section_calc_dir / "result.md"
        shutil.copy2(result_md_path, target_md)
        base_result["result_md"] = str(target_md.relative_to(REPO_ROOT))
    else:
        warnings.append("result.md was not found")

    if completed.returncode != 0 and not result_found:
        status = "failed"
    elif warnings:
        status = "completed_with_warnings"
    else:
        status = "completed"

    base_result["status"] = status
    base_result["warnings"] = warnings
    base_result["warnings_count"] = len(warnings)
    cleanup_external_calculator_outputs(registry, case_dir)
    return base_result


def run_calculation_runner(case_dir: Path) -> dict[str, Any]:
    config = load_json(case_dir / "run_config.json")
    case_generated_root = case_dir / "generated_cases"
    case_calculations_root = case_dir / "calculations"
    output_root = REPO_ROOT / "experiments/calculation_runner/output" / case_dir.name
    output_calculations_root = output_root / "calculations"

    clean_dir(case_generated_root)
    clean_dir(case_calculations_root)
    clean_dir(output_calculations_root)

    sections: list[dict[str, Any]] = []
    warnings: list[Any] = []
    for section_code in RUNNER_REGISTRY:
        if section_code not in enabled_sections(config.get("sections")):
            sections.append({
                "section_code": section_code,
                "section_name": RUNNER_REGISTRY[section_code]["section_name"],
                "enabled": False,
                "status": "skipped",
                "exit_code": None,
                "generated_input_path": "",
                "case_dir": "",
                "result_json": "",
                "result_md": "",
                "internal_materials_total": 0,
                "internal_works_total": 0,
                "internal_section_total": 0,
                "warnings_count": 0,
                "warnings": [],
            })
            continue
        result = run_section(section_code, config, case_generated_root, case_calculations_root)
        sections.append(result)
        warnings.extend(f"{section_code}: {warning}" for warning in result.get("warnings", []))

    totals = {
        "sections_enabled": sum(1 for item in sections if item["enabled"]),
        "sections_completed": sum(1 for item in sections if item["status"] in {"completed", "completed_with_warnings"}),
        "sections_failed": sum(1 for item in sections if item["status"] == "failed"),
        "sections_skipped": sum(1 for item in sections if item["status"].startswith("skipped")),
        "total_materials": sum(as_int(item["internal_materials_total"]) for item in sections),
        "total_works": sum(as_int(item["internal_works_total"]) for item in sections),
        "grand_total": sum(as_int(item["internal_section_total"]) for item in sections),
    }

    result = {
        "project_name": config.get("project_name"),
        "mode": config.get("mode"),
        "generated_inputs_dir": config.get("generated_inputs_dir"),
        "sections": sections,
        "totals": totals,
        "warnings": warnings,
    }

    write_json(case_dir / "result.json", result)
    write_json(output_root / "result.json", result)
    write_markdown(case_dir / "result.md", result)
    write_markdown(output_root / "result.md", result)

    if output_calculations_root.exists():
        shutil.rmtree(output_calculations_root)
    shutil.copytree(case_calculations_root, output_calculations_root)

    return result


def write_markdown(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# Calculation runner result",
        "",
        "## Что сделано",
        "",
        "- Взяты generated `input.json` из input_builder.",
        "- Созданы временные case folders.",
        "- Запущены калькуляторы разделов.",
        "- Собраны результаты по разделам.",
        "",
        "## Важно",
        "",
        f"Этот прогон выполнен в `{result.get('mode')}`.",
        "Недостающие параметры могли быть взяты из template `input.json`.",
        "Это не production-расчёт и не финальная смета.",
        "",
        "## Сводка по разделам",
        "",
        "| Раздел | Статус | Материалы | Работы | Итого | Exit code | Warnings | Result |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for section in result["sections"]:
        lines.append(
            f"| {section['section_name']} | {section['status']} | "
            f"{section['internal_materials_total']} | {section['internal_works_total']} | "
            f"{section['internal_section_total']} | {section['exit_code']} | "
            f"{section['warnings_count']} | {section['result_json']} |"
        )

    totals = result["totals"]
    lines.extend([
        "",
        "## Итоги",
        "",
        f"- Материалы всего: `{totals['total_materials']}`",
        f"- Работы всего: `{totals['total_works']}`",
        f"- Итого: `{totals['grand_total']}`",
        "",
        "## Ошибки и предупреждения",
        "",
    ])
    if result["warnings"]:
        lines.extend([f"- {warning}" for warning in result["warnings"]])
    else:
        lines.append("Warnings нет.")
    lines.extend([
        "",
        "## Следующий шаг",
        "",
        "`box_calculator` — агрегатор, который будет собирать разделы в единую смету коробки дома.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
