import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import date

import volume_ordering as vo


def test_table_has_21_entries():
    assert len(vo.AUTHORITATIVE_DATES) == 21


def test_134_part_2_date():
    assert vo.authoritative_date_for("Volume 134 - Part 2") == date(2025, 4, 10)


def test_vol_61_date():
    assert vo.authoritative_date_for("Volume 61") == date(2025, 10, 4)


def test_vol_63_date():
    assert vo.authoritative_date_for("Volume 63") == date(2025, 10, 4)


def test_vol_61_and_63_share_date():
    """Same authoritative date -> competition ranking will tie them."""
    assert vo.authoritative_date_for("Volume 61") == vo.authoritative_date_for("Volume 63")


def test_vol_62_date():
    assert vo.authoritative_date_for("Volume 62") == date(2025, 11, 5)


def test_134_part_I_date():
    assert vo.authoritative_date_for("Volume 134 - Part I") == date(2025, 10, 9)


def test_vol_120_and_122_share_date():
    assert vo.authoritative_date_for("Volume 120") == vo.authoritative_date_for("Volume 122")
    assert vo.authoritative_date_for("Volume 120") == date(2026, 1, 15)


def test_unknown_volume_returns_none():
    assert vo.authoritative_date_for("Volume 999") is None


def test_chronological_order_matches_user_table():
    """Sort the table by date and verify the order matches the user's Order column."""
    expected_order = [
        "Volume 134 - Part 2",
        "Volume 133",
        "Volume 61",
        "Volume 63",                 # same date as Vol 61; alphabetic tie-break
        "Volume 134 - Part I",
        "Volume 62",
        "Volume 132",
        "Volume 131",
        "Volume 130",
        "Volume 120",   # same-date with 122; alphabetic tie-break
        "Volume 122",
        "Volume 127",
        "Volume 126",
        "Volume 124",
        "Volume 109",
        "Volume 114",
        "Volume 119",
        "Volume 93",
        "Volume 91",
        "Volume 94",
        "Volume 95",
    ]
    actual = sorted(vo.AUTHORITATIVE_DATES.items(), key=lambda kv: (kv[1], kv[0]))
    assert [name for name, _ in actual] == expected_order
