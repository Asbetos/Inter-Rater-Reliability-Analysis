# Inter-Rater Reliability Report

- **Source:** `cross_q_check_vol134p2_second_pass_20251005.xlsx`
- **Orders in workbook:** 400
- **Coders present:** Alia, Bridget, Leah, Rachel
- **Generated (UTC):** 2026-05-26T18:47:21+00:00

## Per-question summary

| Question | Type | N (units) | Raw % agree | Mean Cohen κ | Krippendorff α | Ceiling | Underpowered? |
|---|---|---|---|---|---|---|---|
| Q1 | binary | 22 | 0.9091 | 0.0000 | -0.0238 | poor | yes |
| Q2 | binary | 0 | NaN | NaN | NaN | n/a | yes |
| Q3 | binary | 0 | NaN | NaN | NaN | n/a | yes |
| Q6 | binary | 21 | 0.9524 | 0.0000 | 0.0000 | poor | yes |
| Q4 | multi_label | 18 | 0.0000 | -0.1550 | -0.3462 | poor | yes |
| Q5 | compound_categorical | 17 | 0.0000 | -0.2200 | -0.4311 | poor | yes |

## Per-question detail

### Q1 — binary

- N units: 22 (underpowered if <30: yes)
- Raw % agreement: 0.9091
- Pairwise Cohen κ:
  - Alia vs Bridget: NaN
  - Alia vs Leah: 0.0000
  - Alia vs Rachel: NaN
  - Bridget vs Leah: NaN
  - Bridget vs Rachel: NaN
  - Leah vs Rachel: NaN
- Krippendorff α: -0.0238
- Disagreement rows (2): see `disagreements` sheet

### Q2 — binary

- N units: 0 (underpowered if <30: yes)
- Raw % agreement: NaN
- Pairwise Cohen κ:
  - Alia vs Bridget: NaN
  - Alia vs Leah: NaN
  - Alia vs Rachel: NaN
  - Bridget vs Leah: NaN
  - Bridget vs Rachel: NaN
  - Leah vs Rachel: NaN
- Krippendorff α: NaN

### Q3 — binary

- N units: 0 (underpowered if <30: yes)
- Raw % agreement: NaN
- Pairwise Cohen κ:
  - Alia vs Bridget: NaN
  - Alia vs Leah: NaN
  - Alia vs Rachel: NaN
  - Bridget vs Leah: NaN
  - Bridget vs Rachel: NaN
  - Leah vs Rachel: NaN
- Krippendorff α: NaN

### Q6 — binary

- N units: 21 (underpowered if <30: yes)
- Raw % agreement: 0.9524
- Pairwise Cohen κ:
  - Alia vs Bridget: NaN
  - Alia vs Leah: 0.0000
  - Alia vs Rachel: NaN
  - Bridget vs Leah: NaN
  - Bridget vs Rachel: NaN
  - Leah vs Rachel: NaN
- Krippendorff α: 0.0000
- Disagreement rows (1): see `disagreements` sheet

### Q4 — multi_label

- Strict % agreement: 0.0000
- Mean Jaccard: 0.0000
- N units: 18 (underpowered if <30: yes)
- Raw % agreement: 0.0000
- Pairwise Cohen κ:
  - Alia vs Bridget: NaN
  - Alia vs Leah: -0.3101
  - Alia vs Rachel: NaN
  - Bridget vs Leah: NaN
  - Bridget vs Rachel: 0.0000
  - Leah vs Rachel: NaN
- Krippendorff α: -0.3462
- Disagreement rows (18): see `disagreements` sheet

### Q5 — compound_categorical

- Strict % agreement: 0.0000
- Mean Jaccard: 0.0000
- N units: 17 (underpowered if <30: yes)
- Raw % agreement: 0.0000
- Pairwise Cohen κ:
  - Alia vs Bridget: NaN
  - Alia vs Leah: -0.4400
  - Alia vs Rachel: NaN
  - Bridget vs Leah: NaN
  - Bridget vs Rachel: 0.0000
  - Leah vs Rachel: NaN
- Krippendorff α: -0.4311
- Disagreement rows (17): see `disagreements` sheet

## Methodology

Inter-rater reliability is computed from the per-coder answer columns of the cross_q_check workbook, not from the precomputed `qN.agree` flags. For binary questions (Q1, Q2, Q3, Q6), units are included where at least two coders gave non-blank answers. For multi-label / compound questions (Q4, Q5), units are included where at least one coder gave a non-empty answer set; both strict (exact-match) and lenient (Jaccard) agreement are reported. The Krippendorff α and ceiling-band columns are the recommended summary statistics: bands are < 0.4 poor; 0.4–0.6 moderate; 0.6–0.8 substantial; ≥ 0.8 almost perfect (Landis & Koch 1977, applied to α).

## Caveats

- Pilot on a single volume and single (earliest) snapshot.
- Q2/Q3/Q4/Q5 are conditional on Q1=yes; their N is small and the underpowered flag is set if N < 30.
- Multi-label Q4 has two views (strict and Jaccard); choose the one that matches your LLM-benchmark scoring rule.
- The earliest snapshot may already include partial reconciliation; verify against any older raw-coder exports if available.
