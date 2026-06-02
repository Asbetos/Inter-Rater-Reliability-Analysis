"""Authoritative volume ordering for the v2 dataset build.

The team uses inconsistent date encodings in agreement-sheet names, so the
parse_agreement_sheet.candidate_dates() heuristic can't reliably recover
the real coding-completion date. This module hardcodes the canonical
(volume_label -> date) mapping based on the team's records.

For any whitelisted volume, the orchestrator should prefer AUTHORITATIVE_DATES
over the heuristic.
"""
from __future__ import annotations

from datetime import date
from typing import Dict, Optional


# Volume labels are the canonical labels emitted by volume_whitelist.match_volume().
# Dates are the date of the FIRST agreement (per the team's records, 2026-05-28).
AUTHORITATIVE_DATES: Dict[str, date] = {
    "Volume 134 - Part 2": date(2025, 4, 10),
    "Volume 133":          date(2025, 9, 22),
    "Volume 61":           date(2025, 10, 4),
    "Volume 134 - Part I": date(2025, 10, 9),
    "Volume 62":           date(2025, 11, 5),
    "Volume 132":          date(2025, 11, 13),
    "Volume 131":          date(2025, 11, 21),
    "Volume 130":          date(2026, 1, 1),
    "Volume 120":          date(2026, 1, 15),
    "Volume 122":          date(2026, 1, 15),
    "Volume 127":          date(2026, 2, 4),
    "Volume 126":          date(2026, 2, 17),
    "Volume 124":          date(2026, 2, 24),
    "Volume 109":          date(2026, 3, 3),
    "Volume 114":          date(2026, 3, 10),
    "Volume 119":          date(2026, 3, 24),
    "Volume 93":           date(2026, 3, 30),
    "Volume 91":           date(2026, 4, 5),
    "Volume 94":           date(2026, 4, 12),
    "Volume 95":           date(2026, 4, 21),
}


def authoritative_date_for(volume_label: str) -> Optional[date]:
    """Return the canonical agreement-sheet date for this volume, or None
    if the label is not in the hardcoded table (heuristic fallback in caller).
    """
    return AUTHORITATIVE_DATES.get(volume_label)
