"""Per-workbook completeness check: agreement sheet present + per-coder fill threshold."""
from __future__ import annotations

from typing import Dict

import openpyxl


KNOWN_CODERS = ("Leah", "Bridget", "Rachel", "Alia", "Brian")


def _coder_fill_fraction(wb: openpyxl.Workbook, coder: str) -> float:
    if coder not in wb.sheetnames:
        return float("nan")
    ws = wb[coder]
    header = next(ws.iter_rows(values_only=True), None)
    if header is None:
        return 0.0
    # Find the column with the first per-question answer.
    # Header convention is "1. (question)" or "Q1. (question)" — accept either.
    q1_idx = None
    for i, h in enumerate(header):
        if h and isinstance(h, str):
            s = h.lstrip()
            if s.startswith("1.") or s.startswith("Q1.") or s.startswith("q1."):
                q1_idx = i
                break
    if q1_idx is None:
        return 0.0
    total = 0
    filled = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row is None or row[0] is None:
            continue
        total += 1
        v = row[q1_idx] if q1_idx < len(row) else None
        if v is not None and (not isinstance(v, str) or v.strip() not in ("", "(blank)")):
            filled += 1
    return filled / total if total else 0.0


def check(wb: openpyxl.Workbook, threshold: float = 0.80) -> Dict:
    agreement_sheets = [s for s in wb.sheetnames if "agreement" in s.lower()]
    present_coders = [c for c in KNOWN_CODERS if c in wb.sheetnames]
    fractions = {c: _coder_fill_fraction(wb, c) for c in present_coders}

    if not agreement_sheets:
        return {
            "agreement_sheets": [],
            "coder_fill_fractions": fractions,
            "passes": False,
            "reason": "no_agreement_sheet",
        }
    for c, f in fractions.items():
        if f < threshold:
            return {
                "agreement_sheets": agreement_sheets,
                "coder_fill_fractions": fractions,
                "passes": False,
                "reason": f"coder_{c}_underfilled",
            }
    return {
        "agreement_sheets": agreement_sheets,
        "coder_fill_fractions": fractions,
        "passes": True,
        "reason": "ok",
    }
