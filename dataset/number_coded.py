"""Compute number_coded_prior per (volume, coder) from agreement-sheet dates."""
from __future__ import annotations

from datetime import date
from typing import Dict, List, Tuple

Participation = Tuple[str, str, date]  # (volume_id, coder, agreement_sheet_date)


def compute(participations: List[Participation]) -> Dict[Tuple[str, str], int]:
    """For each (volume, coder), return the count of OTHER volumes the coder
    participated in whose agreement_sheet_date is STRICTLY earlier.

    Volumes tied on date receive the SAME number_coded_prior (competition
    ranking); the next non-tied volume skips ahead by the size of the tied
    group. This generalizes to any number of tied volumes.

    Examples:
        Three volumes V1, V2, V3 dated 2025-01-01, 2025-01-01, 2025-02-01:
          V1 -> 0, V2 -> 0, V3 -> 2  (V3 skips rank 1 because two volumes
          shared rank 0)
    """
    # Group by coder
    by_coder: Dict[str, List[Tuple[str, date]]] = {}
    for vol, coder, d in participations:
        by_coder.setdefault(coder, []).append((vol, d))

    result: Dict[Tuple[str, str], int] = {}
    for coder, entries in by_coder.items():
        for vol, d in entries:
            # Count volumes for this coder whose date is STRICTLY less than d.
            n_strictly_earlier = sum(1 for _, d2 in entries if d2 < d)
            result[(vol, coder)] = n_strictly_earlier
    return result
