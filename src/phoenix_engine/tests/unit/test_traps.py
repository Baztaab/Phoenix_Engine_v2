from __future__ import annotations
import pytest
from phoenix_engine.core.config.calibration import CalibrationConfig
from phoenix_engine.vedic.panchanga.temporal import unwrap_relative, norm_deg
from phoenix_engine.domain.enums import PlanetId

# ---------------------------------------------------------
# TRAP 1: The "Mutable Default" Argument Trap
# AI Mistake: Using mutable objects (list/dict/dataclass) as defaults
# without field(default_factory=...).
# ---------------------------------------------------------
def test_trap_mutable_defaults_in_config():
    """
    Ensures that modifying a nested config object does NOT affect 
    new instances (checking for shared reference bugs).
    """
    cfg1 = CalibrationConfig()
    # Modify a nested object
    cfg1.sunrise.use_refraction = False
    cfg1.topo.enabled = True
    
    # Create fresh instance
    cfg2 = CalibrationConfig()
    
    # TRAP CHECK: cfg2 should have defaults, not cfg1's values
    assert cfg2.sunrise.use_refraction is True, "CRITICAL: SunriseConfig is shared between instances!"
    assert cfg2.topo.enabled is False, "CRITICAL: TopoConfig is shared between instances!"

# ---------------------------------------------------------
# TRAP 2: The "Circle Wrap" Trap
# AI Mistake: Implementing abs(a-b) without modulo 360 logic.
# ---------------------------------------------------------
def test_trap_angle_normalization():
    """
    Ensures norm_deg handles negative inputs correctly (Python % operator 
    is good, but strict math logic must be verified).
    """
    # 1 degree minus 359 degrees = -358 math, but +2 degrees on circle
    diff = norm_deg(1.0 - 359.0)
    assert diff == 2.0, f"Angle logic failed. Expected 2.0, got {diff}"
    
    # Wrap multiple times
    huge_angle = 725.0 # 2 * 360 + 5
    assert norm_deg(huge_angle) == 5.0

# ---------------------------------------------------------
# TRAP 3: The "Unwrap" Heuristic Trap
# AI Mistake: "Phase Unwrapping" logic often breaks near boundaries 
# if simply checking "if val < threshold".
# ---------------------------------------------------------
@pytest.mark.parametrize("val, target, period, expected", [
    (0.1,  30.0, 30.0, 30.1),  # Wrap forward (Tithi end case)
    (29.9, 0.0,  30.0, -0.1),  # Wrap backward (Start of Tithi case)
    (15.0, 14.0, 30.0, 15.0),  # No wrap needed
    (2.0,  25.0, 27.0, 29.0),  # Nakshatra wrap (2 + 27 = 29, close to 25? No wait.)
                               # unwrap logic: diff = 2 - 25 = -23. 
                               # (-23 + 13.5) % 27 - 13.5 = (-9.5) % 27 - 13.5 = 17.5 - 13.5 = 4.0
                               # result = 25 + 4 = 29. CORRECT.
])
def test_trap_unwrap_relative_logic(val, target, period, expected):
    """
    Verifies that unwrap_relative strictly maintains continuity
    regardless of where we are in the cycle.
    """
    res = unwrap_relative(val, target, period)
    assert abs(res - expected) < 1e-9, f"Unwrap failed for {val} near {target}. Got {res}, expected {expected}"

# ---------------------------------------------------------
# TRAP 4: The "Enum Type" Trap
# AI Mistake: Treating IntEnum solely as int and losing type safety semantics,
# or assuming equality with string representation.
# ---------------------------------------------------------
def test_trap_enum_integrity():
    """
    Ensures Enums act like Integers for C-interop but maintain Identity.
    """
    sun_id = PlanetId.SUN
    
    # Must behave like int 0 for swisseph
    assert sun_id == 0 
    assert int(sun_id) == 0
    
    # Must be hashable (usable as dict key)
    d = {PlanetId.SUN: "Star"}
    assert d[0] == "Star" # IntEnum property
    
    # Type check
    assert isinstance(sun_id, PlanetId)

# ---------------------------------------------------------
# TRAP 5: The "Floating Point Equality" Trap
# AI Mistake: Using '==' for float comparison.
# ---------------------------------------------------------
def test_trap_float_equality():
    a = 1.0 / 3.0
    b = 0.3333333333333333
    
    # This assertion EXPECTS a failure if code relies on strict equality
    # We enforce using tolerance (approx)
    
    # Good practice check:
    assert a == pytest.approx(b), "Float comparison needs pytest.approx"