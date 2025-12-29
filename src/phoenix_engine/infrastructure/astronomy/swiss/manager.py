from __future__ import annotations
import os, threading, warnings
from dataclasses import dataclass
from typing import Optional
import swisseph as swe
from phoenix_engine.core.config.calibration import CalibrationConfig, AyanamsaMode
from phoenix_engine.domain.enums import PerspectiveType, ZodiacType
from .engine import SwissEngine 

_GLOBAL_SWISS_LOCK = threading.RLock()

@dataclass(frozen=True)
class SwissAssets:
    ephe_path: str

def _default_ephe_path() -> str:
    return os.path.join(os.getcwd(), "ephe")

def ensure_ephemeris_path(ephe_path: Optional[str]) -> SwissAssets:
    path = ephe_path or _default_ephe_path()
    os.makedirs(path, exist_ok=True)
    has_se1 = False
    if os.path.exists(path):
        try: has_se1 = any(f.endswith(".se1") for f in os.listdir(path))
        except OSError: pass
    
    if not has_se1:
        # SYNTAX FIXED HERE (Clean strings)
        warnings.warn(
            f"Swiss Ephemeris path {path} is empty. Engine will fall back to Moshier mode.",
            RuntimeWarning
        )
    return SwissAssets(ephe_path=path)

class SwissContext:
    def __init__(self, config: CalibrationConfig, *, ephe_path: Optional[str] = None, lon: float = 0.0, lat: float = 0.0, alt_m: float = 0.0):
        self.config = config
        self.assets = ensure_ephemeris_path(ephe_path)
        self.lon = lon; self.lat = lat; self.alt_m = alt_m
        self._lock = _GLOBAL_SWISS_LOCK
        self._engine = SwissEngine() # Instantiate Class
        self._topo_used = False

    def __enter__(self):
        self._lock.acquire()
        self._engine.set_ephe_path(self.assets.ephe_path)
        
        if self.config.zodiac_type == ZodiacType.SIDEREAL:
            ay = self.config.ayanamsa
            if ay.mode == AyanamsaMode.USER_DEFINED:
                self._engine.set_sid_mode(swe.SIDM_USER, ay.t0, ay.ayan_t0)
            else:
                mode_int = getattr(swe, f"SIDM_{ay.mode.value}", swe.SIDM_LAHIRI)
                self._engine.set_sid_mode(mode_int, 0, 0)

        if self.config.perspective == PerspectiveType.TOPOCENTRIC and self.config.topo.enabled:
            self._engine.set_topo(self.lon, self.lat, self.alt_m)
            self._topo_used = True

        from .provider import EphemerisProvider
        # INJECT ENGINE HERE
        return EphemerisProvider(config=self.config, engine=self._engine, lon=self.lon, lat=self.lat, alt_m=self.alt_m)

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._topo_used and self.config.reset_topo_on_exit:
                self._engine.set_topo(0.0, 0.0, 0.0)
        finally:
            self._lock.release()

# ALIAS FOR BACKWARD COMPATIBILITY (Satisfies GPT Smoke Test)
SwissContextManager = SwissContext