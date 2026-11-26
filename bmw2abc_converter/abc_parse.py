"""Parser for the subset of ABC used in Ed's pipe tune collection.

Produces abc_model.Tune objects for bww_writer. Anything not understood is
reported in Tune.warnings rather than silently dropped.
"""

from __future__ import annotations

import re
from fractions import Fraction

from .abc_model import Bar, Ending, EndingClose, Line, Meter, Note, Rest, Tune, Tuplet

_FIELD_RE = re.compile(r"^([A-Za-z]):(.*)$")
_PART_RE = re.compile(r"^%\s*(\d+(?:st|nd|rd|th)\s+Part)\s*$", re.IGNORECASE)

_TOKEN_RE = re.compile(
    r"""
    (?P<ws>\s+)
  | (?P<comment>%.*)
  | (?P<label_end>\["(?P<label_n>[1-9])\ of\ (?P<label_m>[1-9])")
  | (?P<grace>\{(?P<grace_body>[^}]*)\})
  | (?P<quote>"[^"]*")
  | (?P<deco>![^!\s]*!)
  | (?P<field>\[(?P<fname>[A-Za-z]):(?P<fval>[^\]]*)\])
  | (?P<bracket_end>\[(?P<bracket_num>[1-9]))
  | (?P<bar>\[\|:|:\|\]|::|:\|\|?|\|:|\|\]|\[\||\|\||\|)(?P<bar_num>[1-9])?
  | (?P<end_close>\])
  | (?P<tuplet>\((?P<tuplet_n>[2-9])(?::\d*){0,2})
  | (?P<slur>[()])
  | (?P<note>(?P<acc>[_=^]*)(?P<pitch>[A-Ga-g])(?P<octave>[,']*)(?P<len>\d*/*\d*))
  | (?P<rest>[zx](?P<rest_len>\d*/*\d*))
  | (?P<broken>[<>]{1,3})
  | (?P<tie>-)
  | (?P<ignore>[.y\\])
    """,
    re.VERBOSE,
)

_BROKEN = {
    ">": (Fraction(3, 2), Fraction(1, 2)),
    ">>": (Fraction(7, 4), Fraction(1, 4)),
    ">>>": (Fraction(15, 8), Fraction(1, 8)),
    "<": (Fraction(1, 2), Fraction(3, 2)),
    "<<": (Fraction(1, 4), Fraction(7, 4)),
    "<<<": (Fraction(1, 8), Fraction(15, 8)),
}


def _length_multiplier(spec: str) -> Fraction:
    """ABC length suffix ('', '2', '/', '//', '3/', '3/2') -> multiplier of L."""
    m = re.fullmatch(r"(\d*)(/*)(\d*)", spec)
    if not m:
        return Fraction(1)
    num = int(m.group(1)) if m.group(1) else 1
    slashes = len(m.group(2))
    if not slashes:
        return Fraction(num)
    den = int(m.group(3)) if m.group(3) else 2 ** slashes
    return Fraction(num, den)


def _parse_unit(value: str, warn) -> Fraction:
    m = re.match(r"\s*(\d+)/(\d+)(.*)$", value)
    if not m:
        warn(f"L:{value} not understood; using 1/8")
        return Fraction(1, 8)
    if m.group(3).strip():
        warn(f"L:{value.strip()} has trailing text '{m.group(3).strip()}'; using {m.group(1)}/{m.group(2)}")
    return Fraction(int(m.group(1)), int(m.group(2)))


def _parse_tempo(value: str) -> int | None:
    m = re.search(r"=\s*(\d+)", value) or re.fullmatch(r"\s*(\d+)\s*", value)
    return int(m.group(1)) if m else None


class _TuneParser:
    def __init__(self) -> None:
        self.tune = Tune()
        self.unit = Fraction(1, 8)
        self.in_body = False
        self.have_title = False
        self.have_composer = False
        self.kept_voice: str | None = None
        self.voice: str | None = None
        self.dropped_voices: set[str] = set()
        self.pending_label: str | None = None
        self.chords = 0
        self.slurs = 0
        self.slash_rests = 0
        self.decorations: dict[str, int] = {}
        # rhythm state
        self.last_note: Note | None = None
        self.pending_factor: Fraction | None = None

    def warn(self, msg: str) -> None:
        self.tune.warnings.append(msg)

    # -- fields -----------------------------------------------------------
    def field(self, name: str, value: str, inline: bool = False) -> list:
        value = value.strip()
        if name == "T":
            if not self.have_title:
                self.tune.title = value
                self.have_title = True
        elif name == "R":
            self.tune.tune_type = self.tune.tune_type or value or None
        elif name == "C":
            if not self.have_composer:
                self.tune.composer = value or None
                self.have_composer = True
        elif name == "Q":
            if self.tune.tempo is None:
                self.tune.tempo = _parse_tempo(value)
        elif name == "L":
            self.unit = _parse_unit(value, self.warn)
        elif name == "M":
            if self.in_body:
                return [Meter(value)]
            self.tune.meter = value
        elif name == "K":
            if value.split()[0:1] not in (["HP"], ["Hp"]):
                self.warn(f"K:{value} — only K:HP / K:Hp are supported; writing the pipe key")
            self.in_body = True
        elif name == "V":
            vid = value.split()[0] if value else ""
            if self.kept_voice is None:
                self.kept_voice = vid
            self.voice = vid
            if vid != self.kept_voice and vid not in self.dropped_voices:
                self.dropped_voices.add(vid)
                self.warn(f"harmony voice V:{vid} dropped")
        # all other fields ignored
        return []

    def voice_kept(self) -> bool:
        return self.voice is None or self.voice == self.kept_voice

    # -- music ------------------------------------------------------------
    def music_line(self, text: str, lineno: int) -> None:
        items: list = []
        # beam_start: whitespace/bar/line start since the last note
        separated = True
        pos = 0
        pending_grace = ""
        grace_separated = True
        while pos < len(text):
            m = _TOKEN_RE.match(text, pos)
            if not m or m.end() == pos:
                self.warn(f"*** '{text[pos]}' not recognised *** (line {lineno})")
                pos += 1
                continue
            pos = m.end()
            kind = m.lastgroup
            if kind in ("grace_body", "fname", "fval", "bracket_num", "bar_num", "tuplet_n",
                        "acc", "pitch", "octave", "len", "rest_len", "label_n", "label_m"):
                kind = next(k for k in ("label_end", "grace", "field", "bracket_end", "bar", "tuplet",
                                        "note", "rest") if m.group(k))
            if kind == "ws":
                separated = True
            elif kind == "comment":
                break
            elif kind == "grace":
                if not pending_grace:
                    grace_separated = separated
                pending_grace += m.group("grace_body")
            elif kind == "quote":
                self.chords += 1
            elif kind == "deco":
                name = m.group("deco")
                if name == "!head-slashr!":
                    self.slash_rests += 1
                else:
                    self.decorations[name] = self.decorations.get(name, 0) + 1
            elif kind == "field":
                fname, fval = m.group("fname"), m.group("fval")
                if fname == "V":
                    self.field("V", fval)
                    if not self.voice_kept():
                        return
                else:
                    items.extend(self.field(fname, fval, inline=True))
            elif kind == "label_end":
                # BWW writes "N of M" endings as 'NM
                items.append(Ending(int(m.group("label_n") + m.group("label_m"))))
                separated = True
            elif kind == "bracket_end":
                items.append(Ending(int(m.group("bracket_num"))))
                separated = True
            elif kind == "bar":
                bar = m.group("bar")
                bar = {":||": ":|", ":|]": ":|", "[|:": "|:"}.get(bar, bar)
                items.append(Bar(bar))
                if m.group("bar_num"):
                    items.append(Ending(int(m.group("bar_num"))))
                separated = True
            elif kind == "end_close":
                items.append(EndingClose())
            elif kind == "tuplet":
                items.append(Tuplet(int(m.group("tuplet_n"))))
            elif kind == "slur":
                self.slurs += 1
            elif kind == "note":
                if m.group("acc"):
                    self.warn(f"line {lineno}: accidental {m.group('acc')}{m.group('pitch')} ignored")
                if m.group("octave"):
                    self.warn(f"line {lineno}: octave mark on {m.group('pitch')}{m.group('octave')} ignored")
                pitch = m.group("pitch")
                if pitch in "CDEF":
                    self.warn(f"line {lineno}: {pitch} is below the chanter range; written as {pitch.lower()}")
                    pitch = pitch.lower()
                if pitch == "b":
                    self.warn(f"line {lineno}: b is above the chanter range; written as B")
                    pitch = "B"
                length = self.unit * _length_multiplier(m.group("len"))
                if self.pending_factor is not None:
                    length *= self.pending_factor
                    self.pending_factor = None
                beam_start = grace_separated if pending_grace else separated
                note = Note(pitch, length, pending_grace, beam_start=beam_start)
                pending_grace = ""
                items.append(note)
                self.last_note = note
                separated = False
            elif kind == "rest":
                length = self.unit * _length_multiplier(m.group("rest_len"))
                if self.pending_factor is not None:
                    length *= self.pending_factor
                    self.pending_factor = None
                items.append(Rest(length))
                self.last_note = None
                separated = True
            elif kind == "broken":
                first, second = _BROKEN[m.group("broken")]
                if self.last_note is None:
                    self.warn(f"line {lineno}: broken rhythm '{m.group('broken')}' with no preceding note")
                else:
                    self.last_note.length *= first
                    self.pending_factor = second
            elif kind == "tie":
                if self.last_note is None:
                    self.warn(f"line {lineno}: tie with no preceding note")
                else:
                    self.last_note.tie = True
            # "ignore": staccato dots, spacers, continuations
        if pending_grace:
            self.warn(f"line {lineno}: grace {{{pending_grace}}} at end of line with no note")
        if items:
            self.tune.lines.append(Line(items, self.pending_label))
            self.pending_label = None

    def feed(self, raw: str, lineno: int) -> None:
        line = raw.rstrip()
        if not line:
            return
        if line.startswith("%"):
            if m := _PART_RE.match(line):
                self.pending_label = m.group(1)
            return
        if m := _FIELD_RE.match(line):
            self.field(m.group(1), m.group(2))
            return
        if not self.in_body:
            return
        if not self.voice_kept():
            # inline [V:..] at line start may switch back to the kept voice
            if not line.lstrip().startswith("[V:"):
                return
        self.music_line(line, lineno)

    def finish(self) -> Tune:
        if self.chords:
            self.warn(f"dropped {self.chords} chord symbol(s)/annotation(s)")
        if self.slurs:
            self.warn(f"dropped {self.slurs} slur mark(s)")
        if self.slash_rests:
            self.warn(f"{self.slash_rests} slash beat marks written as plain rests")
        for name, n in self.decorations.items():
            self.warn(f"decoration {name} dropped ({n}×)")
        return self.tune


def parse_abc(text: str) -> list[Tune]:
    """Parse an ABC file into one Tune per X: field, in file order."""
    tunes: list[Tune] = []
    parser: _TuneParser | None = None
    raw_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    joined: list[tuple[int, str]] = []
    carry: tuple[int, str] | None = None
    for lineno, raw in enumerate(raw_lines, 1):
        if carry:
            lineno, raw = carry[0], carry[1] + " " + raw
            carry = None
        stripped = raw.rstrip()
        if stripped.endswith("\\") and not stripped.startswith("%"):
            carry = (lineno, stripped[:-1])
            continue
        joined.append((lineno, raw))
    if carry:
        joined.append(carry)
    for lineno, raw in joined:
        if raw.startswith("X:"):
            if parser:
                tunes.append(parser.finish())
            parser = _TuneParser()
            continue
        if parser is not None:
            parser.feed(raw, lineno)
    if parser:
        tunes.append(parser.finish())
    return tunes
