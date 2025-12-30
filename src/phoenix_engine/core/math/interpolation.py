from __future__ import annotations

"""Interpolation helpers for Panchanga calculations."""

from typing import Iterable, List


def inverse_lagrange(
    x_list: Iterable[float],
    y_list: Iterable[float],
    y_target: float,
    *,
    max_points: int = 5,
    eps: float = 1e-10,
) -> float:
    """Inverse Lagrange interpolation: estimate x such that y(x)=y_target.

    Numerically safer for Panchanga use:
    - Uses barycentric Lagrange form for x as a function of y.
    - Uses only up to `max_points` nearest samples to y_target (local fit).
    - Handles exact-hit nodes and detects duplicate/near-duplicate y.
    """
    xs: List[float] = [float(v) for v in x_list]
    ys: List[float] = [float(v) for v in y_list]

    if len(xs) != len(ys):
        raise ValueError("x_list and y_list must be the same length.")
    n = len(xs)
    if n < 2:
        raise ValueError("Need at least 2 points for inverse interpolation.")

    k = max(2, int(max_points))
    if n > k:
        idx = sorted(range(n), key=lambda i: abs(ys[i] - float(y_target)))[:k]
        xs = [xs[i] for i in idx]
        ys = [ys[i] for i in idx]
        n = len(xs)

    yt = float(y_target)

    # exact-hit shortcut
    for xi, yi in zip(xs, ys):
        if abs(yt - yi) <= eps:
            return xi

    # duplicate/near-duplicate y check
    for i in range(n):
        for j in range(i + 1, n):
            if abs(ys[i] - ys[j]) <= eps:
                raise ValueError("Duplicate/near-duplicate y values; inverse interpolation is ill-defined.")

    # barycentric weights in y-domain: w_i = 1 / Π_{j≠i}(y_i - y_j)
    w: List[float] = []
    for i in range(n):
        denom = 1.0
        yi = ys[i]
        for j in range(n):
            if j == i:
                continue
            denom *= (yi - ys[j])
        if abs(denom) <= eps:
            raise ZeroDivisionError("Ill-conditioned inverse interpolation (denominator too small).")
        w.append(1.0 / denom)

    # evaluate barycentric rational form
    num = 0.0
    den = 0.0
    for xi, yi, wi in zip(xs, ys, w):
        t = wi / (yt - yi)
        num += t * xi
        den += t

    if abs(den) <= eps:
        raise ZeroDivisionError("Ill-conditioned inverse interpolation (final denominator too small).")

    return num / den


__all__ = ["inverse_lagrange"]
