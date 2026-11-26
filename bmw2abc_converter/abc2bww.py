"""abc2bww: convert pipe-tune ABC files to Bagpipe Music Writer Gold (.bww)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .abc_parse import parse_abc
from .bww_writer import write_bww

# BMW Gold is a Windows program; write its files the way it does.
BWW_ENCODING = "cp1252"
BWW_NEWLINE = "\r\n"


def convert_abc(text: str) -> list[tuple[str, list[str]]]:
    """(bww_text, warnings) for each X: tune in the ABC text, in file order."""
    results = []
    for tune in parse_abc(text):
        bww = write_bww(tune)
        results.append((bww, list(tune.warnings)))
    return results


def output_names(abc_path: Path, n_tunes: int) -> list[str]:
    """name.bww for one tune; name001.bww, name002.bww, ... for several (abcm2ps style)."""
    stem = abc_path.stem
    if n_tunes == 1:
        return [f"{stem}.bww"]
    return [f"{stem}{i:03d}.bww" for i in range(1, n_tunes + 1)]


def _read_abc(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def _write_bww(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding=BWW_ENCODING, errors="replace", newline=BWW_NEWLINE) as fh:
        fh.write(text)


def _convert_one(src: Path, out_dir: Path, force: bool) -> tuple[bool, bool]:
    """Convert one ABC file. Returns (ok, had_warnings)."""
    try:
        results = convert_abc(_read_abc(src))
    except OSError as exc:
        print(f"{src}: cannot read ({exc.strerror})", file=sys.stderr)
        return False, False
    if not results:
        print(f"{src}: no X: tunes found", file=sys.stderr)
        return False, False
    names = output_names(src, len(results))
    targets = [out_dir / n for n in names]
    existing = [t for t in targets if t.exists()]
    if existing and not force:
        for t in existing:
            print(f"{src.name}: {t} exists; use --force to overwrite", file=sys.stderr)
        return False, False
    had_warnings = False
    for target, (text, warnings) in zip(targets, results):
        _write_bww(target, text)
        print(f"{src.name} → {target}", file=sys.stderr)
        for w in warnings:
            print(f"    {w}", file=sys.stderr)
        had_warnings |= bool(warnings)
    return True, had_warnings


def _collect_all(root: Path) -> list[tuple[Path, Path]]:
    """(abc file, relative output folder) for every ABC file under pipe_* folders."""
    pairs = []
    for folder in sorted(p for p in root.iterdir() if p.is_dir() and p.name.startswith("pipe_")):
        for abc in sorted(folder.rglob("*.abc")):
            pairs.append((abc, abc.parent.relative_to(root)))
    return pairs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="abc2bww",
        description="Convert pipe-tune ABC files to Bagpipe Music Writer Gold (.bww).",
    )
    parser.add_argument("files", nargs="*", type=Path, help="ABC file(s) to convert")
    parser.add_argument("-o", "--out", type=Path, help="output folder (default: current folder)")
    parser.add_argument("--force", action="store_true", help="overwrite existing .bww files")
    parser.add_argument("--stdout", action="store_true",
                        help="print the BWW instead of writing a file (one single-tune file only)")
    parser.add_argument("--all", type=Path, metavar="DIR",
                        help="convert every ABC file in DIR's pipe_* folders (needs -o)")
    args = parser.parse_args(argv)

    if args.stdout:
        if args.all or len(args.files) != 1:
            print("--stdout takes exactly one ABC file", file=sys.stderr)
            return 2
        try:
            results = convert_abc(_read_abc(args.files[0]))
        except OSError as exc:
            print(f"{args.files[0]}: cannot read ({exc.strerror})", file=sys.stderr)
            return 1
        if len(results) != 1:
            print(f"--stdout needs a single-tune file; {args.files[0].name} has {len(results)} tunes",
                  file=sys.stderr)
            return 2
        text, warnings = results[0]
        sys.stdout.write(text)
        for w in warnings:
            print(f"    {w}", file=sys.stderr)
        return 0

    jobs: list[tuple[Path, Path]] = []
    if args.all:
        if args.out is None:
            print("--all needs -o OUTPUT_FOLDER", file=sys.stderr)
            return 2
        jobs = [(abc, args.out / rel) for abc, rel in _collect_all(args.all)]
    out_dir = args.out if args.out is not None else Path.cwd()
    jobs += [(f, out_dir) for f in args.files]
    if not jobs:
        parser.print_usage(sys.stderr)
        return 2

    failed = written = warned = 0
    for src, dest in jobs:
        ok, had_warnings = _convert_one(src, dest, args.force)
        if ok:
            written += 1
            warned += had_warnings
        else:
            failed += 1
    if len(jobs) > 1:
        print(f"{written} files written, {warned} with warnings"
              + (f", {failed} failed" if failed else ""), file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
