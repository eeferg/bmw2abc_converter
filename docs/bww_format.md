# BWW File Format Reference

BWW (Bagpipe Music Writer) files are plain-text files produced by Bagpipe Music Writer Gold
and the free Bagpipe Reader/Player. Both `.bmw` and `.bww` extensions exist; the format is
identical.

Primary references:
- BNF spec: http://forums.bobdunsire.com/forums/showthread.php?t=123219
- Bagpipe_Reader.pdf (bundled with Bagpipe Reader)
- MuseScore bww2mxml lexer: `docs/musescore_bww_lexer.cpp`
- bww2abc.js by Jean-Francois Moine (GPL3+): `docs/bww2abc_original.js`

---

## Overall Structure

```
<file-header lines>        -- MIDINoteMappings, FrequencyMappings, etc. (ignored)
<metadata lines>           -- "Title", "Composer", etc.
TuneTempo,<bpm>            -- optional tempo in header
& <accidentals> <timesig>  -- CLEF LINE: marks start of music; may span two lines
<music lines>              -- space-separated tokens, multiple per line
```

---

## File Header Lines (ignored in conversion)

Lines that appear before the metadata and are skipped:

```
Bagpipe Reader:1.0
MIDINoteMappings,(54,56,...)
FrequencyMappings,(370,415,...)
InstrumentMappings,(71,71,...)
GracenoteDurations,(20,40,...)
FontSizes,(100,90,90)
TuneFormat,(1,0,M,L,500,500,500,500)
```

---

## Metadata Lines (header section)

All metadata appears before the `&` clef line.

| BWW token | Meaning | ABC output |
|-----------|---------|------------|
| `"Title",(T,...)` | Tune title | `T:Title` |
| `"Composer",(M,...)` | Composer | `C:Composer` |
| `"Type",(Y,...)` | Tune type/rhythm | `R:Type` |
| `"Footer",(F,...)` | Footer text | `%%footer \tFooter` |
| `"Text",(...)` | Other text (no `,T/M/Y/F`) | `% Text` (comment) |
| `TuneTempo,90` | Tempo (♩= 90) | `Q:1/4=90` |

The format of a metadata line is:
```
"<text>",(<type>,<align>,<x>,<y>,<font>,<size>,<weight>,<italic>,<underline>,<strike>)
```
`<type>` is the letter after the closing `"` and comma: T=title, M=composer, Y=type, F=footer.

---

## Clef Line (`&`)

The `&` line signals the start of musical content. It contains the key signature
(accidentals) and the time signature. The time signature may appear on the following line.

```
& sharpf sharpc 3_4
& sharpf sharpc
3_4
& sharpf sharpc C
& sharpf sharpc C_
```

### Accidental tokens on `&` line

| BWW token | Meaning | ABC key modifier |
|-----------|---------|-----------------|
| `sharpf` | F sharp | `^f` |
| `sharpc` | C sharp | `^c` |
| `sharpg` | G sharp | `^g` |
| `flatb` | B flat | `_b` |
| `naturalhg` | High-G natural | `=g` |
| `naturalha` | High-A natural | `=a` |
| `naturallg` | Low-G natural | `=G` |
| `naturalla` | Low-A natural | `=A` |

General pattern: `(sharp|flat|natural)(note)` where note is a pitch name
(`a`, `b`, `c`, `d`, `e`, `f`, `g`, `hg`, `ha`, `lg`, `la`).

High/low note suffix mapping:
- `hg` → ABC `g` (High-G)
- `ha` → ABC `a` (High-A)
- `lg` → ABC `G` (Low-G)
- `la` → ABC `A` (Low-A)

### Time signature tokens

| BWW token | Meaning | ABC output |
|-----------|---------|------------|
| `C` | Common time (4/4) | `M:C` |
| `C_` | Cut time (2/2) | `M:C|` |
| `2_4` | 2/4 | `M:2/4` |
| `3_4` | 3/4 | `M:3/4` |
| `4_4` | 4/4 | `M:4/4` |
| `6_8` | 6/8 | `M:6/8` |
| `9_8` | 9/8 | `M:9/8` |
| `12_8` | 12/8 | `M:12/8` |

Format: `N_M` where N=numerator, M=denominator. Converted to ABC `N/M`.

---

## Note Tokens

Pattern: `[HL]?[ABCDEFG][rl]?_<denom>`

### Pitch encoding

Bagpipe range: Low-G, Low-A, B, C, D, E, F, High-G, High-A

| BWW token prefix | Octave | ABC case |
|-----------------|--------|----------|
| `L` or bare for B | Low | Uppercase |
| `H` or bare non-B | High | Lowercase |

Full pitch mapping:

| BWW note | Bagpipe pitch | ABC note |
|----------|--------------|----------|
| `LG_N` | Low-G | `G` |
| `LA_N` | Low-A | `A` |
| `B_N` | B (always low) | `B` |
| `C_N` | C | `c` |
| `D_N` | D | `d` |
| `E_N` | E | `e` |
| `F_N` | F | `f` |
| `HG_N` or `G_N` | High-G | `g` |
| `HA_N` or `A_N` | High-A | `a` |

### Duration encoding

`N` is the denominator of the note value relative to a whole note:

| BWW denom | Note value | ABC length (base L:1/8) |
|-----------|-----------|------------------------|
| `1` | Whole | `8` |
| `2` | Half | `4` |
| `4` | Quarter | `2` |
| `8` | Eighth | *(nothing, = 1 unit)* |
| `16` | Sixteenth | `/` |
| `32` | 32nd | `//` |

### Dotted notes

A dot token follows the note token. Tokens: `'<letter>` (single dot) or `''<letter>` (double dot),
where letter is one of `a b c d e f g h l`.

| Dot | BWW denom | ABC modifier |
|-----|-----------|-------------|
| Single | 2 | `6` |
| Single | 4 | `3` |
| Single | 8 | `3/` |
| Double | 2 | `7` |
| Double | 4 | `7/` |
| Double | 8 | `7//` |

### Beaming (`r`/`l` suffix)

On eighth notes and shorter, `r` (right stem, beam open) and `l` (left stem, beam close)
indicate grouping. ABC spaces separate beaming groups.

### Accidentals (inline)

Appear as a separate token *before* the note:

| BWW token | ABC |
|-----------|-----|
| `sharpX` | `^` |
| `flatX` | `_` |
| `naturalX` | `=` |

---

## Barline and Structure Tokens

| BWW token | Meaning | ABC output |
|-----------|---------|------------|
| `!t` | Single barline | `|` (line break) |
| `!!t` | Double barline | `||` |
| `!I` | Final barline | `|]` |
| `I!` | Double barline | `||` |
| `I!''` | Repeat start | `|:` |
| `''!I` | Repeat end | `:|` |
| `!` (other) | Barline variant | `|` |

---

## Repeat Bracket Tokens

| BWW token | Meaning | ABC output |
|-----------|---------|------------|
| `'1` | First ending | `[1` |
| `'2` | Second ending | `[2` |
| `'12` | "1 of 2" | `["1 of 2"` |
| `'123` | "1 of 2 & 3" | `["1 of 2 & 3"` |
| `_` | Close bracket | `]` |
| `'intro` | Introduction | `["Introduction"` |

---

## Rests

Pattern: `REST_<denom>`

| BWW token | Duration | ABC |
|-----------|---------|-----|
| `REST_1` | Whole rest | `z8` |
| `REST_2` | Half rest | `z4` |
| `REST_4` | Quarter rest | `z2` |
| `REST_8` | Eighth rest | `z` |
| `REST_16` | 16th rest | `z/` |
| `REST_32` | 32nd rest | `z//` |

---

## Tuplets

| BWW token | Meaning | ABC |
|-----------|---------|-----|
| `^2s` | Duplet start | `(2` |
| `^2e` | Duplet end | *(ignored)* |
| `^3s` | Triplet start | `(3` |
| `^3e` | Triplet end | *(ignored)* |
| `^4s` ... `^7s` | Other tuplets | `(N:M` |

---

## Ties and Slurs

| BWW token | Meaning | ABC |
|-----------|---------|-----|
| `^ts` | Tie start | `-` appended after next note |
| `^te` | Tie end | *(ignored)* |

---

## Inline Tempo / Time Signature Changes

| BWW token | Meaning | ABC |
|-----------|---------|-----|
| `TuneTempo,90` | Tempo change | `[Q:1/4=90]` |
| `4_4` | Time sig change | `[M:4/4]` |
| `C` | Common time change | `[M:C]` |
| `C_` | Cut time change | `[M:C|]` |

---

## Fermata

A fermata is indicated by the token `fermat` or `fermata` appearing *after* a note token.
The note gets `H` prepended in ABC. The fermata token is consumed.

---

## Decorations (`deco` table)

| BWW token | ABC decoration |
|-----------|---------------|
| `pembari` | `P` |
| `pendari` | `P` |
| `pechedari` | `P` |
| `pehedari` | `P` |
| `pdili` | `!trill!` |
| `ptra` | `!trill!` |
| `phtra` | `!trill!` |
| `ptra8` | `!trill!` |
| `pgrp` | `!trill!` |
| `pdarodo` | `!turn!` |
| `pdarodo16` | `!turn!` |
| `phdarodo` | `!turn!` |
| `phiharin` | `P` |
| `fine` | `!fine!y` |
| `dacapoalfine` | `!D.C.alfine!y` |
| `coda` | `O` |
| `dacapoalcoda` | `!D.C.alcoda!y` |
| `codasection` | `O` |

---

## Grace Note Tokens (`grace` table)

Grace notes are rendered in ABC as `{<grace_seq>}` before the principal note.
ABC note letters: `G`=Low-G, `A`=Low-A, `B`=B, `c`=C, `d`=D, `e`=E, `f`=F, `g`=High-G, `a`=High-A.

### Single Grace Notes
| BWW | ABC grace | Description |
|-----|-----------|-------------|
| `ag` | `A` | Low-A grace |
| `bg` | `B` | B grace |
| `cg` | `c` | C grace |
| `dg` | `d` | D grace |
| `eg` | `e` | E grace |
| `fg` | `f` | F grace |
| `gg` | `g` | High-G grace |
| `tg` | `a` | Thumb (High-A) grace |

### Regular Doublings
| BWW | ABC grace |
|-----|-----------|
| `dblg` | `gGd` |
| `dbla` | `gAd` |
| `dbb` | `gBd` |
| `dbc` | `gcd` |
| `dbd` | `gde` |
| `dbe` | `gef` |
| `dbf` | `gfg` |
| `dbhg` | `gf` |
| `dbha` | `ag` |

### Thumb Doublings
| BWW | ABC grace |
|-----|-----------|
| `tdblg` | `aGd` |
| `tdbla` | `aAd` |
| `tdbb` | `aBd` |
| `tdbc` | `acd` |
| `tdbd` | `ade` |
| `tdbe` | `aef` |
| `tdbf` | `afg` |

### Half Doublings
| BWW | ABC grace |
|-----|-----------|
| `hdblg` | `Gd` |
| `hdbla` | `Ad` |
| `hdbb` | `Bd` |
| `hdbc` | `cd` |
| `hdbd` | `de` |
| `hdbe` | `ef` |
| `hdbf` | `fg` |

See `docs/bww2abc_original.js` for the complete grace note table including strikes,
grips, taorluaths, birls, throws, peles, cadences, and echo beats.

---

## ABC Output Format

```
%abc-2.2
% Converted from <filename> to ABC by bww2abc

X:1
T:<title>
C:<composer>
R:<type>
Q:1/4=<bpm>
M:<time_sig>
L:1/8
K:Hp exp <accidentals>
<music lines>
```

- `K:Hp exp <key>` — bagpipe key; `exp` means explicit accidentals follow
- Each barline causes a newline in the output
- Grace notes: `{<sequence>}` immediately before the note, no space
- Beamed groups: no space between notes; `l`-flagged note adds a space after
