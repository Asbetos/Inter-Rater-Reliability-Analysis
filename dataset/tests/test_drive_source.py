from datetime import datetime
from conftest import MINI_DRIVE_DIR
import drive_source


def test_local_drive_source_lists_workbooks():
    src = drive_source.LocalDriveSource(MINI_DRIVE_DIR)
    handles = src.list_workbooks()
    names = sorted(h.name for h in handles)
    assert names == [
        "Volume-A_complete.xlsx",
        "Volume-B_two_agreements.xlsx",
        "Volume-C_incomplete.xlsx",
        "Volume-D_no_agreement.xlsx",
    ]


def test_local_drive_source_opens_workbook():
    src = drive_source.LocalDriveSource(MINI_DRIVE_DIR)
    handle = [h for h in src.list_workbooks() if h.name == "Volume-A_complete.xlsx"][0]
    wb = src.open(handle)
    assert "33 agreement" in wb.sheetnames
    assert "Leah" in wb.sheetnames


def test_local_drive_source_last_modified_is_datetime():
    src = drive_source.LocalDriveSource(MINI_DRIVE_DIR)
    handle = src.list_workbooks()[0]
    mtime = src.last_modified(handle)
    assert isinstance(mtime, datetime)


def test_workbook_handle_has_mime_type_field():
    """The dataclass must carry a mime_type field (default empty)
    so OAuthDriveSource (Task 3) can record native Google Sheets vs xlsx."""
    h = drive_source.WorkbookHandle(id="x", name="y")
    assert h.mime_type == ""  # default
    h2 = drive_source.WorkbookHandle(id="x", name="y", mime_type="some/mime")
    assert h2.mime_type == "some/mime"


from unittest.mock import MagicMock


def test_oauth_drive_source_lists_workbooks_with_mime_types():
    fake_service = MagicMock()
    fake_service.files().list().execute.side_effect = [
        {
            "files": [
                {"id": "abc", "name": "Volume-X", "mimeType": drive_source.MIMETYPE_GOOGLE_SHEET, "modifiedTime": "2025-10-04T12:00:00Z"},
                {"id": "def", "name": "Volume-Y.xlsx", "mimeType": drive_source.MIMETYPE_XLSX, "modifiedTime": "2025-10-05T12:00:00Z"},
            ],
            "nextPageToken": None,
        }
    ]
    src = drive_source.OAuthDriveSource(folder_id="folder-1", service=fake_service)
    handles = src.list_workbooks()
    assert sorted(h.name for h in handles) == ["Volume-X", "Volume-Y.xlsx"]
    by_name = {h.name: h.mime_type for h in handles}
    assert by_name["Volume-X"] == drive_source.MIMETYPE_GOOGLE_SHEET
    assert by_name["Volume-Y.xlsx"] == drive_source.MIMETYPE_XLSX


def test_oauth_drive_source_last_modified_parses_drive_timestamp():
    fake_service = MagicMock()
    fake_service.files().get().execute.return_value = {
        "id": "abc", "name": "Volume-X", "modifiedTime": "2025-10-04T12:00:00Z"
    }
    src = drive_source.OAuthDriveSource(folder_id="folder-1", service=fake_service)
    handle = drive_source.WorkbookHandle(id="abc", name="Volume-X", mime_type=drive_source.MIMETYPE_GOOGLE_SHEET)
    mtime = src.last_modified(handle)
    assert mtime.year == 2025
    assert mtime.month == 10
    assert mtime.day == 4
