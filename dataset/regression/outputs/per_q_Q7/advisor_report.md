# IRR Per-Question Regression — Q7

**Research question:** Within this single question, do per-coder agreement levels and per-coder coding experience (`number_coded_prior`) predict inter-rater agreement, after controlling for volume?

**Subsample:** N = 45 (coder-pair × volume) rows where `question == Q7`. Volumes represented: 13 of 21. Mean `pct_agreement` = 0.8301 (min 0.000, max 0.980).

**Model design:**

```
pct_agreement ~ 0 + is_<coder>(x5) + ncp_<coder>(x5) + vol_<id>(x20)
```

- **No intercept** (`~ 0 + ...`): the 5 coder dummies are all included; each row has exactly two of them set to 1, so they collectively span the implicit baseline.
- **Reference volume:** `vol_95` is dropped, so all `vol_*` coefficients are differences vs. Vol 95.
- **Target:** `pct_agreement` (raw % agreement from precomputed `qN.agree` booleans).
- **n_overlap_orders / n_disagreements / volume / question:** retained as metadata only — NOT regressors.

> **Note on R²:** This is a no-intercept model, but the 5 coder dummies sum to a constant (= 2) per row, so statsmodels detects an implicit constant in the design and reports the **centered R²** (the familiar variance-explained interpretation). Treat it as comparable to ordinary OLS R², not as the uncentered no-intercept R².

## 1. Performance metrics

| Metric | Value | Note |
|---|---|---|
| N (observations) | 45 | filtered to question Q7 |
| k (predictors) | 20 | no intercept |
| Residual df | 24 | OK |
| R² | 0.6499 | centered R² (implicit-constant design) |
| Adjusted R² | 0.3581 | k-penalized variant |
| F-statistic | 2.23 | joint significance of all predictors |
| F p-value | 0.03141 | |
| RMSE | 0.1632 | typical residual on pct_agreement |
| MAE | 0.1153 | mean absolute residual |
| AIC | 6.6 | |
| BIC | 44.5 | |
| Condition number | 83930614.58 | >30 = moderate collinearity; >100 = severe |

## 2. Variance decomposition (Type II ANOVA)

| Term | df | F | p-value | % of model SS | % of total SS |
|---|---|---|---|---|---|
| `is_brian` | 1 | 15.90 | 0.000544 *** | 26.1% | 18.7% |
| `vol_119` | 1 | 5.84 | 0.02361 * | 9.6% | 6.9% |
| `vol_114` | 1 | 5.17 | 0.03224 * | 8.5% | 6.1% |
| `vol_127` | 1 | 4.98 | 0.03525 * | 8.2% | 5.9% |
| `vol_126` | 1 | 4.22 | 0.05101  | 6.9% | 5.0% |
| `vol_132` | 1 | 4.04 | 0.05578  | 6.6% | 4.8% |
| `vol_131` | 1 | 4.04 | 0.05578  | 6.6% | 4.8% |
| `vol_133` | 1 | 4.04 | 0.05578  | 6.6% | 4.8% |
| `vol_130` | 1 | 2.49 | 0.1274  | 4.1% | 2.9% |
| `ncp_alia` | 1 | 2.22 | 0.1496  | 3.6% | 2.6% |
| `ncp_bridget` | 1 | 2.21 | 0.1502  | 3.6% | 2.6% |
| `is_rachel` | 1 | 1.84 | 0.1872  | 3.0% | 2.2% |
| `vol_109` | 1 | 1.56 | 0.2244  | 2.6% | 1.8% |
| `ncp_leah` | 1 | 1.02 | 0.3218  | 1.7% | 1.2% |
| `is_bridget` | 1 | 0.47 | 0.5006  | 0.8% | 0.6% |
| `vol_93` | 1 | 0.29 | 0.5978  | 0.5% | 0.3% |
| `vol_91` | 1 | 0.17 | 0.6842  | 0.3% | 0.2% |
| `ncp_rachel` | 1 | 0.13 | 0.7259  | 0.2% | 0.1% |
| `is_alia` | 1 | 0.08 | 0.7822  | 0.1% | 0.1% |
| `vol_94` | 1 | 0.04 | 0.8386  | 0.1% | 0.1% |
| `is_leah` | 1 | 0.03 | 0.8678  | 0.0% | 0.0% |
| `vol_122` | 1 | 0.02 | 0.898  | 0.0% | 0.0% |
| `ncp_brian` | 1 | 0.01 | 0.9118  | 0.0% | 0.0% |
| `vol_124` | 1 | 0.00 | 0.9533  | 0.0% | 0.0% |
| `vol_120` | 1 | 0.00 | 0.9958  | 0.0% | 0.0% |
| `vol_134_part_2` | 1 | nan | nan  | nan% | nan% |
| `vol_134_part_i` | 1 | nan | nan  | nan% | nan% |
| `vol_61` | 1 | nan | nan  | nan% | nan% |
| `vol_62` | 1 | nan | nan  | nan% | nan% |
| `vol_63` | 1 | nan | nan  | nan% | nan% |

## 3. Coefficient table

| Term | Coef | Std Err | t | p-value | 95% CI | Sig |
|---|---|---|---|---|---|---|
| `is_alia` | -0.07782 | 0.27831 | -0.28 | 0.7822 | [-0.6522, +0.4966] |  |
| `is_brian` | +0.54718 | 0.13723 | +3.99 | 0.000544 | [+0.2640, +0.8304] | *** |
| `is_bridget` | -0.20297 | 0.29679 | -0.68 | 0.5006 | [-0.8155, +0.4096] |  |
| `is_leah` | +0.04626 | 0.27485 | +0.17 | 0.8678 | [-0.5210, +0.6135] |  |
| `is_rachel` | +0.37025 | 0.27269 | +1.36 | 0.1872 | [-0.1926, +0.9331] |  |
| `ncp_alia` | +0.03093 | 0.02078 | +1.49 | 0.1496 | [-0.0120, +0.0738] |  |
| `ncp_brian` | -0.00214 | 0.01910 | -0.11 | 0.9118 | [-0.0416, +0.0373] |  |
| `ncp_bridget` | +0.03741 | 0.02517 | +1.49 | 0.1502 | [-0.0145, +0.0894] |  |
| `ncp_leah` | +0.02559 | 0.02530 | +1.01 | 0.3218 | [-0.0266, +0.0778] |  |
| `ncp_rachel` | +0.00705 | 0.01987 | +0.35 | 0.7259 | [-0.0340, +0.0481] |  |
| `vol_109` | +0.15845 | 0.12705 | +1.25 | 0.2244 | [-0.1038, +0.4207] |  |
| `vol_114` | -0.29594 | 0.13017 | -2.27 | 0.03224 | [-0.5646, -0.0273] | * |
| `vol_119` | -0.33300 | 0.13777 | -2.42 | 0.02361 | [-0.6173, -0.0487] | * |
| `vol_120` | +0.00125 | 0.23479 | +0.01 | 0.9958 | [-0.4833, +0.4858] |  |
| `vol_122` | -0.03042 | 0.23479 | -0.13 | 0.898 | [-0.5150, +0.4542] |  |
| `vol_124` | +0.00751 | 0.12698 | +0.06 | 0.9533 | [-0.2546, +0.2696] |  |
| `vol_126` | +0.25393 | 0.12362 | +2.05 | 0.05101 | [-0.0012, +0.5091] |  |
| `vol_127` | +0.25657 | 0.11497 | +2.23 | 0.03525 | [+0.0193, +0.4939] | * |
| `vol_130` | +0.20687 | 0.13100 | +1.58 | 0.1274 | [-0.0635, +0.4772] |  |
| `vol_131` | +0.00000 | 0.00000 | +2.01 | 0.05578 | [-0.0000, +0.0000] |  |
| `vol_132` | +0.00000 | 0.00000 | +2.01 | 0.05578 | [-0.0000, +0.0000] |  |
| `vol_133` | -0.00000 | 0.00000 | -2.01 | 0.05578 | [-0.0000, +0.0000] |  |
| `vol_134_part_2` | +0.00000 | 0.00000 | +nan | nan | [+0.0000, +0.0000] |  |
| `vol_134_part_i` | +0.00000 | 0.00000 | +nan | nan | [+0.0000, +0.0000] |  |
| `vol_61` | +0.00000 | 0.00000 | +nan | nan | [+0.0000, +0.0000] |  |
| `vol_62` | +0.00000 | 0.00000 | +nan | nan | [+0.0000, +0.0000] |  |
| `vol_63` | +0.00000 | 0.00000 | +nan | nan | [+0.0000, +0.0000] |  |
| `vol_91` | +0.05929 | 0.14401 | +0.41 | 0.6842 | [-0.2379, +0.3565] |  |
| `vol_93` | +0.08074 | 0.15103 | +0.53 | 0.5978 | [-0.2310, +0.3925] |  |
| `vol_94` | +0.03284 | 0.15947 | +0.21 | 0.8386 | [-0.2963, +0.3620] |  |

Significance codes: `***` p<0.001, `**` p<0.01, `*` p<0.05.

## 4. Variance Inflation Factors (VIF)

VIF measured on the no-intercept design matrix. Note: in no-intercept models, absolute VIF values are less straightforward to interpret than in standard intercept models — treat large values as a flag for relative collinearity rather than absolute severity.

| Predictor | VIF | Severity |
|---|---|---|
| `is_alia` | infinite / undefined | infinite / undefined |
| `ncp_alia` | infinite / undefined | infinite / undefined |
| `is_brian` | infinite / undefined | infinite / undefined |
| `ncp_brian` | infinite / undefined | infinite / undefined |
| `is_bridget` | infinite / undefined | infinite / undefined |
| `ncp_bridget` | infinite / undefined | infinite / undefined |
| `is_leah` | infinite / undefined | infinite / undefined |
| `ncp_leah` | infinite / undefined | infinite / undefined |
| `is_rachel` | infinite / undefined | infinite / undefined |
| `ncp_rachel` | infinite / undefined | infinite / undefined |
| `vol_109` | infinite / undefined | infinite / undefined |
| `vol_114` | infinite / undefined | infinite / undefined |
| `vol_119` | infinite / undefined | infinite / undefined |
| `vol_120` | infinite / undefined | infinite / undefined |
| `vol_122` | infinite / undefined | infinite / undefined |
| `vol_124` | infinite / undefined | infinite / undefined |
| `vol_126` | infinite / undefined | infinite / undefined |
| `vol_127` | infinite / undefined | infinite / undefined |
| `vol_130` | infinite / undefined | infinite / undefined |
| `vol_91` | infinite / undefined | infinite / undefined |
| `vol_93` | infinite / undefined | infinite / undefined |
| `vol_94` | infinite / undefined | infinite / undefined |
| `vol_131` | infinite / undefined | infinite / undefined |
| `vol_132` | infinite / undefined | infinite / undefined |
| `vol_133` | infinite / undefined | infinite / undefined |
| `vol_134_part_2` | infinite / undefined | infinite / undefined |
| `vol_134_part_i` | infinite / undefined | infinite / undefined |
| `vol_61` | infinite / undefined | infinite / undefined |
| `vol_62` | infinite / undefined | infinite / undefined |
| `vol_63` | infinite / undefined | infinite / undefined |

## 5. Multicollinearity diagnostics

- Condition number: **83930614.58** — **severe** multicollinearity.
- Predictors with VIF > 10 (severe): `is_alia`, `ncp_alia`, `is_brian`, `ncp_brian`, `is_bridget`, `ncp_bridget`, `is_leah`, `ncp_leah`, `is_rachel`, `ncp_rachel`, `vol_109`, `vol_114`, `vol_119`, `vol_120`, `vol_122`, `vol_124`, `vol_126`, `vol_127`, `vol_130`, `vol_91`, `vol_93`, `vol_94`

## 6. Plain-language interpretation

**Coder presence effects (significant at p<0.05):** `is_brian` = +0.5472 (higher, p = 0.000544).

**Per-coder experience (NCP) effects:** No `ncp_<coder>` term reaches p<0.05. Within this question, prior-volume count does not statistically predict pair agreement for any single coder.

**Top 3 volume effects by p-value (vs. Vol 95 reference):** `vol_119` = -0.3330 (p = 0.02361 *); `vol_114` = -0.2959 (p = 0.03224 *); `vol_127` = +0.2566 (p = 0.03525 *).

**Largest contributor to explained variance:** `is_brian` (26.1% of model SS, F = 15.90, p = 0.000544).

## 7. Caveats

- **Sample size:** N = 45 with k = 20 predictors leaves 24 residual df. Adequate but not generous.
- **No-intercept R² is uncentered:** do not compare these R² values to centered R² from intercept-bearing OLS models. Use the F p-value or the variance decomposition to gauge fit.
- **Multicollinearity expected:** the 5 coder dummies sum to 2 per row (a structural constraint), and NCP values are correlated with the corresponding coder indicators by construction (NCP > 0 ⇒ coder in pair). Some VIF inflation is design-induced, not a bug.
- **Target ceiling effect:** `pct_agreement` is heavily skewed toward 1.0. Effects are compressed by the bounded scale.
- **Q7-specific:** Q7 has the smallest subsample (~45 rows). Coefficient power is low.
