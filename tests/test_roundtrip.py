"""Round-trip tests over real tunes.

- Fixtures (always run): Ed's ABC → abc2bww → bmw2abc → same notes.
- LEE_BWW_DIR: Lee BWW → bmw2abc → abc2bww → bmw2abc → same notes.
- LEE_BWW_DIR + NA_MARAGAN_DIR: Ed's ABC marked "B:Lee & Sons" → abc2bww must match
  Lee's original BWW note for note (pitch, duration, gracenotes).
- NA_MARAGAN_DIR: whole-collection sweep, no exceptions.
"""

from __future__ import annotations

import os
import difflib
import re
import unicodedata
from fractions import Fraction
from pathlib import Path

import pytest

from bmw2abc_converter import convert as bmw2abc
from bmw2abc_converter.abc2bww import convert_abc
from bmw2abc_converter.abc_model import Note
from bmw2abc_converter.abc_parse import parse_abc
from bmw2abc_converter.grace_notes import GRACE
from bmw2abc_converter.grace_reverse import embellishment_tokens

FIXTURES = sorted((Path(__file__).parent / "fixtures" / "abc").glob("*.abc"))
LEE_DIR = Path(os.environ["LEE_BWW_DIR"]) if os.environ.get("LEE_BWW_DIR") else None
NA_DIR = Path(os.environ["NA_MARAGAN_DIR"]).expanduser() if os.environ.get("NA_MARAGAN_DIR") else None

# Files whose differences are real (not converter bugs), with the reason.
# Each was inspected (2026-11-26): the converter reproduces Ed's ABC faithfully and
# the ABC differs from Lee's BWW. Listed for Ed to review — either side may be wrong.
KNOWN_DIFFS: dict[str, str] = {
    "angus_j_maclellan.abc": "3rd part: Ed e3/16+d1/32 where Lee has e3/16+d1/16",
    "clan_maccoll_2_4.abc": "4th part: Ed {gef}e dotted-8th + A 16th, Lee dotted-16th + 32nd",
    "donald_maciver_2_4.abc": "2nd ending: Ed a 32nd after dotted c (Lee 16th, doesn't add up); last A 8th vs Lee quarter",
    "donald_macleans_farewell_to_oban_2_4.abc": "2nd ending: last {GAG}A 8th vs Lee quarter",
    "flowers_of_the_forest.abc": "Lee has a duplicated dot token ('d 'd) on a D; Ed single dot",
    "glendaurel_highlanders_6_8.abc": "2nd ending: Ed {GAG}A/ (16th) vs Lee dotted 8th",
    "haughs_of_cromdale_2_4.abc": "2nd part: Ed {g}g (g-gracenote on high G) vs Lee {f}g",
    "meg_macrae_6_8.abc": "2nd ending: Ed {GdGe}B/ (16th) vs Lee dotted 8th",
    "newmarket_house.abc": "2nd part: Ed doubling {gef}e vs Lee single {g}e",
    "shepherds_crook.abc": "Ed starts with an extra C pickup; Lee's 'C' there is the common-time sign",
    "thornton_jig_pipes.abc": "Ed's setting adds 1st/2nd endings where Lee has a plain repeat",
}


def _lee_files() -> list[Path]:
    if not LEE_DIR or not LEE_DIR.is_dir():
        return []
    return sorted(p for p in LEE_DIR.rglob("*") if p.suffix.lower() in (".bww", ".bmw"))


def _collection_files(pattern: str = "pipe_*/*.abc") -> list[Path]:
    if not NA_DIR or not (NA_DIR / "tunes").is_dir():
        return []
    return sorted((NA_DIR / "tunes").glob(pattern))


def _read(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


# -- signatures ------------------------------------------------------------

def _grace_seq(grace: str, pitch: str) -> str:
    """Canonical gracenote string: what the chosen BWW tokens render as."""
    tokens, _ = embellishment_tokens(grace, pitch)
    return "".join(GRACE.get(t, "") for t in tokens)


def note_signature(abc_text: str) -> list[list[tuple[str, Fraction, str]]]:
    """Per tune: (pitch, length, canonical grace) for each note."""
    sigs = []
    for tune in parse_abc(abc_text):
        sig = []
        for line in tune.lines:
            for item in line.items:
                if isinstance(item, Note):
                    sig.append((item.pitch, item.length, _grace_seq(item.grace, item.pitch)))
        sigs.append(sig)
    return sigs


_BWW_NOTE = re.compile(r"(LG|LA|B|C|D|E|F|HG|HA)[rl]?_(\d+)$")
_BWW_DOT = re.compile(r"('{1,2})(lg|la|b|c|d|e|f|hg|ha)$")


def bww_signature(text: str) -> list[tuple[str, str, str]]:
    """(gracenotes, pitch, duration) for every melody note in BWW text."""
    sig: list[tuple[str, str, str]] = []
    graces = ""
    started = False
    for line in text.splitlines():
        if line.startswith("&"):
            started = True
        if not started or line.lstrip().startswith('"'):
            continue
        for tok in line.split():
            if tok in GRACE:
                graces += GRACE[tok]
            elif m := _BWW_NOTE.match(tok):
                sig.append((graces, m.group(1), m.group(2)))
                graces = ""
            elif (m := _BWW_DOT.match(tok)) and sig:
                g, p, d = sig[-1]
                sig[-1] = (g, p, d + m.group(1))
    return sig


def _first_diff(a: list, b: list) -> str:
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return f"index {i}:\n  ours: {a[max(0, i - 2):i + 3]}\n  ref:  {b[max(0, i - 2):i + 3]}"
    return f"lengths differ: ours {len(a)} vs ref {len(b)}"


def _unit(abc_text: str) -> int:
    return 16 if re.search(r"^L:\s*1/16", abc_text, re.M) else 8


def _roundtrip_abc(abc_text: str) -> list[str]:
    unit = _unit(abc_text)
    return [bmw2abc(bww, filename="rt.bww", unit=unit) for bww, _ in convert_abc(abc_text)]


# -- fixtures ---------------------------------------------------------------

@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.stem)
def test_fixture_roundtrip(path):
    src = _read(path)
    expected = note_signature(src)
    back = [note_signature(abc)[0] for abc in _roundtrip_abc(src)]
    assert len(back) == len(expected)
    for n, (exp, got) in enumerate(zip(expected, back), 1):
        assert got == exp, f"tune {n}: {_first_diff(got, exp)}"


# -- Lee corpus --------------------------------------------------------------

@pytest.mark.parametrize("path", _lee_files(), ids=lambda p: p.stem)
def test_lee_roundtrip(path):
    if path.name in KNOWN_DIFFS:
        pytest.skip(KNOWN_DIFFS[path.name])
    abc1 = bmw2abc(_read(path), filename=path.name)
    sig1 = note_signature(abc1)
    back = [note_signature(abc)[0] for abc in _roundtrip_abc(abc1)]
    assert len(back) == len(sig1)
    for exp, got in zip(sig1, back):
        assert got == exp, _first_diff(got, exp)


def _norm_title(title: str) -> str:
    t = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode().lower().strip()
    t = re.sub(r"\s+-\s+.*$", "", t)  # "High Road to Linton - Needs Edited More"
    t = re.sub(r"[()]", "", t)
    t = re.sub(r"^the\s+", "", t)
    return re.sub(r"[^a-z0-9]", "", t)


def _lee_by_title() -> dict[str, list[tuple[Path, str]]]:
    """normalised title -> [(path, tune type)]. Lee files keep the title in Y, type in T."""
    index: dict[str, list[tuple[Path, str]]] = {}
    for p in _lee_files():
        text = _read(p)
        title = re.search(r'^"(.*)",\(Y,', text, re.M)
        ttype = re.search(r'^"(.*)",\(T,', text, re.M)
        if title:
            index.setdefault(_norm_title(title.group(1)), []).append(
                (p, ttype.group(1).lower() if ttype else ""))
    return index


def _same_type(ours: str | None, lee: str) -> bool:
    ours = (ours or "").lower()
    kinds = ("march", "strathspey", "reel", "jig", "air", "hornpipe", "retreat", "polka")
    if not ours or not lee or not any(k in ours for k in kinds):
        return True
    return any(k in ours and k in lee for k in kinds)


def _lee_marked() -> list[Path]:
    return [p for p in _collection_files()
            if re.search(r"^B:\s*Lee & Sons", _read(p), re.M)]


_LEE_INDEX: dict[str, list[tuple[Path, str]]] | None = None


@pytest.mark.parametrize("path", _lee_marked(), ids=lambda p: p.stem)
def test_lee_marked_matches_original(path):
    global _LEE_INDEX
    if _LEE_INDEX is None:
        _LEE_INDEX = _lee_by_title()
    if path.name in KNOWN_DIFFS:
        pytest.skip(KNOWN_DIFFS[path.name])
    src = _read(path)
    tunes = parse_abc(src)
    results = convert_abc(src)
    # the Lee setting is the X: tune whose B: says Lee & Sons; usually the first
    idx = 0
    for i, block in enumerate(re.split(r"^X:", src, flags=re.M)[1:]):
        if re.search(r"^B:\s*Lee & Sons", block, re.M):
            idx = i
            break
    key = _norm_title(tunes[idx].title)
    if key not in _LEE_INDEX:  # e.g. McGregor vs MacGregor
        close = difflib.get_close_matches(key, list(_LEE_INDEX), n=1, cutoff=0.9)
        key = close[0] if close else key
    candidates = [p for p, ttype in _LEE_INDEX.get(key, [])
                  if _same_type(tunes[idx].tune_type, ttype)]
    if not candidates:
        pytest.skip(f"no Lee {tunes[idx].tune_type or ''} file titled {tunes[idx].title!r}")
    lee = candidates[0]
    ours = bww_signature(results[idx][0])
    ref = bww_signature(_read(lee))
    assert ours == ref, f"{lee.name}: {_first_diff(ours, ref)}"


# -- sweep ------------------------------------------------------------------

@pytest.mark.skipif(not _collection_files(), reason="NA_MARAGAN_DIR not set")
def test_collection_sweep(capsys):
    from collections import Counter
    tally: Counter = Counter()
    for path in _collection_files():
        for _, warnings in convert_abc(_read(path)):
            for w in warnings:
                tally[re.sub(r"staff \d+: |line \d+: |\(line \d+\)", "", w)[:60]] += 1
    with capsys.disabled():
        print("\nwarning tally:")
        for w, n in tally.most_common(25):
            print(f"  {n:4d}  {w}")
