"""Parse agreement sheet names into candidate (month, day) tuples.

The name encodes the date of cross-check generation, but the encoding is
ambiguous: 2 digits could be MD (3/3); 3 digits could be MDD (3/10) or
MMD (11/5); 4 digits are MMDD.

This module returns the *list* of plausible candidates; resolution
against the Drive last_modified timestamp happens in pick_agreement_sheet.py.
"""
from __future__ import annotations

import re
from typing import List, Tuple


_DIGIT_RUN = re.compile(r"\d+")


def _valid(month: int, day: int) -> bool:
    if not (1 <= month <= 12):
        return False
    if not (1 <= day <= 31):
        return False
    # Per-month day caps (ignoring leap years; we don't know the year)
    caps = {1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    return day <= caps[month]


def candidate_dates(sheet_name: str) -> List[Tuple[int, int]]:
    """Return ordered list of plausible (month, day) tuples for a sheet name."""
    m = _DIGIT_RUN.search(sheet_name)
    if not m:
        return []
    digits = m.group(0)
    n = len(digits)
    out = []
    if n == 1:
        # too short to be a date
        return []
    elif n == 2:
        # MD
        month, day = int(digits[0]), int(digits[1])
        if _valid(month, day):
            out.append((month, day))
    elif n == 3:
        # MDD (e.g., 310 = Mar 10)
        m1, d1 = int(digits[0]), int(digits[1:])
        if _valid(m1, d1):
            out.append((m1, d1))
        # MMD (e.g., 115 = Nov 5) -- only when middle digit is non-zero;
        # otherwise MDD's day already represents a single-digit day (e.g.,
        # "104" is Jan 4, not also Oct 4).
        if digits[1] != "0":
            m2, d2 = int(digits[:2]), int(digits[2])
            if _valid(m2, d2) and (m2, d2) not in out:
                out.append((m2, d2))
    elif n == 4:
        # MMDD
        month, day = int(digits[:2]), int(digits[2:])
        if _valid(month, day):
            out.append((month, day))
    return out
