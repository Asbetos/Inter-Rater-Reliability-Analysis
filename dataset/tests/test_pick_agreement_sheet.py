from datetime import datetime, timezone

import pick_agreement_sheet as pas


def test_simple_two_agreement_picks_earliest():
    drive_mtime = datetime(2025, 10, 15, tzinfo=timezone.utc)
    result = pas.pick(
        sheet_names=["38 agreement", "310 agreement"],
        drive_mtime=drive_mtime,
        overrides={},
        volume_id="X",
    )
    assert result["chosen_sheet"] == "38 agreement"
    assert result["chosen_date"].month == 3
    assert result["chosen_date"].day == 8
    assert result["manual_review"] is False


def test_override_wins_unconditionally():
    drive_mtime = datetime(2025, 10, 15, tzinfo=timezone.utc)
    result = pas.pick(
        sheet_names=["38 agreement", "310 agreement"],
        drive_mtime=drive_mtime,
        overrides={"X": "310 agreement"},
        volume_id="X",
    )
    assert result["chosen_sheet"] == "310 agreement"
    assert result["manual_review"] is False


def test_ambiguous_sheet_resolved_by_mtime():
    # "115" could be Jan 15 or Nov 5. Drive mtime is Jan 20 -- only Jan 15 valid.
    drive_mtime = datetime(2025, 1, 20, tzinfo=timezone.utc)
    result = pas.pick(
        sheet_names=["115 agreement"],
        drive_mtime=drive_mtime,
        overrides={},
        volume_id="X",
    )
    assert result["chosen_sheet"] == "115 agreement"
    assert result["chosen_date"].month == 1
    assert result["chosen_date"].day == 15


def test_truly_ambiguous_flags_manual_review():
    # Drive mtime Dec 31 -- both Jan 15 and Nov 5 are valid candidates
    drive_mtime = datetime(2025, 12, 31, tzinfo=timezone.utc)
    result = pas.pick(
        sheet_names=["115 agreement"],
        drive_mtime=drive_mtime,
        overrides={},
        volume_id="X",
    )
    assert result["manual_review"] is True
    assert "ambiguous" in result["manual_review_reason"]


def test_no_candidates_flags_manual_review():
    drive_mtime = datetime(2025, 3, 15, tzinfo=timezone.utc)
    result = pas.pick(
        sheet_names=["agreement v.2"],
        drive_mtime=drive_mtime,
        overrides={},
        volume_id="X",
    )
    assert result["chosen_sheet"] is None
    assert result["manual_review"] is True


def test_multi_sheet_with_ambiguous_chosen_sheet_flags_manual_review():
    # Drive mtime Dec 31 -- "115" candidates are Jan 15 AND Nov 5 (both valid).
    # Internal resolution picks the latest <= mtime, i.e. Nov 5.
    # The OTHER sheet "1215" (Dec 15) is unambiguous but LATER than Nov 5.
    # Best (earliest) chosen_sheet is therefore "115 agreement" (Nov 5).
    # But "115" is internally ambiguous, so should flag manual_review.
    drive_mtime = datetime(2025, 12, 31, tzinfo=timezone.utc)
    result = pas.pick(
        sheet_names=["115 agreement", "1215 agreement"],
        drive_mtime=drive_mtime,
        overrides={},
        volume_id="X",
    )
    assert result["chosen_sheet"] is not None
    assert result["manual_review"] is True
    assert "ambiguous" in result["manual_review_reason"]


def test_empty_sheets_flags_manual_review():
    drive_mtime = datetime(2025, 3, 15, tzinfo=timezone.utc)
    result = pas.pick(
        sheet_names=[],
        drive_mtime=drive_mtime,
        overrides={},
        volume_id="X",
    )
    assert result["chosen_sheet"] is None
    assert result["manual_review"] is True
    assert result["manual_review_reason"] == "no_agreement_sheets"
