# Per-Question OLS — Cross-Question Summary

Seven OLS regressions, one per question, on the v2 per-pair dataset's one-hot encoding. Design: no intercept (`~ 0 + ...`), all five coder dummies included, Vol 95 as the implicit reference volume.

> **R² note:** Although the formula has no intercept, the 5 coder dummies sum to a constant per row, so statsmodels detects an implicit constant and reports the standard **centered R²**. The numbers below are directly comparable to ordinary OLS R².

## 1. Headline table

| Question | N | k | df_resid | R² (centered) | Adj R² | F p-value | RMSE |
|---|---|---|---|---|---|---|---|
| Q1 | 65 | 29 | 35 | 0.6720 | 0.4002 | 0.005641 | 0.1384 |
| Q2 | 65 | 29 | 35 | 0.8005 | 0.6352 | 8.027e-06 | 0.0115 |
| Q3 | 65 | 29 | 35 | 0.8015 | 0.6371 | 7.454e-06 | 0.0117 |
| Q4 | 65 | 29 | 35 | 0.7859 | 0.6085 | 2.196e-05 | 0.0125 |
| Q5 | 65 | 29 | 35 | 0.7953 | 0.6256 | 1.165e-05 | 0.0117 |
| Q6 | 65 | 29 | 35 | 0.6853 | 0.4246 | 0.003463 | 0.1338 |
| Q7 | 45 | 20 | 24 | 0.6499 | 0.3581 | 0.03141 | 0.1632 |

## 2. Coder coefficients across questions (`is_<coder>`)

Bold + asterisk marks p < 0.05.

| Coder | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 |
|---|---|---|---|---|---|---|---|
| Alia | -1.6604 | **+0.4783\*** | **+0.4205\*** | **+0.4556\*** | **+0.4380\*** | -1.8007 | -0.0778 |
| Brian | -0.6043 | **+0.4662\*** | **+0.4342\*** | **+0.4557\*** | **+0.4439\*** | -0.7147 | **+0.5472\*** |
| Bridget | -1.6597 | **+0.4871\*** | **+0.4300\*** | **+0.4634\*** | **+0.4487\*** | -1.8300 | -0.2030 |
| Leah | -1.5909 | **+0.4869\*** | **+0.4297\*** | **+0.4624\*** | **+0.4462\*** | -1.7226 | +0.0463 |
| Rachel | -1.5803 | **+0.4858\*** | **+0.4288\*** | **+0.4627\*** | **+0.4485\*** | -1.7396 | +0.3703 |

## 3. Per-coder NCP coefficients across questions (`ncp_<coder>`)

Bold + asterisk marks p < 0.05. **Significant NCP = experience effect for that coder on that question.**

| Coder | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 |
|---|---|---|---|---|---|---|---|
| Alia | +0.11817 | +0.00064 | +0.00377 | +0.00171 | +0.00276 | +0.12498 | +0.03093 |
| Brian | +0.09591 | +0.00272 | +0.00561 | +0.00315 | +0.00420 | +0.10368 | -0.00214 |
| Bridget | +0.11965 | -0.00020 | +0.00339 | +0.00166 | +0.00236 | +0.12987 | +0.03741 |
| Leah | +0.13083 | -0.00050 | +0.00329 | +0.00114 | +0.00201 | +0.13951 | +0.02559 |
| Rachel | +0.10601 | +0.00038 | +0.00318 | +0.00161 | +0.00229 | +0.11249 | +0.00705 |

## 4. Top 3 volume effects per question (by p-value)

| Question | Top 3 `vol_*` (term, coef, p) |
|---|---|
| Q1 | `vol_62` (+3.250, p=0.144); `vol_63` (+3.829, p=0.145); `vol_134_part_2` (+4.225, p=0.147) |
| Q2 | `vol_94` (-0.042, p=0.0311*); `vol_91` (-0.016, p=0.592); `vol_119` (-0.026, p=0.634) |
| Q3 | `vol_94` (-0.039, p=0.0432*); `vol_130` (+0.105, p=0.486); `vol_131` (+0.103, p=0.514) |
| Q4 | `vol_94` (-0.048, p=0.0233*); `vol_93` (-0.017, p=0.716); `vol_62` (+0.065, p=0.743) |
| Q5 | `vol_94` (-0.043, p=0.0285*); `vol_130` (+0.076, p=0.614); `vol_62` (+0.089, p=0.631) |
| Q6 | `vol_62` (+3.484, p=0.106); `vol_134_part_2` (+4.536, p=0.108); `vol_63` (+4.089, p=0.109) |
| Q7 | `vol_119` (-0.333, p=0.0236*); `vol_114` (-0.296, p=0.0322*); `vol_127` (+0.257, p=0.0352*) |

## 5. Plain-language interpretation per question

### Q1

- N = 65, residual df = 35, R² = 0.6720, F p = 0.005641.
- No coder-presence dummy reaches p < 0.05.
- No per-coder NCP reaches p < 0.05 — no detectable single-coder experience effect.

### Q2

- N = 65, residual df = 35, R² = 0.8005, F p = 8.027e-06.
- **is_alia** (higher agreement contribution, coef = +0.4783, p = 0.0003403).
- **is_brian** (higher agreement contribution, coef = +0.4662, p = 1.26e-06).
- **is_bridget** (higher agreement contribution, coef = +0.4871, p = 0.0002607).
- **is_leah** (higher agreement contribution, coef = +0.4869, p = 0.000137).
- **is_rachel** (higher agreement contribution, coef = +0.4858, p = 0.0002557).
- No per-coder NCP reaches p < 0.05 — no detectable single-coder experience effect.

### Q3

- N = 65, residual df = 35, R² = 0.8015, F p = 7.454e-06.
- **is_alia** (higher agreement contribution, coef = +0.4205, p = 0.001507).
- **is_brian** (higher agreement contribution, coef = +0.4342, p = 5.311e-06).
- **is_bridget** (higher agreement contribution, coef = +0.4300, p = 0.001157).
- **is_leah** (higher agreement contribution, coef = +0.4297, p = 0.0006794).
- **is_rachel** (higher agreement contribution, coef = +0.4288, p = 0.001142).
- No per-coder NCP reaches p < 0.05 — no detectable single-coder experience effect.

### Q4

- N = 65, residual df = 35, R² = 0.7859, F p = 2.196e-05.
- **is_alia** (higher agreement contribution, coef = +0.4556, p = 0.001324).
- **is_brian** (higher agreement contribution, coef = +0.4557, p = 7.126e-06).
- **is_bridget** (higher agreement contribution, coef = +0.4634, p = 0.001067).
- **is_leah** (higher agreement contribution, coef = +0.4624, p = 0.000632).
- **is_rachel** (higher agreement contribution, coef = +0.4627, p = 0.00104).
- No per-coder NCP reaches p < 0.05 — no detectable single-coder experience effect.

### Q5

- N = 65, residual df = 35, R² = 0.7953, F p = 1.165e-05.
- **is_alia** (higher agreement contribution, coef = +0.4380, p = 0.001032).
- **is_brian** (higher agreement contribution, coef = +0.4439, p = 3.816e-06).
- **is_bridget** (higher agreement contribution, coef = +0.4487, p = 0.0007679).
- **is_leah** (higher agreement contribution, coef = +0.4462, p = 0.0004614).
- **is_rachel** (higher agreement contribution, coef = +0.4485, p = 0.0007383).
- No per-coder NCP reaches p < 0.05 — no detectable single-coder experience effect.

### Q6

- N = 65, residual df = 35, R² = 0.6853, F p = 0.003463.
- No coder-presence dummy reaches p < 0.05.
- No per-coder NCP reaches p < 0.05 — no detectable single-coder experience effect.

### Q7

- N = 45, residual df = 24, R² = 0.6499, F p = 0.03141.
- **is_brian** (higher agreement contribution, coef = +0.5472, p = 0.000544).
- No per-coder NCP reaches p < 0.05 — no detectable single-coder experience effect.

## 6. Caveats

- **Sample sizes are small (~60 per Q, ~45 for Q7) relative to ~30 predictors.** Residual df is typically ~30 — adequate but not generous. Q7 is the most underpowered.
- **R² is centered (standard) here**, because the coder dummies sum to a constant (implicit intercept). Per-question Adj R² values in the 0.36–0.64 range mean the design captures a substantial but far-from-complete share of the variance.
- **Multicollinearity is structural:** the 5 coder dummies sum to 2 per row, and NCP is non-zero only when the corresponding coder is in the pair. Some VIF inflation is by construction, not a flaw.
- **Q7 low-power warning:** only ~45 rows; individual coefficient significance is very fragile. Treat any single-Q7 finding as preliminary.
- **Ceiling-bounded target:** `pct_agreement` ∈ [0, 1] with most mass near 1.0; effect sizes are compressed and skewness is non-trivial. Cohen's κ would have a wider range and likely more signal.
- **Volume reference = Vol 95.** All `vol_*` coefficients are deltas vs. Vol 95. Choice of reference is arbitrary; alternative references would relabel coefficients but not change overall model fit.
