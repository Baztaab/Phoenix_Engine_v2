from __future__ import annotations

\"\"\"Panchanga event facade.

- Solver-based continuous events: PanchangaFinder
- Sunrise-anchored nakshatra facade: nakshatra() (TODO wiring per nakshatra.md)
\"\"\"

from typing import List

from phoenix_engine.vedic.panchanga.finder import PanchangaFinder, SearchParams, _get_nakshatra_end_hours


def nakshatra(
    jd: float,
    place,
    *,
    sunrise_fn=None,
    sidereal_longitude_fn=None,
    lunar_longitude_fn=None,
    jd_to_gregorian_fn=None,
    gregorian_to_jd_fn=None,
    moon_id=None,
) -> List[float]:
    today = _get_nakshatra_end_hours(
        jd,
        place,
        sunrise_fn=sunrise_fn,
        sidereal_longitude_fn=sidereal_longitude_fn,
        lunar_longitude_fn=lunar_longitude_fn,
        jd_to_gregorian_fn=jd_to_gregorian_fn,
        gregorian_to_jd_fn=gregorian_to_jd_fn,
        moon_id=moon_id,
    )
    prev = _get_nakshatra_end_hours(
        jd - 1,
        place,
        sunrise_fn=sunrise_fn,
        sidereal_longitude_fn=sidereal_longitude_fn,
        lunar_longitude_fn=lunar_longitude_fn,
        jd_to_gregorian_fn=jd_to_gregorian_fn,
        gregorian_to_jd_fn=gregorian_to_jd_fn,
        moon_id=moon_id,
    )

    start = prev[2]
    if start < 24.0:
        start = -start
    elif start > 24.0:
        start -= 24.0

    return [today[0], today[1], start, today[2]] + today[3:]


__all__ = ["PanchangaFinder", "SearchParams", "nakshatra"]