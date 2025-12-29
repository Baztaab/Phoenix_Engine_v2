from __future__ import annotations

from enum import Enum, IntEnum


# -----------------------------
# Core policy enums (used by v2)
# -----------------------------

class ZodiacType(str, Enum):
    TROPICAL = "Tropical"
    SIDEREAL = "Sidereal"


class PerspectiveType(str, Enum):
    """
    Maps to Swiss flags policy in provider:
      - TRUE_GEOCENTRIC -> FLG_TRUEPOS (if enabled)
      - HELIOCENTRIC    -> FLG_HELCTR
      - TOPOCENTRIC     -> FLG_TOPOCTR (+ set_topo state by context manager)
    """
    TRUE_GEOCENTRIC = "TrueGeocentric"
    HELIOCENTRIC = "Heliocentric"
    TOPOCENTRIC = "Topocentric"


class NodeMode(str, Enum):
    MEAN = "Mean"
    TRUE = "True"


class HouseCalculationMode(str, Enum):
    """
    - SIDEREAL_NATIVE: swe.houses_ex(..., FLG_SIDEREAL)
    - TROPICAL_DERIVED: compute tropical then subtract ayanamsa (Parity-friendly)
    """
    SIDEREAL_NATIVE = "SiderealNative"
    TROPICAL_DERIVED = "TropicalDerived"


class HouseSystem(str, Enum):
    """
    Swiss house system identifiers (hsys bytes):
      P Placidus, W Whole sign, E Equal, O Porphyry, K Koch, C Campanus, R Regiomontanus, A Equal(Asc), etc.
    Keep this minimal; extend as needed.
    """
    PLACIDUS = "P"
    WHOLE_SIGN = "W"
    EQUAL = "E"
    PORPHYRY = "O"
    KOCH = "K"
    CAMPANUS = "C"
    REGIOMONTANUS = "R"
    EQUAL_ASC = "A"


class SunriseDisc(str, Enum):
    """
    Rise/Set disc policy (translated to rsmi bits in provider):
      - DISC_CENTER -> BIT_DISC_CENTER
      - DISC_EDGE   -> BIT_DISC_BOTTOM  (upper limb / edge)
    """
    DISC_CENTER = "Center"
    DISC_EDGE = "Edge"


class AyanamsaMode(str, Enum):
    """
    Mapped in SwissContext._map_ayanamsa_mode
    """
    LAHIRI_CLASSIC = "LahiriClassic"
    TRUE_CITRA = "TrueCitra"
    KRISHNAMURTI = "KP"
    RAMAN = "Raman"
    USER_DEFINED = "UserDefined"


# Optional: used later for Vedic strength logic (Chesta Bala etc.)
class MotionState(str, Enum):
    DIRECT = "Direct"
    RETROGRADE = "Retrograde"
    STATIONARY = "Stationary"


class PlanetId(IntEnum):
    SUN = 0
    MOON = 1
