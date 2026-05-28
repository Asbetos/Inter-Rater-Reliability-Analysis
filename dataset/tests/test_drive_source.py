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
