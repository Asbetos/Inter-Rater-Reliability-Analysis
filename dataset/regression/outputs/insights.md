# IRR v2 — Regression Insights (volume FE removed)

**Dataset:** `outputs/irr_dataset_v2_per_pair.csv` — 435 rows, 21 volumes, 7 questions, 8 coder slots.

**Target:** `pct_agreement`. Mean = 0.9290, std = 0.1687, min = 0.0000, max = 1.0000.

## Model variants

| Variant | R² | Adj R² | F p-value | Key coefficient: number_coded_prior_a |
|---|---|---|---|---|
| OLS (linear NCP) | 0.1938 | 0.1650 | 4.892e-13 | coef = -0.01650, p = 0.08481 |
| WLS (weighted by N) | 0.1739 | 0.1443 | 4.114e-11 | coef = -0.01485, p = 0.09286 |
| OLS (log NCP) | 0.1975 | 0.1688 | 2.113e-13 | coef = -0.01283, p = 0.6226 |

## Per-question fits

| Question | N | R² | F p-value | NCP_a coef | NCP_a p | NCP_b coef | NCP_b p |
|---|---|---|---|---|---|---|---|
| Q1 | 65 | 0.2203 | 0.1048 | -0.03718 | 0.3142 | 0.02700 | 0.4466 |
| Q2 | 65 | 0.4845 | 1.361e-05 | -0.00253 | 0.4276 | -0.00023 | 0.9393 |
| Q3 | 65 | 0.4881 | 1.148e-05 | -0.00245 | 0.4485 | -0.00045 | 0.8839 |
| Q4 | 65 | 0.4620 | 3.777e-05 | -0.00243 | 0.4765 | -0.00018 | 0.9551 |
| Q5 | 65 | 0.4836 | 1.422e-05 | -0.00221 | 0.4911 | -0.00040 | 0.8957 |
| Q6 | 65 | 0.1977 | 0.1692 | -0.03317 | 0.3693 | 0.02235 | 0.5287 |
| Q7 | 45 | 0.2669 | 0.1485 | -0.03193 | 0.7296 | 0.04438 | 0.6356 |

## Coder effects (from OLS-linear)

**Coder A dummies** (each is delta vs the reference coder):
- `C(coder_a)[T.Brian]` = -0.0502 (p = 0.456)
- `C(coder_a)[T.Bridget]` = +0.0193 (p = 0.56)
- `C(coder_a)[T.Leah]` = -0.0067 (p = 0.833)

**Coder B dummies**:
- `C(coder_b)[T.Bridget]` = -0.1652 (p = 0.00383) *
- `C(coder_b)[T.Leah]` = -0.1422 (p = 0.00429) *
- `C(coder_b)[T.Rachel]` = -0.1254 (p = 0.0838)

## Volume effects

**Volume fixed effects have been removed from this model** to recover the cross-volume variance in `number_coded_prior` that was previously absorbed. Volume-level variation now flows into the residual + the experience and legacy-volume coefficients. To control for volume difficulty in this spec, use `n_overlap_orders` as a regression weight (see WLS variant) or add `is_legacy_volume` as a partial proxy.

## Experience effect (key research question)

`number_coded_prior_a` coefficient = **-0.01650** (p = 0.08481, **NOT significant** at α=0.05).
This is a **negative** effect: every additional volume coder_a had completed prior is associated with a 0.01650 change in `pct_agreement`.

`number_coded_prior_b` coefficient = **+0.01155** (p = 0.2102, **NOT significant** at α=0.05).
Direction: **positive**.

In the log-experience variant, `log_ncp_a` coefficient = -0.01283 (p = 0.6226). If this fits notably better than linear (Adj R² goes up), there's diminishing returns to experience.

## Legacy volumes (Vol ≤ 63)

`is_legacy_volume` coefficient = +0.04718 (p = 0.1349). This may be unstable because volume fixed effects already absorb most volume-level variation; the legacy flag adds little orthogonal information unless many legacy volumes existed (we have 3: Vol 61, 62, 63).

## Caveats

- **Multicollinearity**: volume fixed effects absorb most of `number_coded_prior` variance because volume order is tightly correlated with experience. The remaining NCP signal is the cross-coder variation in experience on the same volume.
- **No chance correction**: `pct_agreement` is raw % agreement; high values on questions like Q1 where one answer dominates can be misleading. The v3 build (Cohen's κ) is the next step.
- **Asymmetric pair encoding**: `coder_a` is always alphabetically before `coder_b`, so `coder_a == Brian` only happens for pairs where Brian is alphabetically first (he's first vs Bridget, Leah, Rachel — but Alia is first vs Brian). The two coder dummies are NOT independent — they're paired with each other.
- **Small samples**: some (volume, question, pair) cells have `n_overlap_orders < 5`. The WLS variant down-weights these.

## Suggested next steps

1. Re-run with Cohen's κ as the target (requires the v3 build that reads per-coder Q-answer cells).
2. Try interaction terms: `coder_a × question`, `volume × question`.
3. Mixed-effects model treating coder as a random effect (e.g., `Mixedlm`).
4. Filter to `n_overlap_orders >= 30` and refit to see if the experience effect strengthens.