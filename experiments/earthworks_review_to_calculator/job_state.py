from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
JOB_STATE_FILENAME = "job_state.json"
SCHEMA_VERSION = 1


def _rel_to_repo(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _extract_project_name(job_id: str) -> str:
    marker = "_earthworks_stage1_"
    if marker in job_id:
        return job_id.split(marker)[0].upper()
    return job_id


def load_job_state(stage1_job_dir: Path) -> dict[str, Any]:
    path = stage1_job_dir / JOB_STATE_FILENAME
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_job_state(stage1_job_dir: Path, state: dict[str, Any]) -> None:
    path = stage1_job_dir / JOB_STATE_FILENAME
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def init_or_update_from_stage1(stage1_job_dir: Path) -> dict[str, Any]:
    state = load_job_state(stage1_job_dir)
    job_id = stage1_job_dir.name

    metadata_path = stage1_job_dir / "google" / "google_sheet_metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"google_sheet_metadata.json not found: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    spreadsheet_id = metadata.get("spreadsheet_id", "")
    if not spreadsheet_id:
        raise ValueError(f"spreadsheet_id is empty in {metadata_path}")

    project_name = state.get("project_name") or _extract_project_name(job_id)

    state["schema_version"] = SCHEMA_VERSION
    state["job_id"] = job_id
    state["project_name"] = project_name
    state["section_code"] = "earthworks"
    state["section_title"] = "Земляные работы"
    state["stage1"] = {
        "job_dir": _rel_to_repo(stage1_job_dir),
        "status": "prepared",
        "summary_json": "reports/stage1_summary.json",
    }
    state["google_sheet"] = {
        "status": metadata.get("status", "unknown"),
        "spreadsheet_id": spreadsheet_id,
        "url": metadata.get("url", ""),
        "sharing": metadata.get("sharing", {"mode": "owner_only", "type": None, "role": None, "status": "skipped"}),
        "metadata_json": "google/google_sheet_metadata.json",
        "local_review_workbook": "google/review_workbook.xlsx",
    }

    if "last_build" not in state:
        state["last_build"] = {"status": "not_built"}

    return state


def update_source_and_parser(
    stage1_job_dir: Path,
    input_pdfs: list[dict[str, Any]],
    parser_run: dict[str, Any],
) -> dict[str, Any]:
    """Add source (PDF info) and parser (run stats) blocks to job_state."""
    state = load_job_state(stage1_job_dir)
    state["source"] = {
        "input_pdfs": input_pdfs,
    }
    state["parser"] = {
        "active_run": "run_001",
        "active_artifacts_dir": parser_run.get("out_dir", ""),
        "status": "ok" if not parser_run.get("errors") else "errors",
        "pages_count": parser_run.get("pages_count"),
        "tables_count": parser_run.get("tables_count"),
        "logical_pages_count": parser_run.get("logical_pages_count"),
        "candidates_count": parser_run.get("candidates_count"),
        "errors": parser_run.get("errors", []),
    }
    save_job_state(stage1_job_dir, state)
    return state


def update_after_rerun(
    stage1_job_dir: Path,
    old_parser_block: dict[str, Any],
    new_run_name: str,
    new_run_rel: str,
    new_parser_run: dict[str, Any],
    old_google_sheet: dict[str, Any],
    new_metadata: dict[str, Any],
    archive_dir_rel: str,
    reason: str,
    rerun_at: str,
) -> dict[str, Any]:
    """Switch active parser run, preserve old run in history, update Google Sheet."""
    state = load_job_state(stage1_job_dir)

    # Archive old parser block
    parser_history: list[dict[str, Any]] = state.get("parser_history", [])
    if old_parser_block.get("active_run"):
        parser_history.append({
            "archived_at": rerun_at,
            "run": old_parser_block["active_run"],
            "artifacts_dir": old_parser_block.get("active_artifacts_dir", ""),
            "status": old_parser_block.get("status", ""),
            "reason": "replaced_by_rerun",
        })
    state["parser_history"] = parser_history

    # Set new active parser
    errors = new_parser_run.get("errors", [])
    state["parser"] = {
        "active_run": new_run_name,
        "active_artifacts_dir": new_run_rel,
        "status": "completed" if not errors else "completed_with_errors",
        "pages_count": new_parser_run.get("pages_count"),
        "tables_count": new_parser_run.get("tables_count"),
        "logical_pages_count": new_parser_run.get("logical_pages_count"),
        "candidates_count": new_parser_run.get("candidates_count"),
        "warnings": new_parser_run.get("warnings", []),
        "errors": errors,
        "rerun_at": rerun_at,
        "rerun_reason": reason,
    }

    # Archive old Google Sheet reference
    gs_history: list[dict[str, Any]] = state.get("google_sheet_history", [])
    if old_google_sheet.get("spreadsheet_id"):
        gs_history.append({
            "archived_at": rerun_at,
            "spreadsheet_id": old_google_sheet.get("spreadsheet_id", ""),
            "spreadsheet_url": old_google_sheet.get("url", ""),
            "local_archive_dir": archive_dir_rel,
            "reason": f"parser_rerun",
        })
    state["google_sheet_history"] = gs_history

    # Set new Google Sheet
    state["google_sheet"] = {
        "status": new_metadata.get("status", "unknown"),
        "spreadsheet_id": new_metadata.get("spreadsheet_id", ""),
        "url": new_metadata.get("url", ""),
        "sharing": new_metadata.get("sharing", {"mode": "owner_only", "type": None, "role": None, "status": "skipped"}),
        "metadata_json": "google/google_sheet_metadata.json",
        "local_review_workbook": "google/review_workbook.xlsx",
        "created_from_parser_run": new_run_name,
    }

    save_job_state(stage1_job_dir, state)
    return state


def update_after_recreate(
    stage1_job_dir: Path,
    old_google_sheet: dict[str, Any],
    new_metadata: dict[str, Any],
    archive_dir_rel: str,
    reason: str,
    recreated_at: str,
) -> dict[str, Any]:
    """Archive old Google Sheet reference and write new one into job_state."""
    state = load_job_state(stage1_job_dir)

    history: list[dict[str, Any]] = state.get("google_sheet_history", [])
    if old_google_sheet.get("spreadsheet_id"):
        history.append({
            "archived_at": recreated_at,
            "spreadsheet_id": old_google_sheet.get("spreadsheet_id", ""),
            "spreadsheet_url": old_google_sheet.get("url", ""),
            "local_archive_dir": archive_dir_rel,
            "reason": reason,
        })
    state["google_sheet_history"] = history

    state["google_sheet"] = {
        "status": new_metadata.get("status", "unknown"),
        "spreadsheet_id": new_metadata.get("spreadsheet_id", ""),
        "url": new_metadata.get("url", ""),
        "sharing": new_metadata.get("sharing", {"mode": "owner_only", "type": None, "role": None, "status": "skipped"}),
        "metadata_json": "google/google_sheet_metadata.json",
        "local_review_workbook": "google/review_workbook.xlsx",
        "recreated_at": recreated_at,
        "recreate_reason": reason,
    }

    save_job_state(stage1_job_dir, state)
    return state


def update_after_build(
    stage1_job_dir: Path,
    out_dir: Path,
    returncode: int,
    started_at: str,
    excel_filename: str = "earthworks_formula_review.xlsx",
) -> dict[str, Any]:
    state = load_job_state(stage1_job_dir)
    now = datetime.now().isoformat(timespec="seconds")
    out_dir_rel = _rel_to_repo(out_dir)

    if returncode != 0:
        state["last_build"] = {
            "status": "failed",
            "started_at": started_at,
            "failed_at": now,
            "out_dir": out_dir_rel,
            "returncode": returncode,
            "error": "full flow failed",
            "full_flow_report": "full_review_flow_report.json",
            "excel_validation_report": "excel_validation_report.md",
        }
        save_job_state(stage1_job_dir, state)
        return state

    totals: dict[str, Any] = {}
    key_values: dict[str, Any] = {}
    result_path = out_dir / "calculation_result" / "result.json"
    if result_path.exists():
        result_data = json.loads(result_path.read_text(encoding="utf-8"))
        it = result_data.get("internal_totals") or {}
        vr = result_data.get("volume_result") or {}
        inp = result_data.get("inputs") or {}
        totals = {
            "materials": it.get("internal_materials_total"),
            "works": it.get("internal_works_total"),
            "section_total": it.get("internal_section_total"),
        }
        key_values = {
            "pit_area_m2": inp.get("pit_area_m2"),
            "consumables_amount": inp.get("consumables_amount"),
            "manual_excavation_total_m3": vr.get("manual_excavation_total_m3"),
            "excavator_shifts": vr.get("excavator_shifts"),
        }

    excel_validation = "unknown"
    full_report_path = out_dir / "full_review_flow_report.json"
    if full_report_path.exists():
        full_report = json.loads(full_report_path.read_text(encoding="utf-8"))
        val_status = full_report.get("excel_validation_status", "")
        if val_status == "ok":
            excel_validation = "PASS"
        elif val_status == "failed":
            excel_validation = "FAIL"
        else:
            excel_validation = val_status or "unknown"

    state["last_build"] = {
        "status": "passed",
        "started_at": started_at,
        "built_at": now,
        "out_dir": out_dir_rel,
        "downloaded_review_workbook": "downloaded_review_workbook.xlsx",
        "final_excel": excel_filename,
        "excel_validation": excel_validation,
        "full_flow_report": "full_review_flow_report.json",
        "excel_validation_report": "excel_validation_report.md",
        "totals": totals,
        "key_values": key_values,
    }
    save_job_state(stage1_job_dir, state)
    return state
