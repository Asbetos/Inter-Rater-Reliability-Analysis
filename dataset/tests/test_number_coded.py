from datetime import date

import number_coded


def test_simple_timeline_per_coder():
    participations = [
        ("V1", "Leah", date(2025, 1, 1)),
        ("V2", "Leah", date(2025, 2, 1)),
        ("V3", "Leah", date(2025, 3, 1)),
        ("V1", "Alia", date(2025, 1, 1)),
        ("V3", "Alia", date(2025, 3, 1)),
    ]
    result = number_coded.compute(participations)
    assert result[("V1", "Leah")] == 0
    assert result[("V2", "Leah")] == 1
    assert result[("V3", "Leah")] == 2
    assert result[("V1", "Alia")] == 0
    assert result[("V3", "Alia")] == 1  # only V1 was earlier; Alia didn't do V2


def test_ties_get_same_rank_competition_ranking():
    """Tied dates produce SAME number_coded_prior (competition ranking).
    Next non-tied volume skips ahead by the tie-group size."""
    participations = [
        ("V1", "Leah", date(2025, 1, 1)),
        ("V2", "Leah", date(2025, 1, 1)),  # same date as V1
        ("V3", "Leah", date(2025, 2, 1)),
    ]
    result = number_coded.compute(participations)
    # V1 and V2 are tied -> both 0; V3 skips to 2 (because two volumes had
    # strictly-earlier-than V3's date)
    assert result[("V1", "Leah")] == 0
    assert result[("V2", "Leah")] == 0
    assert result[("V3", "Leah")] == 2


def test_three_way_tie_skips_three():
    """Three volumes tied -> all 0, next gets 3."""
    participations = [
        ("V1", "Leah", date(2025, 1, 1)),
        ("V2", "Leah", date(2025, 1, 1)),
        ("V3", "Leah", date(2025, 1, 1)),
        ("V4", "Leah", date(2025, 2, 1)),
    ]
    result = number_coded.compute(participations)
    assert result[("V1", "Leah")] == 0
    assert result[("V2", "Leah")] == 0
    assert result[("V3", "Leah")] == 0
    assert result[("V4", "Leah")] == 3


def test_tie_in_middle_of_sequence():
    """Ties can occur anywhere; subsequent items still count all earlier ones."""
    participations = [
        ("V0", "Leah", date(2025, 1, 1)),
        ("V1", "Leah", date(2025, 2, 1)),
        ("V2", "Leah", date(2025, 2, 1)),
        ("V3", "Leah", date(2025, 3, 1)),
    ]
    result = number_coded.compute(participations)
    assert result[("V0", "Leah")] == 0
    assert result[("V1", "Leah")] == 1   # only V0 is strictly earlier
    assert result[("V2", "Leah")] == 1   # only V0 is strictly earlier (V1 is tied, not earlier)
    assert result[("V3", "Leah")] == 3   # V0, V1, V2 all strictly earlier


def test_empty_input_returns_empty_dict():
    assert number_coded.compute([]) == {}


def test_single_volume_single_coder():
    result = number_coded.compute([("V1", "Leah", date(2025, 1, 1))])
    assert result == {("V1", "Leah"): 0}
