import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import openpyxl
import pytest

import assignment_sheet


# ---------- Schema A helpers (single 'Rows' column) ----------

def _build_schema_a(tmp_path, sheet_name, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.append(["Coder", "Rows", "#Count"])
    for r in rows:
        ws.append(r)
    fpath = tmp_path / f"{sheet_name}.xlsx"
    wb.save(fpath)
    return openpyxl.load_workbook(fpath, read_only=True, data_only=True)


def test_schema_a_simple_two_coder(tmp_path):
    wb = _build_schema_a(tmp_path, "Assignment", [
        ("Leah", "1-200", 200),
        ("Alia", "1-200", 200),
    ])
    result = assignment_sheet.parse(wb)
    assert result["Leah"] == set(range(1, 201))
    assert result["Alia"] == set(range(1, 201))


def test_schema_a_multiple_coders_different_ranges(tmp_path):
    wb = _build_schema_a(tmp_path, "Assignment", [
        ("Alia", "1-400", 400),
        ("Rachel", "1-300", 300),
        ("Brian", "301-600", 300),
        ("Bridget", "401-500", 100),
    ])
    result = assignment_sheet.parse(wb)
    assert result["Alia"] == set(range(1, 401))
    assert result["Rachel"] == set(range(1, 301))
    assert result["Brian"] == set(range(301, 601))
    assert result["Bridget"] == set(range(401, 501))


def test_schema_a_en_dash_in_range(tmp_path):
    wb = _build_schema_a(tmp_path, "Assignment", [
        ("Leah", "1–200", 200),
    ])
    result = assignment_sheet.parse(wb)
    assert result["Leah"] == set(range(1, 201))


def test_schema_a_skips_unknown_coder_names(tmp_path):
    wb = _build_schema_a(tmp_path, "Assignment", [
        ("Leah", "1-100", 100),
        ("SOMETOTAL", "1-100", 100),
        ("", "150-200", 50),
    ])
    result = assignment_sheet.parse(wb)
    assert "Leah" in result
    assert "SOMETOTAL" not in result
    assert "" not in result


def test_schema_a_lowercase_assignments_sheet_name(tmp_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "assignments"
    ws.append(["Coder", "Rows", "#Count"])
    ws.append(("Leah", "1-100", 100))
    fpath = tmp_path / "lc.xlsx"
    wb.save(fpath)
    wb2 = openpyxl.load_workbook(fpath, read_only=True, data_only=True)
    result = assignment_sheet.parse(wb2)
    assert result["Leah"] == set(range(1, 101))


# ---------- Schema B helpers (numeric start/stop columns, possibly repeated) ----------

def _build_schema_b(tmp_path, sheet_name, rows, n_pairs=2):
    """Build a workbook whose Assignment sheet has the start/stop schema.

    `rows` is a list of (coder, [(start, stop), ...]) tuples. `n_pairs` is
    the maximum number of (start, stop) pairs in any row - defines the
    header width.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name
    header = ["Coder"] + ["start", "stop"] * n_pairs
    ws.append(header)
    for coder, ranges in rows:
        row = [coder]
        for i in range(n_pairs):
            if i < len(ranges):
                row.extend([ranges[i][0], ranges[i][1]])
            else:
                row.extend([None, None])
        ws.append(row)
    fpath = tmp_path / f"{sheet_name}.xlsx"
    wb.save(fpath)
    return openpyxl.load_workbook(fpath, read_only=True, data_only=True)


def test_schema_b_single_range_per_coder(tmp_path):
    wb = _build_schema_b(tmp_path, "assignments", [
        ("Bridget", [(1, 200)]),
        ("Rachel", [(200, 400)]),
    ], n_pairs=2)
    result = assignment_sheet.parse(wb)
    assert result["Bridget"] == set(range(1, 201))
    assert result["Rachel"] == set(range(200, 401))


def test_schema_b_multiple_disjoint_ranges_per_coder(tmp_path):
    wb = _build_schema_b(tmp_path, "assignments", [
        ("Alia", [(1, 100), (300, 400)]),       # two disjoint ranges
        ("Leah", [(1, 22), (100, 299)]),
        ("Bridget", [(1, 200)]),                # only one range; 2nd pair None
        ("Rachel", [(200, 400)]),
    ], n_pairs=2)
    result = assignment_sheet.parse(wb)
    assert result["Alia"] == set(range(1, 101)) | set(range(300, 401))
    assert result["Leah"] == set(range(1, 23)) | set(range(100, 300))
    assert result["Bridget"] == set(range(1, 201))
    assert result["Rachel"] == set(range(200, 401))


def test_schema_b_three_pair_header(tmp_path):
    """Future-proof: 3 (start, stop) column pairs."""
    wb = _build_schema_b(tmp_path, "Assignment", [
        ("Alia", [(1, 50), (100, 150), (300, 400)]),
    ], n_pairs=3)
    result = assignment_sheet.parse(wb)
    assert result["Alia"] == set(range(1, 51)) | set(range(100, 151)) | set(range(300, 401))


def test_schema_b_skips_unknown_coder_names(tmp_path):
    wb = _build_schema_b(tmp_path, "Assignment", [
        ("Leah", [(1, 100)]),
        ("Unknown", [(1, 100)]),
    ], n_pairs=2)
    result = assignment_sheet.parse(wb)
    assert "Leah" in result
    assert "Unknown" not in result


def test_schema_b_invalid_start_gt_stop_skipped(tmp_path):
    wb = _build_schema_b(tmp_path, "Assignment", [
        ("Leah", [(1, 100), (500, 200)]),   # second range is invalid (start > stop)
    ], n_pairs=2)
    result = assignment_sheet.parse(wb)
    assert result["Leah"] == set(range(1, 101))   # only the valid range


# ---------- Cross-schema and edge cases ----------

def test_no_assignment_sheet_returns_empty(tmp_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "SomeOtherSheet"
    fpath = tmp_path / "no_assign.xlsx"
    wb.save(fpath)
    wb2 = openpyxl.load_workbook(fpath, read_only=True, data_only=True)
    result = assignment_sheet.parse(wb2)
    assert result == {}


def test_empty_assignment_sheet_returns_empty(tmp_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Assignment"
    # only header, no data rows
    ws.append(["Coder", "Rows", "#Count"])
    fpath = tmp_path / "empty.xlsx"
    wb.save(fpath)
    wb2 = openpyxl.load_workbook(fpath, read_only=True, data_only=True)
    result = assignment_sheet.parse(wb2)
    assert result == {}
