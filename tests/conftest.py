import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def _isolated_data_dir(tmp_path_factory, monkeypatch):
    """Keep progress databases and caches out of the real home directory."""
    base = tmp_path_factory.getbasetemp() / "pylearn-data"
    base.mkdir(exist_ok=True)
    monkeypatch.setenv("PYLEARN_DATA_DIR", str(base))
    yield
