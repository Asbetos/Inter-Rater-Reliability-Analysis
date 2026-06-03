"""Per-volume manual overrides for the v2 dataset build.

Two override types:

1. MANUAL_ASSIGNMENTS — replaces the Assignment-sheet-parsed coder→orders
   mapping with an operator-supplied one. Used when the Assignment sheet's
   parsed output is known to be wrong or incomplete.

2. COMPOSITE_SHEET_OVERRIDES — splices qN.agree values from a SECONDARY
   agreement sheet into the chosen (primary) sheet's data, but only for rows
   assigned to specific coders. Used when one subset of coders' cross-check
   was completed on a different date than the rest.
"""
from __future__ import annotations

from typing import Dict, Set


# {volume_label -> {coder_name -> set of order.num}}
# Use to fully replace what `assignment_sheet.parse()` returned.
MANUAL_ASSIGNMENTS: Dict[str, Dict[str, Set[int]]] = {
    "Volume 133": {
        "Alia":    set(range(1, 201)) | {236} | set(range(300, 601)),
        "Rachel":  set(range(1, 300)) | set(range(401, 601)),
        "Bridget": set(range(200, 601)),
    },
}


# {volume_label -> dict with:
#       "alternate_sheet": name of a second agreement sheet to splice in
#       "use_alternate_when_any_coder_in": frozenset of coder names; if any
#                                         of these are assigned to a row,
#                                         use alternate sheet's qN.agree
#                                         for that row instead of the primary
# }
COMPOSITE_SHEET_OVERRIDES: Dict[str, Dict] = {
    "Volume 114": {
        "alternate_sheet": "agreement 324",
        "use_alternate_when_any_coder_in": frozenset({"Brian", "Rachel"}),
    },
}


def manual_assignment_for(volume_label: str):
    """Return the manual assignment dict for this volume, or None."""
    return MANUAL_ASSIGNMENTS.get(volume_label)


def composite_sheet_for(volume_label: str):
    """Return the composite-sheet config dict for this volume, or None."""
    return COMPOSITE_SHEET_OVERRIDES.get(volume_label)
