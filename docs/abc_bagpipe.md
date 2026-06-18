# ABC Notation for Bagpipes — Reference

Source: https://bagpipejourney.com/articles/abc_for_bagpipes.shtml
and analysis of bww2abc.js by Jean-Francois Moine.

---

## Key Signature

Two standard options for bagpipe ABC:

```
K:HP     -- no key signature on staff (piping tradition)
K:Hp     -- F#, C# on staff, G-natural (most common for display)
K:Hp exp ^f ^c ...  -- explicit accidentals override
```

`exp` after `Hp` means the following accidentals are explicit (used when the source
BWW file specifies its own accidentals).

---

## Note Names and Octave

With `K:Hp` and `L:1/8` (eighth note default):

| Bagpipe Pitch | ABC Letter | Case |
|--------------|-----------|------|
| Low-G | `G` | Uppercase |
| Low-A | `A` | Uppercase |
| B | `B` | Uppercase |
| C | `c` | Lowercase |
| D | `d` | Lowercase |
| E | `e` | Lowercase |
| F | `f` | Lowercase |
| High-G | `g` | Lowercase |
| High-A | `a` | Lowercase |

B, C, D, E, F each exist only in one octave for the bagpipe. G and A have
both a high and low version; uppercase = low, lowercase = high.

---

## Note Durations (with L:1/8)

| Duration | ABC | Example |
|----------|-----|---------|
| Whole | `8` | `A8` |
| Half | `4` | `A4` |
| Quarter | `2` | `A2` |
| Eighth | *(nothing)* | `A` |
| Sixteenth | `/` | `A/` |
| 32nd | `//` | `A//` |

---

## Dotted Notes

Dots are written as multipliers, not as `.`:

| Note value | Single dot (×3/2) | Double dot (×7/4) |
|-----------|-------------------|-------------------|
| Half | `A6` | `A7` |
| Quarter | `A3` | `A7/` |
| Eighth | `A3/` | `A7//` |
| Sixteenth | `A3//` | `A7///` |

---

## Grace Notes

Written in curly braces `{}` immediately before the principal note, no space:

```
{g}d2      -- High-G grace before D quarter
{GdG}d2    -- grip before D quarter
{gAd}a2    -- doubling before High-A quarter
```

Grace notes do not count toward the bar's duration. In `K:Hp`, grace notes
are automatically rendered small and stem upward.

---

## Barlines

| ABC | Meaning |
|-----|---------|
| `|` | Single barline |
| `||` | Double barline |
| `|]` | Final barline (thin-thick) |
| `[|` | Start section (thick-thin) |
| `|:` | Repeat start |
| `:|` | Repeat end |
| `::` | Repeat both ways |

---

## Repeats and First/Second Endings

```
|: music1 |1 music2 :| music3 |2 music4 |]
```

Or using explicit volta brackets:
```
[1 music :|
[2 music |]
```

---

## Tuplets

```
(3 A2 d2 e2     -- triplet of three quarter notes
(2 A2 d2        -- duplet (2 in time of 3)
```

---

## Ties

```
A2- A2          -- tied A quarters (= half)
```

---

## Fermata

```
HA2             -- H before note = fermata/hold
```

---

## Inline Directives

```
[M:3/4]         -- time signature change
[Q:1/4=120]     -- tempo change
[M:C]           -- common time change
[M:C|]          -- cut time change
```

---

## Decorations Used for Bagpipe

| ABC | Visual |
|-----|--------|
| `P` | Segno / repeat sign |
| `!trill!` | Trill marking |
| `!turn!` | Turn ornament |
| `!fine!` | Fine |
| `!D.C.alfine!` | D.C. al fine |
| `O` | Coda symbol |
| `!D.C.alcoda!` | D.C. al coda |
| `H` | Fermata (before note) |
| `y` | Extra space (visual separator) |

---

## Full Header Example

```abc
%abc-2.2
% Converted from amazing_grace.bww to ABC by bww2abc

X:1
T:Amazing Grace
C:John Newton
R:Hymn
Q:1/4=90
M:3/4
L:1/8
K:Hp exp ^f ^c
A2 | d3 e d2 | B6 | d3 B d2 | A6 | ...
```

---

## Software That Renders Bagpipe ABC

- **EasyABC** — desktop, supports `K:Hp` natively
- **abcjs** — JavaScript library; used by michaeleskin.com ABC tools
- **abcm2ps** — command-line, PostScript/PDF output
- **abc2midi** — MIDI output (limited bagpipe grace note support)
