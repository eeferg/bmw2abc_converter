# bww-abc

Convert bagpipe music between **Bagpipe Music Writer** (`.bww`) and **ABC**
notation, in both directions.

- **`bww2abc`** — BWW → ABC, for typesetting with
  [abcm2ps](https://github.com/lewdlime/abcm2ps) or editing as text. It also
  reads legacy pre-Gold `.bmw` files.
- **`abc2bww`** — ABC → BWW (Bagpipe Music Writer Gold), for opening ABC tunes
  in BMW Gold or importing them into apps that read BWW but not ABC (such as
  Braw Tunes).

Embellishments stay named on both sides: `{gef}e` ↔ `dbe`, `{Gdc}d` ↔ `thrd`,
`{GdGe}A` ↔ `tar`. `bww2abc` is based on
[bww2abc.js](http://moinejf.free.fr/bww2abc) by Jean-Francois Moine.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/eeferg/bww-abc
cd bww-abc
uv tool install .            # puts bww2abc and abc2bww on your PATH
uv tool install . --reinstall   # after pulling updates
```

To run from the source folder without installing, use `uv run bww2abc …`.

## bww2abc (BWW → ABC)

```bash
bww2abc tune.bww                  # ABC to the screen
bww2abc tune.bww -o tune.abc      # ABC to a file
cat tune.bww | bww2abc            # read from a pipe
bww2abc tune.bww --hp             # K:Hp (F# and C# drawn) instead of K:HP
bww2abc tune.bww --unit 1/16      # L:1/16, for marches with 32nd-note detail
bww2abc tune.bww --swap-title-type   # bagpipemusic.com files: title and type swapped
```

| BWW | ABC |
|---|---|
| title / type / composer / footer | `T:` `R:` `C:` `%%footer` |
| `TuneTempo,90` | `Q:1/4=90` |
| notes, dots, beaming | `A2`, `A>B`, `A3/` … |
| named embellishments | `{gef}` etc. |
| repeats, 1st/2nd endings | `\|:` `:\|` `[1` `[2` `]` |
| ties, triplets, rests | `-`, `(3`, `z` |
| `"2nd Part"` labels | `% 2nd Part` |

Accented text (Gaelic titles, for example) is preserved. Unknown tokens are
reported as `*** 'xyz' not recognised ***` on stderr.

## abc2bww (ABC → BWW)

Written for pipe-tune ABC as typeset with abcm2ps (`K:HP` or `K:Hp`), not the
full ABC standard.

```bash
abc2bww tune.abc                      # → ./tune.bww
abc2bww a.abc b.abc -o ~/bww/         # several files, into a chosen folder
abc2bww tune.abc --stdout             # print instead of writing
abc2bww tune.abc --force              # overwrite an existing .bww
abc2bww --all tunes/ -o bww_out/      # every .abc under tunes/pipe_* folders
```

- A file holding several `X:` tunes gives `name001.bww`, `name002.bww` and so
  on, one tune per file, numbered the way abcm2ps numbers EPS files.
- `T:` → title, `R:` → tune type, `C:` → composer, `B:` → footer, `Q:` → tempo
  (default 90).
- Chord symbols, slurs and harmony voices (`V:2` and later) are dropped. Each
  drop prints a warning under the file it came from, as do gracenote groups
  that can't be played (`{ed}d`).
- Output matches BMW Gold's own files: the Gold 1.0 header, Windows line
  endings and the Windows-1252 character set.

## Documentation

| File | Contents |
|---|---|
| [docs/bww_format.md](docs/bww_format.md) | BWW Gold token reference: notes, dots, gracenotes, barlines, repeats, tuplets |
| [docs/bmw_legacy_format.md](docs/bmw_legacy_format.md) | The older pre-Gold BMW format and how it differs |
| [docs/abc_bagpipe.md](docs/abc_bagpipe.md) | ABC notation for bagpipes |
| [docs/conversion_notes.md](docs/conversion_notes.md) | How the two converters map one format onto the other, and their known limits |
| [docs/bagpipe_notation_for_ai.md](docs/bagpipe_notation_for_ai.md) | Reading bagpipe sheet music, for image-to-ABC work with AI models |
| [docs/reference/](docs/reference/) | Moine's original `bww2abc.js` and MuseScore's BWW lexer |

## Tests

```bash
uv run pytest
```

Tests that need private tune collections (`LEE_BWW_DIR`, `NA_MARAGAN_DIR`) are
skipped when those aren't set.

## License

GPL-3.0-or-later; see [LICENSE](LICENSE). `bww2abc` is a port of Jean-Francois
Moine's `bww2abc.js` (GPL3+), and the gracenote tables derive from it.

Copyright © Jean-Francois Moine (bww2abc.js) and eeferg (this port and abc2bww).
