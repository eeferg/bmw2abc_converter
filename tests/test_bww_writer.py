from bww_abc.abc_parse import parse_abc
from bww_abc.bww_writer import write_bww

HDR = "X:1\nT:Barren Rocks\nR:March\nC:A. MacKellar\nM:2/4\nL:1/16\nK:HP\n"
HDR8 = HDR.replace("L:1/16", "L:1/8")


def music(abc_body, hdr=HDR):
    out = write_bww(parse_abc(hdr + abc_body)[0])
    return out[out.index("&"):].split()


def test_header():
    out = write_bww(parse_abc(HDR + "A4|\n")[0])
    assert out.startswith("Bagpipe Music Writer Gold:1.0")
    assert '"Barren Rocks",(T,C,0,0,Times New Roman,24,700,0,0,18,0,0,0)' in out
    assert '"March",(Y,L,0,0,Times New Roman,14,700,0,0,18,0,0,0)' in out
    assert '"A. MacKellar",(M,R,0,0,Times New Roman,14,700,0,0,18,0,0,0)' in out
    assert "TuneTempo,90" in out


def test_header_tempo_and_missing_fields():
    out = write_bww(parse_abc("X:1\nT:X\nM:C|\nL:1/8\nQ:1/4=70\nK:HP\nA4|\n")[0])
    assert "TuneTempo,70" in out and "(Y," not in out and "(M," not in out
    assert music("A4|\n", "X:1\nT:X\nM:C|\nL:1/8\nK:HP\n")[:4] == ["&", "sharpf", "sharpc", "C_"]


def test_first_line_barren_rocks():
    assert music("|: e2 | {g}f2>g2 {fg}f2>e2 |\n") == [
        "&", "sharpf", "sharpc", "2_4", "I!''", "E_8",
        "!", "gg", "Fr_8", "'f", "HGl_16", "hdbf", "Fr_8", "'f", "El_16", "!t"]


def test_second_staff_has_no_time_sig():
    m = music("A4|\nB4|\n")
    assert m == ["&", "sharpf", "sharpc", "2_4", "LA_4", "!t", "&", "sharpf", "sharpc", "B_4", "!t"]


def test_repeat_end_and_quarter():
    assert music("{Gdc}d4{gdc}d2 :|\n")[-4:] == ["D_4", "lgstd", "D_8", "''!I"]


def test_tie_and_triplet():
    assert music("{g}A4- A4 |\n", HDR8)[4:] == ["gg", "^ts", "LA_2", "LA_2", "^te", "!t"]
    assert music("(3efg A2|\n", HDR8)[4:] == ["^3s", "Er_8", "Fl_8", "HGl_8", "^3e", "LA_4", "!t"]


def test_endings():
    m = music("|1 B8 :|2 c8 |]\n", HDR8)
    # Lee writes the repeat before a 2nd ending ('_' ''!I' 17x vs '_' !' once)
    assert m[4:] == ["'1", "B_1", "_'", "''!I", "'2", "C_1", "_'", "!I"]


def test_explicit_ending_close_and_n_of_m():
    m = music('A4 [1 B4 ] :|\n', HDR8)
    assert m[4:] == ["LA_2", "'1", "B_2", "_'", "''!I"]
    assert music('["2 of 2" B4 ] :|\n', HDR8)[4] == "'22"


def test_mid_line_repeats():
    assert music("A4 :: B4 |\n", HDR8)[4:] == ["LA_2", "''!I", "I!''", "B_2", "!t"]


def test_rest():
    assert music("z2 A2|\n", HDR8)[4:] == ["REST_4", "LA_4", "!t"]


def test_part_label():
    out = write_bww(parse_abc(HDR + "A4|\n% 2nd Part\nB4|\n")[0])
    assert '\n"2nd Part"\n& sharpf sharpc' in out


def test_line_ending_mid_bar_warns():
    t = parse_abc(HDR + "A4 B4\nc4 d4|\n")[0]
    write_bww(t)
    assert any("mid-bar" in w for w in t.warnings)


def test_unmappable_duration_warns():
    t = parse_abc(HDR8 + "c5 z|\n")[0]
    out = write_bww(t)
    assert "C_2" in out and any("no BWW duration" in w for w in t.warnings)


def test_grace_warning_carried():
    t = parse_abc(HDR8 + "{gcdc}A2|\n")[0]
    write_bww(t)
    assert any("no named embellishment" in w for w in t.warnings)


def test_inline_meter_change():
    assert "C_" in music("A4 | [M:C|] B4|\n", HDR8)[5:]


def test_triplet_marker_follows_grace_like_lee():
    # Lee: "thrd D_4 gg ^3s Er_16 Fl_16 HGl_16 ^3e"
    assert music("{g}(3efg A2|\n", HDR8)[4:] == [
        "gg", "^3s", "Er_8", "Fl_8", "HGl_8", "^3e", "LA_4", "!t"]


def test_trailing_pickup_moves_to_next_staff():
    t = parse_abc(HDR8 + "A2 B2 | c2 e\n|1 f2 d2 :|\n")[0]
    out = write_bww(t)
    m = out[out.index("&"):].split()
    # the unfinished bar "c2 e" continues at the start of the next staff
    assert m == ["&", "sharpf", "sharpc", "2_4", "LA_4", "B_4", "!t",
                 "&", "sharpf", "sharpc", "C_4", "E_8", "!", "'1", "F_4", "D_4", "_'", "''!I"]
    assert not any("mid-bar" in w for w in t.warnings)


def test_mid_line_double_bar_is_I():
    t = parse_abc(HDR8 + "A4 || B4 |\n")[0]
    assert music("A4 || B4 |\n", HDR8)[4:] == ["LA_2", "I!", "B_2", "!t"]


def test_ending_started_at_line_end_moves_to_next_staff():
    t = parse_abc(HDR8 + "|1 A4 :|2\nB4 |]\n")[0]
    out = write_bww(t)
    assert out[out.index("&"):].split() == [
        "&", "sharpf", "sharpc", "2_4", "'1", "LA_2", "_'", "''!I",
        "&", "sharpf", "sharpc", "'2", "B_2", "_'", "!I"]
    assert not any("mid-bar" in w for w in t.warnings)


def test_staff_with_no_notes_is_skipped():
    t = parse_abc(HDR8 + "A4 |\n |   |   |\n")[0]
    out = write_bww(t)
    assert out.count("& sharpf sharpc") == 1
    assert any("no notes" in w for w in t.warnings)


def test_repeat_before_second_ending_kept_across_lines():
    m = music("|1 A4 :|\n[2 B4 |]\n", HDR8)
    assert m == ["&", "sharpf", "sharpc", "2_4", "'1", "LA_2", "_'", "''!I",
                 "&", "sharpf", "sharpc", "'2", "B_2", "_'", "!I"]


def test_body_meter_line_kept():
    m = music("A2 B2 |\nM:3/4\nA2 B2 c2 |]\n", HDR8)
    assert m[6:] == ["!t", "&", "sharpf", "sharpc", "3_4", "LA_4", "B_4", "C_4", "!I"]


def test_source_written_as_footer():
    out = write_bww(parse_abc(HDR.replace("K:HP", "B:PM Tom Johnstone Handout\nK:HP") + "A4|\n")[0])
    assert '"PM Tom Johnstone Handout",(F,L,0,0,Times New Roman,10,400,0,0,18,0,0,0)' in out
    assert out.index("(F,") < out.index("&")


def test_no_footer_without_source():
    assert "(F," not in write_bww(parse_abc(HDR + "A4|\n")[0])
