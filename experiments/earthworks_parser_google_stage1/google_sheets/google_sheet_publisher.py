from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from config import EXPERIMENT_DIR


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
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:
        return {
            "status": "skipped",
            "reason": f"Google libraries are not installed: {exc}",
            "workbook": str(workbook_path),
            "sharing": {"mode": sharing, "type": None, "role": None, "status": "skipped"},
        }

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
    ]
    credentials_path = os.getenv("GOOGLE_OAUTH_CREDENTIALS_PATH", "credentials.json")
    token_path = os.getenv("GOOGLE_TOKEN_PATH", "token.json")
    creds = None
    if Path(token_path).exists():
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            creds = flow.run_local_server(port=0)
        Path(token_path).write_text(creds.to_json(), encoding="utf-8")

    drive = build("drive", "v3", credentials=creds)
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
