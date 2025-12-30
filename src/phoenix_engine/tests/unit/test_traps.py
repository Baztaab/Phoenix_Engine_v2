from __future__ import annotations
import pytest
from phoenix_engine.core.config.calibration import CalibrationConfig
# FIXED IMPORTS: Moved from temporal to core.math.angles
from phoenix_engine.core.math.angles import unwrap_relative, normalize_angle
from phoenix_engine.domain.enums import PlanetId

# ---------------------------------------------------------
# TRAP 1: The "Mutable Default" Argument Trap
# ---------------------------------------------------------
def test_trap_mutable_defaults_in_config():
    """
    Ensures that modifying a nested config object does NOT affect 
    new instances (checking for shared reference bugs).
    """
    cfg1 = CalibrationConfig()
    cfg1.sunrise.use_refraction = False
    cfg1.topo.enabled = True
    
    cfg2 = CalibrationConfig()
    
    assert cfg2.sunrise.use_refraction is True, "CRITICAL: SunriseConfig is shared between instances!"
    assert cfg2.topo.enabled is False, "CRITICAL: TopoConfig is shared between instances!"

# ---------------------------------------------------------
# TRAP 2: The "Circle Wrap" Trap
# ---------------------------------------------------------
def test_trap_angle_normalization():
    """
    Ensures normalize_angle handles negative inputs correctly.
    """
    # 1 degree minus 359 degrees = -358 math, but +2 degrees on circle
    # Renamed: norm_deg -> normalize_angle
    diff = normalize_angle(1.0 - 359.0)
    assert diff == 2.0, f"Angle logic failed. Expected 2.0, got {diff}"
    
    # Wrap multiple times
    huge_angle = 725.0 # 2 * 360 + 5
    assert normalize_angle(huge_angle) == 5.0

# ---------------------------------------------------------
# TRAP 3: The "Unwrap" Heuristic Trap
# ---------------------------------------------------------
@pytest.mark.parametrize("val, target, period, expected", [
    (0.1,  30.0, 30.0, 30.1),  # Wrap forward (Tithi end case)
    (29.9, 0.0,  30.0, -0.1),  # Wrap backward (Start of Tithi case)
    (15.0, 14.0, 30.0, 15.0),  # No wrap needed
    (2.0,  25.0, 27.0, 29.0),  # Nakshatra wrap
])
def test_trap_unwrap_relative_logic(val, target, period, expected):
    """
    Verifies that unwrap_relative strictly maintains continuity.
    """
    res = unwrap_relative(val, target, period=period)
    assert abs(res - expected) < 1e-9, f"Unwrap failed for {val} near {target}. Got {res}, expected {expected}"

# ---------------------------------------------------------
# TRAP 4: The "Enum Type" Trap
# ---------------------------------------------------------
def test_trap_enum_integrity():
    """
    Ensures Enums act like Integers for C-interop but maintain Identity.
    """
    sun_id = PlanetId.SUN
    
    # Must behave like int 0 for swisseph
    assert sun_id == 0 
    assert int(sun_id) == 0
    
    # Must be hashable
    d = {PlanetId.SUN: "Star"}
    assert d[0] == "Star" 
    
    assert isinstance(sun_id, PlanetId)

# ---------------------------------------------------------
# TRAP 5: The "Floating Point Equality" Trap
# ---------------------------------------------------------
def test_trap_float_equality():
    a = 1.0 / 3.0
    b = 0.3333333333333333
    
    assert a == pytest.approx(b), "Float comparison needs pytest.approx"
