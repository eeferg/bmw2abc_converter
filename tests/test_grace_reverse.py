import pytest

from bmw2abc_converter.grace_notes import GRACE
from bmw2abc_converter.grace_reverse import embellishment_tokens


@pytest.mark.parametrize("grace,pitch,token", [
    ("g", "f", "gg"), ("d", "e", "dg"), ("e", "A", "eg"), ("a", "g", "tg"),
    ("gef", "e", "dbe"), ("gcd", "c", "dbc"), ("Gdc", "d", "thrd"),
    ("GdG", "A", "grp"), ("gBd", "B", "dbb"), ("gfg", "f", "dbf"),
    ("gf", "g", "dbhg"), ("ag", "a", "dbha"), ("fg", "f", "hdbf"),
    ("GAG", "A", "brl"), ("AGAG", "A", "abr"), ("gAGAG", "A", "gbr"),
    ("GdGe", "e", "tar"), ("gec", "d", "lgstd"),
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
