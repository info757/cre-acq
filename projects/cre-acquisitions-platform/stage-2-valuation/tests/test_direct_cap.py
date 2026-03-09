"""Tests for direct_cap.py"""
import json
import tempfile
import pytest
from decimal import Decimal

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from direct_cap import direct_cap


def test_direct_cap_basic():
    assert direct_cap(1983900, 0.051) == pytest.approx(38900000, rel=1e-2)
    assert direct_cap(1000000, 0.05) == 20000000


def test_direct_cap_invalid():
    with pytest.raises(ValueError):
        direct_cap(1000000, 0)
