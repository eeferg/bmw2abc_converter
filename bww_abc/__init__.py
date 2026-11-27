import argparse
import sys
from pathlib import Path

from .converter import convert, convert_file, decode_text


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bww2abc",
        description="Convert Bagpipe Music Writer (.bww, and legacy .bmw) files to ABC notation"
    )
    parser.add_argument("input", nargs="?", help="Input .bww or legacy .bmw file (omit to read stdin)")
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
    parser.add_argument(
        "--swap-title-type",
        action="store_true",
        help="swap title and tune type (bagpipemusic.com / Lee & Sons files store them reversed)",
    )
    args = parser.parse_args()

    key_type = "Hp" if args.hp else "HP"
    unit = 16 if args.unit == "1/16" else 8

    if args.input:
        abc = convert_file(args.input, key_type=key_type, unit=unit,
                           swap_title_type=args.swap_title_type)
    else:
        bww_text = decode_text(sys.stdin.buffer.read())
        abc = convert(bww_text, filename="stdin", key_type=key_type, unit=unit,
                      swap_title_type=args.swap_title_type)

    if args.output:
        Path(args.output).write_text(abc, encoding="utf-8")
    else:
        sys.stdout.write(abc)


__all__ = ["convert", "main"]
