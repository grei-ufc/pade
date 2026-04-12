"""Small phasor utilities compatible with the legacy power-systems example."""

from __future__ import annotations

import cmath
import math
from typing import Iterable


def p2r(magnitude: float, angle_degrees: float) -> complex:
    """Convert a polar value into rectangular form."""
    return cmath.rect(magnitude, math.radians(angle_degrees))


def r2p(value: complex) -> tuple[float, float]:
    """Convert a rectangular value into (magnitude, angle_degrees)."""
    return abs(value), math.degrees(cmath.phase(value))


def P(magnitude: float, angle_degrees: float) -> complex:
    """Legacy alias for polar-to-rectangular conversion."""
    return p2r(magnitude, angle_degrees)


def R(value: complex | Iterable[complex]) -> tuple[float, float] | list[tuple[float, float]]:
    """Legacy helper that mirrors the rectangular-to-polar conversion."""
    if isinstance(value, (list, tuple)):
        return [r2p(item) for item in value]
    return r2p(value)
