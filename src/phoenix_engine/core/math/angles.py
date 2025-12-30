from __future__ import annotations

"""Angle helpers used by Panchanga math.

All angles are in degrees unless stated otherwise.
"""

from typing import Iterable, List


def normalize_angle(angle: float, *, start: float = 0.0, period: float = 360.0) -> float:
    """Normalize angle into [start, start + period)."""
    a = float(angle)
    s = float(start)
    p = float(period)
    return (a - s) % p + s


def unwrap_angles(angles: Iterable[float], *, period: float = 360.0) -> List[float]:
    """Unwrap circular angles into a continuous sequence.

    Uses the shortest signed difference to avoid jumps at wrap boundaries.
    Example: [340, 350, 10, 20] -> [340, 350, 370, 380]
    """
    seq = [float(x) for x in angles]
    if not seq:
        return []

    out = [seq[0]]
    half = period / 2.0
    for a in seq[1:]:
        prev = out[-1]
        diff = (a - prev + half) % period - half
        out.append(prev + diff)
    return out


def unwrap_relative(val: float, target: float, *, period: float = 360.0) -> float:
    """Unwrap val (mod period) to be continuous around target.

    Keeps (val - target) in [-period/2, +period/2].
    """
    v = float(val)
    t = float(target)
    p = float(period)
    half = p / 2.0
    diff = (v - t + half) % p - half
    return t + diff


def extend_angle_range(
    angles: Iterable[float], *, span: float = 360.0, period: float = 360.0
) -> List[float]:
    """Extend angles by adding +period copies until covered span >= span."""
    base = [float(x) for x in angles]
    if not base:
        return []
    ext = base[:]
    while max(ext) - min(ext) < float(span):
        ext += [a + float(period) for a in base]
    return ext


__all__ = [
    "extend_angle_range",
    "normalize_angle",
    "unwrap_angles",
    "unwrap_relative",
]
