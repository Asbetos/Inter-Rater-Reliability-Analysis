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
