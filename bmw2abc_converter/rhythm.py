"""Mapping between note lengths (fractions of a whole note) and BWW durations."""

from __future__ import annotations

from fractions import Fraction

PITCH_TO_BWW: dict[str, str] = {
    "G": "LG", "A": "LA", "B": "B", "c": "C", "d": "D",
    "e": "E", "f": "F", "g": "HG", "a": "HA",
}

PITCH_TO_DOT: dict[str, str] = {
    "G": "lg", "A": "la", "B": "b", "c": "c", "d": "d",
    "e": "e", "f": "f", "g": "hg", "a": "ha",
}

_DENOMS = (1, 2, 4, 8, 16, 32)
_DOT_FACTORS = (Fraction(1), Fraction(3, 2), Fraction(7, 4))

# length -> (denom, dots)
_TABLE: dict[Fraction, tuple[int, int]] = {}
for _d in _DENOMS:
    for _dots, _f in enumerate(_DOT_FACTORS):
        _TABLE.setdefault(Fraction(1, _d) * _f, (_d, _dots))


def bww_duration(length: Fraction) -> tuple[int, int] | None:
    """Return (denom, dots) for a note length, or None if BWW can't express it."""
    return _TABLE.get(Fraction(length))


def nearest_duration(length: Fraction) -> tuple[int, int]:
    """Largest expressible duration not longer than length (shortest if none)."""
    fits = [v for v in _TABLE if v <= length]
    best = max(fits) if fits else min(_TABLE)
    return _TABLE[best]
