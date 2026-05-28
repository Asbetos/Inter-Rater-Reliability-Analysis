"""Compute number_coded_prior per (volume, coder) from agreement-sheet dates."""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Tuple

Participation = Tuple[str, str, date]  # (volume_id, coder, agreement_sheet_date)


def compute(participations: List[Participation]) -> Dict[Tuple[str, str], int]:
    """For each (volume, coder), return how many earlier volumes the coder participated in.

    Ordering: by `agreement_sheet_date` ascending, with ties broken by
    lexicographic `volume_id` ascending.
    """
    # Group by coder
    by_coder: Dict[str, List[Tuple[str, date]]] = {}
    for vol, coder, d in participations:
        by_coder.setdefault(coder, []).append((vol, d))

    result: Dict[Tuple[str, str], int] = {}
    for coder, entries in by_coder.items():
        # Sort by (date, volume_id) ascending
        ordered = sorted(entries, key=lambda x: (x[1], x[0]))
        for idx, (vol, _) in enumerate(ordered):
            result[(vol, coder)] = idx
    return result
