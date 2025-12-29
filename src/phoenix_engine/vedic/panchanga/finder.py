from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Tuple

from phoenix_engine.core.math.solver import solve_root, SolveResult
from phoenix_engine.infrastructure.astronomy.swiss.provider import EphemerisProvider

from phoenix_engine.vedic.panchanga.temporal import (
    tithi_continuous,
    nakshatra_continuous,
    yoga_continuous,
)

# Prefer Body constants from domain/enums.py if present, else fallback to domain/bodies.py
try:
    from phoenix_engine.domain.enums import SUN as _SUN, MOON as _MOON  # type: ignore
    SUN = int(_SUN)
    MOON = int(_MOON)
except Exception:
    try:
        from phoenix_engine.domain.bodies import Body
        SUN = int(Body.SUN)
        MOON = int(Body.MOON)
    except Exception:
        # final fallback: Swiss IDs (Sun=0, Moon=1)
        SUN = 0
        MOON = 1


def _unwrap_cycle(val: float, target: float, period: float) -> float:
    """
    Keep f(t) continuous across wrap boundary.
    If target is at/after period and current val is in early half, treat as val+period.
    """
    if target >= period and val < (period / 2.0):
        return val + period
    return val


@dataclass(frozen=True)
class SearchParams:
    accuracy_seconds: float = 0.1
    scan_step_days: float = 1.0 / 12.0  # 2 hours
    max_days_ahead: float = 1.5


class PanchangaFinder:
    """
    Event finder over an EphemerisProvider.
    Returns SolveResult directly (keeps solver diagnostics).
    """

    def __init__(self, provider: EphemerisProvider):
        self.provider = provider

    def next_tithi_end(self, start_jd: float, *, params: Optional[SearchParams] = None) -> SolveResult:
        p = params or SearchParams(max_days_ahead=1.5)

        s0, ss0 = self.provider.planet_lon_speed(start_jd, SUN)
        m0, ms0 = self.provider.planet_lon_speed(start_jd, MOON)

        curr, _ = tithi_continuous(m0, ms0, s0, ss0)
        target = math.floor(curr) + 1.0
        period = 30.0

        def f(jd: float) -> Tuple[float, float]:
            s, ss = self.provider.planet_lon_speed(jd, SUN)
            m, ms = self.provider.planet_lon_speed(jd, MOON)
            val, speed = tithi_continuous(m, ms, s, ss)
            val = _unwrap_cycle(val, target, period)
            return (val - target, speed)

        return solve_root(
            f,
            float(start_jd),
            float(start_jd + p.max_days_ahead),
            accuracy_seconds=float(p.accuracy_seconds),
            scan_step_days=float(p.scan_step_days),
        )

    def next_nakshatra_end(self, start_jd: float, *, params: Optional[SearchParams] = None) -> SolveResult:
        p = params or SearchParams(max_days_ahead=1.3)

        m0, ms0 = self.provider.planet_lon_speed(start_jd, MOON)
        curr, _ = nakshatra_continuous(m0, ms0)
        target = math.floor(curr) + 1.0
        period = 27.0

        def f(jd: float) -> Tuple[float, float]:
            m, ms = self.provider.planet_lon_speed(jd, MOON)
            val, speed = nakshatra_continuous(m, ms)
            val = _unwrap_cycle(val, target, period)
            return (val - target, speed)

        return solve_root(
            f,
            float(start_jd),
            float(start_jd + p.max_days_ahead),
            accuracy_seconds=float(p.accuracy_seconds),
            scan_step_days=float(p.scan_step_days),
        )

    def next_yoga_end(self, start_jd: float, *, params: Optional[SearchParams] = None) -> SolveResult:
        p = params or SearchParams(max_days_ahead=1.3)

        s0, ss0 = self.provider.planet_lon_speed(start_jd, SUN)
        m0, ms0 = self.provider.planet_lon_speed(start_jd, MOON)

        curr, _ = yoga_continuous(m0, ms0, s0, ss0)
        target = math.floor(curr) + 1.0
        period = 27.0

        def f(jd: float) -> Tuple[float, float]:
            s, ss = self.provider.planet_lon_speed(jd, SUN)
            m, ms = self.provider.planet_lon_speed(jd, MOON)
            val, speed = yoga_continuous(m, ms, s, ss)
            val = _unwrap_cycle(val, target, period)
            return (val - target, speed)

        return solve_root(
            f,
            float(start_jd),
            float(start_jd + p.max_days_ahead),
            accuracy_seconds=float(p.accuracy_seconds),
            scan_step_days=float(p.scan_step_days),
        )