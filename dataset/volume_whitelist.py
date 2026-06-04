"""Volume whitelist + hardcoded sheet overrides for the v2 dataset build.

Per user spec (2026-05-28): only 20 specific volumes contribute to the
v2 dataset. For 5 of those, the operator pre-specified which agreement
sheet to use; the rest fall back to auto-detection.
"""
from __future__ import annotations

from typing import Optional


# Most-specific-first so "Volume 134 - Part 2" matches before "Volume 134"
# would (defensively — "Volume 134" isn't in the list).
VOLUME_WHITELIST_SUBSTRINGS = [
    "Volume 134 - Part 2",
    "Volume 134 - Part I",
    "Volume 133",
    "Volume 132",
    "Volume 131",
    "Volume 130",
    "Volume 127",
    "Volume 126",
    "Volume 124",
    "Volume 122",
    "Volume 120",
    "Volume 119",
    "Volume 114",
    "Volume 109",
    "Volume 95",
    "Volume 94",
    "Volume 93",
    "Volume 91",
    "Volume 63",
    "Volume 62",
    "Volume 61",
]


HARDCODED_SHEET_OVERRIDES = {
    "Volume 61": "104 agreement",
    "Volume 62": "115 agreement",
    "Volume 63": "104 agreement",          # not in whitelist; pre-filled for future
    "Volume 134 - Part I": "109 agreement",
    "Volume 134 - Part 2": "104 agreement",
}


def match_volume(filename: str) -> Optional[str]:
    """Return the matching whitelist substring (canonical volume label),
    or None if the filename doesn't match any whitelisted volume."""
    for sub in VOLUME_WHITELIST_SUBSTRINGS:
        if sub in filename:
            return sub
    return None


def override_sheet_for(filename: str) -> Optional[str]:
    """Return the hardcoded agreement-sheet name for this volume, or None
    if the volume has no override.

    Most-specific keys checked first (handles 'Part 2' vs 'Part I')."""
    for key in sorted(HARDCODED_SHEET_OVERRIDES, key=len, reverse=True):
        if key in filename:
            return HARDCODED_SHEET_OVERRIDES[key]
    return None
