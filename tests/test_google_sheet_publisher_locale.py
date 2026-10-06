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
SPEC = importlib.util.spec_from_file_location("google_sheet_publisher_locale", MODULE_PATH)
assert SPEC and SPEC.loader
google_sheet_publisher = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(google_sheet_publisher)


class _Request:
    def __init__(self, response=None, error: Exception | None = None) -> None:
        self.response = response or {}
        self.error = error

    def execute(self):
        if self.error:
            raise self.error
        return self.response


class _SpreadsheetResource:
    def __init__(self, *, failures: int = 0, locale: str = "ru_RU", time_zone: str = "Europe/Moscow") -> None:
        self.failures = failures
        self.locale = locale
        self.time_zone = time_zone
        self.batch_calls: list[dict] = []
        self.get_calls: list[dict] = []

    def batchUpdate(self, *, spreadsheetId, body):
        self.batch_calls.append({"spreadsheetId": spreadsheetId, "body": body})
        if len(self.batch_calls) <= self.failures:
            return _Request(error=RuntimeError("spreadsheet conversion is not ready"))
        return _Request()

    def get(self, *, spreadsheetId, fields):
        self.get_calls.append({"spreadsheetId": spreadsheetId, "fields": fields})
        return _Request(
            {
                "properties": {
                    "locale": self.locale,
                    "timeZone": self.time_zone,
                }
            }
        )


class _Sheets:
    def __init__(self, resource: _SpreadsheetResource) -> None:
        self.resource = resource

    def spreadsheets(self) -> _SpreadsheetResource:
        return self.resource


def test_configure_spreadsheet_properties_sets_and_verifies_russian_locale() -> None:
    resource = _SpreadsheetResource()

    result = google_sheet_publisher._configure_spreadsheet_properties(
        _Sheets(resource),
        "sheet-123",
        retry_delays=(0.0,),
    )

    assert result == {
        "status": "configured",
        "locale": "ru_RU",
        "time_zone": "Europe/Moscow",
        "attempts": 1,
    }
    assert resource.batch_calls == [
        {
            "spreadsheetId": "sheet-123",
            "body": {
                "requests": [
                    {
                        "updateSpreadsheetProperties": {
                            "properties": {
                                "locale": "ru_RU",
                                "timeZone": "Europe/Moscow",
                            },
                            "fields": "locale,timeZone",
                        }
                    }
                ]
            },
        }
    ]
    assert resource.get_calls == [
        {
            "spreadsheetId": "sheet-123",
            "fields": "properties(locale,timeZone)",
        }
    ]


def test_configure_spreadsheet_properties_retries_transient_conversion_error() -> None:
    resource = _SpreadsheetResource(failures=1)

    result = google_sheet_publisher._configure_spreadsheet_properties(
        _Sheets(resource),
        "sheet-123",
        retry_delays=(0.0, 0.0),
    )

    assert result["status"] == "configured"
    assert result["attempts"] == 2
    assert len(resource.batch_calls) == 2
    assert len(resource.get_calls) == 1


def test_configure_spreadsheet_properties_fails_on_unconfirmed_locale() -> None:
    resource = _SpreadsheetResource(locale="en_US", time_zone="America/Los_Angeles")

    result = google_sheet_publisher._configure_spreadsheet_properties(
        _Sheets(resource),
        "sheet-123",
        retry_delays=(0.0, 0.0),
    )

    assert result["status"] == "failed"
    assert result["attempts"] == 2
    assert "unexpected properties" in result["error"]


class _DriveFiles:
    def create(self, *, body, media_body, fields):
        return _Request(
            {
                "id": "sheet-123",
                "webViewLink": "https://docs.google.test/sheet-123",
            }
        )


class _DrivePermissions:
    def __init__(self) -> None:
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        return _Request({"id": "permission-123"})


class _Drive:
    def __init__(self) -> None:
        self.files_resource = _DriveFiles()
        self.permissions_resource = _DrivePermissions()

    def files(self) -> _DriveFiles:
        return self.files_resource

    def permissions(self) -> _DrivePermissions:
        return self.permissions_resource


def test_publish_does_not_report_success_when_locale_configuration_fails(
    monkeypatch,
    tmp_path: Path,
) -> None:
    import googleapiclient.http

    drive = _Drive()
    workbook = tmp_path / "review.xlsx"
    workbook.write_bytes(b"xlsx-placeholder")
    monkeypatch.setenv("GOOGLE_OAUTH_CREDENTIALS_PATH", "credentials.json")
    monkeypatch.setenv("GOOGLE_TOKEN_PATH", "token.json")
    monkeypatch.delenv("GOOGLE_DRIVE_FOLDER_ID", raising=False)
    monkeypatch.setattr(google_sheet_publisher, "_get_drive_service", lambda: drive)
    monkeypatch.setattr(google_sheet_publisher, "_get_sheets_service", lambda: object())
    monkeypatch.setattr(
        google_sheet_publisher,
        "_configure_spreadsheet_properties",
        lambda sheets, spreadsheet_id: {
            "status": "failed",
            "attempts": 4,
            "error": "locale was not confirmed",
        },
    )
    monkeypatch.setattr(googleapiclient.http, "MediaFileUpload", lambda *args, **kwargs: object())

    result = google_sheet_publisher.publish_workbook_if_configured(
        workbook,
        "Проверка локали",
        sharing="anyone_writer",
    )

    assert result["status"] == "failed"
    assert result["spreadsheet_id"] == "sheet-123"
    assert result["spreadsheet_properties"]["status"] == "failed"
    assert result["sharing"]["status"] == "skipped"
    assert drive.permissions_resource.calls == 0
