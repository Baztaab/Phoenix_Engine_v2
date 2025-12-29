from __future__ import annotations
from enum import Enum
import swisseph as swe

class TimeScale(str, Enum):
    UT = "UT"
    TT = "TT"

def delta_t_days(jd_ut: float) -> float:
    """Returns Delta T in DAYS (calculated automatically via Swiss Ephemeris)."""
    dt = float(swe.deltat(jd_ut))
    if abs(dt) > 0.5: # Heuristic for seconds
        return dt / 86400.0
    return dt

def ut_to_tt(jd_ut: float) -> float:
    return jd_ut + delta_t_days(jd_ut)

def tt_to_ut(jd_tt: float) -> float:
    jd_ut = jd_tt
    for _ in range(4):
        jd_ut = jd_tt - delta_t_days(jd_ut)
    return jd_ut