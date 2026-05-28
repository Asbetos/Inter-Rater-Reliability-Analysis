import parse_agreement_sheet as pas


def test_two_digit_md():
    assert pas.candidate_dates("33 agreement") == [(3, 3)]
    assert pas.candidate_dates("agreement 38") == [(3, 8)]
    assert pas.candidate_dates("28 agreement") == [(2, 8)]


def test_three_digit_mdd_or_mmd():
    # "310" -- most likely Mar 10 (MDD)
    assert (3, 10) in pas.candidate_dates("310 agreement")
    # "115" is genuinely ambiguous: Jan 15 (MDD) or Nov 5 (MMD)
    cands = pas.candidate_dates("115 agreement")
    assert (1, 15) in cands or (11, 5) in cands


def test_four_digit_mmdd():
    assert pas.candidate_dates("1024 agreement") == [(10, 24)]
    assert pas.candidate_dates("agreement 1121") == [(11, 21)]


def test_sheet_without_digits_returns_empty():
    assert pas.candidate_dates("agreement") == []
    assert pas.candidate_dates("agreement v.2") == []


def test_extracts_digits_anywhere():
    assert pas.candidate_dates("agreement 33 v.2") == [(3, 3)]
    assert pas.candidate_dates("104 agreement") == [(1, 4)]
