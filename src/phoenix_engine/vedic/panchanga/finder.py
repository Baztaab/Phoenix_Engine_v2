from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from phoenix_engine.core.math.angles import extend_angle_range, normalize_angle, unwrap_angles
from phoenix_engine.core.math.interpolation import inverse_lagrange
from phoenix_engine.core.math.solver import SolveResult, solve_root
from phoenix_engine.infrastructure.astronomy.swiss.provider import EphemerisProvider
from phoenix_engine.vedic.panchanga.temporal import (
    ONE_STAR,
    nakshatra_continuous,
    nakshatra_pada_from_longitude,
    tithi_continuous,
    yoga_continuous,
)

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
        SUN = 0
        MOON = 1


def _unwrap_cycle(val: float, target: float, period: float) -> float:
    if target >= period and val < (period / 2.0):
        return val + period
    return val


@dataclass(frozen=True)
class SearchParams:
    accuracy_seconds: float = 0.1
    scan_step_days: float = 1.0 / 12.0
    max_days_ahead: float = 1.5


class PanchangaFinder:
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

        return solve_root(f, float(start_jd), float(start_jd + p.max_days_ahead),
                          accuracy_seconds=float(p.accuracy_seconds), scan_step_days=float(p.scan_step_days))

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

        return solve_root(f, float(start_jd), float(start_jd + p.max_days_ahead),
                          accuracy_seconds=float(p.accuracy_seconds), scan_step_days=float(p.scan_step_days))

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

        return solve_root(f, float(start_jd), float(start_jd + p.max_days_ahead),
                          accuracy_seconds=float(p.accuracy_seconds), scan_step_days=float(p.scan_step_days))


def _get_nakshatra_end_hours(
    jd: float,
    place,
    sunrise_fn: Optional[Callable] = None,
    sidereal_longitude_fn: Optional[Callable] = None,
    lunar_longitude_fn: Optional[Callable] = None,
    jd_to_gregorian_fn: Optional[Callable] = None,
    gregorian_to_jd_fn: Optional[Callable] = None,
    moon_id: Optional[int] = None,
) -> List[float]:
    """Compute nakshatra end times anchored to sunrise.

    TODO (PyJHora method): مطابق nakshatra.md
    - jd_utc = jd - tz/24
    - rise = sunrise(jd_utc, place)[2]
    - sample Moon lon at rise + [0, .25, .5, .75, 1.0]
    - unwrap/extend angles
    - inverse_lagrange for boundary (nak * ONE_STAR)
    """
    if sunrise_fn is None:
        raise NotImplementedError("TODO: inject sunrise_fn (see nakshatra.md)")
    if sidereal_longitude_fn is None:
        raise NotImplementedError("TODO: inject sidereal_longitude_fn (see nakshatra.md)")
    if jd_to_gregorian_fn is None:
        raise NotImplementedError("TODO: inject jd_to_gregorian_fn (see nakshatra.md)")
    if gregorian_to_jd_fn is None:
        raise NotImplementedError("TODO: inject gregorian_to_jd_fn (see nakshatra.md)")

    tz = place.timezone
    jd_utc = jd - tz / 24.0

    rise = sunrise_fn(jd_utc, place)[2]
    year, month, day, _ = jd_to_gregorian_fn(jd)
    jd_ut0 = gregorian_to_jd_fn(year, month, day)

    offsets = [0.0, 0.25, 0.5, 0.75, 1.0]
    longs = [sidereal_longitude_fn(rise + off, moon_id) for off in offsets]

    unwrapped = unwrap_angles(longs)
    extended = extend_angle_range(unwrapped, span=360.0)
    x = offsets * (len(extended) // len(unwrapped))

    moon_long = sidereal_longitude_fn(jd_utc, moon_id) if lunar_longitude_fn is None else lunar_longitude_fn(jd_utc)
    nak_no, pada_no, _ = nakshatra_pada_from_longitude(moon_long)

    y1 = normalize_angle(nak_no * ONE_STAR, start=min(extended))
    approx1 = inverse_lagrange(x, extended, y1)
    end_hours = (rise - jd_ut0 + approx1) * 24.0 + tz

    leap_nak = 1 if nak_no == 27 else (nak_no + 1)
    y2 = normalize_angle(leap_nak * ONE_STAR, start=min(extended))
    approx2 = inverse_lagrange(x, extended, y2)
    end2_hours = (rise - jd_ut0 + approx2) * 24.0 + tz

    return [nak_no, pada_no, end_hours, leap_nak, pada_no, end2_hours]


__all__ = ["PanchangaFinder", "SearchParams", "_get_nakshatra_end_hours"]
