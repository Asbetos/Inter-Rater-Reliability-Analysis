"""Pick the earliest agreement sheet, resolving date ambiguity against Drive mtime."""
from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional

import parse_agreement_sheet


def pick(
    sheet_names: List[str],
    drive_mtime: datetime,
    overrides: Dict[str, str],
    volume_id: str,
) -> Dict:
    if volume_id in overrides:
        chosen = overrides[volume_id]
        cands = parse_agreement_sheet.candidate_dates(chosen)
        chosen_date = (
            _earliest_date(cands, drive_mtime)
            if cands
            else date(drive_mtime.year, 1, 1)
        )
        return {
            "chosen_sheet": chosen,
            "chosen_date": chosen_date,
            "manual_review": False,
            "manual_review_reason": "",
        }

    if not sheet_names:
        return {
            "chosen_sheet": None,
            "chosen_date": None,
            "manual_review": True,
            "manual_review_reason": "no_agreement_sheets",
        }

    # For each sheet, determine its chosen date (filtered by drive_mtime)
    sheet_to_date: Dict[str, date] = {}
    for sn in sheet_names:
        cands = parse_agreement_sheet.candidate_dates(sn)
        valid = [
            date(drive_mtime.year, m, d)
            for (m, d) in cands
            if date(drive_mtime.year, m, d) <= drive_mtime.date()
        ]
        if not valid:
            # try previous year (sheet generated in prior year)
            valid = [date(drive_mtime.year - 1, m, d) for (m, d) in cands]
        if len(valid) > 1:
            # within a single sheet, pick the closest-to-but-not-after mtime
            valid_sorted = sorted(valid)
            # closest = the latest one not exceeding mtime
            valid = [
                d for d in valid_sorted if d <= drive_mtime.date()
            ] or valid_sorted
            valid = [valid[-1]]
        if valid:
            sheet_to_date[sn] = valid[0]

    if not sheet_to_date:
        return {
            "chosen_sheet": None,
            "chosen_date": None,
            "manual_review": True,
            "manual_review_reason": "no_valid_dates",
        }

    best_sheet = min(sheet_to_date, key=lambda s: (sheet_to_date[s], s))

    # Detect raw ambiguity for the single-sheet case
    raw_cands = parse_agreement_sheet.candidate_dates(best_sheet)
    raw_valid_count = sum(
        1 for (m, d) in raw_cands
        if date(drive_mtime.year, m, d) <= drive_mtime.date()
    )
    if raw_valid_count > 1:
        return {
            "chosen_sheet": best_sheet,
            "chosen_date": sheet_to_date[best_sheet],
            "manual_review": True,
            "manual_review_reason": f"ambiguous_date_for_{best_sheet}",
        }

    return {
        "chosen_sheet": best_sheet,
        "chosen_date": sheet_to_date[best_sheet],
        "manual_review": False,
        "manual_review_reason": "",
    }


def _earliest_date(cands, drive_mtime: datetime) -> date:
    valid = [
        date(drive_mtime.year, m, d)
        for (m, d) in cands
        if date(drive_mtime.year, m, d) <= drive_mtime.date()
    ]
    return min(valid) if valid else date(drive_mtime.year, cands[0][0], cands[0][1])
