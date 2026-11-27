from pathlib import Path

from bww_abc.abc2bww import convert_abc, main, output_names

TUNE = "X:1\nT:Tune\nR:Reel\nM:C|\nL:1/8\nK:HP\nA2 B2 c2 d2|\n"


def write(path: Path, text: str = TUNE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_output_names():
    assert output_names(Path("x/cullen_bay.abc"), 1) == ["cullen_bay.bww"]
    assert output_names(Path("x/cullen_bay.abc"), 3) == [
        "cullen_bay001.bww", "cullen_bay002.bww", "cullen_bay003.bww"]


def test_convert_abc_returns_text_and_warnings():
    [(text, warnings)] = convert_abc(TUNE)
    assert text.startswith("Bagpipe Music Writer Gold:1.0") and warnings == []


def test_single_file_to_cwd_with_crlf(tmp_path, monkeypatch):
    src = write(tmp_path / "in" / "tune.abc")
    monkeypatch.chdir(tmp_path)
    assert main([str(src)]) == 0
    data = (tmp_path / "tune.bww").read_bytes()
    assert data.startswith(b"Bagpipe Music Writer Gold:1.0\r\n")
    assert b"\n" not in data.replace(b"\r\n", b"")


def test_multi_tune_file_numbered(tmp_path, monkeypatch):
    src = write(tmp_path / "tune.abc", TUNE + "\n" + TUNE)
    monkeypatch.chdir(tmp_path)
    assert main([str(src)]) == 0
    assert (tmp_path / "tune001.bww").exists() and (tmp_path / "tune002.bww").exists()
    assert not (tmp_path / "tune.bww").exists()


def test_several_files_to_out_dir(tmp_path):
    a, b = write(tmp_path / "a.abc"), write(tmp_path / "b.abc")
    out = tmp_path / "out"
    assert main([str(a), str(b), "-o", str(out)]) == 0
    assert (out / "a.bww").exists() and (out / "b.bww").exists()


def test_no_overwrite_without_force(tmp_path, monkeypatch):
    src = write(tmp_path / "tune.abc")
    monkeypatch.chdir(tmp_path)
    (tmp_path / "tune.bww").write_text("keep me")
    assert main([str(src)]) == 1
    assert (tmp_path / "tune.bww").read_text() == "keep me"
    assert main([str(src), "--force"]) == 0
    assert (tmp_path / "tune.bww").read_text() != "keep me"


def test_stdout(tmp_path, monkeypatch, capsys):
    src = write(tmp_path / "tune.abc")
    monkeypatch.chdir(tmp_path)
    assert main([str(src), "--stdout"]) == 0
    assert capsys.readouterr().out.startswith("Bagpipe Music Writer Gold:1.0")
    assert not (tmp_path / "tune.bww").exists()


def test_stdout_rejects_multi_tune(tmp_path):
    src = write(tmp_path / "tune.abc", TUNE + "\n" + TUNE)
    assert main([str(src), "--stdout"]) == 2


def test_all_only_pipe_folders(tmp_path):
    write(tmp_path / "tunes" / "pipe_reel" / "a.abc")
    write(tmp_path / "tunes" / "piobaireachd" / "b.abc")
    out = tmp_path / "out"
    assert main(["--all", str(tmp_path / "tunes"), "-o", str(out)]) == 0
    assert (out / "pipe_reel" / "a.bww").exists()
    assert not (out / "piobaireachd").exists()


def test_all_requires_out(tmp_path):
    assert main(["--all", str(tmp_path)]) == 2


def test_missing_file_fails(tmp_path, capsys):
    assert main([str(tmp_path / "nope.abc"), "-o", str(tmp_path)]) == 1


def test_warnings_printed(tmp_path, capsys):
    src = write(tmp_path / "tune.abc", TUNE.replace("A2 B2", '"Bm"A2 B2'))
    main([str(src), "-o", str(tmp_path)])
    assert "chord" in capsys.readouterr().err


def test_all_missing_folder_is_an_error(tmp_path, capsys):
    assert main(["--all", str(tmp_path / "nope"), "-o", str(tmp_path / "o")]) == 2
    assert "not a folder" in capsys.readouterr().err
