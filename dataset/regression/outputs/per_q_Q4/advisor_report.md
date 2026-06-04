# IRR Per-Question Regression — Q4

**Research question:** Within this single question, do per-coder agreement levels and per-coder coding experience (`number_coded_prior`) predict inter-rater agreement, after controlling for volume?

**Subsample:** N = 65 (coder-pair × volume) rows where `question == Q4`. Volumes represented: 21 of 21. Mean `pct_agreement` = 0.9692 (min 0.890, max 1.000).

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
| N (observations) | 65 | filtered to question Q4 |
| k (predictors) | 29 | no intercept |
| Residual df | 35 | OK |
| R² | 0.7859 | centered R² (implicit-constant design) |
| Adjusted R² | 0.6085 | k-penalized variant |
| F-statistic | 4.43 | joint significance of all predictors |
| F p-value | 2.196e-05 | |
| RMSE | 0.0125 | typical residual on pct_agreement |
| MAE | 0.0090 | mean absolute residual |
| AIC | -325.6 | |
| BIC | -260.4 | |
| Condition number | 3805.49 | >30 = moderate collinearity; >100 = severe |

## 2. Variance decomposition (Type II ANOVA)

| Term | df | F | p-value | % of model SS | % of total SS |
|---|---|---|---|---|---|
| `is_brian` | 1 | 27.75 | 7.126e-06 *** | 32.0% | 22.8% |
| `is_leah` | 1 | 14.09 | 0.000632 *** | 16.2% | 11.6% |
| `is_rachel` | 1 | 12.80 | 0.00104 ** | 14.7% | 10.5% |
| `is_bridget` | 1 | 12.73 | 0.001067 ** | 14.7% | 10.4% |
| `is_alia` | 1 | 12.18 | 0.001324 ** | 14.0% | 10.0% |
| `vol_94` | 1 | 5.62 | 0.02334 * | 6.5% | 4.6% |
| `ncp_brian` | 1 | 0.18 | 0.6737  | 0.2% | 0.1% |
| `vol_93` | 1 | 0.13 | 0.7164  | 0.2% | 0.1% |
| `vol_62` | 1 | 0.11 | 0.7432  | 0.1% | 0.1% |
| `vol_130` | 1 | 0.11 | 0.7476  | 0.1% | 0.1% |
| `vol_114` | 1 | 0.10 | 0.7501  | 0.1% | 0.1% |
| `vol_63` | 1 | 0.10 | 0.7562  | 0.1% | 0.1% |
| `vol_61` | 1 | 0.10 | 0.7562  | 0.1% | 0.1% |
| `vol_131` | 1 | 0.09 | 0.7614  | 0.1% | 0.1% |
| `vol_134_part_2` | 1 | 0.09 | 0.7628  | 0.1% | 0.1% |
| `vol_133` | 1 | 0.08 | 0.7791  | 0.1% | 0.1% |
| `vol_134_part_i` | 1 | 0.08 | 0.7792  | 0.1% | 0.1% |
| `vol_91` | 1 | 0.08 | 0.7817  | 0.1% | 0.1% |
| `vol_132` | 1 | 0.07 | 0.7987  | 0.1% | 0.1% |
| `ncp_rachel` | 1 | 0.07 | 0.7994  | 0.1% | 0.1% |
| `ncp_alia` | 1 | 0.06 | 0.8128  | 0.1% | 0.0% |
| `vol_127` | 1 | 0.06 | 0.815  | 0.1% | 0.0% |
| `vol_119` | 1 | 0.05 | 0.8322  | 0.1% | 0.0% |
| `ncp_bridget` | 1 | 0.04 | 0.8333  | 0.1% | 0.0% |
| `vol_109` | 1 | 0.02 | 0.8794  | 0.0% | 0.0% |
| `ncp_leah` | 1 | 0.02 | 0.8869  | 0.0% | 0.0% |
| `vol_120` | 1 | 0.01 | 0.9192  | 0.0% | 0.0% |
| `vol_122` | 1 | 0.01 | 0.9192  | 0.0% | 0.0% |
| `vol_126` | 1 | 0.01 | 0.9254  | 0.0% | 0.0% |
| `vol_124` | 1 | 0.01 | 0.9273  | 0.0% | 0.0% |

## 3. Coefficient table

| Term | Coef | Std Err | t | p-value | 95% CI | Sig |
|---|---|---|---|---|---|---|
| `is_alia` | +0.45558 | 0.13052 | +3.49 | 0.001324 | [+0.1906, +0.7206] | ** |
| `is_brian` | +0.45572 | 0.08651 | +5.27 | 7.126e-06 | [+0.2801, +0.6313] | *** |
| `is_bridget` | +0.46344 | 0.12989 | +3.57 | 0.001067 | [+0.1997, +0.7271] | ** |
| `is_leah` | +0.46244 | 0.12318 | +3.75 | 0.000632 | [+0.2124, +0.7125] | *** |
| `is_rachel` | +0.46272 | 0.12935 | +3.58 | 0.00104 | [+0.2001, +0.7253] | ** |
| `ncp_alia` | +0.00171 | 0.00718 | +0.24 | 0.8128 | [-0.0129, +0.0163] |  |
| `ncp_brian` | +0.00315 | 0.00741 | +0.42 | 0.6737 | [-0.0119, +0.0182] |  |
| `ncp_bridget` | +0.00166 | 0.00782 | +0.21 | 0.8333 | [-0.0142, +0.0175] |  |
| `ncp_leah` | +0.00114 | 0.00796 | +0.14 | 0.8869 | [-0.0150, +0.0173] |  |
| `ncp_rachel` | +0.00161 | 0.00627 | +0.26 | 0.7994 | [-0.0111, +0.0143] |  |
| `vol_109` | +0.01330 | 0.08707 | +0.15 | 0.8794 | [-0.1635, +0.1901] |  |
| `vol_114` | -0.02354 | 0.07333 | -0.32 | 0.7501 | [-0.1724, +0.1253] |  |
| `vol_119` | -0.01272 | 0.05959 | -0.21 | 0.8322 | [-0.1337, +0.1083] |  |
| `vol_120` | +0.01562 | 0.15284 | +0.10 | 0.9192 | [-0.2947, +0.3259] |  |
| `vol_122` | +0.01562 | 0.15284 | +0.10 | 0.9192 | [-0.2947, +0.3259] |  |
| `vol_124` | +0.00938 | 0.10199 | +0.09 | 0.9273 | [-0.1977, +0.2164] |  |
| `vol_126` | -0.01092 | 0.11577 | -0.09 | 0.9254 | [-0.2460, +0.2241] |  |
| `vol_127` | +0.03030 | 0.12856 | +0.24 | 0.815 | [-0.2307, +0.2913] |  |
| `vol_130` | +0.05146 | 0.15862 | +0.32 | 0.7476 | [-0.2706, +0.3735] |  |
| `vol_131` | +0.05097 | 0.16658 | +0.31 | 0.7614 | [-0.2872, +0.3891] |  |
| `vol_132` | +0.04653 | 0.18106 | +0.26 | 0.7987 | [-0.3211, +0.4141] |  |
| `vol_133` | +0.06942 | 0.24557 | +0.28 | 0.7791 | [-0.4291, +0.5680] |  |
| `vol_134_part_2` | +0.07791 | 0.25614 | +0.30 | 0.7628 | [-0.4421, +0.5979] |  |
| `vol_134_part_i` | +0.05842 | 0.20676 | +0.28 | 0.7792 | [-0.3613, +0.4782] |  |
| `vol_61` | +0.07236 | 0.23124 | +0.31 | 0.7562 | [-0.3971, +0.5418] |  |
| `vol_62` | +0.06459 | 0.19556 | +0.33 | 0.7432 | [-0.3324, +0.4616] |  |
| `vol_63` | +0.07236 | 0.23124 | +0.31 | 0.7562 | [-0.3971, +0.5418] |  |
| `vol_91` | -0.00875 | 0.03133 | -0.28 | 0.7817 | [-0.0724, +0.0549] |  |
| `vol_93` | -0.01681 | 0.04592 | -0.37 | 0.7164 | [-0.1100, +0.0764] |  |
| `vol_94` | -0.04761 | 0.02007 | -2.37 | 0.02334 | [-0.0884, -0.0069] | * |

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

**Coder presence effects (significant at p<0.05):** `is_alia` = +0.4556 (higher, p = 0.001324); `is_brian` = +0.4557 (higher, p = 7.126e-06); `is_bridget` = +0.4634 (higher, p = 0.001067); `is_leah` = +0.4624 (higher, p = 0.000632); `is_rachel` = +0.4627 (higher, p = 0.00104).

**Per-coder experience (NCP) effects:** No `ncp_<coder>` term reaches p<0.05. Within this question, prior-volume count does not statistically predict pair agreement for any single coder.

**Top 3 volume effects by p-value (vs. Vol 95 reference):** `vol_94` = -0.0476 (p = 0.02334 *); `vol_93` = -0.0168 (p = 0.7164); `vol_62` = +0.0646 (p = 0.7432).

**Largest contributor to explained variance:** `is_brian` (32.0% of model SS, F = 27.75, p = 7.126e-06).

## 7. Caveats

- **Sample size:** N = 65 with k = 29 predictors leaves 35 residual df. Adequate but not generous.
- **R² is centered standard R² here** (the 5 coder dummies sum to a constant, giving an implicit intercept). Adjusted R² is the more honest fit indicator given k ≈ N/2.
- **Multicollinearity expected:** the 5 coder dummies sum to 2 per row (a structural constraint), and NCP values are correlated with the corresponding coder indicators by construction (NCP > 0 ⇒ coder in pair). Some VIF inflation is design-induced, not a bug.
- **Target ceiling effect:** `pct_agreement` is heavily skewed toward 1.0. Effects are compressed by the bounded scale.
- **Q4 is conditional on Q1:** Rows where Q1 disagreed feed into this analysis; downstream agreement may inherit Q1 disagreement structure.
