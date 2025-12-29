from __future__ import annotations

import swisseph as swe

from phoenix_engine.core.config.calibration import CalibrationConfig, RiseSetStyle
from phoenix_engine.infrastructure.astronomy.swiss.manager import SwissContextManager


def test_rise_set_style_differs():
    cfg_py = CalibrationConfig()
    cfg_disc = CalibrationConfig()
    cfg_disc.sunrise.style = RiseSetStyle.DISC_POLICY

    start_jd = 2460310.5  # ~2024-01-01
    lon, lat = 77.2090, 28.6139

    with SwissContextManager(cfg_py, lon=lon, lat=lat) as provider_py:
        jd_py, _ = provider_py.rise_set(start_jd, int(swe.SUN), rise=True)

    with SwissContextManager(cfg_disc, lon=lon, lat=lat) as provider_disc:
        jd_disc, _ = provider_disc.rise_set(start_jd, int(swe.SUN), rise=True)

    diff_min = abs(jd_py - jd_disc) * 1440.0
    assert diff_min >= 1.0, f"Expected >=1 min difference, got {diff_min:.3f} min"
