"""Pytest config for the dataset test suite."""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent   # irr_analysis/dataset/
_pkg = _root.parent                                # irr_analysis/

# Both on sys.path so tests can import dataset modules AND existing pilot modules.
sys.path.insert(0, str(_root))
sys.path.insert(0, str(_pkg))

MINI_DRIVE_DIR = Path(__file__).parent / "fixtures" / "mini_drive_tree"
