"""Basic smoke tests for the BWW -> ABC converter."""

from bmw2abc_converter import convert

AMAZING_GRACE_BWW = """\
Bagpipe Reader:1.0
MIDINoteMappings,(54,56,58,59,61,63,64,66,68,56,58,59,61,63,64,66,68,70)
FrequencyMappings,(370,415,466,494,554,622,659,740,831,415,466,494,554,622,659,740,831,932)
InstrumentMappings,(71,71,45,33,1000,60,70)
GracenoteDurations,(20,40,30,50,40,30,20)
FontSizes,(100,90,90)
TuneFormat,(1,0,M,L,500,500,500,500)
TuneTempo,90
"Amazing Grace",(T,L,0,0,Times New Roman,14,700,0,0,0)
"John Newton",(M,L,0,0,Times New Roman,12,400,0,0,0)
"Hymn",(Y,L,0,0,Times New Roman,11,400,0,0,0)
& sharpf sharpc 3_4
LA_4 LA_8 LA_8 B_4 LA_4 B_8 B_8 LA_4
!t
LA_4 LA_4 LG_8 LA_4 B_4
!t
"""


def test_header_title():
    abc = convert(AMAZING_GRACE_BWW, "amazing_grace.bww")
    assert "T:Amazing Grace" in abc


def test_header_composer():
    abc = convert(AMAZING_GRACE_BWW, "amazing_grace.bww")
    assert "C:John Newton" in abc


def test_header_rhythm():
    abc = convert(AMAZING_GRACE_BWW, "amazing_grace.bww")
    assert "R:Hymn" in abc


def test_tempo():
    abc = convert(AMAZING_GRACE_BWW, "amazing_grace.bww")
    assert "Q:1/4=90" in abc


def test_time_signature():
    abc = convert(AMAZING_GRACE_BWW, "amazing_grace.bww")
    assert "M:3/4" in abc


def test_key_signature_default_hp():
    # Default: K:HP — standard F#/C# accidentals are not emitted explicitly.
    abc = convert(AMAZING_GRACE_BWW, "amazing_grace.bww")
    assert "K:HP" in abc
    assert "exp" not in abc


def test_key_signature_hp_flag():
    # --hp flag: K:Hp — standard accidentals still not repeated as exp.
    abc = convert(AMAZING_GRACE_BWW, "amazing_grace.bww", key_type="Hp")
    assert "K:Hp" in abc
    assert "exp" not in abc


def test_key_signature_non_standard_acc():
    # Non-standard accidental (e.g. naturalc) should appear as exp.
    bww = """\
& sharpf sharpc naturalc 3_4
LA_4
!t
"""
    abc = convert(bww)
    assert "exp" in abc
    assert "=c" in abc


def test_barlines():
    abc = convert(AMAZING_GRACE_BWW, "amazing_grace.bww")
    assert " |" in abc


def test_low_a_note():
    abc = convert(AMAZING_GRACE_BWW, "amazing_grace.bww")
    # LA_4 -> quarter Low-A -> ABC 'A2'
    assert "A2" in abc


def test_low_g_note():
    abc = convert(AMAZING_GRACE_BWW, "amazing_grace.bww")
    # LG_8 -> eighth Low-G -> ABC 'G' (no suffix)
    assert "G " in abc or "G\n" in abc or "G|" in abc


def test_grace_note_doubling_low_g():
    # dblg = regular doubling on Low-G -> {gGd}
    bww = """\
& sharpf sharpc 4_4
dblg LG_8
!t
"""
    abc = convert(bww)
    assert "{gGd}" in abc


def test_grace_note_doubling_low_a():
    # dbla = regular doubling on Low-A -> {gAd}
    bww = """\
& sharpf sharpc 4_4
dbla LA_8
!t
"""
    abc = convert(bww)
    assert "{gAd}" in abc


def test_dotted_quarter():
    bww = """\
& sharpf sharpc 4_4
LA_4 'a B_8
!t
"""
    abc = convert(bww)
    # dotted quarter Low-A: denom=4 single dot -> 'A3'
    assert "A3" in abc


def test_repeat_barlines():
    bww = """\
& sharpf sharpc 4_4
I!'' LA_8 LA_8 LA_8 LA_8 ''!I
"""
    abc = convert(bww)
    assert "|:" in abc
    assert ":|" in abc


def test_rest():
    bww = """\
& sharpf sharpc 4_4
REST_4 LA_4
!t
"""
    abc = convert(bww)
    assert "z2" in abc


def test_abc_header_present():
    abc = convert(AMAZING_GRACE_BWW)
    assert abc.startswith("%abc-2.2")
    assert "X:1" in abc
    assert "L:1/8" in abc
