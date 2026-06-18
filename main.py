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
    args = parser.parse_args()

    if args.input:
        abc = convert_file(args.input)
    else:
        bww_text = sys.stdin.read()
        abc = convert(bww_text, filename="stdin")

    if args.output:
        Path(args.output).write_text(abc, encoding="utf-8")
    else:
        sys.stdout.write(abc)


if __name__ == "__main__":
    main()
