import math
import pytest

from conftest import FIXTURE_PATH
import compute_irr


@pytest.fixture(scope="module")
def result():
    return compute_irr.run(FIXTURE_PATH)


def test_result_has_top_level_keys(result):
    assert set(result.keys()) >= {"source", "n_orders", "coders_present", "per_question"}
    assert result["n_orders"] == 10
    assert set(result["coders_present"]) == {"Leah", "Rachel", "Alia"}


def test_q1_has_all_metric_fields(result):
    q1 = result["per_question"]["Q1"]
    expected_keys = {
        "type", "n_units", "raw_pct_agreement", "pairwise_cohen",
        "mean_pairwise_cohen", "krippendorff_alpha", "fleiss_kappa",
        "strict_pct_agreement", "mean_jaccard", "underpowered", "disagreements",
    }
    assert set(q1.keys()) == expected_keys
    assert q1["type"] == "binary"


def test_q1_n_units_and_agreement_match_fixture(result):
    q1 = result["per_question"]["Q1"]
    # All 10 rows have both coders non-blank on Q1; 1 disagreement (row 4).
    assert q1["n_units"] == 10
    assert q1["raw_pct_agreement"] == pytest.approx(0.9, abs=1e-9)
    # 1 disagreement row should appear in q1["disagreements"]
    assert len(q1["disagreements"]) == 1
    assert q1["disagreements"][0]["order_num"] == 4


def test_q6_n_units_and_agreement_match_fixture(result):
    q6 = result["per_question"]["Q6"]
    # All 10 rows non-blank; 1 disagreement (row 5).
    assert q6["n_units"] == 10
    assert q6["raw_pct_agreement"] == pytest.approx(0.9, abs=1e-9)
    assert q6["disagreements"][0]["order_num"] == 5


def test_q4_strict_and_jaccard_match_fixture(result):
    q4 = result["per_question"]["Q4"]
    assert q4["type"] == "multi_label"
    # Rows with at least one Q4 non-blank: 3, 4, 6, 8, 10. That's 5 units.
    # So n_units == 5. Strict matches: 3 (yes), 4 (no), 6 (no), 8 (yes), 10 (yes) -> 3 matches -> 0.6.
    assert q4["n_units"] == 5
    assert q4["strict_pct_agreement"] == pytest.approx(0.6, abs=1e-9)
    # Jaccard: row 3 = 1.0, row 4 = 0.0 (one set empty -> Jaccard of singleton vs empty = 0.0
    # since union = {the public}, intersection = {} -> 0/1 = 0.0),
    # row 6 = {academia, the public} vs {the public} -> 1/2 = 0.5,
    # row 8 = {experts} vs {experts} = 1.0,
    # row 10 = {tribes} vs {tribes} = 1.0.
    # Mean = (1.0 + 0.0 + 0.5 + 1.0 + 1.0) / 5 = 3.5/5 = 0.7
    assert q4["mean_jaccard"] == pytest.approx(0.7, abs=1e-9)


def test_q2_q3_flagged_underpowered_when_blank_only(result):
    # In the fixture Q2 and Q3 are answered only on the few Q1=yes rows
    # (orders 3, 4, 6, 8, 10) and only by participating coders. Both coders
    # answered both. So n_units > 0 but smaller — make sure the
    # "underpowered" flag is set when n_units < 30 (which it always is here).
    assert result["per_question"]["Q2"]["underpowered"] is True
    assert result["per_question"]["Q3"]["underpowered"] is True


def test_q1_pairwise_cohen_includes_leah_rachel(result):
    pairs = result["per_question"]["Q1"]["pairwise_cohen"]
    assert ("Leah", "Rachel") in pairs
    # Numeric value: Leah/Rachel coded rows 1, 2, 3, 4, 9 together (5 rows).
    # Q1 values: (no,no), (no,no), (yes,yes), (yes,no), (no,no) -> table:
    # yes/yes: 1, yes/no: 1, no/no: 3 -> Po = 4/5 = 0.8, Pe = (2/5)(1/5) + (3/5)(4/5) = 2/25 + 12/25 = 14/25
    # kappa = (0.8 - 0.56)/(1 - 0.56) = 0.24/0.44 ≈ 0.5454
    assert pairs[("Leah", "Rachel")] == pytest.approx(0.5454, abs=1e-3)
