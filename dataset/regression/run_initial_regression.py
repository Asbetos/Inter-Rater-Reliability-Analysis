"""Initial IRR regression model against v2 per-pair dataset.

Reads outputs/irr_dataset_v2_per_pair.csv. Fits multiple model variants:
  1. OLS with all features (linear experience term)
  2. WLS weighted by n_overlap_orders (gives larger pairs more weight)
  3. OLS with log(number_coded_prior + 1) (non-linear experience)
  4. Per-question OLS (separate model per Q1..Q7)

Writes:
  outputs/coefficients_summary.csv   -- coefficient table across variants
  outputs/full_summary_<variant>.txt -- statsmodels textual summary per variant
  outputs/per_question_summary.csv   -- one row per question with key stats
  outputs/insights.md                -- narrative interpretation of findings
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# Paths
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent
_INPUT_CSV = _REPO_ROOT / "outputs" / "irr_dataset_v2_per_pair.csv"
_OUTPUT_DIR = _HERE / "outputs"


def load() -> pd.DataFrame:
    df = pd.read_csv(_INPUT_CSV)
    # Drop excluded columns per user spec
    df = df.drop(columns=["agreement_sheet_date", "chosen_sheet"], errors="ignore")
    # Coerce types
    df["is_legacy_volume"] = df["is_legacy_volume"].astype(int)  # statsmodels wants numeric
    return df


def fit_ols_linear(df: pd.DataFrame):
    formula = (
        "pct_agreement ~ C(coder_a) + C(coder_b) + C(question) "
        "+ number_coded_prior_a + number_coded_prior_b + is_legacy_volume"
    )
    return smf.ols(formula, data=df).fit()


def fit_wls(df: pd.DataFrame):
    formula = (
        "pct_agreement ~ C(coder_a) + C(coder_b) + C(question) "
        "+ number_coded_prior_a + number_coded_prior_b + is_legacy_volume"
    )
    return smf.wls(formula, data=df, weights=df["n_overlap_orders"]).fit()


def fit_ols_log_experience(df: pd.DataFrame):
    df = df.copy()
    df["log_ncp_a"] = np.log1p(df["number_coded_prior_a"])
    df["log_ncp_b"] = np.log1p(df["number_coded_prior_b"])
    formula = (
        "pct_agreement ~ C(coder_a) + C(coder_b) + C(question) "
        "+ log_ncp_a + log_ncp_b + is_legacy_volume"
    )
    return smf.ols(formula, data=df).fit()


def fit_per_question_models(df: pd.DataFrame):
    """One OLS per Q1..Q7. Drop question dummies; otherwise same features.
    Filter to questions with >= 20 rows to avoid degenerate fits."""
    results = {}
    formula = (
        "pct_agreement ~ C(coder_a) + C(coder_b) "
        "+ number_coded_prior_a + number_coded_prior_b + is_legacy_volume"
    )
    for q in sorted(df["question"].unique()):
        sub = df[df["question"] == q]
        if len(sub) < 20:
            continue
        try:
            results[q] = smf.ols(formula, data=sub).fit()
        except Exception as e:
            print(f"per-question fit failed for {q}: {e}")
    return results


def coefficients_summary(models: dict) -> pd.DataFrame:
    """One row per (variant, coefficient) with estimate, std_err, p_value, n_obs, r2."""
    records = []
    for variant_name, model in models.items():
        params = model.params
        pvals = model.pvalues
        bse = model.bse
        for name in params.index:
            records.append({
                "variant": variant_name,
                "term": name,
                "coef": params[name],
                "std_err": bse[name],
                "p_value": pvals[name],
                "significant_05": pvals[name] < 0.05,
                "n_obs": int(model.nobs),
                "r2": float(model.rsquared),
                "r2_adj": float(model.rsquared_adj),
            })
    return pd.DataFrame.from_records(records)


def main():
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load()
    print(f"Loaded {len(df)} rows from {_INPUT_CSV}")
    print(f"Columns: {sorted(df.columns)}")
    print(f"Coders: {sorted(df.coder_a.unique())} x {sorted(df.coder_b.unique())}")
    print(f"Volumes: {df.volume.nunique()}, Questions: {sorted(df.question.unique())}")
    print(f"pct_agreement summary: mean={df.pct_agreement.mean():.4f}, std={df.pct_agreement.std():.4f}")
    print()

    # Fit all 3 main variants
    print("Fitting OLS (linear experience)...")
    m_ols = fit_ols_linear(df)
    print(f"  n={int(m_ols.nobs)}, R²={m_ols.rsquared:.4f}, adj R²={m_ols.rsquared_adj:.4f}, F p-value={m_ols.f_pvalue:.4g}")
    (_OUTPUT_DIR / "full_summary_ols_linear.txt").write_text(str(m_ols.summary()))

    print("Fitting WLS (weighted by n_overlap_orders)...")
    m_wls = fit_wls(df)
    print(f"  n={int(m_wls.nobs)}, R²={m_wls.rsquared:.4f}, adj R²={m_wls.rsquared_adj:.4f}")
    (_OUTPUT_DIR / "full_summary_wls.txt").write_text(str(m_wls.summary()))

    print("Fitting OLS (log experience)...")
    m_log = fit_ols_log_experience(df)
    print(f"  n={int(m_log.nobs)}, R²={m_log.rsquared:.4f}, adj R²={m_log.rsquared_adj:.4f}, F p-value={m_log.f_pvalue:.4g}")
    (_OUTPUT_DIR / "full_summary_ols_log.txt").write_text(str(m_log.summary()))

    # Aggregate coefficients
    coef_df = coefficients_summary({
        "ols_linear": m_ols,
        "wls": m_wls,
        "ols_log": m_log,
    })
    coef_df.to_csv(_OUTPUT_DIR / "coefficients_summary.csv", index=False)
    print(f"Wrote {_OUTPUT_DIR / 'coefficients_summary.csv'}")

    # Per-question
    print("Fitting per-question OLS...")
    per_q = fit_per_question_models(df)
    rows = []
    for q, m in per_q.items():
        ncp_a_coef = m.params.get("number_coded_prior_a", np.nan)
        ncp_a_p = m.pvalues.get("number_coded_prior_a", np.nan)
        ncp_b_coef = m.params.get("number_coded_prior_b", np.nan)
        ncp_b_p = m.pvalues.get("number_coded_prior_b", np.nan)
        rows.append({
            "question": q,
            "n_obs": int(m.nobs),
            "r2": float(m.rsquared),
            "r2_adj": float(m.rsquared_adj),
            "f_pvalue": float(m.f_pvalue),
            "ncp_a_coef": ncp_a_coef,
            "ncp_a_p": ncp_a_p,
            "ncp_b_coef": ncp_b_coef,
            "ncp_b_p": ncp_b_p,
        })
        (_OUTPUT_DIR / f"full_summary_per_q_{q}.txt").write_text(str(m.summary()))
    per_q_df = pd.DataFrame.from_records(rows)
    per_q_df.to_csv(_OUTPUT_DIR / "per_question_summary.csv", index=False)
    print(f"Wrote per-question results: {len(per_q_df)} questions")
    print(per_q_df.to_string(index=False))

    # Insights markdown
    insights = _build_insights_md(df, m_ols, m_wls, m_log, per_q_df, per_q)
    (_OUTPUT_DIR / "insights.md").write_text(insights)
    print(f"\nWrote {_OUTPUT_DIR / 'insights.md'}")


def _build_insights_md(df, m_ols, m_wls, m_log, per_q_df, per_q_models):
    lines = []
    lines.append("# IRR v2 — Regression Insights (volume FE removed)")
    lines.append("")
    lines.append(f"**Dataset:** `outputs/irr_dataset_v2_per_pair.csv` — {len(df)} rows, {df.volume.nunique()} volumes, "
                 f"{df.question.nunique()} questions, {df['coder_a'].nunique() + df['coder_b'].nunique()} coder slots.")
    lines.append("")
    lines.append(f"**Target:** `pct_agreement`. Mean = {df.pct_agreement.mean():.4f}, std = {df.pct_agreement.std():.4f}, "
                 f"min = {df.pct_agreement.min():.4f}, max = {df.pct_agreement.max():.4f}.")
    lines.append("")
    lines.append("## Model variants")
    lines.append("")
    lines.append("| Variant | R² | Adj R² | F p-value | Key coefficient: number_coded_prior_a |")
    lines.append("|---|---|---|---|---|")
    for name, m in [("OLS (linear NCP)", m_ols), ("WLS (weighted by N)", m_wls), ("OLS (log NCP)", m_log)]:
        ncp_a = m.params.get("number_coded_prior_a") or m.params.get("log_ncp_a")
        ncp_a_p = m.pvalues.get("number_coded_prior_a") or m.pvalues.get("log_ncp_a")
        f_p = m.f_pvalue if hasattr(m, "f_pvalue") else float("nan")
        lines.append(f"| {name} | {m.rsquared:.4f} | {m.rsquared_adj:.4f} | {f_p:.4g} | "
                     f"coef = {ncp_a:.5f}, p = {ncp_a_p:.4g} |")
    lines.append("")
    lines.append("## Per-question fits")
    lines.append("")
    lines.append("| Question | N | R² | F p-value | NCP_a coef | NCP_a p | NCP_b coef | NCP_b p |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for _, r in per_q_df.iterrows():
        lines.append(f"| {r.question} | {int(r.n_obs)} | {r.r2:.4f} | {r.f_pvalue:.4g} | "
                     f"{r.ncp_a_coef:.5f} | {r.ncp_a_p:.4g} | {r.ncp_b_coef:.5f} | {r.ncp_b_p:.4g} |")
    lines.append("")

    # Coder fixed-effects size — variance of coder dummy coefficients
    lines.append("## Coder effects (from OLS-linear)")
    lines.append("")
    coder_a_coefs = {k: v for k, v in m_ols.params.items() if k.startswith("C(coder_a)")}
    coder_b_coefs = {k: v for k, v in m_ols.params.items() if k.startswith("C(coder_b)")}
    lines.append("**Coder A dummies** (each is delta vs the reference coder):")
    for k, v in coder_a_coefs.items():
        p = m_ols.pvalues[k]
        sig = " *" if p < 0.05 else ""
        lines.append(f"- `{k}` = {v:+.4f} (p = {p:.3g}){sig}")
    lines.append("")
    lines.append("**Coder B dummies**:")
    for k, v in coder_b_coefs.items():
        p = m_ols.pvalues[k]
        sig = " *" if p < 0.05 else ""
        lines.append(f"- `{k}` = {v:+.4f} (p = {p:.3g}){sig}")
    lines.append("")

    # Volume FE removed in this model variant — note the design decision
    lines.append("## Volume effects")
    lines.append("")
    lines.append(
        "**Volume fixed effects have been removed from this model** to recover the "
        "cross-volume variance in `number_coded_prior` that was previously absorbed. "
        "Volume-level variation now flows into the residual + the experience and "
        "legacy-volume coefficients. To control for volume difficulty in this spec, "
        "use `n_overlap_orders` as a regression weight (see WLS variant) or add "
        "`is_legacy_volume` as a partial proxy."
    )
    lines.append("")

    # Number_coded_prior interpretation
    ncp_a = m_ols.params.get("number_coded_prior_a", 0)
    ncp_a_p = m_ols.pvalues.get("number_coded_prior_a", 1)
    ncp_b = m_ols.params.get("number_coded_prior_b", 0)
    ncp_b_p = m_ols.pvalues.get("number_coded_prior_b", 1)
    lines.append("## Experience effect (key research question)")
    lines.append("")
    sig_a = "significant" if ncp_a_p < 0.05 else "NOT significant"
    sig_b = "significant" if ncp_b_p < 0.05 else "NOT significant"
    direction_a = "positive" if ncp_a > 0 else "negative"
    direction_b = "positive" if ncp_b > 0 else "negative"
    lines.append(
        f"`number_coded_prior_a` coefficient = **{ncp_a:+.5f}** (p = {ncp_a_p:.4g}, **{sig_a}** at α=0.05).")
    lines.append(f"This is a **{direction_a}** effect: every additional volume coder_a had completed prior is associated "
                 f"with a {abs(ncp_a):.5f} change in `pct_agreement`.")
    lines.append("")
    lines.append(
        f"`number_coded_prior_b` coefficient = **{ncp_b:+.5f}** (p = {ncp_b_p:.4g}, **{sig_b}** at α=0.05).")
    lines.append(f"Direction: **{direction_b}**.")
    lines.append("")

    # Log-NCP variant for comparison
    log_a = m_log.params.get("log_ncp_a", 0)
    log_a_p = m_log.pvalues.get("log_ncp_a", 1)
    lines.append(f"In the log-experience variant, `log_ncp_a` coefficient = {log_a:+.5f} (p = {log_a_p:.4g}). "
                 f"If this fits notably better than linear (Adj R² goes up), there's diminishing returns to experience.")
    lines.append("")

    # is_legacy_volume
    leg = m_ols.params.get("is_legacy_volume", 0)
    leg_p = m_ols.pvalues.get("is_legacy_volume", 1)
    lines.append("## Legacy volumes (Vol ≤ 63)")
    lines.append("")
    lines.append(f"`is_legacy_volume` coefficient = {leg:+.5f} (p = {leg_p:.4g}). "
                 f"This may be unstable because volume fixed effects already absorb most volume-level variation; "
                 f"the legacy flag adds little orthogonal information unless many legacy volumes existed (we have 3: Vol 61, 62, 63).")
    lines.append("")

    # Caveats
    lines.append("## Caveats")
    lines.append("")
    lines.append("- **Multicollinearity**: volume fixed effects absorb most of `number_coded_prior` variance because "
                 "volume order is tightly correlated with experience. The remaining NCP signal is the cross-coder variation "
                 "in experience on the same volume.")
    lines.append("- **No chance correction**: `pct_agreement` is raw % agreement; high values on questions like Q1 "
                 "where one answer dominates can be misleading. The v3 build (Cohen's κ) is the next step.")
    lines.append("- **Asymmetric pair encoding**: `coder_a` is always alphabetically before `coder_b`, so `coder_a == Brian` only "
                 "happens for pairs where Brian is alphabetically first (he's first vs Bridget, Leah, Rachel — but Alia is "
                 "first vs Brian). The two coder dummies are NOT independent — they're paired with each other.")
    lines.append("- **Small samples**: some (volume, question, pair) cells have `n_overlap_orders < 5`. The WLS variant down-weights these.")
    lines.append("")

    lines.append("## Suggested next steps")
    lines.append("")
    lines.append("1. Re-run with Cohen's κ as the target (requires the v3 build that reads per-coder Q-answer cells).")
    lines.append("2. Try interaction terms: `coder_a × question`, `volume × question`.")
    lines.append("3. Mixed-effects model treating coder as a random effect (e.g., `Mixedlm`).")
    lines.append("4. Filter to `n_overlap_orders >= 30` and refit to see if the experience effect strengthens.")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
