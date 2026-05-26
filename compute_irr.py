"""IRR pilot orchestrator.

Loads a cross_q_check workbook, normalizes answers, computes per-question
IRR metrics, returns a structured dict. The reporting layer (`report.py`)
consumes the dict and emits Excel + Markdown.
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
from typing import Dict, List

import io_xlsx
import irr_metrics
import normalize


BINARY_QUESTIONS = ("Q1", "Q2", "Q3", "Q6")
MULTI_LABEL_QUESTIONS = ("Q4",)
COMPOUND_CATEGORICAL_QUESTIONS = ("Q5",)
QUESTIONS = BINARY_QUESTIONS + MULTI_LABEL_QUESTIONS + COMPOUND_CATEGORICAL_QUESTIONS
ALL_CODERS = ("Leah", "Bridget", "Rachel", "Alia")

UNDERPOWERED_THRESHOLD = 30


def _question_type(q: str) -> str:
    if q in BINARY_QUESTIONS:
        return "binary"
    if q in MULTI_LABEL_QUESTIONS:
        return "multi_label"
    if q in COMPOUND_CATEGORICAL_QUESTIONS:
        return "compound_categorical"
    raise ValueError(f"unknown question {q}")


def _pivot_to_units_x_coders(df, question: str, coders: List[str]):
    """Return dict mapping order_num -> {coder: normalized_answer}.

    For multi-label / compound questions, the answer is a frozenset.
    For binary questions, the answer is a string ('yes' / 'no') or None.
    """
    sub = df[df["question"] == question]
    grouped = {}
    for _, row in sub.iterrows():
        order = row["order_num"]
        ans = row["answer"]
        if question in MULTI_LABEL_QUESTIONS or question in COMPOUND_CATEGORICAL_QUESTIONS:
            ans = normalize.split_label_set(ans)
        else:
            ans = normalize.normalize_categorical(ans)
        grouped.setdefault(order, {})[row["coder"]] = ans
    return grouped


def _compute_question_metrics(question: str, units_x_coders, coders: List[str]) -> Dict:
    qtype = _question_type(question)
    out = {
        "type": qtype,
        "n_units": 0,
        "raw_pct_agreement": float("nan"),
        "pairwise_cohen": {},
        "mean_pairwise_cohen": float("nan"),
        "krippendorff_alpha": float("nan"),
        "fleiss_kappa": float("nan"),
        "strict_pct_agreement": None,
        "mean_jaccard": None,
        "underpowered": True,
        "disagreements": [],
    }

    if qtype == "binary":
        # Denominator: units where >=2 coders answered non-blank.
        eligible_units = []
        for order, by_coder in units_x_coders.items():
            non_blank_coders = [c for c, v in by_coder.items() if v is not None]
            if len(non_blank_coders) >= 2:
                eligible_units.append(order)
        out["n_units"] = len(eligible_units)

        # Raw agreement
        agreed = 0
        for order in eligible_units:
            vals = [v for v in units_x_coders[order].values() if v is not None]
            if len(set(vals)) == 1:
                agreed += 1
            else:
                # capture disagreement
                disagreement_row = {"order_num": order}
                for c in coders:
                    disagreement_row[c] = units_x_coders[order].get(c)
                out["disagreements"].append(disagreement_row)
        out["raw_pct_agreement"] = agreed / out["n_units"] if out["n_units"] else float("nan")

        # Pairwise Cohen
        pairs = list(combinations(coders, 2))
        cohen_values = []
        for a, b in pairs:
            ra, rb = [], []
            for order in eligible_units:
                va = units_x_coders[order].get(a)
                vb = units_x_coders[order].get(b)
                if va is None or vb is None:
                    continue
                ra.append(va); rb.append(vb)
            k = irr_metrics.cohen_kappa(ra, rb)
            out["pairwise_cohen"][(a, b)] = k
            import math
            if not math.isnan(k):
                cohen_values.append(k)
        if cohen_values:
            out["mean_pairwise_cohen"] = sum(cohen_values) / len(cohen_values)

        # Krippendorff alpha
        matrix = []
        for order in eligible_units:
            row = [units_x_coders[order].get(c) for c in coders]
            matrix.append(row)
        out["krippendorff_alpha"] = irr_metrics.krippendorff_alpha_nominal(matrix)

        # Fleiss kappa: only units where ALL coders participated
        fleiss_rows = []
        for order in eligible_units:
            vals = [units_x_coders[order].get(c) for c in coders]
            if all(v is not None for v in vals):
                fleiss_rows.append(vals)
        if fleiss_rows:
            cats = sorted({v for row in fleiss_rows for v in row})
            counts = []
            for row in fleiss_rows:
                counts.append([sum(1 for v in row if v == c) for c in cats])
            try:
                out["fleiss_kappa"] = irr_metrics.fleiss_kappa(counts)
            except ValueError:
                pass

        out["underpowered"] = out["n_units"] < UNDERPOWERED_THRESHOLD

    else:  # multi_label or compound_categorical
        # Denominator: units where >=1 coder gave a non-empty set
        eligible_units = []
        for order, by_coder in units_x_coders.items():
            non_blank = [c for c, v in by_coder.items() if v is not None and len(v) > 0]
            if len(non_blank) >= 1:
                eligible_units.append(order)
        out["n_units"] = len(eligible_units)

        # Strict % agreement: among pairs of coders on each unit who participated,
        # count rows where the sets are exactly equal.
        agreed_rows = 0
        for order in eligible_units:
            sets_present = [v for v in units_x_coders[order].values() if v is not None]
            if len(sets_present) >= 2 and len(set(sets_present)) == 1:
                agreed_rows += 1
            elif len(sets_present) >= 2:
                disagreement_row = {"order_num": order}
                for c in coders:
                    v = units_x_coders[order].get(c)
                    disagreement_row[c] = ", ".join(sorted(v)) if v is not None else None
                out["disagreements"].append(disagreement_row)
        out["strict_pct_agreement"] = (
            agreed_rows / out["n_units"] if out["n_units"] else float("nan")
        )
        out["raw_pct_agreement"] = out["strict_pct_agreement"]  # used by report uniformly

        # Mean Jaccard across all coder pairs on each unit (mean of pair means)
        per_unit_jaccards = []
        for order in eligible_units:
            present = [(c, v) for c, v in units_x_coders[order].items() if v is not None]
            if len(present) < 2:
                # Single coder: define Jaccard as 1 if non-empty (no disagreement possible)
                continue
            pair_jaccards = []
            for (c1, v1), (c2, v2) in combinations(present, 2):
                import math
                j = normalize.jaccard(v1, v2)
                if not math.isnan(j):
                    pair_jaccards.append(j)
            if pair_jaccards:
                per_unit_jaccards.append(sum(pair_jaccards) / len(pair_jaccards))
        if per_unit_jaccards:
            out["mean_jaccard"] = sum(per_unit_jaccards) / len(per_unit_jaccards)

        # Pairwise Cohen on the strict (stringified) categorical
        pairs = list(combinations(coders, 2))
        cohen_values = []
        for a, b in pairs:
            ra, rb = [], []
            for order in eligible_units:
                va = units_x_coders[order].get(a)
                vb = units_x_coders[order].get(b)
                if va is None or vb is None:
                    continue
                ra.append(",".join(sorted(va)))
                rb.append(",".join(sorted(vb)))
            k = irr_metrics.cohen_kappa(ra, rb)
            out["pairwise_cohen"][(a, b)] = k
            import math
            if not math.isnan(k):
                cohen_values.append(k)
        if cohen_values:
            out["mean_pairwise_cohen"] = sum(cohen_values) / len(cohen_values)

        # Krippendorff alpha on stringified sets
        matrix = []
        for order in eligible_units:
            row = []
            for c in coders:
                v = units_x_coders[order].get(c)
                row.append(",".join(sorted(v)) if v is not None else None)
            matrix.append(row)
        out["krippendorff_alpha"] = irr_metrics.krippendorff_alpha_nominal(matrix)

        out["underpowered"] = out["n_units"] < UNDERPOWERED_THRESHOLD

    return out


def run(path) -> Dict:
    df = io_xlsx.load_cross_q_check(path)
    coders_present = sorted(df["coder"].unique())
    result = {
        "source": Path(path),
        "n_orders": int(df["order_num"].nunique()),
        "coders_present": coders_present,
        "per_question": {},
    }
    for q in QUESTIONS:
        units = _pivot_to_units_x_coders(df, q, coders_present)
        result["per_question"][q] = _compute_question_metrics(q, units, coders_present)
    return result
