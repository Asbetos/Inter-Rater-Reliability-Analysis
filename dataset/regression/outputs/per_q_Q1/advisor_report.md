# IRR Per-Question Regression — Q1

**Research question:** Within this single question, do per-coder agreement levels and per-coder coding experience (`number_coded_prior`) predict inter-rater agreement, after controlling for volume?

**Subsample:** N = 65 (coder-pair × volume) rows where `question == Q1`. Volumes represented: 21 of 21. Mean `pct_agreement` = 0.8878 (min 0.000, max 1.000).

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
| N (observations) | 65 | filtered to question Q1 |
| k (predictors) | 29 | no intercept |
| Residual df | 35 | OK |
| R² | 0.6720 | centered R² (implicit-constant design) |
| Adjusted R² | 0.4002 | k-penalized variant |
| F-statistic | 2.47 | joint significance of all predictors |
| F p-value | 0.005641 | |
| RMSE | 0.1384 | typical residual on pct_agreement |
| MAE | 0.0875 | mean absolute residual |
| AIC | -12.6 | |
| BIC | 52.6 | |
| Condition number | 3805.49 | >30 = moderate collinearity; >100 = severe |

## 2. Variance decomposition (Type II ANOVA)

| Term | df | F | p-value | % of model SS | % of total SS |
|---|---|---|---|---|---|
| `ncp_rachel` | 1 | 2.31 | 0.1373  | 4.7% | 2.7% |
| `vol_62` | 1 | 2.24 | 0.1437  | 4.5% | 2.6% |
| `vol_63` | 1 | 2.22 | 0.1451  | 4.5% | 2.6% |
| `vol_134_part_2` | 1 | 2.20 | 0.1465  | 4.4% | 2.6% |
| `vol_61` | 1 | 2.20 | 0.1469  | 4.4% | 2.6% |
| `vol_131` | 1 | 2.20 | 0.1469  | 4.4% | 2.6% |
| `ncp_alia` | 1 | 2.20 | 0.1473  | 4.4% | 2.6% |
| `ncp_leah` | 1 | 2.19 | 0.148  | 4.4% | 2.6% |
| `vol_133` | 1 | 2.17 | 0.1498  | 4.4% | 2.6% |
| `vol_132` | 1 | 2.16 | 0.1504  | 4.4% | 2.6% |
| `vol_134_part_i` | 1 | 2.08 | 0.1586  | 4.2% | 2.5% |
| `vol_127` | 1 | 1.98 | 0.1681  | 4.0% | 2.3% |
| `vol_126` | 1 | 1.96 | 0.1708  | 3.9% | 2.3% |
| `ncp_bridget` | 1 | 1.90 | 0.1773  | 3.8% | 2.2% |
| `vol_109` | 1 | 1.79 | 0.1898  | 3.6% | 2.1% |
| `vol_130` | 1 | 1.75 | 0.1949  | 3.5% | 2.1% |
| `vol_93` | 1 | 1.55 | 0.2216  | 3.1% | 1.8% |
| `vol_120` | 1 | 1.53 | 0.2245  | 3.1% | 1.8% |
| `vol_122` | 1 | 1.52 | 0.2252  | 3.1% | 1.8% |
| `vol_91` | 1 | 1.52 | 0.226  | 3.1% | 1.8% |
| `vol_124` | 1 | 1.37 | 0.2504  | 2.8% | 1.6% |
| `ncp_brian` | 1 | 1.36 | 0.2517  | 2.7% | 1.6% |
| `is_leah` | 1 | 1.35 | 0.2529  | 2.7% | 1.6% |
| `is_bridget` | 1 | 1.32 | 0.2579  | 2.7% | 1.6% |
| `is_alia` | 1 | 1.31 | 0.26  | 2.6% | 1.5% |
| `is_rachel` | 1 | 1.21 | 0.279  | 2.4% | 1.4% |
| `vol_94` | 1 | 0.69 | 0.4105  | 1.4% | 0.8% |
| `vol_114` | 1 | 0.57 | 0.454  | 1.2% | 0.7% |
| `vol_119` | 1 | 0.40 | 0.5327  | 0.8% | 0.5% |
| `is_brian` | 1 | 0.40 | 0.5336  | 0.8% | 0.5% |

## 3. Coefficient table

| Term | Coef | Std Err | t | p-value | 95% CI | Sig |
|---|---|---|---|---|---|---|
| `is_alia` | -1.66037 | 1.45002 | -1.15 | 0.26 | [-4.6041, +1.2833] |  |
| `is_brian` | -0.60426 | 0.96103 | -0.63 | 0.5336 | [-2.5552, +1.3467] |  |
| `is_bridget` | -1.65974 | 1.44302 | -1.15 | 0.2579 | [-4.5892, +1.2697] |  |
| `is_leah` | -1.59093 | 1.36849 | -1.16 | 0.2529 | [-4.3691, +1.1872] |  |
| `is_rachel` | -1.58026 | 1.43700 | -1.10 | 0.279 | [-4.4975, +1.3370] |  |
| `ncp_alia` | +0.11817 | 0.07974 | +1.48 | 0.1473 | [-0.0437, +0.2801] |  |
| `ncp_brian` | +0.09591 | 0.08228 | +1.17 | 0.2517 | [-0.0711, +0.2630] |  |
| `ncp_bridget` | +0.11965 | 0.08689 | +1.38 | 0.1773 | [-0.0568, +0.2960] |  |
| `ncp_leah` | +0.13083 | 0.08844 | +1.48 | 0.148 | [-0.0487, +0.3104] |  |
| `ncp_rachel` | +0.10601 | 0.06970 | +1.52 | 0.1373 | [-0.0355, +0.2475] |  |
| `vol_109` | +1.29335 | 0.96731 | +1.34 | 0.1898 | [-0.6704, +3.2571] |  |
| `vol_114` | +0.61686 | 0.81467 | +0.76 | 0.454 | [-1.0370, +2.2707] |  |
| `vol_119` | +0.41711 | 0.66197 | +0.63 | 0.5327 | [-0.9268, +1.7610] |  |
| `vol_120` | +2.09954 | 1.69789 | +1.24 | 0.2245 | [-1.3474, +5.5464] |  |
| `vol_122` | +2.09621 | 1.69789 | +1.23 | 0.2252 | [-1.3507, +5.5431] |  |
| `vol_124` | +1.32410 | 1.13303 | +1.17 | 0.2504 | [-0.9761, +3.6243] |  |
| `vol_126` | +1.79836 | 1.28617 | +1.40 | 0.1708 | [-0.8127, +4.4094] |  |
| `vol_127` | +2.01009 | 1.42824 | +1.41 | 0.1681 | [-0.8894, +4.9096] |  |
| `vol_130` | +2.32879 | 1.76218 | +1.32 | 0.1949 | [-1.2486, +5.9062] |  |
| `vol_131` | +2.74500 | 1.85057 | +1.48 | 0.1469 | [-1.0118, +6.5018] |  |
| `vol_132` | +2.95733 | 2.01148 | +1.47 | 0.1504 | [-1.1262, +7.0408] |  |
| `vol_133` | +4.01782 | 2.72811 | +1.47 | 0.1498 | [-1.5206, +9.5562] |  |
| `vol_134_part_2` | +4.22512 | 2.84552 | +1.48 | 0.1465 | [-1.5516, +10.0018] |  |
| `vol_134_part_i` | +3.30892 | 2.29696 | +1.44 | 0.1586 | [-1.3542, +7.9720] |  |
| `vol_61` | +3.81141 | 2.56897 | +1.48 | 0.1469 | [-1.4039, +9.0267] |  |
| `vol_62` | +3.24966 | 2.17249 | +1.50 | 0.1437 | [-1.1607, +7.6600] |  |
| `vol_63` | +3.82891 | 2.56897 | +1.49 | 0.1451 | [-1.3864, +9.0442] |  |
| `vol_91` | +0.42891 | 0.34804 | +1.23 | 0.226 | [-0.2777, +1.1355] |  |
| `vol_93` | +0.63479 | 0.51008 | +1.24 | 0.2216 | [-0.4007, +1.6703] |  |
| `vol_94` | +0.18575 | 0.22300 | +0.83 | 0.4105 | [-0.2670, +0.6385] |  |

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

**Top 3 volume effects by p-value (vs. Vol 95 reference):** `vol_62` = +3.2497 (p = 0.1437); `vol_63` = +3.8289 (p = 0.1451); `vol_134_part_2` = +4.2251 (p = 0.1465).

**Largest contributor to explained variance:** `ncp_rachel` (4.7% of model SS, F = 2.31, p = 0.1373).

## 7. Caveats

- **Sample size:** N = 65 with k = 29 predictors leaves 35 residual df. Adequate but not generous.
- **No-intercept R² is uncentered:** do not compare these R² values to centered R² from intercept-bearing OLS models. Use the F p-value or the variance decomposition to gauge fit.
- **Multicollinearity expected:** the 5 coder dummies sum to 2 per row (a structural constraint), and NCP values are correlated with the corresponding coder indicators by construction (NCP > 0 ⇒ coder in pair). Some VIF inflation is design-induced, not a bug.
- **Target ceiling effect:** `pct_agreement` is heavily skewed toward 1.0. Effects are compressed by the bounded scale.
