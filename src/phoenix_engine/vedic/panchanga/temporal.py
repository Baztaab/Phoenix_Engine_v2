from __future__ import annotations

\"\"\"Temporal helpers for Panchanga calculations.\"\"\"

from typing import Tuple

from phoenix_engine.core.math.angles import normalize_angle

ONE_STAR = 360.0 / 27.0
ONE_PADA = 360.0 / 108.0


def tithi_continuous(moon_lon: float, moon_spd: float, sun_lon: float, sun_spd: float) -> Tuple[float, float]:
    \"\"\"Return (tithi_index, tithi_speed_per_day).

    1 tithi = 12 degrees of (Moon - Sun). Index in [0, 30).
    \"\"\"
    dist = normalize_angle(moon_lon - sun_lon, start=0.0, period=360.0)
    rel_speed = moon_spd - sun_spd
    return dist / 12.0, rel_speed / 12.0


def nakshatra_continuous(moon_lon: float, moon_spd: float) -> Tuple[float, float]:
    \"\"\"Return (nak_index, nak_speed_per_day) with 27 divisions.\"\"\"
    scale = 27.0 / 360.0
    lon = normalize_angle(moon_lon, start=0.0, period=360.0)
    return lon * scale, moon_spd * scale


def yoga_continuous(moon_lon: float, moon_spd: float, sun_lon: float, sun_spd: float) -> Tuple[float, float]:
    \"\"\"Return (yoga_index, yoga_speed_per_day) where yoga uses (Moon + Sun) over 27.\"\"\"
    scale = 27.0 / 360.0
    s = normalize_angle(moon_lon + sun_lon, start=0.0, period=360.0)
    spd = moon_spd + sun_spd
    return s * scale, spd * scale


def nakshatra_pada_from_longitude(lon_deg: float) -> tuple[int, int, float]:
    \"\"\"Return (nakshatra_no, pada_no, remainder) from sidereal longitude.\"\"\"
    lon = normalize_angle(lon_deg, start=0.0, period=360.0)
    quotient = int(lon / ONE_STAR)
    remainder = lon % ONE_STAR
    pada = int(remainder / ONE_PADA)
    return 1 + quotient, 1 + pada, remainder


__all__ = [
    "ONE_PADA",
    "ONE_STAR",
    "nakshatra_pada_from_longitude",
    "nakshatra_continuous",
    "tithi_continuous",
    "yoga_continuous",
]