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


# ---- OAuth Drive source (Google Drive API) ----

import io
from googleapiclient.http import MediaIoBaseDownload

MIMETYPE_GOOGLE_SHEET = "application/vnd.google-apps.spreadsheet"
MIMETYPE_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class OAuthDriveSource:
    """Google Drive API source. Auth handled separately in `auth.py`.

    Accepts an already-built googleapiclient Resource so tests can pass a mock.
    Production callers build the Resource via:
        creds = auth.get_credentials(credentials_path, token_path)
        from googleapiclient.discovery import build
        service = build("drive", "v3", credentials=creds)

    Handles both native Google Sheets (export-as-xlsx) and uploaded .xlsx
    files (direct download).
    """

    def __init__(self, folder_id: str, service):
        self.folder_id = folder_id
        self.service = service

    def list_workbooks(self) -> List[WorkbookHandle]:
        handles: List[WorkbookHandle] = []
        page_token = None
        mime_filter = (
            f"(mimeType='{MIMETYPE_GOOGLE_SHEET}' or "
            f"mimeType='{MIMETYPE_XLSX}')"
        )
        while True:
            query = (
                f"'{self.folder_id}' in parents and "
                f"{mime_filter} and trashed=false"
            )
            response = self.service.files().list(
                q=query,
                pageSize=1000,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
            ).execute()
            for f in response.get("files", []):
                handles.append(WorkbookHandle(
                    id=f["id"],
                    name=f["name"],
                    mime_type=f["mimeType"],
                ))
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        return handles

    def open(self, handle: WorkbookHandle) -> openpyxl.Workbook:
        if handle.mime_type == MIMETYPE_GOOGLE_SHEET:
            request = self.service.files().export_media(
                fileId=handle.id, mimeType=MIMETYPE_XLSX,
            )
        else:
            request = self.service.files().get_media(fileId=handle.id)
        buf = io.BytesIO()
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        buf.seek(0)
        return openpyxl.load_workbook(buf, read_only=True, data_only=True)

    def last_modified(self, handle: WorkbookHandle) -> datetime:
        f = self.service.files().get(
            fileId=handle.id, fields="modifiedTime",
        ).execute()
        ts = f["modifiedTime"]
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts).astimezone(timezone.utc)
