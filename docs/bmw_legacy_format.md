# Legacy BMW (pre-Gold) format: findings

Notes from a survey on 2026-11-27 of about 2,900 old `.bmw`/`.bww` files: an
archive Ed collected years ago, plus the "sprague" tunes. The files weren't
kept, so this document records what they showed. Counts are files or tokens in
that archive.

## Which files are old-format

| First line | Files | Meaning |
|---|---|---|
| `Bagpipe Music Writer Gold:1.0` / `Bagpipe Musicworks Gold:1.0` | 414 | Gold (current) format |
| a quoted string (`"Tune Title"`) | 2,476 | old (pre-Gold) format |
| `<!DOCTYPE HTML …` | 10 | not tunes (saved web pages) |

The file extension says nothing about the format. `.bmw` files can be Gold
format, and `.bww` files can be old format. Detect the format from the first
line.

## Differences from Gold

### Header
- There's no `Bagpipe Music Writer Gold:` line, no `MIDINoteMappings` and
  similar lines, and no `TuneTempo`.
- Text lines have no `(T,…)` / `(Y,…)` / `(M,…)` / `(F,…)` codes. The meaning
  comes from position: line 1 is the title, line 2 the tune type, line 3 the
  composer or arranger, and line 4 the footer (often `""`).
  ```
  "Eibhli Geal Ciuin ni Cearbhaill"
  "Slow Air"
  "Arranged by Dave Rickard"
  ""
  ```
- bmw2abc turns these lines into `%` comments, so the ABC has no title.

### Clef line
- `& 6_8` or `& c_` appears without `sharpf sharpc`. Later staves are often a
  bare `&`.

### Ties: the pitch-named marker goes after the FIRST note
```
LA_4 'la ^tla LA_4        old:  ^t + pitch, after the first note (and its dot)
^ts LA_4 LA_4 ^te         Gold: ^ts before the first note, ^te after the second
```
Pitch suffixes: `lg la b c d e f hg ha`. In the archive: `^te` 682, `^tla` 656,
`^td` 628, `^tf` 486, `^tc` 460, `^tb` 312, `^tha` 304, `^thg` 112, `^tlg` 60.

**Clash:** the old tie on E is `^te`, the same token as Gold's tie end. Some
Gold-format files mix the two styles: 58 more `^te` than `^ts`.

### Triplets: the pitch-named marker goes after the THIRD note
```
Br_16 Cl_16 Dl_16 ^3d     old:  ^3 + pitch, after the triplet
^3s Br_16 Cl_16 Dl_16 ^3e Gold: ^3s before, ^3e after
```
In the archive: `^3hg` 358, `^3d` 256, `^3ha` 224, `^3f` 174, `^3c` 56, `^3e` 50,
`^3b` 26, `^3lg` 8, `^3la` 8.

**Clash:** the old triplet ending on E is `^3e`, the same token as Gold's
triplet end.

### Line endings and file end
- Lines end in CR CR LF (`\r\r\n`). Some files have no usable line breaks at
  all, so tokens run together: `HAl_16!`, `!t&!`, `''!I&`, `A_8I!''`.
- A DOS end-of-file byte, `\x1a` (Ctrl-Z), sits at the end of the file
  (108 tokens).

### Character set
- None of the old-format files contain bytes above 127, so the DOS code page
  (CP437) question didn't come up in practice.

### Other tokens seen (for later)
- `SP2`, `SP4`, `SP6`, `sp2`: spacing directives, probably.
- Lowercase notes `al_8`, `a_4`, and `c`/`c_` used as a time signature
  (common time).
- Possible old embellishment names: `hrst`, `wrst`, `dbsthg`, `3g`.
- Piobaireachd movements, out of scope for Ed: `crunl`, `edre`, `edreb`,
  `chedare`, `cnat`, `podro`, `ptbrea`, `pdare`, `htarla`, `pt`, `pc`, `pl`,
  `ptb`.
- In Gold files: `'bis` / `bis_'` (a "bis", play-twice, bracket), and `'si`,
  `'do` (probably "segno" and "D.C."-style marks).
- Gold files with a second `Bagpipe Music Writer Gold:1.0` header partway
  through (29 files): several tunes joined into one file.

## What bmw2abc does with old-format files

The 2026-11-27 survey found these problems. None is fixed yet.

| Problem | Severity | Status |
|---|---|---|
| Old tie on E (`^te`) treated as a Gold tie end, so the tie is silently dropped | wrong output | open |
| Old triplets: `(3` written after the triplet, onto the following notes, not before it | wrong output | open |
| Old header gives no `T:`/`R:`/`C:`; title, type and composer become `%` comments | wrong output | open |
| `\x1a` reported as an unknown token | noise | open |
| Tokens run together with no line breaks (`HAl_16!`) | wrong output | open |

Proposed fixes:

- **Ties on E:** a `^te` is a Gold tie end only when a `^ts` is open. Otherwise
  it's an old tie on E.
- **Triplets:** an old `^3<pitch>` puts `(3` before the last three notes of the
  measure. A `^3e` with no `^3s` open is an old triplet ending on E.
- **Header:** the leading quoted lines are mapped by position: title → `T:`,
  type → `R:`, composer → `C:`, footer → `%%footer`.
- **`\x1a`:** stripped as the file is read.
