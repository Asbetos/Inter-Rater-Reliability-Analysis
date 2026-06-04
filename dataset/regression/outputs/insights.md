# IRR v2 — Initial Regression Insights

**Dataset:** `outputs/irr_dataset_v2_per_pair.csv` — 435 rows, 21 volumes, 7 questions, 8 coder slots.

**Target:** `pct_agreement`. Mean = 0.9290, std = 0.1687, min = 0.0000, max = 1.0000.

## Model variants

| Variant | R² | Adj R² | F p-value | Key coefficient: number_coded_prior_a |
|---|---|---|---|---|
| OLS (linear NCP) | 0.3805 | 0.3279 | 3.408e-25 | coef = 0.00887, p = 0.7296 |
| WLS (weighted by N) | 0.3323 | 0.2755 | 1.322e-19 | coef = 0.01087, p = 0.6178 |
| OLS (log NCP) | 0.3784 | 0.3256 | 6.215e-25 | coef = 0.01079, p = 0.8002 |

## Per-question fits

| Question | N | R² | F p-value | NCP_a coef | NCP_a p | NCP_b coef | NCP_b p |
|---|---|---|---|---|---|---|---|
| Q1 | 65 | 0.6527 | 0.006615 | 0.02549 | 0.7781 | 0.04877 | 0.2792 |
| Q2 | 65 | 0.7849 | 1.049e-05 | 0.00208 | 0.7834 | 0.00271 | 0.4706 |
| Q3 | 65 | 0.7971 | 4.434e-06 | 0.00359 | 0.632 | 0.00258 | 0.4866 |
| Q4 | 65 | 0.7927 | 6.095e-06 | 0.00066 | 0.9329 | 0.00192 | 0.6191 |
| Q5 | 65 | 0.7940 | 5.563e-06 | 0.00252 | 0.7345 | 0.00248 | 0.502 |
| Q6 | 65 | 0.6625 | 0.004703 | 0.03047 | 0.7293 | 0.04779 | 0.2759 |
| Q7 | 45 | 0.6226 | 0.03517 | -0.01298 | 0.8725 | 0.04435 | 0.6195 |

## Coder effects (from OLS-linear)

**Coder A dummies** (each is delta vs the reference coder):
- `C(coder_a)[T.Brian]` = +0.1167 (p = 0.468)
- `C(coder_a)[T.Bridget]` = -0.0012 (p = 0.974)
- `C(coder_a)[T.Leah]` = +0.0024 (p = 0.965)

**Coder B dummies**:
- `C(coder_b)[T.Bridget]` = -0.2365 (p = 0.00151) *
- `C(coder_b)[T.Leah]` = -0.1855 (p = 0.00334) *
- `C(coder_b)[T.Rachel]` = -0.2115 (p = 0.0352) *

## Volume effects (top 5 most + least)

**Lowest 5** (associated with LOWER pct_agreement, controlling for everything else):
- Volume 119 → -0.2618 (p = 0.000477)
- Volume 114 → -0.2423 (p = 1.03e-06)
- Volume 95 → -0.1632 (p = 0.401)
- Volume 94 → -0.1601 (p = 0.329)
- Volume 91 → -0.1179 (p = 0.373)

**Highest 5** (associated with HIGHER pct_agreement):
- Volume 131 → +0.2480 (p = 0.161)
- Volume 132 → +0.2684 (p = 0.196)
- Volume 134 - Part I → +0.3015 (p = 0.28)
- Volume 133 → +0.4154 (p = 0.244)
- Volume 134 - Part 2 → +0.4448 (p = 0.234)

## Experience effect (key research question)

`number_coded_prior_a` coefficient = **+0.00887** (p = 0.7296, **NOT significant** at α=0.05).
This is a **positive** effect: every additional volume coder_a had completed prior is associated with a 0.00887 change in `pct_agreement`.

`number_coded_prior_b` coefficient = **+0.02312** (p = 0.07119, **NOT significant** at α=0.05).
Direction: **positive**.

In the log-experience variant, `log_ncp_a` coefficient = +0.01079 (p = 0.8002). If this fits notably better than linear (Adj R² goes up), there's diminishing returns to experience.

## Legacy volumes (Vol ≤ 63)

`is_legacy_volume` coefficient = +0.27889 (p = 0.198). This may be unstable because volume fixed effects already absorb most volume-level variation; the legacy flag adds little orthogonal information unless many legacy volumes existed (we have 3: Vol 61, 62, 63).

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