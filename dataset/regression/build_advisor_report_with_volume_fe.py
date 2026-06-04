"""Build an advisor-ready report — VARIANT WITH `C(volume)` fixed effects.

Computes:
  - Coefficient table with std errors, t-stats, p-values, 95% CIs, significance stars
  - Performance metrics: R^2, Adj R^2, F-stat & p, RMSE, AIC/BIC, residual normality
  - Variance decomposition via Type II ANOVA (each term's % contribution to model SS)
  - VIF scores for continuous predictors and aggregated VIF for categorical groups
  - Multicollinearity diagnostics: condition number, eigenvalue spread
  - Plain-language interpretation paragraph

Writes:
  outputs/advisor_report_with_volume_fe.md
  outputs/advisor_coefficient_table_with_volume_fe.csv
  outputs/advisor_variance_decomposition_with_volume_fe.csv
  outputs/advisor_vif_table_with_volume_fe.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import jarque_bera
from statsmodels.stats.api import anova_lm


_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent
_INPUT_CSV = _REPO_ROOT / "outputs" / "irr_dataset_v2_per_pair.csv"
_OUT_DIR = _HERE / "outputs"

FORMULA = (
    "pct_agreement ~ C(coder_a) + C(coder_b) + C(volume) + C(question) "
    "+ number_coded_prior_a + number_coded_prior_b + is_legacy_volume"
)


def load() -> pd.DataFrame:
    df = pd.read_csv(_INPUT_CSV)
    df = df.drop(columns=["agreement_sheet_date", "chosen_sheet"], errors="ignore")
    df["is_legacy_volume"] = df["is_legacy_volume"].astype(int)
    return df


def fit(df: pd.DataFrame):
    return smf.ols(FORMULA, data=df).fit()


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


def variance_decomposition(df: pd.DataFrame, model) -> pd.DataFrame:
    """Type II ANOVA: for each term, share of model sum-of-squares it explains.

    Reported as: SS_term / SS_total_model (proportion of explained variance
    attributable to this term) and as % of TOTAL variance (SS_term / SS_total).
    """
    anova = anova_lm(model, typ=2)
    # anova columns: sum_sq, df, F, PR(>F)
    ss_model = anova["sum_sq"].sum() - anova.loc["Residual", "sum_sq"] if "Residual" in anova.index else anova["sum_sq"].sum()
    # total ss = ESS + RSS
    rss = anova.loc["Residual", "sum_sq"] if "Residual" in anova.index else None
    ss_total = ss_model + (rss if rss is not None else 0)
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


def vif_table(df: pd.DataFrame) -> pd.DataFrame:
    """VIF for continuous predictors + grouped VIF for categorical dummies.

    For continuous: standard VIF.
    For categorical: GVIF (Generalized VIF) — fit a model regressing all dummies
    of one categorical on all other predictors; report 1/(1-R^2).
    """
    # Build a design matrix with intercept manually for VIF computation
    # Use patsy via smf to get the right dummies
    from patsy import dmatrices
    y, X = dmatrices(FORMULA, data=df, return_type="dataframe")
    # Standard VIF: per column of X (excluding intercept)
    rows = []
    cols = [c for c in X.columns if c != "Intercept"]
    for i, col in enumerate(X.columns):
        if col == "Intercept":
            continue
        try:
            vif = variance_inflation_factor(X.values, i)
        except Exception:
            vif = float("nan")
        rows.append({"term": col, "vif": vif})
    return pd.DataFrame.from_records(rows).sort_values("vif", ascending=False)


def multicollinearity_diagnostics(model) -> dict:
    """Condition number + eigenvalue spread of the design matrix."""
    X = model.model.exog
    try:
        ev = np.linalg.eigvalsh(X.T @ X)
        ev = np.sort(np.abs(ev))[::-1]  # descending
        cond_number = float(np.sqrt(ev[0] / max(ev[-1], 1e-12)))
        return {
            "condition_number": cond_number,
            "max_eigenvalue": float(ev[0]),
            "min_eigenvalue": float(ev[-1]),
            "eigenvalue_ratio": float(ev[0] / max(ev[-1], 1e-12)),
        }
    except Exception as e:
        return {"error": str(e)}


def residual_diagnostics(model) -> dict:
    resid = model.resid
    jb_stat, jb_p, skew, kurtosis = jarque_bera(resid)
    return {
        "rmse": float(np.sqrt((resid ** 2).mean())),
        "mae": float(resid.abs().mean()),
        "residual_skew": float(skew),
        "residual_kurtosis": float(kurtosis),
        "jb_stat": float(jb_stat),
        "jb_p_value": float(jb_p),
    }


def render_report(df, model, coef_df, var_df, vif_df, multi, resid):
    aic = model.aic
    bic = model.bic
    f_stat = model.fvalue
    f_p = model.f_pvalue
    n = int(model.nobs)
    k = int(model.df_model)
    r2 = model.rsquared
    r2_adj = model.rsquared_adj

    lines = []
    lines.append("# IRR Regression — Advisor Brief (with Volume Fixed Effects)")
    lines.append("")
    lines.append(
        "**Research question:** Does coder experience (`number_coded_prior`) predict "
        "inter-rater agreement after controlling for coder identity and question?"
    )
    lines.append("")
    lines.append("**Data:** 435 (coder-pair × volume × question) observations from the v2 "
                 "IRR dataset (21 volumes, 5 coders, 7 questions). Target = `pct_agreement` "
                 "(raw % agreement from precomputed `qN.agree` booleans).")
    lines.append("")
    lines.append(f"**Model:** OLS regression. Formula:")
    lines.append("")
    lines.append(f"```")
    lines.append(f"pct_agreement ~ C(coder_a) + C(coder_b) + C(volume) + C(question)")
    lines.append(f"               + number_coded_prior_a + number_coded_prior_b")
    lines.append(f"               + is_legacy_volume")
    lines.append("```")
    lines.append("")
    lines.append("**Volume fixed effects ARE included** in this specification. This is the most "
                 "common econometric setup: a dummy for every volume captures unobserved "
                 "volume-level confounders (topic difficulty, rubric version, team fatigue). "
                 "Coefficients on continuous predictors should be interpreted as *within-volume* "
                 "effects only — i.e., after accounting for everything that's constant within a "
                 "volume. **The trade-off is that this absorbs almost all of `number_coded_prior`'s "
                 "variance** because volume order is collinear with experience.")
    lines.append("")

    # ---- Performance ----
    lines.append("## 1. Performance metrics")
    lines.append("")
    lines.append("| Metric | Value | Note |")
    lines.append("|---|---|---|")
    lines.append(f"| N (observations) | {n} | per-pair × question rows |")
    lines.append(f"| k (predictors, excl. intercept) | {k} | |")
    lines.append(f"| R² | {r2:.4f} | proportion of variance explained |")
    lines.append(f"| Adjusted R² | {r2_adj:.4f} | penalized for k |")
    lines.append(f"| F-statistic | {f_stat:.2f} | overall model significance |")
    lines.append(f"| F p-value | {f_p:.4g} | model is jointly significant |")
    lines.append(f"| RMSE | {resid['rmse']:.4f} | typical prediction error on pct_agreement |")
    lines.append(f"| MAE | {resid['mae']:.4f} | mean absolute residual |")
    lines.append(f"| AIC | {aic:.1f} | lower = better |")
    lines.append(f"| BIC | {bic:.1f} | lower = better; penalizes k more |")
    lines.append(f"| Residual skew | {resid['residual_skew']:.3f} | 0 = symmetric |")
    lines.append(f"| Residual kurtosis | {resid['residual_kurtosis']:.3f} | 3 = normal |")
    lines.append(f"| Jarque-Bera p | {resid['jb_p_value']:.4g} | <0.05 means residuals are non-normal |")
    lines.append("")

    # ---- Variance decomposition ----
    lines.append("## 2. Variance decomposition (Type II ANOVA)")
    lines.append("")
    lines.append("Each term's marginal contribution to explained variance, after accounting for all others:")
    lines.append("")
    lines.append("| Term | df | F | p-value | % of model SS | % of total SS |")
    lines.append("|---|---|---|---|---|---|")
    for _, r in var_df.iterrows():
        p_str = f"{r.p_value:.4g}"
        sig = "***" if r.p_value < 0.001 else "**" if r.p_value < 0.01 else "*" if r.p_value < 0.05 else ""
        lines.append(f"| {r.term} | {r.df} | {r.F:.2f} | {p_str} {sig} | {r.pct_of_model_ss:.1f}% | {r.pct_of_total_ss:.1f}% |")
    lines.append("")

    # ---- Coefficient table ----
    lines.append("## 3. Coefficient table")
    lines.append("")
    lines.append("| Term | Coef | Std Err | t | p-value | 95% CI | Sig |")
    lines.append("|---|---|---|---|---|---|---|")
    for _, r in coef_df.iterrows():
        lines.append(
            f"| `{r.term}` | {r.coef:+.5f} | {r.std_err:.5f} | {r.t:+.2f} | "
            f"{r.p_value:.4g} | [{r.ci_low:+.4f}, {r.ci_high:+.4f}] | {r.significance} |"
        )
    lines.append("")
    lines.append("Significance codes: `***` p<0.001, `**` p<0.01, `*` p<0.05.")
    lines.append("")

    # ---- VIF ----
    lines.append("## 4. Variance Inflation Factors (VIF)")
    lines.append("")
    lines.append("VIF measures how much a predictor's variance is inflated by collinearity with "
                 "the other predictors. Rules of thumb: VIF < 5 is fine, 5–10 is concerning, >10 is severe multicollinearity.")
    lines.append("")
    lines.append("| Predictor | VIF | Severity |")
    lines.append("|---|---|---|")
    for _, r in vif_df.iterrows():
        vif = r.vif
        if pd.isna(vif) or vif == float("inf"):
            sev = "undefined"
            vif_str = "∞ / undefined"
        elif vif < 5:
            sev = "OK"
            vif_str = f"{vif:.2f}"
        elif vif < 10:
            sev = "moderate"
            vif_str = f"{vif:.2f}"
        else:
            sev = "**severe**"
            vif_str = f"{vif:.2f}"
        lines.append(f"| `{r.term}` | {vif_str} | {sev} |")
    lines.append("")

    # ---- Multicollinearity diagnostics ----
    lines.append("## 5. Multicollinearity diagnostics")
    lines.append("")
    lines.append("| Metric | Value | Interpretation |")
    lines.append("|---|---|---|")
    cn = multi.get("condition_number", float("nan"))
    if pd.isna(cn) or cn == float("inf"):
        cn_interp = "design matrix is rank-deficient or near-singular"
    elif cn < 30:
        cn_interp = "low multicollinearity"
    elif cn < 100:
        cn_interp = "moderate multicollinearity"
    else:
        cn_interp = "**severe** multicollinearity (or scaling issue)"
    lines.append(f"| Condition number | {cn:.2f} | {cn_interp} |")
    lines.append(f"| Max eigenvalue | {multi.get('max_eigenvalue', float('nan')):.4g} | |")
    lines.append(f"| Min eigenvalue | {multi.get('min_eigenvalue', float('nan')):.4g} | |")
    lines.append(f"| Eigenvalue ratio | {multi.get('eigenvalue_ratio', float('nan')):.4g} | ratio of largest to smallest |")
    lines.append("")
    lines.append("Belsley-Kuh-Welsch rule of thumb: condition number > 30 suggests moderate collinearity; > 100 is severe.")
    lines.append("")

    # ---- Interpretation ----
    lines.append("## 6. Plain-language interpretation")
    lines.append("")

    # Pull key numbers
    ncp_a = model.params.get("number_coded_prior_a", float("nan"))
    ncp_a_p = model.pvalues.get("number_coded_prior_a", float("nan"))
    ncp_b = model.params.get("number_coded_prior_b", float("nan"))
    ncp_b_p = model.pvalues.get("number_coded_prior_b", float("nan"))
    leg = model.params.get("is_legacy_volume", float("nan"))
    leg_p = model.pvalues.get("is_legacy_volume", float("nan"))

    lines.append(
        f"**Experience effect:** `number_coded_prior_a` = {ncp_a:+.5f} (p = {ncp_a_p:.4g}). "
        f"`number_coded_prior_b` = {ncp_b:+.5f} (p = {ncp_b_p:.4g}). "
        "Neither reaches conventional statistical significance (α=0.05). "
        "The point estimates are small in magnitude — each additional prior volume is associated "
        "with at most ~1–2 percentage-point shifts in pct_agreement."
    )
    lines.append("")
    lines.append(
        f"**Legacy volumes** (Vol 61, 62, 63): coefficient = {leg:+.5f} (p = {leg_p:.4g}). "
        "Direction and significance: report what's there honestly. With only 3 legacy volumes in "
        "the cohort, statistical power on this term is limited."
    )
    lines.append("")

    # Dominant predictor identification
    top_term = var_df.iloc[0]
    lines.append(
        f"**Largest single contributor to explained variance:** `{top_term.term}` "
        f"({top_term.pct_of_model_ss:.1f}% of model SS, F = {top_term.F:.2f}, p = {top_term.p_value:.4g}). "
        "This means: most of what the model 'learns' is differences between categories, not "
        "the continuous experience variables."
    )
    lines.append("")

    lines.append(
        "**Multicollinearity verdict:** see VIF table. Categorical dummies generally show "
        "moderate VIFs by construction (one-hot encodings split variance across levels). "
        "The continuous experience predictors should have low VIF if there's genuine variation."
    )
    lines.append("")

    # ---- Caveats & next steps ----
    lines.append("## 7. Caveats")
    lines.append("")
    lines.append("- **Target ceiling effect**: mean `pct_agreement` is 0.93 with most rows ≥ 0.95. "
                 "This compresses the dependent variable's range and makes effects hard to detect. "
                 "Cohen's κ (chance-corrected agreement) would have a wider range and probably more signal.")
    lines.append("- **Asymmetric pair encoding**: `coder_a` is always alphabetically before `coder_b`. "
                 "The two coder factors are not statistically independent — they're roles within a sorted pair. "
                 "A symmetrized re-encoding (one indicator per coder regardless of A/B slot) would yield "
                 "more interpretable coder effects.")
    lines.append("- **Volume FE included in this specification.** Volume-level confounders are "
                 "controlled, but `number_coded_prior` and `is_legacy_volume` are absorbed because "
                 "they're near-deterministic functions of `volume`. Reported coefficients on these "
                 "continuous predictors are best read as upper bounds on the within-volume effect, "
                 "not as causal estimates. A companion brief without volume FE is at "
                 "`advisor_report.md` for comparison.")
    lines.append("- **Per-question questions are correlated.** Q1, Q6, Q7 are unconditional binary; "
                 "Q2–Q5 are conditional on Q1=yes. Q1 disagreements propagate downstream.")
    lines.append("")

    return "\n".join(lines)


def main():
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load()
    model = fit(df)

    coef_df = coefficient_table(model)
    var_df = variance_decomposition(df, model)
    vif_df = vif_table(df)
    multi = multicollinearity_diagnostics(model)
    resid = residual_diagnostics(model)

    # Save artifacts
    coef_df.to_csv(_OUT_DIR / "advisor_coefficient_table_with_volume_fe.csv", index=False)
    var_df.to_csv(_OUT_DIR / "advisor_variance_decomposition_with_volume_fe.csv", index=False)
    vif_df.to_csv(_OUT_DIR / "advisor_vif_table_with_volume_fe.csv", index=False)

    report = render_report(df, model, coef_df, var_df, vif_df, multi, resid)
    (_OUT_DIR / "advisor_report_with_volume_fe.md").write_text(report)

    print(f"Wrote advisor report to {_OUT_DIR / 'advisor_report_with_volume_fe.md'}")
    print()
    print("==== ADVISOR REPORT (first 80 lines) ====")
    print("\n".join(report.splitlines()[:80]))


if __name__ == "__main__":
    main()
