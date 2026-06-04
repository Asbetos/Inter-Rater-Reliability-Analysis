"""Per-question OLS regression on a one-hot encoded version of the v2 per-pair dataset.

Pipeline (single in-memory pass, one script invocation):
  Phase A: build one-hot dataframe; persist to disk for audit
  Phase B: for each Q in Q1..Q7, filter + fit OLS (no intercept) + compute diagnostics + write per-Q report
  Phase C: write cross-question summary

Design choices:
  - No intercept (formula `~ 0 + ...`): all 5 coder dummies (is_alia ... is_rachel) are included
    explicitly. Per row exactly two are 1, so collectively they span the implicit baseline.
  - Volume 95 is dropped to serve as the reference category (its effect folds into the null space).
  - n_overlap_orders, n_disagreements, volume, question are AUDIT/metadata only — NOT regressors.
  - Note: with no intercept, statsmodels reports an UNCENTERED R^2 by default; this is NOT directly
    comparable to the standard centered R^2.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.api import anova_lm

_HERE = Path(__file__).resolve().parent
_INPUT_CSV = _HERE.parent.parent / "outputs" / "irr_dataset_v2_per_pair.csv"
_OUT_DIR = _HERE / "outputs"

CODERS = ("Alia", "Brian", "Bridget", "Leah", "Rachel")
QUESTIONS = ("Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7")
VOLUME_REFERENCE = "Volume 95"   # dropped column -> reference category


def _volume_to_col(vol: str) -> str:
    """Normalize a volume label like "Volume 134 - Part 2" -> "vol_134_part_2"."""
    base = vol.lower().replace("volume ", "").strip()
    base = re.sub(r"\s+-\s+", "_", base)        # " - " -> "_"
    base = re.sub(r"\s+", "_", base)             # spaces -> _
    return f"vol_{base}"


# ----------------------------------------------------------------------------
# Phase A: one-hot dataframe construction
# ----------------------------------------------------------------------------

def build_onehot(df_in: pd.DataFrame) -> pd.DataFrame:
    df = df_in.drop(columns=[
        "is_legacy_volume", "agreement_sheet_date", "chosen_sheet",
    ], errors="ignore").copy()

    # Coder presence indicators + per-coder NCP
    for coder in CODERS:
        in_pair = ((df["coder_a"] == coder) | (df["coder_b"] == coder)).astype(int)
        df[f"is_{coder.lower()}"] = in_pair
        ncp = np.where(
            df["coder_a"] == coder, df["number_coded_prior_a"],
            np.where(df["coder_b"] == coder, df["number_coded_prior_b"], 0),
        )
        df[f"ncp_{coder.lower()}"] = ncp.astype(int)

    # Volume one-hots (ordered alphabetically for stable column order)
    volumes_sorted = sorted(df["volume"].unique())
    for vol in volumes_sorted:
        df[_volume_to_col(vol)] = (df["volume"] == vol).astype(int)

    # Question one-hots
    for q in QUESTIONS:
        df[f"q_{q}"] = (df["question"] == q).astype(int)

    # Drop now-redundant raw coder/NCP columns
    df = df.drop(columns=[
        "coder_a", "coder_b",
        "number_coded_prior_a", "number_coded_prior_b",
    ])

    # ---- Sanity assertions ----
    coder_cols = [f"is_{c.lower()}" for c in CODERS]
    assert (df[coder_cols].sum(axis=1) == 2).all(), (
        "Each row must have exactly 2 coder indicators set to 1"
    )
    vol_cols = [_volume_to_col(v) for v in volumes_sorted]
    assert (df[vol_cols].sum(axis=1) == 1).all(), (
        "Each row must have exactly one volume one-hot set to 1"
    )
    q_cols = [f"q_{q}" for q in QUESTIONS]
    assert (df[q_cols].sum(axis=1) == 1).all(), (
        "Each row must have exactly one question one-hot set to 1"
    )
    # NCP == 0 whenever coder not in pair (the converse direction — NCP > 0 only if in pair)
    for c in CODERS:
        is_col = f"is_{c.lower()}"
        ncp_col = f"ncp_{c.lower()}"
        ncp_when_out = df.loc[df[is_col] == 0, ncp_col]
        assert (ncp_when_out == 0).all(), (
            f"{ncp_col} must be 0 when {is_col} == 0"
        )

    return df


# ----------------------------------------------------------------------------
# Phase B: per-question fit + diagnostics
# ----------------------------------------------------------------------------

def fit_per_question(df: pd.DataFrame, q: str):
    """Filter to question q, drop q_* one-hots, drop vol_95, fit OLS no-intercept."""
    q_col = f"q_{q}"
    sub = df[df[q_col] == 1].copy()
    if len(sub) == 0:
        return None, sub

    # Drop all q_* columns (constant within filter)
    sub = sub.drop(columns=[f"q_{x}" for x in QUESTIONS])
    # Drop reference volume (Vol 95)
    ref_col = _volume_to_col(VOLUME_REFERENCE)
    sub = sub.drop(columns=[ref_col], errors="ignore")

    drop_for_design = ["volume", "question", "n_disagreements"]
    predictor_cols = [
        c for c in sub.columns
        if c not in ("pct_agreement", "n_overlap_orders") + tuple(drop_for_design)
    ]
    df_design = sub.drop(columns=drop_for_design)
    formula = "pct_agreement ~ 0 + " + " + ".join(predictor_cols)
    model = smf.ols(formula, data=df_design).fit()
    return model, sub


def coefficient_table(model) -> pd.DataFrame:
    params = model.params
    bse = model.bse
    tvals = model.tvalues
    pvals = model.pvalues
    ci = model.conf_int(alpha=0.05)
    rows = []
    for name in params.index:
        p = pvals[name]
        stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        rows.append({
            "term": name,
            "coef": params[name],
            "std_err": bse[name],
            "t": tvals[name],
            "p_value": p,
            "ci_low": ci.loc[name, 0],
            "ci_high": ci.loc[name, 1],
            "significance": stars,
        })
    return pd.DataFrame.from_records(rows)


def variance_decomposition(model) -> pd.DataFrame:
    try:
        anova = anova_lm(model, typ=2)
    except Exception as e:
        return pd.DataFrame([{"error": str(e)}])
    rss = anova.loc["Residual", "sum_sq"] if "Residual" in anova.index else 0.0
    ss_model = anova["sum_sq"].sum() - rss
    ss_total = ss_model + rss
    rows = []
    for term in anova.index:
        if term == "Residual":
            continue
        ss = anova.loc[term, "sum_sq"]
        rows.append({
            "term": term,
            "sum_sq": ss,
            "df": int(anova.loc[term, "df"]),
            "F": anova.loc[term, "F"],
            "p_value": anova.loc[term, "PR(>F)"],
            "pct_of_model_ss": 100.0 * ss / ss_model if ss_model else float("nan"),
            "pct_of_total_ss": 100.0 * ss / ss_total if ss_total else float("nan"),
        })
    return pd.DataFrame.from_records(rows).sort_values("pct_of_model_ss", ascending=False)


def vif_table(model) -> pd.DataFrame:
    X = pd.DataFrame(model.model.exog, columns=model.model.exog_names)
    rows = []
    for i, col in enumerate(X.columns):
        try:
            vif = variance_inflation_factor(X.values, i)
        except Exception:
            vif = float("nan")
        rows.append({"term": col, "vif": vif})
    return pd.DataFrame.from_records(rows).sort_values("vif", ascending=False)


def _condition_number(model) -> float:
    X = model.model.exog
    try:
        ev = np.linalg.eigvalsh(X.T @ X)
        ev = np.sort(np.abs(ev))[::-1]
        return float(np.sqrt(ev[0] / max(ev[-1], 1e-12)))
    except Exception:
        return float("nan")


def _vif_severity(v: float) -> tuple[str, str]:
    if pd.isna(v) or v == float("inf"):
        return "infinite / undefined", "infinite / undefined"
    if v < 5:
        return f"{v:.2f}", "OK"
    if v < 10:
        return f"{v:.2f}", "moderate"
    return f"{v:.2f}", "**severe**"


def render_advisor_report(q, model, sub_df, coef_df, var_df, vif_df) -> str:
    n = int(model.nobs)
    k = int(model.df_model)
    df_resid = int(model.df_resid)
    r2 = model.rsquared            # uncentered R^2 (no-intercept model)
    r2_adj = model.rsquared_adj
    f_stat = model.fvalue
    f_p = model.f_pvalue
    aic = model.aic
    bic = model.bic
    rmse = float(np.sqrt((model.resid ** 2).mean()))
    mae = float(model.resid.abs().mean())
    cond = _condition_number(model)

    # Volume distribution within the subsample, for context
    vol_counts = sub_df["volume"].value_counts().sort_index()

    lines: list[str] = []
    lines.append(f"# IRR Per-Question Regression — {q}")
    lines.append("")
    lines.append(
        "**Research question:** Within this single question, do per-coder agreement levels "
        "and per-coder coding experience (`number_coded_prior`) predict inter-rater agreement, "
        "after controlling for volume?"
    )
    lines.append("")
    lines.append(
        f"**Subsample:** N = {n} (coder-pair × volume) rows where `question == {q}`. "
        f"Volumes represented: {len(vol_counts)} of 21. "
        f"Mean `pct_agreement` = {sub_df['pct_agreement'].mean():.4f} "
        f"(min {sub_df['pct_agreement'].min():.3f}, max {sub_df['pct_agreement'].max():.3f})."
    )
    lines.append("")
    lines.append("**Model design:**")
    lines.append("")
    lines.append("```")
    lines.append(f"pct_agreement ~ 0 + is_<coder>(x5) + ncp_<coder>(x5) + vol_<id>(x20)")
    lines.append("```")
    lines.append("")
    lines.append(
        "- **No intercept** (`~ 0 + ...`): the 5 coder dummies are all included; each row has "
        "exactly two of them set to 1, so they collectively span the implicit baseline.\n"
        f"- **Reference volume:** `{_volume_to_col(VOLUME_REFERENCE)}` is dropped, so all `vol_*` "
        "coefficients are differences vs. Vol 95.\n"
        "- **Target:** `pct_agreement` (raw % agreement from precomputed `qN.agree` booleans).\n"
        "- **n_overlap_orders / n_disagreements / volume / question:** retained as metadata only — "
        "NOT regressors."
    )
    lines.append("")
    lines.append(
        "> **Note on R²:** This is a no-intercept model, but the 5 coder dummies sum to a constant "
        "(= 2) per row, so statsmodels detects an implicit constant in the design and reports the "
        "**centered R²** (the familiar variance-explained interpretation). Treat it as comparable "
        "to ordinary OLS R², not as the uncentered no-intercept R²."
    )
    lines.append("")

    # ---- 1. Performance ----
    lines.append("## 1. Performance metrics")
    lines.append("")
    lines.append("| Metric | Value | Note |")
    lines.append("|---|---|---|")
    lines.append(f"| N (observations) | {n} | filtered to question {q} |")
    lines.append(f"| k (predictors) | {k} | no intercept |")
    lines.append(f"| Residual df | {df_resid} | {'OK' if df_resid > 5 else '**LOW**'} |")
    lines.append(f"| R² | {r2:.4f} | centered R² (implicit-constant design) |")
    lines.append(f"| Adjusted R² | {r2_adj:.4f} | k-penalized variant |")
    lines.append(f"| F-statistic | {f_stat:.2f} | joint significance of all predictors |")
    lines.append(f"| F p-value | {f_p:.4g} | |")
    lines.append(f"| RMSE | {rmse:.4f} | typical residual on pct_agreement |")
    lines.append(f"| MAE | {mae:.4f} | mean absolute residual |")
    lines.append(f"| AIC | {aic:.1f} | |")
    lines.append(f"| BIC | {bic:.1f} | |")
    lines.append(f"| Condition number | {cond:.2f} | >30 = moderate collinearity; >100 = severe |")
    lines.append("")
    if df_resid <= 5:
        lines.append(
            "> **WARNING:** Residual degrees of freedom ≤ 5. The model is essentially "
            "saturating the available variance and individual coefficients are highly unstable."
        )
        lines.append("")

    # ---- 2. Variance decomposition ----
    lines.append("## 2. Variance decomposition (Type II ANOVA)")
    lines.append("")
    if "error" in var_df.columns:
        lines.append(f"ANOVA could not be computed: `{var_df.iloc[0]['error']}`")
    else:
        lines.append("| Term | df | F | p-value | % of model SS | % of total SS |")
        lines.append("|---|---|---|---|---|---|")
        for _, r in var_df.iterrows():
            sig = ("***" if r.p_value < 0.001 else "**" if r.p_value < 0.01
                   else "*" if r.p_value < 0.05 else "")
            lines.append(
                f"| `{r.term}` | {r.df} | {r.F:.2f} | {r.p_value:.4g} {sig} | "
                f"{r.pct_of_model_ss:.1f}% | {r.pct_of_total_ss:.1f}% |"
            )
    lines.append("")

    # ---- 3. Coefficient table ----
    lines.append("## 3. Coefficient table")
    lines.append("")
    lines.append("| Term | Coef | Std Err | t | p-value | 95% CI | Sig |")
    lines.append("|---|---|---|---|---|---|---|")
    # Sort coefs in a stable, readable order: coder indicators, then NCP, then volumes
    def _sort_key(name: str) -> tuple:
        if name.startswith("is_"):
            return (0, name)
        if name.startswith("ncp_"):
            return (1, name)
        if name.startswith("vol_"):
            return (2, name)
        return (3, name)
    coef_sorted = coef_df.iloc[coef_df["term"].map(_sort_key).argsort()]
    for _, r in coef_sorted.iterrows():
        lines.append(
            f"| `{r.term}` | {r.coef:+.5f} | {r.std_err:.5f} | {r.t:+.2f} | "
            f"{r.p_value:.4g} | [{r.ci_low:+.4f}, {r.ci_high:+.4f}] | {r.significance} |"
        )
    lines.append("")
    lines.append("Significance codes: `***` p<0.001, `**` p<0.01, `*` p<0.05.")
    lines.append("")

    # ---- 4. VIF ----
    lines.append("## 4. Variance Inflation Factors (VIF)")
    lines.append("")
    lines.append(
        "VIF measured on the no-intercept design matrix. Note: in no-intercept models, "
        "absolute VIF values are less straightforward to interpret than in standard intercept "
        "models — treat large values as a flag for relative collinearity rather than absolute severity."
    )
    lines.append("")
    lines.append("| Predictor | VIF | Severity |")
    lines.append("|---|---|---|")
    for _, r in vif_df.iterrows():
        vif_str, sev = _vif_severity(r.vif)
        lines.append(f"| `{r.term}` | {vif_str} | {sev} |")
    lines.append("")

    # ---- 5. Multicollinearity diagnostics ----
    lines.append("## 5. Multicollinearity diagnostics")
    lines.append("")
    if pd.isna(cond) or cond == float("inf"):
        cond_interp = "design matrix is rank-deficient or near-singular"
    elif cond < 30:
        cond_interp = "low multicollinearity"
    elif cond < 100:
        cond_interp = "moderate multicollinearity"
    else:
        cond_interp = "**severe** multicollinearity"
    lines.append(f"- Condition number: **{cond:.2f}** — {cond_interp}.")
    lines.append(f"- Predictors with VIF > 10 (severe): " + (
        ", ".join(f"`{t}`" for t in vif_df.loc[vif_df.vif > 10, "term"]) or "none"
    ))
    lines.append("")

    # ---- 6. Interpretation ----
    lines.append("## 6. Plain-language interpretation")
    lines.append("")

    # Coder effects
    coder_rows = coef_df[coef_df.term.str.startswith("is_")]
    sig_coders = coder_rows[coder_rows.p_value < 0.05]
    if len(sig_coders):
        bits = []
        for _, r in sig_coders.iterrows():
            direction = "higher" if r.coef > 0 else "lower"
            bits.append(f"`{r.term}` = {r.coef:+.4f} ({direction}, p = {r.p_value:.4g})")
        lines.append("**Coder presence effects (significant at p<0.05):** " + "; ".join(bits) + ".")
    else:
        lines.append(
            "**Coder presence effects:** No `is_<coder>` term reaches p<0.05. "
            "Coder identity does not show a statistically detectable shift in agreement for this question."
        )
    lines.append("")

    # NCP effects
    ncp_rows = coef_df[coef_df.term.str.startswith("ncp_")]
    sig_ncp = ncp_rows[ncp_rows.p_value < 0.05]
    if len(sig_ncp):
        bits = []
        for _, r in sig_ncp.iterrows():
            direction = "higher" if r.coef > 0 else "lower"
            bits.append(
                f"`{r.term}` = {r.coef:+.5f} ({direction} agreement per additional prior volume, "
                f"p = {r.p_value:.4g})"
            )
        lines.append("**Per-coder experience (NCP) effects (significant at p<0.05):** " + "; ".join(bits) + ".")
        lines.append("")
        lines.append("> This is evidence that for **this question**, the named coder(s) show a "
                     "real association between prior coding experience and agreement.")
    else:
        lines.append(
            "**Per-coder experience (NCP) effects:** No `ncp_<coder>` term reaches p<0.05. "
            "Within this question, prior-volume count does not statistically predict pair agreement "
            "for any single coder."
        )
    lines.append("")

    # Volume effects: top by p-value
    vol_rows = coef_df[coef_df.term.str.startswith("vol_")].copy()
    if len(vol_rows):
        vol_rows["p_value"] = vol_rows["p_value"].fillna(1.0)
        top3 = vol_rows.nsmallest(3, "p_value")
        bits = []
        for _, r in top3.iterrows():
            sig = (" *" if r.p_value < 0.05 else "")
            bits.append(f"`{r.term}` = {r.coef:+.4f} (p = {r.p_value:.4g}{sig})")
        lines.append("**Top 3 volume effects by p-value (vs. Vol 95 reference):** " + "; ".join(bits) + ".")
    lines.append("")

    # Dominant variance contributor
    if "error" not in var_df.columns and len(var_df):
        top_term = var_df.iloc[0]
        lines.append(
            f"**Largest contributor to explained variance:** `{top_term.term}` "
            f"({top_term.pct_of_model_ss:.1f}% of model SS, F = {top_term.F:.2f}, p = {top_term.p_value:.4g})."
        )
    lines.append("")

    # ---- 7. Caveats ----
    lines.append("## 7. Caveats")
    lines.append("")
    lines.append(
        f"- **Sample size:** N = {n} with k = {k} predictors leaves {df_resid} residual df. "
        f"{'Adequate but not generous.' if df_resid > 20 else 'Limited statistical power.' if df_resid > 5 else 'Very limited — interpret individual coefficients with extreme caution.'}"
    )
    lines.append(
        "- **No-intercept R² is uncentered:** do not compare these R² values to centered R² from "
        "intercept-bearing OLS models. Use the F p-value or the variance decomposition to gauge fit."
    )
    lines.append(
        "- **Multicollinearity expected:** the 5 coder dummies sum to 2 per row (a structural "
        "constraint), and NCP values are correlated with the corresponding coder indicators by "
        "construction (NCP > 0 ⇒ coder in pair). Some VIF inflation is design-induced, not a bug."
    )
    lines.append(
        "- **Target ceiling effect:** `pct_agreement` is heavily skewed toward 1.0. Effects are "
        "compressed by the bounded scale."
    )
    if q == "Q7":
        lines.append(
            "- **Q7-specific:** Q7 has the smallest subsample (~45 rows). Coefficient power is low."
        )
    if q in ("Q2", "Q3", "Q4", "Q5"):
        lines.append(
            f"- **{q} is conditional on Q1:** Rows where Q1 disagreed feed into this analysis; "
            "downstream agreement may inherit Q1 disagreement structure."
        )
    lines.append("")

    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Phase C: cross-question summary
# ----------------------------------------------------------------------------

def render_cross_summary(per_q_results: dict) -> str:
    lines: list[str] = []
    lines.append("# Per-Question OLS — Cross-Question Summary")
    lines.append("")
    lines.append(
        "Seven OLS regressions, one per question, on the v2 per-pair dataset's one-hot encoding. "
        "Design: no intercept (`~ 0 + ...`), all five coder dummies included, Vol 95 as the "
        "implicit reference volume."
    )
    lines.append("")
    lines.append(
        "> **R² note:** Although the formula has no intercept, the 5 coder dummies sum to a "
        "constant per row, so statsmodels detects an implicit constant and reports the standard "
        "**centered R²**. The numbers below are directly comparable to ordinary OLS R²."
    )
    lines.append("")

    # ---- 1. Headline table ----
    lines.append("## 1. Headline table")
    lines.append("")
    lines.append("| Question | N | k | df_resid | R² (centered) | Adj R² | F p-value | RMSE |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for q, res in per_q_results.items():
        m = res["model"]
        rmse = float(np.sqrt((m.resid ** 2).mean()))
        lines.append(
            f"| {q} | {int(m.nobs)} | {int(m.df_model)} | {int(m.df_resid)} | "
            f"{m.rsquared:.4f} | {m.rsquared_adj:.4f} | {m.f_pvalue:.4g} | {rmse:.4f} |"
        )
    lines.append("")

    # ---- 2. Coder coefficient comparison ----
    lines.append("## 2. Coder coefficients across questions (`is_<coder>`)")
    lines.append("")
    lines.append("Bold + asterisk marks p < 0.05.")
    lines.append("")
    header = "| Coder | " + " | ".join(per_q_results.keys()) + " |"
    lines.append(header)
    lines.append("|" + "---|" * (len(per_q_results) + 1))
    for coder in CODERS:
        term = f"is_{coder.lower()}"
        cells = [coder]
        for q, res in per_q_results.items():
            coef_df = res["coef_df"]
            row = coef_df[coef_df.term == term]
            if len(row) == 0:
                cells.append("—")
            else:
                r = row.iloc[0]
                if r.p_value < 0.05:
                    cells.append(f"**{r.coef:+.4f}\\***")
                else:
                    cells.append(f"{r.coef:+.4f}")
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    # ---- 3. NCP coefficient comparison ----
    lines.append("## 3. Per-coder NCP coefficients across questions (`ncp_<coder>`)")
    lines.append("")
    lines.append("Bold + asterisk marks p < 0.05. **Significant NCP = experience effect for that coder on that question.**")
    lines.append("")
    lines.append(header)
    lines.append("|" + "---|" * (len(per_q_results) + 1))
    for coder in CODERS:
        term = f"ncp_{coder.lower()}"
        cells = [coder]
        for q, res in per_q_results.items():
            coef_df = res["coef_df"]
            row = coef_df[coef_df.term == term]
            if len(row) == 0:
                cells.append("—")
            else:
                r = row.iloc[0]
                if r.p_value < 0.05:
                    cells.append(f"**{r.coef:+.5f}\\***")
                else:
                    cells.append(f"{r.coef:+.5f}")
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    # ---- 4. Top volume effects per Q ----
    lines.append("## 4. Top 3 volume effects per question (by p-value)")
    lines.append("")
    lines.append("| Question | Top 3 `vol_*` (term, coef, p) |")
    lines.append("|---|---|")
    for q, res in per_q_results.items():
        coef_df = res["coef_df"]
        vol_rows = coef_df[coef_df.term.str.startswith("vol_")].copy()
        vol_rows["p_value"] = vol_rows["p_value"].fillna(1.0)
        top3 = vol_rows.nsmallest(3, "p_value")
        bits = []
        for _, r in top3.iterrows():
            sig = "*" if r.p_value < 0.05 else ""
            bits.append(f"`{r.term}` ({r.coef:+.3f}, p={r.p_value:.3g}{sig})")
        lines.append(f"| {q} | " + "; ".join(bits) + " |")
    lines.append("")

    # ---- 5. Plain-language per-Q interpretation ----
    lines.append("## 5. Plain-language interpretation per question")
    lines.append("")
    for q, res in per_q_results.items():
        m = res["model"]
        coef_df = res["coef_df"]
        sig_coders = coef_df[
            coef_df.term.str.startswith("is_") & (coef_df.p_value < 0.05)
        ]
        sig_ncp = coef_df[
            coef_df.term.str.startswith("ncp_") & (coef_df.p_value < 0.05)
        ]
        lines.append(f"### {q}")
        lines.append("")
        lines.append(
            f"- N = {int(m.nobs)}, residual df = {int(m.df_resid)}, "
            f"R² = {m.rsquared:.4f}, F p = {m.f_pvalue:.4g}."
        )
        if len(sig_coders):
            for _, r in sig_coders.iterrows():
                direction = "higher" if r.coef > 0 else "lower"
                lines.append(
                    f"- **{r.term}** ({direction} agreement contribution, coef = {r.coef:+.4f}, p = {r.p_value:.4g}).")
        else:
            lines.append("- No coder-presence dummy reaches p < 0.05.")
        if len(sig_ncp):
            for _, r in sig_ncp.iterrows():
                direction = "positive" if r.coef > 0 else "negative"
                lines.append(
                    f"- **{r.term}** shows a {direction} experience association "
                    f"(coef = {r.coef:+.5f} per prior volume, p = {r.p_value:.4g}).")
        else:
            lines.append("- No per-coder NCP reaches p < 0.05 — no detectable single-coder experience effect.")
        lines.append("")

    # ---- 6. Caveats ----
    lines.append("## 6. Caveats")
    lines.append("")
    lines.append(
        "- **Sample sizes are small (~60 per Q, ~45 for Q7) relative to ~30 predictors.** "
        "Residual df is typically ~30 — adequate but not generous. Q7 is the most underpowered."
    )
    lines.append(
        "- **R² is centered (standard) here**, because the coder dummies sum to a constant "
        "(implicit intercept). Per-question Adj R² values in the 0.36–0.64 range mean the "
        "design captures a substantial but far-from-complete share of the variance."
    )
    lines.append(
        "- **Multicollinearity is structural:** the 5 coder dummies sum to 2 per row, and NCP "
        "is non-zero only when the corresponding coder is in the pair. Some VIF inflation is "
        "by construction, not a flaw."
    )
    lines.append(
        "- **Q7 low-power warning:** only ~45 rows; individual coefficient significance is very "
        "fragile. Treat any single-Q7 finding as preliminary."
    )
    lines.append(
        "- **Ceiling-bounded target:** `pct_agreement` ∈ [0, 1] with most mass near 1.0; effect "
        "sizes are compressed and skewness is non-trivial. Cohen's κ would have a wider range "
        "and likely more signal."
    )
    lines.append(
        "- **Volume reference = Vol 95.** All `vol_*` coefficients are deltas vs. Vol 95. "
        "Choice of reference is arbitrary; alternative references would relabel coefficients but "
        "not change overall model fit."
    )
    lines.append("")

    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------------

def main():
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    df_raw = pd.read_csv(_INPUT_CSV)
    df_oh = build_onehot(df_raw)

    out_csv = _OUT_DIR / "irr_dataset_v2_per_pair_onehot.csv"
    out_pq = _OUT_DIR / "irr_dataset_v2_per_pair_onehot.parquet"
    df_oh.to_csv(out_csv, index=False)
    try:
        df_oh.to_parquet(out_pq)
    except Exception as e:
        print(f"WARNING: parquet write failed ({e}); CSV is still available.")
    print(f"Wrote one-hot dataset: {len(df_oh)} rows, {len(df_oh.columns)} cols")

    per_q: dict = {}
    for q in QUESTIONS:
        out_dir = _OUT_DIR / f"per_q_{q}"
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            model, sub = fit_per_question(df_oh, q)
        except Exception as e:
            print(f"{q}: FIT FAILED ({e}); skipped")
            continue
        if model is None:
            print(f"{q}: no data; skipped")
            continue
        if model.df_resid <= 5:
            print(f"{q}: WARNING residual df = {int(model.df_resid)} (<= 5)")

        coef_df = coefficient_table(model)
        var_df = variance_decomposition(model)
        vif_df = vif_table(model)
        coef_df.to_csv(out_dir / "coefficient_table.csv", index=False)
        var_df.to_csv(out_dir / "variance_decomposition.csv", index=False)
        vif_df.to_csv(out_dir / "vif_table.csv", index=False)
        (out_dir / "full_summary.txt").write_text(str(model.summary()))

        report = render_advisor_report(q, model, sub, coef_df, var_df, vif_df)
        (out_dir / "advisor_report.md").write_text(report)

        per_q[q] = {
            "model": model,
            "n": int(model.nobs),
            "r2": model.rsquared,
            "r2_adj": model.rsquared_adj,
            "f_pvalue": model.f_pvalue,
            "coef_df": coef_df,
            "var_df": var_df,
        }
        print(
            f"{q}: n={int(model.nobs)}, df_resid={int(model.df_resid)}, "
            f"R²={model.rsquared:.4f}, Adj R²={model.rsquared_adj:.4f}, "
            f"F p={model.f_pvalue:.4g}"
        )

    summary = render_cross_summary(per_q)
    summary_path = _OUT_DIR / "per_q_cross_summary.md"
    summary_path.write_text(summary)
    print(f"Wrote cross-Q summary: {summary_path}")


if __name__ == "__main__":
    main()
