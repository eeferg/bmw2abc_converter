import argparse
import sys
from pathlib import Path

from .converter import convert, convert_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert Bagpipe Music Writer (.bww/.bmw) files to ABC notation"
    )
    parser.add_argument("input", nargs="?", help="Input BWW/BMW file (omit to read stdin)")
    parser.add_argument("-o", "--output", help="Output ABC file (default: stdout)")
    parser.add_argument(
        "--hp",
        action="store_true",
        help="Use K:Hp key signature (shows F#/C# on staff) instead of default K:HP",
    )
    parser.add_argument(
        "--unit",
        choices=["1/8", "1/16"],
        default="1/8",
        help="Unit note length: 1/8 (default) or 1/16",
    )
    args = parser.parse_args()

    key_type = "Hp" if args.hp else "HP"
    unit = 16 if args.unit == "1/16" else 8

    if args.input:
        abc = convert_file(args.input, key_type=key_type, unit=unit)
    else:
        bww_text = sys.stdin.read()
        abc = convert(bww_text, filename="stdin", key_type=key_type, unit=unit)

    if args.output:
        Path(args.output).write_text(abc, encoding="utf-8")
    else:
        sys.stdout.write(abc)


__all__ = ["convert", "main"]
