from __future__ import annotations

from typing import Tuple


def norm_deg(d: float) -> float:
    d = d % 360.0
    return d + 360.0 if d < 0 else d


def tithi_continuous(
    moon_lon: float,
    moon_spd: float,
    sun_lon: float,
    sun_spd: float,
) -> Tuple[float, float]:
    """
    Returns (tithi_index, tithi_speed_per_day).
    Index is continuous in [0, 30). 1 tithi = 12 degrees of (Moon - Sun).
    """
    dist = norm_deg(moon_lon - sun_lon)        # 0..360
    rel_speed = moon_spd - sun_spd             # deg/day
    val = dist / 12.0                          # 0..30
    speed = rel_speed / 12.0                   # tithi/day
    return val, speed


def nakshatra_continuous(
    moon_lon: float,
    moon_spd: float,
) -> Tuple[float, float]:
    """
    Returns (nak_index, nak_speed_per_day).
    Nakshatra is 27 divisions: 360/27 = 13.333... degrees.
    """
    scale = 27.0 / 360.0
    val = norm_deg(moon_lon) * scale
    speed = moon_spd * scale
    return val, speed


def yoga_continuous(
    moon_lon: float,
    moon_spd: float,
    sun_lon: float,
    sun_spd: float,
) -> Tuple[float, float]:
    """
    Returns (yoga_index, yoga_speed_per_day).
    Yoga uses (Moon + Sun) over 27 divisions.
    """
    scale = 27.0 / 360.0
    s = norm_deg(moon_lon + sun_lon)
    spd = moon_spd + sun_spd
    val = s * scale
    speed = spd * scale
    return val, speed

def unwrap_relative(val: float, target: float, period: float = 360.0) -> float:
    """
    Unwrap `val` (modulo `period`) to be continuous around `target`.

    Example:
      target=359.9, val=0.1  -> 360.1
      target=0.1,   val=359.9 -> -0.1

    This keeps (val - target) in [-period/2, +period/2].
    """
    val = float(val)
    target = float(target)
    period = float(period)
    diff = (val - target + period / 2.0) % period - period / 2.0
    return target + diff

