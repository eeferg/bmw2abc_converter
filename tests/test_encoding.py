"""Accented text (Gaelic titles, composers) must survive both directions."""

import io
import sys

from bww_abc import main as bww2abc_main
from bww_abc.abc2bww import convert_abc, main as abc2bww_main
from bww_abc.converter import convert_file

GAELIC = "Cabar Fèidh — Mòrag à Tìr nan Òg, Ùisdean"
BWW = ('Bagpipe Music Writer Gold:1.0\r\n'
       f'"{GAELIC}",(T,C,0,0,Times New Roman,24,700,0,0,18,0,0,0)\r\n'
       '& sharpf sharpc 2_4 LA_4 !I\r\n')


def test_bww2abc_reads_windows_encoded_file(tmp_path):
    f = tmp_path / "t.bww"
    f.write_bytes(BWW.encode("cp1252"))
    assert f"T:{GAELIC}" in convert_file(f)


def test_bww2abc_reads_utf8_file(tmp_path):
    f = tmp_path / "t.bww"
    f.write_bytes(BWW.encode("utf-8"))
    assert f"T:{GAELIC}" in convert_file(f)


def test_bww2abc_reads_windows_encoded_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["bww2abc"])
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(BWW.encode("cp1252")), encoding="utf-8"))
    bww2abc_main()
    assert f"T:{GAELIC}" in capsys.readouterr().out


def test_gaelic_round_trip(tmp_path):
    abc = tmp_path / "t.abc"
    abc.write_text(f"X:1\nT:{GAELIC}\nC:Ùisdean MacDhòmhnaill\nM:2/4\nL:1/8\nK:HP\nA4|]\n", encoding="utf-8")
    assert abc2bww_main([str(abc), "-o", str(tmp_path)]) == 0
    back = convert_file(tmp_path / "t.bww")
    assert f"T:{GAELIC}" in back and "C:Ùisdean MacDhòmhnaill" in back


def test_abc2bww_warns_on_characters_bmw_cannot_store():
    (_, warnings), = convert_abc("X:1\nT:Ŵyn ăla\nM:2/4\nL:1/8\nK:HP\nA4|]\n")
    assert any("Ŵ" in w and "ă" in w and "?" in w for w in warnings)


def test_abc2bww_no_warning_for_gaelic():
    (_, warnings), = convert_abc(f"X:1\nT:{GAELIC}\nM:2/4\nL:1/8\nK:HP\nA4|]\n")
    assert not any("character" in w for w in warnings)
