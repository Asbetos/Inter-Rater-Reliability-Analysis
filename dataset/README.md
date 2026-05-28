# IRR Dataset Build

Produces a longitudinal inter-rater-reliability (IRR) dataset from Citizen Voice coder workbooks on Google Drive, ready for regression analysis of coder experience effects.

## What this builds

Two CSVs in `--output-dir` (default `outputs/`):

- **`irr_dataset_per_coder.csv`** — one row per `(volume, coder, question)`. Carries two IRR variants for that coder on that question: leave-one-out raw agreement (Variant A) and mean pairwise Cohen's kappa (Variant B), plus the experience covariate.
- **`irr_dataset_per_pair.csv`** — one row per `(volume, coder_a, coder_b, question)`. Carries the third IRR variant: pairwise Cohen's kappa (Variant C), plus per-side experience covariates.

A `dataset_metadata.csv` is also emitted (one row per volume) recording which agreement sheet was chosen and its assigned date.

Three IRR variants:

| Variant | Where | Definition |
|---|---|---|
| A. leave-one-out | per-coder | % of eligible orders where this coder matches the modal answer of the other coders |
| B. mean pairwise kappa | per-coder | mean of this coder's Cohen kappa against each peer (non-NaN values) |
| C. pairwise kappa | per-pair | Cohen kappa between two specific coders |

## One-time setup

1. Create a Google Cloud project and enable the **Google Drive API**.
2. Create **OAuth client ID** credentials of type *Desktop app*; download as `credentials.json`.
3. Phase A — kick off the PKCE flow, which prints an authorization URL and stashes a PKCE code verifier:
   ```bash
   python -m dataset.auth --credentials /home/G39248410/.config/citizen_voice_irr/credentials.json
   ```
4. Phase B — open the URL in a browser, grant Drive read access, copy the `code=` value from the localhost redirect URL, and paste it back via `--code`:
   ```bash
   python -m dataset.auth --credentials /home/G39248410/.config/citizen_voice_irr/credentials.json --code 4/0A...
   ```
   The refresh token lands at `~/.config/citizen_voice_irr/token.json` (or `--token <path>`). Subsequent runs do not require the browser.

## How to run

All commands accept either Drive (`--drive-folder-id <id> --credentials <path>`) or a local mirror for testing (`--local-root <path>`).

### `check-completeness` — eligibility inspection

First pass. Walks Drive, runs per-coder fill-rate against the completeness threshold (default `0.05`), and writes `completeness_report.csv`. Use this to see which volumes will be picked up before paying for the full pipeline.

```bash
python -m dataset.build_dataset check-completeness \
    --drive-folder-id 1SJmgLW_6NjGLwZOT873LxDinFSwVqGRA \
    --credentials /home/G39248410/.config/citizen_voice_irr/credentials.json \
    --output-dir /home/G39248410/citizen_voice/Code/irr_analysis/outputs
```

### `pick-sheets` — date-disambiguation review

Runs the agreement-sheet picker against complete volumes and emits `agreement_sheet_picks.csv` plus `manual_review.csv`. Use this to inspect ambiguous date cases and add overrides before running `compute`.

```bash
python -m dataset.build_dataset pick-sheets \
    --local-root /home/G39248410/citizen_voice/drive_mirror \
    --output-dir /home/G39248410/citizen_voice/Code/irr_analysis/outputs
```

### `compute` — full pipeline

End-to-end: walk → completeness → pick → IRR → join `number_coded_prior` → write CSVs (and Parquet siblings).

```bash
python -m dataset.build_dataset compute \
    --drive-folder-id 1SJmgLW_6NjGLwZOT873LxDinFSwVqGRA \
    --credentials /home/G39248410/.config/citizen_voice_irr/credentials.json \
    --overrides /home/G39248410/citizen_voice/Code/irr_analysis/dataset/agreement_sheet_overrides.yaml \
    --output-dir /home/G39248410/citizen_voice/Code/irr_analysis/outputs
```

## Output schema

### `irr_dataset_per_coder.csv`

| Column | Type | Meaning |
|---|---|---|
| `coder` | str | Coder identifier (sheet name) |
| `volume` | str | Volume id (workbook stem) |
| `question` | str | Question id (Q1...Qn) |
| `irr_leave_one_out` | float | Variant A: % agreement with modal peer answer; NaN if no eligible orders |
| `irr_mean_pairwise_kappa` | float | Variant B: mean Cohen kappa across peers; NaN if no defined pair |
| `n_orders_eligible` | int | Orders where this coder and at least one peer are both non-blank |
| `n_disagreements` | int | Orders where this coder differs from the modal peer answer |
| `agreement_sheet_date` | str (ISO) | Date assigned to the volume's chosen agreement sheet |
| `is_legacy_volume` | bool | True when the volume's number is ≤ 63 (the legacy identifier-format cohort) |
| `number_coded_prior` | int | Count of volumes this coder participated in with an earlier `agreement_sheet_date` |

### `irr_dataset_per_pair.csv`

| Column | Type | Meaning |
|---|---|---|
| `coder_a` | str | Lexicographically smaller coder id |
| `coder_b` | str | Lexicographically larger coder id |
| `volume` | str | Volume id |
| `question` | str | Question id |
| `irr_pairwise_kappa` | float | Variant C: Cohen kappa between a and b; NaN if no overlap |
| `n_overlap_orders` | int | Orders where both a and b are non-blank |
| `n_disagreements` | int | Orders where a's token differs from b's |
| `agreement_sheet_date` | str (ISO) | Volume's chosen agreement sheet date |
| `is_legacy_volume` | bool | Legacy cohort flag |
| `number_coded_prior_a` | int | Prior-volume count for coder a |
| `number_coded_prior_b` | int | Prior-volume count for coder b |

## `number_coded_prior` interpretation

The count of prior cross-checks a coder had completed before this volume's agreement sheet. Acts as a coarse experience covariate.

**Timing caveat.** We use the *team's* first cross-check date (the chosen agreement sheet date) as a proxy for each coder's individual completion date. A coder who finished their pass weeks before another may receive the same date stamp. Treat `number_coded_prior` as an ordering signal, not a precise time-since-coding measurement.

## Handling `manual_review.csv`

The picker writes a row to `manual_review.csv` when it cannot confidently pick a single agreement sheet. Reasons:

- `no_agreement_sheets` — no candidate sheets matched the recognition heuristic.
- `no_valid_dates` — candidates exist but none had a parseable date and Drive mtime fallback failed.
- `ambiguous_date_for_<sheet>` — date encoding heuristic returned multiple plausible dates for the chosen sheet.

Resolve by adding an override keyed by `volume_id` (workbook stem) mapping to the exact sheet name to use. The overrides file is a **flat map** of `volume_id: sheet_name`. Edit `dataset/agreement_sheet_overrides.yaml`:

```yaml
# Flat map: volume_id (workbook stem) -> sheet name to pin.
"Volume-131": "11"
"2025-06-17 first coding check : Volume 134 - Part I": "109 agreement"
```

Re-run `pick-sheets` to confirm the override clears the entry, then run `compute`.

## Running the regression

```python
import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv("outputs/irr_dataset_per_coder.csv")

# Filter to one question at a time (optional)
df_q1 = df[df.question == "Q1"]

# Linear: experience term assumed constant per volume coded
model = smf.ols(
    "irr_leave_one_out ~ C(coder) + C(volume) + number_coded_prior",
    data=df_q1.dropna(subset=["irr_leave_one_out"]),
).fit()
print(model.summary())

# Non-linear (log) experience term
import numpy as np
model_log = smf.ols(
    "irr_leave_one_out ~ C(coder) + C(volume) + np.log1p(number_coded_prior)",
    data=df_q1.dropna(subset=["irr_leave_one_out"]),
).fit()
print(model_log.summary())
```

Swap `irr_leave_one_out` for `irr_mean_pairwise_kappa` to fit Variant B; load `irr_dataset_per_pair.csv` and use `irr_pairwise_kappa ~ C(coder_a) + C(coder_b) + C(volume) + number_coded_prior_a + number_coded_prior_b` for Variant C.

## Known limitations

- **Q4/Q5 multi-label questions** are reduced to a single comma-joined sorted token; agreement is strict set-equality, not partial overlap. A coder who picks `{A, B}` vs `{A}` counts as a full disagreement.
- **Completeness calibration.** The default `--completeness-threshold` is `0.05` (very permissive), reflecting that real coder sheets carry the full law inventory but only a small fraction of rows are actually coded. The `_coder_fill_fraction` heuristic uses a **Selection-aware denominator**: when the coder sheet has a `Selection` column, only rows with `Selection == 1` count toward the denominator. Without a `Selection` column it falls back to all data rows. Operators may need to tune `--completeness-threshold` based on the cohort.
- **Agreement-sheet-date heuristic** can misfire on free-form sheet names. Use `agreement_sheet_overrides.yaml` to correct.
- **`number_coded_prior` shares one date per volume** across all coders on it (see caveat above) — it approximates rather than measures individual coding history.
- **Brian appears only in some legacy volumes** (`is_legacy_volume == True`). Treat his coder fixed effect with caution; cells against current-era coders are mostly empty.

## Files in this directory

| File | Role |
|---|---|
| `auth.py` | OAuth installed-app device flow; token persistence |
| `drive_source.py` | `LocalDriveSource` and `OAuthDriveSource` abstractions |
| `drive_walk.py` | List volume workbooks under a folder |
| `completeness.py` | Per-coder fill-rate check against the threshold |
| `tracking_oracle.py` | Resolves volume status against the project tracking sheet |
| `parse_agreement_sheet.py` | Heuristics to identify agreement sheets and extract dates |
| `pick_agreement_sheet.py` | Single-sheet selection + manual_review emission |
| `irr_per_volume.py` | Computes the three IRR variants on one workbook |
| `number_coded.py` | Builds the `(volume, coder) -> prior count` map |
| `build_dataset.py` | CLI orchestrator (`check-completeness`, `pick-sheets`, `compute`) |

## Pointer to spec + plan

- Spec: `/home/G39248410/docs/superpowers/specs/2026-05-26-irr-dataset-design.md`
- Plan: `/home/G39248410/docs/superpowers/plans/2026-05-26-irr-dataset.md`
