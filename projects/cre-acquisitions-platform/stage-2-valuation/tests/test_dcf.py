"""Tests for dcf.py"""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from dcf import project_noi_simple, pv_cash_flows, irr_newton


def test_project_noi():
    cf = project_noi_simple(1000000, 10, 0.03)
    assert len(cf) == 10
    assert cf[0] == pytest.approx(1000000)
    assert cf[9] == pytest.approx(1000000 * (1.03 ** 9), rel=1e-2)


def test_pv_cash_flows():
    cf = [100] * 5
    pv = pv_cash_flows(cf, 0.10)
    assert pv == pytest.approx(379.08, rel=1e-2)


def test_irr():
    # 100 initial, 110 back in 1 year -> 10% IRR
    irr = irr_newton(100, [110])
    assert irr == pytest.approx(0.10, rel=1e-2)
