import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import volume_overrides as vo


def test_manual_assignment_for_vol_133_alia():
    m = vo.manual_assignment_for("Volume 133")
    assert m is not None
    assert m["Alia"] == set(range(1, 201)) | {236} | set(range(300, 601))
    assert len(m["Alia"]) == 502


def test_manual_assignment_for_vol_133_rachel():
    m = vo.manual_assignment_for("Volume 133")
    assert m["Rachel"] == set(range(1, 300)) | set(range(401, 601))
    assert len(m["Rachel"]) == 499


def test_manual_assignment_for_vol_133_bridget():
    m = vo.manual_assignment_for("Volume 133")
    assert m["Bridget"] == set(range(200, 601))
    assert len(m["Bridget"]) == 401


def test_manual_assignment_triple_overlap():
    """All 3 coders on Vol 133 share orders {200, 236, 401-600} = 202 rows."""
    m = vo.manual_assignment_for("Volume 133")
    triple = m["Alia"] & m["Rachel"] & m["Bridget"]
    expected = {200, 236} | set(range(401, 601))
    assert triple == expected
    assert len(triple) == 202


def test_no_manual_assignment_for_other_volumes():
    assert vo.manual_assignment_for("Volume 109") is None
    assert vo.manual_assignment_for("Volume 134 - Part 2") is None


def test_composite_sheet_for_vol_114():
    c = vo.composite_sheet_for("Volume 114")
    assert c is not None
    assert c["alternate_sheet"] == "agreement 324"
    assert c["use_alternate_when_any_coder_in"] == frozenset({"Brian", "Rachel"})


def test_no_composite_sheet_for_other_volumes():
    assert vo.composite_sheet_for("Volume 109") is None
    assert vo.composite_sheet_for("Volume 133") is None
