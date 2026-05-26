"""Build Excel + Markdown reports from the dict returned by compute_irr.run."""
from __future__ import annotations

import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

import openpyxl


def _ceiling_band(alpha: float) -> str:
    """Map Krippendorff's alpha to a 4-band qualitative ceiling label."""
    if alpha is None or (isinstance(alpha, float) and math.isnan(alpha)):
        return "n/a"
    if alpha < 0.4:
        return "poor"
    if alpha < 0.6:
        return "moderate"
    if alpha < 0.8:
        return "substantial"
    return "almost perfect"


def _fmt(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        return f"{value:.4f}"
    return str(value)


def write_excel(result: Dict, out_path: Path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook()
    # Default sheet is named 'Sheet'; we rename rather than create+remove.
    summary = wb.active
    summary.title = "summary"

    summary.append([
        "question", "type", "n_units", "raw_pct_agreement",
        "mean_pairwise_cohen", "krippendorff_alpha", "fleiss_kappa",
        "strict_pct_agreement", "mean_jaccard",
        "ceiling_band", "underpowered",
    ])
    for q, m in result["per_question"].items():
        summary.append([
            q, m["type"], m["n_units"],
            _fmt(m["raw_pct_agreement"]),
            _fmt(m["mean_pairwise_cohen"]),
            _fmt(m["krippendorff_alpha"]),
            _fmt(m["fleiss_kappa"]),
            _fmt(m["strict_pct_agreement"]),
            _fmt(m["mean_jaccard"]),
            _ceiling_band(m["krippendorff_alpha"]),
            "yes" if m["underpowered"] else "no",
        ])

    # Pairwise kappa sheet
    pk = wb.create_sheet("pairwise_kappa")
    pk.append(["question", "coder_a", "coder_b", "cohen_kappa"])
    for q, m in result["per_question"].items():
        for (a, b), k in m["pairwise_cohen"].items():
            pk.append([q, a, b, _fmt(k)])

    # Disagreements sheet
    dis = wb.create_sheet("disagreements")
    coders = result["coders_present"]
    dis.append(["question", "order_num"] + coders)
    for q, m in result["per_question"].items():
        for d in m["disagreements"]:
            dis.append([q, d["order_num"]] + [d.get(c, "") if d.get(c) is not None else "" for c in coders])

    # Metadata sheet
    meta = wb.create_sheet("metadata")
    meta.append(["key", "value"])
    meta.append(["source", str(result["source"])])
    meta.append(["n_orders", result["n_orders"]])
    meta.append(["coders_present", ", ".join(result["coders_present"])])
    meta.append(["generated_at_utc", datetime.now(timezone.utc).isoformat(timespec="seconds")])
    meta.append(["ceiling_bands", "alpha<0.4 poor; 0.4-0.6 moderate; 0.6-0.8 substantial; >=0.8 almost perfect"])

    wb.save(out_path)
