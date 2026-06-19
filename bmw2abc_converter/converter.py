"""
BWW -> ABC converter.
Ported from bww2abc.js by Jean-Francois Moine (GPL3+).
See docs/bww_format.md for format details.
"""

import re
import sys
from pathlib import Path

from .grace_notes import DECO, GRACE

_NOTE_RE = re.compile(r"([ABCDEFG])([rl]?)_(\d+)")
_ACC_RE = re.compile(r"(sharp|flat|natural)(.*)")
_TIMESIG_RE = re.compile(r"\d+_\d+")
# Dot marker: one or two apostrophes then a letter (a-h or l).
# Use match() not fullmatch() — the original JS uses .test() which is a partial
# match, allowing 'la' and 'ha' (two-char note names) to be detected via 'l/'h'.
_DOT_RE = re.compile(r"'{1,2}[abcdefghl]")
# Dotted-rhythm shorthands (fraction pairs, always applied):
#   A3/{grace}c/ → A>{grace}c   (dotted-16th + 32nd at L:1/8, dotted-32nd + 64th at L:1/16)
#   A/{grace}c3/ → A<{grace}c
_DOTTED_GT_RE = re.compile(r"([A-Ga-g])3\/ ?((?:\{[^}]*\})?)([A-Ga-g])\/(?!\/)")
_DOTTED_LT_RE = re.compile(r"([A-Ga-g])\/(?!\/) ?((?:\{[^}]*\})?)([A-Ga-g])3\/")
# Integer dotted pairs (only applied at L:1/16):
#   A3{grace}c → A2>{grace}c2  (dotted-8th + 16th)
#   A{grace}c3 → A2<{grace}c2  (16th + dotted-8th)
_DOTTED_GT2_RE = re.compile(r"([A-Ga-g])3 ?((?:\{[^}]*\})?)([A-Ga-g])(?![/\d])")
_DOTTED_LT2_RE = re.compile(r"([A-Ga-g])((?:\{[^}]*\})?)([A-Ga-g])3(?![/\d])")

# BWW visual-spacing tokens with no musical meaning.
_SKIP_TOKENS = frozenset({"space"})

# Accidentals already implied by K:Hp / K:HP — no need to emit them explicitly.
_STANDARD_ACC = frozenset({"^f", "^c"})


def _parse_accidental_note(note_suffix: str) -> str:
    return {"hg": "g", "ha": "a", "lg": "G", "la": "A"}.get(note_suffix, note_suffix)


_DUR_PLAIN = {
    8:  {1: "8",  2: "4",  4: "2",  8: "",   16: "/",   32: "//"},
    16: {1: "16", 2: "8",  4: "4",  8: "2",  16: "",    32: "/"},
}
_DUR_DOT = {
    8:  {1: "12", 2: "6",  4: "3",  8: "3/", 16: "3//", 32: "3///"},
    16: {1: "24", 2: "12", 4: "6",  8: "3",  16: "3/",  32: "3//"},
}
_DUR_DDOT = {
    8:  {1: "14", 2: "7",  4: "7/", 8: "7//",  16: "7///",  32: "7////"},
    16: {1: "28", 2: "14", 4: "7",  8: "7/",   16: "7//",   32: "7///"},
}


def _abc_duration(denom: int, dot: str | None, unit: int = 8) -> str:
    """Return ABC duration modifier for a BWW denominator and optional dot token."""
    if dot is None:
        return _DUR_PLAIN[unit].get(denom, "")
    double_dot = len(dot) >= 2 and dot[1] == "'"
    return (_DUR_DDOT if double_dot else _DUR_DOT)[unit].get(denom, "")


def _parse_clef_line(line: str) -> tuple[str | None, list[str]]:
    """Parse a '&' clef line.

    Returns (time_sig or None, list of music tokens).
    Accidentals are not returned here; the header parser extracts them separately.
    """
    time_sig = None
    music_tokens = []
    for tok in line.strip().split():
        if tok == "&":
            continue
        if _ACC_RE.fullmatch(tok):
            continue
        if re.fullmatch(r"C|C_|\d+_\d+", tok) and time_sig is None:
            time_sig = tok
            continue
        music_tokens.append(tok)
    return time_sig, music_tokens


def convert(bww_text: str, filename: str = "input.bww", key_type: str = "HP", unit: int = 8) -> str:
    """Convert the text of a BWW file to ABC notation.

    key_type: "HP" (default, no key sig on staff) or "Hp" (shows F#/C# on staff).
    unit: unit note length denominator — 8 for L:1/8 (default), 16 for L:1/16.
    """
    lines = bww_text.splitlines()
    out: list[str] = []
    out.append(f"%abc-2.2\n% Converted from {filename} to ABC by bmw2abc_converter\n\nX:1")

    key_acc = ""
    i = 0
    pending_music_tokens: list[str] = []

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
            # Single pass: collect accidentals, time sig, and any trailing music tokens.
            time_sig = None
            for tok in l.split():
                if tok == "&":
                    continue
                acc_m = _ACC_RE.fullmatch(tok)
                if acc_m:
                    acc_type, acc_note = acc_m.group(1), acc_m.group(2)
                    sep = " " if key_acc else ""
                    prefix = {"sharp": "^", "flat": "_", "natural": "="}.get(acc_type, "")
                    key_acc += sep + prefix + _parse_accidental_note(acc_note)
                    continue
                if re.fullmatch(r"C|C_|\d+_\d+", tok) and time_sig is None:
                    time_sig = tok
                    continue
                pending_music_tokens.append(tok)

            if time_sig is None:
                # look on the next line for the time signature
                if i < len(lines):
                    next_ts, next_music = _parse_clef_line(lines[i].strip())
                    if next_ts:
                        i += 1
                        time_sig = next_ts
                        pending_music_tokens = pending_music_tokens + next_music

            if time_sig == "C_":
                out.append("M:C|")
            elif time_sig:
                out.append("M:" + time_sig.replace("_", "/"))
            else:
                out.append("M:2/4")
            break

    out.append(f"L:1/{unit}")
    extra_acc = [a for a in key_acc.split() if a not in _STANDARD_ACC]
    key_line = f"K:{key_type}"
    if extra_acc:
        key_line += " exp " + " ".join(extra_acc)
    out.append(key_line)

    # --- Music ---
    measure = ""
    tie = False
    pending_acc = ""
    beam = False
    fermata = False

    def process_tokens(tokens: list[str]) -> None:
        nonlocal measure, tie, pending_acc, beam, fermata

        k = 0
        while k < len(tokens):
            t = tokens[k]
            k += 1

            if not t or t in _SKIP_TOKENS:
                continue

            # --- Structural / barline tokens ---

            if t == "''!I":
                out.append(measure + " :|")
                measure = ""
                continue

            if t in ("_", "_'"):
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
                measure += "z" + _abc_duration(denom, None, unit)
                continue

            # --- Tuplets ---

            if t[0] == "^":
                ch = t[1] if len(t) > 1 else ""
                if ch == "t":
                    if len(t) > 2 and t[2] == "s":
                        # New format: tie starts here; output '-' after the next note.
                        tie = True
                    elif len(t) > 2 and t[2] == "e":
                        pass  # new format end: nothing to do
                    else:
                        # Old format bare ^t: output '-' immediately.
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

                if k < len(tokens) and "fermat" in tokens[k]:
                    fermata = True
                    measure += "H"

                if letter == "B":
                    low = True

                measure += letter if low else letter.lower()

                # dotted note: _DOT_RE.match (partial) mirrors JS .test() behaviour,
                # allowing two-char note names like 'la and 'ha to be detected.
                dot_token = None
                if k < len(tokens) and _DOT_RE.match(tokens[k]):
                    dot_token = tokens[k]
                    k += 1

                measure += _abc_duration(denom, dot_token, unit)

                if tie:
                    measure += "-"
                    tie = False

                if denom >= 8:
                    if beam_dir == "l":
                        beam = False
                    elif beam_dir == "r":
                        beam = True
                    if not beam:
                        measure += " "

                if fermata:
                    k += 1
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

    # Process any music tokens found on the initial & line (e.g. I!'')
    if pending_music_tokens:
        process_tokens(pending_music_tokens)

    # Process music lines
    while i < len(lines):
        raw = lines[i]
        i += 1
        stripped = raw.strip()

        if not stripped:
            continue

        # Section label lines: "2nd Part", "3rd Part", etc.
        if stripped.startswith('"'):
            end = stripped.rfind('"')
            label = stripped[1:end].strip() if end > 0 else stripped[1:]
            if label:
                out.append("% " + label)
            continue

        # Subsequent & lines: strip the clef/accidental/timesig tokens,
        # then process any remaining music tokens (e.g. I!'').
        if stripped.startswith("&"):
            _, music_toks = _parse_clef_line(stripped)
            if music_toks:
                process_tokens(music_toks)
            continue

        process_tokens(stripped.split())

    if measure.strip():
        out.append(measure)

    result = "\n".join(out) + "\n"
    result = _DOTTED_GT_RE.sub(r"\1>\2\3", result)
    result = _DOTTED_LT_RE.sub(r"\1<\2\3", result)
    if unit == 16:
        result = _DOTTED_GT2_RE.sub(r"\g<1>2>\g<2>\g<3>2", result)
        result = _DOTTED_LT2_RE.sub(r"\g<1>2<\g<2>\g<3>2", result)
    return result


def convert_file(path: str | Path, key_type: str = "HP", unit: int = 8) -> str:
    """Read a BWW file and return ABC notation as a string."""
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    return convert(text, filename=path.name, key_type=key_type, unit=unit)
