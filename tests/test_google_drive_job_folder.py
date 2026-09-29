from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "earthworks_parser_google_stage1"
    / "google_sheets"
    / "google_sheet_publisher.py"
)
sys.path.insert(0, str(MODULE_PATH.parents[1]))
SPEC = importlib.util.spec_from_file_location("google_sheet_publisher", MODULE_PATH)
assert SPEC and SPEC.loader
google_sheet_publisher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(google_sheet_publisher)


class _Request:
    def __init__(self, response: dict[str, str]) -> None:
        self.response = response

    def execute(self) -> dict[str, str]:
        return self.response


class _Files:
    def __init__(self) -> None:
        self.body = None
        self.fields = None

    def create(self, *, body, fields):
        self.body = body
        self.fields = fields
        return _Request({"id": "folder-123", "webViewLink": "https://drive.test/folder-123"})


class _Drive:
    def __init__(self) -> None:
        self.files_resource = _Files()

    def files(self) -> _Files:
        return self.files_resource


def test_create_project_folder_under_configured_root() -> None:
    drive = _Drive()

    result = google_sheet_publisher._create_drive_folder(
        drive,
        "ТРЦ — 29.09.2026",
        "root-folder",
    )

    assert drive.files_resource.body == {
        "name": "ТРЦ — 29.09.2026",
        "mimeType": "application/vnd.google-apps.folder",
        "parents": ["root-folder"],
    }
    assert result == {
        "id": "folder-123",
        "name": "ТРЦ — 29.09.2026",
        "url": "https://drive.test/folder-123",
    }
