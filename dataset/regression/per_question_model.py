"""Per-question OLS regression of inter-rater agreement on coder and volume features.

Run:
    python per_question_model.py

Reads a pre-built, one-hot encoded per-pair dataset
(`outputs/irr_dataset_v2_per_pair_onehot.csv`) and fits one OLS regression
per question (Q1..Q7), saving the coefficient table and statsmodels summary
for each.

Model spec (per question Q in Q1..Q7):

    pct_agreement_q = sum_c (alpha_c * is_<c>)
                    + sum_c (beta_c  * ncp_<c>)
                    + sum_v (gamma_v * vol_<v>)
                    + error

where:
  - pct_agreement_q is the per-pair raw % agreement on question Q (computed
    upstream as (n_overlap - n_disagreements) / n_overlap from the qN.agree
    boolean column of the chosen agreement sheet).
  - is_<c> is 1 if coder c is in the pair, else 0. Each row has exactly two.
  - ncp_<c> is c's count of prior volumes coded if c is in the pair, else 0.
  - vol_<v> is the standard volume one-hot. Volume 95 (`vol_95`) is dropped
    from the design matrix to serve as the reference category, so the
    remaining vol_<v> coefficients are read as "volume v vs Volume 95."
  - NO intercept. The 5 coder dummies sum to a constant (2) per row, which
    spans the implicit baseline direction; an intercept would be redundant.
"""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
INPUT_CSV = HERE / "outputs" / "irr_dataset_v2_per_pair_onehot.csv"
OUTPUT_DIR = HERE / "outputs"

CODERS = ["Alia", "Brian", "Bridget", "Leah", "Rachel"]
QUESTIONS = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"]
VOLUME_REFERENCE_COL = "vol_95"   # dropped from the design -> reference category


# ---------------------------------------------------------------------------
# Step 1: fit one OLS per question
# ---------------------------------------------------------------------------

def fit_question(df: pd.DataFrame, q: str):
    """Filter the dataset to question q and fit an OLS with no intercept.

    Predictors:
      - 5 coder indicators:   is_Alia, is_Brian, is_Bridget, is_Leah, is_Rachel
      - 5 per-coder NCP:      ncp_Alia, ncp_Brian, ncp_Bridget, ncp_Leah, ncp_Rachel
      - 20 volume one-hots:   every vol_<v> column EXCEPT VOLUME_REFERENCE_COL
    """
    # Keep only rows for this question.
    rows = df[df[f"q_{q}"] == 1].copy()
    if rows.empty:
        return None

    # Build the predictor list. Column names in the one-hot CSV use lowercase
    # coder names (e.g. is_alia, ncp_alia).
    coder_terms = [f"is_{c.lower()}" for c in CODERS]
    ncp_terms = [f"ncp_{c.lower()}" for c in CODERS]
    volume_terms = [
        c for c in rows.columns
        if c.startswith("vol_") and c != VOLUME_REFERENCE_COL
    ]
    predictors = coder_terms + ncp_terms + volume_terms

    # "~ 0 + ..." suppresses the intercept; target on the left.
    formula = "pct_agreement ~ 0 + " + " + ".join(predictors)
    return smf.ols(formula, data=rows).fit()


# ---------------------------------------------------------------------------
# Step 2: save per-question outputs
# ---------------------------------------------------------------------------

def save_outputs(q: str, model) -> None:
    """Write a tidy coefficient CSV + the full statsmodels summary as text."""
    out_dir = OUTPUT_DIR / f"per_q_{q}"
    out_dir.mkdir(parents=True, exist_ok=True)

    ci = model.conf_int(alpha=0.05)
    coef_df = pd.DataFrame({
        "term": model.params.index,
        "coef": model.params.values,
        "std_err": model.bse.values,
        "t": model.tvalues.values,
        "p_value": model.pvalues.values,
        "ci_low": ci[0].values,
        "ci_high": ci[1].values,
    })
    coef_df["significant_at_0.05"] = coef_df["p_value"] < 0.05
    coef_df.to_csv(out_dir / "coefficients.csv", index=False)

    (out_dir / "summary.txt").write_text(str(model.summary()))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns from {INPUT_CSV.name}")
    print(f"Coders: {CODERS}")
    print(f"Questions: {QUESTIONS}")
    print(f"Volume reference (dropped from design): {VOLUME_REFERENCE_COL!r}")
    print()

    print(f"{'Q':<4} {'N':>5} {'R^2':>8} {'Adj R^2':>9} {'F p-value':>14}")
    print("-" * 45)
    for q in QUESTIONS:
        model = fit_question(df, q)
        if model is None:
            print(f"{q:<4}  no rows")
            continue
        save_outputs(q, model)
        print(
            f"{q:<4} {int(model.nobs):>5} {model.rsquared:>8.4f} "
            f"{model.rsquared_adj:>9.4f} {model.f_pvalue:>14.4g}"
        )

    print()
    print(f"Per-question coefficient tables: {OUTPUT_DIR}/per_q_<Q>/coefficients.csv")
    print(f"Full statsmodels summaries:      {OUTPUT_DIR}/per_q_<Q>/summary.txt")


if __name__ == "__main__":
    main()
