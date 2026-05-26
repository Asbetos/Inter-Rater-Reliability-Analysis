"""Pure-numpy IRR metrics: Cohen's kappa, Fleiss' kappa, Krippendorff's alpha, mean Jaccard.

Each function accepts data in a form natural to citizen_voice cross_q_check files:
two parallel lists for Cohen, a units-by-raters matrix (with None for missing) for
Fleiss and Krippendorff, paired iterables of frozensets for Jaccard.
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Iterable, List, Optional, Sequence


def _drop_missing_pairs(a, b):
    """Yield (x, y) for pairs where neither is None."""
    for x, y in zip(a, b):
        if x is None or y is None:
            continue
        yield x, y


def cohen_kappa(rater_a: Sequence, rater_b: Sequence) -> float:
    """Cohen's kappa for two raters over the same items.

    Pairs where either rater is None are dropped (treated as missing data,
    not as a third category).

    Returns NaN if there is insufficient data or only one category was used
    by both raters (kappa is undefined when Pe == 1).
    """
    pairs = list(_drop_missing_pairs(rater_a, rater_b))
    if not pairs:
        return math.nan
    categories = sorted({x for pair in pairs for x in pair})
    idx = {c: i for i, c in enumerate(categories)}
    n = len(pairs)
    k = len(categories)
    if k == 1:
        return math.nan
    table = [[0] * k for _ in range(k)]
    for x, y in pairs:
        table[idx[x]][idx[y]] += 1
    po = sum(table[i][i] for i in range(k)) / n
    marg_a = [sum(table[i]) / n for i in range(k)]
    marg_b = [sum(table[i][j] for i in range(k)) / n for j in range(k)]
    pe = sum(marg_a[i] * marg_b[i] for i in range(k))
    if pe == 1.0:
        return math.nan
    return (po - pe) / (1.0 - pe)
