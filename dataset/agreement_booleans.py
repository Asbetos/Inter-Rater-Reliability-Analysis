"""Read the qN.agree boolean columns from a specific agreement sheet.

Returns {order_num: {Q1..Q7: bool|None}}. None for cells that are blank
or not parseable as a boolean. Raises ValueError if the sheet is missing
order.num or has no qN.agree columns at all.

The question count varies across volumes (some have Q1-Q6, some Q1-Q7);
the reader includes only the questions actually present in the header.
"""
from __future__ import annotations

from typing import Dict, Optional

import openpyxl


QUESTIONS = ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7")


def _to_bool(v) -> Optional[bool]:
    if v is True:
        return True
    if v is False:
        return False
    if isinstance(v, str):
        stripped = v.strip().upper()
        if stripped == "TRUE":
            return True
        if stripped == "FALSE":
            return False
    return None


def read(wb: openpyxl.Workbook, sheet_name: str) -> Dict[int, Dict[str, Optional[bool]]]:
    """Read the qN.agree boolean table from `wb[sheet_name]`.

    Returns {order_num: {"Q1": bool|None, ...}}. Only the questions actually
    present in the sheet's header appear in the inner dict.

    Raises:
        ValueError: if 'order.num' column is missing OR no qN.agree columns
                    are present.
    """
    ws = wb[sheet_name]
    header = list(next(ws.iter_rows(values_only=True), []))
    col_idx: Dict[str, int] = {}
    for i, h in enumerate(header):
        if isinstance(h, str):
            col_idx[h.strip().lower()] = i
    if "order.num" not in col_idx:
        raise ValueError(f"sheet {sheet_name!r} missing 'order.num' column")
    order_col = col_idx["order.num"]
    q_cols: Dict[str, int] = {}
    for q in QUESTIONS:
        key = f"{q.lower()}.agree"
        if key in col_idx:
            q_cols[q] = col_idx[key]
    if not q_cols:
        raise ValueError(f"sheet {sheet_name!r} has no qN.agree columns")
    result: Dict[int, Dict[str, Optional[bool]]] = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or order_col >= len(row) or row[order_col] is None:
            continue
        try:
            order = int(row[order_col])
        except (TypeError, ValueError):
            continue
        per_q = {}
        for q, ci in q_cols.items():
            v = row[ci] if ci < len(row) else None
            per_q[q] = _to_bool(v)
        result[order] = per_q
    return result
