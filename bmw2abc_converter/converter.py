"""
BWW -> ABC converter.
Ported from bww2abc.js by Jean-Francois Moine (GPL3+).
See docs/bww_format.md for format details.
"""

import re
import sys
from pathlib import Path

from .grace_notes import DECO, GRACE

# Regex for a note token: optional high/low prefix is already stripped before matching.
_NOTE_RE = re.compile(r"([ABCDEFG])([rl]?)_(\d+)")
# Regex for an accidental token preceding a note.
_ACC_RE = re.compile(r"(sharp|flat|natural)(.*)")
# Regex for a time-signature token (used inline in music).
_TIMESIG_RE = re.compile(r"\d+_\d+")
# Regex for dotted-note marker: one or two apostrophes then a letter a-h or l.
_DOT_RE = re.compile(r"'{1,2}[abcdefghl]")


def _abc_duration(denom: int, dot: str | None) -> str:
    """Return ABC duration string for a given BWW denominator and optional dot marker."""
    if dot is None:
        return {1: "8", 2: "4", 4: "2", 8: "", 16: "/", 32: "//"}.get(denom, "")
    double_dot = len(dot) >= 2 and dot[1] == "'"
    if double_dot:
        return {1: "14", 2: "7", 4: "7/", 8: "7//", 16: "7///", 32: "7////",}.get(denom, "")
    else:
        return {1: "12", 2: "6", 4: "3", 8: "3/", 16: "3//", 32: "3///",}.get(denom, "")


def _parse_accidental_note(note_suffix: str) -> str:
    """Convert BWW note suffix (hg/ha/lg/la/a-g) to ABC pitch letter."""
    mapping = {"hg": "g", "ha": "a", "lg": "G", "la": "A"}
    return mapping.get(note_suffix, note_suffix)


def convert(bww_text: str, filename: str = "input.bww") -> str:
    """Convert the text of a BWW file to ABC notation."""
    lines = bww_text.splitlines()
    out: list[str] = []

    out.append(f"%abc-2.2\n% Converted from {filename} to ABC by bmw2abc_converter\n\nX:1")

    key_acc = ""
    i = 0

    # --- Header ---
    while i < len(lines):
        raw = lines[i]
        l = raw.strip()
        i += 1
        if not l:
            continue

        first = l[0]

        if first == '"':
            j = l.find('"', 1)
            if j <= 0:
                continue
            text = l[1:j]
            if not text:
                continue
            # character after closing quote + comma determines type
            if len(l) <= j + 2 or l[j + 1] != ",":
                out.append("% " + text)
                continue
            kind = l[j + 3] if len(l) > j + 3 else ""
            if kind == "T":
                out.append("T:" + text)
            elif kind == "M":
                out.append("C:" + text)
            elif kind == "Y":
                out.append("R:" + text)
            elif kind == "F":
                out.append("%%footer \t" + text)
            continue

        if first == "T":
            parts = l.split(",")
            if parts[0] == "TuneTempo":
                out.append("Q:1/4=" + parts[1])
            continue

        if first == "&":
            # parse accidentals and time signature from the clef line
            tokens = l.split()
            for tok in tokens:
                m = _ACC_RE.fullmatch(tok)
                if not m:
                    continue
                acc_type, acc_note = m.group(1), m.group(2)
                sep = " " if key_acc else ""
                prefix = {"sharp": "^", "flat": "_", "natural": "="}.get(acc_type, "")
                key_acc += sep + prefix + _parse_accidental_note(acc_note)

            # time signature is the last token on the & line
            last = tokens[-1]
            if not re.match(r"C$|C_$|\d+_\d+", last):
                # look on the next line
                if i < len(lines):
                    next_tokens = lines[i].strip().split()
                    i += 1
                    last = next_tokens[0] if next_tokens else ""
                if not re.match(r"C$|C_$|\d+_\d+", last):
                    out.append("M:2/4")
                    break

            if last == "C_":
                out.append("M:C|")
            else:
                out.append("M:" + last.replace("_", "/"))
            break  # clef line consumed; music starts from current i

        # ignore unrecognised header lines (MIDINoteMappings, etc.)

    out.append("L:1/8")
    out.append("K:Hp exp " + key_acc)

    # --- Music ---
    measure = ""
    tie = False
    pending_acc = ""
    beam = False
    fermata = False

    while i < len(lines):
        raw = lines[i]
        i += 1
        if not raw or raw[0] == "&":
            continue

        tokens = raw.strip().split()
        k = 0
        while k < len(tokens):
            t = tokens[k]
            k += 1

            if not t:
                continue

            # --- Structural / barline tokens ---

            if t == "''!I":
                out.append(measure + " :|")
                measure = ""
                continue

            if t == "_":
                measure += "]"
                continue

            if t == "!t":
                out.append(measure + " |")
                measure = ""
                continue

            if t == "!!t":
                out.append(measure + " ||")
                measure = ""
                continue

            if t == "!I":
                out.append(measure + " |]")
                measure = ""
                continue

            if t == "I!''":
                measure += "|: "
                continue

            if t == "I!":
                measure += "|| "
                continue

            if t[0] == "!":
                measure += "| "
                continue

            if t == "'intro":
                measure += '["Introduction"'
                continue

            if t[0] == "'" and len(t) > 1 and t[1].isdigit():
                # repeat volta bracket: '1, '2, '12, '123
                measure += "["
                bracket = t[1:]
                if len(bracket) == 1:
                    measure += bracket
                elif len(bracket) == 2:
                    measure += f'"{bracket[0]} of {bracket[1]}"'
                else:
                    measure += f'"{bracket[0]} of {bracket[1]} & {bracket[2]}"'
                continue

            # --- Rests ---

            if t.startswith("REST_"):
                denom_str = t[5:]
                denom = int(denom_str) if denom_str.isdigit() else 8
                measure += "z" + _abc_duration(denom, None)
                continue

            # --- Tuplets ---

            if t[0] == "^":
                ch = t[1] if len(t) > 1 else ""
                if ch == "t":
                    if len(t) > 2 and t[2] == "s":
                        tie = True
                    if len(t) > 2 and t[2] != "e":
                        measure += "-"
                elif ch in "23":
                    if len(t) <= 2 or t[2] != "e":
                        measure += "(" + ch
                elif ch in "4567":
                    if len(t) <= 2 or t[2] != "e":
                        measure += "(" + ch + ":" + (t[2] if len(t) > 2 else "")
                continue

            # --- Inline time sig / tempo ---

            if _TIMESIG_RE.fullmatch(t):
                measure += "[M:" + t.replace("_", "/") + "]"
                continue

            if t == "C":
                measure += "[M:C]"
                continue

            if t == "C_":
                measure += "[M:C|]"
                continue

            if t.startswith("TuneTempo,"):
                bpm = t.split(",", 1)[1]
                measure += "[Q:1/4=" + bpm + "]"
                continue

            # --- High / Low octave prefix ---

            low = False
            if t[0] == "H":
                low = False
                t = t[1:]
            elif t[0] == "L":
                low = True
                t = t[1:]

            # --- Note token ---

            m = _NOTE_RE.fullmatch(t)
            if m:
                letter, beam_dir, denom_str = m.group(1), m.group(2), m.group(3)
                denom = int(denom_str)

                if pending_acc:
                    measure += pending_acc
                    pending_acc = ""

                # fermata: next token contains "fermat"
                if k < len(tokens) and "fermat" in tokens[k]:
                    fermata = True
                    measure += "H"

                # B is always low (Low-B is the only B on the bagpipe)
                if letter == "B":
                    low = True

                measure += letter if low else letter.lower()

                # dotted note: consume next token if it is a dot marker
                dot_token = None
                if k < len(tokens) and _DOT_RE.fullmatch(tokens[k]):
                    dot_token = tokens[k]
                    k += 1

                measure += _abc_duration(denom, dot_token)

                if tie:
                    measure += "-"
                    tie = False

                # beaming: eighth notes and shorter use r/l to group
                if denom >= 8:
                    if beam_dir == "l":
                        beam = False
                    elif beam_dir == "r":
                        beam = True
                    if not beam:
                        measure += " "

                if fermata:
                    k += 1  # consume the fermat token
                    fermata = False

                continue

            # --- Grace notes and decorations ---

            if t in GRACE:
                measure += "{" + GRACE[t] + "}"
                continue

            if t in DECO:
                measure += DECO[t]
                continue

            # --- Inline accidental (before a note) ---

            acc_m = _ACC_RE.match(t)
            if acc_m:
                acc_type = acc_m.group(1)
                pending_acc = {"sharp": "^", "flat": "_", "natural": "="}.get(acc_type, "")
                continue

            print(f"*** {t!r} not recognised ***", file=sys.stderr)

    if measure.strip():
        out.append(measure)

    return "\n".join(out) + "\n"


def convert_file(path: str | Path) -> str:
    """Read a BWW file and return ABC notation as a string."""
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    return convert(text, filename=path.name)
