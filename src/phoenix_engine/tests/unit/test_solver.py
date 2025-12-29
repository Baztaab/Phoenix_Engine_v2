from __future__ import annotations

import math
import pytest

from phoenix_engine.core.math.solver import solve_root, NoBracketError


def test_solve_root_linear_newton_fast():
    # f(x)=x-10, speed=1 => root at 10
    def f(jd: float):
        return (jd - 10.0, 1.0)

    res = solve_root(f, 0.0, 20.0, accuracy_seconds=0.001, scan_step_days=1.0)
    assert abs(res.root_jd - 10.0) < (0.001 / 86400.0)
    assert res.method in ("newton", "bisection", "bracket_hit")


def test_solve_root_quadratic_newton():
    # f(x)=x^2-4, speed=2x => roots at -2 and +2
    def f(jd: float):
        return (jd * jd - 4.0, 2.0 * jd)

    res = solve_root(f, 0.0, 5.0, accuracy_seconds=0.001, scan_step_days=0.5)
    assert abs(res.root_jd - 2.0) < (0.001 / 86400.0)


def test_solve_root_stationary_fallback_bisection():
    # speed near zero at root triggers fallback; choose function that crosses with tiny slope near 0.
    # f(x)=x^3, speed=3x^2 -> at x=0 speed=0 (stationary), but bracketed root exists.
    def f(jd: float):
        return (jd ** 3, 3.0 * (jd ** 2))

    res = solve_root(f, -1.0, 1.0, accuracy_seconds=0.001, scan_step_days=0.2, min_speed=1e-6)
    assert abs(res.root_jd - 0.0) < (0.001 / 86400.0)
    # most likely bisection
    assert res.method in ("bisection", "newton", "bracket_hit")


def test_no_bracket_raises():
    # Always positive
    def f(jd: float):
        return (jd * jd + 1.0, 2.0 * jd)

    with pytest.raises(NoBracketError):
        solve_root(f, 0.0, 2.0, scan_step_days=0.5)