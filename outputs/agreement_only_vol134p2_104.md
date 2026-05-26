# Inter-Rater Agreement Report (boolean-only)

- **Source:** `2025-06-30 Second Coding Check _ Volume 134 - Part 2.xlsx`
- **Sheet:** `104 agreement`
- **Rows in sheet:** 400
- **Coders in q1.rest columns:** Leah, Bridget, Rachel, Alia
- **Generated (UTC):** 2026-05-26T19:26:35+00:00

## Per-question agreement

| Question | N | # agree | # disagree | % agreement | Ceiling |
|---|---|---|---|---|---|
| Q1 | 400 | 398 | 2 | 0.9950 | almost perfect |
| Q2 | 400 | 400 | 0 | 1.0000 | almost perfect |
| Q3 | 400 | 400 | 0 | 1.0000 | almost perfect |
| Q4 | 400 | 400 | 0 | 1.0000 | almost perfect |
| Q5 | 400 | 400 | 0 | 1.0000 | almost perfect |
| Q6 | 400 | 399 | 1 | 0.9975 | almost perfect |

## Disagreements

### Q1 (2 rows)

| order_num | Leah | Bridget | Rachel | Alia |
|---|---|---|---|---|
| 7 | ok |  |  | ok |
| 16 | ok |  |  | ok |

### Q6 (1 row)

| order_num |
|---|
| 5 |

## Methodology

Agreement is taken directly from the workbook's precomputed `qN.agree` columns in the specified sheet. The denominator is the number of rows where the flag is True or False; rows where the flag is blank (None) are excluded. **No per-coder answer cells are read**, so chance-corrected metrics (Cohen's κ, Fleiss' κ, Krippendorff's α) and label-set agreement (Jaccard) are not computed. Ceiling bands (poor / moderate / substantial / almost perfect) use stricter thresholds than the Landis-Koch κ bands because raw % agreement is uncorrected for chance.

## Caveats

- The `qN.agree` columns may treat *'both coders left this blank'* as agreement. On conditional questions (Q2–Q5, only filled when Q1=yes), this inflates % agreement relative to a per-coder reconstruction.
- For Q1 disagreements, the `q1.rest.<coder>` columns show each coder's Q1 answer side-by-side. For Q2–Q6, only the disagreement order numbers are listed (the source sheet has no per-coder detail for those).
- For chance-corrected metrics and label-set agreement, run `compute_irr.py` against the same workbook (it reads the per-coder Q.* cells from the coder sheets instead).
