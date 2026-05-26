"""Answer normalization and label-set utilities for IRR metrics."""
from __future__ import annotations

import math
from typing import FrozenSet, Optional


def normalize_categorical(value) -> Optional[str]:
    """Normalize a single categorical answer to lowercase stripped string, or None.

    Treats None, empty string, and "(blank)" as None.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        value = str(value)
    s = value.strip()
    if s == "" or s == "(blank)":
        return None
    return s.lower()


def split_label_set(value) -> FrozenSet[str]:
    """Split a Q4/Q5 comma-separated multi-label string into a frozenset of normalized labels.

    Blank/None input returns an empty frozenset.

    Naive: splits on `,` not contained in quotes. Labels are stripped and lowercased.
    """
    if value is None:
        return frozenset()
    if not isinstance(value, str):
        value = str(value)
    s = value.strip()
    if s == "" or s == "(blank)":
        return frozenset()

    # Walk the string and split on commas that are not inside double-quotes.
    parts = []
    buf = []
    in_quote = False
    for ch in s:
        if ch == '"':
            in_quote = not in_quote
            buf.append(ch)
        elif ch == "," and not in_quote:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf).strip())
    return frozenset(p.lower() for p in parts if p)


def jaccard(a: FrozenSet[str], b: FrozenSet[str]) -> float:
    """Jaccard similarity of two label sets. Returns NaN if both sets are empty."""
    if not a and not b:
        return math.nan
    union = a | b
    inter = a & b
    return len(inter) / len(union)
