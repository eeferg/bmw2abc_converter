"""Legacy (pre-Gold) BMW files. See docs/bmw_legacy_format.md."""

from bmw2abc_converter import convert

GOLD = "Bagpipe Music Writer Gold:1.0\r\n"
LEGACY_HDR = '"My Tune"\r\r\n"Slow Air"\r\r\n"Arr. A. Piper"\r\r\n""\r\r\n\r\r\n'


def music(body: str, header: str = LEGACY_HDR) -> str:
    """ABC music lines (after K:), with spaces removed for easy matching."""
    out = convert(header + body)
    return out[out.index("K:"):].split("\n", 1)[1].replace(" ", "")


# -- ties -------------------------------------------------------------------

def test_old_tie_on_e_is_kept():
    assert "e2-e2" in music("& 2_4 E_4 ^te E_4 !I\r\r\n")


def test_old_tie_on_other_pitches():
    assert "A2-A2" in music("& 2_4 LA_4 ^tla LA_4 !I\r\r\n")
    assert "e-e" in music("& 2_4 Er_8 ^te El_8 LA_4 !I\r\r\n")


def test_gold_tie_end_does_not_add_a_second_tie():
    m = music("& sharpf sharpc 2_4 ^ts E_4 E_4 ^te !I\n", GOLD)
    assert "e2-e2" in m and m.count("-") == 1


def test_gold_file_mixing_old_tie_on_e():
    m = music("& sharpf sharpc 2_4 ^ts LA_4 LA_4 ^te E_4 ^te E_4 !I\n", GOLD)
    assert "A2-A2e2-e2" in m


# -- triplets ---------------------------------------------------------------

def test_old_triplet_goes_before_its_three_notes():
    m = music("& 2_4 gg Br_16 Cl_16 Dl_16 ^3d LA_4 !I\r\r\n")
    assert "(3{g}B/c/d/" in m and m.count("(3") == 1


def test_old_triplet_ending_on_e():
    m = music("& 2_4 LA_4 Cr_16 Dl_16 El_16 ^3e !I\r\r\n")
    assert "A2(3c/d/e/" in m and m.count("(3") == 1


def test_old_triplet_with_grace_and_dot_inside():
    m = music("& 2_4 LA_4 dbc Cr_16 'c eg Dl_32 El_16 ^3e !I\r\r\n")
    assert "A2(3{gcd}c" in m


def test_gold_triplet_unchanged():
    m = music("& sharpf sharpc 2_4 ^3s Br_16 Cl_16 Dl_16 ^3e LA_4 !I\n", GOLD)
    assert "(3B/c/d/" in m and m.count("(3") == 1


# -- header -----------------------------------------------------------------

def test_legacy_header_by_position():
    out = convert(LEGACY_HDR + "& 2_4 LA_4 !I\r\r\n")
    assert "T:My Tune" in out and "R:Slow Air" in out and "C:Arr. A. Piper" in out
    assert out.index("T:") < out.index("R:") < out.index("C:")
    assert "%%footer" not in out  # empty 4th line


def test_legacy_header_footer_and_extra_lines():
    hdr = '"T1"\n"March"\n"Trad"\n"Set by X"\n"a note"\n'
    out = convert(hdr + "& 2_4 LA_4 !I\n")
    assert "%%footer \tSet by X" in out and "% a note" in out


def test_legacy_header_unterminated_quote():
    out = convert('"T1"\n"Slow Air ( prelude\n"Trad"\n& 2_4 LA_4 !I\n')
    assert "R:Slow Air ( prelude" in out and "C:Trad" in out


def test_gold_bare_quoted_line_stays_a_comment():
    out = convert(GOLD + '"Some text"\n"Title",(T,C,0,0,Times New Roman,24,700,0,0,18,0,0,0)\n'
                  "& sharpf sharpc 2_4 LA_4 !I\n")
    assert "% Some text" in out and "T:Title" in out and "T:Some text" not in out


# -- DOS end-of-file byte ----------------------------------------------------

def test_ctrl_z_is_ignored(capsys):
    out = convert(LEGACY_HDR + "& 2_4 LA_4 ''!I\x1a\r\r\n\x1a")
    assert "not recognised" not in capsys.readouterr().err
    assert ":|" in out


def test_old_tie_after_a_barline_attaches_to_the_note_before_it():
    assert "d2-|d2" in music("& 2_4 LA_4 D_4 ! ^td D_4 E_4 !I\r\r\n")


def test_old_tie_at_start_of_next_staff():
    m = music("& 2_4 LA_4 D_4 !t\r\r\n& ^td D_4 E_4 !I\r\r\n")
    assert "d2-|" in m


def test_old_tie_written_on_both_sides_of_a_staff_break_is_one_tie():
    m = music("& 2_4 LA_4 E_4 'e ^te !t\r\r\n& ^te E_4 LA_4 !I\r\r\n")
    assert "e3-|" in m and "--" not in m
