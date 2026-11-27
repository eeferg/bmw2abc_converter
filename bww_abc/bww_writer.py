"""Write an abc_model.Tune as Bagpipe Music Writer Gold (.bww) text.

Layout follows the BMW Gold / Lee & Sons files: one staff per ABC source line,
each bar after the first on its own tab-indented line introduced by '!'.
Returned text uses '\\n'; the CLI writes it with CRLF like BMW Gold does.
"""

from __future__ import annotations

from fractions import Fraction

from .abc_model import Bar, Ending, EndingClose, Line, Meter, Note, Rest, Tune, Tuplet
from .grace_reverse import embellishment_tokens
from .rhythm import PITCH_TO_BWW, PITCH_TO_DOT, bww_duration, nearest_duration

BWW_BOILERPLATE = """Bagpipe Music Writer Gold:1.0

MIDINoteMappings,(54,56,58,59,61,63,64,66,68,56,58,60,61,63,65,66,68,70,55,57,59,60,62,64,65,67,69)

FrequencyMappings,(370,415,466,494,554,622,659,740,831,415,466,523,554,622,699,740,831,932,392,440,494,523,587,659,699,784,880)

InstrumentMappings,(71,71,45,33,1000,60,70)

GracenoteDurations,(20,40,30,50,100,200,800,1200,250,250,250,500,200)

FontSizes,(90,110,65,80,0)

TuneFormat,(1,1,F,L,400,400,400,400,L,0,0)"""

DEFAULT_TEMPO = 90

_TITLE_FMT = "(T,C,0,0,Times New Roman,24,700,0,0,18,0,0,0)"
_TYPE_FMT = "(Y,L,0,0,Times New Roman,14,700,0,0,18,0,0,0)"
_COMPOSER_FMT = "(M,R,0,0,Times New Roman,14,700,0,0,18,0,0,0)"
_FOOTER_FMT = "(F,L,0,0,Times New Roman,10,400,0,0,18,0,0,0)"

_CLEF = "& sharpf sharpc"
_CLOSERS = {":|", "||", "|]", "|:", "::"}


def meter_token(meter: str) -> str:
    meter = meter.strip()
    if meter == "C":
        return "C"
    if meter == "C|":
        return "C_"
    return meter.replace("/", "_")


def _quote(text: str) -> str:
    return '"' + text.replace('"', "'") + '"'


def _header(tune: Tune) -> list[str]:
    out = [BWW_BOILERPLATE, "", f"TuneTempo,{tune.tempo or DEFAULT_TEMPO}", ""]
    out.append(_quote(tune.title or "Untitled") + "," + _TITLE_FMT)
    if tune.tune_type:
        out.append(_quote(tune.tune_type) + "," + _TYPE_FMT)
    if tune.composer:
        out.append(_quote(tune.composer) + "," + _COMPOSER_FMT)
    if tune.source:  # B: has no BWW field; the footer is the closest home
        out.append(_quote(tune.source) + "," + _FOOTER_FMT)
    out += ["", ""]
    return out


class _StaffWriter:
    """Holds cross-staff state: open endings, ties, tuplets, carried repeats."""

    def __init__(self, tune: Tune) -> None:
        self.tune = tune
        self.ending_open = False
        self.tie_pending = False
        self.tuplet_left = 0
        self.tuplet_n = 0
        self.carry_repeat_start = False

    def warn(self, msg: str) -> None:
        self.tune.warnings.append(msg)

    # -- helpers ----------------------------------------------------------
    @staticmethod
    def _beamable(length: Fraction) -> bool:
        dur = bww_duration(length) or nearest_duration(length)
        return dur[0] >= 8

    def _beam_suffixes(self, items: list) -> dict[int, str]:
        """Map item index -> 'r'/'l' for notes in beam groups of 2+."""
        suffix: dict[int, str] = {}
        group: list[int] = []

        def flush() -> None:
            if len(group) >= 2:
                suffix[group[0]] = "r"
                for i in group[1:]:
                    suffix[i] = "l"
            group.clear()

        for i, item in enumerate(items):
            if isinstance(item, Note):
                if not self._beamable(item.length):
                    flush()
                    continue
                if item.beam_start:
                    flush()
                group.append(i)
            elif isinstance(item, (Tuplet, EndingClose, Meter)):
                continue
            else:
                flush()
        flush()
        return suffix

    def _note_tokens(self, note: Note, suffix: str, staff_no: int) -> list[str]:
        toks: list[str] = []
        emb, warning = embellishment_tokens(note.grace, note.pitch)
        if warning:
            self.warn(f"staff {staff_no}: {warning}")
        toks += emb
        if self.tuplet_left == -1:  # tuplet announced; Lee puts ^3s after the grace
            toks.append(f"^{self.tuplet_n}s")
            self.tuplet_left = self.tuplet_n
        if note.tie:
            toks.append("^ts")
        dur = bww_duration(note.length)
        if dur is None:
            dur = nearest_duration(note.length)
            self.warn(f"staff {staff_no}: {note.pitch} length {note.length} has no BWW duration; "
                      f"wrote 1/{dur[0]}")
        denom, dots = dur
        toks.append(f"{PITCH_TO_BWW[note.pitch]}{suffix}_{denom}")
        if dots:
            toks.append("'" * dots + PITCH_TO_DOT[note.pitch])
        if self.tie_pending:
            toks.append("^te")
            self.tie_pending = False
        if note.tie:
            self.tie_pending = True
        if self.tuplet_left > 0:
            self.tuplet_left -= 1
            if self.tuplet_left == 0:
                toks.append(f"^{self.tuplet_n}e")
        return toks

    # -- staff ------------------------------------------------------------
    def staff(self, line: Line, staff_no: int, first: bool, next_item) -> list[str]:
        """Return the physical text lines for one staff."""
        items = line.items
        suffix = self._beam_suffixes(items)
        content_idx = [i for i, it in enumerate(items) if isinstance(it, (Note, Rest, Ending, Tuplet))]
        first_content = content_idx[0] if content_idx else len(items)
        last_content = content_idx[-1] if content_idx else -1

        head = _CLEF + (f" {meter_token(self.tune.meter)}" if first else "")
        physical: list[list[str]] = [[head]]
        if self.carry_repeat_start:
            physical[0].append("I!''")
            self.carry_repeat_start = False
        cur = physical[0]
        terminated = False

        for i, item in enumerate(items):
            if isinstance(item, Note):
                cur += self._note_tokens(item, suffix.get(i, ""), staff_no)
            elif isinstance(item, Rest):
                dur = bww_duration(item.length) or nearest_duration(item.length)
                if dur[1] or bww_duration(item.length) is None:
                    self.warn(f"staff {staff_no}: rest length {item.length} written as 1/{dur[0]}")
                cur.append(f"REST_{dur[0]}")
            elif isinstance(item, Tuplet):
                self.tuplet_n = item.count
                self.tuplet_left = -1
            elif isinstance(item, Ending):
                if self.ending_open:
                    cur.append("_'")
                cur.append(f"'{item.number}")
                self.ending_open = True
            elif isinstance(item, EndingClose):
                if self.ending_open:
                    cur.append("_'")
                    self.ending_open = False
            elif isinstance(item, Meter):
                cur.append(meter_token(item.meter))
            elif isinstance(item, Bar):
                at_start = i < first_content
                at_end = i > last_content
                kind = item.kind
                if (self.ending_open and kind in _CLOSERS and not at_start) or (
                        self.ending_open and at_end):
                    cur.append("_'")
                    self.ending_open = False
                if at_start:
                    if kind in ("|:", "::"):
                        cur.append("I!''")
                    elif kind == "[|":
                        cur.append("I!")
                elif at_end:
                    terminated = True
                    if kind in (":|", "::"):
                        cur.append("''!I")
                        if kind == "::":
                            self.carry_repeat_start = True
                    elif kind == "|]":
                        cur.append("!I")
                    elif kind == "||":
                        cur.append("!!t")
                    elif kind == "|:":
                        cur.append("!t")
                        self.carry_repeat_start = True
                    else:
                        cur.append("!t")
                else:
                    tok = {"|": "!", ":|": "''!I", "|:": "I!''", "::": "''!I I!''",
                           "|]": "!I", "[|": "I!", "||": "I!"}[kind]
                    if tok == "!":
                        cur = ["!"]
                        physical.append(cur)
                    else:
                        cur.append(tok)
        if not terminated:
            if self.ending_open:
                cur.append("_'")
                self.ending_open = False
            self.warn(f"staff {staff_no}: line ends mid-bar (no barline at end of ABC line)")
        return [_format(p, idx == 0) for idx, p in enumerate(physical)]


def _format(tokens: list[str], first: bool) -> str:
    if first:
        return " ".join(tokens)
    return tokens[0] + "\t" + " ".join(tokens[1:])


def _carry_pickups(lines: list[Line]) -> list[Line]:
    """Move notes after a line's last barline to the start of the next line.

    ABC often ends a line with the lead-in to the next part; BWW staves end on a
    barline, and Lee's files put such pickups at the start of the next staff.
    """
    out = [Line(list(l.items), l.part_label) for l in lines]
    for n in range(len(out) - 1):
        if not any(isinstance(it, (Note, Rest)) for it in out[n].items):
            continue
        items = out[n].items
        last_bar = max((i for i, it in enumerate(items) if isinstance(it, Bar)), default=None)
        if last_bar is None:
            continue
        trailing = items[last_bar + 1:]
        if any(isinstance(it, (Note, Rest, Ending, Tuplet)) for it in trailing):
            del items[last_bar + 1:]
            out[n + 1].items[:0] = trailing
    return out


def write_bww(tune: Tune) -> str:
    """Complete BWW file text for one tune ('\\n' line endings)."""
    out = _header(tune)
    writer = _StaffWriter(tune)
    lines = _carry_pickups(tune.lines)
    empty = [n for n, l in enumerate(lines) if not any(isinstance(it, (Note, Rest)) for it in l.items)]
    for n in empty:
        writer.warn(f"staff {n + 1}: has no notes; skipped")
    lines = [l for n, l in enumerate(lines) if n not in empty]
    for n, line in enumerate(lines):
        next_item = lines[n + 1].items[0] if n + 1 < len(lines) and lines[n + 1].items else None
        if line.part_label:
            out.append("")
            out.append(_quote(line.part_label))
        out += writer.staff(line, n + 1, n == 0, next_item)
        out.append("")
    if writer.ending_open:
        writer.warn("ending still open at end of tune")
    return "\n".join(out).rstrip("\n") + "\n"
