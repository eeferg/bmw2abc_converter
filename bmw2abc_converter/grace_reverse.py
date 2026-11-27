"""Reverse embellishment lookup: ABC grace group + following note -> BWW tokens."""

from __future__ import annotations

from collections import defaultdict

from .grace_notes import GRACE
from .grace_prefs import GRACE_PREFS

# Grace string -> all BWW tokens that render to it.
_BY_SEQ: dict[str, list[str]] = defaultdict(list)
for _tok, _seq in GRACE.items():
    _BY_SEQ[_seq].append(_tok)

# Preferred token when several share a grace string and the Lee corpus gives
# no preference for this note.
_OVERRIDES: dict[str, str] = {
    "A": "ag",      # single grace, not a strike
    "B": "bg",
    "c": "cg",
    "d": "dg",
    "e": "eg",
    "f": "fg",
    "g": "gg",
    "gf": "dbhg",   # doubling on high G
    "ag": "dbha",   # doubling on high A
    "dG": "hgrp",   # half grip
    "fe": "hstf",   # half strike on F
    "eA": "hste",   # half strike on E
    "GdG": "grp",   # grip
    "GBG": "grpb",  # grip with B
    "gdGdG": "ggrpd",
    "adGdG": "tgrpd",
    "dGdG": "hgrpd",
    "dGcG": "hbubly",
    "GAG": "brl",   # birl
    "AGAG": "abr",  # birl from A
    "gAGAG": "gbr",  # G-gracenote birl
    "aAGAG": "tbr",  # thumb birl
    "dc": "hthrd",  # half D throw
    "G2dc": "tra",
    "G2": "echolg",
}

# Grace strings written by older versions of the BWW->ABC converter.
_LEGACY: dict[tuple[str, str], str] = {
    ("gec", "d"): "lgstd",  # bww2abc.js rendered lgstd as {gec}; correct is {gdc}
}

_SINGLE = {"A": "ag", "B": "bg", "c": "cg", "d": "dg", "e": "eg",
           "f": "fg", "g": "gg", "a": "tg"}


def embellishment_tokens(grace: str, pitch: str) -> tuple[list[str], str | None]:
    """BWW tokens for ABC grace group `grace` before note `pitch`, plus a warning."""
    if not grace:
        return [], None
    if (grace, pitch) in _LEGACY:
        return [_LEGACY[(grace, pitch)]], None
    if (grace, pitch) in GRACE_PREFS:
        return [GRACE_PREFS[(grace, pitch)]], None
    candidates = _BY_SEQ.get(grace, [])
    if len(candidates) == 1:
        return [candidates[0]], None
    if candidates:
        if grace in _OVERRIDES:
            return [_OVERRIDES[grace]], None
        choice = sorted(candidates)[0]
        return [choice], f"ambiguous grace {{{grace}}} before {pitch}: chose {choice} from {sorted(candidates)}"
    tokens = [_SINGLE[ch] for ch in grace if ch in _SINGLE]
    warning = f"no named embellishment for {{{grace}}} before {pitch}; written as single graces"
    if "G" in grace:
        warning += f"; low-G grace in {{{grace}}} cannot be written"
    if unknown := [ch for ch in grace if ch not in _SINGLE and ch != "G"]:
        warning += f"; dropped {''.join(unknown)!r}"
    return tokens, warning
