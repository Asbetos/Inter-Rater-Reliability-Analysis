# IRR Per-Question Regression — Q3

**Research question:** Within this single question, do per-coder agreement levels and per-coder coding experience (`number_coded_prior`) predict inter-rater agreement, after controlling for volume?

**Subsample:** N = 65 (coder-pair × volume) rows where `question == Q3`. Volumes represented: 21 of 21. Mean `pct_agreement` = 0.9736 (min 0.910, max 1.000).

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
| N (observations) | 65 | filtered to question Q3 |
| k (predictors) | 29 | no intercept |
| Residual df | 35 | OK |
| R² | 0.8015 | centered R² (implicit-constant design) |
| Adjusted R² | 0.6371 | k-penalized variant |
| F-statistic | 4.87 | joint significance of all predictors |
| F p-value | 7.454e-06 | |
| RMSE | 0.0117 | typical residual on pct_agreement |
| MAE | 0.0085 | mean absolute residual |
| AIC | -334.3 | |
| BIC | -269.1 | |
| Condition number | 3805.49 | >30 = moderate collinearity; >100 = severe |

## 2. Variance decomposition (Type II ANOVA)

| Term | df | F | p-value | % of model SS | % of total SS |
|---|---|---|---|---|---|
| `is_brian` | 1 | 28.78 | 5.311e-06 *** | 31.8% | 22.9% |
| `is_leah` | 1 | 13.90 | 0.0006794 *** | 15.3% | 11.1% |
| `is_rachel` | 1 | 12.56 | 0.001142 ** | 13.9% | 10.0% |
| `is_bridget` | 1 | 12.52 | 0.001157 ** | 13.8% | 10.0% |
| `is_alia` | 1 | 11.86 | 0.001507 ** | 13.1% | 9.4% |
| `vol_94` | 1 | 4.40 | 0.0432 * | 4.9% | 3.5% |
| `ncp_brian` | 1 | 0.66 | 0.4237  | 0.7% | 0.5% |
| `vol_130` | 1 | 0.50 | 0.4857  | 0.5% | 0.4% |
| `vol_131` | 1 | 0.44 | 0.5137  | 0.5% | 0.3% |
| `vol_132` | 1 | 0.42 | 0.5217  | 0.5% | 0.3% |
| `vol_62` | 1 | 0.41 | 0.5286  | 0.4% | 0.3% |
| `vol_134_part_i` | 1 | 0.40 | 0.5291  | 0.4% | 0.3% |
| `vol_63` | 1 | 0.38 | 0.541  | 0.4% | 0.3% |
| `vol_61` | 1 | 0.38 | 0.541  | 0.4% | 0.3% |
| `vol_133` | 1 | 0.37 | 0.5455  | 0.4% | 0.3% |
| `vol_134_part_2` | 1 | 0.37 | 0.5476  | 0.4% | 0.3% |
| `ncp_alia` | 1 | 0.31 | 0.5786  | 0.3% | 0.3% |
| `ncp_rachel` | 1 | 0.29 | 0.5917  | 0.3% | 0.2% |
| `vol_127` | 1 | 0.29 | 0.5935  | 0.3% | 0.2% |
| `vol_122` | 1 | 0.28 | 0.5976  | 0.3% | 0.2% |
| `vol_120` | 1 | 0.27 | 0.6057  | 0.3% | 0.2% |
| `ncp_bridget` | 1 | 0.22 | 0.6457  | 0.2% | 0.2% |
| `vol_109` | 1 | 0.20 | 0.6582  | 0.2% | 0.2% |
| `ncp_leah` | 1 | 0.19 | 0.6618  | 0.2% | 0.2% |
| `vol_124` | 1 | 0.13 | 0.7161  | 0.1% | 0.1% |
| `vol_126` | 1 | 0.07 | 0.7975  | 0.1% | 0.1% |
| `vol_91` | 1 | 0.03 | 0.8749  | 0.0% | 0.0% |
| `vol_93` | 1 | 0.00 | 0.9835  | 0.0% | 0.0% |
| `vol_114` | 1 | 0.00 | 0.9861  | 0.0% | 0.0% |
| `vol_119` | 1 | 0.00 | 0.9961  | 0.0% | 0.0% |

## 3. Coefficient table

| Term | Coef | Std Err | t | p-value | 95% CI | Sig |
|---|---|---|---|---|---|---|
| `is_alia` | +0.42047 | 0.12211 | +3.44 | 0.001507 | [+0.1726, +0.6684] | ** |
| `is_brian` | +0.43418 | 0.08093 | +5.36 | 5.311e-06 | [+0.2699, +0.5985] | *** |
| `is_bridget` | +0.43003 | 0.12152 | +3.54 | 0.001157 | [+0.1833, +0.6767] | ** |
| `is_leah` | +0.42968 | 0.11524 | +3.73 | 0.0006794 | [+0.1957, +0.6636] | *** |
| `is_rachel` | +0.42879 | 0.12101 | +3.54 | 0.001142 | [+0.1831, +0.6745] | ** |
| `ncp_alia` | +0.00377 | 0.00671 | +0.56 | 0.5786 | [-0.0099, +0.0174] |  |
| `ncp_brian` | +0.00561 | 0.00693 | +0.81 | 0.4237 | [-0.0085, +0.0197] |  |
| `ncp_bridget` | +0.00339 | 0.00732 | +0.46 | 0.6457 | [-0.0115, +0.0182] |  |
| `ncp_leah` | +0.00329 | 0.00745 | +0.44 | 0.6618 | [-0.0118, +0.0184] |  |
| `ncp_rachel` | +0.00318 | 0.00587 | +0.54 | 0.5917 | [-0.0087, +0.0151] |  |
| `vol_109` | +0.03634 | 0.08146 | +0.45 | 0.6582 | [-0.1290, +0.2017] |  |
| `vol_114` | -0.00120 | 0.06860 | -0.02 | 0.9861 | [-0.1405, +0.1381] |  |
| `vol_119` | -0.00028 | 0.05575 | -0.00 | 0.9961 | [-0.1134, +0.1129] |  |
| `vol_120` | +0.07449 | 0.14298 | +0.52 | 0.6057 | [-0.2158, +0.3648] |  |
| `vol_122` | +0.07616 | 0.14298 | +0.53 | 0.5976 | [-0.2141, +0.3664] |  |
| `vol_124` | +0.03498 | 0.09541 | +0.37 | 0.7161 | [-0.1587, +0.2287] |  |
| `vol_126` | +0.02800 | 0.10831 | +0.26 | 0.7975 | [-0.1919, +0.2479] |  |
| `vol_127` | +0.06480 | 0.12027 | +0.54 | 0.5935 | [-0.1794, +0.3090] |  |
| `vol_130` | +0.10456 | 0.14839 | +0.70 | 0.4857 | [-0.1967, +0.4058] |  |
| `vol_131` | +0.10282 | 0.15584 | +0.66 | 0.5137 | [-0.2135, +0.4192] |  |
| `vol_132` | +0.10963 | 0.16939 | +0.65 | 0.5217 | [-0.2342, +0.4535] |  |
| `vol_133` | +0.14025 | 0.22974 | +0.61 | 0.5455 | [-0.3261, +0.6066] |  |
| `vol_134_part_2` | +0.14552 | 0.23962 | +0.61 | 0.5476 | [-0.3409, +0.6320] |  |
| `vol_134_part_i` | +0.12297 | 0.19343 | +0.64 | 0.5291 | [-0.2697, +0.5157] |  |
| `vol_61` | +0.13354 | 0.21633 | +0.62 | 0.541 | [-0.3056, +0.5727] |  |
| `vol_62` | +0.11645 | 0.18295 | +0.64 | 0.5286 | [-0.2550, +0.4878] |  |
| `vol_63` | +0.13354 | 0.21633 | +0.62 | 0.541 | [-0.3056, +0.5727] |  |
| `vol_91` | -0.00465 | 0.02931 | -0.16 | 0.8749 | [-0.0641, +0.0549] |  |
| `vol_93` | -0.00089 | 0.04295 | -0.02 | 0.9835 | [-0.0881, +0.0863] |  |
| `vol_94` | -0.03940 | 0.01878 | -2.10 | 0.0432 | [-0.0775, -0.0013] | * |

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

**Coder presence effects (significant at p<0.05):** `is_alia` = +0.4205 (higher, p = 0.001507); `is_brian` = +0.4342 (higher, p = 5.311e-06); `is_bridget` = +0.4300 (higher, p = 0.001157); `is_leah` = +0.4297 (higher, p = 0.0006794); `is_rachel` = +0.4288 (higher, p = 0.001142).

**Per-coder experience (NCP) effects:** No `ncp_<coder>` term reaches p<0.05. Within this question, prior-volume count does not statistically predict pair agreement for any single coder.

**Top 3 volume effects by p-value (vs. Vol 95 reference):** `vol_94` = -0.0394 (p = 0.0432 *); `vol_130` = +0.1046 (p = 0.4857); `vol_131` = +0.1028 (p = 0.5137).

**Largest contributor to explained variance:** `is_brian` (31.8% of model SS, F = 28.78, p = 5.311e-06).

## 7. Caveats

- **Sample size:** N = 65 with k = 29 predictors leaves 35 residual df. Adequate but not generous.
- **R² is centered standard R² here** (the 5 coder dummies sum to a constant, giving an implicit intercept). Adjusted R² is the more honest fit indicator given k ≈ N/2.
- **Multicollinearity expected:** the 5 coder dummies sum to 2 per row (a structural constraint), and NCP values are correlated with the corresponding coder indicators by construction (NCP > 0 ⇒ coder in pair). Some VIF inflation is design-induced, not a bug.
- **Target ceiling effect:** `pct_agreement` is heavily skewed toward 1.0. Effects are compressed by the bounded scale.
- **Q3 is conditional on Q1:** Rows where Q1 disagreed feed into this analysis; downstream agreement may inherit Q1 disagreement structure.
