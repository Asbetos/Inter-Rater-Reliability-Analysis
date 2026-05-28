"""Abstract DriveSource interface + LocalDriveSource (for tests)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Protocol, Union

import openpyxl


@dataclass(frozen=True)
class WorkbookHandle:
    """Opaque identifier for a workbook on the source.

    For LocalDriveSource, `id` is the absolute file path as a string.
    For OAuthDriveSource, `id` is the Google Drive file ID and `mime_type`
    records whether it's a native Google Sheet or an uploaded xlsx, so
    OAuthDriveSource.open() can dispatch correctly.
    """
    id: str
    name: str
    mime_type: str = ""


class DriveSource(Protocol):
    def list_workbooks(self) -> List[WorkbookHandle]: ...
    def open(self, handle: WorkbookHandle) -> openpyxl.Workbook: ...
    def last_modified(self, handle: WorkbookHandle) -> datetime: ...


class LocalDriveSource:
    """Reads .xlsx files from a local directory. Used by tests and as a
    fallback when Drive auth is unavailable."""

    def __init__(self, root: Union[str, Path]):
        self.root = Path(root)

    def list_workbooks(self) -> List[WorkbookHandle]:
        return [
            WorkbookHandle(id=str(p.resolve()), name=p.name)
            for p in sorted(self.root.glob("*.xlsx"))
        ]

    def open(self, handle: WorkbookHandle) -> openpyxl.Workbook:
        return openpyxl.load_workbook(handle.id, read_only=True, data_only=True)

    def last_modified(self, handle: WorkbookHandle) -> datetime:
        return datetime.fromtimestamp(Path(handle.id).stat().st_mtime, tz=timezone.utc)
