# Bagpipe Sheet Music — Reference for AI Image Recognition

This document is designed to be included as context when prompting a vision-capable
LLM to read bagpipe sheet music from an image and produce ABC notation output.

---

## The Bagpipe Scale

The Great Highland Bagpipe has a fixed nine-note scale. There are no sharps or flats
chosen by the player — the instrument is always in the same key.

| Degree | Name | ABC letter | Staff position (K:HP treble clef) |
|--------|------|-----------|----------------------------------|
| 1 | Low-G | `G` | Below the staff (ledger line below) |
| 2 | Low-A | `A` | First space below the staff |
| 3 | B | `B` | First line of staff |
| 4 | C | `c` | First space |
| 5 | D | `d` | Second line |
| 6 | E | `e` | Second space |
| 7 | F | `f` | Third line |
| 8 | High-G | `g` | Third space |
| 9 | High-A | `a` | Fourth line |

These nine pitches cover the entire range. There are no accidentals in the melody.
Low-G and Low-A are below the staff; the rest are on the lower half of the staff.
The key signature (`K:HP` or `K:Hp`) implies F# and C#.

---

## Note Durations

Standard note shapes apply. Bagpipe tunes most commonly use:

| Duration | Shape | ABC (with L:1/8) |
|----------|-------|-----------------|
| Breve (double whole) | Two vertical bars through head | `8` after note |
| Semibreve (whole) | Open oval, no stem | `8` after note |
| Minim (half) | Open oval with stem | `4` after note |
| Crotchet (quarter) | Filled oval with stem | `2` after note |
| Quaver (eighth) | Filled oval, stem, one flag/beam | *(nothing)* |
| Semiquaver (sixteenth) | Filled oval, stem, two flags/beams | `/` after note |
| Demisemiquaver (32nd) | Filled oval, stem, three flags/beams | `//` after note |

### Dotted Notes

A dot to the right of the note head increases duration by half (single dot) or
three-quarters (double dot).

| Duration | Single dot (×3/2) | Double dot (×7/4) |
|---------|-------------------|-------------------|
| Quarter | `A3` | `A7/` |
| Eighth | `A3/` | `A7//` |
| Sixteenth | `A3//` | `A7///` |

### Beaming

Eighth notes and shorter are often beamed in groups. A beam connecting notes means
they are grouped rhythmically. In ABC, beamed notes have no space between them;
unbeamed groups are separated by a space.

---

## Grace Notes (Embellishments)

Bagpipe embellishments are written as small notes (grace notes) before the principal
note. They appear in ABC as `{sequence}` immediately before the note: `{gAd}A2`.

Grace notes are always High-G (`g`), High-A (`a`), Low-G (`G`), Low-A (`A`),
B (`B`), c, d, e, f in ABC. They have no rhythmic duration — they are ornamental.

### Identifying Embellishments Visually

Grace notes are noticeably smaller than principal notes, with upward stems. They
appear to the left of the principal note. Multiple grace notes form a beamed group.

### Common Embellishments

#### Single Grace Notes
One small note. Named for the grace note pitch:

| Visual | Name | ABC |
|--------|------|-----|
| Small High-G before note | `gg` (High-G grace) | `{g}` |
| Small High-A before note | `tg` (thumb grace) | `{a}` |
| Small Low-A before note | `ag` | `{A}` |
| Small D before note | `dg` | `{d}` |
| Small E before note | `eg` | `{e}` |

#### Doublings
Two grace notes — High-G + a lower grace — producing a "doubled" effect.
The first grace is always High-G; the second varies by pitch of principal note.

| Principal note | Name | ABC grace |
|---------------|------|-----------|
| Low-G | `dblg` | `{gGd}` |
| Low-A | `dbla` | `{gAd}` |
| B | `dbb` | `{gBd}` |
| C | `dbc` | `{gcd}` |
| D | `dbd` | `{gde}` |
| E | `dbe` | `{gef}` |
| F | `dbf` | `{gfg}` |
| High-G | `dbhg` | `{gf}` |
| High-A | `dbha` | `{ag}` |

Thumb doublings (`tdbl…`) use High-A as first grace instead of High-G.
Half doublings (`hdbl…`) omit the first grace entirely.

#### Grips
Three small notes: Low-G, D, Low-G. Written above a principal note of any pitch.
Visually: three beamed grace notes with a distinctive Low-G D Low-G pattern.

| Name | ABC grace |
|------|-----------|
| `grp` (regular) | `{GdG}` |
| `hgrp` (half) | `{dG}` |

#### Taorluath
Four grace notes: Low-G, D, Low-G, E.

| Name | ABC |
|------|-----|
| `tar` | `{GdGe}` |

#### Birl
Three grace notes on Low-A: Low-G, Low-A, Low-G.
Appears on a Low-A principal note.

| Name | ABC |
|------|-----|
| `brl` | `{GAG}` |
| `abr` (A birl) | `{AGAG}` |

#### D Throws
Two or three grace notes producing a throwing effect before D.

| Name | ABC |
|------|-----|
| `thrd` (light D throw) | `{Gdc}` |
| `hvthrd` (heavy D throw) | `{GdGc}` |

#### Strikes
Single grace note before a note, same as single grace notes but named differently.
Visually identical to single grace notes.

| Name | ABC |
|------|-----|
| `strlg` / `strla` / `strb` etc. | Same as single grace, e.g. `{G}` |

#### Peles, Cadences, Echo Beats
Complex multi-grace patterns; see `docs/bww_format.md` for the complete table.
Peles: five grace notes in a characteristic repeated pattern.
Cadences: end-of-phrase ornaments, often with a held grace note (`H` prefix in ABC).
Echo beats: two identical grace notes creating a rhythmic echo effect.

---

## Barlines and Structure

| Visual appearance | Meaning | ABC |
|------------------|---------|-----|
| Single thin vertical line | Barline | `|` |
| Two thin vertical lines | Double barline | `||` |
| Thin + thick line | Final barline | `|]` |
| Thick + thin line | Start of piece | `[|` |
| Thin line + two dots | Repeat start | `|:` |
| Two dots + thin line | Repeat end | `:|` |

### First and Second Endings

Bracket above the staff with a `1` or `2` (or `1.` / `2.`) indicates a volta
bracket (first/second ending). In ABC: `[1 ... :| [2 ... |]`

---

## Time Signatures

Bagpipe tunes use a small set of time signatures:

| Signature | Tune type | ABC |
|-----------|-----------|-----|
| 2/4 | March, Quickstep | `M:2/4` |
| 3/4 | Waltz, Slow Air | `M:3/4` |
| 4/4 | March, Slow March | `M:4/4` |
| 6/8 | Jig, March | `M:6/8` |
| 9/8 | Slip Jig | `M:9/8` |
| 12/8 | Reel (rare) | `M:12/8` |
| C | Common time (4/4) | `M:C` |
| ₵ | Cut time (2/2) | `M:C|` |

Strathspeys are typically 4/4 but written with many dotted-note and "snap" patterns.
Reels are typically 4/4 with even eighth notes.
Hornpipes are 4/4 with dotted-note patterns.

---

## Key Signatures

The bagpipe has exactly one key:

```
K:HP   -- no marks on staff (traditional)
K:Hp   -- F# and C# written on staff
```

If you see a one-sharp or two-sharp key signature on bagpipe music, it is the
bagpipe key (F# or F# + C#). Treat both as `K:HP` or `K:Hp`.

---

## Tempo and Expression

Tempo markings appear above the staff. Common bagpipe markings:

| Marking | Typical BPM range |
|---------|------------------|
| Slow Air | 40–60 |
| Slow March | 60–76 |
| March (quick) | 80–120 |
| Strathspey | 80–96 |
| Reel | 96–126 |
| Jig | 80–112 |

In ABC: `Q:1/4=90` for ♩ = 90.

---

## Ties and Slurs

A curved line connecting two notes:

- **Tie** — connects two notes of the **same pitch**; the second note is not re-tongued.
  In ABC: `-` appended after the first note. `A2-A`
- **Slur** — connects notes of **different pitches** for legato effect. Bagpipe players
  rarely notate slurs; when present, in ABC use `(` before and `)` after.

A grace note before a tied note is still part of the second note:
```
{G}A2-A   -- correct: grace on the tied-to note, tie after A2
```

---

## Repeats and Sections

Many bagpipe tunes have multiple parts (1st Part, 2nd Part, 3rd Part, 4th Part),
each with its own repeat. Typical structure:

```
Part 1:  |: A A :| (played twice)
Part 2:  |: B B :| (played twice)
...
```

Section names may appear above the staff as text. In ABC output, emit as a comment:
`% 2nd Part`

---

## ABC Output Template

```abc
%abc-2.2
% Converted from image

X:1
T:Tune Title
C:Composer Name
R:Tune Type (March / Strathspey / Reel / Jig)
Q:1/4=80
M:4/4
L:1/8
K:HP
|: {g}A2{d}c2 {gef}e2{d}c2 | {gde}d2{G}A2-A2 | ... :|
% 2nd Part
|: ... :|
```

---

## Practical Tips for Image Recognition

1. **Identify the staff** — treble clef, key sig (1–2 sharps = bagpipe), time sig.
2. **Map note positions to pitches** — use the staff position table above. Low-G is
   on a ledger line below; Low-A is the space just below the staff.
3. **Identify grace notes** — small notes to the left of principal notes. Count them
   and note their positions to identify the embellishment type.
4. **Read note stems and flags** for duration.
5. **Look for dots** after note heads (dotted rhythms are very common).
6. **Find barlines** to divide the music into measures.
7. **Find repeat signs** (double bars with dots).
8. **Read section labels** in the text above the staff.
9. **Output one measure per line** of ABC for readability.
10. **If you cannot identify an embellishment** with certainty, output the grace notes
    you can see by pitch; a reviewer familiar with bagpipe music will recognise the pattern.

---

## Common Pitfalls

- **Ties vs slurs**: a curved line between two notes of the **same pitch** is a tie (`-`).
  Between different pitches it would be a slur (very rare on bagpipe).
- **Dotted notes in strathspeys**: strathspeys use a characteristic "Scottish snap"
  (short note before a long note, e.g. `A/d3/` — sixteenth then dotted eighth).
- **Grace notes are NOT part of the bar's duration**: the bar's note values must add
  up to the time signature without counting grace notes.
- **Low-G and Low-A look similar**: Low-G is on a ledger line below the staff;
  Low-A is in the space just below the first line.
- **High-G and High-A**: High-G is on the third space; High-A is on the fourth line.
  High-A appears much less often than High-G.
- **Beaming**: eighth-note groups beamed together should have no ABC space between them.
