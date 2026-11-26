from fractions import Fraction as F

from bmw2abc_converter.abc_model import Bar, Note
from bmw2abc_converter.abc_parse import parse_abc

HDR = "X:1\nT:Test Tune\nT:Second Title\nR:March\nC:Trad\nM:2/4\nL:1/8\nK:HP\n"


def notes(tune):
    return [i for l in tune.lines for i in l.items if isinstance(i, Note)]


def test_header_fields():
    t = parse_abc(HDR + "A2 B2|\n")[0]
    assert (t.title, t.tune_type, t.composer, t.meter, t.tempo) == ("Test Tune", "March", "Trad", "2/4", None)


def test_tempo():
    assert parse_abc(HDR + "Q:1/4=80\nA2|\n")[0].tempo == 80


def test_broken_rhythm_and_grace():
    n = notes(parse_abc(HDR + "{g}f>e {Gdc}d<{g}e|\n")[0])
    assert [(x.pitch, x.length, x.grace) for x in n] == [
        ("f", F(3, 16), "g"), ("e", F(1, 16), ""), ("d", F(1, 16), "Gdc"), ("e", F(3, 16), "g")]
    assert [x.beam_start for x in n] == [True, False, True, False]


def test_broken_rhythm_across_grace_and_unit_16():
    t = parse_abc(HDR.replace("L:1/8", "L:1/16") + "A2>{GdG}B2|\n")[0]
    assert [x.length for x in notes(t)] == [F(3, 16), F(1, 16)]


def test_length_modifiers():
    n = notes(parse_abc(HDR + "A/ B// c3/ d3/2 e4|\n")[0])
    assert [x.length for x in n] == [F(1, 16), F(1, 32), F(3, 16), F(3, 16), F(1, 2)]


def test_endings_repeats_tuplet_tie_rest():
    items = parse_abc(HDR + "|: (3efg A2- | A2 z2 |1 B4 :|2 c4 |]\n")[0].lines[0].items
    kinds = [type(i).__name__ if not isinstance(i, Bar) else i.kind for i in items]
    assert kinds == ["|:", "Tuplet", "Note", "Note", "Note", "Note", "|", "Note", "Rest", "|",
                     "Ending", "Note", ":|", "Ending", "Note", "|]"]
    assert notes(parse_abc(HDR + "A2- A2|\n")[0])[0].tie is True


def test_bracket_endings():
    items = parse_abc(HDR + "A4 [1 B4 :|[2 c4 |]\n")[0].lines[0].items
    kinds = [type(i).__name__ if not isinstance(i, Bar) else i.kind for i in items]
    assert kinds == ["Note", "Ending", "Note", ":|", "Ending", "Note", "|]"]


def test_multiple_tunes_and_preamble():
    text = "%%flatbeams 1\n" + HDR + "A2|\n" + HDR + "B2|\n"
    assert len(parse_abc(text)) == 2


def test_part_label_and_crlf():
    t = parse_abc((HDR + "A2|\n% 2nd Part\nB2|\n").replace("\n", "\r\n"))[0]
    assert [l.part_label for l in t.lines] == [None, "2nd Part"]


def test_harmony_dropped():
    t = parse_abc(HDR + "V:1\nA2|\nV:2\nc2|\n")[0]
    assert [x.pitch for x in notes(t)] == ["A"] and any("V:2" in w for w in t.warnings)


def test_inline_voice_field_dropped():
    t = parse_abc(HDR + "[V:1] A2|\n[V:2] c2|\n")[0]
    assert [x.pitch for x in notes(t)] == ["A"]


def test_chords_and_unknown_warn():
    t = parse_abc(HDR + '"Bm"A2 &B2|\n')[0]
    assert any("chord" in w for w in t.warnings) and any("not recognised" in w for w in t.warnings)


def test_slash_rest_decoration():
    t = parse_abc(HDR + "!head-slashr!z2 A2|]\n")[0]
    assert any("slash" in w for w in t.warnings)
    assert type(t.lines[0].items[0]).__name__ == "Rest"


def test_l_trailing_junk_warns():
    t = parse_abc(HDR.replace("L:1/8", "L:1/8 8 40") + "A|\n")[0]
    assert notes(t)[0].length == F(1, 8) and t.warnings


def test_lyrics_and_trailing_fields_ignored():
    t = parse_abc(HDR + "A2|\nW:some words\nW:\n")[0]
    assert len(t.lines) == 1 and not t.warnings


def test_inline_meter():
    items = parse_abc(HDR + "A2 | [M:C|] B4|\n")[0].lines[0].items
    assert any(type(i).__name__ == "Meter" and i.meter == "C|" for i in items)


def test_thick_repeat_variants_and_ending_close():
    items = parse_abc(HDR + "[|: A2 | B2 [1 c2 ][2 d2 ] :|]\n")[0].lines[0].items
    kinds = [type(i).__name__ if not isinstance(i, Bar) else i.kind for i in items]
    assert kinds == ["|:", "Note", "|", "Note", "Ending", "Note", "EndingClose", "Ending", "Note",
                     "EndingClose", ":|"]
    assert not parse_abc(HDR + "[|: A2 :|]\n")[0].warnings


def test_labelled_ending_n_of_m():
    items = parse_abc(HDR + '["2 of 2"A2 ] :|\n')[0].lines[0].items
    assert items[0] == __import__("bmw2abc_converter.abc_model", fromlist=["Ending"]).Ending(22)
    assert not parse_abc(HDR + '["2 of 2"A2 ] :|\n')[0].warnings
