from __future__ import annotations

import swisseph as swe

from phoenix_engine.core.config.calibration import CalibrationConfig
from phoenix_engine.infrastructure.astronomy.swiss.manager import SwissContextManager
from phoenix_engine.vedic.panchanga.events import PanchangaFinder

def _near_boundary(rem: float, unit: float, eps: float) -> bool:
    return (rem < eps) or (abs(rem - unit) < eps)

def test_tithi_end_sanity():
    cfg = CalibrationConfig()
    start_jd = 2460310.5  # ~2024-01-01

    with SwissContextManager(cfg) as provider:
        finder = PanchangaFinder(provider)
        res = finder.next_tithi_end(start_jd)

        assert res.root_jd > start_jd
        assert (res.root_jd - start_jd) < 1.1

        s_end, _ = provider.planet_lon_speed(res.root_jd, int(swe.SUN))
        m_end, _ = provider.planet_lon_speed(res.root_jd, int(swe.MOON))

        dist = (m_end - s_end) % 360.0
        unit = 12.0
        rem = dist % unit

        eps = 1e-2  # 0.01 deg ~= 36 arcsec (less flaky than 1e-3)
        assert _near_boundary(rem, unit, eps), f"Tithi remainder {rem} not near 0/12"

def test_nakshatra_end_sanity():
    cfg = CalibrationConfig()
    start_jd = 2460310.5

    with SwissContextManager(cfg) as provider:
        finder = PanchangaFinder(provider)
        res = finder.next_nakshatra_end(start_jd)

        assert res.root_jd > start_jd
        assert (res.root_jd - start_jd) < 1.2

        m_end, _ = provider.planet_lon_speed(res.root_jd, int(swe.MOON))
        unit = 360.0 / 27.0
        rem = m_end % unit

        eps = 1e-2
        assert _near_boundary(rem, unit, eps), f"Nakshatra remainder {rem} not near boundary"

def test_yoga_end_sanity():
    cfg = CalibrationConfig()
    start_jd = 2460310.5

    with SwissContextManager(cfg) as provider:
        finder = PanchangaFinder(provider)
        res = finder.next_yoga_end(start_jd)

        assert res.root_jd > start_jd
        assert (res.root_jd - start_jd) < 1.2

        s_end, _ = provider.planet_lon_speed(res.root_jd, int(swe.SUN))
        m_end, _ = provider.planet_lon_speed(res.root_jd, int(swe.MOON))
        total = (s_end + m_end) % 360.0

        unit = 360.0 / 27.0
        rem = total % unit

        eps = 1e-2
        assert _near_boundary(rem, unit, eps), f"Yoga remainder {rem} not near boundary"