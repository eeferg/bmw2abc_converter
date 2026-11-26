"""Data model for parsed ABC tunes (input to the BWW writer)."""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction


@dataclass
class Note:
    pitch: str  # ABC letter: G A B c d e f g a
    length: Fraction  # fraction of a whole note, after broken rhythm
    grace: str = ""  # contents of {...}
    tie: bool = False  # ABC '-' after this note
    beam_start: bool = True  # whitespace / bar / line start precedes it


@dataclass
class Rest:
    length: Fraction


@dataclass
class Bar:
    kind: str  # "|" "||" "|]" "[|" "|:" ":|" "::"


@dataclass
class Ending:
    number: int


@dataclass
class Tuplet:
    count: int


@dataclass
class Meter:
    meter: str  # as in ABC, e.g. "C|", "6/8"


Item = Note | Rest | Bar | Ending | Tuplet | Meter


@dataclass
class Line:
    items: list[Item] = field(default_factory=list)
    part_label: str | None = None


@dataclass
class Tune:
    title: str = ""
    tune_type: str | None = None
    composer: str | None = None
    tempo: int | None = None
    meter: str = "4/4"
    lines: list[Line] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
