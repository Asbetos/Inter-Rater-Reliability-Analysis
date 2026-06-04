# IRR Per-Question Regression — Q5

**Research question:** Within this single question, do per-coder agreement levels and per-coder coding experience (`number_coded_prior`) predict inter-rater agreement, after controlling for volume?

**Subsample:** N = 65 (coder-pair × volume) rows where `question == Q5`. Volumes represented: 21 of 21. Mean `pct_agreement` = 0.9706 (min 0.900, max 1.000).

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
| N (observations) | 65 | filtered to question Q5 |
| k (predictors) | 29 | no intercept |
| Residual df | 35 | OK |
| R² | 0.7953 | centered R² (implicit-constant design) |
| Adjusted R² | 0.6256 | k-penalized variant |
| F-statistic | 4.69 | joint significance of all predictors |
| F p-value | 1.165e-05 | |
| RMSE | 0.0117 | typical residual on pct_agreement |
| MAE | 0.0087 | mean absolute residual |
| AIC | -334.0 | |
| BIC | -268.8 | |
| Condition number | 3805.49 | >30 = moderate collinearity; >100 = severe |

## 2. Variance decomposition (Type II ANOVA)

| Term | df | F | p-value | % of model SS | % of total SS |
|---|---|---|---|---|---|
| `is_brian` | 1 | 29.96 | 3.816e-06 *** | 32.0% | 23.3% |
| `is_leah` | 1 | 14.93 | 0.0004614 *** | 16.0% | 11.6% |
| `is_rachel` | 1 | 13.68 | 0.0007383 *** | 14.6% | 10.6% |
| `is_bridget` | 1 | 13.58 | 0.0007679 *** | 14.5% | 10.6% |
| `is_alia` | 1 | 12.81 | 0.001032 ** | 13.7% | 10.0% |
| `vol_94` | 1 | 5.22 | 0.02849 * | 5.6% | 4.1% |
| `ncp_brian` | 1 | 0.37 | 0.5489  | 0.4% | 0.3% |
| `vol_130` | 1 | 0.26 | 0.6143  | 0.3% | 0.2% |
| `vol_62` | 1 | 0.24 | 0.6306  | 0.3% | 0.2% |
| `vol_63` | 1 | 0.22 | 0.6445  | 0.2% | 0.2% |
| `vol_61` | 1 | 0.22 | 0.6445  | 0.2% | 0.2% |
| `vol_131` | 1 | 0.21 | 0.6476  | 0.2% | 0.2% |
| `vol_134_part_2` | 1 | 0.21 | 0.6518  | 0.2% | 0.2% |
| `vol_134_part_i` | 1 | 0.18 | 0.6701  | 0.2% | 0.1% |
| `vol_133` | 1 | 0.18 | 0.6729  | 0.2% | 0.1% |
| `vol_132` | 1 | 0.18 | 0.6752  | 0.2% | 0.1% |
| `ncp_alia` | 1 | 0.17 | 0.6837  | 0.2% | 0.1% |
| `ncp_rachel` | 1 | 0.15 | 0.699  | 0.2% | 0.1% |
| `vol_127` | 1 | 0.15 | 0.7028  | 0.2% | 0.1% |
| `vol_120` | 1 | 0.10 | 0.7495  | 0.1% | 0.1% |
| `ncp_bridget` | 1 | 0.10 | 0.7496  | 0.1% | 0.1% |
| `vol_122` | 1 | 0.10 | 0.7582  | 0.1% | 0.1% |
| `vol_109` | 1 | 0.09 | 0.7638  | 0.1% | 0.1% |
| `ncp_leah` | 1 | 0.07 | 0.7891  | 0.1% | 0.1% |
| `vol_93` | 1 | 0.06 | 0.8007  | 0.1% | 0.1% |
| `vol_124` | 1 | 0.06 | 0.8016  | 0.1% | 0.0% |
| `vol_114` | 1 | 0.02 | 0.8855  | 0.0% | 0.0% |
| `vol_119` | 1 | 0.01 | 0.9258  | 0.0% | 0.0% |
| `vol_91` | 1 | 0.01 | 0.933  | 0.0% | 0.0% |
| `vol_126` | 1 | 0.00 | 0.9486  | 0.0% | 0.0% |

## 3. Coefficient table

| Term | Coef | Std Err | t | p-value | 95% CI | Sig |
|---|---|---|---|---|---|---|
| `is_alia` | +0.43798 | 0.12235 | +3.58 | 0.001032 | [+0.1896, +0.6864] | ** |
| `is_brian` | +0.44387 | 0.08109 | +5.47 | 3.816e-06 | [+0.2792, +0.6085] | *** |
| `is_bridget` | +0.44870 | 0.12176 | +3.69 | 0.0007679 | [+0.2015, +0.6959] | *** |
| `is_leah` | +0.44621 | 0.11547 | +3.86 | 0.0004614 | [+0.2118, +0.6806] | *** |
| `is_rachel` | +0.44852 | 0.12125 | +3.70 | 0.0007383 | [+0.2024, +0.6947] | *** |
| `ncp_alia` | +0.00276 | 0.00673 | +0.41 | 0.6837 | [-0.0109, +0.0164] |  |
| `ncp_brian` | +0.00420 | 0.00694 | +0.61 | 0.5489 | [-0.0099, +0.0183] |  |
| `ncp_bridget` | +0.00236 | 0.00733 | +0.32 | 0.7496 | [-0.0125, +0.0172] |  |
| `ncp_leah` | +0.00201 | 0.00746 | +0.27 | 0.7891 | [-0.0131, +0.0172] |  |
| `ncp_rachel` | +0.00229 | 0.00588 | +0.39 | 0.699 | [-0.0096, +0.0142] |  |
| `vol_109` | +0.02472 | 0.08162 | +0.30 | 0.7638 | [-0.1410, +0.1904] |  |
| `vol_114` | -0.00997 | 0.06874 | -0.15 | 0.8855 | [-0.1495, +0.1296] |  |
| `vol_119` | -0.00524 | 0.05586 | -0.09 | 0.9258 | [-0.1186, +0.1082] |  |
| `vol_120` | +0.04611 | 0.14326 | +0.32 | 0.7495 | [-0.2447, +0.3370] |  |
| `vol_122` | +0.04444 | 0.14326 | +0.31 | 0.7582 | [-0.2464, +0.3353] |  |
| `vol_124` | +0.02421 | 0.09560 | +0.25 | 0.8016 | [-0.1699, +0.2183] |  |
| `vol_126` | +0.00704 | 0.10852 | +0.06 | 0.9486 | [-0.2133, +0.2274] |  |
| `vol_127` | +0.04635 | 0.12051 | +0.38 | 0.7028 | [-0.1983, +0.2910] |  |
| `vol_130` | +0.07561 | 0.14869 | +0.51 | 0.6143 | [-0.2262, +0.3775] |  |
| `vol_131` | +0.07199 | 0.15615 | +0.46 | 0.6476 | [-0.2450, +0.3890] |  |
| `vol_132` | +0.07171 | 0.16972 | +0.42 | 0.6752 | [-0.2728, +0.4163] |  |
| `vol_133` | +0.09801 | 0.23019 | +0.43 | 0.6729 | [-0.3693, +0.5653] |  |
| `vol_134_part_2` | +0.10930 | 0.24010 | +0.46 | 0.6518 | [-0.3781, +0.5967] |  |
| `vol_134_part_i` | +0.08327 | 0.19381 | +0.43 | 0.6701 | [-0.3102, +0.4767] |  |
| `vol_61` | +0.10088 | 0.21676 | +0.47 | 0.6445 | [-0.3392, +0.5409] |  |
| `vol_62` | +0.08892 | 0.18331 | +0.49 | 0.6306 | [-0.2832, +0.4611] |  |
| `vol_63` | +0.10088 | 0.21676 | +0.47 | 0.6445 | [-0.3392, +0.5409] |  |
| `vol_91` | -0.00249 | 0.02937 | -0.08 | 0.933 | [-0.0621, +0.0571] |  |
| `vol_93` | -0.01095 | 0.04304 | -0.25 | 0.8007 | [-0.0983, +0.0764] |  |
| `vol_94` | -0.04299 | 0.01882 | -2.28 | 0.02849 | [-0.0812, -0.0048] | * |

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

**Coder presence effects (significant at p<0.05):** `is_alia` = +0.4380 (higher, p = 0.001032); `is_brian` = +0.4439 (higher, p = 3.816e-06); `is_bridget` = +0.4487 (higher, p = 0.0007679); `is_leah` = +0.4462 (higher, p = 0.0004614); `is_rachel` = +0.4485 (higher, p = 0.0007383).

**Per-coder experience (NCP) effects:** No `ncp_<coder>` term reaches p<0.05. Within this question, prior-volume count does not statistically predict pair agreement for any single coder.

**Top 3 volume effects by p-value (vs. Vol 95 reference):** `vol_94` = -0.0430 (p = 0.02849 *); `vol_130` = +0.0756 (p = 0.6143); `vol_62` = +0.0889 (p = 0.6306).

**Largest contributor to explained variance:** `is_brian` (32.0% of model SS, F = 29.96, p = 3.816e-06).

## 7. Caveats

- **Sample size:** N = 65 with k = 29 predictors leaves 35 residual df. Adequate but not generous.
- **R² is centered standard R² here** (the 5 coder dummies sum to a constant, giving an implicit intercept). Adjusted R² is the more honest fit indicator given k ≈ N/2.
- **Multicollinearity expected:** the 5 coder dummies sum to 2 per row (a structural constraint), and NCP values are correlated with the corresponding coder indicators by construction (NCP > 0 ⇒ coder in pair). Some VIF inflation is design-induced, not a bug.
- **Target ceiling effect:** `pct_agreement` is heavily skewed toward 1.0. Effects are compressed by the bounded scale.
- **Q5 is conditional on Q1:** Rows where Q1 disagreed feed into this analysis; downstream agreement may inherit Q1 disagreement structure.
