import sys
from pathlib import Path
# build_dataset.py is at dataset/build_dataset.py; add dataset/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build_dataset


def test_is_legacy_volume_true_for_vol_61():
    assert build_dataset._is_legacy_volume("Volume-61_Coded") is True


def test_is_legacy_volume_true_for_vol_63():
    assert build_dataset._is_legacy_volume("Volume 63 - Some Suffix") is True


def test_is_legacy_volume_false_for_vol_82():
    assert build_dataset._is_legacy_volume("2026-04-13 First Coding Check _ Volume 82") is False


def test_is_legacy_volume_false_for_vol_134():
    assert build_dataset._is_legacy_volume("2025-06-17 first coding check : Volume 134 - Part I") is False


def test_is_legacy_volume_handles_bare_number_after_volume():
    assert build_dataset._is_legacy_volume("VolumeId-42") is True


def test_is_legacy_volume_false_when_no_volume_substring():
    assert build_dataset._is_legacy_volume("just_some_other_id") is False


def test_volume_id_from_filename_strips_extension():
    assert build_dataset._volume_id_from_filename("Volume-A_complete.xlsx") == "Volume-A_complete"
    assert build_dataset._volume_id_from_filename("2026-04-13 First Coding Check _ Volume 82") == "2026-04-13 First Coding Check _ Volume 82"
