import pytest

from bww_abc import convert
from bww_abc.grace_notes import GRACE
from bww_abc.grace_reverse import embellishment_tokens


@pytest.mark.parametrize("grace,pitch,token", [
    ("g", "f", "gg"), ("d", "e", "dg"), ("e", "A", "eg"), ("a", "g", "tg"),
    ("gef", "e", "dbe"), ("gcd", "c", "dbc"), ("Gdc", "d", "thrd"),
    ("GdG", "A", "grp"), ("gBd", "B", "dbb"), ("gfg", "f", "dbf"),
    ("gf", "g", "dbhg"), ("ag", "a", "dbha"), ("fg", "f", "hdbf"),
    ("GAG", "A", "brl"), ("AGAG", "A", "abr"), ("gAGAG", "A", "gbr"),
    ("GdGe", "A", "tar"), ("gdc", "d", "lgstd"),
])
def test_common_collection_graces(grace, pitch, token):
    assert embellishment_tokens(grace, pitch) == ([token], None)


def test_unnamed_group_falls_back_with_warning():
    tokens, warning = embellishment_tokens("gcdc", "A")
    assert tokens == ["gg", "cg", "dg", "cg"]
    assert "no named embellishment" in warning


def test_low_g_in_unnamed_group_warns():
    tokens, warning = embellishment_tokens("GfGf", "A")
    assert "low-G" in warning
    assert tokens == ["fg", "fg"]


def test_every_grace_token_round_trips_or_is_known_collision():
    collisions = []
    for token, seq in GRACE.items():
        hits = [p for p in "GABcdefga" if embellishment_tokens(seq, p)[0] == [token]]
        if not hits:
            collisions.append(token)
    print("collisions:", collisions)
    assert len(collisions) < 40, collisions


def test_light_g_strike_on_d_is_gdc():
    # Ed's collection writes this 115x as {gdc}d; ltstd is "adc" by the same pattern.
    assert GRACE["lgstd"] == "gdc"
    assert embellishment_tokens("gdc", "d") == (["lgstd"], None)


def test_bww2abc_renders_lgstd_as_gdc():
    from bww_abc import convert
    out = convert("& sharpf sharpc 2_4 lgstd D_4 !t\n")
    assert "{gdc}d" in out


def test_legacy_gec_before_d_still_means_lgstd():
    # ABC made by the old converter wrote lgstd as {gec}d
    assert embellishment_tokens("gec", "d") == (["lgstd"], None)


def test_light_half_strike_on_d():
    # BMW manual: lhstd = light half strike on D = {dc}d ({ed}d is unplayable)
    assert GRACE["lhstd"] == "dc"
    assert "{dc}d" in convert('& sharpf sharpc 2_4 lhstd D_4 !I\n', filename="t.bww")


@pytest.mark.parametrize("grace,pitch", [("ed", "d"), ("g", "g"), ("gef", "f"), ("a", "a"), ("fg", "g")])
def test_grace_ending_on_melody_pitch_warns(grace, pitch):
    tokens, warning = embellishment_tokens(grace, pitch)
    assert tokens  # still written, so nothing is silently lost
    assert warning and "ends on the melody note" in warning


def test_grace_ending_elsewhere_does_not_warn():
    assert embellishment_tokens("dc", "d") == (["hthrd"], None)
    assert embellishment_tokens("gdG", "d")[1] is None
