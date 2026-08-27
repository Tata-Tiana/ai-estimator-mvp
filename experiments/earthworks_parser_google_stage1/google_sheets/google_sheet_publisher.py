from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from config import EXPERIMENT_DIR, REPO_ROOT


def _resolve_env_path(raw: str) -> Path:
    """Absolute paths pass through untouched; relative ones are anchored to REPO_ROOT (where
    .env values for this module are written from), never to the calling process's cwd."""
    path = Path(raw)
    return path if path.is_absolute() else (REPO_ROOT / path)


_SHARING_PERMISSIONS: dict[str, dict[str, str]] = {
    "anyone_reader": {"type": "anyone", "role": "reader"},
    "anyone_writer": {"type": "anyone", "role": "writer"},
}


def _apply_sharing(drive: Any, file_id: str, sharing: str) -> dict[str, Any]:
    if sharing == "owner_only" or sharing not in _SHARING_PERMISSIONS:
        return {"mode": "owner_only", "type": None, "role": None, "status": "skipped"}
    permission = _SHARING_PERMISSIONS[sharing]
    try:
        drive.permissions().create(
            fileId=file_id,
            body=permission,
            fields="id",
        ).execute()
        return {
            "mode": sharing,
            "type": permission["type"],
            "role": permission["role"],
            "status": "applied",
        }
    except Exception as exc:
        return {
            "mode": sharing,
            "type": permission["type"],
            "role": permission["role"],
            "status": "failed",
            "error": str(exc),
        }


_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


def _get_drive_service() -> Any:
    """Shared OAuth + Drive client bootstrap for publish and download - was duplicated inline in
    publish_workbook_if_configured until the download path needed the exact same setup (2026-08-26).
    Raises ImportError if the google-* libraries aren't installed; caller decides how to report that."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    # 2026-08-25: these env values are written relative to REPO_ROOT (see .env), but this
    # function used to pass them straight to Path(...) - which silently resolves against
    # whatever the CALLING PROCESS's cwd happens to be, not REPO_ROOT. Any caller running
    # from a different cwd (a one-off script, a differently-configured service) couldn't find
    # the already-existing token, looked expired, and launched a real interactive OAuth
    # browser flow instead - happened 3 times in a row while wiring this into the bot. Anchor
    # explicitly to REPO_ROOT so this only ever depends on the .env value, never on cwd.
    credentials_path = _resolve_env_path(os.getenv("GOOGLE_OAUTH_CREDENTIALS_PATH", "credentials.json"))
    token_path = _resolve_env_path(os.getenv("GOOGLE_TOKEN_PATH", "token.json"))
    creds = None
    if Path(token_path).exists():
        creds = Credentials.from_authorized_user_file(token_path, _SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, _SCOPES)
            creds = flow.run_local_server(port=0)
        Path(token_path).write_text(creds.to_json(), encoding="utf-8")

    return build("drive", "v3", credentials=creds)


def extract_spreadsheet_id(spreadsheet_id_or_url: str) -> str:
    """Accepts either a bare spreadsheet_id or a full Google Sheets URL (what the bot actually
    has stored per job - see telegram_bot.py's _register_user_job) and returns the bare id."""
    value = spreadsheet_id_or_url.strip()
    if "/spreadsheets/d/" in value:
        return value.split("/spreadsheets/d/", 1)[1].split("/", 1)[0]
    return value


def download_spreadsheet_as_xlsx(spreadsheet_id_or_url: str, output_path: Path) -> dict[str, Any]:
    """Downloads a Google Sheet this app published (drive.file scope only sees files the app
    itself created/opened) as .xlsx - the reverse of publish_workbook_if_configured, needed so
    /build can pick up Elena's/the user's edits made directly in the Sheet rather than the stale
    local snapshot from before publishing (2026-08-26: no such path existed anywhere in the
    pipeline before this - /build was still calling the old single-section PDF-flow build script)."""
    load_dotenv(EXPERIMENT_DIR / ".env")
    if not os.getenv("GOOGLE_OAUTH_CREDENTIALS_PATH") or not os.getenv("GOOGLE_TOKEN_PATH"):
        return {"status": "skipped", "reason": "Google OAuth paths are not configured"}
    try:
        drive = _get_drive_service()
    except ImportError as exc:
        return {"status": "skipped", "reason": f"Google libraries are not installed: {exc}"}

    spreadsheet_id = extract_spreadsheet_id(spreadsheet_id_or_url)
    try:
        data = drive.files().export_media(
            fileId=spreadsheet_id,
            mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ).execute()
    except Exception as exc:  # noqa: BLE001 - report any Drive API failure to the caller, don't crash
        return {"status": "failed", "reason": str(exc)}

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data)
    return {"status": "downloaded", "path": str(output_path)}


def publish_workbook_if_configured(
    workbook_path: Path,
    title: str,
    sharing: str = "owner_only",
) -> dict[str, Any]:
    load_dotenv(EXPERIMENT_DIR / ".env")
    if not os.getenv("GOOGLE_OAUTH_CREDENTIALS_PATH") or not os.getenv("GOOGLE_TOKEN_PATH"):
        return {
            "status": "skipped",
            "reason": "Google OAuth paths are not configured",
            "workbook": str(workbook_path),
            "sharing": {"mode": sharing, "type": None, "role": None, "status": "skipped"},
        }
    try:
        from googleapiclient.http import MediaFileUpload

        drive = _get_drive_service()
    except ImportError as exc:
        return {
            "status": "skipped",
            "reason": f"Google libraries are not installed: {exc}",
            "workbook": str(workbook_path),
            "sharing": {"mode": sharing, "type": None, "role": None, "status": "skipped"},
        }

    metadata: dict[str, Any] = {
        "name": title,
        "mimeType": "application/vnd.google-apps.spreadsheet",
    }
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip()
    if folder_id:
        metadata["parents"] = [folder_id]
    media = MediaFileUpload(
        str(workbook_path),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        resumable=False,
    )
    created = drive.files().create(body=metadata, media_body=media, fields="id, webViewLink").execute()
    spreadsheet_id = created["id"]

    sharing_info = _apply_sharing(drive, spreadsheet_id, sharing)

    return {
        "status": "published",
        "spreadsheet_id": spreadsheet_id,
        "url": created.get("webViewLink", f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"),
        "sharing": sharing_info,
    }
