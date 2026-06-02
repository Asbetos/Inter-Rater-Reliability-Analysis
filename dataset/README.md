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

---

## v2 dataset — agreement-boolean methodology

A parallel builder (`build_dataset_from_agreements.py`) produces an IRR dataset using a stricter, simpler methodology than v1:

- **Inputs:** only the boolean `q1.agree` … `q7.agree` columns from each volume's chosen agreement sheet, plus the `Assignment` sheet for coder-pair attribution.
- **Volumes:** restricted to a 20-volume whitelist (see `volume_whitelist.VOLUME_WHITELIST_SUBSTRINGS`).
- **Sheet selection:** 5 volumes have hardcoded sheet overrides (Vol 61 → `"104 agreement"`, Vol 62 → `"115 agreement"`, Vol 63 → `"104 agreement"`, Vol 134 - Part I → `"109 agreement"`, Vol 134 - Part 2 → `"104 agreement"`). All others fall back to the same earliest-by-date heuristic v1 uses.
- **Metric:** raw % agreement per (coder, volume, question) — no chance-correction, no Cohen's κ. An agreement-sheet row contributes a disagreement when its `qN.agree` value is `False`.
- **Coder attribution:** each disagreement is attributed to whichever coder(s) the Assignment sheet says were assigned to that `order.num`.
- **Fallback for missing Assignment sheets:** if a workbook has no Assignment sheet (e.g., Volume 134 - Part I), the builder derives the coder→order mapping from the agreement sheet's bare coder-indicator columns (a column named exactly `"Leah"`, `"Alia"`, etc., with `"1"` on rows that coder coded).
- **Dual-schema Assignment parser:** handles both the `Coder | Rows ("1-400") | #Count` layout (Vol 109 and similar) and the `Coder | start | stop | start | stop | ...` layout with repeated `(start, stop)` pairs for multiple disjoint ranges per coder (Vol 134 - Part 2).

### v2 outputs

| File | Contents |
|---|---|
| `outputs/irr_dataset_v2_per_coder.csv` (+ `.parquet`) | One row per (coder, volume, question) |
| `outputs/irr_dataset_v2_per_pair.csv` (+ `.parquet`) | One row per (coder_a, coder_b, volume, question) — only pairs with row overlap |
| `outputs/irr_dataset_v2_metadata.csv` | Per-volume audit trail (chosen_sheet, chosen_date, drive_mtime, n_orders_in_agreement_sheet, coders_in_assignment) |
| `outputs/irr_dataset_v2_errors.csv` | (Only present if any volume errored) |

### v2 vs v1 — when to use which

- **v2** is closer to what the team intended per the 2026-05-28 spec: simple raw-agreement-rate counts from the official precomputed `qN.agree` booleans.
- **v1** (per-coder-cells methodology) is retained for comparison; it computes Cohen's κ, Krippendorff α, and leave-one-out variants that v2 cannot because v2 only sees booleans.

### Running v2

```bash
/home/G39248410/citizen_voice/venv/bin/python -m dataset.build_dataset_from_agreements \
    --drive-folder-id 1SJmgLW_6NjGLwZOT873LxDinFSwVqGRA \
    --credentials /home/G39248410/.config/citizen_voice_irr/credentials.json \
    --output-dir outputs/
```

CLI flags:
- `--drive-folder-id` (required) — the Google Drive folder ID containing the volume workbooks
- `--credentials` (required) — path to the OAuth `credentials.json`
- `--token` (default `~/.config/citizen_voice_irr/token.json`) — path to the cached OAuth token
- `--output-dir` (default `outputs`) — directory to write the CSV/Parquet files

### v2 schema — per-coder

| Column | Type | Meaning |
|---|---|---|
| `coder` | str | One of: Alia, Brian, Bridget, Leah, Rachel |
| `volume` | str | Canonical label (e.g., `Volume 91`, `Volume 134 - Part 2`) |
| `question` | str | `Q1`..`Q7` (some volumes only have Q1-Q6) |
| `n_assigned_orders` | int | Rows in the agreement sheet that this coder was assigned to AND that have a `qN.agree` value for this Q |
| `n_disagreements` | int | Of those, count where `qN.agree == False` |
| `pct_agreement` | float | `(n_assigned_orders - n_disagreements) / n_assigned_orders` |
| `number_coded_prior` | int | Count of OTHER volumes this coder participated in whose `agreement_sheet_date` is strictly earlier (tie-broken by volume label) |
| `agreement_sheet_date` | date | The earliest-agreement-sheet date used for this volume |
| `is_legacy_volume` | bool | `True` for volumes ≤ 63 (Vol 61, Vol 62 in this dataset; Vol 63 not in whitelist) |
| `chosen_sheet` | str | Audit: which agreement sheet name was actually read |

### v2 schema — per-pair

| Column | Type | Meaning |
|---|---|---|
| `coder_a`, `coder_b` | str | Pair, alphabetized |
| `volume` | str | as above |
| `question` | str | as above |
| `n_overlap_orders` | int | Orders assigned to BOTH coders (intersection) |
| `n_disagreements` | int | Of those, count where `qN.agree == False` |
| `pct_agreement` | float | `(n_overlap - n_disagreements) / n_overlap` |
| `number_coded_prior_a`, `number_coded_prior_b` | int | Per-coder experience counts |
| `agreement_sheet_date`, `is_legacy_volume`, `chosen_sheet` | as above |

### Running the regression on v2 data

```python
import pandas as pd
import statsmodels.formula.api as smf
import numpy as np

df = pd.read_csv("outputs/irr_dataset_v2_per_coder.csv")

# Focus on Q1 (largest N, binary)
df_q1 = df[df.question == "Q1"].dropna(subset=["pct_agreement"])

# Linear experience term
model = smf.ols(
    "pct_agreement ~ C(coder) + C(volume) + number_coded_prior",
    data=df_q1,
).fit()
print(model.summary())

# Non-linear (log) experience term
model_log = smf.ols(
    "pct_agreement ~ C(coder) + C(volume) + np.log1p(number_coded_prior)",
    data=df_q1,
).fit()
print(model_log.summary())
```

### v2 known limitations

- **Volume 133 has zero per-pair rows.** Its Assignment sheet gives Alia 100 orders and Rachel 41 orders with no overlap between their assigned ranges, so no pair comparison is possible. Per-coder rows are still emitted for both.
- **`number_coded_prior` has minor inversions** for volumes that share an `agreement_sheet_date`. The sort is `(date, volume_label)` so ties are broken alphabetically by label, not by volume number. Inversions are small (1–2 positions) and only affect coders with multiple same-date volumes.
- **No chance correction.** `pct_agreement` is uncorrected — a question where 95% of answers are "no" trivially scores 0.95 even with random coders. To get Cohen's κ you need v1.
- **Q2–Q5 are conditional on Q1 = yes** in the underlying coding rubric, so their `n_assigned_orders` per (coder, volume) is much smaller than Q1/Q6/Q7. Regression on Q2–Q5 alone will be underpowered.
- **`q1.rest.*` columns are NOT used** in v2's IRR computation — they would only confirm Q1-level participation, but the bare coder indicator columns already serve that purpose for the fallback.
