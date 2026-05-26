# IRR Analysis (citizen_voice)

Single-volume inter-rater reliability pilot. Computes per-question IRR metrics from a `cross_q_check_volNNN_*.xlsx` workbook and produces Excel + Markdown reports.

## Why

The team is preparing to benchmark an LLM against the law-RA codings of U.S. federal statutes. For any question, the LLM's accuracy ceiling is bounded by the inter-rater reliability between the human coders: if humans agree only 70% of the time on Q4, no LLM can exceed ~70% on Q4 against either coder individually. This package computes those ceilings, per question, from the earliest pre-consensus snapshot of a volume.

## Design and plan

- Spec: `/home/G39248410/docs/superpowers/specs/2026-05-26-irr-pilot-design.md`
- Build plan: `/home/G39248410/docs/superpowers/plans/2026-05-26-irr-pilot.md`

## How to run

```bash
/home/G39248410/citizen_voice/venv/bin/python compute_irr.py \
    --input /groups/brooksgrp/citizen_voice/r_output/cross_check_classification/cross_q_check_vol134p2_second_pass_20251005.xlsx \
    --output-xlsx outputs/irr_report_vol134p2_20251005.xlsx \
    --output-md outputs/irr_report_vol134p2_20251005.md
```

To run on a different snapshot, replace the `--input` path. For each volume, **use the earliest cross_q_check snapshot** (smaller date suffix) — later snapshots include reconciliation and inflate IRR.

## How to test

```bash
/home/G39248410/citizen_voice/venv/bin/pytest -v
```

To rebuild the test fixture:

```bash
/home/G39248410/citizen_voice/venv/bin/python tests/build_fixture.py
```

## Output sheets

| Sheet | What it tells you |
|---|---|
| `summary` | Per-question table: N, raw % agreement, mean pairwise Cohen κ, Krippendorff α, ceiling band, underpowered flag |
| `pairwise_kappa` | Cohen κ for each (coder_a, coder_b, question) triple |
| `disagreements` | Every row where coders disagreed, with each coder's answer side by side |
| `metadata` | Source path, generation timestamp, ceiling-band definitions |

## Interpreting the ceiling

Krippendorff's α is the primary summary statistic. Bands follow Landis & Koch (1977):

- α < 0.4 — **poor**: the question's intent is ambiguous; refine the rubric before benchmarking the LLM
- 0.4 ≤ α < 0.6 — **moderate**: usable benchmark, but report LLM accuracy alongside the human ceiling
- 0.6 ≤ α < 0.8 — **substantial**: strong benchmark; expect the LLM to approach but not exceed α
- α ≥ 0.8 — **almost perfect**: reliable benchmark; LLM should reach ≥ 0.9·α to be considered competitive

## What this pilot found (Vol 134 Part 2 Oct 5)

The first pilot run on `cross_q_check_vol134p2_second_pass_20251005.xlsx` produced surprisingly small N and near-zero α across every question. This is **not a bug** — it accurately reflects the per-coder data in that snapshot:

| Question | N (units) | Raw % agree | Krippendorff α | Reading |
|---|---|---|---|---|
| Q1 | 22 | 0.91 | ≈ 0 | Only 22 orders had ≥2 coders actually answering Q1 |
| Q2 | 0 | NaN | NaN | No order had ≥2 coders answer Q2 |
| Q3 | 0 | NaN | NaN | Same |
| Q4 | 18 | 0.00 | poor | All 18 cases are one-coder-answered, other-blank (no pairwise agreement possible) |
| Q5 | 17 | 0.00 | poor | Same pattern as Q4 |
| Q6 | 21 | 0.95 | 0.00 | Small overlap, all-no answers → Pe == 1 → α undefined → reported as 0 |

**Why so sparse?** The Oct 5 file lists four coders (Leah, Bridget, Rachel, Alia) with participation indicators, but:

- Bridget has **0 filled answer cells** across the whole file (200 indicator-rows, no actual answers entered)
- Coding pairs are non-overlapping across the volume (Leah+Alia on one half, Rachel+Bridget on the other), so cross-pair IRR is structurally impossible
- Within the Leah+Alia half, the per-question fill overlap is only ~20 rows

**The precomputed `q1.agree` column in the source file shows 398/400 (99.5%) agreement**, but that column treats *"both coders left this blank"* as agreement. The per-coder pipeline here correctly only counts rows where ≥2 coders actually answered — a stricter and more honest first-pass measure.

**What to do with this finding:**

1. **Don't anchor the LLM benchmark to this snapshot's IRR**. The N is too small to draw conclusions.
2. **Try a later snapshot** (e.g., the Oct 24 file) — but note that post-consensus IRR is artificially inflated.
3. **Verify with the original raw coder Google Sheets** if older exports exist (the cross_q_check file is itself a derived snapshot).
4. **Use the 22-row Leah+Alia subset** for downstream LLM benchmarking as a small but real sample.

## Known limitations

- Pilot scope: one volume, one snapshot (Vol 134 Part 2, Oct 5 2025). Re-run on other volumes to test generalization.
- The Oct 5 snapshot has very sparse per-coder data; the IRR pipeline accurately reports this sparsity rather than masking it via "blank == agree" conventions.
- Q2/Q3/Q4/Q5 are conditional on Q1=yes, so their N is already structurally small (only Q1=yes rows have non-blank conditional answers).
- Multi-label Q4 reports both strict and Jaccard agreement — choose the one that matches your LLM-benchmark scoring rule.
- "Earliest snapshot" may already include partial reconciliation. If raw per-coder exports with even earlier timestamps exist, verify.

## Code layout

```
irr_analysis/
├── compute_irr.py       # orchestrator + CLI
├── io_xlsx.py           # cross_q_check loader
├── normalize.py         # answer + label-set normalization
├── irr_metrics.py       # Cohen / Fleiss / Krippendorff / Jaccard (pure numpy)
├── report.py            # Excel + Markdown writers
├── tests/
│   ├── conftest.py
│   ├── build_fixture.py        # one-shot fixture generator
│   ├── fixtures/mini_cross_check.xlsx
│   ├── test_io_xlsx.py
│   ├── test_normalize.py
│   ├── test_metrics.py
│   └── test_compute_irr.py
├── outputs/             # generated reports (.gitignored except first pilot run)
└── README.md
```

## Environment

- Python 3.11 from `/home/G39248410/citizen_voice/venv/`
- No `pip install` needed — all metrics implemented from scratch in numpy/stdlib because the venv lacks `pip`
- pandas 3.x compatible (answer/notes columns explicitly object-dtype to preserve `None` vs `NaN`)
