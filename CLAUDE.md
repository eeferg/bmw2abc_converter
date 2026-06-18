# CLAUDE.md — bmw2abc_converter

Context for AI assistants working in this repository.

---

## Project Purpose

Convert Bagpipe Music Writer (`.bww` / `.bmw`) plain-text files to ABC music notation.
Python port of `bww2abc.js` by Jean-Francois Moine (GPL3+).

---

## Repository Layout

```
bmw2abc_converter/      Python package
  __init__.py           exposes convert()
  converter.py          main conversion logic
  grace_notes.py        GRACE and DECO lookup tables (~200 embellishments)
docs/
  bww_format.md         Complete BWW token reference (START HERE for format questions)
  abc_bagpipe.md        ABC notation for bagpipes
  bagpipe_notation_for_ai.md  Image-to-ABC concepts for LLM/vision skills
  bww2abc_original.js   Original JS source (reference)
  musescore_bww_lexer.cpp  MuseScore C++ lexer (reference)
tests/
  test_converter.py     17 pytest tests
main.py                 CLI entry point
pyproject.toml          uv/hatchling build config
```

---

## Running the Converter

```bash
uv run python main.py tune.bww              # stdout
uv run python main.py tune.bww -o tune.abc  # file output
uv run python main.py tune.bww --hp         # K:Hp instead of K:HP
uv run pytest tests/ -v                     # run tests
```

---

## Architecture — How Conversion Works

Single-pass line/token scanner in `converter.py`:

1. **Header phase** — processes lines until the first `&` clef line:
   - `"Title",(T,...)` → `T:` metadata
   - `TuneTempo,90` → `Q:1/4=90`
   - `& sharpf sharpc 3_4` → key accidentals + time sig; any trailing tokens (e.g. `I!''`) are carried as `pending_music_tokens`

2. **Music phase** — processes remaining lines token by token:
   - `&` lines: strip clef/accidental/timesig tokens, process remaining as music
   - `"2nd Part"` lines: emit as `% 2nd Part` comment
   - `space` tokens: silently ignored
   - Notes (`LA_8`, `HGl_16`): H/L prefix → octave; `[rl]` → beaming; `_N` → duration
   - Grace notes (`dblg`, `grp`, `brl`…): looked up in `GRACE` dict → `{seq}`
   - Decorations (`pgrp`, `fine`…): looked up in `DECO` dict → ABC decoration
   - Ties (`^ts`/`^te`): new format — `^ts` sets flag, `-` emitted AFTER the note (not before grace notes)
   - Barline tokens (`!t`, `''!I`…): flush current measure to output

---

## Key Design Decisions

### Key signature
- Default: `K:HP` (no marks on staff — piping tradition)
- `--hp` flag: `K:Hp` (F# and C# shown)
- Standard accidentals (`^f`, `^c`) are **never** emitted as `exp` modifiers — they are implied by both key types
- Non-standard accidentals (e.g. `=g` for natural High-G) are emitted as `exp` modifiers automatically

### Dot markers
- BWW dot tokens: `'f`, `'la`, `''e` etc. (one or two apostrophes + note name)
- Detection uses `re.match()` not `re.fullmatch()` — mirrors JS `.test()` partial match, allowing two-char note names like `'la` and `'ha`

### Ties vs grace notes
- `^ts` (tie start) sets `tie=True`; the `-` is emitted **after** the note, so grace notes on the following note appear correctly: `{G}A2-A` not `{G}-A2-A`
- Original JS had a bug here (ran both old-format and new-format paths); the fix uses mutually exclusive branches

### `&` clef lines in music section
- Multiple `&` lines appear throughout a BWW file (one per staff line visually)
- The time signature is found by scanning all tokens, not just the last one
- Music tokens embedded in `&` lines (e.g. `I!''` repeat starts) are extracted and processed

---

## Bagpipe Scale → ABC Mapping

| Bagpipe pitch | ABC letter | Notes |
|--------------|-----------|-------|
| Low-G | `G` (upper) | BWW: `LG_N` |
| Low-A | `A` (upper) | BWW: `LA_N` |
| B | `B` (upper) | BWW: `B_N` — always uppercase |
| C | `c` (lower) | BWW: `C_N` |
| D | `d` (lower) | BWW: `D_N` |
| E | `e` (lower) | BWW: `E_N` |
| F | `f` (lower) | BWW: `F_N` |
| High-G | `g` (lower) | BWW: `HG_N` |
| High-A | `a` (lower) | BWW: `HA_N` |

Bare note letters without H/L prefix default to lowercase (high register) except B.

---

## Common Bugs to Watch For

1. **`space` tokens** — appear in many BWW files as visual spacers; must be silently ignored
2. **Two-char dot suffixes** (`'la`, `'ha`) — use `re.match` not `re.fullmatch`
3. **Section labels** (`"2nd Part"`) — standalone quoted lines between parts; detect at line level before splitting tokens
4. **Tie + grace note ordering** — tie flag must output `-` after the note, not immediately when `^ts` is seen
5. **Time sig not last on `&` line** — scan all tokens for time sig; trailing tokens may be music (e.g. `I!''`)

---

## Adding New Embellishments

If a BWW token is reported as `*** 'xyz' not recognised ***`:
1. Check if it should be in `GRACE` (grace note sequence) or `DECO` (ABC decoration mark)
2. Look up the embellishment name in `docs/bww_format.md` or the Bagpipe Music Writer manual
3. Add to `bmw2abc_converter/grace_notes.py` — the ABC grace sequence uses the same pitch letters as the note mapping table above

---

## Future Skill: Image → ABC

See `docs/bagpipe_notation_for_ai.md` for a comprehensive reference on recognising
bagpipe sheet music visually and converting it to ABC notation. This document is
designed to be included as context when prompting a vision-capable LLM.
