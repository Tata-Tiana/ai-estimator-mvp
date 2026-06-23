#!/usr/bin/env python3
"""
clean_test_jobs.py — очистить тестовые job-папки и Google Sheets перед новым тестом.

Usage:
  python clean_test_jobs.py --dry-run --all --clean-telegram-data --backup-first
  python clean_test_jobs.py --apply --all --clean-telegram-data --backup-first
  python clean_test_jobs.py --dry-run --project-prefix ЮСВ
  python clean_test_jobs.py --apply --project-prefix МКП1
"""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
BASE_DIR = Path(__file__).resolve().parent

STAGE1_DIR = REPO_ROOT / "experiments" / "earthworks_parser_google_stage1"
STAGE1_ENV = STAGE1_DIR / ".env"
JOBS_ROOT = STAGE1_DIR / "data" / "jobs"

OUTPUTS_ROOT = BASE_DIR / "outputs" / "jobs"

TELEGRAM_LOGS_DIR = BASE_DIR / "data" / "telegram_logs"
TELEGRAM_UPLOADS_DIR = BASE_DIR / "data" / "telegram_uploads"
TELEGRAM_SESSIONS_DIR = BASE_DIR / "data" / "telegram_sessions"

BACKUPS_DIR = BASE_DIR / "backups"


# ---------------------------------------------------------------------------
# Job scanning
# ---------------------------------------------------------------------------

def _load_job_state(job_dir: Path) -> dict[str, Any] | None:
    p = job_dir / "job_state.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _collect_spreadsheet_ids(state: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    gs = state.get("google_sheet", {})
    sid = gs.get("spreadsheet_id")
    if sid:
        ids.append(sid)
    for entry in state.get("google_sheet_history", []):
        sid = entry.get("spreadsheet_id")
        if sid and sid not in ids:
            ids.append(sid)
    return ids


def _scan_jobs(project_prefixes: list[str] | None) -> list[dict[str, Any]]:
    """Return list of job info dicts for jobs matching the given prefixes (or all)."""
    jobs: list[dict[str, Any]] = []
    if not JOBS_ROOT.exists():
        return jobs

    for job_dir in sorted(JOBS_ROOT.iterdir()):
        if not job_dir.is_dir():
            continue
        job_id = job_dir.name
        if project_prefixes:
            lo = job_id.lower()
            if not any(lo.startswith(p.lower()) for p in project_prefixes):
                continue

        state = _load_job_state(job_dir)
        if state is None:
            jobs.append({
                "job_id": job_id,
                "job_dir": job_dir,
                "status": "broken_no_job_state",
                "project_name": None,
                "spreadsheet_ids": [],
                "spreadsheet_url": None,
                "last_build": None,
                "source_pdfs_count": 0,
                "parser_active_run": None,
                "output_dir": None,
            })
            continue

        spreadsheet_ids = _collect_spreadsheet_ids(state)
        gs = state.get("google_sheet", {})

        # find output dir
        output_dir: Path | None = None
        candidate = OUTPUTS_ROOT / job_id
        if candidate.exists():
            output_dir = candidate

        jobs.append({
            "job_id": job_id,
            "job_dir": job_dir,
            "status": "ok",
            "project_name": state.get("project_name"),
            "spreadsheet_ids": spreadsheet_ids,
            "spreadsheet_url": gs.get("url"),
            "last_build": state.get("last_build", {}).get("status"),
            "source_pdfs_count": len(state.get("source", {}).get("input_pdfs", [])),
            "parser_active_run": state.get("parser", {}).get("active_run"),
            "output_dir": output_dir,
        })

    return jobs


# ---------------------------------------------------------------------------
# Google Drive — trash spreadsheet
# ---------------------------------------------------------------------------

def _build_drive_service():
    try:
        from dotenv import load_dotenv
        load_dotenv(STAGE1_ENV)
    except ImportError:
        pass

    token_path_raw = os.getenv("GOOGLE_TOKEN_PATH", "")
    if not token_path_raw:
        raise RuntimeError("GOOGLE_TOKEN_PATH not set in .env")
    token_path = Path(token_path_raw)
    if not token_path.is_absolute():
        token_path = REPO_ROOT / token_path
    if not token_path.exists():
        raise FileNotFoundError(f"token.json not found: {token_path}")

    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(f"Google libraries not installed: {exc}") from exc

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
    ]
    creds = Credentials.from_authorized_user_file(str(token_path), scopes)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("drive", "v3", credentials=creds)


def _trash_spreadsheet(drive, spreadsheet_id: str) -> tuple[bool, str]:
    """Move file to trash. Returns (success, error_message)."""
    try:
        drive.files().update(
            fileId=spreadsheet_id,
            body={"trashed": True},
        ).execute()
        return True, ""
    except Exception as exc:
        return False, str(exc)


# ---------------------------------------------------------------------------
# Backup
# ---------------------------------------------------------------------------

def _create_backup() -> Path:
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = BACKUPS_DIR / f"cleanup_{ts}.zip"

    dirs_to_backup = [
        JOBS_ROOT,
        TELEGRAM_UPLOADS_DIR,
        TELEGRAM_LOGS_DIR,
        TELEGRAM_SESSIONS_DIR,
    ]

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for base_dir in dirs_to_backup:
            if not base_dir.exists():
                continue
            for fpath in sorted(base_dir.rglob("*")):
                if fpath.is_dir():
                    continue
                # Skip PDFs to keep archive size manageable
                if fpath.suffix.lower() == ".pdf":
                    continue
                try:
                    arcname = fpath.relative_to(REPO_ROOT)
                    zf.write(fpath, arcname)
                except Exception:
                    pass

    return archive_path


# ---------------------------------------------------------------------------
# Dry-run report
# ---------------------------------------------------------------------------

def _print_dry_run(jobs: list[dict[str, Any]], clean_telegram: bool) -> None:
    broken = [j for j in jobs if j["status"] == "broken_no_job_state"]
    ok = [j for j in jobs if j["status"] == "ok"]
    all_sheet_ids: list[str] = []
    for j in jobs:
        for sid in j["spreadsheet_ids"]:
            if sid not in all_sheet_ids:
                all_sheet_ids.append(sid)

    output_dirs = [j["output_dir"] for j in jobs if j["output_dir"]]

    print()
    print("DRY RUN")
    print("=" * 60)
    print(f"Jobs found:                    {len(jobs)}")
    print(f"Jobs to delete:                {len(jobs)}")
    print(f"Google Sheets to trash:        {len(all_sheet_ids)}")
    print(f"Broken jobs without state:     {len(broken)}")
    print(f"Output dirs to delete:         {len(output_dirs)}")
    if clean_telegram:
        tg_uploads = _count_files(TELEGRAM_UPLOADS_DIR)
        tg_sessions = _count_files(TELEGRAM_SESSIONS_DIR)
        tg_logs = _count_files(TELEGRAM_LOGS_DIR)
        print(f"Telegram uploads to delete:    {tg_uploads} files")
        print(f"Telegram sessions to delete:   {tg_sessions} files")
        print(f"Telegram logs to delete:       {tg_logs} files")
    print()

    print("Jobs:")
    for j in jobs:
        state_label = j["status"]
        pn = j["project_name"] or "?"
        lb = j["last_build"] or "—"
        sheet_count = len(j["spreadsheet_ids"])
        print(f"  {j['job_id']}")
        print(f"    project: {pn}  |  last_build: {lb}  |  sheets: {sheet_count}  |  state: {state_label}")
        if j["output_dir"]:
            print(f"    output_dir: {j['output_dir'].relative_to(REPO_ROOT)}")
    print()

    print("Google Sheets to trash:")
    for sid in all_sheet_ids:
        print(f"  https://docs.google.com/spreadsheets/d/{sid}/edit")
    print()


def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for f in path.rglob("*") if f.is_file())


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

def _apply(
    jobs: list[dict[str, Any]],
    clean_telegram: bool,
    backup_first: bool,
) -> None:
    backup_path: Path | None = None

    if backup_first:
        print("Creating backup...")
        backup_path = _create_backup()
        print(f"Backup: {backup_path}")
        size_mb = backup_path.stat().st_size / (1024 * 1024)
        print(f"  Size: {size_mb:.1f} MB")
        print()

    # --- Trash Google Sheets ---
    all_sheet_ids: list[str] = []
    sheet_id_to_url: dict[str, str] = {}
    for j in jobs:
        for sid in j["spreadsheet_ids"]:
            if sid not in all_sheet_ids:
                all_sheet_ids.append(sid)
                if j["spreadsheet_url"] and sid == j["spreadsheet_ids"][0]:
                    sheet_id_to_url[sid] = j["spreadsheet_url"]

    trashed_ok: list[str] = []
    trashed_fail: list[tuple[str, str]] = []
    drive_available = False

    if all_sheet_ids:
        print(f"Trashing {len(all_sheet_ids)} Google Sheets...")
        try:
            drive = _build_drive_service()
            drive_available = True
        except Exception as exc:
            print(f"  WARNING: Cannot connect to Google Drive API: {exc}")
            print("  Sheets will NOT be trashed automatically.")
            trashed_fail = [(sid, "no drive access") for sid in all_sheet_ids]

        if drive_available:
            for sid in all_sheet_ids:
                ok, err = _trash_spreadsheet(drive, sid)
                if ok:
                    trashed_ok.append(sid)
                    print(f"  trashed: {sid}")
                else:
                    trashed_fail.append((sid, err))
                    print(f"  FAILED:  {sid} — {err}")
        print()

    # --- Delete output dirs first (inside job-related outputs) ---
    deleted_outputs = 0
    for j in jobs:
        if j["output_dir"] and j["output_dir"].exists():
            shutil.rmtree(j["output_dir"])
            deleted_outputs += 1

    # --- Delete job dirs ---
    deleted_jobs = 0
    for j in jobs:
        job_dir: Path = j["job_dir"]
        if job_dir.exists():
            shutil.rmtree(job_dir)
            deleted_jobs += 1

    # --- Clean telegram data ---
    cleaned_uploads = False
    cleaned_sessions = False
    cleaned_logs = False
    if clean_telegram:
        for tg_dir, label in [
            (TELEGRAM_UPLOADS_DIR, "uploads"),
            (TELEGRAM_SESSIONS_DIR, "sessions"),
            (TELEGRAM_LOGS_DIR, "logs"),
        ]:
            if tg_dir.exists():
                shutil.rmtree(tg_dir)
                tg_dir.mkdir(parents=True, exist_ok=True)
                if label == "uploads":
                    cleaned_uploads = True
                elif label == "sessions":
                    cleaned_sessions = True
                elif label == "logs":
                    cleaned_logs = True

    # --- Report ---
    print()
    print("Cleanup completed")
    print("=" * 60)
    if backup_path:
        print(f"Backup:                   {backup_path}")
    print(f"Deleted local jobs:       {deleted_jobs}")
    print(f"Deleted output dirs:      {deleted_outputs}")
    print(f"Trashed Google Sheets:    {len(trashed_ok)}")
    print(f"Failed to trash:          {len(trashed_fail)}")
    if clean_telegram:
        print(f"Cleaned telegram uploads: {'yes' if cleaned_uploads else 'no (not found)'}")
        print(f"Cleaned telegram sessions:{'yes' if cleaned_sessions else 'no (not found)'}")
        print(f"Cleaned telegram logs:    {'yes' if cleaned_logs else 'no (not found)'}")

    if trashed_fail:
        print()
        print("Manual cleanup required (spreadsheets NOT trashed):")
        for sid, err in trashed_fail:
            url = sheet_id_to_url.get(sid, f"https://docs.google.com/spreadsheets/d/{sid}/edit")
            print(f"  {sid}  {url}")
            print(f"    reason: {err}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean test jobs and Google Sheets before a new Telegram test run."
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Show what would be deleted, without doing anything.")
    mode.add_argument("--apply", action="store_true", help="Actually delete jobs and trash Google Sheets.")

    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--all", action="store_true", help="Clean all jobs.")
    scope.add_argument(
        "--project-prefix",
        action="append",
        dest="project_prefixes",
        metavar="PREFIX",
        help="Clean only jobs whose job_id starts with this prefix (e.g. юсв, мкп1). Repeatable.",
    )

    parser.add_argument("--clean-telegram-data", action="store_true", help="Also clean telegram_uploads/ and telegram_sessions/.")
    parser.add_argument("--backup-first", action="store_true", help="Create a zip backup before deleting anything.")

    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if not args.all and not args.project_prefixes:
        print("ERROR: Refusing to clean without --all or --project-prefix.", file=sys.stderr)
        print("  Use --all to clean everything, or --project-prefix <PREFIX> to target specific projects.", file=sys.stderr)
        sys.exit(1)

    project_prefixes = args.project_prefixes if not args.all else None

    jobs = _scan_jobs(project_prefixes)

    if not jobs:
        print("No jobs found matching the given criteria.")
        sys.exit(0)

    if args.dry_run:
        _print_dry_run(jobs, args.clean_telegram_data)
        print("(dry-run — nothing deleted)")
    else:
        _apply(jobs, args.clean_telegram_data, args.backup_first)


if __name__ == "__main__":
    main()
