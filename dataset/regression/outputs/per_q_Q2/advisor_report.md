# IRR Per-Question Regression — Q2

**Research question:** Within this single question, do per-coder agreement levels and per-coder coding experience (`number_coded_prior`) predict inter-rater agreement, after controlling for volume?

**Subsample:** N = 65 (coder-pair × volume) rows where `question == Q2`. Volumes represented: 21 of 21. Mean `pct_agreement` = 0.9722 (min 0.910, max 1.000).

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
| N (observations) | 65 | filtered to question Q2 |
| k (predictors) | 29 | no intercept |
| Residual df | 35 | OK |
| R² | 0.8005 | centered R² (implicit-constant design) |
| Adjusted R² | 0.6352 | k-penalized variant |
| F-statistic | 4.84 | joint significance of all predictors |
| F p-value | 8.027e-06 | |
| RMSE | 0.0115 | typical residual on pct_agreement |
| MAE | 0.0088 | mean absolute residual |
| AIC | -336.0 | |
| BIC | -270.8 | |
| Condition number | 3805.49 | >30 = moderate collinearity; >100 = severe |

## 2. Variance decomposition (Type II ANOVA)

| Term | df | F | p-value | % of model SS | % of total SS |
|---|---|---|---|---|---|
| `is_brian` | 1 | 34.09 | 1.26e-06 *** | 31.6% | 23.9% |
| `is_leah` | 1 | 18.34 | 0.000137 *** | 17.0% | 12.8% |
| `is_rachel` | 1 | 16.56 | 0.0002557 *** | 15.4% | 11.6% |
| `is_bridget` | 1 | 16.50 | 0.0002607 *** | 15.3% | 11.6% |
| `is_alia` | 1 | 15.76 | 0.0003403 *** | 14.6% | 11.0% |
| `vol_94` | 1 | 5.05 | 0.03106 * | 4.7% | 3.5% |
| `vol_91` | 1 | 0.29 | 0.5919  | 0.3% | 0.2% |
| `vol_119` | 1 | 0.23 | 0.6337  | 0.2% | 0.2% |
| `vol_114` | 1 | 0.22 | 0.639  | 0.2% | 0.2% |
| `vol_93` | 1 | 0.21 | 0.6477  | 0.2% | 0.1% |
| `ncp_brian` | 1 | 0.16 | 0.6931  | 0.1% | 0.1% |
| `vol_126` | 1 | 0.06 | 0.8099  | 0.1% | 0.0% |
| `vol_130` | 1 | 0.06 | 0.8114  | 0.1% | 0.0% |
| `vol_62` | 1 | 0.03 | 0.871  | 0.0% | 0.0% |
| `vol_131` | 1 | 0.02 | 0.8758  | 0.0% | 0.0% |
| `vol_132` | 1 | 0.02 | 0.8849  | 0.0% | 0.0% |
| `vol_63` | 1 | 0.02 | 0.8877  | 0.0% | 0.0% |
| `vol_61` | 1 | 0.02 | 0.8877  | 0.0% | 0.0% |
| `vol_133` | 1 | 0.02 | 0.8886  | 0.0% | 0.0% |
| `vol_134_part_i` | 1 | 0.02 | 0.8893  | 0.0% | 0.0% |
| `vol_134_part_2` | 1 | 0.02 | 0.8967  | 0.0% | 0.0% |
| `ncp_alia` | 1 | 0.01 | 0.9236  | 0.0% | 0.0% |
| `vol_122` | 1 | 0.01 | 0.9338  | 0.0% | 0.0% |
| `vol_124` | 1 | 0.01 | 0.9355  | 0.0% | 0.0% |
| `vol_127` | 1 | 0.01 | 0.9414  | 0.0% | 0.0% |
| `ncp_leah` | 1 | 0.00 | 0.9465  | 0.0% | 0.0% |
| `ncp_rachel` | 1 | 0.00 | 0.948  | 0.0% | 0.0% |
| `vol_120` | 1 | 0.00 | 0.9524  | 0.0% | 0.0% |
| `vol_109` | 1 | 0.00 | 0.973  | 0.0% | 0.0% |
| `ncp_bridget` | 1 | 0.00 | 0.9777  | 0.0% | 0.0% |

## 3. Coefficient table

| Term | Coef | Std Err | t | p-value | 95% CI | Sig |
|---|---|---|---|---|---|---|
| `is_alia` | +0.47834 | 0.12048 | +3.97 | 0.0003403 | [+0.2337, +0.7229] | *** |
| `is_brian` | +0.46623 | 0.07985 | +5.84 | 1.26e-06 | [+0.3041, +0.6283] | *** |
| `is_bridget` | +0.48706 | 0.11990 | +4.06 | 0.0002607 | [+0.2436, +0.7305] | *** |
| `is_leah` | +0.48693 | 0.11371 | +4.28 | 0.000137 | [+0.2561, +0.7178] | *** |
| `is_rachel` | +0.48582 | 0.11940 | +4.07 | 0.0002557 | [+0.2434, +0.7282] | *** |
| `ncp_alia` | +0.00064 | 0.00663 | +0.10 | 0.9236 | [-0.0128, +0.0141] |  |
| `ncp_brian` | +0.00272 | 0.00684 | +0.40 | 0.6931 | [-0.0112, +0.0166] |  |
| `ncp_bridget` | -0.00020 | 0.00722 | -0.03 | 0.9777 | [-0.0149, +0.0145] |  |
| `ncp_leah` | -0.00050 | 0.00735 | -0.07 | 0.9465 | [-0.0154, +0.0144] |  |
| `ncp_rachel` | +0.00038 | 0.00579 | +0.07 | 0.948 | [-0.0114, +0.0121] |  |
| `vol_109` | -0.00274 | 0.08037 | -0.03 | 0.973 | [-0.1659, +0.1604] |  |
| `vol_114` | -0.03203 | 0.06769 | -0.47 | 0.639 | [-0.1695, +0.1054] |  |
| `vol_119` | -0.02644 | 0.05500 | -0.48 | 0.6337 | [-0.1381, +0.0852] |  |
| `vol_120` | +0.00847 | 0.14108 | +0.06 | 0.9524 | [-0.2779, +0.2949] |  |
| `vol_122` | +0.01181 | 0.14108 | +0.08 | 0.9338 | [-0.2746, +0.2982] |  |
| `vol_124` | -0.00768 | 0.09414 | -0.08 | 0.9355 | [-0.1988, +0.1834] |  |
| `vol_126` | -0.02591 | 0.10687 | -0.24 | 0.8099 | [-0.2429, +0.1911] |  |
| `vol_127` | +0.00879 | 0.11867 | +0.07 | 0.9414 | [-0.2321, +0.2497] |  |
| `vol_130` | +0.03521 | 0.14642 | +0.24 | 0.8114 | [-0.2620, +0.3325] |  |
| `vol_131` | +0.02421 | 0.15377 | +0.16 | 0.8758 | [-0.2880, +0.3364] |  |
| `vol_132` | +0.02437 | 0.16714 | +0.15 | 0.8849 | [-0.3149, +0.3637] |  |
| `vol_133` | +0.03197 | 0.22668 | +0.14 | 0.8886 | [-0.4282, +0.4922] |  |
| `vol_134_part_2` | +0.03093 | 0.23644 | +0.13 | 0.8967 | [-0.4491, +0.5109] |  |
| `vol_134_part_i` | +0.02676 | 0.19086 | +0.14 | 0.8893 | [-0.3607, +0.4142] |  |
| `vol_61` | +0.03036 | 0.21346 | +0.14 | 0.8877 | [-0.4030, +0.4637] |  |
| `vol_62` | +0.02953 | 0.18051 | +0.16 | 0.871 | [-0.3369, +0.3960] |  |
| `vol_63` | +0.03036 | 0.21346 | +0.14 | 0.8877 | [-0.4030, +0.4637] |  |
| `vol_91` | -0.01565 | 0.02892 | -0.54 | 0.5919 | [-0.0744, +0.0431] |  |
| `vol_93` | -0.01954 | 0.04238 | -0.46 | 0.6477 | [-0.1056, +0.0665] |  |
| `vol_94` | -0.04163 | 0.01853 | -2.25 | 0.03106 | [-0.0792, -0.0040] | * |

Significance codes: `***` p<0.001, `**` p<0.01, `*` p<0.05.

## 4. Variance Inflation Factors (VIF)

VIF measured on the no-intercept design matrix. Note: in no-intercept models, absolute VIF values are less straightforward to interpret than in standard intercept models — treat large values as a flag for relative collinearity rather than absolute severity.

| Predictor | VIF | Severity |
|---|---|---|
| `is_alia` | 2304.55 | **severe** |
| `is_rachel` | 1799.06 | **severe** |
| `vol_134_part_2` | 1239.32 | **severe** |
| `is_bridget` | 1228.95 | **severe** |
| `is_leah` | 1000.02 | **severe** |
| `vol_133` | 598.54 | **severe** |
| `ncp_alia` | 525.64 | **severe** |
| `is_brian` | 519.12 | **severe** |
| `ncp_rachel` | 400.10 | **severe** |
| `vol_61` | 359.54 | **severe** |
| `vol_63` | 359.54 | **severe** |
| `ncp_bridget` | 301.49 | **severe** |
| `ncp_leah` | 266.56 | **severe** |
| `vol_62` | 257.13 | **severe** |
| `vol_130` | 249.73 | **severe** |
| `vol_132` | 220.42 | **severe** |
| `vol_127` | 215.20 | **severe** |
| `vol_131` | 186.57 | **severe** |
| `vol_126` | 174.52 | **severe** |
| `ncp_brian` | 153.04 | **severe** |
| `vol_134_part_i` | 146.00 | **severe** |
| `vol_124` | 135.43 | **severe** |
| `vol_109` | 98.71 | **severe** |
| `vol_122` | 79.77 | **severe** |
| `vol_120` | 79.77 | **severe** |
| `vol_114` | 70.02 | **severe** |
| `vol_119` | 46.23 | **severe** |
| `vol_93` | 27.45 | **severe** |
| `vol_91` | 12.78 | **severe** |
| `vol_94` | 5.25 | moderate |

## 5. Multicollinearity diagnostics

- Condition number: **3805.49** — **severe** multicollinearity.
- Predictors with VIF > 10 (severe): `is_alia`, `is_rachel`, `vol_134_part_2`, `is_bridget`, `is_leah`, `vol_133`, `ncp_alia`, `is_brian`, `ncp_rachel`, `vol_61`, `vol_63`, `ncp_bridget`, `ncp_leah`, `vol_62`, `vol_130`, `vol_132`, `vol_127`, `vol_131`, `vol_126`, `ncp_brian`, `vol_134_part_i`, `vol_124`, `vol_109`, `vol_122`, `vol_120`, `vol_114`, `vol_119`, `vol_93`, `vol_91`

## 6. Plain-language interpretation

**Coder presence effects (significant at p<0.05):** `is_alia` = +0.4783 (higher, p = 0.0003403); `is_brian` = +0.4662 (higher, p = 1.26e-06); `is_bridget` = +0.4871 (higher, p = 0.0002607); `is_leah` = +0.4869 (higher, p = 0.000137); `is_rachel` = +0.4858 (higher, p = 0.0002557).

**Per-coder experience (NCP) effects:** No `ncp_<coder>` term reaches p<0.05. Within this question, prior-volume count does not statistically predict pair agreement for any single coder.

**Top 3 volume effects by p-value (vs. Vol 95 reference):** `vol_94` = -0.0416 (p = 0.03106 *); `vol_91` = -0.0156 (p = 0.5919); `vol_119` = -0.0264 (p = 0.6337).

**Largest contributor to explained variance:** `is_brian` (31.6% of model SS, F = 34.09, p = 1.26e-06).

## 7. Caveats

- **Sample size:** N = 65 with k = 29 predictors leaves 35 residual df. Adequate but not generous.
- **R² is centered standard R² here** (the 5 coder dummies sum to a constant, giving an implicit intercept). Adjusted R² is the more honest fit indicator given k ≈ N/2.
- **Multicollinearity expected:** the 5 coder dummies sum to 2 per row (a structural constraint), and NCP values are correlated with the corresponding coder indicators by construction (NCP > 0 ⇒ coder in pair). Some VIF inflation is design-induced, not a bug.
- **Target ceiling effect:** `pct_agreement` is heavily skewed toward 1.0. Effects are compressed by the bounded scale.
- **Q2 is conditional on Q1:** Rows where Q1 disagreed feed into this analysis; downstream agreement may inherit Q1 disagreement structure.
