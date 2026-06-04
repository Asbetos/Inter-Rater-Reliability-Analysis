# IRR Per-Question Regression — Q6

**Research question:** Within this single question, do per-coder agreement levels and per-coder coding experience (`number_coded_prior`) predict inter-rater agreement, after controlling for volume?

**Subsample:** N = 65 (coder-pair × volume) rows where `question == Q6`. Volumes represented: 21 of 21. Mean `pct_agreement` = 0.8693 (min 0.000, max 1.000).

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
| N (observations) | 65 | filtered to question Q6 |
| k (predictors) | 29 | no intercept |
| Residual df | 35 | OK |
| R² | 0.6853 | centered R² (implicit-constant design) |
| Adjusted R² | 0.4246 | k-penalized variant |
| F-statistic | 2.63 | joint significance of all predictors |
| F p-value | 0.003463 | |
| RMSE | 0.1338 | typical residual on pct_agreement |
| MAE | 0.0840 | mean absolute residual |
| AIC | -17.0 | |
| BIC | 48.2 | |
| Condition number | 3805.49 | >30 = moderate collinearity; >100 = severe |

## 2. Variance decomposition (Type II ANOVA)

| Term | df | F | p-value | % of model SS | % of total SS |
|---|---|---|---|---|---|
| `ncp_rachel` | 1 | 2.79 | 0.1039  | 4.5% | 2.9% |
| `vol_62` | 1 | 2.75 | 0.1061  | 4.4% | 2.8% |
| `vol_134_part_2` | 1 | 2.72 | 0.1081  | 4.4% | 2.8% |
| `vol_63` | 1 | 2.71 | 0.1086  | 4.4% | 2.8% |
| `vol_131` | 1 | 2.70 | 0.109  | 4.4% | 2.8% |
| `ncp_leah` | 1 | 2.66 | 0.1117  | 4.3% | 2.7% |
| `vol_132` | 1 | 2.65 | 0.1128  | 4.3% | 2.7% |
| `ncp_alia` | 1 | 2.63 | 0.1139  | 4.2% | 2.7% |
| `vol_61` | 1 | 2.63 | 0.1141  | 4.2% | 2.7% |
| `vol_133` | 1 | 2.63 | 0.1141  | 4.2% | 2.7% |
| `vol_134_part_i` | 1 | 2.48 | 0.1239  | 4.0% | 2.6% |
| `vol_126` | 1 | 2.39 | 0.1311  | 3.9% | 2.5% |
| `ncp_bridget` | 1 | 2.39 | 0.1311  | 3.9% | 2.5% |
| `vol_127` | 1 | 2.30 | 0.1384  | 3.7% | 2.4% |
| `vol_130` | 1 | 2.24 | 0.1431  | 3.6% | 2.3% |
| `vol_109` | 1 | 2.17 | 0.1494  | 3.5% | 2.2% |
| `vol_122` | 1 | 1.97 | 0.1688  | 3.2% | 2.0% |
| `vol_120` | 1 | 1.97 | 0.1697  | 3.2% | 2.0% |
| `vol_93` | 1 | 1.96 | 0.1701  | 3.2% | 2.0% |
| `vol_91` | 1 | 1.91 | 0.1761  | 3.1% | 2.0% |
| `vol_124` | 1 | 1.80 | 0.1888  | 2.9% | 1.9% |
| `is_bridget` | 1 | 1.72 | 0.1981  | 2.8% | 1.8% |
| `ncp_brian` | 1 | 1.70 | 0.201  | 2.7% | 1.8% |
| `is_leah` | 1 | 1.70 | 0.2014  | 2.7% | 1.7% |
| `is_alia` | 1 | 1.65 | 0.2074  | 2.7% | 1.7% |
| `is_rachel` | 1 | 1.57 | 0.2188  | 2.5% | 1.6% |
| `vol_94` | 1 | 1.32 | 0.2577  | 2.1% | 1.4% |
| `vol_114` | 1 | 0.80 | 0.3783  | 1.3% | 0.8% |
| `is_brian` | 1 | 0.59 | 0.4469  | 1.0% | 0.6% |
| `vol_119` | 1 | 0.53 | 0.4728  | 0.8% | 0.5% |

## 3. Coefficient table

| Term | Coef | Std Err | t | p-value | 95% CI | Sig |
|---|---|---|---|---|---|---|
| `is_alia` | -1.80072 | 1.40176 | -1.28 | 0.2074 | [-4.6464, +1.0450] |  |
| `is_brian` | -0.71465 | 0.92904 | -0.77 | 0.4469 | [-2.6007, +1.1714] |  |
| `is_bridget` | -1.83004 | 1.39499 | -1.31 | 0.1981 | [-4.6620, +1.0019] |  |
| `is_leah` | -1.72263 | 1.32294 | -1.30 | 0.2014 | [-4.4083, +0.9631] |  |
| `is_rachel` | -1.73956 | 1.38917 | -1.25 | 0.2188 | [-4.5597, +1.0806] |  |
| `ncp_alia` | +0.12498 | 0.07709 | +1.62 | 0.1139 | [-0.0315, +0.2815] |  |
| `ncp_brian` | +0.10368 | 0.07955 | +1.30 | 0.201 | [-0.0578, +0.2652] |  |
| `ncp_bridget` | +0.12987 | 0.08400 | +1.55 | 0.1311 | [-0.0407, +0.3004] |  |
| `ncp_leah` | +0.13951 | 0.08550 | +1.63 | 0.1117 | [-0.0341, +0.3131] |  |
| `ncp_rachel` | +0.11249 | 0.06738 | +1.67 | 0.1039 | [-0.0243, +0.2493] |  |
| `vol_109` | +1.37834 | 0.93511 | +1.47 | 0.1494 | [-0.5200, +3.2767] |  |
| `vol_114` | +0.70271 | 0.78756 | +0.89 | 0.3783 | [-0.8961, +2.3015] |  |
| `vol_119` | +0.46445 | 0.63994 | +0.73 | 0.4728 | [-0.8347, +1.7636] |  |
| `vol_120` | +2.30144 | 1.64138 | +1.40 | 0.1697 | [-1.0307, +5.6336] |  |
| `vol_122` | +2.30644 | 1.64138 | +1.41 | 0.1688 | [-1.0257, +5.6386] |  |
| `vol_124` | +1.46813 | 1.09532 | +1.34 | 0.1888 | [-0.7555, +3.6917] |  |
| `vol_126` | +1.92244 | 1.24336 | +1.55 | 0.1311 | [-0.6017, +4.4466] |  |
| `vol_127` | +2.09392 | 1.38070 | +1.52 | 0.1384 | [-0.7091, +4.8969] |  |
| `vol_130` | +2.55212 | 1.70353 | +1.50 | 0.1431 | [-0.9062, +6.0105] |  |
| `vol_131` | +2.94195 | 1.78897 | +1.64 | 0.109 | [-0.6899, +6.5738] |  |
| `vol_132` | +3.16287 | 1.94453 | +1.63 | 0.1128 | [-0.7847, +7.1105] |  |
| `vol_133` | +4.27367 | 2.63731 | +1.62 | 0.1141 | [-1.0804, +9.6277] |  |
| `vol_134_part_2` | +4.53621 | 2.75081 | +1.65 | 0.1081 | [-1.0482, +10.1206] |  |
| `vol_134_part_i` | +3.50038 | 2.22051 | +1.58 | 0.1239 | [-1.0075, +8.0083] |  |
| `vol_61` | +4.02438 | 2.48346 | +1.62 | 0.1141 | [-1.0173, +9.0661] |  |
| `vol_62` | +3.48380 | 2.10018 | +1.66 | 0.1061 | [-0.7798, +7.7474] |  |
| `vol_63` | +4.08938 | 2.48346 | +1.65 | 0.1086 | [-0.9523, +9.1311] |  |
| `vol_91` | +0.46459 | 0.33646 | +1.38 | 0.1761 | [-0.2185, +1.1476] |  |
| `vol_93` | +0.69068 | 0.49311 | +1.40 | 0.1701 | [-0.3104, +1.6917] |  |
| `vol_94` | +0.24805 | 0.21558 | +1.15 | 0.2577 | [-0.1896, +0.6857] |  |

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

**Coder presence effects:** No `is_<coder>` term reaches p<0.05. Coder identity does not show a statistically detectable shift in agreement for this question.

**Per-coder experience (NCP) effects:** No `ncp_<coder>` term reaches p<0.05. Within this question, prior-volume count does not statistically predict pair agreement for any single coder.

**Top 3 volume effects by p-value (vs. Vol 95 reference):** `vol_62` = +3.4838 (p = 0.1061); `vol_134_part_2` = +4.5362 (p = 0.1081); `vol_63` = +4.0894 (p = 0.1086).

**Largest contributor to explained variance:** `ncp_rachel` (4.5% of model SS, F = 2.79, p = 0.1039).

## 7. Caveats

- **Sample size:** N = 65 with k = 29 predictors leaves 35 residual df. Adequate but not generous.
- **No-intercept R² is uncentered:** do not compare these R² values to centered R² from intercept-bearing OLS models. Use the F p-value or the variance decomposition to gauge fit.
- **Multicollinearity expected:** the 5 coder dummies sum to 2 per row (a structural constraint), and NCP values are correlated with the corresponding coder indicators by construction (NCP > 0 ⇒ coder in pair). Some VIF inflation is design-induced, not a bug.
- **Target ceiling effect:** `pct_agreement` is heavily skewed toward 1.0. Effects are compressed by the bounded scale.
