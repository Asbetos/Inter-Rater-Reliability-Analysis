"""Per-question OLS regression of inter-rater agreement on coder and volume features.

Simple, readable version for an academic review. One file, one pass, no extra
abstractions. Reads outputs/irr_dataset_v2_per_pair.csv and writes one CSV of
coefficients per question to outputs/per_q_<Q>/coefficients.csv, plus the
statsmodels textual summary to outputs/per_q_<Q>/summary.txt.

Run:
    python per_question_model.py

Model spec (per question Q in Q1..Q7):

    pct_agreement_q = sum_c (alpha_c * is_coder_c)
                    + sum_c (beta_c  * ncp_coder_c)
                    + sum_v (gamma_v * is_volume_v)
                    + error

where:
  - pct_agreement_q is the per-pair raw % agreement on question Q
    (computed upstream as (n_overlap - n_disagreements) / n_overlap from the
    qN.agree boolean column of the chosen agreement sheet).
  - is_coder_c is 1 if coder c is in the pair, else 0. Each row has exactly two.
  - ncp_coder_c is c's count of prior volumes coded if c is in the pair, else 0.
  - is_volume_v is the standard volume dummy (Volume 95 is the dropped
    reference; its mean folds into the null space).
  - NO intercept. The 5 coder dummies sum to a constant (2), which spans the
    implicit baseline direction, so an intercept would be redundant.

The model is fit independently for each question on the rows of the per-pair
dataset where question == Q (~60-65 rows per Q; ~45 for Q7).
"""

from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
INPUT_CSV = HERE.parent.parent / "outputs" / "irr_dataset_v2_per_pair.csv"
OUTPUT_DIR = HERE / "outputs"

CODERS = ["Alia", "Brian", "Bridget", "Leah", "Rachel"]
QUESTIONS = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"]
VOLUME_REFERENCE = "Volume 95"   # dropped from the design matrix as the reference


# ---------------------------------------------------------------------------
# Step 1: load and reshape
# ---------------------------------------------------------------------------

def load_dataset() -> pd.DataFrame:
    """Read the per-pair CSV and add one-hot / per-coder feature columns.

    Returns a wide dataframe with:
      - target:      pct_agreement
      - metadata:    volume, question, n_overlap_orders   (not used as predictors)
      - coder dummies:  is_<coder>           (one column per coder)
      - coder NCP:      ncp_<coder>          (one column per coder)
      - volume dummies: is_volume_<volume>   (one column per volume)
    """
    df = pd.read_csv(INPUT_CSV)

    # Drop columns we will not use anywhere (target is pct_agreement; the
    # original number_coded_prior_a/_b are replaced by per-coder columns below).
    df = df.drop(columns=[
        "is_legacy_volume", "agreement_sheet_date", "chosen_sheet",
        "n_disagreements",
    ], errors="ignore")

    # ---- Per-coder dummies and per-coder NCP -----------------------------
    # Each row's pair is (coder_a, coder_b). For each coder we create:
    #   is_<coder>  = 1 if that coder is in the pair, else 0
    #   ncp_<coder> = that coder's number_coded_prior if in the pair, else 0
    for coder in CODERS:
        in_pair_as_a = df["coder_a"] == coder
        in_pair_as_b = df["coder_b"] == coder
        df[f"is_{coder}"] = (in_pair_as_a | in_pair_as_b).astype(int)
        df[f"ncp_{coder}"] = (
            in_pair_as_a * df["number_coded_prior_a"]
            + in_pair_as_b * df["number_coded_prior_b"]
        ).astype(int)

    # ---- Volume dummies --------------------------------------------------
    # One column per volume, except the reference (Volume 95) which is
    # dropped so the coefficients are read as "volume X vs Volume 95".
    volumes = sorted(df["volume"].unique())
    for v in volumes:
        if v == VOLUME_REFERENCE:
            continue   # skip: this becomes the reference category
        df[f"is_volume_{v}"] = (df["volume"] == v).astype(int)

    # Drop columns now subsumed by the new features
    df = df.drop(columns=[
        "coder_a", "coder_b", "number_coded_prior_a", "number_coded_prior_b",
    ])

    return df


# ---------------------------------------------------------------------------
# Step 2: fit one OLS per question
# ---------------------------------------------------------------------------

def fit_question(df: pd.DataFrame, q: str):
    """Filter the dataset to question q and fit an OLS with no intercept.

    The formula is built dynamically because volume column names contain
    spaces; we use the `data=` dataframe and patsy-quoted (`Q()`) names.
    """
    rows = df[df["question"] == q].copy()
    if rows.empty:
        return None

    # Build the list of predictors:
    #   5 coder indicators + 5 per-coder NCP + (n_volumes - 1) volume dummies
    coder_terms = [f"is_{c}" for c in CODERS]
    ncp_terms = [f"ncp_{c}" for c in CODERS]
    volume_terms = [c for c in rows.columns if c.startswith("is_volume_")]

    # Use Q("...") to quote column names that contain spaces (e.g. "is_volume_Volume 134 - Part 2").
    predictor_terms = (
        coder_terms
        + ncp_terms
        + [f'Q("{c}")' for c in volume_terms]
    )

    # "~ 0 + ..." suppresses the intercept; pct_agreement on the left.
    formula = "pct_agreement ~ 0 + " + " + ".join(predictor_terms)
    return smf.ols(formula, data=rows).fit()


# ---------------------------------------------------------------------------
# Step 3: write the per-question outputs
# ---------------------------------------------------------------------------

def write_outputs(q: str, model) -> None:
    """Save a tidy coefficient CSV + the full statsmodels summary as text."""
    out_dir = OUTPUT_DIR / f"per_q_{q}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Tidy coefficient table — what an advisor would read in Excel.
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
    # Significance flag for quick scanning.
    coef_df["significant_at_0.05"] = coef_df["p_value"] < 0.05
    coef_df.to_csv(out_dir / "coefficients.csv", index=False)

    # Full statsmodels summary for reproducibility.
    (out_dir / "summary.txt").write_text(str(model.summary()))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_dataset()
    print(f"Loaded {len(df)} rows from {INPUT_CSV.name}")
    print(f"Coders: {CODERS}")
    print(f"Volumes: {df['volume'].nunique()} (reference = {VOLUME_REFERENCE!r})")
    print(f"Questions: {QUESTIONS}")
    print()

    print(f"{'Q':<4} {'N':>5} {'R^2':>8} {'Adj R^2':>9} {'F p-value':>14}")
    print("-" * 45)
    for q in QUESTIONS:
        model = fit_question(df, q)
        if model is None:
            print(f"{q:<4}  no rows")
            continue
        write_outputs(q, model)
        print(
            f"{q:<4} {int(model.nobs):>5} {model.rsquared:>8.4f} "
            f"{model.rsquared_adj:>9.4f} {model.f_pvalue:>14.4g}"
        )

    print()
    print(f"Per-question coefficient tables written to {OUTPUT_DIR}/per_q_<Q>/coefficients.csv")
    print(f"Full statsmodels summaries written to {OUTPUT_DIR}/per_q_<Q>/summary.txt")


if __name__ == "__main__":
    main()
