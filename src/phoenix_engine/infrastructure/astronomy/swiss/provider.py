from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple, List

import swisseph as swe

from phoenix_engine.core.config.calibration import (
    CalibrationConfig,
    NodeMode,
    HouseCalculationMode,
    SunriseDisc,
    RiseSetStyle,
)
from phoenix_engine.domain.enums import ZodiacType, PerspectiveType

from .engine import SwissEngine


def norm360(x: float) -> float:
    x = x % 360.0
    return x + 360.0 if x < 0 else x


@dataclass
class EphemerisProvider:
    """
    Session-local Swiss Ephemeris provider with mandatory L1 cache.
    Expects a pre-configured SwissEngine instance (injected by SwissContext).
    """
    config: CalibrationConfig
    engine: SwissEngine
    lon: float = 0.0
    lat: float = 0.0
    alt_m: float = 0.0

    _cache: Dict[Tuple[Any, ...], Any] = field(init=False, default_factory=dict)
    _sig: Tuple[Any, ...] = field(init=False, default=())

    def __post_init__(self) -> None:
        self._sig = tuple(self.config.signature()) if hasattr(self.config, "signature") else ("no-signature",)

    # -----------------------
    # Internal helpers
    # -----------------------
    def _jd_key(self, jd_ut: float, *, ndigits: int = 9) -> float:
        return round(float(jd_ut), ndigits)

    def _planet_flags(self) -> int:
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED

        # Robust config access
        if getattr(self.config, "use_truepos", False):
            flags |= swe.FLG_TRUEPOS

        if getattr(self.config, "zodiac_type", ZodiacType.TROPICAL) == ZodiacType.SIDEREAL:
            flags |= swe.FLG_SIDEREAL

        if (
            getattr(self.config, "perspective", PerspectiveType.TRUE_GEOCENTRIC) == PerspectiveType.TOPOCENTRIC
            and getattr(getattr(self.config, "topo", None), "enabled", False)
        ):
            flags |= swe.FLG_TOPOCTR

        return int(flags)

    def _map_nodes(self, body_id: int) -> int:
        if int(body_id) in (int(swe.TRUE_NODE), int(swe.MEAN_NODE)):
            nodes_mode = getattr(self.config, "nodes", NodeMode.TRUE)
            return int(swe.TRUE_NODE) if nodes_mode == NodeMode.TRUE else int(swe.MEAN_NODE)
        return int(body_id)

    # -----------------------
    # Public API
    # -----------------------
    def planet_lon_speed(self, jd_ut: float, body_id: int) -> Tuple[float, float]:
        body = self._map_nodes(body_id)
        flags = self._planet_flags()

        key = ("calc_ut", self._sig, self._jd_key(jd_ut), int(body), int(flags))
        if key in self._cache:
            return self._cache[key]

        pr = self.engine.calc_ut(float(jd_ut), int(body), int(flags))
        out = (float(pr.lon), float(pr.speed_lon))
        self._cache[key] = out
        return out

    def ayanamsa(self, jd_ut: float) -> float:
        key = ("ayan", self._sig, self._jd_key(jd_ut), int(swe.FLG_SWIEPH))
        if key in self._cache:
            return self._cache[key]
        ay = float(self.engine.get_ayanamsa_ex_ut(float(jd_ut), int(swe.FLG_SWIEPH)))
        self._cache[key] = ay
        return ay

    def houses(
        self,
        jd_ut: float,
        hsys: bytes,
        *,
        house_mode: Optional[HouseCalculationMode] = None,
    ) -> Tuple[List[float], List[float]]:
        mode = house_mode or getattr(self.config, "houses", HouseCalculationMode.TROPICAL_DERIVED)

        if mode == HouseCalculationMode.TROPICAL_DERIVED:
            key = ("houses_trop", self._sig, self._jd_key(jd_ut), round(self.lat, 8), round(self.lon, 8), hsys)
            if key in self._cache:
                cusps, ascmc = self._cache[key]
            else:
                cusps, ascmc = self.engine.houses_ex(float(jd_ut), float(self.lat), float(self.lon), hsys, int(swe.FLG_SWIEPH))
                self._cache[key] = (cusps, ascmc)

            ay = self.ayanamsa(jd_ut)
            cusps2 = [norm360(float(c) - ay) for c in cusps]
            ascmc2 = [norm360(float(a) - ay) for a in ascmc]
            return cusps2, ascmc2

        # SIDEREAL_NATIVE
        flags = int(swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        key = ("houses_sid", self._sig, self._jd_key(jd_ut), round(self.lat, 8), round(self.lon, 8), hsys, flags)
        if key in self._cache:
            return self._cache[key]

        cusps, ascmc = self.engine.houses_ex(float(jd_ut), float(self.lat), float(self.lon), hsys, flags)
        self._cache[key] = (cusps, ascmc)
        return cusps, ascmc

    def rise_set(
        self,
        jd_ut: float,
        body_id: int,
        *,
        rise: bool = True,
        atpress: Optional[float] = None,
        attemp: Optional[float] = None,
    ) -> Tuple[float, int]:
        sunrise_cfg = getattr(self.config, "sunrise", None)
        style = getattr(sunrise_cfg, "style", RiseSetStyle.PYJHORA_DRiK)

        if style == RiseSetStyle.PYJHORA_DRiK:
            ephe_flags = 0
            rsmi = int(swe.CALC_RISE if rise else swe.CALC_SET)
            rsmi |= int(swe.BIT_HINDU_RISING)
            rsmi |= int(swe.FLG_TRUEPOS)
            rsmi |= int(swe.FLG_SPEED)

            rounded_geo = (round(self.lon, 6), round(self.lat, 6), 0.0)
            key = (
                "rise_set",
                self._sig,
                round(float(jd_ut), 9),
                int(body_id),
                bool(rise),
                int(ephe_flags),
                int(rsmi),
                rounded_geo,
            )
            if key in self._cache:
                return self._cache[key]

            geopos = (float(self.lon), float(self.lat), 0.0)
            out = self.engine.rise_trans(float(jd_ut), int(body_id), ephe_flags, rsmi, geopos, None, None)
            self._cache[key] = out
            return out

        # DISC_POLICY (legacy)
        ephe_flags = int(swe.FLG_SWIEPH)
        rsmi = int(swe.CALC_RISE if rise else swe.CALC_SET)

        # FIX: Default to DISC_EDGE (Upper Limb) matching domain/enums.py
        disc = getattr(sunrise_cfg, "disc", SunriseDisc.DISC_EDGE)
        use_refrac = getattr(sunrise_cfg, "use_refraction", True)

        if disc == SunriseDisc.DISC_CENTER:
            rsmi |= int(swe.BIT_DISC_CENTER)
        else:
            # DISC_EDGE implies Upper Limb -> BIT_DISC_BOTTOM
            rsmi |= int(swe.BIT_DISC_BOTTOM)

        if not use_refrac:
            rsmi |= int(swe.BIT_NO_REFRACTION)

        atm = getattr(sunrise_cfg, "atmosphere", None)
        p_default = getattr(atm, "pressure_mbar", 1013.25)
        t_default = getattr(atm, "temperature_c", 15.0)

        p = float(p_default if atpress is None else atpress)
        t = float(t_default if attemp is None else attemp)

        rounded_geo = (round(self.lon, 6), round(self.lat, 6), round(self.alt_m, 1))
        key = (
            "rise_set",
            self._sig,
            round(float(jd_ut), 9),
            int(body_id),
            bool(rise),
            int(ephe_flags),
            int(rsmi),
            rounded_geo,
            round(p, 2),
            round(t, 2),
        )
        if key in self._cache:
            return self._cache[key]

        geopos = (float(self.lon), float(self.lat), float(self.alt_m))
        out = self.engine.rise_trans(float(jd_ut), int(body_id), ephe_flags, rsmi, geopos, p, t)
        self._cache[key] = out
        return out
