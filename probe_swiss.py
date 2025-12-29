import swisseph as swe
import sys

print("Codex Probe Initiated...")
print(f"SwissEph Version: {swe.version}")
print(f"Python Version: {sys.version.split()[0]}")

# Test Data
jd = 2460310.5
body = 0 # Sun
geo_tup = (51.5, 0.0, 0.0)
lon, lat, alt = 51.5, 0.0, 0.0
rsmi = 1 # Rise
flags = 2 # Speed
press = 1013.25
temp = 15.0

signatures = [
    {
        "name": "Standard (8 args)",
        "args": (jd, body, "", flags, rsmi, geo_tup, press, temp),
        "desc": "(tjd, body, '', flags, rsmi, (geo), p, t)"
    },
    {
        "name": "Legacy String (7 args)",
        "args": (jd, body, "", rsmi, geo_tup, press, temp),
        "desc": "(tjd, body, '', rsmi, (geo), p, t)"
    },
    {
        "name": "Legacy Int (7 args) [Strategy 3]",
        "args": (jd, body, 0, rsmi, geo_tup, press, temp),
        "desc": "(tjd, body, 0, rsmi, (geo), p, t)"
    },
    {
        "name": "Flattened Geo (9 args)",
        "args": (jd, body, "", flags, rsmi, lon, lat, alt, press, temp),
        "desc": "(tjd, body, '', flags, rsmi, lon, lat, alt, p, t)"
    },
    {
        "name": "Flattened Geo Int (9 args)",
        "args": (jd, body, 0, rsmi, lon, lat, alt, press, temp),
        "desc": "(tjd, body, 0, rsmi, lon, lat, alt, p, t)"
    },
    {
        "name": "Flattened Geo Short (7 args) [Strategy 4]",
        "args": (jd, body, 0, rsmi, lon, lat, alt),
        "desc": "(tjd, body, 0, rsmi, lon, lat, alt)"
    },
    {
        "name": "No Star Arg (6 args)",
        "args": (jd, body, rsmi, geo_tup, press, temp),
        "desc": "(tjd, body, rsmi, (geo), p, t)"
    },
     {
        "name": "No Star Arg Flattened (8 args)",
        "args": (jd, body, rsmi, lon, lat, alt, press, temp),
        "desc": "(tjd, body, rsmi, lon, lat, alt, p, t)"
    }
]

print("\nTesting Signatures:")
success = False
for sig in signatures:
    print(f"\n[?] Trying: {sig['name']}")
    print(f"    Signature: {sig['desc']}")
    try:
        res = swe.rise_trans(*sig['args'])
        print(f"SUCCESS! Result: {res}")
        success = True
        break
    except Exception as e:
        print(f"Failed: {e}")

if not success:
    print("\nAll probes failed. This binary is extremely non-standard.")
else:
    print("\nProbe Complete. We found the correct signature!")
