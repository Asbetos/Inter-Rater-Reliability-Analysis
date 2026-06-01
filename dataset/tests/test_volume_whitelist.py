import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import volume_whitelist as vw


def test_whitelist_count():
    assert len(vw.VOLUME_WHITELIST_SUBSTRINGS) == 20


def test_match_volume_91_filename():
    assert vw.match_volume("2026-03-20 First Coding Check _ Volume 91") == "Volume 91"


def test_match_volume_134_part_2_filename():
    assert vw.match_volume("2025-06-30 Second Coding Check : Volume 134 - Part 2") == "Volume 134 - Part 2"


def test_match_volume_134_part_I_filename():
    assert vw.match_volume("2025-06-17 first coding check : Volume 134 - Part I") == "Volume 134 - Part I"


def test_match_volume_61_filename():
    assert vw.match_volume("2025-09-14 First Coding Check: Volume 61") == "Volume 61"


def test_match_excludes_non_whitelisted_volume():
    assert vw.match_volume("2026-04-13 First Coding Check _ Volume 80") is None


def test_overrides_for_61():
    assert vw.override_sheet_for("2025-09-14 First Coding Check: Volume 61") == "104 agreement"


def test_overrides_for_62():
    assert vw.override_sheet_for("2025-09-14 First Coding Check: Volume 62") == "115 agreement"


def test_overrides_for_134_part_I():
    assert vw.override_sheet_for("2025-06-17 first coding check : Volume 134 - Part I") == "109 agreement"


def test_overrides_for_134_part_2():
    assert vw.override_sheet_for("2025-06-30 Second Coding Check : Volume 134 - Part 2") == "104 agreement"


def test_overrides_returns_none_for_non_overridden():
    assert vw.override_sheet_for("2026-02-18 First Coding Check : Volume 109") is None


def test_volume_134_part_2_matches_before_part_I():
    """Specificity: 'Volume 134 - Part 2' must not accidentally bind to Part-I rules."""
    p2_name = "2025-06-30 Second Coding Check : Volume 134 - Part 2"
    p1_name = "2025-06-17 first coding check : Volume 134 - Part I"
    assert vw.match_volume(p2_name) == "Volume 134 - Part 2"
    assert vw.match_volume(p1_name) == "Volume 134 - Part I"
    assert vw.override_sheet_for(p2_name) == "104 agreement"
    assert vw.override_sheet_for(p1_name) == "109 agreement"
