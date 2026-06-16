from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from config import EXPERIMENT_DIR


def publish_workbook_if_configured(workbook_path: Path, title: str) -> dict[str, str]:
    load_dotenv(EXPERIMENT_DIR / ".env")
    if not os.getenv("GOOGLE_OAUTH_CREDENTIALS_PATH") or not os.getenv("GOOGLE_TOKEN_PATH"):
        return {"status": "skipped", "reason": "Google OAuth paths are not configured", "workbook": str(workbook_path)}
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:
        return {"status": "skipped", "reason": f"Google libraries are not installed: {exc}", "workbook": str(workbook_path)}

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
    metadata = {
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
    return {
        "status": "published",
        "spreadsheet_id": created["id"],
        "url": created.get("webViewLink", f"https://docs.google.com/spreadsheets/d/{created['id']}/edit"),
    }
