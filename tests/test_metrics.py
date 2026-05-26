import math
import pytest
import irr_metrics


# --- Cohen's kappa ---

def test_cohen_kappa_textbook_example():
    a = ["yes", "yes", "no"]
    b = ["yes", "no",  "no"]
    # Hand-computed: Po=2/3, Pe=4/9, kappa=0.4
    assert irr_metrics.cohen_kappa(a, b) == pytest.approx(0.4, abs=1e-9)


def test_cohen_kappa_perfect_agreement():
    a = ["yes", "no", "yes", "no"]
    assert irr_metrics.cohen_kappa(a, a) == pytest.approx(1.0, abs=1e-9)


def test_cohen_kappa_zero_when_at_chance():
    # 4 rows: AB pairs (yes,no), (no,yes), (yes,no), (no,yes).
    # Marginal A = [yes:2, no:2]; Marginal B = [yes:2, no:2]. Po=0, Pe=0.5, kappa = -1.
    a = ["yes", "no", "yes", "no"]
    b = ["no",  "yes","no",  "yes"]
    assert irr_metrics.cohen_kappa(a, b) == pytest.approx(-1.0, abs=1e-9)


def test_cohen_kappa_handles_one_class_only():
    # Both raters always say "no" -> Po=1, Pe=1, kappa is undefined; return NaN.
    a = ["no"] * 5
    b = ["no"] * 5
    assert math.isnan(irr_metrics.cohen_kappa(a, b))


def test_cohen_kappa_drops_pairs_with_None():
    a = ["yes", "yes", None, "no"]
    b = ["yes", "no",  "yes", "no"]
    # Effective pairs are (yes,yes), (yes,no), (no,no) -> same as textbook -> 0.4
    assert irr_metrics.cohen_kappa(a, b) == pytest.approx(0.4, abs=1e-9)


# --- Fleiss' kappa ---

def test_fleiss_kappa_textbook_example():
    # 3 raters, 4 units, 2 categories ('yes', 'no')
    # N[i] = counts per category per unit
    counts = [
        [3, 0],
        [2, 1],
        [1, 2],
        [0, 3],
    ]
    # Hand-computed: 1/3
    assert irr_metrics.fleiss_kappa(counts) == pytest.approx(1/3, abs=1e-9)


def test_fleiss_kappa_perfect_agreement():
    counts = [
        [3, 0],
        [3, 0],
        [0, 3],
    ]
    assert irr_metrics.fleiss_kappa(counts) == pytest.approx(1.0, abs=1e-9)


def test_fleiss_kappa_raises_on_uneven_rater_count():
    counts = [
        [3, 0],
        [2, 0],  # only 2 raters for unit 2
    ]
    with pytest.raises(ValueError):
        irr_metrics.fleiss_kappa(counts)


def test_fleiss_kappa_returns_nan_when_one_category():
    counts = [
        [3, 0],
        [3, 0],
        [3, 0],
    ]
    # All units in category 0 -> Pe == 1 -> undefined
    assert math.isnan(irr_metrics.fleiss_kappa(counts))


# --- Krippendorff's alpha (nominal) ---

def test_krippendorff_alpha_published_example():
    """Hand-derived nominal-alpha example: two raters, four units, four categories.

    Matrix (rows=units, cols=raters):
        unit 1: 1, 1
        unit 2: 1, 1
        unit 3: 2, 2
        unit 4: 3, 4

    Coincidence marginals: n_c = [4, 2, 1, 1], n_total = 8.
    D_o = 2/8 = 0.25.
    D_e = (sum_{i!=j} n_c[i]*n_c[j]) / (n_total*(n_total-1)) = 42/56 = 0.75.
    alpha = 1 - D_o/D_e = 1 - 1/3 = 2/3 ≈ 0.6667.
    """
    matrix = [
        ["1", "1"],
        ["1", "1"],
        ["2", "2"],
        ["3", "4"],
    ]
    a = irr_metrics.krippendorff_alpha_nominal(matrix)
    assert a == pytest.approx(2/3, abs=1e-9)


def test_krippendorff_alpha_perfect():
    matrix = [
        ["yes", "yes", "yes"],
        ["no",  "no",  "no"],
    ]
    assert irr_metrics.krippendorff_alpha_nominal(matrix) == pytest.approx(1.0, abs=1e-9)


def test_krippendorff_alpha_handles_missing_per_unit():
    # Unit 1 has only 1 rater -> contributes nothing
    # Unit 2 has 2 raters in agreement
    # Unit 3 has 2 raters in disagreement
    matrix = [
        ["yes", None, None],
        ["yes", "yes", None],
        ["yes", None, "no"],
    ]
    # Should return a finite number (not NaN), exercising the per-unit
    # missing-data handling.
    result = irr_metrics.krippendorff_alpha_nominal(matrix)
    assert not math.isnan(result)


def test_krippendorff_alpha_nan_when_no_pairs():
    # Every unit has < 2 raters -> no pairs -> NaN
    matrix = [
        ["yes", None],
        [None,  "no"],
    ]
    assert math.isnan(irr_metrics.krippendorff_alpha_nominal(matrix))
