# test_final_core.py
from phoenix_engine.core.config.calibration import CalibrationConfig
from phoenix_engine.infrastructure.time.scale import TimeScale, delta_t_days
from phoenix_engine.infrastructure.astronomy.swiss.manager import SwissContextManager
import swisseph as swe

def run_diagnostics():
    print("🦅 Phoenix Engine v2 Core Diagnostic")
    print("====================================")
    
    # 1. Test Scale & Delta T
    print(f"[1] TimeScale Enum: {TimeScale.UT}")
    try:
        dt = delta_t_days(2460000.5) # Some modern date
        print(f"    Delta T (auto): {dt:.6f} days (~{dt*86400:.2f}s)")
    except Exception as e:
        print(f"❌ Delta T Failed: {e}")

    # 2. Test Configuration
    cfg = CalibrationConfig()
    print(f"[2] Config Loaded: {type(cfg).__name__}")

    # 3. Test Manager & Engine Injection
    try:
        mgr = SwissContextManager(cfg)
        print(f"[3] Manager Initialized: {type(mgr).__name__}")
        
        with mgr as provider:
            print(f"    [+] Provider yielded: {type(provider).__name__}")
            
            # Check Engine Injection
            if hasattr(provider, 'engine'):
                print(f"    [+] Engine Injected: {type(provider.engine).__name__}")
            else:
                print(f"❌ Engine NOT Injected!")

            # 4. Test Calculation (Real Swiss Call)
            # Julian Day for 2024-01-01
            jd = 2460310.5 
            sun_pos = provider.planet_lon_speed(jd, swe.SUN)
            print(f"[4] Calculation Test (Sun):")
            print(f"    Lon: {sun_pos[0]:.4f}° | Speed: {sun_pos[1]:.4f}°/day")
            
            if sun_pos[0] > 0:
                print("✅ SYSTEM OPERATIONAL")
            else:
                print("⚠️ Warning: Sun longitude seems 0.0 (Check Ephemeris path)")

    except Exception as e:
        print(f"❌ Core Crash: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_diagnostics()