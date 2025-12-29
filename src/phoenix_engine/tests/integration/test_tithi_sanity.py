from __future__ import annotations

import swisseph as swe

from phoenix_engine.core.config.calibration import CalibrationConfig
from phoenix_engine.infrastructure.astronomy.swiss.manager import SwissContextManager
from phoenix_engine.vedic.panchanga.events import PanchangaFinder


def test_tithi_end_sanity():
    cfg = CalibrationConfig()

    # roughly 2024-01-01 00:00 UT (kept as example; any JD works)
    start_jd = 2460310.5

    with SwissContextManager(cfg) as provider:
        finder = PanchangaFinder(provider)
        res = finder.next_tithi_end(start_jd)

        assert res.root_jd > start_jd
        assert (res.root_jd - start_jd) < 1.1  # tithi usually < ~26h

        # verify angle at root is near multiple of 12°
        s_end, _ = provider.planet_lon_speed(res.root_jd, int(swe.SUN))
        m_end, _ = provider.planet_lon_speed(res.root_jd, int(swe.MOON))

        dist = (m_end - s_end) % 360.0
        rem = dist % 12.0

        # tolerance: degrees (solver 0.1s + float noise)
        eps = 1e-3
        assert (rem < eps) or (abs(rem - 12.0) < eps), f"dist={dist}, rem={rem}, method={res.method}"