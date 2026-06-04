# IRR Regression — Advisor Brief (with Volume Fixed Effects)

**Research question:** Does coder experience (`number_coded_prior`) predict inter-rater agreement after controlling for coder identity and question?

**Data:** 435 (coder-pair × volume × question) observations from the v2 IRR dataset (21 volumes, 5 coders, 7 questions). Target = `pct_agreement` (raw % agreement from precomputed `qN.agree` booleans).

**Model:** OLS regression. Formula:

```
pct_agreement ~ C(coder_a) + C(coder_b) + C(volume) + C(question)
               + number_coded_prior_a + number_coded_prior_b
               + is_legacy_volume
```

**Volume fixed effects ARE included** in this specification. This is the most common econometric setup: a dummy for every volume captures unobserved volume-level confounders (topic difficulty, rubric version, team fatigue). Coefficients on continuous predictors should be interpreted as *within-volume* effects only — i.e., after accounting for everything that's constant within a volume. **The trade-off is that this absorbs almost all of `number_coded_prior`'s variance** because volume order is collinear with experience.

## 1. Performance metrics

| Metric | Value | Note |
|---|---|---|
| N (observations) | 435 | per-pair × question rows |
| k (predictors, excl. intercept) | 34 | |
| R² | 0.3805 | proportion of variance explained |
| Adjusted R² | 0.3279 | penalized for k |
| F-statistic | 7.23 | overall model significance |
| F p-value | 3.408e-25 | model is jointly significant |
| RMSE | 0.1326 | typical prediction error on pct_agreement |
| MAE | 0.0748 | mean absolute residual |
| AIC | -453.3 | lower = better |
| BIC | -310.6 | lower = better; penalizes k more |
| Residual skew | -2.595 | 0 = symmetric |
| Residual kurtosis | 14.003 | 3 = normal |
| Jarque-Bera p | 0 | <0.05 means residuals are non-normal |

## 2. Variance decomposition (Type II ANOVA)

Each term's marginal contribution to explained variance, after accounting for all others:

| Term | df | F | p-value | % of model SS | % of total SS |
|---|---|---|---|---|---|
| C(volume) | 20 | 6.17 | 2.073e-14 *** | 58.6% | 20.2% |
| C(question) | 6 | 9.28 | 1.569e-09 *** | 26.4% | 9.1% |
| C(coder_b) | 3 | 8.33 | 2.182e-05 *** | 11.9% | 4.1% |
| number_coded_prior_b | 1 | 3.27 | 0.07119  | 1.6% | 0.5% |
| is_legacy_volume | 1 | 1.66 | 0.198  | 0.8% | 0.3% |
| C(coder_a) | 3 | 0.47 | 0.6999  | 0.7% | 0.2% |
| number_coded_prior_a | 1 | 0.12 | 0.7296  | 0.1% | 0.0% |

## 3. Coefficient table

| Term | Coef | Std Err | t | p-value | 95% CI | Sig |
|---|---|---|---|---|---|---|
| `Intercept` | +0.70441 | 0.34211 | +2.06 | 0.04014 | [+0.0318, +1.3770] | * |
| `C(coder_a)[T.Brian]` | +0.11673 | 0.16064 | +0.73 | 0.4678 | [-0.1991, +0.4325] |  |
| `C(coder_a)[T.Bridget]` | -0.00117 | 0.03524 | -0.03 | 0.9736 | [-0.0704, +0.0681] |  |
| `C(coder_a)[T.Leah]` | +0.00242 | 0.05512 | +0.04 | 0.965 | [-0.1059, +0.1108] |  |
| `C(coder_b)[T.Bridget]` | -0.23647 | 0.07401 | -3.20 | 0.001507 | [-0.3820, -0.0910] | ** |
| `C(coder_b)[T.Leah]` | -0.18548 | 0.06283 | -2.95 | 0.003343 | [-0.3090, -0.0620] | ** |
| `C(coder_b)[T.Rachel]` | -0.21149 | 0.10007 | -2.11 | 0.03518 | [-0.4082, -0.0148] | * |
| `C(volume)[T.Volume 114]` | -0.24231 | 0.04882 | -4.96 | 1.026e-06 | [-0.3383, -0.1463] | *** |
| `C(volume)[T.Volume 119]` | -0.26183 | 0.07433 | -3.52 | 0.0004769 | [-0.4080, -0.1157] | *** |
| `C(volume)[T.Volume 120]` | +0.09940 | 0.16771 | +0.59 | 0.5537 | [-0.2303, +0.4291] |  |
| `C(volume)[T.Volume 122]` | +0.09559 | 0.16771 | +0.57 | 0.569 | [-0.2341, +0.4253] |  |
| `C(volume)[T.Volume 124]` | -0.05666 | 0.04946 | -1.15 | 0.2527 | [-0.1539, +0.0406] |  |
| `C(volume)[T.Volume 126]` | +0.05828 | 0.07453 | +0.78 | 0.4347 | [-0.0882, +0.2048] |  |
| `C(volume)[T.Volume 127]` | +0.08946 | 0.10680 | +0.84 | 0.4027 | [-0.1205, +0.2994] |  |
| `C(volume)[T.Volume 130]` | +0.15311 | 0.16907 | +0.91 | 0.3657 | [-0.1793, +0.4855] |  |
| `C(volume)[T.Volume 131]` | +0.24803 | 0.17654 | +1.40 | 0.1608 | [-0.0990, +0.5951] |  |
| `C(volume)[T.Volume 132]` | +0.26835 | 0.20719 | +1.30 | 0.196 | [-0.1390, +0.6757] |  |
| `C(volume)[T.Volume 133]` | +0.41539 | 0.35636 | +1.17 | 0.2444 | [-0.2852, +1.1160] |  |
| `C(volume)[T.Volume 134 - Part 2]` | +0.44477 | 0.37316 | +1.19 | 0.234 | [-0.2888, +1.1784] |  |
| `C(volume)[T.Volume 134 - Part I]` | +0.30146 | 0.27838 | +1.08 | 0.2795 | [-0.2458, +0.8487] |  |
| `C(volume)[T.Volume 61]` | +0.10893 | 0.10369 | +1.05 | 0.2941 | [-0.0949, +0.3128] |  |
| `C(volume)[T.Volume 62]` | +0.04728 | 0.03871 | +1.22 | 0.2226 | [-0.0288, +0.1234] |  |
| `C(volume)[T.Volume 63]` | +0.12268 | 0.10369 | +1.18 | 0.2375 | [-0.0812, +0.3265] |  |
| `C(volume)[T.Volume 91]` | -0.11792 | 0.13228 | -0.89 | 0.3732 | [-0.3780, +0.1421] |  |
| `C(volume)[T.Volume 93]` | -0.10844 | 0.10306 | -1.05 | 0.2933 | [-0.3111, +0.0942] |  |
| `C(volume)[T.Volume 94]` | -0.16007 | 0.16370 | -0.98 | 0.3287 | [-0.4819, +0.1617] |  |
| `C(volume)[T.Volume 95]` | -0.16322 | 0.19420 | -0.84 | 0.4012 | [-0.5450, +0.2186] |  |
| `C(question)[T.Q2]` | +0.08444 | 0.02426 | +3.48 | 0.0005543 | [+0.0368, +0.1321] | *** |
| `C(question)[T.Q3]` | +0.08577 | 0.02426 | +3.54 | 0.0004536 | [+0.0381, +0.1335] | *** |
| `C(question)[T.Q4]` | +0.08142 | 0.02426 | +3.36 | 0.0008651 | [+0.0337, +0.1291] | *** |
| `C(question)[T.Q5]` | +0.08281 | 0.02426 | +3.41 | 0.0007054 | [+0.0351, +0.1305] | *** |
| `C(question)[T.Q6]` | -0.01851 | 0.02426 | -0.76 | 0.446 | [-0.0662, +0.0292] |  |
| `C(question)[T.Q7]` | -0.03630 | 0.02722 | -1.33 | 0.1831 | [-0.0898, +0.0172] |  |
| `number_coded_prior_a` | +0.00887 | 0.02565 | +0.35 | 0.7296 | [-0.0415, +0.0593] |  |
| `number_coded_prior_b` | +0.02312 | 0.01278 | +1.81 | 0.07119 | [-0.0020, +0.0482] |  |
| `is_legacy_volume` | +0.27889 | 0.21627 | +1.29 | 0.198 | [-0.1463, +0.7041] |  |

Significance codes: `***` p<0.001, `**` p<0.01, `*` p<0.05.

## 4. Variance Inflation Factors (VIF)

VIF measures how much a predictor's variance is inflated by collinearity with the other predictors. Rules of thumb: VIF < 5 is fine, 5–10 is concerning, >10 is severe multicollinearity.

| Predictor | VIF | Severity |
|---|---|---|
| `C(volume)[T.Volume 62]` | ∞ / undefined | undefined |
| `C(volume)[T.Volume 63]` | ∞ / undefined | undefined |
| `is_legacy_volume` | ∞ / undefined | undefined |
| `C(volume)[T.Volume 61]` | ∞ / undefined | undefined |
| `number_coded_prior_a` | 504.48 | **severe** |
| `C(volume)[T.Volume 134 - Part 2]` | 240.45 | **severe** |
| `number_coded_prior_b` | 120.58 | **severe** |
| `C(volume)[T.Volume 133]` | 114.59 | **severe** |
| `C(coder_a)[T.Brian]` | 97.11 | **severe** |
| `C(coder_b)[T.Rachel]` | 56.79 | **severe** |
| `C(volume)[T.Volume 95]` | 51.67 | **severe** |
| `C(volume)[T.Volume 94]` | 36.71 | **severe** |
| `C(volume)[T.Volume 130]` | 29.87 | **severe** |
| `C(volume)[T.Volume 132]` | 26.20 | **severe** |
| `C(volume)[T.Volume 134 - Part I]` | 23.98 | **severe** |
| `C(volume)[T.Volume 91]` | 23.97 | **severe** |
| `C(coder_b)[T.Bridget]` | 22.81 | **severe** |
| `C(volume)[T.Volume 131]` | 19.02 | **severe** |
| `C(volume)[T.Volume 127]` | 15.63 | **severe** |
| `C(volume)[T.Volume 93]` | 14.55 | **severe** |
| `C(coder_b)[T.Leah]` | 12.81 | **severe** |
| `C(volume)[T.Volume 122]` | 10.13 | **severe** |
| `C(volume)[T.Volume 120]` | 10.13 | **severe** |
| `C(volume)[T.Volume 126]` | 7.61 | moderate |
| `C(volume)[T.Volume 119]` | 7.57 | moderate |
| `C(coder_a)[T.Leah]` | 7.03 | moderate |
| `C(volume)[T.Volume 124]` | 3.35 | OK |
| `C(volume)[T.Volume 114]` | 3.26 | OK |
| `C(coder_a)[T.Bridget]` | 1.92 | OK |
| `C(question)[T.Q2]` | 1.70 | OK |
| `C(question)[T.Q3]` | 1.70 | OK |
| `C(question)[T.Q6]` | 1.70 | OK |
| `C(question)[T.Q5]` | 1.70 | OK |
| `C(question)[T.Q4]` | 1.70 | OK |
| `C(question)[T.Q7]` | 1.56 | OK |

## 5. Multicollinearity diagnostics

| Metric | Value | Interpretation |
|---|---|---|
| Condition number | 309650056.30 | **severe** multicollinearity (or scaling issue) |
| Max eigenvalue | 9.588e+04 | |
| Min eigenvalue | 9.069e-13 | |
| Eigenvalue ratio | 9.588e+16 | ratio of largest to smallest |

Belsley-Kuh-Welsch rule of thumb: condition number > 30 suggests moderate collinearity; > 100 is severe.

## 6. Plain-language interpretation

**Experience effect:** `number_coded_prior_a` = +0.00887 (p = 0.7296). `number_coded_prior_b` = +0.02312 (p = 0.07119). Neither reaches conventional statistical significance (α=0.05). The point estimates are small in magnitude — each additional prior volume is associated with at most ~1–2 percentage-point shifts in pct_agreement.

**Legacy volumes** (Vol 61, 62, 63): coefficient = +0.27889 (p = 0.198). Direction and significance: report what's there honestly. With only 3 legacy volumes in the cohort, statistical power on this term is limited.

**Largest single contributor to explained variance:** `C(volume)` (58.6% of model SS, F = 6.17, p = 2.073e-14). This means: most of what the model 'learns' is differences between categories, not the continuous experience variables.

**Multicollinearity verdict:** see VIF table. Categorical dummies generally show moderate VIFs by construction (one-hot encodings split variance across levels). The continuous experience predictors should have low VIF if there's genuine variation.

## 7. Caveats

- **Target ceiling effect**: mean `pct_agreement` is 0.93 with most rows ≥ 0.95. This compresses the dependent variable's range and makes effects hard to detect. Cohen's κ (chance-corrected agreement) would have a wider range and probably more signal.
- **Asymmetric pair encoding**: `coder_a` is always alphabetically before `coder_b`. The two coder factors are not statistically independent — they're roles within a sorted pair. A symmetrized re-encoding (one indicator per coder regardless of A/B slot) would yield more interpretable coder effects.
- **Volume FE included in this specification.** Volume-level confounders are controlled, but `number_coded_prior` and `is_legacy_volume` are absorbed because they're near-deterministic functions of `volume`. Reported coefficients on these continuous predictors are best read as upper bounds on the within-volume effect, not as causal estimates. A companion brief without volume FE is at `advisor_report.md` for comparison.
- **Per-question questions are correlated.** Q1, Q6, Q7 are unconditional binary; Q2–Q5 are conditional on Q1=yes. Q1 disagreements propagate downstream.
