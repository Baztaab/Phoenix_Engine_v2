from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple


# f(jd) -> (value, speed)
ValueSpeedFn = Callable[[float], Tuple[float, float]]


@dataclass(frozen=True)
class SolveResult:
    root_jd: float
    method: str
    iterations: int
    bracket: Optional[Tuple[float, float]] = None


class SolverError(RuntimeError):
    pass


class NoBracketError(SolverError):
    pass


class NonConvergenceError(SolverError):
    pass


def _sign(x: float) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def bracket_root(
    f: ValueSpeedFn,
    start_jd: float,
    end_jd: float,
    *,
    step_days: float,
) -> Tuple[float, float]:
    """
    Find [a,b] such that f(a) and f(b) have opposite signs.
    Uses a forward scan with step_days.
    """
    if end_jd <= start_jd:
        raise ValueError("end_jd must be > start_jd")
    if step_days <= 0:
        raise ValueError("step_days must be > 0")

    a = float(start_jd)
    va, _ = f(a)
    sa = _sign(va)
    if sa == 0:
        return (a, a)

    x = a
    while x < end_jd:
        nx = min(x + step_days, end_jd)
        vb, _ = f(nx)
        sb = _sign(vb)
        if sb == 0:
            return (nx, nx)
        if sa != sb:
            return (x, nx)
        x = nx
        va, sa = vb, sb

    raise NoBracketError("No sign change found in [start_jd, end_jd].")


def bisection(
    f: ValueSpeedFn,
    a: float,
    b: float,
    *,
    tol_days: float,
    max_iter: int = 80,
) -> SolveResult:
    """
    Robust fallback root finder using bisection on value sign.
    """
    a = float(a)
    b = float(b)
    if b < a:
        a, b = b, a

    va, _ = f(a)
    vb, _ = f(b)
    sa = _sign(va)
    sb = _sign(vb)

    if sa == 0:
        return SolveResult(root_jd=a, method="bisection", iterations=0, bracket=(a, b))
    if sb == 0:
        return SolveResult(root_jd=b, method="bisection", iterations=0, bracket=(a, b))
    if sa == sb:
        raise NoBracketError("Bisection requires opposite signs at endpoints.")

    it = 0
    lo, hi = a, b
    vlo, vhi = va, vb
    while it < max_iter and (hi - lo) > tol_days:
        mid = (lo + hi) / 2.0
        vm, _ = f(mid)
        sm = _sign(vm)
        if sm == 0:
            return SolveResult(root_jd=mid, method="bisection", iterations=it + 1, bracket=(a, b))
        if sm == _sign(vlo):
            lo, vlo = mid, vm
        else:
            hi, vhi = mid, vm
        it += 1

    return SolveResult(root_jd=(lo + hi) / 2.0, method="bisection", iterations=it, bracket=(a, b))


def newton_speed_assisted(
    f: ValueSpeedFn,
    x0: float,
    *,
    bracket: Optional[Tuple[float, float]] = None,
    tol_days: float,
    max_iter: int = 20,
    min_speed: float = 1e-10,
) -> SolveResult:
    """
    Newton-Raphson using speed (derivative) returned by f.
    If bracket is provided, keep iterates inside it (clamp).
    """
    x = float(x0)
    a: Optional[float] = None
    b: Optional[float] = None
    if bracket is not None:
        a, b = float(bracket[0]), float(bracket[1])
        if b < a:
            a, b = b, a
        # clamp initial point
        if x < a:
            x = a
        elif x > b:
            x = b

    for it in range(1, max_iter + 1):
        v, spd = f(x)
        if abs(v) <= 1e-14:
            return SolveResult(root_jd=x, method="newton", iterations=it, bracket=bracket)

        if abs(spd) < min_speed:
            raise NonConvergenceError("Newton derivative too small (stationary / ill-conditioned).")

        dx = v / spd
        nx = x - dx

        # Convergence on x-step
        if abs(nx - x) <= tol_days:
            return SolveResult(root_jd=nx, method="newton", iterations=it, bracket=bracket)

        # If bracketed, clamp iterate (keeps safety)
        if a is not None and b is not None:
            if nx < a:
                nx = a
            elif nx > b:
                nx = b

        x = nx

    raise NonConvergenceError("Newton did not converge within max_iter.")


def solve_root(
    f: ValueSpeedFn,
    start_jd: float,
    end_jd: float,
    *,
    accuracy_seconds: float = 0.5,
    scan_step_days: float = 1.0 / 24.0,  # 1 hour
    newton_max_iter: int = 20,
    bisection_max_iter: int = 80,
    min_speed: float = 1e-10,
) -> SolveResult:
    """
    Hybrid solver:
      1) Bracket using scan steps.
      2) Try speed-assisted Newton inside bracket (fast).
      3) Fallback to bisection (robust).

    All time values are in Julian Days (UT or TT depending on caller convention).
    """
    tol_days = float(accuracy_seconds) / 86400.0

    a, b = bracket_root(f, start_jd, end_jd, step_days=scan_step_days)
    if a == b:
        return SolveResult(root_jd=a, method="bracket_hit", iterations=0, bracket=(a, b))

    # initial guess: midpoint
    x0 = (a + b) / 2.0

    try:
        res = newton_speed_assisted(
            f,
            x0,
            bracket=(a, b),
            tol_days=tol_days,
            max_iter=newton_max_iter,
            min_speed=min_speed,
        )
        return SolveResult(root_jd=res.root_jd, method="newton", iterations=res.iterations, bracket=(a, b))
    except (NonConvergenceError, NoBracketError):
        # fallback robust
        return bisection(
            f,
            a,
            b,
            tol_days=tol_days,
            max_iter=bisection_max_iter,
        )