# Conversion notes: design decisions and limits

How `bww2abc` and `abc2bww` map one notation onto the other, why, and what they
don't handle. For the token-level reference, see [bww_format.md](bww_format.md)
(BWW Gold), [bmw_legacy_format.md](bmw_legacy_format.md) (pre-Gold) and
[abc_bagpipe.md](abc_bagpipe.md) (ABC for pipes).

## Principles

- **Never silently wrong.** A tune that imports with a wrong note, a lost
  repeat, or a doubling turned into a strike is worse than a loud failure.
  Every lossy step prints a warning; unknown BWW tokens print
  `*** 'xyz' not recognised ***`.
- **BWW output looks like BMW Gold's own.** Use the same header block, staff
  layout and token order, so the files open cleanly in BMW Gold and import
  into apps that read BWW (for example Braw Tunes).
- **Named embellishments.** abc2bww writes `dbe`, `grp`, `tar` and so on, not
  strings of single gracenotes, whenever a named token exists.

## Pitch mapping

| Bagpipe | ABC | BWW note | BWW dot suffix |
|---|---|---|---|
| Low G | `G` | `LG_n` | `lg` |
| Low A | `A` | `LA_n` | `la` |
| B | `B` | `B_n` | `b` |
| C | `c` | `C_n` | `c` |
| D | `d` | `D_n` | `d` |
| E | `e` | `E_n` | `e` |
| F | `f` | `F_n` | `f` |
| High G | `g` | `HG_n` | `hg` |
| High A | `a` | `HA_n` | `ha` |

## bww2abc (BWW → ABC)

A Python port of Jean-Francois Moine's `bww2abc.js`
([reference/bww2abc_original.js](reference/bww2abc_original.js)), with these
changes:

- **Key:** `K:HP` by default, with no sharps drawn (the piping convention);
  `--hp` gives `K:Hp`. F♯ and C♯ are never written as accidentals; any other
  accidental (for example a natural high G) is.
- **Header codes:** `T` = title, `Y` = tune type, `M` = composer, `F` = footer.
  Files from bagpipemusic.com (Lee & Sons) store title and type the other way
  round; `--swap-title-type` fixes that.
- **Dots:** `'x` / `''x`, matched as a prefix so that two-letter suffixes
  (`'la`, `'ha`) work.
- **Ties:** Gold `^ts` sets a flag, and the `-` is written after the next note,
  so its gracenotes stay in front: `{G}A2-A`. The original JS ran both the old
  and the new tie code here.
- **Legacy ties and triplets:** `^t<pitch>` and `^3<pitch>` follow the
  note(s). A `^te` or `^3e` is a Gold "end" only when a `^ts` or `^3s` is open;
  otherwise it's an old-style tie or triplet on E.
- **Clef lines:** the time signature can be anywhere on an `&` line, and any
  music on the same line (such as `I!''`) is kept. Later `&` lines are staff
  starts.
- **Ignored:** `space` tokens, layout lines, and the DOS end-of-file byte.
- **Character set:** UTF-8 if valid, else Windows-1252 (what BMW Gold writes),
  so Gaelic accents survive.
- **Grace table corrections:** `lgstd` = `{gdc}`, `lhstd` = `{dc}`.

## abc2bww (ABC → BWW)

Written for the pipe-tune ABC subset in practical use, not the full ABC
standard. It was surveyed from a 203-tune collection:

- `K:HP`/`K:Hp` only.
- `L:1/8` or `1/16`.
- Broken rhythm `>` and `<` everywhere.
- Triplets `(3`.
- Ties.
- Repeats, and 1st/2nd endings.
- Rests.

### Pipeline
1. Split the file on `X:` into tunes. Each tune becomes one `.bww` file, since
   apps like Braw Tunes expect one arrangement per file. A file with one tune
   gives `name.bww`; one with N tunes gives `name001.bww` … `name00N.bww`, the
   way abcm2ps numbers its EPS files.
2. Read the header:
   - `T:` (first) → title (`T`).
   - `R:` → type (`Y`).
   - `C:` (first) → composer (`M`).
   - `B:` (joined with `; `) → footer (`F`).
   - `Q:` → `TuneTempo`. The default is 90, and the beat unit in `Q:` isn't
     converted.
   - `M:` → time signature: `C` → `C`, `C|` → `C_`, `6/8` → `6_8`.
3. Keep only the first voice; each dropped `V:` voice gets a warning. Harmony
   is not converted.
4. Tokenize. Chords, slurs and `!head-slashr!` marks are dropped with a
   warning. `\` continues a line. Several grace groups in a row are joined.
5. Turn lengths into BWW durations (denominator plus `'x` / `''x` dots),
   including broken rhythm. A length with no BWW equivalent is rounded, with a
   warning.
6. Embellishments: see below.
7. Beaming: notes not separated by spaces in the ABC form a beam group; the
   first is `r`, the rest `l`.
8. Write the BWW. Each ABC source line becomes one staff (`& sharpf sharpc`,
   with the time signature on the first staff only). Each later bar starts on
   a new line with `!` and a tab. Output uses CRLF line endings and the
   Windows-1252 character set. A character that won't fit gets a warning and
   is written as `?`.

### Structure mapping

| ABC | BWW |
|---|---|
| `\|` mid-line / at line end | `!` / `!t` |
| `\|\|` at line end / mid-line | `!!t` / `I!` |
| `\|]` | `!I` |
| `\|:` / `[\|:` | `I!''` |
| `:\|` / `:\|]` / `:\|\|` | `''!I` (also before a 2nd ending) |
| `::` | `''!I`, then `I!''` on the next staff |
| `[1` `\|1` `[2` `["2 of 2"` | `'1` `'1` `'2` `'22` |
| end of ending (`]`, a closing barline, or the end of a line) | `_'` |
| `(3abc` | `^3s` after the first note's gracenote … `^3e` after the third note (Lee's order) |
| `a-a` | `^ts` after the gracenote, before the first note … `^te` after the second |
| `z` | `REST_n` |
| `% 2nd Part` | a standalone `"2nd Part"` line between staves |
| body `M:` / `[M:]` | a time-signature token in place |

Notes after a line's last barline (a pickup into the next part), or an ending
that starts at the end of a line, move to the start of the next staff, which
is where Lee's files put them. A staff with no notes is skipped, with a
warning.

### Embellishments
The lookup key is (grace string, following note), because BWW names encode the
principal note (`dbla` versus `dbb`, `grp` versus `hgrp`). The order:

1. **Legacy:** `{gec}d` → `lgstd`, so ABC written with the old wrong table
   still maps.
2. **`grace_prefs.py`:** the token Lee & Sons' files actually use for that
   (grace, note) pair. It's generated by `scripts/build_grace_prefs.py` and
   stores token counts only, no tune content.
3. **A unique match** in `GRACE`.
4. **`_OVERRIDES`:** a hand-chosen token for strings that several tokens share
   (for example `{dc}` → `hthrd`).
5. **Fallback:** single gracenotes, with a warning. Low-G gracenotes can't be
   written this way.

Some light-music gracings resolve to piobaireachd token names that BMW draws
identically: `{eAfA}` → `embari`, `{fege}` → `endari`, `{gBeBG}` → `pelb`,
`{GBG}` → `rodin`.

## Testing approach

- **Unit tests:** one per mapping rule (`tests/test_*.py`).
- **Fixtures:** in `tests/fixtures/abc/`, from Ed's own collection, never from
  purchased books. Each tune goes ABC → BWW → ABC and must give the same notes,
  durations and gracenotes.
- **`LEE_BWW_DIR`:** 97 purchased BWW files go BWW → ABC → BWW → ABC with no
  change. These files are never copied into the repo.
- **`NA_MARAGAN_DIR`:**
  - Tunes marked `B:Lee & Sons` must match Lee's original note for note.
    Genuine transcription differences are listed in `KNOWN_DIFFS`.
  - A sweep of the whole collection checks for crashes and tallies warnings.
- **Legacy:** `tests/test_legacy_bmw.py` uses made-up snippets. The fixes were
  also checked against a 2,900-file archive through abcm2ps; see
  [bmw_legacy_format.md](bmw_legacy_format.md).

## Known limitations

- Harmony voices are dropped, and BWW has no chords.
- `:|:` and `||:` lose the repeat start (a warning prints).
- Tuplet counting ignores rests, so a triplet that contains a rest closes on
  the wrong note.
- Three or more notes tied in a row produce overlapping tie marks.
- A staff that's only a final barline is skipped, so the tune ends on a plain
  barline.
- `abc2bww --stdout` writes UTF-8 with LF line endings; files are
  Windows-1252 with CRLF.
- A part label inside a dropped harmony voice attaches to the melody.
- Duration warnings name the staff but not the bar.
- With `--force`, two inputs that have the same name overwrite each other in
  one output folder.
- Legacy files whose tokens run together (no line breaks, as in `HAl_16!`)
  aren't split.
- Piobaireachd is out of scope; its movement tokens are reported as not
  recognised.
