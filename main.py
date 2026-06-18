import argparse
import sys
from pathlib import Path

from bmw2abc_converter.converter import convert_file, convert


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
    args = parser.parse_args()

    key_type = "Hp" if args.hp else "HP"

    if args.input:
        abc = convert_file(args.input, key_type=key_type)
    else:
        bww_text = sys.stdin.read()
        abc = convert(bww_text, filename="stdin", key_type=key_type)

    if args.output:
        Path(args.output).write_text(abc, encoding="utf-8")
    else:
        sys.stdout.write(abc)


if __name__ == "__main__":
    main()
