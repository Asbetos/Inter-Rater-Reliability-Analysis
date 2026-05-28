from conftest import MINI_DRIVE_DIR
import openpyxl

import completeness


def _load(name):
    return openpyxl.load_workbook(MINI_DRIVE_DIR / name, read_only=True, data_only=True)


def test_volume_a_passes():
    wb = _load("Volume-A_complete.xlsx")
    result = completeness.check(wb, threshold=0.80)
    assert result["passes"] is True
    assert result["reason"] == "ok"
    assert "33 agreement" in result["agreement_sheets"]
    assert result["coder_fill_fractions"]["Leah"] == 1.0
    assert result["coder_fill_fractions"]["Alia"] == 1.0


def test_volume_b_two_agreements_passes():
    wb = _load("Volume-B_two_agreements.xlsx")
    result = completeness.check(wb, threshold=0.80)
    assert result["passes"] is True
    assert sorted(result["agreement_sheets"]) == ["310 agreement", "38 agreement"]


def test_volume_c_incomplete_fails_due_to_coder_fill():
    wb = _load("Volume-C_incomplete.xlsx")
    result = completeness.check(wb, threshold=0.80)
    assert result["passes"] is False
    assert "Alia" in result["reason"] or result["reason"].startswith("coder_")
    assert result["coder_fill_fractions"]["Alia"] < 0.80


def test_volume_d_no_agreement_fails():
    wb = _load("Volume-D_no_agreement.xlsx")
    result = completeness.check(wb, threshold=0.80)
    assert result["passes"] is False
    assert result["reason"] == "no_agreement_sheet"
    assert result["agreement_sheets"] == []
