"""Filter and list candidate workbooks from a DriveSource.

The DriveSource.list_workbooks() implementation is expected to have already
filtered by mimeType (Google Sheets + xlsx) -- this layer just handles
naming-based rejection of lock files, templates, drafts, and hidden files.
"""
from __future__ import annotations

from typing import List

from drive_source import DriveSource, WorkbookHandle


_EXCLUDE_PREFIXES = ("~$", ".", "_")
_EXCLUDE_KEYWORDS = ("TEMPLATE", "DRAFT", "BACKUP")


def list_eligible(src: DriveSource) -> List[WorkbookHandle]:
    """Return workbook handles for files that look like real coding workbooks."""
    handles = src.list_workbooks()
    out = []
    for h in handles:
        name = h.name
        if any(name.startswith(p) for p in _EXCLUDE_PREFIXES):
            continue
        upper = name.upper()
        if any(k in upper for k in _EXCLUDE_KEYWORDS):
            continue
        out.append(h)
    return out
