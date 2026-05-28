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


def test_ties_broken_by_volume_id():
    participations = [
        ("V1", "Leah", date(2025, 1, 1)),
        ("V2", "Leah", date(2025, 1, 1)),  # same date as V1
        ("V3", "Leah", date(2025, 2, 1)),
    ]
    result = number_coded.compute(participations)
    # V1 < V2 lexicographically, so V1 comes first
    assert result[("V1", "Leah")] == 0
    assert result[("V2", "Leah")] == 1
    assert result[("V3", "Leah")] == 2


def test_empty_input_returns_empty_dict():
    assert number_coded.compute([]) == {}


def test_single_volume_single_coder():
    result = number_coded.compute([("V1", "Leah", date(2025, 1, 1))])
    assert result == {("V1", "Leah"): 0}
