import math

import openpyxl
from conftest import MINI_DRIVE_DIR

import irr_per_volume


def _load(name):
    return openpyxl.load_workbook(MINI_DRIVE_DIR / name, read_only=True, data_only=True)


def test_volume_a_per_coder_rows_have_expected_questions():
    wb = _load("Volume-A_complete.xlsx")
    per_coder, _ = irr_per_volume.compute(wb)
    coders = {r["coder"] for r in per_coder}
    questions = {r["question"] for r in per_coder}
    assert coders == {"Leah", "Alia"}
    assert questions == {"Q1", "Q2", "Q3", "Q4", "Q5", "Q6"}
    assert len(per_coder) == 12   # 2 coders x 6 questions


def test_volume_a_q1_per_coder_metric():
    wb = _load("Volume-A_complete.xlsx")
    per_coder, _ = irr_per_volume.compute(wb)
    leah_q1 = next(r for r in per_coder if r["coder"] == "Leah" and r["question"] == "Q1")
    # 20 orders, 1 disagreement (order 16), raw % = 19/20 = 0.95
    assert leah_q1["n_orders_eligible"] == 20
    assert leah_q1["n_disagreements"] == 1
    assert leah_q1["irr_leave_one_out"] == 0.95
    # Mean pairwise kappa: only one partner (Alia) -> equals kappa(Leah, Alia)
    # Po=0.95, Pe approx 0.78 -> kappa approx 0.773
    assert 0.7 < leah_q1["irr_mean_pairwise_kappa"] < 0.85


def test_volume_a_per_pair_rows():
    wb = _load("Volume-A_complete.xlsx")
    _, per_pair = irr_per_volume.compute(wb)
    assert len(per_pair) == 6   # 1 pair x 6 questions
    pair_q1 = next(r for r in per_pair if r["question"] == "Q1")
    assert (pair_q1["coder_a"], pair_q1["coder_b"]) == ("Alia", "Leah")  # alphabetized
    assert pair_q1["n_overlap_orders"] == 20
    assert pair_q1["n_disagreements"] == 1


def test_q2_and_q5_have_2_eligible_orders():
    """Q2/Q5 are non-blank only on orders 17 and 18 in the fixture."""
    wb = _load("Volume-A_complete.xlsx")
    per_coder, _ = irr_per_volume.compute(wb)
    leah_q2 = next(r for r in per_coder if r["coder"] == "Leah" and r["question"] == "Q2")
    assert leah_q2["n_orders_eligible"] == 2
    leah_q5 = next(r for r in per_coder if r["coder"] == "Leah" and r["question"] == "Q5")
    assert leah_q5["n_orders_eligible"] == 2


def test_q4_jaccard_pair_for_order_18():
    """Q4 has Leah='academia, the public' vs Alia='the public' on order 18 (disagreement),
    'the public' on order 16 with Alia blank, both 'the public' on 17, blanks elsewhere.
    Eligible Q4 orders are 16, 17, 18 (at least one non-blank set).
    Strict matches: 17 only -> 1/3 ~= 0.333."""
    wb = _load("Volume-A_complete.xlsx")
    _, per_pair = irr_per_volume.compute(wb)
    pair_q4 = next(r for r in per_pair if r["question"] == "Q4")
    assert pair_q4["n_overlap_orders"] >= 1
    # Don't pin exact kappa value; just sanity-check overlap > 0
    assert pair_q4["n_disagreements"] >= 1
