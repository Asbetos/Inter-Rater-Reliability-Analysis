"""Pytest configuration for the irr_analysis test suite.

Adds the parent directory to sys.path so tests can `import io_xlsx`,
`import irr_metrics`, etc., without the package being pip-installed.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

FIXTURE_PATH = (
    Path(__file__).parent / "fixtures" / "mini_cross_check.xlsx"
)
