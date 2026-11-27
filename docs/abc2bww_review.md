# abc2bww — things for Ed to check

Open items from the first abc2bww build (2026-11-26). Tick them off or delete
them as you go.

## 1. Try the output in the real programs

- [ ] Open some files from `~/bww_test/` in BMW Gold. That folder has 21 `.bww`
      files made from 12 ABC tunes: marches, strathspeys, reels, a jig, an air,
      a hornpipe, a harmony tune and files with several X: settings.
- [ ] Import a few of them into Braw Tunes.
- [ ] Check how the gracenote groups that come out under piobaireachd names
      look in BMW: `{eAfA}` → `embari`, `{fege}` → `endari`, `{gBeBG}` → `pelb`,
      `{GBG}` → `rodin`.

## 2. Embellishment tables

- [x] `lgstd` changed from `{gec}` to `{gdc}`, the way you write it 115 times.
      `bmw2abc` now writes `{gdc}d` as well. Confirmed: your commit 3027efd on
      main (2026-11-25) made the same fix.
- [x] `lhstd` was `{ed}`, which is wrong. The BMW manual gives the light half
      strike on D as `{dc}d`, and the table now has that. `{ed}d` appears
      nowhere in the collection. abc2bww writes `{dc}d` as `hthrd` (half D
      throw), which has the same gracenotes.
- [x] `gstd` = `{gdG}d`, confirmed from the BMW manual.

## 3. Lee-marked tunes that differ from Lee's file

The converter copies your ABC faithfully, so in each case either your
transcription or Lee's file is different. These are listed in `KNOWN_DIFFS` in
`tests/test_roundtrip.py`. Remove an entry from that list once its tune is
fixed, so the test checks it again.

- [ ] angus_j_maclellan: 3rd part, you have e3/16 + d1/32 where Lee has e3/16 + d1/16
- [ ] clan_maccoll_2_4: 4th part, you have `{gef}e` dotted 8th + A 16th, Lee has a dotted 16th + 32nd
- [ ] donald_maciver_2_4: 2nd ending, a 32nd after the dotted c (Lee has a 16th, and yours doesn't add up); the last A is an 8th where Lee has a quarter
- [ ] donald_macleans_farewell_to_oban_2_4: 2nd ending, the last `{GAG}A` is an 8th where Lee has a quarter
- [ ] flowers_of_the_forest: Lee's file has a stray double dot token on a D (probably Lee's error)
- [ ] glendaurel_highlanders_6_8: 2nd-ending pickup `{GAG}A/` is a 16th where Lee has a dotted 8th
- [ ] meg_macrae_6_8: 2nd-ending pickup `{GdGe}B/` is a 16th where Lee has a dotted 8th
- [ ] haughs_of_cromdale_2_4: 2nd part, `{g}g` where Lee has `{f}g`
- [ ] newmarket_house: 2nd part, doubling `{gef}e` where Lee has a single `{g}e`
- [ ] shepherds_crook: extra C pickup at the start (Lee's "C" there is the common-time sign)
- [ ] thornton_jig_pipes: your setting adds 1st/2nd endings where Lee has a plain repeat

These Lee-marked tunes have no Lee file to compare against: Camanachd Ghlaschu,
both Cabar Fèidh settings, and Farewell to the Creeks (reel).

## 4. Collection typos

- [ ] `tail_toddle.abc` has a capital `D` twice. That's below the chanter's
      range; it's converted as `d`.

### Gracenote groups that end on the melody note's own pitch

A group like `{ed}d` can't be played: nothing separates the last gracenote
from the melody note. abc2bww now warns about these ("ends on the melody
note"). The line numbers are from the 2026-11-27 copy of the collection.

- [ ] pipe_hornpipe/crossing_the_minch.abc line 13: `{g}g`
- [ ] pipe_march/father_eugenes_welcome_to_cape_north_2_4.abc line 12: `{g}g`
- [ ] pipe_march/haughs_of_cromdale_2_4.abc lines 30, 31, 34: `{g}g` (Lee has `{f}g`; see section 3)
- [ ] pipe_march/macleod_of_mull_6_8.abc line 15: `{gef}f` (`{gef}` is the doubling on E)
- [ ] pipe_march/minstrel_boy_4_4.abc line 24: `{fg}g`
- [ ] pipe_march/teribus_2_4.abc lines 10, 12: `{gf}f`
- [ ] pipe_march/wagenborgen_4_4.abc lines 14, 16, 23: `{f}f`. This tune is also
      a test fixture (`tests/fixtures/abc/`), so fix the copy there as well.
- [ ] pipe_reel/kalabakan.abc line 11 (twice) and line 12: `{a}a`
- [ ] pipe_strathspey/dalnahassaig.abc line 10: `{gf}f`. This tune is also a test
      fixture, so fix the copy there as well.

## 5. Decisions made while you were away

Change any you disagree with.

1. The plan's 7 test tunes were all transcriptions of Lee tunes, so they were
   replaced with non-Lee tunes from your collection.
2. When several BWW names give the same gracenotes, the converter picks the one
   Lee uses most often. Only the counts are stored in `grace_prefs.py`.
3. The triplet marker goes after the gracenote (`gg ^3s`), as Lee does it.
4. Notes or an ending after a line's last barline move to the start of the next
   staff.
5. An ending still open at the end of a line is closed there. A mid-line `||`
   becomes `I!`. Staves with no notes are skipped, with a warning.
6. ABC forms now accepted: `[|:`, `:|]`, a bare `]`, `["2 of 2"` (written
   `'22`), `\` line continuation, and grace groups written one after another.
7. Uppercase C–F are lowered, with a warning. Slurs are dropped, with a
   warning. `Q:` is read wherever it appears.
8. Output files use Windows line endings and the cp1252 character set. No
   `space` tokens are written, so the layout is a bit tighter than Lee's.
9. Tempo defaults to 90 when there's no `Q:`. The note value in `Q:` isn't
   converted.

## 6. Known minor gaps (not fixed)

- `:|:` and `||:` lose the repeat start. A warning prints; none of these are
  in your collection.
- A triplet that contains a rest closes on the wrong note.
- Three notes tied in a row produce overlapping tie marks.
- A staff that's only a final barline is skipped, so the tune ends on a plain
  barline instead of the final double bar.
- Characters outside cp1252 become `?` without a warning.
- `--stdout` output uses Unix line endings.
- A part label inside a dropped harmony voice attaches to the melody.
- Duration warnings name the staff but not the bar.
- `CLAUDE.md` still lists the deleted `tests/test_converter.py`.
- With `--force`, two inputs that have the same name overwrite each other in
  one output folder.

## 7. Repo housekeeping

- [ ] Local refs under `refs/agents/…/checkpoints/` (commit 3601f90) contain
      purchased BWW files. A normal push doesn't send them, but
      `git push --mirror` would. Consider deleting them:
      `git for-each-ref refs/agents --format='%(refname)' | xargs -n1 git update-ref -d`
- [x] `scratch/` is now git-ignored.
- [ ] Open a pull request for `abc2bww` when you're ready:
      https://github.com/eeferg/bmw2abc_converter/pull/new/abc2bww
