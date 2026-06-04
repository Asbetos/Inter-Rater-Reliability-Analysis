# IRR Regression — Advisor Brief

**Research question:** Does coder experience (`number_coded_prior`) predict inter-rater agreement after controlling for coder identity and question?

**Data:** 435 (coder-pair × volume × question) observations from the v2 IRR dataset (21 volumes, 5 coders, 7 questions). Target = `pct_agreement` (raw % agreement from precomputed `qN.agree` booleans).

**Model:** OLS regression. Formula:

```
pct_agreement ~ C(coder_a) + C(coder_b) + C(question)
               + number_coded_prior_a + number_coded_prior_b
               + is_legacy_volume
```

Volume fixed effects were intentionally OMITTED so that `number_coded_prior` (which moves in lockstep with volume order) retains identifiable variance.

## 1. Performance metrics

| Metric | Value | Note |
|---|---|---|
| N (observations) | 435 | per-pair × question rows |
| k (predictors, excl. intercept) | 15 | |
| R² | 0.1938 | proportion of variance explained |
| Adjusted R² | 0.1650 | penalized for k |
| F-statistic | 6.72 | overall model significance |
| F p-value | 4.892e-13 | model is jointly significant |
| RMSE | 0.1513 | typical prediction error on pct_agreement |
| MAE | 0.0761 | mean absolute residual |
| AIC | -376.6 | lower = better |
| BIC | -311.4 | lower = better; penalizes k more |
| Residual skew | -3.719 | 0 = symmetric |
| Residual kurtosis | 19.027 | 3 = normal |
| Jarque-Bera p | 0 | <0.05 means residuals are non-normal |

## 2. Variance decomposition (Type II ANOVA)

Each term's marginal contribution to explained variance, after accounting for all others:

| Term | df | F | p-value | % of model SS | % of total SS |
|---|---|---|---|---|---|
| C(question) | 6 | 8.01 | 3.402e-08 *** | 62.7% | 9.7% |
| C(coder_b) | 3 | 6.81 | 0.000173 *** | 26.7% | 4.1% |
| number_coded_prior_a | 1 | 2.98 | 0.08481  | 3.9% | 0.6% |
| is_legacy_volume | 1 | 2.24 | 0.1349  | 2.9% | 0.5% |
| number_coded_prior_b | 1 | 1.58 | 0.2102  | 2.1% | 0.3% |
| C(coder_a) | 3 | 0.45 | 0.7202  | 1.7% | 0.3% |

## 3. Coefficient table

| Term | Coef | Std Err | t | p-value | 95% CI | Sig |
|---|---|---|---|---|---|---|
| `Intercept` | +1.04697 | 0.06803 | +15.39 | 1.112e-42 | [+0.9132, +1.1807] | *** |
| `C(coder_a)[T.Brian]` | -0.05017 | 0.06725 | -0.75 | 0.4561 | [-0.1824, +0.0820] |  |
| `C(coder_a)[T.Bridget]` | +0.01929 | 0.03303 | +0.58 | 0.5596 | [-0.0456, +0.0842] |  |
| `C(coder_a)[T.Leah]` | -0.00666 | 0.03148 | -0.21 | 0.8326 | [-0.0685, +0.0552] |  |
| `C(coder_b)[T.Bridget]` | -0.16524 | 0.05682 | -2.91 | 0.003829 | [-0.2769, -0.0536] | ** |
| `C(coder_b)[T.Leah]` | -0.14218 | 0.04951 | -2.87 | 0.004292 | [-0.2395, -0.0449] | ** |
| `C(coder_b)[T.Rachel]` | -0.12541 | 0.07235 | -1.73 | 0.08379 | [-0.2676, +0.0168] |  |
| `C(question)[T.Q2]` | +0.08444 | 0.02704 | +3.12 | 0.001914 | [+0.0313, +0.1376] | ** |
| `C(question)[T.Q3]` | +0.08577 | 0.02704 | +3.17 | 0.001623 | [+0.0326, +0.1389] | ** |
| `C(question)[T.Q4]` | +0.08142 | 0.02704 | +3.01 | 0.002759 | [+0.0283, +0.1346] | ** |
| `C(question)[T.Q5]` | +0.08281 | 0.02704 | +3.06 | 0.002333 | [+0.0297, +0.1360] | ** |
| `C(question)[T.Q6]` | -0.01851 | 0.02704 | -0.68 | 0.4941 | [-0.0717, +0.0346] |  |
| `C(question)[T.Q7]` | -0.04637 | 0.03024 | -1.53 | 0.1259 | [-0.1058, +0.0131] |  |
| `number_coded_prior_a` | -0.01650 | 0.00955 | -1.73 | 0.08481 | [-0.0353, +0.0023] |  |
| `number_coded_prior_b` | +0.01155 | 0.00920 | +1.26 | 0.2102 | [-0.0065, +0.0296] |  |
| `is_legacy_volume` | +0.04718 | 0.03150 | +1.50 | 0.1349 | [-0.0147, +0.1091] |  |

Significance codes: `***` p<0.001, `**` p<0.01, `*` p<0.05.

## 4. Variance Inflation Factors (VIF)

VIF measures how much a predictor's variance is inflated by collinearity with the other predictors. Rules of thumb: VIF < 5 is fine, 5–10 is concerning, >10 is severe multicollinearity.

| Predictor | VIF | Severity |
|---|---|---|
| `number_coded_prior_a` | 56.32 | **severe** |
| `number_coded_prior_b` | 50.30 | **severe** |
| `C(coder_b)[T.Rachel]` | 23.90 | **severe** |
| `C(coder_a)[T.Brian]` | 13.70 | **severe** |
| `C(coder_b)[T.Bridget]` | 10.82 | **severe** |
| `C(coder_b)[T.Leah]` | 6.40 | moderate |
| `C(coder_a)[T.Leah]` | 1.85 | OK |
| `C(question)[T.Q2]` | 1.70 | OK |
| `C(question)[T.Q6]` | 1.70 | OK |
| `C(question)[T.Q3]` | 1.70 | OK |
| `C(question)[T.Q4]` | 1.70 | OK |
| `C(question)[T.Q5]` | 1.70 | OK |
| `C(question)[T.Q7]` | 1.55 | OK |
| `is_legacy_volume` | 1.38 | OK |
| `C(coder_a)[T.Bridget]` | 1.36 | OK |

## 5. Multicollinearity diagnostics

| Metric | Value | Interpretation |
|---|---|---|
| Condition number | 271.81 | **severe** multicollinearity (or scaling issue) |
| Max eigenvalue | 9.586e+04 | |
| Min eigenvalue | 1.297 | |
| Eigenvalue ratio | 7.388e+04 | ratio of largest to smallest |

Belsley-Kuh-Welsch rule of thumb: condition number > 30 suggests moderate collinearity; > 100 is severe.

## 6. Plain-language interpretation

**Experience effect:** `number_coded_prior_a` = -0.01650 (p = 0.08481). `number_coded_prior_b` = +0.01155 (p = 0.2102). Neither reaches conventional statistical significance (α=0.05). The point estimates are small in magnitude — each additional prior volume is associated with at most ~1–2 percentage-point shifts in pct_agreement.

**Legacy volumes** (Vol 61, 62, 63): coefficient = +0.04718 (p = 0.1349). Direction and significance: report what's there honestly. With only 3 legacy volumes in the cohort, statistical power on this term is limited.

**Largest single contributor to explained variance:** `C(question)` (62.7% of model SS, F = 8.01, p = 3.402e-08). This means: most of what the model 'learns' is differences between categories, not the continuous experience variables.

**Multicollinearity verdict:** see VIF table. Categorical dummies generally show moderate VIFs by construction (one-hot encodings split variance across levels). The continuous experience predictors should have low VIF if there's genuine variation.

## 7. Caveats

- **Target ceiling effect**: mean `pct_agreement` is 0.93 with most rows ≥ 0.95. This compresses the dependent variable's range and makes effects hard to detect. Cohen's κ (chance-corrected agreement) would have a wider range and probably more signal.
- **Asymmetric pair encoding**: `coder_a` is always alphabetically before `coder_b`. The two coder factors are not statistically independent — they're roles within a sorted pair. A symmetrized re-encoding (one indicator per coder regardless of A/B slot) would yield more interpretable coder effects.
- **Volume FE omitted by design** to recover experience-term identifiability. This means volume-specific difficulty (some volumes are inherently harder to agree on) is now in the residual rather than controlled.
- **Per-question questions are correlated.** Q1, Q6, Q7 are unconditional binary; Q2–Q5 are conditional on Q1=yes. Q1 disagreements propagate downstream.
