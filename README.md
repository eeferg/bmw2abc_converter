# bmw2abc_converter

Convert Bagpipe Music Writer (`.bww` / `.bmw`) files to ABC music notation — and back.

- `bmw2abc` — BWW → ABC
- `abc2bww` — ABC → BWW (Bagpipe Music Writer Gold), for importing ABC tunes into
  apps such as Braw Tunes that read BWW but not ABC

Python port of [bww2abc.js](http://moinejf.free.fr/bww2abc) by Jean-Francois Moine (GPL3+).

---

## Installation

Requires Python 3.12+. Uses [uv](https://docs.astral.sh/uv/) for dependency management.

### As an installable command (recommended)

Install once and run `bmw2abc` from anywhere:

```bash
git clone https://github.com/eeferg/bmw2abc_converter
cd bmw2abc_converter
uv tool install .
```

After that, `bmw2abc` is available system-wide:

```bash
bmw2abc tune.bww
bmw2abc tune.bww -o tune.abc
bmw2abc tune.bww --hp
```

To update after pulling new changes:

```bash
uv tool install . --reinstall
```

### Run without installing

```bash
git clone https://github.com/eeferg/bmw2abc_converter
cd bmw2abc_converter
uv sync
```

---

## Usage

```bash
# File to stdout
bmw2abc tune.bww

# File to file
bmw2abc tune.bww -o tune.abc

# From stdin
cat tune.bww | bmw2abc

# Use K:Hp key signature (shows F#/C# on staff) instead of default K:HP
bmw2abc tune.bww --hp

# Use L:1/16 unit note length (suits marches with 32nd-note detail)
bmw2abc tune.bww --unit 1/16

# bagpipemusic.com (Lee & Sons) files: put the title and tune type the right way round
bmw2abc tune.bww --swap-title-type
```

If running without installing, prefix commands with `uv run python main.py` instead of `bmw2abc`.

### Key signature options

| Flag | ABC output | Effect |
|------|-----------|--------|
| *(default)* | `K:HP` | No key signature marks on staff (traditional piping style) |
| `--hp` | `K:Hp` | F# and C# shown on staff |

Non-standard accidentals (e.g. a naturalised High-G) are always emitted as `exp` modifiers regardless of flag.

### Unit note length

| Flag | ABC output | Best for |
|------|-----------|---------|
| *(default)* | `L:1/8` | Reels, jigs, strathspeys — 8th note as unit |
| `--unit 1/16` | `L:1/16` | Marches and slow airs with 32nd-note detail |

At `L:1/16`, dotted rhythms are written with `>` and `<` shorthands (`A>B`, `A<B`) rather than explicit fraction multipliers, which produces cleaner, more readable notation.

---

## ABC → BWW (`abc2bww`)

Converts pipe-tune ABC (the style written for abcm2ps with `K:HP`) to BWW files
that open in Bagpipe Music Writer Gold.

```bash
abc2bww tune.abc                      # → ./tune.bww
abc2bww a.abc b.abc c.abc             # several at once, into the current folder
abc2bww pipe_march/*.abc -o ~/bww/    # choose the output folder
abc2bww tune.abc --stdout             # print instead of writing
abc2bww tune.abc --force              # overwrite an existing .bww
abc2bww --all tunes/ -o bww_out/      # every ABC file in tunes/pipe_* folders
```

- A file with several `X:` tunes gives `name001.bww`, `name002.bww`, … (one
  arrangement per file, as Braw Tunes requires), numbered like abcm2ps EPS files.
- `T:` → title, `R:` → tune type, `C:` → composer, `Q:` → tempo (default 90).
- Embellishments become named BWW tokens (`{Gdc}d` → `thrd`, `{gef}e` → `dbe`…).
- Chord symbols, slurs, `%%` directives and harmony voices (`V:2`…) are dropped,
  each with a warning. Every warning is printed under the file it came from.
- Output uses Windows line endings and the BMW Gold 1.0 header.

---

## ABC Output Format

```abc
%abc-2.2
% Converted from tune.bww to ABC by bmw2abc_converter

X:1
T:Tune Title
C:Composer
R:Tune Type
Q:1/4=80
M:4/4
L:1/8
K:HP
|: {g}A2{d}c2 ... :|
```

Grace notes appear in `{}` immediately before their principal note. Each barline token in the source flushes the current measure to a new output line.

---

## What Gets Converted

| BWW element | ABC output |
|------------|-----------|
| Title / Composer / Type / Footer | `T:` `C:` `R:` `%%footer` |
| Tempo (`TuneTempo,90`) | `Q:1/4=90` |
| Time signature | `M:3/4` etc. |
| Notes with H/L prefix (High-G, Low-A…) | `g` `A` etc. |
| Dotted notes (`'la`, `''f`) | `>` / `<` shorthands or duration multipliers (`A3/`, `f7//`) |
| Grace note embellishments | `{gAd}` etc. — full table in `docs/bww_format.md` |
| Repeat barlines | `|:` `:|` |
| First/second endings (`'1`, `'2`, `_'`) | `[1` `[2` `["1 of 2"` `]` |
| Ties (`^ts` / `^te`) | `-` after first note |
| Rests (`REST_4`) | `z2` |
| Tuplets (`^3s`) | `(3` |
| Section labels (`"2nd Part"`) | `% 2nd Part` |
| `space` tokens | silently ignored |

---

## Reference Docs

| File | Contents |
|------|---------|
| [`docs/bww_format.md`](docs/bww_format.md) | Complete BWW token reference — notes, grace notes, barlines, time sigs, dots, tuplets |
| [`docs/abc_bagpipe.md`](docs/abc_bagpipe.md) | ABC notation for bagpipes — pitches, durations, grace syntax, key sigs |
| [`docs/bagpipe_notation_for_ai.md`](docs/bagpipe_notation_for_ai.md) | Bagpipe sheet music concepts for AI image recognition / LLM skills |
| [`docs/bww2abc_original.js`](docs/bww2abc_original.js) | Original JS source (GPL3+) |
| [`docs/musescore_bww_lexer.cpp`](docs/musescore_bww_lexer.cpp) | MuseScore C++ BWW lexer (secondary reference) |

---

## Running Tests

```bash
uv run pytest tests/ -v
```

---

## Known Limitations / Future Work

- Repeats with more than two endings may not render perfectly in all ABC players
- Piobaireacd ornaments (not present in standard march/strathspey/reel repertoire) are not mapped
- Multi-staff scores (e.g. harmonised pipe band scores) are not supported
- bagpipemusic.com (Lee & Sons) BWW files store the tune type in the title field
  and vice versa; use `bmw2abc --swap-title-type` for those files

---

## License

Code: MIT.
`docs/bww2abc_original.js` and derived grace-note tables: GPL3+ (Jean-Francois Moine).
