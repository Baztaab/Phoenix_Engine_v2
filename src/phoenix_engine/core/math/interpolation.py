"""Interpolation helpers for Panchanga calculations."""

from __future__ import annotations

from typing import Iterable, List, Optional


def inverse_lagrange(
    x_list: Iterable[float],
    y_list: Iterable[float],
    y_target: float,
    *,
    max_points: int = 5,
    eps: float = 1e-10,
) -> float:
    """
    Inverse Lagrange interpolation: estimate x such that y(x)=y_target
    given sample pairs (x_i, y_i).

    Numerically-stable implementation:
    - Uses barycentric Lagrange form for x as a function of y.
    - Uses only the max_points nearest samples to y_target (local fit).
    - Handles exact-hit nodes and detects duplicate/near-duplicate y.

    Args:
        x_list, y_list: sample points (must be same length).
        y_target: desired y value.
        max_points: number of nearest samples to use (>=2). Default 5 is ideal for Panchanga.
        eps: tolerance for node hit / duplicate detection.

    Raises:
        ValueError: bad input, insufficient points, or duplicate/near-duplicate y values.
        ZeroDivisionError: ill-conditioned evaluation.
    """
    xs = [float(v) for v in x_list]
    ys = [float(v) for v in y_list]
    if len(xs) != len(ys):
        raise ValueError("x_list and y_list must be the same length.")
    n = len(xs)
    if n < 2:
        raise ValueError("Need at least 2 points for interpolation.")

    k = max(2, int(max_points))
    if n > k:
        idx = sorted(range(n), key=lambda i: abs(ys[i] - float(y_target)))[:k]
        xs = [xs[i] for i in idx]
        ys = [ys[i] for i in idx]
        n = len(xs)

    yt = float(y_target)

    # Exact-hit short-circuit
    for xi, yi in zip(xs, ys):
        if abs(yt - yi) <= eps:
            return xi

    # Duplicate/near-duplicate y detection (ill-defined)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(ys[i] - ys[j]) <= eps:
                raise ValueError("Duplicate/near-duplicate y values; inverse Lagrange is ill-defined.")

    # Barycentric weights in y-domain: w_i = 1 / Π_{j≠i}(y_i - y_j)
    w: List[float] = []
    for i in range(n):
        denom = 1.0
        yi = ys[i]
        for j in range(n):
            if j == i:
                continue
            denom *= (yi - ys[j])
        w.append(1.0 / denom)

    # Evaluate barycentric rational form
    num = 0.0
    den = 0.0
    for xi, yi, wi in zip(xs, ys, w):
        t = wi / (yt - yi)
        num += t * xi
        den += t

    if abs(den) <= eps:
        raise ZeroDivisionError("Ill-conditioned interpolation: denominator too small.")

    return num / den
