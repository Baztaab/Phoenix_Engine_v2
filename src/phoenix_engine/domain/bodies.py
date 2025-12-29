from __future__ import annotations
from enum import IntEnum

class Body(IntEnum):
    """
    Swiss Ephemeris body ids (subset).
    Keep this minimal and stable.
    """
    SUN = 0
    MOON = 1