from __future__ import annotations

import os
import time
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

SPREADSHEET_LOCALE = "ru_RU"
SPREADSHEET_TIME_ZONE = "Europe/Moscow"
SPREADSHEET_PROPERTY_RETRY_DELAYS = (0.0, 0.5, 1.0, 2.0)


def _get_google_credentials() -> Any:
    """Loads or refreshes the shared OAuth credentials for Drive and Sheets."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow

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

    return creds


def _get_drive_service() -> Any:
    """Builds the Drive client shared by publication and download."""
    from googleapiclient.discovery import build

    return build("drive", "v3", credentials=_get_google_credentials())


def _get_sheets_service() -> Any:
    """Builds a Sheets client with the same OAuth configuration as the Drive client."""
    from googleapiclient.discovery import build

    return build("sheets", "v4", credentials=_get_google_credentials())


def _configure_spreadsheet_properties(
    sheets: Any,
    spreadsheet_id: str,
    retry_delays: tuple[float, ...] = SPREADSHEET_PROPERTY_RETRY_DELAYS,
) -> dict[str, Any]:
    """Sets and verifies locale immediately after Drive converts the uploaded XLSX.

    A newly converted spreadsheet may briefly return a not-found/transient API error, so the
    operation is retried. Publication is not considered successful until the values are read
    back: otherwise decimal commas such as ``27,2125`` are parsed by Google as ``272125``.
    """
    request_body = {
        "requests": [
            {
                "updateSpreadsheetProperties": {
                    "properties": {
                        "locale": SPREADSHEET_LOCALE,
                        "timeZone": SPREADSHEET_TIME_ZONE,
                    },
                    "fields": "locale,timeZone",
                }
            }
        ]
    }
    last_error = "Google Sheets did not confirm spreadsheet properties."

    for attempt, delay in enumerate(retry_delays, start=1):
        if delay:
            time.sleep(delay)
        try:
            resource = sheets.spreadsheets()
            resource.batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body,
            ).execute()
            metadata = resource.get(
                spreadsheetId=spreadsheet_id,
                fields="properties(locale,timeZone)",
            ).execute()
            properties = metadata.get("properties", {})
            locale = properties.get("locale")
            time_zone = properties.get("timeZone")
            if locale == SPREADSHEET_LOCALE and time_zone == SPREADSHEET_TIME_ZONE:
                return {
                    "status": "configured",
                    "locale": locale,
                    "time_zone": time_zone,
                    "attempts": attempt,
                }
            last_error = (
                "Google Sheets returned unexpected properties: "
                f"locale={locale!r}, timeZone={time_zone!r}."
            )
        except Exception as exc:  # noqa: BLE001 - retry and return a safe diagnostic result
            last_error = str(exc)

    return {
        "status": "failed",
        "locale": None,
        "time_zone": None,
        "attempts": len(retry_delays),
        "error": last_error,
    }


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


def _create_drive_folder(drive: Any, folder_name: str, parent_folder_id: str = "") -> dict[str, str]:
    metadata: dict[str, Any] = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_folder_id:
        metadata["parents"] = [parent_folder_id]
    created = drive.files().create(body=metadata, fields="id, webViewLink").execute()
    folder_id = created["id"]
    return {
        "id": folder_id,
        "name": folder_name,
        "url": created.get("webViewLink", f"https://drive.google.com/drive/folders/{folder_id}"),
    }


def publish_workbook_if_configured(
    workbook_path: Path,
    title: str,
    sharing: str = "owner_only",
    folder_id: str = "",
    folder_name: str = "",
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
        sheets = _get_sheets_service()
    except ImportError as exc:
        return {
            "status": "skipped",
            "reason": f"Google libraries are not installed: {exc}",
            "workbook": str(workbook_path),
            "sharing": {"mode": sharing, "type": None, "role": None, "status": "skipped"},
        }

    root_folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip()
    project_folder: dict[str, str] | None = None
    target_folder_id = folder_id.strip()
    if not target_folder_id and folder_name.strip():
        project_folder = _create_drive_folder(drive, folder_name.strip(), root_folder_id)
        target_folder_id = project_folder["id"]

    metadata: dict[str, Any] = {
        "name": title,
        "mimeType": "application/vnd.google-apps.spreadsheet",
    }
    if target_folder_id:
        metadata["parents"] = [target_folder_id]
    elif root_folder_id:
        metadata["parents"] = [root_folder_id]
    media = MediaFileUpload(
        str(workbook_path),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        resumable=False,
    )
    created = drive.files().create(body=metadata, media_body=media, fields="id, webViewLink").execute()
    spreadsheet_id = created["id"]
    spreadsheet_url = created.get(
        "webViewLink",
        f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
    )

    spreadsheet_properties = _configure_spreadsheet_properties(sheets, spreadsheet_id)
    if spreadsheet_properties.get("status") != "configured":
        return {
            "status": "failed",
            "reason": "Google-таблица создана, но русская локаль не была подтверждена.",
            "spreadsheet_id": spreadsheet_id,
            "url": spreadsheet_url,
            "spreadsheet_properties": spreadsheet_properties,
            "sharing": {"mode": sharing, "type": None, "role": None, "status": "skipped"},
            "drive_folder_id": target_folder_id,
            "drive_folder_name": (project_folder or {}).get("name", folder_name),
            "drive_folder_url": (project_folder or {}).get(
                "url",
                f"https://drive.google.com/drive/folders/{target_folder_id}" if target_folder_id else "",
            ),
        }

    sharing_info = _apply_sharing(drive, spreadsheet_id, sharing)

    return {
        "status": "published",
        "spreadsheet_id": spreadsheet_id,
        "url": spreadsheet_url,
        "spreadsheet_properties": spreadsheet_properties,
        "sharing": sharing_info,
        "drive_folder_id": target_folder_id,
        "drive_folder_name": (project_folder or {}).get("name", folder_name),
        "drive_folder_url": (project_folder or {}).get(
            "url",
            f"https://drive.google.com/drive/folders/{target_folder_id}" if target_folder_id else "",
        ),
    }
