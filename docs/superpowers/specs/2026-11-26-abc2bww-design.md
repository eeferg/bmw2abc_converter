# ABC → BWW converter — design

Date: 2026-11-26
Status: approved by Ed, 2026-11-26

## Intent

Ed's pipe tune collection (`~/projects/eeferg/na_maragan_collection/tunes/pipe_*`,
203 `.abc` files) is authored in ABC and typeset with abcm2ps + LaTeX. That stays.
But the apps he wants to use — specifically **Braw Tunes** (iOS/Android practice
app: listens to you play, recognises the tune, shows the music) — import only
Bagpipe Music Writer (`.bww`/`.bmw`) or MusicXML. Ed owns Bagpipe Music Writer
Gold, and BWW is the dominant bagpipe notation format, so BWW is the target: it
keeps embellishments as named tokens rather than anonymous grace notes, and Ed can
open and fix output directly in BMW.

The ABC being converted is either hand-transcribed by Ed or was itself produced
from BWW by this repo's existing `bmw2abc` converter.

## Goals

- Convert every tune in `tunes/pipe_*` to a `.bww` file that opens cleanly in
  Bagpipe Music Writer Gold and imports into Braw Tunes.
- Correct pitches, durations, embellishments, ties, triplets, barlines, repeats
  and 1st/2nd endings. These are what Braw Tunes uses.
- Embellishments come out as **named BWW tokens** (`dblg`, `strla`, `grp`, `tar`,
  …), never as strings of single grace notes, whenever a named token exists.
- Anything not understood is reported loudly (`*** '<token>' not recognised ***`
  style, as in the existing converter) — never silently dropped or guessed.
- Titles, composer and tune type carried into the BWW header.

## Non-goals

- Piobaireachd (`tunes/piobaireachd`) and non-pipe tunes (folders not named
  `pipe_*`). Ed handles piobaireachd separately.
- The full ABC standard. Only the subset Ed actually writes (surveyed below).
- Chord symbols (`"Bm"` etc.) — dropped; BWW has no equivalent.
- Harmony voices — only the first voice is converted (see Decisions).
- MusicXML output.
- Reproducing abcm2ps layout (`%%` directives, spacing, page breaks). ABC source
  lines become BWW staff lines; that's the extent of layout fidelity.

## Anti-goals

- **Silently wrong music.** A tune that imports but has a wrong note, a lost
  repeat, or a doubling turned into a strike is worse than a loud failure. Every
  lossy step warns.
- Producing BWW that only this tool's own reverse converter can read. Output must
  look like what BMW Gold itself writes.

## Constraints

- Python, same package and tooling as the existing converter (uv, hatchling,
  pytest). Lives in this repo alongside `bmw2abc`.
- Braw Tunes: "A Bagpipe Music Writer file must contain a single arrangement."
  → one tune per output file.
- Output header must match BMW Gold's (`Bagpipe Music Writer Gold:1.0`, the
  `MIDINoteMappings` / `FrequencyMappings` / `InstrumentMappings` /
  `GracenoteDurations` / `FontSizes` / `TuneFormat` block copied verbatim from a
  real BMW Gold file such as `bmw-to-convert/Barren Rocks of Aden.bww`).

## The ABC subset (survey of all 203 pipe_* files)

- `K:HP` (250) or `K:Hp` (3). No other keys, no inline accidentals.
- `L:1/8` (≈216) or `L:1/16` (32). One odd `L:1/8 8 40` — treat trailing junk as
  a warning.
- `M:` 6/8, 2/4, C, 4/4, C|, 3/4, 9/8, 5/4, 6/4, 3/2. One inline `[M:C|]`.
- Header fields used: X T R C B W N V P S Q O Z H F. Only X T R C Q V matter
  for conversion; the rest are ignored (W:, lyrics-after-tune, is ignored).
- `%%` directives (mostly `%%flatbeams`) — ignored.
- 64 distinct grace groups; the top ten (`{g} {d} {gef} {e} {Gdc} {gcd} {G}
  {ag} {GdG} {gBd}`) cover the vast majority. Full list in the appendix.
- Broken rhythm `>` (5537) and `<` (1797) — pervasive.
- Triplets `(3` (106). No other tuplets.
- Ties `-` (186).
- Barlines/repeats: `|`, `||`, `|]`, `[|`, `|:`, `:|`, `::`; endings `[1 [2 |1 |2`.
- Rests `z` (18). One stray staccato dot.
- Decoration `!head-slashr!` (18 uses, 2 files: `duncan_macrae_of_kintails_lament`,
  `march_of_the_king_of_laoise_alt`) — always on rests (`!head-slashr!z`), drawn
  as slash beat marks in empty closing bars. Converted as plain rests, with a
  warning.
- Chord symbols (18) and one `"2 of 2"` annotation.
- `% 2nd Part`-style comments between parts.
- Multiple `X:` tunes in one file: ~a dozen files (settings / variations, e.g.
  `cullen_bay.abc` has 3).
- Multiple voices `V:`: 4 files (`hector_the_hero`, `ceo_ile`, `wagenborgen_4_4`,
  `wings_4_4`) — harmony.

## Approaches considered

1. **Purpose-built ABC-subset parser → BWW writer in this repo.** *(Chosen.)*
   Small tokenizer for Ed's ABC, inverted embellishment tables from
   `grace_notes.py`, BWW writer that mimics BMW Gold output. Targets the format Ed
   wants, reuses existing tables, and fails loudly on anything unfamiliar.
2. **ABC → MusicXML via an existing tool (abc2xml / music21).** Near-zero code,
   but embellishments become anonymous grace notes and it's unknown whether Braw
   Tunes recognises them as doublings, throws, etc. Rejected as the product; a
   single-tune import test is an optional comparison.
3. **ABC → MusicXML → BWW.** Worst of both; rejected.

Ed chose option 1: he owns BMW Gold, so going straight to its native format gives
the fewest chances for error.

## Design

### Package layout

```
bmw2abc_converter/
  converter.py        existing BWW→ABC
  grace_notes.py      existing tables (GRACE, DECO) — source of truth
  abc2bww.py          NEW: ABC tokenizer + BWW writer
  bww_header.py       NEW: BMW Gold boilerplate header text
```

A second CLI entry point `abc2bww` in `pyproject.toml`, alongside `bmw2abc`.

### Pipeline

1. **Split** the file on `X:` into tunes. Shared file-level lines before the first
   `X:` (e.g. `%%flatbeams`) are ignored.
2. **Header** per tune: read T (first T: only), R, C, Q, M, L, K, V.
3. **Voice selection**: if `V:` present, keep only the first voice's music; warn
   `harmony voice V:2 dropped`.
4. **Tokenize** the body into: grace group, note (pitch + length), broken-rhythm
   marker, tie, tuplet start, barline/repeat, ending, rest, chord symbol, inline
   field, decoration, comment, line end.
5. **Resolve rhythm**: compute each note's absolute duration from `L:` × length
   modifier, then apply broken rhythm (`a>b` → a ×3/2, b ×1/2; `a<b` the reverse;
   `>>` / `<<` likewise ×7/4, ×1/4). Map to BWW denominator + dot (`'x`) or
   double dot (`''x`). Any duration that doesn't map → warning.
6. **Resolve embellishments**: map each `{...}` + following note to a BWW token
   (see below).
7. **Beaming**: notes not separated by whitespace in ABC form a beam group; within
   a group emit `r` on all but the last eighth-or-shorter and `l` on the last
   (match the convention BMW Gold uses — verify against sample files during
   implementation; the reverse converter's handling of `r`/`l` is the reference).
8. **Write** BWW.

### Header mapping

Standard BWW (per the BMW format and Moine's `bww2abc.js`): `T` = **title**,
`Y` = **tune type**, `M` = composer, `F` = footer. Output uses the standard codes.

Note: the bagpipemusic.com (Lee & Sons) files swap these — all 97 purchased files
put the type ("March", "Reel"…) under `T` and the title under `Y`. Ed has always
had to fix this by hand. Output must **not** copy Lee's swap; the font/position
part of each tuple can be copied from Lee's files (title centred 24pt, type left
14pt, composer right 14pt).

| ABC | BWW |
|-----|-----|
| `T:` (first) | `"…",(T,C,0,0,Times New Roman,24,700,0,0,18,0,0,0)` |
| `R:` | `"…",(Y,L,0,0,Times New Roman,14,700,0,0,18,0,0,0)` |
| `C:` | `"…",(M,R,0,0,Times New Roman,14,700,0,0,18,0,0,0)` |
| `Q:1/4=N` | `TuneTempo,N` (if absent, omit — Builder's call to confirm BMW default) |
| `K:HP` / `K:Hp` | `& sharpf sharpc` |
| `M:6/8` etc. | `6_8`; `M:C` → `C`; `M:C|` → `C_` on the first `&` line |

**Lee swap flag in the existing BWW→ABC converter (low priority, last task):**
`converter.py` reads the codes correctly, so Lee files come out as `T:March`,
`R:The Barren Rocks of Aden`. Add an opt-in flag (e.g. `bmw2abc --swap-title-type`)
that swaps the two fields. Not needed for the ABC→BWW work; the Lee round-trip
tests compare music tokens only, so they don't depend on it.

### Embellishment mapping

Build a reverse table from `GRACE`: `ABC grace string → [BWW tokens]`. Many grace
strings are ambiguous on their own; disambiguate with the **following melody
note**, because BWW embellishment names encode the principal note (`dblg` vs
`dbla`, `grp` vs `hgrp`…).

- Lookup key = (grace string, following note pitch). Pre-compute from `GRACE`
  plus each token's known principal note (derivable from the token name family:
  `db*`, `tdb*`, `hdb*`, `str*`, `gst*`, `tst*`, `brl`, `grp`, `tar`, …).
- Single grace notes: `{g}` → `gg`, `{d}` → `dg`, `{e}` → `eg`, `{a}` → `tg`,
  `{A}` → `ag`, etc.
- If no named token matches, emit the grace notes as single-grace tokens in order
  **and warn** (e.g. `{fege}` may have no name).
- Where more than one token matches the same (string, note), prefer the one BMW
  Gold would produce when typing that embellishment; record choices in a small
  explicit override table in `abc2bww.py` with a comment per entry.
- Round-trip check: for every token in `GRACE`, `abc2bww(bmw2abc(token+note))`
  must give back the same token, or be listed as a known collision.

### Structure mapping

| ABC | BWW |
|-----|-----|
| `|` mid-line | `!` |
| `|` at end of source line | `!t` |
| `||` | `!!t` |
| `|]` | `!I` |
| `[|` | `I!` |
| `|:` | `I!''` |
| `:|` | `''!I` |
| `::` | `''!I` then `I!''` |
| `[1` / `|1` | `'1` |
| `[2` / `|2` | `'2` |
| end of ending | `_'` |
| `(3abc` | `^3s` … `^3e` around the three notes |
| `a-a` | `^ts` before the first note's token… `^te` after the second (match BMW Gold ordering) |
| `z`, `z2` … | `REST_8`, `REST_4` … |
| `% 2nd Part` (comment matching `Nth Part`) | standalone `"2nd Part"` line between staves, as in BMW Gold files |
| other `%` comments | dropped |
| chord symbols, `"…"` annotations | dropped, one summary warning per tune |
| `[M:…]` inline | time-sig token on its own (`C_` etc.) |

Each ABC source line becomes one BWW staff: a `&` clef line (`& sharpf sharpc`,
plus time sig on the first) followed by the line's music, ending `!t` / `!I` /
`''!I` as appropriate. Pickup (anacrusis) bars need no special handling.

### Multi-tune files and output naming

One `.bww` per `X:` tune. Naming follows abcm2ps EPS numbering:

- File with one tune: `<abc basename>.bww`
- File with N > 1 tunes: `<abc basename>001.bww`, `002.bww`, … in file order
  (not by X: number, since Ed sometimes repeats `X:1`).

### CLI

The primary use is **converting one or a few tunes at a time** so Ed can test each
in BMW Gold / Braw Tunes before trusting it. Converting the whole collection is a
secondary convenience he may not use until individual tunes check out.

```
abc2bww tune.abc                       # → ./tune.bww (or ./tune001.bww, 002 …)
abc2bww a.abc b.abc c.abc              # several tunes → current directory
abc2bww pipe_march/*.abc -o ~/bww/     # shell glob, into ~/bww/
abc2bww tune.abc --stdout              # print instead of writing (single-tune only)
abc2bww --all tunes/ -o bww_out/       # secondary: every pipe_* folder, mirrored tree
```

- Output goes to the **current directory** by default (never next to the input,
  which would litter the LaTeX tree); `-o DIR` picks another.
- Existing `.bww` files are not overwritten without `--force`.
- Each file prints its warnings as it goes; with more than one input, a short
  summary at the end (files written, files with warnings).
- `--all` takes a directory, only descends into `pipe_*` folders, mirrors the
  folder structure under `-o` (required with `--all`).

## Testing

1. **Unit tests** per mapping table (durations, broken rhythm, barlines, header).
2. **Embellishment round trip** over the whole `GRACE` table (above).
3. **Real-file round trip, BWW side**: the 97 Lee & Sons files (NAS:
   `…/Dropbox/_.piping/00.lee_and_sons/Light Music/<Tune>/<Tune>.bww`, alongside
   `.pdf`/`.mp3`) → `bmw2abc` → `abc2bww` → compare music tokens to the original
   (ignoring header boilerplate, whitespace, `space` tokens). Path comes from an
   env var (`LEE_BWW_DIR`); tests skip when it isn't set or mounted.
4. **Real-file round trip, ABC side**: every `pipe_*` tune → `abc2bww` →
   `bmw2abc` → compare normalised notes/durations/graces to the source ABC. This
   catches hand-transcribed quirks. Path via `NA_MARAGAN_DIR`, skip if absent.
   A handful of marches, strathspeys and reels are copied into `tests/fixtures/`
   so the core tests always run.

**Licensing:** this repo is public on GitHub. The Lee & Sons files are purchased —
they are never copied into the repo (including `bmw-to-convert/` and `convert/`,
which hold Lee files and stay untracked). Fixtures come only from Ed's own
na_maragan_collection ABC.

Priority: marches, strathspeys and reels first (Ed's current focus); jigs, airs,
hornpipes, lowland follow from the same code but get less test attention.
5. **Collection sweep (developer check)**: run over all 203 files; zero crashes;
   collect warnings. This is for finding gaps in the converter — Ed doesn't need to
   review it before testing individual tunes.
6. **Manual acceptance (Ed)**: open a sample of ~10 output files (covering march,
   strathspey, reel, jig, air, a multi-X file, a harmony file, an L:1/16 file) in
   BMW Gold and import into Braw Tunes.

## Decisions

Ed's:
- Target BWW (option 1), not MusicXML.
- Only `tunes/pipe_*`; no piobaireachd, no non-pipe trad tunes.
- Only the ABC Ed writes, not the full standard.
- Chords ignored.
- Multiple `X:` → separate numbered files, abcm2ps-style.
- na_maragan_collection and the Lee & Sons downloads are the official
  collection; borrowing ABC from na_maragan_collection for tests is fine.
- Marches, strathspeys, reels are the current focus.
- Old `tests/test_converter.py` deletion stands; not needed.

Claude's calls (correct any of these):
- Harmony: first voice only, with a warning. Braw Tunes imports only the melody
  and structure anyway. BMW harmony staves can be a later addition.
- `R:` → BWW type field, `C:` → composer; `B:`, `S:`, `N:`, `O:`, `W:` dropped.
- Lee's title/type swap: an opt-in flag on `bmw2abc` (Ed: "perhaps a flag…
  not priority").
- Write fresh tests for both directions in a new test file.
- Output naming: `name.bww` for one tune, `name001.bww`… for several.
- CLI: one or more files → current directory (or `-o`); no overwrite without
  `--force`; `--stdout` for quick looks; whole-collection `--all` is secondary.
- Part labels only from comments matching `% <ordinal> Part`.

## Left to the builder

- Exact BMW Gold conventions for beaming suffixes, tie token placement, and
  ending close (`_'`) — confirm from the sample BWW files, not from guesses.
- The override table for ambiguous embellishments.
- Whether `TuneTempo` is required by BMW Gold when `Q:` is absent.

## Appendix: grace groups in the collection

```
6098 {g}     1698 {d}     1300 {gef}   1202 {e}     974 {Gdc}    855 {gcd}
 664 {G}      639 {ag}     537 {GdG}    511 {gBd}    497 {gfg}    450 {gf}
 388 {a}      371 {A}      344 {fg}     341 {GAG}    255 {GdGe}   252 {ef}
 198 {gde}    141 {gAGAG}  126 {gdc}     87 {gBG}     86 {AGAG}    78 {cd}
  63 {gdG}     55 {f}       32 {afg}     27 {c}       23 {fege}    19 {dc}
  19 {Bd}      18 {GBG}     15 {gBeBG}   14 {gAd}     12 {BG}      11 {gGd}
   7 {gec}  7 {dG}  7 {cGdG}  6 {geA}  6 {eAfA}  6 {dGcG}  5 {de}  4 {ade}
   4 {aBd}  3 {GeGcG}  3 {gdf}  3 {Ad}  2 {GdGcG}  2 {Gd}  2 {gcGdG}  2 {gcG}
   2 {ga}  2 {acd}  1 {gfgf}  1 {gcdc}  1 {gBGdG}  1 {gBe}  1 {eg}  1 {ec}
```
