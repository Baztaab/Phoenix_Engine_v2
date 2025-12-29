from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Tuple

from phoenix_engine.domain.enums import (
    NodeMode,
    HouseCalculationMode,
    HouseSystem,
    SunriseDisc,
    AyanamsaMode,
    ZodiacType,
    PerspectiveType,
)


class AtmosphericConfig(BaseModel):
    pressure_mbar: float = 1013.25
    temperature_c: float = 15.0


class RiseSetStyle(str, Enum):
    PYJHORA_DRiK = "PYJHORA_DRiK"
    DISC_POLICY = "DISC_POLICY"


class RiseSetPolicy(BaseModel):
    style: RiseSetStyle = RiseSetStyle.PYJHORA_DRiK
    disc: SunriseDisc = SunriseDisc.DISC_EDGE
    use_refraction: bool = True
    atmosphere: AtmosphericConfig = Field(default_factory=AtmosphericConfig)


class AyanamsaConfig(BaseModel):
    mode: AyanamsaMode = AyanamsaMode.TRUE_CITRA
    # Only used if mode == USER_DEFINED
    t0: float = 0.0
    ayan_t0: float = 0.0


class TopoConfig(BaseModel):
    enabled: bool = False
    altitude_m: float = 0.0


class CalibrationConfig(BaseModel):
    """
    Single Source of Truth for Swiss Ephemeris calculation policy.
    Apply at *session scope* (one chart / one batch).
    """

    zodiac_type: ZodiacType = ZodiacType.SIDEREAL
    perspective: PerspectiveType = PerspectiveType.TOPOCENTRIC

    ayanamsa: AyanamsaConfig = Field(default_factory=AyanamsaConfig)
    nodes: NodeMode = NodeMode.TRUE

    houses: HouseCalculationMode = HouseCalculationMode.TROPICAL_DERIVED
    house_system: HouseSystem = HouseSystem.PLACIDUS

    sunrise: RiseSetPolicy = Field(default_factory=RiseSetPolicy)
    topo: TopoConfig = Field(default_factory=TopoConfig)

    # Precision
    use_microseconds: bool = True
    use_speed: bool = True
    use_truepos: bool = True  # relevant when perspective == TRUE_GEOCENTRIC

    # Cleanup policy (perf-first; lock provides safety)
    reset_topo_on_exit: bool = True

    def signature(self) -> Tuple:
        """Hashable signature for session-local caching keys."""
        a = self.ayanamsa
        s = self.sunrise
        return (
            self.zodiac_type.value,
            self.perspective.value,
            a.mode.value, float(a.t0), float(a.ayan_t0),
            self.nodes.value,
            self.houses.value,
            self.house_system.value,
            s.style.value, s.disc.value, bool(s.use_refraction),
            float(s.atmosphere.pressure_mbar),
            float(s.atmosphere.temperature_c),
            bool(self.topo.enabled),
            float(self.topo.altitude_m),
            bool(self.use_microseconds),
            bool(self.use_speed),
            bool(self.use_truepos),
            bool(self.reset_topo_on_exit),
        )
