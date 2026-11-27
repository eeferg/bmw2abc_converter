from bww_abc import convert

BWW = ('Bagpipe Music Writer Gold:1.0\n'
       '"March",(T,L,0,0,Times New Roman,14,700,0,0,18,0,0,0)\n'
       '"The Barren Rocks of Aden",(Y,C,0,0,Times New Roman,24,700,0,0,18,0,0,0)\n'
       '& sharpf sharpc 2_4 LA_4 !t\n')


def test_default_reads_codes_literally():
    out = convert(BWW)
    assert "T:March" in out and "R:The Barren Rocks of Aden" in out


def test_swap_flag():
    out = convert(BWW, swap_title_type=True)
    assert "T:The Barren Rocks of Aden" in out and "R:March" in out
    assert out.index("T:The Barren") < out.index("R:March")
