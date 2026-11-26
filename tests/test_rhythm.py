from fractions import Fraction as F

from bmw2abc_converter.rhythm import PITCH_TO_BWW, PITCH_TO_DOT, bww_duration, nearest_duration


def test_plain_durations():
    assert bww_duration(F(1, 1)) == (1, 0)
    assert bww_duration(F(1, 4)) == (4, 0)
    assert bww_duration(F(1, 8)) == (8, 0)
    assert bww_duration(F(1, 32)) == (32, 0)


def test_dotted():
    assert bww_duration(F(3, 16)) == (8, 1)
    assert bww_duration(F(3, 8)) == (4, 1)
    assert bww_duration(F(3, 32)) == (16, 1)


def test_double_dotted():
    assert bww_duration(F(7, 32)) == (8, 2)


def test_unmappable():
    assert bww_duration(F(5, 8)) is None
    assert nearest_duration(F(5, 8)) == (2, 0)


def test_pitch_maps():
    assert PITCH_TO_BWW["G"] == "LG" and PITCH_TO_BWW["a"] == "HA" and PITCH_TO_BWW["c"] == "C"
    assert PITCH_TO_DOT["A"] == "la" and PITCH_TO_DOT["g"] == "hg" and PITCH_TO_DOT["e"] == "e"
