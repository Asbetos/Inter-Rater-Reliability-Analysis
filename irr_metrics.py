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


def fleiss_kappa(counts: Sequence[Sequence[int]]) -> float:
    """Fleiss' kappa over a fixed-N raters-by-categories count matrix.

    `counts[i][j]` = number of raters assigning unit i to category j.
    All rows must sum to the same total (raters per unit).

    Returns NaN if Pe == 1 (only one category used) or N == 0.
    """
    if not counts:
        return math.nan
    N = len(counts)
    k = len(counts[0])
    n = sum(counts[0])
    if n < 2:
        raise ValueError("Fleiss kappa requires at least 2 raters per unit")
    for row in counts:
        if len(row) != k or sum(row) != n:
            raise ValueError(
                "Fleiss kappa requires all units have the same total rater count "
                "and the same category dimension"
            )
    p_j = [sum(counts[i][j] for i in range(N)) / (N * n) for j in range(k)]
    P_i = [
        (sum(counts[i][j] ** 2 for j in range(k)) - n) / (n * (n - 1))
        for i in range(N)
    ]
    P_bar = sum(P_i) / N
    Pe = sum(p ** 2 for p in p_j)
    if Pe == 1.0:
        return math.nan
    return (P_bar - Pe) / (1.0 - Pe)


def krippendorff_alpha_nominal(matrix: Sequence[Sequence[Optional[str]]]) -> float:
    """Krippendorff's alpha for nominal data with missing values.

    `matrix[i]` is a list of values from each rater for unit i. Missing
    values are None.

    Implementation follows Krippendorff (2011) "Computing Krippendorff's
    alpha-reliability". Builds the coincidence matrix and computes observed
    vs expected disagreement.

    Returns NaN if no unit has >= 2 non-missing values (no pairs to count).
    """
    # Collect categories from non-missing values.
    categories = sorted({v for row in matrix for v in row if v is not None}, key=str)
    if not categories:
        return math.nan
    idx = {c: i for i, c in enumerate(categories)}
    k = len(categories)

    O = [[0.0] * k for _ in range(k)]
    for row in matrix:
        present = [v for v in row if v is not None]
        m = len(present)
        if m < 2:
            continue
        # For each ordered pair (i, j) with i != j of the m values, add
        # 1 / (m - 1) to O[present[i]][present[j]]. This is equivalent to:
        # for each pair of distinct positions, contribute both (a,b) and
        # (b,a). The sum yields the standard Krippendorff coincidence count.
        counts_per_value = Counter(present)
        for c1, n1 in counts_per_value.items():
            for c2, n2 in counts_per_value.items():
                if c1 == c2:
                    # number of ordered same-value pairs = n1 * (n1 - 1)
                    contribution = n1 * (n1 - 1) / (m - 1)
                else:
                    # number of ordered different-value pairs = n1 * n2
                    contribution = n1 * n2 / (m - 1)
                O[idx[c1]][idx[c2]] += contribution

    n_c = [sum(O[i]) for i in range(k)]
    n_total = sum(n_c)
    if n_total == 0 or n_total == 1:
        return math.nan

    # Observed disagreement (nominal: 1 if c != c', else 0)
    D_o_num = sum(O[i][j] for i in range(k) for j in range(k) if i != j)
    D_o = D_o_num / n_total

    # Expected disagreement
    D_e_num = sum(
        n_c[i] * n_c[j] for i in range(k) for j in range(k) if i != j
    )
    D_e = D_e_num / (n_total * (n_total - 1))

    if D_e == 0:
        # Perfect agreement -> alpha defined as 1
        return 1.0
    return 1.0 - D_o / D_e
